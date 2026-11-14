# trees-v2：樹木重做 v2（照天空島世界樹的做法）

工作包：2026-11-14「樹木重做 v2：照『天空島世界樹』的做法，三人分工」，B 的份：TR01／02／03／05。
本批先交 **TR01 松樣品**（A、B、C 三棵）；審查通過後再做 TR02 柏、TR03 樟、TR05 銀杏。

2026-11-15 重做：先前的 TR01 版本與 `art/references/TR01/v002/` 的三視圖全部作廢，改照新三視圖重建。

| 狀態 | TR01 三棵 |
|---|---|
| Exported | 是（FBX、GLB、model_info.json、validation.json） |
| Imported | 是：Unity 6000.3.28f1 編輯器批次檢查 `TreesV2ModelCheck`，60 項全過 |
| Visually Verified | Blender 審圖：是；Unity 截圖：是（編輯器暫用地面，不是遊戲場景） |
| In-game Verified | 未驗（沒放進任何遊戲場景） |

**沒有改主場景、區塊 JSON、世界填充表。** 只做 Unity 用的模型。

## 三視圖

Codex image_gen 依工作包生成，兩輪各 4 張：`art/references/TR01/v002-r2/`（第一輪）、`art/references/TR01/v002-r3/`（加密枝葉後）。
建模依據：**`v002-r3/TR01-cand-1.png`**（寬冠分層、層間看得到枝幹、一條低長枝；選用理由寫在同資料夾的 `prompt.txt`）。
TR02 cand-3、TR03 cand-2、TR05 cand-4 也已選定，等 TR01 審過再做。

## 做法（照 docs/execution/2026-11-14/tree-method 的順序）

1. S 形主幹，9 個控制點；根瓣五片埋入地面 0.3 m；兩到三處斷樁、兩個樹瘤。
2. 先放 3 條剪影主枝（較粗、較長），再用黃金角加抖動補其餘主枝；方位、高度、長度都不同，不鏡像。主枝離幹先上揚、外段近水平、梢端上翹。
3. 次枝左右交錯、越往梢越短；每條次枝外段 3–4 根末梢枝，每條主枝梢端再一叢 3 根。
4. 枝幹每根是一條管，子枝從母枝軸心長出（不用 Skin 修改器，所以枝上沒有接縫）；末梢枝只有兩圈，省下的面數給針葉。
5. 葉冠錨點：每條主枝一個，枝梢數 = 次枝數 + 梢端一叢；不足 7 股的併到最近的鄰枝，每個錨點 7–13 股。A 19、B 16、C 14 個。
6. 針葉：**油松兩針一束**（`tv2_core.Buf2.needle_pair`：5 頂點、2 面，兩根針從同一基點張開 16–34 度）。9–12 束圍成一刷，沿末梢枝往前掃、略壓扁；刷沿每根末梢枝的參數 t 從 30 % 排到梢端。每刷上亮下暗，所以一層層看起來是厚墊，不是散針。
7. LOD1、LOD2 也是雙針束，束數少、單束放大（LOD1 長 0.75–0.95 m、6–8 束一刷；LOD2 長 1.2–1.5 m、4–5 束一刷）；葉量依預算平均分到整個樹冠。LOD3 是交叉替身卡。
8. 頂點色：依高度、離幹遠近、在層裡的上下與 t 連續混色，A = 遮蔽；同樣的值也寫在 UV0，指向調色盤貼圖。
9. 最後才做樹皮：中低頻的根瓣、稜線、樹瘤做在幾何上，再上手繪樹皮貼圖。

沒有使用葉片卡、葉團圖集，也沒有在球體或橢球裡撒葉；枝不鏡像，粗細也不相同。

## 三棵

| 件 | 高 | 寬 × 深 | 形 | 錨點 | 主枝 | 種子 |
|---|---|---|---|---|---|---|
| TR01_A_Pine | 17.0 m | 19.1 × 13.9 m | 主幹 S 彎，左側一條 8.4 m 低長枝定剪影，寬冠分層 | 19 | 19 | 131 |
| TR01_B_Pine | 15.8 m | 13.5 × 10.9 m | 幹微右傾，冠較高較窄，長枝往右後 | 16 | 19 | 227 |
| TR01_C_CliffPine | 14.6 m | 12.1 × 8.4 m | 崖松（B1）：細幹大斜，一條長枝外伸，冠小，三處斷樁 | 14 | 15 | 313 |

高、寬、深是 LOD0 外框（高不含埋入地下的 0.3 m）。實際數字以各件 `model_info.json` 為準；種子固定，可重建出同一棵樹。

## 面數（三角面）

| LOD | 上限 | A | B | C | 內容（A） |
|---|---|---|---|---|---|
| LOD0 | 60,000 | 59,100 | 59,100 | 48,372 | 枝幹 11,404＋雙針束 23,848 束 |
| LOD1 | 15,000 | 14,766 | 14,774 | 12,260 | 枝幹 3,654＋雙針束 5,556 束 |
| LOD2 | 4,000 | 3,772 | 3,940 | 3,115 | 枝幹 702＋雙針束 1,535 束 |
| LOD3 | 200 | 4 | 4 | 4 | 交叉替身卡 |

LOD 建議切換距離：35／90／220 m，1200 m 外淡出（`lod_switch_distance_m`）。

## 物件、材質、貼圖

- 每件 FBX：根空物件 `<ID>`，子物件 `<ID>_LOD0`～`_LOD3`（每級 1 個網格）與 `<ID>_Collision`（樹幹八角柱，高 3 m；半徑 A 0.53、B 0.39、C 0.26 m；隱藏渲染，當 MeshCollider 或同尺寸膠囊用；樹冠不擋路）。共 5 個網格、1 個空物件。
- 材質 3 種：`M_TR01_Bark`、`M_TR01_Leaves`（LOD0–2 各 2 個材質槽），`M_TR01_Impostor`（只用在 LOD3）。
- 共用貼圖 `TR01_Shared/Textures/`：

| 檔 | 尺寸 | 用途 |
|---|---|---|
| TR01_Bark_BaseColor.png | 1024 × 1024 | 樹皮顏色（sRGB） |
| TR01_Bark_Normal.png | 1024 × 1024 | 樹皮法線 |
| TR01_Bark_MetallicSmoothness.png | 1024 × 1024 | 金屬 0、平滑度低（linear） |
| TR01_Leaves_Palette.png | 256 × 64 | 葉色調色盤：u = 色調暗→亮，v = 遮蔽（sRGB；不要 mipmap、Clamp） |
| TR01_Impostor_BaseColor.png | 1536 × 512 | LOD3 三棵正面（含 alpha，裁切 0.5） |
| TR01_Impostor_Normal.png | 1536 × 512 | LOD3 法線 |

- 頂點色 `Color`（FBX 頂點色，linear）：葉子 RGB 是葉色，A 是遮蔽（不是透明度）；木頭 RGB 1、A 1。
- 風：UV1 `Wind`，u = 擺動權重（主幹 0，主枝 0.03–0.3，次枝 0.3–0.5，末梢 0.5–0.8，葉 0.62–1），v = 相位 0–1。

## 座標

1 單位 = 1 m。原點在樹幹底部中心，z = 0 是地面；根往下埋 0.3 m。Blender −Y 是正面（Unity 是 −Z）。

## 重建與審圖

```
blender -b --factory-startup -P art/source/trees-v2/build_trees_v2.py -- TR01 --force
blender -b art/source/trees-v2/blend/TR01_v002.blend -P art/source/trees-v2/preview_trees_v2.py -- <輸出資料夾>/TR01_A_Pine TR01_A_Pine
uv run --offline --no-project --with pillow python art/source/trees-v2/compose_review.py <輸出資料夾> <審查圖資料夾> TR01 TR01_A_Pine TR01_B_Pine TR01_C_CliffPine
Unity.exe -batchmode -projectPath apps/game -executeMethod YunJing.Editor.TreesV2ModelCheck.Run -trees TR01 -quit
```

產生器：`art/source/trees-v2/tv2_pine.py`（TR01 的樹形、枝幹、針葉都在這裡）；`build_trees_v2.py` 負責 LOD、匯出、model_info、validation。
`compose_review.py` 的標準圖並排需要 `docs/execution/2026-11-14/tree-method/標準-天空島世界樹.png`（z1nnz 的 `feature/qingxi-creek-chapter` 分支）。
Unity 檢查會把模型與貼圖複製到 `Assets/YunJing/Generated/TreesV2`（已被 git 忽略），輸出到 `artifacts/trees-v2-unity/`（已被 git 忽略）；本批的報告與截圖另存一份在 `art/previews/trees-v2/unity/`。

## Unity（6000.3.28f1，編輯器批次檢查）

`TreesV2ModelCheck` 自動檢查 60 項，0 項失敗（`art/previews/trees-v2/unity/unity-verify-report.txt`）：
- 每件 LODGroup 都有 LOD0–LOD3，每級 1 個 renderer；面數和 model_info 一致，也都在上限內。
- LOD0–2 各 2 個材質，LOD3 1 個；每個頂點都有 `Color` 頂點色和 UV1 風權重；樹幹 2 m 以下風權重為 0。
- 高度和 model_info 一致；碰撞體是隱藏 renderer 的 MeshCollider。
- 1.75 m 的 CharacterController 朝樹幹走會被擋住；在樹幹旁 1.5 m 走過樹冠下不會被擋。這是腳本模擬，不是真人操作。
- 葉材質用 URP Lit：不透明、雙面，BaseMap 是調色盤貼圖。沒有自訂 shader，也還沒接上風動。

截圖在 `art/previews/trees-v2/unity/`：正面、三分之四側、1.7 m 視高樹下仰看、LOD0–3 強制切換、20 m 與 60 m 遠景、三棵與 1.75 m 人形並排。
專案的 LOD bias 是 2.0，所以 20 m 時 LODGroup 還在 LOD0。

## 審查圖

`art/previews/trees-v2/<ID>/`：
- `_vs_reference_cand1`：選定三視圖 cand-1 和正面、左 35°、右 35° 並排
- `_vs_standard`：工作包標準圖（天空島世界樹）和正面、左 35°、右 35° 並排（同一個太陽與天空）
- `_silhouettes`：三張黑剪影（正面、右 35°、頂視）
- 灰模、線框（全樹與樹冠近照）、樹下仰看、20 m（LOD0）與 60 m（LOD1）遠景、LOD 對照、1.75 m 人形尺

`art/previews/trees-v2/TR01_variants_front.png`：三棵的正面並排。

## 檢查表（指南第四節，照實勾）

大形
- [x] 關閉材質後仍有可辨識的重心與剪影（`_silhouettes`）。
- [x] 主幹不是直柱，也沒有硬折角（9 個控制點的 S 形）。
- [x] 至少三條主枝分別負責左右跨度、最高點與前後厚度（前三條主枝較粗較長）。
- [x] 左右不鏡像，葉冠有大小不同的負空間。
- [x] 縮到 60 m 遠景仍能看出主枝（`_far60m_LOD1`、Unity `_far_60m`）。

枝幹
- [x] 主幹、主枝、次枝、末梢枝的粗細分級清楚。
- [ ] 分叉處沒有平均鼓包或夾縮：只從線框、灰模和樹下仰看大致看過，沒有逐一檢查每個分叉。
- [x] 末梢枝真的進入葉冠（`_under_crown`）。
- [x] 有少量斷樁、樹瘤，沒有均勻鋪滿（A、B 兩處斷樁，C 三處；樹瘤兩個）。

葉冠
- [x] 針葉沿末梢枝（枝梢流）分布，不是在球體裡亂撒。
- [x] 前後葉冠分層，轉到 ±35° 仍有厚度。
- [ ] 主要葉叢厚、外圍疏：分層、外圍疏有做到，但和 cand-1 並排時，主要葉叢仍比較透。LOD0 上限 6 萬面，枝幹佔 1.1 萬，針葉約 2.4 萬束。
- [x] 葉色依高度、內外與遮蔽連續變化，沒有硬色帶。
- [x] 葉片表示法符合平台與距離（LOD0–2 用雙針束，LOD3 用替身卡）。

根與地形
- [x] 根瓣往下埋入地面 0.3 m，不是浮在地上。
- 垂根沿岩壁：不適用（A、B 是平地樹；C 是崖松，但沒有附岩壁，放到 B1 時要另外對位）。
- [ ] 主根、次根、細根的主次：只有根瓣，沒有做分級根。
- [ ] 根部接觸處的陰影與重量：沒有在遊戲場景地形上驗證。

材質
- [x] 樹皮高粗糙、低金屬，色差不過度。
- [x] 中尺度的根瓣、稜線、樹瘤做在幾何上，比高頻紋理先做。
- [x] 葉片不靠高金屬度或強鏡面製造亮點（金屬 0）。
- 瀑布、雲、岩壁：不適用。

遊戲資產
- [x] 亂數種子固定，可重建同一棵樹。
- [ ] 掛點名稱和索引穩定：錨點由種子固定，但沒有匯出成具名掛點。
- [x] 葉片整併在每級 LOD 的單一網格裡，不是大量獨立物件。
- [x] FBX／GLB、母稿、model_info 與 Unity 檢查同步更新。
- [ ] 實際裝置的幀率、記憶體與發熱：沒有量測。

證據
- [x] 同相機、同光線的正面、±35° 圖，以及和三視圖、標準圖的並排圖。
- [x] 正面、左右 35°、剪影都有；沒有單獨拍根部近照。
- [ ] 旋轉或風動來自引擎實際畫面：還沒有接風動 shader，Unity 只有靜態截圖。
- [x] 測試結果（Blender validation、Unity 60 項）、美術自評與真機（未測）分開記錄。

## 自評

約 90 分（還沒到 95）。
- 好的地方：一看就是松（雙針束成刷、樹下仰看是松針刷蓋著枝幹）；A 的 S 彎主幹和左側低長枝接近 cand-1；三棵剪影各不相同；三個 LOD 都是針葉，遠看不會變成竹葉或禿枝。
- 還差的地方：和 cand-1 並排，樹冠仍比較透、層與層之間的空隙比較大；A 的冠頂偏平，cand-1 是圓頂。主因是 LOD0 的 6 萬面上限；若允許 LOD0 再多 2–3 萬面，可以直接補厚主要葉叢。
