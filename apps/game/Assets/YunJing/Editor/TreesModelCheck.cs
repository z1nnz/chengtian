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
    // Work pack 2026-11-11 B-64h (every tree in the world rebuilt): the TR species in art/exports/trees-b, three variants each.
    // Imports each variant FBX with the species' shared textures, builds the materials (bark: URP Lit; leaves: URP Lit, alpha clip 0.5,
    // both faces, BaseColor imported with Mip Maps Preserve Coverage), sets the LODGroup transitions from model_info, and checks:
    // LOD count and triangles against model_info and the pack caps, two materials on LOD0-2 and one on LOD3, the Wind vertex colour,
    // height, the trunk collider (a 1.75 m CharacterController walked at the trunk stops; one walking past 1.5 m to the side goes on:
    // the crown does not block). Shots: three-quarter at eye height, every LOD forced, 50 m and 100 m with the LODGroup choosing,
    // the variants beside VL02 and a 1.75 m capsule. Writes artifacts/trees-b-unity/. Not placed in any game scene.
    // Run: -executeMethod YunJing.Editor.TreesModelCheck.Run [-trees TR01,TR02]
    public static class TreesModelCheck
    {
        const string Root = "Assets/YunJing/Generated/TreesB";
        static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ".."));
        static string Exports => Path.Combine(Repo, "art", "exports", "trees-b");
        static string Out => Path.Combine(Repo, "artifacts", "trees-b-unity");
        static readonly List<string> Report = new List<string>();
        static int failed;

        [Serializable] class Budget { public int triangles, objects, materials, cap, wood_triangles, leaf_cards; }
        [Serializable] class BudgetPerLod { public Budget LOD0, LOD1, LOD2, LOD3; }
        [Serializable] class Capsule { public float radius, height; public float[] centre; }
        [Serializable] class ModelInfo { public string asset, version, minTier, species; public float height_m; public float[] dimensions_m, bounds_min_m, bounds_max_m, lod_switch_distance_m; public string[] materials; public BudgetPerLod budget_per_lod; public Capsule collision_capsule; }

        static readonly Dictionary<string, ModelInfo> infos = new Dictionary<string, ModelInfo>();
        static ModelInfo Info(string id)
        {
            if (!infos.TryGetValue(id, out var i)) infos[id] = i = JsonUtility.FromJson<ModelInfo>(File.ReadAllText(Path.Combine(Exports, id, "model_info.json")));
            return i;
        }
        static string Sp(string id) => id.Substring(0, 4);
        static string Fbx(string id) => $"{Root}/{id}/{id}_{Info(id).version}.fbx";
        static Budget B(string id, int l) => l == 0 ? Info(id).budget_per_lod.LOD0 : l == 1 ? Info(id).budget_per_lod.LOD1 : l == 2 ? Info(id).budget_per_lod.LOD2 : Info(id).budget_per_lod.LOD3;
        static void Check(bool ok, string what) { Report.Add((ok ? "PASS " : "FAIL ") + what); if (!ok) failed++; }

        static void UsePipeline()
        {
            var pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>("Assets/YunJing/Generated/URP.asset");
            if (pipeline == null) { ProjectBuilder.Generate(); pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>("Assets/YunJing/Generated/URP.asset"); }
            if (GraphicsSettings.defaultRenderPipeline != pipeline) GraphicsSettings.defaultRenderPipeline = pipeline;
            if (QualitySettings.renderPipeline != pipeline) QualitySettings.renderPipeline = pipeline;
            pipeline.shadowDistance = 120;
        }

        static string[] WantedSpecies()
        {
            var args = Environment.GetCommandLineArgs(); int k = Array.IndexOf(args, "-trees");
            if (k >= 0 && k + 1 < args.Length) return args[k + 1].Split(',');
            return Directory.GetDirectories(Exports, "TR??_Shared").Select(d => Path.GetFileName(d).Substring(0, 4)).ToArray();
        }

        public static void Run()
        {
            Report.Clear(); failed = 0; infos.Clear();
            UsePipeline();
            if (Directory.Exists(Out)) Directory.Delete(Out, true);
            Directory.CreateDirectory(Out);
            var species = WantedSpecies();
            var ids = species.SelectMany(sp => Directory.GetDirectories(Exports, sp + "_?_*").Select(Path.GetFileName)).Where(i => File.Exists(Path.Combine(Exports, i, "model_info.json"))).OrderBy(i => i).ToArray();
            Report.Add("INFO species " + string.Join(", ", species) + "; variants " + string.Join(", ", ids));
            foreach (var sp in species) CopyDir(Path.Combine(Exports, sp + "_Shared", "Textures"), $"{Root}/{sp}_Shared/Textures");
            foreach (var id in ids) CopyDir(Path.Combine(Exports, id), $"{Root}/{id}", "*.fbx");
            var vl = Path.Combine(Repo, "art", "exports", "village-houses-b", "VL02_MovedInHouse");
            CopyDir(vl, $"{Root}/VL02_MovedInHouse", "*.fbx"); CopyDir(Path.Combine(vl, "Textures"), $"{Root}/VL02_MovedInHouse/Textures");
            AssetDatabase.Refresh();
            foreach (var sp in species) ConfigureTextures($"{Root}/{sp}_Shared/Textures");
            ConfigureTextures($"{Root}/VL02_MovedInHouse/Textures");
            foreach (var id in ids) ConfigureModel(Fbx(id));
            ConfigureModel($"{Root}/VL02_MovedInHouse/VL02_MovedInHouse_v001.fbx");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Lighting();
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane); ground.name = "Placeholder_Ground"; ground.transform.localScale = new Vector3(120, 1, 120);
            var gm = new Material(Shader.Find("Universal Render Pipeline/Lit")); gm.SetColor("_BaseColor", new Color(.34f, .36f, .24f)); gm.SetFloat("_Smoothness", .05f);
            ground.GetComponent<Renderer>().sharedMaterial = gm;
            var placed = new Dictionary<string, GameObject>();
            for (int i = 0; i < ids.Length; i++)
            {
                var go = Place(ids[i], new Vector3(400 + i * 40, 0, 400)); placed[ids[i]] = go; Verify(ids[i], go);
            }
            Physics.SyncTransforms();
            foreach (var id in ids) Walks(id, placed[id]);
            foreach (var id in ids) Shots(id, placed[id]);
            foreach (var sp in species) Lineup(sp, ids.Where(i => i.StartsWith(sp)).ToArray());
            File.WriteAllText(Path.Combine(Out, "unity-verify-report.txt"), string.Join("\n", Report) + $"\n\nUnity {Application.unityVersion}; failed checks: {failed}; walking is a scripted CharacterController, not a person; screenshots are editor renders with a placeholder ground, not the game scene\n");
            Debug.Log("TREES_B_" + (failed == 0 ? "PASS" : "FAIL") + "\n" + string.Join("\n", Report));
            if (failed > 0 && Application.isBatchMode) EditorApplication.Exit(1);
        }

        static void CopyDir(string src, string dstAsset, string pattern = "*.png")
        {
            var dst = Path.Combine(Repo, "apps", "game", dstAsset); Directory.CreateDirectory(dst);
            foreach (var f in Directory.GetFiles(src, pattern)) File.Copy(f, Path.Combine(dst, Path.GetFileName(f)), true);
        }

        static void ConfigureTextures(string folder)
        {
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { folder }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid); var ti = AssetImporter.GetAtPath(path) as TextureImporter; if (ti == null) continue;
                bool normal = path.EndsWith("_Normal.png"); bool data = path.EndsWith("_MetallicSmoothness.png") || path.EndsWith("_Roughness.png") || path.EndsWith("_Metallic.png");
                ti.textureType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default; ti.sRGBTexture = !normal && !data; ti.maxTextureSize = 2048; ti.mipmapEnabled = true;
                if (path.EndsWith("_Leaves_BaseColor.png")) { ti.alphaSource = TextureImporterAlphaSource.FromInput; ti.alphaIsTransparency = true; ti.mipMapsPreserveCoverage = true; ti.alphaTestReferenceValue = .5f; }
                ti.SaveAndReimport();
            }
        }

        static void ConfigureModel(string path)
        {
            var importer = AssetImporter.GetAtPath(path) as ModelImporter;
            if (importer == null) throw new FileNotFoundException("FBX not imported", path);
            importer.bakeAxisConversion = true; importer.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription;
            importer.importAnimation = false; importer.importCameras = false; importer.importLights = false; importer.addCollider = false;
            importer.importNormals = ModelImporterNormals.Import; importer.importTangents = ModelImporterTangents.CalculateMikk; importer.isReadable = true;
            importer.SaveAndReimport();
        }

        static Texture2D Tex(string folder, string file) => AssetDatabase.LoadAssetAtPath<Texture2D>($"{folder}/{file}");

        static readonly Dictionary<string, Material> mats = new Dictionary<string, Material>();
        static Material Mat(string folder, string prefix, bool leaves)
        {
            var key = folder + prefix; if (mats.TryGetValue(key, out var m)) return m;
            var path = $"{folder}/../M_{prefix}.mat";
            m = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            m.SetTexture("_BaseMap", Tex(folder, prefix + "_BaseColor.png")); m.SetColor("_BaseColor", Color.white);
            m.SetTexture("_BumpMap", Tex(folder, prefix + "_Normal.png")); m.EnableKeyword("_NORMALMAP");
            m.SetTexture("_MetallicGlossMap", Tex(folder, prefix + "_MetallicSmoothness.png")); m.EnableKeyword("_METALLICSPECGLOSSMAP"); m.SetFloat("_Smoothness", 1);
            if (leaves)
            {
                m.SetFloat("_AlphaClip", 1); m.SetFloat("_Cutoff", .5f); m.EnableKeyword("_ALPHATEST_ON");
                m.SetFloat("_Cull", (float)CullMode.Off); m.doubleSidedGI = true;
                m.SetOverrideTag("RenderType", "TransparentCutout"); m.renderQueue = (int)RenderQueue.AlphaTest;
                m.SetFloat("_BumpScale", .6f);
            }
            AssetDatabase.CreateAsset(m, AssetDatabase.GenerateUniqueAssetPath(path)); mats[key] = m; return m;
        }

        static GameObject Place(string id, Vector3 pos)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Fbx(id)));
            PrefabUtility.UnpackPrefabInstance(go, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            go.transform.position = pos;
            var tex = $"{Root}/{Sp(id)}_Shared/Textures";
            var bark = Mat(tex, Sp(id) + "_Bark", false); var leaves = Mat(tex, Sp(id) + "_Leaves", true);
            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
            {
                if (r.name.EndsWith("_Collision")) { r.enabled = false; continue; }
                r.sharedMaterials = r.sharedMaterials.Select(x => x != null && x.name.Contains("Bark") ? bark : leaves).ToArray();
                // LOD3 is two crossed impostor cards: they would shade each other, so no shadows (README: LOD3 shadows off)
                bool card = r.name.EndsWith("_LOD3");
                r.shadowCastingMode = card ? ShadowCastingMode.Off : ShadowCastingMode.On;
                r.receiveShadows = !card;
            }
            foreach (var mf in go.GetComponentsInChildren<MeshFilter>(true).Where(m => m.name.EndsWith("_Collision")))
                mf.gameObject.AddComponent<MeshCollider>().sharedMesh = mf.sharedMesh;
            var lg = go.GetComponent<LODGroup>(); if (lg == null) lg = go.AddComponent<LODGroup>();
            var lods = new LOD[4];
            for (int l = 0; l < 4; l++) lods[l] = new LOD(.5f / (l + 1), go.GetComponentsInChildren<Renderer>(true).Where(r => r.name.EndsWith("_LOD" + l)).ToArray());
            lg.SetLODs(lods); lg.RecalculateBounds();
            // transition heights from the suggested switch distances (model_info), this group's size, a 40 deg vertical FOV and the project LOD bias
            var sw = Info(id).lod_switch_distance_m; float t = 2 * Mathf.Tan(20 * Mathf.Deg2Rad);
            for (int l = 0; l < 4; l++) lods[l].screenRelativeTransitionHeight = Mathf.Min(.98f - l * .01f, lg.size / (sw[l] * t) * QualitySettings.lodBias);
            lg.SetLODs(lods);
            return go;
        }

        static GameObject PlaceHouse(Vector3 pos)
        {
            var path = $"{Root}/VL02_MovedInHouse/VL02_MovedInHouse_v001.fbx";
            var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(path));
            PrefabUtility.UnpackPrefabInstance(go, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction); go.transform.position = pos;
            var folder = $"{Root}/VL02_MovedInHouse/Textures";
            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
            {
                if (r.name.Contains("Collision") || r.name.Contains("_LOD1") || r.name.Contains("_LOD2")) { r.enabled = false; continue; }
                r.sharedMaterials = r.sharedMaterials.Select(x =>
                {
                    var n = x == null ? "" : x.name;
                    string prefix = n.Contains("RoofTiles") ? "VL_RoofTiles" : n.Contains("Stone") ? "VL02_MovedInHouse_Stone" : n.Contains("Wood") ? "VL02_MovedInHouse_Wood" : "VL02_MovedInHouse";
                    return Mat(folder, prefix, false);
                }).ToArray();
            }
            return go;
        }

        static void Verify(string id, GameObject go)
        {
            var info = Info(id);
            var lg = go.GetComponent<LODGroup>(); var lods = lg.GetLODs();
            Check(lods.Length == 4 && lods.All(l => l.renderers.Length == 1), $"{id}: LODGroup with LOD0-LOD3, one renderer each (size {lg.size:F1} m, transition heights {string.Join(" / ", lods.Select(x => x.screenRelativeTransitionHeight.ToString("F3")))} for {string.Join(" / ", Info(id).lod_switch_distance_m)} m at LOD bias {QualitySettings.lodBias:F1})");
            for (int l = 0; l < 4; l++)
            {
                var r = lods[l].renderers.FirstOrDefault(); var mf = r ? r.GetComponent<MeshFilter>() : null; var mesh = mf ? mf.sharedMesh : null;
                int tris = mesh ? mesh.triangles.Length / 3 : -1; var b = B(id, l);
                Check(mesh != null && tris == b.triangles && tris <= b.cap, $"{id}: LOD{l} {tris} triangles (model_info {b.triangles}, cap {b.cap})");
                int want = l == 3 ? 1 : 2;
                Check(r != null && r.sharedMaterials.Length == want, $"{id}: LOD{l} {(r ? r.sharedMaterials.Length : 0)} material(s), want {want} ({string.Join(", ", r ? r.sharedMaterials.Select(m => m.name) : new string[0])})");
                Check(mesh != null && mesh.colors.Length == mesh.vertexCount && mesh.colors.Length > 0, $"{id}: LOD{l} has the Wind vertex colour on every vertex ({(mesh ? mesh.colors.Length : 0)}/{(mesh ? mesh.vertexCount : 0)})");
                if (l == 0 && mesh != null)
                {
                    var c = mesh.colors; var vs = mesh.vertices; float trunkMax = 0, leafMin = 1;
                    var sub0 = new HashSet<int>(mesh.GetTriangles(0)); var sub1 = new HashSet<int>(mesh.GetTriangles(1));
                    foreach (int v in sub0) if (vs[v].y < 2f) trunkMax = Mathf.Max(trunkMax, c[v].r);
                    foreach (int v in sub1) leafMin = Mathf.Min(leafMin, c[v].r);
                    Check(trunkMax < .05f && leafMin >= .5f, $"{id}: wind weights: bark below 2 m <= {trunkMax:F2} (trunk 0), leaf cards >= {leafMin:F2}");
                }
            }
            var b0 = lods[0].renderers[0].bounds;
            float h = b0.max.y - go.transform.position.y, dz = b0.min.y - go.transform.position.y;
            Check(Mathf.Abs(h - info.height_m) < .02f, $"{id}: height {h:F2} m (model_info {info.height_m:F2} m), roots down to {dz:F2} m");
            var col = go.GetComponentsInChildren<MeshCollider>(true).FirstOrDefault(c => c.name.EndsWith("_Collision"));
            var cr = go.GetComponentsInChildren<Renderer>(true).FirstOrDefault(r => r.name.EndsWith("_Collision"));
            Check(col != null && cr != null && !cr.enabled, $"{id}: {id}_Collision is a MeshCollider with its renderer hidden");
            var leafTex = AssetImporter.GetAtPath($"{Root}/{Sp(id)}_Shared/Textures/{Sp(id)}_Leaves_BaseColor.png") as TextureImporter;
            Check(leafTex != null && leafTex.mipMapsPreserveCoverage && Mathf.Abs(leafTex.alphaTestReferenceValue - .5f) < 1e-3, $"{id}: leaves BaseColor imported with Mip Maps Preserve Coverage at 0.5");
        }

        static CharacterController Walker()
        {
            var body = new GameObject("Walker_1.75m"); var cc = body.AddComponent<CharacterController>();
            cc.height = 1.75f; cc.radius = .25f; cc.center = new Vector3(0, .875f, 0); cc.stepOffset = .3f; cc.slopeLimit = 45; cc.skinWidth = .02f;
            return cc;
        }

        static void Stroll(CharacterController cc, Vector3 dir, int n)
        {
            for (int f = 0; f < n; f++) cc.Move(dir * (1.4f / 60f) + Vector3.down * (9.8f / 60f));
        }

        // Unity (x, up, z) = Blender (x, z, y)
        static void Walks(string id, GameObject go)
        {
            var cap = Info(id).collision_capsule; var o = go.transform.position;
            var trunk = o + new Vector3(cap.centre[0], 0, cap.centre[1]);
            var cc = Walker();
            cc.transform.position = trunk + new Vector3(0, .02f, -4f); Physics.SyncTransforms();
            Stroll(cc, Vector3.forward, 360);
            float gap = trunk.z - cc.transform.position.z;
            Check(gap > cap.radius + .2f && gap < cap.radius + .45f, $"{id}: a walker heading at the trunk stops at it ({gap:F2} m from the trunk axis, trunk collider radius {cap.radius:F2} m)");
            cc.transform.position = trunk + new Vector3(cap.radius + 1.5f, .02f, -4f); Physics.SyncTransforms();
            Stroll(cc, Vector3.forward, 360);
            float past = cc.transform.position.z - trunk.z;
            Check(past > 3f, $"{id}: a walker passing 1.5 m beside the trunk under the crown goes on ({past:F2} m past it): the crown does not block");
            UnityEngine.Object.DestroyImmediate(cc.gameObject);
        }

        static void Lighting()
        {
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(.6f, .68f, .74f); RenderSettings.ambientEquatorColor = new Color(.46f, .47f, .42f); RenderSettings.ambientGroundColor = new Color(.22f, .2f, .16f);
            var sun = new GameObject("Sun").AddComponent<Light>(); sun.type = LightType.Directional; sun.intensity = 1.35f;
            sun.color = new Color(1, .93f, .8f); sun.transform.rotation = Quaternion.Euler(36, -40, 0); sun.shadows = LightShadows.Soft;
            var cam = new GameObject("Main Camera", typeof(Camera)).GetComponent<Camera>(); cam.tag = "MainCamera"; cam.nearClipPlane = .05f; cam.farClipPlane = 1500;
            cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = new Color(.72f, .8f, .84f);
            cam.GetUniversalAdditionalCameraData().renderPostProcessing = false;
            RenderSettings.fog = true; RenderSettings.fogMode = FogMode.Linear; RenderSettings.fogColor = new Color(.74f, .8f, .82f); RenderSettings.fogStartDistance = 60; RenderSettings.fogEndDistance = 900;
        }

        static void Shot(string file, Vector3 target, Vector3 eye, float fov = 40, int w = 1600, int h = 900)
        {
            var cam = Camera.main; var rt = new RenderTexture(w, h, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            cam.transform.position = eye; cam.transform.LookAt(target); cam.fieldOfView = fov; cam.targetTexture = rt; cam.Render();
            RenderTexture.active = rt; var tex = new Texture2D(w, h, TextureFormat.RGB24, false); tex.ReadPixels(new Rect(0, 0, w, h), 0, 0); tex.Apply();
            File.WriteAllBytes(Path.Combine(Out, file + ".png"), tex.EncodeToPNG()); UnityEngine.Object.DestroyImmediate(tex);
            RenderTexture.active = null; cam.targetTexture = null; rt.Release(); Report.Add("SHOT " + file);
        }

        static int LodAt(GameObject go, float dist, float fov)
        {
            var lg = go.GetComponent<LODGroup>(); float size = lg.size * Mathf.Max(go.transform.lossyScale.y, .0001f);
            float rel = size / (2 * dist * Mathf.Tan(fov * .5f * Mathf.Deg2Rad)) * QualitySettings.lodBias;
            var lods = lg.GetLODs(); for (int l = 0; l < lods.Length; l++) if (rel >= lods[l].screenRelativeTransitionHeight) return l;
            return -1;
        }

        static void Shots(string id, GameObject go)
        {
            var o = go.transform.position; float H = Info(id).height_m; var lg = go.GetComponent<LODGroup>();
            var c = o + Vector3.up * H * .5f;
            Shot($"{id}_three_quarter", c, o + new Vector3(15, 1.7f, -17), 45);
            Shot($"{id}_under_crown_eye_1p7", o + new Vector3(0, H * .55f, 0), o + new Vector3(5, 1.7f, -6), 60);
            Shot($"{id}_front", c, o + new Vector3(0, H * .45f, -26), 40);
            for (int l = 0; l < 4; l++) { lg.ForceLOD(l); Shot($"{id}_LOD{l}", c, o + new Vector3(0, H * .45f, -26), 40); }
            lg.ForceLOD(-1);
            foreach (float d in new[] { 50f, 100f })
            {
                var eye = o + new Vector3(d * .7f, 1.7f, -d * .71f);
                int k = LodAt(go, Vector3.Distance(eye, c), 40);
                Shot($"{id}_far_{d:F0}m", c, eye, 40);
                Report.Add($"INFO {id}: at {d:F0} m the LODGroup shows LOD{k} (LOD bias {QualitySettings.lodBias:F2})");
            }
        }

        static void Lineup(string sp, string[] ids)
        {
            var o = new Vector3(-400, 0, -400); var row = new List<GameObject>();
            for (int i = 0; i < ids.Length; i++) row.Add(Place(ids[i], o + new Vector3((i - (ids.Length - 1) * .5f) * 13, 0, 0)));
            var house = PlaceHouse(o + new Vector3(-28, 0, 2));
            var man = GameObject.CreatePrimitive(PrimitiveType.Capsule); man.name = "Figure_1.75m"; man.transform.localScale = new Vector3(.5f, .875f, .5f);
            man.transform.position = o + new Vector3(-20, .875f, -5); var mm = new Material(Shader.Find("Universal Render Pipeline/Lit")); mm.SetColor("_BaseColor", new Color(.75f, .3f, .12f)); man.GetComponent<Renderer>().sharedMaterial = mm;
            UnityEngine.Object.DestroyImmediate(man.GetComponent<Collider>());
            Shot($"{sp}_lineup_with_VL02_and_1p75m", o + new Vector3(-6, 6, 0), o + new Vector3(-6, 3.5f, -46), 40, 1920, 900);
            Shot($"{sp}_lineup_far_100m", o + new Vector3(-6, 6, 0), o + new Vector3(-6, 3f, -104), 40, 1920, 900);
            foreach (var g in row) UnityEngine.Object.DestroyImmediate(g); UnityEngine.Object.DestroyImmediate(house); UnityEngine.Object.DestroyImmediate(man);
        }
    }
}
