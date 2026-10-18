from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.users import User
from app.dependencies.auth import get_current_admin, get_current_user
from app.service import lab_service
from app.common.response import Response
from app.schemas.lab import (
    LabResponse, LabUpdateRequest, LabCreateRequest
)

router = APIRouter(prefix="/lab", tags=["实验室信息接口"])


@router.get("/list")
def get_lab_list(
    db: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),  # 获得权限才能查看实验室
    keywords: str | None = None,
):
    res = lab_service.get_lab_page_list(db, page, page_size, keywords)

    return Response.success(message="获取成功", data=res)


# 获取实验室详情页
@router.get("/list/{lab_id}")
def get_lab_id(
    lab_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 获得权限才能查看实验室

):
    res = lab_service.get_lab(lab_id, db )

    return Response.success(message="获取成功", data=res)


@router.post("")
def create_lab(
    data: LabCreateRequest,
    current_user: User = Depends(get_current_admin),  # 管理员权限才能更新实验室
    db: Session = Depends(get_db),
):
    res = lab_service.create_lab(db, data)
    return Response.success(data=res)


@router.put("/{lab_id}")
def update_lab(
    lab_id: int,
    data: LabUpdateRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    res = lab_service.update_lab(db, lab_id, data)
    return Response.success(data=res)


@router.delete("/{lab_id}")
def delete_lab(
    lab_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    lab_service.delete_lab(db, lab_id)
    return Response.success(message="删除成功")
