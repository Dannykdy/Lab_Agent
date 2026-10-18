/*用户信息逻辑 */

import request from '@/utils/request'

/*获取用户逻辑 */
export function getUserInfoApi() {
  return request({
    url: '/api/user/me',
    method: 'get'
  })
}

/*更改用户信息逻辑 */
export function updateUserInfoApi(data) {
  return request({
    url: '/api/user/update_me',
    method: 'put',
    data
  })
}
/*更改用户密码逻辑 */
export function updatePasswordApi(data) {
  return request({
    url: '/api/user/password',
    method: 'put',
    data
  })
}

/*获取用户列表逻辑 */
export function getUserPageListApi(params) {
  return request({
    url: '/api/user/list',
    method: 'get',
    params
  })
}

/**
 * 新增用户
 */
export function createUserApi(data) {
  return request({
    url: '/api/user',
    method: 'post',
    data
  })
}

/**
 * 修改用户
 */
export function updateUserApi(userId, data) {
  return request({
    url: `/api/user/${userId}`,
    method: 'put',
    data
  })
}
/**
 * 删除用户
 */
export function deleteUserApi(userId) {
  return request({
    url: `/api/user/${userId}`,
    method: 'delete'
  })
}
