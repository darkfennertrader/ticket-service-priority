from typing import Dict, Any
from datetime import datetime


# ---------------------------------------------------------------------
# Friendly date-time formatter
# ---------------------------------------------------------------------
def _pretty(ts: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    2025-07-06T21:44:05Z  →  2025-07-06 21:44:05
    """
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime(fmt)


def _humanise_dates(t: Dict[str, Any]) -> Dict[str, Any]:
    return {
        **t,
        "created_at": _pretty(t["created_at"]),
        "updated_at": _pretty(t["updated_at"]),
    }
