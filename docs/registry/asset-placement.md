# 物件整合清冊

> 由 `node tools/registry/asset-placement.mjs` 從目前分支的 FBX（另補只含 GLB 的物件）、Unity 模型檔、區塊 JSON 與 Editor 程式產生。這是靜態證據；「配置」仍須遊戲截圖驗收。來源 PR 採 `docs/registry/folders.md`，新交付而尚無 PR 的資料夾標待查。

模型檔 466 件；Unity 同名匯入 182 件；有資料配置或生成程式引用 20 件；空格位 34 件。

## 素材組總覽

| 素材組 | 作者／組別 | 來源 PR | 模型檔 | Unity 同名 | 配置或程式引用 |
|---|---|---|---:|---:|---:|
| `aptitude-plaza-v1` | 核心組 | #5 | 1 | 0 | 0 |
| `creek-repair-b` | B | #70 | 34 | 0 | 0 |
| `creek-repair-b-props` | B | #71 | 5 | 5 | 0 |
| `elder-trees-v1` | 核心組 | 待查 | 33 | 33 | 0 |
| `elder-world-tree-hero-v1` | 核心組 | #17 | 1 | 0 | 0 |
| `giant-tree-v1` | 核心組 | #17 | 1 | 0 | 0 |
| `harvest-market-b` | B | #63 | 4 | 0 | 0 |
| `irrigation-v1` | — | — | 3 | 0 | 0 |
| `irrigation-v2` | — | — | 6 | 0 | 0 |
| `modelling-basics-c` | C | #67 | 27 | 0 | 0 |
| `qingxi-alchemy-b` | 核心組、B | #37 | 15 | 15 | 0 |
| `qingxi-alchemy-table-v1` | 核心組 | #49 | 1 | 0 | 0 |
| `qingxi-day12-c` | C | #60 | 5 | 0 | 0 |
| `qingxi-day34-c` | C | #62 | 11 | 11 | 6 |
| `qingxi-detail-props-v2` | 核心組 | #17 | 4 | 0 | 0 |
| `qingxi-encounter-a` | A | #39 | 13 | 13 | 0 |
| `qingxi-entry-assets-v13` | 核心組 | #22 | 4 | 0 | 0 |
| `qingxi-gathering-visual-kit-v1` | B、核心組 | #31 | 23 | 12 | 0 |
| `qingxi-ground-v1` | 核心組 | 待查 | 8 | 8 | 0 |
| `qingxi-listening-terrace-v1.fbx` | 待查 | — | 1 | 1 | 1 |
| `qingxi-mountain-rabbit-v003` | A | #21 | 8 | 1 | 0 |
| `qingxi-prop-kit-v1` | 核心組 | #17 | 3 | 0 | 0 |
| `qingxi-return-c` | 核心組、C | #37 | 8 | 0 | 0 |
| `qingxi-riverbank-v2` | 核心組 | #17 | 1 | 0 | 0 |
| `qingxi-road-props-v12` | 核心組 | #20 | 4 | 0 | 0 |
| `qingxi-road-props-v13` | 核心組 | #27 | 1 | 0 | 0 |
| `qingxi-town-blockout-v1` | 核心組 | #17 | 0 | 0 | 0 |
| `qingxi-training-yard-v1` | A | #32 | 6 | 6 | 0 |
| `qingxi-village-signs-v1` | 核心組、C | #37 | 4 | 0 | 0 |
| `qingxi-water-report-c` | C | #47 | 32 | 0 | 0 |
| `qingxi-waterhead-a` | A | #45 | 24 | 24 | 8 |
| `qingxi-waterworks-b` | B | #52 | 41 | 37 | 0 |
| `qingxi-winding-road-v1` | 核心組 | #17 | 1 | 0 | 0 |
| `qingxi-world-ruins-b` | B | #57 | 16 | 16 | 5 |
| `sky-and-distance-v1` | Codex（舊分支交付） | 尚無 PR | 2 | 0 | 0 |
| `tea-brewing-b` | B | #58 | 3 | 0 | 0 |
| `tea-terraces-b` | 核心組 | #74 | 40 | 0 | 0 |
| `territory-backyard-a` | A | #56 | 5 | 0 | 0 |
| `territory-interior-b` | B | #54 | 22 | 0 | 0 |
| `valley-and-home-v1` | Codex（舊分支交付） | 尚無 PR | 10 | 0 | 0 |
| `world-props-a` | A、核心組 | #68 | 32 | 0 | 0 |
| `zhuo-boar-a` | A | #61 | 3 | 0 | 0 |

## 逐件證據

| 素材檔 | 作者／組別 | PR | 預定區塊 | Unity 模型 | 已配格位 | 狀態 |
|---|---|---|---|---|---|---|
| `art/exports/aptitude-plaza-v1/aptitude-plaza-v1.glb` | 核心組 | #5 | B2 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b-props/A04_SiltBar/A04_SiltBar.fbx` | B | #71 | A1／A3／D3 | `Assets/YunJing/Models/WaterheadA/A04_SiltBar.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/creek-repair-b-props/C03/C03.fbx` | B | #71 | A1／A3／D3 | `Assets/YunJing/Models/VillageReturnC/C03.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/creek-repair-b-props/C04/C04.fbx` | B | #71 | A1／A3／D3 | `Assets/YunJing/Models/VillageReturnC/C04.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/creek-repair-b-props/C06/C06.fbx` | B | #71 | A1／A3／D3 | `Assets/YunJing/Models/VillageReturnC/C06.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/creek-repair-b-props/C07/C07.fbx` | B | #71 | A1／A3／D3 | `Assets/YunJing/Models/VillageReturnC/C07.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/creek-repair-b/CR03_MudHeap/CR03_MudHeap_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR03_StonePile/CR03_StonePile_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR03_TimberRack/CR03_TimberRack_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR04_Tools/CR04_Tools_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR05_WorkShelter/CR05_WorkShelter_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR06_Bend/CR06_Bend_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR06_Bend/CR06_Bend_water_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR06_Short/CR06_Short_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR06_Short/CR06_Short_water_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR06_Straight/CR06_Straight_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR06_Straight/CR06_Straight_water_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR07_Celebration/CR07_Celebration_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR08_Bend/CR08_Bend_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR08_Bend/CR08_Bend_water_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR08_Straight/CR08_Straight_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR08_Straight/CR08_Straight_water_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR08_Trestle_080/CR08_Trestle_080_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR08_Trestle_150/CR08_Trestle_150_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR08_Trestle_250/CR08_Trestle_250_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR09_A_RopeGate/CR09_A_RopeGate_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR09_B_TenonGate/CR09_B_TenonGate_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR10_CharmStall/CR10_CharmStall_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR11_NoodleStall/CR11_NoodleStall_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR12_RankingBoard/CR12_RankingBoard_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR14_WeedClump/CR14_WeedClump_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR15_DitchCross/CR15_DitchCross_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/CR15_DitchCross/CR15_DitchCross_water_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/F01_Field/F01_Field.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/WM01_MillHouse/WM01_MillHouse_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/WM02_WaterWheel/WM02_WaterWheel_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/WM04_Millstones/WM04_Millstones_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/WM05_WashSteps/WM05_WashSteps_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/WM07_StoneBridge/WM07_StoneBridge_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/creek-repair-b/WM09_BambooPavilion/WM09_BambooPavilion_v001.fbx` | B | #70 | A3／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/elder-trees-v1/ElderCamphor_B.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderCamphor_B.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderCamphor_C.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderCamphor_C.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderCamphor_D.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderCamphor_D.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderCamphor_E.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderCamphor_E.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderCamphor_F.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderCamphor_F.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderCamphor.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderCamphor.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderCypress_B.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderCypress_B.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderCypress_C.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderCypress_C.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderCypress_D.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderCypress_D.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderCypress.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderCypress.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderGinkgo_B.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderGinkgo_B.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderGinkgo_C.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderGinkgo_C.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderGinkgo_D.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderGinkgo_D.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderGinkgo.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderGinkgo.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderGuardian.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderGuardian.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderMaple_B.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderMaple_B.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderMaple_C.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderMaple_C.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderMaple_D.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderMaple_D.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderMaple.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderMaple.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderPine_B.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderPine_B.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderPine_C.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderPine_C.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderPine_D.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderPine_D.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderPine.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderPine.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderPlum_B.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderPlum_B.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderPlum_C.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderPlum_C.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderPlum_D.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderPlum_D.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderPlum_E.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderPlum_E.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderPlum_F.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderPlum_F.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderPlum.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderPlum.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderWillow_B.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderWillow_B.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderWillow.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderWillow.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/ElderWithered.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/ElderWithered.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-trees-v1/JianmuSapling.fbx` | 核心組 | 待查 | A1／D1 | `Assets/YunJing/Models/ElderTreesV1/JianmuSapling.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/elder-world-tree-hero-v1/elder-world-tree-hero-v1.glb` | 核心組 | #17 | D2 | — | — | 素材檔；未證實匯入 |
| `art/exports/giant-tree-v1/giant-tree.fbx` | 核心組 | #17 | D2 | — | — | 素材檔；未證實匯入 |
| `art/exports/harvest-market-b/MK01_Steelyard/MK01_Steelyard_v001.fbx` | B | #63 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/harvest-market-b/MK02_HarvestSieve/MK02_HarvestSieve_v001.fbx` | B | #63 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/harvest-market-b/MK03_PriceBoard/MK03_PriceBoard_v001.fbx` | B | #63 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/harvest-market-b/MK04_BackBasket/MK04_BackBasket_v001.fbx` | B | #63 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/irrigation-v1/cistern.glb` | — | — | A6 | — | — | 素材檔；未證實匯入 |
| `art/exports/irrigation-v1/spirit-bed.glb` | — | — | A6 | — | — | 素材檔；未證實匯入 |
| `art/exports/irrigation-v1/water-channel.glb` | — | — | A6 | — | — | 素材檔；未證實匯入 |
| `art/exports/irrigation-v2/cistern-lod1.glb` | — | — | A6 | — | — | 素材檔；未證實匯入 |
| `art/exports/irrigation-v2/cistern.glb` | — | — | A6 | — | — | 素材檔；未證實匯入 |
| `art/exports/irrigation-v2/spirit-bed-lod1.glb` | — | — | A6 | — | — | 素材檔；未證實匯入 |
| `art/exports/irrigation-v2/spirit-bed.glb` | — | — | A6 | — | — | 素材檔；未證實匯入 |
| `art/exports/irrigation-v2/water-channel-lod1.glb` | — | — | A6 | — | — | 素材檔；未證實匯入 |
| `art/exports/irrigation-v2/water-channel.glb` | — | — | A6 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM01_01.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM01_02.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM01_03.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM02_01.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM02_02.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM03_01.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM03_02.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM03_03.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM04_01.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM04_02.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM04_03.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM04_04.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM05_01.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM05_02.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM05_03.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM06_01.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM06_02.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM06_03.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM06_04.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM07_01.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM08_01.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM08_02.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM09_01.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM09_02.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM10_01.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM10_02.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/modelling-basics-c/BM10_03.fbx` | C | #67 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-alchemy-b/B01_BronzeFurnace/v001/B01_BronzeFurnace_cold.fbx` | 核心組、B | #37 | A1 | `Assets/YunJing/Models/AlchemyB/B01_BronzeFurnace/B01_BronzeFurnace_cold.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-alchemy-b/B01_BronzeFurnace/v001/B01_BronzeFurnace_heating.fbx` | 核心組、B | #37 | A1 | `Assets/YunJing/Models/AlchemyB/B01_BronzeFurnace/B01_BronzeFurnace_heating.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-alchemy-b/B02_FurnaceLid/v001/B02_FurnaceLid_heating.fbx` | 核心組、B | #37 | A1 | `Assets/YunJing/Models/AlchemyB/B02_FurnaceLid/B02_FurnaceLid_heating.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-alchemy-b/B02_FurnaceLid/v001/B02_FurnaceLid.fbx` | 核心組、B | #37 | A1 | `Assets/YunJing/Models/AlchemyB/B02_FurnaceLid/B02_FurnaceLid.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-alchemy-b/B03_StoneMortar/v001/B03_StoneMortar.fbx` | 核心組、B | #37 | A1 | `Assets/YunJing/Models/AlchemyB/B03_StoneMortar/B03_StoneMortar.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-alchemy-b/B04_BambooSortingTrays/v001/B04_BambooSortingTrays.fbx` | 核心組、B | #37 | A1 | `Assets/YunJing/Models/AlchemyB/B04_BambooSortingTrays/B04_BambooSortingTrays.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-alchemy-b/B05_HerbDrawerCabinet/v001/B05_HerbDrawerCabinet.fbx` | 核心組、B | #37 | A1 | `Assets/YunJing/Models/AlchemyB/B05_HerbDrawerCabinet/B05_HerbDrawerCabinet.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-alchemy-b/B06_CeramicWaterJar/v001/B06_CeramicWaterJar.fbx` | 核心組、B | #37 | A1 | `Assets/YunJing/Models/AlchemyB/B06_CeramicWaterJar/B06_CeramicWaterJar.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-alchemy-b/B07_WoodenFuelBox/v001/B07_WoodenFuelBox.fbx` | 核心組、B | #37 | A1 | `Assets/YunJing/Models/AlchemyB/B07_WoodenFuelBox/B07_WoodenFuelBox.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-alchemy-b/B08_VentilatedDryingBasket/v001/B08_VentilatedDryingBasket.fbx` | 核心組、B | #37 | A1 | `Assets/YunJing/Models/AlchemyB/B08_VentilatedDryingBasket/B08_VentilatedDryingBasket.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-alchemy-b/B09_ClothFilterFrame/v001/B09_ClothFilterFrame.fbx` | 核心組、B | #37 | A1 | `Assets/YunJing/Models/AlchemyB/B09_ClothFilterFrame/B09_ClothFilterFrame.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-alchemy-b/B10_WaxSealedBottle/v001/B10_WaxSealedBottle_empty.fbx` | 核心組、B | #37 | A1 | `Assets/YunJing/Models/AlchemyB/B10_WaxSealedBottle/B10_WaxSealedBottle_empty.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-alchemy-b/B10_WaxSealedBottle/v001/B10_WaxSealedBottle_filled.fbx` | 核心組、B | #37 | A1 | `Assets/YunJing/Models/AlchemyB/B10_WaxSealedBottle/B10_WaxSealedBottle_filled.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-alchemy-b/B11_BambooRecipeStand/v001/B11_BambooRecipeStand.fbx` | 核心組、B | #37 | A1 | `Assets/YunJing/Models/AlchemyB/B11_BambooRecipeStand/B11_BambooRecipeStand.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-alchemy-b/B12_WorkshopChimney/v001/B12_WorkshopChimney.fbx` | 核心組、B | #37 | A1 | `Assets/YunJing/Models/AlchemyB/B12_WorkshopChimney/B12_WorkshopChimney.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-alchemy-table-v1/QX_AlchemyWorkTable_v001.glb` | 核心組 | #49 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-day12-c/G01.fbx` | C | #60 | A1／A2 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-day12-c/RK03.fbx` | C | #60 | A1／A2 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-day12-c/TY04.fbx` | C | #60 | A1／A2 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-day12-c/TY08.fbx` | C | #60 | A1／A2 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-day12-c/TY09.fbx` | C | #60 | A1／A2 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-day34-c/UP01.fbx` | C | #62 | D3 | `Assets/YunJing/Models/Day34C/UP01/UP01.fbx` | D3:D3_Weir | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-day34-c/UP02_01.fbx` | C | #62 | D3 | `Assets/YunJing/Models/Day34C/UP02_01/UP02_01.fbx` | D3:D3_WarmStone_01 | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-day34-c/UP02_02.fbx` | C | #62 | D3 | `Assets/YunJing/Models/Day34C/UP02_02/UP02_02.fbx` | D3:D3_WarmStone_02 | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-day34-c/UP02_03.fbx` | C | #62 | D3 | `Assets/YunJing/Models/Day34C/UP02_03/UP02_03.fbx` | D3:D3_WarmStone_03 | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-day34-c/UP03.fbx` | C | #62 | D3 | `Assets/YunJing/Models/Day34C/UP03/UP03.fbx` | D3:D3_WaterMark | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-day34-c/UP04.fbx` | C | #62 | D3 | `Assets/YunJing/Models/Day34C/UP04/UP04.fbx` | D3:D3_DrawingStone | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-day34-c/UP05_Burner.fbx` | C | #62 | A3／D3 | `Assets/YunJing/Models/Day34C/UP05_Burner/UP05_Burner.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-day34-c/UP05_CushionNew.fbx` | C | #62 | A3／D3 | `Assets/YunJing/Models/Day34C/UP05_CushionNew/UP05_CushionNew.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-day34-c/UP05_CushionOld.fbx` | C | #62 | A3／D3 | `Assets/YunJing/Models/Day34C/UP05_CushionOld/UP05_CushionOld.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-day34-c/UP05_Table.fbx` | C | #62 | A3／D3 | `Assets/YunJing/Models/Day34C/UP05_Table/UP05_Table.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-day34-c/UP06.fbx` | C | #62 | A3／D3 | `Assets/YunJing/Models/Day34C/UP06/UP06.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-detail-props-v2/qingxi-fern-flower-v2.glb` | 核心組 | #17 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-detail-props-v2/qingxi-moss-boulder-v2.glb` | 核心組 | #17 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-detail-props-v2/qingxi-river-reed-v2.glb` | 核心組 | #17 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-detail-props-v2/qingxi-trail-lantern-v2.glb` | 核心組 | #17 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-encounter-a/A01_SlopeTile.fbx` | A | #39 | D1 | `Assets/YunJing/Models/ForestEncounterA/A01_SlopeTile.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-encounter-a/A02_HollowTile.fbx` | A | #39 | D1 | `Assets/YunJing/Models/ForestEncounterA/A02_HollowTile.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-encounter-a/A03_FallenLog.fbx` | A | #39 | D1 | `Assets/YunJing/Models/ForestEncounterA/A03_FallenLog.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-encounter-a/A04_MossBoulderCover.fbx` | A | #39 | D1 | `Assets/YunJing/Models/ForestEncounterA/A04_MossBoulderCover.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-encounter-a/A05_LayeredRockCover.fbx` | A | #39 | D1 | `Assets/YunJing/Models/ForestEncounterA/A05_LayeredRockCover.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-encounter-a/A06_RootStump.fbx` | A | #39 | D1 | `Assets/YunJing/Models/ForestEncounterA/A06_RootStump.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-encounter-a/A07_RabbitTrailTile.fbx` | A | #39 | D1 | `Assets/YunJing/Models/ForestEncounterA/A07_RabbitTrailTile.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-encounter-a/A08_BrokenBambooFence.fbx` | A | #39 | D1 | `Assets/YunJing/Models/ForestEncounterA/A08_BrokenBambooFence.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-encounter-a/A09_StoneShelter.fbx` | A | #39 | D1 | `Assets/YunJing/Models/ForestEncounterA/A09_StoneShelter.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-encounter-a/A10_WatchPlatform.fbx` | A | #39 | D1 | `Assets/YunJing/Models/ForestEncounterA/A10_WatchPlatform.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-encounter-a/A11_WarningClothRack.fbx` | A | #39 | D1 | `Assets/YunJing/Models/ForestEncounterA/A11_WarningClothRack.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-encounter-a/A12_VineDummy_worn.fbx` | A | #39 | D1 | `Assets/YunJing/Models/ForestEncounterA/A12_VineDummy_worn.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-encounter-a/A12_VineDummy.fbx` | A | #39 | D1 | `Assets/YunJing/Models/ForestEncounterA/A12_VineDummy.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-entry-assets-v13/herb-basket-v13.glb` | 核心組 | #22 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-entry-assets-v13/novice-cultivator-v13.glb` | 核心組 | #22 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-entry-assets-v13/road-dressing-v13.glb` | 核心組 | #22 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-entry-assets-v13/village-gate-v13.glb` | 核心組 | #22 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_CreekSteppingPlank/v001/QX_CreekSteppingPlank.fbx` | B、核心組 | #31 | A1／D1 | `Assets/YunJing/Models/GatheringB/Creek/QX_CreekSteppingPlank.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_CreekSteppingPlank/v002/QX_CreekSteppingPlank.fbx` | B、核心組 | #31 | A1／D1 | `Assets/YunJing/Models/GatheringB/Creek/QX_CreekSteppingPlank.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_EmbeddedOre_Yumai/v001/QX_EmbeddedOre_Yumai_post.fbx` | B、核心組 | #31 | A1／D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_EmbeddedOre_Yumai/v001/QX_EmbeddedOre_Yumai_pre.fbx` | B、核心組 | #31 | A1／D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_EmbeddedOre_Yumai/v002/QX_EmbeddedOre_Yumai_post.fbx` | B、核心組 | #31 | A1／D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_EmbeddedOre_Yumai/v002/QX_EmbeddedOre_Yumai_pre.fbx` | B、核心組 | #31 | A1／D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_GatheringLandmark/v001/QX_GatheringLandmark.fbx` | B、核心組 | #31 | A1／D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_GatheringLandmark/v002/QX_GatheringLandmark.fbx` | B、核心組 | #31 | A1／D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_SpiritHerb_Chilu/v001/QX_SpiritHerb_Chilu_post.fbx` | B、核心組 | #31 | A1／D1 | `Assets/YunJing/Models/GatheringB/Chilu/QX_SpiritHerb_Chilu_post.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_SpiritHerb_Chilu/v001/QX_SpiritHerb_Chilu_pre.fbx` | B、核心組 | #31 | A1／D1 | `Assets/YunJing/Models/GatheringB/Chilu/QX_SpiritHerb_Chilu_pre.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_SpiritHerb_Chilu/v002/QX_SpiritHerb_Chilu_post_LOD1_mobile.glb` | B、核心組 | #31 | A1／D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_SpiritHerb_Chilu/v002/QX_SpiritHerb_Chilu_post.fbx` | B、核心組 | #31 | A1／D1 | `Assets/YunJing/Models/GatheringB/Chilu/QX_SpiritHerb_Chilu_post.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_SpiritHerb_Chilu/v002/QX_SpiritHerb_Chilu_pre_LOD1_mobile.glb` | B、核心組 | #31 | A1／D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_SpiritHerb_Chilu/v002/QX_SpiritHerb_Chilu_pre.fbx` | B、核心組 | #31 | A1／D1 | `Assets/YunJing/Models/GatheringB/Chilu/QX_SpiritHerb_Chilu_pre.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_SpiritHerb_Qinglan/v001/QX_SpiritHerb_Qinglan_post.fbx` | B、核心組 | #31 | A1／D1 | `Assets/YunJing/Models/GatheringB/Qinglan/QX_SpiritHerb_Qinglan_post.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_SpiritHerb_Qinglan/v001/QX_SpiritHerb_Qinglan_pre.fbx` | B、核心組 | #31 | A1／D1 | `Assets/YunJing/Models/GatheringB/Qinglan/QX_SpiritHerb_Qinglan_pre.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_SpiritHerb_Qinglan/v002/QX_SpiritHerb_Qinglan_post_LOD1_mobile.glb` | B、核心組 | #31 | A1／D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_SpiritHerb_Qinglan/v002/QX_SpiritHerb_Qinglan_post.fbx` | B、核心組 | #31 | A1／D1 | `Assets/YunJing/Models/GatheringB/Qinglan/QX_SpiritHerb_Qinglan_post.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_SpiritHerb_Qinglan/v002/QX_SpiritHerb_Qinglan_pre_LOD1_mobile.glb` | B、核心組 | #31 | A1／D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_SpiritHerb_Qinglan/v002/QX_SpiritHerb_Qinglan_pre.fbx` | B、核心組 | #31 | A1／D1 | `Assets/YunJing/Models/GatheringB/Qinglan/QX_SpiritHerb_Qinglan_pre.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_WaterReeds/v001/QX_WaterReeds.fbx` | B、核心組 | #31 | A1／D1 | `Assets/YunJing/Models/GatheringB/Creek/QX_WaterReeds.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_WaterReeds/v002/QX_WaterReeds_LOD1_mobile.glb` | B、核心組 | #31 | A1／D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-gathering-visual-kit-v1/QX_WaterReeds/v002/QX_WaterReeds.fbx` | B、核心組 | #31 | A1／D1 | `Assets/YunJing/Models/GatheringB/Creek/QX_WaterReeds.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-ground-v1/FlowerBlue.fbx` | 核心組 | 待查 | A1／A2／A3／D1／D3 | `Assets/YunJing/Models/QingxiGroundV1/FlowerBlue.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-ground-v1/FlowerWhite.fbx` | 核心組 | 待查 | A1／A2／A3／D1／D3 | `Assets/YunJing/Models/QingxiGroundV1/FlowerWhite.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-ground-v1/FlowerYellow.fbx` | 核心組 | 待查 | A1／A2／A3／D1／D3 | `Assets/YunJing/Models/QingxiGroundV1/FlowerYellow.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-ground-v1/GrassDry.fbx` | 核心組 | 待查 | A1／A2／A3／D1／D3 | `Assets/YunJing/Models/QingxiGroundV1/GrassDry.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-ground-v1/GrassLush.fbx` | 核心組 | 待查 | A1／A2／A3／D1／D3 | `Assets/YunJing/Models/QingxiGroundV1/GrassLush.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-ground-v1/GrassTall.fbx` | 核心組 | 待查 | A1／A2／A3／D1／D3 | `Assets/YunJing/Models/QingxiGroundV1/GrassTall.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-ground-v1/Pebbles.fbx` | 核心組 | 待查 | A1／A2／A3／D1／D3 | `Assets/YunJing/Models/QingxiGroundV1/Pebbles.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-ground-v1/StonesMossy.fbx` | 核心組 | 待查 | A1／A2／A3／D1／D3 | `Assets/YunJing/Models/QingxiGroundV1/StonesMossy.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-listening-terrace-v1.fbx` | 待查 | — | 待指定 | `Assets/YunJing/Models/QingxiListeningTerraceV1/qingxi-listening-terrace-v1.fbx` | Editor 程式引用 | 生成程式引用；未截圖確認 |
| `art/exports/qingxi-mountain-rabbit-v003/QingxiMountainRabbit_v003_LOD1.fbx` | A | #21 | D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-mountain-rabbit-v003/QingxiMountainRabbit_v003_LOD2.fbx` | A | #21 | D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-mountain-rabbit-v003/QingxiMountainRabbit_v003.fbx` | A | #21 | D1 | `Assets/YunJing/Models/ForestEncounterA/Rabbit/QingxiMountainRabbit_v003.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-mountain-rabbit-v003/Rabbit_Death.fbx` | A | #21 | D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-mountain-rabbit-v003/Rabbit_Flee.fbx` | A | #21 | D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-mountain-rabbit-v003/Rabbit_Hit.fbx` | A | #21 | D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-mountain-rabbit-v003/Rabbit_Hop.fbx` | A | #21 | D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-mountain-rabbit-v003/Rabbit_Idle.fbx` | A | #21 | D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-prop-kit-v1/qingxi-cobble-v1.glb` | 核心組 | #17 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-prop-kit-v1/qingxi-grass-v1.glb` | 核心組 | #17 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-prop-kit-v1/qingxi-wildflower-v1.glb` | 核心組 | #17 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-return-c/C01.glb` | 核心組、C | #37 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-return-c/C02.glb` | 核心組、C | #37 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-return-c/C03.glb` | 核心組、C | #37 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-return-c/C04.glb` | 核心組、C | #37 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-return-c/C05.glb` | 核心組、C | #37 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-return-c/C06.glb` | 核心組、C | #37 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-return-c/C07.glb` | 核心組、C | #37 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-return-c/C08.glb` | 核心組、C | #37 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-riverbank-v2/qingxi-riverbank-v2.fbx` | 核心組 | #17 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-road-props-v12/qingxi-bridge-rail-v12.glb` | 核心組 | #20 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-road-props-v12/qingxi-herb-rack-v12.glb` | 核心組 | #20 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-road-props-v12/qingxi-road-v12.glb` | 核心組 | #20 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-road-props-v12/qingxi-waymarker-v12.glb` | 核心組 | #20 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-road-props-v13/qingxi-road-v13.glb` | 核心組 | #27 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-training-yard-v1/agility-post.fbx` | A | #32 | A1 | `Assets/YunJing/Models/CollaboratorNoviceV1/agility-post.fbx`、`Assets/YunJing/Models/TrainingYardA/agility-post.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-training-yard-v1/engraved-training-stone.fbx` | A | #32 | A1 | `Assets/YunJing/Models/TrainingYardA/engraved-training-stone.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-training-yard-v1/qi-striking-post.fbx` | A | #32 | A1 | `Assets/YunJing/Models/CollaboratorNoviceV1/qi-striking-post.fbx`、`Assets/YunJing/Models/TrainingYardA/qi-striking-post.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-training-yard-v1/training-banner.fbx` | A | #32 | A1 | `Assets/YunJing/Models/CollaboratorNoviceV1/training-banner.fbx`、`Assets/YunJing/Models/TrainingYardA/training-banner.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-training-yard-v1/training-shelter.fbx` | A | #32 | A1 | `Assets/YunJing/Models/CollaboratorNoviceV1/training-shelter.fbx`、`Assets/YunJing/Models/TrainingYardA/training-shelter.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-training-yard-v1/weapon-rack.fbx` | A | #32 | A1 | `Assets/YunJing/Models/CollaboratorNoviceV1/weapon-rack.fbx`、`Assets/YunJing/Models/TrainingYardA/weapon-rack.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-village-signs-v1/Q01.glb` | 核心組、C | #37 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-village-signs-v1/Q02.glb` | 核心組、C | #37 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-village-signs-v1/Q03.glb` | 核心組、C | #37 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-village-signs-v1/Q04.glb` | 核心組、C | #37 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/c01-v002/C01_CouncilTable_v002.fbx` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/C01.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/C02.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/C03.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/C04.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/C05.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/C06-complete.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/C06.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/C07.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/C08.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/v002/C02_v002.fbx` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/v002/C03_bail_03_v002.fbx` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/v002/C03_low_02_v002.fbx` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/v002/C03_tall_01_v002.fbx` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/v002/C04_v002.fbx` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/v002/C05_fork_02_v002.fbx` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/v002/C05_notch_01_v002.fbx` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/v002/C06_fork_01_v002.fbx` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/v002/C06_slant_02_v002.fbx` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/v002/C07_v002.fbx` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/v002/C08_v002.fbx` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/variants/C03_bail_03.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/variants/C03_low_02.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/variants/C03_tall_01.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/variants/C05_fork_02.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/variants/C05_notch_01.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/variants/C06_fork_01-complete.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/variants/C06_fork_01.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/variants/C06_slant_02-complete.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/variants/C06_slant_02.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/variants/VillageCorner-a.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-water-report-c/variants/VillageCorner-b.glb` | C | #47 | A1 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-waterhead-a/A01_bend_left_01.fbx` | A | #45 | A3／D3 | `Assets/YunJing/Models/WaterheadA/A01_bend_left_01.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterhead-a/A01_bend_right_01.fbx` | A | #45 | A3／D3 | `Assets/YunJing/Models/WaterheadA/A01_bend_right_01.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterhead-a/A01_end_source_01.fbx` | A | #45 | A3／D3 | `Assets/YunJing/Models/WaterheadA/A01_end_source_01.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterhead-a/A01_narrow_01.fbx` | A | #45 | A3／D3 | `Assets/YunJing/Models/WaterheadA/A01_narrow_01.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterhead-a/A01_straight_01.fbx` | A | #45 | A3／D3 | `Assets/YunJing/Models/WaterheadA/A01_straight_01.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterhead-a/A02_end_break_01.fbx` | A | #45 | D3 | `Assets/YunJing/Models/WaterheadA/A02_end_break_01.fbx` | D3:D3_CrackedSluice | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-waterhead-a/A02_side_crack_01.fbx` | A | #45 | A3／D3 | `Assets/YunJing/Models/WaterheadA/A02_side_crack_01.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterhead-a/A03_FormationBase.fbx` | A | #45 | D3 | `Assets/YunJing/Models/WaterheadA/A03_FormationBase.fbx` | D3:D3_FormationBase | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-waterhead-a/A04_SiltBar_cleared.fbx` | A | #45 | A3／D3 | `Assets/YunJing/Models/WaterheadA/A04_SiltBar_cleared.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterhead-a/A04_SiltBar.fbx` | A | #45 | A3／D3 | `Assets/YunJing/Models/WaterheadA/A04_SiltBar.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterhead-a/A04_SiltJam_03.fbx` | A | #45 | A3／D3 | `Assets/YunJing/Models/WaterheadA/A04_SiltJam_03.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterhead-a/A04_SiltSide_02.fbx` | A | #45 | A3／D3 | `Assets/YunJing/Models/WaterheadA/A04_SiltSide_02.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterhead-a/A05_WitheredSedge_01.fbx` | A | #45 | A3／D3 | `Assets/YunJing/Models/WaterheadA/A05_WitheredSedge_01.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterhead-a/A05_WitheredSedge_02.fbx` | A | #45 | A3／D3 | `Assets/YunJing/Models/WaterheadA/A05_WitheredSedge_02.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterhead-a/A05_WitheredSedge_03.fbx` | A | #45 | A3／D3 | `Assets/YunJing/Models/WaterheadA/A05_WitheredSedge_03.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterhead-a/A06_MarkerStone.fbx` | A | #45 | D3 | `Assets/YunJing/Models/WaterheadA/A06_MarkerStone.fbx` | D3:D3_MarkerStone | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-waterhead-a/A07_NurseryTracks.fbx` | A | #45 | D3 | `Assets/YunJing/Models/WaterheadA/A07_NurseryTracks.fbx` | D3:D3_NurseryTracks | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-waterhead-a/A08_gravel_bar_01.fbx` | A | #45 | A3／D3 | `Assets/YunJing/Models/WaterheadA/A08_gravel_bar_01.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterhead-a/A08_slabs_stagger_01.fbx` | A | #45 | A3／D3 | `Assets/YunJing/Models/WaterheadA/A08_slabs_stagger_01.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterhead-a/A08_steps_line_01.fbx` | A | #45 | A3／D3 | `Assets/YunJing/Models/WaterheadA/A08_steps_line_01.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterhead-a/A09_WaterGauge.fbx` | A | #45 | D3 | `Assets/YunJing/Models/WaterheadA/A09_WaterGauge.fbx` | D3:D3_WaterGauge | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-waterhead-a/A10_FallenBamboo.fbx` | A | #45 | D3 | `Assets/YunJing/Models/WaterheadA/A10_FallenBamboo.fbx` | D3:D3_FallenBamboo | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-waterhead-a/A11_PavilionRuin.fbx` | A | #45 | D3 | `Assets/YunJing/Models/WaterheadA/A11_PavilionRuin.fbx` | D3:D3_PavilionRuin | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-waterhead-a/A12_ResonanceStone.fbx` | A | #45 | D3 | `Assets/YunJing/Models/WaterheadA/A12_ResonanceStone.fbx` | D3:D3_ResonanceStone | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-waterworks-b/B01/B01_water.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B01/B01_water.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B01/B01.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B01/B01.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B02-V02/B02-V02_water.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B02-V02/B02-V02_water.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B02-V02/B02-V02.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B02-V02/B02-V02.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B02-V03/B02-V03_water.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B02-V03/B02-V03_water.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B02-V03/B02-V03.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B02-V03/B02-V03.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B02-V04/B02-V04_water.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B02-V04/B02-V04_water.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B02-V04/B02-V04.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B02-V04/B02-V04.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B02-V05/B02-V05_water.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B02-V05/B02-V05_water.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B02-V05/B02-V05.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B02-V05/B02-V05.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B02/B02_water.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B02/B02_water.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B02/B02.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B02/B02.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B03-V02/B03-V02_water.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B03-V02/B03-V02_water.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B03-V02/B03-V02.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B03-V02/B03-V02.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B03-V03/B03-V03_water.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B03-V03/B03-V03_water.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B03-V03/B03-V03.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B03-V03/B03-V03.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B03-V04/B03-V04_water.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B03-V04/B03-V04_water.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B03-V04/B03-V04.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B03-V04/B03-V04.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B03/B03_water.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B03/B03_water.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B03/B03.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B03/B03.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B04-V02/B04-V02_water.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B04-V02/B04-V02_water.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B04-V02/B04-V02.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B04-V02/B04-V02.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B04/B04_water.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B04/B04_water.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B04/B04.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B04/B04.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B05/B05_water.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B05/B05_water.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B05/B05.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B05/B05.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B06/B06.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B06/B06.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B07-V02/B07-V02.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B07-V02/B07-V02.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B07-V03/B07-V03.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B07-V03/B07-V03.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B07/B07.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B07/B07.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B08/B08.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B08/B08.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B09/B09.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B09/B09.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B10-V02/B10-V02.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B10-V02/B10-V02.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B10-V03/B10-V03.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B10-V03/B10-V03.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B10/B10.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B10/B10.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B11/B11.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B11/B11.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/B12/B12.fbx` | B | #52 | A1／A3 | `Assets/YunJing/Models/WaterworksB/B12/B12.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-waterworks-b/F01/F01_water.fbx` | B | #52 | A1／A3 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-waterworks-b/F01/F01.fbx` | B | #52 | A1／A3 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-waterworks-b/S01/S01.fbx` | B | #52 | A1／A3 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-waterworks-b/S02/S02.fbx` | B | #52 | A1／A3 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-winding-road-v1/qingxi-winding-road-v1.glb` | 核心組 | #17 | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/qingxi-world-ruins-b/A2_OverturnedCart/A2_OverturnedCart_v001.fbx` | B | #57 | A2 | `Assets/YunJing/Models/RuinsB/A2_OverturnedCart/A2_OverturnedCart_v001.fbx` | A2:A2_OverturnedCart | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-world-ruins-b/D3_DryWell/D3_DryWell_v001.fbx` | B | #57 | D3 | `Assets/YunJing/Models/RuinsB/D3_DryWell/D3_DryWell_v001.fbx` | D3:D3_DryWell | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-world-ruins-b/H01_StoneTimberHouse/H01_StoneTimberHouse_v001.fbx` | B | #57 | D3 | `Assets/YunJing/Models/RuinsB/H01_StoneTimberHouse/H01_StoneTimberHouse_v001.fbx` | D3:D3_AbandonedHut | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-world-ruins-b/R01_DryStoneWall_Collapsed/R01_DryStoneWall_Collapsed_v001.fbx` | B | #57 | A2／A3／D3 | `Assets/YunJing/Models/RuinsB/R01_DryStoneWall_Collapsed/R01_DryStoneWall_Collapsed_v001.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-world-ruins-b/R01_DryStoneWall_Corner/R01_DryStoneWall_Corner_v001.fbx` | B | #57 | A2／A3／D3 | `Assets/YunJing/Models/RuinsB/R01_DryStoneWall_Corner/R01_DryStoneWall_Corner_v001.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-world-ruins-b/R01_DryStoneWall_EndCap/R01_DryStoneWall_EndCap_v001.fbx` | B | #57 | A2／A3／D3 | `Assets/YunJing/Models/RuinsB/R01_DryStoneWall_EndCap/R01_DryStoneWall_EndCap_v001.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-world-ruins-b/R01_DryStoneWall_Straight/R01_DryStoneWall_Straight_v001.fbx` | B | #57 | A2／A3／D3 | `Assets/YunJing/Models/RuinsB/R01_DryStoneWall_Straight/R01_DryStoneWall_Straight_v001.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-world-ruins-b/R02_BambooFence_Corner/R02_BambooFence_Corner_v001.fbx` | B | #57 | A2／A3／D3 | `Assets/YunJing/Models/RuinsB/R02_BambooFence_Corner/R02_BambooFence_Corner_v001.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-world-ruins-b/R02_BambooFence_EndPost/R02_BambooFence_EndPost_v001.fbx` | B | #57 | A2／A3／D3 | `Assets/YunJing/Models/RuinsB/R02_BambooFence_EndPost/R02_BambooFence_EndPost_v001.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-world-ruins-b/R02_BambooFence_Leaning/R02_BambooFence_Leaning_v001.fbx` | B | #57 | A2／A3／D3 | `Assets/YunJing/Models/RuinsB/R02_BambooFence_Leaning/R02_BambooFence_Leaning_v001.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-world-ruins-b/R02_BambooFence_Straight/R02_BambooFence_Straight_v001.fbx` | B | #57 | A2／A3／D3 | `Assets/YunJing/Models/RuinsB/R02_BambooFence_Straight/R02_BambooFence_Straight_v001.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-world-ruins-b/R03_FirewoodNeat/R03_FirewoodNeat_v001.fbx` | B | #57 | A2／A3／D3 | `Assets/YunJing/Models/RuinsB/R03_FirewoodNeat/R03_FirewoodNeat_v001.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-world-ruins-b/R03_FirewoodScattered/R03_FirewoodScattered_v001.fbx` | B | #57 | A2／A3／D3 | `Assets/YunJing/Models/RuinsB/R03_FirewoodScattered/R03_FirewoodScattered_v001.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-world-ruins-b/R04_StoneLanternBroken/R04_StoneLanternBroken_v001.fbx` | B | #57 | A2／A3／D3 | `Assets/YunJing/Models/RuinsB/R04_StoneLanternBroken/R04_StoneLanternBroken_v001.fbx` | — | Unity 已匯入；未證實擺放 |
| `art/exports/qingxi-world-ruins-b/R04_StoneLanternIntact/R04_StoneLanternIntact_v001.fbx` | B | #57 | A2 | `Assets/YunJing/Models/RuinsB/R04_StoneLanternIntact/R04_StoneLanternIntact_v001.fbx` | A2:A2_LampPost_1 | 區塊資料配置；未截圖確認 |
| `art/exports/qingxi-world-ruins-b/R05_Milestone/R05_Milestone_v001.fbx` | B | #57 | A2 | `Assets/YunJing/Models/RuinsB/R05_Milestone/R05_Milestone_v001.fbx` | A2:A2_Milestone_1 | 區塊資料配置；未截圖確認 |
| `art/exports/sky-and-distance-v1/MO01/SM_Moon.fbx` | Codex（舊分支交付） | 尚無 PR | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/sky-and-distance-v1/SK/SM_Skyline_Arc.fbx` | Codex（舊分支交付） | 尚無 PR | 待指定 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-brewing-b/RK04_TeaStall/v001/RK04_TeaStall_v001.fbx` | B | #58 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-brewing-b/TI09_TeaStove/v001/TI09_TeaStove_v001.fbx` | B | #58 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-brewing-b/TI10_TeaSet/v001/TI10_TeaSet_v001.fbx` | B | #58 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/RI03_GreatWheel/RI03_GreatWheel_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_Broken/TE01_Broken_v002.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_Broken/v001/TE01_Broken_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_End_H08/TE01_End_H08_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_End_H12/TE01_End_H12_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_End/TE01_End_v002.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_End/v001/TE01_End_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_GentleInner/TE01_GentleInner_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_GentleOuter/TE01_GentleOuter_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_InnerBend/TE01_InnerBend_v002.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_InnerBend/v001/TE01_InnerBend_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_OuterBend/TE01_OuterBend_v002.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_OuterBend/v001/TE01_OuterBend_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_StraightA/TE01_StraightA_v002.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_StraightA/v001/TE01_StraightA_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_StraightB_H08/TE01_StraightB_H08_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_StraightB_H12/TE01_StraightB_H12_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_StraightB/TE01_StraightB_v002.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE01_StraightB/v001/TE01_StraightB_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE02_Hedge/TE02_Hedge_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE02_HedgeEnd/TE02_HedgeEnd_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE02_HedgeShort/TE02_HedgeShort_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE02_Round/TE02_Round_v004.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE02_Round/v001/TE02_Round_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE02_Round/v002/TE02_Round_v002.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE02_Round/v003/TE02_Round_v003.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE02_Tall/TE02_Tall_v004.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE02_Tall/v001/TE02_Tall_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE02_Tall/v002/TE02_Tall_v002.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE02_Tall/v003/TE02_Tall_v003.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE02_Wide/TE02_Wide_v004.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE02_Wide/v001/TE02_Wide_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE02_Wide/v002/TE02_Wide_v002.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE02_Wide/v003/TE02_Wide_v003.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE03_Path/TE03_Path_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE03_Stair/TE03_Stair_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE03_Stepping/TE03_Stepping_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE04_Basket/TE04_Basket_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE04_Tray/TE04_Tray_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/tea-terraces-b/TE05_Pavilion/TE05_Pavilion_v001.fbx` | 核心組 | #74 | A4 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-backyard-a/TY01_SpiritField_v001.fbx` | A | #56 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-backyard-a/TY01_SpiritField_v002.fbx` | A | #56 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-backyard-a/TY02_QinglingGrass_v001.fbx` | A | #56 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-backyard-a/TY02_QinglingGrass_v002.fbx` | A | #56 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-backyard-a/TY07_Gate_v001.fbx` | A | #56 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI01_BoguShelf/TI01_BoguShelf_v001.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI01_BoguShelf/TI01_BoguShelf_v002.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI02_HomeFurnace/TI02_HomeFurnace_v001.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI02_HomeFurnace/TI02_HomeFurnace_v002.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI03_JournalDesk/TI03_JournalDesk_v001.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI03_JournalDesk/TI03_JournalDesk_v002.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI04_PaperLamp/TI04_PaperLamp_v001.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI04_PaperLamp/TI04_PaperLamp_v002.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI05_LandscapeScreen/TI05_LandscapeScreen_v001.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI05_LandscapeScreen/TI05_LandscapeScreen_v002.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI06_WovenMat/TI06_WovenMat_v001.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI06_WovenMat/TI06_WovenMat_v002.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI07_LinenCurtain/TI07_LinenCurtain_v001.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI07_LinenCurtain/TI07_LinenCurtain_v002.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI08a_KeepsakeBox/TI08a_KeepsakeBox_v001.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI08a_KeepsakeBox/TI08a_KeepsakeBox_v002.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI08b_PaperScroll/TI08b_PaperScroll_v001.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI08b_PaperScroll/TI08b_PaperScroll_v002.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI08c_CeladonJar/TI08c_CeladonJar_v001.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI08c_CeladonJar/TI08c_CeladonJar_v002.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI08d_MedicinePot/TI08d_MedicinePot_v001.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/territory-interior-b/TI08d_MedicinePot/TI08d_MedicinePot_v002.fbx` | B | #54 | 領地 | — | — | 素材檔；未證實匯入 |
| `art/exports/valley-and-home-v1/FE01/Corner/v004/FE01_Corner.fbx` | Codex（舊分支交付） | 尚無 PR | A5 | — | — | 素材檔；未證實匯入 |
| `art/exports/valley-and-home-v1/FE01/End/v004/FE01_End.fbx` | Codex（舊分支交付） | 尚無 PR | A5 | — | — | 素材檔；未證實匯入 |
| `art/exports/valley-and-home-v1/FE01/Straight/v006/FE01_Straight.fbx` | Codex（舊分支交付） | 尚無 PR | A5 | — | — | 素材檔；未證實匯入 |
| `art/exports/valley-and-home-v1/FE02/v007/FE02_Ferry.fbx` | Codex（舊分支交付） | 尚無 PR | A5 | — | — | 素材檔；未證實匯入 |
| `art/exports/valley-and-home-v1/FE03/v007/FE03_FerryShed.fbx` | Codex（舊分支交付） | 尚無 PR | A5 | — | — | 素材檔；未證實匯入 |
| `art/exports/valley-and-home-v1/RI01/v014/RI01_Bund_Corner.fbx` | Codex（舊分支交付） | 尚無 PR | A6 | — | — | 素材檔；未證實匯入 |
| `art/exports/valley-and-home-v1/RI01/v014/RI01_Bund_Straight.fbx` | Codex（舊分支交付） | 尚無 PR | A6 | — | — | 素材檔；未證實匯入 |
| `art/exports/valley-and-home-v1/RI01/v014/RI01_Bund_T.fbx` | Codex（舊分支交付） | 尚無 PR | A6 | — | — | 素材檔；未證實匯入 |
| `art/exports/valley-and-home-v1/RI01/v014/RI01_Paddy.fbx` | Codex（舊分支交付） | 尚無 PR | A6 | — | — | 素材檔；未證實匯入 |
| `art/exports/valley-and-home-v1/RI02/v006/RI02_Rice.fbx` | Codex（舊分支交付） | 尚無 PR | A6 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/RK01A.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/RK01B.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/RK05.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/RK06.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/RK09.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/RK10A.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/RK10B.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/RK12A.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/RK12B.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/RK12C.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/RK12D.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/SC01.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/SC02.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/SC03.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/SC04.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/TY03A.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/TY03B.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/TY03C.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/TY03D.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/TY05A.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/TY05B.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/TY06.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/TY10A.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/TY10B.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/TY10C.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/WM08A.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/WM08B.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/WM08C.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/WM10A.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/WM10B.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/WM10C.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/world-props-a/WM10D.fbx` | A、核心組 | #68 | A1／A2／A3／D1／D3 | — | — | 素材檔；未證實匯入 |
| `art/exports/zhuo-boar-a/BR01_ZhuoBoar/BR01_ZhuoBoar_v001.fbx` | A | #61 | D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/zhuo-boar-a/BR02_YoungPine_A/BR02_YoungPine_A_v001.fbx` | A | #61 | D1 | — | — | 素材檔；未證實匯入 |
| `art/exports/zhuo-boar-a/BR02_YoungPine_B/BR02_YoungPine_B_v001.fbx` | A | #61 | D1 | — | — | 素材檔；未證實匯入 |

## 尚未接模型的區塊格位

| 區塊 | 格位 | 物件／角色 | 負責 | 配置檔 |
|---|---|---|---|---|
| A1 | `Creek_StoneBridge` | 石拱橋（取代木板踏步） | joshsu54 | `tools/qingxi-terrain/novice-village.json` |
| A1 | `Gate_Lantern_L` | 村口石燈（左） | codex | `tools/qingxi-terrain/novice-village.json` |
| A1 | `Gate_Lantern_R` | 村口石燈（右） | codex | `tools/qingxi-terrain/novice-village.json` |
| A1 | `Homes_House_01` | 民居一（藥農家） | joshsu54 | `tools/qingxi-terrain/novice-village.json` |
| A1 | `Homes_House_02` | 民居二（獵戶家） | joshsu54 | `tools/qingxi-terrain/novice-village.json` |
| A1 | `Homes_House_03` | 民居三（老夫子家） | joshsu54 | `tools/qingxi-terrain/novice-village.json` |
| A1 | `Homes_House_04` | 民居四（空屋，機緣） | joshsu54 | `tools/qingxi-terrain/novice-village.json` |
| A1 | `Homes_Well` | 井與洗衣石 | codex | `tools/qingxi-terrain/novice-village.json` |
| A1 | `Plaza_ElderTree` | 村中古樹（地標） | codex | `tools/qingxi-terrain/novice-village.json` |
| A1 | `Plaza_Well` | 水井 | codex | `tools/qingxi-terrain/novice-village.json` |
| A1 | `Shops_Teahouse` | 茶棚（休息、聽傳聞） | codex | `tools/qingxi-terrain/novice-village.json` |
| A2 | `A2_Cart` | 載貨板車（RK05） | codex | `tools/qingxi-terrain/blocks/A2.json` |
| A2 | `A2_Haystack` | 草垛（RK10） | codex | `tools/qingxi-terrain/blocks/A2.json` |
| A2 | `A2_RestPavilionRuin` | 倒塌的歇腳亭 | Johnnnny0823 | `tools/qingxi-terrain/blocks/A2.json` |
| A2 | `A2_RoadSign` | 岔路路牌（RK01） | codex | `tools/qingxi-terrain/blocks/A2.json` |
| A2 | `A2_Shrine` | 土地祠・機緣點（RK06） | codex | `tools/qingxi-terrain/blocks/A2.json` |
| A2 | `A2_TeaPavilion` | 路邊茶亭（RK03） | codex | `tools/qingxi-terrain/blocks/A2.json` |
| A2 | `A2_TeaStall` | 茶亭旁小攤（RK04） | codex | `tools/qingxi-terrain/blocks/A2.json` |
| A2 | `A2_ViewBench` | 觀景石凳（RK09） | codex | `tools/qingxi-terrain/blocks/A2.json` |
| A2 | `A2_Wayfarer` | 路人（靜態 NPC） | joshsu54 | `tools/qingxi-terrain/blocks/A2.json` |
| A3 | `A3_BambooPavilion` | 竹林小亭（WM09） | codex | `tools/qingxi-terrain/blocks/A3.json` |
| A3 | `A3_FishPlatform_Bank` | 釣魚台岸邊（WM06 接岸處） | codex | `tools/qingxi-terrain/blocks/A3.json` |
| A3 | `A3_Miller` | 磨坊主（NPC） | joshsu54 | `tools/qingxi-terrain/blocks/A3.json` |
| A3 | `A3_MillHouse` | 水磨坊主屋（WM01） | codex | `tools/qingxi-terrain/blocks/A3.json` |
| A3 | `A3_Millstones` | 磨盤堆與麻袋（WM04） | codex | `tools/qingxi-terrain/blocks/A3.json` |
| A3 | `A3_StoneBridge` | 單拱石橋（WM07） | codex | `tools/qingxi-terrain/blocks/A3.json` |
| A3 | `A3_WashSteps` | 洗衣石階埠頭（WM05） | codex | `tools/qingxi-terrain/blocks/A3.json` |
| A3 | `A3_WaterWheel` | 水車（WM02） | codex | `tools/qingxi-terrain/blocks/A3.json` |
| A3 | `A3_WestSign` | 往湖岸路牌 | codex | `tools/qingxi-terrain/blocks/A3.json` |
| D1 | `D1_HunterShed` | 獵人的工具棚 | core | `tools/qingxi-terrain/blocks/D1.json` |
| D1 | `D1_WatchTower` | 林緣瞭望台（獵人用的木台） | core | `tools/qingxi-terrain/blocks/D1.json` |
| D3 | `D3_DamRemains` | 斷流石壩遺跡（區塊地標，待規劃） | core | `tools/qingxi-terrain/blocks/D3.json` |
| D3 | `D3_FallenShrine` | 倒在路邊的土地公小廟 | Johnnnny0823 | `tools/qingxi-terrain/blocks/D3.json` |
| D3 | `D3_HunterCamp` | 熄掉的營火與獵人的木凳 | Johnnnny0823 | `tools/qingxi-terrain/blocks/D3.json` |

## 查核限制

- 同名 Unity FBX 與輸出 FBX 只證明檔名相同；素材版本、渲染、碰撞與實際可達性須進 Unity 確認。
- 生成程式可能在執行時條件式放置；程式引用不等於遊戲畫面已看見。
- 本清冊逐一列出 FBX 與無對應 FBX 的 GLB，包含舊版與變體；數量不是可獨立擺放物件數。
- 只有貼圖、JSON 或原始檔的素材組列於總覽，沒有模型檔可對位，須另外判定。
