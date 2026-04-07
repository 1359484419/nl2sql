"""
NL2SQL Agent 核心 — 基于 LangGraph 的状态机编排

整个 NL2SQL 流程：
1. intent_classification  → 意图分类（指标查询/趋势分析/部门对比/TOP N/同比环比）
2. context_retrieval     → RAG 检索（Schema + 指标 + SQL 示例）
3. sql_generation        → LLM 生成 SQL
4. sql_validation        → SQL 语法和逻辑校验
5. sql_execution         → 实际执行 SQL
6. chart_selection       → 图表类型推荐
7. response_building     → 构建最终响应
"""

import re
import time
from typing import Any, Dict, List, Literal, Optional, TypedDict, Annotated
from operator import add

from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END

from backend.config import settings
from backend.rag import UnifiedRetriever
from backend.rag.metrics_library import BUSINESS_METRICS
from backend.rag.sql_examples import SQL_EXAMPLES


# ═══════════════════════════════════════════════════════════════════════════════
# LLM 初始化
# ═══════════════════════════════════════════════════════════════════════════════

def _get_llm():
    """获取 LLM 实例"""
    if settings.use_ollama:
        from langchain_ollama import ChatOllama
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=0.1,
        )
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            model=settings.openai_model,
            temperature=0.1,
        )


llm = _get_llm()


# ═══════════════════════════════════════════════════════════════════════════════
# Agent State 定义
# ═══════════════════════════════════════════════════════════════════════════════

class NL2SQLState(TypedDict, total=False):
    # 输入
    question: str
    org_id: str
    conversation_id: Optional[str]

    # 中间状态
    intent: Optional[str]
    time_range: Optional[Dict[str, str]]  # {start_date, end_date}
    dimensions: Optional[List[str]]        # 维度列（用于 GROUP BY）
    metrics: Optional[List[str]]           # 指标列（用于 SELECT）
    group_by_fields: Optional[List[str]]   # 分组字段

    # RAG 上下文
    schema_context: Optional[str]
    metrics_context: Optional[str]
    examples_context: Optional[str]

    # SQL 相关
    generated_sql: Optional[str]
    retry_count: int  # 校验/执行失败后的重试次数
    sql_valid: bool
    sql_error: Optional[str]
    sql_executed: bool
    execution_error: Optional[str]

    # 执行结果
    query_result: Optional[Dict[str, Any]]   # {columns, rows, row_count, execution_time_ms}
    chart_config: Optional[Dict[str, Any]]     # 图表推荐配置

    # 输出
    steps: Annotated[List[Dict[str, Any]], add]  # 执行步骤链
    final_response: Optional[Dict[str, Any]]
    error_message: Optional[str]


# ═══════════════════════════════════════════════════════════════════════════════
# 提示词模板
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """你是一个专业的 NL2SQL 助手，专注于帮助企业协作 SaaS 平台的数据分析。

你的任务是根据用户的自然语言问题，生成准确的 PostgreSQL SQL 查询语句。

【数据库 Schema】
{schema_context}

【业务指标定义】
{metrics_context}

【SQL 参考示例】
{examples_context}

【重要规则】
1. 所有查询必须包含 WHERE org_id = '{org_id}' 条件（多租户隔离）
2. 日期时间字段支持 DATE_TRUNC、EXTRACT、DATE 等函数
3. 使用 PostgreSQL 语法（DATE_TRUNC('month', ...)、EXTRACT(HOUR FROM ...)、INTERVAL 等）
4. 不要使用 SELECT *，只选择需要的字段
5. 所有表名和字段名使用小写加下划线
6. 如果问题涉及时间（如"最近一周"、"本月"），需要推断时间范围
7. GROUP BY 的字段必须是 SELECT 列表中出现的字段
8. 对于百分比计算，使用 ROUND(..., 2) 保留 2 位小数
9. 对于时长（秒转分钟），使用 /60.0；秒转小时，使用 /3600.0
10. 如果用户没有指定排序，默认按有意义的字段排序
11. 【严禁臆造列名】只能使用上下文 Schema 与示例中出现的字段。fact_workspace 表：
    - 日期字段为 record_date（DATE），禁止使用 usage_date、activity_date 等不存在列名
    - 用户活跃/使用时长（秒）为 total_active_time_seconds，禁止使用 usage_duration_seconds、active_duration 等不存在列名
    - 还可使用 total_session_time_seconds、total_idle_time_seconds、login_count 等已定义字段
"""


def _build_system_prompt(org_id: str, schema_ctx: str, metrics_ctx: str, examples_ctx: str) -> str:
    return SYSTEM_PROMPT.format(
        org_id=org_id,
        schema_context=schema_ctx,
        metrics_context=metrics_ctx,
        examples_context=examples_ctx,
    )


SQL_GENERATION_PROMPT = """根据用户问题，生成 SQL 查询。

【用户问题】
{question}

【推断的时间范围】
{time_range}

请按以下 JSON 格式输出（只输出 JSON，不要其他内容）：
{{
    "sql": "完整的 SQL 语句",
    "intent": "指标查询/趋势分析/部门对比/TOP N/同比环比/分布分析/明细查询",
    "dimensions": ["维度字段列表，如部门、日期"],
    "metrics": ["指标字段列表，如会议数量、通话时长"],
    "group_by": ["GROUP BY 字段列表"],
    "reasoning": "简要说明为什么这样生成 SQL"
}}
"""


SQL_VALIDATION_PROMPT = """请验证以下 SQL 语句的正确性：

【SQL】
{sql}

【Schema】
{schema_context}

检查以下内容：
1. SQL 语法是否正确（PostgreSQL）
2. SELECT 的字段是否在 FROM 的表中存在
3. WHERE 条件是否完整（必须包含 org_id 过滤）
4. GROUP BY 字段是否正确
5. 字段类型是否匹配（如日期字段不能用 SUM 聚合）

请按以下 JSON 格式输出：
{{
    "is_valid": true/false,
    "errors": ["错误列表，如果有的话"],
    "suggestions": ["修改建议，如果有的话"]
}}
"""


CHART_SELECTION_PROMPT = """根据 SQL 查询结果，推荐合适的图表类型。

【用户问题】
{question}

【查询意图】
{intent}

【SQL 查询结果】
- 列数：{column_count}
- 行数：{row_count}
- 列名及示例值：
{columns_info}

【数据特征】
- 是否为时间序列：{is_time_series}
- 是否有多个数值列：{has_multiple_values}
- 维度基数（不同值数量）：{dimension_cardinality}
- 数值范围：{value_range}

请按以下 JSON 格式输出：
{{
    "chart_type": "line/bar/pie/scatter/area/radar/gauge/table",
    "title": "图表标题",
    "x_axis_label": "X轴标签",
    "y_axis_label": "Y轴标签",
    "series_names": ["系列名称列表"],
    "recommended_reason": "推荐该图表类型的原因"
}}
"""


# ═══════════════════════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════════════════════

def _format_schema_context(schema_chunks: List[Dict]) -> str:
    """将 Schema 检索结果格式化为上下文文本"""
    if not schema_chunks:
        return "（未检索到相关 Schema）"
    lines = []
    for chunk in schema_chunks[:8]:
        chunk_type = chunk.get("chunk_type", "")
        table_name = chunk.get("table_name", "")
        text = chunk.get("text", "")
        score = chunk.get("score", 0)
        lines.append(f"[{chunk_type}] {table_name} (相关性: {score:.2f})\n{text}")
    return "\n---\n".join(lines)


def _format_metrics_context(metrics: List[Dict]) -> str:
    """将指标检索结果格式化为上下文文本"""
    if not metrics:
        return "（未匹配到业务指标）"
    lines = []
    for m in metrics[:5]:
        meta = m.get("metadata", {})
        lines.append(
            f"指标: {meta.get('metric_name', '')} | "
            f"别名: {', '.join(meta.get('aliases', [])[:5])} | "
            f"定义: {meta.get('definition_desc', '')}"
        )
    return "\n".join(lines)


def _format_examples_context(examples: List[Dict]) -> str:
    """将 SQL 示例检索结果格式化为上下文文本"""
    if not examples:
        return "（无参考示例）"
    lines = []
    for ex in examples[:5]:
        meta = ex.get("metadata", {})
        lines.append(
            f"问题: {meta.get('question_pattern', '')}\n"
            f"SQL: {meta.get('sql', '').strip()}\n"
            f"说明: {meta.get('description', '')}\n"
        )
    return "\n---\n".join(lines)


def _infer_time_range(question: str) -> Dict[str, str]:
    """从用户问题中推断时间范围（PostgreSQL 格式）"""
    q = question.lower()
    if "本月" in q or "这个月" in q:
        return {
            "start_date": "DATE_TRUNC('month', CURRENT_DATE)",
            "end_date": "CURRENT_DATE + INTERVAL '1 day'",
            "label": "本月"
        }
    elif "上月" in q or "上个月" in q:
        return {
            "start_date": "DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')",
            "end_date": "DATE_TRUNC('month', CURRENT_DATE)",
            "label": "上月"
        }
    elif "本周" in q or "这周" in q:
        return {
            "start_date": "DATE_TRUNC('week', CURRENT_DATE)",
            "end_date": "CURRENT_DATE + INTERVAL '1 day'",
            "label": "本周"
        }
    elif "最近一周" in q or "过去一周" in q:
        return {
            "start_date": "CURRENT_DATE - INTERVAL '7 days'",
            "end_date": "CURRENT_DATE + INTERVAL '1 day'",
            "label": "最近一周"
        }
    elif "最近一个月" in q or "过去一个月" in q:
        return {
            "start_date": "CURRENT_DATE - INTERVAL '1 month'",
            "end_date": "CURRENT_DATE + INTERVAL '1 day'",
            "label": "最近一个月"
        }
    elif "最近三个月" in q or "过去三个月" in q:
        return {
            "start_date": "CURRENT_DATE - INTERVAL '3 months'",
            "end_date": "CURRENT_DATE + INTERVAL '1 day'",
            "label": "最近三个月"
        }
    elif "今天" in q:
        return {
            "start_date": "CURRENT_DATE",
            "end_date": "CURRENT_DATE + INTERVAL '1 day'",
            "label": "今天"
        }
    elif "昨天" in q:
        return {
            "start_date": "CURRENT_DATE - INTERVAL '1 day'",
            "end_date": "CURRENT_DATE",
            "label": "昨天"
        }
    else:
        # 默认最近 30 天
        return {
            "start_date": "CURRENT_DATE - INTERVAL '30 days'",
            "end_date": "CURRENT_DATE + INTERVAL '1 day'",
            "label": "最近30天（默认）"
        }


# ═══════════════════════════════════════════════════════════════════════════════
# LangGraph 节点函数
# ═══════════════════════════════════════════════════════════════════════════════

def intent_classification_node(state: NL2SQLState) -> NL2SQLState:
    """节点 1：意图分类"""
    question = state["question"]
    time_range = _infer_time_range(question)
    state["time_range"] = time_range

    state["steps"].append({
        "step_type": "intent",
        "content": f"意图识别完成，时间范围：{time_range.get('label', '默认30天')}",
        "is_success": True,
    })
    return state


def context_retrieval_node(state: NL2SQLState) -> NL2SQLState:
    """节点 2：RAG 上下文检索"""
    question = state["question"]
    retriever = UnifiedRetriever()
    retrieval_result = retriever.retrieve(question)

    schema_ctx = _format_schema_context(retrieval_result["schema_chunks"])
    metrics_ctx = _format_metrics_context(retrieval_result["metrics"])
    examples_ctx = _format_examples_context(retrieval_result["sql_examples"])

    state["schema_context"] = schema_ctx
    state["metrics_context"] = metrics_ctx
    state["examples_context"] = examples_ctx

    state["steps"].append({
        "step_type": "schema_select",
        "content": f"检索到 {len(retrieval_result['schema_chunks'])} 个 Schema 片段，"
                   f"{len(retrieval_result['metrics'])} 个指标，"
                   f"{len(retrieval_result['sql_examples'])} 个 SQL 示例",
        "is_success": True,
    })
    return state


def sql_generation_node(state: NL2SQLState) -> NL2SQLState:
    """节点 3：SQL 生成"""
    question = state["question"]
    org_id = state.get("org_id", "demo_tenant")
    time_range = state.get("time_range", _infer_time_range(question))
    schema_ctx = state.get("schema_context", "")
    metrics_ctx = state.get("metrics_context", "")
    examples_ctx = state.get("examples_context", "")

    system_prompt = _build_system_prompt(org_id, schema_ctx, metrics_ctx, examples_ctx)

    # 重试时附加上一次的校验 / 执行错误（与 DataGrip 报错一致）
    retry_count = state.get("retry_count", 0)
    prev_err = state.get("sql_error") or state.get("execution_error")
    error_feedback = ""
    if retry_count > 0 and prev_err:
        error_feedback = (
            f"\n\n【上一次的 SQL 错误或执行失败，请修复后重新生成】\n"
            f"错误信息：{prev_err}\n"
            f"有问题的 SQL：{state.get('generated_sql', '')}\n"
            f"请根据错误信息修正 SQL，确保字段名和表名与上面提供的 Schema 完全一致，禁止臆造列名。"
        )
        state["sql_error"] = None
        state["execution_error"] = None

    user_prompt = SQL_GENERATION_PROMPT.format(
        question=question,
        time_range=f"start: {time_range.get('start_date')}  end: {time_range.get('end_date')} ({time_range.get('label', '')})",
    ) + error_feedback

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])
        content = response.content.strip()

        # 解析 JSON 响应
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            import json
            parsed = json.loads(json_match.group())
            sql = parsed.get("sql", "").strip()
            # 清理 SQL 中的 org_id 占位符
            sql = sql.replace("'{org_id}'", f"'{org_id}'")
            sql = sql.replace("'{start_date}'", time_range.get("start_date", "CURRENT_DATE - INTERVAL '30 days'"))
            sql = sql.replace("'{end_date}'", time_range.get("end_date", "CURRENT_DATE + INTERVAL '1 day'"))
            state["generated_sql"] = sql
            state["intent"] = parsed.get("intent", "指标查询")
            state["dimensions"] = parsed.get("dimensions", [])
            state["metrics"] = parsed.get("metrics", [])
            state["group_by_fields"] = parsed.get("group_by", [])

            state["steps"].append({
                "step_type": "sql_generate",
                "content": f"SQL 生成完成（意图：{state['intent']}）\n{sql[:200]}...",
                "sql": sql,
                "is_success": True,
            })
        else:
            state["generated_sql"] = content
            state["steps"].append({
                "step_type": "sql_generate",
                "content": "SQL 生成完成（解析失败，使用原始响应）",
                "sql": content,
                "is_success": True,
            })
    except Exception as e:
        state["generated_sql"] = None
        state["sql_error"] = f"SQL 生成失败: {str(e)}"
        state["steps"].append({
            "step_type": "sql_generate",
            "content": f"SQL 生成失败: {str(e)}",
            "is_success": False,
            "error_message": str(e),
        })

    return state


def sql_validation_node(state: NL2SQLState) -> NL2SQLState:
    """节点 4：SQL 校验"""
    sql = state.get("generated_sql")
    if not sql:
        state["sql_valid"] = False
        state["sql_error"] = "没有生成的 SQL 可校验"
        return state

    schema_ctx = state.get("schema_context", "")

    # 基本语法检查（LLM 校验误判较多，暂禁用）
    sql_lower = sql.lower().strip()
    errors = []

    if not sql_lower.startswith("select"):
        errors.append("SQL 必须以 SELECT 开头")
    if "org_id" not in sql_lower:
        errors.append("缺少 org_id 过滤条件（多租户安全）")
    if "from" not in sql_lower:
        errors.append("缺少 FROM 子句")
    if sql.count(";") > 1:
        errors.append("不支持多条 SQL 语句")

    if errors:
        state["sql_valid"] = False
        state["sql_error"] = "; ".join(errors)
        state["steps"].append({
            "step_type": "sql_validate",
            "content": f"SQL 校验失败: {state['sql_error']}",
            "sql": sql,
            "is_success": False,
            "error_message": state["sql_error"],
        })
        return state

    # 在真实 PostgreSQL 上 EXPLAIN，捕获「列不存在」等与 DataGrip 一致的错误
    from backend.tools.sql_executor import sql_executor

    ok, explain_err = sql_executor.validate_with_explain(sql)
    if not ok:
        state["sql_valid"] = False
        state["sql_error"] = explain_err or "EXPLAIN 校验失败"
        state["steps"].append({
            "step_type": "sql_validate",
            "content": f"数据库 EXPLAIN 校验失败: {state['sql_error']}",
            "sql": sql,
            "is_success": False,
            "error_message": state["sql_error"],
        })
        return state

    state["sql_valid"] = True
    state["steps"].append({
        "step_type": "sql_validate",
        "content": "SQL 校验通过（含数据库 EXPLAIN）",
        "sql": sql,
        "is_success": True,
    })

    return state


def sql_execution_node(state: NL2SQLState) -> NL2SQLState:
    """节点 5：SQL 执行"""
    if not state.get("sql_valid", False):
        state["sql_executed"] = False
        state["execution_error"] = state.get("sql_error", "SQL 未通过校验")
        return state

    sql = state["generated_sql"]
    if not sql:
        state["sql_executed"] = False
        state["execution_error"] = "没有可执行的 SQL"
        return state

    try:
        from backend.tools.sql_executor import sql_executor
        result = sql_executor.execute(sql)
        state["query_result"] = result
        state["sql_executed"] = True

        state["steps"].append({
            "step_type": "sql_execute",
            "content": f"SQL 执行完成，返回 {result.get('row_count', 0)} 行，耗时 {result.get('execution_time_ms', 0)}ms",
            "is_success": True,
        })
    except Exception as e:
        state["sql_executed"] = False
        state["execution_error"] = str(e)
        state["steps"].append({
            "step_type": "sql_execute",
            "content": f"SQL 执行失败: {str(e)}",
            "is_success": False,
            "error_message": str(e),
        })

    return state


def chart_selection_node(state: NL2SQLState) -> NL2SQLState:
    """节点 6：图表推荐"""
    question = state["question"]
    intent = state.get("intent", "指标查询")
    query_result = state.get("query_result")

    if not query_result or not query_result.get("rows"):
        # 没有数据，使用默认表格
        state["chart_config"] = {
            "chart_type": "table",
            "title": "查询结果",
            "x_axis_label": "",
            "y_axis_label": "",
            "series_names": [],
            "recommended_reason": "数据量较大或为空，使用表格展示",
        }
        return state

    columns = query_result.get("columns", [])
    rows = query_result.get("rows", [])
    column_count = len(columns)
    row_count = len(rows)

    # 分析数据特征
    is_time_series = any(
        c.get("name", "").lower() in ["date", "day", "hour", "month", "week", "record_date"]
        for c in columns
    )
    numeric_cols = [c for c in columns if any(t in c.get("data_type", "").lower() for t in ["int", "decimal", "float", "numeric", "bigint"])]
    has_multiple_values = len(numeric_cols) > 1

    # 维度基数
    if rows:
        first_col = columns[0]["name"]
        dimension_cardinality = len(set(str(row.get(first_col, "")) for row in rows[:100]))
    else:
        dimension_cardinality = 0

    # 数值范围
    if numeric_cols:
        values = [float(row.get(numeric_cols[0]["name"], 0) or 0) for row in rows if row.get(numeric_cols[0]["name"]) is not None]
        value_range = (min(values) if values else 0, max(values) if values else 0)
    else:
        value_range = (0, 0)

    # 列信息
    columns_info = "\n".join(
        f"- {c['name']} ({c.get('data_type', 'unknown')}): "
        f"{[row.get(c['name']) for row in rows[:3]]}"
        for c in columns
    )

    try:
        prompt = CHART_SELECTION_PROMPT.format(
            question=question,
            intent=intent,
            column_count=column_count,
            row_count=row_count,
            columns_info=columns_info,
            is_time_series=is_time_series,
            has_multiple_values=has_multiple_values,
            dimension_cardinality=dimension_cardinality,
            value_range=value_range,
        )
        response = llm.invoke([
            SystemMessage(content="你是一个数据可视化专家，只返回 JSON 格式的图表推荐。"),
            HumanMessage(content=prompt),
        ])
        json_match = re.search(r'\{[\s\S]*\}', response.content)
        if json_match:
            import json
            chart_config = json.loads(json_match.group())
            state["chart_config"] = chart_config
        else:
            state["chart_config"] = _auto_chart_selection(
                columns, rows, is_time_series, has_multiple_values, dimension_cardinality
            )
    except Exception:
        state["chart_config"] = _auto_chart_selection(
            columns, rows, is_time_series, has_multiple_values, dimension_cardinality
        )

    state["steps"].append({
        "step_type": "chart_select",
        "content": f"推荐图表类型：{state['chart_config'].get('chart_type', 'table')}，"
                   f"原因：{state['chart_config'].get('recommended_reason', '')}",
        "is_success": True,
    })
    return state


def _auto_chart_selection(
    columns: List[Dict],
    rows: List[Dict],
    is_time_series: bool,
    has_multiple_values: bool,
    dimension_cardinality: int,
) -> Dict[str, Any]:
    """当 LLM 调用失败时，自动选择图表类型"""
    numeric_cols = [c for c in columns if any(t in c.get("data_type", "").lower() for t in ["int", "decimal", "float", "numeric", "bigint"])]
    first_col = columns[0]["name"] if columns else ""
    first_col_is_dim = not any(t in columns[0].get("data_type", "").lower() for t in ["int", "decimal", "float", "numeric"])

    # 决策树
    if dimension_cardinality > 20 or not numeric_cols:
        return {
            "chart_type": "table",
            "title": "查询结果",
            "x_axis_label": first_col,
            "y_axis_label": "",
            "series_names": [c["name"] for c in numeric_cols] if numeric_cols else [],
            "recommended_reason": f"维度基数较大（{dimension_cardinality}），使用表格展示更清晰",
        }
    elif is_time_series and len(numeric_cols) == 1:
        return {
            "chart_type": "line",
            "title": "趋势分析",
            "x_axis_label": "日期/时间",
            "y_axis_label": numeric_cols[0]["name"] if numeric_cols else "数值",
            "series_names": [numeric_cols[0]["name"]],
            "recommended_reason": "时间序列数据，使用折线图展示趋势变化",
        }
    elif is_time_series and has_multiple_values:
        return {
            "chart_type": "area",
            "title": "多指标趋势",
            "x_axis_label": "日期/时间",
            "y_axis_label": "数值",
            "series_names": [c["name"] for c in numeric_cols],
            "recommended_reason": "时间序列多指标数据，使用面积图展示多系列变化",
        }
    elif first_col_is_dim and len(numeric_cols) == 1 and dimension_cardinality <= 10:
        return {
            "chart_type": "bar",
            "title": "对比分析",
            "x_axis_label": first_col,
            "y_axis_label": numeric_cols[0]["name"],
            "series_names": [numeric_cols[0]["name"]],
            "recommended_reason": f"1个维度×1个指标（{dimension_cardinality}个类别），使用柱状图对比",
        }
    elif first_col_is_dim and dimension_cardinality <= 6 and len(numeric_cols) == 1:
        return {
            "chart_type": "pie",
            "title": "占比分布",
            "x_axis_label": first_col,
            "y_axis_label": numeric_cols[0]["name"],
            "series_names": [numeric_cols[0]["name"]],
            "recommended_reason": f"低基数维度（{dimension_cardinality}个类别），适合饼图展示占比",
        }
    else:
        return {
            "chart_type": "bar",
            "title": "数据分析",
            "x_axis_label": first_col,
            "y_axis_label": "数值",
            "series_names": [c["name"] for c in numeric_cols] if numeric_cols else [],
            "recommended_reason": "综合数据特征，使用柱状图展示",
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 构建 LangGraph
# ═══════════════════════════════════════════════════════════════════════════════

def _route_after_validation(state: NL2SQLState) -> str:
    """条件路由：校验通过则执行 SQL，失败则重试（最多3次）"""
    if state.get("sql_valid", False):
        return "execute"
    retry_count = state.get("retry_count", 0)
    if retry_count < settings.max_sql_retries:
        state["retry_count"] = retry_count + 1
        return "generate"  # 把错误信息带回去重新生成
    state["error_message"] = state.get("sql_error") or "SQL 校验失败（已达最大重试次数）"
    return "end"


def _route_after_execution(state: NL2SQLState) -> str:
    """条件路由：执行成功则选图表；失败则带错误重试生成（与校验失败一致）"""
    if state.get("sql_executed", False):
        return "chart"
    retry_count = state.get("retry_count", 0)
    if retry_count < settings.max_sql_retries:
        state["retry_count"] = retry_count + 1
        state["sql_error"] = state.get("execution_error") or "SQL 执行失败"
        return "generate"
    state["sql_valid"] = False
    state["error_message"] = state.get("execution_error") or "SQL 执行失败（已达最大重试次数）"
    return "end"


def build_nl2sql_graph() -> StateGraph:
    """构建 NL2SQL 状态图"""
    graph = StateGraph(NL2SQLState)

    # 添加节点
    graph.add_node("classify_intent", intent_classification_node)
    graph.add_node("retrieve", context_retrieval_node)
    graph.add_node("generate", sql_generation_node)
    graph.add_node("validate", sql_validation_node)
    graph.add_node("execute", sql_execution_node)
    graph.add_node("chart", chart_selection_node)

    # 设置边
    graph.set_entry_point("classify_intent")
    graph.add_edge("classify_intent", "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "validate")

    # 条件路由：校验通过则执行，失败则重试
    graph.add_conditional_edges(
        "validate",
        _route_after_validation,
        {
            "execute": "execute",
            "generate": "generate",
            "end": END,
        }
    )
    graph.add_conditional_edges(
        "execute",
        _route_after_execution,
        {
            "chart": "chart",
            "end": END,
        }
    )
    graph.add_edge("chart", END)

    return graph.compile()


# 全局单例
nl2sql_graph = build_nl2sql_graph()
