from __future__ import annotations

import re

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.reference import Sport, SportAlias, SportEntity
from app.reference.teams import TEAM_ALIASES, TEAMS_BY_SPORT


def slugify(value: str) -> str:
    normalized = re.sub(r"[^\w\s-]", "", value).strip().lower()
    normalized = re.sub(r"[\s_-]+", "-", normalized)
    return normalized or "sport"


def seed_reference_data() -> None:
    session = SessionLocal()
    try:
        existing = session.execute(select(Sport.id).limit(1)).first()
        if existing:
            return

        entity_lookup: dict[str, SportEntity] = {}

        for sport_name, entities in TEAMS_BY_SPORT.items():
            sport = Sport(
                name=sport_name,
                slug=slugify(sport_name),
                category="sport",
                is_user_defined=False,
            )
            session.add(sport)
            session.flush()

            for entity_name in entities:
                entity = SportEntity(
                    sport_id=sport.id,
                    name=entity_name,
                    entity_type="team",
                    is_user_defined=False,
                )
                session.add(entity)
                session.flush()
                entity_lookup[entity_name] = entity

        for alias, canonical in TEAM_ALIASES.items():
            entity = entity_lookup.get(canonical)
            if not entity:
                continue
            normalized = alias.strip().lower()
            session.add(
                SportAlias(
                    entity_id=entity.id,
                    alias=alias,
                    normalized_alias=normalized,
                )
            )

        session.commit()
    finally:
        session.close()
