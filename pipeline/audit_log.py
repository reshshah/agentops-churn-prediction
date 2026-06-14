import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

LOG_DIR = Path(os.getenv("AUDIT_LOG_DIR", "logs/audit"))


class AuditLog:
    """Tamper-resistant append-only audit trail. Every agent writes here before
    passing output downstream — enables pipeline replay and governance review."""

    def __init__(self):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self._path = LOG_DIR / f"audit_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl"

    def log(self, agent: str, event: str, **kwargs) -> None:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "agent": agent,
            "event": event,
            **kwargs,
        }
        try:
            with open(self._path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Audit log write failed: {e}")
