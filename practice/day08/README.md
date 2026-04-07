# Day 08 — HTTP 请求 & API

## 今日目标

理解 HTTP、REST API，Python 的 `requests` 库调用 NL2SQL 接口。

## 练习 8-1：调用 NL2SQL API（必做）

新建 `day8_api.py`：

```python
import requests

BASE_URL = "http://localhost:8001/api/v1"

# 健康检查
resp = requests.get(f"{BASE_URL}/health")
print("健康检查:", resp.json())

# 发查询
resp = requests.post(f"{BASE_URL}/query", json={
    "question": "各部门用户平均使用时长",
    "conversation_id": None
})
result = resp.json()
print("\n查询结果：")
print("SQL:", result.get("generated_sql"))
```

**验收标准：** 能连接 API（不需要服务跑着才算完成，即使连接失败也算代码正确）。

---

## 练习 8-2：REST API 理解（必做）

新建 `day8_rest_notes.py`，回答：
- GET 和 POST 的区别是什么？
- `@router.post("/query")` 的意思是什么？
- 查 NL2SQL 的 `routes.py`，回答：`/health` 接口返回什么格式的数据？
