# GT05 河谷暖灰岩地形材質

- 用途：Unity Terrain 的露岩層，沿河谷坡面及裸露岩台使用。
- 內容：2048 × 2048 Albedo、Normal、URP Mask Map，另附已目視檢查的 3 × 3 平鋪預覽。
- 視覺檢查：暖灰礦物紋理與淺裂紋可辨；四邊無明顯接縫。較長裂紋在 3 × 3 預覽中有可辨重複，場景端需以地形層混合及獨立岩石打散。
- 技術檢查：`validation.json` 記錄三張圖四邊最大像素差均為 0。AI 原圖為 1254 × 1254，輸出放大至 2048 × 2048；放大不增加原生細節。
- 製程：選用 AI 原圖位於 `art/references/ground-textures-v2/GT05/`；`art/source/ground-textures-v2/build_gt05.py` 可重建輸出。
- 狀態：材質候選已完成；Unity 內實際比例、光照、與溪岸材質混合及效能尚未驗證。
