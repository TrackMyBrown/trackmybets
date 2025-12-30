from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.services.metrics_breakdown import breakdown_by
from app.services.metrics_service import get_cashflow_totals, get_overview_metrics
from app.services.timeseries import fetch_profit_timeseries

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/overview")
def metrics_overview(db: Session = Depends(get_session)) -> list[dict[str, str | float]]:
    return get_overview_metrics(db)


@router.get("/cashflow")
def cashflow_overview(db: Session = Depends(get_session)) -> dict[str, float]:
    return get_cashflow_totals(db)


@router.get("/breakdown/{dimension}")
def metrics_breakdown(
    dimension: str,
    category: str | None = Query(default=None),
    sport: str | None = Query(default=None),
    db: Session = Depends(get_session),
) -> list[dict[str, str | float]]:
    if dimension not in {"sport", "bet_type", "market_type", "track"}:
        raise HTTPException(status_code=400, detail="Unsupported dimension")
    if category not in (None, "sport", "racing"):
        raise HTTPException(status_code=400, detail="Unsupported category")
    rows = breakdown_by(db, dimension, category, sport=sport)  # type: ignore[arg-type]
    normalized: list[dict[str, str | float]] = []
    for row in rows:
        label = row.key or "Unknown"
        normalized.append(
            {
                "key": label,
                "stake": float(row.stake or 0),
                "payout": float(row.payout or 0),
                "profit": float(row.profit or 0),
                "roi": float(row.roi or 0),
                "win_rate": float(row.win_rate or 0),
            }
        )
    return normalized


@router.get("/timeseries")
def profit_timeseries(
    category: str | None = Query(default=None),
    db: Session = Depends(get_session),
) -> list[dict[str, str | float]]:
    if category not in (None, "sport", "racing"):
        raise HTTPException(status_code=400, detail="Unsupported category")
    return fetch_profit_timeseries(db, category)
