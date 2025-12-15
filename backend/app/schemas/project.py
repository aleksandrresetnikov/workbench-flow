from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime, date
from typing import Optional, List
from enum import Enum

from app.schemas.store_files import StoreFile
from app.schemas.users import User


class ProjectRole(str, Enum):
    OWNER = "Owner"
    COMMON = "Common"
    ADMIN = "Admin"


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

# Update forward references
ProjectWithDetails.model_rebuild()
ProjectMemberWithUser.model_rebuild()