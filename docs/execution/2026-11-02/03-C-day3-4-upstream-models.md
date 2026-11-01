# C｜Eli-0731（約 20 小時）：第 3、4 天的模型（只做模型）

> 共同規則見 [00-overview](00-overview.md) 第 2 節。美術提示詞照 [風格指南](../art-style-guide-v1.md) 第 5 節。
> 這一包不排玩法。你的模型交件後，核心組放進格位、接上狀態切換。

## 0. 這兩天在故事裡

- **第 3 天**：玩家和同屆五人走到上游，看見溪是在一座**老石壩**那裡斷的：水閘被泥沙和斷木塞住，壩下只剩濕石頭。溪邊有幾顆石頭摸起來是**溫的**（伏筆，不解釋）。做機關的孩子不講話，蹲在一塊平石上**用炭畫水路**。岸邊一根老石樁刻著一道一道從前的水位。
- **第 4 天**：柳知微在聽風台教新人引氣，教到一半臉色發白、扶著矮几。夜裡玩家看見她**一個人提燈**出村。

你做的是這些場景裡會被看、被摸、被走過的東西。

## 1. 模型總表

| 編號 | 東西 | 格位 | 尺寸上限（寬 × 深 × 高 m） | 約 |
|---|---|---|---|---|
| UP01 | 斷流石壩（堵住／清開兩種狀態） | `D3_Weir` | 14 × 4 × 3.5 | 7 h |
| UP02 | 溫石 3 種 | `D3_WarmStone_01..03` | 每顆 0.9 × 0.7 × 0.6 以內 | 3 h |
| UP03 | 水位刻痕石樁 | `D3_WaterMark` | 0.5 × 0.4 × 1.4 | 2 h |
| UP04 | 畫了水路的平石 | `D3_DrawingStone` | 1.4 × 1.0 × 0.35 | 2 h |
| UP05 | 引氣課擺設：蒲團、矮几、小香爐 | 聽風台 `LT_QiLesson` | 蒲團 Ø0.55、矮几 0.8 × 0.45 × 0.3、香爐 0.15 | 3 h |
| UP06 | 柳知微的提燈（亮／不亮） | 拿在手上 `Socket_Hand` | 0.3 × 0.3 × 0.9（含提桿） | 2 h |
| — | 並排審圖、整理 `model_info.json`、PR | | | 1 h |
| | **合計** | | | **20 h** |

並排比較請用：A 的上游河段 `art/exports/qingxi-waterhead-a`（A01 河段、A04 泥沙洲）、河岸 v2 `art/exports/qingxi-riverbank-v2`、聽風台 `art/exports/qingxi-listening-terrace-v1.glb`。

## 2. 每一件

### UP01 斷流石壩（約 7 小時）

上游溪谷的地標，玩家第 3 天看到「溪為什麼停」的答案，第 7、8 天修好以後水重新流過。

- 構造：一道低矮的老石壩橫在溪上，中間一個木閘門（閘框是石、閘板是木），兩側壩身接進岸邊的岩石。壩頂可以走（寬約 0.9 m）。
- **兩種狀態，做成兩層**：
  - 壩本體 `Weir`：永遠在；
  - 堵塞物 `Debris`（獨立子網格）：塞在閘口的泥沙、斷木、枯枝、一團水草。遊戲第 8 天把它關掉 = 清開。
  - 閘板做成獨立物件 `Gate`，pivot 在閘框頂端，能往上拉 1.2 m（修好那天打開）。
- 生活痕跡：壩面上的苔、從石縫長出的蕨、一塊後來補上的新石（顏色淺一點）、閘框上的繩磨痕。
- 碰撞：`_Collision` 壩身（可以站上壩頂）；`Debris` 另附 `_Collision_Debris`（清開時一起關）。
- 不做水面：水由核心組的溪流材質處理。壩上游側的底部做到水線以下 0.5 m 即可。

```
UP01  Three-view and three-quarter concept of an old low stone weir across a mountain creek about 10 m wide, span about 14 m, 3.5 m high at the centre, with a walkable top about 0.9 m wide, made of fitted warm-grey granite blocks with a central stone sluice frame holding a heavy wooden sluice gate, with details: the sluice mouth choked with silt, broken logs, dead branches and a clump of water weed so that the creek below has stopped and only wet stones remain, rope-worn grooves on the sluice frame, one newer paler replacement block, moss and ferns in the joints, a few stones fallen at the foot, water: a still turquoise pool behind the weir and a nearly dry rocky creek bed below it with small puddles. Layout: one three-quarter view with the water, plus front, side and top orthographic views of the structure alone on a plain light warm-grey background, same scale.
```

### UP02 溫石（約 3 小時）

溪邊幾顆摸起來是溫的石頭。**要很淡**：玩家第一眼只覺得「這顆石頭好像怪怪的」，不是發光的寶石。

- 3 種外形（不同大小、不同裂紋），不要只靠旋轉。
- 材質參數 `_Warmth`（0–1）：
  - 0 = 普通的溪石；
  - 1 = 細細的裂紋裡透出**極淡的琥珀色**，石頭周圍一小圈苔蘚是乾的、偏黃（溫度把苔烤乾了）；
  - 不要火紅、不要岩漿感；亮度上限：在午後陽光下幾乎看不出，傍晚才看得見。
- 頂面附一個空物件 `Socket_Steam`（核心組之後可能加一縷很淡的水氣）。
- 碰撞：較大的那一顆附 `_Collision`。

```
UP02  Three-view turnaround of a group of three rounded creek-side stones, about the largest 0.9 m long and 0.6 m tall, form: smooth water-worn shapes with one or two fine hairline cracks each, half sunk into damp gravel, surface: warm grey stone with darker wet patches, the hairline cracks holding a barely visible faint amber warmth, the moss on and around the stones slightly dried and yellowed in a small ring as if warmed from inside, small ferns and grass tufts at the base. Layout: front, side and top views, same scale, plain light warm-grey background, even soft lighting.
```

### UP03 水位刻痕石樁（約 2 小時）

一根老石樁立在岸邊，從前的人在上面刻一道道橫線記水位。最低那一道也比現在的水面高很多。

- 石樁上 6–8 道深淺不同的橫刻痕、旁邊幾個小圓點（**不刻字、不刻數字**）。
- 最上面一道旁刻一個很小的波浪記號。
- 刻痕用法線＋模型凹槽，近看要看得到刻痕裡的苔。
- 碰撞：`_Collision`。

```
UP03  Three-view orthographic turnaround sheet of an old square stone post standing on a creek bank, about 0.4 m wide and 1.4 m tall, made of weathered warm-grey granite, with six to eight horizontal carved lines of different depths marking past water levels and small carved dots beside them (no letters, no numbers, no text), a tiny carved wave sign beside the highest line, showing moss growing inside the grooves, a dark old waterline stain far above the ground, lichen spots, a chipped corner, used on the bank of a creek that has nearly stopped flowing in a mountain valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```

### UP04 畫了水路的平石（約 2 小時）

做機關的孩子蹲在這塊平石上，用燒過的木炭畫溪流和水路。

- 一塊頂面平的大溪石，頂面有**炭筆畫**：彎彎的溪、幾條分出去的水路、幾個小圓圈和箭頭（像孩子畫的機關圖，**沒有字**）。
- 畫是**獨立貼圖層**（第二套 UV 或 decal 網格 `Drawing`），核心組之後可能讓它一天一天多畫幾筆；先交一張「畫了一半」的。
- 石邊放一根短炭棒（0.1 m，獨立物件）。
- 碰撞：`_Collision`（可以坐、可以站）。

```
UP04  Three-view turnaround of a single large flat-topped creek stone, about 1.4 m long, 1.0 m wide and 0.35 m tall, form: a low water-worn slab with a smooth nearly flat top surface and rounded edges, surface: warm grey stone with lichen on the sides, the flat top covered with a child's charcoal drawing of a winding creek, branching water channels, small circles and arrows like a little machine diagram (no letters, no numbers, no text), a short stick of burnt charcoal lying on the edge, small grass tufts at the base. Layout: front, side and top views, same scale, plain light warm-grey background, even soft lighting.
```

### UP05 引氣課擺設（約 3 小時）

柳知微在聽風台教引氣用。學生各坐一個蒲團（遊戲會複製擺 5–6 個），老師前面一張矮几、几上一個小香爐。

| 件 | 規格 |
|---|---|
| 蒲團 | Ø0.55 × 0.12 m，草編；2 種（新一點、舊一點壓扁的） |
| 矮几 | 0.8 × 0.45 × 0.3 m，舊木；几面一角有一塊手扶過的磨亮痕跡 |
| 小香爐 | Ø0.15 × 0.12 m，青銅、三足；附空物件 `Socket_Smoke`（核心組加一縷香煙） |

- 三件分開交（各自原點、各自 LOD）；蒲團不用碰撞，矮几附 `_Collision`。

```
UP05  Three-view orthographic turnaround sheet of a small meditation lesson set laid out together: two round woven straw meditation cushions about 0.55 m wide (one fresh, one old and flattened), a low old wooden table about 0.8 m wide, 0.45 m deep and 0.3 m tall with one corner worn shiny where a hand often rests, and a small three-legged bronze incense burner about 0.15 m wide on the table, made of woven straw, aged elm wood and patinated bronze, showing frayed straw edges, a water ring on the table, ash spilled near the burner, used on an open stone terrace where a teacher shows newcomers how to draw in spiritual breath. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.
```

### UP06 柳知微的提燈（約 2 小時）

第 4 天夜裡，玩家遠遠看見柳知微一個人提著這盞燈往山城走。遠看要認得出是**她的燈**：比村裡的燈細長、樸素。

- 一根竹提桿（0.9 m）＋一盞細長的紙燈籠（0.3 m 高），燈籠下面一個小木底。
- 燈室是**獨立發光材質**，參數 `_Lit`（0–1）；燈紙是很淡的月白色，亮的時候光偏暖白、不要橘紅。
- 附 `Socket_Hand`（提桿握的位置）。
- 和 C 自己的村口石燈 G01、TY04 守燈並排比較：三盞燈放在一起要看得出是三種不同的燈。

```
UP06  Three-view orthographic turnaround sheet of a slender hand-held paper lantern hanging from a bamboo carrying pole, the pole about 0.9 m long, the lantern about 0.3 m tall and 0.15 m wide, with a pale moon-white paper shade on a thin bamboo frame and a small dark wooden base and cap, made of split bamboo, mulberry paper and old wood, showing a small mended tear in the paper, a worn grip on the pole, a faint soot mark at the top of the shade, used by a quiet woman teacher walking alone at night on a mountain path; shown unlit. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```

（每一段後面都接 5.2 固定風格段；負面欄貼 5.3。）

## 3. 不要做

- 不要做水面、溪流、瀑布（核心組的溪流材質）。
- 不要做人物（同屆五人、柳知微都由核心組做）。
- 不要在任何東西上刻字、寫字、畫數字。
- 不改 `apps/game`、伺服器、主場景、別人的資料夾。
