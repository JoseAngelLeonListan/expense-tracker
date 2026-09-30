from fastapi import FastAPI

from database import Base, engine
import models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API")


@app.get("/health")
def health():
    return {"status": "ok"}
