# D2 神木與樹皮標準：試做程式（核心組，2026-11-15）

- `godtree_base.py`：樹皮標準的核心。`tube()` 把一條路徑做成管子，並把 Poly Haven 掃描樹皮（`bark_brown_02`）的 Displacement 推進幾何。這條管子有扭轉粗稜，有苔／裂溝／地衣的頂點色遮罩。`bark_material()` 是對應的材質：掃描貼圖降飽和、灰化，裂溝壓暗，凸起處加地衣，朝上處長苔。
- `godtree_v3.py`：神木 v3，照 `art/references/core-d2-v1/godtree/godtree-concept-1.png` 做。六股粗木絞成樹幹，往下散成板根，往上分成彎曲的主枝和次枝；樹冠用天空島世界樹的做法。
- `bark_sample.py`：最早的樹皮試做。

掃描樹皮貼圖不放進 repo。從 https://polyhaven.com/a/bark_brown_02 下載 2k PNG（CC0），把 `diff`、`nor_gl`、`rough`、`ao`、`disp` 放進本目錄的 `tex/`；該目錄已由 `.gitignore` 排除。素材作者 Rob Tuytel，來源與授權以 Poly Haven 頁面為準。

渲染高模試作：`blender -b --factory-startup -P godtree_v3.py -- <tag> quick`。

遊戲版匯出：`blender -b --factory-startup -P bake_godtree.py -- game`。會輸出 GT01 的 FBX、GLB、LOD0–2、2k 樹皮圖、model_info.json、validation.json、.blend 和預覽圖。樹皮幾何使用掃描位移；目前貼圖是掃描來源圖，**尚未完成高模到遊戲模的獨立 Normal／AO／Base Color 烘焙**。葉叢是遊戲版葉片幾何試作，仍需和三視圖及 D2 設定圖做同鏡位美術驗收。

神木三視圖：`art/references/core-d2-v1/godtree/godtree-three-view-v1.png`，由 imagegen 生成並檢視後保存；建模規格參考同目錄的 `godtree-concept-1.png`。
