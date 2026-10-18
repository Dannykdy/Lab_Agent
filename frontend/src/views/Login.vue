<template>
  <div class="login-container">
    <div class="login-box">
      <h1 style="font-size: 28px">实验室预约系统登录</h1>
      <div style="margin-top: 5px; margin-bottom: 30px">基于Agent智能预约系统</div>

      <!--表单提交布局-->
      <el-form ref="formRef" :rules="rules" :model="form" label-width="0px" style="width: 100%">
        <el-form-item prop="username">
          <el-input
            size="large"
            v-model="form.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            size="large"
            v-model="form.password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            type="password"
            show-password
          />
        </el-form-item>
        <el-button style="width: 100%" type="success" @click="login" :loading="loadingValue">
          登 陆
        </el-button>
        <div style="text-align: right; font-size: small; padding: 10px; color: #808080">
          还没有账号？点击
          <router-link to="/register" style="color: #409eff">注册</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { User, Lock } from '@element-plus/icons-vue'
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { loginApi } from '@/api/auth'
import { useUser } from '@/utils/user'

const { saveLoginData } = useUser()

//调用表单的方法
const formRef = ref()

//控制登录按钮旋转
const loadingValue = ref(false)

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const form = reactive({
  username: '',
  password: ''
})

const login = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return // 校验失败,退出
  }

  loadingValue.value = true
  try {
    const res = await loginApi(form)
    if (res.code === 200) {
      saveLoginData(res.data)
      ElMessage.success('登陆成功!')
      await router.push('/manager/home')
    } else {
      router.push('/login')
    }
  } finally {
    loadingValue.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;

  /* ★ 背景图铺满整屏 ★ */
  background-image: url('@/assets/img/login-bg01.jpg');
  background-size: cover; /* 铺满，保持比例，可能裁剪 */
  background-position: center; /* 居中显示 */
  background-repeat: no-repeat; /* 不重复 */
  background-attachment: fixed; /* 可选：滚动时固定 */
}
.login-box {
  width: 380px;
  border-radius: 25px;
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1);
  padding: 30px;
  text-align: center;
  background-color: #eef1d0b6;
}
</style>
