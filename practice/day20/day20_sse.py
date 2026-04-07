"""
Day 20 — 练习 20-1：SSE 流式输出服务
"""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

@app.get("/stream")
async def stream_events():
    """模拟流式输出：每秒推送一个字"""
    words = ["你", "好", "，", "这", "是", "一", "个", "流", "式", "响", "应", "！"]
    async def event_generator():
        for word in words:
            await asyncio.sleep(0.3)
            data = json.dumps({"token": word, "type": "content"})
            yield f"data: {data}\n\n"
        # 发送完成信号
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/")
async def root():
    return {"message": "SSE 服务已启动", "endpoint": "/stream"}

if __name__ == "__main__":
    import uvicorn
    print("启动 SSE 服务: http://localhost:8002/stream")
    print("用浏览器打开查看流式效果！\n")
    uvicorn.run(app, host="0.0.0.0", port=8002)
