"""
NL2SQL BI Agent + Learning Tracker — FastAPI 主程序入口
"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.api.routes import router as nl2sql_router
from backend.learning_tracker.api.routes import router as tracker_router
from backend.learning_tracker.core.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建学习追踪系统的所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="NL2SQL BI Agent + Learning Tracker",
    description="NL2SQL 查询系统 + AI 学习进度打卡系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 NL2SQL 路由（/api/v1/*）
app.include_router(nl2sql_router)

# 注册学习打卡路由（/api/v1/learning/*）
app.include_router(tracker_router)


@app.get("/health")
async def health():
    return {"status": "ok", "nl2sql": "ok", "learning_tracker": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info",
    )
