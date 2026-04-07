# Day 21 — Agent 新节点：结果解释

## 今日目标

在 NL2SQL Agent 里加一个新节点：用 LLM 把 SQL 执行结果翻译成人话。

## 练习 21-1：写结果解释节点（必做）

新建 `day21_explain_node.py`，实现 `explain_result` 函数：

```python
def explain_result(state: NL2SQLState) -> NL2SQLState:
    """把 SQL 执行结果翻译成人话"""
    data = state.get("sql_result_data", {})
    if not data or not data.get("rows"):
        state["result_explanation"] = "查询结果为空"
        return state
    # 用 LLM 或简单规则生成解读
    state["result_explanation"] = f"查询返回 {len(rows)} 行..."
    return state
```

---

## 练习 21-2：集成到 Agent（必做）

修改 `backend/agents/nl2sql_agent.py`：
1. 在 `NL2SQLState` 里加字段：`result_explanation: Optional[str]`
2. 注册新节点：`graph.add_node("explain_result", explain_result)`
3. 在 `chart` 节点后连接：`graph.add_edge("chart", "explain_result")`
4. 在响应里加上这个字段

重启服务，测试是否有 `result_explanation` 字段。

---

## 练习 21-3：测试记录（必做）

新建 `day21_test.py`，调用 API 测试新节点，记录结果到 `DEBUG_LOG.md`。
