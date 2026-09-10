from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.content import SiteContent

router = APIRouter(prefix="/content", tags=["content"])


@router.get("")
def get_homepage_content(db: Session = Depends(get_db)) -> dict:
    """Return the configurable homepage content or an empty object for frontend fallbacks."""
    content = db.get(SiteContent, "homepage")
    return content.data if content else {}
