using System;
using System.Linq;
using QingxiWorld;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.UI;
using UnityEngine.UI;

namespace YunJing
{
    // Local Qingxi walkthrough UI. No account, inventory or reward authority.
    public sealed partial class QingxiHud : MonoBehaviour
    {
        public QingxiFirstPerson walker;
        public QingxiLocalForaging foraging;
        public Material uiMaterial;

        RectTransform safe, root, marker, promptRow;
        GameObject journal;
        Text foragingText, journalWhere, journalToday;
        Text bannerText, bannerSub, objectiveText, toastText, markerText;
        CanvasGroup bannerGroup, objectiveGroup, promptGroup, toastGroup, hintGroup, markerGroup;
        readonly GameObject[] promptKeys = new GameObject[2];
        readonly Text[] promptKeyTexts = new Text[2], promptLabels = new Text[2];
        Button journalButton;
        Font font;
        Canvas hudCanvas;
        Text fortuneText;
        bool open, started;
        int width, height;
        string placeName = "青溪小鎮", objective, shownPrompt;
        Vector3? target;
        float bannerUntil, objectiveBrightUntil, toastUntil, hintUntil, nextObjectiveCheck;

        /// <summary>True while this HUD shows results as toasts, so other scripts need not draw their own box.</summary>
        public static bool ShowsToasts { get; private set; }

        static readonly Color Cream = new Color(.96f, .94f, .86f), Gold = new Color(.95f, .86f, .62f), Ink = new Color(.03f, .05f, .06f);

        // The outdoor HUD keeps the view clear: the place name fades in and out at the top, today's thread is one
        // quiet line at the upper left, what F does here and the last result sit low in the middle only while they
        // matter, and the numbers live in the journal (M).
        void Start()
        {
            if (walker == null) { enabled = false; return; }
            font = QingxiFonts.Ui != null ? QingxiFonts.Ui : Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            var canvas = new GameObject("Qingxi HUD Canvas", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            canvas.transform.SetParent(transform, false);
            var cv = canvas.GetComponent<Canvas>();
            hudCanvas = cv;
            cv.renderMode = RenderMode.ScreenSpaceOverlay;
            cv.sortingOrder = 20;
            var scaler = canvas.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1280, 720);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
            scaler.matchWidthOrHeight = .5f;
            root = canvas.GetComponent<RectTransform>();

            safe = Rect("Safe Area", canvas.transform, Vector2.zero, Vector2.one, Vector2.zero,
                Vector2.zero, Vector2.zero);
            SafeArea();
            EnsureEventSystem();

            // Where today's thread leads, as a small diamond in the world (under everything else).
            marker = Rect("Objective Marker", safe, Vector2.zero, Vector2.zero, Vector2.zero, new Vector2(18, 18), new Vector2(.5f, .5f));
            markerGroup = marker.gameObject.AddComponent<CanvasGroup>(); markerGroup.alpha = 0; markerGroup.blocksRaycasts = false;
            Diamond("Marker Diamond", marker, Vector2.zero, 11, Gold);
            markerText = Free("Marker Distance", marker, new Vector2(.5f, 0), new Vector2(0, -4), new Vector2(120, 18), "", 12, false, Cream, TextAnchor.UpperCenter);

            // Place name: top centre, shown for a few seconds when the place changes.
            var banner = Rect("Place Banner", safe, new Vector2(.5f, 1), new Vector2(.5f, 1), new Vector2(0, -40), new Vector2(560, 84), new Vector2(.5f, 1));
            bannerGroup = banner.gameObject.AddComponent<CanvasGroup>(); bannerGroup.alpha = 0; bannerGroup.blocksRaycasts = false;
            bannerText = Free("Place", banner, new Vector2(.5f, 1), Vector2.zero, new Vector2(560, 44), "", 30, true, Cream, TextAnchor.UpperCenter);
            Line("Place Rule", banner, new Vector2(.5f, 1), new Vector2(0, -47), new Vector2(300, 1.5f), FadeBoth(), new Color(Gold.r, Gold.g, Gold.b, .85f));
            bannerSub = Free("Place Time", banner, new Vector2(.5f, 1), new Vector2(0, -54), new Vector2(560, 22), "", 14, false, new Color(.85f, .9f, .87f), TextAnchor.UpperCenter);

            // Today's thread: one line, no box.
            var goal = Rect("Objective", safe, new Vector2(0, 1), new Vector2(0, 1), new Vector2(0, -24), new Vector2(470, 40), new Vector2(0, 1));
            objectiveGroup = goal.gameObject.AddComponent<CanvasGroup>(); objectiveGroup.alpha = 0; objectiveGroup.blocksRaycasts = false;
            Line("Objective Wash", goal, new Vector2(0, 1), Vector2.zero, new Vector2(470, 40), FadeLeft(), new Color(Ink.r, Ink.g, Ink.b, .5f)).pivot = new Vector2(0, 1);
            Diamond("Objective Diamond", goal, new Vector2(34, -20), 8, Gold);
            objectiveText = Free("Objective Text", goal, new Vector2(0, 1), new Vector2(50, -9), new Vector2(410, 24), "", 16, false, Cream, TextAnchor.UpperLeft);

            journalButton = Action("Journey Button", safe, "手札  M", new Vector2(1, 1),
                new Vector2(-24, -24), new Vector2(92, 34), ToggleJournal);
            journalButton.GetComponent<UnityEngine.UI.Image>().color = new Color(Ink.r, Ink.g, Ink.b, .5f);
            var caption = journalButton.GetComponentInChildren<Text>(); caption.fontSize = 15; caption.fontStyle = FontStyle.Normal; caption.font = font;
            caption.rectTransform.anchoredPosition = new Vector2(10, -6);

            // Keys: shown while the newcomer finds their feet, then out of the way (they stay listed in the journal).
            var hint = Rect("Control Hint", safe, Vector2.zero, Vector2.zero, new Vector2(26, 20), new Vector2(560, 22), Vector2.zero);
            hintGroup = hint.gameObject.AddComponent<CanvasGroup>(); hintGroup.blocksRaycasts = false;
            Free("Control Text", hint, new Vector2(0, 1), Vector2.zero, new Vector2(560, 22), "WASD 行走  ·  Shift 奔跑  ·  空白鍵 跳躍  ·  F 互動  ·  M 手札", 13, false,
                new Color(.9f, .93f, .9f, .9f), TextAnchor.UpperLeft);
            hintUntil = Time.unscaledTime + 14;

            // What F does here.
            promptRow = Panel("Interaction Prompt", safe, new Vector2(.5f, 0), new Vector2(.5f, 0), new Vector2(0, 118), new Vector2(200, 40), new Color(Ink.r, Ink.g, Ink.b, .58f));
            promptRow.pivot = new Vector2(.5f, 0);
            promptRow.GetComponent<UnityEngine.UI.Image>().raycastTarget = false;
            promptGroup = promptRow.gameObject.AddComponent<CanvasGroup>(); promptGroup.alpha = 0; promptGroup.blocksRaycasts = false;
            var row = promptRow.gameObject.AddComponent<HorizontalLayoutGroup>();
            row.padding = new RectOffset(14, 16, 7, 7); row.spacing = 8; row.childAlignment = TextAnchor.MiddleCenter;
            row.childControlWidth = row.childControlHeight = true; row.childForceExpandWidth = row.childForceExpandHeight = false;
            var fit = promptRow.gameObject.AddComponent<ContentSizeFitter>();
            fit.horizontalFit = fit.verticalFit = ContentSizeFitter.FitMode.PreferredSize;
            for (int i = 0; i < 2; i++)
            {
                var key = Panel("Key " + i, promptRow, new Vector2(.5f, .5f), new Vector2(.5f, .5f), Vector2.zero, new Vector2(26, 26), Cream);
                key.GetComponent<UnityEngine.UI.Image>().pixelsPerUnitMultiplier = 2.6f;
                var le = key.gameObject.AddComponent<LayoutElement>(); le.minWidth = le.preferredWidth = 26; le.minHeight = le.preferredHeight = 26;
                promptKeyTexts[i] = Free("Letter", key, new Vector2(.5f, .5f), Vector2.zero, new Vector2(26, 26), "F", 15, false, Ink, TextAnchor.MiddleCenter, false);
                promptKeyTexts[i].rectTransform.pivot = new Vector2(.5f, .5f); promptKeyTexts[i].fontStyle = FontStyle.Bold;
                promptKeys[i] = key.gameObject;
                promptLabels[i] = Free("Label " + i, promptRow, new Vector2(.5f, .5f), Vector2.zero, new Vector2(100, 26), "", 16, false, Cream, TextAnchor.MiddleLeft, false);
                promptLabels[i].horizontalOverflow = HorizontalWrapMode.Overflow;
            }

            // The last result, and what people say: low in the middle, gone after a moment.
            var toast = Rect("Toast", safe, new Vector2(.5f, 0), new Vector2(.5f, 0), new Vector2(0, 172), new Vector2(820, 64), new Vector2(.5f, 0));
            toastGroup = toast.gameObject.AddComponent<CanvasGroup>(); toastGroup.alpha = 0; toastGroup.blocksRaycasts = false;
            Line("Toast Wash", toast, new Vector2(.5f, .5f), Vector2.zero, new Vector2(820, 64), FadeBoth(), new Color(Ink.r, Ink.g, Ink.b, .62f));
            toastText = Free("Toast Text", toast, new Vector2(.5f, .5f), Vector2.zero, new Vector2(680, 56), "", 17, false, Cream, TextAnchor.MiddleCenter);
            toastText.rectTransform.pivot = new Vector2(.5f, .5f);

            if (foraging != null) foraging.Changed += RefreshForaging;

            journal = Panel("Journey Journal", safe, new Vector2(.5f, .5f), new Vector2(.5f, .5f),
                Vector2.zero, new Vector2(560, 500), new Color(.045f, .075f, .085f, .96f)).gameObject;
            var page = journal.GetComponent<RectTransform>();
            Label("Journal Title", page, "旅途手札", 28, FontStyle.Bold,
                new Vector2(30, -24), new Vector2(300, 40), Gold);
            journalWhere = Label("Journal Where", page, "", 14, FontStyle.Normal, new Vector2(30, -66), new Vector2(500, 22), new Color(.67f, .79f, .76f));
            Line("Journal Rule", page, new Vector2(0, 1), new Vector2(30, -92), new Vector2(500, 1), null, new Color(Gold.r, Gold.g, Gold.b, .35f)).pivot = new Vector2(0, 1);
            Label("Today Head", page, "今日", 14, FontStyle.Bold, new Vector2(30, -104), new Vector2(200, 22), Gold);
            journalToday = Label("Journal Body", page, "", 17, FontStyle.Normal, new Vector2(30, -128), new Vector2(500, 50), Cream);
            Label("Bag Head", page, "行囊", 14, FontStyle.Bold, new Vector2(30, -186), new Vector2(200, 22), Gold);
            foragingText = Label("Activity Counts", page, "", 16, FontStyle.Normal, new Vector2(30, -210), new Vector2(500, 48), Cream);
            Label("Fortune Head", page, "機緣", 14, FontStyle.Bold, new Vector2(30, -266), new Vector2(200, 22), Gold);
            // 機緣 (K4): found finds by title; the rest only as a count.
            fortuneText = Label("Journal Fortunes", page, "", 15, FontStyle.Normal, new Vector2(30, -290), new Vector2(500, 104),
                new Color(.93f, .84f, .62f));
            Label("Journal Keys", page, "WASD 行走 · Shift 奔跑 · 空白鍵 跳躍 · F 互動 · M 手札 · Esc 游標", 13, FontStyle.Normal,
                new Vector2(30, -402), new Vector2(500, 20), new Color(.6f, .68f, .66f));
            Action("Go Plaza", page, "回廣場", new Vector2(0, 0), new Vector2(28, 25),
                new Vector2(128, 48), () => { walker.Teleport(0); ToggleJournal(); });
            if (walker.spotNames.Length > 8)
                Action("Go Terrace", page, "聽風台入口", new Vector2(0, 0), new Vector2(172, 25),
                    new Vector2(146, 48), () => { walker.Teleport(8); ToggleJournal(); });
            Action("Close Journal", page, "繼續探索", new Vector2(0, 0), new Vector2(384, 25),
                new Vector2(148, 48), ToggleJournal);
            journal.SetActive(false);
            walker.useDesignedHud = true;
            walker.LocationChanged += OnLocation;
            OnLocation("青溪小鎮");
            BuildCollaboratorPanels();
            RefreshForaging();
            started = true; ShowsToasts = true;
        }

        void OnDestroy()
        {
            if (started) ShowsToasts = false;
            if (walker != null) walker.LocationChanged -= OnLocation;
            if (foraging != null) foraging.Changed -= RefreshForaging;
        }

        // With on-screen controls the keyboard hint goes away; the rest already keeps clear of the joystick and
        // the button arc in the lower corners.
        bool touchLayout;
        void TouchLayout(bool touch)
        {
            touchLayout = touch;
            if (hintGroup != null) hintGroup.gameObject.SetActive(!touch);
        }

        static void Fade(CanvasGroup group, float to, float speed = 3)
        {
            if (group != null && group.alpha != to) group.alpha = Mathf.MoveTowards(group.alpha, to, Time.unscaledDeltaTime * speed);
        }

        void Update()
        {
            // Johnnnny0823's drills take the whole screen, as in his web demo.
            if (hudCanvas != null) hudCanvas.enabled = !QingxiTrainingPractice.Practising;
            if (QingxiTouchControls.Active != touchLayout) TouchLayout(QingxiTouchControls.Active);
            if (Screen.width != width || Screen.height != height) SafeArea();
            if (Keyboard.current != null && Keyboard.current.mKey.wasPressedThisFrame) ToggleJournal();
            UpdateCollaboratorPanels();

            float now = Time.unscaledTime;
            bool busy = open || sortingOpen || waterOpen;
            if (now >= nextObjectiveCheck)
            {
                nextObjectiveCheck = now + .5f;
                // The novice days (QingxiNoviceDays): today's thread, when there is one.
                var today = QingxiNoviceDays.Objective;
                if (today != objective)
                {
                    objective = today; objectiveBrightUntil = now + 6;
                    if (objectiveText != null) objectiveText.text = today ?? "";
                }
                target = ObjectiveTarget();
            }
            Fade(bannerGroup, now < bannerUntil && !busy ? 1 : 0, 1.6f);
            Fade(objectiveGroup, objective == null || busy ? 0 : now < objectiveBrightUntil ? 1 : .82f);
            Fade(hintGroup, now < hintUntil && !busy ? 1 : 0, 1.2f);
            Fade(toastGroup, now < toastUntil && !busy ? 1 : 0, 4);

            string prompt = foraging != null && !busy ? foraging.Prompt(walker.transform.position) : null;
            if (prompt == QingxiLocalForaging.IdlePrompt) prompt = null;
            if (prompt != null && prompt != shownPrompt) ShowPrompt(prompt);
            Fade(promptGroup, prompt != null ? 1 : 0, 6);
            UpdateMarker(busy);
        }

        // "F 採集靈草" or "F 交換材料  ·  E 煉調息散": a key cap for each key, plain words for the rest.
        void ShowPrompt(string prompt)
        {
            shownPrompt = prompt;
            var parts = prompt.Split(new[] { '·' }, 2);
            for (int i = 0; i < 2; i++)
            {
                string part = i < parts.Length ? parts[i].Trim() : null;
                bool key = part != null && part.Length > 2 && part[1] == ' ' && part[0] < 128 && char.IsLetter(part[0]);
                promptKeys[i].SetActive(key);
                promptLabels[i].gameObject.SetActive(part != null);
                if (part == null) continue;
                if (key) promptKeyTexts[i].text = part.Substring(0, 1);
                promptLabels[i].text = key ? part.Substring(2).Trim() : part;
                promptLabels[i].color = key ? Cream : new Color(.82f, .87f, .85f);
            }
            LayoutRebuilder.ForceRebuildLayoutImmediate(promptRow);
        }

        // Day 1's places, where they are loaded: the tea pavilion, the lodging door, the spot for the seedling.
        Vector3? ObjectiveTarget()
        {
            if (objective == null || QingxiNoviceDays.Day != 1) return null;
            bool tea = QingxiNoviceDays.Has("tea"), house = QingxiNoviceDays.Has("house"), plum = QingxiNoviceDays.Has("plum");
            foreach (var spots in QingxiDayOneSpots.All)
            {
                if (!tea && spots.teaPoint != null) return spots.teaPoint.position;
                if (tea && house && !plum && spots.plumPoint != null) return spots.plumPoint.position;
            }
            if (tea && !house && walker.spotNames != null && walker.spotPositions != null)
            {
                int i = Array.FindIndex(walker.spotNames, n => n != null && n.Contains("借住"));
                if (i >= 0 && i < walker.spotPositions.Length) return walker.spotPositions[i];
            }
            return null;
        }

        void UpdateMarker(bool busy)
        {
            var cam = Camera.main;
            float distance = target.HasValue ? Vector3.Distance(target.Value, walker.transform.position) : 0;
            bool show = target.HasValue && cam != null && !busy && distance > 5 && hudCanvas.scaleFactor > 0;
            Fade(markerGroup, show ? .95f : 0, 4);
            if (!show) return;
            var v = cam.WorldToScreenPoint(target.Value + Vector3.up * 2.2f);
            float w = Screen.width, h = Screen.height, edge = 46 * hudCanvas.scaleFactor;
            if (v.z < 0) { v.x = w - v.x; v.y = edge; }   // behind: point along the bottom edge
            v.x = Mathf.Clamp(v.x, edge, w - edge); v.y = Mathf.Clamp(v.y, edge * 1.6f, h - edge * 2.4f);
            var s = Screen.safeArea;
            marker.anchoredPosition = new Vector2(v.x - s.xMin, v.y - s.yMin) / hudCanvas.scaleFactor;
            markerText.text = Mathf.Max(10, Mathf.RoundToInt(distance * 1.4f / 10) * 10) + " 步";
        }

        void RefreshForaging()
        {
            if (foraging == null) return;
            if (foragingText != null)
                foragingText.text = $"靈草 {foraging.Herbs}　山兔 {foraging.Rabbits}　練習靈石 {foraging.PracticeStones}\n線索 {foraging.ObservedClues}　調息散 {foraging.PracticePellets}　領悟 {foraging.Insights}";
            if (!started || toastText == null || string.IsNullOrEmpty(foraging.LastMessage)) return;
            toastText.text = foraging.LastMessage;
            toastUntil = Time.unscaledTime + Mathf.Clamp(2.5f + foraging.LastMessage.Length * .11f, 3.5f, 9);
        }

        void OnLocation(string location)
        {
            if (bannerText == null) return;
            string name = location == "Entrance_ListeningTerrace" ? "聽風台入口" :
                location == "Entrance_MaterialShop" ? "坊市入口" : location;
            // Markers the walker passes (TrailClue_Q01, HerbNode_…) are not places.
            if (string.IsNullOrEmpty(name) || name.All(c => c < 128)) return;
            placeName = name;
            bannerText.text = name.Length <= 6 ? string.Join(" ", name.ToCharArray()) : name;
            bannerSub.text = QingxiDayNight.Current != null ? QingxiDayNight.PhaseName(QingxiDayNight.Current.Hour) : "";
            bannerUntil = Time.unscaledTime + 5;
        }

        void ToggleJournal()
        {
            open = !open;
            journal.SetActive(open);
            walker.SetMenuOpen(open);
            if (open)
            {
                if (fortuneText != null) fortuneText.text = QingxiFortunes.Current != null ? QingxiFortunes.Current.JournalText() : "";
                journalWhere.text = placeName + (QingxiDayNight.Current != null ? "　·　" + QingxiDayNight.PhaseName(QingxiDayNight.Current.Hour) : "");
                journalToday.text = QingxiNoviceDays.Objective ?? "今天沒有非做不可的事。山道有線索，溪邊有靈草，坊市也開著。";
            }
            if (open && EventSystem.current != null)
            {
                var button = journal.transform.Find("Close Journal")?.gameObject;
                EventSystem.current.SetSelectedGameObject(button);
            }
            else if (EventSystem.current != null) EventSystem.current.SetSelectedGameObject(journalButton.gameObject);
        }

        void SafeArea()
        {
            width = Screen.width; height = Screen.height;
            var s = Screen.safeArea;
            safe.anchorMin = new Vector2(s.xMin / width, s.yMin / height);
            safe.anchorMax = new Vector2(s.xMax / width, s.yMax / height);
        }

        static RectTransform Rect(string name, Transform parent, Vector2 min, Vector2 max,
            Vector2 anchored, Vector2 size, Vector2 pivot)
        {
            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            var rect = go.GetComponent<RectTransform>();
            rect.anchorMin = min; rect.anchorMax = max; rect.pivot = pivot;
            rect.anchoredPosition = anchored; rect.sizeDelta = size;
            return rect;
        }

        RectTransform Panel(string name, Transform parent, Vector2 anchorMin, Vector2 anchorMax,
            Vector2 anchored, Vector2 size, Color color)
        {
            var pivot = anchorMin == new Vector2(1, 1) ? new Vector2(1, 1) :
                anchorMin == new Vector2(1, 0) ? new Vector2(1, 0) :
                anchorMin == new Vector2(0, 1) ? new Vector2(0, 1) :
                anchorMin == new Vector2(0, 0) ? new Vector2(0, 0) : new Vector2(.5f, .5f);
            var rect = Rect(name, parent, anchorMin, anchorMax, anchored, size, pivot);
            var image = rect.gameObject.AddComponent<UnityEngine.UI.Image>();
            image.color = color;
            image.sprite = Round(); image.type = UnityEngine.UI.Image.Type.Sliced; image.pixelsPerUnitMultiplier = 1.6f;
            if (uiMaterial != null) image.material = uiMaterial;
            return rect;
        }

        // Text that sits on the world itself, with a soft shadow in place of a box behind it.
        Text Free(string name, Transform parent, Vector2 anchor, Vector2 offset, Vector2 bounds, string value, int size, bool title,
            Color color, TextAnchor align, bool shadow = true)
        {
            var rect = Rect(name, parent, anchor, anchor, offset, bounds, new Vector2(anchor.x, 1));
            var t = rect.gameObject.AddComponent<Text>();
            t.font = title && QingxiFonts.Title != null ? QingxiFonts.Title : font; t.text = value; t.fontSize = size;
            if (uiMaterial != null) t.material = uiMaterial;
            t.color = color; t.alignment = align; t.raycastTarget = false;
            t.horizontalOverflow = HorizontalWrapMode.Wrap; t.verticalOverflow = VerticalWrapMode.Overflow;
            if (shadow)
            {
                var sh = rect.gameObject.AddComponent<Shadow>();
                sh.effectColor = new Color(0, 0, 0, .75f); sh.effectDistance = new Vector2(1.2f, -1.2f);
            }
            return t;
        }

        RectTransform Line(string name, Transform parent, Vector2 anchor, Vector2 offset, Vector2 size, Sprite sprite, Color color)
        {
            var rect = Rect(name, parent, anchor, anchor, offset, size, new Vector2(.5f, anchor.y));
            var image = rect.gameObject.AddComponent<UnityEngine.UI.Image>();
            image.sprite = sprite; image.color = color; image.raycastTarget = false;
            if (uiMaterial != null) image.material = uiMaterial;
            return rect;
        }

        void Diamond(string name, Transform parent, Vector2 offset, float size, Color color)
        {
            bool centred = offset == Vector2.zero;
            var anchor = centred ? new Vector2(.5f, .5f) : new Vector2(0, 1);
            var rect = Rect(name, parent, anchor, anchor, offset, new Vector2(size, size), new Vector2(.5f, .5f));
            rect.localRotation = Quaternion.Euler(0, 0, 45);
            var image = rect.gameObject.AddComponent<UnityEngine.UI.Image>();
            image.color = color; image.raycastTarget = false;
            if (uiMaterial != null) image.material = uiMaterial;
            rect.gameObject.AddComponent<Shadow>().effectColor = new Color(0, 0, 0, .7f);
        }

        static Sprite round, fadeLeft, fadeBoth;

        static Sprite Round()
        {
            if (round != null) return round;
            const int n = 48; const float r = 16;
            var tex = new Texture2D(n, n, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Clamp, hideFlags = HideFlags.HideAndDontSave };
            for (int y = 0; y < n; y++)
                for (int x = 0; x < n; x++)
                {
                    float dx = Mathf.Max(0, Mathf.Max(r - x - .5f, x + .5f - (n - r))), dy = Mathf.Max(0, Mathf.Max(r - y - .5f, y + .5f - (n - r)));
                    tex.SetPixel(x, y, new Color(1, 1, 1, Mathf.Clamp01(r - Mathf.Sqrt(dx * dx + dy * dy) + .5f)));
                }
            tex.Apply();
            return round = Sprite.Create(tex, new Rect(0, 0, n, n), new Vector2(.5f, .5f), 100, 0, SpriteMeshType.FullRect, new Vector4(r, r, r, r));
        }

        static Sprite FadeLeft() => fadeLeft != null ? fadeLeft : fadeLeft = Gradient(x => Mathf.SmoothStep(1, 0, x));
        static Sprite FadeBoth() => fadeBoth != null ? fadeBoth : fadeBoth = Gradient(x => Mathf.Sin(Mathf.PI * x));

        static Sprite Gradient(Func<float, float> alpha)
        {
            const int n = 64;
            var tex = new Texture2D(n, 1, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Clamp, hideFlags = HideFlags.HideAndDontSave };
            for (int x = 0; x < n; x++) tex.SetPixel(x, 0, new Color(1, 1, 1, Mathf.Clamp01(alpha(x / (n - 1f)))));
            tex.Apply();
            return Sprite.Create(tex, new Rect(0, 0, n, 1), new Vector2(.5f, .5f), 100);
        }

        Text Label(string name, Transform parent, string value, int size, FontStyle style,
            Vector2 offset, Vector2 bounds, Color color)
        {
            var rect = Rect(name, parent, new Vector2(0, 1), new Vector2(0, 1), offset, bounds,
                new Vector2(0, 1));
            var t = rect.gameObject.AddComponent<Text>();
            t.font = style == FontStyle.Bold && size >= 18 && QingxiFonts.Title != null ? QingxiFonts.Title : font; t.text = value; t.fontSize = size; t.fontStyle = style;
            if (uiMaterial != null) t.material = uiMaterial;
            t.color = color; t.alignment = TextAnchor.UpperLeft;
            t.horizontalOverflow = HorizontalWrapMode.Wrap;
            t.verticalOverflow = VerticalWrapMode.Overflow;
            return t;
        }

        Button Action(string name, Transform parent, string title, Vector2 anchor, Vector2 offset,
            Vector2 size, UnityEngine.Events.UnityAction clicked)
        {
            var rect = Panel(name, parent, anchor, anchor, offset, size, new Color(.13f, .31f, .33f, .94f));
            var button = rect.gameObject.AddComponent<Button>();
            button.onClick.AddListener(clicked);
            var text = Label("Caption", rect, title, 17, FontStyle.Bold, new Vector2(10, -10),
                size - new Vector2(20, 12), new Color(.95f, .94f, .84f));
            text.alignment = TextAnchor.MiddleCenter;
            return button;
        }

        static void EnsureEventSystem()
        {
            if (EventSystem.current != null) return;
            var go = new GameObject("Qingxi UI Event System", typeof(EventSystem), typeof(InputSystemUIInputModule));
            go.GetComponent<EventSystem>().sendNavigationEvents = true;
            go.GetComponent<InputSystemUIInputModule>().AssignDefaultActions();
        }
    }
}
