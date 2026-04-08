<template>
  <div>
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin text-4xl text-purple-400">⟳</div>
    </div>

    <div v-else-if="day?.is_checked_in && !submitting" class="text-center py-20">
      <div class="text-5xl mb-4">✅</div>
      <h2 class="text-xl font-bold text-white mb-2">今日已打卡！</h2>
      <p class="text-gray-400 mb-6">你今天的学习进度已记录</p>
      <div v-if="day.checkin" class="max-w-md mx-auto bg-slate-800 border border-slate-700 rounded-2xl p-5 text-left mb-6">
        <div class="flex items-center gap-2 mb-3">
          <span class="px-3 py-1 rounded-full text-sm font-bold"
            :class="{
              'bg-green-500/10 text-green-400': day.checkin.mood === 'great',
              'bg-blue-500/10 text-blue-400': day.checkin.mood === 'good',
              'bg-yellow-500/10 text-yellow-400': day.checkin.mood === 'okay',
              'bg-red-500/10 text-red-400': day.checkin.mood === 'bad',
            }">{{ moodLabel }}</span>
        </div>
        <div v-if="day.checkin.note" class="mb-3">
          <div class="text-xs text-gray-500 mb-1">学习心得</div>
          <div class="text-sm text-gray-300 bg-slate-700 rounded-xl p-3">{{ day.checkin.note }}</div>
        </div>
        <div v-if="day.checkin.completed_tasks?.length" class="mb-3">
          <div class="text-xs text-gray-500 mb-1">完成任务</div>
          <div class="flex flex-wrap gap-1">
            <span v-for="task in day.checkin.completed_tasks" :key="task"
              class="px-2 py-0.5 bg-green-500/10 text-green-400 text-xs rounded-full">{{ task }}</span>
          </div>
        </div>
        <div v-if="day.checkin.git_commits?.length">
          <div class="text-xs text-gray-500 mb-2">Git 提交</div>
          <div class="space-y-1.5">
            <div v-for="commit in day.checkin.git_commits" :key="commit.hash"
              class="flex items-center gap-2 text-xs">
              <span class="text-purple-400 font-mono font-bold">{{ commit.hash }}</span>
              <span class="text-gray-400 truncate flex-1">{{ commit.message }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="flex gap-3 justify-center">
        <router-link v-if="day.question" :to="`/question/${day.id}`"
          class="px-5 py-2.5 bg-purple-600 text-white font-bold rounded-xl no-underline">去答题 →</router-link>
        <router-link to="/" class="px-5 py-2.5 bg-slate-800 border border-slate-700 text-gray-400 rounded-xl no-underline">返回首页</router-link>
      </div>
    </div>

    <div v-else class="max-w-lg mx-auto">
      <router-link to="/" class="text-sm text-gray-500 hover:text-gray-300 no-underline flex items-center gap-1 mb-6">← 返回首页</router-link>
      <h2 class="text-xl font-bold text-white mb-1">今日打卡</h2>
      <p class="text-sm text-gray-500 mb-5">{{ day?.title }}</p>

      <div class="mb-5">
        <div class="text-sm text-gray-400 mb-2">今日心情</div>
        <div class="flex gap-2">
          <button v-for="m in moods" :key="m.value" @click="mood = m.value"
            class="flex-1 py-2.5 rounded-xl border text-sm font-medium transition-all"
            :class="mood === m.value ? 'border-purple-500 bg-purple-500/10 text-purple-400' : 'border-slate-700 text-gray-400 hover:border-purple-500/50'">
            {{ m.emoji }} {{ m.label }}
          </button>
        </div>
      </div>

      <div class="mb-5">
        <div class="text-sm text-gray-400 mb-2">任务完成情况</div>
        <div class="space-y-2">
          <div v-for="(task, i) in day?.tasks" :key="i" @click="toggleTask(task)"
            class="flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all text-sm"
            :class="completedTasks.includes(task) ? 'border-purple-500 bg-purple-500/5' : 'border-slate-700 hover:border-purple-500/30'">
            <div class="w-5 h-5 rounded flex items-center justify-center text-xs font-bold flex-shrink-0 transition-all"
              :class="completedTasks.includes(task) ? 'bg-purple-500 text-white' : 'border border-slate-600 text-transparent'">✓</div>
            <span :class="completedTasks.includes(task) ? 'text-gray-400 line-through' : 'text-gray-300'">{{ task }}</span>
          </div>
        </div>
      </div>

      <div class="mb-5">
        <div class="text-sm text-gray-400 mb-2">学习心得（可选）</div>
        <textarea v-model="note" rows="3" placeholder="今天学到了什么？有什么收获..."
          class="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-sm text-gray-300 placeholder-gray-600 resize-none focus:outline-none focus:border-purple-500 transition-colors"></textarea>
      </div>

      <div v-if="gitCommits.length" class="mb-5">
        <div class="text-sm text-gray-400 mb-2">检测到今日 Git 提交 {{ gitCommits.length }} 条</div>
        <div class="space-y-1.5">
          <div v-for="c in gitCommits.slice(0, 5)" :key="c.hash" class="flex items-center gap-2 text-xs text-gray-400">
            <span class="text-purple-400 font-mono font-bold">{{ c.hash }}</span>
            <span class="truncate">{{ c.message }}</span>
          </div>
        </div>
      </div>

      <button @click="submit" :disabled="submitting"
        class="w-full py-3.5 bg-purple-600 text-white font-bold rounded-xl hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
        {{ submitting ? '提交中...' : '确认打卡 ✅' }}
      </button>
      <div v-if="error" class="mt-3 text-center text-sm text-red-400">{{ error }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useLearningStore, type LearningDay } from '@/stores/learning'

const route = useRoute()
const store = useLearningStore()
const dayId = computed(() => route.params.dayId as string)
const day = ref<LearningDay | null>(null)
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const mood = ref('great')
const completedTasks = ref<string[]>([])
const note = ref('')
const gitCommits = ref<any[]>([])

const moods = [
  { value: 'great', emoji: '🚀', label: '超棒' },
  { value: 'good',  emoji: '😊', label: '不错' },
  { value: 'okay',  emoji: '😐', label: '一般' },
  { value: 'bad',   emoji: '😔', label: '低落' },
]
const moodLabel = computed(() => moods.find(m => m.value === mood.value)?.emoji + ' ' + moods.find(m => m.value === mood.value)?.label || '')

function toggleTask(task: string) {
  const idx = completedTasks.value.indexOf(task)
  if (idx === -1) completedTasks.value.push(task)
  else completedTasks.value.splice(idx, 1)
}

async function submit() {
  if (!day.value) return
  submitting.value = true
  error.value = ''
  const allTasks = day.value.tasks
  const uncompleted = allTasks.filter(t => !completedTasks.value.includes(t))
  try {
    await store.submitCheckin({ day_id: dayId.value, mood: mood.value, note: note.value, completed_tasks: completedTasks.value, uncompleted_tasks: uncompleted })
    day.value.is_checked_in = true
    day.value.checkin = { id: 'temp', day_id: dayId.value, checked_at: new Date().toISOString(), mood: mood.value, note: note.value, completed_tasks: completedTasks.value, uncompleted_tasks: uncompleted, git_commits: gitCommits.value }
  } catch (e: any) { error.value = e?.response?.data?.detail || e.message || '提交失败' }
  finally { submitting.value = false }
}

onMounted(async () => {
  day.value = await store.fetchDay(dayId.value)
  if (day.value) {
    completedTasks.value = [...day.value.tasks]
    gitCommits.value = await store.fetchGitCommits({ since: day.value.date, until: day.value.date })
  }
  loading.value = false
})
</script>
