"""
Day 06 — 练习 6-1：BankAccount 类
"""

class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            print(f"存了 {amount}，余额 {self.balance}")
        else:
            print("存款必须是正数")

    def withdraw(self, amount):
        if amount > self.balance:
            print(f"余额不足！余额 {self.balance}")
        else:
            self.balance -= amount
            print(f"取了 {amount}，余额 {self.balance}")

    def __str__(self):
        return f"账户：{self.owner}，余额：{self.balance}"


# ══════════════════════════════════════════════════════════════
# 测试
# ══════════════════════════════════════════════════════════════
acc = BankAccount("小明", 1000)
print(acc)

acc.deposit(500)       # 存500 → 余额1500
acc.withdraw(200)      # 取200 → 余额1300
acc.withdraw(2000)     # 余额不足
acc.deposit(-50)       # 无效存款

print(acc)             # 打印最终余额
