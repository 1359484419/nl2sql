"""
Day 06 — 练习 6-2：TypedDict vs dict 理解
"""

from typing import TypedDict

# 普通 dict：类型随意
person1 = {"name": "张三", "age": 28, "is_student": True}
person1["age"] = "hello"   # 不报错，但不符合语义
person1["abc"] = 123       # 不报错，多余的键
print(f"普通 dict：{person1}")

# TypedDict：规定每个字段的类型
class Person(TypedDict, total=False):
    name: str
    age: int
    is_student: bool

person2: Person = {"name": "李四", "age": 25}
print(f"TypedDict：{person2}")

print("\n" + "=" * 50)
print("  区别总结")
print("=" * 50)
print("""
1. 普通 dict：
   - 任何键都可以，任何类型的值都可以
   - Python 不检查，写错了也不知道

2. TypedDict：
   - 规定每个键的名字和值的类型
   - IDE/类型检查器会报错（PyCharm 会有黄色警告）
   - 总分=False：所有字段都是可选的（可以只填部分）
   - total=True（默认）：所有字段都必须填
""")

# 演示 total=False
class PartialPerson(TypedDict, total=False):
    name: str      # 可选
    age: int       # 可选
    city: str       # 可选

p: PartialPerson = {"name": "王五"}  # 只填 name 也合法
print(f"total=False 允许只填部分字段：{p}")
