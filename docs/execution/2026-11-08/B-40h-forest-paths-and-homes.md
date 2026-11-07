# B｜40 小時：古林步道套件、有人住的民居變體

> 交給 joshsu54（Josh）。2026-11-08，Claude Code 依 z1nnz 指示撰寫：「三個人都再加一份；John 80、其他人 40。」
> **接在 11/07 的 104 小時包後面做**（你已交第一部分 PR #79，剩 SG、FR、VL、LOD）。這份不用等那份做完才能開始，但建議照順序。
> 這一輪**只做模型**，不做玩法、人物、文字。

---

## 0. 先讀

- **新的標註規則**：[`docs/standards/labeling-v1.md`](../../standards/labeling-v1.md)
- 交件規則與提示詞固定段：照 [11/07 你的包](../2026-11-07/B-104h-tea-wheel-and-mountain-way.md) 第 1 節與附錄
- `docs/execution/2026-11-03/00-overview.md` 第 2、3 節（不重複總表）

## 1. 為什麼做這些

| 套件 | 在遊戲裡 |
|---|---|
| FP 古林步道 | 玩家第 3、7 天從青溪走進古林。現在古林只有零件（巨根、倒木、苔石），還沒有「路」，玩家不知道往哪走。這套讓林子裡有一條看得出來、走得上去的小路 |
| VL 民居變體 | 你 11/07 的 VL01–03 是空屋；村裡也要有「有人住」的屋子，而且不能每間都一樣 |

## 2. 要交的東西

| ID | 東西 | 尺寸上限（w×d×h） | 重點 | 時數 |
|---|---|---|---|---:|
| FP01 | 林間土路直段 | 6 × 1.6 × 0.3 m | 踩實的土路、兩側落葉與蕨、路面有樹根淺淺露出；兩端截面相同可接 | 4 |
| FP02 | 林間土路彎段（左、右） | 6 × 6 × 0.3 m | 30° 與 60° 各一，接口和 FP01 同截面 | 5 |
| FP03 | 林間土路坡段 | 6 × 1.6 × 1.5 m | 上升 1.2 m，坡度 ≤ 25°，可走 | 4 |
| FP04 | 巨根橫過的路段 | 6 × 2 × 0.8 m | 一條粗根橫越路面，被踩出一個凹口讓人跨過；**接 FR01 巨根的風格** | 5 |
| FP05 | 原木階梯段 | 1.6 × 3 × 1.5 m | 半埋的圓木當踏階，木樁固定；接 FP01 截面 | 4 |
| FP-組裝 | 40 m 古林小路樣張 | — | FP01–05 拼一條上下坡、轉兩次彎的小路，旁邊擺 FR 巨根與現成倒木、苔石，附人形尺與行走檢查 | 3 |
| VL04 | 有人住的民居（勤快人家） | 照 StarterHouse 外框 | 門前晾衣竹竿與衣物、牆邊整齊柴堆、窗台曬乾菜、門口一雙鞋 | 5 |
| VL05 | 有人住的民居（老人家） | 同上 | 門口小竹椅、屋簷下吊一串乾玉米、窗紙補過好幾塊、門邊一盆老盆景 | 5 |
| 檢查 | VL01–05 五種並排、FP 行走 | — | — | 5 |
| **小計** | | | | **40** |

- VL04、VL05 和 VL01–03 一樣**另存新檔，不改 Dondon 的 `StarterHouse` 原檔**。門前小物要做成 `Detail_*`，低畫質可以關掉。
- FP 的路面要可走（MeshCollider 或簡化碰撞），接縫 ≤ 2 mm。

## 3. 規則

- 交件規則照 11/07 包第 1 節，加上標註規則。
- 分支建議：`art/b-1108-fp-forest-paths`、`art/b-1108-vl-lived-homes`
- PR 標題：`【B】11/08 FP01–FP05：古林步道套件`、`【B】11/08 VL04–VL05：有人住的民居變體`
- 素材資料夾 README 開頭照標註規則第 5 節。

## 4. 不要做

- 不做已有的：Dondon `MountainStonePath`、`MountainStoneStairs`；`qingxi-winding-road-v1`、`qingxi-road-props-v12／v13` 的村路；TE03 茶田步道；A 的碎石小徑 TY10。FP 是**林子裡的土路**，要和這些一眼分得出來。
- 不做古林碑、坑、樹洞（等故事）；不做人物、文字、玩法、主場景。

## 5. 物件句（正面提示 = 物件句 + 固定 Layout 段〔VL 用建築 Layout 段〕 + 5.2；負面用 5.3）

**FP01**
```text
Three-view orthographic turnaround sheet of a straight modular section of a narrow trodden dirt footpath through an ancient forest, with identical cross-sections at both ends, about 6 m long and 1.6 m wide, made of packed dark-brown forest soil, thin roots showing at the surface, fallen leaves and ferns along both edges, showing a worn centre line, small stones pushed to the sides and moss creeping onto the edges.
```

**FP02**
```text
Three-view orthographic turnaround sheet of two curved modular sections of a narrow trodden dirt footpath through an ancient forest, one bending 30 degrees and one bending 60 degrees, each matching a 1.6 m wide straight path at both ends, made of packed dark-brown forest soil, thin surface roots, fallen leaves and ferns along the edges, showing the worn inner curve where people cut the corner.
```

**FP03**
```text
Three-view orthographic turnaround sheet of a sloping modular section of a narrow trodden dirt footpath climbing 1.2 m through an ancient forest, about 6 m long and 1.6 m wide, made of packed dark-brown forest soil with a few flat stones pressed into the steepest part for footing, showing erosion grooves from rain, exposed roots holding the slope and ferns on both banks.
```

**FP04**
```text
Three-view orthographic turnaround sheet of a modular dirt footpath section in an ancient forest where one thick gnarled tree root crosses the path, worn down into a shallow notch where people step over it, about 6 m long, 2 m wide and 0.8 m high, made of dark-brown bark polished smooth on the notch, packed forest soil, moss and fallen leaves, showing the bright worn wood in the notch and mud on both sides of the root.
```

**FP05**
```text
Three-view orthographic turnaround sheet of a short flight of rustic log steps set into a forest slope, half-buried round logs held by wooden stakes with packed soil behind each log, about 1.6 m wide, 3 m long and 1.5 m rise, made of old dark logs, pale stake heads and dark-brown forest soil, showing moss on the log ends, worn tops of the logs and one replaced log of lighter colour.
```

**VL04**
```text
Architectural concept of a small lived-in single-storey village house belonging to a hard-working family, white plaster walls and a blue-grey tile roof in a warm mountain valley village, footprint about 7 m wide and 6 m deep, timber frame on a low stone base, bamboo poles with drying clothes in front of the door, a neatly stacked woodpile along one wall, dried vegetables on the window sill and a pair of straw sandals at the doorstep, weathering: repaired plaster, well-swept ground, faded but cared-for timber.
```

**VL05**
```text
Architectural concept of a small lived-in single-storey village house belonging to an elderly couple, white plaster walls and a blue-grey tile roof in a warm mountain valley village, footprint about 7 m wide and 6 m deep, timber frame on a low stone base, a small bamboo chair by the door, a string of dried corn cobs hanging under the eaves, window paper patched in several places, an old potted bonsai beside the door, weathering: very old dark timber, moss on the stone base, roof tiles of mixed age.
```
