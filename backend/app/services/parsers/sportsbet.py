from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List

from app.reference.loader import load_reference_mappings
from app.reference.teams import BET_TYPE_KEYWORDS

TRACK_SPLIT = re.compile(r"\s*-\s*")
RUNNER_REGEX = re.compile(r"(?P<number>\d+)\.\s+(?P<name>[^@]+)")
ODDS_REGEX = re.compile(r"@\s*(?P<odds>[\d\.]+(?:/[\d\.]+)?)")
OUTCOME_REGEX = re.compile(r"\((?P<result>Win|Place|Each Way)\)", re.IGNORECASE)
TEAM_DELIMITERS = [" v ", " vs ", " at ", " @ "]
PLAYER_MARKET_SPLIT = re.compile(r"\s+[–-]\s+")
TRACK_RACE_PREFIX = re.compile(r"^(r\d+|race\b|heat\b|trial\b|leg\b|bm\d+)", re.IGNORECASE)

TEAM_LOOKUP, TEAM_SPORT_LOOKUP, AMBIGUOUS_TEAM_LOOKUP = load_reference_mappings()


@dataclass
class ParsedBet:
    bet_type: str | None
    market_type: str | None
    sport: str | None
    league: str | None
    teams: List[str]
    track: str | None
    race: str | None
    runner_number: str | None
    runner_name: str | None
    odds: str | None
    result: str | None
    summary: str


def parse_summary(summary: str) -> ParsedBet:
    event_line, market_line, selection_line = split_summary_lines(summary)
    normalized = summary.lower()
    detected_bet_type = detect_bet_type(normalized)
    teams = detect_teams(event_line)
    track, race = extract_track_and_race(event_line or "")
    sport = infer_sport(teams, event_line)
    if track:
        teams = []
        sport = sport or "Racing"
    runner_number, runner_name = extract_runner(selection_line or summary)
    odds = extract_odds(selection_line or summary)
    result = extract_result(selection_line or summary)
    player_name, player_market = extract_player_market(market_line)
    market_label = player_market or market_line
    market_type = normalize_label(market_label) or detect_market(normalized, summary)
    if not runner_name and player_name:
        runner_name = player_name
    league = sport

    return ParsedBet(
        bet_type=detected_bet_type,
        market_type=market_type,
        sport=sport,
        league=league,
        teams=teams,
        track=track,
        race=race,
        runner_number=runner_number,
        runner_name=runner_name,
        odds=odds,
        result=result,
        summary=summary,
    )


def split_summary_lines(summary: str) -> tuple[str | None, str | None, str | None]:
    lines = [line.strip() for line in summary.split("\n") if line.strip()]
    if not lines:
        return None, None, None
    event = lines[0]
    market = lines[1] if len(lines) > 1 else None
    selection = " ".join(lines[2:]) if len(lines) > 2 else None
    return event, market, selection


def normalize_label(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"\s+", " ", value).strip()
    cleaned = re.sub(r"\s*\([\s\d,]+\)\s*$", "", cleaned)
    return cleaned or None


def extract_player_market(line: str | None) -> tuple[str | None, str | None]:
    if not line:
        return None, None
    parts = PLAYER_MARKET_SPLIT.split(line.strip(), maxsplit=1)
    if len(parts) == 2:
        player, market = parts
        return player.strip() or None, market.strip() or None
    return None, None


def detect_bet_type(text: str) -> str:
    for bet_type, keywords in BET_TYPE_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return bet_type
    return "Single"


def detect_market(text: str, summary: str) -> str | None:
    if "same game multi" in text:
        return "Same Game Multi"
    if "head to head" in text or "match betting" in text:
        return "Head to Head"
    if "win or place" in text:
        if "each way" in text:
            return "Each Way"
        return "Win or Place"
    if "line" in text:
        return "Line"
    if "over" in text or "under" in text:
        return "Total"
    if "boxed" in text or "trifecta" in text or "quinella" in text:
        return "Exotic"
    if "@" in summary:
        return "Fixed Odds"
    return None


def detect_teams(event_line: str | None) -> list[str]:
    if not event_line:
        return []
    parts = [event_line]
    for delimiter in TEAM_DELIMITERS:
        if re.search(delimiter, event_line, flags=re.IGNORECASE):
            parts = re.split(delimiter, event_line, flags=re.IGNORECASE)
            break
    teams_metadata: list[dict[str, object]] = []
    for part in parts:
        candidate = part.strip().split("\n")[0].strip()
        if not candidate:
            continue
        candidate = re.sub(r"\s+", " ", candidate)
        lowered = candidate.lower()
        canonical = TEAM_LOOKUP.get(lowered)
        if canonical:
            teams_metadata.append({"name": canonical, "sport": TEAM_SPORT_LOOKUP.get(lowered)})
        elif lowered in AMBIGUOUS_TEAM_LOOKUP:
            teams_metadata.append({"name": candidate, "sport": None, "options": AMBIGUOUS_TEAM_LOOKUP[lowered]})
        else:
            teams_metadata.append({"name": candidate, "sport": None})
        if len(teams_metadata) == 2:
            break

    resolve_ambiguous_teams(teams_metadata)
    teams = [meta["name"] for meta in teams_metadata if meta.get("name")]
    if teams:
        return teams

    lower_event = event_line.lower()
    for normalized, canonical in TEAM_LOOKUP.items():
        if normalized in lower_event and canonical not in teams:
            teams.append(canonical)
            if len(teams) == 2:
                break
    return teams[:2]


def resolve_ambiguous_teams(teams_metadata: list[dict[str, object]]) -> None:
    def current_known_sports() -> set[str]:
        return {meta["sport"] for meta in teams_metadata if meta.get("sport")}

    for meta in teams_metadata:
        options = meta.get("options")
        if not options:
            continue
        chosen = pick_team_option(options, current_known_sports())
        if chosen:
            meta["name"], meta["sport"] = chosen
        else:
            meta["name"] = meta["name"]  # keep alias
        meta.pop("options", None)


def pick_team_option(options: list[tuple[str, str]], known_sports: set[str]) -> tuple[str, str] | None:
    if known_sports:
        for sport in known_sports:
            for name, option_sport in options:
                if option_sport == sport:
                    return name, option_sport
    # try intersection when no known sports
    sport_counts = defaultdict(int)
    for _, sport in options:
        sport_counts[sport] += 1
    if len(sport_counts) == 1:
        sport = next(iter(sport_counts))
        for name, option_sport in options:
            if option_sport == sport:
                return name, option_sport
    return None


def infer_sport(teams: list[str], event_line: str | None = None) -> str | None:
    for team in teams:
        sport = TEAM_SPORT_LOOKUP.get(team.lower())
        if sport:
            return sport
    if event_line:
        lowered = event_line.lower()
        if "afl" in lowered:
            return "AFL"
        if "nrl" in lowered:
            return "NRL"
        if "nba" in lowered or "basketball" in lowered:
            return "Basketball"
        if "bbl" in lowered or "cricket" in lowered:
            return "Cricket"
    return None


def extract_track_and_race(summary: str) -> tuple[str | None, str | None]:
    lines = [line.strip() for line in summary.split("\n") if line.strip()]
    if not lines:
        return None, None
    first_line = lines[0]
    lowered = first_line.lower()
    if any(delim in lowered for delim in [" v ", " vs ", " vs.", " @ "]):
        return None, None
    parts = TRACK_SPLIT.split(first_line, maxsplit=1)
    if len(parts) == 2:
        track_candidate, race_candidate = parts[0].strip(), parts[1].strip()
        if TRACK_RACE_PREFIX.match(race_candidate):
            return track_candidate or None, race_candidate or None
    return None, None


def extract_runner(summary: str) -> tuple[str | None, str | None]:
    match = RUNNER_REGEX.search(summary)
    if not match:
        return None, None
    return match.group("number"), match.group("name").strip()


def extract_odds(summary: str) -> str | None:
    match = ODDS_REGEX.search(summary)
    if not match:
        return None
    return match.group("odds")


def extract_result(summary: str) -> str | None:
    match = OUTCOME_REGEX.search(summary)
    if not match:
        return None
    return match.group("result").title()
