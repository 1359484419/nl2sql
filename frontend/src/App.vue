<template>
  <div class="min-h-screen bg-dark">
    <!-- Learning Tracker Navigation -->
    <nav class="border-b border-slate-800 bg-slate-900/90 sticky top-0 z-50 backdrop-blur-sm">
      <div class="max-w-5xl mx-auto px-4 py-3 flex items-center gap-6">
        <router-link to="/" class="flex items-center gap-2 text-white font-bold text-lg no-underline">
          <span class="text-xl">📚</span> AI 学习追踪
        </router-link>
        <div class="flex gap-1">
          <router-link
            v-for="w in [1,2,3,4]" :key="w"
            :to="`/week/${w}`"
            class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors no-underline"
            :class="currentWeekNum === w
              ? 'bg-purple-600 text-white'
              : 'text-slate-500 hover:text-white hover:bg-slate-800'">
            W{{ w }}
          </router-link>
        </div>
        <div class="flex-1"></div>
        <router-link
          to="/nl2sql"
          class="px-3 py-1.5 rounded-lg text-sm font-medium text-slate-500 hover:text-white hover:bg-slate-800 no-underline transition-colors">
          NL2SQL 查询
        </router-link>
      </div>
    </nav>
    <main class="max-w-5xl mx-auto px-4 py-6">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentWeekNum = computed(() => {
  const id = route.params.id
  return id ? Number(id) : null
})
</script>
