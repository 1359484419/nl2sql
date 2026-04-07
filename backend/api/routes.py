"""
API 路由 — NL2SQL BI Agent 对外接口
"""

import asyncio
import json
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from backend.schemas.query import QueryRequest, QueryResponse, QueryStreamEvent, QueryStep, ChartConfig, DataColumn, RetrievalContext
from backend.agents.nl2sql_agent import nl2sql_graph
from backend.services.conversation import ConversationService

router = APIRouter(prefix="/api/v1", tags=["NL2SQL BI"])


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "1.0.0"}


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    同步查询接口 — 适合简单请求
    返回完整的 NL2SQL 查询结果
    """
    conversation_id = request.conversation_id or ConversationService.create_conversation("demo_org_001")

    try:
        result = nl2sql_graph.invoke({
            "question": request.question,
            "org_id": "demo_org_001",
            "conversation_id": conversation_id,
            "steps": [],
        })
    except Exception as e:
        return QueryResponse(
            conversation_id=conversation_id,
            question=request.question,
            error_message=f"Agent 执行失败: {str(e)}",
        )

    response = _build_response(result, conversation_id, request.question)
    ConversationService.add_message(conversation_id, "user", request.question)
    ConversationService.add_message(conversation_id, "assistant", result.get("generated_sql", ""))
    return response


@router.post("/query/stream")
async def query_stream(request: QueryRequest):
    """
    流式查询接口 — 适合复杂请求，SSE 流式输出 Agent 思考过程
    """
    conversation_id = request.conversation_id or ConversationService.create_conversation("demo_org_001")

    async def event_generator():
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        # 前端步骤提示（可选择去掉，加快响应速度）
        yield _sse_event("step", {
            "step_type": "start",
            "content": f"开始处理问题: {request.question}",
        })
        yield _sse_event("step", {
            "step_type": "intent",
            "content": "🔍 正在识别用户意图和时间范围...",
        })
        yield _sse_event("step", {
            "step_type": "schema_select",
            "content": "📚 正在从向量数据库检索相关 Schema 和业务指标...",
        })
        yield _sse_event("step", {
            "step_type": "sql_generate",
            "content": "💡 正在根据上下文生成 SQL 语句...",
        })

        try:
            # 在线程池中同步运行 langgraph，避免阻塞事件循环
            with ThreadPoolExecutor(max_workers=1) as pool:
                result = await asyncio.get_running_loop().run_in_executor(
                    pool,
                    lambda: nl2sql_graph.invoke({
                        "question": request.question,
                        "org_id": "demo_org_001",
                        "conversation_id": conversation_id,
                        "steps": [],
                    })
                )
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield _sse_event("error", {"message": str(e)})
            yield _sse_event("done", {})
            return

        # 发送 SQL
        sql = result.get("generated_sql", "")
        if sql:
            yield _sse_event("sql", {"sql": sql, "valid": result.get("sql_valid", False)})

        # 发送数据
        qr = result.get("query_result")
        if qr:
            yield _sse_event("data", {
                "columns": qr.get("columns", []),
                "rows": qr.get("rows", []),
                "row_count": qr.get("row_count", 0),
                "execution_time_ms": qr.get("execution_time_ms", 0),
            })

        # 发送图表配置
        chart = result.get("chart_config", {})
        if chart:
            yield _sse_event("chart", chart)

        # 发送执行步骤
        steps = result.get("steps", [])
        for step in steps:
            yield _sse_event("step", step)

        yield _sse_event("done", _build_response(result, conversation_id, request.question).model_dump(mode="json"))

    return EventSourceResponse(event_generator())


@router.post("/index/build")
async def build_indexes(drop: bool = False):
    """
    构建所有向量索引
    """
    from backend.rag.retriever import UnifiedRetriever
    try:
        retriever = UnifiedRetriever()
        retriever.build_all_indexes(drop_existing=drop)
        return {"status": "ok", "message": "索引构建完成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema/stats")
async def schema_stats():
    """获取 Schema 索引统计"""
    from backend.rag.schema_indexer import SchemaIndexer
    try:
        indexer = SchemaIndexer()
        return indexer.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _sse_event(event: str, data: dict) -> dict:
    return {"event": event, "data": json.dumps(data, ensure_ascii=False, default=str)}


def _build_response(result: dict, conversation_id: str, question: str) -> QueryResponse:
    qr = result.get("query_result", {})
    chart = result.get("chart_config", {})
    steps_data = result.get("steps", [])

    steps = [
        QueryStep(
            step_type=s.get("step_type", ""),
            content=s.get("content", ""),
            sql=s.get("sql"),
            is_success=s.get("is_success", True),
            error_message=s.get("error_message"),
        )
        for s in steps_data
    ]

    chart_config = None
    if chart:
        chart_config = ChartConfig(
            chart_type=chart.get("chart_type", "table"),
            title=chart.get("title", "查询结果"),
            x_axis_label=chart.get("x_axis_label", ""),
            y_axis_label=chart.get("y_axis_label", ""),
            series_names=chart.get("series_names", []),
            recommended_reason=chart.get("recommended_reason", ""),
        )

    columns = [DataColumn(**c) for c in qr.get("columns", [])]

    return QueryResponse(
        conversation_id=conversation_id,
        question=question,
        generated_sql=result.get("generated_sql", ""),
        sql_valid=result.get("sql_valid", False),
        execution_time_ms=qr.get("execution_time_ms", 0),
        rows_returned=qr.get("row_count", 0),
        columns=columns,
        rows=qr.get("rows", []),
        total_rows=qr.get("row_count", 0),
        chart_config=chart_config,
        error_message=result.get("error_message"),
    )
