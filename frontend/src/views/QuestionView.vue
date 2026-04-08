<template>
  <div>
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin text-4xl text-purple-400">⟳</div>
    </div>

    <div v-else-if="!question" class="text-center py-20">
      <div class="text-4xl mb-3">📝</div>
      <div class="text-gray-400 mb-4">今天没有答题</div>
      <router-link to="/" class="px-5 py-2.5 bg-slate-800 border border-slate-700 text-gray-400 rounded-xl no-underline">返回首页</router-link>
    </div>

    <div v-else class="max-w-xl mx-auto">
      <router-link to="/" class="text-sm text-gray-500 hover:text-gray-300 no-underline flex items-center gap-1 mb-6">← 返回首页</router-link>

      <div class="bg-slate-800 border border-slate-700 rounded-2xl p-6 mb-4">
        <div class="flex items-center gap-2 mb-4">
          <span class="px-3 py-1 text-xs font-bold rounded-full"
            :class="{
              'bg-blue-500/10 text-blue-400': question.question_type === 'single',
              'bg-orange-500/10 text-orange-400': question.question_type === 'multiple',
              'bg-green-500/10 text-green-400': question.question_type === 'concept',
            }">{{ typeLabel }}</span>
          <span class="px-2 py-1 bg-slate-700 text-gray-500 text-xs rounded-full">难度 {{ '⭐'.repeat(question.difficulty) }}</span>
        </div>
        <div class="text-lg font-semibold text-white mb-6 leading-relaxed">{{ question.question_text }}</div>

        <div v-if="question.question_type !== 'concept'" class="space-y-3">
          <div v-for="opt in question.options" :key="opt.label" @click="toggleOption(opt.label)"
            class="flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all"
            :class="isSelected(opt.label) ? 'border-purple-500 bg-purple-500/10' : 'border-slate-700 hover:border-purple-500/50'">
            <div class="w-7 h-7 rounded-lg border-2 flex items-center justify-center text-sm font-bold flex-shrink-0"
              :class="isSelected(opt.label) ? 'border-purple-500 bg-purple-500 text-white' : 'border-slate-600 text-gray-500'">{{ opt.label }}</div>
            <span class="text-gray-300 text-sm">{{ opt.text }}</span>
          </div>
        </div>
        <div v-else>
          <textarea v-model="conceptAnswer" placeholder="写下你的理解..." rows="5"
            class="w-full bg-slate-700 border border-slate-700 rounded-xl p-4 text-sm text-gray-300 placeholder-gray-600 resize-none focus:outline-none focus:border-purple-500 transition-colors"></textarea>
        </div>
      </div>

      <button v-if="!submitted" @click="submitAnswer" :disabled="!canSubmit"
        class="w-full py-3.5 bg-purple-600 text-white font-bold rounded-xl hover:bg-purple-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
        提交答案
      </button>

      <div v-if="submitted && result" class="mt-4">
        <div class="rounded-2xl p-5 border"
          :class="{
            'bg-green-500/5 border-green-500/40': result.is_correct === true,
            'bg-red-500/5 border-red-500/40': result.is_correct === false,
            'bg-slate-800 border-slate-700': result.is_correct === null,
          }">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-2xl">{{ result.is_correct === true ? '🎉' : result.is_correct === false ? '😢' : '📝' }}</span>
            <span class="font-bold text-sm"
              :class="{
                'text-green-400': result.is_correct === true,
                'text-red-400': result.is_correct === false,
                'text-gray-400': result.is_correct === null,
              }">{{ result.is_correct === true ? '回答正确！' : result.is_correct === false ? '回答错误' : '已提交' }}</span>
          </div>
          <div v-if="result.correct_answer" class="mb-3">
            <div class="text-xs text-gray-500 mb-1">正确答案</div>
            <div class="text-white text-sm font-mono bg-slate-700 rounded-lg px-3 py-2 inline-block">{{ result.correct_answer }}</div>
          </div>
          <div v-if="result.explanation">
            <div class="text-xs text-gray-500 mb-1">解析</div>
            <div class="text-sm text-gray-300 leading-relaxed">{{ result.explanation }}</div>
          </div>
        </div>
        <router-link to="/" class="block mt-4 text-center py-3 bg-slate-800 border border-slate-700 text-gray-400 rounded-xl no-underline">返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useLearningStore, type DailyQuestion } from '@/stores/learning'

const route = useRoute()
const store = useLearningStore()
const dayId = computed(() => route.params.dayId as string)
const question = ref<DailyQuestion | null>(null)
const loading = ref(true)
const selectedLabels = ref<string[]>([])
const conceptAnswer = ref('')
const submitted = ref(false)
const result = ref<any>(null)

const typeLabel = computed(() => {
  const map: Record<string, string> = { single: '单选题', multiple: '多选题', concept: '概念题' }
  return map[question.value?.question_type || ''] || ''
})
const canSubmit = computed(() => {
  if (!question.value) return false
  if (question.value.question_type === 'concept') return conceptAnswer.value.trim().length > 0
  return selectedLabels.value.length > 0
})
function isSelected(label: string) { return selectedLabels.value.includes(label) }
function toggleOption(label: string) {
  if (question.value?.question_type === 'single') { selectedLabels.value = [label] }
  else {
    const idx = selectedLabels.value.indexOf(label)
    if (idx === -1) selectedLabels.value.push(label)
    else selectedLabels.value.splice(idx, 1)
  }
}
async function submitAnswer() {
  if (!question.value) return
  const userAnswer = question.value.question_type === 'concept' ? 'concept' : selectedLabels.value.join(',')
  result.value = await store.submitAnswer({ question_id: question.value.id, user_answer: userAnswer, answer_text: conceptAnswer.value })
  submitted.value = true
}
onMounted(async () => {
  question.value = await store.getQuestion(dayId.value)
  loading.value = false
})
</script>
