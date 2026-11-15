# Codex v12｜D2 11/15 工作包接線紀錄

2026-11-15，分支 `game/codex-1113-world-plan`。

## 已處理

- 抓取遠端並合併 `origin/art/core-1114-d2-altar-terrace`。合併內容為神木全身參考圖和試做腳本；該分支沒有可匯入 Unity 的神木 FBX、LOD、材質或碰撞殼。
- 依 11/15 三份 300 小時包，把 DR01–DR16、DS01–DS13、DP01–DP22 共 51 個 ID 登記於 `D2.json` 的 `workpackAssets`。每筆有目標數量、代表錨點、整合備註及 `missing` 狀態；這是待交付清單，**不是已放入場景的件數**。
- 把原本已定位的 14 種缺件代碼改為工作包 ID，保留原座標與聚落數量。`placements` 仍是 212 件、`clusters` 仍是 38 組／展開 886 件，合計 1,098 件；其中 480 件缺模型、16 件暫緩顯示。
- FR03 藤簾 12 個定位繼續 `blocked`。DR16 換葉片後還要依 DR01／DR02 正式模型找掛點；現有 FR01／FR02 不能代替新根拱和外圈板根牆。
- 首次 Windows 建置後的 smoke 連續三次在吐納引導或住宿屋轉場檢查失敗。原測試以固定幀數／秒數等待，與實際時間和場景淡入不同步；改為等待狀態達成或逾時，並在出口互動前等 `QingxiSceneFade.Busy` 解除。未改動正式互動流程。
- 保留本機 `ProjectSettings` 與 `UniversalRenderPipelineGlobalSettings.asset` 修改，未列入本輪提交。沒有使用生圖工具，也沒有自行建模。

## 對圖與尺寸風險

11/15 共同標準把 D2 驗收線定為六張同鏡位畫面與設定圖相似 **85–90%**。目前 V1、V6 並排仍缺神木本體、放射板根、入口根拱和林床細節；本輪只更新待交付規劃，畫面相似度沒有因此提高。11/15 估算文件的加權進度約 15% 與使用者主觀判斷「約 40% 像」是兩種量尺，不能互換。三份 300 小時包做完後的約 55%、核心組同步完成後接近 90%，均是**預測**，不是實測進度。

現有 `D2.json` 的 `WORLD_TREE` 預留外框為 40 × 40 × 90 m；11/15 共同標準描述神木底部連板根寬約 60 m，原先文件則寫主幹底徑約 10 m、板根延伸 20 m 以上。這些可能分別指主幹、根盤與佔地，須以正式三視圖及交付模型量測後統一；不能把 40 m 外框當成最終神木尺寸。`godtree_v3.py` 是參考試做，依賴儲存庫外的樹皮來源與腳本，尚非遊戲交付件。

## 驗證與待辦

- `python tools/qingxi-terrain/build_d2_layout.py`：212 件、38 組、1,098 定位、67 種代碼、480 缺件。
- 解析 `D2.json`：51 個工作包 ID 齊全、沒有重複，全部 `missing`；212 個 placement ID 唯一，16 件仍 `blocked`。
- 第一次 Unity `NoviceVillageWindows` 建置成功；場景 log 記錄 `QINGXI_D2_CLUSTERS 886`、`QINGXI_BLOCK_GENERATED D2: 4 pads, 11 roads, 1098 slots`。
- 修正版 Unity `NoviceVillageWindows` 建置成功；`--abc-smoke` 連續兩次退出碼 0，log 均有 `QINGXI_ABC_SMOKE PASS`（`artifacts/abc-d2-v12-gate.log`、`abc-d2-v12-confirm.log`）。
- 最終玩家 `--keyart-shots` 退出碼 0（`artifacts/keyart-d2-v12-final.log`）；D2-V1–V6 均拍到有效畫面並已重做並排圖。逐張檢視仍與設定圖差距很大，尤其 V1–V3 沒有主體、V6 地面缺密實細節。

下一步按工作包交件順序處理樣品：DR01、DS01、DP01 先各自通過對圖與 QA，再把交付路徑接入 D2 匯入器與逐件／聚落落位，重建六鏡位並排圖。神木正式模型、外圈樹與氣氛仍由核心組另行完成。
