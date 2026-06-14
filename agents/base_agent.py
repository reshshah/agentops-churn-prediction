import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from pipeline.audit_log import AuditLog

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    agent_name: str
    success: bool
    output: Any
    duration_ms: float
    metadata: dict = field(default_factory=dict)
    error: str | None = None


class BaseAgent(ABC):
    """All AgentOps agents inherit from this class."""

    def __init__(self, name: str):
        self.name = name
        self.audit = AuditLog()

    def run(self, payload: dict) -> AgentResult:
        start = time.perf_counter()
        self.audit.log(agent=self.name, event="started", payload_keys=list(payload.keys()))
        try:
            output = self.execute(payload)
            duration = (time.perf_counter() - start) * 1000
            self.audit.log(agent=self.name, event="completed", duration_ms=round(duration))
            return AgentResult(
                agent_name=self.name,
                success=True,
                output=output,
                duration_ms=round(duration),
            )
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            self.audit.log(agent=self.name, event="error", error=str(e))
            logger.error(f"[{self.name}] failed: {e}", exc_info=True)
            return AgentResult(
                agent_name=self.name,
                success=False,
                output=None,
                duration_ms=round(duration),
                error=str(e),
            )

    @abstractmethod
    def execute(self, payload: dict) -> Any:
        ...

    def health_check(self) -> bool:
        return True
