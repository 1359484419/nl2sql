"""
初始化数据库并填充四周学习计划数据
运行: cd /Users/liuzhuoran/cursor/nl2sql-bi-agent && python -m backend.learning_tracker.scripts.seed_data
"""
import uuid
from datetime import date, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import asyncio
from sqlalchemy import text
from backend.learning_tracker.core.database import engine, async_session, Base
from backend.learning_tracker.models.models import LearningDay, DailyQuestion


WEEKS = [
  {"week": 1, "title": "Python 速通 + LLM API 初体验", "subtitle": "目标：跑通项目，理解 LLM 如何「听话」", "days": [
    {"day": 1, "title": "环境搭建 + 跑通第一个 LLM 调用", "tasks": ["安装 Python 3.10+，配置虚拟环境", "安装 OpenAI SDK 或 Ollama", "发送第一条 API 调用", "尝试不同的 system prompt，观察回答差异", "git commit — 记录环境配置"], "objectives": "理解 LLM API 的基本调用方式，感受 Prompt 对输出的影响", "q_type": "single", "q_text": "在 LLM API 调用中，system prompt 和 user prompt 的主要区别是？", "options": [{"label": "A", "text": "system prompt 控制语气和角色，user prompt 是具体问题，两者作用完全不同"}, {"label": "B", "text": "system prompt 会被作为历史消息保存，user prompt 不会"}, {"label": "C", "text": "system prompt 每次调用都必须相同，user prompt 可以随时变化"}, {"label": "D", "text": "两者功能完全相同，只是叫法不同"}], "correct": "A", "explanation": "system prompt 用于设定角色、约束和全局行为；user prompt 是用户当前的问题。两者在 LLM 眼中都是输入，但语义角色不同。", "difficulty": 1},
    {"day": 2, "title": "Python 核心语法（Java 程序员重点）", "tasks": ["学装饰器（@decorator）：类比 Java 注解", "学上下文管理器（with）：类比 try-with-resources", "学 async/await：类比 Java CompletableFuture", "学字典/列表推导式", "git commit — 练习代码"], "objectives": "掌握 Python 与 Java 的概念映射，快速建立 Python 肌肉记忆", "q_type": "concept", "q_text": "用自己的话解释 Python 的装饰器（@decorator）和 Java 的注解（@Annotation）有什么本质区别？请举例说明", "options": None, "correct": None, "explanation": None, "difficulty": 2},
    {"day": 3, "title": "Prompt Engineering 核心原则", "tasks": ["学习 5 大原则：明确性、分解任务、Few-shot、角色设定、输出格式约束", "在项目中修改 SYSTEM_PROMPT", "对比不同 Prompt 下 SQL 生成质量", "git commit — Prompt 调优"], "objectives": "深刻理解 LLM 是「模式补全」而非「思考」，Prompt 是控制输出的关键", "q_type": "multiple", "q_text": "以下哪些是好的 Prompt 工程实践？（多选）", "options": [{"label": "A", "text": "在 Prompt 中给出 2-3 个输入输出示例（Few-shot）"}, {"label": "B", "text": "给 LLM 设定一个具体角色，如「你是一个资深 PostgreSQL DBA」"}, {"label": "C", "text": "Prompt 越短越好，减少 token 消耗"}, {"label": "D", "text": "明确指定输出格式，如「请以 JSON 格式返回，包含 code 和 explanation 字段」"}], "correct": "A,B,D", "explanation": "Few-shot、角色设定、明确输出格式都是有效的 Prompt 工程技巧。Prompt 不是越短越好——信息密度和结构同样重要。", "difficulty": 1},
    {"day": 4, "title": "理解 Embedding：让 AI 读懂语义", "tasks": ["理解 Embedding 本质：文本 → 数值向量", "学习 OpenAI/HuggingFace Embedding 接口", "在项目中找到 embedding.py，阅读理解", "观察「会议」和「meeting」在向量空间的相似度", "git commit — Embedding 调参"], "objectives": "理解 Embedding 把文本变成数字，数字的「距离」代表语义相似度", "q_type": "single", "q_text": "Word Embedding 的核心思想是：", "options": [{"label": "A", "text": "将单词转换为二进制编码，用于快速查找"}, {"label": "B", "text": "将单词映射为高维向量，语义相近的词向量距离更近"}, {"label": "C", "text": "将单词按字母序排列，生成唯一数字 ID"}, {"label": "D", "text": "将单词拆分为字符级别，用于拼写纠错"}], "correct": "B", "explanation": "Embedding 的核心是将离散的符号（文本）映射为连续的向量空间。语义相似的词在向量空间中距离更近，这是 RAG 检索的技术基础。", "difficulty": 1},
    {"day": 5, "title": "向量数据库：Milvus / ChromaDB", "tasks": ["理解为什么需要向量数据库", "跑通 Milvus Lite 零配置版本", "理解 ANN（近似最近邻）检索原理", "在项目中执行一次完整的 RAG 检索链路", "git commit — RAG 流程分析"], "objectives": "理解向量数据库解决的是「海量向量快速相似搜索」问题", "q_type": "single", "q_text": "向量数据库（如 Milvus）和普通关系型数据库（如 PostgreSQL）的核心区别是？", "options": [{"label": "A", "text": "向量数据库支持 SQL，向量数据库不支持"}, {"label": "B", "text": "向量数据库专门优化了高维向量的相似搜索，而关系型数据库优化了结构化数据的事务和关联查询"}, {"label": "C", "text": "向量数据库存储的是图片，向量数据库存储文本"}, {"label": "D", "text": "两者本质相同，只是向量数据库性能更好"}], "correct": "B", "explanation": "向量数据库的核心能力是 ANN（近似最近邻）搜索：在海量高维向量中找到与查询向量最相似的 Top-K 结果，关系型数据库不具备这个能力。", "difficulty": 1},
    {"day": 6, "title": "RAG 核心原理 + 项目检索链路分析", "tasks": ["完整走一遍 RAG 流程：问题→Embedding→向量检索→上下文→LLM生成", "找到 retriever.py，理解三路检索（Schema+指标+SQL示例）", "画出 RAG 流程图", "git commit — RAG 流程图和注释"], "objectives": "掌握 RAG 核心链路，理解「给 LLM 喂正确上下文」为什么有效", "q_type": "concept", "q_text": "RAG（检索增强生成）的核心价值是什么？它解决了 LLM 的哪些根本问题？", "options": None, "correct": None, "explanation": None, "difficulty": 2},
    {"day": 7, "title": "Week1 总结 + 在项目中加一个小功能", "tasks": ["建议：在 RAG 检索时打印命中的 Schema 片段（方便调试）", "写一篇 Week1 学习总结（300字）", "git commit — 你的第一个功能点", "整理 DEBUG_LOG.md"], "objectives": "本周核心：LLM 是「模式补全」，Embedding 是「语义匹配」，RAG 是「给 LLM 喂正确上下文」", "q_type": "single", "q_text": "如果想查询「过去 7 天每天的会议数量」，RAG 系统的 Schema 检索最可能命中哪个字段？", "options": [{"label": "A", "text": "fact_meeting.actual_duration_seconds（会议时长）"}, {"label": "B", "text": "fact_meeting.start_time（会议开始时间）+ COUNT(*)"}, {"label": "C", "text": "fact_calling.call_status（通话状态）"}, {"label": "D", "text": "dim_user.user_name（用户名）"}], "correct": "B", "explanation": "「每天的会议数量」需要 GROUP BY 日期并计数，核心是 start_time（时间字段）+ COUNT() 聚合，与会议时长、通话状态、用户名无关。", "difficulty": 2},
  ]},
  {"week": 2, "title": "LangGraph 状态机 + Agent 核心概念", "subtitle": "目标：理解 Agent 如何「编排」思考步骤", "days": [
    {"day": 1, "title": "理解 Agent 本质：循环 + 工具 + 记忆", "tasks": ["理解 Agent = LLM + Tool + Loop + Memory", "用 Java 类比：Agent 像 Spring Bean", "查找项目中 Agent 的定义位置", "git commit"], "objectives": "Agent 不是「智能」，是「受控的循环决策系统」", "q_type": "single", "q_text": "LLM Agent 的核心循环通常包含哪三个要素？", "options": [{"label": "A", "text": "输入 → 处理 → 输出"}, {"label": "B", "text": "思考（Think）→ 行动（Act）→ 观察（Observe）"}, {"label": "C", "text": "训练 → 推理 → 部署"}, {"label": "D", "text": "请求 → 认证 → 响应"}], "correct": "B", "explanation": "ReAct（Reason + Act）是 Agent 的经典循环：思考决定做什么 → 执行 Action → 观察结果 → 继续循环。", "difficulty": 1},
    {"day": 2, "title": "LangGraph 状态机：概念入门", "tasks": ["阅读 LangGraph 官方文档（30分钟）", "理解 StateGraph、Node、Edge、ConditionalEdge", "用生活类比：餐厅流程 = 状态机", "git commit"], "objectives": "LangGraph 用状态机解决「Agent 步骤编排」的问题", "q_type": "concept", "q_text": "LangGraph 中的 State（状态）和 Node（节点）分别代表什么？它们如何配合工作？", "options": None, "correct": None, "explanation": None, "difficulty": 2},
    {"day": 3, "title": "深度阅读 nl2sql_agent.py 状态图", "tasks": ["画出完整状态图：classify_intent→retrieve→generate→validate→execute→chart", "理解每个节点的输入/输出", "重点：State 类型定义和传递方式", "git commit — 状态图文档"], "objectives": "能向别人讲清楚 Agent 的完整决策链路", "q_type": "multiple", "q_text": "在 LangGraph 中，以下哪些可以作为节点（Node）？", "options": [{"label": "A", "text": "一个调用 LLM 生成 SQL 的函数"}, {"label": "B", "text": "一个执行 SQL 并返回结果的数据库查询函数"}, {"label": "C", "text": "一个根据条件决定下一步的路由函数（ConditionalEdge）"}, {"label": "D", "text": "一个包含复杂循环逻辑的完整子图（SubGraph）"}], "correct": "A,B,D", "explanation": "Node 必须是可执行的函数（同步或异步）；路由逻辑属于 Edge，不是 Node。B 和 D 也是 Node，只是分别对应工具调用和子图。", "difficulty": 2},
    {"day": 4, "title": "Self-Correction 循环：让 Agent 自我纠错", "tasks": ["理解 EXPLAIN 校验 + 重试机制", "找到 _route_after_validation 和 _route_after_execution", "理解失败时如何回到生成节点", "git commit — Self-Correction 分析"], "objectives": "Self-Correction 是生产级 Agent 的标配，单次生成几乎必然出错", "q_type": "single", "q_text": "在 LangGraph 中，实现「SQL 执行失败后自动重试」的最佳方式是？", "options": [{"label": "A", "text": "在 generate 节点里写一个 try-catch 循环"}, {"label": "B", "text": "在 execute 节点的边（Edge）上定义 ConditionalEdge，失败时指向 generate 节点"}, {"label": "C", "text": "把 SQL 执行写到一个无限循环里直到成功"}, {"label": "D", "text": "让 LLM 生成多个 SQL，选择第一个成功的"}], "correct": "B", "explanation": "LangGraph 的推荐模式：在 Edge 上通过条件判断决定路由。execute 失败 → 返回 generate 重试，这保持了节点的纯粹性。", "difficulty": 2},
    {"day": 5, "title": "SQL Executor：数据库连接 + SQL 注入防护", "tasks": ["理解 SQLAlchemy 的 text() 防注入机制", "对比 Java PreparedStatement", "找到 sql_executor.py 中的 execute 和 validate_with_explain", "git commit"], "objectives": "参数化查询是 SQL 安全的基石，理解其原理", "q_type": "single", "q_text": "SQLAlchemy 的 text() 函数防注入的原理是：", "options": [{"label": "A", "text": "对用户输入进行 HTML 转义"}, {"label": "B", "text": "将参数与 SQL 语句分离传输，由数据库驱动处理参数绑定"}, {"label": "C", "text": "对所有输入进行 Base64 编码"}, {"label": "D", "text": "禁止使用任何变量，只允许写死 SQL"}], "correct": "B", "explanation": "text() 使用参数绑定，参数值不参与 SQL 语句的编译过程，从根本上防止注入攻击。Java 的 PreparedStatement 原理完全相同。", "difficulty": 1},
    {"day": 6, "title": "流式输出 SSE：FastAPI + Server-Sent Events", "tasks": ["理解 SSE 和 WebSocket 的区别", "找到 routes.py 的 /query/stream 接口", "对比 Java 的 Flux / SSE 实现", "git commit — SSE 注释"], "objectives": "SSE 是服务端推送数据的轻量方案，比 WebSocket 更适合「服务端→客户端」单向流", "q_type": "single", "q_text": "Server-Sent Events (SSE) 和 WebSocket 的主要区别是：", "options": [{"label": "A", "text": "SSE 支持双向通信，WebSocket 只支持单向"}, {"label": "B", "text": "SSE 是基于 HTTP 的单向推送，WebSocket 是独立的双向协议"}, {"label": "C", "text": "SSE 的性能比 WebSocket 更好"}, {"label": "D", "text": "两者完全等价，只是 API 不同"}], "correct": "B", "explanation": "SSE 基于 HTTP 单向通道（服务端→客户端），实现简单，自动重连；WebSocket 是独立协议，支持双向通信，适合游戏/实时协作等场景。", "difficulty": 1},
    {"day": 7, "title": "Week2 总结 + 给 Agent 加一个新节点", "tasks": ["建议：在状态图中加「结果解释」节点", "画出手绘或 Mermaid 状态图", "git commit — 新节点代码", "DEBUG_LOG.md 追加"], "objectives": "本周核心：Agent = 状态机 + 工具调用 + 自我纠错", "q_type": "concept", "q_text": "LangGraph 中「边（Edge）」和「条件边（ConditionalEdge）」有什么区别？什么场景适合用 ConditionalEdge？", "options": None, "correct": None, "explanation": None, "difficulty": 2},
  ]},
  {"week": 3, "title": "RAG 进阶 + 前沿技术", "subtitle": "目标：掌握生产级 RAG 优化方法", "days": [
    {"day": 1, "title": "Chunk 策略：如何分块比什么更重要", "tasks": ["学固定窗口、语义段落、层级分块三种策略", "分析项目的 Schema 分块方式（表级 vs 字段级）", "在 schema_indexer.py 中添加新分块策略", "git commit"], "objectives": "Chunk 太大 → 上下文溢出；太小 → 语义不完整。两者都要控制好。", "q_type": "single", "q_text": "在 RAG 系统中，如果 Chunk 设置过大，会导致什么问题？", "options": [{"label": "A", "text": "Embedding 计算变慢，但检索精度更高"}, {"label": "B", "text": "上下文窗口溢出，LLM 无法处理，且噪声过多导致检索精度下降"}, {"label": "C", "text": "向量数据库存储空间不足"}, {"label": "D", "text": "不会产生任何问题"}], "correct": "B", "explanation": "大 Chunk 浪费有限的上下文窗口，同时引入过多无关内容（噪声），降低答案质量。", "difficulty": 1},
    {"day": 2, "title": "混合检索：向量 + BM25 关键词", "tasks": ["理解纯向量检索对专有名词不友好的问题", "学习 BM25 算法原理", "理解 RRF 融合方法", "git commit — 混合检索实现"], "objectives": "混合检索 = 向量检索（语义）+ BM25（关键词），两者互补", "q_type": "single", "q_text": "BM25 相比纯向量检索，更擅长处理哪种查询？", "options": [{"label": "A", "text": "语义相似但用词不同的查询，如「不开心」和「情绪低落」"}, {"label": "B", "text": "精确的专有名词或数据库列名，如 fact_meeting、total_active_time_seconds"}, {"label": "C", "text": "模糊的、多义的、需要推理的查询"}, {"label": "D", "text": "所有类型的查询 BM25 都比向量检索更好"}], "correct": "B", "explanation": "BM25 是基于词频的精确匹配，适合专有名词、列名等向量模型容易误匹配的词。", "difficulty": 2},
    {"day": 3, "title": "重排序（ReRanking）：精排优于粗排", "tasks": ["理解两阶段检索：粗排（向量 ANN）→ 精排（Cross-Encoder）", "学习 Cohere Rerank 或 BGE-Reranker", "尝试给项目加一个 ReRanker", "git commit"], "objectives": "Top-K 召回后用重排序模型精选 Top-3，效果显著好于直接取 Top-K", "q_type": "concept", "q_text": "两阶段检索（粗排+精排）的设计动机是什么？为什么不直接用向量检索取 Top-3？", "options": None, "correct": None, "explanation": None, "difficulty": 2},
    {"day": 4, "title": "Function Calling / Tool Use：让 Agent 调用工具", "tasks": ["学习 OpenAI Function Calling 格式", "对比 LangGraph 的 Tool 机制", "理解项目中 Agent 调用 SQL Executor 就是 Function Calling", "git commit"], "objectives": "Function Calling 是最实用的 Agent 能力，让 LLM 有能力调用任意外部 API", "q_type": "single", "q_text": "在 LangGraph 中，Tool（工具）的核心作用是：", "options": [{"label": "A", "text": "提供用户界面交互"}, {"label": "B", "text": "让 Agent 能够执行外部操作（查数据库、调用 API等），并将结果返回给 LLM 继续决策"}, {"label": "C", "text": "替代 LLM 做推理"}, {"label": "D", "text": "存储 Agent 的记忆"}], "correct": "B", "explanation": "Tool 是 Agent 连接外部世界的桥梁：LLM 决定「需要调用工具」→ 执行 Tool → 结果返回 LLM → LLM 继续决策。", "difficulty": 1},
    {"day": 5, "title": "多租户安全：RAG 中的数据隔离", "tasks": ["理解 RAG 场景下的多租户问题", "理解 Agent 用 org_id 过滤数据", "分析项目中的多租户隔离实现", "git commit"], "objectives": "多租户隔离是 SaaS 的生命线，任何数据泄露都是严重问题", "q_type": "single", "q_text": "在 NL2SQL BI 系统中，防止 A 公司看到 B 公司数据的核心手段是：", "options": [{"label": "A", "text": "使用不同的向量数据库实例"}, {"label": "B", "text": "在 SQL 查询中强制拼接 org_id 过滤条件，由后端自动注入"}, {"label": "C", "text": "让用户每次查询时手动输入公司 ID"}, {"label": "D", "text": "使用不同的 Embedding 模型"}], "correct": "B", "explanation": "最简洁有效的方案是后端在生成 SQL 后统一注入 org_id 过滤条件（白名单模式），用户无感知，无法绕过。", "difficulty": 1},
    {"day": 6, "title": "评估体系：如何衡量 RAG 质量", "tasks": ["学习 RAG 三指标：Context Precision/Recall + Answer Correctness", "学习 LLM-as-Judge 自动评估", "为项目写一个 SQL 正确性评估脚本", "git commit — eval 脚本"], "objectives": "没有评估就没有优化。RAG 质量必须可量化才能持续改进。", "q_type": "concept", "q_text": "LLM-as-Judge 是什么？用它评估 RAG 输出的优势和潜在问题是什么？", "options": None, "correct": None, "explanation": None, "difficulty": 2},
    {"day": 7, "title": "Week3 总结 + RAG 优化实战", "tasks": ["推荐：给 RAG 加上 BM25 混合检索", "写 Week3 学习总结（300字）", "git commit — RAG 优化", "DEBUG_LOG.md 追加"], "objectives": "本周核心：RAG 质量 = Chunk 策略 × 检索质量 × 上下文利用率", "q_type": "multiple", "q_text": "以下哪些优化可以提升 RAG 系统的检索质量？", "options": [{"label": "A", "text": "使用混合检索（向量+BM25）"}, {"label": "B", "text": "使用重排序（Reranker）精选 Top 结果"}, {"label": "C", "text": "增加 Embedding 模型的维度（从 384 维提升到 1536 维）"}, {"label": "D", "text": "在检索前对用户问题做 Query Rewriting/Decomposition"}], "correct": "A,B,D", "explanation": "A+B 是检索阶段的优化，D 是查询理解优化。C 维度不是越多越好，过高维度反而导致「维度灾难」。", "difficulty": 2},
  ]},
  {"week": 4, "title": "前沿扩展 + 项目收尾", "subtitle": "目标：接触最新技术方向，确定个人技术栈", "days": [
    {"day": 1, "title": "MCP（Model Context Protocol）：Agent 互联标准", "tasks": ["阅读 MCP 官方文档", "理解 Host/Client/Server 架构", "与 Java SPI 机制做对比", "git commit"], "objectives": "MCP 是最火热的 Agent 工具互联协议，类似 USB-C 的 AI 版本", "q_type": "concept", "q_text": "MCP（Model Context Protocol）的核心设计目标是什么？它解决了什么问题？", "options": None, "correct": None, "explanation": None, "difficulty": 2},
    {"day": 2, "title": "Memory / 长期记忆：让 Agent 记住上下文", "tasks": ["理解 Agent Memory 三层：Working/Session/Long-term", "用向量数据库实现跨会话记忆", "在项目中实现「记住上次查询」能力", "git commit"], "objectives": "Memory 让 Agent 从「单次问答」进化到「持续对话」", "q_type": "single", "q_text": "Session Memory 和 Long-term Memory 的主要区别是：", "options": [{"label": "A", "text": "Session Memory 存储在向量数据库，Long-term Memory 存储在内存"}, {"label": "B", "text": "Session Memory 在会话结束时清空，Long-term Memory 持久化跨会话"}, {"label": "C", "text": "Session Memory 比 Long-term Memory 更大"}, {"label": "D", "text": "两者没有本质区别，只是叫法不同"}], "correct": "B", "explanation": "Session Memory 只在当前会话中有效；Long-term Memory 通过向量数据库持久化，实现跨会话记住用户的偏好、历史问题等。", "difficulty": 1},
    {"day": 3, "title": "LLM Observability：LangSmith / OpenTelemetry", "tasks": ["理解 LLM 可观测性三件套：Trace + Metrics + Logging", "用 LangSmith 追踪 Agent 节点耗时和 token 消耗", "对比 Java 的 SkyWalking/Jaeger", "git commit"], "objectives": "可观测性是生产级 AI 应用的基础，不知道 Agent 在干什么就无法优化", "q_type": "single", "q_text": "LLM Tracing（链路追踪）主要用于解决什么问题？", "options": [{"label": "A", "text": "加快 LLM 的推理速度"}, {"label": "B", "text": "追踪 Agent 的每个决策步骤、耗时、token 消耗，便于性能分析和错误定位"}, {"label": "C", "text": "自动修复 LLM 的幻觉问题"}, {"label": "D", "text": "减少 LLM 的 API 调用成本"}], "correct": "B", "explanation": "Tracing 记录 Agent 每个节点的输入、输出、耗时和 token 消耗，帮助开发者理解 Agent 行为、定位性能瓶颈和错误。", "difficulty": 1},
    {"day": 4, "title": "本地模型：Ollama / vLLM / LM Studio", "tasks": ["尝试用 Ollama 跑 qwen2.5:14b", "对比本地模型 vs GPT-4o 的效果差距", "评估推理速度和显存需求", "git commit"], "objectives": "本地模型是数据隐私和成本控制的好方案，适合学习和轻量应用", "q_type": "concept", "q_text": "vLLM 的 PagedAttention 技术主要解决了什么问题？", "options": None, "correct": None, "explanation": None, "difficulty": 2},
    {"day": 5, "title": "项目总结：性能优化 + 工程化", "tasks": ["实现 LLM 响应缓存", "调优向量检索 TopK 参数", "分析连接池配置", "git commit — 优化代码"], "objectives": "「AI Native 应用」和传统应用的区别：传统是确定逻辑，AI 是概率输出，需要额外的容错设计", "q_type": "single", "q_text": "在 NL2SQL 系统中，加入 SQL 执行结果缓存的主要目的是：", "options": [{"label": "A", "text": "减少数据库查询压力，加速响应"}, {"label": "B", "text": "A + 避免对相同问题重复调用 LLM，节省 token 成本"}, {"label": "C", "text": "将 SQL 结果永久存储方便日后查询"}, {"label": "D", "text": "作为 LLM 的长期记忆"}], "correct": "B", "explanation": "缓存同时解决两个问题：减少数据库查询（性能）和避免重复调用 LLM 生成相同 SQL（成本）。", "difficulty": 1},
    {"day": 6, "title": "技术博客 + 简历更新", "tasks": ["写一篇技术博客（1500+ 字）", "博客主题：「用 LangGraph + RAG 打造 NL2SQL 查询助手」", "更新简历项目经历", "整理 GitHub 项目 README"], "objectives": "写下来才是真正学会。能讲清楚 → 能写清楚 → 真正理解", "q_type": "concept", "q_text": "从 Java 转向 AI Agent 开发，最大的思维方式转变是什么？请从「确定性 vs 概率性」的角度分析。", "options": None, "correct": None, "explanation": None, "difficulty": 3},
    {"day": 7, "title": "Week4 收尾 + 新项目构思", "tasks": ["完成 DEBUG_LOG.md 最终总结", "整理 30 天学习笔记", "构思下一个 AI 项目", "给自己一个 milestone 庆祝！"], "objectives": "4 周不是终点，而是起点。AI 技术日新月异，保持持续学习的习惯比学什么更重要。", "q_type": "concept", "q_text": "基于这 4 周的学习，你认为 AI Agent 在你的工作场景中最可能落地哪个方向？为什么？", "options": None, "correct": None, "explanation": None, "difficulty": 3},
  ]},
]


async def seed():
    print("开始初始化数据库...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("表创建完成")

    async with async_session() as session:
        await session.execute(text("TRUNCATE TABLE daily_questions CASCADE"))
        await session.execute(text("TRUNCATE TABLE learning_days CASCADE"))
        await session.commit()
        print("旧数据已清理")

        start_date = date(2026, 4, 6)
        total_days = 0

        for week_data in WEEKS:
            for day_data in week_data["days"]:
                day_date = start_date + timedelta(days=total_days)
                day_id = str(uuid.uuid4())

                learning_day = LearningDay(
                    id=day_id,
                    week_number=week_data["week"],
                    day_number=day_data["day"],
                    date=day_date,
                    title=day_data["title"],
                    subtitle=week_data["subtitle"],
                    tasks=day_data["tasks"],
                    objectives=day_data.get("objectives"),
                    git_filter=None,
                    is_rest_day=False,
                )
                session.add(learning_day)

                question = DailyQuestion(
                    id=str(uuid.uuid4()),
                    day_id=day_id,
                    question_type=day_data["q_type"],
                    question_text=day_data["q_text"],
                    options=day_data["options"],
                    correct_answer=day_data.get("correct"),
                    explanation=day_data.get("explanation"),
                    difficulty=day_data.get("difficulty", 1),
                )
                session.add(question)
                total_days += 1

        await session.commit()

    print(f"数据初始化完成！共插入 {total_days} 个学习日，{total_days} 道题目")
    print(f"开始日期：{start_date}")
    print(f"结束日期：{start_date + timedelta(days=total_days - 1)}")


if __name__ == "__main__":
    asyncio.run(seed())
