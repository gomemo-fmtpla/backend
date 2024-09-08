from app.database.models import User
from app.database.schemas.user import UserCreate, UserUpdate
from sqlalchemy.orm import Session

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    db_user = User(
        username=user.username,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: UserUpdate):
    db_user = get_user(db, user_id)
    if db_user:
        for field, value in vars(user).items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def get_subscription_status(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user:
        return {
            "subscription_plan": user.subscription_plan,
            "transaction_receipt": user.transaction_receipt,
        }
    else:
        raise ValueError("User not found")


# def delete_user(db: Session, user_id: int):
#     db_user = get_user(db, user_id)
#     if db_user:
#         db.delete(db_user)
#         db.commit()
#     return db_user

