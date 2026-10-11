from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, database, crud, security, models, dependencies, refresh_tokens

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

@router.post("/login", response_model=schemas.Token)
async def user_login(user: schemas.UserLogin, db: Session = Depends(database.get_db)):
    userFromEmail = crud.get_user_by_email(db, user.email)
    if userFromEmail is None:
        raise HTTPException(status_code=401, detail="Invalid login details")
    elif security.verify_password(user.password, userFromEmail.hashed_password):
        access_token = security.create_access_token({"sub": str(userFromEmail.id)})
        refresh_token, _ = refresh_tokens.store_refresh_token(userFromEmail.id)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid login details")

@router.get("/me", response_model=schemas.UserResponse)
async def read_current_user(current_user: models.User = Depends(dependencies.get_current_user)):
    return current_user

@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(body: schemas.RefreshRequest, db: Session = Depends(database.get_db)):
    raw_token = body.refresh_token
    data = refresh_tokens.lookup_token(raw_token)
    if data is None:
        raise HTTPException(401, "Invalid or expired refresh token")
    elif data["used"] == "1":
        refresh_tokens.revoke_family(data["family_id"])
        raise HTTPException(401, "Invalid or expired refresh token")
    else:
        user = crud.get_user_by_id(db, int(data["user_id"]))
        if user is None:
            raise HTTPException(401, "Invalid or expired refresh token")
        refresh_tokens.mark_used(raw_token)
        new_token, _ = refresh_tokens.store_refresh_token(data["user_id"], data["family_id"])
        access_token = security.create_access_token({"sub": data["user_id"]})
        return {"access_token": access_token, "refresh_token": new_token, "token_type": "bearer"}