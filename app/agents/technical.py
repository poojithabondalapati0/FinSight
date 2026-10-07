from app.schemas import Finding
from app.state import ResearchState, trace_event


def technical_node(state: ResearchState) -> dict:
    # Phase 1 stub: no data source connected yet.
    ticker = state["ticker"]
    finding = Finding(
        agent="technical",
        summary=f"No technical data connected yet for {ticker}.",
        data_available=False,
    )
    return {"technical": finding, "trace": [trace_event("technical", "stub: no data source connected")]}
