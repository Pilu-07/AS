from fastapi import Depends, HTTPException, status, Header
from as_ai.database.models import get_db, User
from sqlalchemy.orm import Session
from as_ai.auth.auth_service import verify_token
from typing import Optional

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not authorization or not authorization.startswith("Bearer "):
        raise credentials_exception
        
    token = authorization.split(" ")[1]
    user_id = verify_token(token)
    
    if user_id is None:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
