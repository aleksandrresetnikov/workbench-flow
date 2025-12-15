import os
import uuid
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.crud.store_file import create_store_file, get_store_file_by_filename
from app.database import get_db

from app.auth import get_current_active_user
from app import schemas, models

router = APIRouter()

# Ensure Uploads directory exists
UPLOAD_DIR = "Uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=schemas.StoreFile)
async def upload_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a file and create a store file record"""
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        # Save file to disk
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Create store file record
        store_file_data = schemas.StoreFileCreate(
            SourceName=file.filename,
            TagName=unique_filename
        )
        
        store_file = create_store_file(db, store_file_data, current_user.Id)
        
        return store_file
        
    except Exception as e:
        # Clean up if file was partially saved
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )

@router.get("/download/{filename}")
async def download_file(
    filename: str,
    db: Session = Depends(get_db)
):
    """Download a file by its unique filename - no authentication required"""
    
    # Check if file exists in database
    store_file = get_store_file_by_filename(db, filename)
    if not store_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if file exists on disk
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    try:
        # Return file with appropriate headers
        return FileResponse(
            file_path,
            filename=store_file.SourceName,
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File download failed: {str(e)}"
        )
