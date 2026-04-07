#!/usr/bin/env python3
"""
NL2SQL 练习评判系统 — 便捷入口
用法：
  python run_grade.py               # 评判今日（自动检测最新未完成 day）
  python run_grade.py day01         # 评判指定 day
  python run_grade.py all           # 评判所有 day
  python run_grade.py --history     # 查看历史成绩
  python run_grade.py --next        # 找出下一个未完成的 day
  python run_grade.py --progress    # 显示进度条

示例：
  python run_grade.py day05          # 评判 Day 05
  python run_grade.py day08 --v     # 评判 Day 08（详细模式）
  python run_grade.py --next        # 告诉我今天应该做哪一天
"""

import sys
import os
from pathlib import Path

# 把 practice 目录加入路径，方便直接 import
PRACTICE_DIR = Path(__file__).parent
sys.path.insert(0, str(PRACTICE_DIR))

from grading_system import (
    run_day_grade, run_all_grade, show_summary,
    load_history, get_day_config
)
import argparse


def find_next_day() -> str | None:
    """找出下一个未完成的 day"""
    history = load_history()
    passed_days = {d for d, v in history.items() if v.get("status") == "PASS"}

    # 按顺序检查 day01 - day23
    for i in range(1, 24):
        day = f"day{i:02d}"
        if day not in passed_days:
            return day
    return None


def main():
    parser = argparse.ArgumentParser(
        description="NL2SQL 练习评判系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("target", nargs="?", default=None,
                        help="day 编号，如 day01，或 all（默认：自动找下一个未完成的 day）")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="详细模式：显示完整标题信息")
    parser.add_argument("--history", action="store_true",
                        help="显示历史成绩总览")
    parser.add_argument("--next", action="store_true",
                        help="显示下一个需要完成的 day")
    parser.add_argument("--progress", action="store_true",
                        help="显示完成进度条")
    args = parser.parse_args()

    if args.history:
        show_summary()
        return

    if args.next:
        next_day = find_next_day()
        if next_day:
            print(f"\n  📌 下一步：{next_day}")
            config = get_day_config(next_day)
            if config:
                print(f"  📝 {config.get('title', '')}")
        else:
            print("\n  🎉 太棒了！所有 23 个练习全部完成！")
        return

    if args.progress:
        history = load_history()
        total = 23
        passed = sum(1 for v in history.values() if v.get("status") == "PASS")
        pct = round(passed / total * 100)
        bar_len = 30
        filled = round(passed / total * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"\n  进度: [{bar}] {passed}/{total} ({pct}%)")
        # 列出未完成的
        passed_set = {d for d, v in history.items() if v.get("status") == "PASS"}
        remaining = [f"day{i:02d}" for i in range(1, 24)
                      if f"day{i:02d}" not in passed_set]
        if remaining:
            print(f"  剩余: {', '.join(remaining[:10])}{'...' if len(remaining) > 10 else ''}")
        print()
        return

    if args.target == "all":
        run_all_grade()
    elif args.target:
        run_day_grade(args.target, verbose=args.verbose)
    else:
        # 默认：找下一个未完成的 day
        next_day = find_next_day()
        if next_day:
            print(f"\n  📌 今日任务：{next_day}")
            print(f"  （可用 --next 查看其他选项，--progress 查看总进度）\n")
            run_day_grade(next_day, verbose=True)
        else:
            print("\n  🎉 所有练习已完成！用 --history 查看成绩，--progress 查看进度。\n")


if __name__ == "__main__":
    main()
