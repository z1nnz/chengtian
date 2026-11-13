# Codex v9｜一次一塊：設計完就自己整合進遊戲

> 2026-11-14，Claude Code 依 z1nnz 指示撰寫。z1nnz 重新定了分工：
> **Codex 負責區塊設計和遊戲整合；Claude Code 負責建模（ChatGPT 出三視圖 → Blender）；協作者做模型包。**
> v8 規定你「只改資料和文件、不改 `.cs`」，這一條從 v9 起**取消**。v8 的規劃成果（D2、A6、D1、A5… 的 `<ID>.md`、配置圖、`blocks/<ID>.json`）就是這一輪的輸入。

## 1. 工作方式

| 項目 | 規定 |
|---|---|
| 工作目錄 | `D:\chengtian\1-進行中\world-link-v1`，分支 `game/codex-1113-world-plan`。開工先 `git fetch`，把 `origin/game/core-1110-hud-redesign` 合進來（有 `--keyart-shots` 同鏡位截圖工具） |
| 可以改 | `apps/game/Assets/YunJing/Editor/`、`Runtime/`、`Shaders/` 的程式；`tools/qingxi-terrain/`；`docs/execution/world-plan/` |
| 不要改 | `art/` 底下的交付模型（原始美術不動，匯入器把檔案複製到 `Assets/YunJing/Models/<Kit>/`，該資料夾已 gitignore）；`ProjectSettings`、`*GlobalSettings.asset`（Unity 自己改到的不要提交）；`main`、`feature/qingxi-creek-chapter` |
| 提交 | 每完成一個檢查點就 commit、push。作者 z1nnz，不加任何 AI 署名 |
| 建置 | `tools/unity.ps1 -Target NoviceVillageWindows`（約 15 分鐘）。產物 `artifacts/windows-novice-village/`。執行檔參數：`--abc-smoke`（結果在 `%USERPROFILE%\AppData\LocalLow\YunJing\承天 · 青溪新手村\Player.log`，要有 `QINGXI_ABC_SMOKE PASS`）、`--keyart-shots`、`--time-shots`、`--tea-shots`、`--upstream-shots` |
| 語言 | 文件繁體中文；程式註解英文、照現有檔案的寫法 |

## 2. 先讀的程式

- `Editor/QingxiBlockBuilder.cs`：`Blocks` 登記表，一塊怎麼從 `blocks/<ID>.json` 變成串流場景。
- `Editor/QingxiVillageTerrain.cs`：區塊 JSON 的欄位。
- 匯入器範例：`Editor/QingxiVillageHouseKit.cs`（最完整：複製檔案、材質槽、LOD、碰撞殼）、`QingxiScenePropKits.cs`、`QingxiDeliveredKits.cs`、`QingxiTeaTerraceKit.cs`。新匯入器照 `Owns(model)`／`Ensure(model)`／`Prepare(go, model)` 的形狀寫，路徑開頭 `Assets/YunJing/Models/<Kit>/`。
- `Runtime/QingxiKeyArtShots.cs`：同鏡位截圖；新區塊的鏡位加進 `Views`。

## 3. 每一塊的流程（做完一塊才做下一塊）

順序：**D2 古樹神木 → A6 稻田與大水車 → D1 補完 → A5 河灣渡口 → D4 → D6 → B1 → B2**。

1. **匯入器**：把這一塊 `status: needs-importer` 的模型逐類寫好匯入器（FR 巨根、FP 步道、CO 遺跡件、神木…）。交付檔如果還是 LFS 指標，用 `git lfs pull -I <路徑>` 拉下來。
2. **登記**：`QingxiBlockBuilder.Blocks` 加這一塊，和鄰塊的邊接上；`world-dressing.json` 這一筆的 `status` 改 `built`。
3. **建置＋自動測試**：`--abc-smoke` 要 PASS。編譯錯誤自己修到過。
4. **拍圖**：把施工圖的 `shots` 加進 `QingxiKeyArtShots.Views`，跑 `--keyart-shots`。
5. **對圖、改到像**：和主視覺並排（`compare/<ID>-<KA>.jpg`），照 v8 的七項表格找差異，**自己改資料或程式再建一次**，至少兩輪。重點：地形起伏對不對、主體在畫面的位置、前景密度、霧和光。
6. **走一遍**：從鄰塊的入口走進來到主要停留點，確認不卡住、不穿模、邊界高度接得上（可寫成自動走查，或用 `--abc-smoke` 的方式加檢查點）。
7. **交付**：`docs/execution/world-plan/<ID>-built.md`：六項檢查（地形、模型、植被、氣氛、對圖、測試）各自過或沒過、最後的並排圖、**還缺的模型清單（東西、尺寸、放哪、參考圖）**。這張缺件清單是 Claude Code 的建模工作單，寫清楚。

缺模型的位置：不要放假的替代品，留空地並在 `<ID>-built.md` 列出；模型交來後再補。

## 4. 驗收

1. `--abc-smoke` PASS，建置沒有錯誤或粉紅材質。
2. 每塊有並排圖，肉眼看構圖對得上主視覺（主體位置、遠中近三層、光的方向）。
3. 沒有動到 `art/` 的交付檔，沒有提交 `ProjectSettings`。
4. 每塊 commit、push；`docs/execution/world-plan/codex-v9-report.md` 記錄做到哪裡。

用量用完就停在那個檢查點，把狀態寫進報告，下次接著做。
