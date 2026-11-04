import os
from uuid import uuid4
from langchain_text_splitters import RecursiveCharacterTextSplitter
from services.langchain_service import LangchainService
from services.document_reader import DocumentReader
from sql.cruds import documents as document_crud
from utils.logger import logger
import db
from core.config import settings


class DocumentIngestionService:
    def __init__(self):
        self.langchain_service = LangchainService()
        self.document_reader = DocumentReader()
        self.__db = db.get_db()

        self.data_folder = str(settings.document_dir_name).strip()
        self.chunk_size = 1000
        self.chunk_overlap = 100

        self.vector_store = self.langchain_service.chroma_store()

    def ingest_file(self, path: str, type: str = "public") -> bool:
        """Parse document, split into chunks, and save embeddings in Chroma."""
        try:
            logger.info(f"Starting ingestion for file: {path}")

            loaded_documents = self.document_reader.file_loader(path)
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=["\n", " ", ""],
            )
            documents = text_splitter.split_documents(loaded_documents)
            uuids = [str(uuid4()) for _ in range(len(documents))]

            logger.info(
                f"Prepared {len(documents)} document chunks for vector storage."
            )
            self.vector_store.add_documents(documents=documents, ids=uuids)

            logger.info(f"File successfully ingested: {path}")
            return True

        except Exception as e:
            logger.error(f"Error ingesting file '{path}': {str(e)}", exc_info=True)
            return False

    def main_loop(self) -> bool:
        """Poll the documents directory, embed new files, and prefix them with '_' when done."""
        logger.info("Background scheduler main_loop started.")
        processed_files = []

        try:
            for filename in os.listdir(self.data_folder):
                # Skip files already processed in previous runs
                if not filename.startswith("_"):
                    file_path = os.path.join(self.data_folder, filename)

                    logger.info(f"Processing new file: {filename}")
                    success = self.ingest_file(file_path)

                    if not success:
                        logger.warning(
                            f"Skipping file due to ingestion failure: {filename}"
                        )
                        continue

                    # Update record in DB with the prefixed filename
                    new_filename = "_" + filename
                    document = document_crud._get_document_by_dir_name(
                        self.__db, filename
                    )

                    if document:
                        document.doc_path = str(new_filename)  # type: ignore
                        self.__db.add(document)
                        self.__db.commit()
                        self.__db.refresh(document)
                        logger.debug(f"Updated DB record for file: {filename}")

                    # Rename on disk so the scheduler ignores it in future runs
                    new_file_path = os.path.join(self.data_folder, new_filename)
                    os.rename(file_path, new_file_path)
                    processed_files.append(file_path)

            logger.info(
                f"Main loop completed. Total files processed: {len(processed_files)}"
            )
            return True

        except Exception as e:
            logger.error(f"Error in main_loop: {str(e)}", exc_info=True)
            return False

