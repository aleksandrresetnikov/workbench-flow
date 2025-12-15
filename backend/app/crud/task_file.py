from sqlalchemy.orm import Session
from typing import Optional, List
from app import models

def get_task_file(db: Session, task_id: int, file_id: int) -> Optional[models.TaskFile]:
    return db.query(models.TaskFile).filter(
        models.TaskFile.TaskId == task_id,
        models.TaskFile.FileId == file_id
    ).first()

def get_task_files(db: Session, task_id: int) -> List[models.TaskFile]:
    return db.query(models.TaskFile).filter(
        models.TaskFile.TaskId == task_id
    ).all()

def add_task_file(db: Session, task_id: int, file_id: int) -> models.TaskFile:
    db_task_file = models.TaskFile(TaskId=task_id, FileId=file_id)
    db.add(db_task_file)
    db.commit()
    db.refresh(db_task_file)
    return db_task_file

def remove_task_file(db: Session, task_id: int, file_id: int) -> bool:
    db_task_file = get_task_file(db, task_id, file_id)
    if not db_task_file:
        return False
    
    db.delete(db_task_file)
    db.commit()
    return True