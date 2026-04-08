import axios from 'axios'
const api = axios.create({ baseURL: '/api/v1' })

export const learningApi = {
  getAllDays: () => api.get('/learning/all-days'),
  getToday: () => api.get('/learning/today'),
  getDay: (dayId: string) => api.get(`/learning/day/${dayId}`),
  getWeek: (week: number) => api.get(`/learning/week/${week}`),
  checkin: (payload: any) => api.post('/learning/checkin', payload),
  getCheckin: (dayId: string) => api.get(`/learning/checkin/${dayId}`),
  getQuestion: (dayId: string) => api.get(`/learning/question/${dayId}`),
  submitAnswer: (payload: any) => api.post('/learning/answer', payload),
  getGitCommits: (params: any) => api.get('/learning/git/commits', { params }),
}
