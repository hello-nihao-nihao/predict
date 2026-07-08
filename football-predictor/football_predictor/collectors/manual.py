from __future__ import annotations

from typing import Any, Dict, Iterable, List


def build_match_payload(matches: Iterable[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Wrap hand-collected normalized match dictionaries for the CLI."""
    return {"matches": list(matches)}

