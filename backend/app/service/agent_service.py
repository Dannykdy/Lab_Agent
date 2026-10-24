import json
import traceback

from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, AIMessageChunk
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.common.exceptions import BusinessException
from app.models.users import User
from app.schemas.ai import ChatRequest
from app.service import agent_tools
from app.config import settings

SYSTEM_PROMPT = """你是智能实验室预约系统的 Agent，回答要简洁。
你可以：
1. 使用 search_lab_docs 查询实验室的规则、安全、开放时间等问题
2. 使用 list_open_labs / list_lab_equipments  查询真实的实验室和设备
3. 再用户进行了预约确认后，使用 create_lab_reservation 来进行真实的预约落库
4. 当用户查询自身预约的所有实验室清单时，使用list_my_reservations来进行真实的数据库查询
5. 当用户需要取消实验室预约时，使用cancel_reservation来进行取消预约
6. 使用 get_today 来进行日期的换算

## 必须遵守
当用户提到了 今天、明天、后天 等日期相关的问题，请先调用 get_today 来获取日期，**不要直接返回 我需要确定明天的具体日期**。

在提交预约之前必须向用户复述：实验室ID与名称（或设备ID和名称）、日期、开始时间、结束时间。并得到用户确认再进行实际操作。
用户没说【确认】【确认预约】【就这样预约】等确定性回复之前，不要调用 create_lab_reservation以及cancel_reservation。
工作流的确认环节里如果缺少了 lab_id，请先 list_open_labs 查到了 lab_id 再创建，不要瞎写。
工作流的确认环节里如果缺少了 equipment_id，请先 list_lab_equipments 查到了 equipment_id 再创建，不要瞎写。

预约成功后状态是待审核，必须管理员确认后实验室（或设备）才能使用。
不要瞎编数据库里没有的实验室或者设备信息。
如果是问开放时间或者实验室规则，优先调用 search_lab_docs，不要凭空回复。
"""


def build_agent(db: Session, current_user: User):
    """构建 LangGraph Agent（agent 节点 + tools 节点）"""
    tools = agent_tools.build_tools(db, current_user)
    llm = ChatOpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        model=settings.LLM_MODEL,
        temperature=0,
        # 底层 LLM 开流式：让大模型按 token 吐字。
        # 注意：这里开了只是"允许"流式，上层必须用 agent.stream() 去消费（见 stream_agent）；
        # 如果上层用 invoke()，会把所有 token 攒齐拼成完整消息才返回，等于白开。
        streaming=True,
    ).bind_tools(tools)

    def agent_node(state: MessagesState):
        """langGraph 执行的工作流 的节点"""
        response = llm.invoke(state["messages"])
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)  # 调用大模型的节点
    graph.add_node("tools", ToolNode(tools))  # tool call的节点
    graph.add_edge(START, "agent")  # 流程的起点，call LLM
    graph.add_conditional_edges(
        "agent", tools_condition
    )  # 看有无 tool_call  有就继续call  没有就END 输出
    graph.add_edge("tools", "agent")  # 让agent看tool调用的结果
    return graph.compile()


def _build_history(data: ChatRequest) -> list:
    """把前端传来的消息列表转成 LangChain 消息对象（只保留有内容的 user/assistant 消息）"""
    if not data.messages:
        raise BusinessException(message="对话内容为空")
    history = []
    for message in data.messages:
        if message.role == "user" and message.content.strip():
            history.append(HumanMessage(content=message.content.strip()))
        elif message.role == "assistant" and message.content.strip():
            history.append(AIMessage(content=message.content.strip()))
    if not history:
        raise BusinessException(message="请输入您要对话的内容")
    return history


def _sse(data: dict) -> str:
    """把一个 dict 包装成一条 SSE 事件帧。

    SSE 协议格式：每帧以 "data: " 开头，帧与帧之间用空行（\n\n）分隔。
    ensure_ascii=False 让中文直接明文传输，便于调试。
    """
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def _chunk_text(chunk) -> str:
    """从 LLM 输出的一个分片（AIMessageChunk）里取出纯文本。

    - 普通文本模型的 content 就是 str；
    - 多模态模型的 content 可能是 [{"text": "..."}] 列表，统一转成字符串；
    - 工具调用的分片 content 为空，返回 ""，由下游自然过滤掉。
    """
    if not isinstance(chunk, AIMessageChunk):
        return ""
    content = chunk.content
    if isinstance(content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    return content or ""


def stream_agent(db: Session, current_user: User, data: ChatRequest):
    """SSE 流式对话：边生成边把 token 推给前端，而不是等全部生成完一次性返回。

    为什么校验和建图放在生成器【外面】：
    - 这两步出错时 HTTP 响应还没开始，BusinessException 会被 FastAPI
      转成正常的 400 JSON 错误，前端能拿到明确报错；
    - 一旦 StreamingResponse 开始吐数据，状态码就是 200 了，
      之后的错误只能包装成 {"type":"error"} 事件推进流里（见 event_stream 的 except）。

    另外 FastAPI 会等整个流结束后才执行 get_db 的收尾（关闭 db session），
    所以流式过程中 tools 访问数据库是安全的。
    """
    history = _build_history(data)
    agent = build_agent(db, current_user)

    def event_stream():
        """SSE 生成器：FastAPI 的 StreamingResponse 会逐个消费这里 yield 的帧"""
        try:
            # stream_mode="messages" 是 LangGraph 的 token 级流式：
            #   每生成一个 token，就 yield 一个 (消息分片, 元数据) 元组。
            # 对比其他粒度：
            #   stream_mode="updates" -> 每个节点跑完才吐一次（整段回答一起出）
            #   stream_mode="values"   -> 每次状态变化吐一次完整状态（最粗）
            for chunk, metadata in agent.stream(
                {"messages": [SystemMessage(content=SYSTEM_PROMPT), *history]},
                stream_mode="messages",
                config={"recursion_limit": 10},  # 设置对话循环的上限是10轮
            ):
                # 只转发 agent 节点吐出的 AI token。
                # tools 节点也会吐 ToolMessage（工具执行结果），不需要逐字推给用户。
                # 注：若某轮 agent 先说了话再调工具，那段话也会被流式转发
                #（类似 ChatGPT 展示思考过程）；不调工具的最终回答更是逐字转发。
                if metadata.get("langgraph_node") != "agent":
                    continue
                text = _chunk_text(chunk)
                if text:
                    # 每拿到一小段文字就立刻推给前端，前端拼起来形成打字机效果
                    yield _sse({"type": "token", "content": text})
            # 全部生成完毕，通知前端收尾
            yield _sse({"type": "done"})
        except Exception as e:
            # 流式进行到一半出错：HTTP 状态码已经发出去了（200），
            # 只能把错误包装成 SSE 事件通知前端，由前端弹提示。
            traceback.print_exc()
            yield _sse({"type": "error", "message": f"大模型调用失败: {type(e).__name__}: {e}"})

    return event_stream()
