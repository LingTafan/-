# Unity 最小演示（第 1 周：只说明怎么接 JSON）

第 1 周重点在 Python Graph。这里**先不放完整 Unity 工程二进制**，只约定：如何把 `level-agent/output/*.json` 读进场景。

## 你以后要做的（约第 4 天）

1. 新建 3D/2D 空项目，建场景 `Demo`。
2. 把导出的 JSON 拷到例如：

   ```text
   Assets/Levels/port_rain_01.json
   ```

   （Unity 若不能直接当 TextAsset 读 `.json`，可改后缀为 `.json.txt`，或放 StreamingAssets。）

3. 用下面数据结构对齐字段名（与 `level-agent` schema 一致）。
4. Play：按某一波的 `enemies[].count` 生成占位物体（胶囊 / Cube 即可）。

## 数据结构（C# 草稿）

```csharp
using System;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class LevelData
{
    public string level_id;
    public string theme;
    public List<WaveData> waves;
}

[Serializable]
public class WaveData
{
    public int wave;
    public int budget;
    public List<EnemySpawn> enemies;
}

[Serializable]
public class EnemySpawn
{
    public string id;
    public int count;
    public List<string> tags;
}
```

## 加载（草稿）

```csharp
using System.IO;
using UnityEngine;

public class LevelLoader : MonoBehaviour
{
    public string fileName = "port_rain_01.json"; // 放在 StreamingAssets
    public LevelData level;

    void Awake()
    {
        var path = Path.Combine(Application.streamingAssetsPath, fileName);
        var json = File.ReadAllText(path);
        level = JsonUtility.FromJson<LevelData>(json);
        Debug.Log($"Loaded {level.level_id} waves={level.waves.Count}");
    }
}
```

> 注意：`JsonUtility` 对顶层 `List<>` 有时别扭；若解析失败，可改用 Newtonsoft / Unity `Json` 包，或给根对象再包一层。字段名保持与 JSON 一致即可。

## 刷怪（草稿）

```csharp
using UnityEngine;

public class WaveSpawner : MonoBehaviour
{
    public LevelLoader loader;
    public GameObject placeholderPrefab; // 任意胶囊
    public int playWave = 1;

    void Start()
    {
        var wave = loader.level.waves.Find(w => w.wave == playWave);
        if (wave == null) return;

        int i = 0;
        foreach (var e in wave.enemies)
        {
            for (int n = 0; n < e.count; n++)
            {
                var pos = transform.position + new Vector3(i * 1.2f, 0, 0);
                var go = Instantiate(placeholderPrefab, pos, Quaternion.identity);
                go.name = $"{e.id}_{n}";
                i++;
            }
        }
    }
}
```

敌人 `id`（`crab` / `drone` / `elite_brute`…）先映射到同一占位预制体；以后再换成正式美术。

## 验收标准（学习计划 D4）

Play 时，某一波刷出来的占位数量 = JSON 里该波 `enemies` 的 `count` 之和。
