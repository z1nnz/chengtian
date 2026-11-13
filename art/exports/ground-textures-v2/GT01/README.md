| 項目 | 內容 |
|---|---|
| 誰做的 | z1nnz |
| 工作包 | `docs/execution/2026-11-13/codex-v7-redo-and-second-ring.md`，D／GT01 |
| ID | GT01 草地 |
| 分支／PR | `art/codex-1113-ground-textures-v2` ／ PR 待核心組建立 |
| 版本 | v002 AI 源圖，v003 平鋪處理；最終候選 |
| 狀態 | Exported；3×3 預覽已實際檢視；Unity 匯入及實景未驗 |
| 素材來源 | 原創 AI 生成；選定源圖在 `art/references/ground-textures-v2/GT01/` |

## 交付

- `GT01_Albedo_2048.png`：2048×2048 RGB，預定每片對應 4×4 m Unity Terrain。灰綠短草、少量枯草及白花。
- `GT01_Normal_2048.png`：由選定圖像的亮度坡度推算，非幾何掃描；Unity 匯入時設為 Normal Map、Non-Color。
- `GT01_MaskURP_2048.png`：R 金屬度 0、G AO、B 細節遮罩 0、A 光滑度約 0.11–0.15；匯入時關閉 sRGB。
- `GT01_3x3-preview.png`：九片等比例平鋪檢視；`validation.json` 記錄各貼圖四邊首尾像素差皆為 0。
- 來源與再製腳本：`art/references/ground-textures-v2/GT01/source-ai-v002-selected.png`、`art/source/ground-textures-v2/build_gt01.py`。

## 視覺檢查與限制

- 已實際開啟 3×3 預覽。灰綠方向比首版黃褐色接近 KA01 地面。沒有硬邊接縫；小白花在每個 4 m 週期重複，大片地形仍可能被看出規律，建議與其他草層混合並用獨立植被散布遮蓋。
- 自評 7.0／10，候選。AI 源圖為 1254×1254，放大至 2048 並未增加原生細節；法線與 AO 是圖像衍生值，尚未在 Unity 的斜坡、黃昏照明或手機畫質實測。
- 首版源圖偏黃褐，第二版改灰綠；最終腳本對低頻明暗作一次均衡。遵守每階段修正輪次上限，不再反覆調色。
