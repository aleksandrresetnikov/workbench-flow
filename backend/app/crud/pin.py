from sqlalchemy.orm import Session
from typing import Optional, List
from app import models, schemas

def get_pin(db: Session, user_id: int, task_id: int) -> Optional[models.Pin]:
    return db.query(models.Pin).filter(
        models.Pin.UserId == user_id,
        models.Pin.TaskId == task_id
    ).first()

def get_user_pins(db: Session, user_id: int) -> List[models.Pin]:
    return db.query(models.Pin).filter(
        models.Pin.UserId == user_id
    ).all()

def create_pin(db: Session, user_id: int, task_id: int) -> models.Pin:
    db_pin = models.Pin(UserId=user_id, TaskId=task_id)
    db.add(db_pin)
    db.commit()
    db.refresh(db_pin)
    return db_pin

def delete_pin(db: Session, user_id: int, task_id: int) -> bool:
    db_pin = get_pin(db, user_id, task_id)
    if not db_pin:
        return False
    
    db.delete(db_pin)
    db.commit()
    return True