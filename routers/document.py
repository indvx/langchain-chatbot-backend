from fastapi import APIRouter, HTTPException, File, Form, UploadFile, Depends
from services.document import DocumentService
from fastapi.responses import JSONResponse
from typing import Literal, Optional
from models.document import URLUpload
import typing as t

router = APIRouter(
    prefix="/doc",
    tags=["Document"],
    responses={404: {"description": "Not found"}},
)

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
}


@router.post('/upload')
def upload_document(
    file: UploadFile = File(...),
    type: Literal['public'] = Form(default='public'),
    employee_id: Optional[int] = Form(default=None),
    service: t.Any = Depends(DocumentService)

):
    """Upload a file (PDF, DOCX, TXT) for vector indexing."""
    try:
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail="This file type is not allowed")

        doc = service.create_document(file, "public", employee_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return doc


@router.post('/url/upload')
def upload_url_document(
    data: URLUpload, 
    employee_id: Optional[int] = None,
    service: t.Any = Depends(DocumentService)
    ):
    """Ingest content from a web URL."""
    try:
        doc = service.create_url_document(data.url, "public", employee_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return doc


@router.get('/list')
def read_documents(
    filter: str = '',
    order_by: str = 'id',
    order_direction: Literal['desc', 'asc'] = 'desc',
    limit: int = 10,
    type: str = 'all',
    page: int = 1,
    service: t.Any = Depends(DocumentService)
):
    """List documents with pagination and optional search filter."""
    try:
        response = service.read_documents(
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
def delete_document(
    id: int,
    service: t.Any = Depends(DocumentService)
    ):
    """Delete a document from the database, disk, and vector store."""
    try:
        response = service.delete_document(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content=response, status_code=200)


