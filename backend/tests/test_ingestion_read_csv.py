from decimal import Decimal

from app.services.ingestion_service import read_csv, summarize_cash_movements


def test_read_csv_handles_multiline_summaries(tmp_path):
    csv_text = (
        '"Time (AEST)","Type","Summary","Transaction Id","Bet Id","Amount","Balance","Single","Multiple","Exotic","Pool"\n'
        '"01/01/2024 12:00","Bet Stake","Flemington - R7 Lexus Melbourne Cup\n Win or Place\n2. Buckaroo @ 12.00 (Win)",1,10,-5,0.07,true,false,false,false\n'
        '"02/01/2024 13:00","Win","Arsenal v Nottm Forest\n Win-Draw-Win\nArsenal @ 1.36 (Win)",2,11,1.36,5.07,true,false,false,false\n'
    )
    csv_path = tmp_path / "transaction_history.csv"
    csv_path.write_text(csv_text, encoding="utf-8")

    rows = read_csv(csv_path)

    assert len(rows) == 2
    assert rows[0]["Summary"].startswith("Flemington - R7")
    assert "Win-Draw-Win" in rows[1]["Summary"]


def test_summarize_cash_movements_handles_deposits_and_withdrawals():
    rows = [
        {"Type": "Deposit", "Amount": "10"},
        {"Type": "Withdrawal", "Amount": "-5.5"},
        {"Type": "Bet Stake", "Amount": "-1"},
    ]

    totals = summarize_cash_movements(rows)

    assert totals["deposit"] == Decimal("10")
    assert totals["withdrawal"] == Decimal("5.5")
