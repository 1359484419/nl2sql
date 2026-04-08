<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <div>
        <router-link to="/" class="text-sm text-gray-500 hover:text-gray-300 no-underline flex items-center gap-1 mb-1">← 返回首页</router-link>
        <h1 class="text-2xl font-bold text-white">W{{ weekNumber }} · {{ weekTitle }}</h1>
      </div>
      <div class="text-right">
        <div class="text-3xl font-black text-purple-400">{{ summary?.completion_rate || 0 }}%</div>
        <div class="text-xs text-gray-500">打卡完成率</div>
      </div>
    </div>

    <div class="bg-slate-800 border border-slate-700 rounded-2xl p-5 mb-6">
      <div class="flex justify-between text-sm text-gray-400 mb-2">
        <span>学习进度</span>
        <span>{{ summary?.checked_in_days || 0 }} / {{ summary?.total_days || 0 }} 天</span>
      </div>
      <div class="h-3 bg-slate-700 rounded-full overflow-hidden">
        <div class="h-full bg-gradient-to-r from-purple-600 to-green-500 rounded-full transition-all duration-700"
          :style="{ width: (summary?.completion_rate || 0) + '%' }"></div>
      </div>
      <div class="grid grid-cols-3 gap-4 mt-4">
        <div class="text-center p-3 bg-slate-700 rounded-xl">
          <div class="text-lg font-bold text-blue-400">{{ summary?.questions_total || 0 }}</div>
          <div class="text-xs text-gray-500">总题目</div>
        </div>
        <div class="text-center p-3 bg-slate-700 rounded-xl">
          <div class="text-lg font-bold text-green-400">{{ summary?.questions_answered || 0 }}</div>
          <div class="text-xs text-gray-500">已答题</div>
        </div>
        <div class="text-center p-3 bg-slate-700 rounded-xl">
          <div class="text-lg font-bold text-yellow-400">{{ summary?.questions_correct || 0 }}</div>
          <div class="text-xs text-gray-500">答对</div>
        </div>
      </div>
    </div>

    <div class="space-y-3">
      <div v-for="day in summary?.days" :key="day.id"
        class="bg-slate-800 border rounded-2xl p-4 transition-all"
        :class="{
          'border-green-500/40 bg-green-500/5': day.is_checked_in,
          'border-orange-500/30': !day.is_checked_in && !day.is_rest_day,
          'border-slate-700 opacity-60': day.is_rest_day,
        }">
        <div class="flex items-start gap-4">
          <div class="flex flex-col items-center gap-1 flex-shrink-0">
            <div class="w-10 h-10 rounded-full border-2 flex items-center justify-center font-bold text-sm"
              :class="{
                'border-green-500 bg-green-500 text-black': day.is_checked_in,
                'border-orange-400 bg-orange-500/10 text-orange-400': !day.is_checked_in && !day.is_rest_day,
                'border-slate-600 text-gray-600': day.is_rest_day,
              }">
              <span v-if="day.is_checked_in">✓</span>
              <span v-else-if="day.is_rest_day">休</span>
              <span v-else>{{ day.day_number }}</span>
            </div>
            <div class="text-xs text-gray-600">{{ formatDate(day.date) }}</div>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="font-bold text-white text-sm">{{ day.title }}</span>
              <span v-if="day.is_rest_day" class="px-2 py-0.5 bg-slate-700 text-gray-500 text-xs rounded-full">休息日</span>
            </div>
            <div v-if="day.subtitle" class="text-xs text-gray-500 mb-2">{{ day.subtitle }}</div>
            <div v-if="day.tasks.length" class="mb-2">
              <div v-for="(task, i) in day.tasks.slice(0, 3)" :key="i" class="text-xs text-gray-400 flex items-center gap-1.5 mb-0.5">
                <span class="w-1.5 h-1.5 rounded-full" :class="day.is_checked_in ? 'bg-green-500' : 'bg-slate-600'"></span>
                {{ task }}
              </div>
              <div v-if="day.tasks.length > 3" class="text-xs text-gray-600 mt-1">+{{ day.tasks.length - 3 }} 项...</div>
            </div>
            <div v-if="day.checkin?.git_commits?.length" class="mt-2">
              <div v-for="commit in day.checkin.git_commits.slice(0, 2)" :key="commit.hash"
                class="text-xs text-gray-600 font-mono flex items-center gap-1.5 mb-0.5">
                <span class="text-purple-400">{{ commit.hash }}</span>
                <span class="truncate">{{ commit.message }}</span>
              </div>
            </div>
          </div>
          <div class="flex flex-col gap-1.5 flex-shrink-0">
            <router-link v-if="!day.is_checked_in && !day.is_rest_day" :to="`/checkin/${day.id}`"
              class="px-3 py-1.5 bg-purple-600 text-white text-xs font-bold rounded-lg hover:bg-purple-700 no-underline text-center">
              打卡
            </router-link>
            <router-link v-if="day.is_checked_in && day.question" :to="`/question/${day.id}`"
              class="px-3 py-1.5 border border-slate-600 text-gray-400 text-xs rounded-lg hover:bg-slate-700 no-underline text-center">
              答题
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useLearningStore } from '@/stores/learning'

const route = useRoute()
const store = useLearningStore()
const weekNumber = computed(() => Number(route.params.id))
const summary = computed(() => store.weekSummaries[weekNumber.value])
const weekTitle = computed(() => {
  const titles: Record<number, string> = {
    1: 'Python · LLM · RAG 基础', 2: 'LangGraph · Agent 编排',
    3: 'RAG 进阶 · 前沿技术', 4: '收尾 · 前沿扩展',
  }
  return titles[weekNumber.value] || ''
})
function formatDate(dateStr: string) {
  const d = new Date(dateStr)
  return `${d.getMonth()+1}/${d.getDate()}`
}
onMounted(async () => {
  await store.fetchAllDays()
  await store.fetchWeek(weekNumber.value)
})
</script>
