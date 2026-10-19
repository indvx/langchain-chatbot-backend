from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from services.telegram_service import TelegramService


# Telegram Bot Webhook API Router.
# Receives update events sent by the Telegram Bot API server.
router = APIRouter(
    prefix='/telegram',
    tags=["Tele-Gram"]
)


@router.post("/webhook")
async def webhook(request: Request):
    """
    Primary Telegram webhook listener.
    Telegram sends updates here whenever a user interacts with the bot:
    - If user sends '/start': triggers welcome greeting and bot instructions.
    - Otherwise: sends question to LangChain QA pipeline and replies directly to chat_id.
    
    Always acknowledges with HTTP 200 {"ok": True} so Telegram stops retry delivery.
    """
    try:
        data = await request.json()
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")
            print(data)

            # Route slash command vs natural query
            if text != '/start':
                TelegramService()._reply_message(chat_id, text)
            else:
                TelegramService()._start_app(chat_id)
    except Exception as e:
        print("HTTPException", str(e))
        raise HTTPException(status_code=400, detail=str(e))

    # Acknowledge event reception to Telegram servers
    return JSONResponse(status_code=200, content={"ok": True})


