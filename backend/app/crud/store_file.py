from sqlalchemy.orm import Session
from typing import Optional, List
from app import models, schemas

def get_store_file(db: Session, file_id: int) -> Optional[models.StoreFile]:
    return db.query(models.StoreFile).filter(models.StoreFile.Id == file_id).first()

def get_store_file_by_filename(db: Session, filename: str) -> Optional[models.StoreFile]:
    return db.query(models.StoreFile).filter(models.StoreFile.TagName == filename).first()

def get_store_files(db: Session, skip: int = 0, limit: int = 100) -> List[models.StoreFile]:
    return db.query(models.StoreFile).offset(skip).limit(limit).all()

def create_store_file(db: Session, file: schemas.StoreFileCreate, author_id: int) -> models.StoreFile:
    db_file = models.StoreFile(**file.model_dump(), AuthorId=author_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file