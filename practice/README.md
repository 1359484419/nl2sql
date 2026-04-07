# NL2SQL 练习系统

> Python 零基础 → AI 工程师 · 每天作业评判

## 快速开始

```bash
cd /Users/liuzhuoran/cursor/nl2sql-bi-agent/practice

# 评判今天的作业
python run_grade.py

# 评判指定 day
python run_grade.py day01

# 评判所有 day
python run_grade.py all

# 查看历史成绩
python run_grade.py --history

# 查看完成进度
python run_grade.py --progress

# 查看下一步该做哪一天
python run_grade.py --next
```

## 评分规则

| 评级 | 得分率 | 含义 |
|------|--------|------|
| ✅ PASS | 100% | 全部通过，继续前进 |
| 👍 GOOD | 80-99% | 做得不错，修复红色项即可满分 |
| 📝 PARTIAL | 50-79% | 有进步，继续加油 |
| 💪 TODO | < 50% | 刚开始或问题较多，先解决报错 |

## 目录结构

```
practice/
├── run_grade.py           # 评判入口（直接运行）
├── grading_system.py       # 评判核心引擎
├── config.py               # 每天评判规则（修改这里可定制评分）
├── score_history.json      # 成绩记录（自动生成）
├── README.md               # 本文件
└── day01/                  # Day 01 的作业文件夹
    ├── day1_hello.py       # 练习1：自我介绍程序
    ├── day1_hello_stub.py  # （可选）进阶练习
    ├── day1_backend_test.py # 练习2：后端启动测试
    └── README.md           # 当天说明
day02/
    ├── day2_types.py
    ├── README.md
    ...
day23/
    ├── day23_bm25.py
    └── README.md
```

## 每天要做的事

1. **读** `dayXX/README.md` — 了解当天目标和练习要求
2. **写** `dayXX/dayXX_*.py` — 完成练习代码
3. **测** `python run_grade.py dayXX` — 自动评判
4. **记** 有问题记在 `DEBUG_LOG.md`

## 评判标准

每项检查有 `weight`（权重），满分因天而异。

- **文件存在 + 语法正确**：1 分
- **代码能运行 + 输出正确**：2-3 分
- **理解题（回答问题）**：1-2 分
- **项目集成（改了 NL2SQL 源码）**：3 分

## 学习顺序（对应 LEARNING_ROADMAP.html）

| Day | 主题 |
|-----|------|
| day01-day05 | Python 基础语法 |
| day06-day10 | Python 进阶（OOP/JSON/API/SQL） |
| day11-day15 | AI 基础（LLM/Embedding/RAG/Prompt） |
| day16-day20 | LangGraph 状态机 / Agent |
| day21-day23 | NL2SQL 项目开发 |
