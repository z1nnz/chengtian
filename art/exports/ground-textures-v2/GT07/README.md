# GT07 水田濕泥地形材質

- 用途：Unity Terrain 的水田濕泥層；較深水面與田埂由場景系統另外處理。
- 內容：2048 × 2048 Albedo、Normal、URP Mask Map，以及已目視檢查的 3 × 3 平鋪預覽。
- 視覺檢查：深褐濕泥和零星淺水窪可辨；四邊沒有明顯接縫。水窪在連續鋪設時重複可辨，場景端需與水面、其他土層混合。
- 技術檢查：`validation.json` 記錄三張圖四邊最大像素差均為 0。Mask Map 的 A 通道讓較亮水窪比泥面更平滑。AI 原圖為 1254 × 1254，輸出放大至 2048 × 2048，放大不增加原生細節。
- 製程：AI 原圖位於 `art/references/ground-textures-v2/GT07/`；`art/source/ground-textures-v2/build_gt07.py` 可重建輸出。
- 狀態：材質候選已完成；Unity 內反光、光照、水面銜接、比例和效能尚未驗證。
