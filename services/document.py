import db
import os
from core.config import settings
from sql.cruds import documents as document_crud
import uuid
from services.langchain_service import LangchainService
from services.document_ingestion_service import DocumentIngestionService
import validators


class DocumentService:
    def __init__(self):
        self.__db = db.get_db()
        self.__dir_name = str(settings.document_dir_name).strip()
        self.__opne_ai_model = LangchainService()
        self.__ingestion_service = DocumentIngestionService()

    def create_document(self, file, type: str = "public", employee_id: int = None):
        """Save an uploaded file to disk and create its database record."""
        try:
            filename = (f"{file.filename}").strip()
            exist_document = document_crud._get_document_by_original_name(
                self.__db, filename
            )
            if exist_document:
                raise ValueError(
                    "Please rename this file because it already exists in our records."
                )

            os.makedirs(self.__dir_name, exist_ok=True)

            extension = os.path.splitext(file.filename)[1].lower()
            file_name = f"public_{uuid.uuid4().hex}{extension}"
            file_path = os.path.join(self.__dir_name, file_name)

            with open(file_path, "wb") as out_file:
                out_file.write(file.file.read())

            doc_data = {"original_path": filename, "doc_path": file_name, "type": "public"}

            doc = document_crud.create_doc(self.__db, doc_data, employee_id)
            return doc

        except Exception as e:
            raise ProcessLookupError(str(e))

    def read_documents(
        self,
        filter: str = "",
        order_by: str = "id",
        order_direction: str = "desc",
        limit: int = 10,
        type: str = "all",
        page: int = 1,
    ):
        """Return a paginated list of documents."""
        try:
            if limit < 1:
                limit = 10
            if page < 1:
                page = 1

            docs = document_crud.list_documents(
                self.__db,
                filter,
                order_by,
                order_direction,
                limit,
                type,
                page,
            )

            all_items = docs["all_items"]
            documents = docs["docs"]

            meta = {
                "current_item": len(documents),
                "limit": limit,
                "page": page,
                "total_items": all_items,
            }

            return {"meta": meta, "documents": documents}

        except Exception as e:
            raise ProcessLookupError(str(e))

    def delete_document(self, id: int):
        """Delete document from database, remove file from disk, and evict embeddings."""
        try:
            file = document_crud._get_document_by_id(self.__db, id)

            if file:
                filepath = ""
                _path = str(file.doc_path)

                self.__db.delete(file)

                # Remove local file from disk if not a URL
                if validators.url(_path):
                    filepath = _path
                else:
                    file_path = os.path.join(self.__dir_name, _path)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        # Strip leading '_' so vector search lookup matches original source path
                        filepath = file_path.replace("_", "")

                # Delete embeddings from vector store
                if filepath != "":
                    self.__opne_ai_model._delete_documents(filepath)

                self.__db.commit()
                return "Document has been deleted successfully."

            raise ValueError("Document not found for the provided ID.")

        except Exception as e:
            raise ProcessLookupError(str(e))

    def create_url_document(self, url, type: str = "public", employee_id: int = None):
        """Scrape web page content and store its URL in the database."""
        try:
            self.__ingestion_service.ingest_file(url, "public")
            filename = url.split("/")[-1]

            doc_data = {"original_path": filename, "doc_path": url, "type": "public"}

            doc = document_crud.create_doc(self.__db, doc_data, employee_id)
            return doc

        except Exception as e:
            print(f"Exception {str(e)}")
            raise ProcessLookupError(str(e))

