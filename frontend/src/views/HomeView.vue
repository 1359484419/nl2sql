<template>
  <div>
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin text-4xl text-purple-400">⟳</div>
    </div>
    <div v-else>
      <!-- Today's Task -->
      <div v-if="today" class="mb-8">
        <div class="flex items-center gap-3 mb-4">
          <div class="text-3xl">🌟</div>
          <div>
            <div class="text-xs text-gray-500 uppercase tracking-widest">今日任务</div>
            <div class="text-xl font-bold text-white">{{ today.title }}</div>
          </div>
          <div class="ml-auto flex gap-2">
            <span v-if="today.is_checked_in" class="px-3 py-1 bg-green-500/10 text-green-400 text-sm font-bold rounded-full">✓ 已打卡</span>
            <span v-else class="px-3 py-1 bg-orange-500/10 text-orange-400 text-sm font-bold rounded-full">待打卡</span>
          </div>
        </div>
        <div class="bg-slate-800 border border-slate-700 rounded-2xl p-5">
          <div class="text-sm text-gray-400 mb-3">{{ today.subtitle }}</div>
          <div class="space-y-2 mb-5">
            <div v-for="(task, i) in today.tasks" :key="i" class="flex items-center gap-3 text-sm text-gray-300">
              <span class="w-5 h-5 rounded-full border border-slate-600 flex-shrink-0 flex items-center justify-center text-xs text-gray-500">{{ i+1 }}</span>
              {{ task }}
            </div>
          </div>
          <div class="flex gap-3">
            <router-link v-if="!today.is_checked_in" :to="`/checkin/${today.id}`"
              class="px-5 py-2.5 bg-purple-600 text-white font-bold rounded-xl hover:bg-purple-700 transition-colors no-underline">
              打卡 →
            </router-link>
            <router-link v-if="today.question" :to="`/question/${today.id}`"
              class="px-5 py-2.5 border border-purple-600 text-purple-400 font-bold rounded-xl hover:bg-purple-600/10 transition-colors no-underline">
              答题 →
            </router-link>
          </div>
        </div>
      </div>
      <div v-else class="mb-8 p-8 bg-slate-800 border border-slate-700 rounded-2xl text-center">
        <div class="text-4xl mb-3">📅</div>
        <div class="text-gray-400">今天没有安排学习日</div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-4 gap-4 mb-8">
        <div class="bg-slate-800 border border-slate-700 rounded-2xl p-4 text-center">
          <div class="text-2xl font-bold text-purple-400">{{ allDays.length }}</div>
          <div class="text-xs text-gray-500 mt-1">总天数</div>
        </div>
        <div class="bg-slate-800 border border-slate-700 rounded-2xl p-4 text-center">
          <div class="text-2xl font-bold text-green-400">{{ checkedInDays }}</div>
          <div class="text-xs text-gray-500 mt-1">已打卡</div>
        </div>
        <div class="bg-slate-800 border border-slate-700 rounded-2xl p-4 text-center">
          <div class="text-2xl font-bold text-blue-400">{{ weekCommits }}</div>
          <div class="text-xs text-gray-500 mt-1">本周提交</div>
        </div>
        <div class="bg-slate-800 border border-slate-700 rounded-2xl p-4 text-center">
          <div class="text-2xl font-bold text-yellow-400">{{ answerRate }}%</div>
          <div class="text-xs text-gray-500 mt-1">正确率</div>
        </div>
      </div>

      <!-- Weeks overview -->
      <div class="text-xs uppercase tracking-widest text-gray-600 mb-3 font-bold">四周概览</div>
      <div class="grid grid-cols-2 gap-4">
        <router-link v-for="w in 4" :key="w" :to="`/week/${w}`"
          class="bg-slate-800 border border-slate-700 rounded-2xl p-5 hover:border-purple-500/50 transition-all no-underline block">
          <div class="flex items-center justify-between mb-3">
            <div class="font-bold text-white">W{{ w }}</div>
            <div class="text-xs text-gray-500">{{ weekTitles[w] }}</div>
          </div>
          <div class="h-2 bg-slate-700 rounded-full overflow-hidden mb-3">
            <div class="h-full bg-gradient-to-r from-purple-600 to-green-500 rounded-full transition-all duration-700"
              :style="{ width: getWeekRate(w) + '%' }"></div>
          </div>
          <div class="flex justify-between text-xs text-gray-500">
            <span>打卡 {{ getWeekCheckins(w) }}/{{ getWeekDays(w) }}</span>
            <span>{{ getWeekRate(w) }}%</span>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { useLearningStore } from '@/stores/learning'

const store = useLearningStore()
const loading = ref(true)
const commits = ref<any[]>([])

onMounted(async () => {
  await Promise.all([store.fetchAllDays(), store.fetchToday()])
  try {
    const res = await store.fetchGitCommits({})
    commits.value = res || []
  } catch {}
  loading.value = false
})

const today = computed(() => store.today)
const allDays = computed(() => store.allDays)
const checkedInDays = computed(() => allDays.value.filter(d => d.is_checked_in).length)
const weekCommits = computed(() => commits.value.length)
const answerRate = computed(() => {
  if (!allDays.value.length) return 0
  const answered = allDays.value.filter(d => d.question).length
  return Math.round(answered / allDays.value.length * 100)
})

function getWeekDays(w: number) { return store.getWeekDays(w).length }
function getWeekCheckins(w: number) { return store.getWeekCheckins(w).length }
function getWeekRate(w: number) { return store.getWeekRate(w) }

const weekTitles: Record<number, string> = {
  1: 'Python · LLM · RAG 基础', 2: 'LangGraph · Agent 编排',
  3: 'RAG 进阶 · 前沿技术', 4: '收尾 · 前沿扩展',
}
</script>
