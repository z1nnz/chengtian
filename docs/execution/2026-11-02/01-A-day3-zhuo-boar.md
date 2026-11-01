# A｜鄭翔元 John（約 20 小時）：第 3 天・濁化山豬

> 共同規則見 [00-overview](00-overview.md) 第 2 節。美術提示詞照 [風格指南](../art-style-guide-v1.md) 第 5 節。
> 為什麼是你：山兔遭遇（`QingxiRabbit`、山兔 v003 的 17 骨五段動畫）和練功試招（`QingxiTrainingPractice`）都是你做的，這一包是同一套東西往前走一步。

## 0. 這一段在故事裡

第 3 天，玩家和同屆五人到上游溪谷看溪為什麼停。走到溪邊，一隻**濁化的山豬**從林子衝出來。
怕死的胖子第一個尖叫，卻第一個擋到大家前面：「我是怕死，可我更怕你們死！」（這一段演出由核心組做）
接著換玩家：閃開牠的衝撞，引牠撞上樹或石頭，趁牠暈的時候把牠身上的濁氣驅掉。濁氣散了，牠就是一隻普通的山豬，愣一下，跑回山裡。

**定調**：牠不是怪物，是生病的動物。不殺、不掉肉、不掉皮；玩家被撞到也不會死。打完的感覺是「好險」和「牠好可憐」，不是「打贏了」。

## 1. 玩法（約 11 小時）

### 1.1 流程

```text
[核心組演出：胖子擋第一下] → 玩家接手
  └─ 循環：警戒 → 刨地預告 → 衝撞 →（撞到障礙：暈眩 → 玩家驅濁）/（沒撞到：煞車回頭）
  └─ 驅濁累計 2 次 → 濁氣散 → 山豬恢復、逃回山裡 → 發出 zhuoBoar.cleansed
  └─ 玩家被撞 3 次 → 山豬跑掉 → 發出 zhuoBoar.escaped → 30 秒後可在原處再遇
```

### 1.2 數值（寫進 `packages/content/zhuo-boar-encounter-v1.json`，程式不寫死）

| 欄位 | 值 | 說明 |
|---|---|---|
| `noticeRadiusM` | 12 | 玩家進入範圍才開始 |
| `pawTelegraphSeconds` | 1.2 | 刨地預告；這段時間牠會轉向對準玩家 |
| `trackTurnDegPerSecond` | 90 | 預告時的轉向速度 |
| `chargeSpeedMps` | 9 | 衝撞時直線前進，**衝出去後不轉彎** |
| `chargeMaxDistanceM` | 14 | 沒撞到東西，衝到這個距離煞車 |
| `brakeRecoverSeconds` | 1.5 | 煞車後回頭的時間（玩家喘口氣） |
| `dazeSeconds` | 2.5 | 撞到樹或石頭後暈眩 |
| `cleanseHoldSeconds` | 1.5 | 暈眩時靠近（2 m 內）按住互動鍵這麼久，算一次驅濁 |
| `cleanseNeeded` | 2 | 驅濁幾次濁氣才散 |
| `hitKnockbackM` | 3 | 被撞到往後退 |
| `hitStaminaLoss` | 15 | 被撞扣體力（最低留 1，不會倒下） |
| `hitsBeforeEscape` | 3 | 被撞幾次牠就跑掉 |
| `retryCooldownSeconds` | 30 | 跑掉後多久能再遇 |
| `dodgeIFrameSeconds` | 0.35 | 閃避的無敵時間 |
| `dodgeDistanceM` | 2.5 | 閃避距離 |

**手感目標**：第一次玩的人大約 60–90 秒完成；看懂「刨地 → 往側邊閃 → 牠撞樹」以後，幾乎不會再被撞。衝撞要**看得見方向**：刨地時地上出現一條淡淡的衝撞線（寬 1.2 m），預告結束時線固定。

### 1.3 規則程式（純邏輯，附測試）

- `packages/content/zhuo-boar-encounter-v1.json`：上表數值。
- 規則程式放你自己的套件資料夾（例如 `tools/zhuo-boar/zhuo-boar-rules.mjs`，或照你山兔／練功時的位置），輸入「時間、玩家位置、障礙列表、按鍵」，輸出「狀態、事件」。**不碰 Unity、不碰網路。**
- 狀態：`idle` → `alert` → `telegraph` → `charge` → `daze` / `brake` → … → `cleansed` / `escaped`。
- 測試至少涵蓋：
  1. 預告時會轉向、衝撞開始後不轉向；
  2. 衝撞線上有障礙 → 進 `daze`；沒有 → 衝滿距離進 `brake`；
  3. 暈眩中按住 1.5 秒算一次驅濁，放手重算，暈眩結束沒按滿不算；
  4. 驅濁 2 次 → `cleansed`，只發一次事件；
  5. 閃避無敵時間內不算被撞；被撞 3 次 → `escaped`，30 秒內不能再開始；
  6. 被撞體力最低留 1。

### 1.4 Unity 元件

- 元件名 `QingxiZhuoBoarEncounter`，放你自己的資料夾；掛在格位 `D3_BoarEncounter`（核心組放在上游溪谷；你先在自己的測試場景放一個 20 × 20 m 平地、3 棵樹的格位框、2 顆石頭的格位框）。
- 障礙物：場景裡帶 `BoarObstacle` 標記（或元件）的碰撞體都算；**樹用 BR02 的格位名 `D3_BoarTree_01..03`**。
- 山豬先用 1.5 × 0.9 m 的膠囊體；BR01 交件後換成你的模型和動畫（動畫名照 2.1 表）。
- 閃避：鍵盤 `Shift` 或空白鍵＋方向；手機右下「閃」按鈕，方向用左手搖桿。驅濁：鍵盤 `F`、手機「驅」按鈕（暈眩且 2 m 內才出現），按住時按鈕外圈填滿。
- 畫面回饋：刨地時衝撞線、撞樹時鏡頭輕震 0.15 秒、驅濁時黑紫色霧氣從身上往上飄（粒子先用簡單的就好）、濁氣散時一聲輕的「呼」（音效先用占位）。
- 事件：`zhuoBoar.cleansed { durationSeconds, hitsTaken }`、`zhuoBoar.escaped { hitsTaken }`。核心組接：清掉 → 手札記一條「溪邊的山豬身上有黑氣」、練體經驗少量；跑掉 → 什麼都不扣。
- 胖子那一段演出由核心組做：你只要讓元件有 `BeginFromScript()`，核心組演完再呼叫它開始。

### 1.5 交

- `zhuo-boar-encounter-v1.json`、規則程式＋測試、`QingxiZhuoBoarEncounter` 元件、測試場景。
- 錄影兩段：一段順利清掉、一段被撞 3 次牠跑掉。
- 手感問題至少 3 點（例如衝撞太快看不清、暈眩時間太短）。

## 2. 模型（約 9 小時）

### 2.1 BR01 濁化山豬（約 7 小時，含骨架和動畫）

| 項目 | 規格 |
|---|---|
| 尺寸上限 | 長 1.6 × 寬 0.6 × 肩高 1.0 m（成年野山豬，比玩家矮，但衝起來要有份量） |
| 外形 | 厚肩、短腿、長吻、一對短小的獠牙、背上一排鬃毛；**不要畫成魔物**：沒有角、沒有尖刺、沒有發光大眼 |
| 濁化 | 一張材質，參數 `_Zhuo`（0–1）：1 = 鬃毛和身側有黑紫色的濁氣紋路（像墨滲進毛裡），眼睛帶一點暗紅；0 = 普通的暖褐色山豬。紋路用遮罩貼圖，不另做網格 |
| 骨架 | 約 20–26 骨：脊椎 4、頸 2、頭、下顎、耳 ×2、尾 2、四腳各 3；沿用山兔 v003 的命名方式 |
| 動畫 | `Idle`（呼吸、耳朵抖）、`Paw`（刨地 1.2 秒，前蹄扒地、低頭）、`Charge`（衝撞循環）、`Daze`（撞暈、搖頭、站不穩，2.5 秒循環）、`Cleanse`（濁氣散，站直、甩頭，2 秒）、`Flee`（轉身跑回林子的循環） |
| LOD | 三級；LOD2 保留獠牙和鬃毛的剪影 |
| 碰撞 | `_Collision` 一個凸包（身體），不要包到腳下的地 |
| 並排比較 | 和你的山兔 v003、1.75 m 人形尺放在一起 |

```
BR01  Three-view orthographic turnaround sheet of a wild mountain boar that has been sickened by a dark corrupted energy, about 1.5 m long and 0.95 m tall at the shoulder, with a heavy hunched shoulder, short strong legs, a long snout, two small curved tusks and a ridge of coarse bristles along the spine, made of coarse warm brown fur whose bristles and flanks are stained with ink-like dark violet-black veins of corruption seeping through the fur, eyes with a faint dull red tint, showing mud caked on the legs, a torn ear, burrs and pine needles caught in the fur, used as a sick wild animal in the upstream creek valley of a mountain village (not a monster: no horns, no spikes, no glowing eyes); neutral standing pose for modelling. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```
（後面接 5.2 固定風格段；負面欄貼 5.3。另外再出一張同提示詞、把 "stained with ink-like dark violet-black veins of corruption…dull red tint" 改成 "clean healthy warm brown fur, calm dark eyes" 的版本，當 `_Zhuo = 0` 的參考。）

### 2.2 BR02 會被撞歪的小松（約 2 小時）

山豬撞上的樹。三棵擺在格位 `D3_BoarTree_01..03`，每棵撞一下會歪、會掉松針。

| 項目 | 規格 |
|---|---|
| 尺寸上限 | 寬 2.5 × 深 2.5 × 高 5 m；樹幹直徑約 0.25 m |
| 變體 | 2 種外形（不同枝形），不要只靠旋轉 |
| 狀態 | 一個網格，樹幹底部一根骨（或 pivot 在根部）讓遊戲可以讓它**晃一下、歪 8°**；樹皮上一塊被撞掉的淺色傷痕用材質參數 `_Scar`（0–1）開 |
| 碰撞 | `_Collision`：樹幹圓柱凸包（直徑 0.35 m、高 2 m） |
| 並排比較 | 和 D3 既有的松樹、你的 A01 上游河段放在一起 |

```
BR02  Three-view turnaround of a single young mountain pine, about 5 m tall with a crown 2.5 m wide, silhouette: a slim slightly leaning trunk with irregular tiers of short branches and a soft uneven crown, bark: rough grey-brown bark with resin drops and a pale freshly scraped patch near the base where an animal hit it, foliage: tufts of long soft needles, warm sunlit yellow-green on top and cool teal-green underneath, base: the trunk only slightly widens where it meets the ground and a few roots show briefly before diving into the soil (no swollen base, no roots lying on the ground, no exposed root legs), a few broken twigs and fallen needles at the foot. Layout: front, side and top-down views side by side, same scale, aligned on one ground line, plain light warm-grey background, even soft lighting, one tree only.
```
（後面接 5.2；負面欄貼 5.3。）

## 3. 時數參考

| 項目 | 小時 |
|---|---|
| 規則資料＋規則程式＋測試 | 4 |
| Unity 元件、測試場景、手機按鈕、回饋 | 5 |
| 錄影、手感調整、寫問題 | 2 |
| BR01 三視圖、建模、貼圖、LOD | 4 |
| BR01 骨架、權重、6 段動畫 | 3 |
| BR02 兩種小松、狀態、碰撞 | 2 |
| **合計** | **20** |

## 4. 不要做

- 不要做血、肉、掉落物、死亡動畫；不要寫攻擊山豬扣血的系統。
- 不要做胖子、同屆五人、對白（核心組）。
- 不改主場景、`QingxiHud`、伺服器 `apps/server`、別人的資料夾。
