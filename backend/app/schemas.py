from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime, date
from typing import Optional, List
from enum import Enum

# Enums
class ProjectRole(str, Enum):
    COMMON = "Common"
    ADMIN = "Admin"

# Base Schemas
class UserBase(BaseModel):
    Username: str
    Email: EmailStr

class UserCreate(UserBase):
    Password: str

class UserUpdate(BaseModel):
    Username: Optional[str] = None
    Email: Optional[EmailStr] = None
    Password: Optional[str] = None

class User(UserBase):
    Id: int
    CreateDate: datetime
    IsDeleted: bool
    
    model_config = ConfigDict(from_attributes=True)

class UserWithToken(User):
    access_token: str
    token_type: str = "bearer"

class StoreFileBase(BaseModel):
    SourceName: str
    TagName: str

class StoreFileCreate(StoreFileBase):
    pass

class StoreFile(StoreFileBase):
    Id: int
    AuthorId: Optional[int] = None
    CreateDate: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ProjectBase(BaseModel):
    Name: str
    Description: Optional[str] = None
    ProjectLogoId: Optional[int] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    Name: Optional[str] = None
    Description: Optional[str] = None
    ProjectLogoId: Optional[int] = None
    IsDeleted: Optional[bool] = None

class Project(ProjectBase):
    Id: int
    OwnerId: Optional[int] = None
    CreateDate: datetime
    IsDeleted: bool
    
    model_config = ConfigDict(from_attributes=True)

class ProjectWithDetails(Project):
    owner: Optional[User] = None
    logo: Optional[StoreFile] = None
    members: List['ProjectMember'] = []
    task_groups: List['TaskGroup'] = []

class ProjectMemberBase(BaseModel):
    Role: ProjectRole = ProjectRole.COMMON

class ProjectMemberCreate(ProjectMemberBase):
    MemnerId: int

class ProjectMember(ProjectMemberBase):
    Id: int
    ProjectId: int
    MemnerId: int
    CreateDate: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ProjectMemberWithUser(ProjectMember):
    member: User

class TaskGroupBase(BaseModel):
    Name: str
    ProjectId: int

class TaskGroupCreate(TaskGroupBase):
    pass

class TaskGroup(TaskGroupBase):
    Id: int
    CreateDate: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TaskGroupWithTasks(TaskGroup):
    tasks: List['Task'] = []

class TaskStateBase(BaseModel):
    Name: str

class TaskStateCreate(TaskStateBase):
    pass

class TaskState(TaskStateBase):
    Id: int
    
    model_config = ConfigDict(from_attributes=True)

class TaskBase(BaseModel):
    Title: str
    Text: str
    TargetId: Optional[int] = None
    StateId: Optional[int] = 0
    GroupId: Optional[int] = None
    DeadLine: Optional[date] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    Title: Optional[str] = None
    Text: Optional[str] = None
    TargetId: Optional[int] = None
    StateId: Optional[int] = None
    GroupId: Optional[int] = None
    IsClosed: Optional[bool] = None
    DeadLine: Optional[date] = None

class Task(TaskBase):
    Id: int
    AuthorId: Optional[int] = None
    CreateDate: datetime
    IsClosed: bool
    
    model_config = ConfigDict(from_attributes=True)

class TaskWithDetails(Task):
    author: Optional[User] = None
    target: Optional[User] = None
    state: Optional[TaskState] = None
    group: Optional[TaskGroup] = None
    comments: List['Comment'] = []
    task_files: List['TaskFileWithFile'] = []
    pins: List['Pin'] = []

class TaskFileBase(BaseModel):
    FileId: int
    TaskId: int

class TaskFileCreate(TaskFileBase):
    pass

class TaskFile(TaskFileBase):
    Id: int
    
    model_config = ConfigDict(from_attributes=True)

class TaskFileWithFile(TaskFile):
    file: StoreFile

class CommentBase(BaseModel):
    Text: str
    TaskId: int

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    Id: int
    AuthorId: Optional[int] = None
    CreateDate: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CommentWithAuthor(Comment):
    author: Optional[User] = None

class PinBase(BaseModel):
    TaskId: int

class PinCreate(PinBase):
    pass

class Pin(PinBase):
    Id: int
    UserId: int
    
    model_config = ConfigDict(from_attributes=True)

class PinWithTask(Pin):
    task: Task

# Update forward references
ProjectWithDetails.model_rebuild()
ProjectMemberWithUser.model_rebuild()
TaskGroupWithTasks.model_rebuild()
TaskWithDetails.model_rebuild()
TaskFileWithFile.model_rebuild()
CommentWithAuthor.model_rebuild()
PinWithTask.model_rebuild()