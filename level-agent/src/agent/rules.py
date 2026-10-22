"""纯规则校验（不靠模型判对错）。

默认约束（可在 constraints 里覆盖，README 有说明）：
- max_budget_per_wave: 100
- elite_min_wave: 3          # 精英不可早于第 N 波
- fly_min_wave: 2            # 飞行单位不可早于第 K 波
- wave_count: 3              # 期望波次数（可选硬检查）
"""

from __future__ import annotations

from typing import Any

DEFAULT_CONSTRAINTS: dict[str, Any] = {
    "wave_count": 3,
    "max_budget_per_wave": 100,
    "elite_min_wave": 3,
    "fly_min_wave": 2,
}


def merge_constraints(user: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_CONSTRAINTS)
    if user:
        merged.update(user)
    return merged


def validate_waves(
    waves: list[dict[str, Any]] | None,
    constraints: dict[str, Any] | None = None,
) -> list[str]:
    """返回错误列表；空列表表示通过。"""
    c = merge_constraints(constraints)
    errors: list[str] = []

    if not waves:
        return ["waves 为空：需要至少一波敌人表"]

    # 1) 波次单调递增且从 1 起连续（允许仅检查严格递增）
    wave_nums = [w.get("wave") for w in waves]
    if any(n is None for n in wave_nums):
        errors.append("每波必须有整数字段 wave")
        return errors

    if wave_nums != sorted(wave_nums):
        errors.append(f"波次必须单调递增，当前: {wave_nums}")
    if len(set(wave_nums)) != len(wave_nums):
        errors.append(f"波次编号不可重复: {wave_nums}")
    if wave_nums and wave_nums[0] != 1:
        errors.append(f"第一波编号应为 1，当前: {wave_nums[0]}")
    for i in range(1, len(wave_nums)):
        if wave_nums[i] != wave_nums[i - 1] + 1:
            errors.append(
                f"波次应连续递增，在 wave={wave_nums[i - 1]} 之后期望 "
                f"{wave_nums[i - 1] + 1}，实际 {wave_nums[i]}"
            )
            break

    expected_count = c.get("wave_count")
    if expected_count is not None and len(waves) != int(expected_count):
        errors.append(f"波次数应为 {expected_count}，实际 {len(waves)}")

    max_budget = int(c.get("max_budget_per_wave", 100))
    elite_min = int(c.get("elite_min_wave", 3))
    fly_min = int(c.get("fly_min_wave", 2))

    for w in waves:
        wn = int(w["wave"])
        budget = w.get("budget")
        if budget is None:
            errors.append(f"第 {wn} 波缺少 budget")
        else:
            try:
                b = int(budget)
            except (TypeError, ValueError):
                errors.append(f"第 {wn} 波 budget 不是整数: {budget}")
            else:
                if b > max_budget:
                    errors.append(
                        f"第 {wn} 波预算 {b} 超过上限 {max_budget}"
                    )
                if b < 0:
                    errors.append(f"第 {wn} 波预算不能为负: {b}")

        enemies = w.get("enemies") or []
        if not enemies:
            errors.append(f"第 {wn} 波 enemies 为空")

        for e in enemies:
            tags = set(e.get("tags") or [])
            eid = e.get("id", "?")
            count = e.get("count", 0)
            try:
                if int(count) <= 0:
                    errors.append(f"第 {wn} 波敌人 {eid} count 必须 > 0")
            except (TypeError, ValueError):
                errors.append(f"第 {wn} 波敌人 {eid} count 非法: {count}")

            if "elite" in tags and wn < elite_min:
                errors.append(
                    f"精英不可早于第 {elite_min} 波："
                    f"第 {wn} 波出现了 {eid}"
                )
            if "fly" in tags and wn < fly_min:
                errors.append(
                    f"飞行单位不可早于第 {fly_min} 波："
                    f"第 {wn} 波出现了 {eid}"
                )

    return errors
