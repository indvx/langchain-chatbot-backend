from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from services.telegram_service import TelegramService
import typing as t

router = APIRouter(
    prefix='/telegram',
    tags=["Tele-Gram"]
)


@router.post("/webhook")
async def webhook(request: Request, service: t.Any = Depends(TelegramService)):
    """Handle incoming Telegram messages and send responses."""
    try:
        data = await request.json()
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")
            print(data)

            # Send welcome message on /start, otherwise query LLM
            if text != '/start':
                service._reply_message(chat_id, text)
            else:
                service._start_app(chat_id)
    except Exception as e:
        print("HTTPException", str(e))
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(status_code=200, content={"ok": True})


