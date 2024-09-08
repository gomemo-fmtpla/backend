from pydantic import BaseModel
from datetime import date

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    # hashed_password: str
    subscription_plan: str 
    subscription_end_date: date = None

class UserUpdate(BaseModel):
    # hashed_password: str | None = None
    subscription_plan: str | None = None
    transaction_receipt: str
    # subscription_end_date: date | None = None