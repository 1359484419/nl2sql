"""
Day 21 — 练习 21-3：测试结果解释节点
"""

import requests

BASE_URL = "http://localhost:8001/api/v1"

questions = [
    "各部门用户平均使用时长",
    "过去7天活跃用户数",
]

print("=" * 55)
print("  测试结果解释节点")
print("=" * 55)

for q in questions:
    print(f"\n问题: {q}")
    try:
        resp = requests.post(f"{BASE_URL}/query", json={"question": q, "conversation_id": None}, timeout=30)
        result = resp.json()

        # 打印关键字段
        print(f"  SQL: {result.get('generated_sql', '无')[:60]}...")
        print(f"  数据行数: {len(result.get('data', {}).get('rows', []))}")

        # 检查是否有 result_explanation（新节点）
        explanation = result.get("result_explanation")
        if explanation:
            print(f"  解读: {explanation}")
        else:
            print(f"  ⚠️  result_explanation 字段不存在（可能节点未集成）")

    except requests.exceptions.ConnectionError:
        print("  ⚠️  服务未启动，请先运行 python backend/main.py")
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
