# 給 Codex：2026-11-07 改名、資料夾搬家、開發方向與平台（請先讀完再繼續工作）

> Claude Code 依 z1nnz 指示撰寫：「那你幫我跟 Codex 講好了，因為我也在用 Codex。」
> 這份是**通知加規則更新**，不是新的建模工作包。和舊文件衝突時，以這份為準。

---

## 1. 遊戲改名：承天

- 遊戲名稱從「雲境」改為 **承天**（在世界觀裡，「雲境」只是天缺正下方的一個地名）。
- 新寫的文件、介面文字、回報、PR 標題一律用「承天」。
- 舊檔案裡的「雲境」、`yun-jing`、`YunJing` **先不要自己大規模改名**（包括 C# 命名空間、Unity 資料夾、資產路徑）。之後會用一張專門的 PR 統一處理；自己改會和別人衝突。

## 2. GitHub 儲存庫改名

- 舊：`z1nnz/yun-jing-rpg` → 新：**`z1nnz/chengtian`**。舊網址會自動轉址。
- 本機所有工作樹的 `origin` 已改成 `https://github.com/z1nnz/chengtian.git`，你不用再改。
- 用 API 開 PR、看 CI 時，路徑改成 `/repos/z1nnz/chengtian/...`。

## 3. 資料夾搬家（最重要）

`D:\yun-jing-rpg-workspace\` 已經不存在。所有工作樹都搬到 **`D:\chengtian\`**，並分成四類，名稱也去掉了 `yun-jing-rpg-` 前綴：

```
D:\chengtian\
  chengtian\           主專案（見下方「尚未搬」）
  1-進行中\            main-scene-abc-v1、codex-v3-d1、codex-v3-d2、codex-v3-d3、next-packs-20261105、terrain-audit-v1
  2-舊工作保留\        camera-v1、entry-v13、listening-terrace-v1、heroine-*、distant-peaks-v1、interior-kit-v1、
                       alchemy-table-pbr-v1、village-props-c7、plaza-tree-c8、a3-watermill-c9、web-shell-v1 等
  3-PR審查用\          review-pr64～73、review-*、pr-review-64-73、pr60-fix、rabbit-review
  4-素材與快取\        ui-concepts-v1、main-move-overflow-cache
  README.md            每個資料夾一行說明
```

對照範例：

| 舊路徑 | 新路徑 |
|---|---|
| `D:\yun-jing-rpg-workspace\yun-jing-rpg-main-scene-abc-v1` | `D:\chengtian\1-進行中\main-scene-abc-v1` |
| `D:\yun-jing-rpg-workspace\yun-jing-rpg-codex-v3-d1` | `D:\chengtian\1-進行中\codex-v3-d1` |
| `D:\yun-jing-rpg-workspace\yun-jing-rpg-codex-v3-d2` | `D:\chengtian\1-進行中\codex-v3-d2` |
| `D:\yun-jing-rpg-workspace\yun-jing-rpg-codex-v3-d3` | `D:\chengtian\1-進行中\codex-v3-d3` |
| `D:\yun-jing-rpg-workspace\yun-jing-rpg-interior-kit-v1` | `D:\chengtian\2-舊工作保留\interior-kit-v1` |

- 每個工作樹都已用 `git worktree repair` 重新接好，分支、未提交的修改、未推送的提交都保留，**沒有任何東西被刪**。
- 你的對話如果還開在舊路徑，請**關掉後用新路徑重新開**。舊路徑已經不存在，在那裡寫檔會失敗，或在錯的地方建出新資料夾。
- **新工作樹一律開在對應分類裡**，例如：
  `git worktree add "D:/chengtian/1-進行中/<主題>" -b <分支> origin/feature/qingxi-creek-chapter`
  開完在 `D:\chengtian\README.md` 補一行。
- `docs/execution/codex-v3/00-README-rules.md` 第 2 節寫的 `D:\yun-jing-rpg-workspace\...` 已經過時，以這份為準。
- 你自己的工作樹 `C:\Users\User\.codex\worktrees\progress-roadmap\yun-jing-rpg` 沒有動，也已經接好。

### 尚未搬：主專案 `D:\yun-jing-rpg`

主專案要搬到 `D:\chengtian\chengtian`，但**你（Codex）的背景程式把工作目錄停在 `D:\yun-jing-rpg`，資料夾被鎖住了**：Firebase MCP、computer-use 的 node。

- **請不要再用 `D:\yun-jing-rpg` 當工作目錄開新的對話或工具。**
- z1nnz 會找時間把 Codex 完全結束，讓 Claude Code 完成搬家。搬好之後主專案是 `D:\chengtian\chengtian`，Codex 的信任設定已經先改成新路徑。

## 4. 開發方向：從現在起照「四步做場景」（z1nnz 2026-11-07 決定）

參考一部「一個人用 AI 做 3A 場景」的影片，以後每一個區域都照這四步做，目的是讓畫面好看、有電影感：

1. **先有一張圖**：每個區域先產出一張**場景概念圖**（用你的 image_gen），加一張俯視分區圖（路、島、主殿在哪）。z1nnz 看過、同意了才往下做。之後所有的活都照這張圖做。
2. **把空間搭出來（白模）**：先用白色方塊和簡單形狀定出比例與配置。
   - 放一個 1.7 m 的人物尺規。
   - **相機對齊概念圖的角度**，把白模渲染出來，和概念圖**並排比對**。
   - 最常見的失敗是把又大又空曠的空間擠成一個小碗，空間對了才能進下一步。
3. **做零件**：曲面類（雕像、怪石、樹根、燈籠、裝飾）可以先用圖生 3D，再清理、減面、做 LOD；建築、橋、欄杆、地形照原本的腳本建模流程做。**先做一塊樣品，z1nnz 看過再批量做。**
4. **進遊戲打光**：光、霧、材質、燈籠。氛圍主要出在這一步。

分工：Claude Code 偏氛圍與搭場景，**Codex 偏細節檢查**。檢查做法是在可走範圍隨機取 16 個機位截圖，找出：
- 懸空的石頭或草
- 穿牆的模型
- 太平的地面
- 像一塊塊堆上去的石頭

其中一方卡住修不好，就換另一方。另外，**岩壁要用高品質岩石模型拼，不要只改地形高度。**

風格維持承天的中式山水（璃月感），**只學流程，不學影片的日式外觀**（鳥居、狐仙）。

## 5. 平台與效能（研究結果，部分還在等 z1nnz 決定）

完整研究在 `D:\chengtian\承天-平台與驗收研究-2026-11-07.md`。和你工作有關的重點：

- **目標平台**：Steam（Windows）、Android、iOS。**同一個 Unity 專案**出三種安裝包，不是做兩個遊戲；內容與模型共用，差別只在操作、畫質預設、下載分包與付款。
- **網頁版（PWA）建議不再當正式產品**（等 z1nnz 確認）。在確認之前，**不要再開新的 PWA 玩法或頁面**；新東西直接做在 Unity。
- **手機從來沒實測過。** 所以你的回報**不准承諾 FPS**，只寫實際面數、網格數、材質數、貼圖大小。
- 請在 `model_info.json` 或回報裡**多寫兩個數字**：
  - **網格／材質數**：會變成 draw call，這是手機最可能先爆的地方。
  - **貼圖總記憶體**：估算即可。
- 規則不變：畫質分級（`docs/standards/quality-tiers-v1.md`）照舊，LOD0 不減面，LOD1 是手機近處會看到的版本，也要好看。
- 起始效能目標，等手機實測後會調整：

  | | 電腦 | 手機 |
  |---|---|---|
  | 幀數 | 60 fps | 30 fps |
  | 單畫面 draw call | — | 200 以下 |
  | 記憶體 | — | 2.5 GB 以下 |

- 文件裡 Unity 版本不一致（`architecture.md` 寫 `6000.0.85f1`，實際建置用 `6000.0.82f1`），之後會統一。**你先繼續用 `6000.0.82f1`**，不要自己升級。

## 6. 你現在要做的事

1. 讀完這份，用一段話回報你理解的四件事：新名稱、新路徑、四步流程、平台規則。
2. 把你開在舊路徑的對話全部改到新路徑；如果有工作在舊路徑寫到一半，回報是哪些檔案。
3. 繼續原本的 codex-v3 工作包（D1／D2／D3），但：
   - 往後的新區域照第 4 節的四步做；
   - 回報加上第 5 節的數字。
4. 不要提交、不要推送；照舊由 Claude Code 審查後以 z1nnz 名義提交。
