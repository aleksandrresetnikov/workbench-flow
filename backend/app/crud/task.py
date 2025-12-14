from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from app import models, schemas

def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    return db.query(models.Task).filter(models.Task.Id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[models.Task]:
    return db.query(models.Task).offset(skip).limit(limit).all()

def get_user_tasks(db: Session, user_id: int, closed: Optional[bool] = None) -> List[models.Task]:
    query = db.query(models.Task).filter(
        or_(
            models.Task.AuthorId == user_id,
            models.Task.TargetId == user_id
        )
    )
    
    if closed is not None:
        query = query.filter(models.Task.IsClosed == closed)
    
    return query.all()

def get_project_tasks(db: Session, project_id: int, closed: Optional[bool] = None) -> List[models.Task]:
    # Получаем все задачи через группы проекта
    query = db.query(models.Task).join(models.TaskGroup).filter(
        models.TaskGroup.ProjectId == project_id
    )
    
    if closed is not None:
        query = query.filter(models.Task.IsClosed == closed)
    
    return query.all()

def create_task(db: Session, task: schemas.TaskCreate, author_id: int) -> models.Task:
    db_task = models.Task(**task.model_dump(), AuthorId=author_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate) -> Optional[models.Task]:
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int) -> bool:
    db_task = get_task(db, task_id)
    if not db_task:
        return False
    
    db.delete(db_task)
    db.commit()
    return True