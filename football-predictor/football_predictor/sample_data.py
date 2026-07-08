from __future__ import annotations

from typing import Any, Dict


def sample_payload() -> Dict[str, Any]:
    return {
        "matches": [
            {
                "match_id": "sample-france-morocco",
                "competition": "World Cup",
                "kickoff": "2026-07-10T03:00:00+08:00",
                "home": "France",
                "away": "Morocco",
                "odds_1x2": [
                    {"provider": "average", "timestamp": "T-48", "home": 1.66, "draw": 3.90, "away": 5.60},
                    {"provider": "bet365", "timestamp": "T-24", "home": 1.62, "draw": 3.95, "away": 6.00},
                    {"provider": "pinnacle", "timestamp": "T-6", "home": 1.64, "draw": 3.88, "away": 5.80}
                ],
                "asian_handicap": [
                    {"provider": "average", "timestamp": "T-48", "home_line": -0.75, "home_water": 0.92, "away_water": 0.96},
                    {"provider": "average", "timestamp": "T-6", "home_line": -0.75, "home_water": 0.86, "away_water": 1.02}
                ],
                "totals": [
                    {"provider": "average", "timestamp": "T-48", "line": 2.5, "over_water": 0.96, "under_water": 0.90},
                    {"provider": "average", "timestamp": "T-6", "line": 2.5, "over_water": 1.00, "under_water": 0.84}
                ],
                "strength": {"home_elo": 2050, "away_elo": 1885},
                "context": {"knockout": True, "home_rest_days": 5, "away_rest_days": 5},
                "lineup": {"home_xg_delta": 0.0, "away_xg_delta": 0.0}
            },
            {
                "match_id": "sample-spain-belgium",
                "competition": "World Cup",
                "kickoff": "2026-07-11T03:00:00+08:00",
                "home": "Spain",
                "away": "Belgium",
                "odds_1x2": [
                    {"provider": "average", "timestamp": "T-48", "home": 1.70, "draw": 3.80, "away": 5.10},
                    {"provider": "bet365", "timestamp": "T-24", "home": 1.64, "draw": 4.00, "away": 5.40},
                    {"provider": "pinnacle", "timestamp": "T-6", "home": 1.66, "draw": 3.95, "away": 5.30}
                ],
                "asian_handicap": [
                    {"provider": "average", "timestamp": "T-48", "home_line": -0.75, "home_water": 0.98, "away_water": 0.90},
                    {"provider": "average", "timestamp": "T-6", "home_line": -0.75, "home_water": 0.88, "away_water": 1.00}
                ],
                "totals": [
                    {"provider": "average", "timestamp": "T-48", "line": 2.5, "over_water": 0.94, "under_water": 0.92},
                    {"provider": "average", "timestamp": "T-6", "line": 2.5, "over_water": 0.86, "under_water": 1.02}
                ],
                "strength": {"home_elo": 2040, "away_elo": 1900},
                "context": {"knockout": True, "home_rest_days": 5, "away_rest_days": 4},
                "lineup": {"home_xg_delta": 0.0, "away_xg_delta": 0.05}
            }
        ]
    }

