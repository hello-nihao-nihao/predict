from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Sequence, Tuple, TypeVar

from .types import HandicapPoint, Odds1X2Point, TotalPoint

T = TypeVar("T")


def no_vig_1x2(home: float, draw: float, away: float) -> Dict[str, float]:
    raw = {"home": 1.0 / home, "draw": 1.0 / draw, "away": 1.0 / away}
    total = sum(raw.values())
    return {key: value / total for key, value in raw.items()}


def weighted_average_probabilities(
    points: Sequence[Odds1X2Point],
    provider_weights: Dict[str, float],
) -> Dict[str, float]:
    latest = latest_by_provider(points)
    if not latest:
        return {"home": 0.36, "draw": 0.28, "away": 0.36}

    totals = {"home": 0.0, "draw": 0.0, "away": 0.0}
    weight_sum = 0.0
    for point in latest:
        weight = provider_weights.get(point.provider, provider_weights.get("average", 1.0))
        probs = no_vig_1x2(point.home, point.draw, point.away)
        for key in totals:
            totals[key] += probs[key] * weight
        weight_sum += weight
    return {key: totals[key] / weight_sum for key in totals}


def movement_1x2(
    points: Sequence[Odds1X2Point],
    provider_weights: Dict[str, float],
) -> Dict[str, float]:
    first = earliest_timestamp_points(points)
    latest = latest_timestamp_points(points)
    if not first or not latest:
        return {"home": 0.0, "draw": 0.0, "away": 0.0}
    start = weighted_average_probabilities(first, provider_weights)
    end = weighted_average_probabilities(latest, provider_weights)
    return {key: end[key] - start[key] for key in end}


def latest_by_provider(points: Sequence[T]) -> List[T]:
    grouped: Dict[str, List[T]] = defaultdict(list)
    for point in points:
        grouped[getattr(point, "provider")].append(point)
    return [sorted(items, key=lambda item: getattr(item, "timestamp"))[-1] for items in grouped.values()]


def first_by_provider(points: Sequence[T]) -> List[T]:
    grouped: Dict[str, List[T]] = defaultdict(list)
    for point in points:
        grouped[getattr(point, "provider")].append(point)
    return [sorted(items, key=lambda item: getattr(item, "timestamp"))[0] for items in grouped.values()]


def earliest_timestamp_points(points: Sequence[T]) -> List[T]:
    if not points:
        return []
    first_timestamp = sorted(getattr(point, "timestamp") for point in points)[0]
    return [point for point in points if getattr(point, "timestamp") == first_timestamp]


def latest_timestamp_points(points: Sequence[T]) -> List[T]:
    if not points:
        return []
    last_timestamp = sorted(getattr(point, "timestamp") for point in points)[-1]
    return [point for point in points if getattr(point, "timestamp") == last_timestamp]


def latest_handicap(points: Sequence[HandicapPoint]) -> HandicapPoint:
    if not points:
        return HandicapPoint("synthetic", "", 0.0, 0.95, 0.95)
    return sorted(points, key=lambda item: item.timestamp)[-1]


def first_handicap(points: Sequence[HandicapPoint]) -> HandicapPoint:
    if not points:
        return HandicapPoint("synthetic", "", 0.0, 0.95, 0.95)
    return sorted(points, key=lambda item: item.timestamp)[0]


def average_total_line(points: Sequence[TotalPoint]) -> float:
    latest = latest_by_provider(points)
    if not latest:
        return 2.45
    weight = 0.0
    total = 0.0
    for point in latest:
        total += point.line
        weight += 1.0
    return total / weight


def total_pressure(points: Sequence[TotalPoint]) -> Tuple[float, str]:
    latest = latest_by_provider(points)
    if not latest:
        return 0.0, "no total-goals market supplied"

    over_edges = [point.under_water - point.over_water for point in latest]
    avg_edge = sum(over_edges) / len(over_edges)
    if avg_edge > 0.08:
        return 0.06, "over price is lower than under, total expectation leans higher"
    if avg_edge < -0.08:
        return -0.06, "under price is lower than over, total expectation leans lower"
    return 0.0, "over/under water is balanced"
