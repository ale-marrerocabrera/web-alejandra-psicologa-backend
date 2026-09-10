from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import require_admin, require_csrf
from app.db import get_db
from app.models.contact import ContactMessage
from app.models.content import SiteContent
from app.models.user import User
from app.schemas.admin import (
    ContactMessageResponse,
    ContactMessageStatusUpdate,
    HomepageContentResponse,
    HomepageContentUpdate,
    MessageStatus,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/content/homepage", response_model=HomepageContentResponse)
def get_admin_homepage_content(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> HomepageContentResponse:
    content = db.get(SiteContent, "homepage")
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contenido no encontrado.")
    return HomepageContentResponse(data=content.data, updated_at=content.updated_at)


@router.put("/content/homepage", response_model=HomepageContentResponse)
def update_admin_homepage_content(
    payload: HomepageContentUpdate,
    _: User = Depends(require_admin),
    __: None = Depends(require_csrf),
    db: Session = Depends(get_db),
) -> HomepageContentResponse:
    content = db.get(SiteContent, "homepage")
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contenido no encontrado.")
    content.data = payload.data.model_dump(mode="json")
    db.commit()
    db.refresh(content)
    return HomepageContentResponse(data=content.data, updated_at=content.updated_at)


@router.get("/messages", response_model=list[ContactMessageResponse])
def list_contact_messages(
    status_filter: MessageStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[ContactMessage]:
    query = select(ContactMessage).order_by(ContactMessage.created_at.desc()).limit(limit).offset(offset)
    if status_filter:
        query = query.where(ContactMessage.status == status_filter)
    return list(db.scalars(query))


@router.patch("/messages/{message_id}", response_model=ContactMessageResponse)
def update_contact_message_status(
    message_id: int,
    payload: ContactMessageStatusUpdate,
    _: User = Depends(require_admin),
    __: None = Depends(require_csrf),
    db: Session = Depends(get_db),
) -> ContactMessage:
    message = db.get(ContactMessage, message_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensaje no encontrado.")

    message.status = payload.status
    message.read_at = datetime.utcnow() if payload.status == "read" else None
    db.commit()
    db.refresh(message)
    return message


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact_message(
    message_id: int,
    _: User = Depends(require_admin),
    __: None = Depends(require_csrf),
    db: Session = Depends(get_db),
) -> Response:
    message = db.get(ContactMessage, message_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensaje no encontrado.")
    db.delete(message)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
