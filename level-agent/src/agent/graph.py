"""组装 LangGraph：generate → validate → (retry) → human_review → export。"""

from __future__ import annotations

from typing import Any, Literal

from langgraph.graph import END, START, StateGraph

from agent.nodes.export import export_node
from agent.nodes.generate import generate_node
from agent.nodes.human_review import human_review_node
from agent.nodes.validate import validate_node
from agent.state import LevelAgentState


def _route_after_validate(
    state: LevelAgentState,
) -> Literal["generate", "human_review", "__end__"]:
    errors = state.get("validation_errors") or []
    if not errors:
        return "human_review"

    retry = int(state.get("retry_count") or 0)
    max_retries = int(state.get("max_retries") or 3)
    if retry < max_retries:
        print(
            f"[graph] 校验失败，回修 generate "
            f"(retry {retry + 1}/{max_retries})"
        )
        return "generate"

    print(f"[graph] 已达 max_retries={max_retries}，停止")
    return "__end__"


def _bump_retry(state: LevelAgentState) -> dict[str, Any]:
    """在再次进入 generate 前递增 retry_count。"""
    return {"retry_count": int(state.get("retry_count") or 0) + 1}


def _route_after_review(
    state: LevelAgentState,
) -> Literal["export", "generate"]:
    if state.get("approved"):
        return "export"
    print("[graph] 人审打回 → generate")
    return "generate"


def build_graph():
    g = StateGraph(LevelAgentState)

    g.add_node("generate", generate_node)
    g.add_node("validate", validate_node)
    g.add_node("human_review", human_review_node)
    g.add_node("export", export_node)
    g.add_node("bump_retry", _bump_retry)

    g.add_edge(START, "generate")
    g.add_edge("generate", "validate")
    g.add_conditional_edges(
        "validate",
        _route_after_validate,
        {
            "generate": "bump_retry",
            "human_review": "human_review",
            "__end__": END,
        },
    )
    g.add_edge("bump_retry", "generate")
    g.add_conditional_edges(
        "human_review",
        _route_after_review,
        {
            "export": "export",
            "generate": "bump_retry",
        },
    )
    g.add_edge("export", END)

    return g.compile()
