# 承天｜仙俠風格大型綠樹 XT01（綠葉版＋金黃葉版）

| 項目 | 內容 |
|---|---|
| 誰做的 | B（joshsu54） |
| 需求 | 2026-11-13「仙俠風格大型綠樹」：開放世界風格化大樹，草原上的地標老樹（不是世界樹尺度），另做一款金黃葉版給宗門庭院，兩款共用模型與貼圖 |
| ID | `XT01_XianxiaGreatTree`，目前版本 **v003**（v001、v002 都被退件，檔案保留，見下方「版本」） |
| 分支 | `art/xianxia-great-tree`（從 `art/b-1111-tr-trees-broadleaf` 開出，B 批 TR03–TR07 在底下）；尚未推送、尚未開 PR |
| 狀態 | Exported ／ Imported（Unity 6000.3.28f1 編輯器批次檢查 38 項 PASS，0 項失敗）／ Visually Verified（Blender 與 Unity 截圖逐張目視）；In-game Verified：**部分**（只在 Qingxi 灰模裡臨時擺拍，場景沒有存檔，沒有放進正式場景） |
| 素材來源 | 原創。Blender 5.2 程序化建模（沿用 B 批 `tr_broad` 枝幹生長與 `tr_skin` 樹皮網格）；樹皮取自團隊手繪古樹樹皮（`art/source/trees-b/bark_src/elder_tree_bark_v1.png`）再調色；葉片圖集用 numpy 逐片繪製；LOD3 遠景圖是成品樹在 Blender Cycles 渲染的結果 |
| 參考圖 | 使用者 2026-11-13 提供的 15 張參考圖：外形照「草原上的地標樹」那張（寬傘形樹冠、短粗主幹、一叢叢花椰菜狀葉叢），葉叢層次與綠／金配色照「庭院金樹＋綠樹」那張。那些是商業遊戲截圖，只當參考，**沒有放進版本庫**，也沒有照抄任何造型 |

**沒有改主場景、沒有改區塊 JSON、沒有改世界填充表、沒有動角色、古樹、山兔或其他既有素材。** 共用的 `art/source/trees-b/tr_skin.py` 只有 v001 時加的三個預設關閉參數（`trunk_below`、`seal`、`face_uv`），TR01–TR07 重建結果不受影響；v002、v003 沒有再改共用腳本。

## 版本

| 版本 | 結果 | 檔案 |
|---|---|---|
| v001 | 退件（「全部都不對」）：幾顆大圓球葉團、樹形偏高，不像參考圖的寬傘形大樹 | `blend/..._v001.blend`、`..._v001.fbx`／`.glb`、Unity `Models/XianxiaGreatTreeV1/`、預覽 `previews/.../v001/` |
| v002 | 退件（「還是一坨，為什麼都是一團的」）：整個樹冠用一個平滑場打光，把葉叢的層次抹平了，遠看是一整塊 | `blend/..._v002.blend`、`..._v002.fbx`／`.glb`、Unity `Models/XianxiaGreatTreeV2/`、預覽 `previews/.../v002/` |
| v003 | 本次交付樣本，等待確認 | 下表 |

匯出資料夾的 `Textures/` 檔名沒有版本號，現在放的是 v003 貼圖；舊版貼圖留在各自的 Unity 資料夾（V1、V2）與 git 紀錄。

v003 重做的地方：

- **三層樹冠**：大葉團（34 團，排成偏一側的寬傘形）→ 中葉叢（每團上鋪數個 2.5–4 m 的花椰菜狀葉叢）→ 葉卡。參考圖的樹冠就是這種一叢叢堆起來的樣子。
- **每叢自己受光**：每個葉叢像一顆小球，頂部亮黃綠、底面深青綠，叢與叢之間是暗色凹縫；再疊上整體的高度與深度明暗。
- **枝幹看得到**：主枝從葉叢縫隙露出來（參考圖也是），枝路徑多做平滑，轉折不會出現方塊角。
- **從地面仰看**：葉叢下半部的葉卡朝外朝下，從樹下看是一片片葉叢，不是拉長的細條。
- **各層 LOD 輪廓一致**：LOD1、LOD2 的大葉卡往內收，沒有葉卡高過樹冠頂，四層最高點相差 0.1 m 以內。

## 檔案位置

| 用途 | 位置 |
|---|---|
| 可編輯原始檔 | `art/source/trees-xianxia/blend/XT01_XianxiaGreatTree_v003.blend`（綠樹 LOD0–3＋碰撞體；`_GoldPreview` 集合裡是金樹預覽副本，x = 40 m） |
| 生成腳本 | `art/source/trees-xianxia/build_xianxia_tree.py`（主建模）、`xt_leaves.py`（葉片圖集）、`preview_xianxia_tree.py`（審圖） |
| 匯出 | `art/exports/trees-xianxia/XT01_XianxiaGreatTree/`：`XT01_XianxiaGreatTree_v003.fbx`、`.glb`、`Textures/`、`model_info.json`、`validation.json` |
| Unity 素材 | `apps/game/Assets/YunJing/Models/XianxiaGreatTreeV3/`：FBX、`Textures/`、`Materials/`（5 個材質）、`XT01_XianxiaGreatTree_Green.prefab`、`XT01_XianxiaGreatTree_Gold.prefab` |
| Unity Shader | `apps/game/Assets/YunJing/Shaders/XianxiaTreeLeaves.shader`（`YunJing/XianxiaTreeLeaves`）、`XianxiaTreeBark.shader`（`YunJing/XianxiaTreeBark`） |
| Unity 安裝＋檢查程式 | `apps/game/Assets/YunJing/Editor/XianxiaTreeCheck.cs` |
| 預覽圖 | `art/previews/trees-xianxia/XT01_XianxiaGreatTree/`：Blender 審圖（hero、clay、線框、LOD、比例尺、遠景、樹冠下視角）、`turnaround_green/`、`turnaround_gold/`（各十方位）；`unity/` 是 Unity 實拍與檢查報告；`v001/`、`v002/` 是退件版的舊圖 |

匯出資料夾與 Unity 資料夾的 FBX、葉片圖集雜湊相同（SHA-256 已比對）。

重建與檢查：

```bash
blender --background --factory-startup --python art/source/trees-xianxia/build_xianxia_tree.py
```

```bash
blender -b art/source/trees-xianxia/blend/XT01_XianxiaGreatTree_v003.blend --python art/source/trees-xianxia/preview_xianxia_tree.py -- hero D:/yun-jing-trees/art/previews/trees-xianxia/XT01_XianxiaGreatTree
```

```bash
Unity.exe -batchmode -projectPath apps/game -executeMethod YunJing.Editor.XianxiaTreeCheck.Run -quit -logFile unity-xt01.log
```

審圖模式：`hero`、`ten`、`tengold`、`clay`、`wire`、`lods`、`ruler`、`far`。輸出資料夾請用絕對路徑。Unity 檢查程式只把目前版本的 FBX 與貼圖複製進 `Models/XianxiaGreatTreeV3/`，設定匯入、建立材質與兩個 prefab，再做檢查與拍照（輸出到 `artifacts/xianxia-tree-unity/`，該資料夾不進版本庫）。

## 尺寸與構造

- 樹高 15.75 m，樹冠 26.4 × 26.4 m，主幹基部半徑約 1.6 m，6 條地表根往外伸 1.2–2.2 m。
- 原點在樹幹底部中心，z = 0 是地面；根往下埋到 z = −0.3。1 單位 = 1 m，Blender −Y 是正面（FBX／Unity 是 −Z）。
- 主幹：短而粗、略向一側傾斜、往上收細，帶板根、淺肋、兩個樹瘤；約 6.6 m 處分出主枝，主枝從葉叢縫隙露出。
- 樹冠：34 團扁平大葉團（頂部 1＋周圍 4、中圈 8、外圈 10、貼近主幹的低圈 6、外緣下垂 5，高度與大小錯開），每團上鋪數個中葉叢，約兩成葉叢往外凸，輪廓起伏。

## 面數、物件、材質、貼圖

| LOD | 三角面 | 上限 | 頂點（Unity） | 物件 | 材質槽 | 內容 |
|---|---|---|---|---|---|---|
| LOD0 | 23,985 | 25,000 | 35,835 | 1 | 2 | 樹皮 10,798 面＋5,605 張葉卡＋地表根 |
| LOD1 | 7,383 | 8,000 | 11,405 | 1 | 2 | 樹皮 3,000 面＋1,899 張大葉卡＋地表根 |
| LOD2 | 2,400 | 2,500 | 3,819 | 1 | 2 | 樹皮 820 面＋790 張大葉卡 |
| LOD3 | 4 | 200 | 8 | 1 | 1 | 兩片十字交叉遠景圖 |
| 碰撞 | 36 | — | — | 1 | — | 包住主幹的 10 邊柱（半徑 1.47 m，0–3.5 m），渲染關閉 |

一棵樹＝1 個 prefab、5 個子物件（LOD0–3＋碰撞）。Unity 材質共 5 個：

| 材質 | Shader | 用在 |
|---|---|---|
| `M_XT01_Bark` | `YunJing/XianxiaTreeBark` | 綠樹、金樹共用 |
| `M_XT01_Leaves_Green` | `YunJing/XianxiaTreeLeaves` | 綠樹 LOD0–2 |
| `M_XT01_Leaves_Gold` | `YunJing/XianxiaTreeLeaves` | 金樹 LOD0–2 |
| `M_XT01_Impostor_Green` | `YunJing/XianxiaTreeLeaves`（Impostor 開） | 綠樹 LOD3 |
| `M_XT01_Impostor_Gold` | `YunJing/XianxiaTreeLeaves`（Impostor 開，貼圖位移 u 0.5） | 金樹 LOD3 |

| 貼圖 | 原檔大小 | Unity 匯入 | 說明 |
|---|---|---|---|
| `XT01_Bark_BaseColor.png` | 1024×1024 | 1024 | 手繪樹皮，暖褐、裂紋柔和 |
| `XT01_Bark_Normal.png` | 1024×1024 | 1024 | 法線（OpenGL，+Y） |
| `XT01_Bark_MetallicSmoothness.png` | 1024×1024 | 1024 | R 金屬 0，A 光滑度（低） |
| `XT01_Leaves_BaseColor.png` | 2048×2048 | **1024** | 上半 8 格小葉叢（LOD0）、第三列 4 格大葉叢（LOD1／LOD2），都是**灰階**；最下一列是 LOD3 遠景圖（左綠右金，已上色）。alpha 剪裁 0.5 |

葉片圖集原檔是 2048，但專案的 `QingxiImportBudget.cs` 會把 `Assets/YunJing/Models/` 下所有貼圖壓到最大 1024 並開 crunch，所以遊戲裡實際是 1024。檢查程式照這個規則驗證，沒有去改專案規則。

## 綠葉與金葉：怎麼用、怎麼調

- 直接拖 `XT01_XianxiaGreatTree_Green.prefab` 或 `_Gold.prefab` 進場景。兩個 prefab 是同一個 FBX、同一套貼圖，只換葉材質與遠景材質。
- 葉色不是畫在貼圖上：灰階葉片由 Shader 依三段漸層上色，所以換色只要改材質數值，不必重畫貼圖。
- 需要第三種顏色（例如秋紅），複製 `M_XT01_Leaves_Gold` 改顏色，再把 prefab LOD0–2 的葉材質換掉。LOD3 遠景圖是渲染好的綠／金兩張，新顏色要重渲遠景（在 `build_xianxia_tree.py` 的 `LOOKS` 加一組）。

`YunJing/XianxiaTreeLeaves` 主要參數（材質上的實際值）：

| 參數 | 作用 | 綠 | 金 |
|---|---|---|---|
| Deep / Mid / Tip Color | 葉叢底面與凹縫 → 側面 → 頂部受光的三段顏色 | #2F6A58 / #77B046 / #B7DA58 | #C47528 / #EDAE22 / #FFE35E |
| Variation A / B、Amount | 每叢葉子的色偏（綠：偏黃、偏青；金：偏黃綠、偏橘），0.5 灰＝不偏 | #C2C25A / #64A07E、0.35 | #CFC948 / #E5843A、0.40 |
| Mid Point | 三段漸層中間色的位置 | 0.48 | 0.46 |
| Light mask offset | 整棵樹變亮（+）或變深（−） | 0 | 0 |
| Leaf-by-leaf light | 葉叢內每簇小枝的明暗（0＝整叢一樣亮） | 0.55 | 0.55 |
| Painted value on colour | 手繪明暗疊上顏色的程度 | 0.3 | 0.3 |
| Wrap / Shadow tint / Ambient | 受光柔和度、陰影偏藍的程度、環境光 | 0.5 / (0.62,0.74,0.9) / 1 | 同左 |
| Back-light glow | 逆光時葉子透光 | 0.35 | 0.35 |
| Cast shadow strength | 樹冠自身陰影的深淺（太深會變成黑斑） | 0.55 | 0.55 |
| Graze min / max | 葉卡側面對鏡頭時漸漸剪掉，避免拉長的細條 | 0.3 / 0.66 | 同左 |
| Wind strength / speed / flutter / dir | 擺動幅度（m）、速度、葉片抖動、風向 | 0.22 / 1 / 0.035 / (1,0,0.35) | 同左 |

想讓樹冠更亮或更深，先調 `Light mask offset`；想讓葉叢之間的凹縫更深或更淺，只改 `Deep Color`。**風的參數在樹皮與葉兩種材質上要保持一樣**（`_WindStrength`、`_WindSpeed`、`_WindDir`），不然枝與葉會分開。

## 技術細節

- 葉卡：雙面（Cull Off）、alpha 剪裁 0.5，匯入開 Mip Maps Preserve Coverage（0.5），遠看不會變稀。正反兩面用同一個法線受光（葉叢球面法線為主，加一點整體樹冠形狀），相鄰葉卡不會一片亮一片暗。
- 頂點色 `Wind`（FBX 線性色）：R 擺動權重（主幹 0、主枝 0.02–0.25、細枝到約 0.55、葉卡 0.56–1），G 相位，B 受光遮罩（葉：葉叢自身的朝上程度＋朝外程度＋高度－在樹冠裡的深度），A 每叢色偏（葉）。
- 風：Shader 內的頂點擺動（兩個正弦疊成陣風＋葉片小抖動），每棵樹依位置錯開相位。沒有用 Unity WindZone 或骨架。
- 碰撞：`_Collision` 是凸面 MeshCollider（renderer 關閉）；只擋主幹，樹冠與地表根不擋人。若改用 CapsuleCollider，數值在 `model_info.json` 的 `collision_capsule`（半徑 1.47、高 3.5）。
- LOD：切換距離 60 / 110 / 280 m，1500 m 外淡出。檢查程式依專案 LOD bias 2.0 換算 LODGroup 高度 0.980 / 0.784 / 0.308 / 0.057。四層最高點 15.75 / 15.82 / 15.86 / 15.80 m。LOD3 不投影。
- 樹皮 UV：主幹依高度與方位角展開；每個三角面只用同一根枝段算 UV（`face_uv`），分叉處不會出現斜紋。主幹與枝的接縫在減面時鎖住（`seal`），不會裂出細縫。

## 做過的檢查

Blender（`validation.json`）：LOD 面數上限、樹高 14–17 m、根到 −0.3、FBX 回匯物件、FBX 回匯高度誤差 0.000 m、FBX 帶 Wind 頂點色，全部通過。

Unity 6000.3.28f1（URP，Gamma 色彩空間；報告在 `art/previews/trees-xianxia/XT01_XianxiaGreatTree/unity/unity-verify-report.txt`），38 項 PASS、0 項失敗：

- 綠、金兩個 prefab：LODGroup 4 層、每層一個 renderer；各層面數與 model_info 一致；材質與 Shader 正確。
- 每個頂點都有頂點色；主幹 2 m 以下擺動權重 0；葉卡權重 0.56–1；法線全部單位長度。
- 樹高 15.75 m、樹冠 26.4 × 26.4 m、根到 −0.30 m；碰撞體凸面且隱藏；葉圖集 Preserve Coverage 0.5、匯入 1024。
- 走路測試（腳本控制的 CharacterController，1.75 m）：朝主幹走會在離軸心 1.67 m 處停下；從主幹旁 1.5 m 走過會穿過樹冠下繼續前進。
- 風：同一畫面在擺動 0 與 10 倍預設值（2.2 m）各拍一次，確認主幹不動、樹冠與枝一起擺。
- 拍照審圖：正、右、後、左、四分之三、樹冠下 1.7 m 視高（綠、金）、樹皮與根近照、樹冠邊緣近照、LOD0–3、50 / 100 / 250 m（LODGroup 實際顯示 LOD0 / LOD1 / LOD2）、與 VL02 民居及 1.75 m 人形並排、120 m 遠景、放進 Qingxi 庭院灰模（金樹在院內西北角，綠樹在東北牆外；院外鋪了一塊暫時地面，場景不存檔）。

這一輪審圖後修掉的問題：葉叢太稀、樹冠中段露出太多枝（加密葉叢）；葉叢明暗對比太弱（加深底面）；輪廓太規整像扁蘑菇（大葉團高度、大小、間距錯開）；從樹下仰看有拉長的葉卡條紋（下半部葉卡朝下）；主枝轉折有方塊角（路徑平滑加倍）；LOD1／LOD2 比 LOD0 高 0.5–1.3 m（大葉卡內收＋高度上限）。

## 請在編輯器裡確認

1. 放進正式場景後的比例與顏色：在實際地形、天空與後處理下看綠／金兩款，必要時用上表的參數調亮度與色偏。
2. Play 模式下的風：批次檢查只拍了靜態畫面（含 10 倍擺動），擺動節奏與幅度請進 Play 看一次，覺得太晃或太僵就調 `_WindStrength`／`_WindSpeed`（兩個材質一起調）。
3. LOD 切換：跑一段由遠到近的移動，看換層時跳動是否可以接受（目前沒有 cross-fade）。
4. 效能：沒有做實機測試，不提供 FPS 數字；請在目標裝置上量。大量種植時建議 LOD0 只給玩家附近的少數幾棵。
5. Unity 裡退件的 `Models/XianxiaGreatTreeV1/`、`XianxiaGreatTreeV2/` 依版本規則保留，確定不要後可以刪除。

## 自評（模型總指令六項，每項 95 分門檻）

| 項目 | 分數 | 依據 |
|---|---|---|
| 造型與輪廓（25） | 95 | 寬傘形樹冠由一叢叢葉叢堆成，輪廓起伏、有凹縫，主枝從縫隙露出；四面看都成立（十方位圖）；主幹短粗彎曲、板根明顯 |
| 拓撲與結構（20） | 95 | 枝幹融合成一個網格，分叉處不裂縫、不斜紋；LOD 逐級減面，四層輪廓與高度一致；法線全部正常 |
| 材質與光影（20） | 95 | 灰階圖集＋三段漸層上色；每叢頂亮底深、叢間暗縫，整體再上亮下深；金樹黃 → 金 → 橘；遠景圖沒有黑斑 |
| 風格一致性（15） | 95 | 明亮、柔和手繪感，葉叢是蓬鬆花椰菜狀；比例與既有民居、人形對照合理 |
| 動畫／互動（10） | 95 | 頂點擺動、枝葉同步（10 倍擺動驗證）、主幹碰撞走路測試通過；Play 模式動態效果仍請使用者確認 |
| 效能與匯出（10） | 95 | 各 LOD 在上限內、物件與材質少、貼圖照專案規則；FBX／GLB 回匯檢查通過；沒有實機數據 |
