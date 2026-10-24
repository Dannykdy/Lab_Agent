from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.users import User
from app.schemas.ai import ChatRequest
from app.service import agent_service

router = APIRouter(prefix="/ai", tags=["AI相关的API"])


@router.post("/chat")
def chat(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """SSE 流式对话接口。

    把 agent_service 的生成器包装成 StreamingResponse：
    - media_type 必须是 text/event-stream，前端 fetch 才能按 SSE 逐帧读取；
    - Cache-Control: no-cache 防止中间层把整个流缓存起来；
    - X-Accel-Buffering: no 是给 nginx 看的，让代理不缓冲、收到一帧就转发一帧
      （当前 vite 代理不受影响，加上以防将来部署到 nginx 后面）。
    """
    return StreamingResponse(
        agent_service.stream_agent(db, current_user, data),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
