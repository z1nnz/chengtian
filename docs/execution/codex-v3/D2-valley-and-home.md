# D2｜第 2 天：把河谷和家做完（約 50 小時）

> 開工前先讀 [00-README-rules](00-README-rules.md) 和 [01-project-briefing](01-project-briefing.md)。
> 工作樹 `yun-jing-rpg-codex-v3-d2`，分支 `feature/codex-v3-d2-valley`。資產資料夾 `valley-and-home-v1`。

## 0. 為什麼做這些

遊戲的順序是**先把一個區域做完整**。河谷 A1–A3 大家在補，但玩家每天回去的**家**還沒有正式外殼，河谷另外三塊 A4、A5、A6 完全沒有模型。第 8 天水要流過每一戶田，田和大水車不能沒有。

| 段 | 內容 | 時數 |
|---|---|---:|
| 一 | 領地屋內外殼收尾（C2） | 10 |
| 二 | 村中格位：水井、井與洗衣石、茶棚（C7 收尾） | 6 |
| 三 | A4 東坡茶田 | 12 |
| 四 | A6 稻田與大水車 | 10 |
| 五 | A5 河灣蘆葦渡口 | 7 |
| 六 | 古林的兩個小地標：D4 石祠、D5 蕈群 | 5 |
| | **合計** | **50** |

**優先順序照表**。格位名稱如下；A4、A5、A6、D4、D5 的區塊地圖還沒有，核心組會照你的尺寸排，所以尺寸上限要守住。

區域風格：A 河谷，暖舊木、石灰牆、灰青瓦、夯土，晨光暖、薄霧。D 古林，黑舊木、苔石、深樹皮 `#2B2018`、蕈光青 `#8FE3C8`（面積少）。

## 1. 領地屋內外殼（10 h）

玩家每天進出的家，現在有 B 的家具（`territory-interior-b` TI01–08、`tea-brewing-b` TI09、TI10），但屋子本身是舊的。你的 C2 已經做到 v035（舊工作樹 `yun-jing-rpg-interior-kit-v1` 的 `art/exports/lodging-interior-kit-v1`），重用它，**不要從頭做**，只修第二輪審查（`codex-v2/review-2026-10-30.md`）說的問題：

1. **窗和門要和外屋對上**：外屋 `art/incoming/dondon/StarterHouse`（三面格窗、雙開門）。推門進來，門和窗的位置要和外面看到的一樣。外觀不用改。
2. **加後門**：通往後院（領地後院靈田那一邊）。
3. **放得下家具**：把 TI01–TI10 依 `docs/execution/2026-10-31/02-B-territory-interior.md` 的格位擺進去，出一張人眼高度的圖。

**晨光要能從窗戶照進來**：窗要真的透光（窗紙獨立材質），`minTier: standard`。不動 `Runtime`、`QingxiLodgingInteriorBuilder`，只交模型和擺放表 `room-layout.json`（每件編號、位置、旋轉）。

驗收：同一角度外觀和室內並排，門窗對得上；站在屋裡看得到後門。

## 2. 村中格位（6 h）

C7 的 VP01 不用了（C 交了村口石燈 G01）。做完 VP02–04，規格照 [C7 工作單](../codex-v2/C7-village-slot-props.md)，**面數上限作廢**。

| 編號 | 格位 | 世界座標／尺寸上限 | 時數 | 重點 |
|---|---|---|---:|---|
| VP02 | `Plaza_Well` | 1.8 × 1.8 × 2.4 | 2 | 圓形石井欄、木架轆轤，全村共用 |
| VP03 | `Homes_Well` | 2.0 × 2.0 × 2.4 | 2 | 較舊，方形；洗衣石有磨痕、濕痕、木盆 |
| VP04 | `Shops_Teahouse` | 3.6 × 3.0 × 3.0 | 2 | 四根竹木柱的茶棚，走得進去，只擋柱子和桌子 |

和 B 的茶攤 RK04、C 的茶亭 RK03 並排，外形要一眼看得出不同。

## 3. A4 東坡茶田（12 h）

從村子往東上坡，第 5 天往山城的路從這裡開始。**這是全河谷最適合拍照的地方**：一階一階的茶田，高處一座亭子看得到山城。

| 編號 | 東西 | 尺寸上限 | 時數 | 規格 |
|---|---|---|---:|---|
| TE01 | 梯田模組 | 每段 8 × 4 m，階高 0.8–1.2 m | 4 | 乾砌石擋土牆加土面。直段 2 種、內彎、外彎、收尾、斷口（共 6 件），**接口對齊 1 m 格線**，能順著等高線接出弧形；可走，附 `_Collision` |
| TE02 | 茶樹 | 高 0.8–1.1 m，寬 1.2 m | 3 | 圓整修剪過的灌木叢，3 種外形；嫩芽尖端偏亮黃綠。成排種，所以要跑得動：面片葉，頂點色存風的權重。**不是 C 的野灌木**，要看得出是人修剪的 |
| TE03 | 田間石階和小徑 | 寬 1.2 m | 1.5 | 石階段、土徑段、踏腳石，接 TE01 |
| TE04 | 採茶竹簍和晾茶竹匾 | 0.5–1.2 m | 1 | 有人剛離開的感覺；`Detail_*` |
| TE05 | 觀景亭 `A4_ViewPavilion` | 5 × 5 × 5 | 2.5 | 木亭、四柱、青瓦翹角，比茶亭 RK03 高一點，朝東開闊，朝東能看到山城 |

組裝預覽：用 TE01–05 拼一片 40 × 40 m 的山坡，從下往上看，和 `A-river-valley.png` 的梯田並排。

```
TE01  Three-view and three-quarter concept of a modular dry-stone terrace wall for hillside tea fields, each section 8 m long and 1 m high, holding a 4 m deep level soil step, made of fitted warm-grey fieldstones with soil and grass in the joints, with details: a small water runoff gap, ferns in the wall, a few tumbled stones, water: none. Layout: one three-quarter view of three terraces rising, plus front, side and top orthographic views of one wall section alone on a plain light warm-grey background, same scale.

TE02  Three-view orthographic turnaround sheet of a neatly pruned tea bush in a hillside tea field, about 1.2 m wide and 1 m tall, a rounded flat-topped dome of small dense glossy leaves with bright yellow-green young shoots on top, made of woody stems and leaves, showing plucked tips, a few older dark leaves near the bottom, soil at the base, tended by hand for many years. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.

TE05  Architectural concept of an open hilltop viewing pavilion above tea terraces for villagers and travellers to rest, footprint about 5 m wide and 5 m deep, ridge 5 m high, timber post-and-beam frame with gently upturned eave corners, blue-grey clay tile roof with a moss-covered ridge, open on all sides with a low railing and a bench along it, worn stone plinth with three steps, details: a wooden signboard without text, a clay water jar, weathering: sun-faded timber on the east side, a repaired roof corner with newer tiles. Layout: one three-quarter view from slightly above at eye height of a person, plus front, side and back orthographic views on the same sheet at the same scale, plain light warm-grey background, even soft lighting, building only (no landscape around it except a small ground patch).
```

## 4. A6 稻田與大水車（10 h）

村子東南的田。第 8 天水回來時，音樂起、水流過每一戶田，**就是這裡**。

| 編號 | 東西 | 尺寸上限 | 時數 | 規格 |
|---|---|---|---:|---|
| RI01 | 水田模組 | 每塊 10 × 6 m | 3 | 田埂土堤圍成，田面有三種狀態：`Dry`（裂土）、`Flooded`（有水）、`Grown`（秧苗）。**狀態用材質參數和可開關的子物件**；田埂接得起來，直段、轉角、T 字。田面水不做動畫 |
| RI02 | 稻 | 高 0.8 m | 2 | 3 種成長（秧苗、綠、金黃），面片，可大量擺；`minTier: standard`，密度由核心組調 |
| RI03 | 大水車 `A6_GreatWheel` | 直徑 9 m，寬 2 m | 3.5 | 灌溉用翻水車，比 B 的磨坊水車（4.6 m）大一倍，輪緣綁竹筒把水舀上來倒進高處的木槽。**原點在轉軸中心**，軸要正圓；附木槽和石座支架（獨立，不轉）。附 `_Collision` |
| RI04 | 田邊擺設 | 0.5–2 m | 1.5 | 稻草人（**不做臉**）、田間小土地石、竹架、水牛的木犁（不做牛）；`Detail_*` |

B 正在做的水渠接田的小閘（CR09）寬 0.8 m；田埂留 0.8 m 的缺口格位 `Slot_Inlet`，**不用等 B**。

```
RI03  Three-view orthographic turnaround sheet of a great irrigation water wheel, about 9 m in diameter and 2 m wide, a huge spoked bamboo and timber wheel with many tilted bamboo tubes lashed around the rim that lift water and pour it into a raised wooden trough, on heavy stone and timber supports, made of old timber, split bamboo and hemp rope, showing wet dark lower spokes, algae, lashings repaired with fresh rope, drips from the tubes, used to water rice fields in a mountain valley. Layout: front view, side view and back view side by side in one image, all at the same scale and aligned on the same ground line, orthographic (no perspective), centred, full object visible with margin around it, plain light warm-grey background, even soft studio lighting so shapes and materials read clearly, no cast shadows on the background, one object only.
```

## 5. A5 河灣蘆葦渡口（7 h）

| 編號 | 東西 | 尺寸上限 | 時數 | 規格 |
|---|---|---|---:|---|
| FE01 | 木棧橋 | 每段 3 × 1.6 m | 2 | 直段、轉角、盡頭平台；木樁入水（水下 1 m），可走 |
| FE02 | 擺渡船 `A5_Ferry` | 6 × 1.8 × 1.2 | 3 | 平底木船，竹篷（可開關子物件），一根長篙；擺在水上；原點在吃水線中心 |
| FE03 | 渡口小棚 `A5_FerryShed` | 3 × 2.5 × 2.6 | 2 | 候船的小棚和一塊空白木牌、繫纜樁 |

水面不做，蘆葦用現有的（`qingxi-detail-props-v2`、`QX_WaterReeds`）。和你以前的 A3 風格一致；舊 C9 的釣魚台不做。

## 6. 古林的兩個小地標（5 h）

| 編號 | 東西 | 格位／尺寸 | 時數 | 規格 |
|---|---|---|---:|---|
| FO01 | 半埋的苔石古祠 | `D4_MossShrine`，7 × 6 × 4.5 | 3 | D4 地標，古老、石造，被根和苔蓋住一半，門洞黑暗；比 A 的小土地祠大很多，不是同一類。附 `_Collision` |
| FO02 | 發光蕈群 | `D5_GlowCap`，每叢 1–2.5 m，3 種 | 2 | 高矮不一，傘面帶蕈光青 `#8FE3C8`，參數 `_Glow`（白天 0.2、夜晚 1）；頂點色存風。`minTier: standard` 留一款，其餘 `high` |

## 7. 不要做

- **A、B、C 的東西不要做**：水磨坊、小水車、石橋、埠頭、竹林小亭、板車、土地祠、路牌、草垛、踏石、溪石、灌木、蕨、舊石碑。
- 不做人物、水牛、NPC；不做水面著色器；不改 `Runtime`、場景。
- 不要把稻草人做成有表情的角色。
- 不寫字：招牌全部空白。
