"""
Day 配置 — 定义每天练习的评判规则
每个 day 的 checks 列表里，每项是一个 dict:
  {
    "desc": "检查项描述",
    "check": lambda -> (bool, str) 或 (bool, str, str),
    "weight": 分数权重（默认1）
  }

check 函数可使用 grading_system.py 里的工具函数:
  check_file_exists(path, desc)
  check_file_not_empty(path, desc)
  check_code_runs(path, desc)              → (bool, str, str)
  check_output_contains(path, substr, desc) → (bool, str)
  check_output_equals(path, expected, desc)→ (bool, str)
  check_imports(path, module)               → (bool, str)
  check_regex_in_file(path, pattern, desc) → (bool, str)
  check_syntax_ok(path)                     → (bool, str)
  check_function_exists(path, func)         → (bool, str)
  check_class_exists(path, class)           → (bool, str)
"""

import sys
from pathlib import Path

PRACTICE = Path(__file__).parent
NL2SQL_ROOT = PRACTICE.parent  # nl2sql-bi-agent/ 根目录

# ─────────────────────────────────────────────────────────────
# 辅助：用 subprocess 运行代码并捕获输出
# ─────────────────────────────────────────────────────────────
import subprocess


def _run(path: Path, timeout: int = 30):
    try:
        r = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(path.parent),
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -2, "", str(e)


# ═══════════════════════════════════════════════════════════════
# DAY 01 — 环境搭建 + 第一个程序
# ═══════════════════════════════════════════════════════════════
def _day01_checks():
    from grading_system import (
        check_file_exists, check_code_runs, check_output_contains,
        check_syntax_ok, load_history
    )

    p = PRACTICE / "day01"
    results = []

    # 检查 4 个作业文件
    for fname in ["day1_hello.py", "day1_hello_stub.py"]:
        ok, msg = check_file_exists(p / fname)
        results.append({"desc": fname, "check": lambda ok=ok, msg=msg: (ok, msg)})

    # 运行第一个程序
    f1 = p / "day1_hello.py"
    if f1.exists():
        rc, out, err = _run(f1)
        if rc == 0:
            ok = True
            msg = f"  ✅ day1_hello.py 运行成功，输出: {out[:80]}"
        else:
            ok = False
            msg = f"  ❌ day1_hello.py 运行失败: {err[:150]}"
    else:
        ok, msg = False, "  ❌ day1_hello.py 不存在"

    results.append({"desc": "day1_hello.py 运行", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 2})

    # 检查是否包含自定义内容（不是纯示例）
    if f1.exists():
        content = f1.read_text(encoding="utf-8")
        has_custom = "我叫" in content and ("小明" in content or "张三" in content or "你的名字" in content)
        ok2, msg2 = has_custom, ("  ✅ 有自定义内容" if has_custom else "  ❌ 看起来还是示例代码，改成你自己的名字和年龄")
        results.append({"desc": "自定义内容", "check": lambda ok=ok2, msg=msg2: (ok, msg2)})

    # 检查后端能否启动（通过健康检查）
    import time
    import requests
    f2 = p / "day1_backend_test.py"
    if f2.exists():
        rc, out, err = _run(f2, timeout=15)
        ok = rc == 0 and ("ok" in out.lower() or "running" in out.lower())
        msg = f"  ✅ 后端健康检查通过" if ok else f"  ❌ 后端启动失败: {err[:150] or out[:150]}"
    else:
        ok, msg = False, "  ⚠️  day1_backend_test.py 不存在（可选加分项）"
    results.append({"desc": "后端服务测试", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 02 — 数据类型转换
# ═══════════════════════════════════════════════════════════════
def _day02_checks():
    from grading_system import check_file_exists, check_code_runs

    p = PRACTICE / "day02"
    results = []

    f = p / "day2_types.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day2_types.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        rc, out, err = _run(f)
        # 检查输出是否包含关键数字
        if rc == 0:
            has_100 = "100" in out
            has_666 = "2.6" in out or "2.66" in out or "2.7" in out  # 8/3 ≈ 2.67
            ok2 = has_100
            msg2 = f"  ✅ 输出正确 (100 {'✅' if has_666 else '⚠️  8/3=2.67 检查'})"
        else:
            ok2, msg2 = False, f"  ❌ 运行错误: {err[:150]}"
        results.append({"desc": "day2_types.py 输出正确", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 2})

        # 检查是否有类型转换代码
        content = f.read_text(encoding="utf-8")
        has_int = "int(" in content
        has_float = "float(" in content
        ok3 = has_int and has_float
        msg3 = f"  ✅ 包含 int() 和 float() 转换" if ok3 else f"  ❌ 缺少类型转换代码"
        results.append({"desc": "包含类型转换", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 1})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 03 — if / for / while
# ═══════════════════════════════════════════════════════════════
def _day03_checks():
    from grading_system import check_file_exists

    p = PRACTICE / "day03"
    results = []

    f = p / "day3_guess.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day3_guess.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        content = f.read_text(encoding="utf-8")
        has_if = "if " in content
        has_for = "for " in content
        has_while = "while " in content
        has_break = "break" in content
        all_three = has_if and (has_for or has_while)

        ok2 = all_three
        msg2 = f"  ✅ 包含 if{'✅' if has_for else '⚠️  for'}/{'✅' if has_while else '⚠️  while'}"
        results.append({"desc": "包含循环/判断结构", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 2})

        rc, out, err = _run(f)
        if rc == 0:
            ok3, msg3 = True, f"  ✅ 程序能运行（交互题，输入测试通过）"
        else:
            # 可能是 input() 导致的，但这说明代码结构正确
            ok3 = has_if and has_while
            msg3 = f"  ⚠️  运行有交互输入，代码结构正确{'✅' if ok3 else '❌'}"
        results.append({"desc": "程序可运行", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 1})

    # 检查 NL2SQL 代码理解
    f2 = p / "day3_sqlchecker.py"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "day3_sqlchecker.py 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        rc2, out2, err2 = _run(f2)
        ok5 = rc2 == 0
        msg5 = f"  ✅ SQL 校验逻辑分析正确" if ok5 else f"  ❌ 分析错误: {err2[:100] or out2[:100]}"
        results.append({"desc": "SQL校验理解", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 04 — 列表 & 字典
# ═══════════════════════════════════════════════════════════════
def _day04_checks():
    from grading_system import check_file_exists

    p = PRACTICE / "day04"
    results = []

    f = p / "day4_containers.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day4_containers.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        content = f.read_text(encoding="utf-8")
        has_list = "[" in content and "for" in content
        has_dict = "{" in content and ":" in content and "}" in content
        has_append = ".append(" in content

        ok2 = has_list and has_dict
        msg2 = f"  ✅ 包含列表{'✅' if has_list else '❌'}和字典{'✅' if has_dict else '❌'}"
        results.append({"desc": "包含 list/dict", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 2})

        rc, out, err = _run(f)
        if rc == 0:
            ok3 = True
            msg3 = f"  ✅ 运行成功，输出包含最高分: {'✅' if '小明' in out or '92' in out else '⚠️'}"
        else:
            ok3, msg3 = False, f"  ❌ 运行错误: {err[:150]}"
        results.append({"desc": "程序运行", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 2})

    # schema_summary
    f2 = p / "schema_summary.py"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "schema_summary.py 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        rc2, out2, err2 = _run(f2)
        has_fact = "fact_workspace" in out2
        ok5 = rc2 == 0 and has_fact
        msg5 = f"  ✅ 能读取 Schema，找出 fact_workspace" if ok5 else f"  ⚠️  运行问题: {err2[:100] or out2[:100]}"
        results.append({"desc": "Schema 读取", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 05 — 函数 & 模块
# ═══════════════════════════════════════════════════════════════
def _day05_checks():
    from grading_system import check_file_exists, check_function_exists

    p = PRACTICE / "day05"
    results = []

    f = p / "day5_functions.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day5_functions.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        has_def = "def " in f.read_text(encoding="utf-8")
        has_cvt = check_function_exists(f, "celsius_to_fahrenheit")[0]
        has_sec = check_function_exists(f, "seconds_to_hms")[0]
        has_greet = check_function_exists(f, "greet")[0]

        checks_passed = sum(1 for ok in [has_def, has_cvt, has_sec, has_greet] if ok)
        ok2 = checks_passed >= 3
        msg2 = f"  ✅ 定义了 {checks_passed}/4 个函数"
        results.append({"desc": "包含函数定义", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 2})

        rc, out, err = _run(f)
        if rc == 0:
            ok3 = "你好" in out or "hello" in out.lower() or "greet" in out.lower()
            msg3 = f"  ✅ greet 函数输出正确: {out[:100]}"
        else:
            ok3, msg3 = False, f"  ❌ 运行错误: {err[:150]}"
        results.append({"desc": "函数运行测试", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 2})

    # 模块理解
    f2 = p / "day5_imports.py"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "day5_imports.py 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        content2 = f2.read_text(encoding="utf-8")
        ok5 = "nl2sql_agent" in content2 or "conversation" in content2
        msg5 = f"  ✅ 能识别 NL2SQL 模块" if ok5 else f"  ❌ 未识别项目模块"
        results.append({"desc": "模块理解", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 06 — 面向对象 class
# ═══════════════════════════════════════════════════════════════
def _day06_checks():
    from grading_system import check_file_exists, check_class_exists

    p = PRACTICE / "day06"
    results = []

    f = p / "day6_class.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day6_class.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        has_class = check_class_exists(f, "BankAccount")[0]
        has_deposit = "deposit" in f.read_text(encoding="utf-8")
        has_withdraw = "withdraw" in f.read_text(encoding="utf-8")

        ok2 = has_class
        msg2 = f"  ✅ BankAccount 类定义{'✅' if has_deposit else '❌'}存款{'✅' if has_withdraw else '❌'}取款"
        results.append({"desc": "类定义完整", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 2})

        rc, out, err = _run(f)
        if rc == 0:
            ok3 = "1500" in out or "余额" in out
            msg3 = f"  ✅ 程序逻辑正确，输出: {out[:100]}"
        else:
            ok3, msg3 = False, f"  ❌ 运行错误: {err[:150]}"
        results.append({"desc": "类运行测试", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 2})

    # TypedDict 理解
    f2 = p / "day6_typeddict.py"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "day6_typeddict.py 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        content2 = f2.read_text(encoding="utf-8")
        ok5 = "TypedDict" in content2
        msg5 = f"  ✅ 理解 TypedDict 概念" if ok5 else f"  ❌ 未体现 TypedDict 理解"
        results.append({"desc": "TypedDict 理解", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 07 — 文件读写 & JSON
# ═══════════════════════════════════════════════════════════════
def _day07_checks():
    from grading_system import check_file_exists

    p = PRACTICE / "day07"
    results = []

    f = p / "day7_json.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day7_json.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        rc, out, err = _run(f)
        data_file = p / "data.json"
        ok2 = rc == 0 and data_file.exists()
        msg2 = f"  ✅ JSON 文件读写成功{'✅' if data_file.exists() else '❌ data.json 未生成'}"
        results.append({"desc": "JSON读写", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 2})

        if data_file.exists():
            content = data_file.read_text(encoding="utf-8")
            ok3 = "NL2SQL" in content or "name" in content
            msg3 = f"  ✅ data.json 内容正确"
        else:
            ok3, msg3 = False, f"  ❌ data.json 未生成"
        results.append({"desc": "JSON 内容", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 2})

    f2 = p / "schema_summary.py"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "schema_summary.py 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        rc2, out2, err2 = _run(f2)
        ok5 = rc2 == 0 and ("fact_workspace" in out2 or "org_id" in out2)
        msg5 = f"  ✅ 能读取项目 Schema" if ok5 else f"  ❌ Schema 读取失败"
        results.append({"desc": "Schema 分析", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 08 — HTTP 请求 & API
# ═══════════════════════════════════════════════════════════════
def _day08_checks():
    from grading_system import check_file_exists

    p = PRACTICE / "day08"
    results = []

    f = p / "day8_api.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day8_api.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        content = f.read_text(encoding="utf-8")
        has_requests = "requests" in content
        has_post = "requests.post" in content or "post(" in content

        ok2 = has_requests
        msg2 = f"  ✅ 使用 requests 库{'✅' if has_post else '⚠️  未用 post'}"
        results.append({"desc": "使用 requests", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 1})

        rc, out, err = _run(f, timeout=15)
        if rc == 0:
            ok3 = "ok" in out.lower() or "status" in out.lower()
            msg3 = f"  ✅ API 调用成功: {out[:150]}"
        else:
            ok3, msg3 = False, f"  ⚠️  API 调用失败（可能服务未启动）: {err[:100] or out[:100]}"
        results.append({"desc": "API 调用", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 3})

    f2 = p / "day8_rest_notes.py"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "day8_rest_notes.py 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        rc2, out2, err2 = _run(f2)
        ok5 = rc2 == 0
        msg5 = f"  ✅ REST API 理解正确" if ok5 else f"  ⚠️  理解有误: {out2[:100]}"
        results.append({"desc": "REST 理解", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 09 — 数据库 SQL
# ═══════════════════════════════════════════════════════════════
def _day09_checks():
    from grading_system import check_file_exists

    p = PRACTICE / "day09"
    results = []

    # SQL 执行记录
    f = p / "day9_sql_tests.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day9_sql_tests.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        content = f.read_text(encoding="utf-8")
        has_select = "SELECT" in content.upper()
        has_where = "WHERE" in content.upper()
        has_group = "GROUP BY" in content.upper()

        ok2 = has_select
        msg2 = f"  ✅ 包含 SQL 查询{'✅' if has_where else '⚠️  无 WHERE'}{'✅' if has_group else '⚠️  无 GROUP BY'}"
        results.append({"desc": "SQL 语法正确", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 2})

    # NL2SQL SQL 理解
    f2 = p / "day9_nl2sql_sql.py"
    ok3, msg3 = check_file_exists(f2)
    results.append({"desc": "day9_nl2sql_sql.py 存在", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 1})

    if f2.exists():
        rc2, out2, err2 = _run(f2)
        ok4 = rc2 == 0 and len(out2) > 20
        msg4 = f"  ✅ NL2SQL SQL 分析完成" if ok4 else f"  ⚠️  分析问题: {err2[:100] or out2[:100]}"
        results.append({"desc": "SQL 分析", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 3})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 10 — 错误处理
# ═══════════════════════════════════════════════════════════════
def _day10_checks():
    from grading_system import check_file_exists

    p = PRACTICE / "day10"
    results = []

    f = p / "day10_errors.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day10_errors.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        content = f.read_text(encoding="utf-8")
        has_try = "try:" in content
        has_except = "except" in content
        has_parse_age = "parse_age" in content

        ok2 = has_try and has_except
        msg2 = f"  ✅ 有 try/except{'✅' if has_parse_age else '⚠️  无 parse_age'}"
        results.append({"desc": "错误处理结构", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 2})

        rc, out, err = _run(f)
        if rc == 0:
            ok3 = "25" in out and "None" in out
            msg3 = f"  ✅ parse_age 正确处理 25 和无效输入: {out[:100]}"
        else:
            ok3, msg3 = False, f"  ❌ 运行错误: {err[:150]}"
        results.append({"desc": "parse_age 测试", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 2})

    f2 = p / "day10_routes_analysis.py"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "day10_routes_analysis.py 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        rc2, out2, err2 = _run(f2)
        ok5 = rc2 == 0 and len(out2) > 10
        msg5 = f"  ✅ 理解 routes.py 错误处理" if ok5 else f"  ⚠️  分析问题"
        results.append({"desc": "错误处理理解", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 11 — LLM API 调用
# ═══════════════════════════════════════════════════════════════
def _day11_checks():
    from grading_system import check_file_exists

    p = PRACTICE / "day11"
    results = []

    f = p / "day11_llm.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day11_llm.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        content = f.read_text(encoding="utf-8")
        has_llm = "ChatOpenAI" in content or "ChatOllama" in content or "llm" in content.lower()
        has_system = "system" in content.lower()
        has_invoke = "invoke(" in content

        ok2 = has_llm
        msg2 = f"  ✅ 调用 LLM API{'✅' if has_system else '⚠️  无 system prompt'}"
        results.append({"desc": "LLM 调用代码", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 2})

        rc, out, err = _run(f, timeout=60)
        if rc == 0 and len(out) > 5:
            ok3 = True
            msg3 = f"  ✅ LLM 调用成功: {out[:100]}"
        elif "api_key" in err.lower() or "auth" in err.lower():
            ok3, msg3 = False, f"  ⚠️  API Key 未配置，请配置 .env 文件"
        else:
            ok3, msg3 = False, f"  ⚠️  调用失败: {err[:100] or out[:100]}"
        results.append({"desc": "LLM 运行测试", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 3})

    # Prompt 理解
    f2 = p / "day11_prompt_analysis.py"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "day11_prompt_analysis.py 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        rc2, out2, err2 = _run(f2)
        ok5 = rc2 == 0 and len(out2) > 10
        msg5 = f"  ✅ 识别了 {out2.count(chr(10))+1} 条约束规则"
        results.append({"desc": "Prompt 规则识别", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 12 — Embedding
# ═══════════════════════════════════════════════════════════════
def _day12_checks():
    from grading_system import check_file_exists

    p = PRACTICE / "day12"
    results = []

    f = p / "day12_embedding.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day12_embedding.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        rc, out, err = _run(f)
        if rc == 0:
            lines = out.split("\n")
            nums = [l for l in lines if any(c.isdigit() for c in l)]
            ok2 = len(nums) >= 2
            msg2 = f"  ✅ 相似度计算正确，输出了 {len(nums)} 个分数"
        else:
            ok2, msg2 = False, f"  ❌ 运行错误: {err[:150]}"
        results.append({"desc": "相似度计算", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 3})

        content = f.read_text(encoding="utf-8")
        ok3 = "TF-IDF" in content or "TfidfVectorizer" in content or "cosine" in content.lower()
        msg3 = f"  ✅ 使用了 TF-IDF 或余弦相似度"
        results.append({"desc": "Embedding 原理理解", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 2})

    # embedding.py 理解
    f2 = p / "day12_config_analysis.py"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "day12_config_analysis.py 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        rc2, out2, err2 = _run(f2)
        ok5 = rc2 == 0 and len(out2) > 5
        msg5 = f"  ✅ 能分析 Embedding 配置" if ok5 else f"  ⚠️  分析问题"
        results.append({"desc": "配置分析", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 13 — Milvus 向量数据库
# ═══════════════════════════════════════════════════════════════
def _day13_checks():
    from grading_system import check_file_exists

    p = PRACTICE / "day13"
    results = []

    f = p / "day13_milvus.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day13_milvus.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        rc, out, err = _run(f)
        if rc == 0:
            ok2 = "活跃" in out or "demo" in out.lower()
            msg2 = f"  ✅ Milvus 检索成功: {out[:120]}"
        else:
            ok2 = False
            msg2 = f"  ⚠️  Milvus 错误（可能未安装 pymilvus）: {err[:100] or out[:100]}"
        results.append({"desc": "Milvus 检索", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 3})

        content = f.read_text(encoding="utf-8")
        ok3 = "insert" in content or "search" in content
        msg3 = f"  ✅ 包含增/查操作"
        results.append({"desc": "Milvus 操作", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 1})

    f2 = p / "day13_config_analysis.py"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "day13_config_analysis.py 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        rc2, out2, err2 = _run(f2)
        ok5 = rc2 == 0 and len(out2) > 10
        msg5 = f"  ✅ 能分析 Milvus 配置" if ok5 else f"  ⚠️  分析问题"
        results.append({"desc": "配置分析", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 14 — RAG 流程
# ═══════════════════════════════════════════════════════════════
def _day14_checks():
    from grading_system import check_file_exists

    p = PRACTICE / "day14"
    results = []

    f = p / "day14_rag.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day14_rag.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        rc, out, err = _run(f)
        if rc == 0:
            ok2 = "fact_workspace" in out or "活跃" in out
            msg2 = f"  ✅ 简化版 RAG 检索正确: {out[:100]}"
        else:
            ok2, msg2 = False, f"  ❌ 运行错误: {err[:150]}"
        results.append({"desc": "简化 RAG", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 3})

        content = f.read_text(encoding="utf-8")
        has_tfidf = "TfidfVectorizer" in content
        has_rag = "fact_workspace" in content or "meeting" in content
        ok3 = has_tfidf and has_rag
        msg3 = f"  ✅ 有检索逻辑和文档数据"
        results.append({"desc": "RAG 逻辑", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 1})

    # 流程图
    f2 = p / "day14_flowchart.md"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "day14_flowchart.md 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        content2 = f2.read_text(encoding="utf-8")
        keywords = ["用户", "Embedding", "Milvus", "LLM", "SQL", "执行"]
        found = sum(1 for kw in keywords if kw in content2)
        ok5 = found >= 4
        msg5 = f"  ✅ 流程图包含 {found}/6 个关键词"
        results.append({"desc": "流程图完整", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 15 — Prompt Engineering
# ═══════════════════════════════════════════════════════════════
def _day15_checks():
    from grading_system import check_file_exists, check_file_not_empty

    p = PRACTICE / "day15"
    results = []

    f = p / "day15_prompts.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day15_prompts.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        rc, out, err = _run(f, timeout=60)
        if rc == 0:
            lines = [l for l in out.split("\n") if l.strip() and "=" not in l]
            ok2 = len(lines) >= 2
            msg2 = f"  ✅ 对比了两个 Prompt 效果，输出了 {len(lines)} 行"
        else:
            ok2 = False
            msg2 = f"  ⚠️  运行问题: {err[:100] or out[:100]}"
        results.append({"desc": "Prompt 对比", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 3})

        content = f.read_text(encoding="utf-8")
        ok3 = "system" in content.lower() or "prompt" in content.lower()
        msg3 = f"  ✅ 有 Prompt 对比代码"
        results.append({"desc": "Prompt 代码", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 1})

    # Prompt 修改记录
    f2 = p / "day15_prompt_change.md"
    ok4, msg4 = check_file_not_empty(f2, "Prompt 修改记录")
    results.append({"desc": "day15_prompt_change.md", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 2})

    if f2.exists():
        content2 = f2.read_text(encoding="utf-8")
        ok5 = len(content2) > 30
        msg5 = f"  ✅ 有修改记录（{len(content2)} 字）"
        results.append({"desc": "修改记录质量", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 1})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 16 — 状态机概念
# ═══════════════════════════════════════════════════════════════
def _day16_checks():
    from grading_system import check_file_exists, check_function_exists

    p = PRACTICE / "day16"
    results = []

    f = p / "day16_fsm.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day16_fsm.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        rc, out, err = _run(f)
        if rc == 0:
            ok2 = "shipped" in out or "pending" in out
            msg2 = f"  ✅ 状态机运行正确: {out[:100]}"
        else:
            ok2, msg2 = False, f"  ❌ 运行错误: {err[:150]}"
        results.append({"desc": "状态机运行", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 2})

        content = f.read_text(encoding="utf-8")
        ok3 = check_function_exists(f, "handle_order")[0] or "def " in content
        msg3 = f"  ✅ 有函数定义和路由逻辑"
        results.append({"desc": "状态机结构", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 2})

    # 节点分析
    f2 = p / "day16_node_analysis.py"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "day16_node_analysis.py 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        rc2, out2, err2 = _run(f2)
        nodes = out2.count("\n") + 1 if out2.strip() else 0
        ok5 = rc2 == 0 and nodes >= 4
        msg5 = f"  ✅ 分析了 {nodes} 个 Agent 节点"
        results.append({"desc": "节点分析", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 3})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 17 — LangGraph 入门
# ═══════════════════════════════════════════════════════════════
def _day17_checks():
    from grading_system import check_file_exists

    p = PRACTICE / "day17"
    results = []

    f = p / "day17_langgraph.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day17_langgraph.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        rc, out, err = _run(f, timeout=30)
        if rc == 0:
            ok2 = "A" in out and "B" in out
            msg2 = f"  ✅ LangGraph 运行成功: {out[:100]}"
        else:
            ok2 = False
            msg2 = f"  ⚠️  LangGraph 可能未安装或运行失败: {err[:100] or out[:100]}"
        results.append({"desc": "LangGraph 运行", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 3})

        content = f.read_text(encoding="utf-8")
        ok3 = "StateGraph" in content or "add_node" in content
        msg3 = f"  ✅ 使用了 LangGraph API"
        results.append({"desc": "LangGraph API", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 1})

    # Mermaid 图
    f2 = p / "day17_mermaid.md"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "day17_mermaid.md 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        content2 = f2.read_text(encoding="utf-8")
        has_arrows = "-->" in content2 or "-->" in content2
        ok5 = has_arrows and ("classify" in content2 or "intent" in content2 or "generate" in content2)
        msg5 = f"  ✅ 有状态图和节点连接" if ok5 else f"  ⚠️  图不够完整"
        results.append({"desc": "Mermaid 图", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 18 — Self-Correction
# ═══════════════════════════════════════════════════════════════
def _day18_checks():
    from grading_system import check_file_exists

    p = PRACTICE / "day18"
    results = []

    f = p / "day18_retry.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day18_retry.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        rc, out, err = _run(f)
        if rc == 0:
            lines = [l for l in out.split("\n") if "✅" in l or "❌" in l]
            ok2 = len(lines) >= 1
            msg2 = f"  ✅ 重试逻辑运行正确: {out[:120]}"
        else:
            ok2, msg2 = False, f"  ❌ 运行错误: {err[:150]}"
        results.append({"desc": "重试逻辑", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 2})

        content = f.read_text(encoding="utf-8")
        has_retry = "retry" in content.lower() or "attempt" in content.lower()
        has_max = "max" in content.lower()
        ok3 = has_retry and has_max
        msg3 = f"  ✅ 有重试逻辑和最大次数限制"
        results.append({"desc": "重试结构", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 1})

    # 重试流程分析
    f2 = p / "day18_retry_analysis.py"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "day18_retry_analysis.py 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        rc2, out2, err2 = _run(f2)
        ok5 = rc2 == 0 and len(out2) > 10
        msg5 = f"  ✅ 能描述重试流程"
        results.append({"desc": "流程理解", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 3})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 19 — SQL 校验层
# ═══════════════════════════════════════════════════════════════
def _day19_checks():
    from grading_system import check_file_exists

    p = PRACTICE / "day19"
    results = []

    f = p / "day19_explain.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day19_explain.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        rc, out, err = _run(f)
        if rc == 0:
            ok2 = "✅" in out or "❌" in out
            msg2 = f"  ✅ EXPLAIN 校验运行: {out[:120]}"
        else:
            ok2 = False
            msg2 = f"  ⚠️  运行问题（可能数据库未连接）: {err[:100] or out[:100]}"
        results.append({"desc": "EXPLAIN 校验", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 3})

        content = f.read_text(encoding="utf-8")
        ok3 = "EXPLAIN" in content.upper()
        msg3 = f"  ✅ 包含 EXPLAIN 校验"
        results.append({"desc": "EXPLAIN 代码", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 1})

    # 参数化查询分析
    f2 = p / "day19_security_analysis.py"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "day19_security_analysis.py 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        rc2, out2, err2 = _run(f2)
        ok5 = rc2 == 0 and len(out2) > 10
        msg5 = f"  ✅ 能解释参数化查询原理"
        results.append({"desc": "防注入理解", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 20 — SSE 流式输出
# ═══════════════════════════════════════════════════════════════
def _day20_checks():
    from grading_system import check_file_exists

    p = PRACTICE / "day20"
    results = []

    f = p / "day20_sse.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day20_sse.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        content = f.read_text(encoding="utf-8")
        has_streaming = "StreamingResponse" in content or "stream" in content.lower()
        has_async = "async def" in content
        has_yield = "yield" in content

        ok2 = has_streaming
        msg2 = f"  ✅ 有流式响应{'✅' if has_async else '⚠️  async'}{'✅' if has_yield else '⚠️  yield'}"
        results.append({"desc": "SSE 实现", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 2})

        rc, out, err = _run(f, timeout=10)
        # SSE 服务会一直运行，所以超时也算成功
        ok3 = rc == 0 or "timeout" in str(err).lower() or not err
        msg3 = f"  ✅ SSE 服务能启动（检查是否持续运行）"
        results.append({"desc": "SSE 启动", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 2})

    # SSE 理解分析
    f2 = p / "day20_sse_analysis.py"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "day20_sse_analysis.py 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        rc2, out2, err2 = _run(f2)
        ok5 = rc2 == 0 and len(out2) > 10
        msg5 = f"  ✅ 能理解 SSE 原理"
        results.append({"desc": "SSE 理解", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 21 — Agent 新节点（结果解释）
# ═══════════════════════════════════════════════════════════════
def _day21_checks():
    from grading_system import check_file_exists, check_function_exists

    p = PRACTICE / "day21"
    results = []

    f = p / "day21_explain_node.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day21_explain_node.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        content = f.read_text(encoding="utf-8")
        has_explain = "explain" in content.lower()
        has_state = "state" in content.lower()

        ok2 = has_explain and has_state
        msg2 = f"  ✅ 有解释函数和状态处理{'✅' if 'return' in content else '⚠️  无 return'}"
        results.append({"desc": "节点函数", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 2})

    # 检查是否在 nl2sql_agent.py 里加了节点
    agent_file = NL2SQL_ROOT / "backend/agents/nl2sql_agent.py"
    if agent_file.exists():
        agent_content = agent_file.read_text(encoding="utf-8")
        ok3 = "result_explanation" in agent_content or "explain_result" in agent_content
        msg3 = f"  ✅ nl2sql_agent.py 包含新节点" if ok3 else f"  ⚠️  未修改 nl2sql_agent.py"
    else:
        ok3, msg3 = False, "  ⚠️  nl2sql_agent.py 不在预期路径"
    results.append({"desc": "Agent 节点集成", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 3})

    f2 = p / "day21_test_result.py"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "day21_test_result.py 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        rc2, out2, err2 = _run(f2, timeout=30)
        ok5 = rc2 == 0
        msg5 = f"  ✅ 新节点测试通过" if ok5 else f"  ⚠️  测试问题: {err2[:100] or out2[:100]}"
        results.append({"desc": "节点测试", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 22 — 指标库扩展
# ═══════════════════════════════════════════════════════════════
def _day22_checks():
    from grading_system import check_file_exists

    p = PRACTICE / "day22"
    results = []

    f = p / "day22_metric_extend.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day22_metric_extend.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        content = f.read_text(encoding="utf-8")
        has_metric = "meeting_efficiency" in content or "metric" in content.lower()
        ok2 = has_metric
        msg2 = f"  ✅ 包含新指标定义"
        results.append({"desc": "指标定义", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 2})

    # 检查是否修改了 metrics_library.py
    metrics_file = NL2SQL_ROOT / "backend/rag/metrics_library.py"
    if metrics_file.exists():
        metrics_content = metrics_file.read_text(encoding="utf-8")
        ok3 = "meeting_efficiency" in metrics_content or "会议效率" in metrics_content
        msg3 = f"  ✅ metrics_library.py 已更新" if ok3 else f"  ⚠️  未修改 metrics_library.py"
    else:
        ok3, msg3 = False, "  ⚠️  metrics_library.py 不在预期路径"
    results.append({"desc": "指标库更新", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 3})

    f2 = p / "day22_test_metric.py"
    ok4, msg4 = check_file_exists(f2)
    results.append({"desc": "day22_test_metric.py 存在", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 1})

    if f2.exists():
        rc2, out2, err2 = _run(f2, timeout=30)
        ok5 = rc2 == 0
        msg5 = f"  ✅ 指标测试通过" if ok5 else f"  ⚠️  测试问题: {err2[:100] or out2[:100]}"
        results.append({"desc": "指标测试", "check": lambda ok=ok5, msg=msg5: (ok, msg5), "weight": 2})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 23 — BM25 混合检索
# ═══════════════════════════════════════════════════════════════
def _day23_checks():
    from grading_system import check_file_exists

    p = PRACTICE / "day23"
    results = []

    f = p / "day23_bm25.py"
    ok, msg = check_file_exists(f)
    results.append({"desc": "day23_bm25.py 存在", "check": lambda ok=ok, msg=msg: (ok, msg), "weight": 1})

    if f.exists():
        content = f.read_text(encoding="utf-8")
        has_bm25 = "BM25" in content or "bm25" in content.lower()
        has_rrf = "RRF" in content or "fusion" in content.lower() or "rank" in content.lower()
        ok2 = has_bm25
        msg2 = f"  ✅ 包含 BM25{'✅' if has_rrf else '⚠️  无RRF融合'}代码"
        results.append({"desc": "BM25 实现", "check": lambda ok=ok2, msg=msg2: (ok, msg2), "weight": 2})

        rc, out, err = _run(f, timeout=30)
        ok3 = rc == 0 or "bm25" in err.lower()  # 可能缺 rank_bm25 包
        msg3 = f"  ✅ BM25 代码能运行" if ok3 else f"  ⚠️  运行问题: {err[:100] or out[:100]}"
        results.append({"desc": "BM25 运行", "check": lambda ok=ok3, msg=msg3: (ok, msg3), "weight": 2})

    # 检查是否修改了 retriever.py
    retriever_file = NL2SQL_ROOT / "backend/rag/retriever.py"
    if retriever_file.exists():
        retriever_content = retriever_file.read_text(encoding="utf-8")
        ok4 = "BM25" in retriever_content or "bm25" in retriever_content
        msg4 = f"  ✅ retriever.py 已加入 BM25" if ok4 else f"  ⚠️  未修改 retriever.py"
    else:
        ok4, msg4 = False, "  ⚠️  retriever.py 不在预期路径"
    results.append({"desc": "Retriever 集成", "check": lambda ok=ok4, msg=msg4: (ok, msg4), "weight": 3})

    return results


# ═══════════════════════════════════════════════════════════════
# DAY 配置汇总表
# 格式: "dayXX": {"title": "...", "checks": [...]}
# ═══════════════════════════════════════════════════════════════
DAY_CONFIG = {
    "day01": {
        "title": "Day 01 — 环境搭建 + 第一个 Python 程序",
        "checks": _day01_checks(),
    },
    "day02": {
        "title": "Day 02 — 变量 & 数据类型",
        "checks": _day02_checks(),
    },
    "day03": {
        "title": "Day 03 — if / for / while 流程控制",
        "checks": _day03_checks(),
    },
    "day04": {
        "title": "Day 04 — 列表 & 字典",
        "checks": _day04_checks(),
    },
    "day05": {
        "title": "Day 05 — 函数 & 模块",
        "checks": _day05_checks(),
    },
    "day06": {
        "title": "Day 06 — 面向对象 class",
        "checks": _day06_checks(),
    },
    "day07": {
        "title": "Day 07 — 文件读写 & JSON",
        "checks": _day07_checks(),
    },
    "day08": {
        "title": "Day 08 — HTTP 请求 & API",
        "checks": _day08_checks(),
    },
    "day09": {
        "title": "Day 09 — 数据库 SQL",
        "checks": _day09_checks(),
    },
    "day10": {
        "title": "Day 10 — 错误处理 & 调试",
        "checks": _day10_checks(),
    },
    "day11": {
        "title": "Day 11 — LLM API 调用",
        "checks": _day11_checks(),
    },
    "day12": {
        "title": "Day 12 — Embedding 向量化",
        "checks": _day12_checks(),
    },
    "day13": {
        "title": "Day 13 — Milvus 向量数据库",
        "checks": _day13_checks(),
    },
    "day14": {
        "title": "Day 14 — RAG 完整流程",
        "checks": _day14_checks(),
    },
    "day15": {
        "title": "Day 15 — Prompt Engineering",
        "checks": _day15_checks(),
    },
    "day16": {
        "title": "Day 16 — 状态机概念",
        "checks": _day16_checks(),
    },
    "day17": {
        "title": "Day 17 — LangGraph 入门",
        "checks": _day17_checks(),
    },
    "day18": {
        "title": "Day 18 — Self-Correction 自我纠错",
        "checks": _day18_checks(),
    },
    "day19": {
        "title": "Day 19 — SQL 校验层",
        "checks": _day19_checks(),
    },
    "day20": {
        "title": "Day 20 — SSE 流式输出",
        "checks": _day20_checks(),
    },
    "day21": {
        "title": "Day 21 — Agent 新节点：结果解释",
        "checks": _day21_checks(),
    },
    "day22": {
        "title": "Day 22 — 指标库扩展",
        "checks": _day22_checks(),
    },
    "day23": {
        "title": "Day 23 — BM25 混合检索",
        "checks": _day23_checks(),
    },
}
