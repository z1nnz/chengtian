# B｜48 小時：東坡茶田與稻田大水車

> 交給 joshsu54。這是**新模型製作包**，取代 2026-11-05 先前誤寄的 24 小時「收尾包」。#70–#73 的審查另行處理，舊 PR 結案後開始。TE01–05 與 RI03 從 Codex D2 轉交 B，Codex 不再製作這六項。

## 0. 先讀

`docs/execution/codex-v3/D2-valley-and-home.md` 第 0、3、4、7 節；`docs/execution/2026-11-03/00-overview.md` 第 2、3 節；`docs/art/modeling-style-spec-v1.md` 第 2、6、11 節；`docs/standards/quality-tiers-v1.md` 第 4 節；`docs/execution/art-style-guide-v1.md` 第 5 節；`docs/standards/pr-review.md`。

## 1. 一句話任務

做可拼成 40×40 m 山坡的東坡茶田套件，以及第 8 天稻田會看見的 9 m 灌溉大水車。

## 2. 玩家會經歷什麼

玩家第 5 天沿東坡茶田上山，看到能一階階走上去的茶田、成排修剪的茶樹與觀景亭；第 8 天水回到稻田，遠處有比西溪磨坊水車大一倍的灌溉水車。這包只做美術和可走結構，不做採茶或灌溉玩法。

## 3. 在世界裡的位置

| 格位 | 區塊／空間 | 尺寸上限與接口 |
|---|---|---|
| `A4_TeaTerraces` | A4 東坡茶田，大世界 | TE01 每段 8×4 m、階高 0.8–1.2 m；1 m 格線；40×40 m 組裝樣張 |
| `A4_ViewPavilion` | A4 東坡高處，大世界 | TE05 5×5×5 m，東面開闊 |
| `A6_GreatWheel` | A6 稻田，大世界 | RI03 輪直徑 9 m、寬 2 m；轉軸原點；獨立石座與高木槽 |

A4/A6 block JSON 尚未由核心組落位；尺寸與接口照原 D2 先固定，**不要改主場景或自己宣稱已正式落位**。交 `farm-assembly.json` 提供核心組接入。RI03 接水口留給核心組的水路狀態；不得改 B 先前 WM02 小水車。

## 4. 和世界觀的關係

茶田是通向山城的美景，稻田是水路修好後的可見成果。只用場景形狀表達有人長年照料，不定人物名字、不寫碑文或攤牌。

## 5. 要交的東西

| ID | 新模型 | 交付與接口 | 時數 |
|---|---|---|---:|
| TE01 | 梯田 6 件：直 2、內彎、外彎、收尾、斷口 | 乾砌石擋土牆、土面、排水缺口；1 m 格線、接口≤2 mm、可走碰撞 | 13 |
| TE02 | 3 種修剪茶樹 | 高 0.8–1.1 m、寬 1.2 m；有木枝、嫩芽、葉面片；頂點色風權重 | 7 |
| TE03 | 石階、土徑、踏腳石 | 寬 1.2 m，接 TE01；不重做 A 的碎石小徑 | 4 |
| TE04 | 採茶竹簍與晾茶竹匾 | 0.5–1.2 m；與 `harvest-market-b` 背簍、竹篩外形不同；可作 `Detail_*` | 4 |
| TE05 | 觀景亭 | 5×5×5 m，四柱、青瓦、石基、可走；與 RK03 茶亭及 WM09 竹亭輪廓不同 | 8 |
| RI03 | 稻田大水車 | 直徑 9 m、寬 2 m；竹筒翻水、木槽與石座獨立，輪原點在軸心且軸正圓 | 9 |
| 組裝與回匯 | 40×40 m 茶田樣張及 RI03 對 WM02 同場；QA、FBX 回匯、材質修正 | 3 |
| **合計** | | | **48** |

每個新模型及不同輪廓變體先生成、檢視至少四張三視圖，選圖後才灰模。保留候選與理由；灰模和材質階段均同場並排。交 `.blend`、可重跑腳本、FBX／GLB、貼圖、`model_info.json`、四視圖、線框、LOD0/1 對照及組裝預覽。貼圖與 LOD 按畫質分級，LOD0 不為數字降品質。

## 6. 玩法與伺服器

本包沒有新採茶、種田或通水動作。RI03 僅拆出旋轉輪與固定支架，真正的水流、旋轉控制和伺服器由核心組接入；展示中的假水不能標成正式玩法。

## 7. 風格

先看 `qingxi-world-ruins-b`、`qingxi-day34-c`、`harvest-market-b`、`territory-interior-b`；TE01 與現有水工切石、TE02 與 BM08 野灌木、TE04 與收成道具、TE05 與 RK03、RI03 與 WM02 同場比。真實比例、暖灰石、老褐木、青灰瓦、暖黃綠受光與青綠陰影；灰模和材質各一張同光同角度，含 1.75 m 尺。三個共同點寫進 README；一眼不合即 FAIL。

## 8. 驗收

第一批 TE01+TE02+TE03 能拼出可走的茶田，獨立驗收。逐件 QA errors=0、FBX 回匯誤差≤2 cm、原點與底部正確；`model_info.json` 寫實際 LOD 三角面、`minTier`、`detailObjects`；組裝檢查 TE01 接縫≤2 mm，RI03 軸心與固定件拆分正確。標清 Exported/Imported/Visually Verified/In-game Verified；未做手機實測就寫未驗，不承諾 FPS。

## 9. 不要做的事

不做 D2 的屋內外殼、水井、茶棚、A5 渡口、D4/D5 古林、A6 RI01/RI02/RI04（Codex 保留）；不重做 WM02 西溪小水車、CR09 小閘、既有竹篩背簍；不做人物、文字、水面著色、玩法或主場景。

## 10. 時間與分量

48 小時估計。先 TE01–03（24h，可單獨 PR），再 TE04–05（12h），最後 RI03 與組裝（12h）。每位同時只開一張待審 PR；前一張結案再開下一張。實際工時照實寫；commit 一律用你自己的 GitHub 帳號，不用 z1nnz，也不掛 Claude Code 或其他 AI 的名字（2026-11-09 更正）。

## 11. 已填好的三視圖提示詞

下列正面提示各自接完整固定 5.2，負面提示各自接完整 5.3；每種不同輪廓另出四張。提示詞、候選與理由存 `art/references/<ID>/prompt.txt`。

### TE01-STRAIGHT-A

Positive prompt:

```text
Three-view orthographic turnaround sheet of a straight modular dry-stone tea-terrace wall with level soil step and small runoff gap, about 8 m long, 4 m deep and 1 m high, made of fitted warm-grey fieldstone, packed warm-brown soil, old cedar and sparse yellow-green grass where appropriate, showing hand-worn edges, patched stones, earth in joints, small moss patches only in shaded seams, used in the east-slope tea terraces above a warm mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TE01-STRAIGHT-B

Positive prompt:

```text
Three-view orthographic turnaround sheet of a straight modular dry-stone tea-terrace wall with offset stone courses and a repaired corner, about 8 m long, 4 m deep and 1 m high, made of fitted warm-grey fieldstone, packed warm-brown soil, old cedar and sparse yellow-green grass where appropriate, showing hand-worn edges, patched stones, earth in joints, small moss patches only in shaded seams, used in the east-slope tea terraces above a warm mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TE01-INNER-BEND

Positive prompt:

```text
Three-view orthographic turnaround sheet of an inward-bending modular tea-terrace wall and level soil step with one-metre-grid connectors, about 8 m long, 4 m deep and 1 m high, made of fitted warm-grey fieldstone, packed warm-brown soil, old cedar and sparse yellow-green grass where appropriate, showing hand-worn edges, patched stones, earth in joints, small moss patches only in shaded seams, used in the east-slope tea terraces above a warm mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TE01-OUTER-BEND

Positive prompt:

```text
Three-view orthographic turnaround sheet of an outward-bending modular tea-terrace wall and level soil step with one-metre-grid connectors, about 8 m long, 4 m deep and 1 m high, made of fitted warm-grey fieldstone, packed warm-brown soil, old cedar and sparse yellow-green grass where appropriate, showing hand-worn edges, patched stones, earth in joints, small moss patches only in shaded seams, used in the east-slope tea terraces above a warm mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TE01-END

Positive prompt:

```text
Three-view orthographic turnaround sheet of a tapered end piece closing a dry-stone tea-terrace row, about 8 m long, 4 m deep and 1 m high, made of fitted warm-grey fieldstone, packed warm-brown soil, old cedar and sparse yellow-green grass where appropriate, showing hand-worn edges, patched stones, earth in joints, small moss patches only in shaded seams, used in the east-slope tea terraces above a warm mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TE01-BROKEN

Positive prompt:

```text
Three-view orthographic turnaround sheet of a safely walkable dry-stone tea-terrace segment with one old broken edge and repaired soil bank, about 8 m long, 4 m deep and 1 m high, made of fitted warm-grey fieldstone, packed warm-brown soil, old cedar and sparse yellow-green grass where appropriate, showing hand-worn edges, patched stones, earth in joints, small moss patches only in shaded seams, used in the east-slope tea terraces above a warm mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TE02-ROUND

Positive prompt:

```text
Three-view orthographic turnaround sheet of a rounded flat-topped cultivated tea bush with dense small leaves and hand-plucked yellow-green tips, about 1.2 m wide and 0.9 m tall, made of woody tea stems and clusters of warm yellow-green leaves with cool teal undersides, showing a few older dark leaves, careful plucked tips and soil at the base, used in the east-slope tea terraces above a warm mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TE02-WIDE

Positive prompt:

```text
Three-view orthographic turnaround sheet of a wide asymmetrical cultivated tea bush with low woody branches and neatly trimmed young tips, about 1.2 m wide and 0.8 m tall, made of woody tea stems and clusters of warm yellow-green leaves with cool teal undersides, showing a few older dark leaves, careful plucked tips and soil at the base, used in the east-slope tea terraces above a warm mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TE02-TALL

Positive prompt:

```text
Three-view orthographic turnaround sheet of a slightly taller cultivated tea bush with irregular hand-pruned dome and sparse lower branches, about 1.2 m wide and 1.1 m tall, made of woody tea stems and clusters of warm yellow-green leaves with cool teal undersides, showing a few older dark leaves, careful plucked tips and soil at the base, used in the east-slope tea terraces above a warm mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TE03-STAIR

Positive prompt:

```text
Three-view orthographic turnaround sheet of a narrow fitted-stone stair segment between two tea terraces, about 1.2 m wide and 2.4 m long, made of warm-grey fieldstone and compacted warm-brown earth, showing worn foot surfaces, soil in joints and a few grass stems, used in the east-slope tea terraces above a warm mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TE03-PATH

Positive prompt:

```text
Three-view orthographic turnaround sheet of a compacted-earth terrace path segment with low stone edging, about 1.2 m wide and 3 m long, made of warm-grey fieldstone and compacted warm-brown earth, showing worn foot surfaces, soil in joints and a few grass stems, used in the east-slope tea terraces above a warm mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TE03-STEPPING

Positive prompt:

```text
Three-view orthographic turnaround sheet of a set of three distinct flat stepping stones for one terrace crossing, about 1.2 m wide and 1.8 m long, made of warm-grey fieldstone and compacted warm-brown earth, showing worn foot surfaces, soil in joints and a few grass stems, used in the east-slope tea terraces above a warm mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TE04-BASKET

Positive prompt:

```text
Three-view orthographic turnaround sheet of a low tea-picking bamboo basket with a wide open mouth, unlike a tall back-carried harvest basket, about 0.5 m wide and 0.4 m tall, made of split bamboo and hemp binding, showing softened rim, repaired weave and a few loose tea leaves, used in the east-slope tea terraces above a warm mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TE04-TRAY

Positive prompt:

```text
Three-view orthographic turnaround sheet of a shallow broad woven bamboo tea-drying tray with separated tea leaves, about 1.2 m wide and 0.12 m tall, made of split bamboo and narrow cedar rim, showing darkened binding, repaired weave and a little edge wear, used in the east-slope tea terraces above a warm mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TE05-PAVILION

Positive prompt:

```text
Architectural concept of an open four-post hilltop viewing pavilion above tea terraces for villagers and travellers to rest, footprint about 5 m wide and 5 m deep, ridge 5 m high, timber post-and-beam frame with gently upturned eave corners, blue-grey clay tile roof with a moss-covered ridge, open sides with low railing and built-in bench, worn warm-grey stone plinth with three steps, details: an entirely blank timber panel and a clay water jar, weathering: sun-faded timber, a repaired corner of roof tile and moss in shaded footing joints. Layout: one three-quarter view from slightly above at eye height of a person, plus front, side and back orthographic views on the same sheet at the same scale, plain light warm-grey background, even soft lighting, building only (no landscape around it except a small ground patch).
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### RI03-GREAT-WHEEL

Positive prompt:

```text
Three-view orthographic turnaround sheet of a great irrigation water wheel with bamboo tubes lashed around the rim to lift water to a raised timber trough, rotating wheel separate from fixed stone supports, about 9 m in diameter and 2 m wide, made of old dark timber, split bamboo, hemp rope and warm-grey stone, showing wet lower spokes, algae near the waterline, repaired lashings and worn wooden trough edges, used in rice fields in the southeast of a mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```
