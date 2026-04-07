"""
Day 17 — 练习 17-1：LangGraph 入门
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict

class MyState(TypedDict):
    message: str
    step_count: int

def node_a(state: MyState) -> MyState:
    state["step_count"] += 1
    state["message"] = state["message"] + " → A"
    return state

def node_b(state: MyState) -> MyState:
    state["step_count"] += 1
    state["message"] = state["message"] + " → B"
    return state

def should_continue(state: MyState) -> str:
    if state["step_count"] < 3:
        return "node_a"
    return END

print("=" * 50)
print("  LangGraph 状态机")
print("=" * 50)

graph = StateGraph(MyState)
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.set_entry_point("node_a")
graph.add_conditional_edges("node_a", should_continue, {"node_a": "node_a", END: END})
graph.add_edge("node_b", END)

app = graph.compile()
result = app.invoke({"message": "开始", "step_count": 0})

print(f"\n最终状态: {result}")
print(f"经过的节点: {result['message']}")
print(f"step_count: {result['step_count']} (预期: 3)")
