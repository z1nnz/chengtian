using System;
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
    // 第 4 天・第一次收成, at the field slot (TY_Field01). Two steps:
    //   1. Pull: press on a herb and drag it up (mouse or one thumb), or hold F on the selected herb (A／D picks;
    //      hold Shift to yank). Finishing in less than pullSafeSeconds snaps the root: one grade down.
    //   2. Sort: the camera moves to the sort station beside the field, where the herbs lie in the real MK02 sieve.
    //      Pick one up to look at it (a card names what you see: glowing tips, yellowed edges, a snapped root), then
    //      drag it into the top / mid / low tray (or tap it, then tap a tray, or press 1 2 3). A wrong tray is not
    //      punished; the stall pays by real grade.
    // Ends with harvest.completed { fieldId, plants:[{quality}] } and the bundles in HarvestCarry for the stall.
    public sealed class QingxiHarvestPanel : MonoBehaviour
    {
        public static QingxiHarvestPanel Current { get; private set; }

        public string fieldId = "TY_Field01";
        public Vector2 plotSize = new Vector2(2.6f, 3.4f);   // A's TY01 plot
        public Camera view;
        /// Herb meshes per grade (MK02 single plants); empty means a placeholder block is used.
        public GameObject topPlant, midPlant, lowPlant;
        public float pullPixels = 170;        // drag distance (reference px) for a full pull
        public float keyPullSeconds = 1.1f;   // holding F; Shift pulls four times faster
        public float liftMeters = .32f;

        public enum Phase { Idle, Pull, Sort, Done }
        public Phase Stage { get; private set; }
        public readonly List<Plant> Plants = new List<Plant>();
        public int Selected { get; private set; }
        public string[] Bins { get; private set; }

        public sealed class Plant
        {
            public int index; public string original, grade; public bool pulled, snapped; public float seconds;
            public Transform root, visual, frame; public Renderer frameRenderer; public float progress;
            public Transform sortItem; public Vector3 sortTarget; public Quaternion sortTurn = Quaternion.identity;
        }

        [Header("Sort station (set by the scene builder)")]
        public HarvestCameraRig rig; public int sortView = 2;
        public Transform sortSieve;                                                     // MK02 sieve, pivot at its bottom centre
        public Transform[] trays = new Transform[3], tags = new Transform[3];          // top, mid, low: small sieves and MK03 tags

        Canvas canvas; RectTransform hud, sortUi, card; Text hint, toast, cardBody; float toastUntil;
        Plant active; float pressTime, pressY; bool keyHeld;
        Button tieButton; Material frameMat, frameMatOn;
        static readonly string[] TrayBins = { "top", "mid", "low" };
        readonly Text[] trayNames = new Text[3], trayCounts = new Text[3];
        int picked = -1, down = -1; Vector2 downAt; bool dragging, tied;
        const float HerbLength = .30f, RestY = .06f, LiftY = .2f, DragY = .17f;   // m, above the station cloth

        void Awake() { Current = this; }
        void Start() { BuildPlot(); }

        // --- field ---------------------------------------------------------------------------------------------
        void BuildPlot()
        {
            frameMat = Unlit(new Color(.2f, .85f, .35f)); frameMatOn = Unlit(new Color(1f, .86f, .35f));
            var grades = HarvestContent.FieldPlants(fieldId);
            for (int i = 0; i < grades.Length; i++)
            {
                // Two columns × three rows inside the 2.6 × 3.4 m plot.
                var at = new Vector3((i % 2 - .5f) * plotSize.x * .5f, 0, (1 - i / 2) * plotSize.y / 3f);
                var root = new GameObject($"HerbSlot_{i + 1}").transform; root.SetParent(transform, false); root.localPosition = at;
                var p = new Plant { index = i, original = grades[i], grade = grades[i], root = root };
                p.frame = SlotFrame(root, out p.frameRenderer);
                p.visual = HerbVisual(grades[i], root);
                var hit = root.gameObject.AddComponent<BoxCollider>(); hit.center = new Vector3(0, .25f, 0); hit.size = new Vector3(.6f, .55f, .6f);
                Plants.Add(p);
            }
        }

        // 6 green slot frames: placeholder until the core team swaps in A's TY02 herb.
        Transform SlotFrame(Transform parent, out Renderer first)
        {
            var frame = new GameObject("SlotFrame").transform; frame.SetParent(parent, false); first = null;
            const float s = .62f, t = .025f;
            foreach (var (pos, size) in new[] {
                (new Vector3(0, t / 2, s / 2), new Vector3(s, t, t)), (new Vector3(0, t / 2, -s / 2), new Vector3(s, t, t)),
                (new Vector3(s / 2, t / 2, 0), new Vector3(t, t, s)), (new Vector3(-s / 2, t / 2, 0), new Vector3(t, t, s)) })
            {
                var bar = GameObject.CreatePrimitive(PrimitiveType.Cube); Destroy(bar.GetComponent<Collider>());
                bar.transform.SetParent(frame, false); bar.transform.localPosition = pos; bar.transform.localScale = size;
                var r = bar.GetComponent<Renderer>(); r.sharedMaterial = frameMat; first ??= r;
            }
            return frame;
        }

        public GameObject PlantPrefab(string grade) => grade == "top" ? topPlant : grade == "mid" ? midPlant : lowPlant;

        Transform HerbVisual(string grade, Transform parent)
        {
            var prefab = PlantPrefab(grade);
            if (prefab != null)
            {
                var go = Instantiate(prefab, parent, false); go.name = "Herb_" + grade;
                foreach (var c in go.GetComponentsInChildren<Collider>()) Destroy(c);
                return go.transform;
            }
            var stand = new GameObject("Herb_" + grade).transform; stand.SetParent(parent, false);
            var body = GameObject.CreatePrimitive(PrimitiveType.Cube); Destroy(body.GetComponent<Collider>());
            body.transform.SetParent(stand, false); body.transform.localPosition = new Vector3(0, .15f, 0); body.transform.localScale = new Vector3(.14f, .3f, .14f);
            body.GetComponent<Renderer>().sharedMaterial = Unlit(grade == "low" ? HarvestArt.Yellow : HarvestArt.LeafLight);
            if (grade == "top")
            {
                var tip = GameObject.CreatePrimitive(PrimitiveType.Cube); Destroy(tip.GetComponent<Collider>());
                tip.transform.SetParent(stand, false); tip.transform.localPosition = new Vector3(0, .32f, 0); tip.transform.localScale = new Vector3(.1f, .05f, .1f);
                tip.GetComponent<Renderer>().sharedMaterial = Unlit(HarvestArt.Glow);
            }
            return stand;
        }

        static Material Unlit(Color c)
        {
            var m = new Material(Shader.Find("Universal Render Pipeline/Unlit") ?? Shader.Find("Unlit/Color")); m.color = c;
            if (m.HasProperty("_BaseColor")) m.SetColor("_BaseColor", c); return m;
        }

        // --- flow ----------------------------------------------------------------------------------------------
        public void Begin()
        {
            if (Stage != Phase.Idle) return;
            Stage = Phase.Pull; BuildHud(); SelectNext(0);
            Hint("按住青靈草往上拉。慢慢拉，根才不會斷。");
            QingxiFirstPerson.Current?.SetMenuOpen(true);
        }

        void BuildHud()
        {
            canvas = HarvestUi.Canvas("HarvestCanvas", 20);
            hud = AlchemyUi.Slips("FieldHint", canvas.transform, new Vector2(.5f, 1), new Vector2(.5f, 1), Vector2.zero, Vector2.zero);
            HarvestUi.Fixed(hud, new Vector2(.5f, 1), new Vector2(0, -24), new Vector2(980, 96));
            hint = HarvestUi.Label("Hint", hud, "", 32, TextAnchor.MiddleCenter, AlchemyUi.Ink);
            var tb = AlchemyUi.Panel("Toast", canvas.transform, new Vector2(.5f, .5f), new Vector2(.5f, .5f), Vector2.zero, Vector2.zero, AlchemyUi.Shade);
            HarvestUi.Fixed((RectTransform)tb.transform, new Vector2(.5f, .5f), new Vector2(0, 220), new Vector2(560, 84));
            toast = HarvestUi.Label("Text", tb.transform, "", 34, TextAnchor.MiddleCenter, Color.white); tb.gameObject.SetActive(false);
        }

        void Hint(string text) { if (hint != null) hint.text = text; }
        void Toast(string text, float seconds = 1.4f) { if (toast == null) return; toast.text = text; toast.transform.parent.gameObject.SetActive(true); toastUntil = Time.time + seconds; }

        void SelectNext(int from)
        {
            for (int k = 0; k < Plants.Count; k++) { int i = (from + k) % Plants.Count; if (!Plants[i].pulled) { Selected = i; break; } }
            foreach (var p in Plants) if (p.frameRenderer != null)
                foreach (var r in p.frame.GetComponentsInChildren<Renderer>()) r.sharedMaterial = p.index == Selected && !p.pulled ? frameMatOn : frameMat;
        }

        void Update()
        {
            if (toast != null && toast.transform.parent.gameObject.activeSelf && Time.time > toastUntil) toast.transform.parent.gameObject.SetActive(false);
            if (Stage == Phase.Pull) UpdatePull();
            else if (Stage == Phase.Sort || tied) UpdateSort();
        }

        void UpdatePull()
        {
            var cam = view != null ? view : Camera.main;
            var pointer = Pointer.current;
            if (pointer != null && cam != null)
            {
                var pos = pointer.position.ReadValue();
                if (pointer.press.wasPressedThisFrame && active == null && Physics.Raycast(cam.ScreenPointToRay(pos), out var hit, 50f))
                {
                    var p = Plants.FirstOrDefault(x => !x.pulled && hit.collider.transform == x.root);
                    if (p != null) { active = p; pressTime = Time.time; pressY = pos.y; Selected = p.index; SelectNext(p.index); }
                }
                if (active != null && !keyHeld)
                {
                    if (pointer.press.isPressed) SetProgress(active, (pos.y - pressY) / (pullPixels * (canvas != null ? canvas.scaleFactor : 1)));
                    else { SetProgress(active, 0); active = null; }   // let go early: the herb settles back, nothing lost
                }
            }
            var kb = Keyboard.current; if (kb == null) return;
            if (active == null || keyHeld)
            {
                if (kb.aKey.wasPressedThisFrame || kb.leftArrowKey.wasPressedThisFrame) SelectNext((Selected + Plants.Count - 1) % Plants.Count == Selected ? Selected : PrevOpen());
                if (kb.dKey.wasPressedThisFrame || kb.rightArrowKey.wasPressedThisFrame) SelectNext(Selected + 1);
                if (kb.fKey.isPressed)
                {
                    var p = Plants[Selected];
                    if (!p.pulled)
                    {
                        if (!keyHeld) { keyHeld = true; active = p; pressTime = Time.time; }
                        SetProgress(p, p.progress + Time.deltaTime / keyPullSeconds * (kb.shiftKey.isPressed ? 4 : 1));
                    }
                }
                else if (keyHeld) { keyHeld = false; if (active != null && !active.pulled) SetProgress(active, 0); active = null; }
            }
        }

        int PrevOpen()
        {
            for (int k = 1; k <= Plants.Count; k++) { int i = (Selected - k + Plants.Count) % Plants.Count; if (!Plants[i].pulled) return i; }
            return Selected;
        }

        void SetProgress(Plant p, float value)
        {
            p.progress = Mathf.Clamp01(value);
            p.visual.localPosition = Vector3.up * (p.progress * liftMeters);
            p.visual.localRotation = Quaternion.Euler(Mathf.Sin(Time.time * 30) * 3 * p.progress, 0, 0);   // a little tug wobble
            if (p.progress >= 1) Complete(p, Time.time - pressTime);
        }

        void Complete(Plant p, float seconds)
        {
            p.pulled = true; p.seconds = seconds; p.grade = HarvestRules.PullGrade(p.original, seconds); p.snapped = p.grade != p.original;
            active = null; keyHeld = false;
            Debug.Log($"HARVEST_PULL {p.index} {p.original}->{p.grade} {seconds:0.00}s");
            Toast(p.snapped ? "啪！拉太快，根斷了" : "整株連根拔起", p.snapped ? 1.8f : 1f);
            StartCoroutine(FlyOff(p));
            if (Plants.All(x => x.pulled)) StartCoroutine(OpenSortSoon());
            else SelectNext(p.index + 1);
        }

        IEnumerator FlyOff(Plant p)
        {
            if (p.snapped) Crumbs(p.root.position);
            var from = p.visual.localPosition; float t = 0;
            while (t < .35f) { t += Time.deltaTime; p.visual.localPosition = from + Vector3.up * (t * 1.4f); p.visual.localScale = Vector3.one * (1 - t / .35f); yield return null; }
            p.visual.gameObject.SetActive(false);
            p.frame.gameObject.SetActive(false);
        }

        // A puff of soil where a root snapped.
        void Crumbs(Vector3 at)
        {
            var go = new GameObject("SnapSoil"); go.transform.position = at + Vector3.up * .05f;
            var ps = go.AddComponent<ParticleSystem>(); ps.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);
            var main = ps.main; main.duration = .3f; main.loop = false; main.startLifetime = .7f; main.startSpeed = 1.4f; main.startSize = .05f; main.gravityModifier = 1.2f;
            main.startColor = new Color(.42f, .3f, .18f); main.stopAction = ParticleSystemStopAction.Destroy;
            var em = ps.emission; em.rateOverTime = 0; em.SetBursts(new[] { new ParticleSystem.Burst(0, 24) });
            var shape = ps.shape; shape.shapeType = ParticleSystemShapeType.Hemisphere; shape.radius = .08f; shape.rotation = new Vector3(-90, 0, 0);
            go.GetComponent<ParticleSystemRenderer>().sharedMaterial = Unlit(new Color(.42f, .3f, .18f));
            ps.Play();
        }

        IEnumerator OpenSortSoon() { yield return new WaitForSeconds(.8f); OpenSort(); }

        // --- sort station ------------------------------------------------------------------------------------
        void OpenSort()
        {
            Stage = Phase.Sort; Bins = new string[Plants.Count];
            if (rig != null) StartCoroutine(rig.MoveTo(sortView, 1f));
            Hint("分揀：拿起一株細看，再拖到上品／中品／次品竹匾（也可以點草再點竹匾，或按 1 2 3）。");
            sortUi = AlchemyUi.Rect("SortUi", canvas.transform, Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
            sortUi.SetAsFirstSibling();   // under the hint strip and the toast
            for (int k = 0; k < 3; k++)
            {
                trayNames[k] = HarvestUi.Label("TrayName_" + TrayBins[k], sortUi, HarvestContent.Label(TrayBins[k]), 34, TextAnchor.MiddleCenter, new Color(1, .96f, .86f));
                Size(trayNames[k], new Vector2(160, 60)); trayNames[k].gameObject.AddComponent<Outline>().effectColor = new Color(.18f, .11f, .05f, .9f);
                var pill = AlchemyUi.Panel("TrayCount_" + TrayBins[k], sortUi, Vector2.zero, Vector2.zero, Vector2.zero, Vector2.zero, AlchemyUi.Shade);
                Size(pill, new Vector2(150, 44)); pill.raycastTarget = false;
                trayCounts[k] = HarvestUi.Label("Text", pill.transform, "", 24, TextAnchor.MiddleCenter, Color.white);
            }
            card = AlchemyUi.Slips("InspectCard", sortUi, Vector2.zero, Vector2.zero, Vector2.zero, Vector2.zero);
            HarvestUi.Fixed(card, new Vector2(0, 1), new Vector2(40, -150), new Vector2(470, 210));
            var title = HarvestUi.Label("Title", card, "細看這株", 30, TextAnchor.UpperLeft, AlchemyUi.BambooDark);
            ((RectTransform)title.transform).offsetMin = new Vector2(24, 0); ((RectTransform)title.transform).offsetMax = new Vector2(-16, -16);
            cardBody = HarvestUi.Label("Body", card, "", 30, TextAnchor.UpperLeft, AlchemyUi.Ink);
            ((RectTransform)cardBody.transform).offsetMin = new Vector2(24, 12); ((RectTransform)cardBody.transform).offsetMax = new Vector2(-16, -62);
            card.gameObject.SetActive(false);
            tieButton = HarvestUi.Button("Tie", sortUi, "綁成捆", Tie, new Vector2(0, 0), new Vector2(40, 36), new Vector2(460, 110), AlchemyUi.Jade, 36);   // under the sieve, clear of the trays
            tieButton.interactable = false;
            // The herbs lie side by side in the sieve, roots toward the player, the way they came out of the ground.
            for (int i = 0; i < Plants.Count; i++)
            {
                var p = Plants[i];
                var holder = new GameObject($"SortHerb_{i + 1}").transform; holder.SetParent(sortSieve.parent, false);
                var body = HerbVisual(p.grade, holder);
                body.localRotation = Quaternion.Euler(90, 0, 0); body.localScale = new Vector3(1, 1, .55f);   // lying down, leaves pressed flat
                var hit = holder.gameObject.AddComponent<BoxCollider>(); hit.center = new Vector3(0, .02f, HerbLength / 2); hit.size = new Vector3(.085f, .08f, HerbLength + .02f);
                p.sortItem = holder;
            }
            Lay(true);
        }

        static void Size(Component ui, Vector2 size) { var rt = (RectTransform)ui.transform; rt.anchorMin = rt.anchorMax = rt.pivot = new Vector2(.5f, .5f); rt.sizeDelta = size; }

        // Targets for every herb: on the sieve at its own place, or fanned in its tray (all together once tied).
        void Lay(bool snap = false)
        {
            var s0 = sortSieve.localPosition;
            for (int i = 0; i < Plants.Count; i++)
            {
                var p = Plants[i]; if (Bins[i] != null) continue;
                // head to tail, the way herbs are laid out to sort: a root end beside each leafy end, so the six read apart
                float x = (i - (Plants.Count - 1) / 2f) * .088f; bool flip = i % 2 == 1;
                p.sortTarget = s0 + new Vector3(x, RestY + (i == picked ? LiftY - RestY : 0), (flip ? 1 : -1) * (HerbLength / 2 - .01f) + (i % 3 - 1) * .012f);
                p.sortTurn = Quaternion.Euler(i == picked ? -32 : 0, (flip ? 180 : 0) + (i % 3 - 1) * 5, 0);   // picked: tips raised toward the eye
            }
            for (int k = 0; k < 3; k++)
            {
                var on = Plants.Where(p => Bins[p.index] == TrayBins[k]).ToList(); var t = trays[k].localPosition;
                float step = tied ? .012f : on.Count > 1 ? Mathf.Min(.06f, .2f / (on.Count - 1)) : 0;
                for (int n = 0; n < on.Count; n++)
                {
                    float u = n - (on.Count - 1) / 2f;
                    on[n].sortTarget = t + new Vector3(u * step, RestY * .7f + n * .014f + (on[n].index == picked ? LiftY - RestY : 0), -HerbLength / 2);
                    on[n].sortTurn = Quaternion.Euler(on[n].index == picked ? -32 : 0, u * (tied ? 2 : 7), 0);
                }
                int bundles = (on.Count + HarvestContent.bundleSize - 1) / HarvestContent.bundleSize;
                if (trayCounts[k] != null) trayCounts[k].text = on.Count == 0 ? "空" : $"{on.Count} 株 · {bundles} 捆";
            }
            if (snap) foreach (var p in Plants) p.sortItem.SetLocalPositionAndRotation(p.sortTarget, p.sortTurn);
        }

        static string Traits(Plant p)
        {
            var seen = p.grade == "top" ? "葉尖泛著青光\n葉片飽滿完整" : p.grade == "mid" ? "葉色濃綠、完整\n葉尖沒有光" : "葉緣枯黃，有鏽斑\n葉上有蟲洞";
            return p.snapped ? seen + "\n根是斷的（拔太快）" : seen;
        }

        public void Pick(int plant)
        {
            picked = plant; Lay();
            if (card == null) return;
            card.gameObject.SetActive(plant >= 0);
            if (plant >= 0) cardBody.text = Traits(Plants[plant]);
        }

        /// Drop a herb into a tray (the keys and the playtest go through here too).
        public void Place(int plant, string bin)
        {
            Bins[plant] = bin; Pick(-1);
            tieButton.interactable = Bins.All(b => b != null);
            Hint(tieButton.interactable ? "都分好了。按「綁成捆」。" : $"還有 {Bins.Count(b => b == null)} 株在竹篩上。");
        }

        float Scale => canvas != null ? canvas.scaleFactor : 1;
        Camera SortCamera => view != null ? view : Camera.main;

        int HerbAt(Ray ray, int ignore = -1)
        {
            foreach (var hit in Physics.RaycastAll(ray, 20f).OrderBy(h => h.distance))
            {
                var p = Plants.FirstOrDefault(x => x.sortItem == hit.collider.transform);
                if (p != null && p.index != ignore) return p.index;
            }
            return -1;
        }

        string TrayAt(Ray ray, int ignore = -1)
        {
            foreach (var hit in Physics.RaycastAll(ray, 20f).OrderBy(h => h.distance))
            {
                int t = Array.IndexOf(trays, hit.collider.transform); if (t >= 0) return TrayBins[t];
                var p = Plants.FirstOrDefault(x => x.sortItem == hit.collider.transform);
                if (p != null && p.index != ignore && Bins[p.index] != null) return Bins[p.index];   // a herb already in a tray stands for its tray
            }
            return null;
        }

        void UpdateSort()
        {
            var cam = SortCamera; var pointer = Pointer.current;
            if (Stage == Phase.Sort && pointer != null && cam != null)
            {
                var pos = pointer.position.ReadValue(); var ray = cam.ScreenPointToRay(pos);
                if (pointer.press.wasPressedThisFrame && !RectTransformUtility.RectangleContainsScreenPoint((RectTransform)tieButton.transform, pos, null))
                {
                    int h = HerbAt(ray);
                    if (h >= 0) { down = h; downAt = pos; dragging = false; }
                    else if (picked >= 0) { var bin = TrayAt(ray); if (bin != null) Place(picked, bin); }
                }
                if (down >= 0)
                {
                    if (pointer.press.isPressed)
                    {
                        if (!dragging && (pos - downAt).magnitude > 14 * Scale) { dragging = true; Pick(down); }
                        if (dragging && new Plane(Vector3.up, sortSieve.parent.position + Vector3.up * DragY).Raycast(ray, out var d))
                        {
                            var item = Plants[down].sortItem;   // held by its middle
                            item.position = ray.GetPoint(d) - item.forward * (HerbLength / 2);
                        }
                    }
                    else
                    {
                        if (dragging) { var bin = TrayAt(ray, down); if (bin != null) Place(down, bin); else Pick(-1); }
                        else if (picked >= 0 && picked != down && Bins[down] != null) Place(picked, Bins[down]);
                        else Pick(picked == down ? -1 : down);
                        down = -1; dragging = false;
                    }
                }
                var kb = Keyboard.current;
                if (kb != null)
                {
                    bool k1 = kb.digit1Key.wasPressedThisFrame, k2 = kb.digit2Key.wasPressedThisFrame, k3 = kb.digit3Key.wasPressedThisFrame;
                    if (picked < 0 && (k1 || k2 || k3)) picked = Array.IndexOf(Bins, null);   // nothing picked: the next herb on the sieve
                    if (picked >= 0) { if (k1) Place(picked, "top"); else if (k2) Place(picked, "mid"); else if (k3) Place(picked, "low"); }
                    if (tieButton.interactable && (kb.enterKey.wasPressedThisFrame || kb.spaceKey.wasPressedThisFrame)) Tie();
                }
            }
            // glide every herb that is not in the hand toward its place
            float k = 1 - Mathf.Exp(-Time.deltaTime * 14);
            foreach (var p in Plants)
            {
                if (p.sortItem == null || (dragging && p.index == down)) continue;
                p.sortItem.SetLocalPositionAndRotation(Vector3.Lerp(p.sortItem.localPosition, p.sortTarget, k), Quaternion.Slerp(p.sortItem.localRotation, p.sortTurn, k));
            }
        }

        // Tray names sit on the MK03 tags, the counts above each tray; both follow the camera move.
        void LateUpdate()
        {
            if (Stage != Phase.Sort || sortUi == null) return;
            var cam = SortCamera;
            for (int k = 0; k < 3; k++)
            {
                Vector2 tag = cam.WorldToScreenPoint(Centre(tags[k]));
                trayNames[k].transform.position = tag;
                trayCounts[k].transform.parent.position = tag + new Vector2(0, -64 * Scale);   // just under its name plate
            }
        }

        static Vector3 Centre(Transform t)
        {
            var rs = t.GetComponentsInChildren<Renderer>(); if (rs.Length == 0) return t.position;
            var b = rs[0].bounds; foreach (var r in rs) b.Encapsulate(r.bounds); return b.center;
        }

        public Vector2 HerbScreen(int plant) { var t = Plants[plant].sortItem; return SortCamera.WorldToScreenPoint(t.position + t.forward * (HerbLength * .6f)); }
        public Vector2 TrayScreen(string bin) => SortCamera.WorldToScreenPoint(trays[Array.IndexOf(TrayBins, bin)].position + Vector3.up * .03f);
        public Button TieButton => tieButton;
        public int Picked => picked;

        public void Tie()
        {
            if (Stage != Phase.Sort || Bins.Any(b => b == null)) return;
            var grades = Plants.Select(p => p.grade).ToList();
            HarvestCarry.FieldId = fieldId; HarvestCarry.Bundles = HarvestRules.BundleUp(grades, Bins);
            HarvestMarketEvents.EmitHarvest(fieldId, grades);
            Stage = Phase.Done; tied = true; Pick(-1);   // the herbs in each tray close up into a bundle
            Destroy(sortUi.gameObject);
            Hint($"綁好 {HarvestCarry.Bundles.Count} 捆，放進背簍。帶去坊市草藥攤。");
            QingxiFirstPerson.Current?.SetMenuOpen(false);
            StartCoroutine(CloseHint());
        }

        IEnumerator CloseHint() { yield return new WaitForSeconds(2.5f); if (canvas != null) Destroy(canvas.gameObject); }

        /// Scripted pull for the playtest: animates the same progress the hand would, over the given seconds.
        public IEnumerator PullScripted(int index, float seconds)
        {
            var p = Plants[index]; Selected = index; SelectNext(index); active = p; keyHeld = true; pressTime = Time.time;
            while (!p.pulled) { SetProgress(p, (Time.time - pressTime) / seconds); yield return null; }
        }
    }
}
