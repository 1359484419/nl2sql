"""
Day 21 — 练习 21-1：结果解释节点函数

这个函数在 NL2SQL Agent 里被注册为新节点：
  graph.add_node("explain_result", explain_result)
"""

from typing import Optional

class NL2SQLState(dict):
    """模拟的 Agent State（实际用的是 TypedDict）"""
    def get(self, key, default=None):
        return super().get(key, default)

def explain_result(state: dict) -> dict:
    """
    把 SQL 执行结果翻译成人话。

    这个节点在 chart 节点之后执行：
    chart → explain_result → end

    作用：
    - 如果结果为空，告诉用户"查询结果为空"
    - 如果有数据，生成自然语言解读
    """
    data = state.get("sql_result_data", {})
    if not data:
        state["result_explanation"] = "查询结果为空，请尝试调整查询条件。"
        return state

    rows = data.get("rows", [])
    columns = [c["name"] for c in data.get("columns", [])]

    if not rows:
        state["result_explanation"] = "查询结果为空。"
        return state

    # 简单规则生成解读（也可以调 LLM 生成更好的）
    state["result_explanation"] = (
        f"本次查询返回 {len(rows)} 行数据。"
        f"包含列：{', '.join(columns)}。"
        f"第一行数据：{rows[0] if rows else '无'}。"
    )
    return state

# ══════════════════════════════════════════════════════════════
# 测试
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # 测试1：空数据
    state1 = {"sql_result_data": {"rows": [], "columns": []}}
    result1 = explain_result(state1)
    print(f"空数据: {result1['result_explanation']}")

    # 测试2：有数据
    state2 = {
        "sql_result_data": {
            "rows": [{"dept": "001", "avg_time": 3600}, {"dept": "002", "avg_time": 4200}],
            "columns": [{"name": "dept"}, {"name": "avg_time"}]
        }
    }
    result2 = explain_result(state2)
    print(f"有数据: {result2['result_explanation']}")
