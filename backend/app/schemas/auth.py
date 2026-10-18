"""------------定义数据传输模式格式--------------"""

from pydantic import BaseModel
from app.schemas.users import UserResponse


# 输入体格式
class LoginRequest(BaseModel):
    """登陆传入参数"""
    username : str
    password : str

# 返回体格式
class LoginResponse(BaseModel):
    """登陆成功返回参数"""
    token : str
    user : UserResponse

class RegisterRequest(BaseModel):
    """注册用户传入参数"""
    username: str
    password: str
    name: str | None = None
    phone: str
    email: str
