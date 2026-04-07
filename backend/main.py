"""
NL2SQL BI Agent — FastAPI 主程序入口
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.api.routes import router

app = FastAPI(
    title="NL2SQL BI Agent",
    description="基于自然语言的 BI 查询系统 — NL2SQL + RAG + 可视化",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("  NL2SQL BI Agent 启动中...")
    print(f"  LLM: {'Ollama ' + settings.ollama_model if settings.use_ollama else 'OpenAI ' + settings.openai_model}")
    print(f"  向量数据库: Milvus Lite (本地文件模式)")
    print(f"  业务数据库: postgresql://{settings.db_user}@{settings.db_host}:{settings.db_port}/{settings.db_name}")
    print(f"  访问地址: http://{settings.api_host}:{settings.api_port}")
    print("=" * 60)


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info",
    )
