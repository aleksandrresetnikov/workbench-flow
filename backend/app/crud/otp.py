from sqlalchemy.orm import Session
from typing import Optional
from app import models, schemas
import random
import string
from datetime import datetime, timedelta

def generate_otp_code() -> str:
    """Generate a 6-digit OTP code"""
    return ''.join(random.choices(string.digits, k=6))

def get_otp_by_id(db: Session, otp_id: int) -> Optional[models.Otp]:
    return db.query(models.Otp).filter(models.Otp.Id == otp_id).first()

def get_otp_by_user_email(db: Session, email: str) -> Optional[models.Otp]:
    user = db.query(models.User).filter(models.User.Email == email).first()
    if user and user.OtpId:
        return get_otp_by_id(db, user.OtpId)
    return None

def create_otp(db: Session, user: models.User) -> models.Otp:
    """Create a new OTP for the user"""
    # Delete existing OTP if any
    if user.OtpId:
        existing_otp = get_otp_by_id(db, user.OtpId)
        if existing_otp:
            db.delete(existing_otp)

    otp_code = generate_otp_code()
    db_otp = models.Otp(
        Code=otp_code,
        Attempts=5
    )
    db.add(db_otp)
    db.commit()
    db.refresh(db_otp)

    # Link OTP to user
    user.OtpId = db_otp.Id
    db.commit()

    return db_otp

def verify_otp(db: Session, email: str, code: str) -> tuple[bool, str]:
    """
    Verify OTP code.
    Returns (success, message)
    """
    otp = get_otp_by_user_email(db, email)
    if not otp:
        return False, "OTP not found"

    # Check if OTP is expired (2 minutes)
    if datetime.utcnow() - otp.CreateDate > timedelta(minutes=2):
        return False, "OTP expired"

    # Check attempts
    if otp.Attempts <= 0:
        return False, "No attempts left"

    if otp.Code != code:
        otp.Attempts -= 1
        db.commit()
        return False, f"Invalid OTP code. {otp.Attempts} attempts left"

    # Success - delete OTP and clear user's OtpId
    user = db.query(models.User).filter(models.User.Email == email).first()
    if user:
        user.OtpId = None
    db.delete(otp)
    db.commit()

    return True, "OTP verified successfully"

def can_resend_otp(db: Session, email: str) -> tuple[bool, str]:
    """
    Check if OTP can be resent (30 seconds cooldown).
    Returns (can_resend, message)
    """
    otp = get_otp_by_user_email(db, email)
    if not otp:
        return True, "No existing OTP"

    time_since_creation = datetime.utcnow() - otp.CreateDate
    if time_since_creation < timedelta(seconds=30):
        remaining_seconds = 30 - int(time_since_creation.total_seconds())
        return False, f"Please wait {remaining_seconds} seconds before resending"

    return True, "Can resend OTP"