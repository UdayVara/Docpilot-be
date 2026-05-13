# src/chat/controller.py

import uuid

import cloudinary
import cloudinary.uploader

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.models.chat import Chat
from src.utils.settings import Settings

# Cloudinary Config
cloudinary.config(
    cloud_name=Settings.CLOUDINARY_CLOUD_NAME,
    api_key=Settings.CLOUDINARY_API_KEY,
    api_secret=Settings.CLOUDINARY_API_SECRET,
    secure=True
)


async def create_chat(
        name: str,
        user_id: str,
        file: UploadFile,
        db: Session,
):
    # Validate PDF
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    try:
        # Upload PDF to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file.file,
            resource_type="raw",
            folder="docpilot",
        )

        file_url = upload_result.get("secure_url")

        # Save in DB
        new_chat = Chat(
            name=file.filename,
            fileUrl=file_url,
            user_id=user_id
        )

        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)

        return {
            "success": True,
            "statusCode": 201,
            "message": "PDF uploaded successfully",
            "data": {
                "id": str(new_chat.id),
                "name": new_chat.name,
                "fileUrl": new_chat.fileUrl,
                "user_id": str(new_chat.user_id)
            }
        }

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )