# 承天｜世界裡的樹：TR01 松、TR02 柏（11/11 工作包 B｜64 小時 A 批）

| 項目 | 內容 |
|---|---|
| 誰做的 | B（joshsu54） |
| 工作包 | 2026-11-11 B｜64 小時：世界裡的樹全部重做（九種），A 批（TR01–TR02） |
| ID | TR01 松：A 松（S 形主幹）、B 松（斜幹低長枝）、C 崖松（細幹大斜）。TR02 柏：A 柏（S 形直幹、兩個樹瘤）、B 柏（斜幹寬冠）、C 老柏（大扭大斜、一側枯枝） |
| 分支／PR | art/b-1111-tr-trees-conifer ／ z1nnz/chengtian#106 |
| 版本 | 全部 v001（首次交付，沒有舊版） |
| 狀態 | TR01、TR02 共 6 件都是 Exported ／ Imported（Unity 6000.3.28f1 編輯器批次檢查）／ Visually Verified（Blender 與 Unity 審圖）；In-game Verified：未驗（沒放進正式場景） |
| 預定位置 | 由核心組落位（`slot` 寫在 model_info.json：TR01 A1/A2/A4 全區；TR02 D1/D2/D4 古林） |
| 素材來源 | 原創（Blender 5.2 程序化建模，TR01 樹皮貼圖用 numpy 程式畫；TR02 樹皮取自團隊手繪古樹樹皮再調色；葉片圖集在 Blender 內渲染）。三視圖參考由 Codex image_gen 生成，只當外形參考（`art/references/TR01/`，選 cand-4、備案 cand-2，理由寫在 prompt.txt）；比例照真實松樹，不照圖量 |

**沒有改主場景、沒有改區塊 JSON、沒有改世界填充表。** 只做 Unity 用的模型；不做 ElderGuardian、JianmuSapling，不做人物、動物、文字、玩法。

## 共同做法

- 先生成三視圖（4 張）、自評選一張，再做灰模、線框、LOD，最後上貼圖。
- 原點在樹幹底部中心，z = 0 是地面；根往下埋 0.3 m（z 最低 −0.3）。Blender −Y 是正面（FBX／Unity 是 −Z）。
- 一棵樹一個網格／LOD，兩個材質槽：`M_TR01_Bark`（樹皮）、`M_TR01_Leaves`（葉）；LOD3 只有葉材質。同一樹種三個變體共用一套貼圖（`TR01_Shared/Textures/`）。
- 葉片：BaseColor 的 alpha 做 alpha clip 0.5、雙面；BaseColor 匯入時開 Mip Maps Preserve Coverage（參考值 0.5）。
- 風：寫在頂點色 `Wind`（FBX 線性色）：R 擺動權重（主幹 0、大枝 0.02–0.3、細枝 0.3–0.5、葉團 0.6–1），G 每團相位，B 高度 0..1。
- 碰撞：`<ID>_Collision` 是包住主幹的 8 邊柱（z 0–3 m），渲染關掉、當 MeshCollider 用，或換成同尺寸 CapsuleCollider（數字在 model_info.json `collision_capsule`）。樹冠不擋人。
- LOD 切換距離（model_info.json `lod_switch_distance_m`）：LOD0→1 在 60 m、1→2 在 100 m、2→3 在 260 m、1500 m 以外淡出。Unity 檢查程式依這些距離與專案 LOD bias（2.0）換算 LODGroup 高度，0.98 封頂。
- minTier 都是 `low`（樹是場景主體，最低畫質也要有）。
- 重建：`blender -b --factory-startup -P art/source/trees-b/build_trees_b.py -- TR01 --force`；審圖：`blender -b art/source/trees-b/blend/TR01_v001.blend -P art/source/trees-b/preview_trees_b.py -- TR01 <hero|grey|wire|lods|ruler|ten|far>`；Unity：`Unity.exe -batchmode -projectPath apps/game -executeMethod YunJing.Editor.TreesModelCheck.Run -trees TR01 -quit`。

## 貼圖（TR01 共用）

| 貼圖 | 大小 | 說明 |
|---|---|---|
| `TR01_Bark_BaseColor.png` | 1024×1024 | 可四方連續鋪的松樹皮（灰褐龜甲片、深裂縫），每 1.2 m 鋪一次 |
| `TR01_Bark_Normal.png` | 1024×1024 | 法線（OpenGL，+Y） |
| `TR01_Bark_MetallicSmoothness.png` | 1024×1024 | R 金屬 0，A 光滑度 |
| `TR01_Leaves_BaseColor.png` | 2048×2048 | 上半：兩格松針簇（含 alpha）；下半：三個變體的 LOD3 遠景圖（各一欄） |
| `TR01_Leaves_Normal.png` | 2048×2048 | 法線 |
| `TR01_Leaves_MetallicSmoothness.png` | 2048×2048 | R 金屬 0，A 光滑度 0.18 |

命名：工作包寫「Albedo/Normal/MaskURP，和 VL 一樣」，但 VL 民居實際用的是 `BaseColor` / `Normal` / `MetallicSmoothness`，這裡照 VL 實際命名（BaseColor = Albedo，MetallicSmoothness = URP 的金屬／光滑度遮罩）。

## TR01 松

真實比例的松（約 13 m，胸高主幹直徑約 0.6 m，第一根大枝約 5 m 高），不是盆景比例。主幹彎曲、樹皮灰褐龜甲片；大枝先往上爬、再折彎往外伸，末端托著扁圓、下緣平的雲狀葉團（一團一團分層，不是平板）。

| 變體 | 說明 | 高 × 寬 × 深（m） | 三角面 LOD0 / 1 / 2 / 3 | 物件數（每 LOD） | 材質數 LOD0–2 / LOD3 | 葉片卡數 LOD0 | 碰撞半徑 |
|---|---|---|---|---|---|---|---|
| TR01_A_Pine | 松：S 形主幹、五層葉團 | 12.93 × 12.60 × 10.17 | 23,494 / 6,856 / 1,342 / 4 | 1 | 2 / 1 | 2,505 | 0.55 |
| TR01_B_Pine | 松：斜幹、一條低長枝、樹冠較寬 | 12.51 × 14.65 × 11.12 | 23,494 / 7,518 / 1,670 / 4 | 1 | 2 / 1 | 2,429 | 0.57 |
| TR01_C_CliffPine | 崖松：細幹大斜、葉團少而小 | 12.45 × 10.82 × 8.68 | 15,624 / 3,810 / 728 / 4 | 1 | 2 / 1 | 1,621 | 0.41 |

上限 LOD0 25,000 ／ LOD1 8,000 ／ LOD2 2,500 ／ LOD3 200，三件都在上限內。高度範圍 12–14 m。

檔案：
- `art/exports/trees-b/<ID>/<ID>_v001.fbx`（LOD0–3 與 `_Collision`）
- `<ID>_v001.glb`（同內容）
- `model_info.json`、`validation.json`
- 原始檔 `art/source/trees-b/blend/TR01_v001.blend`

審圖：`art/previews/trees-b/<ID>/`：
- `_hero`、`_grey`、`_wire`
- `_LOD_comparison`
- `turnaround/` 十視圖與 views.json
- `_far_50m_*`、`_far_100m_*`
- 量尺圖：`art/previews/trees-b/TR01_ruler_material.png`、`TR01_ruler_grey.png`（1.75 m 人形 + 每 0.5 m 一格）

Unity 截圖在 `art/previews/trees-b/unity/`。

## 檢查結果

- **Blender**（validation.json，三件全過）：
  - LOD 面數上限
  - 高度在 12–14 m
  - 原點在地面、根不低於 −0.3 m
  - FBX 回匯物件名稱齊全
  - FBX 回匯 LOD0 高度誤差 < 1 mm
  - FBX 帶風頂點色
- **Unity 6000.3.28f1**（`TreesModelCheck`，57 項 PASS、0 FAIL）：
  - LODGroup 四層，各一個 renderer
  - 三角面數和 model_info 相符
  - 材質數
  - 頂點色存在；樹幹 2 m 以下風權重 < 0.05，葉 ≥ 0.5
  - 高度
  - MeshCollider
  - 葉貼圖 Preserve Coverage
  - CharacterController（半徑 0.25、高 1.75）走向主幹會被擋，從主幹旁 1.5 m 走過不被樹冠擋
  - 50 m 顯示 LOD0、100 m 顯示 LOD1（LOD bias 2.0）
- **審圖**：
  - 近看是一團團松針雲團，主幹、大枝看得出是松。
  - 50 m、100 m 葉團仍是成塊的形狀，沒有變成雜訊或閃爍的細點。
  - 和 VL02 民居、1.75 m 人形並排比例合理。

## 保守做法與未驗項目（寫進 PR）

- 三視圖四張都帶盆景味（cand-3 還有注連繩），模型只取「分層雲狀葉團、彎主幹」的外形，比例照真實松樹；圖中樹下的石頭、草不做（不屬於樹）。
- 變體 C 做成崖松（同樹種、外形差最大），沒有另外開一個樹種 ID。
- LOD3 是兩片交叉卡片貼遠景圖。LOD3 不投影、也不接受陰影（Unity 檢查程式擺放時這樣設；正式落位請照做），否則兩片卡會互相遮出一條深色豎帶。沒有改專案設定。
- 風只寫在頂點色，沒有做風的 shader（不在工作包範圍）。目前 Unity 用 URP Lit，樹不會動。
- **未驗**：
  - 正式場景擺放（In-game Verified）
  - 手機效能
  - 光照烘焙
  - 遮擋剔除
  - 大量種植時的批次合併
- 不宣稱任何 FPS 數字。

## 自評（TR01，滿分 100，門檻 95）

| 項目 | 分數 | 說明 |
|---|---|---|
| 外形辨識 | 96 | 不看標籤也認得出松：彎主幹、分層雲狀葉團、大枝先爬升再外伸；三個變體輪廓不同（S 幹、斜幹長枝、崖松） |
| 配色 | 95 | 葉偏灰藍綠、樹皮灰褐；第一版樹皮在 Unity 偏磚紅，已降彩度重做 |
| 遠景 | 95 | 50 m、100 m 仍是成塊葉團、不閃不碎；LOD3 卡片關陰影後沒有深色豎帶 |
| 技術規格 | 97 | 面數、原點、根深、風頂點色、碰撞、LOD、貼圖大小都照工作包，Blender 與 Unity 檢查全過 |
| 比例 | 95 | 和 1.75 m 人形、VL02 民居並排合理 |
| 一致性 | 95 | 和 VL 民居同一套光下不突兀；近看葉團內側有深色空隙（是層次，不是破洞） |
| **平均** | **95.5** | |

---

## TR02 柏

古林的主角，地面以上約 10.2–10.8 m。主幹粗而扭，有樹瘤、隆起的樹皮板塊和深溝。下枝長、上枝短，樹冠往上收成尖頂。深綠偏青，苔從根部往上爬（最高約 1.8 m）。

**做法（2026-11-12 重做）：** 使用者看過雲團版後指示「全部打掉重做，參考剛剛做的金黃樹，不要再雲團了」。現行版照金色靈樹（`art/source/golden-spirit-tree/v001`）的長法，壓進遊戲預算：
- **枝幹：** S 形主幹，一層層長出去：主枝 → 中枝 → 小枝 → 末梢。用 Skin 修改器融成一體，分叉從母枝長出，看得到木頭。
  - 主枝與中枝比母枝細很多，各自是獨立的 Skin 島，從母枝裡面長出；接點沒有鼓包。
  - 低處主枝整根平順抬高到 2.4 m 以上，不硬壓，所以沒有折角。
- **葉：** 不用雲團、不用葉團球。葉子一簇簇長在末梢上，每簇 4–9 片，各自有角度。柏的一「片」是一枝扁平鱗葉（35–55 cm），每片是一張兩個三角面的葉卡，LOD0 約 5,300–6,100 片。
- **顏色：** 每片葉子依位置選 8 個色階之一：高處、外側、朝上的比較亮，下方、內側、下垂的比較暗，另加少量隨機。每個色階是圖集裡的一格，URP Lit 不用改 shader。
- **LOD1／LOD2：** 每張卡畫一整簇（4 種色階），色階與近景同一套。卡的大小是在 Unity 量過葉面覆蓋率後定的，所以遠近顏色一致：四級平均葉色差 ≤ 5%。
- **樹幹去塑膠感：**
  - 樹皮貼圖：對比拉大 2.1 倍，裂紋壓到近黑；法線改用未模糊的圖，強度 16；光滑度 0.07 以下。
  - 主幹表面：做出寬圓板塊加窄深溝，隨高度扭轉。
  - 面數分配：主幹單獨減面，保留四成木頭面數，輪廓不再有折角。
  - 貼圖對應：主幹改用「高度＋繞主軸角度」，根部外擴不再拉成直條紋；改前量到 130 倍拉伸，改後根部已無此問題，全樹最大約 35 倍，在一小段斷枝殘樁上。

參考圖含商業遊戲截圖，只留在本機，不提交。

| 變體 | 說明 | 高 × 寬 × 深（m） | 三角面 LOD0 / 1 / 2 / 3 | 其中木頭 LOD0 / 1 / 2 | 物件數（每 LOD） | 材質數 LOD0–2 / LOD3 | 葉卡數 LOD0 / 1 / 2 | 碰撞半徑 |
|---|---|---|---|---|---|---|---|---|
| TR02_A_Cypress | 柏：S 形直幹、兩個樹瘤、下枝長上枝短 | 10.22 × 8.48 × 9.08 | 22,231 / 4,604 / 2,190 / 4 | 8,999 / 2,599 / 750 | 1 | 2 / 1 | 6,017 / 827 / 720 | 0.51 |
| TR02_B_Cypress | 柏：斜幹、樹冠低而寬、一個大樹瘤 | 10.45 × 10.69 × 9.54 | 22,359 / 4,520 / 2,190 / 4 | 9,000 / 2,598 / 750 | 1 | 2 / 1 | 6,080 / 785 / 720 | 0.55 |
| TR02_C_OldCypress | 老柏：大扭大斜、一側兩根枯枝、樹冠窄高 | 10.82 × 6.29 × 8.37 | 20,722 / 3,793 / 1,592 / 4 | 9,000 / 2,599 / 750 | 1 | 2 / 1 | 5,261 / 421 / 421 | 0.51 |

上表的高是地面以上的高度。寬與深是外框尺寸，含埋在地下的 0.3 m 根。LOD 上限 25,000 ／ 8,000 ／ 2,500 ／ 200，三件都在上限內。高度範圍 9–11 m。材質：`M_TR02_Bark`、`M_TR02_Leaves`。主幹基部的苔是貼在樹皮外的薄片，用葉材質畫，風權重 0。

### 貼圖（TR02 共用，`TR02_Shared/Textures/`）

| 貼圖 | 大小 | 說明 |
|---|---|---|
| `TR02_Bark_BaseColor.png` | 1024×1024 | 可四方連續鋪的柏樹皮，取自團隊手繪的古樹樹皮再調成灰褐。裂紋深，亮度 5%–95% 分位為 0.00–0.44 |
| `TR02_Bark_Normal.png` | 1024×1024 | 法線（OpenGL，+Y） |
| `TR02_Bark_MetallicSmoothness.png` | 1024×1024 | R 金屬 0，A 光滑度（≤ 0.07） |
| `TR02_Leaves_BaseColor.png` | 2048×2048 | 左上：16 格單枝鱗葉（8 色階 × 2 種外形）。右上：4 格整簇（LOD1／LOD2）與苔帶。下半：三個變體的 LOD3 遠景圖。alpha 只有 0 和 1 兩種值 |
| `TR02_Leaves_Normal.png` | 2048×2048 | 法線 |
| `TR02_Leaves_MetallicSmoothness.png` | 2048×2048 | R 金屬 0，A 光滑度 |

顏色：葉的 8 個色階是 `#0F2426`–`#5E825E`（深綠偏青），苔是 `#2E3D2A`–`#4A5A34`。沒有螢光綠、檸檬黃、橘紅。

檔案：`art/exports/trees-b/TR02_*/`，與 TR01 相同結構。原始檔：
- `art/source/trees-b/blend/TR02_v001.blend`
- `art/source/trees-b/tr_cypress.py`
- `art/source/trees-b/tr_skin.py`（融合木頭，共用）

三視圖參考在 `art/references/TR02/`：選 cand-2，備案 cand-3，理由寫在 prompt.txt。

審圖：
- `art/previews/trees-b/TR02_*/`：hero、grey、wire、LOD 對照、十視角 turnaround、50 m／100 m 遠景
- `art/previews/trees-b/TR02_ruler_*.png`：1.75 m 人形尺

Unity 截圖：`art/previews/trees-b/unity/TR02_*`，報告在 `unity/unity-verify-report-TR02.txt`。

### TR02 檢查結果

- **Blender**（validation.json，三件全過）：
  - LOD 面數上限
  - 高度在 9–11 m
  - 原點與根深
  - FBX 回匯物件齊全
  - LOD0 高度誤差 < 1 mm
  - 風頂點色
  - 另查沒有零面積三角形（Unity 會丟掉這種面，造成面數對不上）
- **Unity 6000.3.28f1**（`TreesModelCheck -trees TR02`）：57 項 PASS、0 FAIL，項目同 TR01。
  - 風權重檢查改成可辨認主幹苔片：葉材質中風權重 0 的頂點視為苔，必須低於 2.2 m。
  - 其餘葉卡的風權重仍要 ≥ 0.5。
  - 這項改動在 `TreesModelCheck.cs`。
- **LOD 一致性**（Unity LOD0–3 截圖逐級比較葉面像素，以 LOD0 為 100%）：

  | 變體 | 平均葉色差 | LOD1 覆蓋 | LOD2 覆蓋 | LOD3 覆蓋 |
  |---|---|---|---|---|
  | A | ≤ 5% | 111% | 120% | 80% |
  | C | ≤ 5% | 104% | 113% | 78% |

### TR02 保守做法與已知問題

- 工作包禁色和參考圖不衝突，TR02 照工作包維持深綠偏青。
- 變體 C 的枯枝是刻意保留的（老柏一側枯死），不是漏貼葉。
- 根部外擴最底下（約 z 0–0.15 m）仍有一小段樹皮紋路呈鋸齒，多半被苔和地面蓋住。
- LOD3 是平面卡，比 LOD0 少約兩成覆蓋，在 260 m 以外才出現。
- 共用程式 `tr_skin.py`、`tr_tex.py`、`build_trees_b.py` 改動都是選填參數，或只作用在 Skin 木頭上。TR01 還沒重建，會照同樣做法重做，屆時一起重出。
- **未驗**：正式場景擺放（In-game Verified）、手機效能、光照烘焙、遮擋剔除、大量種植。不宣稱 FPS。

### TR02 自評（2026-11-12 定版，門檻 95）

| 項目 | 分數 | 說明 |
|---|---|---|
| 外形辨識 | 96 | 扭幹、樹瘤、下長上短的尖塔冠，不看標籤也認得出柏；三個變體輪廓不同（直幹、斜幹寬冠、老柏枯枝） |
| 枝幹 | 95 | 主枝→中枝→小枝→末梢一層層長出，接點沒有鼓包和折角；樹皮有板塊與深溝，不再像塑膠 |
| 葉片 | 95 | 葉子一簇簇長在末梢，每片有自己的角度與明暗；不是雲團，也不是葉團球 |
| 配色 | 95 | 深綠偏青，苔偏橄欖，樹皮灰褐；沒有工作包禁色 |
| 遠景 | 95 | 四級 LOD 平均葉色差 ≤ 5%；LOD3 覆蓋少約兩成，已寫在已知問題 |
| 技術規格 | 97 | 面數、原點、根深、風、碰撞、LOD、貼圖大小照工作包，Blender 與 Unity 57 項全過 |
| 比例 | 95 | 和 1.75 m 人形並排合理 |
| **平均** | **95.4** | |
