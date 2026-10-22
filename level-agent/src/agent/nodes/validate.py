"""validate 节点：只跑 rules.py。"""

from __future__ import annotations

from typing import Any

from agent.rules import validate_waves
from agent.state import LevelAgentState


def validate_node(state: LevelAgentState) -> dict[str, Any]:
    errors = validate_waves(state.get("waves"), state.get("constraints"))
    if errors:
        print(f"[validate] 未通过，{len(errors)} 条错误：")
        for e in errors:
            print(f"  - {e}")
    else:
        print("[validate] 通过")
    return {"validation_errors": errors}
