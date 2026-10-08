from dotenv import load_dotenv
from langchain_chroma import Chroma
import os
from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_experimental.sql import SQLDatabaseChain
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.chains.llm import LLMChain
from services.utility import UtilityService
from db import SQLALCHEMY_DATABASE_URL
from services.llm_service import LLMService

load_dotenv()


class LangchainService:
    """RAG and SQL query orchestration service."""

    def __init__(self):
        os.makedirs("vector_db", exist_ok=True)
        self.llm_service = LLMService()
        self.llm = self.llm_service.get_chat_model()
        self.embeddings = self.llm_service.get_embedding_model()
        self._utility_service = UtilityService()

    def chroma_public_store(self):
        return Chroma(
            collection_name="example_collection",
            embedding_function=self.embeddings,
            persist_directory="./vector_db/chroma_langchain_db",
        )

    def chroma_private_store(self):
        return Chroma(
            collection_name="example_private_collection",
            embedding_function=self.embeddings,
            persist_directory="./vector_db/chroma_langchain_db",
        )

    def sql_chain(self):
        """Construct chain for translating text to SQL queries and executing them."""
        db = SQLDatabase.from_uri(SQLALCHEMY_DATABASE_URL)
        execute_query = QuerySQLDataBaseTool(db=db)
        write_query = create_sql_query_chain(self.llm, db)

        answer_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an AI assistant that decides whether to use SQL results to answer questions.",
                ),
                (
                    "human",
                    """
                Question: {question}

                If this is a database-related question:
                    - Use the SQL Query and SQL Result to answer.
                    - Only perform GET operations, never DELETE or UPDATE.
                    - SQL Query: {query}
                    - SQL Result: {result}
                    - Exclude id and created_at fields from your answer.
                    - Provide a human-readable interpretation.

                If not related to the database:
                    - Give simple way you don't have any information about it.
            """,
                ),
                ("ai", "Final Answer:"),
            ]
        )

        answer = answer_prompt | self.llm
        chain = (
            RunnablePassthrough.assign(
                query=write_query
                | RunnableLambda(self._utility_service.clean_sql_query)
            ).assign(result=itemgetter("query") | execute_query)
            | answer
        )
        return chain

    def vector_chain(self, is_logged_in: bool = False):
        """Construct RAG retrieval chain using private or public vector collections."""
        if is_logged_in:
            print("Employee is Logged-In")
            retriever = self.chroma_private_store().as_retriever(search_kwargs={"k": 2})
        else:
            print("Employee is Logged-Out")
            retriever = self.chroma_public_store().as_retriever(search_kwargs={"k": 2})

        rag_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an AI assistant for a consulting company. Only use the provided context from company documents.",
                ),
                ("human", "Context:\n{context}\n\nQuestion:\n{input}"),
                ("ai", "Answer (be clear, professional, and factual):"),
            ]
        )

        combine_docs_chain = create_stuff_documents_chain(self.llm, rag_prompt)
        return create_retrieval_chain(retriever, combine_docs_chain)

    def generate_answer(self, query: str, is_logged_in: bool = False):
        """Combine DB query results and document RAG into a merged response."""
        sql_response = ""
        if is_logged_in:
            response = self.sql_chain().invoke({"question": query})
            sql_response = response.content

        print("SQL Response:", sql_response)
        vector_chain = self.vector_chain(is_logged_in)
        vector_response = vector_chain.invoke({"input": query})
        print("VECTOR Response:", vector_response)

        merged_response = self.final_answer(sql_response, vector_response["answer"])
        return {"answer": merged_response}

    def final_answer(self, sql_response, vector_response):
        """Synthesize SQL and document results into a single non-redundant answer."""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an AI assistant that merges responses into one answer.",
                ),
                (
                    "human",
                    "Context from SQL:\n{sql_response}\n\nContext from RAG:\n{vector_response}\n\nMerge both contexts into a single, human-readable answer without repetition.",
                ),
                ("ai", "Answer (clear and concise):"),
            ]
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)
        final_answer = chain.run(
            {"sql_response": sql_response, "vector_response": vector_response}
        )
        return final_answer

    def _delete_documents(self, file_path):
        """Purge indexed document chunks by source path from vector stores."""
        public_vector_store = self.chroma_public_store()
        private_vector_store = self.chroma_private_store()
        public_vector_store.delete(where={"source": file_path})
        private_vector_store.delete(where={"source": file_path})
        return True
