import axios from 'axios'

/**
 * Базовый URL для API.
 * В development режиме проксируется через Vite (localhost:8000).
 * В production Docker проксируется через Nginx к контейнеру backend.
 * При необходимости может быть переопределен через VITE_API_BASE_URL.
 */
export const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const api = axios.create({
  baseURL: API_BASE
})

export default api
