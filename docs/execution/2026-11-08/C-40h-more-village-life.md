# C｜40 小時：更多村裡生活小物、地上小件

> 交給 Eli-0731（Eli）。2026-11-08，Claude Code 依 z1nnz 指示撰寫：「三個人都再加一份；John 80、其他人 40。」
> **接在 11/07 的 128 小時包後面做**（WL、FI、LV01–12、GC01–06、舊件 LOD）。那份做完再開始這份。
> 全部都是**基礎練習難度**：一件練一兩個技巧。不做建築、地標、人物、玩法、文字。

---

## 0. 先讀

- **新的標註規則**：[`docs/standards/labeling-v1.md`](../../standards/labeling-v1.md)
- 交件規則與提示詞固定段：照 [11/07 你的包](../2026-11-07/C-128h-creekside-and-village-life.md) 第 1 節與附錄
- `docs/execution/2026-11-03/00-overview.md` 第 2、3 節（不重複總表）

## 1. 要交的東西

**A. 村裡生活小物第二批（32 小時，每件約 4 小時）**

| ID | 東西 | 尺寸上限（w×d×h） | 練什麼 |
|---|---|---|---|
| LV13 | 竹蒸籠一疊（三層加蓋） | 0.45 × 0.45 × 0.5 m | 圓形竹圈的重複、層與層的接縫 |
| LV14 | 木提盒（三層食盒） | 0.4 × 0.3 × 0.5 m | 方盒疊放、提把的弧線、漆面磨損 |
| LV15 | 陶油燈台 | 0.2 × 0.2 × 0.4 m | 高腳燈座的旋轉體、燈芯碟 |
| LV16 | 木洗臉盆架與木盆 | 0.5 × 0.4 × 0.9 m | 三腳架的榫接、木盆的箍 |
| LV17 | 書桌小物（筆架、硯台、紙鎮） | 0.5 × 0.3 × 0.2 m | 三件小東西的比例和擺放，**不寫字** |
| LV18 | 木算盤 | 0.35 × 0.12 × 0.05 m | 很多一樣的珠子排整齊（用陣列，不是一顆顆擺） |
| LV19 | 竹簸箕（曬穀用） | 0.8 × 0.6 × 0.15 m | 一邊開口的淺籃形；**和 B 的竹篩、TE04 晾茶竹匾不同** |
| LV20 | 蒲扇與竹扇各一 | 0.4 × 0.3 × 0.05 m | 扁平物件的厚度、扇面紋路用貼圖 |

**B. 地上小件（6 小時）**

| ID | 東西 | 尺寸 | 練什麼 |
|---|---|---|---|
| GC07 | 枯枝散件一組（6 根不同形） | 每根 0.3–1.2 m | 細長形狀的彎曲和分叉，每根能單獨擺 |
| GC08 | 松果與橡實散件一組（8 顆） | 每顆 0.03–0.12 m | 很小的東西要看得清楚輪廓 |

**C. 全包檢查（2 小時）**：LV13–20 並排一張圖，配人形尺和一件舊道具。

| | 時數 |
|---|---:|
| A | 32 |
| B | 6 |
| C | 2 |
| **小計** | **40** |

## 2. 規則

- 交件規則照 11/07 包第 1 節，加上標註規則。
- 分支建議：`art/c-1108-lv13-lv20-village-props`、`art/c-1108-gc07-gc08-ground-bits`
- PR 標題：`【C】11/08 LV13–LV20：村裡生活小物第二批`
- 素材資料夾 README 開頭照標註規則第 5 節。

## 3. 不要做

- 不做已有的：B 的茶具、竹篩、背簍；TE04 晾茶竹匾；你自己的 LV01–12、陶罐 BM03；Dondon 的 `MortarPestle`、`SmithWorkbench`。
- 不做建築、地標、人物、玩法、字、主場景。

## 4. 物件句（正面提示 = 物件句 + 固定 Layout 段 + 5.2；負面用 5.3）

**LV13**
```text
Three-view orthographic turnaround sheet of a stack of three round woven bamboo steamer baskets with a domed bamboo lid, about 0.45 m wide and 0.5 m tall, made of split bamboo rings and woven bamboo bases, showing steam-darkened lower rings, slightly uneven stacking and a frayed lid edge, used in the kitchens of a lived-in mountain valley village.
```

**LV14**
```text
Three-view orthographic turnaround sheet of a three-tier wooden food carrying box with a curved carrying handle that clips over all tiers, about 0.4 m wide, 0.3 m deep and 0.5 m tall, made of old cedar with worn dark-red lacquer, showing lacquer rubbed off at the corners and handle, small brass corner pieces and a slightly misaligned middle tier, used in a lived-in mountain valley village.
```

**LV15**
```text
Three-view orthographic turnaround sheet of a simple tall-stemmed clay oil lamp stand with a shallow oil dish and a cotton wick on top, about 0.2 m wide and 0.4 m tall, made of unglazed warm-brown clay with a darker glazed dish, showing soot above the wick, oil stains running down the stem and a chipped base, used in the houses of a lived-in mountain valley village.
```

**LV16**
```text
Three-view orthographic turnaround sheet of a three-legged wooden washbasin stand holding a round wooden basin bound with bamboo hoops, a small cloth hung on one leg, about 0.5 m wide and 0.9 m tall, made of old cedar, bamboo hoops and coarse cotton, showing water stains on the basin, mortise joints on the stand and a faded cloth, used in the houses of a lived-in mountain valley village.
```

**LV17**
```text
Three-view orthographic turnaround sheet of a small set of desk objects laid out together: a wooden brush rack with three brushes, a rectangular stone inkstone with a shallow well and a plain bronze paperweight bar, group about 0.5 m wide and 0.3 m deep, made of dark wood, black inkstone, bristle brushes and aged bronze, showing dried ink in the inkstone well, worn brush tips and a dull patina on the paperweight, no writing or characters anywhere, used in a house in a lived-in mountain valley village.
```

**LV18**
```text
Three-view orthographic turnaround sheet of a wooden abacus with a dark frame, a centre beam and rows of rounded beads on thin rods, about 0.35 m wide, 0.12 m tall and 0.05 m thick, made of dark hardwood and lighter polished bead wood, showing worn corners of the frame, beads polished by use and one slightly chipped bead, used in the shops of a lived-in mountain valley village.
```

**LV19**
```text
Three-view orthographic turnaround sheet of a shallow woven bamboo winnowing basket open at one side for pouring grain, about 0.8 m wide, 0.6 m deep and 0.15 m tall, made of split bamboo with a thicker bamboo rim, showing a darker worn pouring edge, a few grains of rice caught in the weave and one repaired section, used in the yards of a lived-in mountain valley village.
```

**LV20**
```text
Three-view orthographic turnaround sheet of a round palm-leaf fan with a short handle beside a folding bamboo fan half open, about 0.4 m wide and 0.3 m tall, made of dried palm leaf, bamboo ribs and plain paper, showing a frayed palm-leaf edge, a worn handle and faded plain paper with no painting or writing, used in the houses of a lived-in mountain valley village.
```

**GC07**
```text
Three-view orthographic turnaround sheet of a set of six separate fallen dead branches of different lengths and shapes laid out apart from each other, each about 0.3 to 1.2 m long, made of grey-brown weathered bark and pale exposed wood, showing broken ends, small side twigs, patches of lichen and peeling bark, used on the forest floor near a mountain valley village.
```

**GC08**
```text
Three-view orthographic turnaround sheet of a set of eight separate small pine cones and acorns of different sizes laid out apart from each other, each about 0.03 to 0.12 m long, made of brown woody scales, glossy acorn shells and rough acorn caps, showing half-opened pine cone scales, one acorn without its cap and a little dirt on the bottoms, used on the forest floor near a mountain valley village.
```
