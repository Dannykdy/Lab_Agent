from sqlalchemy.orm import Session
import asyncio
from datetime import datetime

from app.database import SessionLocal

from app.models.users import User
from app.models.lab import Lab
from app.models.equipment import Equipment
from app.models.reservation import Reservation

from app.common.exceptions import BusinessException
from app.common.response import PageResponse
from app.schemas.reservation import ReservationCreateRequest, ReservationResponse


"""创造预约记录"""
def create_reservation(db: Session, current_user: User, data: ReservationCreateRequest):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")

    if data.date < current_date:
        raise BusinessException(message="不能预约过期时间")
    if data.end_time < data.start_time:
        raise BusinessException(message="结束预约时间不得小于开始预约时间")
    if data.date == current_date and data.start_time < current_time:
        raise BusinessException(message="不能预约过期时间")

    lab = db.query(Lab).filter(Lab.id == data.lab_id).first()
    if not lab:
        raise BusinessException(message="预约实验室不存在，请检查！")

    if lab.status != 1 :
        raise BusinessException(message="该实验室正在维修，请稍后预约！")

    if lab.open_time and data.start_time < lab.open_time:
        raise BusinessException(message="预约时间不得早于实验室开馆时间")
    if lab.close_time and data.end_time > lab.close_time:
        raise BusinessException(message="预约时间不得晚于实验室闭馆时间")

    # equipment_id 不为空 则表示这次是预约的实验室设备
    if data.equipment_id:
        equipment = (
            db.query(Equipment).filter(Equipment.id == data.equipment_id).first()
        )
        if not equipment:
            raise BusinessException(message="实验室设备不存在")
        if equipment.status != 1:
            raise BusinessException(message="实验室设备正在维护")
        if equipment.lab_id != data.lab_id:
            raise BusinessException(message="该设备不属于该实验室，请检查！")

    query = db.query(Reservation).filter(
        Reservation.lab_id == data.lab_id,
        Reservation.date == data.date,
        Reservation.start_time < data.end_time,
        Reservation.end_time > data.start_time,
        Reservation.status.in_([0, 1]),  # 0表示待审核  1已通过
    )
    if data.equipment_id:
        query = query.filter(
            Reservation.equipment_id == data.equipment_id
        )  # 预约实验室设备
    else:
        query = query.filter(Reservation.equipment_id.is_(None))  # 只预约实验室

    res = query.first()

    if res:
        raise BusinessException(message="该时段已被预约")

    resvervation_model = Reservation(
        user_id=current_user.id,
        lab_id=data.lab_id,
        equipment_id=data.equipment_id,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
        remark=data.remark,
        status=0,
    )
    db.add(resvervation_model)
    db.commit()


"""查询预约的记录"""
def get_reservation_page_list(
    db: Session,
    current_user: User,
    page: int,
    page_size: int,
    status: int | None = None,
):

    query = db.query(Reservation)
    if current_user.role != "admin":  #学生只显示自己
        query = query.filter(Reservation.user_id == current_user.id)
    if status is not None:  # 此时如果跳过if将代表管理员 显示全部预约
        query = query.filter(Reservation.status == status)
    total = query.count()
    items = (
        query.order_by(Reservation.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    result = []
    for item in items:
        res = ReservationResponse.model_validate(item)
        res.user_name = item.user.name if item.user else None
        res.lab_name = item.lab.name if item.lab else None
        res.equipment_name = item.equipment.name if item.equipment else None
        res.type = "设备" if item.equipment_id else "实验室"
        result.append(res)

    return PageResponse(list=result, total=total)


"""学生取消预约"""
def cancel_reservation(db: Session, current_user: User, reservation_id: int):

    item = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not item:
        raise BusinessException(message="预约记录不存在")
    if item.user_id != current_user.id:
        raise BusinessException(message="无此权限", code=403)
    if item.status not in [0, 1]:
        raise BusinessException(message="当前状态无法取消")
    item.status = 3
    db.commit()


"""管理员审核预约"""
def audit_reservation(db: Session, reservation_id: int, status: int):

    if status not in [1, 2]:
        raise BusinessException(message="审核状态错误")
    item = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not item:
        raise BusinessException(message="预约记录不存在")
    if item.status != 0:
        raise BusinessException(message="当前状态不支持审核")
    item.status = status
    db.commit()


""" 删除已取消的预约单 """
def expire_panding_reservation():
    db = SessionLocal()
   
    try:
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")
        items = db.query(Reservation).filter(Reservation.status).all()
        changed = False
        for item in items:
            if item.date < current_date or (item.date == current_date and item.end_time < current_time):
                item.status = 3
                changed = True
        if changed:
            db.commit()
    finally:
        db.close()
"""轮训检查"""

async def run_expire_scan():
    while True:
        expire_panding_reservation()

        await asyncio.sleep(60)
