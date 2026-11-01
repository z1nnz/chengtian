# B｜蘇奕安 Josh（約 20 小時）：第 4 天・第一次收成

> 共同規則見 [00-overview](00-overview.md) 第 2 節。美術提示詞照 [風格指南](../art-style-guide-v1.md) 第 5 節。
> 為什麼是你：坊市草藥攤 `Market_HerbalStall`、攤主、曬藥架都是你做的，煉丹玩法也是你的。這一包讓玩家第一次把自己種的東西拿到你的攤子上賣。

## 0. 這一段在故事裡

第 2 天玩家在院子種下第一塊青靈草，第 4 天第一次收成。這是**經濟教學**：
- 東西有好有壞，好的賣得比較貴；
- 每天坊市想收的東西不一樣；
- 不一定要全賣：留一點給煉丹、泡茶。

定調：輕鬆、短（一次 2–3 分鐘）、**永遠不虧**。沒有殺價失敗、沒有賣不掉被丟掉；手殘也拿得到錢，只是少一點。

## 1. 玩法（約 11 小時）

### 1.1 流程

```text
田裡（格位 TY_Field01）
  1. 採收：一株一株拔，按住拉起；拉太快斷根 → 降一級
  2. 分揀：拔起來的草出現在竹篩上，拖到三個草藥捆（上品／中品／次品）
坊市（你的 Market_HerbalStall）
  3. 出售：攤主看今天收什麼，選要賣幾捆、留幾捆 → 秤一秤 → 拿錢
  → 發出 harvest.completed、market.sold
```

### 1.2 採收

- 一塊田 6 株（先用 6 個綠色方塊當格位框，核心組之後換成 A 的青靈草模型 TY02，不用等）。
- 按住互動鍵（手機：按住草本身）開始拔，**往上拉的速度**決定結果：
  - 慢慢拉（`pullSafeSeconds` 0.8 秒以上拉完）→ 保持原等級；
  - 太快 → 斷根，降一級（上→中、中→次；次品不再降）。
- 每株的原等級由資料決定（第一次收成固定：上 2、中 3、次 1，讓新手每一級都看得到）。
- 看得出等級：上品葉尖微微發光、葉子完整；中品不發光；次品葉子有破洞或發黃。**不寫字**，要玩家自己看（分揀那一步才是重點）。

### 1.3 分揀

- 竹篩上的草，拖到三個草藥捆其中一個（手機：拖曳；鍵盤：滑鼠拖曳，或選中後按 `1` `2` `3`）。
- 放錯不懲罰，只是賣的時候照**實際等級**算錢；最後一句攤主會說「這捆裡混了一株次的」之類（文字先寫在資料裡，核心組換成正式對白）。
- 分揀完自動綁成捆，每捆最多 3 株。

### 1.4 出售

- 到坊市你的草藥攤，打開出售面板：左邊是玩家帶來的捆，右邊是攤主「今天收」的木牌。
- 每天收購表（寫在資料裡）：第 4 天 `qingling-herb` 加價 1、其他照常。
- 玩家可以每一捆選「賣」或「留著」；留著的回到背包（之後煉丹、泡茶用）。
- 按「秤」：桿秤 MK01 的秤砣滑到位置（動畫 1 秒），顯示銅錢數，錢串落到桌上，結束。
- **價格**（每捆 3 株；不滿 3 株照比例無條件進位）：

| 等級 | 一捆 | 說明 |
|---|---|---|
| 上品 | 5 | 現在商店收購 `qingling-bundle` 是 4，上品比較好 |
| 中品 | 3 | |
| 次品 | 2 | 不會是 0：永遠不虧 |
| 今天加價 | +1／捆 | 第 4 天的 `qingling-herb` |

### 1.5 資料與規則程式（純邏輯，附測試）

- `packages/content/harvest-market-v1.json`：
  - `fields`：`TY_Field01` 的 6 株原等級；
  - `pull`：`pullSafeSeconds`；
  - `grades`：`top` / `mid` / `low`，各自的外觀描述 id、捆價；
  - `bundleSize`：3；
  - `dailyDemand`：`[{ "day": 4, "item": "qingling-herb", "bonusPerBundle": 1 }]`；
  - `lines`：攤主的占位句子（混等級、全上品、全部留著等 6 句以內）。
- 物品照現有 id：`qingling-herb`，等級用欄位 `quality: "top" | "mid" | "low"`。伺服器怎麼存等級由核心組決定，你的規則程式只要算得出結果。
- 規則程式（放你自己的資料夾，例如 `tools/harvest-market/`）：輸入「每株原等級、每株拉起時間、分揀結果、賣／留選擇、第幾天」，輸出「每捆實際等級、錢、留下的物品、攤主句子 id」。
- 測試至少涵蓋：
  1. 拉太快降一級、次品不再降；
  2. 放錯捆照實際等級算錢；
  3. 不滿 3 株的捆照比例進位；
  4. 第 4 天加價、第 5 天不加；
  5. 全部留著 → 錢 0、物品全在；
  6. 次品價格永遠大於 0。

### 1.6 Unity 元件

- `QingxiHarvestPanel`（掛 `TY_Field01` 格位）、`QingxiMarketSellPanel`（掛 `Market_HerbalStall`），放你自己的資料夾。先在你自己的測試場景跑：一塊 2.6 × 3.4 m 的田格位框（A 的 TY01 尺寸）、你的草藥攤。
- 面板用你煉丹面板的寫法；中文字照現有 HUD 的字體。觸控按鈕 88 × 88 px 以上；拖曳要能在手機上用一隻拇指完成。
- 事件：`harvest.completed { fieldId, plants:[{quality}] }`、`market.sold { day, bundles:[{quality, sold, coins}], totalCoins }`。核心組把它們接到伺服器種植、商店帳本；你不用寫網路。
- 模型先用格位框；MK01–MK04 做好後換上你自己的模型。

### 1.7 交

- `harvest-market-v1.json`、規則程式＋測試、兩個面板元件、測試場景。
- 錄影：採收（含一株拉太快）、分揀（含一株放錯）、出售（賣兩捆留一捆）。
- 手感問題至少 3 點。

## 2. 模型（約 9 小時）

### 2.1 MK01 桿秤（約 2.5 小時）

| 項目 | 規格 |
|---|---|
| 尺寸上限 | 長 0.7 m（秤桿）；秤盤直徑 0.25 m；掛起來總高 0.6 m |
| 可動 | 秤砣是**獨立物件**，沿秤桿滑動（局部 X 軸 0–0.5 m）；秤盤用三條繩掛，pivot 在掛鉤 |
| 擺放 | 掛在你的草藥攤上（`Market_HerbalStall` 的 `Socket_Scale`，你自己在攤子模型上加這個空物件） |
| 並排比較 | 和你的草藥攤、攤主放在一起 |

```
MK01  Three-view orthographic turnaround sheet of a traditional Chinese hand-held steelyard balance scale, about 0.7 m long, with a dark polished wooden beam inlaid with small brass dot markings (no numbers, no text), a cast iron counterweight hanging from a cord that slides along the beam, a shallow woven bamboo weighing pan hung by three hemp cords, a brass hook at the top, made of old hardwood, brass, iron and hemp, showing hand-worn shine on the beam, a frayed cord, a small dent in the counterweight, used at a herb buying stall in a valley village market. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```

### 2.2 MK02 收成竹篩＋三級草藥捆（約 3 小時）

| 項目 | 規格 |
|---|---|
| 竹篩 | 直徑 0.6 m、高 0.08 m 的淺圓竹篩，分揀時放在田邊 |
| 草藥捆 | 3 種：上品（葉完整、葉尖用**發光材質**，參數 `_Glow` 0–1）、中品（普通）、次品（葉有洞、偏黃）；每捆約 0.35 m 長，麻繩綁 |
| 單株 | 從三種捆裡各拆一株出來當**單株網格**（拖曳時用），長 0.3 m |
| 並排比較 | 和你的曬藥架 `Market_DryingRack`、煉丹的草藥材料放在一起 |

```
MK02  Three-view orthographic turnaround sheet of a harvest set laid out together: a shallow round woven bamboo sieve about 0.6 m wide, and three bundles of slender serrated jade-green spirit herbs tied with hemp twine, each about 0.35 m long — one top-quality bundle with perfect leaves whose tips glow faintly cyan, one ordinary bundle, one poor bundle with holes in the leaves and yellowing edges — made of split bamboo, fresh herb leaves and hemp twine, showing soil still on the roots, a mended rim on the sieve, a few loose leaves on the sieve, used at the edge of a newcomer's herb field in a mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.
```

### 2.3 MK03 價目木牌＋錢串（約 2 小時）

| 項目 | 規格 |
|---|---|
| 價目木牌 | 0.5 × 0.04 × 0.7 m，掛在草藥攤前；**牌面空白**（遊戲用 UI 疊字），上方一個可替換的小木片 `Plate_Demand`（今天收什麼用圖示貼上去） |
| 錢串 | 方孔銅錢一串（10 枚，0.12 m）、散錢 3 枚、一個小布錢袋（0.15 m）；出售結束落在桌上 |
| 並排比較 | 和 MK01、你的草藥攤 |

```
MK03  Three-view orthographic turnaround sheet of a small market set laid out together: a blank hanging wooden price board about 0.5 m wide and 0.7 m tall with a small removable wooden tag at the top (both completely blank, no writing), a string of ten round bronze coins with square holes, three loose coins, and a small drawstring cloth coin purse, made of weathered pine, bronze and indigo cotton, showing green patina on the coins, a rope-worn hanging hole, chalk smudges on the board, used at a herb buying stall in a valley village market. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.
```

### 2.4 MK04 背簍（約 1.5 小時）

玩家把收成背去坊市。

| 項目 | 規格 |
|---|---|
| 尺寸上限 | 寬 0.45 × 深 0.35 × 高 0.6 m |
| 狀態 | 空／裝滿（裝滿是**另一個子網格** `Fill`，草藥捆露出口外，可整個開關） |
| 掛點 | 兩條肩帶；原點在背部貼身那一面的中間，附一個空物件 `Socket_Back`，核心組掛到角色背上 |
| 並排比較 | 和 1.75 m 人形尺（背在背上的位置畫一張） |

```
MK04  Three-view orthographic turnaround sheet of a woven bamboo back basket for carrying herbs, about 0.45 m wide and 0.6 m tall, slightly tapered toward the bottom, with two hemp shoulder straps and a wooden base frame, shown filled with bundles of green herbs sticking out of the top, made of split bamboo, hemp rope and old wood, showing a mended weave patch, sweat-darkened straps, soil on the bottom, used by a newcomer carrying a harvest to the village market. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```

（每一段後面都接 5.2 固定風格段；負面欄貼 5.3。）

## 3. 時數參考

| 項目 | 小時 |
|---|---|
| 規則資料＋規則程式＋測試 | 4 |
| 採收面板、分揀拖曳 | 3.5 |
| 出售面板、秤的動畫、事件 | 2 |
| 錄影、手感調整、寫問題 | 1.5 |
| MK01 桿秤 | 2.5 |
| MK02 竹篩＋三級草藥捆 | 3 |
| MK03 價目牌＋錢串 | 2 |
| MK04 背簍 | 1.5 |
| **合計** | **20** |

## 4. 不要做

- 不要做殺價、失敗、物品損壞；不要讓錢變 0 或負數。
- 不要改伺服器 `apps/server` 或商店資料 `packages/content/qingxi.json`（核心組會照你的資料改）。
- 不要做攤主新對白配音、新 NPC；不改主場景、`QingxiHud`、別人的資料夾。
