"""
Day 03 — 练习 3-1：猜数字游戏
验收：能运行，猜对数字时程序正常退出
"""

import random

target = random.randint(1, 10)
print("我想了一个1-10的数字，你猜是几？")
print(f"提示：答案是 {target}（测试用）")

while True:
    try:
        guess = int(input("你的猜测: "))
    except ValueError:
        print("请输入数字！")
        continue

    if guess == target:
        print("对了！")
        break
    elif guess < target:
        print("太小了")
    else:
        print("太大了")

print("游戏结束！")
