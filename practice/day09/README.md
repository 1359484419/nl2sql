# Day 09 — 数据库 SQL

## 今日目标

理解 SQL 的核心用法，为理解 NL2SQL 的"生成 SQL"打下基础。

## 练习 9-1：SQL 查询练习（在 DataGrip 里运行）

在 DataGrip 里打开 NL2SQL 的 PostgreSQL 数据库，运行以下 SQL：

```sql
-- 1. 查所有数据（限制10条）
SELECT * FROM fact_workspace LIMIT 10;

-- 2. 查指定租户
SELECT * FROM fact_workspace WHERE org_id = 'demo_org_001';

-- 3. 按用户分组，计算平均活跃时长
SELECT user_id,
       AVG(total_active_time_seconds) as avg_time
FROM fact_workspace
WHERE org_id = 'demo_org_001'
GROUP BY user_id
ORDER BY avg_time DESC
LIMIT 5;

-- 4. 各部门（user_id前3位）的平均活跃时长
SELECT SUBSTRING(user_id, 1, 3) as dept,
       AVG(total_active_time_seconds) as avg_time
FROM fact_workspace
WHERE org_id = 'demo_org_001'
GROUP BY SUBSTRING(user_id, 1, 3)
ORDER BY avg_time DESC;
```

把每条 SQL 的运行结果截图保存到 `day09/` 文件夹。

---

## 练习 9-2：NL2SQL 生成的 SQL 分析（必做）

新建 `day9_nl2sql_sql.py`，写代码：
1. 调用 NL2SQL API 问"各部门使用时长总和"
2. 把生成的 SQL 打印出来
3. 统计 SQL 里有多少个 SELECT/WHERE/GROUP BY

---

## 练习 9-3（可选）：把 SQL 结果转成图表

用 Python 把 SQL 查询结果打印成 ASCII 表格。
