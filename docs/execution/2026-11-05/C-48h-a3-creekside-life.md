# C｜48 小時：A3 西溪洗衣與溪岸生活小物

> 交給 Eli-0731。這是**新模型製作包**，取代 2026-11-05 先前誤寄的 24 小時「收尾包」。#64/#67/#69 的審查另行處理，舊 PR 結案後開始。只排基礎練習難度的生活道具，不派地標、建築或人物。

## 0. 先讀

`docs/execution/2026-11-03/C-28h-modelling-basics.md` 第 0–2 節；`docs/execution/blocks/A2-A3-block-plan.md` 的 A3；`docs/execution/2026-11-03/00-overview.md` 第 2、3 節；`docs/art/modeling-style-spec-v1.md` 第 2、6、11 節；`docs/standards/quality-tiers-v1.md` 第 4 節；`docs/execution/art-style-guide-v1.md` 第 5 節。

## 1. 一句話任務

做一組能讓 A3 西溪洗衣埠頭與釣魚台周邊像有人日常使用的十件小道具，逐件練輪廓、材料和乾淨的手繪貼圖。

## 2. 玩家會經歷什麼

玩家從水磨坊走到洗衣石階，看到洗衣板、木槌與收起的布；沿溪走到釣魚台岸邊，看到靠在一旁的竹竿、抄網和魚筌。這些是靜態環境敘事，不開啟釣魚或洗衣玩法。

## 3. 在世界裡的位置

| 格位 | 區塊／空間 | 尺寸上限與界線 |
|---|---|---|
| `A3_WashProps` | A3 西溪 `A3_WashSteps`（WM05）側邊 | 新規格位，中心世界座標 (-95.2,-14)，容器 1.5×1×0.8 m；五件可分開擺，不改 WM05 石階 |
| `A3_FishBankProps` | A3 西溪 `a3-fish` 岸邊 | 新規格位，中心 (-117,-21)，容器 2×1.5×1.8 m；五件可分開擺，不佔 `A3_FishPlatform_Bank` 的走道 |

兩個格位在本包工作樹的 `tools/qingxi-terrain/blocks/A3.json` 補齊；核心組併入前請核對擺位。模型本身以底部中心為原點、底部 z=0，不把多件焊成不可拆的一塊。

## 4. 和世界觀的關係

只表示村人平常來溪邊洗衣、整理漁具；不設人物身份、台詞、魚種或新故事。所有道具無刻字、記號與標牌。

## 5. 要交的東西

| ID | 新模型與練習重點 | 尺寸上限 | 時數 |
|---|---|---|---:|
| WL01 | 老木洗衣板，練平整面和有節奏的橫肋 | 0.7×0.4×0.12 m | 4 |
| WL02 | 洗衣木槌，練握柄過渡與端面木紋 | 0.45×0.15×0.12 m | 3 |
| WL03 | 捲起的粗布，練布的厚度和不規則摺 | 0.65×0.3×0.25 m | 5 |
| WL04 | 折好的濕布兩疊，練大塊布色與濕邊 | 0.6×0.5×0.25 m | 5 |
| WL05 | 石製皂灰小盤與灰餅，練淺凹槽與磨損 | 0.38×0.28×0.12 m | 4 |
| FI01 | 細竹釣竿（收起狀態），練竹節和繫繩 | 長 2.2 m，收納可斜靠 | 4 |
| FI02 | 木線輪與麻線，練圓形中心和繞線 | Ø0.28×0.12 m | 4 |
| FI03 | 竹圈抄網，練圓環、網結和輪廓 | 1.3×0.45×0.06 m | 5 |
| FI04 | 長錐形竹魚筌，練中空與竹條編織 | 0.9×0.38×0.38 m | 5 |
| FI05 | 三顆不同大小的木浮子與繩，練簡單形狀變體 | 0.5×0.3×0.2 m | 3 |
| 全包檢查 | 同場並排、LOD、回匯、QA、尺寸與交件整理 | — | 6 |
| **合計** | | | **48** |

每件與 FI05 的每個不同輪廓先生成至少四張三視圖、檢視並選一張再做灰模，保存候選與取捨。交 `.blend`、可重跑腳本、FBX／GLB、貼圖、`model_info.json`、四視圖與人形尺、線框、LOD0/1 關 `Detail_*` 對照。不要只靠旋轉、縮放、換色充件數。

## 6. 玩法與伺服器

沒有新玩法、伺服器動作或存檔。釣竿與網是收起的場景小物，不做可操作物、骨架動畫或魚類。正式場景擺放由核心組做。

## 7. 風格

先看 `qingxi-world-ruins-b`、`qingxi-day34-c`、`harvest-market-b`、`territory-interior-b`；WL01/02 與舊木器、WL03/04 與既有布件、WL05 與 BM05/06 石件、FI01–05 與水工竹繩件同場。灰模與材質各做一次同光同角度並排，含 1.75 m 尺；指出三個共同點。真實比例、柔和色塊、少量筆觸、磨損有位置；一眼不合即 FAIL。

## 8. 驗收

第一批 WL01–05 五件可獨立驗收。每件 QA errors=0、FBX 回匯尺寸誤差≤2 cm，LOD0/1/2 面數寫**實際值**，`model_info.json` 加 `minTier`、`detailObjects`，不減 LOD0 保輪廓。逐件標 Exported、Imported、Visually Verified、In-game Verified；正式場景與手機未驗就寫未驗。布與網在 Unity 獨立匯入看雙面材質；不用 CI 代替人工看圖。

## 9. 不要做的事

不做 WM05 洗衣石階、WM06 釣魚台、B 的水磨坊與水工、A 的溪石踏石；不做已交的桶、背簍、竹篩、陶罐、石凳；不做人物、魚、玩法、字、主場景或 Runtime。FI04 是細長魚筌，不能變成舊背簍。

## 10. 時間與分量

48 小時估計。先 WL01–05（21h）和一輪對照/回匯（3h），獨立開第一張 PR；後 FI01–05（21h）和最後檢查（3h）。同時只開一張待審 PR；前一張結案再開下一張。實際工時照實寫。所有 commit 只用 `z1nnz <202040543+z1nnz@users.noreply.github.com>`，不加 AI 署名。

## 11. 已填好的三視圖提示詞

下列每條均附原樣的固定 5.2 和 5.3，不能自行改固定段；四張候選、選圖理由存 `art/references/<ID>/prompt.txt`。

### WL01

Positive prompt:

```text
Three-view orthographic turnaround sheet of an old ribbed wooden washing board with a broad smooth rubbing face, about 0.7 m long, 0.4 m wide and 0.12 m thick, made of old cedar with raised transverse ribs, showing smooth hand-worn ribs, dark damp lower edge and one repaired slat, used in the A3 west-creek washing steps and fishing bank of a lived-in mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### WL02

Positive prompt:

```text
Three-view orthographic turnaround sheet of a short laundry beating paddle with a shaped handle and thick rounded head, about 0.45 m long, 0.15 m wide and 0.12 m thick, made of old brown cedar, showing rounded striking edge, hand-polished grip and fine end-grain checks, used in the A3 west-creek washing steps and fishing bank of a lived-in mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### WL03

Positive prompt:

```text
Three-view orthographic turnaround sheet of a rolled piece of coarse undyed linen tied loosely with hemp cord, about 0.65 m long, 0.3 m wide and 0.25 m tall, made of coarse natural linen and hemp cord, showing irregular thick folds, darker damp corner and slightly frayed edge, used in the A3 west-creek washing steps and fishing bank of a lived-in mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### WL04

Positive prompt:

```text
Three-view orthographic turnaround sheet of two separate folded stacks of washed linen with uneven corners, about 0.6 m wide, 0.5 m deep and 0.25 m tall, made of faded natural linen with one muted blue cloth, showing damp darkened edges, hand-folded uneven layers and one patched corner, used in the A3 west-creek washing steps and fishing bank of a lived-in mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### WL05

Positive prompt:

```text
Three-view orthographic turnaround sheet of a shallow stone dish holding a plain grey laundry-ash cake, about 0.38 m long, 0.28 m wide and 0.12 m tall, made of warm-grey carved fieldstone and matte grey ash, showing worn shallow rim, wet ring and traces of ash in the recess, used in the A3 west-creek washing steps and fishing bank of a lived-in mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### FI01

Positive prompt:

```text
Three-view orthographic turnaround sheet of a slender jointed bamboo fishing pole in a stored, unbaited state, about 2.2 m long, made of old split bamboo and hemp line, showing grip polished by hands, bent tip and repaired line binding, used in the A3 west-creek washing steps and fishing bank of a lived-in mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### FI02

Positive prompt:

```text
Three-view orthographic turnaround sheet of a small wooden line spool with neatly wound hemp fishing line, about 0.28 m wide and 0.12 m deep, made of aged cedar and hemp line, showing worn finger notches, uneven line coils and a replaced wooden peg, used in the A3 west-creek washing steps and fishing bank of a lived-in mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### FI03

Positive prompt:

```text
Three-view orthographic turnaround sheet of a bamboo-ring landing net with a short handle and visible open mesh, about 1.3 m long and 0.45 m wide, made of split bamboo, knotted hemp mesh and dark cord, showing a repaired mesh knot, worn hand grip and damp lower threads, used in the A3 west-creek washing steps and fishing bank of a lived-in mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### FI04

Positive prompt:

```text
Three-view orthographic turnaround sheet of a long tapered hollow bamboo fish trap with a funnel opening, visibly unlike a carrying basket, about 0.9 m long and 0.38 m wide, made of split bamboo and hemp lashings, showing one patched wicker rib, dark wet lower side and frayed binding, used in the A3 west-creek washing steps and fishing bank of a lived-in mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### FI05

Positive prompt:

```text
Three-view orthographic turnaround sheet of three different small wooden fishing floats joined by loose hemp line, about group about 0.5 m wide, 0.3 m deep and 0.2 m tall, made of aged lightweight timber and hemp line, showing water stains, one chipped float and an uneven hand-tied knot, used in the A3 west-creek washing steps and fishing bank of a lived-in mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```
