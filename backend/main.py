import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.routes import auth, admin


def get_application() -> FastAPI:
    _app = FastAPI(title=settings.PROJECT_NAME)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _app.include_router(auth.router)
    _app.include_router(admin.router)

    return _app


app = get_application()


@app.get("/test_connection")
def test_connection() -> dict[str, str]:
    return {"status": "ok"}


def debug() -> None:
    """Launched with `poetry run start` at root level"""
    uvicorn.run("backend.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)


def start() -> None:
    """Launched with `poetry run start` at root level without reload"""
    uvicorn.run("backend.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=False)
