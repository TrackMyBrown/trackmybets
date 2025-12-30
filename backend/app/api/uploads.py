from __future__ import annotations

from fastapi import APIRouter, UploadFile

from app.models.schemas import UploadResponse
from app.services.ingestion_service import process_upload
from app.services.upload_service import persist_upload

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/csv", summary="Upload Sportsbet CSV", response_model=UploadResponse)
async def upload_csv(file: UploadFile) -> UploadResponse:
    """Store uploaded CSV and enqueue ingestion."""
    upload = persist_upload(file)
    processed = process_upload(upload.id)
    await file.close()
    return UploadResponse(
        upload_id=processed.id,
        filename=processed.original_filename,
        stored_path=processed.stored_path,
        status=processed.status,
        created_at=processed.created_at,
        processed_at=processed.processed_at,
        row_count=processed.row_count,
    )
