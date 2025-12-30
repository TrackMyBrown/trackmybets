from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Upload(Base):
    __tablename__ = "uploads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    original_filename: Mapped[str] = mapped_column(String(512))
    stored_path: Mapped[str] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(String(32), default="received")
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deposit_total: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2), default=Decimal("0"))
    withdrawal_total: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2), default=Decimal("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
