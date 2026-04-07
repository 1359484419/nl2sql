# Day 13 — Milvus 向量数据库

## 今日目标

学会用 Milvus 存储和检索向量，理解向量数据库的核心操作。

## 练习 13-1：Milvus 基础操作（必做）

新建 `day13_milvus.py`，实现：创建 Collection → 插入向量 → 检索。

**验收标准：** 运行后能找到语义最相近的文本（活跃用户时长 → fact_workspace）。

---

## 练习 13-2：分析 NL2SQL 的 Milvus 配置（必做）

新建 `day13_config.py`，分析 `backend/config.py`：
- Milvus 数据存在哪里？
- Schema collection 和 Metrics collection 分别叫什么？
- 用的是什么索引类型和相似度度量？
