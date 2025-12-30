from app.services.parsers.sportsbet import parse_summary


def test_parse_summary_extracts_racing_details():
    summary = """Flemington - R7 Lexus Melbourne Cup
 Win or Place
2. Buckaroo @ 12.00 (Win)"""

    parsed = parse_summary(summary)

    assert parsed.bet_type == "Single"
    assert parsed.market_type == "Win or Place"
    assert parsed.track == "Flemington"
    assert parsed.race == "R7 Lexus Melbourne Cup"
    assert parsed.runner_number == "2"
    assert parsed.runner_name == "Buckaroo"
    assert parsed.result == "Win"


def test_parse_summary_detects_teams_and_multi():
    summary = """Brisbane Lions v Gold Coast SUNS
 Same Game Multi"""

    parsed = parse_summary(summary)

    assert parsed.bet_type == "Same Game Multi"
    assert parsed.market_type == "Same Game Multi"
    assert parsed.teams == ["Brisbane Lions", "Gold Coast Suns"]
    assert parsed.sport == "AFL"


def test_parse_summary_extracts_player_and_market():
    summary = """Miami Heat At New York Knicks
 Jimmy Butler - Rebounds
 Jimmy Butler Over (6.5) @ 1.74 (Win)"""

    parsed = parse_summary(summary)

    assert parsed.market_type == "Rebounds"
    assert parsed.runner_name == "Jimmy Butler"


def test_parse_summary_trims_racing_selection_numbers_from_market():
    summary = """Sale - R1 Ladbrokes Sale Cup
  Fixed Odds Boxed Trifecta (2, 3, 4)"""

    parsed = parse_summary(summary)

    assert parsed.market_type == "Fixed Odds Boxed Trifecta"
