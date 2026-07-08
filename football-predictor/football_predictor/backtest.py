from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List

from .model_v5 import predict_match
from .types import MatchSnapshot


def backtest(matches: Iterable[MatchSnapshot], config: Dict[str, Any]) -> Dict[str, float]:
    rows: List[Dict[str, float]] = []
    for match in matches:
        if match.result is None:
            continue
        prediction = predict_match(match, config)
        actual = _actual_outcome(match.result.home_goals, match.result.away_goals)
        probability = max(prediction.probabilities[actual], 1e-9)
        rows.append(
            {
                "hit": 1.0 if _predicted_outcome(prediction.probabilities) == actual else 0.0,
                "log_loss": -math.log(probability),
                "brier": _brier(prediction.probabilities, actual),
            }
        )

    if not rows:
        return {"matches": 0.0, "accuracy": 0.0, "log_loss": 0.0, "brier": 0.0}

    count = float(len(rows))
    return {
        "matches": count,
        "accuracy": sum(row["hit"] for row in rows) / count,
        "log_loss": sum(row["log_loss"] for row in rows) / count,
        "brier": sum(row["brier"] for row in rows) / count,
    }


def _actual_outcome(home_goals: int, away_goals: int) -> str:
    if home_goals > away_goals:
        return "home"
    if home_goals == away_goals:
        return "draw"
    return "away"


def _predicted_outcome(probabilities: Dict[str, float]) -> str:
    return max(probabilities.items(), key=lambda item: item[1])[0]


def _brier(probabilities: Dict[str, float], actual: str) -> float:
    return sum((probabilities[key] - (1.0 if key == actual else 0.0)) ** 2 for key in ("home", "draw", "away"))

