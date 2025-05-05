from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


tag_router = APIRouter(prefix="/tags", tags=["tags"])


# Tag endpoints
@tag_router.post("/", response_model=schemas.Tag)
def create_tag(
    tag: schemas.TagCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    db_tag = models.Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    logger.info(f"Tag {db_tag.name} created by user: {current_user.email}")
    return db_tag


@tag_router.get("/", response_model=List[schemas.Tag])
def read_tags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    tags = db.query(models.Tag).offset(skip).limit(limit).all()
    logger.info(f"Tags retrieved for user: {current_user.email}, count: {len(tags)}")
    return tags
