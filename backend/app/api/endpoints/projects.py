from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud.project import get_user_projects, get_project, create_project, update_project, get_projects
from app.crud.project_member import get_project_members, add_project_member, update_project_member_role, remove_project_member, get_project_member
from app.crud.user import get_user_by_id
from app.database import get_db

from app.auth import get_current_active_user, check_project_access, check_project_admin_access
from fastapi import APIRouter

router = APIRouter()

@router.get("/my")
async def get_my_projects(current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    projects = get_user_projects(db, current_user.Id)
    return projects

@router.get("/", response_model=List[schemas.Project])
async def get_all_projects(current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get all projects (accessible to all authenticated users)"""
    projects = get_projects(db)
    return projects

@router.get("/{project_id}", response_model=schemas.ProjectWithDetails)
async def get_project_details(project_id: int, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get project details - requires project access"""
    # Check if user has access to the project
    if not check_project_access(db, project_id, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project"
        )
    
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project

@router.post("/", response_model=schemas.Project)
async def create_new_project(
    project_data: schemas.ProjectCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new project"""
    project = create_project(db, project_data, current_user.Id)
    return project

@router.put("/{project_id}", response_model=schemas.Project)
async def update_existing_project(
    project_id: int,
    project_data: schemas.ProjectUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update project - requires admin access"""
    # Check if user has admin access to the project
    if not check_project_admin_access(db, project_id, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin access to this project"
        )
    
    project = update_project(db, project_id, project_data)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project

@router.post("/{project_id}/members", response_model=schemas.ProjectMember)
async def add_project_member_endpoint(
    project_id: int,
    member_data: schemas.ProjectMemberCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a member to project - requires admin access"""
    # Check if user has admin access to the project
    if not check_project_admin_access(db, project_id, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin access to this project"
        )
    
    # Check if the user to add exists
    user_to_add = get_user_by_id(db, member_data.MemnerId)
    if not user_to_add:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User to add not found"
        )
    
    # Check if user is already a member
    existing_member = get_project_member(db, project_id, member_data.MemnerId)
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this project"
        )
    
    member = add_project_member(db, project_id, member_data.MemnerId, member_data.Role)
    return member

@router.put("/{project_id}/members/{member_id}", response_model=schemas.ProjectMember)
async def update_project_member_role_endpoint(
    project_id: int,
    member_id: int,
    role_data: schemas.ProjectMemberBase,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update project member role - requires admin access"""
    # Check if user has admin access to the project
    if not check_project_admin_access(db, project_id, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin access to this project"
        )
    
    # Check if trying to modify owner's role (not allowed)
    project = get_project(db, project_id)
    if project and project.OwnerId == member_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify owner's role"
        )
    
    member = update_project_member_role(db, project_id, member_id, role_data.Role)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found"
        )
    
    return member

@router.delete("/{project_id}/members/{member_id}")
async def remove_project_member_endpoint(
    project_id: int,
    member_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove project member - requires admin access"""
    # Check if user has admin access to the project
    if not check_project_admin_access(db, project_id, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin access to this project"
        )
    
    # Check if trying to remove owner (not allowed)
    project = get_project(db, project_id)
    if project and project.OwnerId == member_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove owner from project"
        )
    
    # Check if trying to remove themselves (not allowed)
    if current_user.Id == member_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove yourself from project"
        )
    
    success = remove_project_member(db, project_id, member_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found"
        )
    
    return {"message": "Project member removed successfully"}

@router.get("/{project_id}/members", response_model=List[schemas.ProjectMemberWithUser])
async def get_project_members_endpoint(
    project_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get project members - requires project access"""
    # Check if user has access to the project
    if not check_project_access(db, project_id, current_user.Id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project"
        )
    
    members = get_project_members(db, project_id)
    return members
