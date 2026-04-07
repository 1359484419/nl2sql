# Day 17 — LangGraph 入门

## 今日目标

学会用 LangGraph 写状态机，理解 `StateGraph`、`add_node`、`add_edge`。

## 练习 17-1：写一个 LangGraph（必做）

新建 `day17_langgraph.py`：

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class MyState(TypedDict):
    message: str
    step_count: int

def node_a(state): state["step_count"] += 1; return state
def node_b(state): state["step_count"] += 1; return state

graph = StateGraph(MyState)
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.set_entry_point("node_a")
graph.add_edge("node_b", END)
app = graph.compile()
result = app.invoke({"message": "开始", "step_count": 0})
print(result)
```

**验收标准：** 运行后 step_count = 3（经过 node_a → node_a → node_b → end）

---

## 练习 17-2：画 NL2SQL Mermaid 状态图（必做）

新建 `day17_mermaid.md`，用 Mermaid 语法画出 NL2SQL 的完整状态图，包含所有节点和路由。
