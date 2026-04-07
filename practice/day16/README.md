# Day 16 — 状态机概念

## 今日目标

用生活例子理解状态机（Node + Edge），理解 Agent 为什么需要状态机。

## 练习 16-1：手写状态机（必做）

新建 `day16_fsm.py`，实现一个订单处理状态机：

```python
def handle_order(state):
    if state["action"] == "create":
        state["status"] = "pending"
        return "check_payment"
    ...

ROUTES = {
    "handle_order": handle_order,
    ...
}
```

**验收标准：** 订单从 create → pending → paid → shipped → end。

---

## 练习 16-2：分析 NL2SQL Agent 节点（必做）

新建 `day16_nodes.py`，找出 NL2SQL Agent 的所有节点，回答：
- 一共有多少个节点？
- 每个节点的作用是什么？
- 节点之间的路由条件是什么？
