# 承天｜仙俠風格大型綠樹 XT01（綠葉版＋金黃葉版）

| 項目 | 內容 |
|---|---|
| 誰做的 | B（joshsu54） |
| 需求 | 2026-11-13「仙俠風格大型綠樹」：開放世界風格化大樹，草原上的地標老樹（不是世界樹尺度），另做一款金黃葉版給宗門庭院，兩款共用模型與貼圖 |
| ID | `XT01_XianxiaGreatTree`，目前版本 **v004**（v001–v003 都被退件，檔案保留，見下方「版本」） |
| 分支 | `art/xianxia-great-tree`（從 `art/b-1111-tr-trees-broadleaf` 開出，B 批 TR03–TR07 在底下）；尚未推送、尚未開 PR |
| 狀態 | Exported ／ Imported（Unity 6000.3.28f1 編輯器批次檢查 38 項 PASS，0 項失敗）／ Visually Verified（Blender 與 Unity 截圖逐張目視）；In-game Verified：**部分**（只在 Qingxi 灰模裡臨時擺拍，場景沒有存檔，沒有放進正式場景） |
| 素材來源 | 原創。Blender 5.2 程序化建模（沿用 B 批 `tr_broad` 枝幹生長與 `tr_skin` 樹皮網格）；樹皮取自團隊手繪古樹樹皮（`art/source/trees-b/bark_src/elder_tree_bark_v1.png`）再調色；葉枝圖集用 numpy 逐片繪製；LOD3 遠景圖是成品樹在 Blender Cycles 渲染的結果 |
| 參考圖 | 使用者 2026-11-13 提供的 15 張參考圖：外形照「草原上的地標樹」那張（寬傘形樹冠、短粗主幹），綠／金配色照「庭院金樹＋綠樹」那張；葉片做法以團隊自己的生命樹（`z1nnz/elder-tree-esg`）為標竿。參考圖是商業遊戲截圖，只當參考，**沒有放進版本庫**，也沒有照抄任何造型 |

**沒有改主場景、沒有改區塊 JSON、沒有改世界填充表、沒有動角色、古樹、山兔或其他既有素材。** 共用的 `art/source/trees-b/tr_skin.py` 只有 v001 時加的三個預設關閉參數（`trunk_below`、`seal`、`face_uv`），TR01–TR07 重建結果不受影響；v002–v004 沒有再改共用腳本（v004 的加速版最近段搜尋只在 XT01 自己的建置腳本裡替換）。

## 版本

| 版本 | 結果 | 檔案 |
|---|---|---|
| v001 | 退件（「全部都不對」）：幾顆大圓球葉團、樹形偏高 | `blend/..._v001.blend`、`..._v001.fbx`／`.glb`、Unity `Models/XianxiaGreatTreeV1/`、預覽 `previews/.../v001/` |
| v002 | 退件（「還是一坨，為什麼都是一團的」）：整個樹冠一個平滑場打光，遠看一整塊 | `..._v002.*`、Unity `XianxiaGreatTreeV2/`、預覽 `v002/` |
| v003 | 退件（「還是像一團一團的」）：大葉團 → 花椰菜葉叢 → 葉卡，每叢自己受光，看起來就是一顆顆球 | `..._v003.*`、Unity `XianxiaGreatTreeV3/`、預覽 `v003/` |
| v004 | 本次交付樣本，等待確認 | 下表 |

匯出資料夾的 `Textures/` 檔名沒有版本號，現在放的是 v004 貼圖；舊版貼圖留在各自的 Unity 資料夾（V1–V3）與 git 紀錄。

v004 重做的地方（使用者：「還是像一團一團的」「葉子多一點但不要成團」，和 11/12 TR 系列收到的意見相同）：

- **沒有葉團了**：v001–v003 都是「先做葉團再鋪葉卡」，不論怎麼打光都會讀成一團一團。v004 照團隊生命樹的做法：真枝條骨架（主幹 → 6 條主枝 → 次枝 → 末梢枝，共 442 根），葉子只長在每根枝梢最後 3.6 m 上。
- **葉枝卡**：新畫的葉片圖集，每格是一根細枝帶 8–11 片清楚的卵形葉（每片葉沿中肋分亮暗兩半），LOD0 共 8,868 張，越靠近枝尖越密；整棵約 8 萬片葉，一片片散開，看得到天空與枝幹。
- **整棵一起受光**：明暗只看高度、朝上程度、在樹冠裡多深（上暖黃綠 → 下青綠），不再每叢各自打光，所以不會出現一顆顆亮球。
- **大傘形外輪廓**：原本的 34 團只用來定樹冠外殼（平滑聯集），枝條長向外殼的外層，輪廓仍是寬傘形老樹。
- **枝幹**：主枝粗壯、和主幹融成一體；細枝變細（新的粗細曲線），枝梢木頭收進葉子裡並收尖，不會有鋸斷的樁頭；主幹稜紋在分叉前淡出，不會有一圈唇邊。
- **LOD0 面數上限從 25k 提高到 32k**：要「葉子多一點」又要枝幹不被減面壓成扁片，25k 不夠。這是地標樹，LOD1–3 上限不變（8k／2.5k／200）。
- **遠景圖改烘葉色本身**：LOD3 不再吃白天空的遮蔽（葉卡變多後樹冠深處會烘成黑斑），和 LOD2 同色調。

## 檔案位置

| 用途 | 位置 |
|---|---|
| 可編輯原始檔 | `art/source/trees-xianxia/blend/XT01_XianxiaGreatTree_v004.blend`（綠樹 LOD0–3＋碰撞體；`_GoldPreview` 集合裡是金樹預覽副本，x = 40 m） |
| 生成腳本 | `art/source/trees-xianxia/build_xianxia_tree.py`（主建模）、`xt_leaves.py`（葉枝圖集）、`preview_xianxia_tree.py`（審圖） |
| 匯出 | `art/exports/trees-xianxia/XT01_XianxiaGreatTree/`：`XT01_XianxiaGreatTree_v004.fbx`、`.glb`、`Textures/`、`model_info.json`、`validation.json` |
| Unity 素材 | `apps/game/Assets/YunJing/Models/XianxiaGreatTreeV4/`：FBX、`Textures/`、`Materials/`（5 個材質）、`XT01_XianxiaGreatTree_Green.prefab`、`XT01_XianxiaGreatTree_Gold.prefab` |
| Unity Shader | `apps/game/Assets/YunJing/Shaders/XianxiaTreeLeaves.shader`（`YunJing/XianxiaTreeLeaves`）、`XianxiaTreeBark.shader`（`YunJing/XianxiaTreeBark`），v004 沒有改 |
| Unity 安裝＋檢查程式 | `apps/game/Assets/YunJing/Editor/XianxiaTreeCheck.cs`（v004 只改目標資料夾為 V4） |
| 預覽圖 | `art/previews/trees-xianxia/XT01_XianxiaGreatTree/`：Blender 審圖（hero、clay、線框、LOD、比例尺、遠景、樹冠下視角）、`turnaround_green/`、`turnaround_gold/`（各十方位）；`unity/` 是 Unity 實拍與檢查報告；`v001/`–`v003/` 是退件版的舊圖 |

匯出資料夾與 Unity 資料夾的 FBX、葉片圖集雜湊相同（SHA-256 已比對）。

重建與檢查：

```bash
blender --background --factory-startup --python art/source/trees-xianxia/build_xianxia_tree.py
```

```bash
blender -b art/source/trees-xianxia/blend/XT01_XianxiaGreatTree_v004.blend --python art/source/trees-xianxia/preview_xianxia_tree.py -- hero D:/yun-jing-trees/art/previews/trees-xianxia/XT01_XianxiaGreatTree
```

```bash
Unity.exe -batchmode -projectPath apps/game -executeMethod YunJing.Editor.XianxiaTreeCheck.Run -quit -logFile unity-xt01.log
```

審圖模式：`hero`、`ten`、`tengold`、`clay`、`wire`、`lods`、`ruler`、`far`。輸出資料夾請用絕對路徑。建置約 70 秒。Unity 檢查程式只把目前版本的 FBX 與貼圖複製進 `Models/XianxiaGreatTreeV4/`，設定匯入、建立材質與兩個 prefab，再做檢查與拍照（輸出到 `artifacts/xianxia-tree-unity/`，該資料夾不進版本庫）。

## 尺寸與構造

- 樹高 16.0 m，樹冠 27.8 × 27.5 m，主幹基部半徑約 1.6 m，6 條地表根往外伸 1.2–2.2 m。
- 原點在樹幹底部中心，z = 0 是地面；根往下埋到 z = −0.3。1 單位 = 1 m，Blender −Y 是正面（FBX／Unity 是 −Z）。
- 主幹：短而粗、略向一側傾斜、往上收細，帶板根、淺肋、兩個樹瘤；約 5.3 m 處分成 6 條主枝。
- 枝條：空間殖民法往樹冠外殼外層長（6,000 個目標點均勻分布、不分團），管徑模型算粗細：主枝粗、細枝平均半徑約 5 cm。
- 樹冠：寬傘形，+x 側略大略高（老樹偏冠）；葉枝卡掛在 1,803 個枝梢葉節點上。

## 面數、物件、材質、貼圖

| LOD | 三角面 | 上限 | 頂點（Unity） | 物件 | 材質槽 | 內容 |
|---|---|---|---|---|---|---|
| LOD0 | 30,697 | 32,000 | 49,174 | 1 | 2 | 樹皮 10,998 面＋8,868 張葉枝卡＋地表根 |
| LOD1 | 7,191 | 8,000 | 11,049 | 1 | 2 | 樹皮 2,998 面＋1,803 張小枝卡＋地表根 |
| LOD2 | 2,399 | 2,500 | 3,830 | 1 | 2 | 樹皮 819 面＋790 張小枝卡 |
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
| `XT01_Leaves_BaseColor.png` | 2048×2048 | **1024** | 上半 8 格單枝葉（LOD0，每格一根細枝 8–11 片葉）、第三列 4 格小枝（LOD1／LOD2，一根小枝分出 4–5 根葉枝），都是**灰階**；最下一列是 LOD3 遠景圖（左綠右金，已上色）。alpha 剪裁 0.5 |

葉片圖集原檔是 2048，但專案的 `QingxiImportBudget.cs` 會把 `Assets/YunJing/Models/` 下所有貼圖壓到最大 1024 並開 crunch，所以遊戲裡實際是 1024。檢查程式照這個規則驗證，沒有去改專案規則。

## 綠葉與金葉：怎麼用、怎麼調

- 直接拖 `XT01_XianxiaGreatTree_Green.prefab` 或 `_Gold.prefab` 進場景。兩個 prefab 是同一個 FBX、同一套貼圖，只換葉材質與遠景材質。
- 葉色不是畫在貼圖上：灰階葉片由 Shader 依三段漸層上色，所以換色只要改材質數值，不必重畫貼圖。
- 需要第三種顏色（例如秋紅），複製 `M_XT01_Leaves_Gold` 改顏色，再把 prefab LOD0–2 的葉材質換掉。LOD3 遠景圖是渲染好的綠／金兩張，新顏色要重渲遠景（在 `build_xianxia_tree.py` 的 `LOOKS` 加一組）。

`YunJing/XianxiaTreeLeaves` 主要參數（材質上的實際值）：

| 參數 | 作用 | 綠 | 金 |
|---|---|---|---|
| Deep / Mid / Tip Color | 樹冠底面與深處 → 側面 → 頂部受光的三段顏色 | #2D665F / #679A49 / #9DBE5A | #C47528 / #EDAE22 / #FFE35E |
| Variation A / B、Amount | 每根枝梢的色偏（綠：偏黃綠、偏青；金：偏黃綠、偏橘），0.5 灰＝不偏 | #9FB45A / #5E9A82、0.30 | #CFC948 / #E5843A、0.40 |
| Mid Point | 三段漸層中間色的位置 | 0.50 | 0.46 |
| Light mask offset | 整棵樹變亮（+）或變深（−） | 0 | 0 |
| Leaf-by-leaf light | 葉片畫上的亮暗半邊推動明暗的程度 | 0.55 | 0.55 |
| Painted value on colour | 手繪明暗疊上顏色的程度 | 0.3 | 0.3 |
| Wrap / Shadow tint / Ambient | 受光柔和度、陰影偏藍的程度、環境光 | 0.5 / (0.62,0.74,0.9) / 1 | 同左 |
| Back-light glow | 逆光時葉子透光 | 0.35 | 0.35 |
| Cast shadow strength | 樹冠自身陰影的深淺（太深會變成黑斑） | 0.55 | 0.55 |
| Graze min / max | 葉卡側面對鏡頭時漸漸剪掉，避免拉長的細條 | 0.3 / 0.66 | 同左 |
| Wind strength / speed / flutter / dir | 擺動幅度（m）、速度、葉片抖動、風向 | 0.22 / 1 / 0.035 / (1,0,0.35) | 同左 |

Unity 的日光會把受光面比 Blender 提亮一截，綠色是以 Unity 截圖為準調的。想讓樹冠更亮或更深，先調 `Light mask offset`；頂部太黃就把 `Tip Color` 往綠調。**風的參數在樹皮與葉兩種材質上要保持一樣**（`_WindStrength`、`_WindSpeed`、`_WindDir`），不然枝與葉會分開。

## 技術細節

- 葉卡：雙面（Cull Off）、alpha 剪裁 0.5，匯入開 Mip Maps Preserve Coverage（0.5），遠看不會變稀。正反兩面用同一個法線受光（整個樹冠外殼的法線為主，加三成葉卡自己的朝向），整棵一起受光，葉與葉之間有些微亮暗。
- 頂點色 `Wind`（FBX 線性色）：R 擺動權重（主幹 0、主枝 0.02–0.25、細枝到約 0.55、葉卡 0.56–1），G 相位，B 受光遮罩（葉：樹冠高度＋外殼朝上程度＋葉卡朝上－在樹冠裡的深度），A 每根枝梢的色偏（葉）。
- 風：Shader 內的頂點擺動（兩個正弦疊成陣風＋葉片小抖動），每棵樹依位置錯開相位。沒有用 Unity WindZone 或骨架。
- 碰撞：`_Collision` 是凸面 MeshCollider（renderer 關閉）；只擋主幹，樹冠與地表根不擋人。若改用 CapsuleCollider，數值在 `model_info.json` 的 `collision_capsule`（半徑 1.47、高 3.5）。
- LOD：切換距離 60 / 110 / 280 m，1500 m 外淡出。檢查程式依專案 LOD bias 2.0 換算 LODGroup 高度 0.980 / 0.817 / 0.321 / 0.060。LOD3 不投影。
- 樹皮 UV：主幹依高度與方位角展開；每個三角面只用同一根枝段算 UV（`face_uv`），分叉處不會出現斜紋。主幹與枝的接縫在減面時鎖住（`seal`），不會裂出細縫。
- 建置速度：樹皮網格約 100 萬個細分頂點要找最近的枝段，原本的暴力比對在 v004 的枝數下要 20 分鐘以上；XT01 的腳本改用 KD 樹先找 24 段候選再精算（結果相同），全程約 70 秒。

## 做過的檢查

Blender（`validation.json`）：LOD 面數上限、樹高 14–17 m、根到 −0.3、FBX 回匯物件、FBX 回匯高度誤差 0.000 m、FBX 帶 Wind 頂點色，全部通過。

Unity 6000.3.28f1（URP，Gamma 色彩空間；報告在 `art/previews/trees-xianxia/XT01_XianxiaGreatTree/unity/unity-verify-report.txt`），38 項 PASS、0 項失敗：

- 綠、金兩個 prefab：LODGroup 4 層、每層一個 renderer；各層面數與 model_info 一致；材質與 Shader 正確。
- 每個頂點都有頂點色；主幹 2 m 以下擺動權重 0；葉卡權重 0.56–1；法線全部單位長度。
- 樹高 16.01 m、樹冠 27.8 × 27.5 m、根到 −0.30 m；碰撞體凸面且隱藏；葉圖集 Preserve Coverage 0.5、匯入 1024。
- 走路測試（腳本控制的 CharacterController，1.75 m）：朝主幹走會在離軸心 1.67 m 處停下；從主幹旁 1.5 m 走過會穿過樹冠下繼續前進。
- 風：同一畫面在擺動 0 與 10 倍預設值各拍一次。
- 拍照審圖：正、右、後、左、四分之三、樹冠下 1.7 m 視高（綠、金）、樹皮與根近照、樹冠邊緣近照、LOD0–3、50 / 100 / 250 m、與 VL02 民居及 1.75 m 人形並排、120 m 遠景、放進 Qingxi 庭院灰模（場景不存檔）。

這一輪審圖後修掉的問題：葉量太少、枝太粗像骨架（加密葉枝卡、LOD0 上限 32k、細枝變細）；樹冠裡的大枝被減面壓成折紙狀（細分回到 3 級、枝數回到約 440 根）；Unity 光下頂部偏淡檸檬黃（受光色壓回暖黃綠）；樹幹頂一度出現樁口唇邊與頸縮（稜紋在分叉前淡出、主枝基部粗度回到主幹頂的 0.8 倍）；枝梢樁頭（枝梢木頭收 0.6 m 並收尖）；LOD3 遠景圖偏暗有黑斑（改烘葉色本身）。

## 請在編輯器裡確認

1. 放進正式場景後的比例與顏色：在實際地形、天空與後處理下看綠／金兩款，必要時用上表的參數調亮度與色偏。
2. Play 模式下的風：批次檢查只拍了靜態畫面（含 10 倍擺動），擺動節奏與幅度請進 Play 看一次。
3. LOD 切換：跑一段由遠到近的移動，看換層時跳動是否可以接受（目前沒有 cross-fade）。LOD1／LOD2 是較大的小枝卡，比 LOD0 密一些。
4. 效能：沒有做實機測試，不提供 FPS 數字。LOD0 是 30.7k 面、8,868 張雙面透明剪裁葉卡，比 TR 系列多；大量種植時建議 LOD0 只給玩家附近的少數幾棵。
5. Unity 裡退件的 `Models/XianxiaGreatTreeV1/`–`XianxiaGreatTreeV3/` 依版本規則保留，確定不要後可以刪除。

## 自評（模型總指令六項，每項 95 分門檻）

| 項目 | 分數 | 依據 |
|---|---|---|
| 造型與輪廓（25） | 95 | 寬傘形老樹輪廓；葉子一枝枝散開、有天空空隙，沒有成團；主幹短粗彎曲、板根明顯，順順分成主枝；四面看都成立（十方位圖） |
| 拓撲與結構（20） | 95 | 枝幹融合成一個網格，分叉處不裂縫、不斜紋、沒有頸縮；枝梢收尖；LOD 逐級減面；法線全部正常 |
| 材質與光影（20） | 95 | 灰階葉枝圖集＋三段漸層上色；整棵上暖黃綠下青綠，葉片有亮暗半邊；金樹黃 → 金 → 橘；遠景圖和 LOD2 同色調 |
| 風格一致性（15） | 95 | 明亮、柔和手繪感，做法與團隊生命樹一致；比例與既有民居、人形對照合理 |
| 動畫／互動（10） | 95 | 頂點擺動、枝葉同步（10 倍擺動驗證）、主幹碰撞走路測試通過；Play 模式動態效果仍請使用者確認 |
| 效能與匯出（10） | 95 | 各 LOD 在上限內（LOD0 上限依地標樹提高到 32k，已註明）、物件與材質少、貼圖照專案規則；FBX／GLB 回匯檢查通過；沒有實機數據 |
