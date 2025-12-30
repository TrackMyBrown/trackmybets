from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List

from app.reference.teams import BET_TYPE_KEYWORDS, TEAMS_BY_SPORT

TRACK_SPLIT = re.compile(r"\s*-\s*")
RUNNER_REGEX = re.compile(r"(?P<number>\d+)\.\s+(?P<name>[^@]+)")
ODDS_REGEX = re.compile(r"@\s*(?P<odds>[\d\.]+(?:/[\d\.]+)?)")
OUTCOME_REGEX = re.compile(r"\((?P<result>Win|Place|Each Way)\)", re.IGNORECASE)
TEAM_DELIMITERS = [" v ", " vs ", " at ", " @ "]
PLAYER_MARKET_SPLIT = re.compile(r"\s+[–-]\s+")
TEAM_LOOKUP = {team.lower(): team for teams in TEAMS_BY_SPORT.values() for team in teams}
TEAM_SPORT_LOOKUP = {
    team.lower(): sport for sport, teams in TEAMS_BY_SPORT.items() for team in teams
}


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
    runner_number, runner_name = extract_runner(selection_line or summary)
    odds = extract_odds(selection_line or summary)
    result = extract_result(selection_line or summary)
    player_name, player_market = extract_player_market(market_line)
    market_label = player_market or market_line
    market_type = normalize_label(market_label) or detect_market(normalized, summary)
    if not runner_name and player_name:
        runner_name = player_name

    return ParsedBet(
        bet_type=detected_bet_type,
        market_type=market_type,
        sport=sport,
        league=sport,
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
    teams = []
    for part in parts:
        candidate = part.strip().split("\n")[0].strip()
        if not candidate:
            continue
        candidate = re.sub(r"\s+", " ", candidate)
        canonical = TEAM_LOOKUP.get(candidate.lower())
        teams.append(canonical or candidate)
        if len(teams) == 2:
            break
    if teams:
        return teams
    lower_event = event_line.lower()
    for normalized, canonical in TEAM_LOOKUP.items():
        if normalized in lower_event and canonical not in teams:
            teams.append(canonical)
            if len(teams) == 2:
                break
    return teams[:2]


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
    parts = TRACK_SPLIT.split(first_line, maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
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
