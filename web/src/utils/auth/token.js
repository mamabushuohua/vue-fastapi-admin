import { lStorage } from '@/utils'
import api from '@/api'

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


export async function refreshAccessToken() {
  const refreshToken = getToken(REFRESH_TOKEN_CODE)
  if (!refreshToken) {
    return null
  }

  try {
    const res = await api.refreshToken(refreshToken)
    if (res.code === 200) {
      setToken(TOKEN_CODE, res.data.access_token)
      setToken(REFRESH_TOKEN_CODE, res.data.refresh_token)
      return res.data.access_token
    } else {
      // Refresh token 失效，清除所有 token
      removeToken(TOKEN_CODE)
      removeToken(REFRESH_TOKEN_CODE)
      return null
    }
  } catch (error) {
    console.error('Failed to refresh access token:', error)
    // Refresh token 失效，清除所有 token
    removeToken(TOKEN_CODE)
    removeToken(REFRESH_TOKEN_CODE)
    return null
  }
}