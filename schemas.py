from pydantic import BaseModel

class AccountCreate(BaseModel):
    name: str
    initial_balance: float

class Amount(BaseModel):
    amount: float
