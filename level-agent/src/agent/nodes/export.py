"""export：写入 output/<level_id>.json。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.schema import build_level_payload
from agent.state import LevelAgentState

# level-agent/ 根目录（…/level-agent/src/agent/nodes/export.py → parents[3]）
PACKAGE_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = PACKAGE_ROOT / "output"


def export_node(state: LevelAgentState) -> dict[str, Any]:
    level_id = state.get("level_id") or "untitled_level"
    theme = state.get("theme") or ""
    waves = state.get("waves") or []
    payload = build_level_payload(level_id=level_id, theme=theme, waves=waves)

    out_dir = DEFAULT_OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{level_id}.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[export] 已写入 {path}")
    return {"output_path": str(path)}
