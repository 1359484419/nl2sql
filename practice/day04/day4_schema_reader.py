"""
Day 04 — 练习 4-2：读取 NL2SQL Schema
"""

from pathlib import Path

schema_file = Path(__file__).parent.parent.parent / "backend/schemas/saas_bi_schema.py"
content = schema_file.read_text(encoding="utf-8")

print("=" * 60)
print("  NL2SQL 数据库 Schema 概览")
print("=" * 60)

# 找所有表名（简化的方式）
import re
tables = re.findall(r'"(\w+)":\s*\{', content)
print(f"\n共有 {len(tables)} 张表:")
for t in tables:
    print(f"  - {t}")

# 找 fact_workspace 的所有字段
fw_start = content.find("fact_workspace")
fw_end = content.find("\n    },\n", fw_start) + 1
fw_block = content[fw_start:fw_end]

print("\n" + "=" * 60)
print("  fact_workspace 表字段")
print("=" * 60)

# 提取字段（简化解析）
field_lines = re.findall(r'"(\w+)":\s*\{[^}]*"comment":\s*"([^"]+)"[^}]*"type":\s*"([^"]+)"', fw_block)
for fname, ftype, fcomment in field_lines:
    print(f"  {fname:35s} {ftype:15s} {fcomment}")

print(f"\n共 {len(field_lines)} 个字段")
