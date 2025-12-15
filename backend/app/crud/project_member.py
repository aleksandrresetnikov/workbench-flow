from sqlalchemy.orm import Session
from typing import Optional, List
from app import models, schemas
from app.schemas.project import ProjectRole


def get_project_member(db: Session, project_id: int, member_id: int) -> Optional[models.ProjectMember]:
    return db.query(models.ProjectMember).filter(
        models.ProjectMember.ProjectId == project_id,
        models.ProjectMember.MemnerId == member_id
    ).first()

def get_project_members(db: Session, project_id: int) -> List[models.ProjectMember]:
    return db.query(models.ProjectMember).filter(
        models.ProjectMember.ProjectId == project_id
    ).all()

def add_project_member(db: Session, project_id: int, member_id: int, role: ProjectRole = ProjectRole.COMMON) -> models.ProjectMember:
    db_member = models.ProjectMember(
        ProjectId=project_id,
        MemnerId=member_id,
        Role=role.value
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def update_project_member_role(db: Session, project_id: int, member_id: int, role: ProjectRole) -> Optional[models.ProjectMember]:
    db_member = get_project_member(db, project_id, member_id)
    if not db_member:
        return None
    
    db_member.Role = role.value
    db.commit()
    db.refresh(db_member)
    return db_member

def remove_project_member(db: Session, project_id: int, member_id: int) -> bool:
    db_member = get_project_member(db, project_id, member_id)
    if not db_member:
        return False
    
    db.delete(db_member)
    db.commit()
    return True