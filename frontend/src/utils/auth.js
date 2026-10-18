//定义管理后端向前端发送的token以及userInfo信息，增删改查的方法

const TOKEN_KEY = 'token'
const USER_KEY = 'userInfo'

/* Token相关操作 */
//保存Token
export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

//获取Token
export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

//删除Token
export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
}

/**************************************************************************************************************************************************************/

/* userInfo相关操作 */
//保存userInfo
export function setUserInfo(userInfo) {
  localStorage.setItem(USER_KEY, JSON.stringify(userInfo))
}

//获取userInfo
export function getUserInfo() {
  const str = localStorage.getItem(USER_KEY)
  return str ? JSON.parse(str) : null
}

//删除userInfo
export function removeUserInfo() {
  localStorage.removeItem(USER_KEY)
}

// 登出
export function logout() {
  removeToken()
  removeUserInfo()
}
