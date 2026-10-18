from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.database import get_db
from app.common.response import Response
from app.models.users import User
from app.dependencies.auth import get_current_user, get_current_admin
from app.schemas.reservation import ReservationCreateRequest, AuditReservationRequest
from app.service import reservation_service


router = APIRouter(prefix="/reservation", tags=["预约相关接口"])


@router.post("")
def create_reservation(
    data: ReservationCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), 
):
    reservation_service.create_reservation(db, current_user, data)

    return Response.success(
        message="预约成功！"
    )


@router.get("/list")
def get_reservation_page_list(
    page: int = 1,
    page_size: int = 10,
    status: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    res = reservation_service.get_reservation_page_list(
        db, current_user, page, page_size, status
    )
    return Response.success(data=res)


@router.put("/{reservation_id}/cancel")
def cancel_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reservation_service.cancel_reservation(db, current_user, reservation_id)
    return Response.success()


@router.put("/{reservation_id}/audit")
def audit_reservation(
    reservation_id: int,
    data: AuditReservationRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    reservation_service.audit_reservation(db, reservation_id, data.status)
    return Response.success()
