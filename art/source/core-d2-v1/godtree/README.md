# D2 神木與樹皮標準：試做程式（核心組，2026-11-15）

- `godtree_base.py`：樹皮標準的核心。`tube()` 把一條路徑做成管子，並把 Poly Haven 掃描樹皮（`bark_brown_02`）的 Displacement 推進幾何。這條管子有扭轉粗稜，有苔／裂溝／地衣的頂點色遮罩。`bark_material()` 是對應的材質：掃描貼圖降飽和、灰化，裂溝壓暗，凸起處加地衣，朝上處長苔。
- `godtree_v3.py`：神木 v3，照 `art/references/core-d2-v1/godtree/godtree-concept-1.png` 做。六股粗木絞成樹幹，往下散成板根，往上分成彎曲的主枝和次枝；樹冠用天空島世界樹的做法。
- `bark_sample.py`：最早的樹皮試做。

掃描樹皮貼圖不放進 repo，需要時從 https://polyhaven.com/a/bark_brown_02 下載 2k PNG（CC0），放到 `TEX` 路徑。
執行：`blender -b --factory-startup -P godtree_v3.py -- <tag> [quick]`。
