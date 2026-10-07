import re

from app.schemas import DISCLAIMER, Report
from app.state import ResearchState, trace_event

TICKER_RE = re.compile(r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$")
DIRECTIVE_RE = re.compile(
    r"\b(you should|you must|i recommend)?\s*(buy|sell)\s+(now|immediately|today)\b",
    re.IGNORECASE,
)


def normalize_ticker(raw: str) -> str | None:
    t = raw.strip().upper()
    return t if TICKER_RE.match(t) else None


def redact_directives(text: str) -> tuple[str, bool]:
    new, n = DIRECTIVE_RE.subn("[removed: directive language]", text)
    return new, n > 0


def input_guardrail(state: ResearchState) -> dict:
    ticker = normalize_ticker(state.get("ticker", ""))
    if ticker is None:
        return {
            "guardrail_flags": ["invalid_ticker"],
            "trace": [trace_event("input_guardrail", "rejected: invalid ticker")],
        }
    return {"ticker": ticker, "trace": [trace_event("input_guardrail", f"accepted {ticker}")]}


def output_guardrail(state: ResearchState) -> dict:
    report: Report = state["report"]
    flags: list[str] = []

    # No direct buy/sell instructions.
    for field in ("summary",):
        new, hit = redact_directives(getattr(report, field))
        if hit:
            setattr(report, field, new)
            flags.append("directive_language")
    for field in ("bull_case", "bear_case", "risks"):
        cleaned = []
        for item in getattr(report, field):
            new, hit = redact_directives(item)
            if hit:
                flags.append("directive_language")
            cleaned.append(new)
        setattr(report, field, cleaned)

    # Claims need evidence: flag any agent that has data but cites nothing.
    for name in ("fundamental", "technical", "sentiment", "risk"):
        f = state.get(name)
        if f and f.data_available and not f.evidence:
            flags.append(f"unsupported_claims:{name}")

    report.disclaimer = DISCLAIMER
    return {
        "report": report,
        "guardrail_flags": flags,
        "trace": [trace_event("output_guardrail", f"{len(flags)} flag(s)")],
    }
