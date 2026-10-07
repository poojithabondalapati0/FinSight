import operator
from typing import Annotated, TypedDict

from app.schemas import Chunk, Finding, Report, TraceEvent


class ResearchState(TypedDict, total=False):
    ticker: str
    fundamental: Finding
    technical: Finding
    sentiment: Finding
    risk: Finding
    conflicts: list[str]
    # Reducers: parallel nodes may append to these in the same step.
    retrieved_context: Annotated[list[Chunk], operator.add]
    guardrail_flags: Annotated[list[str], operator.add]
    trace: Annotated[list[TraceEvent], operator.add]
    report: Report
    eval_scores: dict[str, float]


def trace_event(node: str, message: str) -> TraceEvent:
    return TraceEvent(node=node, message=message)
