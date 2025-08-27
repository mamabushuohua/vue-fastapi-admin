import { lStorage } from '@/utils'

export const TOKEN_CODE = 'access_token'
export const REFRESH_TOKEN_CODE = 'refresh_token'

export function getToken(code) {
  return lStorage.get(code || TOKEN_CODE)
}

export function setToken(code, token) {
  lStorage.set(code || TOKEN_CODE, token)
}

export function removeToken(code) {
  lStorage.remove(code || TOKEN_CODE)
}

// export async function refreshAccessToken() {
//   const tokenItem = lStorage.getItem(TOKEN_CODE)
//   if (!tokenItem) {
//     return
//   }
//   const { time } = tokenItem
//   // token生成或者刷新后30分钟内不执行刷新
//   if (new Date().getTime() - time <= 1000 * 60 * 30) return
//   try {
//     const res = await api.refreshToken()
//     setToken(res.data.token)
//   } catch (error) {
//     console.error(error)
//   }
// }
