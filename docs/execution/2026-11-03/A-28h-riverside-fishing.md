# A｜鄭翔元 John（約 28 小時）：第 9 天・溪邊釣魚烤魚＋三個舊場景

> 2026-11-02，Claude Code（核心組）依 z1nnz 指示撰寫。接在 [第 3 天・濁化山豬](../2026-11-02/01-A-day3-zhuo-boar.md)（#61 已合併）之後。
> **11/01 的自然套件取消**（樹和倒木已經有了）；那一包的三個小場景還空著，這次做。不要重做的東西見[總表](00-overview.md)第 3 節。
> 故事依據：[第一章大綱](../../story/第一章大綱-序幕序章與宗門.md) 第 9 天。美術標準和提示詞照 [美術風格指南](../art-style-guide-v1.md)。

## 0. 這一段在故事裡

水回來的隔天，溪裡有魚了。同屆五人在溪邊烤魚，聊以後要進哪個宗門，約好明年春天回茶亭喝茶。這是測資前最後一個快樂的晚上，玩法要**閒、舒服、讓人想多待一下**。

遊戲裡還沒有釣魚，這是全新的玩法；第 9 天之後每天都能回來釣。

| 項目 | 時數 |
|---|---:|
| 釣魚和烤魚的規則、測試 | 4 |
| 釣魚 Unity 元件 | 5 |
| 烤魚 Unity 元件 | 3 |
| 錄影、手感調整 | 2 |
| 魚 3 種（含游動） | 2.5 |
| 魚竿、浮標、魚簍 | 1.5 |
| 溪邊烤架和營火 | 3 |
| 三個舊場景 | 7 |
| **合計** | **28** |

## 1. 玩法（14 小時）

### 1.1 釣魚

地點：A3 釣魚台 `A3_FishPlatform_Bank`（−113, −20）。先在你自己的測試場景跑：一段 10 m 寬的水面加岸邊。

1. **拋竿**：按住蓄力，放開拋出，蓄力越久拋越遠（4–12 m）。手機按住右下「拋」，方向跟鏡頭。
2. **等**：浮標順水慢慢漂。看水面：魚來之前會有一圈小水紋。
3. **咬鉤**：浮標往下一沉，要在時間內按「提」。太早只是白提一下，重拋就好。
4. **拉魚**：張力條。按住收線、張力上升；放手放線、張力下降。張力太高斷線，魚跑了但**不扣東西、魚餌不算錢**。魚會突然衝一下，看竿尖彎曲就知道。
5. **上岸**：魚拉上來看一眼大小（魚身網格＋公分），進魚簍。

**數值寫進 `packages/content/creek-fishing-v1.json`：**

| 欄位 | 值 | 說明 |
|---|---|---|
| `waitSeconds` | 3–9 | 用種子決定，規則程式不直接用亂數 |
| `biteWindowSeconds` | 0.9 | 咬鉤時間 |
| `tensionRisePerSecond` | 0.45 | 收線時張力上升（0–1） |
| `tensionFallPerSecond` | 0.6 | 放線時張力下降 |
| `dashes` | 各魚種 | 衝刺次數、每次加多少張力 |
| `reelNeededSeconds` | 各魚種 | 要收線多久才上岸 |
| `fish` | 3 種 | `creek-dace` 白條（常見、好拉）、`creek-crucian` 溪鯽（普通）、`gold-scale` 金鱗（少見、會衝）；含大小範圍、權重、`sellPrice` |
| `day9Table` | 前 3 條固定 | 白條、溪鯽、白條；第 9 天一定釣得到，金鱗留到之後 |

第一次玩的人，3 條魚大約 3–5 分鐘。

### 1.2 烤魚

釣到 3 條後走到溪邊烤架（FI03）。把魚串上竹籤放到火上：

- 每條魚兩面，魚皮顏色從白變金黃再變焦黑；用**看的**，不要進度條。
- 按一下翻面，金黃時翻最好。
- 全部烤完分三種結果：`raw` 夾生、`good` 剛好、`burnt` 有點焦。**都能吃，不會浪費**：胖子連焦的也搶著吃。

三條魚依序遞給三個位置（`Seat_1..3`，先用膠囊體），核心組接對白。

### 1.3 規則程式和測試

純邏輯放 `tools/creek-fishing/`，測試放 `tests/creek-fishing.test.ts`（`npm test` 全過）。不碰 Unity 和網路，同樣種子結果一樣。測試至少涵蓋：

1. 咬鉤時間外提竿不會上魚，也不會扣東西；
2. 張力到 1 斷線，放線能救回來；
3. 收線滿時間才上岸；
4. `day9Table` 前 3 條固定，之後照權重；
5. 烤魚三種結果的時間邊界；焦了仍然算一條可吃的魚；
6. 上岸和烤完的事件只發一次。

### 1.4 Unity 元件

放 `apps/game/Assets/YunJing/Runtime/CreekFishing/`：`QingxiFishingSpot`、`QingxiCreekGrill`，都留 `BeginFromScript()`。手機和鍵盤滑鼠都能玩，觸控按鈕至少 88 × 88 px。

事件：`fishing.caught { fishId, sizeCm }`、`fishing.lost { reason }`、`grill.finished { results:[{seat, fishId, result}] }`。核心組接背包、伺服器和對白。

交：`creek-fishing-v1.json`、規則＋測試、兩個元件和測試場景、錄影（釣到一條、斷線一次、烤一輪）、手感問題至少 3 點。

## 2. 模型（14 小時）

共同規則：每件先做 AI 三視圖：提示詞整段貼上，**後面接風格指南 5.2**，負面欄貼 **5.3**，至少出 4 張挑最好的，存 `art/references/<編號>/`。品質優先，不要求降面數；三級 LOD 同一檔案；原點在腳印中心、底部高度 0、不附地面底板；擋人的附 `_Collision`；附 `model_info.json`；四視圖加 1.75 m 人形尺，再加一張並排比較圖。**不刻字、不寫字。** 匯出放 `art/exports/creek-fishing-a/`。

### FI01 三種魚（2.5 h）

白條 0.15–0.25 m、溪鯽 0.2–0.35 m、金鱗 0.3–0.5 m（金鱗的鱗片用金色漸層，不要發光）。每種 4–6 根骨，動畫 `Swim`（循環）、`Thrash`（上岸掙扎），加一個烤熟外觀的材質參數 `_Cooked`（0 生、0.5 金黃、1 焦黑）。

```
FI01  Three-view orthographic turnaround sheet of three kinds of mountain creek fish laid out together: a slender silver dace about 0.2 m long, a deep-bodied olive crucian carp about 0.3 m long, and a rare golden-scaled carp about 0.45 m long, made of wet scales and soft translucent fins, showing a nicked tail fin, slightly different scale patterns, a natural darker back and pale belly, used as fish caught from a clear stream in a mountain valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.
```

### FI02 魚竿、浮標、魚簍（1.5 h）

竹竿 3 m（幾根骨，拉魚時會彎；握把 `Socket_Hand`）、蘆葦管浮標 0.08 m（獨立物件）、腰掛的小魚簍 0.3 m（附 `Socket_Waist`，和背簍 MK04、背籠 C01 不一樣：口小肚大、有蓋）。

```
FI02  Three-view orthographic turnaround sheet of a village fishing set laid out together: a long slender split-bamboo fishing rod about 3 m long with a hemp line, a small reed float, and a small lidded waist creel about 0.3 m tall with a narrow neck and round belly, made of bamboo, reed, hemp and woven willow, showing a wrapped grip darkened by hands, a mended rod joint, a damp base on the creel, used by young villagers fishing a mountain creek. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.
```

### FI03 溪邊烤架和營火（3 h）

1.4 × 1.0 × 0.8 m 內。河石圍的火堆、兩根叉枝加一根橫竿、幾支竹籤（獨立物件，串魚用）、圍坐用的 3 顆平石。火焰由遊戲做，附 `Socket_Fire`；木炭用發光參數 `_Ember`（0–1）。這是孩子們臨時搭的，要看起來有點歪。

```
FI03  Three-view orthographic turnaround sheet of a small improvised creek-side campfire cooking setup, about 1.4 m wide, 1.0 m deep and 0.8 m tall, a ring of round river stones holding charcoal and half-burnt driftwood, two forked branches with a crossbar and several bamboo skewers, with three flat stones around it for sitting, made of river stone, driftwood, charcoal and bamboo, showing soot on the stones, a crooked forked stick propped up with a pebble, ash on the gravel, built by a few teenagers on a creek bank. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.
```

### 三個舊場景（7 h）

地圖上已經有格位，到現在還是空的。讓走過的人想停下來看。**只有外觀，互動和文字由核心組接。** 匯出放 `art/exports/world-scenes-a/`。

| 編號 | 格位 | 位置 (x, z)、yaw | 尺寸上限 | 時數 |
|---|---|---|---|---:|
| SC01 | `D3_FallenShrine` 倒下的土地公小廟 | (−100, 65)、200 | 1.6 × 1.4 × 1.8 | 2.5 |
| SC02 | `D3_HunterCamp` 熄掉的獵人營地 | (−66, 102)、30 | 3.0 × 3.0 × 1.2 | 2 |
| SC03 | `A2_RestPavilionRuin` 倒塌的歇腳亭 | (−30, −133)、10 | 4.0 × 4.0 × 3.2 | 2.5 |

```
SC01  Three-view orthographic turnaround sheet of a small roadside earth-god shrine that has toppled over, about 1.6 m wide and 1.8 m tall, a little stone niche with a tiled cap lying tilted on its side half in the soil, a small worn stone figure without a face still inside, made of weathered warm-grey stone and blue-grey tiles, showing cracked tiles, old incense sticks, a fresh small offering of wild fruit someone still leaves there, thick moss on the lower side, used beside a forest path in an upstream valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.

SC02  Three-view orthographic turnaround sheet of an abandoned hunter's camp, about 3 m wide, 3 m deep and 1.2 m tall, a cold fire pit of blackened stones, a wooden stool made from a log, a simple drying frame with a torn hide, a broken snare and a rusty pot, made of old wood, stone, leather and iron, showing weeds growing through the ashes, rain-rotted rope, fallen maple leaves, used in a quiet upstream valley nobody has visited for a while. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.

SC03  Architectural concept of a collapsed old rest pavilion on a country road for travellers who no longer come this way, footprint about 4 m wide and 4 m deep, 3.2 m high at the one post still standing, timber post-and-beam frame with gently upturned eave corners, a caved-in blue-grey clay tile roof sliding to one side, open on all sides with a broken bench, worn stone plinth with one step, details: scattered roof tiles, a fallen beam, a wild vine climbing the standing post, a bird's nest, weathering: rotted timber, grass growing through the plinth. Layout: one three-quarter view from slightly above at eye height of a person, plus front, side and back orthographic views on the same sheet at the same scale, plain light warm-grey background, even soft lighting, building only (no landscape around it except a small ground patch).
```

SC01、SC02 的碰撞附 `_Collision`；SC03 讓人可以走進去，只擋柱子和大塊瓦堆。並排比較：SC01 和 SC02 放你的 A09 避雨龕；SC03 放茶亭 RK03。

## 3. 交件

可分兩張 PR（玩法＋FI01–FI03 一張、三個舊場景一張），從最新 main 開分支。附三視圖、審圖、錄影、實際時數、還沒做完的地方。不改主場景、`QingxiHud`、伺服器、別人的資料夾；人物和對白由核心組做。
