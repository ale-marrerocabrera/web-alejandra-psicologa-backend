from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.content import SiteContent
from app.schemas.content import HomepageContent

router = APIRouter(prefix="/content", tags=["content"])


@router.get("", response_model=HomepageContent)
def get_homepage_content(db: Session = Depends(get_db)) -> HomepageContent:
    """Return the validated content required to render the public homepage."""
    content = db.get(SiteContent, "homepage")
    if not content:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Contenido no disponible.")
    try:
        return HomepageContent.model_validate(content.data)
    except ValidationError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Contenido no disponible.") from error
