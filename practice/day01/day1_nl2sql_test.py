"""
Day 01 — 练习 1-3：测试 NL2SQL 后端
目标：用 requests 调用 API，确认服务正常运行
"""

import requests

BASE_URL = "http://localhost:8001/api/v1"

# 1. 健康检查
resp = requests.get(f"{BASE_URL}/health")
print("健康检查:", resp.json())

# 2. 发送查询
resp = requests.post(f"{BASE_URL}/query", json={
    "question": "各部门用户平均使用时长",
    "conversation_id": None
})
result = resp.json()
print("\n查询结果:")
print("  SQL:", result.get("generated_sql", "无"))
rows = result.get("data", {}).get("rows", [])
print(f"  数据行数: {len(rows)}")
