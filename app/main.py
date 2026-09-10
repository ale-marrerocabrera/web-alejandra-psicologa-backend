from contextlib import asynccontextmanager
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401
from app.core.config import get_settings
from app.db import SessionLocal
from app.models.content import SiteContent
from app.models.user import User
from app.routers.admin import router as admin_router
from app.routers.admin_auth import router as admin_auth_router
from app.routers.contact import router as contact_router
from app.routers.content import router as content_router
from app.schemas.content import HomepageContent

settings = get_settings()
seed_content_path = Path(__file__).resolve().parent.parent / "data" / "homepage-content.json"


def seed_homepage_content() -> None:
    """Seed a new database; refresh it from JSON automatically in development."""
    with SessionLocal() as db:
        content = db.get(SiteContent, "homepage")
        if content is None or settings.app_env == "development":
            with seed_content_path.open(encoding="utf-8") as seed_file:
                seed_data = HomepageContent.model_validate(json.load(seed_file)).model_dump(mode="json")

            if content is None:
                db.add(SiteContent(key="homepage", data=seed_data))
            else:
                content.data = seed_data
            db.commit()


def seed_admin_user() -> None:
    if not settings.admin_email and not settings.admin_password:
        return
    if not settings.admin_email or not settings.admin_password:
        raise RuntimeError("ADMIN_EMAIL y ADMIN_PASSWORD deben configurarse juntos.")
    if len(settings.admin_password) < 12:
        raise RuntimeError("ADMIN_PASSWORD debe tener al menos 12 caracteres.")

    from sqlalchemy import select

    from app.core.auth import hash_password

    with SessionLocal() as db:
        admin_exists = db.scalar(select(User).where(User.role == "admin"))
        if not admin_exists:
            db.add(
                User(
                    email=str(settings.admin_email).lower(),
                    password_hash=hash_password(settings.admin_password),
                    role="admin",
                )
            )
            db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed_homepage_content()
    seed_admin_user()
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
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
)


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok"}


app.include_router(contact_router, prefix="/api")
app.include_router(content_router, prefix="/api")
app.include_router(admin_auth_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
