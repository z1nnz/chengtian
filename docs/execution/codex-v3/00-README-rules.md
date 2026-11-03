# Codex 工作包 v3｜開工前先讀（索引與規則）

> 2026-11-03，Claude Code 依 z1nnz 指示撰寫：「安排 Codex 三天的工作包，每包 50 小時；讓它了解故事、遊戲的全部內容和現在的進度，細節要鉅細靡遺。」
> **這個資料夾取代 `codex-v2/` 的任務清單**（C1–C12）。`codex-v2/00-operating-rules.md` 的製作流程仍然有效，本頁寫的是改動的地方；衝突時以本頁為準。

## 1. 三個工作包

| 順序 | 檔案 | 主題 | 時數 | 工作樹與分支 |
|---|---|---|---:|---|
| 必讀 | [01-project-briefing.md](01-project-briefing.md) | 故事、遊戲、進度、誰做什麼 | — | — |
| 第 1 天 | [D1-sky-and-distance.md](D1-sky-and-distance.md) | 抬頭看到的世界：月亮、遠景、雲、中景山、地面、小生命 | 50 | `yun-jing-rpg-codex-v3-d1`／`feature/codex-v3-d1-sky` |
| 第 2 天 | [D2-valley-and-home.md](D2-valley-and-home.md) | 把河谷做完：屋內外殼、水井、茶棚、東坡茶田、稻田大水車、渡口、古林小地標 | 50 | `yun-jing-rpg-codex-v3-d2`／`feature/codex-v3-d2-valley` |
| 第 3 天 | [D3-mountain-city.md](D3-mountain-city.md) | 垂直山城：飛升榜、大鐘、高塔、太玄分院、街屋、索橋 | 50 | `yun-jing-rpg-codex-v3-d3`／`feature/codex-v3-d3-city` |

照順序做。三包不互相依賴：其中一包卡住，就跳到下一包，回報裡寫清楚。「50 小時」是工作量的估計，不是要你拖時間；比時間更重要的是通過第 4 節的關卡。

## 2. 開工步驟

每一包開工時，在 repo 裡執行（工作樹一定放 `D:\yun-jing-rpg-workspace\`）：

```powershell
git fetch origin
git worktree add -b feature/codex-v3-d1-sky D:\yun-jing-rpg-workspace\yun-jing-rpg-codex-v3-d1 origin/feature/qingxi-creek-chapter
```

第 2、3 天換成上表的名稱。要從 `feature/qingxi-creek-chapter` 開，**不要從 main 開**：故事文件、區塊資料和這份工作包都在這條分支上。

不要用舊工作樹（distant-peaks、interior-kit、village-props-c7 等）繼續做，但可以讀裡面的舊檔案來重用。

## 3. 和 v2 不同的規則

**這六條是 2026-11-02 z1nnz 新定的：**

1. **這三包只做模型和美術，不做玩法。** 遊戲的方向是以建模為主，把世界建得好看。
2. **不做人物。** 人物的故事、名字、誰會出現都還沒定。不做人物模型、人物專屬道具，也不把人物名字寫進資產名稱。擺設不寫死台詞。
3. **不重複。** 開工前看 [11/03 總表](../2026-11-03/00-overview.md)第 2、3 節和本包「不要做」一節。A、B、C 手上正在做的東西不要碰；要重用既有模型，不要重做。
4. **照[畫質分級](../../standards/quality-tiers-v1.md)交件**：同一份模型，畫質越高看到越多。LOD0 不減面，LOD1 是手機近處會看到的版本，也要好看。可有可無的小東西做成 `Detail_*`，`model_info.json` 寫 `minTier` 和 `detailObjects`。
5. **品質優先，不要求降面數**（取代 v2 第 7 節和舊工作單的面數上限）。面數寫實際數字，不准承諾 FPS；手機還沒實測。
6. **不刻字、不寫字、不寫數字。** 要顯示字的地方留空白，由遊戲 UI 疊上去（風格指南第 5 節的負面提示已經包含）。舊工作單寫要刻字的（例如 C10 路牌）一律作廢。

**不要動故事。** 《設定總集》開頭第〇節寫著請 Codex 調整故事內容，那是另一次工作，**這三包只讀不改**。讀到不合理的地方，寫進回報。

**提示詞**：用 [美術風格指南](../art-style-guide-v1.md) 第 5 節：照骨架填【】，後面接 5.2 固定風格段，負面欄貼 5.3，同一段至少出 4 張挑最好的，存 `art/references/<編號>/prompt.txt`。規格表沒寫到的部分你自己決定，寫進 README。本包的三視圖一律先於建模。

**生圖額度用完時**：不要停。先做不用生圖的部分（灰模、腳本、貼圖、LOD、文件），同時用已經存下來的參考圖繼續，回報哪幾件缺參考。

## 4. 流程和關卡（照 v2 第 4–6 節）

每一件：Stage 0 分析 → 1 三視圖 → 2 灰模 → 3 精修 → 4 拓樸與 UV → 5 材質貼圖 → 6 匯出回匯。每階段過視覺檢查，寫進 `PRODUCTION_STATUS.md`，Gate 寫 PASS／FAIL／UNVERIFIED。同一階段最多修 3 輪，還是 FAIL 就留最好的版本、寫清楚，做下一件。

技術上必過：Blender QA `errors = 0`；FBX 回匯尺寸誤差 ≤ 2 cm；原點和底部高度符合規格。

美術上必過（**以這個為準**）：
- 40 m 外輪廓認得出；
- 看得出是木、石、瓦、布、銅；有生活痕跡；
- 顏色符合[建模規格](../../art/modeling-style-spec-v1.md)第 2 節和第 11 節的區域色票；
- 和既有作品並排是同一個世界，指得出至少三個共同點；
- 不是方塊和圓柱拼的灰模。

## 5. 交件

每一件：Blender 母檔、可重跑的腳本、FBX＋GLB、貼圖、預覽（正、側、背、3/4、線框、中性光、遊戲風格光、1.75 m 人形尺、LOD0／LOD1 對照並關掉 `Detail_*`）、`model_info.json`。每一包：`README.md`、`PRODUCTION_STATUS.md`。

路徑：`art/references/`、`art/source/`、`art/exports/`、`art/previews/` 底下各用該包的套件資料夾（寫在每包裡）。**不覆蓋、不刪除既有檔案**，新版本另存。

**狀態四分法**：Exported／Imported／Visually Verified／In-game Verified。最後一項由 Claude Code 整合時做，你不用做。

**不 commit、不 push、不開 PR**，不改 `.gitattributes`、`.gitignore`、`apps/game/Assets/YunJing/Editor`、`Runtime`、`.unity` 場景、`ProjectSettings`。做完留在工作樹，Claude Code 檢查後以 z1nnz 名義提交。不確定就停下來寫進回報，不要猜。

## 6. 回報格式

每完成一包回報一次：

```
【D1 完成／部分完成／卡住】
1. 每件的狀態：編號｜Exported｜Imported｜Visually Verified｜最後一張預覽路徑
2. 實際數字：各級面數、貼圖、檔案大小
3. 技術檢查（QA errors/warnings 和接受理由）
4. 視覺檢查：每件最後 Gate；自己最不滿意的三件和原因
5. 沒做、沒驗證、需要人工的事
6. 生圖用量
7. 讀故事和設定時發現的矛盾（不要自己改）
```

不得宣稱做了實際沒做的事。誠實的 FAIL 比假的 PASS 有用。
