from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime, date
from typing import Optional, List

class OtpBase(BaseModel):
    Code: str

class OtpCreate(OtpBase):
    pass

class Otp(OtpBase):
    Id: int
    CreateDate: datetime
    Attempts: int

    model_config = ConfigDict(from_attributes=True)

class OtpConfirm(BaseModel):
    email: EmailStr
    code: str

class OtpResend(BaseModel):
    email: EmailStr