from __future__ import annotations

import json
from typing import Iterable, List

from .model_v5 import Prediction


def predictions_to_json(predictions: Iterable[Prediction]) -> str:
    payload = []
    for item in predictions:
        payload.append(
            {
                "match_id": item.match_id,
                "home": item.home,
                "away": item.away,
                "probabilities": item.probabilities,
                "market_probabilities": item.market_probabilities,
                "xg": item.xg,
                "top_scores": item.top_scores,
                "confidence": item.confidence,
                "rationale": item.rationale,
            }
        )
    return json.dumps({"predictions": payload}, ensure_ascii=False, indent=2)


def predictions_to_markdown(predictions: List[Prediction]) -> str:
    lines = ["# Football Predictor v5", ""]
    for item in predictions:
        lines.append("## %s vs %s" % (item.home, item.away))
        lines.append("")
        lines.append("| Outcome | Probability |")
        lines.append("|---|---:|")
        lines.append("| Home | %.1f%% |" % (item.probabilities["home"] * 100))
        lines.append("| Draw | %.1f%% |" % (item.probabilities["draw"] * 100))
        lines.append("| Away | %.1f%% |" % (item.probabilities["away"] * 100))
        lines.append("")
        lines.append("Expected goals: %s %.2f, %s %.2f" % (item.home, item.xg["home"], item.away, item.xg["away"]))
        lines.append("Confidence: `%s`" % item.confidence)
        lines.append("")
        lines.append("| Score | Probability |")
        lines.append("|---|---:|")
        for score in item.top_scores:
            lines.append("| %s | %.1f%% |" % (score["score"], score["probability"] * 100))
        lines.append("")
        lines.append("Rationale:")
        for note in item.rationale:
            lines.append("- %s" % note)
        lines.append("")
    return "\n".join(lines)

