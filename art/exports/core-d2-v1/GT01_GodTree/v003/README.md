# GT01 神木 v003（遊戲版）

- 來源：`art/source/core-d2-v1/godtree/godtree_v3.py`（z1nnz 11/16 定版，GT_NSEED=1）。
- 做法：
  1. 同一份程式先產生高模（`GT_STEP=0.1`，掃描樹皮凹凸做進幾何，約 650 萬面）；
  2. 再產生低模三級（`GT_STEP` 0.65／1.3／2.6、`GT_AMP=0`）；
  3. `gt_bake.py` 用 Cycles 把高模的 Normal、Base Color、AO 烘焙到 LOD0（4096，UV0＝BakeUV）；
  4. `gt_stage2.py` 做 LOD1／LOD2（UV 由 LOD0 轉來）、葉子抽稀放大、細枝只留看得到的層級、碰撞殼 `UCX_GT01_GodTree`。
- UV：UV0＝BakeUV（烘焙圖用），UV1＝TileUV（每 2.6 m 重複一次，給 URP Lit 的 Detail Normal 放 Poly Haven `bark_brown_02_nor_gl`，近看才有樹皮細節）。
- 葉子：頂點色 `LeafColour`（金綠漸層），不透明雙面，需要讀頂點色的材質。
- 三角面：LOD0 約 129 萬（樹幹 14.3 萬、葉 67.5 萬、細枝 47.5 萬）；LOD1 約 35 萬；LOD2 約 5.2 萬。手機用 LOD1／LOD2。
- 原點：樹幹底部中心，z = 0 在地面。底部寬約 60 m，總高約 60 m。
- 並排：`art/previews/core-d2-v1/GT01_GodTree/v003/GT01_high_vs_game.jpg`。
