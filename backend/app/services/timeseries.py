from __future__ import annotations

from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.bet import Bet
from app.models.upload import Upload


def fetch_profit_timeseries(db: Session, category: str | None = None) -> List[dict[str, str | float]]:
    date_column = func.date(func.coalesce(Bet.settled_at, Upload.created_at))
    stmt = (
        select(
            date_column.label("bucket"),
            func.coalesce(func.sum(func.coalesce(Bet.payout, 0) - func.coalesce(Bet.stake, 0)), 0).label("profit"),
        )
        .select_from(Bet)
        .join(Upload, Bet.upload_id == Upload.id)
        .group_by(date_column)
        .order_by(date_column)
    )

    if category == "racing":
        stmt = stmt.where(Bet.track.isnot(None))
    elif category == "sport":
        stmt = stmt.where(Bet.track.is_(None))

    rows = db.execute(stmt).all()
    cumulative = 0.0
    output: List[dict[str, str | float]] = []
    for row in rows:
        profit = float(row.profit or 0)
        cumulative += profit
        output.append({"date": str(row.bucket), "profit": profit, "cumulative": round(cumulative, 2)})
    return output
