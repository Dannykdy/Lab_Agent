from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from app.database import Base

class Lab(Base):
    __tablename__ = 'labs'
    __table_args__ = {"comment": "实验室列表"}

    name: Mapped[str] = mapped_column(String(50), comment="实验室名称", nullable=False)
    description: Mapped[str] = mapped_column(String(500), comment="简介")
    img: Mapped[str] = mapped_column(String(200),default='', comment="实验室图片")
    location: Mapped[str] = mapped_column(String(100), comment="位置")
    capacity: Mapped[int] = mapped_column(Integer, comment="容量", default=0)
    open_time: Mapped[str] = mapped_column(String(20), comment="开放时间")
    close_time: Mapped[str] = mapped_column(String(20), comment="闭馆时间")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态: 0-禁用, 1-正常")
