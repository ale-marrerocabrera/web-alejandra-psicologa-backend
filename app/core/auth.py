from datetime import datetime
from hashlib import sha256
from hmac import compare_digest
from secrets import token_urlsafe

from fastapi import Depends, Header, HTTPException, Request, status
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.session import AdminSession
from app.models.user import User

SESSION_COOKIE = "admin_session"
CSRF_COOKIE = "admin_csrf"
password_hash = PasswordHash.recommended()


def hash_token(token: str) -> str:
    return sha256(token.encode()).hexdigest()


def create_token() -> str:
    return token_urlsafe(32)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def get_current_session(request: Request, db: Session = Depends(get_db)) -> AdminSession:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticada.")

    session = db.scalar(select(AdminSession).where(AdminSession.token_hash == hash_token(token)))
    if not session or session.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión no válida o caducada.")
    return session


def require_admin(
    session: AdminSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, session.user_id)
    if not user or not user.is_active or user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso no autorizado.")
    return user


def require_csrf(
    request: Request,
    csrf_header: str | None = Header(default=None, alias="X-CSRF-Token"),
    session: AdminSession = Depends(get_current_session),
) -> None:
    csrf_cookie = request.cookies.get(CSRF_COOKIE)
    if not csrf_cookie or not csrf_header or not compare_digest(csrf_cookie, csrf_header):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token CSRF no válido.")
    if not compare_digest(hash_token(csrf_cookie), session.csrf_token_hash):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token CSRF no válido.")
