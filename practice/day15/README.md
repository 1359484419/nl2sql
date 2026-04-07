# Day 15 — Prompt Engineering

## 今日目标

掌握 Prompt Engineering 的核心原则：角色设定、Few-shot、格式约束、严禁规则。

## 练习 15-1：Prompt 对比实验（必做）

新建 `day15_prompts.py`，对比两个 Prompt 生成的 SQL 效果。

**验收标准：** 详细 Prompt 生成的 SQL 没有臆造列名，模糊 Prompt 可能出现。

---

## 练习 15-2：给 NL2SQL 加一条 Prompt 规则（必做）

修改 `backend/agents/nl2sql_agent.py` 的 SYSTEM_PROMPT，加一条新规则：

```
【严禁】如果用户问的是平均数，SQL 里必须用 AVG() 聚合函数
如果问的是总数，必须用 SUM()
如果问的是计数，必须用 COUNT()
```

重启服务后测试，用 DEBUG_LOG.md 记录结果。

---

## 练习 15-3：修改记录（必做）

新建 `day15_change_record.md`，记录你修改了什么、为什么改、改后的效果。
