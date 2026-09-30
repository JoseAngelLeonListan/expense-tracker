import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0)
    category: str = Field(min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=200)
    date: datetime.date


class ExpenseRead(ExpenseCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)