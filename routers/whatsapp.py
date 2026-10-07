from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.requests import Request
from services.whatsapp_service import WhatsAppService
from decouple import config
from dotenv import load_dotenv


load_dotenv()

router = APIRouter(
    prefix='/whatsapp',
    tags=["What'sApp"]
)


@router.get("/webhook")
async def verify_whatsapp_webhook(
    hub_mode: str = Query(alias='hub.mode'),
    hub_challenge: str = Query(alias='hub.challenge'),
    hub_verify_token: str = Query(alias='hub.verify_token')
):
    # Verify Meta webhook challenge
    if hub_mode == "subscribe" and hub_verify_token == config('VERIFY_TOKEN'):
        return PlainTextResponse(content=hub_challenge, status_code=200)
    else:
        return PlainTextResponse(content="Forbidden", status_code=403)


@router.post("/webhook")
async def reply_incoming_message(request: Request):
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

                        if text:
                            WhatsAppService().reply_whatsapp_message(from_number, text)

        return JSONResponse(content="message: Ok", status_code=200)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

