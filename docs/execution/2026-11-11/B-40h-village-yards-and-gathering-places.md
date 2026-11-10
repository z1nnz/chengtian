# B｜40 小時：院牆院門、水井、石板橋、穀倉、牛棚

> 交給 joshsu54（Josh）。2026-11-11，Claude Code 依 z1nnz 指示撰寫：「你覺得建議他們做的，直接丟給他們新的工作包」。大小由核心組定為 40 小時。
> 這一包**接在 11/09 那份 112 小時後面做**，先把那份做完。
> 這一輪**只做模型**，不做玩法、人物、文字。

---

## 0. 先讀

- **世界完成清單**：`docs/execution/world-blueprint/完成清單.md`（在分支 `game/core-1110-hud-redesign`）第七節。這包是 11/11 實機審查後追加的。
- 標註規則：[`docs/standards/labeling-v1.md`](../../standards/labeling-v1.md)
- 交件規則與提示詞固定段：照 [11/07 你的包](../2026-11-07/B-104h-tea-wheel-and-mountain-way.md) 第 1 節與附錄（單件 Layout 段、建築 Layout 段、5.2、5.3）
- 風格色票：[`docs/art/modeling-style-spec-v1.md`](../../art/modeling-style-spec-v1.md) 第 11 節
- 畫質分級：`docs/standards/quality-tiers-v1.md` 第 4 節

## 1. 為什麼做這包

11/11 進遊戲看青溪村，問題是「空」：房子散在草地上，沒有院子的邊界，村子沒有大家會聚在一起的地方，過溪也沒有東西。這包補這三個洞。

規則和 11/09 那包相同，另外注意：

1. **commit 用你自己的 GitHub 帳號**，不用 z1nnz，也不掛 Claude Code 或其他 AI 的名字。
2. **Unity 檢查用 6000.3.28f1**（main 已升級，11/09 包裡寫的 82f1 作廢）。
3. 核心組負責擺進世界。**不改主場景、不改區塊 JSON。**

## 2. 要交的東西

| ID | 東西 | 尺寸上限（w×d×h） | 放在哪 | 重點 | 時數 |
|---|---|---|---|---|---:|
| CW01 | 夯土院牆組（直段 4 m、轉角、端頭、塌了一角的缺口段） | 每段 4 × 0.5 × 1.8 m | A1 每戶 | 夯土牆身、石腳、牆頂一排黛瓦壓頂。四件要能首尾相接，接縫對齊（`Socket_A`、`Socket_B`）。**和 R01 乾砌石牆、R02 竹籬不同**：這是住家的院牆，較高、較整齊 | 8 |
| CW02 | 院門（2 種：開著、關著） | 2.4 × 1.2 × 2.8 m | A1 每戶 | 木門框加小瓦頂，兩扇舊木門，門檻石。兩側能直接接 CW01。門扇做成獨立物件（`Detail_DoorL`、`Detail_DoorR`），之後才能開關 | 5 |
| WE01 | 村中水井與井亭 | 3.5 × 3.5 × 3.6 m | A1 村心 | 還在用的石砌井圈、木轆轤和繩、一個木桶，上面四柱小瓦頂亭。井邊地面有踩實和濺濕的痕跡。**和 D3_DryWell 枯井不同**：這口井有人天天用 | 7 |
| XB01 | 石板橋與溪中踏石 | 橋 6 × 1.8 × 1.2 m；踏石一組 5 顆 | A1 往 A3 | 兩三塊長石板架在石墩上的矮橋，沒有欄杆。另交一組 5 顆頂面磨平的踏石。**和 WM07 石拱橋、QX_CreekSteppingPlank 木板不同** | 6 |
| GN01 | 穀倉（架高的糧囤） | 4 × 4 × 5 m | A1 村邊、A6 | 圓形或方形的木造糧倉，架在石礎上離地約 0.6 m，草頂或瓦頂，一道短木梯。遠看要和民居的輪廓明顯不同 | 7 |
| AN01 | 牛棚與食槽 | 6 × 4 × 3.2 m | A1 村邊 | 三面開放的木棚、草頂、木欄、一個長木食槽、地上鋪乾草。**不做牛** | 5 |
| 全包檢查 | 村子樣張 | — | — | 用 CW01、CW02 把一間 VL 或 VH 圍成院子，旁邊放 WE01，附 1.75 m 人形尺和 1.7 m 人眼圖各一張 | 2 |
| **合計** | | | | | **40** |

## 3. 風格與驗收

- 全部用**河谷語言**：石木、深色舊木、黛瓦 `#3A4048`、夯土暖黃灰。放在 VL、VH 旁邊要像同一個村。
- **不要日式、歐式**。
- 每件照 11/07 包第 1 節交齊：三視圖、灰模、線框、LOD 對照、人形尺。
- 能走的地方（XB01 橋面和踏石、WE01 亭內、AN01 棚內、CW02 門洞）要附 1.75 m 膠囊走過的檢查。CW02 開著的門洞淨寬至少 1.2 m。
- 逐件標 Exported／Imported／Visually Verified／In-game Verified，沒驗的寫未驗。

## 4. 分支與 PR

| 批 | 分支 | PR 標題 |
|---|---|---|
| A | `art/b-1111-cw-yard-walls-and-well` | `【B】11/11 CW01–02、WE01、XB01：院牆院門、水井、石板橋` |
| B | `art/b-1111-gn-granary-and-shed` | `【B】11/11 GN01、AN01：穀倉與牛棚` |

素材資料夾 README 開頭照標註規則第 5 節。

## 5. 不要做

- 不做已有的：R01 乾砌石牆、R02 竹籬、D3_DryWell 枯井、WM07 石橋、QX_CreekSteppingPlank、A2_OverturnedCart、VL01–05、你 11/09 包裡的全部項目。
- 不做 Eli 這輪的 VG（菜畦、瓜架、晾衣竿、草垛、板車、扁擔籮筐、石磨、石槽）；不做 John 這輪的 CB、OS、MH、AW（風雨橋、戲台、議事堂、布棚）。
- 不做人物、動物、文字、玩法、主場景。

## 6. 物件句（正面提示 = 物件句 + 固定 Layout 段〔建築用建築 Layout 段〕 + 5.2；負面用 5.3，另加下面這句）

```text
not Japanese machiya, no noren, no round paper lanterns, not Tudor half-timbering, no bright teal roof, no glossy plastic look
```

**CW01**
```text
Three-view orthographic turnaround sheet of a modular rural Chinese courtyard wall set, each section about 4 m long, 0.5 m thick and 1.8 m tall, rammed earth wall body in warm yellow-grey on a rough stone footing, capped with a single row of dark grey clay tiles, shown as four pieces: a straight section, a corner, an end cap, and a section with one collapsed corner exposing the earth core, weathered and rain-streaked, no writing.
```

**CW02**
```text
Three-view orthographic turnaround sheet of a small rural Chinese courtyard gate, about 2.4 m wide, 1.2 m deep and 2.8 m tall, a plain timber door frame under a small dark grey tile roof, two old plank doors, a worn stone threshold, short rammed earth wall stubs on both sides, old weathered dark wood, shown in two versions: doors open and doors closed, no writing, no door god prints.
```

**WE01**
```text
Three-view orthographic turnaround sheet of a village well in daily use under a small pavilion, about 3.5 m wide, 3.5 m deep and 3.6 m tall, a round stone well ring, a wooden windlass with rope and one wooden bucket, four plain timber posts carrying a small dark grey tile roof, flat stone paving around the well worn smooth and darkened by water, no people, no writing.
```

**XB01**
```text
Three-view orthographic turnaround sheet of a low rural Chinese stone slab bridge, about 6 m long, 1.8 m wide and 1.2 m tall, two or three long rough-cut stone slabs resting on short stacked stone piers, no railings, edges worn round, moss near the waterline, shown together with a set of five flat-topped stepping stones of different sizes, no writing.
```

**GN01**
```text
Three-view orthographic turnaround sheet of a small raised rural Chinese granary, about 4 m wide, 4 m deep and 5 m tall, a timber plank storehouse standing on stone pad footings about 0.6 m above the ground, a thatched or dark tile roof with deep eaves, one small plank door and a short wooden ladder, old weathered wood, no writing.
```

**AN01**
```text
Three-view orthographic turnaround sheet of a rural Chinese cattle shed, about 6 m wide, 4 m deep and 3.2 m tall, open on three sides, rough timber posts and rails, a thatched lean-to roof, one long wooden feeding trough, dry straw on a packed earth floor, old weathered wood, no animals, no people, no writing.
```

---

有問題直接問；寫不清楚的地方先照最保守的做法做，寫進 PR。
