"""
Day 16 — 练习 16-2：分析 NL2SQL Agent 节点
"""

from pathlib import Path
import re

agent_file = Path(__file__).parent.parent.parent / "backend/agents/nl2sql_agent.py"
content = agent_file.read_text(encoding="utf-8")

print("=" * 55)
print("  NL2SQL Agent 状态机节点分析")
print("=" * 55)

# 找所有 def 开头（节点函数）
functions = re.findall(r"^\s*def\s+(\w+)\s*\(", content, re.MULTILINE)
print(f"\n找到 {len(functions)} 个函数：")
for i, fn in enumerate(functions, 1):
    print(f"  {i}. {fn}()")

# 找 add_node
node_matches = re.findall(r'add_node\s*\(\s*["\'](\w+)["\']', content)
print(f"\n状态机节点：")
for i, node in enumerate(node_matches, 1):
    print(f"  {i}. {node}")

# 节点说明
node_descriptions = {
    "classify_intent": "意图分类（指标查询/趋势分析/部门对比/TOP N/同比环比）",
    "retrieve": "RAG 检索（Schema + 指标 + SQL 示例）",
    "generate": "LLM 生成 SQL",
    "validate": "SQL 校验（EXPLAIN）",
    "execute": "执行 SQL（PostgreSQL）",
    "chart": "图表类型推荐",
    "build_response": "构建最终响应",
}
print("\n节点作用：")
for node in node_matches:
    desc = node_descriptions.get(node, "（未知）")
    print(f"  {node}: {desc}")

print("""
\n节点之间怎么连接？
→ 用 add_edge（固定路由）或 add_conditional_edges（条件路由）
→ 条件路由根据 state 里的字段决定下一步
""")
