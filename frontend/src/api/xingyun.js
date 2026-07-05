import http from './http'

export function getXingyunConfig() {
  return http.get('/xingyun/config')
}
