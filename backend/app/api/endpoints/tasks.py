from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.crud.task import (
    get_task, get_tasks, get_user_tasks, get_project_tasks, 
    create_task, update_task, delete_task
)
from app.crud.task_group import get_task_group
from app.crud.project import get_project
from app.crud.user import get_user
from app.database import get_db

from app.auth import get_current_active_user, check_project_access
from app import schemas, models

router = APIRouter()

@router.get("/tasks/{task_id}", response_model=schemas.TaskWithDetails)
async def get_single_task(
    task_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a single task by ID - requires project access"""
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access to the project (if task has a group)
    if task.GroupId:
        task_group = get_task_group(db, task.GroupId)
        if task_group and not check_project_access(db, task_group.ProjectId, current_user.Id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project"
            )
    
    return task

@router.get("/tasks/", response_model=List[schemas.Task])
async def get_all_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all tasks (accessible to all authenticated users)"""
    tasks = get_tasks(db, skip=skip, limit=limit)
    return tasks

@router.get("/tasks/my", response_model=List[schemas.TaskWithDetails])
async def get_my_tasks(
    closed: Optional[bool] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get tasks assigned to or created by the current user"""
    tasks = get_user_tasks(db, current_user.Id, closed)
    return tasks

@router.get("/projects/{project_id}/tasks", response_model=List[schemas.TaskWithDetails])
async def get_project_tasks_endpoint(
    project_id: int,
    closed: Optional[bool] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all tasks for a project - requires project access"""
    # Check if user has access to the project
    if not check_project_access(db, project_id, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project"
        )
    
    # Check if project exists
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    try:
        tasks = get_project_tasks(db, project_id, closed)
        return tasks
    except Exception as e:
        # If the DB schema is out of date (missing columns), provide a clear error for debugging
        import sqlalchemy
        if isinstance(e, sqlalchemy.exc.ProgrammingError):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=("Database schema mismatch detected (likely a missing migration). "
                        "Please run: `alembic upgrade head` in the backend and restart the server. "
                        f"Original error: {str(e)}"),
            )
        raise

@router.post("/projects/{project_id}/tasks", response_model=schemas.Task)
async def create_new_task(
    project_id: int,
    task_data: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new task in a project - requires project access"""
    # Check if user has access to the project
    if not check_project_access(db, project_id, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project"
        )
    
    # Check if project exists
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if target user exists (if specified)
    if task_data.TargetId:
        target_user = get_user(db, task_data.TargetId)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found"
            )
    
    # Check if task group belongs to this project (if specified)
    if task_data.GroupId:
        task_group = get_task_group(db, task_data.GroupId)
        if not task_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task group not found"
            )
        if task_group.ProjectId != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task group does not belong to this project"
            )
    
    task = create_task(db, task_data, current_user.Id)
    return task

@router.put("/tasks/{task_id}", response_model=schemas.Task)
async def update_existing_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a task - requires project access"""
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access to the project (if task has a group)
    if task.GroupId:
        task_group = get_task_group(db, task.GroupId)
        if task_group and not check_project_access(db, task_group.ProjectId, current_user.Id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project"
            )
    
    # Check if trying to change target user to non-existent user
    if task_update.TargetId is not None:
        target_user = get_user(db, task_update.TargetId)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found"
            )
    
    # Check if trying to change task group to one from different project
    if task_update.GroupId is not None and task_update.GroupId != task.GroupId:
        new_group = get_task_group(db, task_update.GroupId)
        if not new_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New task group not found"
            )
        # Find the project ID of the current task
        current_group = get_task_group(db, task.GroupId)
        if current_group and current_group.ProjectId != new_group.ProjectId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot move task to group in different project"
            )
    
    updated_task = update_task(db, task_id, task_update)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return updated_task

@router.delete("/tasks/{task_id}")
async def delete_existing_task(
    task_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a task - requires project access"""
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access to the project (if task has a group)
    if task.GroupId:
        task_group = get_task_group(db, task.GroupId)
        if task_group and not check_project_access(db, task_group.ProjectId, current_user.Id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project"
            )
    
    success = delete_task(db, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return {"message": "Task deleted successfully"}

@router.post("/tasks/{task_id}/close")
async def close_task(
    task_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Close a task - requires project access"""
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access to the project (if task has a group)
    if task.GroupId:
        task_group = get_task_group(db, task.GroupId)
        if task_group and not check_project_access(db, task_group.ProjectId, current_user.Id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project"
            )
    
    # Update task to set IsClosed = True
    task_update = schemas.TaskUpdate(IsClosed=True)
    updated_task = update_task(db, task_id, task_update)
    
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return {"message": "Task closed successfully", "task": updated_task}

@router.post("/tasks/{task_id}/reopen")
async def reopen_task(
    task_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Reopen a closed task - requires project access"""
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access to the project (if task has a group)
    if task.GroupId:
        task_group = get_task_group(db, task.GroupId)
        if task_group and not check_project_access(db, task_group.ProjectId, current_user.Id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project"
            )
    
    # Update task to set IsClosed = False
    task_update = schemas.TaskUpdate(IsClosed=False)
    updated_task = update_task(db, task_id, task_update)
    
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return {"message": "Task reopened successfully", "task": updated_task}