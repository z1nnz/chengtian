# B｜蘇奕安 Josh（約 56 小時）：第 5–8 天・把水修回來

> 2026-11-02，Claude Code（核心組）依 z1nnz 指示撰寫：「給協作者 B 安排 56 小時的工作包」。
> 接在 [11/02 第 4 天・第一次收成](../2026-11-02/02-B-day4-harvest-market.md)（#63 已合併）之後。
> 故事依據：[第一章大綱](../../story/第一章大綱-序幕序章與宗門.md) 第 5–8 天。美術標準和 AI 提示詞照 [美術風格指南](../art-style-guide-v1.md)。

> **2026-11-02 修訂**：對過所有舊工作包後，改掉和既有成果重複的部分：工具組不再做木槌（C 的工具箱已有），「新舊拼接石渠」改用你現成的 B02＋B07，省下的時間改做溪邊慶祝擺設；編號由 WM 改成 CR（WM 已被 A3 水磨坊套件使用）。

## 0. 為什麼是你、這一包在做什麼

舊水路的 12 件水工模型（`art/exports/qingxi-waterworks-b`）和導水規則（`tools/qingxi-waterworks-b`）都是你做的。但遊戲裡現在只是走到閘門旁邊、選一句話，水路就修好了（核心組的 `QingxiWaterworksSite`）。

第 6–8 天是新手十天中段最重要的一條線，也是序章第一個小高光：**全村一起選方法、一起動手、最後一起看水流過每一戶田。** 這一包把那句話變成真的玩法，再做第 5 天山城要用的三個攤位。

| 段 | 天 | 內容 | 玩法 | 模型 | 合計 |
|---|---|---|---|---|---|
| 一 | 6 | 村會與水路沙盤 | 5 h | 4 h | 9 h |
| 二 | 7 | 修水路：清淤、砌石、接渠 | 15 h | 8 h | 23 h |
| 三 | 8 | 水回來：通水、流過每一戶田 | 8 h | 6 h | 14 h |
| 四 | 5 | 山城的護身符攤、麵攤、人間榜 | — | 10 h | 10 h |
| | | **合計** | **28 h** | **28 h** | **56 h** |

建議順序：一 → 二 → 三，第四段累了隨時可以穿插。**每一段可以各開一張 PR，做完一段就交一段**，不用等全部做完。

**定調**：溫暖、熱鬧、單純的快樂。修水路**不會失敗**：做得慢、做得不漂亮都能完工，只是看起來不一樣。玩家修的時候只覺得在修水路；任何怪事都只看得到、不解釋。

## 1. 三種方法（全部玩法共用）

延用現有的 `packages/content/waterline.json` 三個 id，**不要改這個檔案**。

| id | 名稱 | 取捨（遊戲裡的話） | 村子看起來 | 清淤 | 砌石 | 接渠 | 通水後水量 |
|---|---|---|---|---|---|---|---|
| `clear_silt` | 先清淤 | 工最少、搬石頭最少，舊渠還是舊的 | 土堤木樁護岸（CR06） | 6 處 | 1 塊 | 2 段 | 1.0 |
| `restore_channel` | 修回舊渠 | 水走原路，會經過育幼區旁邊 | 你現成的 B02 系列＋B07 補石 | 3 處 | 2 塊 | 4 段 | 0.85 |
| `protect_nursery` | 保護育幼區 | 繞開育幼區，要搬很多石頭 | 跨過育幼區的竹木渡槽（CR08） | 2 處 | 3 塊 | 3 段 | 0.7 |

- 接渠段數照 `waterline.json` 的 `channel`（2／4／3）；砌石塊數是 `stone` 除以 4 無條件進位（4／6／12 → 1／2／3）。測試要檢查兩者和 `waterline.json` 對得上。
- 水量只影響水面寬度和水聲，**不影響田有沒有水、不影響故事和數值**。
- 三種都一樣好，沒有正解；介面不要標推薦。

## 2. 共同規則

**檔案位置（照你收成那一包的方式）**

| 東西 | 位置 |
|---|---|
| 規則資料 | `packages/content/creek-repair-v1.json` |
| 純規則 | `tools/creek-repair/`（可以 import `tools/qingxi-waterworks-b/src/waterworks-core.mjs`，不要複製） |
| 測試 | `tests/creek-repair.test.ts`（`npm test` 全過） |
| Unity | `apps/game/Assets/YunJing/Runtime/CreekRepair/`，場景產生器放 `Editor/CreekRepairSceneBuilder.cs` |
| 模型 | `art/references/<編號>/`、`art/source/creek-repair-b/`、`art/exports/creek-repair-b/`、`art/previews/creek-repair-b/` |
| 紀錄 | `docs/execution/creek-repair-v1.md` |

**不能改**：主場景、`QingxiHud`、`QingxiWaterworksSite`、`services/api`、`packages/contracts`、`waterline.json`、你以前交過的模型（要改就另存新版本，像 HerbalStall v002 那樣）、別人的資料夾。

**玩法**：純規則不碰 Unity 和網路，不用亂數；手機觸控和鍵盤滑鼠都能玩，觸控按鈕至少 88 × 88 px；每段交實際玩過的錄影（1280×720 以上）和至少 3 點手感問題。先在你自己的測試場景跑，**不用等任何人的東西**；需要的外部模型在第 7 節。

**模型**：每件先做 AI 三視圖：下面的提示詞整段貼上，**後面接風格指南 5.2**，負面欄貼 **5.3**，至少出 4 張挑最好的，提示詞和圖存 `art/references/<編號>/`。品質優先，不要求降面數；三級 LOD 同一檔案（`_LOD1`、`_LOD2`）；原點在腳印中心、底部高度 0、不附地面底板；擋人的附 `_Collision`；附 `model_info.json`；四視圖加 1.75 m 人形尺，再加一張個人單指定的並排比較圖。**所有東西都不刻字、不寫字**；要顯示字的地方由遊戲 UI 疊上去。

**事件**：完成時發出下面規定的事件；核心組接對白、演出、伺服器（沿用現有的 `waterworks-commit`）和存檔。你的元件都留 `BeginFromScript()`，核心組演完開場再呼叫。

## 3. 第一段・第 6 天：村會與水路沙盤（9 h）

### 玩法（5 h）

全村在廣場開會。中間一張**水路沙盤**（CR01），玩家繞著走、看，自己決定。這不是一個選單，要讓人感覺是「大家圍著桌子吵」。

1. 走近沙盤，鏡頭推近，水路用小石子和細沙擺在桌面上。
2. 點三個小木牌其中一個：沙盤上那條路線亮起，一杯水慢慢倒進去，水沿著路線流（一條路約 3 秒）；旁邊出現第 1 節的取捨，和這條路完工後的小模型。
3. 三位村民（先用膠囊體）各站一邊，看玩家指哪條就說一句話（支持或擔心，句子 id 放資料裡，文字先寫占位，核心組換正式對白）。
4. 想好了，把代表玩家的那塊小石頭放到路線起點 → 確認一次 → 全村點頭。
5. 第 7 天開工前可以回來換，開工後鎖定。

事件：`creek.methodChosen { method }`。

### 模型（4 h）

**CR01 水路沙盤**（2 h）：2.0 × 1.4 × 0.9 m 內。舊木桌上鋪細沙，捏出山谷、溪床和村子的小模型。三條路線各是一個子網格 `Route_clear_silt`、`Route_restore_channel`、`Route_protect_nursery`；三個可拿起的小木牌 `Marker_*`（無字）；一塊小石頭 `Marker_Player`。C 做過的議事矮桌（`qingxi-water-report-c` C01）是 1.1 m 的小桌，可以放在旁邊當茶桌，這件要做成明顯不同的大沙盤。附空物件 `Socket_Pour`。並排比較：你的 B01、1.75 m 人形尺。

```
CR01  Three-view orthographic turnaround sheet of a village planning sand table, about 2.0 m wide, 1.4 m deep and 0.9 m tall, an old wooden table with a raised rim filled with fine sand shaped into a tiny valley, a dry creek bed, tiny houses and rice paddies, with three different thin routes marked by small pebbles and twigs and three small blank wooden markers stuck in the sand, made of old elm wood, fine sand, pebbles and twigs, showing hand-worn table edges, water stains, a mended leg, spilled sand on the rim, used in a village square meeting where villagers decide how to repair their creek. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```

**CR02 第 6 天的三件小東西**（2 h）：故事道具，靠近才看得到，近景要耐看。

| 件 | 尺寸 | 規格 |
|---|---|---|
| `Letter` 舊信 | 摺起 0.14 × 0.09 m | 泛黃的摺紙，有壓痕和一點灰；紙面**空白**（字由遊戲 UI 顯示）。另做打開的狀態一個網格 |
| `RoofTile` 屋後的瓦 | 0.28 × 0.2 m | 一片舊青瓦，背面有一小塊光滑的地方（字由 UI 疊上）；留青苔 |
| `Almanac` 曆書 | 0.2 × 0.13 × 0.02 m | 線裝舊書，封面無字，掛繩可掛牆 |

```
CR02  Three-view orthographic turnaround sheet of a set of three small old household objects laid out together: a folded yellowed paper letter about 0.14 m long, an old curved blue-grey roof tile about 0.28 m long with a small smooth patch on its back, and a thin thread-bound almanac about 0.2 m tall with a hanging loop and a blank cover, made of aged paper, fired clay and cotton thread, showing dust, crease marks, moss on the tile, corners softened by years of handling, completely blank with no writing, used as keepsakes found in an empty old house in a mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.
```

## 4. 第二段・第 7 天：修水路（23 h）

### 玩法（15 h）

一整段工地：舊水路旁邊，幾位村民一起做。三種工作**順序自由**，做完第 1 節規定的數量就完工；完整做完約 **8–12 分鐘**，可以中途離開，回來接著做（狀態要能序列化給核心組存）。

**清淤**（你的 B08 清淤篩）
- 用鏟子把泥鏟進篩子，手機和滑鼠都是**拖曳**，一鏟一鏟往外撥；一處要 5–8 鏟。
- 泥少到一定程度，舊槽的石頭露出來。**其中幾處石頭上有很淺的舊刻紋**（`_Pattern` 材質參數），不是字、沒有提示、不能互動，看到就看到。
- 手感重點：泥要有重量，撥開時有濕土聲和水滲出來。

**砌石**（你的 B07 補石）
- 看裂口，從料堆選一塊形狀對的石頭（3 種 B07 變體），放上去轉到合適角度。
- 按下定位時算**貼合度**（角度差和接口差）：貼得越好縫越小。貼不好也能完工，只是接縫比較大，村民幫忙補一道灰（`_Mortar` 參數，看得出是補過的）。不扣東西、不失敗。

**接渠**（你的 `waterworks-core`）
- 沿用導水規則和錯接說明：把段件放進槽位，接不上會說差幾公分、怎麼修，可撤回。
- 依選的方法載入不同的棋盤（寫在 `creek-repair-v1.json`，至少三種，引用你 `board.json` 的格式）。每種都至少有兩種接法能完工。
- 工地版**不做**成本和線索不足的判斷：這些在村會已經決定了，工人只管接。

**一起做的感覺（重要）**
- 4 個村民格位框在工地上做事（先用膠囊體和循環動作），玩家做到一定進度時他們移動到下一處。
- 進度到 25／50／75／100% 各發一次 `creek.workBeat { percent, method }`，核心組掛閒聊。其中一句固定：「以前這條溪是從地底下冒上來的，冬天都不結冰。」
- 工地的樣子跟著進度改變：泥堆變大、新石頭變多、茶水桶旁邊的人變多。

規則程式測試至少涵蓋：
1. 三種方法的工作量和 `waterline.json` 對得上；
2. 順序自由，任何順序都能完工；
3. 貼合度計算、貼不好仍算完成；
4. 接渠接法至少兩種能完工、錯接有說明；
5. 存檔後還原，進度一樣；
6. 重複完成不重複發事件。

事件：`creek.workBeat`、`creek.workCompleted { method, layout, patches, fitAverage, durationSeconds }`（`layout`、`patches` 格式照你的 `CONTRACT.md`，核心組接 `waterworks-commit`）。

### 模型（8 h）

**CR03 工地料堆**（3 h）：石料堆、木料架、泥堆各 3 個階段（少／中／多）；石料堆 2.0 × 1.5 × 1.0 m 內，木料架 2.5 × 1.0 × 1.2 m 內，泥堆 2.0 × 2.0 × 0.8 m 內。階段做成不同網格，同一檔案。泥堆是挖出來堆在岸上的廢土，和 A 的泥沙洲 A04（在河道裡）不同。並排比較：你的 B11 材料推車。

```
CR03  Three-view orthographic turnaround sheet of a village construction yard set laid out together: a pile of rough-cut warm-grey granite blocks about 2.0 m wide and 1.0 m tall, a simple wooden rack of logs and planks about 2.5 m wide and 1.2 m tall, and a heap of wet dark creek silt about 2.0 m wide and 0.8 m tall with a wooden plank laid across it, made of granite, cedar logs, rope and wet mud, showing chisel marks, muddy footprints, a broken stone set aside, rope ties on the rack, used at a site where villagers repair an old water channel in a mountain valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.
```

**CR04 工具組**（2 h）：鏟（1.3 m）、畚箕（0.5 m）、木夯（1.1 m）、灰桶和抹刀（0.3 m）。木槌、鑿、繩不用做：C 的修渠工具箱 C07 已經有，直接擺進工地。每件獨立物件，附 `Socket_Hand`，核心組掛到人手上。並排比較：你的 B08 清淤篩、1.75 m 人形尺。

```
CR04  Three-view orthographic turnaround sheet of a set of old village earthwork tools laid out together: a long-handled iron spade about 1.3 m long, a woven bamboo dirt basket about 0.5 m wide, a heavy wooden tamper about 1.1 m long, and a small mortar bucket with a trowel, made of old ash wood, dark iron, split bamboo and hemp rope, showing mud on the blades, hand-polished grips, a handle mended with rope, used by villagers repairing a water channel. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.
```

**CR05 工地涼棚和茶水**（3 h）：讓大家休息的地方。涼棚 4 × 3 × 2.8 m 內（四根竹柱、一片帆布頂、一張長凳），另有獨立的茶水桶和幾個碗（可和 TI10 同款調子）。附 `_Collision`（柱子）。並排比較：你的 RK04 茶攤。

```
CR05  Three-view and three-quarter concept of a simple temporary work shelter beside a creek, about 4 m wide, 3 m deep and 2.8 m tall, made of four bamboo posts tied with hemp rope holding a patched canvas roof, with a rough wooden bench, a large wooden tea bucket with a ladle and a few clay bowls on a crate, showing sun-faded canvas, a newer patch, muddy post feet, towels hung on the rope, water: a nearly dry creek bed in the background with small puddles. Layout: one three-quarter view with the water, plus front, side and top orthographic views of the structure alone on a plain light warm-grey background, same scale.
```

## 5. 第三段・第 8 天：水回來（14 h）

### 玩法（8 h）

序章第一個小高光。**不用按得準、不會失敗**；重點是畫面和節奏。

1. 全村站在閘門旁（核心組演開場）。玩家走到閘門，**用力轉閘輪**（你的 B06）：按住或拖曳轉一圈半，閘板慢慢升起。
2. 水頭從閘門出發，沿著玩家修的路線往下走。水頭要看得見：前面是乾石頭，水頭一過變深色、變濕，浮著一點碎葉。
3. 玩家可以**跟著水走**，也可以站著看。水頭速度約 2.5 m/s，玩家跑得比它快，不會追丟。
4. 走到每一戶的分水小閘（CR09），閘自己打開，水流進那一戶的田，田從乾變濕（`_Wet` 參數從 0 到 1），村民格位框跑過去看。至少 5 戶。
5. 玩家可以蹲下**摸水**（互動）：出現一小句「水是溫的。」（句子 id，核心組可換），水面有極淡的水氣（`_Warm` 參數，要很淡，傍晚才明顯）。
6. 水走到終點，發事件，核心組接音樂高點和茶亭老人那一句。

**路線資料**：`creek-repair-v1.json` 裡每種方法一條 `flowRoute`，一串節點 `{ id, x, z, kind: "channel|gate|field|end" }`，座標用你的測試場景；核心組之後照它對到真實地圖。水面用你現成的 `_water` 模型加流動材質。

**規則測試**：三條路線都走得到所有 `field` 節點和 `end`；水頭時間只由距離決定（不用亂數）；重複開閘只觸發一次；還沒開閘時田不會變濕。

事件：`creek.flowStarted { method }`、`creek.flowReached { nodeId, kind, seconds }`（核心組拿來對音樂）、`creek.waterTouched`、`creek.flowCompleted { method }`。

錄影：三種方法各一段，從轉閘輪到水走到終點。

### 模型（6 h）

**CR06 土堤木樁護岸**（1.5 h，`clear_silt`）、**CR08 竹木渡槽**（2 h，`protect_nursery`）：各做 2 m 長的**可拼接直段**和一個彎段，接口尺寸和你的 B02／B03 相同（每段 1 m 為單位，CR08 另加 0.8–2.5 m 高的支架 3 種）。水面分開成 `_water`。`restore_channel` 不做新模型，用你現成的 B02 系列加 B07 補石，只新增材料參數 `_Fresh`（0–1，新補的石頭顏色偏淺、沒有苔）。完工後村子看得出選了哪一種。並排比較：同一張圖放你的 B02 和這兩件。

**CR07 溪邊慶祝擺設**（1.5 h）：水回來那天全村圍在溪邊。一張 3 × 0.8 × 0.8 m 的拼湊長桌（幾塊不同的舊木板）、一串 6 m 長的紙燈（每盞獨立發光材質，`_Lit` 0–1）、兩根掛燈竹竿、幾個酒罈和一籃果子。

```
CR06  Three-view and three-quarter concept of a repaired earthen water channel with low packed-earth banks held in place by rows of short wooden stakes woven with willow branches, a straight section 2 m long and 1 m wide, made of dark packed earth, weathered stakes and woven willow, with details: young grass on the banks, a muddy footprint, a few old stones of the former channel showing through, water: clear turquoise water flowing gently, pebbles visible in the shallows. Layout: one three-quarter view with the water, plus front, side and top orthographic views of the structure alone on a plain light warm-grey background, same scale.

CR08  Three-view and three-quarter concept of a raised rustic flume carrying water above the ground, a straight section 2 m long and 0.6 m wide, made of a split-bamboo and cedar plank trough on A-frame wooden trestles tied with hemp rope, 1.5 m above the ground, with details: small drips between planks, rope lashings, a patched section, moss starting at the trestle feet, water: clear turquoise water running along the trough with a few drops falling. Layout: one three-quarter view with the water, plus front, side and top orthographic views of the structure alone on a plain light warm-grey background, same scale.
```

```
CR07  Three-view orthographic turnaround sheet of a village creek-side celebration set laid out together: a long patchwork table about 3 m long made of several mismatched old planks, a 6 m string of small round paper lanterns hung between two bamboo poles, a few clay wine jars and a basket of fruit, made of old timber, split bamboo, mulberry paper, glazed clay and hemp rope, showing uneven plank edges, a mended lantern, spilled water rings on the table, used when a whole village gathers to celebrate the return of their creek. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.
```

**CR09 每戶分水小閘**（1 h）：0.8 × 0.5 × 0.9 m 內。小石框加一片木閘板，閘板是獨立物件 `Gate`，往上開 0.3 m；做 2 種，差別看得出是不同人家修的（一種繩子綁、一種木榫）。和 CR06、CR08、B02 三種渠都接得上。這是給一戶田用的小閘，比你的工程閘板 B05 小得多。並排比較：你的 B05。

```
CR09  Three-view orthographic turnaround sheet of a small household water diversion gate, about 0.8 m wide, 0.5 m deep and 0.9 m tall, a low fitted stone frame holding a single sliding wooden board with a short lifting handle, made of warm-grey stone, old cedar and hemp rope, showing water stains, a wet line, moss in the groove, a rope mended by hand, used where a village channel feeds water into one family's field. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```

## 6. 第四段・第 5 天：山城的攤位（10 h，只有模型）

第 5 天玩家第一次到山城，要覺得**人很多、東西很多、很好玩**。你的攤子一直做得很好，這三件交給你；NPC、對白和互動由核心組做。格位 `B_AmuletStall`、`B_NoodleStall`、`B_RenjianBoard`，由核心組放進山城。

**CR10 護身符攤**（3.5 h）：3.5 × 2 × 2.8 m 內。一個嘴很賤的小販賣「飛升護身符」的攤子，**看起來有點騙人又很熱鬧**：掛滿成串的黃色符紙（**無字**，只有抽象的硃砂紋）、俗氣的金色小葫蘆、一面歪掉的布幡（無字）。符紙做幾串獨立物件，可以在風中晃。並排比較：你的 `Market_HerbalStall`。

```
CR10  Three-view orthographic turnaround sheet of a gaudy little street stall selling lucky charms in a mountain city, about 3.5 m wide, 2 m deep and 2.8 m tall, a wooden cart-like stall with a crooked cloth banner and hundreds of hanging yellow paper charms in strings with abstract red swirl patterns (no letters, no text), rows of cheap gilded little gourds, tassels and tiny bells, made of painted old wood, yellow paper, red cotton and thin gilded tin, showing peeling gold paint, a wobbly leg propped on a brick, a shop-worn cushion, cheerful clutter, a slightly shady salesman's stall. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```

**CR11 麵攤**（4 h）：4.5 × 3.5 × 2.8 m 內。爐灶、大鍋（蒸氣掛點 `Socket_Steam`）、案板、一張方桌兩條長凳、遮雨棚。**碗要獨立**：做一個麵碗網格，有「滿」「空」兩個狀態，核心組會在桌上疊五個空碗，再推一碗滿的給一個小孩，所以碗的大小要在鏡頭裡看得清楚。附 `_Collision`。並排比較：你的 RK04 茶攤。

```
CR11  Architectural concept of a small noodle stall in a mountain city street, footprint about 4.5 m wide and 3.5 m deep, 2.8 m high, a bamboo and timber lean-to with a patched canvas awning, a brick stove with a big steaming iron pot, a floured chopping board with fresh noodles and hanging ladles, one square wooden table with two long benches, details: stacks of large coarse ceramic noodle bowls, chopsticks in a bamboo cup, a bench with one short leg propped up, a cloth sign without text, weathering: smoke-darkened beams, grease stains, worn table top. Layout: one three-quarter view from slightly above at eye height of a person, plus front, side and back orthographic views on the same sheet at the same scale, plain light warm-grey background, even soft lighting, building only (no landscape around it except a small ground patch).
```

**CR12 人間榜告示欄**（2.5 h）：3 × 0.6 × 2.8 m 內。比村子的告示牌大、比較正式、有人氣。上面貼**一張張空白的榜單紙條**（每張是獨立物件 `Slip_01..12`，字由遊戲 UI 疊上），榜首那張最舊、邊角最捲；下面有人留下的爛茶杯、磨亮的欄杆。並排比較：你的 `Plaza_NoticeBoard`。

```
CR12  Three-view orthographic turnaround sheet of a large public ranking notice board in a mountain city, about 3 m wide, 0.6 m deep and 2.8 m tall, a timber frame with a small tiled roof and a wide wooden backing covered in columns of blank paper slips (completely blank, no letters, no text), the top slip much older and curling at the corners, a worn wooden railing in front where people lean, made of dark old timber, blue-grey tiles, yellowed paper and iron nails, showing layers of old torn paper, nail holes, a forgotten tea cup on the railing, hand-polished rail, used in a busy street where people argue about who is the strongest. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```

## 7. 你會用到的現成東西

全部已經在 main 上，**不用等任何人**：

- 你自己的：`art/exports/qingxi-waterworks-b`（B01–B12）、`tools/qingxi-waterworks-b`（規則、棋盤、`CONTRACT.md`）、`art/exports/harvest-market-b`。
- 參考比對用：`art/exports/qingxi-day34-c`（斷流石壩）、`art/exports/territory-backyard-a`（靈田，田的濕土狀態）。
- **直接拿來擺工地，不要重做**：`art/exports/qingxi-water-report-c` 的水桶組 C03、扁擔 C04、田邊濕度木牌 C05、施工布旗 C06、修渠工具箱 C07；`art/exports/qingxi-waterhead-a` 的泥沙洲 A04；你的材料推車 B11。

村民、NPC 都用膠囊體；真實地圖的格位都由核心組對，你用自己的測試場景就好。

## 8. 交件

每一段（可各開一張 PR，從最新 main 開分支），照 PR 範本附：

- 這段的規則、測試（`npm test` 全過）、Unity 元件、測試場景；
- 模型的三視圖、審圖、`model_info.json`；
- 錄影、手感問題至少 3 點；
- 實際時數（大概就好）、還沒做完的地方（老實寫）；
- 超出工作包的改動（像上次的分揀獎勵那樣的好點子很歡迎，寫清楚，只加不扣、不改第 1 節的取捨）。

## 9. 不要做

- 不要做失敗結局、材料不足卡關、賣東西給村民；不要讓三種方法分高下。
- 不要做對白正文、人物模型、音樂、伺服器（核心組）。
- 不要解釋舊刻紋、溫的水、村民說的舊事；只讓玩家看到。
- 不要在任何模型上刻字、寫字、寫數字。
