from sqlalchemy.orm import Session
from operator import or_

from app.common.exceptions import BusinessException
from app.common.response import PageResponse
from app.models.users import User
from app.schemas.users import UserResponse
from app.schemas.users import UserUpdateRequest, UserCreateRequest, PasswordUpdateRequest
from app.utils.password import hash_password, verify_password

def get_user_info(user: User):

    return UserResponse.model_validate(user)


# 更新用户信息
def update_user_info(user: User, db: Session, data:UserUpdateRequest):

    user_dict = data.model_dump(exclude_none=True)

    for field, value in user_dict.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)

# 更新密码
def update_password(user: User, db: Session, data: PasswordUpdateRequest):

    bool = verify_password(data.old_password, user.password)

    if not bool :
        raise BusinessException(message="原密码输入错误")

    if data.old_password == data.new_password:
        raise BusinessException(message="新密码与旧密码不能相同")

    user.password = hash_password(data.new_password)

    db.commit()


# 管理员查看用户列表
def get_user_page_list(
    db: Session, page: int, page_size: int, keywords: str | None = None
):
    query = db.query(User)

    # select * from user where username like '%张%' or name like '%张%';
    if keywords:
        query = query.filter(
            or_(User.username.ilike(f"%{keywords}%"), User.name.ilike(f"%{keywords}%"))
        )

    total = query.count()

    """offset = 「从第几条之后开始取」.offset(10) 意思：跳过前面 10 条，从第 11 条开始。 limit = 「取多少条」"""

    items = (
        query.order_by(User.id.desc())  # ① 先排序
        .offset((page - 1) * page_size) # ② 再跳过
        .limit(page_size)               # ③ 再取数
        .all()                          # ④ 执行
    )

    return PageResponse(total= total, list= [UserResponse.model_validate(item) for item in items])


# 管理员创建用户
def create_user(db: Session, data: UserCreateRequest):

    exit = db.query(User).filter(data.username == User.username).first()
    if exit:
        raise BusinessException(
            message="该用户已存在"
        )
    user = User(
        username = data.username,
        password = hash_password(data.password),
        name=data.name,
        role=data.role,
        email=data.email,
        phone=data.phone,
        avatar=data.avatar,
        status=data.status
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse.model_validate(user)


# 管理员更新用户
def update_user(db: Session, user_id: int, data: UserUpdateRequest):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BusinessException(message="用户不存在")

    user_dict = data.model_dump(exclude_none=True)

    for filed, value in user_dict.items():
        setattr(user, filed, value)

    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)

#管路员删除用户
def delete_user(db: Session, user_id: int, currut_user: User):

    if user_id == currut_user.id:
        raise BusinessException(message="不能删除当前登录的账号")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BusinessException(message="用户不存在")
    db.delete(user)
    db.commit()
