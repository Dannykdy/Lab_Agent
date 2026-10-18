/*实验室信息逻辑 */

import request from '@/utils/request'

/*获取实验室列表逻辑 */
export function getLabPageListApi(params) {
  return request({
    url: '/api/lab/list',
    method: 'get',
    params
  })
}

/*获取实验室详情页逻辑 */
export function getLabDetailsApi(labId) {
  return request({
    url: `/api/lab/list/${labId}`,
    method: 'get'
  })
}

/**
 * 新增实验室
 */
export function createLabApi(data) {
  return request({
    url: '/api/lab',
    method: 'post',
    data
  })
}

/**
 * 修改实验室
 */
export function updateLabApi(labId, data) {
  return request({
    url: `/api/lab/${labId}`,
    method: 'put',
    data
  })
}
/**
 * 删除实验室
 */
export function deleteLabApi(labId) {
  return request({
    url: `/api/lab/${labId}`,
    method: 'delete'
  })
}
