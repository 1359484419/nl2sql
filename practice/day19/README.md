# Day 19 — SQL 校验层

## 今日目标

理解 SQL 校验的两层机制：字符串规则 + EXPLAIN 真实数据库验证。

## 练习 19-1：用 EXPLAIN 验证 SQL（必做）

新建 `day19_explain.py`，用 PostgreSQL 的 `EXPLAIN (COSTS OFF)` 验证 SQL 是否有效。

**验收标准：** 正确的 SQL 显示 ✅，臆造列名的 SQL 显示 ❌。

---

## 练习 19-2：SQL 注入防护分析（必做）

新建 `day19_security.py`，理解为什么用参数化查询可以防止 SQL 注入。
