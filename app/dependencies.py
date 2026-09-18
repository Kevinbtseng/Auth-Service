from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app import security, crud, database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    payload = security.decode_access_token(token)
    if payload is None:
        raise HTTPException(401, "Invalid or expired token")
    
    user = crud.get_user_by_id(db, int(payload["sub"]))
    if user:
        return user
    else:
        raise HTTPException(401, "Invalid or expired token")