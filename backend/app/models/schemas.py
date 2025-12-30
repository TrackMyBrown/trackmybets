from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

class UploadResponse(BaseModel):
    upload_id: str
    filename: str
    stored_path: str
    status: str
    created_at: datetime
    processed_at: datetime | None = None
    row_count: int | None = None

    class Config:
        from_attributes = True


class MetricsCard(BaseModel):
    label: str
    value: float | str
    helper: str
