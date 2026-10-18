from pydantic import BaseModel, ConfigDict


# 成功后拿到用户所有信息
class LabResponse(BaseModel):
    """返回实验室信息的参数列表"""

    id: int
    name: str
    description: str | None = None
    img: str | None = None
    location: str | None = None
    capacity: int
    open_time: str | None = None
    close_time: str | None = None
    status: int

    model_config = ConfigDict(from_attributes=True)


class LabUpdateRequest(BaseModel):
    """更新实验室信息"""

    name: str | None = None
    description: str | None = None
    img: str | None = None
    location: str | None = None
    capacity: int | None = None
    open_time: str | None = None
    close_time: str | None = None
    status: int | None = None


class LabCreateRequest(BaseModel):
    """管理员创建实验室的请求参数"""

    name: str | None = None
    description: str | None = None
    img: str | None = None
    location: str | None = None
    capacity: int = 0
    open_time: str | None = None
    close_time: str | None = None
    status: int = 1
