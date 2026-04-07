"""
Day 18 — 练习 18-2：分析 NL2SQL 重试机制
"""

from pathlib import Path
import re

agent_file = Path(__file__).parent.parent.parent / "backend/agents/nl2sql_agent.py"
content = agent_file.read_text(encoding="utf-8")

print("=" * 55)
print("  NL2SQL Self-Correction 重试机制分析")
print("=" * 55)

# 找 max_sql_retries
retries_match = re.search(r"max_sql_retries\s*[=:]\s*(\d+)", content)
if retries_match:
    print(f"\n最大重试次数: {retries_match.group(1)} 次")

# 找重试相关函数
retry_funcs = re.findall(r"def\s+(\w*retry\w*|w*route\w*)", content, re.IGNORECASE)
print(f"\n重试相关函数: {retry_funcs}")

# 找 retry_count += 1
retry_blocks = re.findall(r".{0,100}retry_count.{0,200}", content)
print("\n重试相关代码片段：")
for block in retry_blocks[:3]:
    print(f"  {block[:200]}")

print("""
\n重试机制总结：
1. 重试发生在两个地方：SQL 校验失败、SQL 执行失败
2. 每次失败 retry_count += 1
3. 如果 retry_count >= max_sql_retries → 返回错误，不再重试
4. 重试流程：校验失败 → generate 节点重新生成 SQL → 再次校验
""")
