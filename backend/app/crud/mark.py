from typing import List, Optional

from sqlalchemy.orm import Session

from app import models, schemas


def get_mark(db: Session, mark_id: int) -> Optional[models.Mark]:
    return db.query(models.Mark).filter(models.Mark.Id == mark_id).first()


def get_task_marks(db: Session, task_id: int) -> List[models.Mark]:
    return (
        db.query(models.Mark)
        .filter(models.Mark.TargetTask == task_id)
        .order_by(models.Mark.CreateDate)
        .all()
    )


def create_mark(db: Session, data: schemas.MarkCreate, user_id: int) -> models.Mark:
    db_mark = models.Mark(
        TargetTask=data.TargetTask,
        MarkedById=user_id,
        Description=data.Description,
        Rate=data.Rate,
    )
    db.add(db_mark)
    db.commit()
    db.refresh(db_mark)
    return db_mark


def update_mark(
    db: Session,
    mark_id: int,
    data: schemas.MarkUpdate,
) -> Optional[models.Mark]:
    db_mark = get_mark(db, mark_id)
    if not db_mark:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_mark, field, value)

    db.commit()
    db.refresh(db_mark)
    return db_mark


def delete_mark(db: Session, mark_id: int) -> bool:
    db_mark = get_mark(db, mark_id)
    if not db_mark:
        return False

    db.delete(db_mark)
    db.commit()
    return True


