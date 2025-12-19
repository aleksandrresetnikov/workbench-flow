from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from app.database import Base
import enum


class AccessLevel(str, enum.Enum):
    COMMON = "Common"
    ADMIN = "Admin"

class User(Base):
    __tablename__ = 'Users'

    Id = Column('Id', Integer, primary_key=True, index=True)
    Username = Column('Username', String(50), nullable=False, index=True)
    Email = Column('Email', String(75), nullable=False, index=True)
    PasswordHash = Column('PasswordHash', String(125), nullable=False)
    CreateDate = Column('CreateDate', DateTime(timezone=True), server_default=func.now(), nullable=False)
    IsDeleted = Column('IsDeleted', Boolean, default=False, nullable=False)
    OtpId = Column('OtpId', Integer, ForeignKey('Otps.Id'), nullable=True)

    # Relationships
    projects_owned = relationship("Project", back_populates="owner", foreign_keys="Project.OwnerId")
    store_files = relationship("StoreFile", back_populates="author")
    tasks_authored = relationship("Task", back_populates="author", foreign_keys="Task.AuthorId")
    tasks_targeted = relationship("Task", back_populates="target", foreign_keys="Task.TargetId")
    comments = relationship("Comment", back_populates="author")
    project_memberships = relationship("ProjectMember", back_populates="member")
    pins = relationship("Pin", back_populates="user")
    otp = relationship("Otp", back_populates="user")
    marks = relationship("Mark", back_populates="author")

class Otp(Base):
    __tablename__ = 'Otps'

    Id = Column('Id', Integer, primary_key=True, index=True)
    Code = Column('Code', String(6), nullable=False)
    CreateDate = Column('CreateDate', DateTime(timezone=True), server_default=func.now(), nullable=False)
    Attempts = Column('Attempts', Integer, default=5, nullable=False)

    # Relationships
    user = relationship("User", back_populates="otp")

class StoreFile(Base):
    __tablename__ = 'StoreFiles'
    
    Id = Column('Id', Integer, primary_key=True, index=True)
    SourceName = Column('SourceName', String(150), nullable=False)
    TagName = Column('TagName', String(150), nullable=False)
    AuthorId = Column('AuthorId', Integer, ForeignKey('Users.Id', ondelete='SET NULL'))
    CreateDate = Column('CreateDate', DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="store_files")
    project_logos = relationship("Project", back_populates="logo")
    task_files = relationship("TaskFile", back_populates="file")

class Project(Base):
    __tablename__ = 'Projects'
    
    Id = Column('Id', Integer, primary_key=True, index=True)
    Name = Column('Name', String(50), nullable=False)
    Description = Column('Description', String(512))
    CreateDate = Column('CreateDate', DateTime(timezone=True), server_default=func.now(), nullable=False)
    IsDeleted = Column('IsDeleted', Boolean, default=False, nullable=False)
    OwnerId = Column('OwnerId', Integer, ForeignKey('Users.Id', ondelete='SET NULL'))
    ProjectLogoId = Column('ProjectLogoId', Integer, ForeignKey('StoreFiles.Id', ondelete='SET NULL'))
    
    # Relationships
    owner = relationship("User", back_populates="projects_owned", foreign_keys=[OwnerId])
    logo = relationship("StoreFile", back_populates="project_logos")
    task_groups = relationship("TaskGroup", back_populates="project", cascade="all, delete-orphan")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")


class ProjectRoleEntity(Base):
    __tablename__ = 'ProjectRoles'

    Id = Column('Id', Integer, primary_key=True, index=True)
    ProjectId = Column('ProjectId', Integer, ForeignKey('Projects.Id', ondelete='CASCADE'), index=True)
    RoleName = Column('RoleName', String(96), nullable=False)
    CreateDate = Column('CreateDate', DateTime(timezone=True), server_default=func.now(), nullable=False)
    Rate = Column('Rate', Integer)

    # Relationships
    project = relationship("Project")
    members = relationship("ProjectMember", back_populates="role")

class ProjectMember(Base):
    __tablename__ = 'ProjectMembers'
    
    Id = Column('Id', Integer, primary_key=True, index=True)
    ProjectId = Column('ProjectId', Integer, ForeignKey('Projects.Id', ondelete='CASCADE'), index=True)
    MemnerId = Column('MemnerId', Integer, ForeignKey('Users.Id', ondelete='CASCADE'), index=True)
    AccessLevel = Column('AccessLevel', String(10), default=AccessLevel.COMMON.value, nullable=False)
    RoleId = Column('RoleId', Integer, ForeignKey('ProjectRoles.Id', ondelete='SET NULL'), nullable=True)
    CreateDate = Column('CreateDate', DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="members")
    member = relationship("User", back_populates="project_memberships")
    role = relationship("ProjectRoleEntity", back_populates="members")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('ProjectId', 'MemnerId', name='UniqueProjectMembers'),
        CheckConstraint('"AccessLevel" IN (\'Common\', \'Admin\')', name='ValidAccessLevels'),
    )

class TaskGroup(Base):
    __tablename__ = 'TaskGroups'
    
    Id = Column('Id', Integer, primary_key=True, index=True)
    Name = Column('Name', String(50), nullable=False)
    CreateDate = Column('CreateDate', DateTime(timezone=True), server_default=func.now(), nullable=False)
    ProjectId = Column('ProjectId', Integer, ForeignKey('Projects.Id', ondelete='CASCADE'), index=True)
    
    # Relationships
    project = relationship("Project", back_populates="task_groups")
    tasks = relationship("Task", back_populates="group", cascade="all, delete-orphan")

class TaskState(Base):
    __tablename__ = 'TaskStates'
    
    Id = Column('Id', Integer, primary_key=True, index=True)
    Name = Column('Name', String(50), nullable=False)
    
    # Relationships
    tasks = relationship("Task", back_populates="state")

class Task(Base):
    __tablename__ = 'Tasks'
    
    Id = Column('Id', Integer, primary_key=True, index=True)
    Title = Column('Title', String(75), nullable=False)
    Text = Column('Text', Text, nullable=False)
    AuthorId = Column('AuthorId', Integer, ForeignKey('Users.Id', ondelete='SET NULL'), index=True)
    TargetId = Column('TargetId', Integer, ForeignKey('Users.Id', ondelete='SET NULL'), index=True)
    StateId = Column('StateId', Integer, ForeignKey('TaskStates.Id', ondelete='SET NULL'), default=0)
    GroupId = Column('GroupId', Integer, ForeignKey('TaskGroups.Id', ondelete='CASCADE'), index=True)
    CreateDate = Column('CreateDate', DateTime(timezone=True), server_default=func.now(), nullable=False)
    IsClosed = Column('IsClosed', Boolean, default=False, nullable=False, index=True)
    DeadLine = Column('DeadLine', Date)
    
    # Relationships
    author = relationship("User", back_populates="tasks_authored", foreign_keys=[AuthorId])
    target = relationship("User", back_populates="tasks_targeted", foreign_keys=[TargetId])
    state = relationship("TaskState", back_populates="tasks")
    group = relationship("TaskGroup", back_populates="tasks")
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    task_files = relationship("TaskFile", back_populates="task", cascade="all, delete-orphan")
    pins = relationship("Pin", back_populates="task", cascade="all, delete-orphan")
    marks = relationship("Mark", back_populates="task", cascade="all, delete-orphan")


class Mark(Base):
    __tablename__ = 'Marks'

    Id = Column('Id', Integer, primary_key=True, index=True)
    TargetTask = Column('TargetTask', Integer, ForeignKey('Tasks.Id', ondelete='CASCADE'), index=True)
    MarkedById = Column('MarkedById', Integer, ForeignKey('Users.Id', ondelete='CASCADE'), index=True)
    Description = Column('Description', Text, nullable=False)
    Rate = Column('Rate', Integer, nullable=True)
    CreateDate = Column('CreateDate', DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint('"Rate" >= 0 AND "Rate" <= 10', name='ValidRates'),
    )

    # Relationships
    task = relationship("Task", back_populates="marks")
    author = relationship("User", back_populates="marks")

class TaskFile(Base):
    __tablename__ = 'TaskFiles'
    
    Id = Column('Id', Integer, primary_key=True, index=True)
    FileId = Column('FileId', Integer, ForeignKey('StoreFiles.Id', ondelete='CASCADE'), index=True)
    TaskId = Column('TaskId', Integer, ForeignKey('Tasks.Id', ondelete='CASCADE'), index=True)
    
    # Relationships
    file = relationship("StoreFile", back_populates="task_files")
    task = relationship("Task", back_populates="task_files")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('FileId', 'TaskId', name='UniqueTaskFiles'),
    )

class Comment(Base):
    __tablename__ = 'Comments'
    
    Id = Column('Id', Integer, primary_key=True, index=True)
    Text = Column('Text', Text, nullable=False)
    AuthorId = Column('AuthorId', Integer, ForeignKey('Users.Id', ondelete='CASCADE'), index=True)
    TaskId = Column('TaskId', Integer, ForeignKey('Tasks.Id', ondelete='CASCADE'), index=True)
    CreateDate = Column('CreateDate', DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="comments")
    task = relationship("Task", back_populates="comments")

class Pin(Base):
    __tablename__ = 'Pins'
    
    Id = Column('Id', Integer, primary_key=True, index=True)
    UserId = Column('UserId', Integer, ForeignKey('Users.Id', ondelete='CASCADE'), index=True)
    TaskId = Column('TaskId', Integer, ForeignKey('Tasks.Id', ondelete='CASCADE'), index=True)
    
    # Relationships
    user = relationship("User", back_populates="pins")
    task = relationship("Task", back_populates="pins")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('UserId', 'TaskId', name='UniquePins'),
    )