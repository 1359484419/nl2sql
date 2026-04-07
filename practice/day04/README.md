# Day 04 — 列表 & 字典

## 今日目标

掌握 Python 最强大的两种数据结构：**列表(list)** 和 **字典(dict)**。

## 练习 4-1：列表和字典操作（必做）

新建 `day4_containers.py`：

```python
# 列表操作
fruits = ["苹果", "香蕉", "橙子"]
fruits.append("葡萄")           # 追加
fruits.insert(1, "西瓜")        # 插入
print(fruits[0])                # 取第1个

# 字典操作
user = {"name": "张三", "age": 28}
user["job"] = "工程师"          # 新增
print(user["name"])             # 读取

# 任务：设计一个学生成绩管理系统
# students = [
#     {"name": "小明", "score": 92},
#     {"name": "小红", "score": 85},
# ]
# 找出最高分学生，打印：最高分：小明，92分
```

---

## 练习 4-2：读取 NL2SQL Schema（必做）

新建 `day4_schema_reader.py`，读取 `backend/schemas/saas_bi_schema.py`，打印：
- 所有表名
- `fact_workspace` 表的所有字段（字段名 + 类型 + 含义）

---

## 练习 4-3（进阶）：统计词频

新建 `day4_wordcount.py`，统计一段文字中出现最多的 3 个词。
