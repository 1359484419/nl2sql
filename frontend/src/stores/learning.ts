import { defineStore } from 'pinia'
import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1' })

export interface GitCommit {
  hash: string; message: string; author: string; date: string
}
export interface OptionItem {
  label: string; text: string
}
export interface DailyQuestion {
  id: string; day_id: string
  question_type: 'single' | 'multiple' | 'concept'
  question_text: string; options: OptionItem[] | null; difficulty: number
}
export interface CheckInRecord {
  id: string; day_id: string; checked_at: string
  mood: string | null; note: string | null
  completed_tasks: string[]; uncompleted_tasks: string[]
  git_commits: GitCommit[]
}
export interface LearningDay {
  id: string; week_number: number; day_number: number; date: string
  title: string; subtitle: string | null; tasks: string[]
  objectives: string | null; is_rest_day: boolean; is_checked_in: boolean
  question: DailyQuestion | null; checkin: CheckInRecord | null
}
export interface WeekSummary {
  week_number: number; days: LearningDay[]
  total_days: number; checked_in_days: number; completion_rate: number
  questions_total: number; questions_answered: number; questions_correct: number
}

export const useLearningStore = defineStore('learning', {
  state: () => ({
    allDays: [] as LearningDay[],
    weekSummaries: {} as Record<number, WeekSummary>,
    today: null as LearningDay | null,
    currentWeek: null as WeekSummary | null,
    loading: false, error: null as string | null,
  }),

  actions: {
    async fetchAllDays() {
      this.loading = true
      try {
        const res = await api.get<LearningDay[]>('/learning/all-days')
        this.allDays = res.data
      } catch (e: any) { this.error = e.message } finally { this.loading = false }
    },
    async fetchWeek(weekNumber: number) {
      try {
        const res = await api.get<WeekSummary>(`/learning/week/${weekNumber}`)
        this.weekSummaries[weekNumber] = res.data
        this.currentWeek = res.data
        return res.data
      } catch (e: any) { this.error = e.message; return null }
    },
    async fetchToday() {
      try {
        const res = await api.get<LearningDay | null>('/learning/today')
        this.today = res.data; return res.data
      } catch (e: any) { this.error = e.message; return null }
    },
    async fetchDay(dayId: string) {
      try {
        const res = await api.get<LearningDay>(`/learning/day/${dayId}`)
        return res.data
      } catch (e: any) { this.error = e.message; return null }
    },
    async submitCheckin(payload: {
      day_id: string; mood?: string; note?: string
      completed_tasks: string[]; uncompleted_tasks: string[]
    }) {
      const res = await api.post<CheckInRecord>('/learning/checkin', payload)
      return res.data
    },
    async getQuestion(dayId: string) {
      const res = await api.get<DailyQuestion | null>(`/learning/question/${dayId}`)
      return res.data
    },
    async submitAnswer(payload: { question_id: string; user_answer: string; answer_text?: string }) {
      return (await api.post('/learning/answer', payload)).data
    },
    async fetchGitCommits(params: { since?: string; until?: string; keyword?: string }) {
      const res = await api.get<{ commits: GitCommit[] }>('/learning/git/commits', { params })
      return res.data.commits
    },
    getWeekDays(w: number) { return this.allDays.filter(d => d.week_number === w) },
    getWeekCheckins(w: number) { return this.allDays.filter(d => d.week_number === w && d.is_checked_in) },
    getWeekRate(w: number) {
      const total = this.getWeekDays(w).length
      return total ? Math.round(this.getWeekCheckins(w).length / total * 100) : 0
    },
  },
})
