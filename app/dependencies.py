from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app import security, crud, database

bearer_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(database.get_db)):
    payload = security.decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(401, "Invalid or expired access token")
    
    try:
        user_id = int(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(401, "Invalid or expired access token")

    user = crud.get_user_by_id(db, user_id)
    if user:
        return user
    else:
        raise HTTPException(401, "Invalid or expired access token")