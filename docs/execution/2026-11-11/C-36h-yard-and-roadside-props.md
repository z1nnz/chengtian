# C｜36 小時：院子和路邊的東西

> 交給 Eli-0731（Eli）。2026-11-11，Claude Code 依 z1nnz 指示撰寫：「你覺得建議他們做的，直接丟給他們新的工作包」。大小由核心組定為 36 小時。
> **接在 11/07 的 128 小時包和 11/08 的 40 小時包後面做**。那兩份做完再開始這份。
> 全部都是**基礎練習難度**：一件練一兩個技巧。不做建築、地標、人物、玩法、文字。

---

## 0. 先讀

- 標註規則：[`docs/standards/labeling-v1.md`](../../standards/labeling-v1.md)
- 交件規則與提示詞固定段：照 [11/07 你的包](../2026-11-07/C-128h-creekside-and-village-life.md) 第 1 節與附錄
- `docs/execution/2026-11-03/00-overview.md` 第 2、3 節（不重複總表）

## 1. 為什麼做這包

11/11 進遊戲看青溪村，院子和路邊都是空的，看不出有人在這裡過日子。你的 LV 是屋簷下和屋裡的小東西；這包做的是**院子裡和路邊比較大件**的東西，遠遠就看得到。

你在 #93 的 FI02、FI03 改得很好：每一步寫原因、前後對照用同光同角度。這包照同樣方式交。

## 2. 要交的東西

每件約 4 小時。

| ID | 東西 | 尺寸上限（w×d×h） | 放在哪 | 練什麼 |
|---|---|---|---|---|
| VG01 | 菜畦一組（三條土壟，各種一種菜：青菜、蘿蔔、蔥） | 3 × 2 × 0.4 m | A1 院內 | 重複排列但每棵略不同（用陣列加隨機，不是一棵棵擺）；土壟的起伏 |
| VG02 | 瓜架（竹架上爬著葫蘆藤，吊三顆葫蘆） | 2.4 × 1.6 × 2.1 m | A1 院內 | 細竹竿的綁接；藤和葉用帶透明貼圖的面片 |
| VG03 | 晾衣竿（兩根叉竿、一根橫竿、晾著兩件布衣） | 2.6 × 0.6 × 1.9 m | A1 院內 | 布掛著往下垂的形狀；你在 WL03、WL04 練過布，這次是掛起來的 |
| VG04 | 草垛（2 種：圓頂的、被抽掉一角的） | 2.2 × 2.2 × 2.4 m | A1、A6 田邊 | 大塊的軟輪廓；邊緣要毛，不要像一顆光滑的饅頭 |
| VG05 | 兩輪手推板車（完好的，空車） | 2.2 × 1.1 × 1 m | A1、A2 路邊 | 輪子的圓和輻條；車架的榫接。**和 A2_OverturnedCart 翻倒的破車不同** |
| VG06 | 扁擔與兩個籮筐 | 1.8 × 0.5 × 0.6 m | A1、A2 路邊 | 竹編的面用貼圖做；扁擔中間被肩膀磨亮 |
| VG07 | 石磨（上下兩片、木推柄、石座） | 1 × 1 × 0.9 m | A1 院內 | 兩個圓柱疊放、磨盤邊的鑿痕、出料的石槽口 |
| VG08 | 餵牲口的長石槽 | 1.6 × 0.5 × 0.45 m | A1 村邊 | 整塊石頭挖空的厚度；內側水漬和青苔 |
| 全包檢查 | 並排圖 | — | — | VG01–08 並排一張，配 1.75 m 人形尺和一件舊道具（4 小時） |

| | 時數 |
|---|---:|
| VG01–08 | 32 |
| 全包檢查 | 4 |
| **合計** | **36** |

## 3. 規則

1. **commit 用你自己的 GitHub 帳號**，不用 z1nnz，也不掛 Claude Code 或其他 AI 的名字。你 #93 做對了，繼續這樣。
2. **Unity 檢查用 6000.3.28f1**。
3. 每件交齊：三視圖、灰模、線框、LOD 對照、人形尺；LOD2 要還看得出是什麼。
4. VG02 的藤葉、VG03 的布、VG04 的草邊用 alpha clip，Unity 匯入打開「Mip Maps Preserve Coverage」，和你 FI03 的做法一樣。
5. 都是 `minTier = standard`（院子裡的大件，標準畫質也要看得到）。VG01、VG05、VG07、VG08 要有簡單碰撞。
6. 核心組負責擺進世界。**不改主場景、不改區塊 JSON。**
7. 一件做到卡住超過預估時間 1.5 倍，就先交目前的樣子並寫明卡在哪，不要硬磨。

## 4. 分支與 PR

| 批 | 分支 | PR 標題 |
|---|---|---|
| A | `art/c-1111-vg-yard-props` | `【C】11/11 VG01–04：菜畦、瓜架、晾衣竿、草垛` |
| B | `art/c-1111-vg-roadside-props` | `【C】11/11 VG05–08：板車、扁擔籮筐、石磨、石槽` |

## 5. 不要做

- 不做已有的：A2_OverturnedCart、MK04 背簍、B08 晾藥竹匾、TE04 採茶竹簍、R03 柴堆、你自己的 LV01–20、GC01–08、WL、FI。
- 不做 Josh 這輪的 CW、WE、XB、GN、AN（院牆院門、水井、石板橋、穀倉、牛棚）；不做 John 這輪的 CB、OS、MH、AW。
- 不做人物、動物、文字、玩法、建築。

## 6. 物件句（正面提示 = 物件句 + 固定 Layout 段 + 5.2；負面用 5.3）

**VG01**
```text
Three-view orthographic turnaround sheet of a small rural Chinese kitchen garden plot, about 3 m wide, 2 m deep and 0.4 m tall, three raised earth ridges each planted with a different crop: leafy greens, radish tops, and spring onions, plants slightly uneven in size and spacing, dark damp soil, no fence, no writing.
```

**VG02**
```text
Three-view orthographic turnaround sheet of a rustic bamboo gourd trellis, about 2.4 m wide, 1.6 m deep and 2.1 m tall, thin bamboo poles lashed together with cord, a gourd vine with broad leaves climbing over the top, three hanging bottle gourds of different sizes, weathered bamboo, no writing.
```

**VG03**
```text
Three-view orthographic turnaround sheet of a rural Chinese clothes-drying pole, about 2.6 m wide and 1.9 m tall, two forked wooden posts stuck in the ground holding one long bamboo pole, two plain faded hemp garments hanging and sagging naturally, simple and worn, no people, no writing.
```

**VG04**
```text
Three-view orthographic turnaround sheet of a rural Chinese rice straw haystack, about 2.2 m in diameter and 2.4 m tall, a rounded dome of bundled dry straw around a central pole with a small straw cap, loose shaggy edges with stray stalks, shown in two versions: complete, and with one side partly pulled away, no writing.
```

**VG05**
```text
Three-view orthographic turnaround sheet of an intact two-wheeled rural Chinese wooden handcart, about 2.2 m long, 1.1 m wide and 1 m tall, a flat plank bed with low side rails, two spoked wooden wheels with iron rims, two long handles and a small prop leg, empty, old worn wood, no writing.
```

**VG06**
```text
Three-view orthographic turnaround sheet of a bamboo shoulder carrying pole with two woven bamboo baskets, about 1.8 m long and 0.6 m tall, a flattened bamboo pole polished at the middle by use, two round open baskets hanging from cords at each end, both empty, weathered bamboo, no writing.
```

**VG07**
```text
Three-view orthographic turnaround sheet of a rural Chinese hand-turned stone grain mill, about 1 m wide and 0.9 m tall, two round millstones stacked on a stone base with a carved runoff channel and spout, a wooden push handle, chisel marks around the rim, worn grey stone with flour-pale dust in the grooves, no writing.
```

**VG08**
```text
Three-view orthographic turnaround sheet of a long rural stone feeding trough, about 1.6 m long, 0.5 m wide and 0.45 m tall, carved from a single block of grey stone with thick uneven walls, water stains and moss inside, chipped rim, sitting on two flat stones, empty, no writing.
```

---

有問題直接問；寫不清楚的地方先照最保守的做法做，寫進 PR。
