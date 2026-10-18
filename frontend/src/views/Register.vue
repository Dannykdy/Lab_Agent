<template>
  <div class="register-container">
    <div class="register-box">
      <h3 style="font-size: 25px">欢迎注册实验室预约系统</h3>

      <!--表单提交布局-->
      <el-form
        ref="formRef"
        :rules="rules"
        :model="form"
        label-width="0px"
        style="width: 100%; margin-top: 20px"
      >
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
        <el-form-item prop="confirmpassword">
          <el-input
            size="large"
            v-model="form.confirmpassword"
            placeholder="请再次确认密码"
            :prefix-icon="Lock"
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item prop="name">
          <el-input
            size="large"
            v-model="form.name"
            placeholder="请输入姓名"
            :prefix-icon="UserFilled"
          />
        </el-form-item>
        <el-form-item prop="phone">
          <el-input
            size="large"
            v-model="form.phone"
            placeholder="请输入手机号码"
            :prefix-icon="Iphone"
          />
        </el-form-item>
        <el-form-item prop="email">
          <el-input
            size="large"
            v-model="form.email"
            placeholder="请输入邮箱"
            :prefix-icon="Promotion"
          />
        </el-form-item>
        <el-button style="width: 100%" type="success" @click="register" :loading="loadingValue"
          >注册</el-button
        >
        <div style="text-align: right; font-size: small; padding: 10px; color: #808080">
          已有账号？点击
          <router-link to="/login" style="color: #409eff">登陆</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { User, Lock, Iphone, Promotion, UserFilled } from '@element-plus/icons-vue'
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { registerApi } from '@/api/auth'
import router from '@/router'

const loadingValue = ref(false)
const formRef = ref()

const form = reactive({
  username: '',
  password: '',
  confirmpassword: '',
  name: '',
  phone: '',
  email: ''
})

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请确认密码'))
  } else {
    if (value !== form.password) {
      callback(new Error('两次密码输入不一致'))
    } else {
      callback()
    }
  }
}

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirmpassword: [{ validator: validatePass, trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号码', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱地址', trigger: 'blur' }]
}

const register = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return // 校验失败,退出
  }
  loadingValue.value = true
  try {
    const res = await registerApi(form)
    if (res.code === 200) {
      ElMessage.success('注册成功')
      await router.push('/login')
    }
  } finally {
    loadingValue.value = false
  }
}
</script>

<style scoped>
.register-container {
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
.register-box {
  width: 380px;
  border-radius: 25px;
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1);
  padding: 30px;
  text-align: center;
  background-color: #eef1d0b6;
}
</style>
