from __future__ import annotations

from fastapi import FastAPI
from uvicorn import Config, Server


def build_app(app) -> FastAPI:
    api = FastAPI(title="Whispefy")

    @api.get("/health")
    async def health():
        print("[Whispefy] GET /health", flush=True)
        return {"status": "ok"}

    @api.post("/toggle")
    async def toggle():
        print("[Whispefy] POST /toggle", flush=True)
        app.toggle()
        return {"ok": True, "active": app.is_active}

    @api.post("/stop")
    async def stop():
        print("[Whispefy] POST /stop", flush=True)
        app.stop()
        return {"ok": True}

    return api


def build_server(port: int, app) -> Server:
    return Server(
        Config(
            build_app(app),
            host="127.0.0.1",
            port=port,
            log_level="warning",
            access_log=False,
            loop="asyncio",
        )
    )
