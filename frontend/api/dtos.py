from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

# ========== Auth DTOs ==========
class UserCreateDTO(BaseModel):
    Username: str
    Email: str
    Password: str
    FirstName: Optional[str] = None
    LastName: Optional[str] = None

class UserLoginDTO(BaseModel):
    username: str
    password: str

class OtpConfirmDTO(BaseModel):
    email: str
    code: str

class OtpResendDTO(BaseModel):
    email: str

class TokenDTO(BaseModel):
    access_token: str
    token_type: str

class UserDTO(BaseModel):
    Id: int
    Username: str
    Email: str
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    CreateDate: Optional[datetime] = None
    IsDeleted: bool

# ========== User DTOs ==========
class UserUpdateDTO(BaseModel):
    Username: Optional[str] = None
    Email: Optional[str] = None
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    Password: Optional[str] = None

# ========== Project DTOs ==========
class ProjectCreateDTO(BaseModel):
    Name: str
    Description: Optional[str] = None

class ProjectUpdateDTO(BaseModel):
    Name: Optional[str] = None
    Description: Optional[str] = None

class ProjectDTO(BaseModel):
    Id: int
    Name: str
    Description: Optional[str] = None
    ProjectLogoId: Optional[int] = None
    OwnerId: Optional[int] = None
    CreateDate: datetime
    IsDeleted: bool

class ProjectWithDetailsDTO(ProjectDTO):
    # Совпадает с backend ProjectWithDetails:
    # owner: Optional[User] = None
    # logo: Optional[StoreFile] = None
    # members: List[ProjectMember] = []
    # task_groups: List[TaskGroup] = []
    owner: Optional[UserDTO] = None
    members: List["ProjectMemberDTO"] = []
    task_groups: List["TaskGroupDTO"] = []
    roles: List["ProjectRoleDTO"] = []

class ProjectMemberCreateDTO(BaseModel):
    MemnerId: int
    AccessLevel: str
    RoleId: Optional[int] = None

class ProjectMemberBaseDTO(BaseModel):
    AccessLevel: str
    RoleId: Optional[int] = None

class ProjectMemberDTO(BaseModel):
    Id: int
    ProjectId: int
    MemnerId: int
    AccessLevel: str
    RoleId: Optional[int] = None
    CreateDate: datetime

class ProjectMemberWithUserDTO(ProjectMemberDTO):
    member: UserDTO


class ProjectRoleCreateDTO(BaseModel):
    RoleName: str
    Rate: Optional[int] = None


class ProjectRoleUpdateDTO(BaseModel):
    RoleName: Optional[str] = None
    Rate: Optional[int] = None


class ProjectRoleDTO(BaseModel):
    Id: int
    ProjectId: int
    RoleName: str
    Rate: Optional[int] = None
    CreateDate: datetime

# ========== Task Group DTOs ==========
class TaskGroupCreateDTO(BaseModel):
    Name: str

class TaskGroupDTO(BaseModel):
    Id: int
    Name: str
    ProjectId: int
    CreateDate: datetime

# ========== Task DTOs ==========
class TaskCreateDTO(BaseModel):
    Name: str
    Description: Optional[str] = None
    GroupId: Optional[int] = None
    Status: Optional[str] = None

class TaskDTO(BaseModel):
    Id: int
    Name: str
    Description: Optional[str] = None
    ProjectId: int
    GroupId: Optional[int] = None
    Status: str
    CreatedAt: datetime

# ========== File DTOs ==========
class FileUploadDTO(BaseModel):
    ProjectId: int
    FilePath: str

class FileDTO(BaseModel):
    Id: int
    ProjectId: int
    FileName: str
    FilePath: str
    FileSize: int
    UploadedAt: datetime

# ========== Response DTOs ==========
class APIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    detail: str
