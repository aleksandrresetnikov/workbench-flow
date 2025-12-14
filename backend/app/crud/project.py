from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
from app import models, schemas
from .project_member import add_project_member

def get_project(db: Session, project_id: int) -> Optional[models.Project]:
    return db.query(models.Project).filter(
        models.Project.Id == project_id,
        models.Project.IsDeleted == False
    ).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[models.Project]:
    return db.query(models.Project).filter(
        models.Project.IsDeleted == False
    ).offset(skip).limit(limit).all()

def get_user_projects(db: Session, user_id: int) -> List[models.Project]:
    # Проекты, где пользователь владелец или участник
    return db.query(models.Project).join(models.ProjectMember).filter(
        and_(
            models.Project.IsDeleted == False,
            or_(
                models.Project.OwnerId == user_id,
                models.ProjectMember.MemnerId == user_id
            )
        )
    ).distinct().all()

def create_project(db: Session, project: schemas.ProjectCreate, owner_id: int) -> models.Project:
    db_project = models.Project(**project.model_dump(), OwnerId=owner_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Автоматически добавляем владельца как админа проекта
    add_project_member(db, db_project.Id, owner_id, schemas.ProjectRole.ADMIN)
    
    return db_project

def update_project(db: Session, project_id: int, project_update: schemas.ProjectUpdate) -> Optional[models.Project]:
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int) -> bool:
    db_project = get_project(db, project_id)
    if not db_project:
        return False
    
    db_project.IsDeleted = True
    db.commit()
    return True