from sqlalchemy.orm import Session
from operator import or_

from app.common.exceptions import BusinessException
from app.common.response import PageResponse
from app.models.lab import Lab

from app.schemas.lab import LabResponse, LabCreateRequest, LabUpdateRequest


# 管理员查看实验室列表
def get_lab_page_list(
    db: Session,
    page: int,
    page_size: int,
    keywords: str | None = None,
    status: int | None = None,
):
    query = db.query(Lab)

    # select * from lab where labname like '%物理实验室%' ;
    if keywords:
        query = query.filter(Lab.name.ilike(f"%{keywords}%"))

    total = query.count()

    """offset = 「从第几条之后开始取」.offset(10) 意思：跳过前面 10 条，从第 11 条开始。 limit = 「取多少条」"""

    items = (
        query.order_by(Lab.id.desc())  # ① 先排序
        .offset((page - 1) * page_size)  # ② 再跳过
        .limit(page_size)  # ③ 再取数
        .all()  # ④ 执行
    )

    return PageResponse(
        total=total, list=[LabResponse.model_validate(item) for item in items]
    )


# 用户获取实验室详情页
def get_lab(lab_id: int, db: Session):
    exist = db.query(Lab).filter(Lab.id == lab_id).first()
    if not exist:
        raise BusinessException(message="该实验室不存在, 请检查您要查询的实验室!")

    return LabResponse.model_validate(exist)


# 管理员创建实验室
def create_lab(db: Session, data: LabCreateRequest):

    exit = db.query(Lab).filter(data.name == Lab.name).first()
    if exit:
        raise BusinessException(message="该实验室已存在")
    lab = Lab(**data.model_dump())
    db.add(lab)
    db.commit()
    db.refresh(lab)

    return LabResponse.model_validate(lab)


# 管理员更新实验室
def update_lab(db: Session, lab_id: int, data: LabUpdateRequest):

    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab:
        raise BusinessException(message="实验室不存在")

    lab_dict = data.model_dump(exclude_none=True)

    for filed, value in lab_dict.items():
        setattr(lab, filed, value)

    db.commit()
    db.refresh(lab)
    return LabResponse.model_validate(lab)


# 管路员删除实验室
def delete_lab(db: Session, lab_id: int):

    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab:
        raise BusinessException(message="实验室不存在")
    db.delete(lab)
    db.commit()
