# Codex v11｜D2 佈局與整合紀錄

2026-11-15，分支 `game/codex-1113-world-plan`。A 佈局已在 `08bdad63` 提交；本輪接續上一輪尚未提交的 B 整合，先檢查並提交為 `1925e507`、推送，再抓取並合併 `origin/game/core-1110-hud-redesign` 與 `origin/art/core-1114-d2-altar-terrace`。未使用生圖工具。

## 本輪完成

- 將 CO01 坑、SS01 踏石 A／B／C、SR01 地表盤根 A／B／C 改為 `core-d2-v1` 的 v002 FBX。依交付資料讓模型原點貼地：坑口直徑約 4 m，含外緣翻土約 6.6 m；D2 Terrain 於坑口開半徑 1.75 m 的洞，避免地形填住坑底。
- 外圈以現有 ElderPine、ElderCypress 與少量 ElderCamphor 加密，並補四組內圈樹。D2 現有 212 件逐件定位、38 組聚落展開 886 件，合計 1,098 件；其中 602 件有交付來源、480 件缺件、16 件暫緩顯示。
- D2 地形使用專用深褐濕泥與落葉材質，取消草地細節；玩家走近 D2 時縮短距離霧。這是距離霧，貼地薄霧仍未製作。
- 重新對準 V6 坑口鏡位，保留並排圖於 `compare/D2-V1.jpg` 至 `compare/D2-V6.jpg`。V1 外圈樹冠明顯變密；V4／V5 的遮擋已消失；V6 可看見新坑口與翻土。

## 驗證

- `python tools/qingxi-terrain/build_d2_layout.py`：212 件、38 組、合計 1,098 件、480 件缺件。
- `NoviceVillageWindows`：Unity 場景生成顯示 `QINGXI_D2_CLUSTERS 886` 與 `QINGXI_BLOCK_GENERATED D2: 4 pads, 11 roads, 1098 slots`；Windows 玩家建置成功。V6 相機調整後另以相同 `QingxiNoviceVillageBuilder.BuildWindows` 方法重建，記錄於 `artifacts/unity-NoviceVillageWindows-v6.log`。
- 最終玩家程式 `--abc-smoke`：退出碼 0，`QINGXI_ABC_SMOKE PASS`，記錄於 `artifacts/abc-d2-final-v6.log`。
- 最終玩家程式 `--keyart-shots`：退出碼 0，D2-V1～V6 均有有效畫面，記錄於 `artifacts/keyart-d2-final-v6.log`；六張並排圖已更新並逐張檢視。

## 尚未通過

神木本體、放射板根、入口大根拱及多數林下小物仍缺，六視圖構圖尚未達設定圖。D1／D4／D6 邊界、坑口碰撞、全場景粉紅材質與效能尚未完整走查；D7 尚未建成。缺件定位未用替代模型冒充，完整清單見 [`D2-built.md`](D2-built.md)。

`ProjectSettings` 與 `UniversalRenderPipelineGlobalSettings.asset` 的本機改動未納入提交。
