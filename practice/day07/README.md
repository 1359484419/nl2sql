# Day 07 — 文件读写 & JSON

## 今日目标

学会用 Python 读写文件，理解 JSON 和 dict 的关系。

## 练习 7-1：JSON 数据读写（必做）

新建 `day7_json.py`：

```python
import json

data = {
    "name": "NL2SQL Agent",
    "version": "1.0",
    "features": ["RAG", "LangGraph", "SSE"]
}

# 保存到文件
json_str = json.dumps(data, ensure_ascii=False, indent=2)
with open("data.json", "w", encoding="utf-8") as f:
    f.write(json_str)

# 读回来
with open("data.json", encoding="utf-8") as f:
    loaded = json.load(f)

# 验证
assert loaded["name"] == data["name"]
print("JSON 读写成功！")
```

**验收标准：** 运行后在 day07 文件夹里生成 `data.json`，内容正确。

---

## 练习 7-2：读取 NL2SQL Schema 并格式化（必做）

新建 `day7_schema_table.py`，把 `fact_workspace` 的所有字段打印成表格格式。
