from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from services.langchain_service import LangchainService
from models.chat_bot import ChatModel

# Chatbot API router for conversational QA endpoint
router = APIRouter(
    prefix="/chat-bot",
    tags=["Chat Bot"],
)

langchain_service = LangchainService()


@router.post("/")
def start_chat(question: ChatModel):
    """Submits a conversational question to the AI assistant."""
    try:
        response = langchain_service.generate_answer(question.query)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(f"{response['answer']}", status_code=200)


