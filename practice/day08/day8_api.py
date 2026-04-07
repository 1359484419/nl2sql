"""
Day 08 — 练习 8-1：调用 NL2SQL API
"""

import requests
import time

BASE_URL = "http://localhost:8001/api/v1"

print("=" * 50)
print("  NL2SQL API 调用测试")
print("=" * 50)

# 1. 健康检查
print("\n1. 健康检查...")
try:
    resp = requests.get(f"{BASE_URL}/health", timeout=5)
    resp.raise_for_status()
    data = resp.json()
    print(f"   ✅ 健康状态: {data}")
except requests.exceptions.ConnectionError:
    print("   ⚠️  无法连接（服务可能未启动）")
    print("   请先运行: python backend/main.py")
    print("   然后再运行这个脚本")
except Exception as e:
    print(f"   ❌ 请求失败: {e}")

# 2. 发查询
print("\n2. 发送查询...")
try:
    resp = requests.post(
        f"{BASE_URL}/query",
        json={
            "question": "各部门用户平均使用时长",
            "conversation_id": None
        },
        timeout=30,
    )
    resp.raise_for_status()
    result = resp.json()
    print(f"   ✅ SQL: {result.get('generated_sql', '无')[:80]}")
    print(f"   ✅ 数据行数: {len(result.get('data', {}).get('rows', []))}")
except requests.exceptions.ConnectionError:
    print("   ⚠️  服务未启动，跳过查询测试")
except Exception as e:
    print(f"   ❌ 查询失败: {e}")

print("\n完成！")
