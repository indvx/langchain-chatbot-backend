from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from services.langchain_service import LangchainService
from models.chat_bot import ChatModel
import typing as t

router = APIRouter(
    prefix="/chat-bot",
    tags=["Chat Bot"],
)

@router.post("/")
def start_chat(
    question: ChatModel,
    service: t.Any = Depends(LangchainService)
):
    """Answer a user query using document and database context."""
    try:
        response = service.generate_answer(question.query)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(f"{response['answer']}", status_code=200)


