from sqlalchemy.orm import Session
from typing import Optional, List
from app import models, schemas

def get_task_state(db: Session, state_id: int) -> Optional[models.TaskState]:
    return db.query(models.TaskState).filter(models.TaskState.Id == state_id).first()

def get_task_states(db: Session) -> List[models.TaskState]:
    return db.query(models.TaskState).all()

def create_task_state(db: Session, state: schemas.TaskStateCreate) -> models.TaskState:
    db_state = models.TaskState(**state.model_dump())
    db.add(db_state)
    db.commit()
    db.refresh(db_state)
    return db_state