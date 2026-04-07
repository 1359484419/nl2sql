"""
SQL 执行器 — 执行 NL2SQL Agent 生成的 SQL，返回查询结果（PostgreSQL）
"""

import time
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import create_engine, text

from backend.config import settings


def _infer_data_type_from_value(value: Any) -> str:
    """根据 Python 值推断与前端 chart 逻辑兼容的 data_type 字符串。"""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "BOOLEAN"
    if isinstance(value, int):
        return "BIGINT"
    if isinstance(value, float):
        return "DOUBLE PRECISION"
    if isinstance(value, Decimal):
        return "NUMERIC"
    if isinstance(value, (datetime, date)):
        return "TIMESTAMP"
    return "VARCHAR"


def _build_columns_metadata(rows: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """从结果行推断列类型（此前全部标成 VARCHAR 会导致前端无法识别数值列、图表无 series）。"""
    if not rows:
        return []
    keys = list(rows[0].keys())
    out: List[Dict[str, str]] = []
    for key in keys:
        data_type = "VARCHAR"
        for row in rows[:80]:
            v = row.get(key)
            if v is not None:
                inferred = _infer_data_type_from_value(v)
                if inferred:
                    data_type = inferred
                    break
        out.append({"name": key, "data_type": data_type})
    return out


class SQLExecutor:
    """SQL 执行器"""

    def __init__(self):
        self._engine = None
        self._init_engine()

    def _init_engine(self):
        db_url = settings.db_url
        self._engine = create_engine(
            db_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=settings.debug,
        )
        print(f"[SQLExecutor] 数据库连接已初始化: PostgreSQL via {db_url[:40]}...")

    def execute(self, sql: str) -> Dict[str, Any]:
        """执行 SQL 并返回结果"""
        start_time = time.time()
        with self._engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = [dict(row._mapping) for row in result.fetchall()]
            columns = _build_columns_metadata(rows)
            execution_time_ms = int((time.time() - start_time) * 1000)

            return {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "execution_time_ms": execution_time_ms,
            }

    def execute_non_query(self, sql: str) -> int:
        """执行非查询 SQL（INSERT/UPDATE/DELETE），返回影响行数"""
        with self._engine.connect() as conn:
            result = conn.execute(text(sql))
            conn.commit()
            return result.rowcount

    def validate_with_explain(self, sql: str) -> Tuple[bool, Optional[str]]:
        """
        用 EXPLAIN 在数据库侧校验 SQL（解析 + 列/表是否存在），不返回真实数据行。
        避免仅靠字符串规则导致「SQL 有效」但列名臆造无法在 DataGrip 执行的问题。
        """
        stmt = sql.strip().rstrip(";")
        if not stmt:
            return False, "SQL 为空"
        explain_sql = f"EXPLAIN (COSTS OFF) {stmt}"
        try:
            with self._engine.connect() as conn:
                conn.execute(text(explain_sql))
            return True, None
        except Exception as e:
            return False, str(e)


# 全局单例
sql_executor = SQLExecutor()
