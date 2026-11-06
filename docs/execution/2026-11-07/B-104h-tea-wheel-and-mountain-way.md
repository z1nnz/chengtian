# B｜104 小時：茶田收尾、大水車，加山城石階、古林巨根、空屋變體

> 交給 joshsu54（Josh）。2026-11-07，Claude Code 依 z1nnz 指示撰寫：「沒做完的包含在新的工作包裡面，另外再加 80 小時。」
> **第一部分**是 11/05 那份 48 小時包還沒交的部分（24 小時）；**第二部分**是新的 80 小時。合計 104 小時。
> 這一輪**只做模型**，不做玩法、不做人物、不寫字。故事還在寫，跟故事綁在一起的東西（測資台、古林碑等）這輪不排。

---

## 0. 先讀

- 11/05 原包：`docs/execution/2026-11-05/B-48h-tea-and-irrigation.md`（在 GitHub `feature/qingxi-creek-chapter` 分支）
- `docs/execution/2026-11-03/00-overview.md` 第 2、3 節（不重複總表）
- `docs/art/modeling-style-spec-v1.md` 第 2、6、11 節
- `docs/standards/quality-tiers-v1.md` 第 4 節（畫質分級）
- `docs/execution/art-style-guide-v1.md` 第 5 節（提示詞固定段）
- `docs/standards/pr-review.md`
- 11/07 給大家的兩封信（遊戲改名承天、GitHub 改成 `z1nnz/chengtian`、交件多寫數字）

## 1. 交件規則（全包共用）

1. **先三視圖再建模**：每件、每種不同輪廓先生成至少四張三視圖，選一張再做灰模；候選和選圖理由存 `art/references/<ID>/prompt.txt`。
2. **畫質分級**：LOD0 不為數字減面；做 LOD1（約 50%）、LOD2（約 15%）；可有可無的小東西拆成 `Detail_*`，`model_info.json` 寫 `minTier`、`detailObjects`。
3. **`model_info.json` 多寫三個數字**（11/07 新規則）：每個 LOD 的實際三角面數、**物件數與材質數**、**每張貼圖解析度**。能合併的零件就合併，材質能共用就共用。
4. **不寫 FPS、不寫「手機跑得動」**。手機還沒實測，未驗的寫「未驗」。
5. 交 `.blend`、可重跑腳本、FBX／GLB、貼圖、四視圖（含 1.75 m 人形尺）、線框、LOD0／1 關 `Detail_*` 對照。
6. 同時只開一張待審 PR；commit 只用 `z1nnz <202040543+z1nnz@users.noreply.github.com>`，不加 AI 署名。實際工時照實寫。
7. 新東西做在 Unity 用的模型裡，**不要再開新的網頁版（PWA）頁面**。

---

## 第一部分｜11/05 沒交的部分（24 小時）

**已收到**：TE01 梯田、TE02 茶樹（含 Hedge 系列）、TE03 步道，在 `feature/tea-terraces-b` 分支。核心組會幫你開 PR 審查，你不用重交。

**還要做**（規格、提示詞照 11/05 原包第 5、11 節，不變）：

| ID | 東西 | 時數 |
|---|---|---:|
| TE04 | 採茶竹簍、晾茶竹匾 | 4 |
| TE05 | 東坡觀景亭（5×5×5 m） | 8 |
| RI03 | 稻田灌溉大水車（直徑 9 m，輪與石座、木槽分開） | 9 |
| 組裝與回匯 | 40×40 m 茶田樣張放上 TE04、TE05；RI03 和 WM02 小水車同場比 | 3 |
| **小計** | | **24** |

第一部分做完開一張 PR，再開始第二部分。

---

## 第二部分｜新的 80 小時

### 為什麼做這些

| 套件 | 在遊戲裡 | 第幾天會走到 |
|---|---|---|
| SG 山城大石階 | 從山腳一路往上到山城的正式石階，故事寫「幾千級，爬到一半回頭看，青溪村小得像一片葉子」 | 第 5 天送東西、第 10 天測資 |
| FR 古林巨根 | 古林裡「樹根從地底拱出來，比人還高，像一道道矮牆」 | 第 3、7 天 |
| VL 空屋變體 | 青溪有很多空屋（土地變差，人家搬走了），玩家分到其中一間 | 第 1 天起每天 |
| LOD 補齊 | 你以前交的大件補 LOD，讓之後的畫質選項能用 | — |

### 要交的東西

| ID | 東西 | 尺寸上限（w×d×h） | 重點 | 時數 |
|---|---|---|---|---:|
| SG01 | 寬石階直段 | 3 × 6 × 3 m（10 階） | 正式鑿切的青灰石階，兩側留欄杆插槽；**不是**現成 Dondon `MountainStoneStairs` 那種山路小階 | 6 |
| SG02 | 轉折平台 | 4 × 4 × 0.4 m | 接 SG01 上下兩端，左右可轉 90°；角落留石燈座插槽（燈用現成 G01） | 5 |
| SG03 | 石欄杆套件 | 每段 2 m，高 0.9 m | 直段、轉角柱、端柱、斜段（配 SG01 坡度）各一 | 5 |
| SG04 | 半途歇腳石亭 | 4 × 3 × 4 m | 背靠崖壁的半開石亭，石柱、石凳、一面擋雨；外形要和 RK03 茶亭、WM09 竹亭、TE05 觀景亭一眼分得出來 | 8 |
| SG-組裝 | 30 m 高的石階樣張 | — | 用 SG01–04 拼一段之字形上山路，起點擺現成 Dondon `SectGate` 當山門 | 4 |
| FR01 | 巨根矮牆段（3 種形） | 每段 6 × 2 × 2.2 m | 從地底拱出、比人高的老樹根，表面苔、裂、泥；三段可接成一道彎牆；**和現成 A04 樹根樁、A03 倒木不同** | 10 |
| FR02 | 根拱門 | 5 × 3 × 3.5 m | 兩條巨根交叉成能走過的拱，下方淨高 ≥ 2.2 m | 7 |
| FR03 | 垂藤幕（2 種） | 2 × 0.2 × 3 m | 從根和枝上垂下的藤，透明貼圖面片；`minTier: high`，標準畫質關掉也不影響走路 | 4 |
| FR04 | 獨木橋 | 7 × 1 × 1.2 m | 倒樹削平頂面當橋，兩端根盤和斷枝，可走；**和 A03 倒木不同**（這是有人整理過、真的能走的橋） | 5 |
| VL01 | 久無人住的空屋 | 照 StarterHouse 外框 | 門窗釘木板、缺瓦、簷下雜草、門前落葉；屋子的大小與輪廓照你 Dondon 的 `StarterHouse`，**另存新檔，不改原檔** | 5 |
| VL02 | 剛有人住的空屋 | 同上 | 新糊的窗紙、門前掃乾淨、窗台一盆小花；玩家第一天分到的就是這種 | 4 |
| VL03 | 半塌的空屋 | 同上 | 屋頂塌一角、一面牆倒、從缺口看得到空屋內；外圍要有碰撞，不要讓人卡進去 | 6 |
| LOD | 自己的舊件補 LOD | — | 見下表 | 11 |
| **小計** | | | | **80** |

**LOD 補齊**（LOD0 不動，只補 LOD1／LOD2 和 `Detail_*`；做前後對照圖）：

| 組 | 在哪 |
|---|---|
| `qingxi-alchemy-b` | `art/exports/` |
| `creek-repair-b-props` | `art/exports/` |
| `StarterHouse`、`TownLayout` 裡會用在青溪的房屋 | `art/incoming/dondon/`（TownLayout 整包約 90 萬面，最需要 LOD） |

### 在世界裡的位置

- SG：B1 山門石階區塊，從山腳到 B2 測資廣場。核心組落位，你只交模型與 `stair-assembly.json`（每件編號、位置、旋轉）。
- FR：D 古林（D1 林緣到 D2 神木一帶）。核心組落位。
- VL：A1 青溪村各處空屋格位。核心組落位。
- **不改主場景、不改區塊 JSON、不自己宣稱已正式落位。**

### 風格

- 先看 `qingxi-world-ruins-b`、`tea-terraces-b`（你自己的）、`qingxi-encounter-a`、Dondon `SectGate`、`StarterHouse`。
- SG 跟 TE01 擋土牆同一種暖灰石，但更規整（這是山城的正式石階，不是農田）。
- FR 的根要像 `elder-world-tree-hero-v1` 神木的根那種老。
- 每套灰模和材質各一張同光同角度並排，含 1.75 m 人形尺；README 寫出和既有件的三個共同點；一眼不合就 FAIL。

### 驗收

- SG 樣張：人形尺從山門走到 30 m 高，台階高度、寬度一致，欄杆接縫 ≤ 2 mm。
- FR02、FR04：用人形尺示範能走過、能走上去，附碰撞。
- VL：三種空屋和 StarterHouse 原版四棟並排一張圖，一眼看得出差別，輪廓仍是同一種房子。
- 每件 QA errors = 0、FBX 回匯誤差 ≤ 2 cm、原點與底部正確；逐件標 Exported／Imported／Visually Verified／In-game Verified，沒驗的寫未驗。

### 不要做

- 不做 Dondon 已有的：`SectGate` 山門、`MountainStoneStairs`、`LayeredCliff`、`CliffBoardwalk`、`MossBoulderSet`。
- 不做 Codex D3 的山城街屋、分院、索橋、飛升榜、大鐘、高塔；不做 D2 的苔石古祠、發光蕈。
- 不做測資台、接引棚、古林碑、坑、樹洞（等故事）。
- 不做人物、文字、玩法、主場景、伺服器。

### 時間順序

1. 第一部分 TE04、TE05、RI03（24h）→ 開 PR
2. SG01–04 與樣張（28h）→ 開 PR
3. FR01–04（26h）→ 開 PR
4. VL01–03 與 LOD 補齊（26h）→ 開 PR

---

## 附：三視圖提示詞

### 固定段（每條都要原樣接上，不能改）

**單件物品的 Layout 段**（接在每條物件句後面）：

```text
Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```

**建築的 Layout 段**（SG04、VL01–03 用這段）：

```text
Layout: one three-quarter view from slightly above at eye height of a person, plus front, side and back orthographic views on the same sheet at the same scale, plain light warm-grey background, even soft lighting, building only (no landscape around it except a small ground patch).
```

**5.2 美術方向**（每條正面提示的最後一段）：

```text
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

**5.3 負面提示**（每條都用這段）：

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

**正面提示 = 物件句 + Layout 段 + 5.2。** 下面是每件已填好的物件句。

### 物件句

**SG01**
```text
Three-view orthographic turnaround sheet of a straight run of ten broad formal carved stone steps climbing a mountain, with square sockets on both sides for balustrade posts, about 3 m wide, 6 m long and 3 m rise, made of dressed blue-grey granite blocks with warm-grey worn treads, showing foot-polished centres, chipped nosings, moss only in the shaded side joints and a few weeds in the cracks, used on the long stair climbing to a vertical mountain city above a valley village.
```

**SG02**
```text
Three-view orthographic turnaround sheet of a square stone landing platform where a mountain stairway turns ninety degrees, with a round stone lantern base at one corner, about 4 m wide, 4 m deep and 0.4 m thick, made of large dressed blue-grey granite slabs with warm-grey worn surface, showing slab seams with soil and moss, rain stains and a worn path across the centre, used on the long stair climbing to a vertical mountain city above a valley village.
```

**SG03**
```text
Three-view orthographic turnaround sheet of a modular carved stone balustrade set: one straight 2 m rail section with square posts, one corner post, one end post with a simple cloud-scroll cap and one sloped section for a stairway, about 2 m long and 0.9 m high, made of blue-grey granite, showing worn rounded handrail tops, small chips, lichen on the posts and soil at the base, used on the long stair climbing to a vertical mountain city above a valley village.
```

**SG04**
```text
Architectural concept of a small half-open stone rest shelter built against a mountain cliff halfway up a long stairway, footprint about 4 m wide and 3 m deep, 4 m high, two square stone columns at the front, the back and one side formed by the rough cliff face, a single-slope blue-grey tile roof, a long stone bench along the cliff wall and a low stone water basin, weathering: rain streaks down the cliff, moss on the roof edge, a cracked bench corner repaired with a fitted stone, clearly different from a four-post timber tea pavilion or a bamboo pavilion.
```

**FR01**
```text
Three-view orthographic turnaround sheet of a long section of giant ancient tree roots arching out of the forest floor like a low wall taller than a person, about 6 m long, 2 m deep and 2.2 m high, made of thick gnarled dark-brown bark with deep cracks and smooth worn upper ridges, showing packed earth and small stones caught between the roots, thick green moss on the shaded side, ferns sprouting from crevices and exposed pale root tips, used in an ancient old-growth forest beside a mountain valley village.
```

**FR02**
```text
Three-view orthographic turnaround sheet of two giant ancient tree roots crossing overhead to form a natural arch that a person can walk under, about 5 m wide, 3 m deep and 3.5 m high, with at least 2.2 m clear height beneath, made of thick gnarled dark-brown bark with deep cracks, showing hanging root tendrils, moss on top, soil and stones gripped at both feet, and a trodden earth path passing through, used in an ancient old-growth forest beside a mountain valley village.
```

**FR03**
```text
Three-view orthographic turnaround sheet of a curtain of hanging forest vines and aerial roots dropping from above, about 2 m wide and 3 m long, thin and layered, made of slender green and brown vines with small leaves and pale root threads, showing a few dry brown strands, uneven tips and drops of dew, used in an ancient old-growth forest beside a mountain valley village.
```

**FR04**
```text
Three-view orthographic turnaround sheet of a fallen giant tree trunk with its top carefully adzed flat to serve as a footbridge across a forest stream, about 7 m long, 1 m wide and 1.2 m high, made of old dark-brown bark and lighter flattened heartwood, showing a root plate with soil at one end, broken branch stubs, adze marks on the walking surface, moss along the sides and a worn path along the top, used in an ancient old-growth forest beside a mountain valley village.
```

**VL01**
```text
Architectural concept of a small long-abandoned single-storey village house with white plaster walls and a blue-grey tile roof in a warm mountain valley village, footprint about 7 m wide and 6 m deep, timber frame on a low stone base, the door and lattice windows boarded over with nailed old planks, several missing roof tiles, grass and small weeds growing along the eaves and roof ridge, fallen leaves piled at the threshold, weathering: peeling plaster showing mud brick, faded timber, rust streaks under the nails.
```

**VL02**
```text
Architectural concept of a small single-storey village house that someone has just moved into, white plaster walls and a blue-grey tile roof in a warm mountain valley village, footprint about 7 m wide and 6 m deep, timber frame on a low stone base, freshly pasted white paper on the lattice windows, the doorstep newly swept, a small clay flower pot on the window sill, old wood still faded but the house cared for, weathering: old repairs in the plaster, a few replaced roof tiles of a slightly different colour.
```

**VL03**
```text
Architectural concept of a small half-collapsed abandoned village house, white plaster walls and a blue-grey tile roof in a warm mountain valley village, footprint about 7 m wide and 6 m deep, one roof corner caved in with broken rafters, one side wall fallen into a heap of mud brick and tiles so the empty interior is visible, a young tree growing through the gap, weathering: blackened damp timber, moss on the fallen tiles, weeds over the rubble.
```
