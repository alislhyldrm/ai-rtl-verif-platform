import asyncio
import uuid
from pathlib import Path

import yaml
from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from backend.orchestrator.loop import VerificationLoop
from backend.parser.rtl_parser import parse_rtl
from backend.plan.schema import VerificationPlan

app = FastAPI(title="AI-RTL Verification Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_UPLOADS_DIR = _PROJECT_ROOT / "uploads"
_GENERATED_DIR = _PROJECT_ROOT / "generated"
_UPLOADS_DIR.mkdir(exist_ok=True)
_GENERATED_DIR.mkdir(exist_ok=True)

# In-memory run store (sufficient for MVP single-user)
_runs: dict[str, dict] = {}
_connections: dict[str, WebSocket] = {}


@app.post("/api/upload-rtl")
async def upload_rtl(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".sv"):
        raise HTTPException(status_code=400, detail="Only .sv files accepted")
    content = await file.read()
    dest = _UPLOADS_DIR / file.filename
    dest.write_bytes(content)
    try:
        iface = parse_rtl(dest)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    return iface.model_dump()


@app.post("/api/validate-plan")
async def validate_plan(data: dict):
    try:
        plan = VerificationPlan(**data)
        return {"valid": True, "plan": plan.model_dump()}
    except ValidationError as e:
        return {"valid": False, "errors": e.errors()}


@app.post("/api/run")
async def start_run(data: dict):
    try:
        plan = VerificationPlan(**data)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    run_id = str(uuid.uuid4())[:8]
    _runs[run_id] = {"status": "pending", "plan": plan.model_dump(), "report": None}

    asyncio.create_task(_run_loop(run_id, plan))
    return {"run_id": run_id}


async def _run_loop(run_id: str, plan: VerificationPlan) -> None:
    _runs[run_id]["status"] = "running"

    async def broadcast(event: dict) -> None:
        if ws := _connections.get(run_id):
            try:
                await ws.send_json(event)
            except Exception:
                pass

    loop = VerificationLoop(plan=plan)
    report = await loop.run(run_id=run_id, on_event=broadcast)
    _runs[run_id]["status"] = "done"
    _runs[run_id]["report"] = {
        "final_pct": report.final_pct,
        "iterations": len(report.iterations),
        "target_reached": report.target_reached,
    }


@app.get("/api/runs/{run_id}/report")
async def get_report(run_id: str):
    if run_id not in _runs:
        raise HTTPException(status_code=404)
    run = _runs[run_id]
    if run["status"] != "done":
        raise HTTPException(status_code=202, detail="Run not complete yet")
    return run["report"]


@app.get("/api/runs/{run_id}/tests/{iteration}")
async def get_test(run_id: str, iteration: int):
    test_file = _GENERATED_DIR / run_id / f"test_iter_{iteration}.py"
    if not test_file.exists():
        raise HTTPException(status_code=404)
    return {"code": test_file.read_text()}


@app.delete("/api/runs/{run_id}")
async def cancel_run(run_id: str):
    _runs.pop(run_id, None)
    _connections.pop(run_id, None)
    return {"cancelled": run_id}


@app.websocket("/ws/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    await websocket.accept()
    _connections[run_id] = websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _connections.pop(run_id, None)
