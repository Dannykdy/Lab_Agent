"""加密密码文件"""

import bcrypt


def hash_password(password: str):

    return bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    """验证密码的有效性"""
    """  "123" -> "xxsdasdasdasfa"  """
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    
