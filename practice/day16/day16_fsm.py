"""
Day 16 — 练习 16-1：订单处理状态机
"""

# ══════════════════════════════════════════════════════════════
# 简化状态机：订单处理流程
# ══════════════════════════════════════════════════════════════

def handle_order(state):
    """接单"""
    state["status"] = "pending"
    print(f"  [{state['step']}] handle_order → pending")
    state["step"] += 1
    return "check_payment"

def check_payment(state):
    """检查支付"""
    if state.get("paid"):
        state["status"] = "paid"
        print(f"  [{state['step']}] check_payment → paid")
    else:
        state["status"] = "payment_failed"
        print(f"  [{state['step']}] check_payment → payment_failed")
        return "notify_user"
    state["step"] += 1
    return "ship"

def ship(state):
    """发货"""
    state["status"] = "shipped"
    print(f"  [{state['step']}] ship → shipped")
    state["step"] += 1
    return "end"

def notify_user(state):
    """通知用户"""
    print(f"  [{state['step']}] notify_user → 支付失败，请重试")
    state["step"] += 1
    return "end"

# 路由表
ROUTES = {
    "handle_order": handle_order,
    "check_payment": check_payment,
    "ship": ship,
    "notify_user": notify_user,
}

def run_order_flow(initial_state):
    """运行订单流程"""
    state = {**initial_state, "step": 1}
    current = "handle_order"

    while current != "end":
        current = ROUTES[current](state)

    print(f"\n最终状态: {state}")
    return state

# ══════════════════════════════════════════════════════════════
# 测试
# ══════════════════════════════════════════════════════════════
print("=" * 50)
print("  订单状态机测试")
print("=" * 50)

print("\n✅ 支付成功路径:")
run_order_flow({"action": "create", "paid": True})

print("\n❌ 支付失败路径:")
run_order_flow({"action": "create", "paid": False})
