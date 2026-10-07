import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = (Index("ix_expenses_user_id_date", "user_id", "date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    category: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    date: Mapped[datetime.date]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))