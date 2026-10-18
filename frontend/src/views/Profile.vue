<template>
  <div class="profile-page">
    <!--卡片式布局:常规系统页面风格-->
    <el-card class="profile-card" shadow="hover">
      <template #header>
        <span class="card-title">个人信息</span>
      </template>

      <!--表单提交布局:字段顺序为 头像 / 账号 / 名称 / 角色 / 邮箱 / 手机号-->
      <el-form
        ref="formRef"
        :rules="rules"
        :model="form"
        label-position="right"
        label-width="80px"
        class="profile-form"
      >
        <!--头像:选择图片后仅本地预览,上传逻辑待后端接口接入
            注意:该表单项不显示"头像"标签文字,仅居中展示头像本体-->
        <el-form-item class="avatar-item" label-width="0">
          <el-upload
            class="avatar-uploader"
            accept="image/*"
            :show-file-list="false"
            :auto-upload="false"
            :on-change="handleAvatarChange"
            :http-request="handleFileUpload"
          >
            <!--内层容器改为纵向排列,保证提示文字居中显示在头像正下方-->
            <div class="upload-inner">
              <el-avatar :size="90" :src="avatarUrl" class="avatar-box">
                <!--无头像时显示默认图标占位-->
                <el-icon :size="40"><UserFilled /></el-icon>
              </el-avatar>
              <div class="avatar-tip">点击更换头像</div>
            </div>
          </el-upload>
        </el-form-item>

        <!--账号:如后端不允许修改账号,可在此处加 disabled-->
        <el-form-item label="账号" prop="username">
          <el-input disabled v-model="form.username" placeholder="请输入账号" :prefix-icon="User" />
        </el-form-item>

        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" :prefix-icon="UserFilled" />
        </el-form-item>

        <!--角色下拉框:选项值 student / admin 为占位,按后端约定调整即可-->
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色" style="width: 100%" disabled>
            <el-option label="学生" value="student" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" :prefix-icon="Promotion" />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号码" :prefix-icon="Iphone" />
        </el-form-item>

        <!--操作按钮区-->
        <el-form-item>
          <el-button type="default" @click="resetForm">重置</el-button>
          <el-button type="primary" @click="submit" :loading="loadingValue">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { User, UserFilled, Iphone, Promotion } from '@element-plus/icons-vue'
import { reactive, ref, onMounted } from 'vue'
import router from '@/router'
import { ElMessage } from 'element-plus'
import { useUser } from '@/utils/user'
import { getUserInfoApi, updateUserInfoApi } from '@/api/user.js'
import { uploadFileApi } from '@/api/file.js'

// ============================================================================
// 【后端接口接入区】
// 接口已定义在 src/api/user.js(返回结构 { code, data },code === 200 表示成功):
//   getUserInfoApi()  获取用户信息
//   updateApi(data)   更改用户信息
// 后续接入后端时,只需在下方两处 TODO 位置补上接口调用,其余逻辑无需改动:
//   1. onMounted 中调用 getUserInfoApi() 拉取最新用户信息
//   2. submit 中调用 updateApi(form) 提交修改
// 调用方式与 Login.vue / Register.vue 一致,本地缓存操作统一走 useUser()
// ============================================================================

const { userInfo, updateUser } = useUser()

// 调用表单的方法
const formRef = ref()

// 控制保存按钮旋转
const loadingValue = ref(false)

// 头像地址(优先展示缓存中的旧头像)
const avatarUrl = ref('')

// 表单数据(字段与后端约定:avatar / username / name / role / email / phone)
const form = reactive({
  avatar: '',
  username: '',
  name: '',
  role: '',
  email: '',
  phone: ''
})

// 表单校验规则
const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号码格式不正确', trigger: 'blur' }
  ]
}

// 从本地缓存填充表单(页面加载与重置按钮共用)

const fillFormFromCache = () => {
  if (userInfo.value) {
    form.username = userInfo.value.username || ''
    form.name = userInfo.value.name || ''
    form.role = userInfo.value.role || ''
    form.email = userInfo.value.email || ''
    form.phone = userInfo.value.phone || ''
    form.avatar = userInfo.value.avatar || ''
    avatarUrl.value = userInfo.value.avatar || ''
  }
}

// 页面加载时,先把本地缓存中的用户信息填充进表单
onMounted(async () => {
  fillFormFromCache()

  // TODO:【后端接口接入】拉取最新用户信息,成功后覆盖本地缓存
  const res = await getUserInfoApi()
  if (res.code === 200) {
    updateUser(res.data) // 写入本地缓存
    fillFormFromCache() // 重新填充表单
  }
})

// 选择新头像:先在本地预览,再立刻上传到后端(真正的头像上传)
const handleAvatarChange = async (uploadFile) => {
  // 释放上一次生成的本地预览地址,避免内存泄漏
  if (avatarUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(avatarUrl.value)
  }
  // 生成本地预览地址,让头像马上显示出来(不用等上传结果)
  avatarUrl.value = URL.createObjectURL(uploadFile.raw)

  // 【真正的头像上传】uploadFile.raw 才是真正的图片文件
  // 调用 src/api/file.js 里的 uploadFileApi,把文件交给后端保存
  try {
    const res = await uploadFileApi(uploadFile.raw)
    if (res.code === 200) {
      // 上传成功:后端返回的 res.data.url 是图片在服务器上的地址(形如 /uploads/xxx.png)
      // 把地址存进 form.avatar,点击"保存修改"时会随表单一起发给后端存进用户信息
      form.avatar = res.data.url
      ElMessage.success('头像上传成功')
    }
    // 上传失败(res.code 不是 200)时,request.js 拦截器已经弹过错误提示,这里不用重复弹
  } catch {
    // 网络异常等意外情况,拦截器同样已经提示过,这里什么都不用做
  }
}

// 重置表单:重新从本地缓存读取并清除校验状态
const resetForm = () => {
  // 释放未保存的本地预览地址
  if (avatarUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(avatarUrl.value)
  }
  fillFormFromCache()
  formRef.value?.clearValidate()
}

// 提交修改
const submit = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return // 校验失败,退出
  }

  loadingValue.value = true
  try {
    // TODO:【后端接口接入】调用 src/api/user.js 中的 updateUserInfoApi 提交修改
    const res = await updateUserInfoApi(form)
    if (res.code === 200) {
      updateUser(res.data) // 把最新用户信息同步到本地缓存(带API的是发后端 不带是更新本地缓存)
      ElMessage.success('保存成功')
    }

    // 仅把文本字段写回本地缓存,头像文件对象不写入 localStorage
  } finally {
    loadingValue.value = false
    await router.push('/manager/home')
  }
}
</script>

<style scoped>
/* 页面整体背景:常规系统的浅灰底色 */
.profile-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 24px;
  box-sizing: border-box;
}

/* 个人信息卡片:居中、限宽 */
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

/* 头像上传区样式 */
/* 直接让表单项的内容区水平居中,确保头像整体不靠左 */
.avatar-item :deep(.el-form-item__content) {
  justify-content: center;
}
/* 内层纵向排列容器:保证提示文字居中显示在头像正下方 */
.upload-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.avatar-box {
  cursor: pointer;
  border: 2px solid #dcdfe6;
  transition: border-color 0.2s; /* 悬浮时高亮描边 */
}
.avatar-box:hover {
  border-color: #409eff;
}
.avatar-tip {
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
  cursor: pointer;
}

/* 表单样式:居中、限宽 */
.profile-form {
  max-width: 400px;
  margin: 0 auto;
}
</style>
