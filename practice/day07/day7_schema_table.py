"""
Day 07 — 练习 7-2：读取并格式化 Schema
"""

from pathlib import Path
import json

schema_file = Path(__file__).parent.parent.parent / "backend/schemas/saas_bi_schema.py"
content = schema_file.read_text(encoding="utf-8")

print("=" * 60)
print("  NL2SQL Schema — fact_workspace 表")
print("=" * 60)

# 提取 fact_workspace
import re
# 找所有字段定义（简化版）
fw_match = re.search(r'"fact_workspace":\s*\{.*?\n    \}', content, re.DOTALL)
if fw_match:
    fw_text = fw_match.group()
    # 提取字段
    fields = re.findall(r'"(\w+)":\s*\{[^}]*"comment":\s*"([^"]+)"', fw_text)
    print(f"\n{'字段名':25s} {'类型':15s} {'含义'}")
    print("-" * 60)
    for fname, fcomment in fields:
        ftype = re.search(rf'"{fname}".*?"type":\s*"([^"]+)"', fw_text)
        ftype_str = ftype.group(1) if ftype else "未知"
        print(f"  {fname:23s} {ftype_str:15s} {fcomment}")

    print(f"\n共 {len(fields)} 个字段")
else:
    print("未找到 fact_workspace 表定义")
