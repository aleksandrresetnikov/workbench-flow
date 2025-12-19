from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.auth import get_current_active_user, check_project_access, check_project_admin_access
from app.crud.mark import (
    get_mark,
    get_task_marks,
    create_mark,
    update_mark,
    delete_mark,
)
from app.crud.task import get_task
from app.crud.task_group import get_task_group
from app.database import get_db


router = APIRouter()


def _get_task_project_id(db: Session, task: models.Task) -> int | None:
    if not task.GroupId:
        return None
    group = get_task_group(db, task.GroupId)
    return group.ProjectId if group else None


def _ensure_can_manage_mark_for_task(
    db: Session,
    task: models.Task,
    current_user: models.User,
) -> int:
    """Return project_id if user is allowed to manage marks for this task."""
    project_id = _get_task_project_id(db, task)
    if project_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not linked to a project",
        )

    # Admin of project always can
    if check_project_admin_access(db, project_id, current_user.Id):
        return project_id

    # Responsible user (TargetId) can create/update/delete their own marks
    if task.TargetId != current_user.Id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only task assignee or project admin can manage marks",
        )

    # Also verify at least project access
    if not check_project_access(db, project_id, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project",
        )

    return project_id


@router.get("/tasks/{task_id}/marks", response_model=List[schemas.Mark])
async def list_task_marks(
    task_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List all marks for a task - requires project access."""
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    project_id = _get_task_project_id(db, task)
    if project_id is not None and not check_project_access(db, project_id, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project",
        )

    return get_task_marks(db, task_id)


@router.post("/tasks/{task_id}/marks", response_model=schemas.Mark)
async def create_task_mark(
    task_id: int,
    mark_data: schemas.MarkCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a mark for a task - only assignee (TargetId) or project admin."""
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    _ensure_can_manage_mark_for_task(db, task, current_user)

    # Ensure MarkCreate.TargetTask matches path
    if mark_data.TargetTask != task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TargetTask mismatch with path parameter",
        )

    return create_mark(db, mark_data, current_user.Id)


@router.put("/marks/{mark_id}", response_model=schemas.Mark)
async def update_task_mark(
    mark_id: int,
    mark_data: schemas.MarkUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update existing mark - only its author (assignee) or project admin."""
    db_mark = get_mark(db, mark_id)
    if not db_mark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mark not found",
        )

    task = get_task(db, db_mark.TargetTask)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    project_id = _ensure_can_manage_mark_for_task(db, task, current_user)

    # If user is not project admin, they must be author of the mark
    if not check_project_admin_access(db, project_id, current_user.Id) and db_mark.MarkedById != current_user.Id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can edit only your own marks",
        )

    updated = update_mark(db, mark_id, mark_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mark not found",
        )

    return updated


@router.delete("/marks/{mark_id}")
async def delete_task_mark(
    mark_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a mark - only its author (assignee) or project admin."""
    db_mark = get_mark(db, mark_id)
    if not db_mark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mark not found",
        )

    task = get_task(db, db_mark.TargetTask)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    project_id = _ensure_can_manage_mark_for_task(db, task, current_user)

    # If user is not project admin, they must be author of the mark
    if not check_project_admin_access(db, project_id, current_user.Id) and db_mark.MarkedById != current_user.Id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can delete only your own marks",
        )

    success = delete_mark(db, mark_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mark not found",
        )

    return {"message": "Mark deleted successfully"}


