"""
FastAPI REST & WebSocket Server for Standalone Multi-Engine Agent Harness.
Exposes control endpoints, multi-provider chat dispatcher, log streaming, and viewport capture.
"""

import asyncio
import io
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import core.bootstrap
from core.config_manager import ConfigManager
from core.engine_controller import EngineController
from core.llm_engine import LLMEngine
from core.logger import get_logger
from core.nexus_bridge import NexusBridge

server_logger = get_logger("HarnessAPIServer", "harness_server.log")

active_websockets: List[WebSocket] = []

config_mgr = ConfigManager()
controller = EngineController(config_mgr)
nexus = NexusBridge()
llm_engine = LLMEngine(config_mgr, controller, nexus)


async def background_log_watcher():
    """Streams log deltas from the active UnrealEd engine to connected WebSocket clients."""
    while True:
        try:
            deltas = controller.get_log_deltas()
            if deltas and active_websockets:
                for line in deltas:
                    msg = {"event": "log_entry", "line": line}
                    for ws in list(active_websockets):
                        try:
                            await ws.send_json(msg)
                        except Exception:
                            pass
        except Exception:
            pass
        await asyncio.sleep(0.5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(background_log_watcher())
    yield
    task.cancel()


app = FastAPI(
    title="Unreal Tournament AI Agent Harness API (Universal Multi-Engine)",
    description="Standalone autonomous level design engine supporting UT99 GOTY, UTron Mod, UT2003, and UT2004.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExecRequest(BaseModel):
    commands: List[str]


class SpawnActorRequest(BaseModel):
    actor_class: str
    location: List[float]
    properties: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, Any]]] = None


class SwitchEngineRequest(BaseModel):
    engine_id: str


@app.get("/api/status")
def get_status():
    hwnd, edit_hwnd, pid = controller.find_unrealed_window()
    active_engine = config_mgr.get_active_engine_profile()
    return {
        "status": "online" if hwnd else "offline",
        "active_engine": active_engine.get("id"),
        "engine_name": active_engine.get("name"),
        "generation": active_engine.get("generation"),
        "unrealed_hwnd": hwnd,
        "edit_hwnd": edit_hwnd,
        "pid": pid,
        "nexus_connected": nexus.is_available,
    }


@app.get("/api/engine/profiles")
def get_engine_profiles():
    return {
        "active_engine": config_mgr.get_active_engine_id(),
        "profiles": config_mgr.get_all_engine_profiles(),
    }


@app.post("/api/engine/switch")
def switch_engine(req: SwitchEngineRequest):
    ok = config_mgr.set_active_engine_id(req.engine_id)
    if not ok:
        raise HTTPException(status_code=400, detail=f"Engine profile '{req.engine_id}' not found.")
    controller._refresh_paths()
    return {"status": "success", "active_engine": req.engine_id}


@app.post("/api/exec")
def execute_commands(req: ExecRequest):
    results = controller.execute_batch(req.commands)
    return {"status": "success", "results": results}


@app.post("/api/spawn_actor")
def spawn_actor(req: SpawnActorRequest):
    loc = req.location if len(req.location) >= 3 else [0.0, 0.0, 0.0]
    cmds = [
        f"BRUSH MOVETO X={loc[0]} Y={loc[1]} Z={loc[2]}",
        f"ACTOR ADD CLASS={req.actor_class}",
        "FLUSH",
    ]
    results = controller.execute_batch(cmds)
    return {"status": "success", "commands": cmds, "results": results}


@app.post("/api/chat")
def chat(req: ChatRequest):
    resp = llm_engine.chat(req.message, req.history)
    return resp


@app.get("/api/viewport")
def get_viewport():
    img_bytes = controller.capture_viewport_image()
    if not img_bytes:
        raise HTTPException(status_code=404, detail="Viewport capture unavailable or UnrealEd not found.")
    return Response(content=img_bytes, media_type="image/png")


@app.websocket("/ws/logs")
async def websocket_logs(ws: WebSocket):
    await ws.accept()
    active_websockets.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        if ws in active_websockets:
            active_websockets.remove(ws)
