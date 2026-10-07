from app.schemas import Finding
from app.state import ResearchState, trace_event


def sentiment_node(state: ResearchState) -> dict:
    # Phase 1 stub: no data source connected yet.
    ticker = state["ticker"]
    finding = Finding(
        agent="sentiment",
        summary=f"No sentiment data connected yet for {ticker}.",
        data_available=False,
    )
    return {"sentiment": finding, "trace": [trace_event("sentiment", "stub: no data source connected")]}
