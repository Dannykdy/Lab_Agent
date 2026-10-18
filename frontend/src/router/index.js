import { getToken } from '@/utils/auth'
import Login from '@/views/Login.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/manager/home'
    },
    {
      //主页面嵌套路由
      path: '/manager',
      name: 'Layouts',
      component: () => import('@/layouts/layouts.vue'),
      children: [
        {
          path: 'home',
          name: 'Home',
          component: () => import('@/views/Home.vue')
        },

        {
          path: 'lab',
          name: 'Lab',
          component: () => import('@/views/Lab.vue')
        },
        {
          path: 'lablist',
          name: 'LabList',
          component: () => import('@/views/LabList.vue')
        },
        {
          path: 'lab-equipment',
          name: 'LabEquipment',
          component: () => import('@/views/LabEquipment.vue')
        },
        {
          path: 'equipment',
          name: 'Equipment',
          component: () => import('@/views/Equipment.vue')
        },
        {
          path: 'aichat',
          name: 'AIChat',
          component: () => import('@/views/AIChat.vue')
        },
        {
          path: 'user-reservation',
          name: 'UserReservation',
          component: () => import('@/views/UserReservation.vue')
        },
        {
          path: 'audit-reservation',
          name: 'AuditReservation',
          component: () => import('@/views/AuditReservation.vue')
        },
        {
          path: 'profile',
          name: 'Profile',
          component: () => import('@/views/Profile.vue')
        },
        {
          path: 'password',
          name: 'Password',
          component: () => import('@/views/Password.vue')
        },
        {
          path: 'user',
          name: 'User',
          component: () => import('@/views/User.vue')
        }
      ]
    },
    //登陆路由
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue')
    },
    //注册路由
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Register.vue')
    }
  ]
})
//to:去哪，from：从哪来 路由守卫验证token 默认没token返回登录页
router.beforeEach((to, from) => {
  const token = getToken()
  if (to.path === '/login' || to.path === '/register') {
    return true
  } else {
    return token ? true : '/login'
  }
})

export default router
