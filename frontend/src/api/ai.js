import { getToken, logout } from '@/utils/auth'
import { ElMessage } from 'element-plus'
import router from '@/router'

/*
 * AI 流式对话（SSE）。
 *
 * 为什么不用 axios：axios 在浏览器端拿不到"边接收边读取"的响应体，
 * 必须等全部数据返回后才能处理，无法实现打字机效果。
 * 所以流式请求用原生 fetch + ReadableStream 实现。
 *
 * 参数：
 *   data    请求体，形如 { messages: [...] }
 *   onEvent 每收到后端一条 SSE 事件就回调一次，事件形如：
 *           { type: 'token', content: '...' }  一段回答文字（逐字追加即可）
 *           { type: 'done' }                   回答结束（后端随后关闭连接）
 *           { type: 'error', message: '...' }  后端生成中途出错
 * 返回 Promise：流正常结束后 resolve；出错（网络/超时/401）时 reject，
 *             此时错误提示已经弹过，调用方只需清理界面。
 */
export async function chatStreamApi(data, onEvent) {
  const baseURL = import.meta.env.VITE_API_BASE_URL || ''

  // 120 秒兜底超时：大模型偶尔会卡住，超时主动断开，避免页面永远转圈
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 120000)

  try {
    const res = await fetch(`${baseURL}/api/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // fetch 不走 axios 拦截器，token 需要手动带上
        Authorization: `Bearer ${getToken()}`
      },
      body: JSON.stringify(data),
      signal: controller.signal
    })

    // 非 200：说明后端在流式开始【之前】就拒绝了（未登录、参数错误等），body 是普通 JSON
    if (!res.ok) {
      if (res.status === 401) {
        ElMessage.error('登录状态已失效，请重新登录')
        logout()
        router.push('/login')
        throw new Error('登录状态已失效')
      }
      const err = await res.json().catch(() => ({}))
      ElMessage.error(err.message || err.detail || '请求失败')
      throw new Error(err.message || err.detail || '请求失败')
    }

    // 200：body 是一条 SSE 流，逐段读取
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = '' // 暂存没读完的字节：网络分包可能把一条事件截成两半，需要拼接

    // 从 buffer 里拆出完整的事件帧（以 \n\n 分隔）逐个处理
    const consumeBuffer = () => {
      const frames = buffer.split('\n\n')
      buffer = frames.pop() // 最后一段可能不完整，留到下一批数据继续拼
      for (const frame of frames) {
        // 取出帧里的 data: 行内容（去掉前缀后拼接就是 JSON 字符串）
        let dataStr = ''
        for (const line of frame.split('\n')) {
          if (line.startsWith('data:')) dataStr += line.slice(5).trim()
        }
        if (!dataStr) continue // 空帧/注释帧，忽略
        onEvent(JSON.parse(dataStr))
      }
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) break // 后端关闭连接，流结束
      // stream: true 防止一个多字节汉字被切成两半导致乱码，最后再 flush 一次
      buffer += decoder.decode(value, { stream: true })
      consumeBuffer()
    }
    buffer += decoder.decode() // 冲刷解码器里残留的字节
    consumeBuffer()
  } catch (e) {
    // AbortError 是 120 秒超时主动断开导致的；其他错误（401/网络）上面已各自提示过
    if (e.name === 'AbortError') {
      ElMessage.error('响应超时，请重试')
    }
    throw e // 抛给调用方，让它清理界面上的占位气泡
  } finally {
    clearTimeout(timer)
  }
}
