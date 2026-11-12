| 項目 | 內容 |
|---|---|
| 誰做的 | A（Johnnnny0823） |
| 工作包 | docs/execution/2026-11-11/A-40h-village-gathering-buildings.md |
| ID | CB01 西溪風雨橋（樣品；OS01、MH01、AW01 之後另開 PR） |
| 分支／PR | art/a-1111-cb-covered-bridge ／ #113 |
| 版本 | v001 |
| 狀態 | Exported；Imported：見「驗收紀錄」的 Unity 6000.3.28f1 檢查；Visually Verified：預覽圖；In-game Verified：未驗 |
| 素材來源 | 原創。建模腳本 `art/source/valley-commons-a/build_valley.py`，沿用 MC01（#80）的建模函式與 TX04（#90）的歇山屋頂函式；三視圖用 Codex CLI 生成，存 `art/references/CB01/` |

# 河谷公共建築：CB01 西溪風雨橋

西溪上的有頂木廊橋，是村子往水磨坊路上的地標。

![溪谷場景](../../previews/valley-commons-a/scene/CB01_scene_three_quarter.png)

## 做法（三視圖選 option 2）

- **橋墩**：兩座灰藍河石砌的橋墩，三層、往上略收。石塊大小不一，鑿面粗；下兩層較暗、長苔，層間有苔，墩頂鋪大石板。
- **橋身**：
  - 每座橋墩上兩層伸臂圓木，一層比一層往外伸。
  - 六根通長圓木主梁，上面橫鋪木板橋面，有幾塊換過的淺色板。
  - 兩側封邊板，兩端封頭板蓋住梁頭。
  - 每座橋墩兩側各一對斜撐，撐到外側主梁。
- **長廊**：
  - 每側 9 根木柱（柱間約 1.9 m），柱頂有額枋、雀替狀斜撐和橫向繫梁。
  - 柱外是木欄杆（扶手 0.95 m）。
  - 中間七開間柱內有一排長坐凳，兩端各留一開間當出入口。
- **屋頂**：
  - 一條連續的長廊屋頂，兩端歇山、屋角起翹，深灰瓦、一條條瓦壟。
  - 屋脊正中架一座小高頂（約 5.2 m 長），兩側是直條通風板，遠看是這座橋最好認的輪廓。
- **和其他橋不同**：WM07 是石拱橋、MC02 是鐵鏈索橋；這座是木構有頂廊橋。

## 河谷用色：新的共用貼圖

- **為什麼不用 MC01 的貼圖**：工作包規定河谷不用山城的灰白花崗石和銅件。所以新做一張 2048 共用貼圖 `art/textures/valley-commons-a/T_ValleyCommons_*`。
- **條帶排法**：和 MC01 共用貼圖完全相同，所以建模函式不用改，只換顏色。
- **顏色**：
  - **石**：灰藍河石（接近 VL 民居的石色），比山城花崗石暗、粗。
  - **木**：深色舊木，淋得到雨的地方偏灰。
  - **瓦**：深灰瓦，介於規格的 `#3A4048` 和 VL 民居的灰綠瓦之間。
  - **鐵件**：深色鐵，不用銅。
- **材質**：只有一個 `M_ValleyCommons_Trim`。OS01、MH01、AW01 也會用這張，四件可以合批。

## 原點與接法

- **原點**：橋的平面中心，z＝0 是橋墩底（溪床），−Y 是上游側。
- **橋面**：整段同高，在 +1.914 m（`model_info.json` 的 `deckTop_m`），沿 X 延伸。
- **兩岸接口**：`Socket_EndA`（x＝−8）、`Socket_EndB`（x＝+8）就是橋面兩端，在橋面高度上，接兩岸的路。
- **碰撞**：一個網格，含：
  - 橋面板；
  - 兩座橋墩；
  - 兩側 1.1 m 高的欄杆牆；
  - 坐凳、立柱；
  - 屋頂一塊（橋面上 3.0 m 起）。

## 數字

| ID | 尺寸 L×W×H（m） | 規格上限 | LOD0 / LOD1 / LOD2 三角面 | 物件 | 材質 | 貼圖 | 碰撞 |
|---|---|---|---|---|---|---|---|
| CB01 | 15.99 × 4.48 × 6.458 | 16 × 4.5 × 6.5 | 179,891 / 87,679 / 24,371 | 2 | 1 | 2048 × 4（Albedo、Normal、MetallicSmoothness、Emission） | 一個網格 |

- **可走空間**：
  - 淨寬：坐凳之間 2.58 m，規格至少 2.4 m；
  - 淨高：繫梁下 2.62 m，規格至少 2.6 m。
- **面數**：LOD0 大部分是一條條建出來的瓦壟和亂石。地標建築，`minTier` 是 low。
- **物件**：主體一個，`Detail_Moss`（苔，可整組關掉）一個。
- **交付格式**：FBX 內含 LOD0/1/2、`CB01_Collision`、兩個接口 empty。不帶切線，Unity 匯入時用 MikkTSpace 算。
- **效能**：不寫 FPS；手機未實測。

## 驗收紀錄

- **Blender 資產 QA**（blender-asset-qa `qa_check`，game profile，LOD0 單獨掃，z-fighting／懸空都有跑）：
  - 主體 errors＝0；苔＋主體合併檢查，懸空＝0。
  - 結果存 `art/source/valley-commons-a/qa_all.json`。
  - 苔單獨掃描會報懸空，因為每叢苔本來就是分開的小葉片。
- **FBX 回匯**：尺寸和建模時相同（誤差 0）。
- **Unity 6000.3.28f1**（`apps/game/Assets/YunJing/Editor/ValleyCommonsVerify.cs`）：26 項全部通過，報告在 `art/previews/valley-commons-a/unity/report.txt`。
  - 一般匯入檢查：尺寸、面數、物件、材質、接口位置、LODGroup、碰撞。
  - 橋面：沿中線每 25 cm 一條向下射線，63 條全部打到，和 +1.914 m 差 0 cm，相鄰兩點沒有台階。
  - 1.75 m 膠囊（半徑 0.35）從一端沿中線走到另一端，沒碰到任何東西。
  - 三個位置量：
    - 淨寬：坐凳之間 2.58 m；
    - 往上射線到屋頂碰撞 3.01 m（繫梁下 2.62 m）；
    - 1 m 高往兩側的射線都被欄杆擋住。
- **修過的問題**：
  - 亂石塊鑿面往內縮，留出縫而被判懸空：層與層改成重疊 3 cm，內核放大到每塊都碰得到，不留碎片小石塊。
  - 立柱和簷檁同寬，側面貼齊而閃爍。
  - 歇山屋角起翹讓幾根椽子離開檁條。
  - 頂上小屋頂太矮，封簷板高度變負數，整片翻面（拿掉，改用直條通風板）。
- **規格的「80 m 外認得出輪廓」**：見 `scene/CB01_silhouette_80m.png`。這是從 80 m 外、1.7 m 人眼高度看的 Blender 渲染，不是遊戲內截圖。

## 怎麼重跑

```
python tools/mountain-city-a/make_prompts_1111.py
python tools/mountain-city-a/gen_threeviews.py --prompts prompts_1111.json CB01
blender -b --factory-startup -P art/source/valley-commons-a/build_valley.py -- sheet CB01
blender -b --factory-startup -P art/source/valley-commons-a/qa_valley.py -- <絕對路徑 out.json> CB01
blender -b --factory-startup -P art/source/valley-commons-a/render_valley.py -- --out <repo 絕對路徑>/art/previews/valley-commons-a [--clay|--wire|--lod 1] CB01
blender -b --factory-startup -P art/source/valley-commons-a/scene_cb01.py -- [--clay]
python art/source/valley-commons-a/sheets_valley.py CB01
Unity -batchmode -quit -projectPath apps/game -executeMethod YunJing.Editor.ValleyCommonsVerify.Run -logFile <log>
```

## 預覽

`art/previews/valley-commons-a/`：

- **CB01 單件**：
  - 3/4、側、正、俯視（含 1.75 m 人形尺）；
  - 灰模、線框、LOD1；
  - `CB01_ref_vs_model.jpg`：參考圖對模型；
  - `CB01_LOD0_vs_LOD1.jpg`。
- `scene/`：放在一條小溪上（兩岸、溪床、水面），有材質和灰模兩版，四個角度：
  - 3/4；
  - 橋上 1.7 m 人眼；
  - 80 m 外輪廓；
  - 從溪裡看。
- `unity/`：Unity 截圖與報告。

## 工時

約 3 小時（11/12，含讀包、三視圖生成與選圖、河谷貼圖、建模、QA 修正、Unity 檢查），由 Claude Code 執行。
