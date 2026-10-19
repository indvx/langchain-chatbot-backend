import db
import os
from core.config import settings
from sql.cruds import documents as document_crud
import uuid
from services.langchain_service import LangchainService
from services.document_ingestion_service import DocumentIngestionService
import validators
from middleware.auth_middleware import get_current_employee


# High-level document management service.
# Coordinates physical disk storage, database records, and vector embeddings.
class DocumentService:
    def __init__(self):
        self.__db = db.get_db()
        self.__dir_name = str(settings.document_dir_name).strip()
        self.__opne_ai_model = LangchainService()
        self.__ingestion_service = DocumentIngestionService()

    def create_document(self, file, type: str):
        """
        Handles physical file upload from multipart/form-data.
        
        1. Verifies caller is an authenticated employee with 'admin' privileges.
        2. Checks for duplicate uploads using the original filename.
        3. Saves file to disk with a collision-free UUID name prefixed by type (e.g. 'public_xyz.pdf').
           The background scheduler watches this folder and will ingest it within 10s.
        4. Saves initial DB record so the file is immediately visible in management listings.
        """
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

            # Generate unique disk filename: <type>_<uuid4_hex>.<extension>
            # The background scheduler relies on the 'private' prefix to route embeddings
            extension = os.path.splitext(file.filename)[1].lower()
            file_name = f"{type}_{uuid.uuid4().hex}{extension}"
            file_path = os.path.join(self.__dir_name, file_name)

            # Stream binary content to local storage directory
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
        """
        Fetches paginated list of uploaded documents.
        Enforces sane defaults for page and limit if bad values are passed.
        """
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

            # Construct standardized pagination envelope
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
        """
        Cascading delete for a document:
        1. Removes database record.
        2. Deletes physical file on disk (handling the '_' ingestion prefix).
        3. Purges associated text chunk embeddings from ChromaDB vector collection.
        """
        try:
            logged_in_employee = get_current_employee()
            file = document_crud._get_document_by_id(self.__db, id)

            if not logged_in_employee and logged_in_employee.employee_type != "admin":
                raise PermissionError("Access denied")

            if file:
                filepath = ""
                _path = str(file.doc_path)

                # Delete SQL record first
                self.__db.delete(file)

                # Clean up local filesystem if not an external URL
                if validators.url(_path):
                    filepath = _path
                else:
                    file_path = os.path.join(self.__dir_name, _path)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        # Remove leading '_' so vector store lookup matches original source path
                        filepath = file_path.replace("_", "")

                # Evict embeddings from ChromaDB
                if filepath != "":
                    self.__opne_ai_model._delete_documents(filepath)

                self.__db.commit()
                return "Document has been deleted successfully."

            raise ValueError("Document not found for the provided ID.")

        except Exception as e:
            raise ProcessLookupError(str(e))

    def create_url_document(self, url, type: str):
        """
        Scrapes and ingests a remote web page directly.
        Unlike local files which wait for the scheduler loop, web URLs are ingested
        synchronously and recorded in the database.
        """
        try:
            employee = get_current_employee()
            if not employee and employee.employee_type != "admin":
                raise PermissionError("Access denied")

            # Scrape, chunk, and embed web content immediately
            self.__ingestion_service.ingest_file(url, type)
            filename = url.split("/")[-1]

            doc_data = {"original_path": filename, "doc_path": url, "type": type}

            doc = document_crud.create_doc(self.__db, doc_data, employee.id)
            return doc

        except Exception as e:
            print(f"Exception {str(e)}")
            raise ProcessLookupError(str(e))

