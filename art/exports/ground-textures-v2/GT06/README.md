# GT06 茶田土地形材質

- 用途：Unity Terrain 的茶田翻土層；茶樹與實際田壟由場景物件及地形決定。
- 內容：2048 × 2048 Albedo、Normal、URP Mask Map，以及已目視檢查的 3 × 3 平鋪預覽。
- 視覺檢查：低飽和紅褐土、細小土塊和淺水平耕痕可辨。四邊無明顯接縫；耕痕仍有週期重複，應與田壟模型及其他土層混合。
- 技術檢查：`validation.json` 記錄三張圖四邊最大像素差均為 0。AI 原圖為 1254 × 1254，輸出放大至 2048 × 2048；放大不增加原生細節。
- 製程：第二版 AI 原圖在 `art/references/ground-textures-v2/GT06/`；`art/source/ground-textures-v2/build_gt06.py` 可重建輸出。
- 狀態：材質候選已完成；Unity 內實際比例、光照、茶田與路面混合及效能尚未驗證。
