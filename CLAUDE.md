# AgentOps — Member Churn Prediction

## What this project does
Predicts RetainIQ member intent-to-churn 30-60 days before cancellation using
real-time behavioral signals, an XGBoost/LightGBM ensemble, and a Claude-powered
LLM explanation layer. Ten agents operate across two layers:
- Static pipeline: deterministic batch scoring (signal → feature → score → explain → intervene)
- Dynamic layer: LLM-powered reasoning, strategy, experimentation, and memory

## Agent hierarchy
OrchestratorAgent is the entry point for all non-batch requests.
It uses Claude to reason about the task and decide which agents to activate.

PersonalizationStrategistAgent runs BEFORE InterventionAgent.
It scores the intervention opportunity and decides:
should we personalize (yes/no), what channel, what offer type, what timing.
Output is a PersonalizationDecision object with a priority score (1-10 per axis).

ExperimentationAgent runs AFTER interventions have been delivered.
It measures causal lift (CUPED / DiD) and writes results to MemoryAgent.

MemoryAgent is a read/write knowledge base (Redis + structured JSON).
Every agent reads from memory at session start before generating recommendations.
Every agent writes lessons learned after task completion.
Memory compounds: the system gets smarter after every experiment.

The static ChurnPredictionPipeline (pipeline/churn_pipeline.py) handles batch
scoring only. The OrchestratorAgent handles everything else.

## Architecture decisions
- Agents are stateless classes inheriting BaseAgent; state lives in Redis
- All agent outputs are written to audit_log.py before downstream routing
- LLM explainer always PII-scrubs before calling Anthropic API
- PersonalizationStrategistAgent must approve before InterventionAgent routes
- Intervention rate is capped at 15% of active members per day (guardrails.py)
- Model retrains automatically when PSI drift > 0.2 (drift_detector.py)
- MemoryAgent knowledge base key schema: memory:{agent_name}:{topic}:{date}

## Personalization decision axes (PersonalizationStrategistAgent)
Score each axis 1-10. Only proceed if total score >= 30/50.
- Customer Value: does this member benefit from the intervention?
- Business Value: what is the estimated incremental revenue lift?
- Technical Feasibility: is the data quality sufficient?
- Confidence Level: how certain are we of the churn signal?
- Strategic Alignment: does this fit RetainIQ membership growth goals?

## Code conventions
- Python 3.10+, type hints everywhere, Pydantic for all schemas
- Black formatting, isort imports, mypy strict mode
- Each agent has its own test file in tests/unit/
- Never hardcode API keys; use .env via python-dotenv
- Commit messages: feat/fix/refactor/test/docs prefix

## Key files to understand first
- agents/base_agent.py — all agents inherit from here
- pipeline/audit_log.py — append-only audit trail
- pipeline/churn_pipeline.py — static batch scoring pipeline
- agents/orchestrator/agent.py — CEO agent, dynamic routing
- agents/memory/knowledge_store.py — shared knowledge base
- data/schemas/member_event.py — the core data contract

## What NOT to do
- Do not put business logic in api/routes/ — it belongs in agents/
- Do not call Anthropic API without going through llm_explainer/claude_client.py
- Do not skip the PII scrubber before any LLM call
- Do not call InterventionAgent without PersonalizationStrategistAgent approval
- Do not write to MemoryAgent without also logging to audit_log.py
- Do not modify main branch directly; always use a feature branch
