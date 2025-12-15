from sqlalchemy.orm import Session
from typing import Optional, List
import hashlib
from app import models
from app.schemas.users import UserCreate, UserUpdate


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

def create_user(db: Session, user: UserCreate) -> models.User:
    hashed_password = hashlib.sha256(user.Password.encode('utf-8')).hexdigest()
    db_user = models.User(
        Username=user.Username,
        Email=user.Email,
        PasswordHash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[models.User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)

    if 'Password' in update_data:
        update_data['PasswordHash'] = hashlib.sha256(update_data.pop('Password').encode('utf-8')).hexdigest()

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

def delete_user_permanent(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    if hashed_password != user.PasswordHash:
        return None
    return user