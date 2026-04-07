"""
Day 10 — 练习 10-1：错误处理
"""

# 安全除法
def safe_divide(a, b):
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("错误：除数不能为0")
        return None
    except TypeError:
        print("错误：类型不对，不能除")
        return None

# 解析年龄
def parse_age(input_str):
    try:
        age = int(input_str)
        if age < 0 or age > 150:
            print("错误：年龄超出正常范围")
            return None
        return age
    except (ValueError, TypeError):
        print("无效输入：年龄必须是数字")
        return None

# ══════════════════════════════════════════════════════════════
# 测试
# ══════════════════════════════════════════════════════════════
print("safe_divide 测试：")
print(f"  safe_divide(10, 2) = {safe_divide(10, 2)}")   # 5.0
print(f"  safe_divide(10, 0) = {safe_divide(10, 0)}")   # None
print(f"  safe_divide('a', 2) = {safe_divide('a', 2)}") # None

print("\nparse_age 测试：")
print(f"  parse_age('25') = {parse_age('25')}")          # 25
print(f"  parse_age('abc') = {parse_age('abc')}")        # None
print(f"  parse_age('-5') = {parse_age('-5')}")          # None
print(f"  parse_age('200') = {parse_age('200')}")        # None

print("\n✅ 错误处理测试完成！")
