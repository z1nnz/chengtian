# 11/03 工作包總表｜誰做什麼，不做重複的東西

> 2026-11-02，Claude Code（核心組）依 z1nnz 指示撰寫：「把其他人的包也一起做，不要讓他們做重複的東西」「他們之前做過的工作包都有紀錄，我要做新的東西」「工作量大概 28 小時」。
> 寫之前對過 `docs/execution/` 裡所有舊工作包、Codex 工作單和 `art/` 裡的模型。開工前先看這一頁。美術標準和 AI 提示詞照 [美術風格指南](../art-style-guide-v1.md)。

## 1. 三份工作包

| 誰 | 工作包 | 時數 | 主題 |
|---|---|---:|---|
| A｜鄭翔元 John | [A-28h-riverside-fishing.md](A-28h-riverside-fishing.md) | 28 | 第 9 天溪邊釣魚烤魚＋三個還空著的舊場景 |
| B｜蘇奕安 Josh | [B-56h-repairing-the-creek.md](B-56h-repairing-the-creek.md) | 56 | 第 5–8 天修水路＋山城三個攤位 |
| C｜Eli-0731 | [C-28h-mountain-city-landmarks.md](C-28h-mountain-city-landmarks.md) | 28 | 山城地標、故事小道具＋灌木和地被（只做模型） |

三份互不依賴，不用等別人交件。

## 2. 這一輪的新東西，每一件只有一個人做

| 東西 | 歸誰 |
|---|---|
| 村會沙盤、舊信、瓦、曆書、工地料堆、鏟與夯等工具、涼棚和茶水、土堤渠、竹木渡槽、溪邊慶祝擺設、每戶分水小閘 | B |
| 護身符攤、麵攤和麵碗、人間榜 | B |
| 釣魚和烤魚玩法、三種魚、魚竿、魚簍、溪邊烤架 | A |
| 倒下的土地公小廟、獵人營地、倒塌的歇腳亭 | A |
| 飛升榜、大鐘和鐘架、高塔、被鑿掉一行的古碑、小本子、舊油紙傘 | C |
| 灌木 3 種、蕨 2 種、苔蘚貼片、落葉貼片 | C |
| 人物、對白、音樂、伺服器、主場景 | 核心組 |

想做沒列到的東西，先問核心組。

## 3. 已經有或已經排給別人，不要再做

| 東西 | 在哪裡或誰的 |
|---|---|
| 建木、樟、楓、銀杏、柳、梅、圓柏、枯樹 | `art/exports/elder-trees-v1` |
| 松、竹 | `art/incoming/dondon/CommonPine`、`BambooClump` |
| 小松 | `art/exports/zhuo-boar-a` BR02 |
| 倒木、樹根樁、苔石、層岩 | `art/exports/qingxi-encounter-a` A03–A06 |
| 蘆葦、蕨草花叢、野花、草 | `qingxi-detail-props-v2`、`qingxi-prop-kit-v1`、`qingxi-gathering-visual-kit-v1` |
| 枯水草、木樁水位尺、泥沙洲 | `art/exports/qingxi-waterhead-a` |
| 石牆、竹籬、柴堆、石燈、里程石、枯井、翻倒的車、舊屋 | `art/exports/qingxi-world-ruins-b` |
| 水槽、閘板、閘輪、補石、浮標、壓水樁、推車、完工碑座 | `art/exports/qingxi-waterworks-b` B01–B12 |
| 水桶、扁擔、濕度木牌、施工布旗、修渠工具箱、共修石牌、議事矮桌 | `art/exports/qingxi-water-report-c` C01–C08 |
| 斷流石壩、溫石、水位石樁、平石、蒲團矮几香爐、提燈 | `art/exports/qingxi-day34-c` |
| 茶亭、茶攤、茶爐、茶具 | `art/exports/tea-brewing-b` 等 |
| 桿秤、竹篩、價目牌、背簍 | `art/exports/harvest-market-b` |
| 回村背籠、分揀桌、座凳、油紙燈 | `art/exports/qingxi-return-c` |
| 村中茶棚、水井、村口燈 | Codex 工作單 C7 |
| 水磨坊、水車、引水渠、木釣魚台、石橋、踏石、水邊小花草 | Codex 工作單 C9 |
| 路牌、板車、土地祠、路燈、草垛、路邊野花 | Codex 工作單 C10 |

11/01 工作包的「N01–N08 自然套件」**取消**：樹和倒木已經有了，只留下真正還缺的灌木和蕨給 C。

## 4. 哪些東西不嫌多

這幾類世界越大越需要，可以同類很多件，但**每件要有自己的外形**，不要只靠旋轉、縮放、換色，也不要和第 3 節的東西長得一樣：灌木和地被的新品種、石頭的新形狀、不同人家的生活小物、賣不同東西的攤位。工作包做完還想多做這幾類，直接做、照規則交，寫清楚是額外的。
