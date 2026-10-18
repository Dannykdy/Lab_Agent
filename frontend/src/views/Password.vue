<template>
  <div class="profile-page">
    <!--卡片式布局:常规系统页面风格-->
    <el-card class="profile-card" shadow="hover">
      <template #header>
        <span class="card-title">修改密码</span>
      </template>
      <el-form
        ref="formRef"
        :rules="rules"
        :model="form"
        label-position="right"
        label-width="80px"
        class="profile-form"
      >
        <el-form-item label="原密码" prop="oldPassword">
          <el-input
            v-model="form.oldPassword"
            type="password"
            show-password
            placeholder="请输入原密码"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="form.newPassword"
            type="password"
            show-password
            placeholder="请输入新密码"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmpassword">
          <el-input
            v-model="form.confirmpassword"
            type="password"
            show-password
            placeholder="二次确认密码"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">确认修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { updatePasswordApi } from '@/api/user'
import { logout } from '@/utils/auth'
import router from '@/router'

const formRef = ref()
const submitting = ref(false)
const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmpassword: ''
})

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请确认密码'))
  } else {
    if (value !== form.newPassword) {
      callback(new Error('两次密码输入不一致'))
    } else {
      callback()
    }
  }
}

const rules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [{ required: true, message: '请输入新密码', trigger: 'blur' }],
  confirmpassword: [{ validator: validatePass, trigger: 'blur' }]
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const res = await updatePasswordApi({
      old_password: form.oldPassword,
      new_password: form.newPassword
    })
    if (res.code === 200) {
      ElMessage.success('密码修改成功，请重新登录')
      logout()
      await router.push('/login')
    }
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
/* 页面整体背景:常规系统的浅灰底色(与修改个人信息页面保持一致) */
.profile-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 24px;
  box-sizing: border-box;
}

/* 密码卡片:居中、限宽 */
.profile-card {
  max-width: 560px;
  margin: 0 auto;
  border-radius: 5%;
}
.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 表单样式:居中、限宽 */
.profile-form {
  max-width: 400px;
  margin: 0 auto;
}
</style>
