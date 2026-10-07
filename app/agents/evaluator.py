from app.agents.aggregator import AGENTS
from app.state import ResearchState, trace_event


def evaluator_node(state: ResearchState) -> dict:
    report = state["report"]
    available = [state[a] for a in AGENTS if a in state and state[a].data_available]

    # Completeness: 6 sections (4 analyses + bull + bear), fraction populated.
    populated = len(available) + bool(report.bull_case) + bool(report.bear_case)
    scores = {"completeness": round(populated / 6, 2)}

    # Groundedness: share of analyses that cite evidence. Omitted if no analyses exist.
    if available:
        scores["groundedness"] = round(sum(1 for f in available if f.evidence) / len(available), 2)

    return {"eval_scores": scores, "trace": [trace_event("evaluator", f"scores={scores}")]}
