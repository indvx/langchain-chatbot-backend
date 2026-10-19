from fastapi import APIRouter, HTTPException, Depends, File, Form, UploadFile
from services.document import DocumentService
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import Literal, Any
from services.jwt_service import JWTBearer
from models.document import URLUpload
import os


# Document management API router.
# All routes in this router require a valid JWT Bearer token (admin/employee).
router = APIRouter(
    prefix="/doc",
    tags=["Document"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(JWTBearer())]
)

# Whitelist of allowed MIME types to prevent malicious file uploads
ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
}


@router.post('/upload')
def upload_document(
    file: UploadFile = File(...),
    type: Literal['public', 'private'] = Form(default='public'),
):
    """
    Uploads a local document (PDF, DOCX, or TXT) for knowledge-base indexing.
    Files are stored in the 'documents/' directory; the background scheduler
    picks them up for text chunking and ChromaDB embedding.
    """
    try:
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail="This file type is not allowed")

        doc = DocumentService().create_document(file, type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return doc


@router.post('/url/upload')
def upload_url_document(data: URLUpload):
    """
    Ingests a public web page into the vector knowledge base directly via its URL.
    Scraping and vector embedding occur immediately.
    """
    try:
        doc = DocumentService().create_url_document(data.url, data.type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return doc


@router.get('/list')
def read_documents(
    filter: str = '',
    order_by: str = 'id',
    order_direction: Literal['desc', 'asc'] = 'desc',
    limit: int = 10,
    type: Literal['all', 'public', 'private'] = 'all',
    page: int = 1
):
    """
    Returns a paginated list of documents with metadata.
    Supports filtering by filename/uploader and sorting by any valid column.
    """
    try:
        response = DocumentService().read_documents(
            filter,
            order_by,
            order_direction,
            limit,
            type,
            page
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return response


@router.delete('/{id:int}')
def delete_document(id: int):
    """
    Permanently deletes a document:
    Removes its database record, deletes the file from disk, and purges
    its embeddings from ChromaDB. (Restricted to admin).
    """
    try:
        response = DocumentService().delete_document(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content=response, status_code=200)


