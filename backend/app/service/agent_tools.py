from datetime import datetime
import json
from sqlalchemy.orm import Session
from langchain_core.tools import tool

from app.common.exceptions import BusinessException
from app.models.reservation import Reservation
from app.models.users import User
from app.service import equipment_service, kb_service, lab_service, reservation_service


def build_tools(db: Session, current_user: User):

    @tool
    def search_lab_docs(query: str) -> str:
        """根据用户的提问检索知识库"""
        try:
            return kb_service.search(query) or "没有检索到相关的资料"
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)

    @tool
    def list_open_labs(keywords: str = "") -> str:
        """查询开放的实验室列表"""
        try:
            keywords = keywords.strip() or None
            page = lab_service.get_lab_page_list(
                db, page=1, page_size=10, keywords=keywords, status=1
            )
            rows = [
                {
                    "id": item.id,
                    "name": item.name,
                    "location": item.location,
                    "capacity": item.capacity,
                    "open_time": item.open_time,
                    "close_time": item.close_time,
                }
                for item in page.list
            ]
            return json.dumps({"total": page.total, "labs": rows}, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)

    @tool
    def list_lab_equipments(lab_id: int, keywords: str = "") -> str:
        """查询某个实验室的设备列表"""
        try:
            keywords = keywords.strip() or None
            page = equipment_service.get_equipment_page_list(
                db, page=1, page_size=10, lab_id=int(lab_id), keywords=keywords
            )
            rows = [
                {
                    "id": item.id,
                    "name": item.name,
                    "lab_id": item.lab_id,
                    "lab_name": item.lab_name,
                    "sepc": item.spec,
                    "quantity": item.quantity,
                    "status": item.status,
                }
                for item in page.list
            ]
            return json.dumps(
                {"total": page.total, "equipments": rows}, ensure_ascii=False
            )
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)

    @tool
    def create_lab_reservation(
        lab_id: int,
        date: str,
        start_time: str,
        end_time: str,
        equipment_id: int | None = None,
        remark: str | None = None,
    ) -> str:
        """创建预约单预约实验室或设备"""
        try:
            data = Reservation(
                lab_id=lab_id,
                equipment_id=equipment_id,
                date=date,
                start_time=start_time,
                end_time=end_time,
                remark=remark,
            )
            reservation_service.create_reservation(db, current_user, data)
            return json.dumps(
                {
                    "ok": True,
                    "message": "预约已提交，请等待管理员审核",
                    "lab_id": lab_id,
                    "equipment_id": equipment_id,
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                },
                ensure_ascii=False,
            )
        except BusinessException as exc:
            return json.dumps({"ok": False, "error": exc.message}, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)

    @tool
    def list_my_reservations(status: int | None = None):
        """查询当前用户的预约记录，返回预约ID、实验室/设备、日期、时段、状态。
        取消预约前必须先调用它找到目标预约的【预约ID】。
        status 可选：0待审核 1已通过 2已拒绝 3已取消，不传则查全部。"""
        try:
            page = reservation_service.get_reservation_page_list(
                db, current_user, page=1, page_size=50, status=status
            )
            if not page.list:
                return "你当前没有任何预约记录。"
            lines = []

            for r in page.list:
                target = r.lab_name or r.equipment_name or "未知"
                lines.append(
                    f"预约ID:{r.id} | 类型:{r.type} | {target} | "
                    f"日期:{r.date} | {r.start_time}-{r.end_time} | 状态:{r.status}"
                )
            return "\n".join(lines)
        except Exception as e:
            return f"查询预约失败：{type(e).__name__}: {e}"

    @tool
    def cancel_reservation(reservation_id: int):
        """根据【预约ID】取消预约。reservation_id 是预约记录的唯一编号，
        不是实验室ID。如果不确定，请先调用 list_my_reservations 查询。"""
        try:
            reservation_service.cancel_reservation(db, current_user, reservation_id)
            return f"预约取消成功，预约ID：{reservation_id}"
        except BusinessException as exc:
            return f"取消预约失败：{exc.message}"

    @tool
    def get_today() -> str:
        """获取服务器当前的日期  2026-09-20"""
        now = datetime.now()
        return now.strftime("%Y-%m-%d")

    return [
        search_lab_docs,
        list_open_labs,
        list_lab_equipments,
        create_lab_reservation,
        list_my_reservations,
        cancel_reservation,
        get_today,
    ]
