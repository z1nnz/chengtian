# A｜40 小時：風雨橋、戲台、議事堂、坊市布棚

> 交給 Johnnnny0823（John）。2026-11-11，Claude Code 依 z1nnz 指示撰寫：「你覺得建議他們做的，直接丟給他們新的工作包」。大小由核心組定為 40 小時。
> **接在 11/08 那份 80 小時後面做**（還沒交的 SF04–06、ST01–06、MC02）。那份做完再開始這份。
> 這一輪**只做模型**，不做玩法、人物、文字。

---

## 0. 先讀

- **世界完成清單**：`docs/execution/world-blueprint/完成清單.md`（在分支 `game/core-1110-hud-redesign`）第七節。這包是 11/11 實機審查後追加的。
- 標註規則：[`docs/standards/labeling-v1.md`](../../standards/labeling-v1.md)
- 交件規則與提示詞固定段：照 [11/07 B 包](../2026-11-07/B-104h-tea-wheel-and-mountain-way.md) 第 1 節與附錄（Layout 段、建築 Layout 段、5.2、5.3）
- 風格色票：[`docs/art/modeling-style-spec-v1.md`](../../art/modeling-style-spec-v1.md) 第 11 節
- 畫質分級：`docs/standards/quality-tiers-v1.md` 第 4 節

## 1. 為什麼做這包

11/11 進遊戲看青溪村，村子沒有「大家會聚在一起的地方」：廣場是一片空地，過西溪沒有一座讓人記得的橋，坊市的攤位太素。你的山城建築（MC01、TX04）做得好，這包請你回到河谷，做三座村子的公共建築。

這三座是**河谷的村子**，不是山城：用石木、深色舊木、黛瓦，樸素，不要山城的灰白花崗石和銅件。

規則：

1. **commit 用你自己的 GitHub 帳號**，不用 z1nnz，也不掛 Claude Code 或其他 AI 的名字。
2. **Unity 檢查用 6000.3.28f1**。
3. **CB01 先交一件樣品**開在 PR 上。沒等到回覆也可以繼續做其他件。
4. `model_info.json` 照 11/08 包的寫法：每個 LOD 的三角面、物件數與材質數、每張貼圖解析度。
5. 核心組負責擺進世界。**不改主場景、不改區塊 JSON。**

## 2. 要交的東西

| ID | 東西 | 尺寸上限（w×d×h） | 放在哪 | 重點 | 時數 |
|---|---|---|---|---|---:|
| CB01 | 風雨橋（有屋頂的木廊橋） | 16 × 4.5 × 6.5 m | A3 西溪，村子往水磨坊的路上 | 兩座石墩、木梁橋身、上面一道長廊屋頂，兩側木欄和一排坐凳。**這是西溪的地標**，從村口 80 m 外要認得出輪廓。橋面可走，淨寬至少 2.4 m、淨高 2.6 m。**和 WM07 石拱橋、MC02 索橋不同** | 13 |
| OS01 | 村戲台 | 8 × 7 × 7 m | A1 廣場北側 | 架高 1.2 m 的木造戲台，三面開敞，後面一道木板牆和兩側小門，歇山瓦頂。台上空著，不放人和道具。側面一道木階可以走上去 | 10 |
| MH01 | 議事堂（村裡議事和議水的地方） | 11 × 8 × 6.5 m | A1 廣場旁 | 三開間的單層廳堂，正面敞開或一排可拆的木板門，前有三級石階和簷廊。廳內留空（放得下一張 2 × 1 m 的議水桌和幾條長凳，桌凳不用做）。要比民居大一號、穩重，但不華麗。門額留 `Socket_Plaque`，**不寫字** | 11 |
| AW01 | 坊市布棚（3 種：單坡、雙坡、撐竿斜拉） | 每頂 3 × 2.5 × 2.6 m | A1 坊市 | 竹竿或木竿撐起的舊布棚，布有補丁和下垂的弧度，三種顏色偏舊的靛藍、赭、米白。只做棚，不做攤位。**和 ST05 空白布幌不同**：這是遮陽的頂 | 4 |
| 全包檢查 | 並排圖 | — | — | CB01、OS01、MH01 各一張 1.7 m 人眼圖；三座和一間 VL 民居並排一張，看大小關係 | 2 |
| **合計** | | | | | **40** |

## 3. 風格與驗收

- **河谷語言**：石木、深色舊木、黛瓦 `#3A4048`。放在 VL、VH 民居旁邊要像同一個村。
- **不要日式、歐式**：不要鳥居感、能舞台感、町屋感；#80 的審查意見可以參考。
- 每件交齊：三視圖、灰模、線框、LOD 對照、人形尺。
- 能走的地方（CB01 橋面、OS01 台面和木階、MH01 簷廊和廳內）附 1.75 m 膠囊走過的檢查。
- 逐件標 Exported／Imported／Visually Verified／In-game Verified，沒驗的寫未驗。

## 4. 分支與 PR

| 批 | 分支 | PR 標題 |
|---|---|---|
| A | `art/a-1111-cb-covered-bridge` | `【A】11/11 CB01：西溪風雨橋` |
| B | `art/a-1111-os-stage-and-hall` | `【A】11/11 OS01、MH01、AW01：戲台、議事堂、坊市布棚` |

素材資料夾 README 開頭照標註規則第 5 節。

## 5. 不要做

- 不做已有的：WM07 石橋、MC02 索橋、TE05 觀景亭、RK03 茶亭、SG04 歇腳石亭、TX04、MC01、ST01–06、SF01–06。
- 不做 Josh 這輪的 CW、WE、XB、GN、AN；不做 Eli 這輪的 VG。
- 不做等故事的：測資台、接引棚、古林碑。
- 不做人物、文字、玩法、主場景；不開新的網頁版頁面。

## 6. 物件句（正面提示 = 物件句 + 建築 Layout 段 + 5.2；負面用 5.3，另加下面這句）

```text
not Japanese, no torii, no Noh stage, no noren, no round paper lanterns, not Tudor half-timbering, no bright teal roof, no gold ornament, no glossy plastic look
```

**CB01**
```text
Three-view orthographic turnaround sheet of a rural Chinese covered timber bridge over a small river, about 16 m long, 4.5 m wide and 6.5 m tall, two rough stone piers, heavy timber beams carrying a plank deck, a long open gallery roof of dark grey clay tiles along the whole bridge, plain wooden railings and a row of built-in benches on both sides, old weathered dark wood, moss on the piers, modest village craftsmanship, no people, no writing.
```

**OS01**
```text
Three-view orthographic turnaround sheet of a small rural Chinese village opera stage, about 8 m wide, 7 m deep and 7 m tall, a timber platform raised about 1.2 m on stone footings, open on three sides, a plank back wall with two small side doors, a hip-and-gable dark grey tile roof with restrained upturned eaves, one wooden side stair, completely empty stage, old weathered dark wood, no people, no props, no writing.
```

**MH01**
```text
Three-view orthographic turnaround sheet of a modest rural Chinese village meeting hall, about 11 m wide, 8 m deep and 6.5 m tall, a single-storey three-bay timber hall on a low stone platform with three stone steps, a front veranda under deep eaves, removable plank doors across the open front, plaster side walls on stone footings, dark grey clay tile gable roof, a blank wooden plaque board above the entrance, sturdy and plain, larger than a farmhouse but not grand, no people, no writing.
```

**AW01**
```text
Three-view orthographic turnaround sheet of three rustic Chinese market cloth awnings, each about 3 m wide, 2.5 m deep and 2.6 m tall, old patched cloth sagging between bamboo and wooden poles with guy ropes, shown as three types: single slope, double slope, and a slanted prop-pole lean-to, in faded indigo, ochre and off-white, no stall, no goods, no writing.
```

---

有問題直接問；寫不清楚的地方先照最保守的做法做，寫進 PR。
