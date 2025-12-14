from sqlalchemy.orm import Session
from typing import Optional, List
from app import models, schemas

def get_task_group(db: Session, group_id: int) -> Optional[models.TaskGroup]:
    return db.query(models.TaskGroup).filter(models.TaskGroup.Id == group_id).first()

def get_project_task_groups(db: Session, project_id: int) -> List[models.TaskGroup]:
    return db.query(models.TaskGroup).filter(
        models.TaskGroup.ProjectId == project_id
    ).all()

def create_task_group(db: Session, group: schemas.TaskGroupCreate) -> models.TaskGroup:
    db_group = models.TaskGroup(**group.model_dump())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def update_task_group(db: Session, group_id: int, name: str) -> Optional[models.TaskGroup]:
    db_group = get_task_group(db, group_id)
    if not db_group:
        return None
    
    db_group.Name = name
    db.commit()
    db.refresh(db_group)
    return db_group

def delete_task_group(db: Session, group_id: int) -> bool:
    db_group = get_task_group(db, group_id)
    if not db_group:
        return False
    
    db.delete(db_group)
    db.commit()
    return True