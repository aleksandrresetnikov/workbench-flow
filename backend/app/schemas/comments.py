from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime, date
from typing import Optional, List

from app.schemas.users import User


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

CommentWithAuthor.model_rebuild()