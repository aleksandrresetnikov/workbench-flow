from pydantic import BaseModel, ConfigDict

from app.schemas.tasks import Task


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

PinWithTask.model_rebuild()