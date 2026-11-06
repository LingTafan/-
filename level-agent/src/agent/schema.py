"""JSON 契约：与 Unity LevelData 字段名对齐。"""

from __future__ import annotations

from typing import Any

# 敌人 id → 说明（Unity 侧映射到占位预制体）
KNOWN_ENEMY_IDS = {
    "crab": "地面小怪",
    "drone": "飞行单位",
    "elite_brute": "精英怪",
    "slime": "地面小怪",
}

# 示例 JSON（与 docs / Unity 约定一致）
EXAMPLE_LEVEL: dict[str, Any] = {
    "level_id": "port_rain_01",
    "theme": "雨夜港口",
    "waves": [
        {
            "wave": 1,
            "budget": 40,
            "enemies": [{"id": "crab", "count": 8, "tags": ["ground"]}],
        },
        {
            "wave": 2,
            "budget": 55,
            "enemies": [
                {"id": "crab", "count": 6, "tags": ["ground"]},
                {"id": "drone", "count": 2, "tags": ["fly"]},
            ],
        },
        {
            "wave": 3,
            "budget": 80,
            "enemies": [
                {"id": "slime", "count": 4, "tags": ["ground"]},
                {"id": "elite_brute", "count": 1, "tags": ["elite", "ground"]},
            ],
        },
    ],
}


def build_level_payload(
    *,
    level_id: str,
    theme: str,
    waves: list[dict[str, Any]],
) -> dict[str, Any]:
    """组装导出给 Unity 的顶层 JSON。"""
    return {
        "level_id": level_id,
        "theme": theme,
        "waves": waves,
    }
