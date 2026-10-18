import request from '@/utils/request'

/* 上传文件接口 */
export function uploadFileApi(file) {
  // FormData 是浏览器自带的"快递打包盒",能把文件打包成后端认识的格式
  // 先 new 一个出来,再调用它的 append 方法把文件装进去
  const formData = new FormData()
  // 'fileobj' 这个字段名必须和后端 files.py 里 File(...) 的参数名一致
  formData.append('fileobj', file)

  return request({
    url: '/api/files/upload',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
