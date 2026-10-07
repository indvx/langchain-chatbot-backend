from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.word_document import Docx2txtLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_core.documents import Document
import validators
import bs4


class DocumentReader:
    def __init__(self):
        print("DocumentReader initialized")

    def file_loader(self, file: str) -> list[Document]:
        """Dispatch document loading based on file extension or URL format."""
        if file:
            if validators.url(file):
                return self.read_web_page(file)
            elif file.endswith(".docx"):
                return self.read_doc(file)
            elif file.endswith(".pdf"):
                return self.read_pdf(file)
            elif file.endswith(".csv"):
                return self.read_csv(file)
            else:
                return self.read_text(file)
        return []

    def read_doc(self, file: str) -> list[Document]:
        doc = Docx2txtLoader(file)
        return doc.load()

    def read_csv(self, file: str) -> list[Document]:
        csv = CSVLoader(file)
        return csv.load()

    def read_pdf(self, file: str) -> list[Document]:
        pdf = PyPDFLoader(file)
        return pdf.load()

    def read_web_page(self, path: str) -> list[Document]:
        web_page = WebBaseLoader(web_path=[path])
        return web_page.load()

    def read_text(self, file: str) -> list[Document]:
        text = TextLoader(file_path=file)
        return text.load()
