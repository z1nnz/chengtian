# 承天｜仙俠風格大型綠樹 XT01（綠葉版＋金黃葉版）

| 項目 | 內容 |
|---|---|
| 誰做的 | B（joshsu54） |
| 需求 | 2026-11-13「仙俠風格大型綠樹」：開放世界風格化大樹，草原上的地標老樹（不是世界樹尺度），另做一款金黃葉版給宗門庭院，兩款共用模型與貼圖 |
| ID | `XT01_XianxiaGreatTree`（樹 XT01，版本 v001，首次交付，沒有舊版） |
| 分支 | `art/xianxia-great-tree`（從 `art/b-1111-tr-trees-broadleaf` 開出，B 批 TR03–TR07 在底下）；尚未推送、尚未開 PR |
| 狀態 | Exported ／ Imported（Unity 6000.3.28f1 編輯器批次檢查，0 項失敗）／ Visually Verified（Blender 與 Unity 審圖）；In-game Verified：**未驗**（只在 Qingxi 灰模裡擺拍，場景沒有存檔，沒有放進正式場景） |
| 素材來源 | 原創。Blender 5.2 程序化建模（沿用 B 批 `tr_broad` 枝幹生長與 `tr_skin` 樹皮網格）；樹皮取自團隊手繪古樹樹皮（`art/source/trees-b/bark_src/elder_tree_bark_v1.png`）再調色；葉片圖集用 numpy 逐片繪製；LOD3 遠景圖是成品樹在 Blender Cycles 渲染的結果 |
| 參考圖 | 需求附的 10 張參考圖**沒有傳到工作環境**。外形與配色改依本機既有參考（草原上的綠色地標樹、綠／金兩色樹、開放世界場景截圖）判斷，那些是商業遊戲截圖，只當參考、沒有放進版本庫。若需要照附件微調，請把圖檔放進工作資料夾 |

**沒有改主場景、沒有改區塊 JSON、沒有改世界填充表、沒有動角色、古樹、山兔或其他既有素材。** 共用的 `art/source/trees-b/tr_skin.py` 只加了三個預設關閉的參數（`trunk_below`、`seal`、`face_uv`），TR01–TR07 重建結果不受影響。

## 檔案位置

| 用途 | 位置 |
|---|---|
| 可編輯原始檔 | `art/source/trees-xianxia/blend/XT01_XianxiaGreatTree_v001.blend`（綠樹 LOD0–3＋碰撞體；`_GoldPreview` 集合裡是金樹預覽副本，x = 40 m） |
| 生成腳本 | `art/source/trees-xianxia/build_xianxia_tree.py`（主建模）、`xt_leaves.py`（葉片圖集）、`preview_xianxia_tree.py`（審圖） |
| 匯出 | `art/exports/trees-xianxia/XT01_XianxiaGreatTree/`：`XT01_XianxiaGreatTree_v001.fbx`、`.glb`、`Textures/`、`model_info.json`、`validation.json` |
| Unity 素材 | `apps/game/Assets/YunJing/Models/XianxiaGreatTreeV1/`：FBX、`Textures/`、`Materials/`（5 個材質）、`XT01_XianxiaGreatTree_Green.prefab`、`XT01_XianxiaGreatTree_Gold.prefab` |
| Unity Shader | `apps/game/Assets/YunJing/Shaders/XianxiaTreeLeaves.shader`（`YunJing/XianxiaTreeLeaves`）、`XianxiaTreeBark.shader`（`YunJing/XianxiaTreeBark`） |
| Unity 安裝＋檢查程式 | `apps/game/Assets/YunJing/Editor/XianxiaTreeCheck.cs` |
| 預覽圖 | `art/previews/trees-xianxia/XT01_XianxiaGreatTree/`：Blender 審圖（hero、clay、線框、LOD、比例尺、遠景、綠／金各十方位）；`unity/` 是 Unity 實拍與檢查報告 |

重建與檢查：

```bash
blender --background --factory-startup --python art/source/trees-xianxia/build_xianxia_tree.py
```

```bash
blender -b art/source/trees-xianxia/blend/XT01_XianxiaGreatTree_v001.blend --python art/source/trees-xianxia/preview_xianxia_tree.py -- hero D:/yun-jing-trees/art/previews/trees-xianxia/XT01_XianxiaGreatTree
```

```bash
Unity.exe -batchmode -projectPath apps/game -executeMethod YunJing.Editor.XianxiaTreeCheck.Run -quit -logFile unity-xt01.log
```

審圖模式：`hero`、`ten`、`tengold`、`clay`、`wire`、`lods`、`ruler`、`far`。輸出資料夾請用絕對路徑。Unity 檢查程式會把匯出複製進 `Models/XianxiaGreatTreeV1/`、設定匯入、建立材質與兩個 prefab，再做檢查與拍照（輸出到 `artifacts/xianxia-tree-unity/`，該資料夾不進版本庫）。

## 尺寸與構造

- 樹高 16.68 m，樹冠 23.5 × 23.8 m，主幹基部半徑約 1.15 m，6 條地表根往外伸 2.0–3.4 m。
- 原點在樹幹底部中心，z = 0 是地面；根往下埋到 z = −0.3。1 單位 = 1 m，Blender −Y 是正面（FBX／Unity 是 −Z）。
- 主幹：彎曲、往上收細，帶板根、淺肋、兩個樹瘤；在約 5.3 m 分成 5 支主枝，主枝從樹冠縫隙露出。
- 樹冠：25 團葉叢再分成 26 個以上大小不等的葉團，團與團之間留縫；約 22% 葉卡往外突出打破輪廓，14% 在內層補深色。上亮下深、外亮內深。

## 面數、物件、材質、貼圖

| LOD | 三角面 | 上限 | 頂點 | 物件 | 材質槽 | 內容 |
|---|---|---|---|---|---|---|
| LOD0 | 19,099 | 25,000 | 26,533 | 1 | 2 | 樹皮 11,500 面＋2,591 張葉卡＋根 |
| LOD1 | 5,379 | 8,000 | 7,625 | 1 | 2 | 樹皮 3,000 面＋827 張葉卡（整團大卡）＋根 |
| LOD2 | 1,384 | 2,500 | 1,794 | 1 | 2 | 樹皮 820 面＋282 張葉卡 |
| LOD3 | 4 | 200 | 8 | 1 | 1 | 兩片十字交叉遠景圖 |
| 碰撞 | 36 | — | — | 1 | — | 包住主幹的 10 邊柱（半徑 1.07 m，0–3.5 m），渲染關閉 |

（頂點數是 Unity 匯入後的數字；三角面數 Blender 與 Unity 一致。）

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
| `XT01_Leaves_BaseColor.png` | 2048×2048 | **1024** | 上半 8 格小葉團（LOD0）、第三列 4 格大葉團（LOD1／LOD2），都是**灰階**；最下一列是 LOD3 遠景圖（左綠右金，已上色）。alpha 剪裁 0.5 |

葉片圖集原檔是 2048，但專案的 `QingxiImportBudget.cs` 會把 `Assets/YunJing/Models/` 下所有貼圖壓到最大 1024 並開 crunch，所以遊戲裡實際是 1024。檢查程式照這個規則驗證，沒有去改專案規則。

## 綠葉與金葉：怎麼用、怎麼調

- 直接拖 `XT01_XianxiaGreatTree_Green.prefab` 或 `_Gold.prefab` 進場景。兩個 prefab 是同一個 FBX、同一套貼圖，只換葉材質與遠景材質。
- 葉色不是畫在貼圖上：灰階葉片由 Shader 依三段漸層上色，所以換色只要改材質數值，不必重畫貼圖。
- 需要第三種顏色（例如秋紅），複製 `M_XT01_Leaves_Gold` 改顏色，再把 prefab LOD0–2 的葉材質換掉。LOD3 遠景圖是渲染好的綠／金兩張，新顏色要重渲遠景（在 `build_xianxia_tree.py` 的 `LOOKS` 加一組）。

`YunJing/XianxiaTreeLeaves` 主要參數：

| 參數 | 作用 | 綠 | 金 |
|---|---|---|---|
| Deep / Mid / Tip Color | 樹冠內側陰面 → 中間 → 頂部受光的三段顏色 | #2C5A52 / #5B9A45 / #B8D86A | #8A5222 / #D8952A / #F2D35C |
| Variation A / B、Amount | 每團葉子的色偏（綠：偏黃、偏青；金：偏黃綠、偏橘），0.5 灰＝不偏 | #B9A35A / #6F9E86、0.45 | #C9B14E / #D9773A、0.45 |
| Mid Point | 三段漸層中間色的位置 | 0.5 | 0.5 |
| Light mask offset | 整棵樹變亮（+）或變深（−） | 0 | 0 |
| Leaf-by-leaf light | 每片葉子的明暗（0＝整團一樣亮） | 0.8 | 0.8 |
| Painted value on colour | 手繪明暗疊上顏色的程度 | 0.45 | 0.45 |
| Wrap / Shadow tint / Ambient | 受光柔和度、陰影偏藍的程度、環境光 | 0.5 / (0.62,0.74,0.9) / 1 | 同左 |
| Back-light glow | 逆光時葉子透光 | 0.35 | 0.35 |
| Cast shadow strength | 樹冠自身陰影的深淺（太深會變成黑斑） | 0.55 | 0.55 |
| Graze min / max | 葉卡側面對鏡頭時漸漸剪掉，避免拉長的細條 | 0.24 / 0.6 | 同左 |
| Wind strength / speed / flutter / dir | 擺動幅度（m）、速度、葉片抖動、風向 | 0.22 / 1 / 0.035 / (1,0,0.35) | 同左 |

**風的參數在樹皮與葉兩種材質上要保持一樣**（`_WindStrength`、`_WindSpeed`、`_WindDir`），不然枝與葉會分開。

## 技術細節

- 葉卡：雙面（Cull Off）、alpha 剪裁 0.5，匯入開 Mip Maps Preserve Coverage（0.5），遠看不會變稀。法線是「葉團法線」（每團像一顆柔和的球），所以受光像手繪的大塊體積，不會一片片閃。
- 頂點色 `Wind`（FBX 線性色）：R 擺動權重（主幹 0、主枝 0.02–0.25、細枝到約 0.55、葉卡 0.56–1），G 相位，B 樹冠受光遮罩（葉），A 每團色偏（葉）。
- 風：Shader 內的頂點擺動（兩個正弦疊成陣風＋葉片小抖動），每棵樹依位置錯開相位。沒有用 Unity WindZone 或骨架。
- 碰撞：`_Collision` 是凸面 MeshCollider（renderer 關閉）；只擋主幹，樹冠與地表根不擋人。若改用 CapsuleCollider，數值在 `model_info.json` 的 `collision_capsule`（半徑 1.074、高 3.5、中心 z 1.75）。
- LOD：切換距離 60 / 110 / 280 m，1500 m 外淡出。檢查程式依專案 LOD bias 2.0 換算 LODGroup 高度 0.980 / 0.618 / 0.243 / 0.045。LOD3 不投影。
- 樹皮 UV：主幹依高度與方位角展開；每個三角面只用同一根枝段算 UV（`face_uv`），分叉處不會出現斜紋。主幹與枝的接縫在減面時鎖住（`seal`），不會裂出細縫。

## 做過的檢查

Blender（`validation.json`）：LOD 面數上限、樹高 15–18.5 m、根到 −0.3、FBX 回匯物件、FBX 回匯高度誤差 0.0004 m、FBX 帶 Wind 頂點色，全部通過。

Unity 6000.3.28f1（URP，Gamma 色彩空間；報告在 `art/previews/trees-xianxia/XT01_XianxiaGreatTree/unity/unity-verify-report.txt`），0 項失敗：

- 綠、金兩個 prefab：LODGroup 4 層、每層一個 renderer；各層面數與 model_info 一致；材質與 Shader 正確。
- 每個頂點都有頂點色；主幹 2 m 以下擺動權重 0；葉卡權重 0.56–1；法線全部單位長度（0 個壞的）。
- 樹高 16.68 m、樹冠 23.5 × 23.8 m、根到 −0.30 m；碰撞體凸面且隱藏；葉圖集 Preserve Coverage 0.5、匯入 1024。
- 走路測試（腳本控制的 CharacterController，1.75 m）：朝主幹走會在離軸心 1.29 m 處停下；從主幹旁 1.5 m 走過會穿過樹冠下繼續前進。
- 風：同一畫面在擺動 0 與 10 倍預設值（2.2 m）各拍一次，主幹不動、樹冠與枝一起偏移、樹皮沒有撕開。10 倍時少數枝頭會露出葉團外；預設強度下枝葉落差不到 0.1 m。
- 拍照審圖：正、右、後、左、四分之三、樹冠下 1.7 m 視高、樹皮與根近照、樹冠邊緣近照、LOD0–3、50 / 100 / 250 m（LODGroup 實際顯示 LOD0 / LOD1 / LOD2）、與 VL02 民居及 1.75 m 人形並排、120 m 遠景、放進 Qingxi 庭院灰模（金樹在院內西北角，綠樹在東北牆外；院外鋪了一塊暫時地面，場景不存檔）。

這一輪審圖後修掉的問題：LOD3 遠景圖重複做伽瑪校正而發白；樹冠頂部側視時有拉長的葉卡細條（掠角剪裁調高到 0.24／0.6）；LOD3 十字面片側對鏡頭時的一條細線；主幹分叉處樹皮斜紋（同一面混用兩套 UV）。

## 請在編輯器裡確認

1. 放進正式場景後的比例與顏色：在實際地形、天空與後處理下看綠／金兩款，必要時用上表的參數調亮度與色偏。
2. Play 模式下的風：批次檢查只拍了靜態畫面（含 10 倍擺動），擺動節奏與幅度請進 Play 看一次，覺得太晃或太僵就調 `_WindStrength`／`_WindSpeed`（兩個材質一起調）。
3. LOD 切換：跑一段由遠到近的移動，看 LOD 換層時跳動是否可以接受（目前沒有 cross-fade）。
4. 效能：沒有做實機測試，不提供 FPS 數字；請在目標裝置上量。大量種植時建議 LOD0 只給玩家附近的少數幾棵。

## 自評（模型總指令六項，每項 95 分門檻）

| 項目 | 分數 | 依據 |
|---|---|---|
| 造型與輪廓（25） | 95 | 寬冠分團、團間留縫、輪廓有起伏；主幹彎曲收細、板根與地表根明顯；四面看都成立（十方位圖）。仍有少數葉團偏圓 |
| 拓撲與結構（20） | 95 | 枝幹融合成一個網格，分叉處不裂縫、不斜紋；根埋入地面；LOD 逐級減面且輪廓一致；法線全部正常 |
| 材質與光影（20） | 95 | 灰階圖集＋三段漸層上色，上亮下深、外亮內深；陰影偏藍不發黑；金樹有黃綠與橘色變化；遠景圖色調與近景一致 |
| 風格一致性（15） | 95 | 明亮、柔和手繪感，介於動畫與自然之間；比例與既有民居、人形對照合理 |
| 動畫／互動（10） | 95 | 頂點擺動、枝葉同步（10 倍擺動驗證）、主幹碰撞走路測試通過；Play 模式動態效果仍請使用者確認 |
| 效能與匯出（10） | 95 | 各 LOD 在上限內、物件與材質少、貼圖照專案規則；FBX／GLB 回匯檢查通過；沒有實機數據 |
