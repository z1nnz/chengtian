# D3｜第 3 天：垂直山城（約 50 小時）

> 開工前先讀 [00-README-rules](00-README-rules.md) 和 [01-project-briefing](01-project-briefing.md)。
> 工作樹 `yun-jing-rpg-codex-v3-d3`，分支 `feature/codex-v3-d3-city`。資產資料夾 `mountain-city-v1`。

## 0. 這個地方在故事裡

玩家第 5 天第一次到山城，第 10 天回來測資，之後在這裡拜入宗門。**第一眼要覺得這裡很了不起**：比青溪大得多、人多、東西多、很高，天下宗門的分院都在這裡。一開始玩家羨慕這裡的一切，想把名字刻上飛升榜。很久以後才懂背後的事。**所以現在要做得讓人嚮往，不要有陰森感。**

區域風格（建模規格第 11 節）：莊嚴、高聳；灰白花崗石 `#C9C6BD` 50%、深色木、黛瓦 `#3A4048`、銅件；宗門朱漆 `#8E2F25` 每棟 ≤ 10%，只用在宗門建築的柱或門。和河谷的共同語言：同樣的屋頂語法、石基、磨損方式。山城的燈是銅框石座。方向圖：`art/references/world-directions-v1/B-vertical-mountains.png`。

| 編號 | 東西 | 時數 |
|---|---|---:|
| MC01 | 山城街屋模組 | 14 |
| MC02 | 索橋 | 4 |
| TX01 | 飛升榜＋太玄的匾 | 6 |
| TX02 | 大鐘和鐘亭 | 5 |
| TX03 | 高塔 | 9 |
| TX04 | 分院模組（太玄版） | 8 |
| MC03 | B 區組裝預覽 | 4 |
| **合計** | | **50** |

**優先順序**：TX01 → TX03 → TX02 → MC01 → TX04 → MC02 → MC03。

**已經有，直接用，不要重做**：山門 `SectGate`、石階 `MountainStoneStairs`、石路 `MountainStonePath`、棧道 `CliffBoardwalk`、斷崖 `LayeredCliff`（都在 `art/incoming/dondon/`）、測資廣場 `aptitude-plaza-v1`、大殿 `SectGrandHall`、藏經閣 `ScriptureLibrary`、倉庫 `SectStorehouse`。
**B 正在做**：符紙飾品攤、麵攤、榜單告示欄（不要做）。街屋要留得下攤位的前廊空間（前面 3 m）。
**不要直接用** `TownLayout`：整包約 90 萬面、3877 個網格，可以看語言，不能當模組。

## 1. TX01 飛升榜＋匾（6 h）

格位 `TX_AscensionBoard`，太玄分院院內。8 × 2 × 6 m 內。歷代飛升者的名字，世人供奉的榜。

- 一道高大的石框木榜，分很多欄；每欄是**獨立的空白名牌** `Slot_01..40`，字由 UI 疊上。
- **最後一行整排空著**，看得出很久沒有新名字：空位的木頭比較新、沒被香火燻黑。
- 榜前一張石案，案上一方硯台（**墨是濕的**，有人每天磨）和一支筆、香爐、供品。
- 要莊嚴、讓人嚮往：香火鼎盛、磨亮的欄杆。
- `TX_Plaque`：分院的匾，2.4 × 0.8 m，**正反兩面都要可用**（都空白，字由遊戲疊上）；獨立物件，`minTier: standard`。

```
TX01  Architectural concept of a monumental honour board for those who ascended to immortality, standing in the courtyard of an old academy in a mountain city, footprint about 8 m wide and 2 m deep, 6 m high, a tall timber post-and-beam frame with gently upturned eave corners, blue-grey clay tile roof with a moss-covered ridge, a huge dark lacquered panel divided into many columns of small blank name plates (completely blank, no letters, no text), the last row of plates visibly empty and newer, worn stone plinth with three steps, details: a stone offering table in front with a wet inkstone and a brush, incense burners, offerings of fruit, weathering: centuries of incense smoke darkening the upper panel, hands-worn railing. Layout: one three-quarter view from slightly above at eye height of a person, plus front, side and back orthographic views on the same sheet at the same scale, plain light warm-grey background, even soft lighting, building only (no landscape around it except a small ground patch).
```

## 2. TX03 高塔（9 h）

格位 `TX_HighTower`，12 × 12 × 40 m 內。**這是 B 區天際線的主角。**

- 七層八角，白石和青瓦，每層翹簷；窗很少、很窄；一道門（`Door` 獨立物件）；只做外觀，內部不做。
- **不是邪惡的黑塔**：乾淨、莊重，太高太冷，很安靜。
- 附空物件 `Socket_TopLight`（核心組之後可能在塔頂放光），不要自己做發光。
- 40 m 和 200 m 外的剪影都要一眼認得出，LOD2 也要保留翹簷的節奏。**加做 LOD3 面片**（遠景卡片），這件特別遠也看得到。
- 玩家什麼時候看得到、擺在哪裡由核心組決定。

```
TX03  Architectural concept of a tall solemn eight-sided pagoda tower of pale stone, for an ancient academy in a mountain city, footprint about 12 m wide and 12 m deep, seven storeys, 40 m high, timber post-and-beam eaves with gently upturned corners on every storey, blue-grey clay tile roofs with a slim bronze finial, smooth pale limestone walls with very few narrow windows, worn stone plinth with nine steps and one heavy door, details: small bronze wind chimes under the eaves, an empty stone courtyard railing, a single swept path to the door, weathering: rain streaks down the pale stone, moss only on the north side, very clean and very quiet. Layout: one three-quarter view from slightly above at eye height of a person, plus front, side and back orthographic views on the same sheet at the same scale, plain light warm-grey background, even soft lighting, building only (no landscape around it except a small ground patch).
```

## 3. TX02 大鐘和鐘亭（5 h）

格位 `TX_GreatBell`，5 × 5 × 6.5 m 內。很老的青銅大鐘，直徑 1.8 m。

- **要看得出很久沒響過**：撞擊點沒有新的磨亮，撞鐘木上有灰，繩子舊了。
- 撞鐘木獨立 `Striker`，pivot 在吊繩頂端，可擺動；鐘可微晃，pivot 在吊環；附 `Socket_Ring`。
- 鐘面只有抽象雲紋、波紋，**沒有銘文**。

```
TX02  Architectural concept of an open bell pavilion holding one enormous ancient bronze bell, in the courtyard of an old academy in a mountain city, footprint about 5 m wide and 5 m deep, 6.5 m high, a heavy timber post-and-beam frame with gently upturned eave corners, blue-grey clay tile roof, open on all sides, worn stone plinth with two steps, details: the bell about 1.8 m wide with abstract cloud and wave relief bands and no inscription, a long horizontal wooden striking log hung on two ropes, a stone drum seat, weathering: green patina streaks, an old dull strike mark untouched for decades, dust on the striking log. Layout: one three-quarter view from slightly above at eye height of a person, plus front, side and back orthographic views on the same sheet at the same scale, plain light warm-grey background, even soft lighting, building only (no landscape around it except a small ground patch).
```

## 4. MC01 山城街屋模組（14 h）

天下宗門、商人都聚在這裡，所以要有一條**沿著山壁往上的街**。不是一棟一棟做，是一套可以拼的模組，核心組和之後的人都能用它拼街。

| 件 | 尺寸 | 數量 |
|---|---|---|
| 石基層 | 4 × 4 × 2 m，直段、轉角、階梯段；可貼著崖壁 | 4 |
| 店面層 | 4 × 4 × 3 m，開敞木格，前廊 3 m 出挑 | 3 |
| 住家層 | 4 × 4 × 3 m，石灰牆、窄窗 | 3 |
| 屋頂 | 歇山、硬山、翹角端；黛瓦 | 4 |
| 懸挑平台 | 4 × 3 m，木撐架，貼崖，欄杆 | 2 |
| 小件 | 銅框石座燈、空白布幌、掛燈、晾竿（`Detail_*`） | 6 |

- 全部 4 m 格線、接縫 ≤ 2 mm；共用同一組 2048 材質（Trim Sheet），才能合批。
- 拼三棟示範：兩層店＋屋頂、三層貼崖、一棟懸挑。**三棟看起來要不一樣**，不能看得出同一塊重複。
- 不做室內：門窗後是暗的。碰撞要能走前廊。
- 和 A 河谷的 `H01` 舊屋並排，指出至少三個共同點。

## 5. TX04 分院模組（8 h）

十四宗都在山城有分院，**用同一套模組加各道統換裝**（總覽第四節）。這次做模組和**太玄道院的版本**，其他宗之後用它換材質和幾件代表擺設。

| 件 | 尺寸 | 規格 |
|---|---|---|
| 院門 | 6 × 3 × 6 | 門樓，匾的掛點 `Socket_Plaque`（放 TX01 的匾）、朱漆門（≤ 10%） |
| 院牆 | 4 m 一段：直段、轉角、門邊 | 石基、白牆、黛瓦壓頂 |
| 正堂 | 14 × 10 × 8 | 分院主建築，比 `SectGrandHall` 小，只做外觀 |
| 廂房 | 8 × 5 × 5 | 同語言，可重複 |
| 院內鋪地和石階 | 4 m 格線 | 用你 D1 的花崗石（`GR05`）或自己的版本 |

換裝的做法寫進 README：`_Accent` 色參數（朱漆換其他道統色）、`Socket_Emblem`（空的，之後放道統徽記）。**不要做徽記和文字。**

## 6. MC02 索橋（4 h）

| 件 | 尺寸 | 規格 |
|---|---|---|
| 索橋 | 長 24 m，寬 1.6 m，下垂 1.5 m | 兩端石橋頭、鐵鏈和木板、可走（碰撞是連續平滑的斜面）；木板少幾塊但不影響走 |
| 短索橋 | 長 12 m | 同一套 |

原點在一端中心，兩端高度相同；接 `CliffBoardwalk` 的棧道。寫明可以用來接的高度差。

## 7. MC03 B 區組裝預覽（4 h）

**這一包的總驗收。** 在 Blender 擺：山門、石階、你的街屋、索橋、分院（太玄）、飛升榜、鐘亭、高塔、測資廣場、`LayeredCliff`。如果 D1 交了，加上遠景和雲。

| 視角 | 內容 |
|---|---|
| 從山門往上看（人眼 1.6 m） | 石階、街屋層層往上，頂上是分院 |
| 分院院內 | 飛升榜、鐘亭、匾 |
| 遠看全區（300 m 外） | 高塔是主角，樓閣貼著崖，雲帶穿過 |

1920 × 1080，和 `B-vertical-mountains.png` 並排，寫最不像的三點和修了什麼；再和河谷截圖並排，指三個共同點。擺放表寫成 `b-district-layout.json`，核心組拿來建區塊。

## 8. 不要做

- 不做測資台玩法、測資演出（K17）；不做高塔內部、不做天柱和天樞。
- 不做攤位（B）、舊石缸和花台（C）、人物、NPC、徽記、文字。
- 不重做 dondon 既有的山門、石階、棧道、大殿；要改就另存新版本並說明。
- 不把任何人物的故事或名字放進物件名稱。
