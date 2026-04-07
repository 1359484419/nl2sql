"""
Day 05 — 练习 5-1：函数定义与调用
"""

# 温度转换
def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32

def fahrenheit_to_celsius(f):
    return (f - 32) * 5 / 9

# 时间转换
def seconds_to_hms(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}小时{minutes}分钟{secs}秒"

# 带默认参数的问候
def greet(name, prefix="你好"):
    return f"{prefix}，{name}！"

# ══════════════════════════════════════════════════════════════
# 测试
# ══════════════════════════════════════════════════════════════
print("温度转换测试：")
print(f"  0°C = {celsius_to_fahrenheit(0):.1f}°F")
print(f"  100°C = {celsius_to_fahrenheit(100):.1f}°F")
print(f"  212°F = {fahrenheit_to_celsius(212):.1f}°C")

print("\n时间转换测试：")
print(f"  3661秒 = {seconds_to_hms(3661)}")
print(f"  3600秒 = {seconds_to_hms(3600)}")
print(f"  90秒 = {seconds_to_hms(90)}")

print("\n问候测试：")
print(f"  {greet('小明')}")
print(f"  {greet('小红', '早上好')}")
print(f"  {greet('小刚', '晚安')}")

# ══════════════════════════════════════════════════════════════
# 进阶：返回多个值
# ══════════════════════════════════════════════════════════════
def find_max_min(numbers):
    return max(numbers), min(numbers)

numbers = [3, 1, 4, 1, 5, 9, 2, 6]
mx, mn = find_max_min(numbers)
print(f"\n最大值: {mx}, 最小值: {mn}")
