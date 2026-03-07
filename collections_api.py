from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from vector_store import create_collection, insert_document, list_collections
import pdfplumber
from io import BytesIO


router = APIRouter(tags=["collections"])


class CreateCollectionRequest(BaseModel):
    domain: str
    recreate: bool = False


@router.get("/collections")
def get_collections():
    return {"collections": list_collections()}


@router.post("/collections")
def create_collection_runtime(payload: CreateCollectionRequest):
    create_collection(payload.domain, recreate=payload.recreate)
    return {"status": "ok", "domain": payload.domain}


@router.post("/collections/{domain}/documents/text")
def insert_text_document(domain: str, payload: dict):
    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        return {"status": "error", "message": "Missing 'text' in body"}

    metadata = payload.get("metadata") or {}
    if not isinstance(metadata, dict):
        metadata = {}

    insert_document(text=text, metadata=metadata, domain=domain)
    return {"status": "ok", "domain": domain}


@router.post("/collections/{domain}/documents/upload")
async def upload_and_ingest(domain: str, files: list[UploadFile] = File(...)):
    """
    Upload one or more files and insert them into the given domain collection.
    Supports PDFs and plain text files.
    """
    inserted = 0
    skipped: list[str] = []

    for f in files:
        filename = f.filename or "uploaded_file"
        raw = await f.read()

        text: str | None = None
        lower = filename.lower()

        if lower.endswith(".pdf"):
            with pdfplumber.open(BytesIO(raw)) as pdf:
                pages = []
                for page in pdf.pages:
                    extracted = page.extract_text() or ""
                    if extracted.strip():
                        pages.append(extracted)
                text = "\n".join(pages).strip()
        else:
            try:
                text = raw.decode("utf-8").strip()
            except Exception:
                text = None

        if not text:
            skipped.append(filename)
            continue

        insert_document(
            text=text,
            metadata={"source_file": filename, "domain": domain},
            domain=domain,
        )
        inserted += 1

    return {"status": "ok", "domain": domain, "inserted_files": inserted, "skipped": skipped}
