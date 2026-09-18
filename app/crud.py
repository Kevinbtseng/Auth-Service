from sqlalchemy.orm import Session
from sqlalchemy import select
from app import models, schemas, security

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email = user.email,
        hashed_password = security.hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    stmt = select(models.User).where(models.User.email == email)
    return db.scalars(stmt).one_or_none()

def get_user_by_id(db: Session, id: int):
    stmt = select(models.User).where(models.User.id == id)
    return db.scalars(stmt).one_or_none()