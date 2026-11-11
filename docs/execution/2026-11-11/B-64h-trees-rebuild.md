# B｜64 小時：世界裡的樹全部重做（九種）

> 交給 joshsu54（Josh）。2026-11-11，Claude Code 依 z1nnz 指示撰寫：「所有樹的模型叫協作者 Josh 改一下」。大小由核心組定為 64 小時。
> **順序**：先把 11/09 那份 112 小時包**手上這一批**做完，接著就做這份；11/11 的 40 小時院牆水井包排在這份後面。
> 這一輪**只做模型**，不做玩法、人物、文字。

---

## 0. 先讀

- 標註規則：[`docs/standards/labeling-v1.md`](../../standards/labeling-v1.md)
- 交件規則與提示詞固定段：照 [11/07 你的包](../2026-11-07/B-104h-tea-wheel-and-mountain-way.md) 第 1 節與附錄（單件 Layout 段、5.2、5.3）
- 風格色票：[`docs/art/modeling-style-spec-v1.md`](../../art/modeling-style-spec-v1.md) 第 2、11 節
- 畫質分級：`docs/standards/quality-tiers-v1.md` 第 4 節
- 現在的樹：`art/exports/elder-trees-v1/`（核心組 10/30–10/31 做的），只當「哪裡要放什麼樹、多高」的參考，**不要沿用它的做法**

## 1. 為什麼重做

11/11 進遊戲看，樹是畫面最弱的一塊：

1. **樹冠像雜訊**：葉片貼圖是一顆顆小點，遠看是一團閃爍的顆粒，讀不出葉團的形狀（紅楓、垂柳、樟樹最明顯）。
2. **太鮮豔**：螢光綠、亮黃的銀杏、粉白的枯樹皮，和你的民居、梯田放在一起不像同一個世界。
3. **風格不統一**：松樹是一層層平的葉盤，闊葉樹是雜訊團，兩種語言混在一起。
4. **太重**：一棵 40 萬到 75 萬個三角面（LOD0），手機撐不住。

你的 **TE02 茶樹**是我們要的方向：葉片卡組成有厚度的葉團，輪廓清楚，顏色沉穩，有頂點色做風。這包就是把那套做法放大到整棵樹。

## 2. 要交的東西

每一種交 **3 個變體**（A、B、C：同一套樹皮和葉團，枝幹和樹冠的排法不同，遠看要分得出來）。

| ID | 樹種 | 自然高度 | 用在哪 | 重點 | 時數 |
|---|---|---|---|---|---:|
| TR01 | 松 | 12–14 m | A1、A2、A4、B1、全區 | 樹幹彎、樹皮龜裂泛紅褐，針葉成幾團有厚度的雲狀葉團（不是平的盤子）；B1 用的崖松要更歪、更瘦 | 8 |
| TR02 | 柏 | 9–11 m | D1、D2、D4 古林 | 古林的主角：樹幹粗、扭、有瘤和裂，樹冠深綠偏暗、往上收成尖塔形；苔從根部往上爬 | 7 |
| TR03 | 樟 | 14–16 m | A1 村中、院子 | 村子的大樹：樹冠寬圓、厚，葉團大而密，樹蔭要能罩住一個小廣場 | 8 |
| TR04 | 楓 | 8–9 m | D3 上游、A3 | 紅要**沉**（暗赭紅、鏽紅，不是亮橘紅），樹冠分成幾層，枝條細 | 7 |
| TR05 | 銀杏 | 17–19 m | A1 地標一棵、D3 | 金要**舊**（暗金、黃褐，不是檸檬黃），樹形高直，樹冠扇形葉團 | 7 |
| TR06 | 垂柳 | 12–13 m | A3、A1 溪邊 | 垂下的枝條是一束束長條葉片卡，會隨風擺；樹幹斜向水面 | 8 |
| TR07 | 梅 | 6–8 m | A1 院子 | 枝幹虬曲、黑褐，花是淡白微粉的小花團，點綴不鋪滿 | 6 |
| TR08 | 枯樹 | 9 m | A1、A9 | 沒有葉子，樹皮灰褐（不是粉白），有斷枝和樹洞 | 5 |
| TR09 | 竹叢 | 5–6 m | 溪邊、A8 竹海 | 取代 Dondon 的 BambooClump：竹竿有節、粗細不一，葉片成串下垂；要能密種 60 叢以上 | 4 |
| 全包檢查 | 並排與林相 | — | — | 九種並排一張（附 1.75 m 人形尺和你的 VL 民居）；每種三個變體並排；一片 30 × 30 m 的混種林相截圖 | 4 |
| **合計** | | | | | **64** |

**不做**：神木（ElderGuardian）、建木苗（JianmuSapling）是故事地標，等故事定稿再談。

## 3. 規格

| 項目 | 規定 |
|---|---|
| 面數（每棵） | LOD0 ≤ 25,000；LOD1 ≤ 8,000；LOD2 ≤ 2,500；**LOD3 遠景卡**（交叉面片或廣告板）≤ 200。竹叢、梅、枯樹各減半 |
| 貼圖 | 每種一套：樹皮可平鋪 1024、葉團圖集 2048（含透明）。Albedo／Normal／MaskURP，和你的 VL 一樣的命名 |
| 葉團 | 葉片卡組成有體積的葉團；葉團圖集是**畫出來的葉群**（看得到一片片葉形），不是雜訊點。透明邊緣照你 TE02 的設定（alpha clip 0.5、Mip Maps Preserve Coverage） |
| 顏色 | 照風格色票第 2、11 節。綠色偏灰、偏藍，陰影帶藍紫，不要螢光綠；同一套光下和你的民居、梯田放在一起要協調 |
| 風 | 頂點色寫風的權重，和 TE02 一樣：樹幹 0、粗枝少、葉團和枝梢多 |
| 原點 | 樹幹底部中心，z = 0 在地面；根部往下埋 0.3 m，放在斜坡上不會露空 |
| 碰撞 | 樹幹一個膠囊（或簡單凸包），樹冠不擋人 |
| `minTier` | 全部 `low`（樹是世界的骨架，每個畫質都要有）；LOD3 給低畫質和遠景 |
| `model_info.json` | 照 11/08 包的寫法：每個 LOD 的三角面、物件數、材質數、貼圖解析度 |

## 4. 驗收

1. 每種交齊：三視圖（先選一張再建）、灰模、線框、LOD 對照、人形尺。
2. **一眼分得出是哪種樹**：不看標籤，松、柏、樟、楓、銀杏、柳、梅、枯樹、竹都要認得出。
3. **遠看**：50 m、100 m 外的截圖各一張，樹冠還是一團團的葉團，不閃、不糊成雜訊。
4. 逐件標 Exported／Imported／Visually Verified／In-game Verified，沒驗的寫未驗。
5. Unity 檢查用 **6000.3.28f1**。

核心組負責換進世界（`QingxiElderTrees` 會改成讀你的 TR 系列）。**不改主場景、不改區塊 JSON、不改世界填充表。**

## 5. 分支與 PR

| 批 | 分支 | PR 標題 |
|---|---|---|
| A | `art/b-1111-tr-trees-conifer` | `【B】11/11 TR01–TR02：松、柏` |
| B | `art/b-1111-tr-trees-broadleaf` | `【B】11/11 TR03–TR07：樟、楓、銀杏、垂柳、梅` |
| C | `art/b-1111-tr-trees-bare-bamboo` | `【B】11/11 TR08–TR09：枯樹、竹叢` |

**TR01 松先交一棵樣品**開在 A 批的 PR 上。沒等到回覆也可以繼續做，審查意見來了再改。

## 6. 規則

1. **commit 用你自己的 GitHub 帳號**，不用 z1nnz，也不掛 Claude Code 或其他 AI 的名字。
2. 素材資料夾 README 開頭照標註規則第 5 節。
3. 不做人物、動物、文字、玩法、主場景。

## 7. 物件句（正面提示 = 物件句 + 單件 Layout 段 + 5.2；負面用 5.3，另加下面這句）

```text
no noisy speckled leaves, no pixel noise foliage, no neon green, no lemon yellow, no orange-red, not a photo-scanned tree, not Japanese bonsai, no flat plate-like leaf pads
```

**TR01**
```text
Three-view orthographic turnaround sheet of a mature Chinese pine tree about 13 m tall, a curved trunk with deeply fissured reddish-brown bark, a few strong horizontal limbs, the needles gathered into five to eight thick rounded cloud-like foliage masses with clear depth and soft shading, muted blue-green needles, a hand-painted stylized game tree with a strong readable silhouette.
```

**TR02**
```text
Three-view orthographic turnaround sheet of an ancient old-forest cypress tree about 10 m tall, a thick twisted trunk with burls, deep cracks and moss climbing from the roots, dense dark green foliage gathered in layered masses that narrow toward a tall pointed crown, a hand-painted stylized game tree, solemn and old.
```

**TR03**
```text
Three-view orthographic turnaround sheet of a large village camphor tree about 15 m tall, a stout grey-brown trunk splitting into several big limbs, a very wide rounded dense crown made of large overlapping leaf clusters, muted glossy sage-green leaves, deep shade under the crown, a hand-painted stylized game tree.
```

**TR04**
```text
Three-view orthographic turnaround sheet of a Chinese maple tree about 8.5 m tall in autumn, a slim dark trunk with fine branching, the crown in several separate layered leaf masses of deep rust red and dark ochre, muted and earthy rather than bright, a hand-painted stylized game tree.
```

**TR05**
```text
Three-view orthographic turnaround sheet of an old ginkgo tree about 18 m tall in autumn, a tall straight grey trunk, upward-reaching limbs, fan-shaped leaf clusters in antique gold and brownish yellow, soft and aged rather than bright, a few fallen leaves at the base, a hand-painted stylized game tree.
```

**TR06**
```text
Three-view orthographic turnaround sheet of a weeping willow about 12.5 m tall leaning over water, a gnarled trunk tilted to one side, long thin hanging branch strands in bundles almost reaching the ground, soft muted grey-green leaves, a hand-painted stylized game tree.
```

**TR07**
```text
Three-view orthographic turnaround sheet of an old Chinese plum blossom tree about 7 m tall, a crooked dark brown-black trunk and angular twisting branches, sparse small clusters of pale white blossoms with a faint pink tint dotted along the branches, a few young leaves, a hand-painted stylized game tree.
```

**TR08**
```text
Three-view orthographic turnaround sheet of a dead leafless tree about 9 m tall, grey-brown weathered bark peeling in places, broken-off limbs, one hollow in the trunk, bare twisting branches, a hand-painted stylized game tree, lonely but not spooky.
```

**TR09**
```text
Three-view orthographic turnaround sheet of a clump of Chinese bamboo about 5.5 m tall, a dozen culms of different thickness with clear nodes, green to yellowish green with darker old culms, slender leaves hanging in drooping sprays near the top, a hand-painted stylized game plant.
```

---

有問題直接問；寫不清楚的地方先照最保守的做法做，寫進 PR。
