from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from core.config import settings


class LLMService:
    """Factory for chat and embedding models based on LLM_PROVIDER ('openai' or 'gemini')."""

    def __init__(self):
        self.__provider = settings.llm_provider.lower()
        self.__chat_model = settings.llm_model_name
        self.__embedding_model = settings.llm_embedding_model
        self.__api_key = settings.api_key
        self.__base_url = settings.base_url

    def gemini_chat_model(self):
        print("api_key", self.__api_key)
        print("__chat_model", self.__chat_model)
        print("__embedding_model", self.__embedding_model)
        print("__base_url", self.__base_url)
        return ChatGoogleGenerativeAI(
            model=self.__chat_model,
            api_key=self.__api_key,
            temperature=0,
            max_output_tokens=None,
            timeout=None,
            max_retries=2,
        )

    def gemini_embedding_model(self):
        return GoogleGenerativeAIEmbeddings(
            model=self.__embedding_model,
            google_api_key=self.__api_key
        )

    def openai_chat_model(self):
        return ChatOpenAI(
            model=self.__chat_model,
            api_key= self.__api_key,
            base_url=self.__base_url,
            temperature=0, 
            verbose=True,
        )

    def openai_embedding_model(self):
        return OpenAIEmbeddings(
            model=self.__embedding_model,
            api_key=self.__api_key,
            base_url=self.__base_url
        )

    def get_chat_model(self):
        """Return the configured chat model."""
        if self.__provider == "gemini":
            return self.gemini_chat_model()
        return self.openai_chat_model()

    def get_embedding_model(self):
        """Return the configured embedding model."""
        if self.__provider == "gemini":
            return self.gemini_embedding_model()
        return self.openai_embedding_model()

