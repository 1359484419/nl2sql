# Day 12 — Embedding 向量化

## 今日目标

理解 Embedding 把文字变成数字向量的原理，用 TF-IDF 模拟实现相似度计算。

## 练习 12-1：计算语义相似度（必做）

新建 `day12_embedding.py`，用 TF-IDF 计算两句话的相似度。

**验收标准：** 输出显示"各部门使用时长"和"活跃时间"相似度高，"使用时长"和"天气"相似度低。

---

## 练习 12-2：分析 Embedding 模型配置（必做）

新建 `day12_config.py`，分析 `backend/rag/embedding.py`：
- 默认用什么 Embedding 模型？
- 向量维度是多少？
- 如果要换成 OpenAI 的 embedding，需要改什么？
