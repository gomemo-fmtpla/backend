from pydantic import BaseModel
from datetime import date

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    # hashed_password: str
    subscription_plan: str | None = None
    subscription_end_date: date = None

class UserUpdate(BaseModel):
    subscription_plan: str | None = None
    transaction_receipt: str

class UserOnboardingUpdate(BaseModel):
    primary_goal: str | None = None
    user_type: str | None = None
    study_format: str | None = None
    usage_frequency: str | None = None
    focus_topic: str | None = None
    learning_style: str | None = None
