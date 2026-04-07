"""
Day 05 — 练习 5-2：理解 NL2SQL 的模块导入
"""

import sys
from pathlib import Path

# 尝试导入（路径处理）
practice_dir = Path(__file__).parent
nl2sql_root = practice_dir.parent
sys.path.insert(0, str(nl2sql_root))

print("=" * 50)
print("  NL2SQL 模块类型分析")
print("=" * 50)

try:
    from backend.agents.nl2sql_agent import nl2sql_graph
    print(f"\nnl2sql_graph 是什么？")
    print(f"  类型: {type(nl2sql_graph)}")
    print(f"  是否可调用: {callable(nl2sql_graph)}")
    print(f"  结论: {'函数（LangGraph编译后的图对象）' if callable(nl2sql_graph) else '不是函数'}")

    # 查看有哪些属性
    attrs = [a for a in dir(nl2sql_graph) if not a.startswith("_")]
    print(f"  主要方法: {attrs[:5]}")
except Exception as e:
    print(f"  导入失败: {e}")

try:
    from backend.services.conversation import ConversationService
    print(f"\nConversationService 是什么？")
    print(f"  类型: {type(ConversationService)}")
    print(f"  是否是类（class）: {isinstance(ConversationService, type)}")
    if isinstance(ConversationService, type):
        print(f"  是类！它的方法包括: {[m for m in dir(ConversationService) if not m.startswith('_')][:5]}")
    else:
        print(f"  是实例对象或函数")
except Exception as e:
    print(f"  导入失败: {e}")

print("\n" + "=" * 50)
print("  判断方法总结")
print("=" * 50)
print("""
判断方法：
1. type(x) → 如果包含 "class" 字样，就是类
2. isinstance(x, type) → 如果返回 True，就是类
3. callable(x) → 如果返回 True，就可以当函数调用
4. hasattr(x, '__call__') → 有 __call__ 方法的就是可调用对象
""")
