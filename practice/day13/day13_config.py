"""
Day 13 — 练习 13-2：分析 NL2SQL 的 Milvus 配置
"""

from pathlib import Path

config_file = Path(__file__).parent.parent.parent / "backend/config.py"
content = config_file.read_text(encoding="utf-8")

print("=" * 50)
print("  Milvus 配置分析")
print("=" * 50)

import re

# 找 Milvus 相关配置
for line in content.split("\n"):
    if "milvus" in line.lower() or "collection" in line.lower():
        print(f"  {line.strip()}")

print("""
\n结论：
1. Milvus 数据存在本地 .db 文件（milvus_lite）
2. Schema collection 存数据库表结构
3. Metrics collection 存业务指标定义
4. 用 COSINE 余弦相似度，距离越小越相似
""")
