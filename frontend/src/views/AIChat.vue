<template>
  <div>
    <el-card>
      <template #header>
        <div style="font-size: 16px; font-weight: bold">
          <span>AI智能助手</span>
        </div>
      </template>

      <!-----------------------------------------------聊天框----------------------------------->
      <div
        ref="listRef"
        style="
          height: 480px;
          overflow-y: auto;
          padding: 8px 4px;
          background-color: #fafafa;
          border-radius: 6px;
        "
      >
        <div
          v-for="(item, index) in messages"
          :key="index"
          :style="{
            display: 'flex',
            alignItems: 'flex-start', // 头像与气泡顶部对齐，多行消息时头像不跟着拉伸
            justifyContent: item.role === 'user' ? 'flex-end' : 'flex-start',
            marginBottom: '12px'
          }"
        >
          <!-- AI 机器人头像：AI 消息显示在气泡左侧 -->
          <div
            v-if="item.role === 'assistant'"
            :style="{
              width: '36px',
              height: '36px',
              marginRight: '8px',
              flexShrink: 0,
              borderRadius: '50%',
              backgroundColor: '#ecf5ff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '20px',
              border: '1px solid #d9ecff'
            }"
          >
            🤖
          </div>

          <div
            :style="{
              maxWidth: '70%',
              padding: '10px 12px',
              borderRadius: '10px',
              backgroundColor: item.role === 'user' ? '#409eff' : '#fff',
              color: item.role === 'user' ? '#fff' : '#333',
              lineHeight: '1.6',
              boxShadow: '0 1px 2px rgba(0, 0, 0, 0.06)'
            }"
            v-html="parseMarkdown(item.content)"
          ></div>

          <!-- 用户自己的头像：用户消息显示在气泡右侧；
               未设置头像时 el-avatar 自动回退显示姓名首字 -->
          <el-avatar
            v-if="item.role === 'user'"
            :size="36"
            :src="userInfo?.avatar"
            :style="{ marginLeft: '8px', flexShrink: 0 }"
          >
            {{ (userInfo?.name || '我')[0] }}
          </el-avatar>
        </div>
      </div>
      <!-----------------------------------------------聊天框----------------------------------->

      <!-----------------------------------------------输入框----------------------------------->
      <div style="margin-top: 12px; display: flex; gap: 8px; align-items: flex-end">
        <el-input
          v-model="input"
          type="textarea"
          :rows="2"
          placeholder="问问实验室怎么预约、开放时间..."
          @keydown.enter.exact.prevent="handleSend"
          @keydown.enter.shift.stop
        ></el-input>
        <el-button type="primary" @click="handleSend" :loading="loading">发送</el-button>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import { chatStreamApi } from '@/api/ai'
import { ref, nextTick, reactive } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify' // 过滤危险的 HTML，防止 XSS 攻击
import { ElMessage } from 'element-plus'
import { useUser } from '@/utils/user'

// 当前登录用户信息（响应式），用于展示用户自己的头像
const { userInfo } = useUser()

const messages = ref([
  {
    role: 'assistant',
    content:
      '你好，我是实验室助手。可以问我怎么预约、开放时间、安全规范。现在哪些实验室能约，请到「实验室列表」查看。'
  }
])
const input = ref('')
const loading = ref(false)
const listRef = ref()

//自动滚动效果
const scrollToBottom = () => {
  nextTick(() => {
    const elem = listRef.value
    if (elem) elem.scrollTop = elem.scrollHeight
  })
}

const handleSend = async () => {
  const text = input.value.trim()
  if (!text || loading.value) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true
  scrollToBottom()

  // 历史消息要在插入占位气泡【之前】取，避免把空气泡也发给后端
  const history = messages.value.filter(
    (item) => item.role === 'user' || item.role === 'assistant'
  )

  // 用 reactive 创建占位气泡：流式期间要频繁修改它的 content，
  // 只有响应式代理被修改时 Vue 才会刷新界面（直接改普通对象不会触发更新）
  const assistantMsg = reactive({ role: 'assistant', content: '' })
  messages.value.push(assistantMsg)
  scrollToBottom()

  try {
    // 流式请求：后端每吐一个 token 就回调一次，追加到占位气泡形成打字机效果
    await chatStreamApi({ messages: history }, (event) => {
      if (event.type === 'token') {
        assistantMsg.content += event.content
      } else if (event.type === 'error') {
        // 生成中途出错：此时 HTTP 已是 200，后端只能通过 SSE 事件传错误
        ElMessage.error(event.message)
      }
      // type === 'done' 时后端会主动关闭连接，读取循环自然结束，无需处理
      scrollToBottom()
    })
  } catch (e) {
    // 网络错误/超时/401 的提示已在 chatStreamApi 里弹过，这里只需清理界面
  } finally {
    loading.value = false
    if (!assistantMsg.content) {
      // 没有任何内容产出（出错或空回复），把占位的空气泡移除
      const index = messages.value.indexOf(assistantMsg)
      if (index !== -1) messages.value.splice(index, 1)
    }
    scrollToBottom()
  }
}

// 将 markdown 字符串转换为安全的 HTML 字符串
const parseMarkdown = (text) => {
  if (!text) return ''
  marked.setOptions({ breaks: true }) // 把 \n 转换成 <br>
  // 使用 marked 解析，然后用 DOMPurify 清理
  const rawHtml = marked.parse(text)
  return DOMPurify.sanitize(rawHtml)
}
</script>
