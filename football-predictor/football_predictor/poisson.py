from __future__ import annotations

import math
from typing import Dict, List, Tuple


def poisson_pmf(lam: float, max_goals: int) -> List[float]:
    lam = max(lam, 0.01)
    values = []
    for goals in range(max_goals + 1):
        values.append(math.exp(-lam) * (lam ** goals) / math.factorial(goals))
    total = sum(values)
    return [value / total for value in values]


def score_grid(home_xg: float, away_xg: float, max_goals: int = 8) -> Dict[Tuple[int, int], float]:
    home_dist = poisson_pmf(home_xg, max_goals)
    away_dist = poisson_pmf(away_xg, max_goals)
    grid: Dict[Tuple[int, int], float] = {}
    for home_goals, home_prob in enumerate(home_dist):
        for away_goals, away_prob in enumerate(away_dist):
            grid[(home_goals, away_goals)] = home_prob * away_prob
    total = sum(grid.values())
    return {score: prob / total for score, prob in grid.items()}


def outcome_probabilities(grid: Dict[Tuple[int, int], float]) -> Dict[str, float]:
    probs = {"home": 0.0, "draw": 0.0, "away": 0.0}
    for (home_goals, away_goals), probability in grid.items():
        if home_goals > away_goals:
            probs["home"] += probability
        elif home_goals == away_goals:
            probs["draw"] += probability
        else:
            probs["away"] += probability
    return probs


def top_scores(grid: Dict[Tuple[int, int], float], limit: int = 5) -> List[Tuple[int, int, float]]:
    ranked = sorted(grid.items(), key=lambda item: item[1], reverse=True)
    return [(score[0], score[1], probability) for score, probability in ranked[:limit]]

