# Day 14 — RAG 完整流程

## 今日目标

把 Embedding + Milvus + LLM 串成完整的 RAG 流程，理解每一步在做什么。

## 练习 14-1：简化版 RAG（必做）

新建 `day14_rag.py`，用 TF-IDF 实现简化版 NL2SQL RAG：
- 存储文档（Schema 描述）
- 检索最相关的文档
- 根据检索结果生成回答

**验收标准：** 问"使用时长"能找到 fact_workspace，问"会议"能找到 fact_meeting。

---

## 练习 14-2：画 RAG 流程图（必做）

新建 `day14_flowchart.md`，用 Mermaid 语法画出 NL2SQL RAG 完整流程（至少 8 个节点）。

---

## 练习 14-3（进阶）：完整 RAG 调用

新建 `day14_full_rag.py`，调用真实的 NL2SQL Agent，感受完整的 RAG 流程。
