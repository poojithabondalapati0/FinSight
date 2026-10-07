# AI Investment Research Lab — Project Log

> Living document. Update it after every change. It answers two questions:
> **1. How does the system work?** (Sections 1–9)  **2. What has changed, and why?** (Section 10)

**Status:** Phase 1 complete (scaffolding, stub agents, end-to-end graph runs)  
**Last updated:** 2026-10-03  
**Disclaimer:** This system is decision support for research. It is **not** financial advice and does **not** place trades.

---

## 1. Overview

A multi-agent system that researches a stock and produces an evidence-backed report.
Specialised agents handle fundamentals, technicals, news/sentiment and risk. A LangGraph
orchestrator coordinates them, aggregates findings, and writes a report with bull/bear
scenarios and risk factors. RAG grounds the LLM in retrieved financial context so claims
are traceable to sources.

**Tech stack:** Python 3.11 · LangGraph · LLM API (Claude/OpenAI) · Vector DB (Chroma locally, OpenSearch/pgvector on AWS) · FastAPI · Pydantic · AWS (ECS/Lambda, S3, Secrets Manager, CloudWatch)

## 2. Architecture

```
User request (ticker)
        │
   FastAPI /research
        │
   Orchestrator (LangGraph)
   ├── Input guardrail (validate ticker, scope check)
   ├── Fan-out (parallel)
   │     ├── Fundamental agent ──► financial APIs + RAG (filings)
   │     ├── Technical agent   ──► price/indicator data
   │     ├── News/Sentiment    ──► news APIs + RAG
   │     └── Risk agent        ──► volatility, drawdown, event risk
   ├── Aggregator (merge findings, resolve conflicts)
   ├── Report writer (bull / bear / risks / evidence)
   ├── Output guardrail (citation check, no "buy/sell" orders, disclaimer)
   └── Evaluator (groundedness + completeness scores)
        │
   Structured report (JSON + Markdown) + trace
```

**Implemented in Phase 1:** the whole graph shape above, with stub agents (no data, no LLM, no RAG yet).
If the input guardrail rejects the ticker, the graph ends early and the API returns 422.

## 3. Shared State (LangGraph)

Defined in `app/state.py`; models in `app/schemas.py`.

| Field | Type | Written by | Purpose |
|---|---|---|---|
| `ticker` | str | input (normalised by input guardrail) | Target symbol |
| `fundamental` / `technical` / `sentiment` / `risk` | `Finding` | each agent | Structured findings, each with `evidence[]` and `data_available` |
| `conflicts` | list[str] | aggregator | Bullish-vs-bearish disagreements between agents |
| `retrieved_context` | list[Chunk] (append reducer) | RAG layer | Source chunks used (unused until Phase 3) |
| `report` | Report | writer, then output guardrail | Final output |
| `guardrail_flags` | list[str] (append reducer) | guardrails | Issues found |
| `eval_scores` | dict[str, float] | evaluator | Quality metrics |
| `trace` | list[TraceEvent] (append reducer) | all nodes | Audit trail |

## 4. Agents

| Agent | Inputs | Tools | Output | Status |
|---|---|---|---|---|
| Fundamental | financial statements, ratios, filings | financial API, RAG | valuation view, growth/margin/debt findings | stub |
| Technical | OHLCV price history | price API, indicator lib (RSI, MACD, SMAs) | trend, momentum, support/resistance | stub |
| News/Sentiment | recent headlines/articles | news API, RAG | sentiment score, key events, source links | stub |
| Risk | price volatility, fundamentals, news | computed metrics | risk factors with severity | stub |
| Aggregator | all four findings | — | conflict list | working (Phase 1) |
| Writer | findings + conflicts | — (LLM in a later phase) | `Report` | working, template-based |
| Evaluator | report + findings | — | completeness, groundedness | working |

## 5. Data Sources & Tool Calling

| Source | Used for | Tool name | Notes |
|---|---|---|---|
| _fill in_ (e.g. yfinance / Alpha Vantage / Finnhub) | prices, fundamentals | `get_price_history`, `get_fundamentals` | rate limits, caching |
| _fill in_ (e.g. NewsAPI / Finnhub news) | headlines | `get_news` | |

All tools have: typed input/output schemas, timeouts, retries, and response caching.

## 6. RAG Pipeline

- **Ingest:** filings/earnings text/news → clean → chunk → embed → vector DB (with metadata: ticker, source, date, URL)
- **Retrieve:** query = agent question + ticker filter, top-k, optional rerank
- **Ground:** agents must cite chunk IDs; claims without evidence are dropped or flagged
- **Embedding model / vector DB used:** _fill in_

## 7. Guardrails

Implemented in `app/guardrails.py`.

- **Input:** ticker must match `^[A-Z]{1,5}(\.[A-Z]{1,2})?$` after trim/uppercase; invalid → flag `invalid_ticker` and stop. The request schema has no trade fields, so trade execution is out of scope by construction.
- **Output:** directive phrases ("buy now", "sell immediately", …) are redacted and flagged `directive_language`; any agent with `data_available=True` but no evidence is flagged `unsupported_claims:<agent>`; the disclaimer is always re-attached.
- **Failure behaviour:** if data is missing, the report says so instead of guessing.

## 8. Evaluation

- **Groundedness:** share of analyses that cite evidence (omitted when no analyses have data)
- **Completeness:** fraction of 6 sections populated (4 analyses + bull + bear)
- **Consistency:** contradictions between agents flagged (aggregator `conflicts`)
- **Regression set:** `evals/run.py` runs a fixed ticker list (AAPL, MSFT, TSLA); saved fixtures come in Phase 2
- **Latest scores:** Phase 1 stubs → completeness 0.0 for all three tickers (expected)

## 9. How to Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # API keys not needed until Phase 4

uvicorn app.main:app --reload
curl -X POST localhost:8000/research -H "Content-Type: application/json" -d '{"ticker":"AAPL"}'

pytest
python -m evals.run
```

---

## 10. Changelog

Newest first.

### [2026-10-03] Phase 1 — Scaffolding and end-to-end skeleton
- **What changed:** added `app/` (config, schemas, state, guardrails, graph, main), `app/agents/` (4 stub analysts, aggregator, writer, evaluator), `tests/` (guardrails, graph, API), `evals/run.py`, `requirements.txt`, `.env.example`, `pytest.ini`, `.gitignore`.
- **Why:** get the full pipeline shape running early so each later phase replaces one stub instead of changing the wiring.
- **How it works now:** `POST /research` → input guardrail → four analysts in parallel → aggregator → writer → output guardrail → evaluator → JSON response with report, eval scores, flags and trace. Analysts return `data_available=False`, so the report states that no data exists yet.
- **Decisions & trade-offs:** one generic `Finding` model for all agents for now (per-agent schemas when each agent gets real data); append-reducers on `trace`, `guardrail_flags`, `retrieved_context` so parallel nodes can write safely; completeness is scored honestly (0.0 for stubs) rather than padding the report with placeholders; rejected tickers return 422 rather than an empty report.
- **Tests/eval result:** 6 tests pass; eval runner completes for AAPL/MSFT/TSLA with completeness 0.0.
- **Known issues / next:** no data, LLM or RAG yet. Phase 2: connect a price/fundamentals API with typed tools, caching, retries, and fixtures.

### [2026-10-03] Phase 0 — Project created
- **What changed:** repo initialised, this log created
- **Why:** starting point
- **How it works now:** n/a
- **Decisions & trade-offs:** _none yet_
- **Tests/eval result:** n/a
- **Known issues / next:** Phase 1 scaffolding

---

## 11. Decisions Log (ADR-lite)

| Date | Decision | Alternatives considered | Reason |
|---|---|---|---|
| 2026-10-03 | LangGraph parallel fan-out with append reducers | Sequential agents; asyncio.gather outside the graph | Keeps state/trace in one place and matches the intended architecture |
| 2026-10-03 | Honest completeness score (0.0 for stubs) | Placeholder bullets in bull/bear | Metric should reflect real coverage, not formatting |
| 2026-10-03 | Invalid ticker → 422 | Return an empty report with a flag | Clear client error; no misleading report |

## 12. Known Limitations

- Data from free APIs can be delayed or incomplete
- LLM output can still be wrong; evidence links must be checked by a human
- Not financial advice; not a trading system
- Phase 1: agents are stubs, so reports contain no real analysis yet
