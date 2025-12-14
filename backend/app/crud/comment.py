from sqlalchemy.orm import Session
from typing import Optional, List
from app import models, schemas

def get_comment(db: Session, comment_id: int) -> Optional[models.Comment]:
    return db.query(models.Comment).filter(models.Comment.Id == comment_id).first()

def get_task_comments(db: Session, task_id: int) -> List[models.Comment]:
    return db.query(models.Comment).filter(
        models.Comment.TaskId == task_id
    ).order_by(models.Comment.CreateDate).all()

def create_comment(db: Session, comment: schemas.CommentCreate, author_id: int) -> models.Comment:
    db_comment = models.Comment(**comment.model_dump(), AuthorId=author_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def update_comment(db: Session, comment_id: int, text: str) -> Optional[models.Comment]:
    db_comment = get_comment(db, comment_id)
    if not db_comment:
        return None
    
    db_comment.Text = text
    db.commit()
    db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, comment_id: int) -> bool:
    db_comment = get_comment(db, comment_id)
    if not db_comment:
        return False
    
    db.delete(db_comment)
    db.commit()
    return True