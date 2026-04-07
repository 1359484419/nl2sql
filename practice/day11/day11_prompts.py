"""
Day 11 — 练习 11-2：Prompt Engineering 对比
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

try:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    question = "各部门用户平均使用时长"

    print("=" * 50)
    print("  Prompt Engineering 对比实验")
    print("=" * 50)

    # Prompt A：模糊
    prompt_a = f"用户问：{question}\n请生成SQL。"
    resp_a = llm.invoke(prompt_a)
    print(f"\n[Prompt A - 模糊版]")
    print(f"SQL: {resp_a.content[:200]}")
    sql_a = resp_a.content.lower()
    print(f"⚠️ 臆造列名: {'有（usage_duration / activity_date）' if 'usage_duration' in sql_a or 'activity_date' in sql_a else '无'}")

    # Prompt B：详细
    prompt_b = f"""你是一个专业的 SQL 生成助手。
已知数据库有一个表 fact_workspace，包含以下字段：
- org_id VARCHAR: 租户ID
- user_id VARCHAR: 用户ID
- record_date DATE: 记录日期
- total_active_time_seconds BIGINT: 用户活跃时长（秒）

生成SQL，要求：
1. 必须有 WHERE org_id = '{{org_id}}' 过滤
2. 只用上面列出的字段名
3. 禁止臆造不存在的列名

用户问：{question}
SQL："""
    resp_b = llm.invoke(prompt_b)
    print(f"\n[Prompt B - 详细版]")
    print(f"SQL: {resp_b.content[:200]}")
    sql_b = resp_b.content.lower()
    print(f"⚠️ 臆造列名: {'有' if 'usage_duration' in sql_b or 'activity_date' in sql_b else '无'}")

    print("\n结论：详细的 Prompt + Schema 信息，大幅减少臆造列名！")

except ImportError:
    print("请先安装依赖: pip install langchain-openai python-dotenv")
except Exception as e:
    print(f"API 调用失败: {e}")
