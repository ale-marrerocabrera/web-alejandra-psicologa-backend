from contextlib import asynccontextmanager
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401
from app.core.config import get_settings
from app.db import Base, SessionLocal, engine
from app.models.content import SiteContent
from app.routers.contact import router as contact_router
from app.routers.content import router as content_router

settings = get_settings()
seed_content_path = Path(__file__).resolve().parent.parent / "data" / "homepage-content.json"


def seed_homepage_content() -> None:
    """Seed a new database; refresh it from JSON automatically in development."""
    with SessionLocal() as db:
        content = db.get(SiteContent, "homepage")
        if content is None or settings.app_env == "development":
            with seed_content_path.open(encoding="utf-8") as seed_file:
                seed_data = json.load(seed_file)

            if content is None:
                db.add(SiteContent(key="homepage", data=seed_data))
            else:
                content.data = seed_data
            db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_homepage_content()
    yield


app = FastAPI(
    title="API — Psicóloga Alejandra",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok"}


app.include_router(contact_router, prefix="/api")
app.include_router(content_router, prefix="/api")
