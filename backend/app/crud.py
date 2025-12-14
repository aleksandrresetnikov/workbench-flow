from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
from passlib.context import CryptContext
from app import models, schemas
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ========== User CRUD ==========
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

# ========== StoreFile CRUD ==========
def get_store_file(db: Session, file_id: int) -> Optional[models.StoreFile]:
    return db.query(models.StoreFile).filter(models.StoreFile.Id == file_id).first()

def get_store_files(db: Session, skip: int = 0, limit: int = 100) -> List[models.StoreFile]:
    return db.query(models.StoreFile).offset(skip).limit(limit).all()

def create_store_file(db: Session, file: schemas.StoreFileCreate, author_id: int) -> models.StoreFile:
    db_file = models.StoreFile(**file.model_dump(), AuthorId=author_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

# ========== Project CRUD ==========
def get_project(db: Session, project_id: int) -> Optional[models.Project]:
    return db.query(models.Project).filter(
        models.Project.Id == project_id,
        models.Project.IsDeleted == False
    ).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[models.Project]:
    return db.query(models.Project).filter(
        models.Project.IsDeleted == False
    ).offset(skip).limit(limit).all()

def get_user_projects(db: Session, user_id: int) -> List[models.Project]:
    # Проекты, где пользователь владелец или участник
    return db.query(models.Project).join(models.ProjectMember).filter(
        and_(
            models.Project.IsDeleted == False,
            or_(
                models.Project.OwnerId == user_id,
                models.ProjectMember.MemnerId == user_id
            )
        )
    ).distinct().all()

def create_project(db: Session, project: schemas.ProjectCreate, owner_id: int) -> models.Project:
    db_project = models.Project(**project.model_dump(), OwnerId=owner_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Автоматически добавляем владельца как админа проекта
    add_project_member(db, db_project.Id, owner_id, schemas.ProjectRole.ADMIN)
    
    return db_project

def update_project(db: Session, project_id: int, project_update: schemas.ProjectUpdate) -> Optional[models.Project]:
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int) -> bool:
    db_project = get_project(db, project_id)
    if not db_project:
        return False
    
    db_project.IsDeleted = True
    db.commit()
    return True

# ========== ProjectMember CRUD ==========
def get_project_member(db: Session, project_id: int, member_id: int) -> Optional[models.ProjectMember]:
    return db.query(models.ProjectMember).filter(
        models.ProjectMember.ProjectId == project_id,
        models.ProjectMember.MemnerId == member_id
    ).first()

def get_project_members(db: Session, project_id: int) -> List[models.ProjectMember]:
    return db.query(models.ProjectMember).filter(
        models.ProjectMember.ProjectId == project_id
    ).all()

def add_project_member(db: Session, project_id: int, member_id: int, role: schemas.ProjectRole = schemas.ProjectRole.COMMON) -> models.ProjectMember:
    db_member = models.ProjectMember(
        ProjectId=project_id,
        MemnerId=member_id,
        Role=role.value
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def update_project_member_role(db: Session, project_id: int, member_id: int, role: schemas.ProjectRole) -> Optional[models.ProjectMember]:
    db_member = get_project_member(db, project_id, member_id)
    if not db_member:
        return None
    
    db_member.Role = role.value
    db.commit()
    db.refresh(db_member)
    return db_member

def remove_project_member(db: Session, project_id: int, member_id: int) -> bool:
    db_member = get_project_member(db, project_id, member_id)
    if not db_member:
        return False
    
    db.delete(db_member)
    db.commit()
    return True

# ========== TaskGroup CRUD ==========
def get_task_group(db: Session, group_id: int) -> Optional[models.TaskGroup]:
    return db.query(models.TaskGroup).filter(models.TaskGroup.Id == group_id).first()

def get_project_task_groups(db: Session, project_id: int) -> List[models.TaskGroup]:
    return db.query(models.TaskGroup).filter(
        models.TaskGroup.ProjectId == project_id
    ).all()

def create_task_group(db: Session, group: schemas.TaskGroupCreate) -> models.TaskGroup:
    db_group = models.TaskGroup(**group.model_dump())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def update_task_group(db: Session, group_id: int, name: str) -> Optional[models.TaskGroup]:
    db_group = get_task_group(db, group_id)
    if not db_group:
        return None
    
    db_group.Name = name
    db.commit()
    db.refresh(db_group)
    return db_group

def delete_task_group(db: Session, group_id: int) -> bool:
    db_group = get_task_group(db, group_id)
    if not db_group:
        return False
    
    db.delete(db_group)
    db.commit()
    return True

# ========== TaskState CRUD ==========
def get_task_state(db: Session, state_id: int) -> Optional[models.TaskState]:
    return db.query(models.TaskState).filter(models.TaskState.Id == state_id).first()

def get_task_states(db: Session) -> List[models.TaskState]:
    return db.query(models.TaskState).all()

def create_task_state(db: Session, state: schemas.TaskStateCreate) -> models.TaskState:
    db_state = models.TaskState(**state.model_dump())
    db.add(db_state)
    db.commit()
    db.refresh(db_state)
    return db_state

# ========== Task CRUD ==========
def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    return db.query(models.Task).filter(models.Task.Id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[models.Task]:
    return db.query(models.Task).offset(skip).limit(limit).all()

def get_user_tasks(db: Session, user_id: int, closed: Optional[bool] = None) -> List[models.Task]:
    query = db.query(models.Task).filter(
        or_(
            models.Task.AuthorId == user_id,
            models.Task.TargetId == user_id
        )
    )
    
    if closed is not None:
        query = query.filter(models.Task.IsClosed == closed)
    
    return query.all()

def get_project_tasks(db: Session, project_id: int, closed: Optional[bool] = None) -> List[models.Task]:
    # Получаем все задачи через группы проекта
    query = db.query(models.Task).join(models.TaskGroup).filter(
        models.TaskGroup.ProjectId == project_id
    )
    
    if closed is not None:
        query = query.filter(models.Task.IsClosed == closed)
    
    return query.all()

def create_task(db: Session, task: schemas.TaskCreate, author_id: int) -> models.Task:
    db_task = models.Task(**task.model_dump(), AuthorId=author_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate) -> Optional[models.Task]:
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int) -> bool:
    db_task = get_task(db, task_id)
    if not db_task:
        return False
    
    db.delete(db_task)
    db.commit()
    return True

# ========== TaskFile CRUD ==========
def get_task_file(db: Session, task_id: int, file_id: int) -> Optional[models.TaskFile]:
    return db.query(models.TaskFile).filter(
        models.TaskFile.TaskId == task_id,
        models.TaskFile.FileId == file_id
    ).first()

def get_task_files(db: Session, task_id: int) -> List[models.TaskFile]:
    return db.query(models.TaskFile).filter(
        models.TaskFile.TaskId == task_id
    ).all()

def add_task_file(db: Session, task_id: int, file_id: int) -> models.TaskFile:
    db_task_file = models.TaskFile(TaskId=task_id, FileId=file_id)
    db.add(db_task_file)
    db.commit()
    db.refresh(db_task_file)
    return db_task_file

def remove_task_file(db: Session, task_id: int, file_id: int) -> bool:
    db_task_file = get_task_file(db, task_id, file_id)
    if not db_task_file:
        return False
    
    db.delete(db_task_file)
    db.commit()
    return True

# ========== Comment CRUD ==========
def get_comment(db: Session, comment_id: int) -> Optional[models.Comment]:
    return db.query(models.Comment).filter(models.Comment.Id == comment_id).first()

def get_task_comments(db: Session, task_id: int) -> List[models.Comment]:
    return db.query(models.Comment).filter(
        models.Comment.TaskId == task_id
    ).order_by(models.Comment.CreateDate).all()

def create_comment(db: Session, comment: schemas.CommentCreate, author_id: int) -> models.Comment:
    db_comment = models.Comment(**comment.model_dump(), AuthorId=author_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def update_comment(db: Session, comment_id: int, text: str) -> Optional[models.Comment]:
    db_comment = get_comment(db, comment_id)
    if not db_comment:
        return None
    
    db_comment.Text = text
    db.commit()
    db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, comment_id: int) -> bool:
    db_comment = get_comment(db, comment_id)
    if not db_comment:
        return False
    
    db.delete(db_comment)
    db.commit()
    return True

# ========== Pin CRUD ==========
def get_pin(db: Session, user_id: int, task_id: int) -> Optional[models.Pin]:
    return db.query(models.Pin).filter(
        models.Pin.UserId == user_id,
        models.Pin.TaskId == task_id
    ).first()

def get_user_pins(db: Session, user_id: int) -> List[models.Pin]:
    return db.query(models.Pin).filter(
        models.Pin.UserId == user_id
    ).all()

def create_pin(db: Session, user_id: int, task_id: int) -> models.Pin:
    db_pin = models.Pin(UserId=user_id, TaskId=task_id)
    db.add(db_pin)
    db.commit()
    db.refresh(db_pin)
    return db_pin

def delete_pin(db: Session, user_id: int, task_id: int) -> bool:
    db_pin = get_pin(db, user_id, task_id)
    if not db_pin:
        return False
    
    db.delete(db_pin)
    db.commit()
    return True