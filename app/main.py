"""
FastAPI entrypoint: HTML page + JSON API.

`app` is meant to be started with Uvicorn from the project root:

    uvicorn app.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import todos_store
from app.db import init_schema
from app.schemas import TodoCreate, TodoRead, TodoUpdate

# Templates and static files live next to the project root (parent of `app/`).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(_PROJECT_ROOT / "templates"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI calls this once on startup and once on shutdown.
    We only need startup: ensure the SQLite schema exists before any request.
    """
    init_schema()
    yield


app = FastAPI(title="Todo demo", lifespan=lifespan)

# Serve everything in `/static` from the `static/` folder (CSS + JS).
app.mount(
    "/static",
    StaticFiles(directory=str(_PROJECT_ROOT / "static")),
    name="static",
)


@app.get("/")
def index(request: Request):
    """Serve the single-page UI."""
    return templates.TemplateResponse(
        request,
        "index.html",
        {"request": request},
    )


@app.get("/api/todos", response_model=list[TodoRead])
def list_todos():
    """Return todos in display order (see `todos_store.get_all_todos`)."""
    return todos_store.get_all_todos()


@app.post("/api/todos", response_model=TodoRead)
def add_todo(body: TodoCreate):
    """Create a todo; Pydantic already trimmed and rejected empty titles."""
    return todos_store.create_todo(body.title)


@app.patch("/api/todos/{todo_id}", response_model=TodoRead)
def patch_todo(todo_id: int, body: TodoUpdate):
    """Toggle completion; missing ids return 404."""
    updated = todos_store.update_todo_completed(todo_id, body.completed)
    if updated is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated


@app.delete("/api/todos/{todo_id}")
def remove_todo(todo_id: int):
    """Delete a todo; missing ids return 404."""
    if not todos_store.delete_todo(todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
    return JSONResponse({"ok": True})
