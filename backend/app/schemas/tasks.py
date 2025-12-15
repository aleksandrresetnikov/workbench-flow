from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime, date
from typing import Optional, List

from app.schemas.store_files import StoreFile
from app.schemas.users import User


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

TaskGroupWithTasks.model_rebuild()
TaskWithDetails.model_rebuild()
TaskFileWithFile.model_rebuild()