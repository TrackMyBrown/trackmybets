from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Bet(Base):
    __tablename__ = "bets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    upload_id: Mapped[str] = mapped_column(String(36), ForeignKey("uploads.id"), index=True)
    bet_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    last_transaction_id: Mapped[str] = mapped_column(String(128))
    sport: Mapped[str | None] = mapped_column(String(128))
    competition: Mapped[str | None] = mapped_column(String(256))
    team: Mapped[str | None] = mapped_column(String(256))
    opponent: Mapped[str | None] = mapped_column(String(256))
    bet_type: Mapped[str | None] = mapped_column(String(64))
    market_type: Mapped[str | None] = mapped_column(String(64))
    description: Mapped[str | None] = mapped_column(Text)
    track: Mapped[str | None] = mapped_column(String(128))
    race: Mapped[str | None] = mapped_column(String(256))
    runner_number: Mapped[str | None] = mapped_column(String(32))
    runner_name: Mapped[str | None] = mapped_column(String(256))
    odds: Mapped[str | None] = mapped_column(String(64))
    result: Mapped[str | None] = mapped_column(String(32))
    stake: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2))
    payout: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2))
    settled_at: Mapped[datetime | None] = mapped_column(DateTime)

    upload = relationship("Upload", backref="bets")
