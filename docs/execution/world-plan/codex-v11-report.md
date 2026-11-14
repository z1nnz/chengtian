# Codex v11｜D2 佈局與整合紀錄

2026-11-14，分支 `game/codex-1113-world-plan`。本輪接續工作區已有的 B 整合改動；A 佈局已在 `08bdad63` 提交。本輪未執行 `git merge`，亦未生圖。

## 已做

- 核對 `D2.json`：212 件逐件定位、34 組聚落展開 694 件，合計 906 件；其中 545 件缺交付模型，361 件有交付來源。JSON 格式檢查通過。
- 接續 `QingxiD2Clusters`、`QingxiD2Kit`、D2 區塊登記及六個相機鏡位。Unity 生成紀錄顯示 `QINGXI_D2_CLUSTERS 694` 與 `QINGXI_BLOCK_GENERATED D2: 4 pads, 11 roads, 906 slots`。
- 發現上一輪 `--keyart-shots` 的 D2-V1～V6 全黑，玩家紀錄顯示 `ReadPixels was called ... not inside drawing frame`。改用 `AsyncGPUReadback`，並讓並排腳本拒絕全黑截圖。重拍後六張皆有有效畫面，已輸出第一輪並排圖。
- 第一輪對圖發現 V2 鏡位落地、FP01–04 橫跨而非沿路、FO02 發光蕈偏大、林地仍像草地。第二輪改用 D2 固定相機高度，校正 FP 的 X 軸方向與下沉、縮小 FO02，並將 D2 地表改為林地層且移除草地細節。第二輪截圖證實這些項目改善，但 V4 相機落進祭壇前景、12 件 FR03 藤簾因缺板根掛點而像孤立直板，FP03／FP05 在斜坡露出大面直壁。最後一輪改回 V4 實際站立面眼高，暫緩 FR03、FP03、FP05 共 16 件顯示並保留定位。
- `NoviceVillageWindows` 建置及 `--abc-smoke` 已通過；煙霧測試紀錄在 `artifacts/abc-d2.log`。建立 `D2-built.md`，列六項驗收狀態與缺件工作單。

## 進行中與限制

- 最後一輪 `NoviceVillageWindows` 建置待執行；完成後須重跑 `--abc-smoke` 與 `--keyart-shots`，檢視六張更新畫面並覆寫並排圖。
- 神木本體、板根、入口大根拱和大量林下物件缺模型。未完成的缺件不以既有模型冒充；因此目前不能宣稱六視圖構圖已符合設定圖。
- `ProjectSettings` 與 `UniversalRenderPipelineGlobalSettings.asset` 為工作區既有 Unity 改動，不納入提交。
