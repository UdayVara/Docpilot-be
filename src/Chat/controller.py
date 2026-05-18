# src/chat/controller.py

import uuid

import cloudinary
import cloudinary.uploader

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.models.chat import Chat
from src.utils.settings import Settings
from src.Chat.services.vector_service import (
    process_pdf_and_store_vectors
)

# Cloudinary Config
cloudinary.config(
    cloud_name=Settings.CLOUDINARY_CLOUD_NAME,
    api_key=Settings.CLOUDINARY_API_KEY,
    api_secret=Settings.CLOUDINARY_API_SECRET,
    secure=True
)


async def create_chat(
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
        result = await process_pdf_and_store_vectors(
            file=file,
            chat_id=str(new_chat.id),
            user_id=user_id
        )

        print("result", result)

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

async def get_chats(
        user_id: str,
        db: Session
):
    try:
        chats = (
            db.query(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(Chat.created_at.desc())
            .all()
        )

        return {
            "success": True,
            "statusCode": 200,
            "message": "Chats fetched successfully",
            "data": [
                {
                    "id": str(chat.id),
                    "name": chat.name,
                    "fileUrl": chat.fileUrl,
                    "user_id": str(chat.user_id),
                    "created_at": chat.created_at.isoformat()
                    if chat.created_at else None
                }
                for chat in chats
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )