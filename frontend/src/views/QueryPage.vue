<template>
  <div class="max-w-5xl mx-auto px-4 py-8">
    <!-- Header -->
    <div class="text-center mb-8">
      <h1 class="text-3xl font-bold text-slate-800 mb-2">NL2SQL BI Agent</h1>
      <p class="text-slate-500">用自然语言探索企业协作数据 — Meeting / Calling / Workspace / Messaging</p>
    </div>

    <!-- 预设问题快捷卡片 -->
    <div class="mb-6">
      <p class="text-sm text-slate-500 mb-3">试试这些问题：</p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="q in presetQuestions"
          :key="q"
          @click="submitQuery(q)"
          class="px-3 py-1.5 text-sm bg-white border border-slate-200 rounded-full hover:border-blue-400 hover:text-blue-600 transition-colors cursor-pointer"
        >
          {{ q }}
        </button>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-4 mb-6">
      <div class="flex gap-3">
        <input
          v-model="question"
          @keyup.enter="submitQuery(question)"
          placeholder="例如：本周各部门开了多少次会？平均会议时长是多少？"
          class="flex-1 text-lg outline-none placeholder-slate-400"
          :disabled="isStreaming"
        />
        <button
          @click="submitQuery(question)"
          :disabled="!question.trim() || isStreaming"
          class="px-6 py-2.5 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <span v-if="isStreaming" class="flex items-center gap-2">
            <span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            分析中...
          </span>
          <span v-else>
            <svg class="w-5 h-5 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
            查询
          </span>
        </button>
      </div>
    </div>

    <!-- Agent 思考过程 -->
    <div v-if="steps.length > 0" class="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 mb-6">
      <h3 class="text-sm font-semibold text-slate-500 mb-4 flex items-center gap-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
        </svg>
        AI 思考过程
      </h3>
      <div class="space-y-3">
        <div
          v-for="(step, idx) in steps"
          :key="idx"
          class="flex gap-3 text-sm"
        >
          <span class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
            :class="step.is_success ? 'bg-blue-100 text-blue-600' : 'bg-red-100 text-red-600'"
          >
            {{ step.is_success ? '✓' : '✗' }}
          </span>
          <div class="flex-1">
            <p class="text-slate-700">{{ step.content }}</p>
            <pre v-if="step.sql" class="mt-2 p-3 bg-slate-50 rounded-lg text-xs text-slate-600 font-mono overflow-x-auto">{{ step.sql }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- 结果区域 -->
    <div v-if="responseData" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 指标卡片 -->
      <div class="lg:col-span-3 grid grid-cols-3 gap-4">
        <div class="bg-white rounded-xl p-4 border border-slate-200 text-center">
          <p class="text-3xl font-bold text-blue-600">{{ responseData.rows_returned }}</p>
          <p class="text-sm text-slate-500 mt-1">返回行数</p>
        </div>
        <div class="bg-white rounded-xl p-4 border border-slate-200 text-center">
          <p class="text-3xl font-bold text-green-600">{{ responseData.execution_time_ms }}ms</p>
          <p class="text-sm text-slate-500 mt-1">执行耗时</p>
        </div>
        <div class="bg-white rounded-xl p-4 border border-slate-200 text-center">
          <p class="text-lg font-bold" :class="responseData.sql_valid ? 'text-green-600' : 'text-red-600'">
            {{ responseData.sql_valid ? '✓ SQL有效' : '✗ SQL无效' }}
          </p>
          <p class="text-sm text-slate-500 mt-1">SQL 校验</p>
        </div>
      </div>

      <!-- 图表 -->
      <div v-if="responseData.chart_config" class="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-200 p-5">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-slate-800">{{ responseData.chart_config.title }}</h3>
          <span class="text-xs text-slate-400 bg-slate-100 px-2 py-1 rounded-full">
            {{ responseData.chart_config.chart_type }} · {{ responseData.chart_config.recommended_reason }}
          </span>
        </div>
        <div ref="chartRef" class="w-full" :style="{ height: chartHeight + 'px' }"></div>
      </div>

      <!-- 生成的 SQL -->
      <div v-if="responseData.generated_sql" class="bg-white rounded-2xl shadow-sm border border-slate-200 p-5">
        <h3 class="font-semibold text-slate-800 mb-3 flex items-center gap-2">
          <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
          </svg>
          生成的 SQL
        </h3>
        <pre class="text-xs font-mono text-slate-600 bg-slate-50 p-3 rounded-lg overflow-x-auto whitespace-pre-wrap">{{ responseData.generated_sql }}</pre>
      </div>

      <!-- 数据表格 -->
      <div v-if="responseData.rows && responseData.rows.length > 0" class="lg:col-span-3 bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div class="p-4 border-b border-slate-100">
          <h3 class="font-semibold text-slate-800">查询结果</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-slate-50">
              <tr>
                <th v-for="col in responseData.columns" :key="col.name"
                  class="px-4 py-3 text-left font-semibold text-slate-600 whitespace-nowrap">
                  {{ col.name }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, ri) in visibleRows" :key="ri" class="border-t border-slate-100 hover:bg-slate-50">
                <td v-for="col in responseData.columns" :key="col.name"
                  class="px-4 py-2.5 text-slate-700 whitespace-nowrap">
                  {{ formatCell(row[col.name]) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="responseData.rows.length > 20" class="p-3 text-center text-sm text-slate-500 border-t">
          显示前 20 条，共 {{ responseData.rows.length }} 条
        </div>
      </div>
    </div>

    <!-- 错误 -->
    <div v-if="errorMsg" class="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700">
      <p class="font-semibold">查询失败</p>
      <p class="text-sm mt-1">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
import { queryApi, type QueryRequest, type QueryResponse, type QueryStep } from '@/api/query'

const question = ref('')
const isStreaming = ref(false)
const steps = ref<QueryStep[]>([])
const responseData = ref<QueryResponse | null>(null)
const errorMsg = ref('')
const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const presetQuestions = [
  '本周各部门开了多少次会？',
  '最近一个月通话接通率是多少？',
  '各部门用户平均使用时长是多少？',
  '每天消息发送量趋势如何？',
  '各部门会议质量评分对比',
  '设备使用分布（桌面端/移动端）',
]

const visibleRows = computed(() => responseData.value?.rows.slice(0, 20) ?? [])

const chartHeight = computed(() => {
  const rows = responseData.value?.rows?.length ?? 0
  return Math.max(300, Math.min(rows * 40, 500))
})

async function submitQuery(q: string) {
  if (!q.trim() || isStreaming.value) return

  question.value = q
  isStreaming.value = true
  steps.value = []
  responseData.value = null
  errorMsg.value = ''

  try {
    const request: QueryRequest = {
      question: q,
      chart_type: undefined,
      top_k: 10,
    }

    // 使用 Fetch API + SSE（浏览器原生支持 ReadableStream）
    const res = await fetch('/api/v1/query/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })
    if (!res.ok) {
      errorMsg.value = `请求失败: ${res.status}`
      return
    }
    const reader = res.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    const STEP_TYPE_MAP: Record<string, string> = {
      'start': 'start',
      'intent': 'intent',
      'schema_select': 'schema_select',
      'sql_generate': 'sql_generate',
      'sql': 'sql_generate',
      'sql_validate': 'sql_validate',
      'execute': 'execute',
      'data': 'execute',
      'chart': 'chart',
      'done': 'done',
      'error': 'error',
    }

    function parseSSELines(raw: string): { event: string; data: string }[] {
      const results: { event: string; data: string }[] = []
      // SSE 块以连续的 '\n\n' 分隔，每块可能有 event: 和多行 data:
      const blocks = raw.split('\n\n')
      for (const block of blocks) {
        const lines = block.split('\n')
        let eventType = ''
        let dataLines: string[] = []
        for (const line of lines) {
          if (line.startsWith('event:')) eventType = line.slice(6).trim()
          if (line.startsWith('data:')) dataLines.push(line.slice(5))
        }
        // 多行 data: 在 SSE 中以 '\n' 连接（标准 SSE 格式）
        const dataContent = dataLines.join('\n')
        if (eventType && dataContent) {
          results.push({ event: eventType, data: dataContent })
        }
      }
      return results
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const events = parseSSELines(buffer)
      buffer = ''
      for (const { event: eventType, data: dataStr } of events) {
        if (eventType === 'done') {
          try {
            responseData.value = JSON.parse(dataStr) as QueryResponse
          } catch {}
          continue
        }
        if (eventType === 'error') {
          try {
            const errData = JSON.parse(dataStr)
            errorMsg.value = errData.message ?? '发生错误'
          } catch {
            errorMsg.value = dataStr
          }
          continue
        }
        if (eventType === 'step') {
          try {
            const step = JSON.parse(dataStr) as { step_type: string; content: string; sql?: string }
            const mappedType = STEP_TYPE_MAP[step.step_type] ?? step.step_type
            const existing = steps.value.findIndex(s => s.step_type === mappedType)
            const stepObj: QueryStep = {
              step_type: mappedType,
              content: step.content,
              sql: step.sql,
              is_success: true,
            }
            if (existing >= 0) {
              steps.value[existing] = stepObj
            } else {
              steps.value.push(stepObj)
            }
          } catch {}
          continue
        }
      }
    }

    // 如果流式没有返回完整数据，尝试同步接口
    if (!responseData.value) {
      try {
        const syncRes = await queryApi.sync(request)
        responseData.value = syncRes.data
      } catch (syncErr: any) {
        errorMsg.value = errorMsg.value || (syncErr?.response?.data?.detail ?? syncErr.message ?? '查询失败')
      }
    }
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail ?? err.message ?? '查询失败'
  } finally {
    isStreaming.value = false
  }
}

function formatCell(val: any): string {
  if (val === null || val === undefined) return '—'
  if (typeof val === 'number') return Number.isInteger(val) ? val.toString() : val.toFixed(2)
  if (typeof val === 'boolean') return val ? '是' : '否'
  return String(val)
}

watch(responseData, async (val) => {
  if (!val || !val.chart_config || !val.rows?.length) return
  await nextTick()
  renderChart()
})

const NUMERIC_DT_KEYWORDS = ['int', 'bigint', 'decimal', 'numeric', 'float', 'double']

function columnLooksNumeric(c: { name: string; data_type: string }): boolean {
  const dt = c.data_type.toLowerCase()
  return NUMERIC_DT_KEYWORDS.some((t) => dt.includes(t))
}

/** 后端若未标数值类型，仍可从单元格解析出数字列（兼容旧数据） */
function inferNumericColumns(
  cols: { name: string; data_type: string }[],
  rows: Record<string, unknown>[],
  max: number
): { name: string; data_type: string }[] {
  const typed = cols.filter(columnLooksNumeric).slice(0, max)
  if (typed.length > 0) return typed
  const out: { name: string; data_type: string }[] = []
  for (const c of cols) {
    for (const r of rows.slice(0, 30)) {
      const v = r[c.name]
      if (v === null || v === undefined) continue
      const n = Number(v)
      if (!Number.isNaN(n) && Number.isFinite(n)) {
        out.push({ name: c.name, data_type: 'NUMERIC' })
        break
      }
    }
    if (out.length >= max) break
  }
  return out
}

function renderChart() {
  if (!chartRef.value || !responseData.value) return
  if (chartInstance) {
    chartInstance.dispose()
  }

  const config = responseData.value!.chart_config!
  const rows = responseData.value!.rows!
  const cols = responseData.value!.columns!

  chartInstance = echarts.init(chartRef.value)

  const numCols = inferNumericColumns(cols, rows, 3)
  const dimCol =
    cols.find((c) => !numCols.some((nc) => nc.name === c.name)) ?? cols[0]

  const xData = rows.map((r) => (dimCol ? String(r[dimCol.name] ?? '') : String(r)))

  if (config.chart_type === 'pie' && numCols.length > 0) {
    const valueCol = numCols[0]
    const option: echarts.EChartsOption = {
      title: { text: config.title, left: 'center', textStyle: { fontSize: 14 } },
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { orient: 'horizontal', bottom: 0 },
      series: [
        {
          type: 'pie',
          radius: ['36%', '62%'],
          data: rows.map((r) => ({
            name: dimCol ? String(r[dimCol.name] ?? '') : '—',
            value: Number(r[valueCol.name] ?? 0),
          })),
        },
      ],
    }
    chartInstance.setOption(option)
    requestAnimationFrame(() => chartInstance?.resize())
    return
  }

  const seriesType = config.chart_type === 'line' ? 'line' : 'bar'
  const seriesData = numCols.map((col) => ({
    name: col.name,
    type: seriesType,
    data: rows.map((r) => {
      const v = r[col.name]
      return v === null || v === undefined ? 0 : Number(v)
    }),
    smooth: config.chart_type === 'line',
    areaStyle: config.chart_type === 'area' ? { opacity: 0.2 } : undefined,
  }))

  const option: echarts.EChartsOption = {
    title: { text: config.title, left: 'center', textStyle: { fontSize: 14 } },
    tooltip: { trigger: 'axis' },
    legend: { data: seriesData.map((s) => s.name), bottom: 0 },
    xAxis: { type: 'category', data: xData, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: config.y_axis_label },
    series: seriesData,
    grid: { left: 50, right: 20, bottom: 60 },
  }

  chartInstance.setOption(option)
  requestAnimationFrame(() => chartInstance?.resize())
}
</script>
