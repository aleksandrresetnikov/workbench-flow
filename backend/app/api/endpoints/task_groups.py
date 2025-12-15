from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud.task_group import get_task_group, get_project_task_groups, create_task_group, update_task_group, delete_task_group
from app.crud.project import get_project
from app.database import get_db

from app.auth import get_current_active_user, check_project_access, check_project_admin_access
from app import schemas, models

router = APIRouter()

@router.get("/projects/{project_id}/groups", response_model=List[schemas.TaskGroup])
async def get_task_groups_for_project(
    project_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all task groups for a project - requires project access"""
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
    
    task_groups = get_project_task_groups(db, project_id)
    return task_groups

@router.get("/groups/{group_id}", response_model=schemas.TaskGroup)
async def get_single_task_group(
    group_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a single task group - requires project access"""
    task_group = get_task_group(db, group_id)
    if not task_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task group not found"
        )
    
    # Check if user has access to the project
    if not check_project_access(db, task_group.ProjectId, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project"
        )
    
    return task_group

@router.post("/projects/{project_id}/groups", response_model=schemas.TaskGroup)
async def create_new_task_group(
    project_id: int,
    group_data: schemas.TaskGroupCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new task group - requires project access"""
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
    
    # Create task group with project_id from path parameter
    task_group_data = schemas.TaskGroupBase(Name=group_data.Name, ProjectId=project_id)
    task_group = create_task_group(db, task_group_data)
    return task_group

@router.put("/groups/{group_id}", response_model=schemas.TaskGroup)
async def update_existing_task_group(
    group_id: int,
    name: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update task group name - requires project access"""
    task_group = get_task_group(db, group_id)
    if not task_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task group not found"
        )
    
    # Check if user has access to the project
    if not check_project_access(db, task_group.ProjectId, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project"
        )
    
    updated_group = update_task_group(db, group_id, name)
    if not updated_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task group not found"
        )
    
    return updated_group

@router.delete("/groups/{group_id}")
async def delete_existing_task_group(
    group_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete task group - requires project access"""
    task_group = get_task_group(db, group_id)
    if not task_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task group not found"
        )
    
    # Check if user has access to the project
    if not check_project_access(db, task_group.ProjectId, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project"
        )
    
    success = delete_task_group(db, group_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task group not found"
        )
    
    return {"message": "Task group deleted successfully"}