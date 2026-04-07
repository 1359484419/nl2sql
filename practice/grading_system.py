"""
NL2SQL 练习评判系统 — Grading Core
用法: python run_grade.py [day_number] 或 python run_grade.py all
"""

import sys
import os
import json
import subprocess
import re
import ast
from pathlib import Path
from datetime import datetime
from typing import Any

# ─────────────────────────────────────────────────────────
# 路径配置
# ─────────────────────────────────────────────────────────
PRACTICE_DIR = Path(__file__).parent
SCORE_HISTORY_FILE = PRACTICE_DIR / "score_history.json"
CONFIG_FILE = PRACTICE_DIR / "config.py"


# ─────────────────────────────────────────────────────────
# 成绩记录读写
# ─────────────────────────────────────────────────────────
def load_history() -> dict:
    if SCORE_HISTORY_FILE.exists():
        return json.loads(SCORE_HISTORY_FILE.read_text(encoding="utf-8"))
    return {}


def save_history(history: dict):
    SCORE_HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def record_score(day: str, score: int, max_score: int, detail: list[str], status: str):
    history = load_history()
    history[day] = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "score": score,
        "max_score": max_score,
        "percentage": round(score / max_score * 100) if max_score else 0,
        "status": status,
        "detail": detail,
    }
    save_history(history)


# ─────────────────────────────────────────────────────────
# 基础检查工具（所有 day 的 check.py 都可以调用这些）
# ─────────────────────────────────────────────────────────

def check_file_exists(filepath: Path | str, desc: str = "") -> tuple[bool, str]:
    """检查文件是否存在"""
    p = Path(filepath)
    if p.exists():
        return True, f"  ✅ {desc or p.name} 存在"
    return False, f"  ❌ {desc or str(p)} 文件不存在！"


def check_file_not_empty(filepath: Path | str, desc: str = "") -> tuple[bool, str]:
    """检查文件是否非空"""
    p = Path(filepath)
    if not p.exists():
        return False, f"  ⚠️  {p.name} 不存在，无法检查内容"
    content = p.read_text(encoding="utf-8").strip()
    if len(content) < 10:
        return False, f"  ⚠️  {p.name} 内容过少（{len(content)} 字符），可能还没写"
    return True, f"  ✅ {p.name} 有内容（{len(content)} 字符）"


def check_code_runs(filepath: Path | str, desc: str = "") -> tuple[bool, str, str]:
    """
    运行一个 Python 文件，返回 (是否成功, 描述, 错误信息)
    """
    p = Path(filepath)
    if not p.exists():
        return False, f"  ❌ {p.name} 不存在", ""

    try:
        result = subprocess.run(
            [sys.executable, str(p)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(p.parent),
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            return True, f"  ✅ {p.name} 运行成功", output
        else:
            error = result.stderr.strip()
            # 截断错误信息
            if len(error) > 300:
                error = error[:300] + "\n  ... (错误过长已截断)"
            return False, f"  ❌ {p.name} 运行失败", error
    except subprocess.TimeoutExpired:
        return False, f"  ⏱️  {p.name} 运行超时（30秒）", "Timeout"
    except Exception as e:
        return False, f"  ❌ {p.name} 运行异常: {e}", str(e)


def check_code_output_contains(
    filepath: Path | str, substr: str, desc: str = "", case_sensitive: bool = False
) -> tuple[bool, str]:
    """
    检查代码输出是否包含某个字符串
    """
    p = Path(filepath)
    if not p.exists():
        return False, f"  ⚠️  {p.name} 不存在"

    try:
        result = subprocess.run(
            [sys.executable, str(p)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(p.parent),
        )
        output = result.stdout if case_sensitive else result.stdout.lower()
        target = substr if case_sensitive else substr.lower()
        if target in output:
            return True, f"  ✅ {desc or f'输出包含「{substr}」'}"
        else:
            # 显示实际输出前100字
            actual = result.stdout.strip()[:150]
            return False, (
                f"  ❌ {desc or f'输出未包含「{substr}」'}\n"
                f"     实际输出: {actual or '(空输出)'}"
            )
    except Exception as e:
        return False, f"  ⚠️  运行检查失败: {e}"


def check_output_equals(
    filepath: Path | str, expected: str, desc: str = ""
) -> tuple[bool, str]:
    """检查代码输出是否等于指定字符串"""
    p = Path(filepath)
    if not p.exists():
        return False, f"  ⚠️  {p.name} 不存在"

    try:
        result = subprocess.run(
            [sys.executable, str(p)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(p.parent),
        )
        actual = result.stdout.strip()
        if actual == expected:
            return True, f"  ✅ {desc or '输出正确'}"
        return False, (
            f"  ❌ {desc or '输出不符'}\n"
            f"     期望: {expected}\n"
            f"     实际: {actual[:150] or '(空)'}"
        )
    except Exception as e:
        return False, f"  ⚠️  运行失败: {e}"


def check_imports(filepath: Path | str, import_name: str) -> tuple[bool, str]:
    """检查文件是否导入了某个模块"""
    p = Path(filepath)
    if not p.exists():
        return False, f"  ⚠️  {p.name} 不存在"

    content = p.read_text(encoding="utf-8")
    # 简单检查 import 行
    if re.search(rf"^\s*(import|from)\s+{re.escape(import_name)}", content, re.MULTILINE):
        return True, f"  ✅ 导入了 {import_name}"
    return False, f"  ❌ 未找到 import {import_name}"


def check_regex_in_file(
    filepath: Path | str, pattern: str, desc: str = "", flags: int = 0
) -> tuple[bool, str]:
    """检查文件内容是否匹配某个正则"""
    p = Path(filepath)
    if not p.exists():
        return False, f"  ⚠️  {p.name} 不存在"

    content = p.read_text(encoding="utf-8")
    if re.search(pattern, content, flags):
        return True, f"  ✅ {desc or f'匹配模式: {pattern}'}"
    return False, f"  ❌ 未找到: {desc or pattern}"


def check_syntax_ok(filepath: Path | str) -> tuple[bool, str]:
    """检查 Python 文件语法是否正确"""
    p = Path(filepath)
    if not p.exists():
        return False, f"  ⚠️  {p.name} 不存在"

    try:
        with open(p, encoding="utf-8") as f:
            ast.parse(f.read())
        return True, f"  ✅ {p.name} 语法正确"
    except SyntaxError as e:
        return False, f"  ❌ {p.name} 语法错误: {e.msg} (line {e.lineno})"


def check_function_exists(filepath: Path | str, func_name: str) -> tuple[bool, str]:
    """检查函数是否定义"""
    p = Path(filepath)
    if not p.exists():
        return False, f"  ⚠️  {p.name} 不存在"

    content = p.read_text(encoding="utf-8")
    # 匹配 def func_name 或 async def func_name
    pattern = rf"^\s*(async\s+)?def\s+{re.escape(func_name)}\s*\("
    if re.search(pattern, content, re.MULTILINE):
        return True, f"  ✅ 函数 {func_name}() 已定义"
    return False, f"  ❌ 未找到函数 {func_name}()"


def check_class_exists(filepath: Path | str, class_name: str) -> tuple[bool, str]:
    """检查类是否定义"""
    p = Path(filepath)
    if not p.exists():
        return False, f"  ⚠️  {p.name} 不存在"

    content = p.read_text(encoding="utf-8")
    pattern = rf"^\s*class\s+{re.escape(class_name)}\s*[\(:]"
    if re.search(pattern, content, re.MULTILINE):
        return True, f"  ✅ 类 {class_name} 已定义"
    return False, f"  ❌ 未找到类 {class_name}"


# ─────────────────────────────────────────────────────────
# 评判执行器
# ─────────────────────────────────────────────────────────
def run_checks(checks: list[dict]) -> tuple[int, int, list[str]]:
    """
    执行一组检查，返回 (得分, 满分, 详细信息)
    每项检查格式: {"desc": str, "check": callable, "weight": int}
    weight 默认为 1
    """
    total_score = 0
    max_score = 0
    detail_lines = []

    for item in checks:
        desc = item.get("desc", "检查项")
        check_fn = item["check"]
        weight = item.get("weight", 1)
        max_score += weight

        try:
            result = check_fn()
            if isinstance(result, tuple):
                ok, msg = result[0], result[1]
                output = result[2] if len(result) > 2 else ""
            else:
                ok, msg = bool(result), "检查完成"

            detail_lines.append(msg)
            if output:
                detail_lines.append(f"     输出: {output[:200]}")
            if ok:
                total_score += weight
                detail_lines[-1] = "✅ " + detail_lines[-1].lstrip(" ✅❌⚠️⏱️ ")
            else:
                detail_lines[-1] = "❌ " + detail_lines[-1].lstrip(" ✅❌⚠️⏱️ ")

        except Exception as e:
            max_score += weight
            detail_lines.append(f"  ⚠️  {desc} 检查异常: {e}")

    return total_score, max_score, detail_lines


def print_report(day: str, score: int, max_score: int, detail: list[str], status: str):
    pct = round(score / max_score * 100) if max_score else 0

    print("\n" + "═" * 60)
    print(f"  📅 Day {day}  —  得分: {score}/{max_score}  ({pct}%)  [{status}]")
    print("═" * 60)

    for line in detail:
        print(line)

    print("─" * 60)

    if status == "PASS":
        print("  🎉 全部通过！今天的练习完成得非常好！")
    elif status == "GOOD":
        print("  👍 做得不错！修复红色项后即可满分。")
    elif status == "PARTIAL":
        print("  📝 有进步！继续加油，完成剩余部分。")
    else:
        print("  💪 继续努力！先解决红色报错，再继续。")

    print()


# ─────────────────────────────────────────────────────────
# Day 配置加载（从 config.py 动态导入）
# ─────────────────────────────────────────────────────────
def get_day_config(day: str) -> dict | None:
    """从 config.py 获取指定 day 的配置"""
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("config", CONFIG_FILE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        config = getattr(module, "DAY_CONFIG", {})
        return config.get(day)
    except Exception as e:
        print(f"  ⚠️  无法加载 config.py: {e}")
        return None


def run_day_grade(day: str, verbose: bool = False) -> bool:
    """评判指定 day，返回是否 PASS"""
    config = get_day_config(day)
    if not config:
        print(f"\n  ❌ Day {day} 配置不存在，请检查 config.py")
        return False

    title = config.get("title", f"Day {day}")
    checks = config.get("checks", [])

    if verbose:
        print(f"\n{'='*60}")
        print(f"  📋 {title}")
        print(f"  ⏱️  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

    score, max_score, detail = run_checks(checks)
    pct = score / max_score if max_score else 0

    # 评级
    if pct >= 1.0:
        status = "PASS"
    elif pct >= 0.8:
        status = "GOOD"
    elif pct >= 0.5:
        status = "PARTIAL"
    else:
        status = "TODO"

    print_report(day, score, max_score, detail, status)

    record_score(day, score, max_score, detail, status)

    return status == "PASS"


def run_all_grade() -> dict[str, str]:
    """评判所有已配置的 day"""
    results = {}

    print("\n" + "█" * 60)
    print("  🏆 NL2SQL 练习评判系统 — 全部 Day 评分")
    print("█" * 60)

    # 找出所有已配置的 day
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("config", CONFIG_FILE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        all_days = sorted(
            getattr(module, "DAY_CONFIG", {}).keys(),
            key=lambda x: int(x.replace("day", "")),
        )
    except Exception:
        all_days = [f"day{i:02d}" for i in range(1, 24)]

    for day in all_days:
        passed = run_day_grade(day, verbose=False)
        results[day] = "PASS" if passed else "FAIL"

    # 汇总
    total = len(all_days)
    passed = sum(1 for v in results.values() if v == "PASS")

    print("\n" + "█" * 60)
    print(f"  📊 总进度: {passed}/{total} 天完成")
    print("  📊 详细结果:")
    for d, r in results.items():
        icon = "✅" if r == "PASS" else "❌"
        print(f"     {icon} {d}: {r}")
    print("█" * 60)

    return results


def show_summary():
    """显示历史成绩总览"""
    history = load_history()
    if not history:
        print("\n  📭 暂无成绩记录，开始 Day 01 吧！\n")
        return

    print("\n" + "─" * 60)
    print("  📊 历史成绩总览")
    print("─" * 60)

    total_days = len(history)
    passed_days = sum(1 for v in history.values() if v["status"] == "PASS")
    total_score = sum(v["score"] for v in history.values())
    total_max = sum(v["max_score"] for v in history.values())

    print(f"  总进度: {passed_days}/{total_days} 天 PASS")
    print(f"  总得分: {total_score}/{total_max} ({round(total_score/total_max*100) if total_max else 0}%)")
    print("─" * 60)

    for day in sorted(history.keys(), key=lambda x: int(x.replace("day", ""))):
        entry = history[day]
        icon = "✅" if entry["status"] == "PASS" else "⚠️ "
        pct = entry.get("percentage", 0)
        print(f"  {icon} {day} ({entry['date']}) — {entry['score']}/{entry['max_score']} ({pct}%) [{entry['status']}]")

    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="NL2SQL 练习评判系统")
    parser.add_argument("target", nargs="?", default="all", help="day 编号，如 day01，或 all")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细模式")
    parser.add_argument("--history", action="store_true", help="显示历史成绩")
    args = parser.parse_args()

    if args.history:
        show_summary()
    elif args.target == "all":
        run_all_grade()
    elif args.target.startswith("day"):
        run_day_grade(args.target, verbose=True)
    else:
        print(f"用法: python run_grade.py day01")
        print(f"       python run_grade.py all")
        print(f"       python run_grade.py --history")
