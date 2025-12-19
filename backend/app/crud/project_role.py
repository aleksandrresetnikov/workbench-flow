from typing import List, Optional

from sqlalchemy.orm import Session

from app import models, schemas


def get_project_roles(db: Session, project_id: int) -> List[models.ProjectRoleEntity]:
    return db.query(models.ProjectRoleEntity).filter(
        models.ProjectRoleEntity.ProjectId == project_id
    ).all()


def get_project_role(db: Session, role_id: int) -> Optional[models.ProjectRoleEntity]:
    return db.query(models.ProjectRoleEntity).filter(
        models.ProjectRoleEntity.Id == role_id
    ).first()


def create_project_role(
    db: Session,
    project_id: int,
    role_data: schemas.ProjectRoleCreate,
) -> models.ProjectRoleEntity:
    db_role = models.ProjectRoleEntity(
        ProjectId=project_id,
        RoleName=role_data.RoleName,
        Rate=role_data.Rate,
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_project_role(
    db: Session,
    role_id: int,
    role_data: schemas.ProjectRoleUpdate,
) -> Optional[models.ProjectRoleEntity]:
    db_role = get_project_role(db, role_id)
    if not db_role:
        return None

    data = role_data.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_role, field, value)

    db.commit()
    db.refresh(db_role)
    return db_role


def delete_project_role(db: Session, role_id: int) -> bool:
    db_role = get_project_role(db, role_id)
    if not db_role:
        return False

    db.delete(db_role)
    db.commit()
    return True


