import pytest
from agents.base_agent import BaseAgent, AgentResult


class EchoAgent(BaseAgent):
    """Minimal concrete agent for testing BaseAgent behavior."""

    def __init__(self):
        super().__init__("EchoAgent")

    def execute(self, payload: dict) -> dict:
        return {"echo": payload}


class BrokenAgent(BaseAgent):
    def __init__(self):
        super().__init__("BrokenAgent")

    def execute(self, payload: dict) -> dict:
        raise ValueError("intentional failure")


def test_successful_run_returns_agent_result():
    result = EchoAgent().run({"key": "value"})
    assert isinstance(result, AgentResult)
    assert result.success is True
    assert result.output == {"echo": {"key": "value"}}
    assert result.duration_ms >= 0
    assert result.error is None


def test_failed_run_captures_error():
    result = BrokenAgent().run({})
    assert result.success is False
    assert result.output is None
    assert "intentional failure" in result.error


def test_health_check_default_true():
    assert EchoAgent().health_check() is True


def test_agent_name_set_correctly():
    assert EchoAgent().name == "EchoAgent"
