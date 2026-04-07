"""
Day 09 — 练习 9-2：分析 NL2SQL 生成的 SQL
"""

import requests

BASE_URL = "http://localhost:8001/api/v1"

questions = [
    "各部门用户平均使用时长",
    "过去7天活跃用户数",
    "各部门会议总时长",
]

print("=" * 60)
print("  NL2SQL 生成的 SQL 分析")
print("=" * 60)

for q in questions:
    print(f"\n问题: {q}")
    try:
        resp = requests.post(f"{BASE_URL}/query", json={"question": q, "conversation_id": None}, timeout=30)
        result = resp.json()
        sql = result.get("generated_sql", "无")

        # 统计关键字
        sql_upper = sql.upper()
        select_count = sql_upper.count("SELECT")
        where_count = sql_upper.count("WHERE")
        group_by_count = sql_upper.count("GROUP BY")
        order_by_count = sql_upper.count("ORDER BY")
        limit_count = sql_upper.count("LIMIT")

        print(f"  SQL: {sql[:100]}{'...' if len(sql) > 100 else ''}")
        print(f"  关键字统计: SELECT={select_count} WHERE={where_count} GROUP={group_by_count} ORDER={order_by_count} LIMIT={limit_count}")

        # 提取表名
        import re
        tables = re.findall(r"FROM\s+(\w+)", sql_upper)
        print(f"  使用的表: {tables}")
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
