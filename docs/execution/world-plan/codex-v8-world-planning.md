# Codex v8｜世界規劃：看主視覺、分析畫面、排好每一塊（場景導演）

> 2026-11-13，Claude Code 依 z1nnz 指示撰寫：「記得我們說過的要請他做世界的規劃（影片裡說的那個）」。
> z1nnz 要的是影片裡那種做法：**由你看整個畫面，分析構圖，決定每樣東西放哪裡**，而不是只做單件美術。
> 這份和 v7（美術件）同時進行，兩份互不相干。v7 在 `codex-v6` 工作區，這份在 `world-link-v1` 工作區。

---

## 0. 你的角色和分工

| 誰 | 做什麼 |
|---|---|
| **你（Codex）** | 場景導演：分析主視覺和遊戲截圖，寫每一塊的**構圖分析**、**佈局資料**（地形、路、平台、每個模型的座標和朝向）、**差異清單** |
| Claude Code | 寫程式把你的佈局資料變成場景、建置、跑測試；模型匯入器；審你的規劃 |
| 協作者 | 做模型 |

你只改**資料和文件**，不改 `.cs`。需要程式配合的事寫進 `docs/execution/world-plan/code-requests.md`，Claude Code 會做。

## 1. 工作方式

| 項目 | 規定 |
|---|---|
| 工作目錄 | `D:\chengtian\1-進行中\world-link-v1`，分支 `game/codex-1113-world-plan`（從世界分支 `game/core-1110-hud-redesign` 開） |
| 可以改 | `tools/qingxi-terrain/blocks/<新區塊>.json`、`tools/qingxi-terrain/world-blueprint.json`、`tools/qingxi-terrain/world-dressing.json`（只改你規劃的區塊那一筆）、`docs/execution/world-plan/` |
| 不能改 | 任何 `.cs`、`.unity`、`.shader`；`blocks/A4.json`（它由 `make-a4.py` 產生）；A1 的 `novice-village.json`（要改就寫進差異清單，由 Claude Code 改） |
| 提交 | 每完成一塊就 commit 並 push，作者 z1nnz（已設定），不加任何 AI 署名 |
| Unity | 6000.3.28f1。可以跑 `tools/unity.ps1 -Target NoviceVillageWindows` 建置，再用 `--time-shots`、`--tea-shots`、`--upstream-shots` 拍圖（圖在 `artifacts/windows-novice-village/` 底下）。第一次開會重新匯入，要等一陣子 |
| 語言 | 文件全部繁體中文 |

## 2. 先讀

1. `docs/execution/world-blueprint/完成清單.md`：完成定義（每塊六項檢查）、區塊進度、還缺的模型。
2. `tools/qingxi-terrain/world-blueprint.json`：19 塊的 `feel`、`terrain`、`landmark`、`zones`（模型與件數）、`shots`（鏡位）。
3. 主視覺：`art/references/keyart/KA01`～`KA13` 的 `chosen.png`（或 `KAxx-selected.png`）、`atmosphere.md`、`parts.md`。對應：KA01 A1、KA02 A2、KA03 A3、KA04-1／KA04-2 A4、KA05 A5、KA06 A6、KA07 D3、KA08 B1 山門、KA09 B2 山城街、KA10 B2 廣場、KA11 D2、KA12 D4、KA13 D6。
4. 區塊資料的格式：`tools/qingxi-terrain/blocks/D1.json`（簡單）、`D3.json`（完整）、`A4.json`（有 `flats`）。欄位說明在 `apps/game/Assets/YunJing/Editor/QingxiVillageTerrain.cs` 開頭的類別（只讀）。
5. 已經能擺進場景的模型（匯入器已寫好，`model` 路徑照這些開頭）：

| 路徑開頭 | 來源 |
|---|---|
| `Assets/YunJing/Models/RuinsB/<件>/<件>_v001.fbx` | `art/exports/qingxi-world-ruins-b`（R01 石牆、R02 竹籬、R03 柴堆、R04 石燈、R05 里程石、H01、枯井、翻車） |
| `Assets/YunJing/Models/VillageHousesB/<件>/<件>_v001.fbx` | `art/exports/village-houses-b`（VL01–05、VH01–03、LT01） |
| `Assets/YunJing/Models/VillageReskinB/<件>/<件>_v001.fbx` | `art/exports/village-reskin-b`（RS01–RS03） |
| `Assets/YunJing/Models/CreeksideC/<ID>/<ID>_v001.fbx` | `art/exports/creekside-life-c`（WL01–05、FI01–05） |
| `Assets/YunJing/Models/WorldPropsA/…`、`Day12C/…`、`ModellingBasicsC/…`、`CreekRepairB/…` | 見現有區塊 JSON 裡的寫法 |

其他模型（TE 梯田、FR 巨根、FP 步道、SG 石階、MC 街屋、TX04、ST 街道小件、PS／BT／FS 等地標、CO 遺跡件）還沒有通用匯入器：**照樣寫進佈局**，`model` 填 `art/exports/...` 的實際路徑、`status` 填 `"needs-importer"`，並在 `code-requests.md` 列出來。

## 3. A 部分：已建的五塊，和主視覺比對（先做，約 10 小時）

A2、A1、A3、D3、A4 已經有場景，但都還沒通過「氣氛」和「對圖」兩項。

每一塊：
1. 建置並拍圖（或用 `artifacts/` 裡現有的圖）。對每張主視覺，找最接近的遊戲截圖，**左右並排**存成 `docs/execution/world-plan/compare/<區塊>-<KA>.jpg`。
2. 寫 `docs/execution/world-plan/compare/<區塊>.md`，照這個格式：

| 項目 | 主視覺 | 遊戲現在 | 要怎麼改（具體） |
|---|---|---|---|
| 前景 5 m 內 | … | … | 例：在 (−3, −27) 加 2 叢 GrassTall、1 顆 StonesMossy |
| 中景 | … | … | … |
| 遠景與天際線 | … | … | … |
| 光的方向和顏色 | … | … | 例：10:00 太陽 yaw 改 −50°、主光色 #F3E2C0 |
| 霧 | … | … | 例：霧距 150 → 110 m、霧色 #A9B8C4 |
| 地面顏色 | … | … | … |
| 密度 | … | … | 例：民居巷 30 m 內現在 4 件小物，主視覺約 20 件 |

每一條「要怎麼改」都要有**座標、數量、色碼或數值**，讓 Claude Code 可以直接照做。最後列「最影響觀感的前五項」。

## 4. B 部分：還沒建的八塊，逐塊規劃（約 30 小時）

順序：**D2 古樹神木 → A6 稻田與大水車 → D1 林緣獵場（補完）→ A5 河灣渡口 → D4 苔石古祠 → D6 古林往山腳 → B1 山門石階 → B2 山城街與測資廣場**。

每一塊交三樣：

### 4.1 構圖分析 `docs/execution/world-plan/<ID>.md`

- **這一塊要給玩家什麼感覺**（取自施工圖 `feel`，用你的話講清楚）。
- **從哪裡進來、第一眼看到什麼、被什麼吸引往前走、走到哪裡停下來看**（動線和視線）。
- **主視覺拆解**：前景、中景、遠景各有什麼；主體在畫面哪裡；光從哪來。
- **俯視配置圖** `<ID>-plan.png`：100 × 100 m 的方格（每格 10 m），標出地形高低、路、平台、每個重點區、每個地標、鏡位和視線方向。可以用程式畫（matplotlib 或 PIL），不要用生圖。
- **和相鄰區塊怎麼接**：邊界上的路、溪、高度要對得上（相鄰區塊的 JSON 和施工圖的 `cell` 可以查）。

### 4.2 佈局資料 `tools/qingxi-terrain/blocks/<ID>.json`

照 `D1.json`、`A4.json` 的格式，世界座標（+Z 北、A1 中心 (0,0)、每塊 100 m，`bounds` 由施工圖的 `cell` 算）：

- `heightPoints`、`relief`、`noise`、`cliffs`：地形起伏。高度要和主視覺的地勢一致，邊界 12 m 內會自動和鄰塊接平，所以邊界附近不要放極端高度。
- `nodes`、`edges`：路。寬度、材質（`dirt`、`plaza`）。
- `pads`：要放建築或聚集的平地（中心、半長、高度）。
- `flats`：需要整平的長條（石階、棧道底下）。
- `creek`：有水的區塊。
- `placements`：**每一件模型**的 `id`、`role`（中文說明）、`model`、`x`、`z`、`yaw`、`footprint`、`collider`、`status`、`author`。件數和種類以施工圖 `zones` 為準，位置由你照構圖決定；可以比施工圖多放，但不要用還沒有的模型（缺的寫進 4.3）。
- 同時在 `world-dressing.json` 這一塊的那一筆填 `species`（樹種和比重）、`waterside`、`landmarks`（刻意擺的單棵樹），`status` 先維持 `planned`。

擺放原則（z1nnz 定的）：樹林成叢、不要平均撒；路和平台周圍留空；最高的丘上放一棵讓眼睛去找的大樹；自由度要高，玩家看得到的地方大多走得到。

### 4.3 缺件與請求

- 還缺的模型：寫進 `<ID>.md` 的「缺件」表（東西、尺寸、建議誰做）。
- 需要程式的：寫進 `code-requests.md`（例：SG 石階要匯入器、D2 神木要 90 m 的 LOD 與碰撞、B1 要瀑布卡）。

## 5. 驗收（Claude Code 審）

1. 每一條修改建議、每一件擺放都有座標和數值，不是形容詞。
2. 配置圖和 JSON 對得上（隨機抽五件核對座標）。
3. 相鄰區塊邊界接得上。
4. 區塊 JSON 能被 `QingxiVillageTerrain.Load` 讀進去（欄位名稱和型別正確；可以對照 D1.json 逐欄檢查）。
5. 每一塊 commit、push 了；最後有 `docs/execution/world-plan/codex-v8-report.md`。

## 6. 順序

A（A1 → A2 → A3 → D3 → A4）→ B（D2 → A6 → D1 → A5 → D4 → D6 → B1 → B2）。
用量用完就停在那一塊，報告寫到哪裡為止，下次接著做。
