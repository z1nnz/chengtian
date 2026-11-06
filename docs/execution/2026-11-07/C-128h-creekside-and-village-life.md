# C｜128 小時：西溪洗衣釣具，加村裡生活小物、地上小石與野菇

> 交給 Eli-0731（Eli）。2026-11-07，Claude Code 依 z1nnz 指示撰寫：「沒做完的包含在新的工作包裡面，另外再加 80 小時。」
> **第一部分**是 11/05 那份 48 小時包（還沒收到交件，整包照做）；**第二部分**是新的 80 小時。合計 128 小時。
> 全部都是**基礎練習難度**的小道具：一件練一兩個技巧。不做建築、地標、人物、玩法、文字。

---

## 0. 先讀

- 11/05 原包：`docs/execution/2026-11-05/C-48h-a3-creekside-life.md`（在 GitHub `feature/qingxi-creek-chapter` 分支）
- 11/03 基礎練習包：`docs/execution/2026-11-03/C-28h-modelling-basics.md` 第 0–2 節（你做 BM01–BM10 的方法照舊）
- `docs/execution/2026-11-03/00-overview.md` 第 2、3 節（不重複總表）
- `docs/art/modeling-style-spec-v1.md` 第 2、6、11 節
- `docs/standards/quality-tiers-v1.md` 第 4 節（畫質分級）
- `docs/execution/art-style-guide-v1.md` 第 5 節（提示詞固定段）
- 11/07 給大家的兩封信（遊戲改名承天、GitHub 改成 `z1nnz/chengtian`、交件多寫數字）

## 1. 交件規則（全包共用）

1. **先三視圖再建模**：每件先生成至少四張三視圖，選一張再做灰模；候選和選圖理由存 `art/references/<ID>/prompt.txt`。
2. **一件一個重點**：每件下面寫了「練什麼」，做的時候先把那一點做好，不用追求很多細節。
3. **畫質分級**：LOD0 不減面；做 LOD1（約 50%）、LOD2（約 15%）；可有可無的小東西拆成 `Detail_*`，`model_info.json` 寫 `minTier`、`detailObjects`。
4. **`model_info.json` 多寫三個數字**（11/07 新規則）：每個 LOD 的實際三角面數、**物件數與材質數**、**每張貼圖解析度**。小道具一件一個材質、貼圖 1024 以內就很好。
5. **不寫 FPS、不寫「手機跑得動」**。沒驗的寫「未驗」。
6. 交 `.blend`、FBX／GLB、貼圖、四視圖（含 1.75 m 人形尺）、線框、LOD0／1 對照。
7. 同時只開一張待審 PR；commit 只用 `z1nnz <202040543+z1nnz@users.noreply.github.com>`，不加 AI 署名。實際工時照實寫。
8. 不要只靠旋轉、縮放、換色充件數；每件要有自己的外形。

---

## 第一部分｜11/05 的西溪洗衣與釣具（48 小時）

整包照 11/05 原包做，規格、尺寸、提示詞都在原包第 5、11 節，不變：

| ID | 東西 | 時數 |
|---|---|---:|
| WL01–WL05 | 洗衣板、洗衣木槌、捲起的粗布、折好的濕布兩疊、石製皂灰盤 | 21 |
| FI01–FI05 | 收起的竹釣竿、木線輪、竹圈抄網、竹魚筌、木浮子三顆 | 21 |
| 全包檢查 | 同場並排、LOD、回匯、QA | 6 |
| **小計** | | **48** |

先交 WL01–05 開一張 PR，再做 FI01–05。

---

## 第二部分｜新的 80 小時

### 為什麼做這些

青溪要讓人覺得「有人住在這裡」：每戶門口、院子、牆邊都有一點生活的東西。地上也要有不同的小石頭、野菇，走起來才不會只看到平平的地面。這些東西種類越多越好，以後整個世界都用得到。

### 要交的東西

**A. 村裡生活小物（48 小時，每件約 4 小時）**

| ID | 東西 | 尺寸上限（w×d×h） | 練什麼 |
|---|---|---|---|
| LV01 | 竹編雞籠（倒扣的圓頂籠） | 0.8 × 0.8 × 0.6 m | 半球形的竹條排列、底部收邊 |
| LV02 | 竹掃帚與木畚箕 | 1.4 × 0.4 × 0.3 m | 細枝束成一把的輪廓、木板拼接 |
| LV03 | 靠牆的竹梯 | 0.5 × 0.1 × 2.4 m | 竹節、橫檔綁繩的重複節奏 |
| LV04 | 竹編吊籃（掛著晾菜乾） | 0.5 × 0.5 × 0.8 m（含掛繩） | 淺籃和吊繩、裡面一點乾菜 |
| LV05 | 醃菜甕三個（大中小，有蓋、壓石） | 0.9 × 0.5 × 0.6 m | **和 BM03 陶罐不同**：寬口、厚蓋、蓋上壓一塊石頭 |
| LV06 | 劈柴木墩與柴刀 | 0.6 × 0.6 × 0.6 m | 年輪切面、刀砍的痕、刀插在木墩上 |
| LV07 | 葫蘆水瓢與木掛勾 | 0.4 × 0.2 × 0.5 m | 葫蘆對半剖的曲面、勾子 |
| LV08 | 斗笠與蓑衣掛在木架上 | 0.8 × 0.4 × 1.6 m | 斗笠的圓錐、蓑衣的一層層草片 |
| LV09 | 竹鳥籠掛在短竿上（空籠） | 0.4 × 0.4 × 1.2 m | 圓柱細竹條、頂部提環 |
| LV10 | 草鞋與木屐各一雙 | 0.4 × 0.3 × 0.1 m | 小物件的比例、編織紋用貼圖表現 |
| LV11 | 磨刀石座（長條石放在木凳上） | 0.8 × 0.3 × 0.5 m | 石頭中間磨凹的形狀、木凳榫接 |
| LV12 | 稻草蛋籃（籃裡墊稻草和幾顆蛋） | 0.35 × 0.35 × 0.25 m | 籃的編織、稻草的亂、蛋的乾淨圓形 |

**B. 地上小石與野菇（21 小時，每件約 3.5 小時）**

| ID | 東西 | 尺寸 | 練什麼 |
|---|---|---|---|
| GC01 | 溪邊圓石散件一組（5 顆不同形） | 每顆 0.1–0.4 m | 被水沖圓的石頭：圓但不完美、底部埋土 |
| GC02 | 山路碎石散件一組（5 顆不同形） | 每顆 0.1–0.3 m | 有稜角的碎石，和 GC01 一眼分得出 |
| GC03 | 半埋在土裡的扁石一組（4 顆） | 每顆 0.3–0.6 m | 石頭和地面接觸的地方：一圈土、草 |
| GC04 | 地上的小野菇一叢（普通、不發光） | 0.3 × 0.3 × 0.15 m | 菇傘和菇柄、大小不一；**和 Codex 的發光蕈不同** |
| GC05 | 長在倒木上的層狀菇 | 0.4 × 0.2 × 0.3 m | 一片片半圓疊上去的層次 |
| GC06 | 小落石堆 | 1.2 × 1 × 0.6 m | 很多石頭堆在一起不穿插、不懸空 |

GC01–GC03 每顆石頭要能**單獨拿出來擺**，不要焊成一塊。

**C. 自己的舊件補 LOD（8 小時）**

LOD0 不動，只補 LOD1／LOD2，做前後對照圖：

| 組 | PR |
|---|---|
| `qingxi-village-signs-v1`（村內告示） | #34 |
| `qingxi-return-c`（回村背籠、分揀桌、座凳、油紙燈） | #35 |
| `qingxi-day12-c`（茶亭、村口石燈、守燈、晾藥架、雜物組） | #60 |

**D. 全包檢查（3 小時）**：LV 十二件放在同一張圖上並排，配人形尺。

| | 時數 |
|---|---:|
| A 村裡生活小物 | 48 |
| B 地上小石與野菇 | 21 |
| C 舊件補 LOD | 8 |
| D 全包檢查 | 3 |
| **小計** | **80** |

### 在世界裡的位置

- LV：A1 青溪村各戶門口、院子、牆邊。
- GC：全區地面（溪邊、山路、古林）。
- 核心組負責擺進世界，你只交模型。**不改主場景、不改區塊 JSON。**

### 風格

- 先看你自己的 `modelling-basics-c`（BM01–BM10）、`qingxi-day34-c`，還有 `qingxi-world-ruins-b`、`harvest-market-b`、`territory-interior-b`。
- 真實比例、柔和色塊、少量筆觸、磨損要有位置（常摸的地方亮、底部髒）。
- 每件灰模和上色各一張，和一件舊道具同光同角度並排；一眼不合就重做。

### 驗收

- 每件 QA errors = 0、FBX 回匯誤差 ≤ 2 cm、原點在底部中心、底部 z = 0。
- 外形和第 3 節列的既有道具不能一樣。
- 逐件標 Exported／Imported／Visually Verified／In-game Verified，沒驗的寫未驗。

### 不要做

- 不做已有的：陶罐 BM03、石凳、座凳、背簍、竹篩、水桶、扁擔、晾藥架 TY08、Dondon 的 `MortarPestle`（石臼）、`DryingRack`（晾架）、`WildShrub`、`MossBoulderSet`、Codex 的發光蕈。
- 不做建築、地標、人物、玩法、字、主場景。

### 時間順序

1. 第一部分 WL01–05（24h）→ 開 PR
2. 第一部分 FI01–05（24h）→ 開 PR
3. LV01–LV06（24h）→ 開 PR
4. LV07–LV12（24h）→ 開 PR
5. GC01–GC06 與舊件補 LOD（32h）→ 開 PR

---

## 附：三視圖提示詞

### 固定段（每條都要原樣接上，不能改）

**Layout 段**（接在每條物件句後面）：

```text
Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
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

**LV01**
```text
Three-view orthographic turnaround sheet of an upturned dome-shaped woven bamboo chicken coop cover resting on packed earth, about 0.8 m wide and 0.6 m tall, made of split bamboo strips and hemp ties, showing a darker worn bottom rim, a few stray feathers, one repaired strip and straw caught in the weave, used in the yards of houses in a lived-in mountain valley village.
```

**LV02**
```text
Three-view orthographic turnaround sheet of a long twig broom bound to a bamboo handle lying beside a shallow wooden dustpan, about 1.4 m long, 0.4 m wide and 0.3 m tall, made of dried brown twigs, bamboo and old cedar boards, showing splayed worn broom tips, hemp binding and a scuffed dustpan lip, used in the yards of houses in a lived-in mountain valley village.
```

**LV03**
```text
Three-view orthographic turnaround sheet of a simple bamboo ladder with lashed rungs, about 0.5 m wide and 2.4 m tall, made of two thick bamboo poles, thinner bamboo rungs and hemp lashings, showing darker hand-worn rungs, uneven bamboo nodes and one replaced rung of lighter colour, used in the yards of houses in a lived-in mountain valley village.
```

**LV04**
```text
Three-view orthographic turnaround sheet of a shallow round woven bamboo basket hanging from three hemp cords, holding a few dried vegetable leaves and chilli-red pods drying in the air, about 0.5 m wide and 0.8 m tall including the cords, made of split bamboo, hemp cord and dried vegetables, showing a sagging rim, frayed cord ends and uneven drying produce, used in the yards of houses in a lived-in mountain valley village.
```

**LV05**
```text
Three-view orthographic turnaround sheet of a group of three wide-mouthed glazed pickling jars of different sizes, each with a heavy clay lid and a smooth river stone pressing on the lid, group about 0.9 m wide, 0.5 m deep and 0.6 m tall, made of dark brown glazed clay, unglazed rims and grey river stones, showing drip marks on the glaze, a chipped lid edge and damp soil around the bases, used in the yards of houses in a lived-in mountain valley village.
```

**LV06**
```text
Three-view orthographic turnaround sheet of a thick tree-stump chopping block with a small chopping knife stuck into its top and a few split firewood pieces at its foot, about 0.6 m wide and 0.6 m tall, made of old pale stump wood with visible growth rings, an iron blade with a wooden handle and split pine, showing many crossing cut marks on the top, bark peeling at the sides and wood chips on the ground, used in the yards of houses in a lived-in mountain valley village.
```

**LV07**
```text
Three-view orthographic turnaround sheet of a dried gourd cut in half lengthways to make a water ladle, hanging on a short wooden peg hook fixed to a small board, about 0.4 m wide and 0.5 m tall, made of tan dried gourd shell and old cedar, showing the darker inner surface of the gourd, a hemp loop through the handle and water stains under the hook, used in the yards of houses in a lived-in mountain valley village.
```

**LV08**
```text
Three-view orthographic turnaround sheet of a conical woven bamboo rain hat and a layered straw rain cape hanging on a simple standing wooden peg rack, about 0.8 m wide, 0.4 m deep and 1.6 m tall, made of split bamboo, dried palm-fibre and straw layers and old cedar, showing overlapping straw layers, a frayed hat rim and a worn peg, used in the yards of houses in a lived-in mountain valley village.
```

**LV09**
```text
Three-view orthographic turnaround sheet of an empty round bamboo birdcage with a domed top and carrying ring, hanging from a short bamboo pole set in a stone base, about 0.4 m wide and 1.2 m tall, made of fine bamboo strips, dark wooden base ring and grey stone, showing the evenly spaced thin bars, a small open door and a little wear on the ring, used in the yards of houses in a lived-in mountain valley village.
```

**LV10**
```text
Three-view orthographic turnaround sheet of a pair of woven straw sandals beside a pair of simple wooden clogs with two teeth under each sole, about 0.4 m wide, 0.3 m deep and 0.1 m tall, made of braided straw, old pale wood and dark cloth straps, showing flattened worn straw, mud on the clog teeth and frayed strap ends, used at the doorsteps of houses in a lived-in mountain valley village.
```

**LV11**
```text
Three-view orthographic turnaround sheet of a long whetstone with a deeply worn concave middle, resting on a low four-legged wooden bench with a small water bowl at one end, about 0.8 m long, 0.3 m wide and 0.5 m tall, made of fine grey sharpening stone, old cedar and clay, showing the smooth hollowed stone surface, wet dark stains on the bench and mortise joints on the legs, used in the yards of houses in a lived-in mountain valley village.
```

**LV12**
```text
Three-view orthographic turnaround sheet of a small round woven basket lined with loose straw holding six pale eggs, about 0.35 m wide and 0.25 m tall, made of split bamboo, golden straw and clean cream-coloured eggshell, showing untidy straw ends sticking out of the rim, a slightly crushed side and a clean smooth egg surface, used in the kitchens and yards of a lived-in mountain valley village.
```

**GC01**
```text
Three-view orthographic turnaround sheet of a set of five separate water-rounded creek pebbles and cobbles of different sizes and shapes laid out apart from each other, each about 0.1 to 0.4 m long, made of smooth warm-grey and blue-grey river stone with pale quartz veins, showing wet darker lower halves, a little silt in the hollows and a thin line of algae, used on the banks of a clear creek in a mountain valley village.
```

**GC02**
```text
Three-view orthographic turnaround sheet of a set of five separate angular broken mountain stones of different sizes laid out apart from each other, each about 0.1 to 0.3 m long, made of sharp-edged warm-grey rock with fresh lighter break faces, showing dust in the creases, small chips and a little lichen on the older faces, used along mountain paths around a valley village.
```

**GC03**
```text
Three-view orthographic turnaround sheet of a set of four separate flat stones half-buried in the ground, each with a ring of packed soil and short grass around its edge, each about 0.3 to 0.6 m wide, made of warm-grey fieldstone and dark earth, showing weathered rounded tops, soil line where the stone meets the ground and small moss patches, used in the ground of a mountain valley village and forest.
```

**GC04**
```text
Three-view orthographic turnaround sheet of a small cluster of ordinary non-glowing wild mushrooms of different heights growing from leaf litter, about 0.3 m wide and 0.15 m tall, made of soft tan and brown caps with pale stems and gills, showing a few broken caps, dirt on the stems and fallen leaves around the base, used on the forest floor near a mountain valley village.
```

**GC05**
```text
Three-view orthographic turnaround sheet of a short section of a mossy fallen log with several layered half-round bracket fungi growing out of its side, about 0.4 m long, 0.2 m deep and 0.3 m tall, made of dark wet bark and pale cream-to-brown shelf fungi with concentric bands, showing the stacked shelf layers, moss on top of the log and crumbling wood at the cut ends, used on the forest floor near a mountain valley village.
```

**GC06**
```text
Three-view orthographic turnaround sheet of a small natural pile of fallen rocks at the foot of a slope, many stones of different sizes resting on each other without floating gaps, about 1.2 m wide, 1 m deep and 0.6 m tall, made of warm-grey angular rock with a few rounded stones, showing soil and gravel filling the gaps, grass growing between the lower stones and fresh light-coloured breaks on the top stones, used along mountain paths around a valley village.
```
