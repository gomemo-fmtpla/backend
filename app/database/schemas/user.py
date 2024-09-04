from app.database.models import SubscriptionPlanType
from pydantic import BaseModel
from datetime import date

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    # hashed_password: str
    subscription_plan: SubscriptionPlanType = SubscriptionPlanType.free
    subscription_end_date: date = None

class UserUpdate(UserBase):
    # hashed_password: str | None = None
    subscription_plan: SubscriptionPlanType | None = None
    subscription_end_date: date | None = None