import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ExpenseCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    category: str = Field(min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=200)
    date: datetime.date


class ExpenseRead(ExpenseCreate):
    id: int
    # En la API el importe sale como número JSON (12.5), no como texto.
    amount: float
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class CategoryTotal(BaseModel):
    category: str
    total: float


class MonthTotal(BaseModel):
    month: str  # formato AAAA-MM
    total: float


class Summary(BaseModel):
    total: float
    count: int
    by_category: list[CategoryTotal]
    by_month: list[MonthTotal]