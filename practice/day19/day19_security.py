"""
Day 19 — 练习 19-2：SQL 注入防护分析
"""

print("=" * 55)
print("  SQL 注入攻击 vs 参数化查询")
print("=" * 55)

print("""
❌ 危险方式：字符串拼接（SQL 注入漏洞）

user_input = "demo_org_001; DROP TABLE fact_workspace; --"
sql = f"SELECT * FROM fact_workspace WHERE org_id = '{user_input}'"
# 执行结果：
# SELECT * FROM fact_workspace WHERE org_id = 'demo_org_001; DROP TABLE...'
#                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                         这整段变成了 SQL 代码，危险！
""")

print("""
✅ 安全方式：参数化查询

from sqlalchemy import text

# 方式1：? 占位符
sql = text("SELECT * FROM fact_workspace WHERE org_id = :org_id")
result = conn.execute(sql, {"org_id": user_input})

# 方式2：%s 占位符
sql = "SELECT * FROM fact_workspace WHERE org_id = %s"
cursor.execute(sql, (user_input,))

# 原理：参数值不会被当成 SQL 代码执行
# 输入 "demo_org_001; DROP TABLE..." 会被当作字符串原样存储
""")

print("""
NL2SQL 项目里怎么做的？

在 sql_executor.py 里：
    with self._engine.connect() as conn:
        result = conn.execute(text(sql), params)

text() = SQLAlchemy 的参数化查询包装器
params = 参数字典
""")
