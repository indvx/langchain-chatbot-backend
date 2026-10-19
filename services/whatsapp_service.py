from alembic import config
import requests
from services.langchain_service import LangchainService
from core.config import settings


# WhatsApp Cloud API messaging integration.
# Generates AI responses using LangChain and sends replies back to users via Meta's Graph API.
class WhatsAppService:
    def __init__(self) -> None:
        self.__access_token = str(settings.meta_access_token).strip()
        self.phone_number_id = settings.meta_phone_number_id
        self.__graph_api_url = settings.meta_graph_api_url
        self.__langchain_service = LangchainService()

    def reply_whatsapp_message(self, to: str, query: str):
        """
        Processes an incoming WhatsApp user message and sends an AI-generated reply.
        
        Note: WhatsApp requests are unauthenticated, so generate_answer queries
        public documents only (no internal database access).
        Formats response according to Meta Graph API v17+ message specifications.
        """
        try:
            url = f"{self.__graph_api_url}/{self.phone_number_id}/messages"
            # Unauthenticated chatbot query: searches public vector knowledge base
            reply_message = self.__langchain_service.generate_answer(query)

            headers = {
                "Authorization": f"Bearer {self.__access_token}",
                "Content-Type": "application/json",
            }

            # Standard Meta Cloud API text message payload structure
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": reply_message["answer"]},
            }

            response = requests.post(url, headers=headers, json=payload)
            print("WhatsApp API Response:", response.json())

            return response.json()

        except Exception as e:
            raise ProcessLookupError(str(e))

