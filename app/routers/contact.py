from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rate_limit import InMemoryRateLimiter
from app.db import get_db
from app.models.contact import ContactMessage
from app.schemas.contact import ContactCreate, ContactResponse

router = APIRouter(prefix="/contact", tags=["contact"])
settings = get_settings()
contact_rate_limiter = InMemoryRateLimiter(
    limit=settings.contact_rate_limit,
    window_seconds=settings.contact_rate_window_seconds,
)


def accepted_response() -> ContactResponse:
    """Use the same answer for valid and blocked submissions to avoid bot feedback."""
    return ContactResponse(id=0, message="Mensaje recibido correctamente.")


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    payload: ContactCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> ContactResponse:
    client_ip = request.client.host if request.client else "unknown"
    if payload.website or not contact_rate_limiter.is_allowed(client_ip):
        return accepted_response()

    contact = ContactMessage(**payload.model_dump(exclude={"website"}))
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return ContactResponse(id=contact.id, message="Mensaje recibido correctamente.")
