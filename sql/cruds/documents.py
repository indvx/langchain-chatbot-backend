from sqlalchemy.orm import Session
from sql.models.documents import Document
from sql.models.employees import Employee
from sqlalchemy import and_, asc, desc, func, or_


# Database CRUD operations for Document records.
# Handles metadata persistence, file path lookups, and multi-field search queries.

def create_doc(db: Session, data: dict, employee_id: int):
    """
    Persists a new document record linked to the uploading employee.
    Initializes doc_path to the raw storage path before ingestion processing.
    """
    document = Document()
    document.original_path = data.get("original_path", "")
    document.doc_path = data.get("doc_path", "")
    document.type = data.get("type", "")
    document.employee_id = employee_id  # type: ignore

    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def _get_document_by_original_name(db: Session, name: str):
    """Find a document using the user-provided filename at time of upload."""
    return db.query(Document).filter(Document.original_path == name).first()


def _get_document_by_dir_name(db: Session, name: str):
    """
    Lookup document by its filename on disk.
    Used by the ingestion scheduler to find the DB row corresponding to a file in documents/.
    """
    return db.query(Document).filter(Document.doc_path == name).first()


def _get_document_by_id(db: Session, id: int) -> Document:
    """Fetch a single document by primary key."""
    return db.query(Document).filter(Document.id == id).first()


def list_documents(
    db: Session,
    filter: str = "",
    order_by: str = "id",
    order_direction: str = "desc",
    limit: int = 10,
    type: str = "",
    page: int = 1,
    employee_id: int = 0,
):
    """
    Paginated search for documents.
    Performs an outer join with Employees so users can search across both document attributes
    (filename, ID) and uploader info (employee name, email) simultaneously.
    """
    query = db.query(Document).join(
        Employee, Employee.id == Document.employee_id, isouter=True
    )

    # Wildcard search across document details and uploader profile
    if filter and filter.strip():
        filter_data = f"%{filter.strip()}%"
        query = query.filter(
            or_(
                Document.id.like(filter_data),
                Document.original_path.like(filter_data),
                Document.doc_path.like(filter_data),
                Document.employee_id.like(filter_data),
                Employee.id.like(filter_data),
                Employee.name.like(filter_data),
                Employee.email.like(filter_data),
            )
        )

    # Optional scope to a specific employee's uploads
    if employee_id > 0:
        query = query.filter(Document.employee_id == employee_id)

    # Filter by visibility ('public' or 'private')
    if type and type.lower() != "all":
        query = query.filter(Document.type == type)

    # Dynamic column ordering
    if order_by:
        direction = desc if order_direction == "desc" else asc
        query = query.order_by(direction(getattr(Document, order_by)))

    total_items = query.count()

    # Offset pagination
    if limit > 0:
        offset = (int(page) - 1) * limit
        query = query.limit(limit).offset(offset)

    docs = query.all()
    return {"all_items": total_items, "docs": docs}

