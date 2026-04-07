import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 120000,
})

export interface ChartConfig {
  chart_type: string
  title: string
  x_axis_label: string
  y_axis_label: string
  series_names: string[]
  recommended_reason: string
}

export interface QueryResult {
  columns: { name: string; data_type: string }[]
  rows: Record<string, any>[]
  row_count: number
  execution_time_ms: number
}

export interface QueryStep {
  step_type: string
  content: string
  sql?: string
  is_success: boolean
  error_message?: string
}

export interface QueryResponse {
  conversation_id: string
  question: string
  generated_sql: string
  sql_valid: boolean
  execution_time_ms: number
  rows_returned: number
  columns: { name: string; data_type: string }[]
  rows: Record<string, any>[]
  chart_config?: ChartConfig
  error_message?: string
}

export interface QueryRequest {
  question: string
  conversation_id?: string
  chart_type?: string
  top_k?: number
}

export const queryApi = {
  sync: (data: QueryRequest) => api.post<QueryResponse>('/query', data),
  
  stream: (data: QueryRequest) => {
    const params = new URLSearchParams()
    if (data.conversation_id) params.set('conversation_id', data.conversation_id)
    return api.post(`/query/stream`, data, {
      params,
      responseType: 'stream',
    })
  },

  buildIndex: (drop?: boolean) => api.post('/index/build', null, { params: { drop } }),
  
  schemaStats: () => api.get('/schema/stats'),
}

export default api
