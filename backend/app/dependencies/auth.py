"""------------JWT token 鉴权验证合法性------------------"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.models.users import User
from app.database import get_db
from app.utils.jwt import decode_access_token
from app.common.exceptions import BusinessException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:

    # 检查是否可以解析 有没有过期，有没有用户ID，签名对不对
    try:
        payload = decode_access_token(token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录失效！请重新登录"
            )
    # 有没有user_id这个字段
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="验证失败，无效的登录凭证"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询不到此用户"

        )

    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号被禁用, 请咨询相关客服申请解禁或者重新申请账号",
        )

    return user

#校验用户角色
def get_current_admin(current_user: User = Depends(get_current_user)) -> User:

    if current_user.role != 'admin':
        raise BusinessException(
            message="无权限访问",
            code=403
        )

    return current_user
