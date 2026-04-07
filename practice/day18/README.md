# Day 18 — Self-Correction 自我纠错

## 今日目标

理解 Agent 的"试错→反馈→修正"循环，理解 retry 机制。

## 练习 18-1：带重试的 API 调用（必做）

新建 `day18_retry.py`，实现一个模拟带重试的 API 调用。

**验收标准：** 运行后能看到"第1次失败 → 重试 → 第2次成功"的过程。

---

## 练习 18-2：分析 NL2SQL 重试逻辑（必做）

新建 `day18_retry_analysis.py`，分析 NL2SQL Agent 的重试机制：
- retry_count 最大是多少？
- 什么情况下触发重试？
- 重试 3 次后仍然失败怎么办？
