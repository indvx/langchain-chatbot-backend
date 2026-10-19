from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.word_document import Docx2txtLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_core.documents import Document
import validators
import bs4


# Document parsing service that handles multiple file types and web URLs.
# Converts arbitrary input into standardized LangChain Document objects.
class DocumentReader:
    def __init__(self):
        print("DocumentReader initialized")

    def file_loader(self, file: str) -> list[Document]:
        """
        Dispatches file to the appropriate LangChain loader based on file extension or URL format.
        Falls back to plain text loader for unknown extensions.
        """
        if file:
            # Check for HTTP/HTTPS web links first
            if validators.url(file):
                return self.read_web_page(file)
            elif file.endswith(".docx"):
                return self.read_doc(file)
            elif file.endswith(".pdf"):
                return self.read_pdf(file)
            elif file.endswith(".csv"):
                return self.read_csv(file)
            else:
                # Fallback for .txt, markdown, or plain text content
                return self.read_text(file)
        return []

    def read_doc(self, file: str) -> list[Document]:
        """Extract text content from Word (.docx) documents."""
        doc = Docx2txtLoader(file)
        return doc.load()

    def read_csv(self, file: str) -> list[Document]:
        """Load tabular data from CSV files, treating each row as a document."""
        csv = CSVLoader(file)
        return csv.load()

    def read_pdf(self, file: str) -> list[Document]:
        """Extract paginated text from PDF documents using PyPDFLoader."""
        pdf = PyPDFLoader(file)
        return pdf.load()

    def read_web_page(self, path: str) -> list[Document]:
        """Scrape and parse raw HTML content from a given web URL."""
        web_page = WebBaseLoader(web_path=[path])
        return web_page.load()

    def read_text(self, file: str) -> list[Document]:
        """Load standard UTF-8 encoded plain text or markdown files."""
        text = TextLoader(file_path=file)
        return text.load()

