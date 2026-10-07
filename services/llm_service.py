from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from decouple import config



class LLMService:
    """Factory for instantiating Chat and Embedding models based on config."""

    def __init__(self):
        self.__provider = str(config("MODEL_PROVIDER"))
        self.__chat_model = str(config("MODEL_NAME"))
        self.__embedding_model = str(config("EMBEDDING_MODEL"))

    def gemini_chat_model(self):
        return ChatGoogleGenerativeAI(
            model=self.__chat_model,
            temperature=0,
            max_output_tokens=None,
            timeout=None,
            max_retries=2,
        )

    def gemini_embedding_model(self):
        return GoogleGenerativeAIEmbeddings(
            model=self.__embedding_model
        )

    def openai_chat_model(self):
        return ChatOpenAI(model=self.__chat_model, temperature=0, verbose=True)

    def openai_embedding_model(self):
        return OpenAIEmbeddings(model=self.__embedding_model)

    def get_chat_model(self):
        if self.__provider == 'openai':
            return self.openai_chat_model()
        return self.gemini_chat_model()

    def get_embedding_model(self):
        if self.__provider == 'openai':
            return self.openai_embedding_model()
        return self.gemini_embedding_model()

