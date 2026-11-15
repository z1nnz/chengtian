# Codex v12｜D2 根部與神木試作記錄

執行：2026-11-15 晚至 11-16。基準：`origin/feature/qingxi-creek-chapter` 的 `docs/execution/2026-11-15/00-300h-共同標準.md`，D2 概念圖，以及 `art/core-1114-d2-altar-terrace` 的神木參考。**本輪產物尚未通過 85–90% 同鏡位美術驗收。**

## 分支與工作樹

- 已 `git fetch origin`，並把 `origin/art/core-1114-d2-altar-terrace` 合併進 `art/core-1113-co-ruins-v2`（合併提交 `5c573b2c`）。
- 開始時已有 BP01 未追蹤目錄、`diagnose_zf.py`、AL01 比較腳本修改與 `AL01_reference_tmp.glb`；全部保留，未納入本次改動。
- 追蹤的 RL01 A/B v001 已存在。本地追蹤資產未見 BP01、MU01、RA01、CO04、CO05；BP01 的未追蹤工作樹仍需作者完成與驗收。未擅自替其他人的 300 小時工作包宣告完成。

## 參考與掃描材質

- 先檢視 `godtree-concept-1.png`，再用內建 imagegen 生成、檢視並保存 [`godtree-three-view-v1.png`](../../../art/references/core-d2-v1/godtree/godtree-three-view-v1.png)，之後才修改模型程式。生成提示：*three-view orthographic model sheet, FRONT/SIDE/TOP, one consistent colossal six-strand ancient god tree, radiating buttress roots, asymmetrical spreading crown, fissured gray-brown bark, muted olive foliage, 1.75 m scale silhouette, neutral background, no perspective distortion*。
- SR01 與 AL01 已各有 AI 多視角參考圖；本輪先檢視後改模。
- 使用 [Poly Haven `bark_brown_02`](https://polyhaven.com/a/bark_brown_02) 2k PNG（CC0，作者 Rob Tuytel）。本機 `art/source/core-d2-v1/godtree/tex/` 有 diff、nor_gl、rough、ao、disp，該原始目錄由 `.gitignore` 排除；GT01 匯出目錄另附四張交付用掃描圖。`godtree_base.py`、`godtree_v3.py` 已改用倉庫相對路徑；樹冠生成依賴 `tree_gen.py` 已收入倉庫。

## 產物與實測

| 資產 | 新版本位置 | LOD0 / LOD1 / LOD2 triangles | Blender 管線驗證 |
|---|---|---:|---|
| SR01 A | `art/exports/core-d2-v1/SR01_SurfaceRoot_A/v003/` | 13,148 / 6,530 / 1,969 | all_pass |
| SR01 B | `art/exports/core-d2-v1/SR01_SurfaceRoot_B/v003/` | 9,758 / 4,877 / 1,462 | all_pass |
| SR01 C | `art/exports/core-d2-v1/SR01_SurfaceRoot_C/v003/` | 8,126 / 4,063 / 1,217 | all_pass |
| AL01 | `art/exports/core-d2-v1/AL01_RootAltarTerrace/v002/` | 152,158 / 76,078 / 22,822 | all_pass |
| GT01 | `art/exports/core-d2-v1/GT01_GodTree/` | 240,426 / 120,212 / 36,062 | validation.json pass |

SR01 A/B/C 改用掃描樹皮，掃描高度在根部幾何產生約 5–15 cm 起伏，再經原有管線烘焙成 2048 的 Base Color、Normal、Roughness 等圖。新增橢圓土床與更明顯的拱起、分岔。AL01 v002 只更新根部掃描表面，石台本體維持原輪廓。**原 AL01 v001、SR01 v002 的原有頂層路徑已恢復**；新版隔離在版本子目錄，避免破壞既有引用。

GT01 使用神木 v3 的六股主幹與板根輪廓、掃描位移幾何、三組 LOD、FBX／GLB 與簡化樹幹碰撞殼。模型範圍約 80.8 × 85.2 × 63.1 m，地面原點 z=0，地下根最低至 z=-2.43 m。預覽圖：[`GT01_GodTree_hero.png`](../../../art/previews/core-d2-v1/GT01_GodTree/GT01_GodTree_hero.png)。

`blender-asset-qa` 對 GT01 木材 LOD0 報告：201,426 triangles、0 邊界邊、0 非流形邊、0 反向封閉部件；**仍有** 100% 平鋪 UV 重疊、10 個重複頂點，因大網格而跳過 z-fighting／floating 掃描。地下根的 z<0 是設計需要。SR01 A 與 AL01 v002 的主體 QA 無 errors；大網格掃描同樣跳過 z-fighting／floating。葉片 QA 全面掃描耗時過長，未完成，不能列為通過。`python -m py_compile` 與 `git diff --check` 通過。

## 美術與交付缺口

1. GT01 目前葉片仍像分離的菱形卡片，樹冠密度、主枝扭轉和根牆氣勢都未到設定圖的 85–90%；沒有 D2 場景同鏡位對照截圖。SR01、AL01 v002 也尚未得到 z1nnz 同鏡位驗收，AL01 v002 根部可能不如已驗收的 v001 融合，故 v001 仍是既有引用版本。
2. GT01 的四張 2k 樹皮圖是**掃描來源圖**，木材 UV 重複平鋪；**不是**高模到 LOD0 的獨立 Base Color／Normal／AO 烘焙。若要真正烘焙，需要先展唯一 UV atlas 並重新投射掃描細節。GT01 葉片材質也尚無最終 cutout atlas。不能以 `bake_godtree.py` 檔名推論已完成高低模烘焙。
3. GT01 碰撞只覆蓋樹幹，外伸板根的碰撞殼、完整貼圖打包（含 Unity MaskURP）、多角度線框與 1.75 m 可辨識尺度對照仍需補齊。沒有跑 Unity 匯入、編譯、手機效能或場景實測。

目前應把 GT01 與 AL01 v002 視作**待美術審核的試作**。SR01 v003 已完成程式化管線檢查，但視覺接近度仍待 D2 同鏡位驗收。這份記錄不代表 D2 已完成，也不把 300 小時工作包算進本次成果。

## 11/16 後續核對：合併神木 v3 定版

- 再次執行 `git fetch origin art/core-1114-d2-altar-terrace`，將 `bb087e86` 合入本分支；Git 自動合併 `godtree_base.py` 與 `godtree_v3.py`。合併後依賴仍指向本倉庫的 `godtree_base.py`、`tree_gen.py`，沒有沿用上游提交中的本機絕對路徑。`GT_NSEED` 預設為 4，供 Blender noise 固定種子。既有的 BP01、AL01 本地未提交內容沒有納入。
- 用 Blender 5.2.2 執行 `godtree_v3.py -- gt01-merged quick` 成功，取得 [`full`](../../../art/previews/core-d2-v1/GT01_GodTree/godtree3_gt01-merged_full.png) 與 [`base`](../../../art/previews/core-d2-v1/GT01_GodTree/godtree3_gt01-merged_base.png)。兩張是高模概念渲染；`full` 的樹冠和板根體量比舊 [`GT01_GodTree_hero.png`](../../../art/previews/core-d2-v1/GT01_GodTree/GT01_GodTree_hero.png) 更接近三視圖，但 `base` 可見木材接縫，光照偏暗，尚未通過美術驗收。
- 現有 `GT01_GodTree_v001.fbx`、`.glb`、LOD 數字及 2K 圖仍來自較早的 `bake_godtree.py` 執行，不代表已套用 `bb087e86` 的種子 4 高模。`bake_godtree.py` 以 `exec` 載入 v3 的樹冠之前程式碼，另建稀疏葉卡；也不做 4K 唯一 UV 的高低模 Base Color／Normal／AO 烘焙。GT01 v002 仍未交付。
