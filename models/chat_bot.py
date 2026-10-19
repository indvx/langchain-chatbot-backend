from pydantic import BaseModel


class ChatModel(BaseModel):
    """Payload schema for user chat queries submitted to POST /chat-bot."""
    query: str

