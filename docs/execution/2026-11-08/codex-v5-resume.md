# Codex v5 接續指示（z1nnz 說要開始才啟動）

> 2026-11-08，Claude Code 依 z1nnz 指示撰寫。上一輪因額度用完中斷在第 3 階段。這份寫清楚現況和接下來的順序；工作包本體仍是 [`codex-v5-world-integration.md`](codex-v5-world-integration.md) 和 [`codex-v5-scene-shots.md`](codex-v5-scene-shots.md)。**世界怎麼建，以 [世界施工圖](../world-blueprint/README.md) 為準**；和舊的區塊規劃衝突時，照施工圖。

## 1. 硬性規定

1. **只能用 `D:\DevTools\Unity\6000.0.82f1\Editor\Unity.exe`，或直接跑 `tools/unity.ps1`。** Hub 裡的 6000.6.7f1 絕對不要用。上一輪用它重建第 3 階段，弄壞了 `Library`，也把 URP 全域設定從版本 8 改到 11，之後 82f1 就拒絕建置。
2. 「建置成功」不算通過。每次驗收都要**實際開執行檔**，看 Player.log 沒有 `corrupted`、`Crash!!!`，並跑 `--abc-smoke`。
3. 提交時不要帶這些建置副產物：`UniversalRenderPipelineGlobalSettings.asset`、`ProjectSettings/GraphicsSettings.asset`、`ProjectSettings.asset`、`QualitySettings.asset`、`Assets/WebGLTemplates.meta`。
4. 模型缺實體檔（還是 LFS 指標）時，用 `git lfs pull --include=...` 只拉需要的路徑，不要整包下載。

## 2. 現況（Claude Code 已處理）

| 項目 | 狀態 |
|---|---|
| 執行檔 `level0` 當機 | 已修。`QingxiNoviceArrival` 寫在 `QingxiDayOneSpots.cs` 裡，類別和檔名不一致，腳本物件被存進場景檔。已移到自己的檔案，連續建兩次都能開。**新的 MonoBehaviour 一定要一個類別一個同名檔案** |
| `--abc-smoke` | 敏捷樁、練功場的檢查已對齊第一堂練體課；儲物箱打不開的 bug 已修（站近 1.5 m 內優先判定箱子） |
| 第 3 階段未提交的水車、石橋、工地工具、市集小物 | 已用 82f1 驗證並提交 |
| 7 個場景的主視覺 | 已選定，並補上 `chosen.png`、`prompt.txt`、`zone-map.png`、`atmosphere.md`、`parts.md` |
| 複製進 `Assets` 的模型 | 已加入 `.gitignore` |

## 3. 接下來的順序

### 3.1 修畫面底子（第 2 階段補完）

現在的畫面和主視覺差太遠，先處理這些，比多擺模型重要：

1. **天空太藍、太飽和**：降到主視覺的層次，加雲和地平線霧。
2. **草地還是螢光綠**：對齊 `#4E6B3A`、`#6F8A4A`、`#2F4A2A`。上游 D3 的草和落葉最明顯。
3. **黃色大樹太亮、幾乎過曝**：降亮度和飽和度。
4. **遠景是空的**：接 SK 弧面，沒有貼圖就先做出遠山色塊和霧，不要讓地平線直接接天空。
5. **夜間太暗**：入夜畫面幾乎看不到路和房子。要像 KA01 那樣有月光和燈光層次。
6. **細彎月沒有入鏡**：`--time-shots` 的入夜圖看不到 MO01。方向或高度要調到玩家朝北平視時看得到。

同鏡位比對圖在 `art/previews/world-integration/stage2-same-camera-compare.jpg`（鏡頭視角已從 70° 改成 60°，所以人物看起來比較大）。目前看得出的進步只有規劃框消失、草地稍微降亮，**上面六項還沒解決**。做完在同位置重拍，並排放同一個資料夾。

### 3.2 照世界施工圖建

從施工順序第 1 塊開始，一塊一塊建，每塊都要拍完施工圖列的所有鏡頭。先把下面的問題修掉：

- **A3 西溪的上游是斷的**：D3 的溪往東流進 A1，A3 的溪從 (-95,49) 憑空開始，沒有水源。從 D3 分一條支流接過來，或改 A3 的走向，並寫清楚選哪個。
- KA00 的民居密度不夠：村子目前像展示場。用現有模型把間距收緊，缺的寫進施工圖。
- A2 的 12 個格位、D3 的 14 個格位逐一核對有沒有入鏡。

有主視覺的鏡頭，和 `art/references/keyart/<ID>/chosen.png` 並排存到 `art/previews/keyart/<ID>/compare.jpg`。

**自由度**：施工圖裡寫了玩家和建造者各自的自由度。除了地標、鏡頭必須看到的東西、感覺、區塊之間的連接，其他都可以改得更好，改了就更新 `tools/qingxi-terrain/world-blueprint.json`，回報時說明原因。

### 3.3 重出 KA01

石燈太像日式石燈籠。重出時形狀對齊 `art/exports/qingxi-day12-c/G01.fbx`，其他不變。

### 3.4 A4 東坡茶田（施工順序第 5 塊）

照四步流程，對齊 `KA04-1`、`KA04-2`。**圖中的河谷比實際開闊，遠處田野用遠景卡片，不要真的建出來。** 轉向東北看山城那一面要補一張主視覺。

**做完 A4（A2、A1、A3、D3、A4 這五塊）就停，照第 6 節格式回報，等 z1nnz 看過。**

## 4. 額度不夠時

優先順序：3.1 → 3.2 的前四塊 → 3.3。每完成一小步就提交並推上去，回報裡寫清楚沒做到的。
