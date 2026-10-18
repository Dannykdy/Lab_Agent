"""-----------------异常处理器组件---------------------"""

from typing import Any
from pydantic import BaseModel

class Response(BaseModel):
    code: int
    message: str
    data: Any = None

    @classmethod
    def success(cls, message: str = "请求成功", data : Any = None):
        return cls(code = 200, message = message, data = data)

    @classmethod
    def error(cls, code : int = 500, message : str = "请求失败"):
        return cls(code = code, message = message)


class PageResponse(BaseModel):
    """分页的返回结果"""

    total: int = 0
    list: Any = []
