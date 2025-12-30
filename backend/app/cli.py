"""Simple CLI utilities for TrackMyBets backend."""
from __future__ import annotations

import argparse

from app.core.database import Base, engine
from app import models  # noqa: F401 - ensure models are imported for metadata


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database schema initialised.")


def main() -> None:
    parser = argparse.ArgumentParser(description="TrackMyBets backend CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init-db", help="Create database tables using SQLAlchemy metadata")

    args = parser.parse_args()

    if args.command == "init-db":
        init_db()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
