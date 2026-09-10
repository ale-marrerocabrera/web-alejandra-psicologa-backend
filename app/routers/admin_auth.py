from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.auth import (
    CSRF_COOKIE,
    SESSION_COOKIE,
    create_token,
    get_current_session,
    hash_token,
    require_admin,
    require_csrf,
    verify_password,
)
from app.core.config import get_settings
from app.db import get_db
from app.models.session import AdminSession
from app.models.user import User
from app.schemas.auth import AdminUserResponse, LoginRequest

router = APIRouter(prefix="/admin/auth", tags=["admin authentication"])
settings = get_settings()


def set_session_cookies(response: Response, session_token: str, csrf_token: str) -> None:
    cookie_options = {
        "max_age": settings.session_duration_hours * 3600,
        "secure": settings.session_cookie_secure,
        "samesite": "lax",
        "path": "/",
    }
    response.set_cookie(SESSION_COOKIE, session_token, httponly=True, **cookie_options)
    response.set_cookie(CSRF_COOKIE, csrf_token, httponly=False, **cookie_options)


@router.post("/login", response_model=AdminUserResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AdminUserResponse:
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email o contraseña incorrectos.")

    session_token = create_token()
    csrf_token = create_token()
    db.execute(delete(AdminSession).where(AdminSession.expires_at <= datetime.utcnow()))
    db.add(
        AdminSession(
            token_hash=hash_token(session_token),
            csrf_token_hash=hash_token(csrf_token),
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(hours=settings.session_duration_hours),
        )
    )
    db.commit()
    set_session_cookies(response, session_token, csrf_token)
    return AdminUserResponse(email=user.email, role=user.role)


@router.get("/me", response_model=AdminUserResponse)
def get_me(user: User = Depends(require_admin)) -> AdminUserResponse:
    return AdminUserResponse(email=user.email, role=user.role)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    session: AdminSession = Depends(get_current_session),
    _: None = Depends(require_csrf),
    db: Session = Depends(get_db),
) -> Response:
    db.delete(session)
    db.commit()
    response.delete_cookie(SESSION_COOKIE, path="/")
    response.delete_cookie(CSRF_COOKIE, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
