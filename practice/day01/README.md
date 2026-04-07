# Day 01 — 环境搭建 + 第一个 Python 程序

## 今日目标

1. 安装并配置 PyCharm + Python
2. 写出并运行第一个 Python 程序
3. 启动 NL2SQL 后端服务

## 练习 1-1：自我介绍程序（必做）

新建文件 `day1_hello.py`，要求：
- 定义两个变量：`name`（你的名字）和 `age`（你的年龄）
- 用 f-string 打印一句话：`我叫 XX，今年 YY 岁`
- 试着加一个变量 `goal`（你的学习目标），也打印出来

**运行：** 在 PyCharm 里点绿色三角 ▶ 运行，确认屏幕有输出

---

## 练习 1-2：启动 NL2SQL 后端（必做）

在 PyCharm Terminal 里运行：

```bash
pip install -r ../requirements.txt
python ../backend/main.py
```

看到 `Uvicorn running on http://0.0.0.0:8001` 就成功了。

然后在浏览器打开 http://localhost:8001/docs ，能看到 API 文档页面。

把截图保存到 `day01/screenshot.png` 或 `day01/screenshot.jpg`。

---

## 练习 1-3（可选加分）：第一次问 NL2SQL

在 PyCharm 新建文件 `day1_nl2sql_test.py`，用 requests 库发请求：

```python
import requests

resp = requests.post("http://localhost:8001/api/v1/query", json={
    "question": "各部门用户平均使用时长",
    "conversation_id": None
})
print(resp.json())
```

运行后把输出复制到 `day01/nl2sql_output.txt` 里。

---

## 验收标准

运行 `python run_grade.py day01`，看得分：
- day1_hello.py 存在 + 能运行 + 有自定义内容 → 4分
- NL2SQL 后端能启动 → 2分
- screenshot 存在 → 1分
