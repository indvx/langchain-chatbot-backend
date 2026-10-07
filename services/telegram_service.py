from core.config import settings
import requests
from services.langchain_service import LangchainService


class TelegramService:
    def __init__(self):
        self.__telegram_token = str(settings.telegram_bot_token).strip()
        self.__telegram_api_url = str(settings.telegram_api_url).strip()
        self.__langchain_service = LangchainService()

    def _start_app(self, chat_id):
        """Send greeting on /start command."""
        try:
            url = f"{self.__telegram_api_url}/bot{self.__telegram_token}"
            reply_text = "👋 Hello! Welcome to the OpenAI Bot. Ask me anything!"
            payload = {"chat_id": chat_id, "text": reply_text}

            response = requests.post(f"{url}/sendMessage", json=payload)
            return response.json()
        except Exception as e:
            raise ProcessLookupError(str(e))

    def _reply_message(self, chat_id, query: str):
        """Pass user query to LangChain and post the reply to Telegram."""
        try:
            url = f"{self.__telegram_api_url}/bot{self.__telegram_token}"

            reply_text = self.__langchain_service.generate_answer(query)

            payload = {"chat_id": chat_id, "text": reply_text["answer"]}
            response = requests.post(f"{url}/sendMessage", json=payload)
            return response.json()
        except Exception as e:
            raise ProcessLookupError(str(e))
