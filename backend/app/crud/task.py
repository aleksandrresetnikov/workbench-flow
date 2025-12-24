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

import logging

logger = logging.getLogger(__name__)

def create_task(db: Session, task: schemas.TaskCreate, author_id: int) -> models.Task:
    task_data = task.model_dump(exclude_unset=True)
    logger.debug("create_task incoming data: %s", task_data)

    # Defensive: if StateId mistakenly set to 0, treat it as unspecified (NULL)
    if task_data.get('StateId') == 0:
        task_data.pop('StateId')

    # If no state specified, try to set a default (first existing TaskState) to avoid NULL/FK issues
    if task_data.get('StateId') is None:
        first_state = db.query(models.TaskState).order_by(models.TaskState.Id).first()
        if not first_state:
            # No states exist yet - create a sensible default so we don't violate FK
            logger.info("No TaskState found; creating default 'To Do' state")
            first_state = models.TaskState(Name='To Do')
            db.add(first_state)
            db.commit()
            db.refresh(first_state)
        task_data['StateId'] = first_state.Id

    logger.debug("create_task final data: %s", task_data)
    db_task = models.Task(**task_data, AuthorId=author_id)
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