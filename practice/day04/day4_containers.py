"""
Day 04 — 练习 4-1：列表和字典操作
"""

# 列表基础
fruits = ["苹果", "香蕉", "橙子"]
fruits.append("葡萄")
fruits.insert(1, "西瓜")
print(f"水果列表: {fruits}")
print(f"第1个水果: {fruits[0]}")
print(f"列表长度: {len(fruits)}")

# 字典基础
user = {"name": "张三", "age": 28, "city": "北京"}
user["job"] = "工程师"
print(f"\n用户信息: {user}")
print(f"用户名: {user['name']}")
for key, value in user.items():
    print(f"  {key}: {value}")

# ══════════════════════════════════════════════════════════════
# 任务：学生成绩管理系统
# ══════════════════════════════════════════════════════════════
students = [
    {"name": "小明", "score": 92},
    {"name": "小红", "score": 85},
    {"name": "小刚", "score": 97},
    {"name": "小丽", "score": 78},
]

# 找出最高分
best = max(students, key=lambda s: s["score"])
print(f"\n最高分：{best['name']}，{best['score']}分")

# 找出最低分
worst = min(students, key=lambda s: s["score"])
print(f"最低分：{worst['name']}，{worst['score']}分")

# 计算平均分
avg = sum(s["score"] for s in students) / len(students)
print(f"平均分：{avg:.1f}分")
