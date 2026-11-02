# B｜蘇奕安 Josh（約 56 小時）：修水路＋把西溪和山城建起來

> 2026-11-02，Claude Code（核心組）依 z1nnz 指示撰寫。**這一版取代先前寄出的版本**：以建模為主，玩法只留必要、能測試好不好玩的；不碰任何人物。村會沙盤、舊信、瓦、曆書都拿掉了。
> 不要重做的東西見[總表](00-overview.md)第 3 節。美術標準和提示詞照 [美術風格指南](../art-style-guide-v1.md)；畫質分級照 [quality-tiers-v1](../../standards/quality-tiers-v1.md) 第四節。

| 段 | 內容 | 時數 |
|---|---|---:|
| 一 | 修水路玩法：清淤、接渠、通水 | 12 |
| 二 | 工地和三種修法的模型 | 13.5 |
| 三 | A3 西溪：水磨坊、水車、石橋等 | 20.5 |
| 四 | 山城的三個攤位 | 10 |
| | **合計** | **56** |

每一段可以各開一張 PR，順序自由。

## 1. 修水路玩法（12 小時）

遊戲裡現在走到閘門選一句話就修好了（`QingxiWaterworksSite`）。修水路是新手篇的主要大事，這一段做一個**短而好玩的版本**，讓我們測試。沿用 `packages/content/waterline.json` 的三個修法，**不改這個檔案**；修法的選擇先用現有的對話。

| 工作 | 玩法 |
|---|---|
| **清淤** | 用鏟子把泥撥開（拖曳），泥要有重量感，舊石頭慢慢露出來 |
| **接渠** | 沿用你的 `waterworks-core` 和錯接說明，放段件，接不上會告訴你差幾公分 |
| **通水** | 轉閘輪（你的 B06），水頭沿路線往下走，流進幾塊田，田變濕；可以跟著走 |

- 三個修法的工作量不同（`clear_silt` 清淤多、接渠 2 段；`restore_channel` 接渠 4 段；`protect_nursery` 接渠 3 段加渡槽）。全程約 5–8 分鐘，**不會失敗**。修法只影響外觀和水面寬度。
- 多人規則照[總覽](../../承天-總覽.md)第六節：工程狀態記在每個人身上，工作量用 `partySize` 調整；這一包只要規則支援，連線由核心組做。
- 資料放 `packages/content/creek-repair-v1.json`，純規則放 `tools/creek-repair/`（import 你的 `waterworks-core`，不要複製），測試放 `tests/creek-repair.test.ts`，Unity 放 `apps/game/Assets/YunJing/Runtime/CreekRepair/`。不改主場景、`QingxiHud`、`QingxiWaterworksSite`、伺服器。手機和鍵盤滑鼠都能玩。
- 事件：`creek.workCompleted { method, layout, patches }`（格式照你的 `CONTRACT.md`）、`creek.flowReached { nodeId }`、`creek.flowCompleted { method }`。
- 測試：工作量和 `waterline.json` 對得上、任何順序都能完工、存檔還原、`partySize` 1–4、事件不重複。
- 交：資料、規則＋測試、元件、測試場景、錄影（三種修法各一段）、手感問題至少 3 點。

## 2. 模型的共同規則

每件先做 AI 三視圖：提示詞整段貼上，**後面接風格指南 5.2**，負面欄貼 **5.3**，至少出 4 張挑最好的，存 `art/references/<編號>/`。品質優先，不要求降面數；LOD0／1／2 同一檔案，`Detail_*` 分開，`model_info.json` 寫 `minTier`；原點在腳印中心、底部高度 0、不附地面底板；擋人的附 `_Collision`；四視圖加 1.75 m 人形尺，再加一張並排比較和 LOD0／LOD1 對照。**不刻字、不寫字。** 匯出放 `art/exports/creek-repair-b/`。

## 3. 工地和三種修法（13.5 小時）

**直接拿來擺、不要重做**：C 的水桶 C03、扁擔 C04、布旗 C06、工具箱 C07（含木槌、鑿、繩）；A 的泥沙洲 A04；你的推車 B11、閘板 B05、閘輪 B06、完工碑座 B12。`restore_channel` 不做新渠，用你的 B02 系列加 B07 補石，材質參數 `_Fresh`（0–1）讓新補的石頭偏淺、沒有苔。

| 編號 | 東西 | 時數 | 規格 |
|---|---|---:|---|
| CR03 | 工地料堆 | 3 | 石料堆 2 × 1.5 × 1、木料架 2.5 × 1 × 1.2、泥堆 2 × 2 × 0.8 m 內；各 3 個階段（少／中／多） |
| CR04 | 工具組 | 2 | 鏟、畚箕、木夯、灰桶和抹刀；各附 `Socket_Hand` |
| CR05 | 涼棚和茶水 | 2.5 | 4 × 3 × 2.8 m 內；柱子附 `_Collision` |
| CR06 | 土堤木樁渠（`clear_silt`） | 1.5 | 2 m 直段和彎段，接口同 B02／B03；水面分開成 `_water` |
| CR08 | 竹木渡槽（`protect_nursery`） | 2 | 同上，另加 0.8–2.5 m 高的支架 3 種 |
| CR07 | 溪邊慶祝擺設 | 1.5 | 3 m 拼湊長桌、6 m 紙燈串（每盞 `_Lit`）、酒罈、果籃；`minTier: high` |
| CR09 | 每戶分水小閘 | 1 | 0.8 × 0.5 × 0.9 m 內，2 種；閘板獨立 `Gate`，往上開 0.3 m |

```
CR03  Three-view orthographic turnaround sheet of a village construction yard set laid out together: a pile of rough-cut warm-grey granite blocks about 2.0 m wide and 1.0 m tall, a simple wooden rack of logs and planks about 2.5 m wide and 1.2 m tall, and a heap of wet dark creek silt about 2.0 m wide and 0.8 m tall with a wooden plank laid across it, made of granite, cedar logs, rope and wet mud, showing chisel marks, muddy footprints, a broken stone set aside, rope ties on the rack, used at a site where villagers repair an old water channel in a mountain valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.

CR04  Three-view orthographic turnaround sheet of a set of old village earthwork tools laid out together: a long-handled iron spade about 1.3 m long, a woven bamboo dirt basket about 0.5 m wide, a heavy wooden tamper about 1.1 m long, and a small mortar bucket with a trowel, made of old ash wood, dark iron, split bamboo and hemp rope, showing mud on the blades, hand-polished grips, a handle mended with rope, used by villagers repairing a water channel. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.

CR05  Three-view and three-quarter concept of a simple temporary work shelter beside a creek, about 4 m wide, 3 m deep and 2.8 m tall, made of four bamboo posts tied with hemp rope holding a patched canvas roof, with a rough wooden bench, a large wooden tea bucket with a ladle and a few clay bowls on a crate, showing sun-faded canvas, a newer patch, muddy post feet, towels hung on the rope, water: a nearly dry creek bed in the background with small puddles. Layout: one three-quarter view with the water, plus front, side and top orthographic views of the structure alone on a plain light warm-grey background, same scale.

CR06  Three-view and three-quarter concept of a repaired earthen water channel with low packed-earth banks held in place by rows of short wooden stakes woven with willow branches, a straight section 2 m long and 1 m wide, made of dark packed earth, weathered stakes and woven willow, with details: young grass on the banks, a muddy footprint, a few old stones of the former channel showing through, water: clear turquoise water flowing gently, pebbles visible in the shallows. Layout: one three-quarter view with the water, plus front, side and top orthographic views of the structure alone on a plain light warm-grey background, same scale.

CR08  Three-view and three-quarter concept of a raised rustic flume carrying water above the ground, a straight section 2 m long and 0.6 m wide, made of a split-bamboo and cedar plank trough on A-frame wooden trestles tied with hemp rope, 1.5 m above the ground, with details: small drips between planks, rope lashings, a patched section, moss starting at the trestle feet, water: clear turquoise water running along the trough with a few drops falling. Layout: one three-quarter view with the water, plus front, side and top orthographic views of the structure alone on a plain light warm-grey background, same scale.

CR07  Three-view orthographic turnaround sheet of a village creek-side celebration set laid out together: a long patchwork table about 3 m long made of several mismatched old planks, a 6 m string of small round paper lanterns hung between two bamboo poles, a few clay wine jars and a basket of fruit, made of old timber, split bamboo, mulberry paper, glazed clay and hemp rope, showing uneven plank edges, a mended lantern, spilled water rings on the table, used when a whole village gathers to celebrate the return of their creek. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.

CR09  Three-view orthographic turnaround sheet of a small household water diversion gate, about 0.8 m wide, 0.5 m deep and 0.9 m tall, a low fitted stone frame holding a single sliding wooden board with a short lifting handle, made of warm-grey stone, old cedar and hemp rope, showing water stains, a wet line, moss in the groove, a rope mended by hand, used where a village channel feeds water into one family's field. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```

## 4. A3 西溪（20.5 小時）

地圖上 A3 的這些格位全部還空著，這裡是新手世界最漂亮的一段溪，水路修好後水也會流到這裡。全部 `minTier: standard`。水面由核心組的材質處理，不做。

| 編號 | 格位 | 尺寸上限（寬 × 深 × 高 m） | 時數 | 規格 |
|---|---|---:|---:|---|
| WM01 | `A3_MillHouse` | 8 × 6 × 6 | 7 | 石基、木構、青灰瓦；側面開口讓水車軸穿入；門窗看得到屋內磨盤，不做室內場景 |
| WM02 | `A3_WaterWheel` | 1.2 × 5 × 5 | 3 | 輪徑 4.6 m、16 片輪葉；**原點在轉軸中心**，遊戲會旋轉，軸要正圓 |
| WM07 | `A3_StoneBridge` | 4 × 12 × 4 | 4 | 單拱，跨距 6 m，橋面寬 2.4 m，坡度 15° 以內，兩端接土路；碰撞要能走 |
| WM04 | `A3_Millstones` | 2 × 1.5 × 1 | 1.5 | 舊磨盤和麻袋 |
| WM05 | `A3_WashSteps` | 6 × 3 × 1.2 | 2 | 四階石階入水，最下一階磨得最亮 |
| WM09 | `A3_BambooPavilion` | 3.5 × 3.5 × 4 | 3 | 六角、竹柱、茅草頂、中間一張石桌 |

```
WM01  Architectural concept of a riverside water mill for a mountain valley village, footprint about 8 m wide and 6 m deep, two low storeys, ridge 6 m high, timber post-and-beam frame with gently upturned eave corners, blue-grey clay tile roof with a moss-covered ridge, plastered lower walls and plank upper walls, paper lattice windows and a wide wooden door, worn stone plinth rising straight from the water's edge, details: an opening in the side wall for a water wheel axle, millstones visible through the doorway, stacked grain sacks under the eaves, flour dust on the door frame, weathering: water stains on the plinth, a repaired roof corner with newer tiles, moss on the north side. Layout: one three-quarter view from slightly above at eye height of a person, plus front, side and back orthographic views on the same sheet at the same scale, plain light warm-grey background, even soft lighting, building only (no landscape around it except a small ground patch).

WM02  Three-view orthographic turnaround sheet of a large wooden water wheel, about 4.6 m in diameter and 1.2 m wide, sixteen evenly spaced wooden paddles on two spoked rims around a thick round axle, made of dark wet oak, iron bands and rope lashings, showing green algae on the lower paddles, one newer replacement paddle, water stains, used on a riverside water mill in a mountain valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.

WM07  Three-view and three-quarter concept of an old single-arch stone bridge over a creek, span 6 m, overall 12 m long, deck 2.4 m wide, arch 4 m above the water, made of fitted warm-grey granite blocks worn smooth on the walking surface, with low stone railings with simple cloud relief and no letters, moss along the waterline, ferns in the joints, water: clear turquoise creek water, pebbles visible in the shallows, white foam where it flows around stones. Layout: one three-quarter view with the water, plus front, side and top orthographic views of the structure alone on a plain light warm-grey background, same scale.

WM04  Three-view orthographic turnaround sheet of a small pile of old millstones and grain sacks, about 2 m wide, 1.5 m deep and 1 m tall, two round grooved millstones leaning together with three hemp sacks and a wooden scoop, made of grey granite, hemp and old wood, showing worn grooves, a cracked stone retired from use, flour on the sacks, moss on the lower stone, used beside a water mill. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.

WM05  Three-view and three-quarter concept of old stone washing steps going down into a creek, 6 m wide, 3 m deep and 1.2 m high, four broad steps of fitted warm-grey granite, the lowest step worn shiny from years of washing, with flat scrubbing stones, a wooden post for tying baskets, moss along the waterline, water: clear turquoise creek water, pebbles visible in the shallows. Layout: one three-quarter view with the water, plus front, side and top orthographic views of the structure alone on a plain light warm-grey background, same scale.

WM09  Architectural concept of a small six-sided bamboo pavilion in a bamboo grove by a creek, for villagers to rest, footprint about 3.5 m wide, 4 m high, bamboo post frame with gently upturned eave corners, thatched roof with a moss-covered peak, open on all sides, low round stone plinth, details: a round stone table with four stone stools, bamboo railings, fallen bamboo leaves, weathering: sun-bleached bamboo, a re-tied joint, a patched section of thatch. Layout: one three-quarter view from slightly above at eye height of a person, plus front, side and back orthographic views on the same sheet at the same scale, plain light warm-grey background, even soft lighting, building only (no landscape around it except a small ground patch).
```

並排比較：WM01、WM09 放你的 H01 舊屋；WM07、WM05 放你的河岸模組。

## 5. 山城的三個攤位（10 小時）

讓山城的街看起來人多、東西多、很熱鬧。格位由核心組放進山城。全部 `minTier: standard`，零碎掛件做成 `Detail_*`。

| 編號 | 東西 | 尺寸上限 | 時數 | 規格 |
|---|---|---|---|---|
| CR10 | 符紙飾品攤 | 3.5 × 2 × 2.8 | 3.5 | 成串的黃符紙（**無字**，抽象硃砂紋）、小葫蘆、歪掉的布幡；符紙串獨立，可在風中晃 |
| CR11 | 麵攤 | 4.5 × 3.5 × 2.8 | 4 | 爐灶、大鍋（`Socket_Steam`）、案板、方桌、長凳、遮雨棚；麵碗獨立，有滿和空兩個狀態 |
| CR12 | 榜單告示欄 | 3 × 0.6 × 2.8 | 2.5 | 空白榜單紙條獨立 `Slip_01..12`，字由遊戲疊上；欄杆磨亮 |

```
CR10  Three-view orthographic turnaround sheet of a gaudy little street stall selling lucky charms in a mountain city, about 3.5 m wide, 2 m deep and 2.8 m tall, a wooden cart-like stall with a crooked cloth banner and hundreds of hanging yellow paper charms in strings with abstract red swirl patterns (no letters, no text), rows of cheap gilded little gourds, tassels and tiny bells, made of painted old wood, yellow paper, red cotton and thin gilded tin, showing peeling gold paint, a wobbly leg propped on a brick, a shop-worn cushion, cheerful clutter. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.

CR11  Architectural concept of a small noodle stall in a mountain city street, footprint about 4.5 m wide and 3.5 m deep, 2.8 m high, a bamboo and timber lean-to with a patched canvas awning, a brick stove with a big steaming iron pot, a floured chopping board with fresh noodles and hanging ladles, one square wooden table with two long benches, details: stacks of large coarse ceramic noodle bowls, chopsticks in a bamboo cup, a bench with one short leg propped up, a cloth sign without text, weathering: smoke-darkened beams, grease stains, worn table top. Layout: one three-quarter view from slightly above at eye height of a person, plus front, side and back orthographic views on the same sheet at the same scale, plain light warm-grey background, even soft lighting, building only (no landscape around it except a small ground patch).

CR12  Three-view orthographic turnaround sheet of a large public ranking notice board in a mountain city, about 3 m wide, 0.6 m deep and 2.8 m tall, a timber frame with a small tiled roof and a wide wooden backing covered in columns of blank paper slips (completely blank, no letters, no text), the top slip much older and curling at the corners, a worn wooden railing in front where people lean, made of dark old timber, blue-grey tiles, yellowed paper and iron nails, showing layers of old torn paper, nail holes, a hand-polished rail, used in a busy street. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```

## 6. 交件和不要做

每段各一張 PR，從最新 main 開分支，照 PR 範本附三視圖、審圖、錄影、實際時數、還沒做完的地方。

**不要做**：人物、NPC、對白、教學；村會玩法；失敗結局；材料卡關；水面模型；在模型上刻字寫字。
