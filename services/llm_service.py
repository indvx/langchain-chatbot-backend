from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from core.config import settings


# LLM and Embeddings model provider abstraction.
# Decouples LangChain logic from specific vendors so we can switch between
# Google Gemini and OpenAI simply by changing LLM_PROVIDER in the .env file.
class LLMService:
    """
    Factory for instantiating Chat and Embedding models based on config.
    Keeps temperature at 0 to minimize hallucinations when generating SQL queries
    and answering factual employee/document questions.
    """

    def __init__(self):
        self.__provider = str(settings.llm_provider).lower()
        self.__chat_model = str(settings.llm_model_name)
        self.__embedding_model = str(settings.llm_embedding_model)

    def gemini_chat_model(self):
        """Build Google Gemini chat model with automatic retry on transient rate limits."""
        return ChatGoogleGenerativeAI(
            model=self.__chat_model,
            temperature=0,
            max_output_tokens=None,
            timeout=None,
            max_retries=2,
        )

    def gemini_embedding_model(self):
        """Build Google Generative AI embeddings model for ChromaDB vector operations."""
        return GoogleGenerativeAIEmbeddings(model=self.__embedding_model)

    def openai_chat_model(self):
        """Build OpenAI chat model (e.g. gpt-4o, gpt-3.5-turbo) with zero temperature."""
        return ChatOpenAI(model=self.__chat_model, temperature=0, verbose=True)

    def openai_embedding_model(self):
        """Build OpenAI embeddings model (e.g. text-embedding-3-small)."""
        return OpenAIEmbeddings(model=self.__embedding_model)

    def get_chat_model(self):
        """Primary getter for chat LLM instance based on configured provider."""
        if self.__provider == "openai":
            return self.openai_chat_model()
        return self.gemini_chat_model()

    def get_embedding_model(self):
        """Primary getter for embedding model instance based on configured provider."""
        if self.__provider == "openai":
            return self.openai_embedding_model()
        return self.gemini_embedding_model()

