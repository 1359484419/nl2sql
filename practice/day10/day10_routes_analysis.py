"""
Day 10 — 练习 10-2：routes.py 错误处理分析
"""

from pathlib import Path

routes_file = Path(__file__).parent.parent.parent / "backend/api/routes.py"
content = routes_file.read_text(encoding="utf-8")

# 找 try/except 块
try_start = content.find("try:")
try_end = content.find("except", try_start + 5)
except_block = content[try_start:try_end + 300]

print("=" * 50)
print("  routes.py 错误处理代码")
print("=" * 50)
print(except_block)

print("""
问题1: 如果 Agent 执行失败，程序返回什么？

答案：
  - 返回一个 QueryResponse 对象，error_message 字段包含错误信息
  - 不是崩溃退出，而是优雅地告诉前端"出错了"
  - HTTP 状态码仍然是 200（而不是 500），前端更容易处理

问题2: except Exception as e 是什么意思？

答案：
  - Exception 是所有 Python 异常的基类
  - "as e" 把捕获的异常对象取名为 e
  - str(e) 就是错误的文字描述
  - 这样做的好处：无论什么错误都能捕获，不会让程序崩溃
""")

# 实际测试错误处理
print("=" * 50)
print("  模拟错误处理")
print("=" * 50)

def simulate_agent():
    raise RuntimeError("模拟：LLM API 调用失败")

def handle_request():
    try:
        result = simulate_agent()
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

response = handle_request()
print(f"错误处理结果: {response}")
