"""
Pydantic 请求 / 响应模型定义
"""

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


# ─── 请求模型 ──────────────────────────────────────────────────


class QueryRequest(BaseModel):
    """用户自然语言查询请求"""
    question: str = Field(..., description="用户的自然语言查询", min_length=1)
    conversation_id: Optional[str] = Field(None, description="会话 ID，用于上下文连续性")
    chart_type: Optional[str] = Field(
        None,
        description="指定图表类型，不指定则由系统自动推荐。可选: pie / bar / line / scatter / area / map / table"
    )
    top_k: int = Field(10, description="检索返回的最相关 Schema 片段数量")

    model_config = {"json_schema_extra": {
        "example": {
            "question": "最近一个月各省份的销售额和订单数是多少？",
            "conversation_id": "sess_001",
            "chart_type": "bar",
            "top_k": 10
        }
    }}


# ─── 响应模型 ──────────────────────────────────────────────────


class ChartConfig(BaseModel):
    """图表配置"""
    chart_type: str = Field(..., description="图表类型: pie/bar/line/scatter/area/map/table")
    title: str = Field(..., description="图表标题")
    x_axis_label: str = Field(..., description="X 轴标签")
    y_axis_label: str = Field(..., description="Y 轴标签")
    series_names: List[str] = Field(default_factory=list, description="系列名称列表")
    recommended_reason: str = Field("", description="推荐该图表类型的原因")


class DataColumn(BaseModel):
    """数据列定义"""
    name: str
    data_type: str  # VARCHAR, INT, DECIMAL, DATE, DATETIME
    comment: str = ""  # 中文注释/业务含义


class QueryStep(BaseModel):
    """SQL 生成过程中的单个步骤"""
    step_type: Literal["intent", "schema_select", "sql_generate", "sql_validate", "sql_execute", "chart_select", "final"] = ""
    content: str = ""
    sql: Optional[str] = None
    is_success: bool = True
    error_message: Optional[str] = None


class RetrievalContext(BaseModel):
    """RAG 检索到的上下文信息"""
    schema_chunks: List[Dict[str, Any]] = Field(default_factory=list)
    metric_definitions: List[Dict[str, Any]] = Field(default_factory=list)
    sql_examples: List[Dict[str, Any]] = Field(default_factory=list)


class QueryResponse(BaseModel):
    """完整查询响应（流式结束后汇总）"""
    conversation_id: str
    question: str
    generated_sql: str = ""
    sql_valid: bool = False
    execution_time_ms: int = 0
    rows_returned: int = 0

    # 数据
    columns: List[DataColumn] = Field(default_factory=list)
    rows: List[Dict[str, Any]] = Field(default_factory=list)
    total_rows: int = 0

    # 图表推荐
    chart_config: Optional[ChartConfig] = None

    # RAG 上下文摘要（用于调试和可解释性）
    retrieval_context: RetrievalContext = Field(default_factory=RetrievalContext)

    # 执行步骤链（展示 AI 思考过程）
    steps: List[QueryStep] = Field(default_factory=list)

    # 错误信息
    error_message: Optional[str] = None

    model_config = {"json_schema_extra": {
        "example": {
            "conversation_id": "sess_001",
            "question": "最近一个月各省份的销售额和订单数是多少？",
            "generated_sql": "SELECT province, SUM(order_amount) AS total_sales, COUNT(*) AS order_count FROM dim_orders WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) GROUP BY province ORDER BY total_sales DESC",
            "sql_valid": True,
            "execution_time_ms": 156,
            "rows_returned": 31,
            "chart_config": {
                "chart_type": "bar",
                "title": "最近一个月各省份销售情况",
                "x_axis_label": "省份",
                "y_axis_label": "销售额 / 订单数",
                "series_names": ["销售额(元)", "订单数"],
                "recommended_reason": "包含1个维度列(省份)和2个数值列，适合用柱状图对比展示"
            }
        }
    }}


class QueryStreamEvent(BaseModel):
    """SSE 流式事件"""
    event: str = ""  # step / data / chart / error / done
    data: Dict[str, Any] = Field(default_factory=dict)
