from app.schemas import Finding
from app.state import ResearchState, trace_event


def risk_node(state: ResearchState) -> dict:
    # Phase 1 stub: no data source connected yet.
    ticker = state["ticker"]
    finding = Finding(
        agent="risk",
        summary=f"No risk data connected yet for {ticker}.",
        data_available=False,
    )
    return {"risk": finding, "trace": [trace_event("risk", "stub: no data source connected")]}
