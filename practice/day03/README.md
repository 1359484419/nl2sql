# Day 03 — if / for / while 流程控制

## 今日目标

学会让程序做**判断**（if）和**循环**（for/while）。

## 练习 3-1：猜数字游戏（必做）

新建 `day3_guess.py`：

```python
import random

target = random.randint(1, 10)
print("我想了一个1-10的数字，你猜是几？")

while True:
    guess = int(input("你的猜测: "))
    if guess == target:
        print("对了！")
        break
    elif guess < target:
        print("太小了")
    else:
        print("太大了")
```

**验收标准：** 能运行，猜对数字时程序正常退出（不崩溃）

---

## 练习 3-2：NL2SQL SQL 校验逻辑（必做）

新建 `day3_sqlchecker.py`，读取 `sql_executor.py` 中的校验逻辑，用大白话描述出来：

```python
# 读取 sql_executor.py，找到校验函数，用 print 输出你的理解
from pathlib import Path

sql_file = Path(__file__).parent.parent.parent / "backend/tools/sql_executor.py"
content = sql_file.read_text()

# 找到 validate 函数附近的代码，打印出来
# 然后用中文写你对这个逻辑的理解
```

---

## 练习 3-3（进阶）：1-100 偶数之和

新建 `day3_sum_even.py`，用 for 循环计算 1-100 所有偶数的和，打印结果（应为 2550）。
