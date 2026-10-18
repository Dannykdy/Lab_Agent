from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.users import User
from app.dependencies.auth import get_current_user, get_current_admin
from app.service import user_service
from app.common.response import Response
from app.schemas.users import UserUpdateRequest, PasswordUpdateRequest, UserCreateRequest

router = APIRouter(prefix="/user", tags=["用户信息接口"])


@router.get("/me")
def get_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return Response.success(
        message="获取成功", data=user_service.get_user_info(current_user)
    )

@router.put("/update_me")
def update_user_info(data: UserUpdateRequest, 
                     current_user: User = Depends(get_current_user), 
                     db: Session = Depends(get_db)):

    #更新当前用户信息
    res = user_service.update_user_info(current_user, db, data)

    return Response.success(
        message="更新用户信息成功",
        data= res
    )


@router.put("/password")
def update_password(
    data: PasswordUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_service.update_password(current_user, db, data)
    return Response.success(
        message="密码修改成功"
    )


@router.get('/list')
def get_user_list(
    db: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_admin),
    keywords: str | None = None,
):
    res = user_service.get_user_page_list(db, page, page_size, keywords)

    return Response.success(
        message="获取成功",
        data= res
    )


@router.post("")
def create_user(
    data: UserCreateRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    res = user_service.create_user(db, data)
    return Response.success(data=res)


@router.put("/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    res = user_service.update_user(db, user_id, data)
    return Response.success(data=res)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user_service.delete_user(db, user_id, current_user)
    return Response.success(message="删除成功")
