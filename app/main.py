from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.graph import build_graph
from app.schemas import ResearchRequest, ResearchResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.graph = build_graph()
    yield


app = FastAPI(title="AI Investment Research Lab", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/research", response_model=ResearchResponse)
async def research(req: ResearchRequest) -> ResearchResponse:
    result = await app.state.graph.ainvoke({"ticker": req.ticker})
    if "report" not in result:
        raise HTTPException(status_code=422, detail={"flags": result.get("guardrail_flags", [])})
    return ResearchResponse(
        report=result["report"],
        eval_scores=result.get("eval_scores", {}),
        guardrail_flags=result.get("guardrail_flags", []),
        trace=result.get("trace", []),
    )
