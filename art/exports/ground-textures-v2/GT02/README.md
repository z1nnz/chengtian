# GT02 灰褐土路地形材質

- 用途：Unity Terrain 的泥土路層。路線形狀與分岔應由地形塗層遮罩決定；此圖沒有硬邊，不作整條道路模型。
- 內容：2048 × 2048 Albedo、Normal、URP Mask Map，以及已目視檢查的 3 × 3 平鋪預覽。
- 視覺檢查：灰褐踩實土與細碎石清楚；連續車轍已弱化。平鋪邊界無可見接縫，但固定石子圖案仍會重複，應與鄰近地形層混合並以小石實體打散。
- 技術檢查：`validation.json` 中三張圖的左右與上下邊界最大像素差均為 0。原始 AI 圖為 1254 × 1254，輸出放大至 2048 × 2048；放大不增加原生細節。
- 製程：選用的 AI 原圖在 `art/references/ground-textures-v2/GT02/`；`art/source/ground-textures-v2/build_gt02.py` 可重新產生輸出。
- 狀態：材質候選已完成；尚未在 Unity Terrain 上驗證實際比例、光照及與 GT01 的混合。
