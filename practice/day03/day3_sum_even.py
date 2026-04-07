"""
Day 03 — 练习 3-3（进阶）：1-100 偶数之和
验收：运行后输出 2550
"""

total = 0
for i in range(1, 101):
    if i % 2 == 0:
        total += i

print(f"1-100 所有偶数的和 = {total}")

# 验证
assert total == 2550, f"应该是 2550，但计算结果是 {total}"
print("✅ 计算正确！")
