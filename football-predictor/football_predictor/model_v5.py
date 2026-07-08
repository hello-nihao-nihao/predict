from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from .odds import (
    average_total_line,
    first_handicap,
    latest_handicap,
    movement_1x2,
    total_pressure,
    weighted_average_probabilities,
)
from .poisson import outcome_probabilities, score_grid, top_scores
from .types import MatchSnapshot


@dataclass
class Prediction:
    match_id: str
    home: str
    away: str
    probabilities: Dict[str, float]
    market_probabilities: Dict[str, float]
    xg: Dict[str, float]
    top_scores: List[Dict[str, Any]]
    confidence: str
    rationale: List[str]


def predict_match(match: MatchSnapshot, config: Dict[str, Any]) -> Prediction:
    weights = config.get("provider_weights", {})
    market_probs = weighted_average_probabilities(match.odds_1x2, weights)
    movement = movement_1x2(match.odds_1x2, weights)

    total_goals = average_total_line(match.totals)
    total_delta, total_note = total_pressure(match.totals)
    total_goals += total_delta

    if bool(match.context.get("knockout", False)):
        total_goals -= float(config.get("knockout_total_penalty", 0.0))

    temp_c = match.context.get("weather_temp_c")
    if temp_c is not None and float(temp_c) >= float(config.get("weather_total_penalty_hot_c", 99)):
        total_goals -= float(config.get("weather_total_penalty", 0.0))

    probability_diff = market_probs["home"] - market_probs["away"]
    goal_diff = float(config.get("prob_goal_diff_scale", 1.25)) * probability_diff

    home_elo = match.strength.get("home_elo")
    away_elo = match.strength.get("away_elo")
    if home_elo is not None and away_elo is not None:
        goal_diff += ((home_elo - away_elo) / 100.0) * float(config.get("elo_goal_diff_per_100", 0.12))

    if bool(match.context.get("home_host_edge", False)):
        goal_diff += float(config.get("host_xg_bonus", 0.12))

    rest_home = match.context.get("home_rest_days")
    rest_away = match.context.get("away_rest_days")
    if rest_home is not None and rest_away is not None:
        goal_diff += (float(rest_home) - float(rest_away)) * float(config.get("rest_day_xg_per_day", 0.03))

    travel_home = float(match.context.get("home_travel_km", 0.0) or 0.0)
    travel_away = float(match.context.get("away_travel_km", 0.0) or 0.0)
    travel_penalty = float(config.get("travel_xg_penalty_per_1000km", 0.02))
    goal_diff += ((travel_away - travel_home) / 1000.0) * travel_penalty

    goal_diff += float(match.lineup.get("home_xg_delta", 0.0))
    goal_diff -= float(match.lineup.get("away_xg_delta", 0.0))
    total_goals += float(match.lineup.get("total_xg_delta", 0.0))

    total_goals = max(total_goals, 1.4)
    goal_diff = max(min(goal_diff, total_goals - 0.25), -total_goals + 0.25)

    home_xg = max(0.15, (total_goals + goal_diff) / 2.0)
    away_xg = max(0.15, (total_goals - goal_diff) / 2.0)

    grid = score_grid(home_xg, away_xg, int(config.get("score_max_goals", 8)))
    poisson_probs = outcome_probabilities(grid)
    blended = _blend_probabilities(poisson_probs, market_probs, float(config.get("market_blend", 0.45)))
    blended = _apply_market_structure_adjustment(blended, match, movement)

    confidence = _confidence(match, blended)
    rationale = _rationale(match, market_probs, movement, total_note)

    return Prediction(
        match_id=match.match_id,
        home=match.home,
        away=match.away,
        probabilities=blended,
        market_probabilities=market_probs,
        xg={"home": home_xg, "away": away_xg},
        top_scores=[
            {"score": f"{home_goals}-{away_goals}", "probability": probability}
            for home_goals, away_goals, probability in top_scores(grid)
        ],
        confidence=confidence,
        rationale=rationale,
    )


def _blend_probabilities(model: Dict[str, float], market: Dict[str, float], market_weight: float) -> Dict[str, float]:
    blended = {
        key: model[key] * (1.0 - market_weight) + market[key] * market_weight
        for key in ("home", "draw", "away")
    }
    return _normalize(blended)


def _apply_market_structure_adjustment(
    probs: Dict[str, float],
    match: MatchSnapshot,
    movement: Dict[str, float],
) -> Dict[str, float]:
    if not match.asian_handicap:
        return probs

    start = first_handicap(match.asian_handicap)
    end = latest_handicap(match.asian_handicap)
    adjusted = dict(probs)

    home_is_favorite = end.home_line < -0.25
    handicap_did_not_deepen = abs(end.home_line - start.home_line) < 0.01
    home_got_bet = movement.get("home", 0.0) > 0.025 or end.home_water < start.home_water - 0.04

    if home_is_favorite and handicap_did_not_deepen and home_got_bet:
        adjusted["home"] -= 0.025
        adjusted["draw"] += 0.017
        adjusted["away"] += 0.008

    away_is_favorite = end.home_line > 0.25
    away_got_bet = movement.get("away", 0.0) > 0.025 or end.away_water < start.away_water - 0.04
    if away_is_favorite and handicap_did_not_deepen and away_got_bet:
        adjusted["away"] -= 0.025
        adjusted["draw"] += 0.017
        adjusted["home"] += 0.008

    return _normalize(adjusted)


def _normalize(values: Dict[str, float]) -> Dict[str, float]:
    clipped = {key: max(0.01, value) for key, value in values.items()}
    total = sum(clipped.values())
    return {key: value / total for key, value in clipped.items()}


def _confidence(match: MatchSnapshot, probs: Dict[str, float]) -> str:
    ordered = sorted(probs.values(), reverse=True)
    edge = ordered[0] - ordered[1]
    has_market = bool(match.odds_1x2 and match.asian_handicap and match.totals)
    if has_market and edge >= 0.24:
        return "high"
    if has_market and edge >= 0.14:
        return "medium"
    return "low"


def _rationale(
    match: MatchSnapshot,
    market_probs: Dict[str, float],
    movement: Dict[str, float],
    total_note: str,
) -> List[str]:
    notes = [
        "no-vig 1X2 market prior: home %.1f%%, draw %.1f%%, away %.1f%%"
        % (market_probs["home"] * 100, market_probs["draw"] * 100, market_probs["away"] * 100),
        "1X2 movement: home %+0.1fpp, draw %+0.1fpp, away %+0.1fpp"
        % (movement["home"] * 100, movement["draw"] * 100, movement["away"] * 100),
        total_note,
    ]
    if match.asian_handicap:
        start = first_handicap(match.asian_handicap)
        end = latest_handicap(match.asian_handicap)
        notes.append(
            "Asian handicap moved from home %.2f %.3f/%.3f to home %.2f %.3f/%.3f"
            % (
                start.home_line,
                start.home_water,
                start.away_water,
                end.home_line,
                end.home_water,
                end.away_water,
            )
        )
    if match.lineup:
        notes.append("lineup adjustment applied: %s" % match.lineup)
    if match.context:
        context_keys = ", ".join(sorted(match.context.keys()))
        notes.append("context features used: %s" % context_keys)
    return notes

