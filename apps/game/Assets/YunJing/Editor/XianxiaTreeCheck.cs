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
    // 承天 XT01 xianxia great tree (仙俠風格大型綠樹 + gold-leaf version, one mesh, one texture set). Installs the export from
    // art/exports/trees-xianxia/XT01_XianxiaGreatTree into Assets/YunJing/Models/XianxiaGreatTreeV4 (FBX, textures, five materials on
    // YunJing/XianxiaTreeBark + YunJing/XianxiaTreeLeaves, two prefabs Green / Gold with LODGroup and trunk collider), then checks
    // LODs, triangles, materials, vertex colours, wind weights, height and the trunk collider (a 1.75 m CharacterController walking
    // at the trunk stops, one walking 1.5 m beside it goes on), and takes shots: views round the tree, under the crown, every LOD,
    // 50 / 100 m, beside VL02 and a 1.75 m figure, close-ups, and both trees dropped into the game scene Qingxi.unity (not saved).
    // Writes artifacts/xianxia-tree-unity/. Run: -executeMethod YunJing.Editor.XianxiaTreeCheck.Run
    public static class XianxiaTreeCheck
    {
        const string Id = "XT01_XianxiaGreatTree";
        const string Dst = "Assets/YunJing/Models/XianxiaGreatTreeV4";
        static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ".."));
        static string Src => Path.Combine(Repo, "art", "exports", "trees-xianxia", Id);
        static string Out => Path.Combine(Repo, "artifacts", "xianxia-tree-unity");
        static readonly List<string> Report = new List<string>();
        static int failed;

        [Serializable] class Budget { public int triangles, cap, objects, materials, wood_triangles, leaf_cards; }
        [Serializable] class BudgetPerLod { public Budget LOD0, LOD1, LOD2, LOD3; }
        [Serializable] class Capsule { public float radius, height; public float[] centre; }
        [Serializable] class Look { public string deep, mid, tip, var_a, var_b; public float var_amount, midpoint; }
        [Serializable] class Looks { public Look green, gold; }
        [Serializable] class LeafShader { public float detail, value, mean_value, graze_min, graze_max; }
        [Serializable] class Info { public string asset, version; public float height_m; public float[] lod_switch_distance_m; public BudgetPerLod budget_per_lod; public Capsule collision_capsule; public Looks looks; public LeafShader leaf_shader; }
        static Info info;
        static Budget B(int l) => l == 0 ? info.budget_per_lod.LOD0 : l == 1 ? info.budget_per_lod.LOD1 : l == 2 ? info.budget_per_lod.LOD2 : info.budget_per_lod.LOD3;
        static void Check(bool ok, string what) { Report.Add((ok ? "PASS " : "FAIL ") + what); if (!ok) failed++; }
        static string Fbx => $"{Dst}/{Id}_{info.version}.fbx";

        public static void Run()
        {
            Report.Clear(); failed = 0;
            info = JsonUtility.FromJson<Info>(File.ReadAllText(Path.Combine(Src, "model_info.json")));
            var pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>("Assets/YunJing/Generated/URP.asset");
            if (pipeline == null) { ProjectBuilder.Generate(); pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>("Assets/YunJing/Generated/URP.asset"); }
            if (GraphicsSettings.defaultRenderPipeline != pipeline) GraphicsSettings.defaultRenderPipeline = pipeline;
            if (QualitySettings.renderPipeline != pipeline) QualitySettings.renderPipeline = pipeline;
            pipeline.shadowDistance = 150;
            if (Directory.Exists(Out)) Directory.Delete(Out, true);
            Directory.CreateDirectory(Out);
            Install();
            var prefabs = new Dictionary<string, GameObject> { ["Green"] = BuildPrefab("Green"), ["Gold"] = BuildPrefab("Gold") };

            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Lighting();
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane); ground.name = "Placeholder_Grass"; ground.transform.localScale = new Vector3(150, 1, 150);
            var gm = new Material(Shader.Find("Universal Render Pipeline/Lit")); gm.SetColor("_BaseColor", new Color(.36f, .55f, .2f)); gm.SetFloat("_Smoothness", .05f);
            ground.GetComponent<Renderer>().sharedMaterial = gm;
            var green = Place(prefabs["Green"], new Vector3(0, 0, 0)); var gold = Place(prefabs["Gold"], new Vector3(300, 0, 0));
            Verify("Green", green); Verify("Gold", gold);
            Physics.SyncTransforms();
            Walks(green);
            gold.SetActive(false); Shots("green", green); gold.SetActive(true);         // one tree in frame at a time
            green.SetActive(false); Shots("gold", gold); green.SetActive(true);
            Lineup(prefabs);
            GameScene(prefabs);
            File.WriteAllText(Path.Combine(Out, "unity-verify-report.txt"), string.Join("\n", Report) + $"\n\nUnity {Application.unityVersion}, colour space {PlayerSettings.colorSpace}; failed checks: {failed}; walking is a scripted CharacterController; the game-scene shots place the trees in Qingxi.unity without saving it\n");
            Debug.Log("XIANXIA_TREE_" + (failed == 0 ? "PASS" : "FAIL") + "\n" + string.Join("\n", Report));
            if (failed > 0 && Application.isBatchMode) EditorApplication.Exit(1);
        }

        // ------------------------------------------------------------------ install
        static void Install()
        {
            var dst = Path.Combine(Repo, "apps", "game", Dst); Directory.CreateDirectory(Path.Combine(dst, "Textures")); Directory.CreateDirectory(Path.Combine(dst, "Materials"));
            foreach (var f in Directory.GetFiles(Path.Combine(Src, "Textures"), "*.png")) File.Copy(f, Path.Combine(dst, "Textures", Path.GetFileName(f)), true);
            var fbx = $"{Id}_{info.version}.fbx"; File.Copy(Path.Combine(Src, fbx), Path.Combine(dst, fbx), true);      // only the current version
            AssetDatabase.Refresh();
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { Dst + "/Textures" }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid); var ti = (TextureImporter)AssetImporter.GetAtPath(path);
                bool normal = path.EndsWith("_Normal.png"), data = path.EndsWith("_MetallicSmoothness.png"), leaves = path.EndsWith("_Leaves_BaseColor.png");
                ti.textureType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default; ti.sRGBTexture = !normal && !data;
                ti.maxTextureSize = leaves ? 2048 : 1024; ti.mipmapEnabled = true; ti.wrapMode = leaves ? TextureWrapMode.Clamp : TextureWrapMode.Repeat;
                if (leaves) { ti.alphaSource = TextureImporterAlphaSource.FromInput; ti.alphaIsTransparency = true; ti.mipMapsPreserveCoverage = true; ti.alphaTestReferenceValue = .5f; }
                ti.SaveAndReimport();
            }
            var mi = (ModelImporter)AssetImporter.GetAtPath(Fbx);
            mi.bakeAxisConversion = true; mi.materialImportMode = ModelImporterMaterialImportMode.None;
            mi.importAnimation = false; mi.importCameras = false; mi.importLights = false; mi.addCollider = false;
            mi.importNormals = ModelImporterNormals.Import; mi.importTangents = ModelImporterTangents.CalculateMikk; mi.isReadable = true;
            mi.SaveAndReimport();
        }

        static Texture2D Tex(string f) => AssetDatabase.LoadAssetAtPath<Texture2D>($"{Dst}/Textures/{f}");
        static Color Hex(string h) { ColorUtility.TryParseHtmlString(h, out var c); return c; }

        static Material Mat(string name, Shader sh)
        {
            var path = $"{Dst}/Materials/{name}.mat"; var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null) { m = new Material(sh); AssetDatabase.CreateAsset(m, path); } else m.shader = sh;
            return m;
        }

        static readonly Dictionary<string, Material[]> mats = new Dictionary<string, Material[]>();
        static Material[] Materials(string look)
        {
            if (mats.TryGetValue(look, out var r)) return r;
            var bark = Mat("M_XT01_Bark", Shader.Find("YunJing/XianxiaTreeBark"));
            bark.SetTexture("_BaseMap", Tex("XT01_Bark_BaseColor.png")); bark.SetTexture("_BumpMap", Tex("XT01_Bark_Normal.png"));
            var L = look == "Green" ? info.looks.green : info.looks.gold; var sh = Shader.Find("YunJing/XianxiaTreeLeaves");
            var leaves = Mat($"M_XT01_Leaves_{look}", sh);
            leaves.SetTexture("_BaseMap", Tex("XT01_Leaves_BaseColor.png")); leaves.SetFloat("_Baked", 0); leaves.SetFloat("_Cutoff", .5f);
            leaves.SetColor("_DeepColor", Hex(L.deep)); leaves.SetColor("_MidColor", Hex(L.mid)); leaves.SetColor("_TipColor", Hex(L.tip));
            leaves.SetColor("_VariationA", Hex(L.var_a)); leaves.SetColor("_VariationB", Hex(L.var_b)); leaves.SetFloat("_VariationAmount", L.var_amount);
            leaves.SetFloat("_MidPoint", L.midpoint); leaves.SetFloat("_DetailMid", info.leaf_shader.mean_value); leaves.SetFloat("_Detail", info.leaf_shader.detail);
            leaves.SetFloat("_ValueStrength", info.leaf_shader.value); leaves.SetFloat("_GrazeMin", info.leaf_shader.graze_min); leaves.SetFloat("_GrazeMax", info.leaf_shader.graze_max);
            leaves.renderQueue = (int)RenderQueue.AlphaTest; leaves.doubleSidedGI = true;
            var imp = Mat($"M_XT01_Impostor_{look}", sh);
            imp.SetTexture("_BaseMap", Tex("XT01_Leaves_BaseColor.png")); imp.SetFloat("_Baked", 1); imp.SetFloat("_Cutoff", .5f);
            imp.SetTextureOffset("_BaseMap", new Vector2(look == "Gold" ? .5f : 0f, 0)); imp.renderQueue = (int)RenderQueue.AlphaTest;
            imp.SetFloat("_GrazeMin", info.leaf_shader.graze_min); imp.SetFloat("_GrazeMax", info.leaf_shader.graze_max);
            EditorUtility.SetDirty(bark); EditorUtility.SetDirty(leaves); EditorUtility.SetDirty(imp); AssetDatabase.SaveAssets();
            return mats[look] = new[] { bark, leaves, imp };
        }

        static GameObject BuildPrefab(string look)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Fbx));
            PrefabUtility.UnpackPrefabInstance(go, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            go.name = $"{Id}_{look}"; var m = Materials(look);
            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
            {
                if (r.name.EndsWith("_Collision")) { r.enabled = false; continue; }
                bool lod3 = r.name.EndsWith("_LOD3");
                r.sharedMaterials = lod3 ? new[] { m[2] } : new[] { m[0], m[1] };
                r.shadowCastingMode = lod3 ? ShadowCastingMode.Off : ShadowCastingMode.On; r.receiveShadows = !lod3;
            }
            foreach (var mf in go.GetComponentsInChildren<MeshFilter>(true).Where(x => x.name.EndsWith("_Collision")))
            {
                var mc = mf.gameObject.GetComponent<MeshCollider>(); if (mc == null) mc = mf.gameObject.AddComponent<MeshCollider>(); mc.sharedMesh = mf.sharedMesh; mc.convex = true;
            }
            var lg = go.GetComponent<LODGroup>(); if (lg == null) lg = go.AddComponent<LODGroup>();
            var lods = new LOD[4];
            for (int l = 0; l < 4; l++) lods[l] = new LOD(.5f / (l + 1), go.GetComponentsInChildren<Renderer>(true).Where(r => r.name.EndsWith("_LOD" + l)).ToArray());
            lg.SetLODs(lods); lg.RecalculateBounds();
            var sw = info.lod_switch_distance_m; float t = 2 * Mathf.Tan(20 * Mathf.Deg2Rad);
            for (int l = 0; l < 4; l++) lods[l].screenRelativeTransitionHeight = Mathf.Min(.98f - l * .01f, lg.size / (sw[l] * t) * QualitySettings.lodBias);
            lg.SetLODs(lods); lg.fadeMode = LODFadeMode.None;
            var path = $"{Dst}/{Id}_{look}.prefab";
            var prefab = PrefabUtility.SaveAsPrefabAsset(go, path); UnityEngine.Object.DestroyImmediate(go);
            Report.Add($"INFO prefab {path}");
            return prefab;
        }

        static GameObject Place(GameObject prefab, Vector3 pos)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab); go.transform.position = pos; return go;
        }

        // ------------------------------------------------------------------ checks
        static void Verify(string look, GameObject go)
        {
            var lg = go.GetComponent<LODGroup>(); var lods = lg.GetLODs();
            Check(lods.Length == 4 && lods.All(l => l.renderers.Length == 1), $"{look}: LODGroup LOD0-LOD3, one renderer each (size {lg.size:F1} m, transition heights {string.Join(" / ", lods.Select(x => x.screenRelativeTransitionHeight.ToString("F3")))} for {string.Join(" / ", info.lod_switch_distance_m)} m, LOD bias {QualitySettings.lodBias:F2})");
            for (int l = 0; l < 4; l++)
            {
                var r = lods[l].renderers[0]; var mesh = r.GetComponent<MeshFilter>().sharedMesh; int tris = mesh.triangles.Length / 3; var b = B(l);
                Check(tris == b.triangles && tris <= b.cap, $"{look}: LOD{l} {tris} triangles (model_info {b.triangles}, cap {b.cap})");
                int want = l == 3 ? 1 : 2;
                Check(r.sharedMaterials.Length == want && r.sharedMaterials.All(x => x != null), $"{look}: LOD{l} materials {string.Join(", ", r.sharedMaterials.Select(x => x ? x.name + " (" + x.shader.name + ")" : "null"))}");
                Check(mesh.colors.Length == mesh.vertexCount && mesh.vertexCount > 0, $"{look}: LOD{l} vertex colour on every vertex ({mesh.colors.Length}/{mesh.vertexCount})");
                if (l == 0)
                {
                    var c = mesh.colors; var vs = mesh.vertices; float trunkMax = 0, leafMin = 1, leafMax = 0, maskMin = 1, maskMax = 0;
                    foreach (int v in mesh.GetTriangles(0)) if (vs[v].y < 2f) trunkMax = Mathf.Max(trunkMax, c[v].r);
                    foreach (int v in mesh.GetTriangles(1)) { leafMin = Mathf.Min(leafMin, c[v].r); leafMax = Mathf.Max(leafMax, c[v].r); maskMin = Mathf.Min(maskMin, c[v].b); maskMax = Mathf.Max(maskMax, c[v].b); }
                    Check(trunkMax < .05f && leafMin >= .5f, $"{look}: wind weights: bark below 2 m <= {trunkMax:F2}, leaf cards {leafMin:F2}-{leafMax:F2}; light mask {maskMin:F2}-{maskMax:F2}");
                    var n = mesh.normals; int bad = n.Count(x => float.IsNaN(x.x) || x.sqrMagnitude < .5f);
                    Check(bad == 0, $"{look}: LOD0 normals all unit length ({bad} bad of {n.Length})");
                }
            }
            var b0 = lods[0].renderers[0].bounds; float h = b0.max.y - go.transform.position.y, dz = b0.min.y - go.transform.position.y;
            Check(Mathf.Abs(h - info.height_m) < .03f, $"{look}: height {h:F2} m (model_info {info.height_m:F2}), crown {b0.size.x:F1} x {b0.size.z:F1} m, roots to {dz:F2} m");
            var col = go.GetComponentsInChildren<MeshCollider>(true).FirstOrDefault(); var cr = col ? col.GetComponent<Renderer>() : null;
            Check(col != null && cr != null && !cr.enabled, $"{look}: trunk MeshCollider (convex) with its renderer hidden");
            var leafTex = (TextureImporter)AssetImporter.GetAtPath($"{Dst}/Textures/XT01_Leaves_BaseColor.png");
            Check(leafTex.mipMapsPreserveCoverage && Mathf.Abs(leafTex.alphaTestReferenceValue - .5f) < 1e-3, $"{look}: leaf atlas Preserve Coverage at 0.5, {leafTex.maxTextureSize} max");
        }

        static void Stroll(CharacterController cc, Vector3 dir, int n) { for (int f = 0; f < n; f++) cc.Move(dir * (1.4f / 60f) + Vector3.down * (9.8f / 60f)); }

        static void Walks(GameObject go)
        {
            var cap = info.collision_capsule; var o = go.transform.position; var trunk = o + new Vector3(cap.centre[0], 0, cap.centre[1]);
            var body = new GameObject("Walker_1.75m"); var cc = body.AddComponent<CharacterController>();
            cc.height = 1.75f; cc.radius = .25f; cc.center = new Vector3(0, .875f, 0); cc.stepOffset = .3f; cc.skinWidth = .02f;
            cc.transform.position = trunk + new Vector3(0, .02f, -6f); Physics.SyncTransforms(); Stroll(cc, Vector3.forward, 420);
            float gap = trunk.z - cc.transform.position.z;
            Check(gap > cap.radius + .15f && gap < cap.radius + .5f, $"walker heading at the trunk stops {gap:F2} m from the axis (collider radius {cap.radius:F2} m)");
            cc.transform.position = trunk + new Vector3(cap.radius + 1.5f, .02f, -6f); Physics.SyncTransforms(); Stroll(cc, Vector3.forward, 420);
            Check(cc.transform.position.z - trunk.z > 3f, $"walker 1.5 m beside the trunk goes on under the crown ({cc.transform.position.z - trunk.z:F2} m past)");
            UnityEngine.Object.DestroyImmediate(body);
        }

        // ------------------------------------------------------------------ shots
        static void Lighting()
        {
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(.62f, .74f, .9f); RenderSettings.ambientEquatorColor = new Color(.52f, .6f, .58f); RenderSettings.ambientGroundColor = new Color(.3f, .34f, .22f);
            var sun = new GameObject("Sun").AddComponent<Light>(); sun.type = LightType.Directional; sun.intensity = 1.25f;
            sun.color = new Color(1, .95f, .84f); sun.transform.rotation = Quaternion.Euler(40, -35, 0); sun.shadows = LightShadows.Soft;
            var cam = new GameObject("Main Camera", typeof(Camera)).GetComponent<Camera>(); cam.tag = "MainCamera"; cam.nearClipPlane = .05f; cam.farClipPlane = 1500;
            cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = new Color(.55f, .72f, .92f);
            cam.GetUniversalAdditionalCameraData().renderPostProcessing = false;
            RenderSettings.fog = true; RenderSettings.fogMode = FogMode.Linear; RenderSettings.fogColor = new Color(.7f, .8f, .9f); RenderSettings.fogStartDistance = 80; RenderSettings.fogEndDistance = 1000;
        }

        static void Shot(string file, Vector3 target, Vector3 eye, float fov = 40, int w = 1600, int h = 1000)
        {
            var cam = Camera.main; var rt = new RenderTexture(w, h, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            cam.transform.position = eye; cam.transform.LookAt(target); cam.fieldOfView = fov; cam.targetTexture = rt; cam.Render();
            RenderTexture.active = rt; var tex = new Texture2D(w, h, TextureFormat.RGB24, false); tex.ReadPixels(new Rect(0, 0, w, h), 0, 0); tex.Apply();
            File.WriteAllBytes(Path.Combine(Out, file + ".png"), tex.EncodeToPNG()); UnityEngine.Object.DestroyImmediate(tex);
            RenderTexture.active = null; cam.targetTexture = null; rt.Release(); Report.Add("SHOT " + file);
        }

        static int LodAt(GameObject go, float dist, float fov)
        {
            var lg = go.GetComponent<LODGroup>(); float rel = lg.size / (2 * dist * Mathf.Tan(fov * .5f * Mathf.Deg2Rad)) * QualitySettings.lodBias;
            var lods = lg.GetLODs(); for (int l = 0; l < lods.Length; l++) if (rel >= lods[l].screenRelativeTransitionHeight) return l;
            return -1;
        }

        static void Shots(string look, GameObject go)
        {
            var o = go.transform.position; float H = info.height_m; var c = o + Vector3.up * H * .5f; var lg = go.GetComponent<LODGroup>();
            Shot($"{Id}_{look}_three_quarter", c, o + new Vector3(22, 2.2f, -26), 42);
            foreach (var (name, az) in new[] { ("front", 0f), ("right", 90f), ("back", 180f), ("left", 270f) })
            {
                var d = Quaternion.Euler(0, -az, 0) * new Vector3(0, 0, -38); Shot($"{Id}_{look}_{name}", c, o + d + Vector3.up * 3f, 40);
            }
            Shot($"{Id}_{look}_under_crown_eye_1p7", o + new Vector3(0, H * .5f, 0), o + new Vector3(5, 1.7f, -8), 62);
            if (look == "green")
            {
                Shot($"{Id}_close_bark_roots", o + new Vector3(0, 1.2f, 0), o + new Vector3(2.5f, 1.6f, -5.5f), 45);
                Shot($"{Id}_close_crown_rim", o + new Vector3(-6, 13, -2), o + new Vector3(-4, 11, -14), 35);
                for (int l = 0; l < 4; l++) { lg.ForceLOD(l); Shot($"{Id}_LOD{l}", c, o + new Vector3(0, H * .45f, -36), 40); }
                lg.ForceLOD(-1);
                // wind: the same frame at sway 0 and at 10x the default sway (bark and leaves alike). The trunk must stay put, twigs and
                // their leaf cards must move together (no leaves left floating off their twigs, no torn bark)
                var mm = Materials("Green"); float ws = mm[0].GetFloat("_WindStrength");
                foreach (var (tag, k) in new[] { ("wind_off", 0f), ("wind_10x", 10f) })
                {
                    foreach (var m in mm) m.SetFloat("_WindStrength", ws * k);
                    Shot($"{Id}_{tag}", c, o + new Vector3(0, H * .45f, -36), 40);
                    Shot($"{Id}_{tag}_close", o + new Vector3(-5, 10, 0), o + new Vector3(-3, 8, -12), 45);
                }
                foreach (var m in mm) m.SetFloat("_WindStrength", ws); EditorUtility.SetDirty(mm[1]); AssetDatabase.SaveAssets();
                Report.Add($"INFO wind shots at sway 0 and {ws * 10:F2} m (10x the default {ws:F2} m); materials put back to {ws:F2}");
                foreach (float dd in new[] { 50f, 100f, 250f })
                {
                    var eye = o + new Vector3(dd * .7f, 1.7f, -dd * .71f); int k = LodAt(go, Vector3.Distance(eye, c), 40);
                    Shot($"{Id}_far_{dd:F0}m", c, eye, 40); Report.Add($"INFO at {dd:F0} m the LODGroup shows LOD{k}");
                }
            }
        }

        static void Lineup(Dictionary<string, GameObject> prefabs)
        {
            var o = new Vector3(-400, 0, -400);
            var g = Place(prefabs["Green"], o + new Vector3(-14, 0, 0)); var y = Place(prefabs["Gold"], o + new Vector3(14, 0, 0));
            var vl = Path.Combine(Repo, "art", "exports", "village-houses-b", "VL02_MovedInHouse"); GameObject house = null;
            if (File.Exists(Path.Combine(vl, "VL02_MovedInHouse_v001.fbx")))
            {
                var d = Path.Combine(Repo, "apps", "game", "Assets", "YunJing", "Generated", "XianxiaTreeCheck"); Directory.CreateDirectory(d);
                File.Copy(Path.Combine(vl, "VL02_MovedInHouse_v001.fbx"), Path.Combine(d, "VL02_MovedInHouse_v001.fbx"), true); AssetDatabase.Refresh();
                house = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/YunJing/Generated/XianxiaTreeCheck/VL02_MovedInHouse_v001.fbx"));
                house.transform.position = o + new Vector3(0, 0, 12);
                var hm = new Material(Shader.Find("Universal Render Pipeline/Lit")); hm.SetColor("_BaseColor", new Color(.72f, .66f, .58f));
                foreach (var r in house.GetComponentsInChildren<Renderer>(true)) { if (r.name.Contains("Collision") || r.name.Contains("_LOD1") || r.name.Contains("_LOD2")) r.enabled = false; else r.sharedMaterials = r.sharedMaterials.Select(_ => hm).ToArray(); }
            }
            var man = GameObject.CreatePrimitive(PrimitiveType.Capsule); man.name = "Figure_1.75m"; man.transform.localScale = new Vector3(.5f, .875f, .5f);
            man.transform.position = o + new Vector3(-3, .875f, -6); var mm = new Material(Shader.Find("Universal Render Pipeline/Lit")); mm.SetColor("_BaseColor", new Color(.75f, .3f, .12f)); man.GetComponent<Renderer>().sharedMaterial = mm;
            UnityEngine.Object.DestroyImmediate(man.GetComponent<Collider>());
            Shot($"{Id}_green_gold_with_VL02_and_1p75m", o + new Vector3(0, 7, 0), o + new Vector3(0, 3, -52), 42, 1920, 1000);
            Shot($"{Id}_green_gold_far_120m", o + new Vector3(0, 7, 0), o + new Vector3(0, 3, -120), 30, 1920, 1000);
            UnityEngine.Object.DestroyImmediate(g); UnityEngine.Object.DestroyImmediate(y); UnityEngine.Object.DestroyImmediate(man); if (house) UnityEngine.Object.DestroyImmediate(house);
        }

        // both trees in the game scene for a look in its own light (the scene is opened and not saved)
        static void GameScene(Dictionary<string, GameObject> prefabs)
        {
            const string scene = "Assets/YunJing/Generated/Qingxi.unity";
            if (!File.Exists(Path.Combine(Repo, "apps", "game", scene))) { Report.Add("INFO game scene not generated here: no in-scene shots"); return; }
            EditorSceneManager.OpenScene(scene, OpenSceneMode.Single);
            Vector3 spawn = Vector3.zero; Vector3 fwd = Vector3.forward;
            var p = GameObject.FindGameObjectsWithTag("Player").FirstOrDefault() ?? UnityEngine.Object.FindObjectsByType<Transform>(FindObjectsSortMode.None).FirstOrDefault(t => t.name.Contains("Spawn") || t.name.Contains("Cultivator"))?.gameObject;
            if (p) { spawn = p.transform.position; fwd = Vector3.ProjectOnPlane(p.transform.forward, Vector3.up).normalized; if (fwd.sqrMagnitude < .1f) fwd = Vector3.forward; }
            Report.Add($"INFO game scene spawn {(p ? p.name : "none")} at {spawn}");
            Vector3 gp, yp, eye, near, nearAt;
            var court = GameObject.Find("Courtyard ground");
            if (court != null && court.GetComponent<Renderer>() != null)
            {
                // Qingxi is a 30 x 26 m walled courtyard greybox with nothing round it. The gold tree (meant for sect courtyards) goes in
                // the north-west corner, its crown over the wall; the green one stands outside beyond the north-east corner on a
                // temporary ground plane in the courtyard's own grass material (the scene is not saved).
                var b = court.GetComponent<Renderer>().bounds; float top = b.max.y;
                var ext = GameObject.CreatePrimitive(PrimitiveType.Cube); ext.name = "XT01 shot ground (temporary)";
                ext.transform.position = new Vector3(b.center.x, top - .32f, b.center.z); ext.transform.localScale = new Vector3(400, .6f, 400);
                ext.GetComponent<Renderer>().sharedMaterial = court.GetComponent<Renderer>().sharedMaterial;
                yp = new Vector3(b.min.x + 6.5f, top, b.max.z - 6.5f); gp = new Vector3(b.max.x + 5f, top, b.max.z + 11f);
                eye = new Vector3(b.center.x + 5f, top + 1.7f, b.min.z + 1.5f); near = yp + new Vector3(6.5f, 1.7f, -9.5f); nearAt = yp + Vector3.up * 5.5f;
                Report.Add($"INFO game scene: gold tree inside the courtyard at {yp}, green tree outside the north-east corner at {gp}, temporary ground outside the walls");
            }
            else
            {
                gp = new Vector3(-9, 0, 30); yp = new Vector3(13, 0, 36); eye = new Vector3(0, 2.2f, -4); near = gp + new Vector3(6, 1.8f, -20); nearAt = gp + Vector3.up * 6;
                Report.Add("INFO game scene: no Courtyard ground, fixed offsets");
            }
            var g = Place(prefabs["Green"], gp); var y = Place(prefabs["Gold"], yp);
            g.transform.rotation = Quaternion.Euler(0, 40, 0); y.transform.rotation = Quaternion.Euler(0, 160, 0);
            Physics.SyncTransforms();
            var cam = Camera.main; bool made = false;
            if (cam == null) { cam = new GameObject("ShotCam", typeof(Camera)).GetComponent<Camera>(); cam.tag = "MainCamera"; made = true; }
            cam.farClipPlane = Mathf.Max(cam.farClipPlane, 1500);
            Shot($"{Id}_in_game_scene_Qingxi", (gp + yp) * .5f + Vector3.up * 6, eye, 64, 1920, 1080);
            Shot($"{Id}_in_game_scene_Qingxi_near", nearAt, near, 64, 1920, 1080);
            if (made) UnityEngine.Object.DestroyImmediate(cam.gameObject);
        }
    }
}
