from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from app import models, schemas
from app.database import get_db
import hashlib

from app.schemas import ProjectRole

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

bearer_scheme = HTTPBearer()

def verify_password(plain_password, hashed_password):
    try:
        # Хешируем введенный пароль и сравниваем с хранимым хешем
        input_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
        return input_hash == hashed_password
    except Exception:
        return False

def get_password_hash(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.Username == username).first()
    if not user:
        return False
    if not verify_password(password, user.PasswordHash):
        return False
    return user

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.Username == username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if current_user.IsDeleted:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def check_project_access(db: Session, project_id: int, user_id: int) -> bool:
    """Check if user has access to the project (is owner or member)"""
    from app.crud.project import get_project
    from app.crud.project_member import get_project_member
    
    project = get_project(db, project_id)
    if not project:
        return False
    
    # Check if user is owner
    if project.OwnerId == user_id:
        return True
    
    # Check if user is member
    member = get_project_member(db, project_id, user_id)
    return member is not None


def check_project_admin_access(db: Session, project_id: int, user_id: int) -> bool:
    """Check if user has admin access to the project (is owner or admin member)"""
    from app.crud.project import get_project
    from app.crud.project_member import get_project_member
    
    project = get_project(db, project_id)
    if not project:
        return False
    
    # Check if user is owner
    if project.OwnerId == user_id:
        return True
    
    # Check if user is admin member
    member = get_project_member(db, project_id, user_id)
    if member and member.Role == ProjectRole.ADMIN.value:
        return True
    
    return False