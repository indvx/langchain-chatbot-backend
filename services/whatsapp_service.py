from decouple import config
import requests
from dotenv import load_dotenv
from services.langchain_service import LangchainService

load_dotenv()



class WhatsAppService:
    def __init__(self) -> None:
        self.__access_token = str(config("ACCESS_TOKEN")).strip()
        self.phone_number_id = config("PHONE_NUMBER_ID")
        self.__graph_api_url = config("GRAPH_API_URL")
        self.__langchain_service = LangchainService()

    def reply_whatsapp_message(self, to: str, query: str):
        """Generate AI response for user query and post to WhatsApp Cloud API."""
        try:
            url = f"{self.__graph_api_url}/{self.phone_number_id}/messages"
            reply_message = self.__langchain_service.generate_answer(query)

            headers = {
                "Authorization": f"Bearer {self.__access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": reply_message["answer"]}
            }

            response = requests.post(url, headers=headers, json=payload)
            print("WhatsApp API Response:", response.json())

            return response.json()

        except Exception as e:
            raise ProcessLookupError(str(e))

