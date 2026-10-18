"""------------定义数据传输模式格式--------------"""

from pydantic import BaseModel, ConfigDict


# 成功后拿到用户所有信息
class UserResponse(BaseModel):
    """返回用户信息的参数列表"""
    id : int
    username: str
    name: str
    role: str
    email: str | None = None
    phone: str
    avatar: str | None = None
    status: int

    model_config = ConfigDict(from_attributes=True)


class UserUpdateRequest(BaseModel):
    """更新用户信息"""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    avatar: str | None = None
    role: str | None = None
    status: int | None = None


class UserCreateRequest(BaseModel):
    """管理员创建用户的请求参数"""

    username: str
    password: str = "123"
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    avatar: str | None = None
    role: str = "student"
    status: int = 1


class PasswordUpdateRequest(BaseModel):
    """修改密码的请求参数"""

    old_password: str
    new_password: str
