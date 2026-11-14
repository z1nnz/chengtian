# Codex v11｜D2 古樹神木：依六張設定圖做佈局，並整合進遊戲

> 2026-11-14，Claude Code 依 z1nnz 指示撰寫。

## 0. 分工（z1nnz 11/14 定，以這裡為準）

| 誰 | 做什麼 |
|---|---|
| **Claude Code** | 所有**生圖**（在 ChatGPT 出場景設定圖、三視圖），列物件清單，建模，審查 |
| **Codex（你）** | **建模**，以及把物件**放進場景**：佈局（地形、路、每件物件的位置、朝向、密度、細節）和遊戲整合 |
| 協作者 | 模型包 |

**你不要再用 image_gen 生任何圖。** 需要參考圖時，在 `code-requests.md` 寫下需要什麼，Claude Code 會出。

## 1. 工作方式

- 工作目錄 `D:\chengtian\1-進行中\world-link-v1`，分支 `game/codex-1113-world-plan`。開工先 `git fetch` 再 `git merge origin/game/core-1110-hud-redesign`。
- 這一輪**可以改程式**（`apps/game/Assets/YunJing/Editor`、`Runtime`、`Shaders`）和 `tools/qingxi-terrain/`。不要改 `art/` 底下的交付檔；不要提交 `ProjectSettings`、`*GlobalSettings.asset`。
- 作者 z1nnz，不加任何 AI 署名。每完成一步就 commit、push。文件繁體中文。
- 建置和測試的方法在 `codex-v9-design-and-integrate.md` 第 1、2 節。

## 2. 輸入

1. 六張設定圖：`art/references/blocks/D2/V1–V6.png`（你上一輪出的，`README.md` 有每張的相機座標）。
2. 物件清單 v1：`docs/execution/world-plan/D2-inventory.md`。**以第零節「對圖後的修改」為準**：約 54 種、約 900 件。
3. 流程：`docs/execution/world-plan/區塊製作流程-v2.md`。
4. 祭壇台石 AL01（已完成）：分支 `art/core-1114-d2-altar-terrace` 的 `art/exports/core-d2-v1/AL01_RootAltarTerrace/`。原點在台座中心底部，台階朝 −Y，可走面高 0.98 m。擺在 (7, 205)，台階朝南。

## 3. 步驟

### A　佈局（先做，做完 commit、push）

照 `codex-v10-d2-concept-set.md` 第 3 節的規定重寫 `blocks/D2.json`、`D2.md`、`D2-plan.png`：

- 總件數 ≥ 600、種類 ≥ 45，每一種清單上的東西都有落位。缺的模型照樣給座標，`status: "missing"`。
- 大型、中型逐件寫 `placements`；小物和樹用 `clusters`（中心、半徑、種類和件數、朝向規則、避開路）。
- 地形照 V1：神木在微高的中央，板根放射圍出空地，南入口根拱、往東 D6 的上坡、往西 D4 的路。邊界高度和 D1、D4、D6、D7 接上。
- 六張圖的相機寫進 `shots`。
- `D2.md` 最後附「六張圖 → 對應的 placements／clusters」對照表。

### B　整合進遊戲

1. **聚落展開**：在 Editor 端寫程式，把 `clusters` 依中心、半徑、件數展開成實際物件（固定亂數種子，避開路和平台，貼地、隨機縮放與朝向）。
2. **匯入器**：D2 用到、還沒有匯入器的模型逐類寫好（FR 巨根、FP 步道、CO 遺跡、AL01、BM、FO02…）。寫法照 `QingxiVillageHouseKit.cs` 的 `Owns`／`Ensure`／`Prepare`。`status: "missing"` 的先跳過，不要放替代品。
3. **登記**：`QingxiBlockBuilder.Blocks` 加 D2，接上鄰塊。
4. **建置＋自動測試**：`--abc-smoke` 要 PASS，沒有粉紅材質。
5. **同鏡位對圖**：六張圖的相機加進 `QingxiKeyArtShots.Views`，跑 `--keyart-shots`，每張和設定圖左右並排存 `docs/execution/world-plan/compare/D2-V<n>.jpg`。
6. **改到像**：照並排圖改佈局、地形、霧和光，至少兩輪。重點：空地被板根圍住的感覺、前景密度、路上的踏石、林下的蕨和蕈。
7. **交付** `docs/execution/world-plan/D2-built.md`：六項檢查各過或沒過、最後的並排圖、還缺的模型清單（東西、尺寸、放哪、在哪張設定圖看得到）。

## 4. 驗收

- 佈局件數和種類達標；JSON 能被讀進去。
- `--abc-smoke` PASS。
- 六張並排圖，構圖看得出是同一個地方。
- 每步 commit、push；`docs/execution/world-plan/codex-v11-report.md` 記錄做到哪裡。

用量用完就停在那一步並寫進報告。
