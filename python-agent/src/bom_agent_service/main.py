"""FastAPI server for BOM Agent Service."""

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException

# Configure logging with file output
LOG_DIR = Path(__file__).parent.parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Create formatters
log_format = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format, datefmt="%H:%M:%S"))

# File handler with rotation (10MB max, keep 5 backups)
log_file = LOG_DIR / f"bom_agent_{datetime.now().strftime('%Y%m%d')}.log"
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding="utf-8",
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    datefmt=date_format,
    handlers=[console_handler, file_handler],
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .api import projects_router, knowledge_router, search_router, api_keys_router, clients_router, admin_router
from .auth import get_current_identity
from .db import init_db
from .flows.bom_flow import initialize_agents


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and agents on startup."""
    print("Starting BOM Agent Service...")
    print("Connecting to database...")
    init_db()
    print("Database connected.")
    initialize_agents()
    print("Ready to process BOMs!")
    yield
    print("Shutting down BOM Agent Service...")


app = FastAPI(
    title="BOM Agent Service",
    description="Multi-agent BOM processing with CrewAI",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers with authentication
app.include_router(projects_router, dependencies=[Depends(get_current_identity)])
app.include_router(knowledge_router, dependencies=[Depends(get_current_identity)])
app.include_router(search_router, dependencies=[Depends(get_current_identity)])
app.include_router(api_keys_router, dependencies=[Depends(get_current_identity)])
app.include_router(clients_router, dependencies=[Depends(get_current_identity)])

# Admin router has its own authentication via ADMIN_API_KEY
app.include_router(admin_router)


# =============================================================================
# OpenAI-compatible chat endpoint (for backward compatibility)
# =============================================================================

# Lazy initialization of crew
_crew = None


def get_crew():
    """Get or create the BOM analysis crew (lazy initialization)."""
    global _crew
    if _crew is None:
        from .agents.bom_agent import BomAnalysisCrew
        _crew = BomAnalysisCrew()
    return _crew


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "bom-agent"
    messages: list[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    response_format: Optional[dict] = None


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionChoice]
    usage: Usage


def detect_task_type(messages: list[ChatMessage]) -> tuple[str, str, str]:
    """Detect what type of task is being requested."""
    system_content = ""
    user_content = ""

    for msg in messages:
        if msg.role == "system":
            system_content = msg.content
        elif msg.role == "user":
            user_content = msg.content

    if "analyze" in system_content.lower() and "bom" in system_content.lower():
        return "analyze_bom", system_content, user_content
    elif "optimization" in system_content.lower() or "strategies" in system_content.lower():
        return "optimize_bom", system_content, user_content
    else:
        return "general_chat", system_content, user_content


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse, dependencies=[Depends(get_current_identity)])
async def create_chat_completion(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint."""
    try:
        task_type, system_content, user_content = detect_task_type(request.messages)

        crew = get_crew()
        if task_type == "analyze_bom":
            result = crew.analyze_bom(user_content)
        elif task_type == "optimize_bom":
            result = crew.generate_optimization_strategies(user_content)
        else:
            result = crew.general_chat(system_content, user_content)

        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:24]}",
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=result),
                    finish_reason="stop",
                )
            ],
            usage=Usage(
                prompt_tokens=len(user_content.split()) * 2,
                completion_tokens=len(result.split()) * 2,
                total_tokens=len(user_content.split()) * 2 + len(result.split()) * 2,
            ),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/models", dependencies=[Depends(get_current_identity)])
async def list_models():
    """List available models."""
    return {
        "object": "list",
        "data": [
            {
                "id": "bom-agent",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "bom-agent-service",
            }
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "service": "BOM Agent Service",
        "version": "0.1.0",
        "endpoints": {
            "projects": "/projects",
            "knowledge": "/knowledge",
            "chat": "/v1/chat/completions",
            "health": "/health",
        },
    }
