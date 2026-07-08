from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .backtest import backtest
from .defaults import DEFAULT_MODEL_CONFIG
from .model_v5 import predict_match
from .reporting import predictions_to_json, predictions_to_markdown
from .sample_data import sample_payload
from .types import load_matches


DEFAULT_SAMPLE = Path("data") / "samples" / "matches.json"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="football", description="Football prediction CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-sample", help="Write a sample match JSON file")
    init_parser.add_argument("--output", default=str(DEFAULT_SAMPLE))

    predict_parser = subparsers.add_parser("predict", help="Predict matches from a JSON snapshot")
    predict_parser.add_argument("--input", required=True)
    predict_parser.add_argument("--config")
    predict_parser.add_argument("--format", choices=["markdown", "json"], default="markdown")

    backtest_parser = subparsers.add_parser("backtest", help="Evaluate matches with known results")
    backtest_parser.add_argument("--input", required=True)
    backtest_parser.add_argument("--config")

    template_parser = subparsers.add_parser("snapshot-template", help="Print an empty match template")

    args = parser.parse_args(argv)

    if args.command == "init-sample":
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(sample_payload(), ensure_ascii=False, indent=2), encoding="utf-8")
        print(str(output))
        return 0

    if args.command == "snapshot-template":
        print(json.dumps(_empty_template(), ensure_ascii=False, indent=2))
        return 0

    if args.command == "predict":
        payload = _load_json(Path(args.input))
        config = _load_config(args.config)
        matches = load_matches(payload)
        predictions = [predict_match(match, config) for match in matches]
        if args.format == "json":
            print(predictions_to_json(predictions))
        else:
            print(predictions_to_markdown(predictions))
        return 0

    if args.command == "backtest":
        payload = _load_json(Path(args.input))
        config = _load_config(args.config)
        matches = load_matches(payload)
        print(json.dumps(backtest(matches, config), indent=2))
        return 0

    parser.error("unknown command")
    return 2


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_config(path: Optional[str]) -> Dict[str, Any]:
    if path:
        return _load_json(Path(path))
    return dict(DEFAULT_MODEL_CONFIG)


def _empty_template() -> Dict[str, Any]:
    return {
        "matches": [
            {
                "match_id": "",
                "competition": "",
                "kickoff": "",
                "home": "",
                "away": "",
                "odds_1x2": [
                    {"provider": "average", "timestamp": "T-48", "home": 0.0, "draw": 0.0, "away": 0.0}
                ],
                "asian_handicap": [
                    {"provider": "average", "timestamp": "T-48", "home_line": 0.0, "home_water": 0.0, "away_water": 0.0}
                ],
                "totals": [
                    {"provider": "average", "timestamp": "T-48", "line": 2.5, "over_water": 0.0, "under_water": 0.0}
                ],
                "strength": {"home_elo": None, "away_elo": None},
                "context": {
                    "knockout": False,
                    "home_rest_days": None,
                    "away_rest_days": None,
                    "home_travel_km": None,
                    "away_travel_km": None,
                    "home_host_edge": False,
                    "weather_temp_c": None
                },
                "lineup": {"home_xg_delta": 0.0, "away_xg_delta": 0.0, "total_xg_delta": 0.0},
                "result": None
            }
        ]
    }
