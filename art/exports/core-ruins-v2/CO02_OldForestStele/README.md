# CO02 古林碑 v002

## 交件

- 區位：D4；正面為 Blender -Y；原點在地表中心。
- 尺寸：1.403 × 0.936 × 2.385 m。LOD0／LOD1／LOD2 為 5888／2214／908 個三角面。
- 三視圖：`art/references/core-ruins-v2/CO02/CO02_threeview_chosen.png`。先生成、檢視並保存原圖，才開始建模。
- 原始檔與可重建腳本：`art/source/core-ruins-v2/`。匯出：本目錄的 FBX（含 LOD）與 GLB（LOD0）。
- 材質：採用 Josh 的 `cr_parts.rbox`、`cr_mats.stone`、`cr_mats.moss_tuft`，顏色取自 `vl_mats.STONE` 色票。三道長短、角度不一的斜鑿痕是實際 Boolean 切槽，沒有文字；上方是嵌入石面的細小缺月。初次材質預覽與 R01 並排後，修正了等距切槽及過平直的鑿面，再重新烘焙。
- 貼圖：2048² Albedo、Normal、ORM、MaskURP；保留顏色、AO、粗糙度、金屬度、物件法線、邊緣與位置烘焙中間圖以便重建。
- 預覽：灰模、材質圖，以及和 Josh R01 乾砌石牆的並排圖位於 `art/previews/core-ruins-v2/CO02_OldForestStele/`。兩張來源預覽的燈光不同，因此並排圖用於材料密度與造型對照，不當作同光色彩測試。

## 檢查

- Blender 5.2.2 重建通過；新版 GLB 與 FBX 均非空，GLB 新版尚未回匯。
- Asset QA：新版 LOD0 通過，5888 三角面、0 懸浮件、0 零面積面、0 反法線、0 UV 越界／重疊。三處半埋石座／苔蘚被列為「包覆但未接觸」警告，屬設計上的半埋狀態。
- Josh 的四支 QA 在初版均通過；修訂版尚未重跑四支，不能沿用初版數值。
- 尚未做 Unity 匯入、碰撞步行與遊戲內檢查；不得視為已可在 Unity 運行。
