"""
Day 07 — 练习 7-1：JSON 数据读写
"""

import json
from pathlib import Path

data = {
    "name": "NL2SQL Agent",
    "version": "1.0",
    "features": ["RAG", "LangGraph", "SSE"],
    "config": {"timeout": 30, "retries": 3}
}

# 写入文件
output_file = Path(__file__).parent / "data.json"
json_str = json.dumps(data, ensure_ascii=False, indent=2)
output_file.write_text(json_str, encoding="utf-8")
print(f"已写入: {output_file}")

# 读回来
loaded = json.loads(output_file.read_text(encoding="utf-8"))
print(f"\n读回来的数据:")
print(json.dumps(loaded, ensure_ascii=False, indent=2))

# 验证
assert loaded["name"] == data["name"], "数据不匹配！"
assert loaded["config"]["timeout"] == 30
print("\n✅ JSON 读写验证通过！")

# ══════════════════════════════════════════════════════════════
# 进阶：添加新字段并保存
# ══════════════════════════════════════════════════════════════
loaded["author"] = "我的名字"
loaded["config"]["max_tokens"] = 2048
output_file.write_text(json.dumps(loaded, ensure_ascii=False, indent=2), encoding="utf-8")
print("\n✅ 添加新字段后重新保存！")
