# A｜鄭翔元 John（約 28 小時）：第 2 天的第一掌和開田

> 2026-11-02，Claude Code（核心組）依 z1nnz 指示撰寫，取代先前草稿的釣魚方案（釣魚不在遊戲安排裡）。
> 故事依據：[第一章故事・詳細版](../../story/第一章故事-詳細版-上.md)「第二天：田和第一掌」。玩法依據：[總覽](../../承天-總覽.md)第五、六節（領地、生活技藝、戰鬥）。
> 不要重做的東西見[總表](00-overview.md)第 3 節。美術標準和提示詞照 [美術風格指南](../art-style-guide-v1.md)。

## 0. 為什麼是這兩件

故事裡的第 2 天有兩件事，遊戲都還沒有：

| 故事寫的 | 遊戲現在 | 缺口 |
|---|---|---|
| 沈岳教第一掌，有節奏條，玩家怎麼打都只有「啪」，沈岳那一掌是「咚」；他說「急什麼，這一掌，有人打了三年。」 | 你的練體課（#59）有站樁、格擋、閃避，**沒有出掌** | 這一掌會跟著玩家很久，之後的故事還會問起 |
| 開田：拔草、撿石頭、翻土、撒種，看著荒地變成整齊的田 | 走到田邊按 F 就種好（`QingxiTerritoryFields`） | 種田是一直都有的玩法，第一次卻沒有手感 |

| 項目 | 時數 |
|---|---:|
| 第一掌：規則、測試 | 4 |
| 第一掌：Unity、接進練體課、家裡的木樁 | 6 |
| 第一掌：錄影、手感調整 | 2 |
| 開田：規則、測試 | 2 |
| 開田：Unity | 5 |
| 開田：錄影、手感調整 | 1 |
| TY11 舊木樁 | 2 |
| TY12 荒地 | 2 |
| TY05 練功地面 | 2 |
| FP01 溪邊烤魚道具 | 1 |
| 審圖、整理 | 1 |
| **合計** | **28** |

## 1. 第一掌（12 小時）

### 1.1 手感

沈岳：「腰沉下去，手不要急。不是用手打，是用腳、用腰，最後才是手。」所以一掌是**三拍**：

1. **腳**：按下，角色沉腰；
2. **腰**：節奏條走到第二格時按；
3. **手**：走到第三格時按，出掌。

每一拍各有判定（`good`、`early`、`late`），三拍都 `good` 算一下**好掌**。節奏條不要太花，重點是聲音和木樁的反應。

**聲音分兩種，是這個玩法的靈魂：**

| 聲音 | 什麼時候 | 畫面 |
|---|---|---|
| **啪**（很輕） | 平常 | 手發紅、木樁幾乎不動 |
| **咚**（很悶、很沉，整根木樁從裡面震一下） | 累積夠了以後才打得出來 | 木樁上的灰全部震下來、鏡頭輕震 |

### 1.2 什麼時候打得出「咚」

第 2 天那堂課**不管怎麼打都是「啪」**，這是故事要的，不是玩家的錯。旁邊的新人打出「咚」由核心組演。

之後每天可以在村裡的練功場或家裡的舊木樁練。規則（寫進 `packages/content/first-palm-v1.json`，數字由核心組之後調）：

| 欄位 | 預設 | 說明 |
|---|---|---|
| `lessonAlwaysPa` | `true` | 第 2 天的課一律是「啪」 |
| `goodStrikesForDong` | 300 | 累積多少下好掌才打得出「咚」 |
| `dailyCountedStrikes` | 30 | 每天最多算幾下，多打不算，不用硬刷 |
| `paTones` | 5 段 | 累積越多，「啪」越沉一點（5 段音高和木樁反應），玩家感覺得到在進步，但介面不顯示數字 |
| `beatWindowSeconds` | 0.18 | 每一拍的判定時間 |

照預設，最快要第 12 天左右才打得出來，也就是**新手十天內通常打不出來**。這是刻意的：之後問玩家「打出來了沒」，兩種答案都要成立。沒上線不扣、打不好不扣，也不能用任何東西加速。

第一次打出「咚」只發生一次：全場安靜一拍，灰震下來，沒有獎勵提示、沒有成就彈窗。

### 1.3 接進現有的東西

- **練體課**：在你的 `body-training-lesson-1.json` 三段之後加第四段 `palm`：沈岳示範一次「咚」，玩家打滿 20 下結束，**不影響「練體入門」的結果**。
- **家裡**：掛在 TY11 舊木樁上，格位 `TY_Practice` 旁。
- **給戰鬥用**：這是戰鬥教學。規則程式提供 `PalmStrike` 的結果（`quality`、`sound`），核心組之後接進戰鬥；這包不做戰鬥本身。

### 1.4 規則和交件

純邏輯放 `tools/first-palm/`，測試放 `tests/first-palm.test.ts`（`npm test` 全過）。Unity 放 `apps/game/Assets/YunJing/Runtime/FirstPalm/`。手機和鍵盤滑鼠都能玩，觸控按鈕至少 88 × 88 px。

測試至少涵蓋：第 2 天的課永遠是「啪」；三拍判定邊界；每日上限和跨日；累積到門檻才「咚」，第一次事件只發一次；打不好不倒扣；存檔還原一樣。

事件：`palm.struck { quality, sound }`、`palm.firstDong { strikes }`（**一定要能存**，之後的故事會問）。

交：`first-palm-v1.json`、規則＋測試、元件、測試場景、錄影（課堂一段、把累積調到門檻前打出第一聲「咚」一段）、手感問題至少 3 點。

## 2. 開田（8 小時）

第一次把荒地變成自己的田，要有成就感，2–3 分鐘。在格位 `TY_Field_1`（2.6 × 3.4 m）。四步，**不會失敗**：

1. **拔草**：一叢一叢按住拉起。和 B 的拔靈草不一樣：這裡不分等級，拔起來有土噴出來就很爽。
2. **撿石頭**：拖到田邊，堆起來。大石頭要拖久一點。
3. **翻土**：沿著壟一道一道劃過，土從乾變深色，留下壟溝。
4. **撒種**：手勢撒開，種子落在壟上；用現有的 `qingling-seed`。

畫面要從 TY12 荒地慢慢變成你的 TY01 田床。**第一塊田走完整四步**；之後的田只要撒種。

資料放 `packages/content/field-opening-v1.json`（草幾叢、石頭幾顆、壟幾道），規則放 `tools/field-opening/`，測試放 `tests/field-opening.test.ts`：四步順序、全部清完才算完成、中途離開能接著做、第二塊田跳過前三步、完成事件只發一次。

元件 `QingxiFieldOpening`，放你的資料夾，先在測試場景跑；**不要改** `QingxiTerritoryFields`，完成時發 `field.opened { fieldId }`，核心組接種植伺服器。

交：資料、規則＋測試、元件、錄影、手感問題至少 3 點。

## 3. 模型（7 小時）

共同規則：每件先做 AI 三視圖：提示詞整段貼上，**後面接風格指南 5.2**，負面欄貼 **5.3**，至少出 4 張挑最好的，存 `art/references/<編號>/`。品質優先，不要求降面數；三級 LOD 同一檔案；原點在腳印中心、底部高度 0、不附地面底板；擋人的附 `_Collision`；附 `model_info.json`；四視圖加 1.75 m 人形尺，再加一張並排比較圖。**不刻字、不寫字。** 匯出放 `art/exports/first-palm-a/`。

### TY11 舊木樁（2 h）

新人分到的舊屋後面有一根練掌的木樁，是很久以前有人用的。上面有**三道磨痕，第三道比另外兩道深得多，深到木頭裂開**。不解釋是誰留的。高 1.6 m、直徑 0.3 m。附空物件 `Socket_Dust`（灰震下來的位置）。一根骨讓它受力輕晃。並排比較：你的 A12 藤靶。

```
TY11  Three-view orthographic turnaround sheet of an old wooden palm-striking training post standing behind a village house, about 0.3 m wide and 1.6 m tall, a single thick weathered post of dark elm wrapped with a few turns of frayed hemp at chest height, with three horizontal worn grooves from years of striking, the third groove much deeper than the other two and split open with a long crack, made of old elm and hemp rope, showing dust settled on the top, hand-polished wood around the grooves, moss at the foot, no carving, no letters, no text, used by someone long ago who practised the same strike for years. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```

### TY12 荒地（2 h）

開田前的樣子，尺寸和 TY01 相同（2.6 × 3.4 m）。雜草叢 3 種、石頭 3 種（小、中、大，都是獨立物件，玩法會一個個拿走），底下一片乾硬的地面。翻土的深色用材質參數 `_Tilled`（0–1）。並排比較：你的 TY01。

```
TY12  Three-view orthographic turnaround sheet of a small overgrown patch of abandoned land about to be cleared for a herb field, about 2.6 m wide, 3.4 m long and 0.4 m tall, dry cracked earth covered with clumps of wild grass and weeds and scattered stones of three sizes, made of dry soil, grass, weeds and warm-grey fieldstones, showing an old rotten stake, a faint trace of old furrows, roots showing in the cracks, used behind an old house given to a newcomer in a mountain valley village. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```

### TY05 練功地面（2 h）

10/31 工作包就排過，格位 `TY_Practice` 到現在還空著。2 種石板排法，中間被踩舊磨亮，縫裡長草，不高出地面 2 cm。規格照 [10/31 A 包](../2026-10-31/01-A-territory-backyard.md)，提示詞用風格指南 5.10 的貼圖骨架加網格。並排比較：TY11。

### FP01 溪邊烤魚道具（1 h）

第 9 天六個人在溪邊烤魚的場景道具。**只有道具，沒有玩法**，演出由核心組做。小石圍的火堆、幾根插地的竹籤、烤好的魚（一種就好，0.25 m，可拿在手上，附 `Socket_Hand`）。

```
FP01  Three-view orthographic turnaround sheet of a small creek-side campfire set laid out together: a little ring of round river stones with burning driftwood about 0.7 m wide, several bamboo skewers stuck in the gravel around it, and one grilled river fish about 0.25 m long on a skewer, golden-brown with charred fin tips, made of river stone, driftwood, bamboo and fish, showing soot on the stones, ash on the gravel, a crooked skewer, made by a few teenagers on a creek bank. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background.
```

## 4. 交件

可分兩張 PR（第一掌＋TY11 一張；開田＋TY12、TY05、FP01 一張），從最新 main 開分支。附三視圖、審圖、錄影、實際時數、還沒做完的地方。不改主場景、`QingxiHud`、`QingxiTerritoryFields`、伺服器、別人的資料夾；人物和對白由核心組做。不要做釣魚。
