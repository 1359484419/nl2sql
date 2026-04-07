"""
Day 08 — 练习 8-2：REST API 理解
"""

from pathlib import Path

routes_file = Path(__file__).parent.parent.parent / "backend/api/routes.py"
content = routes_file.read_text(encoding="utf-8")

print("=" * 50)
print("  REST API 理解问答")
print("=" * 50)

print("""
问题1: GET 和 POST 的区别

GET（查）：
  - 参数在 URL 里：GET /api/query?question=各部门使用时长
  - 用于获取数据，不修改服务器状态
  - 浏览器地址栏输入的就是 GET 请求

POST（增/改）：
  - 参数在请求体里：POST /api/query  body: {"question": "..."}
  - 用于提交数据，可能修改服务器状态
  - 更安全（参数不在 URL 里暴露）
""")

# 找健康检查接口
health_section = content[content.find("@router.get(\"/health\""):content.find("\n@router", content.find("@router.get(\"/health\"")) + 1)]
print(f"\n问题2: /health 接口代码:")
print(health_section[:300])

print("""
\n问题2答案：
  - /health 接受 GET 请求
  - 返回 {"status": "ok", "version": "1.0.0"}
  - 用于健康检查：服务是否正常运行
""")

# 找 query 接口
query_section = content[content.find("@router.post(\"/query\""):content.find("\n@router", content.find("@router.post(\"/query\"")) + 1]
print(f"\n问题3: /query 接口代码:")
print(query_section[:400])

print("""
\n问题3答案：
  - /query 接受 POST 请求
  - 请求体格式：{"question": "...", "conversation_id": "..."}
  - 返回 NL2SQL 查询结果：SQL + 数据 + 图表配置
""")
