# C｜Eli-0731（約 28 小時）：基礎建模練習，同時把世界填起來

> 2026-11-02，Claude Code（核心組）依 z1nnz 指示撰寫。**這一版取代先前寄出的山城地標包**（飛升榜、大鐘、高塔先不用做）。
> 這一輪的重點是把基本功練穩：**形狀好看、比例對、貼圖乾淨**，比細節多重要。每一件都是遊戲真的會用的東西，世界需要很多。
> 只做模型，不排玩法，不做人物。美術標準和提示詞照 [美術風格指南](../art-style-guide-v1.md)。

## 0. 怎麼練

照順序做，由簡單到難，每一件練一個重點。

| 順序 | 東西 | 這件練什麼 | 時數 |
|---:|---|---|---:|
| 1 | BM01 木箱 3 種 | 方形、倒角、木紋貼圖 | 3 |
| 2 | BM02 拴繩矮木樁 2 種 | 圓柱、樹皮和磨損 | 2 |
| 3 | BM03 陶罐 3 種 | 旋轉體、輪廓曲線 | 3 |
| 4 | BM04 山路塊石 4 種 | 自然的形狀、不要像方塊也不要像饅頭 | 3 |
| 5 | BM05 石桌和石凳 | 幾件東西擺成一組、比例 | 2 |
| 6 | BM06 舊石缸和花台 | 把形狀挖空、簡單的浮雕 | 3 |
| 7 | BM07 舊石碑 | 表面風化、一塊被鑿過的粗糙面 | 3 |
| 8 | BM08 灌木 2 種 | 葉片面片、透明貼圖 | 3 |
| 9 | BM09 蕨 2 種 | 葉片的方向和彎曲 | 2 |
| 10 | BM10 苔蘚、落葉貼片 | 可無縫重複的貼圖 | 2 |
| | 審圖、整理 | | 2 |
| | **合計** | | **28** |

**不用做的**：不用做很細的雕刻、複雜結構、骨架動畫、狀態切換。看起來單純沒關係，要的是做得乾淨。

**做完第 1 件（木箱）就先開一張 PR**，讓核心組看一下，有需要調整的地方後面就不會重複踩到；之後其他件可以一起交。

## 1. 每一件的規則

1. **先做三視圖**：下面的提示詞整段貼上，**後面接風格指南 5.2**，負面欄貼 **5.3**，至少出 4 張挑最好的，存 `art/references/<編號>/`。
2. **照真實尺寸**，1 單位 = 1 m；原點在底部中心，底部高度 0，不附地面底板。
3. **先看輪廓**：關掉貼圖，只看灰模的外形，好看了才做貼圖。
4. **貼圖**：大塊柔和的顏色變化加少量筆觸，不要照片貼圖，也不要整片雜訊。
5. **LOD**：LOD0、LOD1（約 50%）、LOD2（約 15%）放同一檔案。小東西用減面工具就好，檢查輪廓沒有破掉。
6. **`model_info.json`**：尺寸、面數、材質、有沒有碰撞，加 `"minTier"`（值見各件；說明在 [畫質分級](../../standards/quality-tiers-v1.md) 第四節）。
7. **碰撞**：要擋人的附一個簡單的 `_Collision`。
8. **審圖**：四視圖加 1.75 m 人形尺，再加一張和指定作品並排的圖。

**不刻字、不寫字、不寫數字。** 匯出放 `art/exports/modelling-basics-c/`。

## 2. 每一件的規格

| 編號 | 尺寸 | 規格 | `minTier` | 並排比較 |
|---|---|---|---|---|
| BM01 | 0.5 / 0.8 / 1.1 m 寬 | 3 種大小的舊木箱，木板拼的，有的帶繩；附 `_Collision` | `standard` | 你的 C07 工具箱 |
| BM02 | 高 0.8–1.1 m，粗 0.2 m | 路邊綁東西用的矮木樁 | `high` | 你的 C05 木牌 |
| BM03 | 高 0.3 / 0.5 / 0.8 m | 粗陶罐：矮胖、細長、大口 | `high` | 你的 C03 水桶 |
| BM04 | 0.4–1.5 m | 4 種風化塊石，半埋；最大的附 `_Collision` | `standard` | `qingxi-moss-boulder-v2`，要看得出不同 |
| BM05 | 桌高 0.75 m、桌面 Ø1 m、凳高 0.45 m | 石桌一張、石凳 2 種；可分開擺 | `standard` | 1.75 m 人形尺 |
| BM06 | 石缸 Ø0.8 m、花台 1.2 m 寬 | 石缸 2 種、花台 2 種；浮雕只要簡單的雲紋 | `standard` | BM05 |
| BM07 | 1.1 × 0.5 × 2.3 m | 一座站著的舊石碑，表面磨到看不清，中間一長條被鑿掉；附 `_Collision` | `standard` | BM04 |
| BM08 | 高 1.0 / 1.2 m | 圓叢和帶紅果的散枝；面片做葉，不帶底座 | 一種 `standard`、一種 `high` | `WildShrub`，要看得出不同 |
| BM09 | 高 0.3 / 0.8 m | 低矮的和長羽葉的 | 一種 `standard`、一種 `high` | `qingxi-fern-flower-v2`，要看得出不同 |
| BM10 | 每片 1 m 見方 | 苔蘚 1 種、紅楓落葉 1 種、黃葉 1 種 | `ultra` | 地面截圖 |

## 3. 提示詞

```
BM01  Three-view orthographic turnaround sheet of a set of three old wooden crates in different sizes, about 0.5, 0.8 and 1.1 m wide, made of plain pine planks with simple corner battens, one tied with hemp rope, showing worn edges, a replaced plank, soil at the bottom, used in a street in a mountain village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.

BM02  Three-view orthographic turnaround sheet of two short weathered wooden hitching posts, about 0.8 and 1.1 m tall and 0.2 m thick, made of round old logs with a groove worn by rope near the top, showing cracked grain, a little moss at the foot, used beside a road in a mountain village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.

BM03  Three-view orthographic turnaround sheet of three plain clay storage jars, about 0.3, 0.5 and 0.8 m tall, one squat, one slender, one with a wide mouth, made of rough fired brown clay with a dark glaze on the upper part, showing a chipped rim, drip marks in the glaze, dust on the shoulder, used along a street in a mountain village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.

BM04  Three-view turnaround of a set of four weathered mountain path stones, about the largest 1.5 m long and 0.9 m tall, form: angular shapes softened by weather with a few flat faces, half buried in the ground, surface: warm grey stone with darker cracks and a little yellow-green lichen, a small tuft of grass at the base. Layout: front, side and top views, same scale, plain light warm-grey background, even soft lighting.

BM05  Three-view orthographic turnaround sheet of a simple stone table and two kinds of stone stools, the round table about 1 m wide and 0.75 m tall, the stools about 0.45 m tall, one drum-shaped and one square, made of plain warm-grey granite, showing worn seat tops, a chipped edge, lichen at the base, used on a resting spot beside old stone stairs. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.

BM06  Three-view orthographic turnaround sheet of a set of old stone garden pieces laid out together: two carved stone water basins about 0.8 m wide, and two low square stone planters about 1.2 m wide (one with a small shrub, one with grass), made of weathered warm-grey granite, showing moss, water lines, chipped corners, one simple cloud relief band with no letters and no text, used at the landings of old stone stairs. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.

BM07  Three-view orthographic turnaround sheet of an ancient standing stone stele in a forest, about 1.1 m wide, 0.5 m deep and 2.3 m tall, made of dark weathered granite on a low square base, its face worn smooth beyond reading with no letters and no text, one long vertical strip roughly chiselled away and paler than the rest, showing moss on the top and base, lichen, fallen needles on the base. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.

BM08  Three-view turnaround of 【shrub，依序填：a round dense creek-side willow-leaf shrub about 1.2 m tall / a loose forest-edge shrub about 1.0 m tall with small red berries】, form: natural irregular branching with visible twigs and clumps of leaves, surface: leaves warm sunlit yellow-green on top and cool teal-green underneath, a few fallen leaves at the base. Layout: front, side and top views, same scale, plain light warm-grey background, even soft lighting.

BM09  Three-view turnaround of 【fern，依序填：a large wild fern with long arching feathery fronds about 0.8 m tall / a low curly woodland fern about 0.3 m tall】, form: fronds rising from one crown at the soil line, surface: fresh green fronds with brown dried tips on the oldest ones. Layout: front, side and top views, same scale, plain light warm-grey background, even soft lighting.

BM10  Seamless tileable square texture of 【patch，依序填：soft thick cushion moss / scattered red maple leaves / scattered golden ginkgo leaves】, viewed straight from above, real-world scale about 1 m by 1 m, hand-painted: large soft colour variation, a few painterly brush strokes, small details readable but not noisy, even flat lighting (no shadows, no highlights baked in), edges must tile seamlessly on all four sides.
```

## 4. 交件

從最新 main 開分支，**開 PR 時請勾選「Allow edits by maintainers」**，核心組才能幫忙處理合併的小問題。第一張 PR 只放木箱，第二張放其他件。附三視圖、審圖、`model_info.json`、實際時數，還有你覺得哪裡做得不順、想多練的地方。

有卡住的地方直接問，不用硬撐；比起做完全部，我們更想看到每一件都做得乾淨。
