from __future__ import annotations

import csv
import io
import re
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.bet import Bet
from app.models.upload import Upload
from app.services.parsers.sportsbet import parse_summary

ROW_START = re.compile(r'^\s*"?\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}')


def process_upload(upload_id: str) -> Upload:
    db = SessionLocal()
    try:
        upload = db.get(Upload, upload_id)
        if not upload:
            raise ValueError(f"Upload {upload_id} not found")

        upload.status = "processing"
        db.commit()
        db.refresh(upload)

        row_count, cash_totals = ingest_file(Path(upload.stored_path), upload, db)

        upload.status = "processed"
        upload.row_count = row_count
        upload.deposit_total = cash_totals.get("deposit")
        upload.withdrawal_total = cash_totals.get("withdrawal")
        upload.processed_at = datetime.utcnow()
        db.commit()
        db.refresh(upload)
        return upload
    except Exception as exc:  # noqa: BLE001 - surface ingestion errors
        logger.exception("Failed to process upload %s", upload_id)
        db.rollback()
        if "upload" in locals() and upload:
            upload.status = "failed"
            db.commit()
        raise exc
    finally:
        db.close()


def ingest_file(path: Path, upload: Upload, db: Session) -> tuple[int, dict[str, Decimal]]:
    rows = read_csv(path)
    aggregated = aggregate_bets(rows)
    upsert_bets(db, upload, aggregated)
    cash_totals = summarize_cash_movements(rows)
    return len(rows), cash_totals


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig") as handle:
        raw_lines = handle.read().splitlines()
    if not raw_lines:
        return []

    header, *data_lines = raw_lines
    normalized_rows: list[str] = []
    current: list[str] = []

    for line in data_lines:
        if not line.strip() and not current:
            continue
        if ROW_START.match(line):
            if current:
                normalized_rows.append("\n".join(current))
            current = [line]
        else:
            current.append(line)

    if current:
        normalized_rows.append("\n".join(current))

    csv_buffer = "\n".join([header, *normalized_rows])
    reader = csv.DictReader(io.StringIO(csv_buffer))
    return [row for row in reader if any(row.values())]


def summarize_cash_movements(rows: list[dict[str, str]]) -> dict[str, Decimal]:
    totals = {"deposit": Decimal("0"), "withdrawal": Decimal("0")}
    for row in rows:
        tx_type = (row.get("Type") or "").strip().lower()
        amount = to_decimal(row.get("Amount"))
        if tx_type == "deposit":
            totals["deposit"] += abs(amount)
        elif tx_type == "withdrawal":
            totals["withdrawal"] += abs(amount)
    return totals


def aggregate_bets(rows: list[dict[str, str]]) -> dict[str, dict[str, object]]:
    aggregates: dict[str, dict[str, object]] = defaultdict(lambda: {
        "stake": Decimal("0"),
        "payout": Decimal("0"),
    })

    for row in rows:
        bet_id = row.get("Bet Id")
        transaction_id = row.get("Transaction Id")
        if not bet_id or not transaction_id:
            continue

        entry = aggregates[bet_id]
        parsed = parse_summary(row.get("Summary", "") or "")
        entry.setdefault("last_transaction_id", transaction_id)
        entry.setdefault("bet_type", parsed.bet_type)
        entry.setdefault("market_type", parsed.market_type)
        entry.setdefault("summary", row.get("Summary", ""))
        entry.setdefault("occurred_at", parse_datetime(row.get("Time (AEST)")))
        entry.setdefault("sport", parsed.sport)
        entry.setdefault("competition", parsed.league)
        entry.setdefault("team", parsed.teams[0] if parsed.teams else None)
        entry.setdefault("opponent", parsed.teams[1] if len(parsed.teams) > 1 else None)
        entry.setdefault("track", parsed.track)
        entry.setdefault("race", parsed.race)
        entry.setdefault("runner_number", parsed.runner_number)
        entry.setdefault("runner_name", parsed.runner_name)
        entry.setdefault("odds", parsed.odds)
        entry.setdefault("result", parsed.result)

        amount = to_decimal(row.get("Amount"))
        if amount < 0:
            entry["stake"] = entry["stake"] + abs(amount)
        else:
            entry["payout"] = entry["payout"] + amount

        entry["last_transaction_id"] = transaction_id

    return aggregates


def upsert_bets(db: Session, upload: Upload, aggregates: dict[str, dict[str, object]]) -> None:
    if not aggregates:
        return

    existing = {
        bet.bet_id: bet
        for bet in db.execute(select(Bet).where(Bet.bet_id.in_(aggregates.keys()))).scalars().all()
    }

    for bet_id, payload in aggregates.items():
        bet = existing.get(bet_id)
        if not bet:
            bet = Bet(bet_id=bet_id)

        bet.upload_id = upload.id
        bet.last_transaction_id = str(payload.get("last_transaction_id"))
        bet.bet_type = payload.get("bet_type")
        bet.market_type = payload.get("market_type")
        bet.description = payload.get("summary")
        bet.sport = payload.get("sport")
        bet.competition = payload.get("competition")
        bet.team = payload.get("team")
        bet.opponent = payload.get("opponent")
        bet.track = payload.get("track")
        bet.race = payload.get("race")
        bet.runner_number = payload.get("runner_number")
        bet.runner_name = payload.get("runner_name")
        bet.odds = payload.get("odds")
        bet.result = payload.get("result")
        bet.stake = payload.get("stake")
        bet.payout = payload.get("payout")
        bet.settled_at = payload.get("occurred_at")

        db.add(bet)

    db.commit()


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    return None


def to_decimal(value: str | None) -> Decimal:
    try:
        return Decimal(value)
    except Exception:  # noqa: BLE001
        return Decimal("0")
