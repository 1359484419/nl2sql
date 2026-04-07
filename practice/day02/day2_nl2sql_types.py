"""
Day 02 — 练习 2-2：理解 NL2SQL 的数据类型
任务：读取 nl2sql_agent.py，回答关于 TypedDict 字段类型的问题
"""

from pathlib import Path
import sys

# 读取 nl2sql_agent.py
nl2sql_file = Path(__file__).parent.parent.parent / "backend/agents/nl2sql_agent.py"
content = nl2sql_file.read_text(encoding="utf-8")

# 找到 TypedDict 定义部分
start = content.find("class NL2SQLState")
end = content.find("}", start) + 1
typeddict_block = content[start:end]

print("NL2SQLState 定义片段：")
print(typeddict_block[:500])
print("\n" + "=" * 50)

# 回答问题
print("\n问题答案：")

# Q1: retry_count 是什么类型？
if "retry_count: int" in typeddict_block:
    print("1. retry_count 类型: int（整数）")
else:
    print("1. retry_count 类型: 未找到（可能在其他位置定义）")

# Q2: sql_valid 是什么类型？
if "sql_valid: bool" in typeddict_block:
    print("2. sql_valid 类型: bool（布尔值）")
elif "sql_valid" in typeddict_block:
    print("2. sql_valid 类型: 找到定义，但可能不是 bool")

# Q3: 把 retry_count = 3 转成字符串
retry_count = 3
retry_str = str(retry_count)
print(f"3. str(retry_count=3) = '{retry_str}'")

# Q4: 把 sql_valid = True 转成整数
sql_valid = True
sql_valid_int = int(sql_valid)
print(f"4. int(sql_valid=True) = {sql_valid_int}（True=1, False=0）")
