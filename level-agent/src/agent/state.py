"""State：一次运行里传来传去的数据包。"""

from __future__ import annotations

from typing import Any, Optional, TypedDict


class LevelAgentState(TypedDict, total=False):
    """图上每个节点读写的共享状态。"""

    prompt: str
    constraints: dict[str, Any]
    waves: Optional[list[dict[str, Any]]]
    level_id: str
    theme: str
    validation_errors: list[str]
    retry_count: int
    max_retries: int
    approved: Optional[bool]
    output_path: Optional[str]
    # 学习用：控制 Mock 行为
    force_invalid: bool
    auto_approve: bool
