from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime, date
from typing import Optional, List


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