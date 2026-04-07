# Day 10 — 错误处理 & 调试

## 今日目标

学会 try/except 捕获异常，理解 Python 程序崩溃的原因。

## 练习 10-1：safe_divide + parse_age（必做）

新建 `day10_errors.py`：

```python
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        print("错误：除数不能为0")
        return None
    except TypeError:
        print("错误：类型不对，不能除")
        return None

def parse_age(input_str):
    try:
        age = int(input_str)
        if age < 0 or age > 150:
            return None
        return age
    except (ValueError, TypeError):
        print("无效输入")
        return None
```

**验收标准：** `parse_age("25")` 返回 25，`parse_age("abc")` 返回 None 并打印"无效输入"。

---

## 练习 10-2：routes.py 错误处理分析（必做）

新建 `day10_routes_analysis.py`，读取 `routes.py`，回答：
- 如果 Agent 执行失败，程序返回什么？
- except Exception as e 是什么意思？
