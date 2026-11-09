# A｜48 小時：山城街屋、太玄分院模組與索橋

> 交給 Johnnnny0823。這是**新模型製作包**，取代 2026-11-05 先前誤寄的 24 小時「收尾包」。#66、#68 的審查另行處理；舊 PR 結案後才開始這包。MC01、MC02、TX04 從 Codex D3 明確轉交 A，Codex 不再製作這三項。

## 0. 先讀

`docs/execution/codex-v3/D3-mountain-city.md` 第 0、4–8 節；`docs/execution/2026-11-03/00-overview.md` 第 2、3 節；`docs/art/modeling-style-spec-v1.md` 第 2、6、11 節；`docs/standards/quality-tiers-v1.md` 第 4 節；`docs/execution/art-style-guide-v1.md` 第 5 節；`docs/standards/pr-review.md`。

## 1. 一句話任務

做一套沿山壁往上的山城街屋、一套可換裝的太玄分院外觀，以及接既有棧道的兩種索橋，讓山城能從山門一路拼到院門。

## 2. 玩家會經歷什麼

玩家第 5 天由既有山門走上石階，看到街屋沿崖層疊，B 已做的攤位前有 3 m 活動空間；再走過索橋抵達分院門前。第 10 天回來時仍是同一座城，只由核心組安排內容。這包只交模型與可走碰撞，不做劇情或測資玩法。

## 3. 在世界裡的位置

| 格位／模組 | 空間 | 尺寸上限與接口 |
|---|---|---|
| `MC_StreetKit`（MC01） | B 山城街巷；詳細擺位由核心組的 B 區地圖決定 | 4 m 格線；石基 4×4×2 m、店住層 4×4×3 m、屋頂 4×4 m、懸挑平台 4×3 m；接縫≤2 mm；前廊留 3 m |
| `TX_AcademyKit`（TX04） | B 山城太玄分院 | 院門 6×3×6 m；牆 4 m 一段；正堂 14×10×8 m；廂房 8×5×5 m；院鋪地 4 m 格線 |
| `MC_RopeBridge`（MC02） | B 山城崖間，接 `CliffBoardwalk` | 長 24 m／12 m，寬 1.6 m，下垂 1.5 m；兩端同高；原點在一端中心 |

**定位界線**：原 D3 尚無 B 區正式 block JSON；上述是已定的模型尺寸與模組接口，**不可自己改主場景或宣稱已正式落位**。交 `b-street-assembly.json` 供核心組接入；若核心組在開工前定出 B 區格位，照實際格位核對再建模。

## 4. 和世界觀的關係

山城要莊嚴、高聳、讓玩家嚮往，沿用青溪的木石尺度與屋頂語言；分院模組只做太玄版的材質接口，不做十四宗徽記和未定人物。任何匾、布幌都空白，文字由 UI 疊上。

## 5. 要交的東西

| ID | 新模型 | 交付與技術接口 | 時數 |
|---|---|---|---:|
| MC01 | 街屋模組：石基 4、店面 3、住家 3、屋頂 4、懸挑平台 2、小件 6 | 同 4 m 格線、共用 2048 Trim Sheet；三棟不同組裝示範；走道碰撞；LOD0/1/2；實際面數與 `minTier` | 24 |
| TX04 | 分院：院門、直／角／門邊牆、正堂、廂房、院鋪地與石階 | `Socket_Plaque`、`Socket_Emblem` 空插槽；`_Accent` 可換色，朱漆≤10%；只有外觀，LOD0/1/2 | 14 |
| MC02 | 24 m 和 12 m 索橋 | 石橋頭、鐵鏈、木板；可走平滑碰撞；LOD0/1/2；兩端高度與 `CliffBoardwalk` 對齊 | 6 |
| 組裝與回匯 | 街屋三棟、分院、兩橋同場預覽；Blender/Unity 隔離匯入與缺陷修正 | 4 |
| **合計** | | | **48** |

每個**獨立新模型／變體**先生成至少四張三視圖（建築加 3/4）、檢視並記錄選圖理由，才做灰模。模組件可共用風格圖，但不同輪廓的模組各有自己的三視圖。建模順序、交件路徑和命名照 D3、`00-README-rules.md`。交 `.blend`、可重跑腳本、FBX／GLB、貼圖、`model_info.json`、四視圖、線框、LOD0/1 對照。

## 6. 玩法與伺服器

本包無新玩法、伺服器動作或存檔。橋可走只代表有連續碰撞；正式場景的通行與內容由核心組接入。展示錄影需標明是模型組裝預覽。

## 7. 風格

先看 `art/previews/qingxi-world-ruins-b`、`qingxi-day34-c`、`harvest-market-b`、`territory-interior-b`，再看山城既有 `SectGate`、`MountainStoneStairs`、`CliffBoardwalk`、`H01`。灰模和材質各做同場同光同角度並排，含 1.75 m 人形尺；指出三個共同點。灰白花崗石、深木、黛瓦、少量銅與朱漆；色值依 D3 第 0 節。看起來不像同一世界就是 FAIL。

## 8. 驗收

第一批 MC01 的三棟組裝可獨立驗收。每件 `model_info.json` 記真實尺寸、LOD 實際三角面、`minTier`、`detailObjects`、碰撞和材質；Blender QA errors=0，FBX 回匯誤差≤2 cm；MC01 接縫≤2 mm；MC02 兩端與既有棧道同高且碰撞可走；TX04 空插槽可用。預覽、匯入、人工看過、正式遊戲實測四種狀態分開寫。手機未實測不承諾 FPS。

## 9. 不要做的事

不做 TX01 飛升榜、TX02 鐘、TX03 塔（Codex 保留）；不重做 `SectGate`、`MountainStoneStairs`、`CliffBoardwalk`、`LayeredCliff`；不做 B 的 CR10–12 攤位；不做人、字、徽記、內部、測資玩法。不要為了面數削弱 LOD0。

## 10. 時間與分量

48 小時估計。先 MC01（24h，可單獨開 PR），再 TX04（14h），最後 MC02 與組裝（10h）。每位同時只開一張待審 PR；前一張收尾後再開下一張。記**實際工時**，不知道就寫未記錄。commit 一律用你自己的 GitHub 帳號，不用 z1nnz，也不掛 Claude Code 或其他 AI 的名字（2026-11-09 更正）。

## 11. 已填好的三視圖提示詞

下列每一條的正面提示都已接原樣的固定風格段，負面提示也已填好；同類模組的各個不同輪廓需替換物件描述另出四張。提示詞與四張候選、選圖理由存 `art/references/<ID>/prompt.txt`。

### MC01-SB01

Positive prompt:

```text
Three-view orthographic turnaround sheet of a straight modular cut-stone foundation bay with one broad flat wall face, about 4 m wide, 4 m deep and 2 m tall, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-SB02

Positive prompt:

```text
Three-view orthographic turnaround sheet of a straight modular cut-stone foundation bay with staggered block joints and a shallow drainage notch, about 4 m wide, 4 m deep and 2 m tall, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-SB03

Positive prompt:

```text
Three-view orthographic turnaround sheet of a ninety-degree corner foundation bay that turns a cliff-hugging street, about 4 m wide, 4 m deep and 2 m tall, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-SB04

Positive prompt:

```text
Three-view orthographic turnaround sheet of a foundation stair bay with safe walkable stone treads, about 4 m wide, 4 m deep and 2 m tall, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-SF01

Positive prompt:

```text
Three-view orthographic turnaround sheet of an open timber shopfront bay with three-metre projecting front veranda and wide entrance, about 4 m wide, 4 m deep and 3 m tall, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-SF02

Positive prompt:

```text
Three-view orthographic turnaround sheet of an open timber shopfront bay with side lattice and a three-metre projecting front veranda, about 4 m wide, 4 m deep and 3 m tall, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-SF03

Positive prompt:

```text
Three-view orthographic turnaround sheet of a corner shopfront bay with two open faces and a three-metre projecting front veranda, about 4 m wide, 4 m deep and 3 m tall, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-HM01

Positive prompt:

```text
Three-view orthographic turnaround sheet of a plaster-walled upper home bay with two narrow paper-lattice windows, about 4 m wide, 4 m deep and 3 m tall, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-HM02

Positive prompt:

```text
Three-view orthographic turnaround sheet of a plaster-walled upper home bay with one narrow recessed window and exposed timber braces, about 4 m wide, 4 m deep and 3 m tall, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-HM03

Positive prompt:

```text
Three-view orthographic turnaround sheet of a corner upper home bay with one small window on each visible side, about 4 m wide, 4 m deep and 3 m tall, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-RF01

Positive prompt:

```text
Three-view orthographic turnaround sheet of a modular blue-grey tiled hip-and-gable roof bay, about 4 m wide and 4 m deep, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-RF02

Positive prompt:

```text
Three-view orthographic turnaround sheet of a modular blue-grey tiled flush-gable roof bay, about 4 m wide and 4 m deep, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-RF03

Positive prompt:

```text
Three-view orthographic turnaround sheet of a modular blue-grey tiled roof-corner end with gently lifted eave, about 4 m wide and 4 m deep, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-RF04

Positive prompt:

```text
Three-view orthographic turnaround sheet of a modular roof junction bay for a tiered cliff street with visibly fitted ridge tiles, about 4 m wide and 4 m deep, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-CP01

Positive prompt:

```text
Three-view orthographic turnaround sheet of a timber cantilever platform with exposed diagonal braces, stone anchors and a safe railing, about 4 m wide and 3 m deep, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-CP02

Positive prompt:

```text
Three-view orthographic turnaround sheet of a corner timber cantilever platform with asymmetrical diagonal braces and a safe railing, about 4 m wide and 3 m deep, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-DT01

Positive prompt:

```text
Three-view orthographic turnaround sheet of a stone-base bronze-frame street lantern with a blank paper panel, about 0.6 m wide and 2.5 m tall, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-DT02

Positive prompt:

```text
Three-view orthographic turnaround sheet of a blank cloth shop pennant on a timber arm, about 1.0 m wide and 1.8 m tall, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-DT03

Positive prompt:

```text
Three-view orthographic turnaround sheet of a small bronze-frame hanging lantern without writing, about 0.4 m wide and 0.7 m tall, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-DT04

Positive prompt:

```text
Three-view orthographic turnaround sheet of a worn bamboo drying pole on two timber brackets, about 2.5 m wide and 1.3 m tall, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-DT05

Positive prompt:

```text
Three-view orthographic turnaround sheet of a narrow stone step-edge cap with rounded walking wear, about 4 m wide and 0.2 m tall, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC01-DT06

Positive prompt:

```text
Three-view orthographic turnaround sheet of a timber and bronze veranda corner brace with visible joinery, about 0.7 m wide and 0.9 m tall, made of warm-grey granite, aged dark-brown cedar, blue-grey clay tiles where present, dark bronze joints, showing hand-worn walking edges, rain streaks, repaired timber joints, moss only in shaded stone seams, used in a steep mountain city street in an Eastern xianxia valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TX04-GATE

Positive prompt:

```text
Three-view orthographic turnaround sheet of a six-metre academy gatehouse with an empty plaque socket and red-lacquer doors, about 6 m wide, 3 m deep and 6 m tall, made of pale warm-grey stone, aged dark cedar, blue-grey clay tiles and restrained dark red lacquer, showing rain streaks, hand-worn steps, repaired eave tiles and a little moss on the north side, used in the exterior of a solemn academy courtyard in a mountain city. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TX04-WALL-ST

Positive prompt:

```text
Three-view orthographic turnaround sheet of a straight academy courtyard wall segment with pale plaster above cut-stone footing and tiled coping, about 4 m long and 2.5 m tall, made of pale warm-grey stone, aged dark cedar, blue-grey clay tiles and restrained dark red lacquer, showing rain streaks, hand-worn steps, repaired eave tiles and a little moss on the north side, used in the exterior of a solemn academy courtyard in a mountain city. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TX04-WALL-CO

Positive prompt:

```text
Three-view orthographic turnaround sheet of a ninety-degree corner academy wall segment with continuous tiled coping, about 4 m by 4 m and 2.5 m tall, made of pale warm-grey stone, aged dark cedar, blue-grey clay tiles and restrained dark red lacquer, showing rain streaks, hand-worn steps, repaired eave tiles and a little moss on the north side, used in the exterior of a solemn academy courtyard in a mountain city. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TX04-WALL-DO

Positive prompt:

```text
Three-view orthographic turnaround sheet of a doorway-edge academy wall segment with fitted timber jamb, about 4 m long and 2.5 m tall, made of pale warm-grey stone, aged dark cedar, blue-grey clay tiles and restrained dark red lacquer, showing rain streaks, hand-worn steps, repaired eave tiles and a little moss on the north side, used in the exterior of a solemn academy courtyard in a mountain city. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TX04-HALL

Positive prompt:

```text
Three-view orthographic turnaround sheet of a solemn academy main hall exterior with deep roof eaves and blank entrance panel, about 14 m wide, 10 m deep and 8 m tall, made of pale warm-grey stone, aged dark cedar, blue-grey clay tiles and restrained dark red lacquer, showing rain streaks, hand-worn steps, repaired eave tiles and a little moss on the north side, used in the exterior of a solemn academy courtyard in a mountain city. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TX04-SIDE

Positive prompt:

```text
Three-view orthographic turnaround sheet of a modest academy side wing exterior with narrow paper windows, about 8 m wide, 5 m deep and 5 m tall, made of pale warm-grey stone, aged dark cedar, blue-grey clay tiles and restrained dark red lacquer, showing rain streaks, hand-worn steps, repaired eave tiles and a little moss on the north side, used in the exterior of a solemn academy courtyard in a mountain city. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TX04-PAVE

Positive prompt:

```text
Three-view orthographic turnaround sheet of a modular four-metre academy courtyard paving bay of fitted warm-grey slabs, about 4 m by 4 m, made of pale warm-grey stone, aged dark cedar, blue-grey clay tiles and restrained dark red lacquer, showing rain streaks, hand-worn steps, repaired eave tiles and a little moss on the north side, used in the exterior of a solemn academy courtyard in a mountain city. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### TX04-STEPS

Positive prompt:

```text
Three-view orthographic turnaround sheet of a modular academy stone stair with worn shallow treads, about 4 m wide and 2 m deep, made of pale warm-grey stone, aged dark cedar, blue-grey clay tiles and restrained dark red lacquer, showing rain streaks, hand-worn steps, repaired eave tiles and a little moss on the north side, used in the exterior of a solemn academy courtyard in a mountain city. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC02-24M

Positive prompt:

```text
Three-view and three-quarter concept of a walkable suspension bridge connecting two cliff boardwalk landings in a mountain city, span 24 m, deck 1.6 m wide and sag 1.5 m, made of fitted warm-grey stone bridgeheads, dark iron chains, weathered cedar planks and hemp lashings, with missing decorative planks outside the continuous safe walking surface, rain wear on the deck and moss in the stone seams; water: none. Layout: one three-quarter view with the cliff gap, plus front, side and top orthographic views of the structure alone on a plain light warm-grey background, same scale.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```

### MC02-12M

Positive prompt:

```text
Three-view and three-quarter concept of a walkable suspension bridge connecting two cliff boardwalk landings in a mountain city, span 12 m, deck 1.6 m wide and sag 1.5 m, made of fitted warm-grey stone bridgeheads, dark iron chains, weathered cedar planks and hemp lashings, with missing decorative planks outside the continuous safe walking surface, rain wear on the deck and moss in the stone seams; water: none. Layout: one three-quarter view with the cliff gap, plus front, side and top orthographic views of the structure alone on a plain light warm-grey background, same scale.
Art direction: stylized hand-painted 3D game art for an Eastern xianxia fantasy world (Chinese immortal-cultivation setting), warm golden morning light from a low sun, soft warm rim light on edges and silhouettes, gentle blue-violet shadows (never pure black), layered soft white mist in the distance, painterly textures made of large soft colour gradients with a few visible brush strokes, rich but natural colour palette (sunlit warm yellow-greens, cool teal shade greens, warm grey stone, aged brown timber, blue-grey roof tiles, turquoise water), lived-in details: wear on edges, moss and soil in the joints, patched and repaired parts, small cracks, weathered wood grain, high level of detail with clear readable shapes and a strong silhouette, real-world scale and proportions, cohesive with a hand-painted xianxia valley village, game-ready asset look, high quality, masterpiece.
```

Negative prompt:

```text
photorealistic, photograph, photo texture, scanned texture, realistic PBR, plastic, glossy, shiny, chrome, pure black shadows, harsh contrast, neon colours, oversaturated, flat lighting, noon lighting, modern objects, cars, wires, concrete, glass windows, text, letters, Chinese characters, signature, logo, UI, watermark, frame, border, anime screenshot, cel-shaded flat colour, Genshin Impact, Mihoyo, copy of an existing game asset, blocky low-poly, voxel, cartoon chibi, noisy texture, blurry, low resolution, cropped, cut off, duplicate objects, extra limbs, floating parts, distorted perspective, fisheye
```
