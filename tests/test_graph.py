from app.graph import build_graph
from app.schemas import DISCLAIMER


def test_happy_path_runs_all_nodes():
    result = build_graph().invoke({"ticker": "aapl"})
    nodes = {e.node for e in result["trace"]}
    assert {"input_guardrail", "fundamental", "technical", "sentiment", "risk",
            "aggregator", "writer", "output_guardrail", "evaluator"} <= nodes
    assert result["report"].ticker == "AAPL"
    assert result["report"].disclaimer == DISCLAIMER
    assert 0.0 <= result["eval_scores"]["completeness"] <= 1.0


def test_invalid_ticker_stops_early():
    result = build_graph().invoke({"ticker": "NOT A TICKER!!"})
    assert "report" not in result
    assert "invalid_ticker" in result["guardrail_flags"]
    assert all(e.node == "input_guardrail" for e in result["trace"])
