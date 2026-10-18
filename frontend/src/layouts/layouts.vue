<template>
  <div class="common-layout">
    <el-container style="min-height: 100vh">
      <!--标题头部设置-->
      <el-header
        style="
          display: flex;
          align-items: center;
          border-bottom: 2px solid #ddd;
          background-color: #fff;
        "
      >
        <div
          style="flex: 1; display: flex; align-items: center; font-size: 24px; font-weight: bolder"
        >
          <img style="width: 40px" src="@/assets/img/logo.png" alt="" />
          <div style="margin: 5px">智能实验室预约系统</div>
        </div>
        <div>
          <el-dropdown>
            <div style="display: flex; align-items: center; cursor: pointer">
              <img style="width: 40px; border-radius: 50%" :src="userInfo?.avatar" />
              <div style="margin: 20px">{{ userInfo.name }}</div>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleprofile">个人信息</el-dropdown-item>
                <el-dropdown-item @click="handlepassword">修改密码</el-dropdown-item>
                <el-dropdown-item divided @click="handlelogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <!--侧边栏设置-->
      <el-container>
        <el-aside width="220px">
          <el-menu
            router
            :default-active="router.currentRoute.value.path"
            style="height: 100%"
            default-active="/manager/home"
          >
            <!---------------------------------------------1----------------------------------------->
            <el-menu-item index="/manager/home">
              <el-icon><icon-menu /></el-icon><!--图标-->
              <span>系统首页</span>
            </el-menu-item>
            <!---------------------------------------------2----------------------------------------->
            <el-menu-item v-if="userInfo?.role === 'student'" index="/manager/lablist">
              <el-icon><List /></el-icon>
              <span>实验室列表</span>
            </el-menu-item>
            <!---------------------------------------------3----------------------------------------->
            <el-menu-item index="/manager/user-reservation" v-if="userInfo?.role === 'student'">
              <el-icon><Notebook /></el-icon>
              <span>我的预约</span>
            </el-menu-item>

            <!---------------------------------------------4------------------------------------------>
            <el-menu-item v-if="userInfo?.role === 'admin'" index="/manager/lab">
              <el-icon><House /></el-icon>
              <span>实验室管理</span>
            </el-menu-item>
            <!---------------------------------------------5----------------------------------------->
            <el-menu-item v-if="userInfo?.role === 'admin'" index="/manager/equipment">
              <el-icon><Setting /></el-icon>
              <span>设备管理</span>
            </el-menu-item>
            <!---------------------------------------------6------------------------------------------>
            <el-menu-item index="/manager/audit-reservation" v-if="userInfo?.role === 'admin'">
              <el-icon><DocumentChecked /></el-icon>
              <span>预约审核</span></el-menu-item
            >
            <!---------------------------------------------7------------------------------------------>
            <el-menu-item v-if="userInfo?.role === 'admin'" index="/manager/user">
              <el-icon><User /></el-icon>
              <span>用户设置</span>
            </el-menu-item>
            <!---------------------------------------------8----------------------------------------->
            <el-menu-item index="/manager/aichat">
              <el-icon><ChatLineRound /></el-icon>
              <span>AI智能助手</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <!--主页面(嵌套)设置-->
        <el-main> <router-view /><!--告诉页面此处重渲染--> </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import router from '@/router'
import { logout } from '@/utils/auth'
import {
  Menu as IconMenu,
  House,
  Setting,
  User,
  Notebook,
  DocumentChecked,
  List,
  ChatLineRound
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUser } from '@/utils/user'

const { userInfo } = useUser()

const handleprofile = () => {
  router.push('/manager/profile')
}

const handlepassword = () => {
  router.push('/manager/password')
}

const handlelogout = () => {
  logout()
  router.push('/login')
}
</script>
