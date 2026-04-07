# Day 22 — 指标库扩展

## 今日目标

给 NL2SQL 的指标库添加新指标，理解业务指标如何驱动 LLM 生成正确 SQL。

## 练习 22-1：添加"会议效率"指标（必做）

修改 `backend/rag/metrics_library.py`，在 `BUSINESS_METRICS` 列表里添加：

```python
{
    "metric_id": "meeting_efficiency",
    "metric_name": "会议效率",
    "aliases": ["会议效率", "会议准时率", "会议超时率"],
    "definition_desc": "实际会议时长 / 预定会议时长",
    "applicable_scenes": ["会议迟到分析", "会议效率评估"],
    "table_used": ["fact_meeting"],
    "calculation": "actual_duration / scheduled_duration",
},
```

---

## 练习 22-2：测试新指标（必做）

重启服务后，用 NL2SQL 问"各部门会议效率"或"哪些部门会议经常超时"，看 Agent 能不能理解并生成相关 SQL。

新建 `day22_test.py` 记录测试结果。

---

## 练习 22-3：修改记录（必做）

在 `day22/change_record.md` 里记录修改内容。
