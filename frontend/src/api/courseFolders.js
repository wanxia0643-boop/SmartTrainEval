import request from './http'

// 获取文件夹列表
export function listFolders(params = {}) {
  return request({
    url: '/course-folders',
    method: 'get',
    params,
  })
}

// 创建文件夹
export function createFolder(data) {
  return request({
    url: '/course-folders',
    method: 'post',
    data,
  })
}

// 更新文件夹
export function updateFolder(id, data) {
  return request({
    url: `/course-folders/${id}`,
    method: 'put',
    data,
  })
}

// 删除文件夹
export function deleteFolder(id) {
  return request({
    url: `/course-folders/${id}`,
    method: 'delete',
  })
}
