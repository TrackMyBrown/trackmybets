from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.bet import Bet


@dataclass
class BreakdownRow:
    key: str | None
    stake: float
    payout: float
    profit: float
    roi: float
    win_rate: float


Dimension = Literal["sport", "bet_type", "market_type", "track"]


def breakdown_by(
    db: Session,
    dimension: Dimension,
    category: str | None = None,
    sport: str | None = None,
) -> list[BreakdownRow]:
    column = getattr(Bet, dimension)
    stmt = (
        select(
            column.label("key"),
            func.coalesce(func.sum(func.coalesce(Bet.stake, 0)), 0).label("stake"),
            func.coalesce(func.sum(func.coalesce(Bet.payout, 0)), 0).label("payout"),
            func.coalesce(
                func.sum(func.coalesce(Bet.payout, 0) - func.coalesce(Bet.stake, 0)),
                0,
            ).label("profit"),
            func.coalesce(
                func.sum(func.coalesce(Bet.payout, 0) - func.coalesce(Bet.stake, 0))
                / func.nullif(func.sum(func.coalesce(Bet.stake, 0)), 0),
                0,
            ).label("roi"),
            func.coalesce(func.avg(case((Bet.payout > Bet.stake, 1), else_=0)), 0).label("win_rate"),
        )
        .group_by(column)
        .order_by(func.coalesce(func.sum(func.coalesce(Bet.payout, 0) - func.coalesce(Bet.stake, 0)), 0).desc())
    )

    if category == "racing":
        stmt = stmt.where(Bet.track.isnot(None))
    elif category == "sport":
        stmt = stmt.where(Bet.track.is_(None))

    if sport:
        normalized = sport.strip().lower()
        if normalized == "unknown":
            stmt = stmt.where(Bet.sport.is_(None))
        else:
            stmt = stmt.where(func.lower(Bet.sport) == normalized)

    results = []
    for row in db.execute(stmt):
        results.append(
            BreakdownRow(
                key=row.key,
                stake=float(row.stake or 0),
                payout=float(row.payout or 0),
                profit=float(row.profit or 0),
                roi=float(row.roi or 0),
                win_rate=float(row.win_rate or 0),
            )
        )
    return results
