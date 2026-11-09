# B｜112 小時：不同外形的民居、舊建築換材質、路上地標

> 交給 joshsu54（Josh）。2026-11-09，Claude Code 依 z1nnz 指示撰寫：「給新的工作包吧」；對象和大小由 z1nnz 選定：只給 Josh，112 小時。
> 這一輪**只做模型**，不做玩法、人物、文字。

---

## 0. 先讀

- **世界施工圖**：[`docs/execution/world-blueprint/README.md`](../world-blueprint/README.md)（在分支 `game/core-1108-world-east-valley`）。這包的東西都是施工圖上還缺的，第 2 節寫了各放在哪個區塊。
- 標註規則：[`docs/standards/labeling-v1.md`](../../standards/labeling-v1.md)
- 交件規則與提示詞固定段：照 [11/07 你的包](../2026-11-07/B-104h-tea-wheel-and-mountain-way.md) 第 1 節與附錄（單件 Layout 段、建築 Layout 段、5.2、5.3）
- 風格色票：[`docs/art/modeling-style-spec-v1.md`](../../art/modeling-style-spec-v1.md) 第 11 節
- 畫質分級：`docs/standards/quality-tiers-v1.md` 第 4 節

## 1. 這輪的變動

1. **commit 用你自己的 GitHub 帳號**，不用 z1nnz，也不掛 Claude Code 或其他 AI 的名字。你最近的 PR 都做對了，繼續這樣。如果你用助手代為提交，也要告訴它這條。
2. **Unity 檢查請用 6000.0.82f1**（專案指定版本）。你那台還沒裝，請從 Unity Hub 裝這一版。裝不了就在 PR 寫明用哪一版，不用停工，核心組接入時會再跑。
3. **一批很多件，先做一件樣品**：VH01、RS01、PS01 各先交一件樣品，開在該批的 PR 上。沒有等到回覆也可以繼續做其他件，不用等核心組；審查意見來了再改。
4. **可以同時開多張 PR**，第 4 節分了三批，每批一張。
5. 核心組負責擺進世界。**不改主場景、不改區塊 JSON。**

## 2. 要交的東西

### A｜村子（青溪村 A1）：50 小時

你的 VL01–05 外框相同，遠看輪廓都一樣；Dondon 的舊建築又是光滑的藍綠屋頂，和 VL 放在一起不搭。這批解決這兩件事。

| ID | 東西 | 尺寸上限（w×d×h） | 重點 | 時數 |
|---|---|---|---|---:|
| VH01 | 兩層民居 | 8 × 7 × 7.5 m | 比 VL 高一層：底層石木、二層木構出挑、一道小外廊，屋頂比 VL 陡。遠看要一眼看出是另一種房子 | 12 |
| VH02 | 曲尺形院落民居 | 12 × 10 × 5.5 m | L 形平面，兩翼圍出小院，院牆和一扇小門。院內留 5 × 4 m 空地放菜圃（菜圃不用做） | 12 |
| VH03 | 窄長小屋 | 5 × 9 × 5 m | 山牆朝路的窄長屋，一側開門，屋後接一段矮棚。放在巷子裡補空隙用 | 5 |
| RS01 | 客棧換材質 | 照原模型 | Dondon `TownLayout` 裡的客棧（#85 的 `lod-backfill-b` 已取出）：**外形不動**，瓦、牆、木、石全部換成 VL 那一套質感 | 6 |
| RS02 | 鐵匠鋪、材料鋪換材質 | 照原模型 | Dondon `Blacksmith`、`MaterialShop`，同上 | 6 |
| RS03 | 山門換材質 | 照原模型 | Dondon `SectGate`：**外形不動**。現在是鮮豔青綠加光滑材質，放在你的 SG 石階前很突兀。改成舊木、深瓦、銅件、石基，顏色收斂，有雨痕和磨損 | 6 |
| LT01 | 村口石燈（中式） | 0.7 × 0.7 × 1.8 m | 現在的 G01 太像日式石燈籠。做一款**方正、敦實的中式石燈**：方形燈室、四角微翹的石頂、素面方柱、石座，燈芯 `Glow`。尺寸和原點照 G01，可直接換；G01 原檔不要改 | 3 |

- RS01–RS03 **都另存新檔，不改原檔**，資料夾 `art/exports/village-reskin-b/`；每件附和原版同光同角度的並排圖。
- VH 系列資料夾 `art/exports/village-houses-b/`（延續 VL），共用 VL 的三張圖集，能共用就不要新開。

### B｜路上的地標：43 小時

玩家走到這些地方，要有東西值得停下來。全部是**沒有人住、沒有文字**的舊東西。

| ID | 東西 | 尺寸上限（w×d×h） | 放在哪 | 重點 | 時數 |
|---|---|---|---|---|---:|
| PS01 | 舊驛站 | 14 × 10 × 6 m | A9 官道南段 | 官道邊廢棄的驛站：前面有拴馬木欄的院子、一排馬廄棚、主屋。半荒，但沒有塌。**和 VL 外形不同** | 11 |
| PS02 | 斷橋 | 14 × 4 × 5 m | A9 路的盡頭 | 被山洪沖斷的石拱橋，只剩兩端橋頭和斷口，河床有落石。**和 WM07、Dondon `StoneArchBridge` 不同**，碰撞要讓人走到斷口就停下來 | 6 |
| BT01 | 舊烽台 | 8 × 8 × 7 m | A7 東坡山脊 | 山脊上塌了一半的圓形石砌烽火台，留一道可以爬上去的殘階，頂上能站人看風景 | 8 |
| FS01 | 田間小廟 | 2.4 × 2 × 2.6 m | A6 稻田 | 田邊的小石龕加矮瓦頂，前面一個小香爐。**和 RK06 土地祠、D3 倒下的小廟外形不同**，不寫字 | 5 |
| RI04 | 稻草人（2 種） | 1.2 × 0.5 × 1.9 m | A6 稻田 | 木十字架綁稻草，舊衣、斗笠，一個歪一點。**Codex 版因太硬、像管子拼的而沒過，你重做**，要有稻草蓬鬆的輪廓 | 3 |
| FE04 | 曬網架與繫纜樁 | 3 × 1 × 2 m | A5 渡口 | 竹木架掛一張舊漁網（`Detail_*`）；另有粗短繫纜木樁 2 種，磨出繩痕 | 4 |
| BS01 | 山腳界碑 | 1 × 0.5 × 2 m | D6 山腳 | 一塊未刻字的舊石碑立在石座上，頂部略殘。**不寫字**，留 `Socket_Inscription` | 2 |
| VH-檢查 | 村子樣張 | — | — | VH01–03、VL01–05、RS01–02 擺成一段 30 m 的巷子，附人形尺 | 4 |

（VH-檢查的 4 小時算在這批。）

### C｜古林與山路：19 小時

| ID | 東西 | 尺寸上限（w×d×h） | 放在哪 | 重點 | 時數 |
|---|---|---|---|---|---:|
| LG01 | 倒伏巨木橋 | 22 × 5 × 4 m | D5 蕈谷 | 比 FR04 大很多的倒樹橫過谷底，樹根盤翹起，表面長苔和蕈。沿著樹幹上方**可以走**，兩端和地面順接 | 5 |
| FO02 | 發光蕈群（3 種叢） | 1.2 × 1.2 × 0.8 m | D5 蕈谷 | 蕈傘有厚度和弧度，大小不一，傘底 `Glow`（青色、面積少）。**Codex 版形狀太簡單、像玩具而沒過，你重做**；和 Eli 的普通野菇 GC04 不同 | 4 |
| SG05 | 寬版大石階直段 | 6 × 3.2 × 2.1 m | B1 山門 | 你的 SG01 寬 3 m，主階要更有氣勢。做**寬 6 m** 版，正中一條雕花御路石；階高、踏面、接口和 SG01 相同，可接 SG03 欄杆 | 4 |
| SG06 | 寬版轉折平台 | 7 × 7 × 0.8 m | B1 山門 | 接 SG05，地磚鋪法和 SG02 同一語言，四角燈座插槽 | 2 |
| 全包檢查 | 路上地標並排 | — | — | PS01、BT01、FS01、LG01 各一張 1.7 m 人眼圖，SG05＋SG06 接 RS03 山門一張 | 4 |

| 批 | 時數 |
|---|---:|
| A 村子 | 50 |
| B 路上的地標（含樣張 4） | 43 |
| C 古林與山路（含檢查 4） | 19 |
| **合計** | **112** |

## 3. 風格與驗收

- **A、B 用河谷語言**：石木、深色舊木、黛瓦 `#3A4048`，不要鮮豔藍綠屋頂。放在 VL 旁邊要像同一個村。
- **不要日式、歐式**：屋頂、窗、燈都不要町屋感或木骨感。#80 的審查意見可以參考。
- **C 用古林語言**：苔綠 `#3F5A2E`、深樹皮 `#2B2018`；**SG、RS03 用灰白花崗石**，花崗白 `#C9C6BD`。
- 每件照 11/07 包第 1 節交齊：三視圖、灰模、線框、LOD 對照、人形尺。
- 能走的地方（BT01 殘階和頂、LG01、PS01 院子、SG05–06）要附 1.75 m 膠囊走過的檢查。
- 逐件標 Exported／Imported／Visually Verified／In-game Verified，沒驗的寫未驗。

## 4. 分支與 PR

| 批 | 分支 | PR 標題 |
|---|---|---|
| A | `art/b-1109-vh-village-houses` | `【B】11/09 VH01–03、RS01–03、LT01：民居新外形與舊建築換材質` |
| B | `art/b-1109-ps-roadside-landmarks` | `【B】11/09 PS01–02、BT01、FS01、RI04、FE04、BS01：路上地標` |
| C | `art/b-1109-lg-forest-and-stairs` | `【B】11/09 LG01、FO02、SG05–06：倒木、發光蕈與寬版石階` |

素材資料夾 README 開頭照標註規則第 5 節。

## 5. 不要做

- 不做已有的：VL01–05、R01 乾砌石牆、R02 竹籬、R03 柴堆、R04 石燈、R05 里程石、WM07 石橋、SG01–04、FR01–04、FP01–05、TE05、RK03、RK06、FE01–03、A11 舊亭。
- 不做等故事的：古林碑、塌牆小祠、神木旁的坑、中空倒樹、測資台、接引棚、戊辰年瓦。
- 不做 John 的 MC、TX、ST；不做 Eli 的 WL、FI、LV、GC。
- 不做人物、文字、玩法、主場景；不開新的網頁版頁面。

## 6. 物件句（正面提示 = 物件句 + 固定 Layout 段〔建築用建築 Layout 段〕 + 5.2；負面用 5.3，另加下面這句）

每條負面都加上：

```text
not Japanese machiya, no noren, no round paper lanterns, no Japanese stone toro lantern, not Tudor half-timbering, no diagonal braces on plaster walls, no bright teal roof, no glossy plastic look
```

**VH01**
```text
Three-view orthographic turnaround sheet of a modest two-storey rural Chinese farmhouse, about 8 m wide, 7 m deep and 7.5 m tall, with a stone and timber ground floor, an overhanging timber upper floor with a small narrow gallery, plaster infill panels with plain vertical wooden lattice windows, and a fairly steep dark grey clay tile gable roof with restrained upturned eaves, old weathered dark wood and repaired plaster, lived-in but unadorned, no writing.
```

**VH02**
```text
Three-view orthographic turnaround sheet of a modest L-shaped rural Chinese courtyard house, about 12 m wide, 10 m deep and 5.5 m tall, two single-storey wings meeting at a corner around a small open yard enclosed by a low stone and plaster wall with one small timber gate, dark grey clay tile roofs at two ridgelines, old weathered wood, stone footing, empty yard floor of packed earth, no writing.
```

**VH03**
```text
Three-view orthographic turnaround sheet of a narrow long rural Chinese cottage, about 5 m wide, 9 m deep and 5 m tall, its gable end facing the lane, entrance door on the long side, plaster and timber walls on a low stone footing, dark grey clay tile roof, a low lean-to shed attached at the rear, old weathered materials, no writing.
```

**LT01**
```text
Three-view orthographic turnaround sheet of a solid squared-off Chinese village stone lantern, about 0.7 m wide and 1.8 m tall, a plain square stone post on a stepped square base, a square lantern chamber with simple rectangular openings, and a low four-sided stone cap with only slightly lifted corners, weathered grey stone with moss at the base, sturdy and plain, no writing.
```

**PS01**
```text
Three-view orthographic turnaround sheet of an abandoned rural Chinese roadside post station, about 14 m wide, 10 m deep and 6 m tall, a main single-storey building with a dark grey tile roof, a row of open-sided timber stable sheds, and a small front yard fenced with a worn wooden hitching rail, missing tiles and faded plaster but still standing, overgrown edges, no people, no horses, no writing.
```

**PS02**
```text
Three-view orthographic turnaround sheet of a broken old Chinese stone arch bridge washed out by a flood, about 14 m long, 4 m wide and 5 m tall, two surviving abutments with the start of the arch on each side and a wide gap in the middle, rough fractured stone edges, fallen stone blocks below, grey weathered masonry with moss, no writing.
```

**BT01**
```text
Three-view orthographic turnaround sheet of a half-collapsed old round stone beacon tower on a mountain ridge, about 8 m in diameter and 7 m tall, dry-laid grey stone courses, one side fallen into a rubble slope, a surviving narrow stone stair climbing to a broken flat top, weathered and wind-worn with dry grass in the cracks, no writing.
```

**FS01**
```text
Three-view orthographic turnaround sheet of a tiny roadside field shrine in Chinese farmland, about 2.4 m wide, 2 m deep and 2.6 m tall, a small stone niche under a low dark tile roof on a stepped stone base, an empty interior with no statue, a small stone incense burner in front, worn and rain-stained, no writing.
```

**RI04**
```text
Three-view orthographic turnaround sheet of a rural Chinese scarecrow, about 1.9 m tall, a rough wooden cross frame wrapped in bundles of loose fluffy rice straw, wearing a tattered faded cloth tunic and a worn conical straw hat, irregular natural silhouette with straw sticking out, leaning slightly, no face, no writing.
```

**FE04**
```text
Three-view orthographic turnaround sheet of a small riverside net-drying rack and mooring posts, about 3 m wide and 2 m tall, a simple bamboo and wood frame with an old fishing net draped over it, plus two thick short wooden mooring posts with worn rope grooves, damp weathered wood, no people, no writing.
```

**BS01**
```text
Three-view orthographic turnaround sheet of an old blank Chinese boundary stone at the foot of a mountain, about 1 m wide and 2 m tall, a plain upright granite stele with a slightly chipped top on a simple rectangular stone base, moss on the lower part, the face completely smooth and blank, no writing, no carving.
```

**LG01**
```text
Three-view orthographic turnaround sheet of an enormous fallen ancient tree lying across a forest ravine as a natural bridge, about 22 m long, 5 m wide and 4 m tall, a huge root plate lifted at one end, broken branches at the other, thick cracked dark bark covered in moss and shelf fungus, a worn walkable line along the top of the trunk, no writing.
```

**FO02**
```text
Three-view orthographic turnaround sheet of a cluster of glowing forest mushrooms, about 1.2 m wide and 0.8 m tall, several mushrooms of very different sizes with thick domed caps, curved fleshy stems and gills under the caps, muted dark caps with a faint cool cyan glow only from the underside, organic and slightly irregular, growing from moss and dark soil, not cute, not cartoon, no writing.
```

**SG05**
```text
Three-view orthographic turnaround sheet of a wide formal Chinese granite stairway section, about 6 m wide, 3.2 m deep and 2.1 m tall, thirteen even steps of grey-white granite, a central carved stone ramp panel with a low-relief cloud pattern running up the middle, side stringers with square sockets for stone railings, weathered edges and a little moss, no writing.
```

**SG06**
```text
Three-view orthographic turnaround sheet of a wide square granite stair landing, about 7 m wide, 7 m deep and 0.8 m tall, large grey-white granite paving slabs in a formal layout with a central panel, low stone kerb, four small round lantern seats at the corners, weathered edges and a little moss, no writing.
```

RS01、RS02、RS03 是換材質，**不用出三視圖**；交原版和新版同光同角度的並排圖就好。

---

有問題直接問；寫不清楚的地方先照最保守的做法做，寫進 PR。
