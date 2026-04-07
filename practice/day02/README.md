# Day 02 — 变量 & 数据类型

## 今日目标

掌握 Python 的 4 种基础数据类型：**整数(int)、小数(float)、字符串(str)、布尔(bool)**，学会它们之间如何互相转换。

## 练习 2-1：数据类型转换（必做）

新建文件 `day2_types.py`，实现以下功能：

```python
# a) 把字符串 "99" 转成整数，加 1，打印结果
# b) 把整数 8 转成小数，除以 3，打印结果（应该是 2.666...）
# c) 把 3.14 转成整数，看看小数部分丢没丢（3.14 → 3）
```

**验收标准：** 运行后屏幕分别显示 `100`、`2.666...`、`3`

---

## 练习 2-2：理解 NL2SQL 的数据类型（必做）

新建 `day2_nl2sql_types.py`，回答以下问题（用 print 输出答案）：

1. 在 `nl2sql_agent.py` 里，`NL2SQLState` 的 `retry_count` 字段是什么类型？（提示：看 TypedDict 定义）
2. `sql_valid` 字段是什么类型？
3. 把 `retry_count = 3` 转成字符串是多少？
4. 把 `sql_valid = True` 转成整数是多少？

把答案用 `print()` 打印出来。

---

## 练习 2-3（进阶）：温度计算器

新建 `day2_temp_calc.py`，写两个函数：

```python
def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32

def fahrenheit_to_celsius(f):
    return (f - 32) * 5 / 9

# 测试
print(celsius_to_fahrenheit(0))     # 应输出 32
print(celsius_to_fahrenheit(100))  # 应输出 212
print(fahrenheit_to_celsius(32))  # 应输出 0
```

然后增加一个功能：把今天的温度（假设 18°C）转换成华氏度，打印出来。
