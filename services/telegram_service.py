from core.config import settings
import requests
from services.langchain_service import LangchainService


# Telegram Bot API messaging integration.
# Listens for webhook updates from Telegram and replies using LangChain AI generation.
class TelegramService:
    def __init__(self):
        self.__telegram_token = str(settings.telegram_bot_token).strip()
        self.__telegram_api_url = str(settings.telegram_api_url).strip()
        self.__langchain_service = LangchainService()

    def _start_app(self, chat_id):
        """
        Sends an introductory welcome message when a user sends the /start command.
        Guides them on how to interact with the bot.
        """
        try:
            url = f"{self.__telegram_api_url}/bot{self.__telegram_token}"
            reply_text = "👋 Hello! Welcome to the OpenAI Bot. Ask me anything!"
            payload = {"chat_id": chat_id, "text": reply_text}

            response = requests.post(f"{url}/sendMessage", json=payload)
            return response.json()
        except Exception as e:
            raise ProcessLookupError(str(e))

    def _reply_message(self, chat_id, query: str):
        """
        Queries the LangChain service with user text and sends the answer back to Telegram.
        Runs under guest/unauthenticated scope (queries public document vectors).
        """
        try:
            url = f"{self.__telegram_api_url}/bot{self.__telegram_token}"

            reply_text = self.__langchain_service.generate_answer(query)

            payload = {"chat_id": chat_id, "text": reply_text["answer"]}
            response = requests.post(f"{url}/sendMessage", json=payload)
            return response.json()
        except Exception as e:
            raise ProcessLookupError(str(e))

