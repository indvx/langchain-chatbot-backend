from pydantic import BaseModel
from typing import Optional, List


# Pydantic schemas for document endpoints, listing, and ingestion requests.

class Document(BaseModel):
    """
    Representation of a stored document in the system.
    original_path: the initial uploaded filename (as provided by the user).
    doc_path: the internal storage filename in 'documents/' (prefixed with '_' once embedded).
    type: access classification ('public' or 'private').
    """
    id: Optional[int] = None
    original_path: str
    doc_path: str
    type: str
    created_at: Optional[str]


class Meta(BaseModel):
    """Standard pagination metadata envelope returned in list responses."""
    current_item: Optional[int]
    total_items: Optional[int]
    limit: Optional[int]
    page: Optional[int]


class DocumentList(BaseModel):
    """Paginated response containing list of documents and pagination metadata."""
    meta: Meta
    documents: List[Document]


class URLUpload(BaseModel):
    """Request payload for ingesting web content via URL instead of a file upload."""
    url: str
    type: str


