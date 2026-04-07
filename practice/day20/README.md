# Day 20 — SSE 流式输出

## 今日目标

理解 SSE（Server-Sent Events）和 WebSocket 的区别，能写简单的 SSE 服务。

## 练习 20-1：写一个 SSE 服务（必做）

新建 `day20_sse.py`：

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio, json

app = FastAPI()

@app.get("/stream")
async def stream_events():
    async def event_generator():
        for word in ["你", "好", "，", "这", "是", "SSE", "！"]:
            await asyncio.sleep(0.3)
            yield f"data: {json.dumps({'token': word})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

启动后用浏览器访问 http://localhost:8002/stream 看效果。

---

## 练习 20-2：分析 routes.py 的 SSE 实现（必做）

新建 `day20_sse_analysis.py`，回答：
- NL2SQL 的 SSE 接口返回什么数据格式？
- `yield` 在 async 函数里是什么意思？
