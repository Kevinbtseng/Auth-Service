from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, database, crud

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/signup", response_model=schemas.UserResponse, status_code=201)
async def user_signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    if crud.get_user_by_email(db, user.email) is None:
        return crud.create_user(db, user)
    else:
        raise HTTPException(status_code=409, detail="User with the same email already exists")

