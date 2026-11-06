"""human_review：第 1 周终端 y/n；可用 --auto-approve 跳过交互。"""

from __future__ import annotations

from typing import Any

from agent.state import LevelAgentState


def human_review_node(state: LevelAgentState) -> dict[str, Any]:
    if state.get("auto_approve"):
        print("[human_review] auto-approve=True → 批准")
        return {"approved": True}

    waves = state.get("waves") or []
    print("\n========== 待人审预览 ==========")
    for w in waves:
        enemies = ", ".join(
            f"{e.get('id')}x{e.get('count')}" for e in (w.get("enemies") or [])
        )
        print(f"  波 {w.get('wave')}: budget={w.get('budget')} | {enemies}")
    print("================================")

    while True:
        answer = input("批准导出？[y/n] ").strip().lower()
        if answer in ("y", "yes", "是"):
            return {"approved": True}
        if answer in ("n", "no", "否"):
            print("[human_review] 打回 → 将重新 generate")
            return {"approved": False}
        print("请输入 y 或 n")
