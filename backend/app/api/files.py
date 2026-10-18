import os
import time
import shutil
import uuid

from pathlib import Path
from fastapi import APIRouter, File, UploadFile

from app.common.exceptions import BusinessException
from app.common.response import Response
from app.schemas.files import FileResponse
from app.config import MAX_FILE_SIZE, UPLOAD_DIR, ALLOWED_EXTENSIONS

router = APIRouter(prefix="/files", tags=["文件管理"])


@router.post("/upload")
def upload(fileobj: UploadFile = File(...)):
    """文件上传接口"""
    # 文件没名字拒绝上传
    if not fileobj.filename:
        raise BusinessException(message="文件未命名，上传失败")
    # 获得文件的原始名字
    original_name = os.path.basename(fileobj.filename)
    # 获得文件的后缀并统一变成小写形式
    extension = Path(original_name).suffix.lower()
    # 获取文件大小
    file_size = fileobj.size

    # 上传文件格式未在合规文件中
    if extension not in ALLOWED_EXTENSIONS:
        raise BusinessException(message="文件上传失败，请上传规定内文件")
    # 上传文件格式大小不合法
    if fileobj.size and fileobj.size > MAX_FILE_SIZE:
        raise BusinessException(
            message=f"文件过大，最大支持 {MAX_FILE_SIZE // 1024 // 1024}MB"
        )

    # 设置一个唯一的名字，按照时间戳的形式 设置唯一性
    disk_name = f"{time.time()*1000}_{uuid.uuid4().hex[:8]}{extension}"
    # 文件保存路径
    save_path = UPLOAD_DIR/disk_name

    with open(save_path, "wb") as f:
        shutil.copyfileobj(fileobj.file, f)

    return Response.success(
        message="文件上传成功",
        data=FileResponse(
            filename=original_name,
            filesize=f"{file_size / 1024 / 1024:.2f} MB",
            diskname=disk_name,
            url=f"/uploads/{disk_name}",
        ),
    )
