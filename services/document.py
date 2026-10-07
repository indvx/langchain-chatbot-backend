import db
import os
from core.config import settings
from sql.cruds import documents as document_crud
import uuid
from services.langchain_service import LangchainService
from services.document_ingestion_service import DocumentIngestionService
import validators
from middleware.auth_middleware import get_current_employee


class DocumentService:
    def __init__(self):
        self.__db = db.get_db()
        self.__dir_name = str(settings.document_dir_name).strip()
        self.__opne_ai_model = LangchainService()
        self.__ingestion_service = DocumentIngestionService()

    def create_document(self, file, type: str):
        """Save uploaded document file and create initial database record."""
        try:
            employee = get_current_employee()
            if not employee and employee.employee_type != "admin":
                raise PermissionError("Access denied")

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
            file_name = f"{type}_{uuid.uuid4().hex}{extension}"
            file_path = os.path.join(self.__dir_name, file_name)

            with open(file_path, "wb") as out_file:
                out_file.write(file.file.read())

            doc_data = {"original_path": filename, "doc_path": file_name, "type": type}

            doc = document_crud.create_doc(self.__db, doc_data, employee.id)
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
        """Fetch documents list with pagination metadata."""
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
        """Delete document record, disk file, and associated vector embeddings."""
        try:
            logged_in_employee = get_current_employee()
            file = document_crud._get_document_by_id(self.__db, id)

            if not logged_in_employee and logged_in_employee.employee_type != "admin":
                raise PermissionError("Access denied")

            if file:
                filepath = ""
                _path = str(file.doc_path)

                self.__db.delete(file)

                if validators.url(_path):
                    filepath = _path
                else:
                    file_path = os.path.join(self.__dir_name, _path)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        filepath = file_path.replace("_", "")

                if filepath != "":
                    self.__opne_ai_model._delete_documents(filepath)

                self.__db.commit()
                return "Document has been deleted successfully."

            raise ValueError("Document not found for the provided ID.")

        except Exception as e:
            raise ProcessLookupError(str(e))

    def create_url_document(self, url, type: str):
        """Ingest document content from web URL and record in DB."""
        try:
            employee = get_current_employee()
            if not employee and employee.employee_type != "admin":
                raise PermissionError("Access denied")

            self.__ingestion_service.ingest_file(url, type)
            filename = url.split("/")[-1]

            doc_data = {"original_path": filename, "doc_path": url, "type": type}

            doc = document_crud.create_doc(self.__db, doc_data, employee.id)
            return doc

        except Exception as e:
            print(f"Exception {str(e)}")
            raise ProcessLookupError(str(e))
