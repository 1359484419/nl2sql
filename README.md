# NL2SQL BI Agent

基于自然语言的 BI 查询系统 — **NL2SQL + RAG（Milvus）+ LangGraph + 可视化图表**

用自然语言探索企业协作 SaaS 平台数据：Meeting（会议）、Calling（通话）、Workspace（工作空间）、Messaging（消息）、Device（设备）、Quality（质量）。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Vue](https://img.shields.io/badge/vue-3.4+-green.svg)

---

## 业务背景

这是一个**企业协作 SaaS 多租户平台**，Supervisor 角色可以看到所在公司的运营 Dashboard，包括：

| 模块 | 典型指标 |
|------|---------|
| **Meeting** | 会议总数、平均时长、质量评分、参会人数、屏幕共享次数 |
| **Calling** | 通话总数、平均通话时长、接通率、未接来电数 |
| **Workspace** | 使用时长、登录次数、文件操作数、任务完成数、存储使用量 |
| **Messaging** | 消息发送数、互动数（Reactions/回复）、活跃频道数 |
| **Device** | 设备分布（桌面端/移动端/平板）、操作系统占比 |
| **Quality** | 综合质量评分、延迟、丢包率、连接失败率 |

---

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Vue 3 前端                            │
│  (流式 SSE + ECharts 可视化 + Tailwind CSS)            │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP / SSE
┌──────────────────────▼──────────────────────────────────┐
│                 FastAPI 后端                             │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ 意图分类    │→│  RAG 检索     │→│  SQL 生成      │  │
│  │ (意图识别)  │  │ (Milvus)     │  │ (LangGraph)   │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
│       ↓                                        ↓        │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ 时间范围推断 │  │ SQL 校验     │→│  图表推荐      │  │
│  │             │  │ (语法+逻辑)   │  │ (ECharts)    │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ↓                         ↓
┌──────────────────┐     ┌─────────────────────┐
│  Milvus Lite      │     │  PostgreSQL         │
│  (向量数据库)      │     │  (业务数据库)        │
│  Schema 向量索引   │     │  模拟数据 ~3000 条   │
│  指标库索引        │     │  10 张表            │
│  SQL 示例索引      │     │  多租户隔离         │
└──────────────────┘     └─────────────────────┘
```

---

## 核心技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 前端 | Vue 3 + TypeScript | 流式 SSE 输出，ECharts 图表 |
| 后端 | FastAPI + Pydantic | 同步/流式双接口 |
| Agent 编排 | LangGraph | 状态机流水线 |
| LLM | Ollama (本地) / OpenAI | 支持切换 |
| 向量数据库 | Milvus Lite | 零 Docker 本地运行 |
| Embedding | HuggingFace SentenceTransformer | CPU 友好 |
| 业务数据库 | PostgreSQL | 生产级首选 |
| ORM | SQLAlchemy | 数据库连接池 |

---

## 快速启动

### 1. 安装依赖

```bash
# 后端
cd nl2sql-bi-agent
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

根据你的环境修改 `.env`：

```ini
# 方式一：使用 Ollama 本地模型（推荐，无需 API Key）
USE_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_EMBED_MODEL=nomic-embed-text

# 方式二：使用 OpenAI（取消注释并填入 Key）
# USE_OLLAMA=false
# OPENAI_API_KEY=sk-xxxxx
# OPENAI_MODEL=gpt-4o-mini
```

### 3. 启动 Ollama（如果使用本地模型）

```bash
# 安装 Ollama：https://ollama.com
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
ollama serve
```

### 4. 初始化数据库

```bash
# 确保 PostgreSQL 已运行，然后生成模拟数据
cd nl2sql-bi-agent
python -m scripts.generate_mock_data
```

### 5. 构建向量索引

```bash
# 方式一：API 接口构建
curl -X POST http://localhost:8000/api/v1/index/build?drop=true

# 方式二：Python 脚本
python -c "from backend.rag.retriever import UnifiedRetriever; UnifiedRetriever().build_all_indexes(drop_existing=True)"
```

### 6. 启动服务

```bash
# 后端（端口 8000）
cd nl2sql-bi-agent
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8000

# 前端（新终端，端口 5173）
cd frontend
npm run dev
```

访问 `http://localhost:5173` 即可使用。

---

## 核心功能演示

### 支持的查询类型

```
✅ 指标查询：本周开了多少次会？
✅ 趋势分析：每天会议数量趋势如何？
✅ 部门对比：各部门会议时长对比
✅ TOP N 分析：开会时长最多的 10 个用户
✅ 同比环比：本月与上月会议数量对比
✅ 分布分析：各部门通话接通率
✅ 时段分析：每小时消息发送量（活跃时段）
✅ 设备分布：桌面端/移动端使用占比
✅ 质量监控：每日质量评分和连接失败趋势
✅ 综合查询：本周各部门会议 + 通话 + 消息联合分析
```

### 示例问题

| 用户问题 | 生成 SQL 意图 |
|---------|-------------|
| 本周各部门开了多少次会？ | 部门 × 会议数 GROUP BY |
| 最近一个月通话接通率是多少？ | 接通数 / 总通话数 |
| 每天消息发送量趋势如何？ | DATE × 消息数 折线图 |
| 会议质量最好的部门是哪个？ | 部门 × AVG(quality_score) |
| 用了多久 workspace？ | SUM(total_active_time_seconds) |

---

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/query` | POST | 同步查询（返回完整结果） |
| `/api/v1/query/stream` | POST | 流式查询（SSE，实时展示思考过程） |
| `/api/v1/index/build` | POST | 构建向量索引 |
| `/api/v1/schema/stats` | GET | 获取 Schema 索引统计 |

---

## 数据库 Schema

共 **10 张表**（4 维度 + 6 事实）：

**维度表：** `dim_tenant`（租户）、`dim_user`（用户）、`dim_meeting_room`（会议室）、`dim_promotion`

**事实表：** `fact_meeting`（会议）、`fact_meeting_participant`（参会者）、`fact_calling`（通话）、`fact_workspace`（工作空间）、`fact_messaging`（消息）、`fact_device_usage`（设备）、`fact_quality`（质量）

---

## RAG 检索策略

系统使用**三路检索**同时为 LLM 提供上下文：

1. **Schema 检索** — 用户问"会议时长" → 命中 `fact_meeting.actual_duration_seconds`
2. **指标库检索** — 用户问"营收" → 命中业务指标定义（别名映射）
3. **SQL 示例检索** — 用户问"各部门趋势" → 命中参考 SQL 模板

---

## 项目结构

```
nl2sql-bi-agent/
├── backend/
│   ├── config.py              # 全局配置（.env 加载）
│   ├── main.py                # FastAPI 入口
│   ├── schemas/
│   │   ├── query.py           # Pydantic 请求/响应模型
│   │   └── saas_bi_schema.py  # PostgreSQL 数据库 Schema 定义
│   ├── rag/
│   │   ├── embedding.py        # 嵌入模型管理（Ollama/OpenAI/HuggingFace）
│   │   ├── schema_indexer.py   # Schema 向量化存入 Milvus
│   │   ├── metrics_library.py  # 业务指标库（25+ 指标）
│   │   ├── sql_examples.py     # SQL 示例库（15+ 参考 SQL）
│   │   └── retriever.py        # 统一检索器（三路检索）
│   ├── agents/
│   │   └── nl2sql_agent.py    # LangGraph 状态机（6 个节点）
│   ├── tools/
│   │   └── sql_executor.py     # SQL 执行器（PostgreSQL/SQLite）
│   ├── services/
│   │   └── conversation.py     # 会话上下文管理
│   └── api/
│       └── routes.py           # API 路由
├── frontend/
│   └── src/
│       ├── views/QueryPage.vue  # 主页面（流式输出 + 图表）
│       └── api/query.ts          # API 调用层
├── scripts/
│   ├── init_db.sql             # PostgreSQL 建表脚本
│   └── generate_mock_data.py   # 模拟数据生成
├── data/
│   ├── milvus/                  # Milvus Lite 数据目录
│   └── db/                      # SQLite 数据目录（备用）
├── requirements.txt
└── README.md
```

---

## 学习路线

这个项目覆盖了以下核心技术点：

```
阶段 1：RAG 基础（Week 1-2）
  ├── 向量数据库原理（Milvus / ChromaDB）
  ├── Embedding 模型（Ollama / OpenAI / HuggingFace）
  ├── Chunk 策略（表级 chunk + 字段级 chunk）
  ├── 混合检索（向量 + 关键词）
  └── 多路召回（RAG Fusion）

阶段 2：LLM 应用开发（Week 3-4）
  ├── Prompt Engineering（系统提示词、Few-shot）
  ├── LangChain / LangGraph（Agent 编排框架）
  ├── 状态机设计（意图识别 → Schema 检索 → SQL 生成 → 校验 → 执行）
  ├── 流式输出（SSE / Server-Sent Events）
  └── SQL 校验与自愈（LLM-as-Judge）

阶段 3：BI 系统工程（Week 5-6）
  ├── PostgreSQL（Schema 设计、索引优化、多租户隔离）
  ├── FastAPI（路由设计、中间件、错误处理）
  ├── 图表推荐引擎（数据特征分析 + LLM 决策）
  ├── 数据可视化（ECharts / Apache ECharts）
  └── 多租户安全（tenant_id 强制过滤）

阶段 4：高级优化（Week 7-8）
  ├── SQL 纠正（Self-Correction Loop）
  ├── 缓存策略（查询结果缓存 / LLM 响应缓存）
  ├── 并发优化（连接池 / 异步 IO）
  ├── 微服务拆分（Agent 服务 / 执行服务 / 检索服务）
  └── Observability（链路追踪、日志、监控）
```

---

## 常见问题

**Q: Milvus Lite 需要 Docker 吗？**
> 不需要。Milvus Lite 是纯 Python 包，直接 `pip install pymilvus` 即可，数据存储在本地文件。

**Q: 没有 Ollama 怎么办？**
> 在 `.env` 中设置 `USE_OLLAMA=false` 并填入 `OPENAI_API_KEY`，系统会自动切换到 OpenAI API。

**Q: 没有 PostgreSQL 怎么办？**
> 系统默认使用 PostgreSQL，但 `config.py` 支持切换到 SQLite 模式（修改 `DB_TYPE=sqlite`），无需安装数据库。

**Q: 模拟数据如何生成？**
> 运行 `python -m scripts.generate_mock_data`，会自动建表并插入 ~3000 条模拟数据（50 用户、500 会议、800 通话、2000 消息等）。

---

## License

MIT
