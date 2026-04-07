"""
Day 15 — 练习 15-1：Prompt Engineering 对比
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

    print("=" * 55)
    print("  Prompt Engineering 对比实验")
    print("=" * 55)

    # 模糊 Prompt
    prompt_a = f"用户问：{question}\n请生成SQL。"
    resp_a = llm.invoke(prompt_a)
    sql_a = resp_a.content
    print(f"\n[模糊 Prompt]\n{sql_a[:200]}")
    has_fake_a = any(w in sql_a.lower() for w in ["usage_duration", "activity_date", "login_time"])
    print(f"臆造列名: {'⚠️  有' if has_fake_a else '✅  无'}")

    # 详细 Prompt
    prompt_b = f"""你是一个专业的 SQL 生成助手。
已知数据库有一个表 fact_workspace：
- org_id VARCHAR: 租户ID
- user_id VARCHAR: 用户ID
- record_date DATE: 记录日期
- total_active_time_seconds BIGINT: 用户活跃时长（秒）

要求：
1. 必须有 WHERE org_id = '{{org_id}}'
2. 只用上面列出的字段名
3. 禁止臆造不存在的列名

用户问：{question}
SQL："""
    resp_b = llm.invoke(prompt_b)
    sql_b = resp_b.content
    print(f"\n[详细 Prompt]\n{sql_b[:200]}")
    has_fake_b = any(w in sql_b.lower() for w in ["usage_duration", "activity_date", "login_time"])
    print(f"臆造列名: {'⚠️  有' if has_fake_b else '✅  无'}")

    print("\n结论：详细 Prompt 大幅提升 SQL 准确性！")

except ImportError:
    print("安装依赖: pip install langchain-openai python-dotenv")
except Exception as e:
    print(f"API 失败: {e}")
