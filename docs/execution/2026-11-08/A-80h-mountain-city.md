# A｜80 小時：山城街屋、分院、索橋，加山城街道小件

> 交給 Johnnnny0823（John）。2026-11-08，Claude Code 依 z1nnz 指示撰寫：「三個人都再加一份；John 80、其他人 40。」
> **第一部分**是 11/05 寫好、還沒寄出的山城包（48 小時），照原包做；**第二部分**是新的 32 小時。合計 80 小時。
> 這一輪**只做模型**，不做玩法、人物、文字。

---

## 0. 先讀

- 11/05 原包：[`docs/execution/2026-11-05/A-48h-mountain-city-architecture.md`](../2026-11-05/A-48h-mountain-city-architecture.md)
- **新的標註規則**：[`docs/standards/labeling-v1.md`](../../standards/labeling-v1.md)（分支、PR 標題、素材 README 開頭、提交訊息）
- 交件規則與提示詞固定段：照 [11/07 B 包](../2026-11-07/B-104h-tea-wheel-and-mountain-way.md) 第 1 節與附錄（Layout 段、建築 Layout 段、5.2、5.3）
- `docs/execution/2026-11-03/00-overview.md` 第 2、3 節（不重複總表）
- `docs/standards/quality-tiers-v1.md` 第 4 節

## 1. 這輪的變動

1. **你 #68 合併後推的 LOD 修正**，核心組已代開 #75 合併進 main。以後合併後要改，就開 `fix/a-<日期>-<主題>` 新分支（標註規則第 4 節）。
2. **`model_info.json` 多寫三個數字**：每個 LOD 的三角面、物件數與材質數、每張貼圖解析度。
3. 新東西做在 Unity 用的模型裡，**不再開新的網頁版頁面**。
4. 你 10/30 的後院完整版（`feature/territory-backyard-a`）審查後關閉（#77），因為 TY03／05／06 已由你在 #68 重做、TY04 由 C 做了。分支保留，不用處理。

---

## 第一部分｜11/05 山城包（48 小時）

照原包第 5、11 節做，規格、提示詞不變：

| ID | 東西 | 時數 |
|---|---|---:|
| MC01 | 山城街屋模組：石基、店面、住家、屋頂、懸挑平台、小件 | 原包 |
| TX04 | 太玄分院模組：院門、牆、正堂、廂房、鋪地與石階 | 原包 |
| MC02 | 24 m 與 12 m 索橋 | 原包 |
| **小計** | | **48** |

Codex 的山城包（D3）只做了 TX01 飛升榜，**MC01、TX04、MC02 都是你的，沒有人重複做**。

建議分支：`art/a-1105-mc01-street-houses`、`art/a-1105-tx04-branch-court`、`art/a-1105-mc02-rope-bridge`。

---

## 第二部分｜山城街道小件（32 小時）

### 為什麼做這些

MC01 的街屋拼起來以後，街上還是空的。這組小件讓山城看起來有人在這裡生活、做生意，而且和青溪村的東西一眼分得出來（山城比較高、比較擠、比較講究）。

### 要交的東西

| ID | 東西 | 尺寸上限（w×d×h） | 重點 | 時數 |
|---|---|---|---|---:|
| SF01 | 山城石燈柱 | 0.6 × 0.6 × 2.4 m | 方形石柱、頂上小石亭、燈芯 `Glow`；**和青溪的 G01 村口石燈不同**（山城款更規整、有雲紋） | 5 |
| SF02 | 跨街燈籠串 | 8 × 0.4 × 1.2 m | 一條繩上掛五盞紙燈籠，兩端掛勾接 MC01 屋簷插槽；燈籠 `Glow`，繩可沿 X 拉長 | 5 |
| SF03 | 街邊排水石槽 | 4 × 0.5 × 0.3 m | 直段、轉角、接台階的跌水段；可和 MC01 石基對齊 | 5 |
| SF04 | 山城石長椅 | 1.8 × 0.5 × 0.5 m | 整塊石板加兩個石墩，坐面磨亮；**和 RK09 觀景石凳不同** | 4 |
| SF05 | 空白布幌（3 種） | 0.6 × 0.1 × 1.8 m | 掛在店門口的長條布幌，**不寫字**；藍、赭、灰三色各一，下擺流蘇 | 5 |
| SF06 | 臨崖欄杆段 | 2 × 0.2 × 1.1 m | 木欄杆加石柱，裝在 MC01 懸挑平台邊；直段、轉角、端柱 | 5 |
| SF-組裝 | 一段 20 m 山城街道樣張 | — | 用 MC01＋SF01–06 拼一段街，附人形尺 | 3 |
| **小計** | | | | **32** |

### 規則

- 照 11/07 B 包第 1 節的交件規則，加上標註規則。
- 分支建議：`art/a-1108-sf-street-furniture`；PR 標題：`【A】11/08 SF01–SF06：山城街道小件`。
- 素材資料夾 `art/exports/mountain-street-a/README.md` 開頭照標註規則第 5 節。

### 不要做

- 不做 Codex D3 的飛升榜、大鐘、高塔；不做 B 的山城大石階 SG、山城攤位 CR10–12；不做 Dondon 的 `SectGate`、`CliffBoardwalk`。
- 不做測資台、接引棚（等故事）。
- 不做人物、文字、玩法、主場景。

### 時間順序

1. MC01（第一部分）→ 開 PR
2. TX04 → 開 PR
3. MC02 → 開 PR
4. SF01–SF06 與樣張 → 開 PR

### 物件句（正面提示 = 物件句 + 固定 Layout 段 + 5.2；負面用 5.3）

**SF01**
```text
Three-view orthographic turnaround sheet of a square carved stone lantern post for a vertical mountain city street, with a small stone pavilion-shaped lamp housing on top and cloud-scroll carving on the shaft, about 0.6 m wide and 2.4 m tall, made of dressed blue-grey granite with a warm glowing lamp inside, showing worn edges, soot above the lamp opening, lichen near the base and a chipped corner, more refined and regular than a village roadside lamp.
```

**SF02**
```text
Three-view orthographic turnaround sheet of a string of five round paper lanterns hanging from a hemp rope stretched across a narrow street, with iron hooks at both ends, about 8 m long and 1.2 m tall, made of warm-red and cream oiled paper over bamboo frames, hemp rope and dark iron, showing slightly sagging rope, faded paper on two lanterns and soot at the lantern tops.
```

**SF03**
```text
Three-view orthographic turnaround sheet of a modular carved stone drainage channel set for a mountain city street: one straight 4 m section, one corner and one stepped cascade section that drops beside stairs, about 0.5 m wide and 0.3 m deep, made of blue-grey granite with a darker wet bottom, showing algae in the wet channel, worn rims and small weeds in the joints.
```

**SF04**
```text
Three-view orthographic turnaround sheet of a long stone street bench made of one thick polished stone slab resting on two carved stone blocks, about 1.8 m long, 0.5 m deep and 0.5 m tall, made of warm-grey granite, showing a seat surface polished by years of sitting, chipped front edge and moss at the feet, more formal than a rustic roadside bench.
```

**SF05**
```text
Three-view orthographic turnaround sheet of three long blank cloth shop banners hanging from short wooden poles, one indigo blue, one ochre red and one stone grey, each about 0.6 m wide and 1.8 m long, made of coarse dyed cotton with tasselled lower edges and a wooden rod at the top, showing faded sun-bleached upper parts, frayed tassels and gentle folds, no writing or symbols on the cloth.
```

**SF06**
```text
Three-view orthographic turnaround sheet of a modular cliff-edge railing set for overhanging platforms in a vertical mountain city: one straight 2 m section with timber rails between square stone posts, one corner post and one end post, about 2 m long and 1.1 m high, made of dark old cedar and blue-grey granite, showing hand-polished top rails, weathered wood, iron brackets and lichen on the stone posts.
```
