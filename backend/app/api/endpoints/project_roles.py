from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.auth import get_current_active_user, check_project_admin_access
from app.crud.project import get_project
from app.crud.project_role import (
    get_project_roles,
    get_project_role,
    create_project_role,
    update_project_role,
    delete_project_role,
)
from app.database import get_db


router = APIRouter()


@router.get(
    "/projects/{project_id}/roles",
    response_model=List[schemas.ProjectRole],
)
async def list_project_roles(
    project_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all roles for a project - requires project admin access."""
    if not check_project_admin_access(db, project_id, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin access to this project",
        )

    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return get_project_roles(db, project_id)


@router.post(
    "/projects/{project_id}/roles",
    response_model=schemas.ProjectRole,
)
async def create_role_for_project(
    project_id: int,
    role_data: schemas.ProjectRoleCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new role for project - requires admin access."""
    if not check_project_admin_access(db, project_id, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin access to this project",
        )

    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return create_project_role(db, project_id, role_data)


@router.put(
    "/roles/{role_id}",
    response_model=schemas.ProjectRole,
)
async def update_project_role_endpoint(
    role_id: int,
    role_data: schemas.ProjectRoleUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a project role - requires admin access for that project."""
    db_role = get_project_role(db, role_id)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    if not check_project_admin_access(db, db_role.ProjectId, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin access to this project",
        )

    updated = update_project_role(db, role_id, role_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    return updated


@router.delete("/roles/{role_id}")
async def delete_project_role_endpoint(
    role_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a project role - requires admin access for that project."""
    db_role = get_project_role(db, role_id)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    if not check_project_admin_access(db, db_role.ProjectId, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin access to this project",
        )

    success = delete_project_role(db, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    return {"message": "Role deleted successfully"}


