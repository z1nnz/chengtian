# GT03 林地地形材質

- 用途：Unity Terrain 的林地層，與 GT01 草地、GT02 土路混合。
- 內容：2048 × 2048 Albedo、Normal、URP Mask Map，以及已目視檢查的 3 × 3 平鋪預覽。
- 視覺檢查：深褐土、細根、稀疏落葉和苔蘚可辨。平鋪邊界無明顯線條；葉片與苔蘚圖案會週期性重複，需要地形混合及散布模型打散。
- 技術檢查：`validation.json` 記錄三張圖四邊最大像素差均為 0。原始 AI 圖為 1254 × 1254，輸出放大至 2048 × 2048；放大不增加原生細節。
- 製程：AI 原圖在 `art/references/ground-textures-v2/GT03/`；`art/source/ground-textures-v2/build_gt03.py` 可重建輸出。
- 狀態：材質候選已完成；Unity 內實際尺度、光照、混合及效能尚未驗證。
