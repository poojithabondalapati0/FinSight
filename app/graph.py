from langgraph.graph import END, START, StateGraph

from app.agents.aggregator import aggregator_node
from app.agents.evaluator import evaluator_node
from app.agents.fundamental import fundamental_node
from app.agents.risk import risk_node
from app.agents.sentiment import sentiment_node
from app.agents.technical import technical_node
from app.agents.writer import writer_node
from app.guardrails import input_guardrail, output_guardrail
from app.state import ResearchState

ANALYSTS = ["fundamental", "technical", "sentiment", "risk"]


def route_after_input(state: ResearchState):
    if state.get("guardrail_flags"):
        return END
    return ANALYSTS  # fan-out: all four run in parallel


def build_graph():
    g = StateGraph(ResearchState)
    g.add_node("input_guardrail", input_guardrail)
    g.add_node("fundamental", fundamental_node)
    g.add_node("technical", technical_node)
    g.add_node("sentiment", sentiment_node)
    g.add_node("risk", risk_node)
    g.add_node("aggregator", aggregator_node)
    g.add_node("writer", writer_node)
    g.add_node("output_guardrail", output_guardrail)
    g.add_node("evaluator", evaluator_node)

    g.add_edge(START, "input_guardrail")
    g.add_conditional_edges("input_guardrail", route_after_input, [*ANALYSTS, END])
    g.add_edge(ANALYSTS, "aggregator")  # fan-in: wait for all four
    g.add_edge("aggregator", "writer")
    g.add_edge("writer", "output_guardrail")
    g.add_edge("output_guardrail", "evaluator")
    g.add_edge("evaluator", END)
    return g.compile()
