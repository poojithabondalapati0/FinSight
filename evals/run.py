"""Regression eval runner. Phase 1: runs a fixed ticker list through the graph and prints scores."""
from app.graph import build_graph

TICKERS = ["AAPL", "MSFT", "TSLA"]


def main() -> None:
    graph = build_graph()
    for t in TICKERS:
        r = graph.invoke({"ticker": t})
        print(t, r["eval_scores"], r["guardrail_flags"])


if __name__ == "__main__":
    main()
