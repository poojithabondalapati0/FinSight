from app.state import ResearchState, trace_event

AGENTS = ("fundamental", "technical", "sentiment", "risk")


def aggregator_node(state: ResearchState) -> dict:
    available = [state[a] for a in AGENTS if a in state and state[a].data_available]
    stances = {f.stance for f in available} & {"bullish", "bearish"}
    conflicts = []
    if stances == {"bullish", "bearish"}:
        bull = [f.agent for f in available if f.stance == "bullish"]
        bear = [f.agent for f in available if f.stance == "bearish"]
        conflicts.append(f"Bullish ({', '.join(bull)}) vs bearish ({', '.join(bear)})")
    return {
        "conflicts": conflicts,
        "trace": [trace_event("aggregator", f"{len(available)} agent(s) with data, {len(conflicts)} conflict(s)")],
    }
