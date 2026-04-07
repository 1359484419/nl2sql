"""
Day 03 — 练习 3-2：理解 NL2SQL SQL 校验逻辑
任务：读 sql_executor.py，用大白话描述校验逻辑
"""

from pathlib import Path

sql_file = Path(__file__).parent.parent.parent / "backend/tools/sql_executor.py"
content = sql_file.read_text(encoding="utf-8")

# 找到校验函数
start = content.find("def validate")
end = content.find("\ndef ", start + 1)
if end == -1:
    end = len(content)
validate_fn = content[start:end]

print("SQL 校验函数代码片段：")
print(validate_fn[:800])
print("\n" + "=" * 50)

# 用大白话描述逻辑
print("\n我的理解（用大白话写出来）：")
print("""
SQL 校验逻辑的作用是：在执行 SQL 之前，检查它是否"看起来合理"。

具体检查：
1. SQL 必须以 SELECT 开头（防止注入攻击）
2. SQL 必须包含 org_id 过滤条件（多租户隔离）
3. 如果有错误，把所有错误信息收集起来
4. 如果有错误，返回 (False, 错误信息)
5. 如果没有错误，返回 (True, None)
""")

# 实际验证
test_sqls = [
    "SELECT * FROM fact_workspace WHERE org_id = 'demo_org_001'",
    "select * from fact_meeting",
    "DELETE FROM fact_workspace",
    "SELECT user_id FROM fact_workspace",
]
print("测试校验逻辑：")
for sql in test_sqls:
    sql_lower = sql.lower()
    errors = []
    if not sql_lower.startswith("select"):
        errors.append("SQL 必须以 SELECT 开头")
    if "org_id" not in sql_lower:
        errors.append("缺少 org_id 过滤条件")
    if errors:
        print(f"  ❌ {sql[:50]:50s} → 错误: {errors[0]}")
    else:
        print(f"  ✅ {sql[:50]:50s} → 通过")
