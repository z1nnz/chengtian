# GT04 溪邊礫石地形材質

- 用途：Unity Terrain 的溪邊礫石層；岸線位置由地形遮罩決定。
- 內容：2048 × 2048 Albedo、Normal、URP Mask Map，另有已目視檢查的 3 × 3 平鋪預覽。
- 視覺檢查：灰色細礫和卵石可辨，局部有暗色濕痕；沒有強反光或硬岸線。平鋪邊界沒有明顯接縫，但較大的石子圖案會重複；應在場景中混合鄰近材質並散布獨立石塊。
- 技術檢查：`validation.json` 記錄三張圖四邊最大像素差均為 0。AI 原圖為 1254 × 1254，輸出放大至 2048 × 2048，放大不增加原生細節。
- 製程：選用 AI 原圖位於 `art/references/ground-textures-v2/GT04/`；`art/source/ground-textures-v2/build_gt04.py` 可重建輸出。Mask A 通道有輕微濕度平滑度變化。
- 狀態：材質候選已完成；Unity 內實際比例、光照、岸線混合及效能尚未驗證。
