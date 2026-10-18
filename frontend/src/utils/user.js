//仅供setup函数使用，保存用户信息的逻辑

import { ref } from 'vue'
import { getUserInfo, setToken, setUserInfo } from './auth'

const userInfo = ref(getUserInfo()) //响应式对象

//定义组合函数(必须用use+Xxx驼峰命名规则)
export function useUser() {
  //保存传入的用户信息
  function saveLoginData(data) {
    setToken(data.token) //保存最新Token
    setUserInfo(data.user) //保存最新用户信息
    userInfo.value = data.user //更新最新的用户信息
  }
  //更新用户信息
  function updateUser(user) {
    setUserInfo(user) //保存最新用户信息
    userInfo.value = user //更新最新的用户信息
  }
  //加载用户信息
  function reloadUser() {
    userInfo.value = getUserInfo() //更新最新的用户信息
  }
  //返回所有的信息
  return {
    userInfo,
    saveLoginData,
    updateUser,
    reloadUser
  }
}

/* 
 仅供页面  setup 函数使用

*/
