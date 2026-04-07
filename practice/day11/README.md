# Day 11 — LLM API 调用

## 今日目标

亲手调用 LLM API，理解 System Prompt 的作用。

## 练习 11-1：调用 LLM 生成文本（必做）

新建 `day11_llm.py`：

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

# 最简单调用
resp = llm.invoke("用一句话解释什么是大语言模型")
print("回答:", resp.content)

# 带角色
resp2 = llm.invoke([
    {"role": "system", "content": "你是一个SQL专家，用简单的中文回答"},
    {"role": "user", "content": "什么是SELECT语句？"}
])
print("专家回答:", resp2.content)
```

**验收标准：** 运行后能看到 LLM 的文字回答。

---

## 练习 11-2：Prompt Engineering 对比（必做）

新建 `day11_prompts.py`，对比"模糊 Prompt"和"详细 Prompt"生成的 SQL 差异。
