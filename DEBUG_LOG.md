# NL2SQL BI Agent — Debug Log & Lessons Learned

> 本文档记录项目开发调试过程中遇到的所有问题、根因和解决方案。
> 后续出现问题也在此追加，格式：【日期】问题描述 → 根因 → 修复 → 验证

---

## 目录
1. [SQL 列名臆造问题](#1-sql-列名臆造问题)
2. [「SQL 有效」假阳性 — 校验层未连接真实数据库](#2-sql-有效假阳性--校验层未连接真实数据库)
3. [org_id 不一致：Mock 数据与 API 硬编码不一致](#3-org_id-不一致mock-数据与-api-硬编码不一致)
4. [数据稀疏：测试数据量不足](#4-数据稀疏测试数据量不足)
5. [开发环境沙盒限制](#5-开发环境沙盒限制)

---

## 1. SQL 列名臆造问题

**发生日期：** 2026-04-06

**问题描述：**
- 用户问「各部门用户平均使用时长」，Agent 生成的 SQL 在 DataGrip 直接执行报错：
  ```
  ERROR: column "usage_duration_seconds" does not exist
  ```
- 同一 SQL 中还使用了不存在的列 `usage_date`（正确应为 `record_date`）

**根因分析：**
LLM 在生成 SQL 时，没有严格对照 Schema 文档中的列名，臆造了 `usage_duration_seconds` 和 `usage_date` 这两个不存在的列名。Schema 文件 `saas_bi_schema.py` 中 `fact_workspace` 的实际列名为：
- `total_active_time_seconds`（用户活跃时长）
- `record_date`（记录日期）

**修复内容：**

1. **`backend/agents/nl2sql_agent.py` — SYSTEM_PROMPT 强化**
   ```python
   11. 【严禁臆造列名】只能使用上下文 Schema 与示例中出现的字段。fact_workspace 表：
       - 日期字段为 record_date（DATE），禁止使用 usage_date、activity_date 等不存在列名
       - 用户活跃/使用时长（秒）为 total_active_time_seconds，禁止使用 usage_duration_seconds、active_duration 等不存在列名
       - 还可使用 total_session_time_seconds、total_idle_time_seconds、login_count 等已定义字段
   ```

2. **`backend/tools/sql_executor.py` — 增加 `validate_with_explain()`**
   在 PostgreSQL 侧执行 `EXPLAIN (COSTS OFF) <SQL>` 做真实数据库校验，与 DataGrip 执行报错一致。详见问题 #2。

**验证方法：**
- 重启服务后重新提问，观察生成的 SQL 列名
- 若仍有错误，EXPLAIN 会捕获并触发重试（最多 3 次）

---

## 2. 「SQL 有效」假阳性 — 校验层未连接真实数据库

**发生日期：** 2026-04-06

**问题描述：**
- UI 前端显示「SQL 有效 ✅」，但将 SQL 拉到 DataGrip 执行报错
- 用户多次反馈此问题，Agent 反复给出相同错误 SQL

**根因分析：**
`sql_validation_node()` 只做字符串规则检查（SELECT 开头、有无 org_id/ FROM），**从未连接真实数据库验证**。LLM 生成的 SQL 只要满足这些字符串规则就标记为 valid。

```python
# 原校验逻辑 — 只检查字符串
if not sql_lower.startswith("select"):
    errors.append("SQL 必须以 SELECT 开头")
if "org_id" not in sql_lower:
    errors.append("缺少 org_id 过滤条件")
# 没有连接数据库验证列名是否真实存在
```

**修复内容：**

1. **`sql_executor.py` 新增方法：**
   ```python
   def validate_with_explain(self, sql: str) -> Tuple[bool, Optional[str]]:
       """用 EXPLAIN 在数据库侧校验 SQL（解析 + 列/表是否存在）"""
       explain_sql = f"EXPLAIN (COSTS OFF) {stmt}"
       try:
           with self._engine.connect() as conn:
               conn.execute(text(explain_sql))
           return True, None
       except Exception as e:
           return False, str(e)
   ```

2. **`nl2sql_agent.py` — 校验节点增加 EXPLAIN 环节：**
   - 通过字符串规则后才调用 `validate_with_explain()`
   - EXPLAIN 失败 → `sql_valid=False`，进入重试流程

3. **`nl2sql_agent.py` — 执行失败也触发重试：**
   ```python
   def _route_after_execution(state: NL2SQLState) -> str:
       if state.get("sql_executed", False):
           return "chart"
       retry_count = state.get("retry_count", 0)
       if retry_count < settings.max_sql_retries:
           state["retry_count"] = retry_count + 1
           state["sql_error"] = state.get("execution_error") or "SQL 执行失败"
           return "generate"  # 与校验失败走同一重试路径
       state["sql_valid"] = False
       state["error_message"] = state.get("execution_error") or "SQL 执行失败（已达最大重试次数）"
       return "end"
   ```

4. **`nl2sql_agent.py` — 强化 State 类型定义：**
   显式声明 `retry_count: int` 字段，避免状态累积问题

**验证方法：**
- 任何生成错误的 SQL 不再显示「SQL 有效」
- 校验/执行失败后会自动重试，最多 3 次
- 仍失败时设置 `sql_valid=False` + `error_message`，不再假阳性

---

## 3. org_id 不一致：Mock 数据与 API 硬编码不一致

**发生日期：** 2026-04-06

**问题描述：**
- Mock 数据生成的 `fact_workspace` 等表，`org_id` 字段值为 `demo_org_001`
- API 层 `routes.py` 硬编码 `org_id = "demo_org"`
- 导致 SQL 查询永远查不到数据（WHERE org_id = 'demo_org' 但表里只有 `demo_org_001`）

**根因分析：**
- `generate_mock_data.py` 中硬编码 `org_id = "demo_org_001"`
- `routes.py` 两个端点（同步/流式）中硬编码 `"demo_org"`

**修复内容：**
统一改为 `demo_org_001`，修改 `routes.py` 两处：
```python
# 修改前
conversation_id = ...create_conversation("demo_org")
"org_id": "demo_org",

# 修改后
conversation_id = ...create_conversation("demo_org_001")
"org_id": "demo_org_001",
```

**教训：**
所有涉及 org_id 的地方必须使用统一常量，建议后续将 org_id 提取到 `config.py` 作为 `DEFAULT_ORG_ID` 统一管理。

---

## 4. 数据稀疏：测试数据量不足

**发生日期：** 2026-04-06

**问题描述：**
- SQL 正确但查询返回 0 行
- 用户体验差，无法验证 Agent 回答质量

**根因分析：**
原 `generate_mock_data.py` 数据量过小：
- `fact_workspace` 仅 500 条记录
- 时间跨度短（仅覆盖近 30 天）
- 仅单租户 `demo_org_001` 有数据
- 随机日期随机用户，数据分布稀疏

**修复内容：**

重写 `generate_mock_data.py`，关键改进：

1. **多租户：** 5 个租户，org_id 分别为 `demo_org_001`、`org_002`、`org_003`、`org_004`、`org_005`

2. **用户数按租户规模分配：** 28~312 人

3. **时间跨度：** 近 1 年，近期数据更密集
   ```python
   # 近期 30 天权重高，历史稀疏
   days_ago = random.choices(
       list(range(0, 31)) + list(range(31, days_back)),
       weights=[5]*31 + [1]*(days_back-31), k=1
   )[0]
   ```

4. **各表数据量：**
   | 表 | 原数量 | 新数量 |
   |---|--------|--------|
   | fact_workspace | 500 | 51,390（每用户近 90 天全覆盖）|
   | fact_meeting | 500 | 4,568 |
   | fact_meeting_participant | — | 25,045 |
   | fact_calling | 800 | 5,730 |
   | fact_messaging | 2000 | 17,130 |
   | fact_device_usage | — | 8,565 |
   | fact_quality | 100 | 1,713 |

5. **TRUNCATE 后重新生成：** 确保每次运行数据干净

---

## 5. 开发环境沙盒限制

**发生日期：** 2026-04-06

**问题描述：**
- Shell 工具默认运行在沙盒中，`lsof -ti:8000` 等命令无法使用
- `base64` 报错：`/dev/stdout: Operation not permitted`
- 启动后台服务时端口被占用，但无法用 `lsof` 找到进程

**根因分析：**
沙盒限制了对 `/dev/stdout` 的访问，以及某些系统调用。

**临时解决方案：**
```bash
# 需要 full_network + all 权限
lsof -ti:8000 | xargs kill -9 2>/dev/null
# 启动服务时明确申请权限
required_permissions: ["all"]
```

**长期建议：**
- 启动服务后记录 PID 到文件，方便后续管理
- 考虑用 `ps aux | grep backend.main` 替代 `lsof`

---

## 后续追加格式

当新问题发生时，按以下格式追加到此文档：

```markdown
---

## N. [简短问题标题]

**发生日期：** YYYY-MM-DD

**问题描述：**
> 具体的错误信息或表现

**根因分析：**
- 原因1
- 原因2

**修复内容：**
- 文件: 修改内容
- 文件: 修改内容

**验证方法：**
如何确认问题已解决

**教训：**
后续避免同类问题的方法
```
