from app.schemas import Finding
from app.state import ResearchState, trace_event


def fundamental_node(state: ResearchState) -> dict:
    # Phase 1 stub: no data source connected yet.
    ticker = state["ticker"]
    finding = Finding(
        agent="fundamental",
        summary=f"No fundamental data connected yet for {ticker}.",
        data_available=False,
    )
    return {"fundamental": finding, "trace": [trace_event("fundamental", "stub: no data source connected")]}
