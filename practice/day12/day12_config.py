"""
Day 12 — 练习 12-2：分析 Embedding 模型配置
"""

from pathlib import Path

embedding_file = Path(__file__).parent.parent.parent / "backend/rag/embedding.py"
content = embedding_file.read_text(encoding="utf-8")

print("=" * 50)
print("  Embedding 模型配置分析")
print("=" * 50)

# 找默认模型
import re

# 找 _provider
provider_match = re.search(r'_provider\s*=\s*"([^"]+)"', content)
if provider_match:
    print(f"\n默认模型提供方: {provider_match.group(1)}")

# 找 dimension
dim_match = re.search(r'_embed_dimension\s*=\s*(\d+)', content)
if dim_match:
    print(f"向量维度: {dim_match.group(1)}")

# 找模型初始化
init_match = re.search(r'def _init_embedding\(self\):.*?(?=\n    def)', content, re.DOTALL)
if init_match:
    print(f"\n初始化代码片段:")
    print(init_match.group()[:400])

print("""
\n结论：
1. 默认用 HuggingFace SentenceTransformer（零配置，CPU 就能跑）
2. 如果要换 OpenAI，改 _provider = "openai"，同时配置 OPENAI_API_KEY
3. 向量维度影响语义表达能力，维度越高越精确（但也更慢）
""")
