from __future__ import annotations

from typing import List

from sqlalchemy import case, func, select
from sqlalchemy.sql import desc, asc
from sqlalchemy.orm import Session

from app.models.bet import Bet
from app.models.upload import Upload


def get_overview_metrics(db: Session) -> List[dict[str, str | float]]:
    has_bets_stmt = select(func.count()).select_from(Bet)
    has_bets = db.execute(has_bets_stmt).scalar_one()
    if not has_bets:
        return []

    total_profit_stmt = select(
        func.coalesce(func.sum(func.coalesce(Bet.payout, 0) - func.coalesce(Bet.stake, 0)), 0)
    )
    total_profit = float(db.execute(total_profit_stmt).scalar_one() or 0)

    win_rate_stmt = select(func.coalesce(func.avg(case((Bet.payout > Bet.stake, 1), else_=0)), 0))
    win_rate = float(db.execute(win_rate_stmt).scalar_one() or 0)

    avg_stake_stmt = select(func.coalesce(func.avg(func.nullif(Bet.stake, 0)), 0))
    avg_stake = float(db.execute(avg_stake_stmt).scalar_one() or 0)

    best_sport = fetch_sport_extreme(db, order="desc")
    worst_sport = fetch_sport_extreme(db, order="asc")

    cards = [
        {
            "label": "Total profit/loss",
            "value": round(total_profit, 2),
            "helper": "Net result since first upload",
        },
        {
            "label": "Win rate",
            "value": round(win_rate * 100, 2),
            "helper": "% of bets returning positive payout",
        },
        {
            "label": "Average stake",
            "value": round(avg_stake, 2),
            "helper": "Mean stake size",
        },
        {
            "label": "Best sport",
            "value": best_sport,
            "helper": "Highest ROI by sport",
        },
        {
            "label": "Worst sport",
            "value": worst_sport,
            "helper": "Lowest ROI by sport",
        },
    ]

    single_multi = fetch_single_multi_metrics(db)
    cards.extend(single_multi)
    return cards


def fetch_sport_extreme(db: Session, order: str) -> str:
    ordering = desc if order == "desc" else asc
    stmt = (
        select(
            Bet.sport,
            func.coalesce(
                func.sum(func.coalesce(Bet.payout, 0) - func.coalesce(Bet.stake, 0))
                / func.nullif(func.sum(func.coalesce(Bet.stake, 0)), 0),
                0,
            ).label("roi"),
        )
        .group_by(Bet.sport)
        .order_by(ordering("roi"))
        .limit(1)
    )
    row = db.execute(stmt).first()
    return row[0] if row else "Unclassified"


def get_cashflow_totals(db: Session) -> dict[str, float]:
    stmt = select(
        func.coalesce(func.sum(func.coalesce(Upload.deposit_total, 0)), 0).label("deposits"),
        func.coalesce(func.sum(func.coalesce(Upload.withdrawal_total, 0)), 0).label("withdrawals"),
    )
    result = db.execute(stmt).one()
    return {
        "deposits": float(result.deposits or 0),
        "withdrawals": float(result.withdrawals or 0),
    }


def fetch_single_multi_metrics(db: Session) -> list[dict[str, str | float]]:
    classification = case(
        (
            func.lower(func.coalesce(Bet.bet_type, "")) == "same game multi",
            "Multi",
        ),
        (
            func.lower(func.coalesce(Bet.bet_type, "")) == "multi",
            "Multi",
        ),
        (
            func.lower(func.coalesce(Bet.bet_type, "")) == "exotic",
            "Multi",
        ),
        else_="Single",
    )

    stmt = (
        select(
            classification.label("grouping"),
            func.coalesce(
                func.sum(func.coalesce(Bet.payout, 0) - func.coalesce(Bet.stake, 0)),
                0,
            ).label("profit"),
            func.coalesce(func.avg(case((Bet.payout > Bet.stake, 1), else_=0)), 0).label("win_rate"),
        )
        .group_by(classification)
    )

    aggregates: dict[str, tuple[float, float]] = {}
    for row in db.execute(stmt):
        label = (row.grouping or "Single").title()
        aggregates[label] = (
            float(row.profit or 0),
            float(row.win_rate or 0),
        )

    response: list[dict[str, str | float]] = []
    for label in ("Single", "Multi"):
        profit, win_rate = aggregates.get(label, (0.0, 0.0))
        response.append(
            {
                "label": f"{label}s P/L",
                "value": round(profit, 2),
                "helper": f"Win rate {round(win_rate * 100, 1)}%",
            }
        )
    return response
