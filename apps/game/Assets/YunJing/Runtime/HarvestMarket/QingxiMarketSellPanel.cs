using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UI;
using QingxiWorld;
using YunJing.Alchemy;

namespace YunJing.HarvestMarket
{
    // 坊市・出售, at joshsu54's herb stall (Market_HerbalStall). Left: the bundles the player brought, each "賣" or
    // "留著". Right: the stall's 今天收 board. 秤: the steelyard counterweight slides out (1 s), the coins show,
    // a coin string drops on the table, the stall keeper says a line or two. Kept bundles go back to the bag.
    // Never a loss: no haggling, nothing refused, the lowest grade still pays. Ends with market.sold.
    public sealed class QingxiMarketSellPanel : MonoBehaviour
    {
        public static QingxiMarketSellPanel Current { get; private set; }

        public Transform scaleWeight;                    // MK01 counterweight, slides on its local X
        public float weightMin = .04f, weightMax = .5f;  // MK01 spec: 0–0.5 m along the beam
        public float weighSeconds = 1f;
        public Transform coinDrop;                       // where the coin string lands on the table
        public GameObject coinStringPrefab;              // MK03 coin string; empty means a placeholder
        public int day = 4;

        public bool Open { get; private set; }
        public bool Weighed { get; private set; }
        public HarvestSettlement Last { get; private set; }
        public readonly List<bool> Sell = new List<bool>();

        Canvas canvas; RectTransform panel, left, result; readonly List<Button> toggles = new List<Button>();
        Button weighButton, doneButton; Text keeper, coinsText; Vector3 weightHome; bool weightHomeSet;

        void Awake() { Current = this; }

        public void Show()
        {
            if (Open) return;
            Open = true; Weighed = false; Last = null; Sell.Clear();
            foreach (var _ in HarvestCarry.Bundles) Sell.Add(true);
            if (scaleWeight != null && !weightHomeSet) { weightHome = scaleWeight.localPosition; weightHomeSet = true; }
            Build();
            QingxiFirstPerson.Current?.SetMenuOpen(true);
        }

        public void Close()
        {
            if (!Open) return;
            Open = false; if (canvas != null) Destroy(canvas.gameObject);
            QingxiFirstPerson.Current?.SetMenuOpen(false);
        }

        void Build()
        {
            canvas = HarvestUi.Canvas("MarketSellCanvas", 21);
            panel = AlchemyUi.Slips("SellPanel", canvas.transform, Vector2.zero, Vector2.one, new Vector2(60, 60), new Vector2(-60, -60));
            var title = HarvestUi.Label("Title", panel, "草藥攤・出售", 40, TextAnchor.UpperCenter, AlchemyUi.Ink);
            ((RectTransform)title.transform).offsetMax = new Vector2(0, -26);

            // Left: the bundles brought from the field.
            left = AlchemyUi.Rect("Bundles", panel, new Vector2(0, 0), new Vector2(.58f, 1), new Vector2(40, 40), new Vector2(-20, -100));
            var head = HarvestUi.Label("Head", left, "你帶來的草藥捆", 30, TextAnchor.UpperLeft, AlchemyUi.Ink);
            if (HarvestCarry.Bundles.Count == 0) HarvestUi.Label("Empty", left, "\n\n背簍裡沒有草藥。", 30, TextAnchor.UpperLeft, AlchemyUi.Ink);
            for (int i = 0; i < HarvestCarry.Bundles.Count; i++)
            {
                var b = HarvestCarry.Bundles[i]; int index = i;
                var card = AlchemyUi.Panel("Bundle_" + i, left, Vector2.zero, Vector2.zero, Vector2.zero, Vector2.zero, new Color(.95f, .9f, .76f, .9f));
                HarvestUi.Fixed((RectTransform)card.transform, new Vector2(0, 1), new Vector2(0, -60 - i * 190), new Vector2(980, 170));
                card.gameObject.AddComponent<Outline>().effectColor = AlchemyUi.BambooDark;
                var name = HarvestUi.Label("Name", card.transform, $"{HarvestContent.Label(b.bin)}捆・{b.grades.Count} 株", 30, TextAnchor.UpperLeft, AlchemyUi.Ink);
                ((RectTransform)name.transform).offsetMin = new Vector2(20, 0); ((RectTransform)name.transform).offsetMax = new Vector2(0, -12);
                for (int k = 0; k < b.grades.Count; k++)
                {
                    var herb = HarvestUi.Sprite("Herb", card.transform, HarvestArt.Herb(b.grades[k]), new Vector2(110, 110));
                    HarvestUi.Fixed((RectTransform)herb.transform, new Vector2(0, 0), new Vector2(20 + k * 104, 6), new Vector2(110, 110));
                }
                var t = HarvestUi.Button("Toggle", card.transform, "賣", () => Toggle(index), new Vector2(1, .5f), new Vector2(-20, 0), new Vector2(230, 120), AlchemyUi.Jade, 36);
                toggles.Add(t);
            }

            // Right: what the stall buys today. The board is blank in the world; the words are UI.
            var board = AlchemyUi.Panel("TodayBoard", panel, Vector2.zero, Vector2.zero, Vector2.zero, Vector2.zero, new Color(.48f, .34f, .2f, .96f));
            HarvestUi.Fixed((RectTransform)board.transform, new Vector2(1, 1), new Vector2(-40, -100), new Vector2(560, 470));
            var bt = HarvestUi.Label("Title", board.transform, "今天收", 38, TextAnchor.UpperCenter, new Color(.98f, .92f, .76f));
            ((RectTransform)bt.transform).offsetMax = new Vector2(0, -18);
            var icon = HarvestUi.Sprite("Herb", board.transform, HarvestArt.Herb("mid"), new Vector2(150, 150));
            HarvestUi.Fixed((RectTransform)icon.transform, new Vector2(.5f, 1), new Vector2(0, -80), new Vector2(150, 150));
            int bonus = HarvestContent.DemandBonus(day);
            var demand = HarvestUi.Label("Demand", board.transform, bonus > 0 ? $"青靈草　每捆加 {bonus}" : "青靈草　照常收", 32, TextAnchor.UpperCenter, new Color(.98f, .92f, .76f));
            ((RectTransform)demand.transform).offsetMax = new Vector2(0, -244);
            var prices = string.Join("　", HarvestContent.gradeRows.Select(g => $"{g.label} {g.bundlePrice + bonus}"));
            var table = HarvestUi.Label("Prices", board.transform, prices + "\n（一捆三株，不滿照比例）", 26, TextAnchor.UpperCenter, new Color(.95f, .88f, .7f));
            ((RectTransform)table.transform).offsetMax = new Vector2(0, -300);

            // Weigh: the big button in the right-thumb corner.
            weighButton = HarvestUi.Button("Weigh", panel, "秤", Weigh, new Vector2(1, 0), new Vector2(-40, 40), new Vector2(560, 150), AlchemyUi.Cinnabar, 48);
            RefreshWeigh();
        }

        public void Toggle(int index)
        {
            if (Weighed || index < 0 || index >= Sell.Count) return;
            Sell[index] = !Sell[index];
            AlchemyUi.SetText(toggles[index], Sell[index] ? "賣" : "留著");
            toggles[index].GetComponent<Image>().color = Sell[index] ? AlchemyUi.Jade : AlchemyUi.BambooDark;
            RefreshWeigh();
        }

        void RefreshWeigh() { if (weighButton != null) AlchemyUi.SetText(weighButton, Sell.Any(s => s) ? "秤" : "都留著"); }

        public void Weigh()
        {
            if (Weighed) return;
            Weighed = true;
            Last = HarvestRules.Settle(day, HarvestCarry.Bundles, Sell);
            HarvestCarry.Coins += Last.totalCoins;
            foreach (var (q, n) in Last.kept) HarvestCarry.Kept[q] = (HarvestCarry.Kept.TryGetValue(q, out var had) ? had : 0) + n;
            foreach (var t in toggles) t.interactable = false;
            weighButton.gameObject.SetActive(false);
            StartCoroutine(WeighRoutine());
        }

        IEnumerator WeighRoutine()
        {
            result = AlchemyUi.Slips("Result", panel, Vector2.zero, Vector2.zero, Vector2.zero, Vector2.zero);
            HarvestUi.Fixed(result, new Vector2(1, 0), new Vector2(-40, 40), new Vector2(560, 330));
            var coin = HarvestUi.Sprite("Coin", result, HarvestArt.Coin(), new Vector2(84, 84));
            HarvestUi.Fixed((RectTransform)coin.transform, new Vector2(0, 1), new Vector2(26, -28), new Vector2(84, 84));
            coinsText = HarvestUi.Label("Coins", result, "", 46, TextAnchor.UpperLeft, AlchemyUi.Ink);
            ((RectTransform)coinsText.transform).offsetMin = new Vector2(126, 0); ((RectTransform)coinsText.transform).offsetMax = new Vector2(0, -42);
            keeper = HarvestUi.Label("Keeper", result, "", 28, TextAnchor.UpperLeft, AlchemyUi.Ink);
            ((RectTransform)keeper.transform).offsetMin = new Vector2(26, 120); ((RectTransform)keeper.transform).offsetMax = new Vector2(-20, -128);

            if (Last.totalCoins > 0)
            {
                // The sheet steps aside so the weighing happens in the world: the counterweight slides out along the
                // beam (more coins, farther out; full beam at 12) and the coin string drops on the counter. A slip at
                // the top keeps the count readable meanwhile.
                var group = panel.gameObject.GetComponent<CanvasGroup>() ?? panel.gameObject.AddComponent<CanvasGroup>();
                var strip = AlchemyUi.Slips("WeighStrip", canvas.transform, new Vector2(.5f, 1), new Vector2(.5f, 1), Vector2.zero, Vector2.zero);
                HarvestUi.Fixed(strip, new Vector2(.5f, 1), new Vector2(0, -24), new Vector2(520, 96));
                var count = HarvestUi.Label("Count", strip, "秤一秤……", 38, TextAnchor.MiddleCenter, AlchemyUi.Ink);
                yield return Fade(group, 1, 0, .3f);
                float target = Mathf.Lerp(weightMin, weightMax, Mathf.Clamp01(Last.totalCoins / 12f)), t = 0;
                while (t < weighSeconds)
                {
                    t += Time.deltaTime; float k = Mathf.SmoothStep(0, 1, t / weighSeconds);
                    if (scaleWeight != null) scaleWeight.localPosition = weightHome + Vector3.right * Mathf.Lerp(weightMin, target, k);
                    coinsText.text = count.text = $"{Mathf.RoundToInt(Last.totalCoins * k)} 靈石";
                    yield return null;
                }
                coinsText.text = count.text = $"得 {Last.totalCoins} 靈石";
                yield return DropCoins();
                yield return new WaitForSeconds(.7f);
                Destroy(strip.gameObject);
                yield return Fade(group, 0, 1, .3f);
            }
            else coinsText.text = "都留著";
            foreach (var id in Last.lines) { keeper.text = "攤主：" + HarvestContent.Line(id); yield return new WaitForSeconds(1.4f); }
            doneButton = HarvestUi.Button("Done", panel, "收好", Finish, new Vector2(1, 0), new Vector2(-40, 390), new Vector2(560, 110), AlchemyUi.Jade, 36);
        }

        static IEnumerator Fade(CanvasGroup g, float from, float to, float seconds)
        {
            g.blocksRaycasts = to > .5f;
            for (float t = 0; t < seconds; t += Time.deltaTime) { g.alpha = Mathf.Lerp(from, to, t / seconds); yield return null; }
            g.alpha = to;
        }

        IEnumerator DropCoins()
        {
            if (coinDrop == null) yield break;
            GameObject coins;
            if (coinStringPrefab != null) coins = Instantiate(coinStringPrefab);
            else
            {
                coins = GameObject.CreatePrimitive(PrimitiveType.Cylinder); Destroy(coins.GetComponent<Collider>());
                coins.transform.localScale = new Vector3(.12f, .006f, .03f);
                coins.GetComponent<Renderer>().material.color = new Color(.6f, .48f, .24f);
            }
            coins.name = "SoldCoins";
            var end = coinDrop.position; var start = end + Vector3.up * .45f; float t = 0;
            while (t < .45f)
            {
                t += Time.deltaTime; float k = t / .45f;
                coins.transform.position = Vector3.Lerp(start, end, k * k) + Vector3.up * (k > .8f ? Mathf.Sin((k - .8f) / .2f * Mathf.PI) * .02f : 0);
                yield return null;
            }
            coins.transform.position = end;
        }

        public Button DoneButton => doneButton;
        public Button ToggleButton(int index) => toggles[index];
        public Button WeighButton => weighButton;

        public void Finish()
        {
            if (!Weighed || Last == null) return;
            HarvestMarketEvents.EmitSold(day, Last);
            HarvestCarry.Bundles = new List<HerbBundle>();
            if (scaleWeight != null) scaleWeight.localPosition = weightHome;
            Close();
        }

        void Update()
        {
            if (!Open) return;
            var kb = Keyboard.current; if (kb == null) return;
            for (int i = 0; i < Mathf.Min(Sell.Count, 9); i++) if (kb[(Key)((int)Key.Digit1 + i)].wasPressedThisFrame) Toggle(i);
            if (kb.spaceKey.wasPressedThisFrame || kb.enterKey.wasPressedThisFrame) { if (!Weighed) Weigh(); else if (doneButton != null) Finish(); }
            if (kb.escapeKey.wasPressedThisFrame && !Weighed) Close();   // walking away before weighing keeps everything
        }
    }
}
