# Day 06 — 面向对象 class

## 今日目标

理解 Python 的 class（类）：把数据和操作打包在一起。

## 练习 6-1：银行账户类（必做）

新建 `day6_class.py`，实现：

```python
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
```

**验收标准：** 运行后余额计算正确（1500 → 1300 → 余额不足）

---

## 练习 6-2：理解 TypedDict（必做）

新建 `day6_typeddict.py`，回答：
- TypedDict 和普通 dict 有什么区别？
- `total=False` 是什么意思？
- 写代码演示两者区别。

---

## 练习 6-3（进阶）：继承和方法覆盖

给 `BankAccount` 加一个子类 `SavingsAccount`（储蓄账户），它有额外的利息计算功能。
