# Codex v5｜把遊戲裡所有物件整合成一張大世界

> 2026-11-08，Claude Code 依 z1nnz 指示撰寫：「把這個遊戲的全部東西、物件的整合丟給 Codex，叫 Codex 幫我去製作。」
> **從現在起，物件整合由 Codex 負責。** Claude Code 改成審查你推上來的東西、開 PR、處理協作者 PR，並繼續負責存檔、登入與把玩法搬進大地圖（S3、S5）。
> 工作順序以本頁為準，取代 [`codex-v4-score-and-next.md`](codex-v4-score-and-next.md) 的順序。v4 的評分、第 2 節新規則和各項規格仍然有效。

---

## 0. 目標

**完成的樣子：** 從官道走進青溪，一路走到古林和山城，全程同一個世界、中間不切展示場景；每個區塊的東西都擺好、接地、光線對，看起來像 `art/references/world-vision-v2/` 那五張方向圖，不像展示場。

這是《前十天試玩版》（`docs/execution/2026-11-07/02-前十天試玩版-完整製作清單.md`）的 S1。

## 1. 開工：環境已經準備好

| 項目 | 內容 |
|---|---|
| 工作資料夾 | `D:\chengtian\1-進行中\world-link-v1`（**直接用這個**，不要另開） |
| 分支 | `game/core-1108-world-east-valley`：已合併最新 `main` 和 `feature/qingxi-creek-chapter`，可以建置 |
| Unity | `D:\DevTools\Unity\6000.0.82f1\Editor\Unity.exe`；`apps/game/Library` 已經匯入好 |
| LFS | 建置要用的模型都下載了。缺的時候用 `git lfs pull --include="art/exports/<資料夾>/**"`，**不要整包下載** |
| 主專案 | 已搬到 `D:\chengtian\chengtian`，舊路徑 `D:\yun-jing-rpg` 不存在了 |

建置與截圖：

```powershell
./tools/unity.ps1 -Target NoviceVillageWindows     # 生成場景並建置，約 10 分鐘內
cd artifacts/windows-novice-village
./YunJingNoviceVillage.exe --time-shots -screen-width 1600 -screen-height 900 -screen-fullscreen 0     # 七張不同時段
./YunJingNoviceVillage.exe --upstream-shots -screen-width 1600 -screen-height 900 -screen-fullscreen 0 # D3 上游七張
```

**今天的基準圖**：`artifacts/baseline-20261108.jpg`（只在本機）。之後每一階段都要拍同一批角度和它比。

**工作資料夾裡有幾個不是你改的檔案**（`GraphicsSettings`、`ProjectSettings`、`QualitySettings`、`UniversalRenderPipelineGlobalSettings`、`WebGLTemplates.meta`），是 Unity 自動改的。除非你確定需要，不要提交；要改就單獨一個提交說明原因。

## 2. 現有的系統（在上面接，不要重寫）

| 東西 | 位置 | 作用 |
|---|---|---|
| 新手村生成器 | `apps/game/Assets/YunJing/Editor/QingxiNoviceVillageBuilder.cs` | **唯一的主線底圖** |
| 區塊生成 | `Editor/QingxiBlockBuilder.cs`，資料在 `tools/qingxi-terrain/blocks/<ID>.json` | 每塊一個場景；目前 A2、A3、D1、D3 |
| 區塊載入 | `Runtime/QingxiBlockStreamer.cs` | 走到 45 m 內載入、90 m 外卸載 |
| 地形 | `Editor/QingxiVillageTerrain.cs`、`tools/qingxi-terrain/novice-village.json` | 道路、平台、外緣 12 m 融合到世界高度，鄰塊不會有縫 |
| 區塊總表 | `tools/qingxi-terrain/novice-world-blocks.json`、`docs/execution/novice-world-block-plan.md` | 每格 100×100 m，A1 中心在 (0,0)；各區座標、高度、出口 |
| 擺設規則 | `docs/execution/novice-world-dressing-plan.md` | 樹與石頭怎麼散 |
| 交付模型匯入 | `Editor/QingxiDeliveredKits.cs` | 複製模型、掛材質、LOD、碰撞的**範本**；新的 kit 照這個寫 |
| 晝夜 | `Runtime/QingxiDayNight.cs` | 已完成，不要重寫 |
| 驗收工具 | `tools/qingxi-terrain/README.md`（`check-grounding.ps1`、`village-checks.mjs`） | 懸空、躺倒、路上有草、坡度 |

`QingxiUnifiedWorldBuilder`、`QingxiWorldBuilder`（較大的小鎮＋狩獵區）**只當參考**，不要再往裡面加東西，也不要刪。

## 3. 目前的物件現況（你第一步要把它查實）

Claude Code 用檔名比對初查的結果，**只是起點，不保證準確**：「程式有提到」可能只是驗證腳本。

**格位還空著的數量**：A1 村 11／29、A2 9／12、A3 9／9、D1 2／2、D3 3／19。

**`art/exports/` 共 39 組**：

| 情況 | 模型組 |
|---|---|
| 程式和區塊資料都有提到（多半已擺，要確認） | `aptitude-plaza-v1`、`elder-trees-v1`、`qingxi-alchemy-b`、`qingxi-encounter-a`、`qingxi-gathering-visual-kit-v1`、`qingxi-mountain-rabbit-v003`、`qingxi-return-c`、`qingxi-training-yard-v1`、`qingxi-waterhead-a`、`qingxi-waterworks-b` |
| 只有程式提到（**要查是真的擺進世界，還是只有驗證腳本**） | `creek-repair-b`、`creek-repair-b-props`、`harvest-market-b`、`qingxi-alchemy-table-v1`、`qingxi-day12-c`、`qingxi-day34-c`、`qingxi-ground-v1`、`qingxi-world-ruins-b`、`tea-brewing-b`、`tea-terraces-b`、`world-props-a`、`zhuo-boar-a` |
| 只有區塊資料提到（**要查格位是否真的有接模型**） | `elder-world-tree-hero-v1`、`giant-tree-v1`、`irrigation-v1`、`irrigation-v2`、`qingxi-detail-props-v2`、`qingxi-entry-assets-v13`、`qingxi-prop-kit-v1`、`qingxi-riverbank-v2`、`qingxi-road-props-v12`、`qingxi-road-props-v13`、`qingxi-village-signs-v1`、`qingxi-water-report-c`、`qingxi-winding-road-v1` |
| 都沒提到（**多半完全沒進遊戲**） | `modelling-basics-c`（54 個）、`territory-backyard-a`、`territory-interior-b`、`qingxi-town-blockout-v1`（沒有模型檔） |
| 另外還有 | `art/incoming/dondon/`（72 組，部分已用）；你自己 v3 的渡口、稻株、月亮（v4 A 部分）；Josh 的 PR #79 竹簍、竹匾、亭子、大水車（**等 z1nnz 同意合併**，還不在這條分支） |

協作者還在陸續交件（John：山城街屋；Josh：石階、巨根、步道、民居；Eli：村裡小物），所以這張表要能**重新產生**，不是手寫一次。

## 4. 工作順序

每個階段做完才進下一個。**每階段結束都拍圖和前一版並排**，推上去並回報。

### 第 0 階段｜收尾你第三輪能收的東西（v4 的 A1、A2、A3）

先把 MO01、SK 弧面、RI02、RI01、FE01–03 交出來，後面要用。A4 飛升榜、A5 屋內殼放到第 3 階段做。

### 第 1 階段｜整合總表（工具）

寫 `tools/registry/asset-placement.mjs`，產生 `docs/registry/asset-placement.md`：每組模型、每個物件，寫清楚：作者、PR、擺在哪個區塊的哪個格位、還是沒擺、為什麼不擺。檢查方式要讀生成器和區塊資料，不是只比對字串；若能從生成出來的場景讀到實際物件更好。

### 第 2 階段｜修畫面底子（最優先的視覺工作）

不修好這些，模型放進去都會被拉低。基準圖上看到的問題：

| # | 問題 | 要做到 |
|---|---|---|
| 1 | 草地是螢光綠，整體飽和度太高、像塑膠 | 照 `docs/art/modeling-style-spec-v1.md` 色票和方向圖，柔和、有層次；地面貼圖與 Color Grading 一起調 |
| 2 | 空中有線框和小字（空格位標記），玩家也看得到 | 空格位標記只在開發模式顯示，正式建置不出現 |
| 3 | 左上地名顯示 `TrailClue_Q01` 內部名稱 | 只顯示玩家看得懂的名字，沒有就不換 |
| 4 | 黃昏整片灰紫，入夜幾乎全黑 | 黃昏要暖，夜要看得見路，村口燈是主要暖光 |
| 5 | 俯瞰時地形外面是空白，看得到世界盡頭 | 遠景山、霧遮住邊界；有 SK 或簡單遠山都可以 |
| 6 | 上游工地的石件又白又平，和預覽圖差很多 | **先查原因**（材質沒掛、URP 轉換、法線、燈光），並檢查其他 kit 是否同樣被拉低 |
| 7 | 模型間距太開，像展示場 | 留到第 3 階段處理 |

主角替身張手的姿勢（S6）這輪不處理，除非五分鐘內能解決。

**做完拍一組和基準圖並排，存 `artifacts/stage2-compare.jpg`，也放進 PR 預覽資料夾。**

### 第 3 階段｜把現有區塊填滿（A1、A2、A3、D1、D3）

1. 依總表，把已交付但沒擺的模型擺進去：先補空格位，再加生活感小物。
2. `modelling-basics-c`、`world-props-a`、`qingxi-world-ruins-b`、`creek-repair-b`、`qingxi-day34-c` 優先。
3. 村子要像有人住：屋與屋之間有小路、圍籬、柴堆、晾衣，不是一件一件隔開展示。
4. 做 v4 的 A5 屋內殼（後牆窗改後門）和 A4 飛升榜。
5. `territory-*` 屬於領地（獨立場景），不要擺進大世界；在總表寫「屬領地」。

### 第 4 階段｜接新區塊（四步流程）

照這個順序：**A4 東坡茶田 → A6 稻田 → A5 渡口 → D2 神木 → D5／D4 → D6 → B1 山門 → B2 測資廣場**。

每一塊都走完四步（`docs/execution/2026-11-07/00-codex-notice-rename-and-direction.md` 有說明）：

1. **主視覺**：v4 B 部分的對應圖 KA，並附氛圍卡；
2. **灰模**：`blocks/<ID>.json` 地形、道路、平台、格位；從主視覺同角度截圖，**並排比對**，防止大空間被壓成一個小碗；
3. **零件**：放已交付的模型；缺的寫進回報，交給協作者或之後的工作包，不要自己重做別人手上的東西；
4. **光影**：調到接近主視覺。

**A4 是試做。** 做完先回報並附並排圖，等 z1nnz 或 Claude Code 看過才接下一塊。方向對了，之後每塊回報一次就繼續做。

### 第 5 階段｜檢查（每個區塊都做）

隨機 16 個可走位置，人眼高度截圖；檢查浮空、穿模、地面太平、石頭堆得太假。用 `check-grounding.ps1` 跑懸空、躺倒、坡度。路線能從官道一路走到當前最遠的區塊，用 `QingxiWalkthroughSmoke` 或新的自動走路檢查。

### 之後

v4 C（遠山、雲、瀑布、中景山）和 D（接月亮）在第 2、4 階段需要時就先做需要的那部分，其餘排在最後。

## 5. 規則

1. **提交**：作者 `z1nnz <202040543+z1nnz@users.noreply.github.com>`，不加 AI 署名。每完成一小步就提交並推上這條分支。
2. **標註**：照 `docs/standards/labeling-v1.md`。這個工作分支繼續用；區塊大到需要分開審查時，再開 `game/codex-1108-<區塊>`。
3. **PR 由 Claude Code 開**，你不合併，也不 force push，不推到 `main`。
4. **不改別人的素材原檔**（`art/source/`、`art/exports/` 別人的資料夾）。要調整另存或寫在匯入程式裡；模型本身有問題就寫進回報，由 Claude Code 通知作者。
5. **不做**：人物模型、故事內容、對白、文字、新網頁版（PWA）頁面、存檔與伺服器（S3）、玩法邏輯（S5）。
6. **玩法互動點不要弄壞**：煉丹、演武、採集、山兔、回村分揀目前都在新手村內。挪位置要確認互動還能用，`QingxiAbcSmoke`（`--abc-smoke`）要過。
7. **時間上限**：同一個問題修 2 輪還不行就留最好的版本、寫清楚，先做下一件。
8. **不要宣稱沒驗證的事**：標清楚有沒有實際進遊戲看過；不寫 FPS，手機不測。

## 6. 回報

每完成一個階段，回報：

```text
【Codex v5 第 N 階段 完成／部分完成】
1. 已推上的提交與分支
2. 做了什麼（幾個物件進世界、哪些區塊、總表路徑）
3. 前後並排圖路徑
4. 檢查結果（懸空、穿模、走路、--abc-smoke）
5. 沒做完、卡住、需要 z1nnz 決定的事
```
