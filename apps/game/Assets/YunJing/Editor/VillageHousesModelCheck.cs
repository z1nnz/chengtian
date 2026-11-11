using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace YunJing.Editor
{
    // Work pack 2026-11-07, part 2 (VL01-VL03 empty-house variants of the Dondon StarterHouse) and 2026-11-08 (VL04-VL05 lived-in variants), exported into art/exports/village-houses-b.
    // Imports each model into a gitignored folder, checks it against its model_info.json (size, origin, LOD levels and triangles, objects,
    // Detail_* objects, collider, four material slots: Main / Stone / Wood atlases and the roof-tile material, sockets), then walks a 1.75 m
    // CharacterController: up the three steps onto the porch and against the (closed) door; pushed at the back, left and right walls from
    // outside it stops outside; VL03: from outside the fallen right wall, up the rubble, stopped at the old wall line (nobody gets into the
    // room or stuck in the heap). VL04/VL05: walkers on the porch pushed at the drying rack, the bamboo chair and the bonsai stop at
    // their boxes in <ID>_Detail_Collision, and walk through once that collider is switched off with Detail_Small. URP captures beside a 1.75 m capsule.
    // Work pack 2026-11-09 (B-112h batch B): PS01 old post station, exported into art/exports/roadside-landmarks-b, its own walks: up the
    // three steps onto the hall's plinth and against the door; into the open stall B as far as the feed trough; stopped by the shut gate
    // of stall A and the hanging gate of stall C; stopped by the hitching rail from the road, and round its end to the water trough;
    // pushed at the hall plinth and the stable's plank wall from behind and at the hall plinth from the left.
    // The rest of batch B (same kit): BS01 boundary stone, FS01 field shrine, RI04 scarecrows A/B, FE04 net rack, each pushed at from the front
    // (stops before it); PS02 broken bridge, up the stairs from both road ends, each stopped at its broken edge, and pushed sideways at
    // the balustrade on the deck; BT01 beacon tower, round the outside stair onto the paved top (feet 5.4 m), and pushed at the
    // standing wall from outside. Material slots for these come from model_info's materials (one to four atlases each).
    // Writes artifacts/village-houses-unity/. Run with -executeMethod YunJing.Editor.VillageHousesModelCheck.Run
    // This is an editor batch check, not play in the game: nothing is placed in the main scene.
    public static class VillageHousesModelCheck
    {
        const string Root = "Assets/YunJing/Generated/VillageHousesB";
        static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ".."));
        static readonly string[] RoadKit = { "PS", "BS", "FS", "RI", "FE", "BT" };
        static bool Road(string id) => RoadKit.Any(k => id.StartsWith(k));
        static string Exports(string id) => Path.Combine(Repo, "art", "exports", Road(id) ? "roadside-landmarks-b" : "village-houses-b");
        static string Out => Path.Combine(Repo, "artifacts", "village-houses-unity");
        static readonly string[] Wanted = { "VL01_LongEmptyHouse", "VL02_MovedInHouse", "VL03_HalfCollapsedHouse", "VL04_DiligentFamilyHouse", "VL05_ElderlyCoupleHouse", "PS01_OldPostStation",
                                                  "BS01_BoundaryStone", "FS01_FieldShrine", "RI04_Scarecrow_A", "RI04_Scarecrow_B", "FE04_NetRackMooring", "PS02_BrokenBridge", "BT01_OldBeaconTower" };
        static readonly string[] Slots = { "Main", "Stone", "Wood", "RoofTiles" };
        static readonly List<string> Report = new List<string>();
        static int failed;

        [Serializable] class Budget { public int triangles, objects, objects_without_detail, materials; }
        [Serializable] class BudgetPerLod { public Budget LOD0, LOD1, LOD2; }
        [Serializable] class LodTotals { public int LOD0, LOD1, LOD2; }
        [Serializable] class DetailBox { public string prop; public float yaw; public float[] centre_xy, half_m, z; }
        [Serializable] class ModelInfo { public string version, minTier; public float[] dimensions_m, bounds_min_m, bounds_max_m, size_limit_m; public float ground_z_m; public bool collision; public string[] materials; public LodTotals lod_totals; public BudgetPerLod budget_per_lod; public string[] detailObjects; public DetailBox[] detail_collision_boxes; }

        static readonly Dictionary<string, ModelInfo> infos = new Dictionary<string, ModelInfo>();
        static ModelInfo Info(string id)
        {
            if (!infos.TryGetValue(id, out var i)) infos[id] = i = JsonUtility.FromJson<ModelInfo>(File.ReadAllText(Path.Combine(Exports(id), id, "model_info.json")));
            return i;
        }
        static string Fbx(string id) => $"{Root}/{id}/{id}_{Info(id).version}.fbx";
        static string[] SlotsOf(string id)
        {
            var m = Info(id).materials;
            if (m == null || m.Length == 0) return Slots;
            return m.Select(x => x.Substring(("M_" + id + "_").Length)).ToArray();
        }
        static void Check(bool ok, string what) { Report.Add((ok ? "PASS " : "FAIL ") + what); if (!ok) failed++; }

        static void UsePipeline()
        {
            var pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>("Assets/YunJing/Generated/URP.asset");
            if (pipeline == null) { ProjectBuilder.Generate(); pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>("Assets/YunJing/Generated/URP.asset"); }
            if (GraphicsSettings.defaultRenderPipeline != pipeline) GraphicsSettings.defaultRenderPipeline = pipeline;
            if (QualitySettings.renderPipeline != pipeline) QualitySettings.renderPipeline = pipeline;
            pipeline.shadowDistance = 60;
        }

        public static void Run()
        {
            Report.Clear(); failed = 0; infos.Clear();
            UsePipeline();
            if (Directory.Exists(Out)) Directory.Delete(Out, true);
            Directory.CreateDirectory(Out);
            var ids = Wanted.Where(i => File.Exists(Path.Combine(Exports(i), i, "model_info.json"))).ToArray();
            Report.Add("INFO checked: " + string.Join(", ", ids.Select(i => $"{i} {Info(i).version}")) + "; not exported yet: " + string.Join(", ", Wanted.Except(ids)));
            foreach (var id in ids) Copy(id);
            AssetDatabase.Refresh();
            foreach (var id in ids) Configure(id);
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Lighting();
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane); ground.name = "Placeholder_Ground"; ground.transform.localScale = new Vector3(80, 1, 20);
            ground.transform.position = new Vector3(ids.Length * 20, -.001f, 0);
            var gm = new Material(Shader.Find("Universal Render Pipeline/Lit")); gm.SetColor("_BaseColor", new Color(.3f, .29f, .24f)); gm.SetFloat("_Smoothness", 0);
            gm.SetFloat("_SpecularHighlights", 0); gm.EnableKeyword("_SPECULARHIGHLIGHTS_OFF");
            gm.SetFloat("_EnvironmentReflections", 0); gm.EnableKeyword("_ENVIRONMENTREFLECTIONS_OFF");
            ground.GetComponent<Renderer>().sharedMaterial = gm;
            for (int n = 0; n < ids.Length; n++)
            {
                var id = ids[n];
                var at = new Vector3(n * 40, -Info(id).ground_z_m, 0);
                var go = Place(id, at); Verify(id, go); Sockets(id, go);
                var foot = new Vector3(at.x, 0, at.z);
                bool ps = id.StartsWith("PS01"), prop = Road(id) && !ps;
                if (ps) PsWalks(id, foot);
                else if (id.StartsWith("PS02")) BridgeWalks(id, foot);
                else if (id.StartsWith("BT01")) BeaconWalks(id, foot);
                else if (prop) FrontPush(id, foot);
                else { UpTheSteps(id, foot); Walls(id, foot); }
                if (id.StartsWith("VL03_")) OverTheRubble(id, foot);
                if (id.StartsWith("VL04_")) AtTheWoodpile(id, foot);
                if (Info(id).detail_collision_boxes != null && Info(id).detail_collision_boxes.Length > 0) IntoTheProps(id, go, foot);
                var b = LodBounds(go);
                var person = Person(foot + new Vector3(-(b.extents.x + .6f), 0, -2f));
                var both = b; both.Encapsulate(person.GetComponent<Renderer>().bounds);
                float d = both.size.magnitude * 1.25f; var c = both.center;
                Shot(id + "_three_quarter", c, c + new Vector3(.75f, .45f, -.85f).normalized * d, 35);
                Shot(id + "_front", c, c + new Vector3(0, .12f, -1).normalized * d, 35);
                Shot(id + "_back_right", c, c + new Vector3(.85f, .4f, .75f).normalized * d, 35);
                person.SetActive(false);
                if (prop)
                {
                    // 1.7 m eye height: a person standing in front of it (and for BT01 on the top, looking out over the breach)
                    float back = Mathf.Max(3.5f, b.extents.z + 2.5f);
                    var eye = foot + new Vector3(-.6f, 1.7f, -(b.extents.z + back));
                    Shot(id + "_eye_1p7", foot + new Vector3(0, Mathf.Min(1.4f, b.size.y * .5f), 0), eye, 50);
                    if (id.StartsWith("BT01"))
                    {
                        var top = foot + new Vector3(-.8f, 5.4f + 1.7f, -.6f);
                        Shot(id + "_eye_1p7_on_top", top + new Vector3(1, -.35f, 1), top, 70);
                        var climb = Person(foot + new Vector3(-.9f, 5.42f, -.3f));
                        Shot(id + "_person_on_top", c, c + new Vector3(-.7f, .45f, -.85f).normalized * d, 35);
                        UnityEngine.Object.DestroyImmediate(climb);
                    }
                    if (id.StartsWith("PS02"))
                    {
                        var stand = Person(foot + new Vector3(-1.45f, 3.5f, 0));
                        Shot(id + "_person_at_gap", c, c + new Vector3(.2f, .3f, -1).normalized * d * .8f, 35);
                        UnityEngine.Object.DestroyImmediate(stand);
                        var ledge = foot + new Vector3(-1.5f, 3.5f + 1.7f, -.3f);
                        Shot(id + "_eye_1p7_at_gap", ledge + new Vector3(1, -.45f, .05f), ledge, 60);
                    }
                }
                var on = prop ? null : Person(foot + (ps ? new Vector3(3.6f, .02f, -.7f) : new Vector3(-.6f, .54f, -3.1f)));   // VL: on the porch at the door; PS01: before the open stall
                var dc = prop ? c : foot + (ps ? new Vector3(3.6f, 1.2f, 1.2f) : new Vector3(0, 1.4f, -3.2f));
                if (ps) Shot(id + "_stable", dc, dc + new Vector3(-.3f, .3f, -1).normalized * 7.5f, 40);
                else if (!prop) Shot(id + "_porch", dc, dc + new Vector3(.55f, .25f, -1).normalized * 6.5f, 40);
                if (on != null) UnityEngine.Object.DestroyImmediate(on);
                if (id.StartsWith("VL04_"))
                {
                    var wp = foot + new Vector3(4.1f, .5f, -.1f);
                    Shot(id + "_woodpile", wp, wp + new Vector3(1, .35f, -.55f).normalized * 4.2f, 40);
                    var sill = foot + new Vector3(2.2f, 1.1f, -2.86f);
                    Shot(id + "_sill_tray", sill, sill + new Vector3(.25f, .55f, -1).normalized * 1.9f, 40);
                }
                if (id.StartsWith("VL05_"))      // Unity (x, up, z) = Blender (x, z, y)
                {
                    var corn = foot + new Vector3(0, 2.95f, -3.46f);
                    Shot(id + "_corn", corn, corn + new Vector3(.3f, -.45f, -1).normalized * 2.6f, 40);
                    var chair = foot + new Vector3(1.36f, .85f, -3.1f);
                    Shot(id + "_chair", chair, chair + new Vector3(-.35f, .3f, -1).normalized * 2.1f, 40);
                    var bon = foot + new Vector3(-1.36f, .85f, -3.0f);
                    Shot(id + "_bonsai", bon, bon + new Vector3(.4f, .3f, -1).normalized * 1.9f, 40);
                    var win = foot + new Vector3(2.35f, 2.0f, -2.6f);
                    Shot(id + "_window_patches", win, win + new Vector3(0, -.05f, -1).normalized * 2.2f, 40);
                }
                var det = go.GetComponentsInChildren<Renderer>(true).Where(r => r.name.Contains("_Detail_")).ToArray();
                if (det.Length > 0)
                {
                    foreach (var r in det) r.enabled = false;
                    if (prop) Shot(id + "_no_detail", c, c + new Vector3(.75f, .45f, -.85f).normalized * d, 35);
                    else Shot(id + "_porch_no_detail", dc, dc + new Vector3(.55f, .25f, -1).normalized * 6.5f, 40);
                    foreach (var r in det) r.enabled = true;
                }
                // LOD1 / LOD2 seen from the three-quarter camera (closer than where the group switches to them, so their loss shows).
                // The group is switched off for these: left on it keeps picking LOD0 at this distance and the hand-picked level renders nothing.
                var group = go.GetComponent<LODGroup>(); var lods = group.GetLODs();
                group.enabled = false;
                for (int lv = 1; lv < 3; lv++)
                {
                    for (int k = 0; k < 3; k++) foreach (var r in lods[k].renderers) r.enabled = k == lv;
                    Shot($"{id}_LOD{lv}", c, c + new Vector3(.75f, .45f, -.85f).normalized * d, 35);
                }
                for (int k = 0; k < 3; k++) foreach (var r in lods[k].renderers) r.enabled = true;
                group.enabled = true;
            }
            File.WriteAllText(Path.Combine(Out, "unity-verify-report.txt"), string.Join("\n", Report) + $"\n\nUnity {Application.unityVersion}; failed checks: {failed}; editor batch check only, not placed in the main scene, not played\n");
            Debug.Log("VILLAGE_HOUSES_" + (failed == 0 ? "PASS" : "FAIL") + "\n" + string.Join("\n", Report));
            if (failed > 0 && Application.isBatchMode) EditorApplication.Exit(1);
        }

        static void Copy(string id)
        {
            var src = Path.Combine(Exports(id), id); var dst = Path.Combine(Repo, "apps", "game", Root, id);
            Directory.CreateDirectory(Path.Combine(dst, "Textures"));
            foreach (var old in Directory.GetFiles(dst, "*.fbx").Where(f => !f.EndsWith($"_{Info(id).version}.fbx"))) { File.Delete(old); if (File.Exists(old + ".meta")) File.Delete(old + ".meta"); }
            foreach (var file in Directory.GetFiles(src, $"{id}_{Info(id).version}.fbx").Concat(Directory.GetFiles(Path.Combine(src, "Textures"), "*.png")))
                File.Copy(file, Path.Combine(dst, file.Substring(src.Length + 1)), true);
        }

        static void Configure(string id)
        {
            var importer = AssetImporter.GetAtPath(Fbx(id)) as ModelImporter;
            if (importer == null) throw new FileNotFoundException("FBX not imported", id);
            importer.bakeAxisConversion = true; importer.isReadable = true;
            importer.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription;     // keeps the FBX slot names (M_<id>_Main ...) to map onto
            importer.materialLocation = ModelImporterMaterialLocation.InPrefab;
            importer.importAnimation = false; importer.importCameras = false; importer.importLights = false; importer.addCollider = false;
            importer.importNormals = ModelImporterNormals.Import;
            importer.SaveAndReimport();
            foreach (var tex in Directory.GetFiles(Path.Combine(Repo, "apps", "game", Root, id, "Textures"), "*.png"))
            {
                var path = $"{Root}/{id}/Textures/{Path.GetFileName(tex)}";
                var ti = AssetImporter.GetAtPath(path) as TextureImporter; if (ti == null) continue;
                bool normal = path.EndsWith("_Normal.png");
                bool data = path.EndsWith("_MetallicSmoothness.png") || path.EndsWith("_Roughness.png") || path.EndsWith("_Metallic.png");
                ti.textureType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
                ti.sRGBTexture = !normal && !data; ti.maxTextureSize = 4096;
                ti.wrapMode = path.Contains("VL_RoofTiles_") ? TextureWrapMode.Repeat : TextureWrapMode.Clamp;   // the atlases are clamped
                ti.SaveAndReimport();
            }
        }

        static Texture2D Tex(string id, string file) => AssetDatabase.LoadAssetAtPath<Texture2D>($"{Root}/{id}/Textures/{file}");

        static string Prefix(string id, string slot) => slot == "Main" ? id : slot == "RoofTiles" ? "VL_RoofTiles" : $"{id}_{slot}";

        static Material Mat(string id, string slot)
        {
            var path = $"{Root}/{id}_{slot}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) { mat = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(mat, path); }
            var p = Prefix(id, slot);
            mat.SetTexture("_BaseMap", Tex(id, p + "_BaseColor.png")); mat.SetColor("_BaseColor", Color.white);
            mat.SetTexture("_BumpMap", Tex(id, p + "_Normal.png")); mat.EnableKeyword("_NORMALMAP");
            mat.SetTexture("_MetallicGlossMap", Tex(id, p + "_MetallicSmoothness.png")); mat.EnableKeyword("_METALLICSPECGLOSSMAP"); mat.SetFloat("_Smoothness", 1);
            EditorUtility.SetDirty(mat); return mat;
        }

        static readonly Dictionary<string, string> unmapped = new Dictionary<string, string>();

        static GameObject Place(string id, Vector3 position)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Fbx(id)));
            PrefabUtility.UnpackPrefabInstance(go, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            go.transform.position = position;
            var slots = SlotsOf(id); var mats = slots.ToDictionary(s => s, s => Mat(id, s));
            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
            {
                if (r.name == id + "_Collision" || r.name == id + "_Detail_Collision") { r.enabled = false; continue; }
                r.sharedMaterials = r.sharedMaterials.Select(m =>
                {
                    var name = m != null ? m.name : "";
                    var slot = slots.OrderByDescending(s => s.Length).FirstOrDefault(s => name.EndsWith("_" + s));
                    if (slot == null) { unmapped[r.name] = name; slot = "Main"; }
                    return mats[slot];
                }).ToArray();
            }
            var cut = new[] { .1f, .035f, .006f };
            var group = go.GetComponent<LODGroup>(); if (group == null) group = go.AddComponent<LODGroup>();
            group.SetLODs(Enumerable.Range(0, 3).Select(i => new LOD(cut[i], go.GetComponentsInChildren<Renderer>(true).Where(r => r.name.EndsWith("_LOD" + i)).ToArray())).ToArray());
            foreach (var col in go.GetComponentsInChildren<MeshFilter>(true).Where(m => m.name == id + "_Collision" || m.name == id + "_Detail_Collision"))
                col.gameObject.AddComponent<MeshCollider>().sharedMesh = col.sharedMesh;
            return go;
        }

        static GameObject Person(Vector3 feet)
        {
            var p = GameObject.CreatePrimitive(PrimitiveType.Capsule); p.name = "Person_1.75m";
            UnityEngine.Object.DestroyImmediate(p.GetComponent<Collider>());
            p.transform.localScale = new Vector3(.45f, .875f, .45f); p.transform.position = feet + Vector3.up * .875f;
            var m = new Material(Shader.Find("Universal Render Pipeline/Lit")); m.SetColor("_BaseColor", new Color(.55f, .57f, .6f)); p.GetComponent<Renderer>().sharedMaterial = m;
            return p;
        }

        static Bounds LodBounds(GameObject go, string suffix = "_LOD0")
        {
            var rs = go.GetComponentsInChildren<Renderer>(true).Where(r => r.name.EndsWith(suffix)).ToArray();
            var b = rs[0].bounds; foreach (var r in rs) b.Encapsulate(r.bounds); return b;
        }

        static void Verify(string id, GameObject go)
        {
            var info = Info(id);
            var b = LodBounds(go); var o = go.transform.position;
            float[] want = info.dimensions_m; Vector3 size = b.size;
            float dx = Mathf.Abs(size.x - want[0]), dy = Mathf.Abs(size.z - want[1]), dz = Mathf.Abs(size.y - want[2]);
            Check(dx < .002f && dy < .002f && dz < .002f, $"{id}: imported size {size.x:F3} x {size.z:F3} x {size.y:F3} m matches model_info (max error {Mathf.Max(dx, dy, dz) * 1000:F1} mm)");
            var lo = b.min - o; var hi = b.max - o;
            float e = Mathf.Max(Mathf.Abs(lo.x - info.bounds_min_m[0]), Mathf.Abs(lo.z - info.bounds_min_m[1]), Mathf.Abs(lo.y - info.bounds_min_m[2]),
                                Mathf.Abs(hi.x - info.bounds_max_m[0]), Mathf.Abs(hi.z - info.bounds_max_m[1]), Mathf.Abs(hi.y - info.bounds_max_m[2]));
            Check(e < .002f, $"{id}: bounds about the origin {lo.x:F3}..{hi.x:F3}, {lo.z:F3}..{hi.z:F3}, {lo.y:F3}..{hi.y:F3} m equal model_info (max error {e * 1000:F1} mm)");
            Report.Add($"INFO {id}: minTier {info.minTier}");
            var lod = go.GetComponent<LODGroup>();
            Check(lod != null && lod.GetLODs().Length == 3 && lod.GetLODs().All(l => l.renderers.Length > 0), $"{id}: LODGroup with 3 filled levels");
            var mfs = go.GetComponentsInChildren<MeshFilter>(true);
            int tri(string s) => mfs.Where(m => m.name.EndsWith(s)).Sum(m => m.sharedMesh.triangles.Length / 3);
            int objs(string s) => mfs.Count(m => m.name.EndsWith(s));
            Check(tri("_LOD0") == info.lod_totals.LOD0 && tri("_LOD1") == info.lod_totals.LOD1 && tri("_LOD2") == info.lod_totals.LOD2,
                  $"{id}: imported LOD triangles {tri("_LOD0")}/{tri("_LOD1")}/{tri("_LOD2")} equal model_info {info.lod_totals.LOD0}/{info.lod_totals.LOD1}/{info.lod_totals.LOD2}");
            if (info.budget_per_lod != null && info.budget_per_lod.LOD0 != null)
            {
                var bl = new[] { info.budget_per_lod.LOD0, info.budget_per_lod.LOD1, info.budget_per_lod.LOD2 };
                Check(Enumerable.Range(0, 3).All(i => objs("_LOD" + i) == bl[i].objects), $"{id}: objects per LOD {objs("_LOD0")}/{objs("_LOD1")}/{objs("_LOD2")} equal model_info {bl[0].objects}/{bl[1].objects}/{bl[2].objects}");
            }
            // every non-Detail LOD0 object together (PS02 exports its balustrade as its own object, PS02_BrokenBridge_Rail_LOD0)
            var bodies = go.GetComponentsInChildren<Renderer>(true).Where(r => r.name.EndsWith("_LOD0") && !r.name.Contains("_Detail_")).ToArray();
            var names = bodies.SelectMany(r => r.sharedMaterials.Select(m => m.name)).Distinct().ToArray();
            var slots = SlotsOf(id);
            Check(names.Length == slots.Length && slots.All(s => names.Contains($"{id}_{s}")),
                  $"{id}: the LOD0 objects ({string.Join(", ", bodies.Select(r => r.name))}) carry the {slots.Length} material slot(s) {string.Join(" / ", slots)}, each mapped from its FBX slot name ({string.Join(", ", names)})");
            Check(!unmapped.Keys.Any(k => k.StartsWith(id)), $"{id}: every FBX material slot name was recognised" + (unmapped.Count > 0 ? " (unmapped: " + string.Join("; ", unmapped.Select(kv => kv.Key + "=" + kv.Value)) + ")" : ""));
            foreach (var d in info.detailObjects ?? new string[0])
            {
                // FE04's net (Detail_Net) is twine that is never decimated: it is whole at LOD0, the main net alone at LOD1, and left out of LOD2
                bool net = d.EndsWith("_Detail_Net"); int levels = net ? 2 : 3;
                Check(Enumerable.Range(0, levels).All(i => mfs.Any(m => m.name == $"{d}_LOD{i}")) && (!net || !mfs.Any(m => m.name == $"{d}_LOD2")),
                      $"{id}: {d} present at LOD0/{(net ? "1 (left out of LOD2 by design)" : "1/2")} as its own object (can be switched off)");
            }
            var col = go.GetComponentsInChildren<MeshCollider>(true).FirstOrDefault(c => c.name == id + "_Collision");
            Check(info.collision && col != null && col.sharedMesh.triangles.Length > 0, $"{id}: {id}_Collision imported as MeshCollider ({(col ? col.sharedMesh.triangles.Length / 3 : 0)} triangles), renderer hidden");
            if (col != null)
            {   // the collider stays inside the piece's size limit about its origin (invisible blockers, such as PS02's 1.1 m stop at the gap, may rise above the visible model)
                var box = col.bounds; var lim = info.size_limit_m;
                // within the model bounds (+0.1 m), or within the size-limit box centred on the model's footprint (VL houses: the origin is not the footprint centre)
                var near = b; near.Expand(.1f);
                bool hasLim = lim != null && lim.Length == 3;
                Bounds LimAt(float cx, float cz) => new Bounds(new Vector3(cx, o.y + lim[2] / 2, cz), new Vector3(lim[0], lim[2], lim[1]) + Vector3.one * .02f);
                bool In(Bounds k) => k.Contains(box.min) && k.Contains(box.max);
                bool inNear = In(near), inOrigin = hasLim && In(LimAt(o.x, o.z)), inFoot = hasLim && In(LimAt(b.center.x, b.center.z));
                Check(inNear || inOrigin || inFoot, $"{id}: the collider ({box.min - o} .. {box.max - o}) stays {(inNear ? "on the model (bounds + 0.1 m)" : hasLim ? $"inside the {lim[0]} x {lim[1]} x {lim[2]} m size limit ({(inOrigin ? "about the origin" : "about the footprint centre")})" : "on the model")}");
            }
            if (info.detail_collision_boxes != null && info.detail_collision_boxes.Length > 0)
            {
                var dcol = go.GetComponentsInChildren<MeshCollider>(true).FirstOrDefault(c => c.name == id + "_Detail_Collision");
                var dr = go.GetComponentsInChildren<Renderer>(true).FirstOrDefault(r => r.name == id + "_Detail_Collision");
                Check(dcol != null && dcol.sharedMesh.triangles.Length / 3 == 12 * info.detail_collision_boxes.Length && (dr == null || !dr.enabled),
                      $"{id}: {id}_Detail_Collision imported as its own MeshCollider ({(dcol ? dcol.sharedMesh.triangles.Length / 3 : 0)} triangles = {info.detail_collision_boxes.Length} boxes: {string.Join(", ", info.detail_collision_boxes.Select(x => x.prop))}), renderer hidden");
            }
            Check(!go.GetComponentsInChildren<Renderer>(true).Any(r => r.enabled && r.sharedMaterials.Any(m => m == null || m.shader.name.Contains("Error"))), $"{id}: no missing or error shaders");
            foreach (var t in Directory.GetFiles(Path.Combine(Repo, "apps", "game", Root, id, "Textures"), "*_BaseColor.png"))
            {
                var tex = Tex(id, Path.GetFileName(t)); if (tex != null) Report.Add($"INFO {id}: texture {tex.name} {tex.width}x{tex.height} (+ Normal, MetallicSmoothness of the same size)");
            }
        }

        static void Sockets(string id, GameObject go)
        {
            var text = File.ReadAllText(Path.Combine(Exports(id), id, "model_info.json"));
            int a = text.IndexOf("\"sockets_blender_xyz\""); if (a < 0) { Report.Add($"INFO {id}: no sockets in model_info"); return; }
            int b = text.IndexOf('{', a), e = text.IndexOf('}', b);
            var o = go.transform.position; float worst = 0; int found = 0, wanted = 0;
            foreach (var entry in text.Substring(b + 1, e - b - 1).Split(new[] { "]," }, StringSplitOptions.RemoveEmptyEntries))
            {
                var kv = entry.Split(':'); var name = kv[0].Trim().Trim('"', ' ', (char)10, (char)13);
                var v = kv[1].Replace("[", "").Replace("]", "").Split(',').Select(x => float.Parse(x.Trim(), System.Globalization.CultureInfo.InvariantCulture)).ToArray();
                wanted++;
                var t = go.GetComponentsInChildren<Transform>(true).FirstOrDefault(x => x.name == name); if (t == null) continue;
                found++; var p = t.position - o; worst = Mathf.Max(worst, Vector3.Distance(p, new Vector3(v[0], v[2], v[1])));
            }
            Check(found == wanted && worst < .002f, $"{id}: {found}/{wanted} socket empties imported at the model_info positions (max error {worst * 1000:F1} mm)");
        }

        static CharacterController Walker()
        {
            var body = new GameObject("Walker_1.75m"); var cc = body.AddComponent<CharacterController>();
            cc.height = 1.75f; cc.radius = .25f; cc.center = new Vector3(0, .875f, 0); cc.stepOffset = .3f; cc.slopeLimit = 45; cc.skinWidth = .02f;
            return cc;
        }

        static Vector2 Stroll(CharacterController cc, Vector3 o, Vector3 dir, int n)
        {
            float lo = 99, hi = -99;
            for (int f = 0; f < n; f++)
            {
                cc.Move(dir * (1.4f / 60f) + Vector3.down * (9.8f / 60f));
                var p = cc.transform.position - o;
                if (f > 20) { lo = Mathf.Min(lo, p.y); hi = Mathf.Max(hi, p.y); }
            }
            return new Vector2(lo, hi);
        }

        // from the path 1 m in front of the bottom step: up the three 0.18 m steps onto the 0.54 m porch, then against the closed door
        static void UpTheSteps(string id, Vector3 o)
        {
            Physics.SyncTransforms(); var cc = Walker();
            foreach (float x in new[] { -.6f, 0f, .6f })
            {
                cc.transform.position = o + new Vector3(x, .02f, -5.7f); Physics.SyncTransforms();
                var feet = Stroll(cc, o, Vector3.forward, 260); var end = cc.transform.position - o;
                Check(Mathf.Abs(end.y - .54f) < .04f && end.z > -3.0f && end.z < -2.61f - .2f && Mathf.Abs(end.x - x) < .15f,
                      $"{id}: walker on x {x:F1} climbs the steps onto the porch and stops at the closed door (end z {end.z:F2} m, feet {end.y:F3} m, highest {feet.y:F3} m)");
            }
            UnityEngine.Object.DestroyImmediate(cc.gameObject);
        }

        // pushed at the back, left and right walls from outside (on the ground): stops outside the wall line (2.61 / 3.61 m)
        static void Walls(string id, Vector3 o)
        {
            Physics.SyncTransforms(); var cc = Walker();
            var tests = new List<(string what, Vector3 start, Vector3 dir, Func<Vector3, bool> ok)>
            {
                ("back wall", new Vector3(-1.5f, .02f, 4.6f), Vector3.back, p => p.z > 2.61f + .2f),
                ("back wall", new Vector3(1.8f, .02f, 4.6f), Vector3.back, p => p.z > 2.61f + .2f),
                ("left wall", new Vector3(-5.6f, .02f, 0f), Vector3.right, p => p.x < -3.61f - .2f),
            };
            if (!id.StartsWith("VL03_")) tests.Add(("right wall", new Vector3(5.6f, .02f, 0f), Vector3.left, p => p.x > 3.61f + .2f));
            foreach (var t in tests)
            {
                cc.transform.position = o + t.start; Physics.SyncTransforms();
                var feet = Stroll(cc, o, t.dir, 240); var end = cc.transform.position - o;
                Check(t.ok(end), $"{id}: a walker pushed at the {t.what} from outside stops outside it (end x {end.x:F2}, z {end.z:F2} m, feet {feet.x:F3}-{feet.y:F3} m)");
            }
            UnityEngine.Object.DestroyImmediate(cc.gameObject);
        }

        // VL03: from outside the fallen right wall, three lines across the heap: up the rubble ramp, stopped at the old wall line,
        // then back down the way it came (it is not caught in the heap)
        static void OverTheRubble(string id, Vector3 o)
        {
            Physics.SyncTransforms(); var cc = Walker();
            foreach (float z in new[] { -.4f, .5f, 1.4f })
            {
                cc.transform.position = o + new Vector3(6.0f, .02f, z); Physics.SyncTransforms();
                var feet = Stroll(cc, o, Vector3.left, 260); var mid = cc.transform.position - o;
                Stroll(cc, o, Vector3.right, 260); var back = cc.transform.position - o;
                Check(mid.x > 3.61f + .2f && back.x > 5.5f && back.y < .05f,
                      $"{id}: on z {z:F1} a walker goes up the rubble, stops outside the fallen wall's line (x {mid.x:F2} m, feet up to {feet.y:F3} m) and walks back off it (x {back.x:F2} m, feet {back.y:F3} m)");
            }
            UnityEngine.Object.DestroyImmediate(cc.gameObject);
        }

        // VL04: the woodpile outside the right gable (x 3.86-4.34, z -1.52..1.32, collision top 0.78 m, higher than the 0.3 m step offset):
        // walkers pushed at it from outside on three lines stop outside it and stay on the ground (nobody climbs the logs)
        static void AtTheWoodpile(string id, Vector3 o)
        {
            Physics.SyncTransforms(); var cc = Walker();
            foreach (float z in new[] { -1.2f, 0f, 1.0f })
            {
                cc.transform.position = o + new Vector3(6.0f, .02f, z); Physics.SyncTransforms();
                var feet = Stroll(cc, o, Vector3.left, 260); var end = cc.transform.position - o;
                Check(end.x > 4.34f + .2f && feet.y < .05f,
                      $"{id}: on z {z:F1} a walker pushed at the woodpile from outside stops outside it (x {end.x:F2} m) and stays on the ground (feet {feet.x:F3}-{feet.y:F3} m)");
            }
            UnityEngine.Object.DestroyImmediate(cc.gameObject);
        }

        // VL04/VL05: on the porch (feet 0.54 m), two lines 0.1 m apart pushed level at each Detail_Small prop from its open side (the rack
        // and the bonsai from the door side, the chair from the door side too: the bench is behind it). With <ID>_Detail_Collision on the
        // walker stops with its 0.25 m capsule touching the prop's box (gap to the box 0.2-0.32 m from the capsule axis) and stays on the
        // porch floor; with that collider switched off (as with Detail_Small at low quality) the same line walks on past the prop's centre.
        static void IntoTheProps(string id, GameObject go, Vector3 o)
        {
            var dcol = go.GetComponentsInChildren<MeshCollider>(true).FirstOrDefault(c => c.name == id + "_Detail_Collision");
            if (dcol == null) { Check(false, $"{id}: no {id}_Detail_Collision to walk into"); return; }
            Physics.SyncTransforms(); var cc = Walker();
            foreach (var bx in Info(id).detail_collision_boxes)
            {
                float ca = Mathf.Cos(bx.yaw), sa = Mathf.Sin(bx.yaw), cx = bx.centre_xy[0], cy = bx.centre_xy[1];
                float gap(Vector3 q)    // distance in plan from q (relative to o; Unity x, z = Blender x, y) to the turned box
                {
                    float dx = q.x - cx, dy = q.z - cy, u = dx * ca + dy * sa, v = -dx * sa + dy * ca;
                    float ou = Mathf.Max(0, Mathf.Abs(u) - bx.half_m[0]), ov = Mathf.Max(0, Mathf.Abs(v) - bx.half_m[1]);
                    return Mathf.Sqrt(ou * ou + ov * ov);
                }
                float reachX = Mathf.Abs(bx.half_m[0] * ca) + Mathf.Abs(bx.half_m[1] * sa);   // the box's half width along x
                float side = cx < 0 ? 1 : -1;                                                // the door side: towards x = 0
                var dir = new Vector3(-side, 0, 0);
                foreach (float dz in new[] { 0f, .1f })
                {
                    var start = new Vector3(cx + side * (reachX + 1.0f), .56f, cy + dz);
                    dcol.enabled = true; cc.transform.position = o + start; Physics.SyncTransforms();
                    var feet = Stroll(cc, o, dir, 150); var end = cc.transform.position - o; float g = gap(end);
                    Check(g > .2f && g < .32f && Mathf.Abs(feet.y - .54f) < .04f && Mathf.Abs(feet.x - .54f) < .04f,
                          $"{id}: on the porch at z {start.z:F2} a walker pushed at the {bx.prop} stops at its collision box (capsule axis {g:F3} m from the box, x {end.x:F2} m) and stays on the floor (feet {feet.x:F3}-{feet.y:F3} m)");
                    dcol.enabled = false; cc.transform.position = o + start; Physics.SyncTransforms();
                    Stroll(cc, o, dir, 150); var through = cc.transform.position - o;
                    Check(side * (through.x - cx) < 0,
                          $"{id}: with {id}_Detail_Collision switched off the same walker goes on past the {bx.prop} (x {through.x:F2} m, prop centre x {cx:F2} m)");
                }
            }
            dcol.enabled = true;
            UnityEngine.Object.DestroyImmediate(cc.gameObject);
        }

        // PS01 (Unity x, up, z = Blender x, z, y): hall plinth y -1.3..4.25 m, 0.4 m high, three steps at x -3; hall front wall z -0.5;
        // stable posts on z 0.2, stall gates z 1.36 (A x 0.76..2.59 shut, C x 4.66..6.24 hanging), stall B open to the troughs (z 3.68);
        // hitching rail z -4.5 (x -1.7..5.1), stone water trough x 4.78..6.22, z -1.3..-0.7; stable plank wall z 4.32
        static void PsWalks(string id, Vector3 o)
        {
            Physics.SyncTransforms(); var cc = Walker();
            var tests = new List<(string what, Vector3 start, Vector3 dir, Func<Vector3, Vector2, bool> ok)>
            {
                ("from the yard up the three steps onto the hall plinth stops at the door", new Vector3(-3f, .02f, -4f), Vector3.forward,
                    (p, f) => p.y > .36f && p.y < .46f && p.z > -.9f && p.z < -.68f),
                ("into the open stall B stops at the feed trough", new Vector3(3.6f, .02f, -3.5f), Vector3.forward, (p, f) => p.z > 3.25f && p.z < 3.5f && f.y < .16f),
                ("at the shut gate of stall A stops before it", new Vector3(1.7f, .02f, -3.5f), Vector3.forward, (p, f) => p.z > .95f && p.z < 1.15f),
                ("at the hanging gate of stall C stops before it", new Vector3(5.4f, .02f, -.3f), Vector3.forward, (p, f) => p.z > .95f && p.z < 1.15f),
                ("from the road at the hitching rail stops before it", new Vector3(2f, .02f, -6.5f), Vector3.forward, (p, f) => p.z > -4.95f && p.z < -4.78f && f.y < .05f),
                ("from the road round the rail's end reaches the water trough", new Vector3(5.75f, .02f, -6.5f), Vector3.forward, (p, f) => p.z > -1.65f && p.z < -1.48f && f.y < .06f),
                ("pushed at the hall plinth from behind stops outside it", new Vector3(-3f, .02f, 6.5f), Vector3.back, (p, f) => p.z > 4.4f && f.y < .05f),
                ("pushed at the stable's plank wall from behind stops outside it", new Vector3(3.6f, .02f, 6.5f), Vector3.back, (p, f) => p.z > 4.45f && f.y < .05f),
                ("pushed at the hall plinth from the left stops outside it", new Vector3(-9f, .02f, 1.8f), Vector3.right, (p, f) => p.x < -6.7f && f.y < .05f),
            };
            foreach (var t in tests)
            {
                cc.transform.position = o + t.start; Physics.SyncTransforms();
                var feet = Stroll(cc, o, t.dir, 400); var end = cc.transform.position - o;
                Check(t.ok(end, feet), $"{id}: a walker {t.what} (end x {end.x:F2}, z {end.z:F2} m, feet {end.y:F3} m, lowest-highest {feet.x:F3}-{feet.y:F3} m)");
            }
            UnityEngine.Object.DestroyImmediate(cc.gameObject);
        }

        // BS01 / FS01 / RI04 / FE04: three lines from 2.5 m in front (Unity -z = Blender -Y, the front) pushed straight at the piece:
        // each stops in front of the origin (nobody walks through it) and stays on the ground or the piece's own low step
        static void FrontPush(string id, Vector3 o)
        {
            Physics.SyncTransforms(); var cc = Walker(); var info = Info(id);
            float front = info.bounds_min_m[1];
            float[] xs = id.StartsWith("FE04") ? new[] { -.95f, 0f, .9f } : new[] { -.08f, 0f, .08f };
            foreach (float x in xs)
            {
                cc.transform.position = o + new Vector3(x, .02f, front - 2.5f); Physics.SyncTransforms();
                var feet = Stroll(cc, o, Vector3.forward, 300); var end = cc.transform.position - o;
                Check(end.z < -.1f && feet.y < .45f,
                      $"{id}: a walker on x {x:F2} pushed at it from the front stops in front of it (end z {end.z:F2} m, front face z {front:F2} m, feet {feet.x:F3}-{feet.y:F3} m)");
            }
            UnityEngine.Object.DestroyImmediate(cc.gameObject);
        }

        // PS02 (Unity x, up, z = Blender x, z, y): road ends at x -6.95 / 6.95 (ground), 20 risers of 0.175 m up to the deck at 3.5 m;
        // the left half breaks at x -0.95, the right at 1.35 (gap 2.3 m), each edge fenced by an invisible 1.1 m lip in the collision.
        // Up each stair on three lines: the walker climbs and stops at the broken edge, high on the bridge (nobody walks into the gap);
        // then from there pushed sideways at the balustrade: it stays on the deck (|z| < 1.52 m) and does not fall off.
        static void BridgeWalks(string id, Vector3 o)
        {
            Physics.SyncTransforms(); var cc = Walker();
            foreach (var (side, edge) in new[] { (-1f, -.95f), (1f, 1.35f) })
                foreach (float z in new[] { -.6f, 0f, .6f })
                {
                    cc.transform.position = o + new Vector3(side * 8.6f, .02f, z); Physics.SyncTransforms();
                    var feet = Stroll(cc, o, new Vector3(-side, 0, 0), 700); var end = cc.transform.position - o;
                    Check(side * end.x > side * edge && Mathf.Abs(end.x - edge) < 1.0f && end.y > 3.0f,
                          $"{id}: from the {(side < 0 ? "left" : "right")} road end on z {z:F1} a walker climbs the stair and stops at the broken edge (end x {end.x:F2} m, edge {edge:F2} m, feet {end.y:F3} m)");
                    if (z == 0f)
                        foreach (float dz in new[] { -1f, 1f })
                        {
                            var at = cc.transform.position; Stroll(cc, o, new Vector3(0, 0, dz), 200); var s2 = cc.transform.position - o;
                            Check(Mathf.Abs(s2.z) < 1.52f && s2.y > 3.0f,
                                  $"{id}: on the {(side < 0 ? "left" : "right")} half near the edge a walker pushed sideways ({(dz < 0 ? "front" : "back")}) stays inside the balustrade (z {s2.z:F2} m, feet {s2.y:F3} m)");
                            cc.transform.position = at; Physics.SyncTransforms();
                        }
                }
            UnityEngine.Object.DestroyImmediate(cc.gameObject);
        }

        // BT01: the stair runs round the outside of the wall clockwise from -100 deg (front) to -240 deg (back-left), 27 risers of
        // 0.2 m, 0.9 m wide on the wall face (radius 2.75 m at the foot, 2.45 m at the 5.4 m top). The walker follows its middle line
        // (steered along the tangent, pulled to the middle radius), and at the end turns in onto the paved top: feet at 5.4 m, inside
        // the wall. Then pushed at the standing wall from outside at -60 deg (between the stair foot and the breach): stops outside it.
        static void BeaconWalks(string id, Vector3 o)
        {
            Physics.SyncTransforms(); var cc = Walker();
            float th0 = -100 * Mathf.Deg2Rad, th1 = -240 * Mathf.Deg2Rad;
            float rad(float z) => 2.75f + (2.45f - 2.75f) * Mathf.Clamp(z, 0, 5.4f) / 5.4f;
            float a0 = th0 + 12 * Mathf.Deg2Rad;
            cc.transform.position = o + new Vector3(Mathf.Cos(a0) * 3.2f, .02f, Mathf.Sin(a0) * 3.2f); Physics.SyncTransforms();
            float unwrapped = a0, prev = a0, lowest = 99, highest = -99; int f = 0;
            for (; f < 1400 && unwrapped > th1 + 4 * Mathf.Deg2Rad; f++)      // stop on the last treads (the stair ends at -240 deg; past it the walker steps off into the air)
            {
                var p = cc.transform.position - o; float phi = Mathf.Atan2(p.z, p.x);
                float dphi = Mathf.DeltaAngle(prev * Mathf.Rad2Deg, phi * Mathf.Rad2Deg) * Mathf.Deg2Rad; unwrapped += dphi; prev = phi;
                float rho = new Vector2(p.x, p.z).magnitude, want = rad(p.y) + .45f;
                var tangent = new Vector3(Mathf.Sin(phi), 0, -Mathf.Cos(phi)); var radial = new Vector3(Mathf.Cos(phi), 0, Mathf.Sin(phi));
                var dir = (tangent + radial * Mathf.Clamp((want - rho) * 2f, -.6f, .6f)).normalized;
                cc.Move(dir * (1.4f / 60f) + Vector3.down * (9.8f / 60f));
                if (f > 20) { lowest = Mathf.Min(lowest, p.y); highest = Mathf.Max(highest, p.y); }
            }
            var atEnd = cc.transform.position - o;
            Check(atEnd.y > 5.0f, $"{id}: a walker follows the outside stair from the foot round to its top (turned {(a0 - unwrapped) * Mathf.Rad2Deg:F0} deg in {f} frames, feet now {atEnd.y:F3} m)");
            var inward = -new Vector3(atEnd.x, 0, atEnd.z).normalized;
            var feet = Stroll(cc, o, inward, 110); var end = cc.transform.position - o; float r = new Vector2(end.x, end.z).magnitude;
            Check(Mathf.Abs(end.y - 5.4f) < .08f && r < 2.0f,
                  $"{id}: from the stair head it steps onto the paved top and stands there (radius {r:F2} m, feet {end.y:F3} m, while crossing {feet.x:F3}-{feet.y:F3} m)");
            Stroll(cc, o, Vector3.zero, 60); var still = cc.transform.position - o;
            Check(Mathf.Abs(still.y - end.y) < .02f, $"{id}: standing still on the top it stays there (feet {still.y:F3} m)");
            float aw = -60 * Mathf.Deg2Rad;
            cc.transform.position = o + new Vector3(Mathf.Cos(aw) * 3.9f, .02f, Mathf.Sin(aw) * 3.9f); Physics.SyncTransforms();
            var f2 = Stroll(cc, o, -new Vector3(Mathf.Cos(aw), 0, Mathf.Sin(aw)), 240); var e2 = cc.transform.position - o;
            float r2 = new Vector2(e2.x, e2.z).magnitude;
            Check(r2 > 2.75f && f2.y < .1f, $"{id}: pushed at the standing wall from outside (-60 deg) a walker stops outside it (radius {r2:F2} m, feet {f2.x:F3}-{f2.y:F3} m)");
            UnityEngine.Object.DestroyImmediate(cc.gameObject);
        }

        static void Lighting()
        {
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(.62f, .68f, .7f); RenderSettings.ambientEquatorColor = new Color(.45f, .44f, .38f); RenderSettings.ambientGroundColor = new Color(.2f, .18f, .14f);
            var sun = new GameObject("Sun").AddComponent<Light>(); sun.type = LightType.Directional; sun.intensity = 1.25f;
            sun.color = new Color(1, .96f, .88f); sun.transform.rotation = Quaternion.Euler(38, -30, 0); sun.shadows = LightShadows.Soft;
            var cam = new GameObject("Main Camera", typeof(Camera)).GetComponent<Camera>(); cam.tag = "MainCamera"; cam.nearClipPlane = .02f; cam.farClipPlane = 300;
            cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = new Color(.74f, .82f, .84f);
            cam.GetUniversalAdditionalCameraData().renderPostProcessing = false;
        }

        static void Shot(string file, Vector3 target, Vector3 eye, float fov = 40)
        {
            var cam = Camera.main; var rt = new RenderTexture(1600, 900, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            cam.transform.position = eye; cam.transform.LookAt(target); cam.fieldOfView = fov; cam.targetTexture = rt; cam.Render();
            RenderTexture.active = rt; var tex = new Texture2D(1600, 900, TextureFormat.RGB24, false); tex.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0); tex.Apply();
            File.WriteAllBytes(Path.Combine(Out, file + ".png"), tex.EncodeToPNG()); UnityEngine.Object.DestroyImmediate(tex);
            RenderTexture.active = null; cam.targetTexture = null; rt.Release(); Report.Add("SHOT " + file);
        }
    }
}
