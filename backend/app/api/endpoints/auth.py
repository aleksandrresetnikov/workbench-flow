from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.auth import authenticate_user, create_access_token, get_current_active_user
from datetime import timedelta

router = APIRouter()

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.Username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/fetch", response_model=schemas.User)
async def fetch_current_user(current_user: models.User = Depends(get_current_active_user)):
    return current_user