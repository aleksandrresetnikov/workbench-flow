from sqlalchemy.orm import Session
from typing import Optional, List
from app import models, schemas


def get_project_member(db: Session, project_id: int, member_id: int) -> Optional[models.ProjectMember]:
    return db.query(models.ProjectMember).filter(
        models.ProjectMember.ProjectId == project_id,
        models.ProjectMember.MemnerId == member_id
    ).first()


def get_project_members(db: Session, project_id: int) -> List[models.ProjectMember]:
    return db.query(models.ProjectMember).filter(
        models.ProjectMember.ProjectId == project_id
    ).all()


def add_project_member(
    db: Session,
    project_id: int,
    member_id: int,
    access_level: schemas.AccessLevel = "Common",
    role_id: Optional[int] = None,
) -> models.ProjectMember:
    db_member = models.ProjectMember(
        ProjectId=project_id,
        MemnerId=member_id,
        AccessLevel=access_level,
        RoleId=role_id,
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def update_project_member_access(
    db: Session,
    project_id: int,
    member_id: int,
    access_level: Optional[schemas.AccessLevel] = None,
    role_id: Optional[int] = None,
) -> Optional[models.ProjectMember]:
    db_member = get_project_member(db, project_id, member_id)
    if not db_member:
        return None

    if access_level is not None:
        db_member.AccessLevel = access_level
    db_member.RoleId = role_id

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