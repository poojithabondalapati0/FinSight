from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

DISCLAIMER = (
    "This report is decision support for research only. It is not financial "
    "advice and does not place trades."
)

Stance = Literal["bullish", "bearish", "neutral", "unknown"]


class Evidence(BaseModel):
    source: str
    chunk_id: str | None = None
    url: str | None = None
    snippet: str = ""


class Chunk(BaseModel):
    id: str
    ticker: str
    source: str
    date: str | None = None
    url: str | None = None
    text: str


class Finding(BaseModel):
    agent: str
    summary: str
    stance: Stance = "unknown"
    data_available: bool = False
    evidence: list[Evidence] = Field(default_factory=list)


class TraceEvent(BaseModel):
    node: str
    message: str
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Report(BaseModel):
    ticker: str
    summary: str
    bull_case: list[str] = Field(default_factory=list)
    bear_case: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    disclaimer: str = DISCLAIMER
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResearchRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=12)


class ResearchResponse(BaseModel):
    report: Report
    eval_scores: dict[str, float]
    guardrail_flags: list[str]
    trace: list[TraceEvent]
