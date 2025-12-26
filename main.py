from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ArmorIQ MCP Server")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/account/create")
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    acc = models.Account(
        name=account.name,
        balance=account.initial_balance
    )
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return {"account_id": acc.id}

@app.post("/account/deposit/{account_id}")
def deposit(account_id: int, amt: schemas.Amount, db: Session = Depends(get_db)):
    acc = db.query(models.Account).get(account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    acc.balance += amt.amount

    txn = models.Transaction(
        account_id=account_id,
        type="deposit",
        amount=amt.amount
    )
    db.add(txn)

    db.commit()
    return {"balance": acc.balance}

@app.post("/account/withdraw/{account_id}")
def withdraw(account_id: int, amt: schemas.Amount, db: Session = Depends(get_db)):
    acc = db.query(models.Account).get(account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    if acc.balance < amt.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    acc.balance -= amt.amount

    txn = models.Transaction(
        account_id=account_id,
        type="withdraw",
        amount=amt.amount
    )
    db.add(txn)

    db.commit()
    return {"balance": acc.balance}

@app.get("/account/balance/{account_id}")
def get_balance(account_id: int, db: Session = Depends(get_db)):
    acc = db.query(models.Account).get(account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"balance": acc.balance}

@app.get("/account/transactions/{account_id}")
def transaction_history(account_id: int, db: Session = Depends(get_db)):
    txns = (
        db.query(models.Transaction)
        .filter(models.Transaction.account_id == account_id)
        .order_by(models.Transaction.timestamp.desc())
        .limit(10)
        .all()
    )

    if not txns:
        raise HTTPException(status_code=404, detail="No transactions found")

    return txns
