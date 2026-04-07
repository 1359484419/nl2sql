# Day 05 — 函数 & 模块

## 今日目标

学会写函数（def）、理解模块（import）、掌握参数和返回值。

## 练习 5-1：温度转换 + 时间转换（必做）

新建 `day5_functions.py`，实现以下函数：

```python
def celsius_to_fahrenheit(c):
    """摄氏度 → 华氏度"""
    return c * 9 / 5 + 32

def seconds_to_hms(seconds):
    """秒 → "X小时X分钟X秒"格式"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}小时{minutes}分钟{secs}秒"

def greet(name, prefix="你好"):
    """带默认参数的问候"""
    return f"{prefix}，{name}！"
```

---

## 练习 5-2：理解 NL2SQL 的模块导入（必做）

新建 `day5_imports.py`，回答：
- `from backend.agents.nl2sql_agent import nl2sql_graph` 导入的是什么？（函数？类？）
- `ConversationService` 是函数还是类？怎么判断？
- 写代码验证你的判断（用 `callable()` 判断）
