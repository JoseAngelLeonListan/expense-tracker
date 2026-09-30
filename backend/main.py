from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db
from schemas import ExpenseCreate, ExpenseRead, UserCreate, UserRead
from security import hash_password

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/expenses", response_model=ExpenseRead, status_code=201)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = models.Expense(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@app.get("/expenses", response_model=list[ExpenseRead])
def list_expenses(db: Session = Depends(get_db)):
    query = select(models.Expense).order_by(models.Expense.date.desc())
    return db.scalars(query).all()

@app.put("/expenses/{expense_id}", response_model=ExpenseRead)
def update_expense(
    expense_id: int, expense: ExpenseCreate, db: Session = Depends(get_db)
):
    db_expense = db.get(models.Expense, expense_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    for field, value in expense.model_dump().items():
        setattr(db_expense, field, value)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    db_expense = db.get(models.Expense, expense_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    db.delete(db_expense)
    db.commit()

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