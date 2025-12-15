from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.util import await_only

from app import schemas, models
from app.database import get_db
from app.auth import authenticate_user, create_access_token, get_current_active_user
from app.crud.user import get_user_by_email, create_user, delete_user
from app.crud.otp import create_otp, verify_otp, can_resend_otp
from app.email_utils import send_otp_email
from datetime import timedelta

router = APIRouter()

@router.post("/register")
async def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user and send OTP"""
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.Email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Create user
    user = create_user(db, user_data)

    # Create OTP
    otp = create_otp(db, user)

    # Send OTP email asynchronously
    email_sent = await send_otp_email(user.Email, otp.Code)
    if not email_sent:
        print(delete_user(db, user_id=user.Id))
        print(user.Id)
        raise HTTPException(status_code=500, detail="Failed to send OTP email")

    return {"message": "User registered successfully. Please check your email for OTP code"}

@router.patch("/confirm-otp")
async def confirm_otp(otp_data: schemas.OtpConfirm, db: Session = Depends(get_db)):
    """Confirm OTP code"""
    success, message = verify_otp(db, otp_data.email, otp_data.code)
    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"message": message}

@router.post("/again-otp")
async def resend_otp(resend_data: schemas.OtpResend, db: Session = Depends(get_db)):
    """Resend OTP code"""
    can_resend, message = can_resend_otp(db, resend_data.email)
    if not can_resend:
        raise HTTPException(status_code=429, detail=message)

    # Get user
    user = get_user_by_email(db, resend_data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create new OTP
    otp = create_otp(db, user)

    # Send OTP email asynchronously
    email_sent = await send_otp_email(user.Email, otp.Code)
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send OTP email")

    return {"message": "OTP code sent successfully"}

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is confirmed (OtpId should be None)
    if user.OtpId is not None:
        raise HTTPException(
            status_code=403,
            detail="Account not confirmed. Please confirm your email first.",
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.Username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/fetch", response_model=schemas.User)
async def fetch_current_user(current_user: models.User = Depends(get_current_active_user)):
    # Check if user is confirmed
    if current_user.OtpId is not None:
        raise HTTPException(
            status_code=403,
            detail="Account not confirmed. Please confirm your email first.",
        )
    return current_user