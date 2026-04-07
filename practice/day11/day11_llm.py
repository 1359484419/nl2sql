"""
Day 11 — 练习 11-1：调用 LLM API
"""

import sys
from pathlib import Path

# 加载 .env
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

try:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

    print("=" * 50)
    print("  LLM API 调用测试")
    print("=" * 50)

    # 简单调用
    print("\n1. 简单调用：")
    resp = llm.invoke("用一句话解释什么是大语言模型")
    print(f"   {resp.content}")

    # 带角色
    print("\n2. 带 System Prompt：")
    resp2 = llm.invoke([
        {"role": "system", "content": "你是一个SQL专家，用简单的中文回答"},
        {"role": "user", "content": "什么是SELECT语句？"}
    ])
    print(f"   {resp2.content}")

except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    print("请运行: pip install langchain-openai python-dotenv")
except Exception as e:
    print(f"⚠️  API 调用失败: {e}")
    print("请确认 .env 文件里有正确的 OPENAI_API_KEY")
