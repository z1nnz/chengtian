# C｜Eli-0731（約 28 小時）：山城地標、故事小道具、灌木和地被（只做模型）

> 2026-11-02，Claude Code（核心組）依 z1nnz 指示撰寫。接在 [第 3、4 天的模型](../2026-11-02/03-C-day3-4-upstream-models.md)（#62 已合併）之後。
> 不要重做的東西見[總表](00-overview.md)第 3 節。美術標準和提示詞照 [美術風格指南](../art-style-guide-v1.md)。

## 0. 這些東西在故事裡

玩家第 5 天第一次到山城，第 10 天回來測資。依[故事定稿](../../story/承天-故事定稿.md)，飛升榜和大鐘都在**太玄道院的分院**裡：匾上寫著「天之道，損有餘而補不足」，大鐘六十年沒響，飛升榜最後一行空著，硯台每天磨好墨。第 10 天有人被帶上高塔。這些都還沒有人做過。

| 編號 | 東西 | 格位 | 尺寸上限（寬 × 深 × 高 m） | 時數 |
|---|---|---|---|---:|
| L01 | 飛升榜 | `TX_AscensionBoard` | 8 × 2 × 6 | 5 |
| L02 | 大鐘和鐘架 | `TX_GreatBell` | 5 × 5 × 6.5 | 5 |
| L03 | 高塔 | `TX_HighTower` | 12 × 12 × 40 | 8 |
| L04 | 被鑿掉一行的古碑 | `D_ChiselledStele` | 1.2 × 0.6 × 2.4 | 2 |
| L05 | 小本子 | 拿在手上 | 0.1 × 0.14 | 1 |
| L06 | 舊油紙傘 | 拿在手上 | Ø1.1，長 0.9 | 1 |
| GC01 | 灌木 3 種 | 大量散布 | 高 0.6–1.6 | 2.5 |
| GC02 | 蕨 2 種 | 大量散布 | 高 0.3–0.8 | 1 |
| GC03 | 苔蘚貼片、落葉貼片 | 大量散布 | 0.5–1.5 m | 1.5 |
| — | 並排審圖、整理、PR | | | 1 |
| | **合計** | | | **28** |

格位由核心組放進地圖。

## 共同規則

每件先做 AI 三視圖：提示詞整段貼上，**後面接風格指南 5.2**，負面欄貼 **5.3**，至少出 4 張挑最好的，存 `art/references/<編號>/`。品質優先，不要求降面數；三級 LOD 同一檔案；原點在腳印中心、底部高度 0、不附地面底板；擋人的附 `_Collision`；附 `model_info.json`；四視圖加 1.75 m 人形尺，再加一張並排比較圖。**不刻字、不寫字、不寫數字**，要顯示字的地方留空，由遊戲 UI 疊上去。匯出放 `art/exports/mountain-city-c/`。

## 1. 山城地標

### L01 飛升榜（5 h）

歷代飛升者的名字，世人供奉的榜。一道高大的石框木榜，分很多欄；每欄是**獨立的空白名牌** `Slot_01..40`，字由 UI 疊上去。**最後一行整排空著**，看得出很久沒有新名字。榜前一張石案，案上一方硯台和一支筆，硯台裡的墨是濕的（有人每天磨），香爐、供品。另做一塊分院的匾 `TX_Plaque`（2.4 × 0.8 m，**正反兩面都空白**，字由遊戲疊上），算在這 5 小時內。並排比較：測資廣場 `aptitude-plaza-v1`。

```
L01  Architectural concept of a monumental honour board for those who ascended to immortality, standing in the courtyard of an old academy in a mountain city, footprint about 8 m wide and 2 m deep, 6 m high, a tall timber post-and-beam frame with gently upturned eave corners, blue-grey clay tile roof with a moss-covered ridge, a huge dark lacquered panel divided into many columns of small blank name plates (completely blank, no letters, no text), the last row of plates visibly empty and unworn, worn stone plinth with three steps, details: a stone offering table in front with a wet inkstone and a brush, incense burners, offerings of fruit, weathering: centuries of incense smoke darkening the upper panel, hands-worn railing. Layout: one three-quarter view from slightly above at eye height of a person, plus front, side and back orthographic views on the same sheet at the same scale, plain light warm-grey background, even soft lighting, building only (no landscape around it except a small ground patch).
```

### L02 大鐘和鐘架（5 h）

一口很老的青銅大鐘（直徑 1.8 m），掛在重木鐘架或小亭裡，要看得出很久沒有響過：撞擊點沒有新的磨亮，撞鐘木上有灰。撞鐘木是獨立物件 `Striker`，pivot 在吊繩頂端，可以擺動；鐘本身也能微微晃，pivot 在吊環。鐘面紋路抽象，**沒有銘文**。附 `Socket_Ring`（核心組放聲波效果）。並排比較：L01。

```
L02  Architectural concept of an open bell pavilion holding one enormous ancient bronze bell, in the courtyard of an old academy in a mountain city, footprint about 5 m wide and 5 m deep, 6.5 m high, a heavy timber post-and-beam frame with gently upturned eave corners, blue-grey clay tile roof, open on all sides, worn stone plinth with two steps, details: the bell about 1.8 m wide with abstract cloud and wave relief bands and no inscription, a long horizontal wooden striking log hung on two ropes, a stone drum seat, weathering: green patina streaks, an old dull strike mark that has not been touched for decades, dust on the striking log. Layout: one three-quarter view from slightly above at eye height of a person, plus front, side and back orthographic views on the same sheet at the same scale, plain light warm-grey background, even soft lighting, building only (no landscape around it except a small ground patch).
```

### L03 高塔（8 h）

第 10 天，有人被帶上這座塔。它很高、很安靜、窗戶很少。玩家什麼時候看得到、放在山城哪裡，由核心組決定，你只做模型。**不要畫成邪惡的黑塔**：是莊重、乾淨、白石和青瓦，只是太高太冷。七層八角，門可以開（`Door` 獨立物件）；只做外觀，內部不做。遠看的剪影要一眼認得出，LOD2 也要保留。

```
L03  Architectural concept of a tall solemn eight-sided pagoda tower of pale stone, for an ancient academy that guards a mountain city, footprint about 12 m wide and 12 m deep, seven storeys, 40 m high, timber post-and-beam eaves with gently upturned corners on every storey, blue-grey clay tile roofs with a slim bronze finial, smooth pale limestone walls with very few narrow windows, worn stone plinth with nine steps and one heavy door, details: small bronze wind chimes under the eaves, an empty stone courtyard railing, a single swept path to the door, weathering: rain streaks down the pale stone, moss only on the north side, very clean and very quiet. Layout: one three-quarter view from slightly above at eye height of a person, plus front, side and back orthographic views on the same sheet at the same scale, plain light warm-grey background, even soft lighting, building only (no landscape around it except a small ground patch).
```

## 2. 古林和故事小道具

### L04 被鑿掉一行的古碑（2 h）

第 7 天古林裡看到的石碑。碑面是風化到看不清的抽象淺刻（**不是真的字**），中間一整行被人**用鑿子鑿掉**，鑿痕粗糙，比碑面新。這是一座完整站著的碑，和你以前見聞裡的斷碑碎片不同。

```
L04  Three-view orthographic turnaround sheet of an ancient standing stone stele deep in a forest, about 1.1 m wide, 0.5 m deep and 2.3 m tall, made of dark weathered granite on a low square base, with its face covered by columns of shallow eroded carving worn beyond reading (abstract marks, no real letters, no text), one whole column violently chiselled away leaving a rough paler gouged strip, showing thick moss on the top and base, lichen, fallen needles on the base, used in an old cypress forest near a mountain village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```

### L05 小本子（1 h）

少女藏在懷裡的小本子。線裝、手掌大、邊角翻舊，開和關兩個狀態；頁面空白。和玩家的手札不同：比較小、比較可愛、封面有一小塊手縫的布補丁。

### L06 舊油紙傘（1 h）

一把舊的油紙傘，開和合兩個網格，附 `Socket_Hand`。傘面有幾處補過的痕跡，竹骨有一根用繩綁過。傘面素色，不畫圖案。

```
L05  Three-view orthographic turnaround sheet of a small thread-bound pocket notebook, about 0.1 m wide and 0.14 m tall, made of soft handmade paper and faded blue cloth with a small hand-sewn patch on the cover, showing dog-eared corners, a thread bookmark, pages completely blank with no writing, carried by a cheerful young girl. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.

L06  Three-view orthographic turnaround sheet of an old oiled-paper umbrella shown open, about 1.1 m wide and 0.9 m long, made of a plain faded amber oiled paper canopy and a split bamboo frame, showing several neatly mended patches, one rib tied with rope, a handle worn smooth, carried for many years by a travelling swordsman on mountain patrols. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```

## 3. 灌木和地被

世界的中景還是空，這一類不嫌多。**外形要和現有的 `WildShrub`、`qingxi-fern-flower-v2` 一眼看得出不同。** 面片做葉、不帶底座、直接插在地上，頂點色存風的權重。做完有力氣可以多做新品種，寫清楚是額外的。

| 編號 | 東西 | 規格 |
|---|---|---|
| GC01 | 灌木 3 種 | 1 種圓叢（溪岸）、1 種散枝帶小紅果（林緣）、1 種高而疏的山茶類（山城石階） |
| GC02 | 蕨 2 種 | 1 種長羽葉、1 種低矮捲曲的（林下） |
| GC03 | 地面貼片 | 苔蘚 3 種、落葉 3 種（楓紅、銀杏黃、褐色雜葉）；貼著地面，高度 2 cm 內，邊緣透明 |

```
GC01  Three-view turnaround of 【shrub，依序填：a round dense creek-side willow-leaf shrub about 1.2 m tall / a loose thorny forest-edge shrub about 1.0 m tall with small red berries / a tall sparse wild camellia shrub about 1.6 m tall with a few pale flowers】, form: natural irregular branching with visible twigs and clumps of leaves, surface: leaves warm sunlit yellow-green on top and cool teal-green underneath, a few fallen leaves at the base. Layout: front, side and top views, same scale, plain light warm-grey background, even soft lighting.

GC02  Three-view turnaround of 【fern，依序填：a large wild fern with long arching feathery fronds about 0.8 m tall / a low curly woodland fern about 0.3 m tall with young coiled fiddleheads】, form: fronds rising from one crown at the soil line, surface: fresh green fronds with brown dried tips on the oldest ones. Layout: front, side and top views, same scale, plain light warm-grey background, even soft lighting.

GC03  Seamless tileable square texture of 【patch，依序填：soft thick cushion moss / scattered red maple leaves / scattered golden ginkgo leaves】, viewed straight from above, real-world scale about 1 m by 1 m, hand-painted: large soft colour variation, a few painterly brush strokes, small details readable but not noisy, even flat lighting (no shadows, no highlights baked in), edges must tile seamlessly on all four sides.
```

## 4. 交件

可分兩張 PR（第 1 節一張；第 2、3 節一張），從最新 main 開分支。附三視圖、審圖、`model_info.json`、實際時數、還沒做完的地方。不改 `apps/game`、伺服器、主場景、別人的資料夾；不做人物。
