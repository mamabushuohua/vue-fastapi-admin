import { getToken } from '@/utils'
import { resolveResError } from './helpers'
import { useUserStore } from '@/store'
import { refreshAccessToken } from '@/utils/auth/token'

// Token 刷新状态管理
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })

  failedQueue = []
}


export function reqResolve(config) {
  // 处理不需要token的请求
  if (config.noNeedToken) {
    return config
  }

  const token = getToken()
  if (token) {
    config.headers.token = config.headers.token || token
  }

  return config
}

export function reqReject(error) {
  return Promise.reject(error)
}

export function resResolve(response) {
  const { data, status, statusText } = response
  if (data?.code !== 200) {
    const code = data?.code ?? status
    /** 根据code处理对应的操作，并返回处理后的message */
    const message = resolveResError(code, data?.msg ?? statusText)
    window.$message?.error(message, { keepAliveOnHover: true })
    return Promise.reject({ code, message, error: data || response })
  }
  return Promise.resolve(data)
}
export async function resReject(error) {
  if (!error || !error.response) {
    const code = error?.code
    /** 根据code处理对应的操作，并返回处理后的message */
    const message = resolveResError(code, error.message)
    window.$message?.error(message)
    return Promise.reject({ code, message, error })
  }
  const { data, status, config } = error.response

  // 如果是 401 错误且不是刷新 token 的请求
  if (data?.code === 401 && !config.url.includes('/base/refresh_token')) {
    return new Promise((resolve, reject) => {
      // 将失败的请求加入队列
      failedQueue.push({ resolve, reject })

      // 如果没有正在刷新 token，则开始刷新
      if (!isRefreshing) {
        isRefreshing = true

        refreshAccessToken()
          .then(newToken => {
            processQueue(null, newToken)
          })
          .catch(err => {
            processQueue(err, null)
            // 刷新失败，执行登出操作
            const userStore = useUserStore()
            userStore.logout()
          })
          .finally(() => {
            isRefreshing = false
          })
      }
    }).then(newToken => {
      if (newToken) {
        // 刷新成功，重新发送原始请求
        config.headers.token = newToken
        return window.$http(config)
      } else {
        // 刷新失败，返回错误
        return Promise.reject({ code: 401, message: '登录已过期，请重新登录', error: data || error.response })
      }
    }).catch(error => {
      return Promise.reject(error)
    })
  }

  // 后端返回的response数据
  const code = data?.code ?? status
  const message = resolveResError(code, data?.msg ?? error.message)
  window.$message?.error(message, { keepAliveOnHover: true })
  return Promise.reject({ code, message, error: error.response?.data || error.response })
}