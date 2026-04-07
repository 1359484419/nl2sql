# NL2SQL BI Agent — Debug Log & 学习笔记

> 本文档记录：① NL2SQL 项目调试过程中遇到的问题，② Python 基础阶段练习时遇到的错误，③ 每天的学习心得。
> 格式：【日期】问题/心得 → 根因 → 修复/答案 → 验证
> 这是你最好的老师。每个问题都是一次进步。

---

## 目录
1. [NL2SQL 项目问题](#nl2sql-项目问题)
2. [Python 基础练习问题](#python-基础练习问题)
3. [AI 概念理解笔记](#ai-概念理解笔记)
4. [Agent / LangGraph 笔记](#agent--langgraph-笔记)
5. [项目改进记录](#项目改进记录)

---

## NL2SQL 项目问题

### 1. greenlet 模块缺失

**发生日期：** 2026-04-07

**问题描述：**
```
ValueError: the greenlet library is required to use this function. No module named 'greenlet'
```

**根因：** SQLAlchemy 的异步驱动需要 greenlet 协程库。

**修复：**
```bash
pip install greenlet
```

---

### 2. `day_date.date()` AttributeError

**发生日期：** 2026-04-07

**问题描述：**
```
AttributeError: 'datetime.date' object has no attribute 'date'
```

**根因：** `day_date` 从数据库读出来已经是 `date` 对象，不需要再调 `.date()`。

**修复（routes.py line 101）：**
```python
# 修改前
commits = git_service.get_commits_by_date(str(day_date.date()))

# 修改后
commits = git_service.get_commits_by_date(str(day_date))
```

---

### 3. SQL 列名臆造问题

**发生日期：** 2026-04-06

**问题描述：**
Agent 生成的 SQL 使用了不存在的列名：`usage_duration_seconds`（正确应为 `total_active_time_seconds`）

**根因：** LLM 生成 SQL 时没有严格对照 Schema。

**修复：**
- 强化 `nl2sql_agent.py` 的 SYSTEM_PROMPT，明确列出可用字段
- `sql_executor.py` 增加 `validate_with_explain()` 方法

---

### 4. 「SQL 有效」假阳性

**发生日期：** 2026-04-06

**问题描述：** UI 显示「SQL 有效 ✅」，但 DataGrip 执行报错。

**根因：** `sql_validation_node()` 只做字符串检查，没有连接真实数据库。

**修复：** 增加 PostgreSQL `EXPLAIN (COSTS OFF)` 真实数据库校验。

---

### 5. org_id 不一致

**发生日期：** 2026-04-06

**根因：** Mock 数据用 `demo_org_001`，API 硬编码 `demo_org`。

**修复：** 统一改为 `demo_org_001`。

---

### 6. 数据稀疏

**发生日期：** 2026-04-06

**修复：** 重写 `generate_mock_data.py`，数据量从 500 条增加到 51,390 条。

---

## Python 基础练习问题

> 从 Day 1 开始，每当你练习时遇到错误，记录在这里。
> 格式：Day X - 练习名 → 错误信息 → 解决方法

<!-- ═══════════════════════════════════════════════ -->
<!-- 你在练习时遇到的问题追加在下面：             -->
<!--                                               -->
<!-- ## Day X - 练习名                             -->
<!-- **问题描述：**                                -->
<!-- ```                                         -->
<!-- 错误信息...                                   -->
<!-- ```                                          -->
<!-- **根因：**                                    -->
<!-- ...                                          -->
<!-- **解决：**                                    -->
<!-- ...                                          -->
<!-- ═══════════════════════════════════════════════ -->


---

## AI 概念理解笔记

> 用大白话记录你对 AI 概念的理解。讲不清楚 = 没学会。

<!-- ═══════════════════════════════════════════════ -->
<!-- 追加你的 AI 概念理解笔记：                    -->
<!--                                               -->
<!-- ### [日期] LLM 是什么？                      -->
<!-- 我的理解：                                    -->
<!-- ...                                           -->
<!--                                               -->
<!-- ### [日期] Embedding 是什么？                -->
<!-- 我的理解：                                    -->
<!-- ...                                           -->
<!--                                               -->
<!-- ### [日期] RAG 是什么？                       -->
<!-- 我的理解：                                    -->
<!-- ...                                           -->
<!-- ═══════════════════════════════════════════════ -->


---

## Agent / LangGraph 笔记

> 记录你对 Agent 状态机、重试机制的理解。

<!-- ═══════════════════════════════════════════════ -->
<!-- 追加笔记：                                     -->
<!--                                               -->
<!-- ### [日期] NL2SQL 状态机节点说明               -->
<!-- 节点名 → 作用                                -->
<!-- ...                                           -->
<!--                                               -->
<!-- ### [日期] Self-Correction 流程               -->
<!-- ...                                           -->
<!-- ═══════════════════════════════════════════════ -->


---

## 项目改进记录

> 记录你在 Week 5 加的每个新功能。

### Day 21 - 新增 Agent 节点
**功能：** 给 Agent 加了 `result_explanation` 节点
**修改文件：** `backend/agents/nl2sql_agent.py`
**效果：** API 响应出现自然语言解读字段
**遇到的问题：** ...
**解决：** ...

### Day 22 - 指标库扩展
**功能：** 添加了 `meeting_efficiency` 指标
**修改文件：** `backend/rag/metrics_library.py`
**效果：** Agent 能理解"会议效率"相关提问
**遇到的问题：** ...
**解决：** ...

### Day 23 - BM25 混合检索
**功能：** 给 RAG 加了 BM25 关键词检索
**修改文件：** `backend/rag/retriever.py`
**效果：** 列名/表名检索更准确
**遇到的问题：** ...
**解决：** ...

---

## 后续追加格式

```markdown
## Day N - 练习名

**问题描述：**
```
错误信息或问题描述
```

**根因：**
...

**解决/答案：**
...

**验证：**
...

---
```

