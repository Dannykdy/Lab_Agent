"""-----------------全局异常处理器---------------------"""
from fastapi import FastAPI
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


from app.common.response import Response
class BusinessException(Exception):
    def __init__(self, message: str, code:int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


async def business_exception_handler(request: Request, exc :BusinessException):
    # 自定义业务逻辑异常处理
    # 返回200代表程序跑通，content内显示具体逻辑错误码
    return JSONResponse(
        status_code=200,
        content=Response.error(code=exc.code, message=exc.message).model_dump(),
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    # Http异常异常处理
    return JSONResponse(
        status_code=exc.status_code,
        content=Response.error(code=exc.status_code, message=exc.detail).model_dump(),
    )


async def validation_exception_handler(request: Request, exc:RequestValidationError):
    """参数异常处理器(用户传参的时候错误)"""
    return JSONResponse(
        status_code=422,
        content=Response.error(code=422, message="请求参数错误(传参错误)").model_dump(),
    )


async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    return JSONResponse(
        status_code=500,
        content=Response.error(code=500, message="服务器内部错误").model_dump(),
    )


# 精简main.py文件，此处完成注册，在主页面完成调用
def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(BusinessException, business_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
