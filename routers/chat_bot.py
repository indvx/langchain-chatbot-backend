from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from services.langchain_service import LangchainService
from models.chat_bot import ChatModel
from middleware.auth_middleware import get_current_employee


# Chatbot API router.
# Exposes the main conversational QA endpoint used by the frontend web client.
router = APIRouter(
    prefix='/chat-bot',
    tags=["Chat Bot"],
)

langchain_service = LangchainService()


@router.post("/")
def start_chat(question: ChatModel):
    """
    Submits a conversational question to the AI assistant.
    
    Dynamically checks the caller's authentication state via AuthMiddleware:
    - Logged-in employees: granted access to internal database SQL queries + private documents.
    - Public / anonymous guests: restricted to public document vector search only.
    """
    try:
        employee = get_current_employee()
        is_logged_in = bool(employee)
        # Generate blended answer from ChromaDB and SQL database
        response = langchain_service.generate_answer(question.query, is_logged_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return JSONResponse(f"{response['answer']}", status_code=200)


