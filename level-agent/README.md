# 关卡参数 Agent（第 1 周骨架）

零基础也能跑通：**一句话设定 →（Mock）生成波次 JSON → 规则校验 / 回修 → 人审 → 导出文件**。

默认路径**不需要 API Key**。真模型接法留到学习计划第 3 天。

---

## 5 分钟跑通（Windows）

在终端里（PowerShell / cmd）：

```bat
cd level-agent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run_cli.py
```

等价：

```bat
.venv\Scripts\python.exe -m agent
```

（需先 `set PYTHONPATH=src`，或继续用上面的 `python run_cli.py`。）

成功时终端会看到类似：

1. `[generate] Mock 第 1 次 → 故意不合格表`
2. `[validate] 未通过…` 若干条规则错误
3. `[graph] 校验失败，回修 generate`
4. `[generate] Mock 第 2 次 → 合格表`
5. `[validate] 通过` → `[human_review] auto-approve` → `[export] 已写入 …`

然后打开：

```text
level-agent\output\port_rain_01.json
```

这就是给 Unity 用的关卡表（结果是 **JSON 文件**，不是「图的截图」）。

可选：双击 `scripts\start_dev.bat`（目前只是帮你跑 CLI；**Web 界面第 2 周**再做）。

---

## 常用参数

| 参数 | 作用 |
|------|------|
| （默认） | 第一次故意不合格 → 回修 → 导出有效 JSON；自动批准人审 |
| `--no-auto-approve` | 终端输入 `y` / `n` 做人审 |
| `--force-invalid` | Mock 始终不合格，打满重试后结束（观察回环上限） |
| `--wave-count 4` | 改波次数 |
| `--max-budget 80` | 改每波预算上限 |
| `--prompt "雪地阵地…"` | 改设定文案（Mock 阶段主要影响 theme） |

示例：

```bat
python run_cli.py --force-invalid
python run_cli.py --no-auto-approve
```

---

## 默认校验规则（`rules.py`）

| 规则 | 默认值 | 含义 |
|------|--------|------|
| 波次单调 | — | `wave` 从 1 起连续递增、不重复 |
| 预算上限 | `max_budget_per_wave=100` | 单波 `budget` 不得超过上限 |
| 精英最早波次 | `elite_min_wave=3` | `tags` 含 `elite` 不可早于第 N 波 |
| 飞行最早波次 | `fly_min_wave=2` | `tags` 含 `fly` 不可早于第 K 波 |
| 波次数 | `wave_count=3` | 表长度须等于约束 |

改 `src/agent/rules.py` 里的 `DEFAULT_CONSTRAINTS`，或用 CLI 参数覆盖，重跑就能看到行为变化（第 2 天练习）。

---

## 本仓库里的 State / Node / Edge

用本项目的话讲，不要背百科：

1. **State**（`src/agent/state.py`）  
   一次运行的「快递袋」：`prompt`、`waves`、`validation_errors`、`retry_count`、`approved`、`output_path`…

2. **Node**（`src/agent/nodes/`）  
   一步函数：  
   - `generate`：Mock 出一张波次表（第 1 周不调模型）  
   - `validate`：只跑 `rules.py`  
   - `human_review`：终端 y/n，或 `--auto-approve`  
   - `export`：写 `output/<level_id>.json`

3. **Edge**（`src/agent/graph.py`）  
   怎么走下一步：校验挂了且未超重试 → 回 `generate`；过了 → `human_review`；批准 → `export`。

图示：

```text
START → generate → validate → 通过?
                    ↓否（且未超重试）→ generate
                    ↓是 → human_review → 批准?
                                      ↓否 → generate
                                      ↓是 → export → END
```

---

## JSON 长什么样

契约见 `examples/port_rain_01.example.json`，字段与 Unity 对齐：

```json
{
  "level_id": "port_rain_01",
  "theme": "雨夜港口",
  "waves": [
    {
      "wave": 1,
      "budget": 40,
      "enemies": [{ "id": "crab", "count": 8, "tags": ["ground"] }]
    }
  ]
}
```

---

## 目录

```text
level-agent/
  run_cli.py           # 推荐入口
  requirements.txt
  .env.example         # 真模型用，Mock 可忽略
  examples/            # 示例 JSON
  output/              # 导出结果（*.json 默认不入库）
  scripts/
    start_dev.bat      # 现跑 CLI；Web 第 2 周
    build_exe.md       # 打包占位，先别做
  src/agent/
    state.py
    graph.py
    rules.py
    schema.py
    nodes/
      generate.py      # MOCK
      validate.py
      human_review.py
      export.py
```

---

## 本周明确不做

本地 Web UI、exe 精包装、公网 SaaS。先把这条 Graph 主链路讲清、跑熟。

Unity 如何读这份 JSON：见仓库根目录旁的 `unity-level-demo/README.md`。
