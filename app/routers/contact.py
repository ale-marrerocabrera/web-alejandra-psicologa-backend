from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.contact import ContactMessage
from app.schemas.contact import ContactCreate, ContactResponse

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)) -> ContactResponse:
    contact = ContactMessage(**payload.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return ContactResponse(id=contact.id, message="Mensaje recibido correctamente.")

