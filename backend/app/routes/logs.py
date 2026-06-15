import asyncio
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.config import settings

router = APIRouter(prefix="/logs", tags=["logs"])
LOG_FILE = Path("logs") / "rag.log"


def ensure_log_file():
    LOG_FILE.parent.mkdir(exist_ok=True)
    LOG_FILE.touch(exist_ok=True)


async def stream_log_lines():
    ensure_log_file()
    position = 0
    heartbeat_count = 0

    while True:
        current_size = LOG_FILE.stat().st_size
        if current_size < position:
            position = 0

        if current_size > position:
            with LOG_FILE.open("r", encoding="utf-8") as log_file:
                log_file.seek(position)
                while True:
                    line = log_file.readline()
                    if not line:
                        break
                    position = log_file.tell()
                    heartbeat_count = 0
                    if line.strip():
                        yield f"data: {line.rstrip()}\n\n"
                        await asyncio.sleep(0)
        else:
            heartbeat_count += 1
            if heartbeat_count >= 30:
                heartbeat_count = 0
                yield ": keep-alive\n\n"
            await asyncio.sleep(0.5)


@router.get("")
async def get_logs():
    ensure_log_file()
    with LOG_FILE.open("r", encoding="utf-8") as log_file:
        lines = [
            line.rstrip()
            for line in log_file.readlines()
            if line.strip()
        ]
    return {"logs": lines[-settings.MAX_LOG_LINES:]}


@router.get("/stream")
async def stream_logs():
    return StreamingResponse(
        stream_log_lines(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )