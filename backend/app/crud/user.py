from sqlalchemy.orm import Session
from typing import Optional, List
from passlib.context import CryptContext
from app import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(
        models.User.Id == user_id,
        models.User.IsDeleted == False
    ).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(
        models.User.Email == email,
        models.User.IsDeleted == False
    ).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(
        models.User.Username == username,
        models.User.IsDeleted == False
    ).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).filter(
        models.User.IsDeleted == False
    ).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = pwd_context.hash(user.Password)
    db_user = models.User(
        Username=user.Username,
        Email=user.Email,
        PasswordHash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    if 'Password' in update_data:
        update_data['PasswordHash'] = pwd_context.hash(update_data.pop('Password'))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db_user.IsDeleted = True
    db.commit()
    return True

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not pwd_context.verify(password, user.PasswordHash):
        return None
    return user