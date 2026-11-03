from fastapi import APIRouter, Query, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.requests import Request
from services.whatsapp_service import WhatsAppService
from core.config import settings
import typing as t

router = APIRouter(prefix="/whatsapp", tags=["What'sApp"])


@router.get("/webhook")
async def verify_whatsapp_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
):
    """Verify webhook handshake request from Meta."""
    if hub_mode == "subscribe" and hub_verify_token == settings.meta_verify_token:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    else:
        return PlainTextResponse(content="Forbidden", status_code=403)


@router.post("/webhook")
async def reply_incoming_message(request: Request, service: t.Any = Depends(WhatsAppService())):
    """Receive incoming WhatsApp messages and reply via LLM."""
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="request body not found")

    try:
        data = await request.json()
        if "entry" in data:
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])

                    for msg in messages:
                        from_number = msg["from"]
                        text = msg.get("text", {}).get("body")

                        # Process text messages only (ignore media, receipts, etc.)
                        if text:
                            service.reply_whatsapp_message(from_number, text)

        return JSONResponse(content="message: Ok", status_code=200)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

