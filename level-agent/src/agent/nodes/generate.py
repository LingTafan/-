"""generate 节点：第 1 周用 Mock，不需要 API Key。

学习设计：
- 默认：第 1 次尝试故意出不合格表，让你看到「校验失败 → 回修」；
  第 2 次起出合格表，默认路径能导出有效 JSON。
- --force-invalid：始终出不合格表（配合有限重试，便于观察打满重试）。
"""

from __future__ import annotations

from typing import Any

from agent.rules import merge_constraints
from agent.state import LevelAgentState


def _invalid_waves(wave_count: int) -> list[dict[str, Any]]:
    """故意违规：波次乱序 + 第 1 波精英 + 超预算 + 过早飞行。"""
    waves: list[dict[str, Any]] = [
        {
            "wave": 1,
            "budget": 999,  # 超预算
            "enemies": [
                {"id": "elite_brute", "count": 1, "tags": ["elite", "ground"]},
                {"id": "drone", "count": 3, "tags": ["fly"]},
            ],
        }
    ]
    for i in range(2, wave_count + 1):
        waves.append(
            {
                "wave": i,
                "budget": 40,
                "enemies": [{"id": "crab", "count": 4, "tags": ["ground"]}],
            }
        )
    # 打乱单调性：把最后一波改成编号更小
    if wave_count >= 2:
        waves[-1]["wave"] = 1
    return waves


def _valid_waves(wave_count: int, max_budget: int) -> list[dict[str, Any]]:
    """合格表示例：波次 1..N 连续；预算递增但不超上限；精英/飞行遵守最早波次。"""
    waves: list[dict[str, Any]] = []
    for i in range(1, wave_count + 1):
        budget = min(30 + i * 15, max_budget)
        enemies: list[dict[str, Any]] = [
            {"id": "crab", "count": 4 + i, "tags": ["ground"]}
        ]
        if i >= 2:
            enemies.append({"id": "drone", "count": i - 1, "tags": ["fly"]})
        if i >= 3:
            enemies.append(
                {"id": "elite_brute", "count": 1, "tags": ["elite", "ground"]}
            )
        waves.append({"wave": i, "budget": budget, "enemies": enemies})
    return waves


def generate_node(state: LevelAgentState) -> dict[str, Any]:
    constraints = merge_constraints(state.get("constraints"))
    wave_count = int(constraints.get("wave_count", 3))
    max_budget = int(constraints.get("max_budget_per_wave", 100))
    retry = int(state.get("retry_count") or 0)
    force_invalid = bool(state.get("force_invalid"))

    # 有校验错误说明这是回修轮：retry_count 在路由里递增
    make_invalid = force_invalid or retry == 0

    if make_invalid:
        waves = _invalid_waves(wave_count)
        print(f"[generate] Mock 第 {retry + 1} 次 → 故意不合格表（学习回环）")
    else:
        waves = _valid_waves(wave_count, max_budget)
        print(f"[generate] Mock 第 {retry + 1} 次 → 合格表")

    theme = state.get("theme") or "雨夜港口"
    level_id = state.get("level_id") or "port_rain_01"
    prompt = state.get("prompt") or ""
    if prompt and not state.get("theme"):
        theme = prompt[:32] or theme

    return {
        "waves": waves,
        "theme": theme,
        "level_id": level_id,
        "validation_errors": [],
    }
