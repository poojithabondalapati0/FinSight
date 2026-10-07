from app.agents.aggregator import AGENTS
from app.schemas import Report
from app.state import ResearchState, trace_event


def writer_node(state: ResearchState) -> dict:
    findings = [state[a] for a in AGENTS if a in state]
    available = [f for f in findings if f.data_available]

    if available:
        summary = " ".join(f.summary for f in available)
    else:
        summary = "No analysis data is available yet; agents are not connected to data sources."

    if state.get("conflicts"):
        summary += " Conflicting signals: " + "; ".join(state["conflicts"]) + "."

    report = Report(
        ticker=state["ticker"],
        summary=summary,
        bull_case=[f.summary for f in available if f.stance == "bullish"],
        bear_case=[f.summary for f in available if f.stance == "bearish"],
        risks=[state["risk"].summary] if "risk" in state and state["risk"].data_available else [],
        evidence=[e for f in available for e in f.evidence],
    )
    return {"report": report, "trace": [trace_event("writer", "report drafted")]}
