from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Odds1X2Point:
    provider: str
    timestamp: str
    home: float
    draw: float
    away: float


@dataclass(frozen=True)
class HandicapPoint:
    provider: str
    timestamp: str
    home_line: float
    home_water: float
    away_water: float


@dataclass(frozen=True)
class TotalPoint:
    provider: str
    timestamp: str
    line: float
    over_water: float
    under_water: float


@dataclass(frozen=True)
class MatchResult:
    home_goals: int
    away_goals: int


@dataclass
class MatchSnapshot:
    match_id: str
    competition: str
    kickoff: str
    home: str
    away: str
    odds_1x2: List[Odds1X2Point] = field(default_factory=list)
    asian_handicap: List[HandicapPoint] = field(default_factory=list)
    totals: List[TotalPoint] = field(default_factory=list)
    strength: Dict[str, float] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    lineup: Dict[str, float] = field(default_factory=dict)
    result: Optional[MatchResult] = None


def _float_or_none(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    return float(value)


def match_from_dict(raw: Dict[str, Any]) -> MatchSnapshot:
    odds = [
        Odds1X2Point(
            provider=str(item.get("provider", "average")).lower(),
            timestamp=str(item.get("timestamp", "")),
            home=float(item["home"]),
            draw=float(item["draw"]),
            away=float(item["away"]),
        )
        for item in raw.get("odds_1x2", [])
    ]
    handicaps = [
        HandicapPoint(
            provider=str(item.get("provider", "average")).lower(),
            timestamp=str(item.get("timestamp", "")),
            home_line=float(item["home_line"]),
            home_water=float(item["home_water"]),
            away_water=float(item["away_water"]),
        )
        for item in raw.get("asian_handicap", [])
    ]
    totals = [
        TotalPoint(
            provider=str(item.get("provider", "average")).lower(),
            timestamp=str(item.get("timestamp", "")),
            line=float(item["line"]),
            over_water=float(item["over_water"]),
            under_water=float(item["under_water"]),
        )
        for item in raw.get("totals", [])
    ]
    result = None
    if raw.get("result"):
        result = MatchResult(
            home_goals=int(raw["result"]["home_goals"]),
            away_goals=int(raw["result"]["away_goals"]),
        )
    return MatchSnapshot(
        match_id=str(raw.get("match_id", "")),
        competition=str(raw.get("competition", "")),
        kickoff=str(raw.get("kickoff", "")),
        home=str(raw["home"]),
        away=str(raw["away"]),
        odds_1x2=odds,
        asian_handicap=handicaps,
        totals=totals,
        strength={k: float(v) for k, v in raw.get("strength", {}).items() if _float_or_none(v) is not None},
        context=raw.get("context", {}),
        lineup={k: float(v) for k, v in raw.get("lineup", {}).items()},
        result=result,
    )


def load_matches(payload: Dict[str, Any]) -> List[MatchSnapshot]:
    return [match_from_dict(item) for item in payload.get("matches", [])]
