"""FastAPI Application Main Entrypoint for JARVIS Local Agent."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jarvis.api.routes import router as api_router
from jarvis.config.settings import get_settings

settings = get_settings()

app = FastAPI(
    title="JARVIS Local Agent API",
    version="0.2.0",
    description="Local Agent Core API bound exclusively to 127.0.0.1:8765",
)

# CORS restricted exclusively to local desktop shell origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1",
        "http://localhost",
        "tauri://localhost",
        "http://tauri.localhost",
        "https://tauri.localhost",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$|^tauri://localhost$|^https?://tauri\.localhost$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def root_health():
    """Root health check for application."""
    return {
        "status": "healthy",
        "agent": "jarvis-local",
        "version": "0.2.0",
        "host": settings.local_host,
        "port": settings.local_port,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "jarvis.main:app",
        host=settings.local_host,
        port=settings.local_port,
        reload=(settings.env == "development"),
    )
