"""命令行入口逻辑。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from agent.graph import build_graph
from agent.rules import DEFAULT_CONSTRAINTS, merge_constraints


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="关卡参数 Agent（Mock）：生成 → 校验 → 人审 → 导出",
    )
    p.add_argument(
        "--prompt",
        default="雨夜港口，节奏由慢到快",
        help="一句话设定",
    )
    p.add_argument("--level-id", default="port_rain_01")
    p.add_argument("--theme", default="雨夜港口")
    p.add_argument(
        "--wave-count",
        type=int,
        default=DEFAULT_CONSTRAINTS["wave_count"],
    )
    p.add_argument(
        "--max-budget",
        type=int,
        default=DEFAULT_CONSTRAINTS["max_budget_per_wave"],
    )
    p.add_argument(
        "--elite-min-wave",
        type=int,
        default=DEFAULT_CONSTRAINTS["elite_min_wave"],
    )
    p.add_argument(
        "--fly-min-wave",
        type=int,
        default=DEFAULT_CONSTRAINTS["fly_min_wave"],
    )
    p.add_argument("--max-retries", type=int, default=3)
    p.add_argument(
        "--auto-approve",
        action="store_true",
        default=True,
        help="跳过终端 y/n（默认开启，方便第一次跑通）",
    )
    p.add_argument(
        "--no-auto-approve",
        action="store_true",
        help="改为终端交互人审",
    )
    p.add_argument(
        "--force-invalid",
        action="store_true",
        help="Mock 始终出不合格表，观察打满重试",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    auto_approve = not args.no_auto_approve

    constraints = merge_constraints(
        {
            "wave_count": args.wave_count,
            "max_budget_per_wave": args.max_budget,
            "elite_min_wave": args.elite_min_wave,
            "fly_min_wave": args.fly_min_wave,
        }
    )

    initial: dict[str, Any] = {
        "prompt": args.prompt,
        "constraints": constraints,
        "waves": None,
        "level_id": args.level_id,
        "theme": args.theme,
        "validation_errors": [],
        "retry_count": 0,
        "max_retries": args.max_retries,
        "approved": None,
        "output_path": None,
        "force_invalid": args.force_invalid,
        "auto_approve": auto_approve,
    }

    print("=== level-agent Mock 运行 ===")
    print(f"prompt={args.prompt!r}")
    print(f"constraints={json.dumps(constraints, ensure_ascii=False)}")
    print(
        f"auto_approve={auto_approve} force_invalid={args.force_invalid} "
        f"max_retries={args.max_retries}"
    )
    print()

    app = build_graph()
    final = app.invoke(initial)

    out = final.get("output_path")
    errors = final.get("validation_errors") or []
    if out:
        print()
        print(f"成功。打开文件查看结果：{out}")
        return 0

    print()
    print("未导出文件。")
    if errors:
        print("最后校验错误：")
        for e in errors:
            print(f"  - {e}")
    if args.force_invalid:
        print("（预期：--force-invalid 会打满重试后结束）")
        return 2
    return 1


if __name__ == "__main__":
    # 直接 python src/agent/cli.py 时补上 src
    src = Path(__file__).resolve().parents[1]
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    raise SystemExit(main())
