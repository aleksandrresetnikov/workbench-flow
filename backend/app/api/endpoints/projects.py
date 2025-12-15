from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.project import get_user_projects
from app.database import get_db

from app.auth import authenticate_user, create_access_token, get_current_active_user
from fastapi import APIRouter
from app import schemas, models

router = APIRouter()

@router.get("/my")
async def get_my_projects(current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    projects = get_user_projects(db, current_user.Id)
    return projects