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
    IsActive: bool
    CreatedAt: datetime

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
    OwnerId: int
    CreatedAt: datetime

class ProjectWithDetailsDTO(ProjectDTO):
    Owner: UserDTO

class ProjectMemberCreateDTO(BaseModel):
    MemnerId: int
    Role: str

class ProjectMemberBaseDTO(BaseModel):
    Role: str

class ProjectMemberDTO(BaseModel):
    Id: int
    ProjectId: int
    UserId: int
    Role: str
    CreatedAt: datetime

class ProjectMemberWithUserDTO(ProjectMemberDTO):
    User: UserDTO

# ========== Task Group DTOs ==========
class TaskGroupCreateDTO(BaseModel):
    Name: str

class TaskGroupDTO(BaseModel):
    Id: int
    Name: str
    ProjectId: int
    CreatedAt: datetime

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