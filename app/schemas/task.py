from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional 

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, examples=["Aprender FastAPI", "Aprender Python"])
    description: Optional[str] = Field(None, max_length=500, examples=["Ver tutoriales y practicar", "Ver documentación"])
    completed: bool = False

    @field_validator("title", "description", mode="before")
    @classmethod
    def trim_spaces(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

class TaskResponse(BaseModel):
    # ready for ORM
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., examples=["abc-123"])
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime