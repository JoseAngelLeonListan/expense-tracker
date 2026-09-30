from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db
from schemas import ExpenseCreate, ExpenseRead

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