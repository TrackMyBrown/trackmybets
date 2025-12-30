from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.upload import Upload


class UploadService:
    """Handles file persistence and Upload record creation."""

    def __init__(self) -> None:
        self.raw_dir = settings.raw_data_dir

    def persist_upload(self, file: UploadFile) -> Upload:
        upload_id = str(uuid.uuid4())
        target_path = self._target_path(upload_id, file.filename or "upload.csv")

        file.file.seek(0)
        with target_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        db = SessionLocal()
        try:
            upload = Upload(
                id=upload_id,
                original_filename=file.filename or "upload.csv",
                stored_path=str(target_path),
                status="received",
            )
            db.add(upload)
            db.commit()
            db.refresh(upload)
            return upload
        finally:
            db.close()

    def _target_path(self, upload_id: str, original: str) -> Path:
        safe_name = original.replace(" ", "_")
        return self.raw_dir / f"{upload_id}-{safe_name}"


def persist_upload(file: UploadFile) -> Upload:
    return UploadService().persist_upload(file)
