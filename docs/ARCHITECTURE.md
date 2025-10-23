# WhatsApp Agent — Architecture (PR1 snapshot)

## Components:
- **apps/api** — FastAPI backend (primary integration point). Exposes REST APIs and webhooks.
- **apps/ui** — lightweight placeholder UI (static) for dev.
- **apps/api/llm_stub** — local LLM stub for deterministic AI responses in dev.
- **infra** — docker-compose to orchestrate Postgres, Redis, MinIO, Adminer, llm-stub, and api service.

## Layers:
- **API layer**: FastAPI, Pydantic schemas, central config.
- **Persistence**: Postgres (SQLAlchemy + Alembic planned in next PR).
- **Queue**: Redis + Celery planned in PR 4.
- **AI**: LangChain patterns and adapters (OpenAI + local stub) planned in PR 1–3; local stub runs at `/v1/complete`.
- **Connectors**: pluggable connectors (playwright experimental, whatsapp cloud adapter stub) — planned in PR 5.

## Compliance:
- Store opt-in evidence at capture time (timestamp, IP, source, opt-in copy).
- Unsubscribe/suppression list enforced at messaging layer.
- Playwright connector is experimental — use only for local testing.