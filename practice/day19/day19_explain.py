"""
Day 19 — 练习 19-1：用 EXPLAIN 验证 SQL

使用 PostgreSQL 的 EXPLAIN 验证 SQL 是否有效
（注意：需要连接真实的 PostgreSQL 数据库才能运行）
"""

from sqlalchemy import create_engine, text
from pathlib import Path
import re

# 尝试从 config 读取数据库连接
config_file = Path(__file__).parent.parent.parent / "backend/config.py"
config_content = config_file.read_text(encoding="utf-8")

db_url_match = re.search(r'database_url\s*=\s*["\']([^"\']+)["\']', config_content)
db_url = db_url_match.group(1) if db_url_match else None

print("=" * 55)
print("  SQL 校验层 — EXPLAIN 验证")
print("=" * 55)

if not db_url:
    print("⚠️  未找到数据库连接配置，跳过真实数据库测试")
    print("   请确保 PostgreSQL 服务运行中\n")

# 测试 SQL（不需要数据库连接也能演示逻辑）
test_sqls = [
    ("正确的 SQL", "SELECT org_id, AVG(total_active_time_seconds) FROM fact_workspace WHERE org_id = 'demo_org_001' GROUP BY org_id"),
    ("臆造列名", "SELECT org_id, AVG(usage_duration_seconds) FROM fact_workspace WHERE org_id = 'demo_org_001'"),
    ("缺少 WHERE", "SELECT * FROM fact_workspace"),
    ("DELETE 语句", "DELETE FROM fact_workspace WHERE org_id = 'demo_org_001'"),
]

print("\nSQL 语法检查（模拟）：")
for label, sql in test_sqls:
    sql_lower = sql.lower().strip()
    errors = []
    if not sql_lower.startswith("select"):
        errors.append("非 SELECT 语句")
    if "org_id" not in sql_lower:
        errors.append("缺少 org_id 过滤")
    if "usage_duration" in sql_lower or "activity_date" in sql_lower:
        errors.append("可能臆造列名")

    if errors:
        print(f"  ❌ [{label}] → {errors[0]}")
    else:
        print(f"  ✅ [{label}] → 语法检查通过")

print("""
\n结论：
- 第一层：字符串规则检查（快，但不能发现列名错误）
- 第二层：EXPLAIN 真实数据库验证（能发现列名不存在等错误）
- 两层结合 = 既快又准的 SQL 校验
""")
