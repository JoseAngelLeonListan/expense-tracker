import datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session
from config import settings

import models
from database import Base, engine, get_db
from schemas import (
    CategoryTotal,
    ExpenseCreate,
    ExpenseRead,
    MonthTotal,
    Summary,
    Token,
    UserCreate,
    UserRead,
)
from security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

from database import get_db

app = FastAPI(title="Expense Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/register", response_model=UserRead, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    email = user.email.lower()
    existing = db.scalar(select(models.User).where(models.User.email == email))
    if existing is not None:
        raise HTTPException(status_code=409, detail="El email ya está registrado")
    db_user = models.User(email=email, hashed_password=hash_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    email = form_data.username.lower()
    user = db.scalar(select(models.User).where(models.User.email == email))
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


@app.get("/me", response_model=UserRead)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user


def get_own_expense(
    db: Session, expense_id: int, user: models.User
) -> models.Expense:
    db_expense = db.get(models.Expense, expense_id)
    if db_expense is None or db_expense.user_id != user.id:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    return db_expense


@app.post("/expenses", response_model=ExpenseRead, status_code=201)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_expense = models.Expense(**expense.model_dump(), user_id=current_user.id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def expense_conditions(
    user: models.User,
    date_from: datetime.date | None,
    date_to: datetime.date | None,
    category: str | None,
) -> list:
    """Condiciones WHERE comunes: siempre los gastos del usuario, más los filtros opcionales."""
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=422,
            detail="La fecha 'desde' no puede ser posterior a 'hasta'",
        )
    conditions = [models.Expense.user_id == user.id]
    if date_from:
        conditions.append(models.Expense.date >= date_from)
    if date_to:
        conditions.append(models.Expense.date <= date_to)
    if category:
        conditions.append(models.Expense.category == category)
    return conditions


@app.get("/expenses", response_model=list[ExpenseRead])
def list_expenses(
    date_from: datetime.date | None = Query(default=None),
    date_to: datetime.date | None = Query(default=None),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    conditions = expense_conditions(current_user, date_from, date_to, category)
    query = (
        select(models.Expense)
        .where(*conditions)
        .order_by(models.Expense.date.desc(), models.Expense.id.desc())
    )
    return db.scalars(query).all()


@app.get("/summary", response_model=Summary)
def read_summary(
    date_from: datetime.date | None = Query(default=None),
    date_to: datetime.date | None = Query(default=None),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    conditions = expense_conditions(current_user, date_from, date_to, category)
    amount_sum = func.sum(models.Expense.amount)

    total, count = db.execute(
        select(func.coalesce(amount_sum, 0), func.count()).where(*conditions)
    ).one()

    by_category = db.execute(
        select(models.Expense.category, amount_sum)
        .where(*conditions)
        .group_by(models.Expense.category)
        .order_by(amount_sum.desc(), models.Expense.category)
    ).all()

    year = extract("year", models.Expense.date)
    month = extract("month", models.Expense.date)
    by_month = db.execute(
        select(year, month, amount_sum)
        .where(*conditions)
        .group_by(year, month)
        .order_by(year, month)
    ).all()

    return Summary(
        total=round(total, 2),
        count=count,
        by_category=[
            CategoryTotal(category=name, total=round(value, 2))
            for name, value in by_category
        ],
        by_month=[
            MonthTotal(month=f"{int(y):04d}-{int(mo):02d}", total=round(value, 2))
            for y, mo, value in by_month
        ],
    )


@app.get("/categories", response_model=list[str])
def list_categories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = (
        select(models.Expense.category)
        .where(models.Expense.user_id == current_user.id)
        .distinct()
        .order_by(models.Expense.category)
    )
    return db.scalars(query).all()


@app.put("/expenses/{expense_id}", response_model=ExpenseRead)
def update_expense(
    expense_id: int,
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_expense = get_own_expense(db, expense_id, current_user)
    for field, value in expense.model_dump().items():
        setattr(db_expense, field, value)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_expense = get_own_expense(db, expense_id, current_user)
    db.delete(db_expense)
    db.commit()