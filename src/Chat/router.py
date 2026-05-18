# src/chat/router.py

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from src.Chat.services.chat import ask_ai
from src.middleware.auth_middleware import get_current_user
from src.utils.db.session import get_db
from src.Chat.controller import create_chat,get_chats

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/")
async def upload_chat_pdf(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    return await create_chat(
        user_id=user_id,
        file=file,
        db=db
    )

@router.get("/")
async def get_chat(db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)):
    return await get_chats(db=db, user_id=user_id)


@router.post("/ask/:chat_id")
async def ask_question_controller(
        chat_id: str,
        question: str
):

    try:

        response = await ask_ai(
            chat_id=chat_id,
            question=question
        )

        return {
            "success": True,
            "statusCode": 200,
            "message": "Answer generated successfully",
            "data": response
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )