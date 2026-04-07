"""
Day 18 — 练习 18-1：带重试的 API 调用
"""

import random

def call_api_may_fail():
    """模拟可能失败的 API 调用，成功率 40%"""
    if random.random() < 0.4:
        return {"success": True, "data": "查询结果：各部门使用时长"}
    return {"success": False, "error": "列名不存在"}

def call_with_retry(max_retries=3):
    """最多重试 max_retries 次"""
    for attempt in range(1, max_retries + 1):
        result = call_api_may_fail()
        if result["success"]:
            print(f"  ✅ 第 {attempt} 次成功: {result['data']}")
            return result["data"]
        print(f"  ❌ 第 {attempt} 次失败: {result['error']}，重试中...")
    print("  ❌ 已达最大重试次数，返回 None")
    return None

print("=" * 50)
print("  带重试的 API 调用模拟")
print("=" * 50)
print("\n第 1 次测试：")
result1 = call_with_retry()
print(f"\n结果: {result1}")

print("\n" + "-" * 50)
print("第 2 次测试：")
result2 = call_with_retry()
print(f"\n结果: {result2}")
