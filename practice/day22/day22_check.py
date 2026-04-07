"""
Day 22 — 练习 22-1：添加会议效率指标

运行此脚本验证 metrics_library.py 已更新
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from backend.rag.metrics_library import BUSINESS_METRICS

    print("=" * 55)
    print("  指标库检查")
    print("=" * 55)

    print(f"\n共有 {len(BUSINESS_METRICS)} 个业务指标")

    # 找会议效率
    meeting_metrics = [m for m in BUSINESS_METRICS if "meeting" in m.get("metric_id", "").lower() or "会议" in m.get("metric_name", "")]
    if meeting_metrics:
        print(f"\n✅ 找到 {len(meeting_metrics)} 个会议相关指标：")
        for m in meeting_metrics:
            print(f"  - {m.get('metric_name')}: {m.get('metric_id')}")
            print(f"    别名: {m.get('aliases', [])}")
    else:
        print("\n⚠️  未找到会议效率指标，请先在 metrics_library.py 中添加")

except ImportError as e:
    print(f"导入失败: {e}")
