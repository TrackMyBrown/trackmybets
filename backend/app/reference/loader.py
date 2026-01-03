from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.reference import Sport, SportAlias, SportEntity
from app.reference.teams import TEAM_ALIASES, TEAMS_BY_SPORT


def build_from_static() -> tuple[dict[str, str], dict[str, str], dict[str, list[tuple[str, str]]]]:
    alias_entries: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for sport, teams in TEAMS_BY_SPORT.items():
        for team in teams:
            alias_entries[team.lower()].append((team, sport))
    for alias, canonical in TEAM_ALIASES.items():
        for sport, teams in TEAMS_BY_SPORT.items():
            if canonical in teams:
                alias_entries[alias.lower()].append((canonical, sport))
                break

    team_lookup: dict[str, str] = {}
    sport_lookup: dict[str, str] = {}
    ambiguous: dict[str, list[tuple[str, str]]] = {}
    for alias, entries in alias_entries.items():
        if len(entries) == 1:
            canonical, sport = entries[0]
            team_lookup[alias] = canonical
            sport_lookup[alias] = sport
        else:
            ambiguous[alias] = entries
    return team_lookup, sport_lookup, ambiguous


def load_reference_mappings() -> tuple[dict[str, str], dict[str, str], dict[str, list[tuple[str, str]]]]:
    session = SessionLocal()
    try:
        entity_rows = session.execute(
            select(SportEntity.name, Sport.name).join(Sport, Sport.id == SportEntity.sport_id)
        ).all()
        if not entity_rows:
            raise RuntimeError("Reference tables empty")

        team_lookup: dict[str, str] = {}
        sport_lookup: dict[str, str] = {}
        alias_entries: dict[str, list[tuple[str, str]]] = defaultdict(list)

        for name, sport in entity_rows:
            lowered = name.lower()
            alias_entries[lowered].append((name, sport))

        alias_rows = session.execute(
            select(SportAlias.alias, SportEntity.name, Sport.name)
            .join(SportEntity, SportEntity.id == SportAlias.entity_id)
            .join(Sport, Sport.id == SportEntity.sport_id)
        ).all()

        for alias, canonical, sport in alias_rows:
            lowered = alias.lower()
            alias_entries[lowered].append((canonical, sport))

        ambiguous: dict[str, list[tuple[str, str]]] = {}
        for alias, entries in alias_entries.items():
            if len(entries) == 1:
                canonical, sport = entries[0]
                team_lookup[alias] = canonical
                sport_lookup[alias] = sport
            else:
                ambiguous[alias] = entries

        return team_lookup, sport_lookup, ambiguous
    except Exception:
        return build_from_static()
    finally:
        session.close()
