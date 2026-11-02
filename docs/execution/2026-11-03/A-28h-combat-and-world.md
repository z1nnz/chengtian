# A｜鄭翔元 John（約 28 小時）：基礎戰鬥手感＋把世界補起來

> 2026-11-02，Claude Code（核心組）依 z1nnz 指示撰寫：以建模為主，玩法只留必要、能測試好不好玩的。
> **這一包不碰任何人物。** 不要重做的東西見[總表](00-overview.md)第 3 節。美術標準和提示詞照 [美術風格指南](../art-style-guide-v1.md)；畫質分級照 [quality-tiers-v1](../../standards/quality-tiers-v1.md) 第四節。

| 項目 | 時數 |
|---|---:|
| 基礎戰鬥手感（玩法） | 8 |
| D1 獵人工具棚 | 3 |
| D3 倒下的土地公小廟 | 2.5 |
| D3 熄掉的獵人營地 | 2 |
| A2 倒塌的歇腳亭 | 2.5 |
| A2 載貨板車 RK05 | 2.5 |
| 領地：淨水蓮 TY03 | 2 |
| 領地：練功地面 TY05 | 2 |
| 領地：練功器材 TY06 | 1.5 |
| 領地：碎石小徑 TY10 | 1.5 |
| 審圖、整理 | 0.5 |
| **合計** | **28** |

## 1. 基礎戰鬥手感（8 小時）

[總覽](../../承天-總覽.md)定的方向：即時動作，比原神簡單、手機好操作。遊戲現在只有林地遭遇和山豬裡的局部動作，這一包做一個共用的版本，**讓我們打木人就能測試好不好玩**。只做新手空手，不分道統、不做法寶、不做教學。

| 動作 | 規格 |
|---|---|
| 普攻 | 空手三段連擊；前搖、判定、收招；收招時按下一下才接得上 |
| 招式 | 一個蓄力重擊，帶擊退，有冷卻 |
| 閃避 | 沿用你的數值（2.5 m、無敵 0.35 秒），可取消普攻收招 |
| 回饋 | 命中停頓、鏡頭輕震、受擊閃白、碎屑、音效（占位） |
| 轉向 | 不做硬鎖定；出招時轉向 4 m 內最近的目標 |

- 數值放 `packages/content/basic-combat-v1.json`；純規則放 `tools/basic-combat/`，測試放 `tests/basic-combat.test.ts`（連擊時間窗、蓄力、冷卻、閃避無敵、同一擊不重複命中）。
- 元件 `QingxiBasicCombat` 放 `apps/game/Assets/YunJing/Runtime/BasicCombat/`，目標用介面 `ICombatTarget`。不改主場景和 `QingxiFirstPerson`。手機右手三個按鈕（攻、招、閃），至少 88 × 88 px。
- 測試場景：你的 A12 藤靶（會回擊）、山兔、山豬，只驗手感，不改那兩個遭遇的規則。動作先用現有試模動畫。
- 事件 `combat.hit { targetId, attackId, damage }`；結算由核心組接。
- 交：資料、規則＋測試、元件、測試場景、錄影、手感問題至少 3 點。

## 2. 模型（20 小時）

地圖上這些格位到現在都是空的。共同規則：每件先做 AI 三視圖：提示詞整段貼上，**後面接風格指南 5.2**，負面欄貼 **5.3**，至少出 4 張挑最好的，存 `art/references/<編號>/`。品質優先，不要求降面數；LOD0／1／2 同一檔案，`Detail_*` 分開，`model_info.json` 寫 `minTier`（這一包全部 `standard`，TY03 以外的小雜物放 `Detail_*`）；原點在腳印中心、底部高度 0、不附地面底板；擋人的附 `_Collision`；四視圖加 1.75 m 人形尺，再加一張並排比較和 LOD0／LOD1 對照。**不刻字、不寫字。**

| 編號 | 格位 | 尺寸上限（寬 × 深 × 高 m） |
|---|---|---|
| SC04 | `D1_HunterShed` | 3.6 × 3 × 2.8 |
| SC01 | `D3_FallenShrine` | 1.6 × 1.4 × 1.8 |
| SC02 | `D3_HunterCamp` | 3 × 3 × 1.2 |
| SC03 | `A2_RestPavilionRuin` | 4 × 4 × 3.2（走得進去，只擋柱子和瓦堆） |
| RK05 | `A2_Cart` | 3.2 × 1.6 × 1.4（輪子獨立可轉） |
| TY03、TY05、TY06、TY10 | 照 [10/31 A 包](../2026-10-31/01-A-territory-backyard.md) | 同左；TY06 不做兵器架 |

```
SC04  Architectural concept of a small hunter's tool shed at a forest edge for an unseen local hunter, footprint about 3.6 m wide and 3 m deep, 2.8 m high, timber post frame, bark and thatch lean-to roof, plank walls open on one side, stacked stone footing, details: hanging traps, coils of rope, drying hides, a chopping block, an axe, stacked firewood, weathering: sun-bleached planks, a patched roof, moss on the north side. Layout: one three-quarter view from slightly above at eye height of a person, plus front, side and back orthographic views on the same sheet at the same scale, plain light warm-grey background, even soft lighting, building only (no landscape around it except a small ground patch).

SC01  Three-view orthographic turnaround sheet of a small roadside earth-god shrine that has toppled over, about 1.6 m wide and 1.8 m tall, a little stone niche with a tiled cap lying tilted on its side half in the soil, a small worn faceless stone figure still inside, made of weathered warm-grey stone and blue-grey tiles, showing cracked tiles, old incense sticks, a small fresh offering of wild fruit, thick moss on the lower side, used beside a forest path in an upstream valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.

SC02  Three-view orthographic turnaround sheet of an abandoned hunter's camp, about 3 m wide, 3 m deep and 1.2 m tall, a cold fire pit of blackened stones, a stool made from a log, a simple drying frame with a torn hide, a broken snare and a rusty pot, made of old wood, stone, leather and iron, showing weeds growing through the ashes, rain-rotted rope, fallen maple leaves, used in a quiet upstream valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.

SC03  Architectural concept of a collapsed old rest pavilion on a country road for travellers, footprint about 4 m wide and 4 m deep, 3.2 m high at the one post still standing, timber post-and-beam frame with gently upturned eave corners, a caved-in blue-grey clay tile roof sliding to one side, open on all sides with a broken bench, worn stone plinth with one step, details: scattered roof tiles, a fallen beam, a wild vine climbing the post, a bird's nest, weathering: rotted timber, grass growing through the plinth. Layout: one three-quarter view from slightly above at eye height of a person, plus front, side and back orthographic views on the same sheet at the same scale, plain light warm-grey background, even soft lighting, building only (no landscape around it except a small ground patch).

RK05  Three-view orthographic turnaround sheet of a two-wheeled wooden goods cart resting on a country road, about 3.2 m long, 1.6 m wide and 1.4 m tall, loaded with hemp sacks and bamboo baskets tied with rope, made of old elm, iron-bound wheels and hemp, showing worn wheel rims, a mended side rail, dried mud on the wheels, used by traders on the road to a valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.

TY03  Growth stage sheet of a magical water lotus in four stages side by side: small floating leaves, upright round leaves, a closed pale bud on a slim stem, a full open pale white and jade flower whose heart glows faintly, each about 0.15 / 0.35 / 0.55 / 0.65 m tall, growing from shallow muddy water, plain light warm-grey background, orthographic side views at the same scale on one ground line, even soft lighting.

TY05  Seamless tileable square texture of old fitted flagstones in a small home practice yard, worn smooth in the middle from years of footsteps, grass and moss growing in the joints, a few cracked stones, viewed straight from above, real-world scale about 2 m by 2 m, hand-painted: large soft colour variation warm grey #8f8878 to pale tan #b5ab94, a few painterly brush strokes, small details readable but not noisy, even flat lighting (no shadows, no highlights baked in), edges must tile seamlessly on all four sides.

TY06  Three-view orthographic turnaround sheet of a pair of old strength training stones laid out together: a stone lock about 0.35 m wide with a carved handle, and a stone barbell about 1.2 m long made of two round stones on a thick wooden bar, made of warm-grey granite and old ash wood, showing a hand-polished grip, chipped edges, moss at the base, used in a small home practice yard in a mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.

TY10  Seamless tileable square texture of a narrow path of small crushed stones and packed earth in a village yard, grass creeping in at both edges, a few larger flat stones, viewed straight from above, real-world scale about 1 m by 1 m, hand-painted: large soft colour variation warm brown #8a6a44 to light tan #b8955e, a few painterly brush strokes, small details readable but not noisy, even flat lighting (no shadows, no highlights baked in), edges must tile seamlessly on all four sides.
```

TY05、TY10 是貼圖加嵌在地面的網格，不高出地面 2 cm。

## 3. 交件

可分兩張 PR（戰鬥一張、模型一張），從最新 main 開分支。附三視圖、審圖、錄影、實際時數、還沒做完的地方。不改主場景、`QingxiHud`、伺服器、別人的資料夾。**不要做**人物、教學劇情、對白。
