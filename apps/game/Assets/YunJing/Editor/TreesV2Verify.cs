using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace YunJing.Editor
{
    // Unity check of the tree redo v2 package A (art/exports/trees-v2-a, Johnnnny0823), starting with the TR06 weeping willow sample (A/B/C).
    // Imports every tree FBX, the bark textures and the far-card textures, builds preview materials (bark: URP Lit; leaves: URP
    // Particles/Simple Lit, because the leaf colour lives in the vertex colours; far card: URP Lit alpha clip), adds a 4-level LODGroup
    // and the trunk MeshCollider, compares each tree with its model_info.json (size, ground, LOD triangles, materials, collision) and
    // checks the vertex data the package asks for (UV2.x wind weight: trunk base 0, leaves high; leaf vertex colour with occlusion in A).
    // Needs a graphics device (no -nographics):
    //   Unity -batchmode -quit -projectPath apps/game -executeMethod YunJing.Editor.TreesV2Verify.Run -logFile <log>
    // Output: art/previews/trees-v2-a/unity/*.png and report.txt; the run fails when a check fails.
    public static class TreesV2Verify
    {
        const string Models = "Assets/YunJing/Models/TreesV2";   // copied from art/exports, gitignored
        const string Pkg = "trees-v2-a";
        static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ".."));
        static string Exports => Path.Combine(Repo, "art/exports", Pkg);
        static string Out => Path.Combine(Repo, "art/previews", Pkg, "unity");
        static readonly List<string> Report = new List<string>();
        static int failures;
        static readonly Dictionary<string, Material> Mats = new Dictionary<string, Material>();
        static readonly float[] Cuts = { .35f, .12f, .03f, .008f };   // LOD0 -> 1 at ~25 m, 1 -> 2 at ~70 m, 2 -> 3 at ~280 m for a 10 m tree (60 deg fov)

        [Serializable] class Lod { public int lod, triangles; public string[] materials; }
        [Serializable] class Info { public string id, collision; public float[] dimensions_m, bounds_min_m; public Lod[] lods; public string[] materials; }

        static string[] Ids => Directory.GetFiles(Exports, "*.fbx").Select(Path.GetFileNameWithoutExtension).OrderBy(s => s).ToArray();

        public static void Run()
        {
            Report.Clear(); failures = 0; Directory.CreateDirectory(Out);
            Import();
            QingxiUrpUpgrade.EnsurePipeline();
            Materials();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            Report.Add($"Unity {Application.unityVersion}, pipeline {GraphicsSettings.currentRenderPipeline?.name ?? "built-in"}");
            Report.Add("INFO axis: Blender +X -> Unity +X (the water side), Blender +Y -> Unity +Z, Blender +Z -> Unity +Y");
            foreach (var id in Ids) Inspect(id, JsonUtility.FromJson<Info>(File.ReadAllText(Path.Combine(Exports, $"{id}.model_info.json"))));
            Shots();
            File.WriteAllLines(Path.Combine(Out, "report.txt"), Report);
            foreach (var line in Report) Debug.Log("TREESV2 " + line);
            if (failures > 0) throw new Exception($"TREESV2_VERIFY {failures} check(s) failed, see {Out}/report.txt");
            Debug.Log($"TREESV2_VERIFY_DONE all checks passed, output {Out}");
        }

        static void Check(bool ok, string line) { Report.Add((ok ? "PASS " : "FAIL ") + line); if (!ok) failures++; }

        // ------------------------------------------------------------------ import
        static void Import()
        {
            Copy(Exports, Path.Combine(Repo, "apps/game", Models), "*.fbx");
            Copy(Path.Combine(Repo, "art/textures", Pkg), Path.Combine(Repo, "apps/game", Models, "Textures"), "T_*.png");
            AssetDatabase.Refresh();
            foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { Models }))
            {
                var importer = (ModelImporter)AssetImporter.GetAtPath(AssetDatabase.GUIDToAssetPath(guid));
                if (importer.bakeAxisConversion && importer.materialImportMode == ModelImporterMaterialImportMode.ImportStandard && importer.materialLocation == ModelImporterMaterialLocation.InPrefab) continue;
                importer.bakeAxisConversion = true; importer.importCameras = false; importer.importLights = false; importer.addCollider = false;
                importer.importAnimation = false; importer.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;
                importer.materialLocation = ModelImporterMaterialLocation.InPrefab; importer.importTangents = ModelImporterTangents.CalculateMikk;
                importer.SaveAndReimport();
            }
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { Models }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var ti = (TextureImporter)AssetImporter.GetAtPath(path);
                bool normal = path.EndsWith("_Normal.png"), far = path.EndsWith("_Far.png");
                var type = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
                if (ti.textureType == type && ti.sRGBTexture == !normal && ti.alphaIsTransparency == far) continue;
                ti.textureType = type; ti.sRGBTexture = !normal; ti.mipmapEnabled = true; ti.alphaIsTransparency = far; ti.SaveAndReimport();
            }
        }

        static void Copy(string sourceDir, string targetDir, string pattern)
        {
            Directory.CreateDirectory(targetDir);
            var files = Directory.GetFiles(sourceDir, pattern);
            if (files.Length == 0) throw new FileNotFoundException($"{sourceDir}/{pattern}");
            foreach (var file in files)
            {
                if (new FileInfo(file).Length < 1024 && File.ReadAllText(file).StartsWith("version https://git-lfs"))
                    throw new InvalidOperationException("Git LFS pointer instead of asset; run git lfs pull: " + file);
                var target = Path.Combine(targetDir, Path.GetFileName(file));
                if (!File.Exists(target) || new FileInfo(target).Length != new FileInfo(file).Length || File.GetLastWriteTimeUtc(target) < File.GetLastWriteTimeUtc(file))
                    File.Copy(file, target, true);
            }
        }

        static Material Mat(string name, string shader)
        {
            var path = $"{Models}/{name}.mat"; var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) { mat = new Material(Shader.Find(shader)); AssetDatabase.CreateAsset(mat, path); }
            mat.shader = Shader.Find(shader); mat.enableInstancing = true; Mats[name] = mat; return mat;
        }

        static void Materials()
        {
            Texture2D T(string name) => AssetDatabase.LoadAssetAtPath<Texture2D>($"{Models}/Textures/{name}.png");
            var alb = T("T_TreeV2_Bark_Albedo"); var nrm = T("T_TreeV2_Bark_Normal");
            Check(alb && nrm, "T_TreeV2_Bark_Albedo / _Normal imported");
            var bark = Mat("M_TreeV2_Bark", "Universal Render Pipeline/Lit");
            bark.SetTexture("_BaseMap", alb); bark.SetColor("_BaseColor", Color.white); bark.SetTexture("_BumpMap", nrm); bark.EnableKeyword("_NORMALMAP");
            bark.SetFloat("_Smoothness", .08f); bark.SetFloat("_Metallic", 0);
            // leaves: the colour is in the vertex colours (RGB), so a vertex-colour shader is needed; Particles/Simple Lit multiplies it in
            var leaf = Mat("M_TreeV2_Leaf", "Universal Render Pipeline/Particles/Simple Lit");
            leaf.SetColor("_BaseColor", Color.white); leaf.SetFloat("_Cull", 0); leaf.SetFloat("_Surface", 0); leaf.SetFloat("_Smoothness", .1f);
            foreach (var id in Ids)
            {
                var far = Mat($"M_{id}_Far", "Universal Render Pipeline/Lit"); var t = T($"T_{id}_Far");
                Check(t, $"T_{id}_Far imported ({(t ? t.width + " x " + t.height : "missing")})");
                far.SetTexture("_BaseMap", t); far.SetColor("_BaseColor", Color.white); far.SetFloat("_AlphaClip", 1); far.SetFloat("_Cutoff", .5f);
                far.EnableKeyword("_ALPHATEST_ON"); far.SetFloat("_Cull", 0); far.SetFloat("_Smoothness", 0); far.renderQueue = (int)RenderQueue.AlphaTest;
                EditorUtility.SetDirty(far);
            }
            EditorUtility.SetDirty(bark); EditorUtility.SetDirty(leaf); AssetDatabase.SaveAssets();
        }

        static Material Map(Material m) => m == null ? null : Mats.OrderByDescending(k => k.Key.Length).FirstOrDefault(kv => m.name.StartsWith(kv.Key)).Value;

        static GameObject Place(string file, Vector3 at, float yaw)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>($"{Models}/{file}.fbx"));
            go.transform.SetPositionAndRotation(at, Quaternion.Euler(0, yaw, 0));
            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
            {
                if (r.name.Contains("_Collision")) { r.enabled = false; continue; }
                r.sharedMaterials = r.sharedMaterials.Select(Map).ToArray();
                r.shadowCastingMode = r.name.EndsWith("_LOD3") ? ShadowCastingMode.Off : ShadowCastingMode.On;
            }
            var lg = go.GetComponent<LODGroup>() ?? go.AddComponent<LODGroup>();
            lg.SetLODs(Enumerable.Range(0, 4).Select(i => new LOD(Cuts[i], Level(go, i))).ToArray());
            var col = go.GetComponentsInChildren<MeshFilter>(true).FirstOrDefault(m => m.name.EndsWith("_Collision"));
            if (col != null && col.GetComponent<MeshCollider>() == null) col.gameObject.AddComponent<MeshCollider>().sharedMesh = col.sharedMesh;
            Physics.SyncTransforms();
            return go;
        }

        static Renderer[] Level(GameObject go, int i) => go.GetComponentsInChildren<Renderer>(true).Where(r => r.name.EndsWith("_LOD" + i)).ToArray();
        static int Tris(IEnumerable<Renderer> rs) => rs.Sum(r => { var m = r.GetComponent<MeshFilter>().sharedMesh; return Enumerable.Range(0, m.subMeshCount).Sum(s => (int)m.GetIndexCount(s)) / 3; });
        static Bounds Box(IEnumerable<Renderer> rs) { var a = rs.ToArray(); var b = a[0].bounds; foreach (var r in a) b.Encapsulate(r.bounds); return b; }

        // ------------------------------------------------------------------ checks
        static void Inspect(string id, Info info)
        {
            var go = Place(id, Vector3.zero, 0);
            var lod0 = Level(go, 0); var b = Box(lod0); var d = info.dimensions_m;
            Check(Mathf.Abs(b.size.x - d[0]) < .03f && Mathf.Abs(b.size.z - d[1]) < .03f && Mathf.Abs(b.size.y - d[2]) < .03f,
                $"{id}: imported size {b.size.x:0.000} x {b.size.z:0.000} x {b.size.y:0.000} m matches model_info {d[0]} x {d[1]} x {d[2]}");
            Check(b.max.y >= 8f && b.max.y <= 12f, $"{id}: height {b.max.y:0.00} m (package 8-12 m)");
            Check(Mathf.Abs(b.min.y + .3f) < .06f, $"{id}: roots end {-b.min.y:0.000} m below ground (package 0.3 m)");
            var tris = Enumerable.Range(0, 4).Select(i => Tris(Level(go, i))).ToArray();
            Check(Enumerable.Range(0, 4).All(i => Mathf.Abs(tris[i] - info.lods[i].triangles) <= info.lods[i].triangles * .01f + 2),
                $"{id}: triangles LOD0/1/2/3 = {string.Join(" / ", tris)}, model_info {string.Join(" / ", info.lods.Select(l => l.triangles))}");
            Check(tris[0] <= 60000 && tris[1] <= 15000 && tris[2] <= 4000 && tris[3] <= 200, $"{id}: within the package budget 60,000 / 15,000 / 4,000 / 200");
            var used = Enumerable.Range(0, 4).SelectMany(i => Level(go, i)).SelectMany(r => r.sharedMaterials).ToArray();
            Check(used.All(m => m != null), $"{id}: every FBX material slot mapped");
            var names = used.Where(m => m).Select(m => m.name).Distinct().OrderBy(s => s).ToArray();
            Check(names.SequenceEqual(info.materials.OrderBy(s => s)), $"{id}: materials {string.Join(", ", names)} (model_info {string.Join(", ", info.materials)})");
            var lods = go.GetComponent<LODGroup>().GetLODs();
            Check(lods.Length == 4 && lods.All(l => l.renderers.Length == 1), $"{id}: LODGroup 4 levels x 1 renderer");
            var col = go.GetComponentsInChildren<MeshCollider>(true).FirstOrDefault();
            Check(col != null && col.sharedMesh.triangles.Length > 0, $"{id}: trunk collision as MeshCollider ({(col ? col.sharedMesh.triangles.Length / 3 : 0)} tris), render hidden");
            Check(Physics.Raycast(new Vector3(-3, 1f, 0), Vector3.right, out var hit, 6) && hit.collider == col,
                  $"{id}: a ray at 1 m from 3 m on the land side hits the trunk at {(hit.collider ? hit.distance.ToString("0.00") : "-")} m");

            // vertex data on LOD0: wind weight in UV2.x, leaf colour + occlusion in the vertex colours
            var mesh = lod0[0].GetComponent<MeshFilter>().sharedMesh; var r0 = lod0[0];
            var uv2 = new List<Vector2>(); mesh.GetUVs(1, uv2); var cols = mesh.colors; var verts = mesh.vertices;
            Check(uv2.Count == mesh.vertexCount && cols.Length == mesh.vertexCount, $"{id}: LOD0 has UV2 ({uv2.Count}) and vertex colours ({cols.Length}) on all {mesh.vertexCount} vertices");
            if (uv2.Count == mesh.vertexCount && cols.Length == mesh.vertexCount)
            {
                int leafSub = Array.FindIndex(r0.sharedMaterials, m => m && m.name == "M_TreeV2_Leaf");
                var leafIdx = new HashSet<int>(leafSub >= 0 ? mesh.GetIndices(leafSub) : new int[0]);
                var baseW = Enumerable.Range(0, mesh.vertexCount).Where(i => !leafIdx.Contains(i) && verts[i].y < 1.2f && new Vector2(verts[i].x, verts[i].z).magnitude < .9f).Select(i => uv2[i].x).DefaultIfEmpty(1).Max();
                var leafW = leafIdx.Select(i => uv2[i].x).DefaultIfEmpty(0).Min();
                Check(baseW <= .05f, $"{id}: wind weight at the trunk base <= 0.05 (max {baseW:0.000})");
                Check(leafIdx.Count > 0 && leafW >= .85f, $"{id}: wind weight on all {leafIdx.Count} leaf vertices >= 0.85 (min {leafW:0.000})");
                var la = leafIdx.Select(i => cols[i].a).ToArray(); var lg = leafIdx.Select(i => cols[i].g).ToArray();
                Check(la.Length > 0 && la.Min() >= .4f && la.Max() <= 1f && la.Max() - la.Min() > .3f, $"{id}: leaf occlusion in vertex alpha {la.Min():0.00}-{la.Max():0.00}");
                Check(lg.Length > 0 && lg.Max() - lg.Min() > .1f, $"{id}: leaf colour varies (green {lg.Min():0.00}-{lg.Max():0.00})");
            }
            UnityEngine.Object.DestroyImmediate(go);
        }

        // ------------------------------------------------------------------ renders
        static Camera cam; static RenderTexture target; static Material groundMat, rulerMat;

        static void Setup()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            var sun = new GameObject("Sun").AddComponent<Light>(); sun.type = LightType.Directional; sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(42, -35, 0); sun.color = new Color(1, .88f, .70f); sun.intensity = 1.6f;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(.52f, .60f, .74f); RenderSettings.ambientEquatorColor = new Color(.48f, .50f, .46f); RenderSettings.ambientGroundColor = new Color(.28f, .26f, .21f);
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane); ground.transform.localScale = Vector3.one * 60;
            groundMat = Flat("ground", new Color(.33f, .34f, .26f)); ground.GetComponent<Renderer>().sharedMaterial = groundMat;
            rulerMat = Flat("ruler", new Color(.30f, .42f, .55f));
            cam = new GameObject("Review Camera").AddComponent<Camera>(); cam.nearClipPlane = .05f; cam.farClipPlane = 800;
            cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = new Color(.62f, .72f, .86f);
            UnityEngine.Rendering.Universal.CameraExtensions.GetUniversalAdditionalCameraData(cam).renderPostProcessing = true;
            target = new RenderTexture(1600, 1200, 24) { antiAliasing = 4 }; cam.targetTexture = target;
            cam.transform.position = new Vector3(0, 20, -40); cam.transform.LookAt(Vector3.zero); cam.Render(); cam.Render();   // warm-up: the first frame of a new scene came out with a white ground
        }

        static void Shots()
        {
            Setup();
            foreach (var id in Ids)
            {
                var go = Place(id, Vector3.zero, 0); var b = Box(Level(go, 0)); var ruler = Ruler(new Vector3(b.min.x - .8f, 0, b.min.z - .5f));
                go.GetComponent<LODGroup>().ForceLOD(0);
                Frame($"{id}-three-quarter", b, new Vector3(-.55f, .25f, -.85f));
                Frame($"{id}-front", b, new Vector3(0, .08f, -1));
                Shot($"{id}-under-canopy", new Vector3(b.center.x * .5f - .8f, 1.6f, b.center.z * .5f - .9f), new Vector3(b.center.x, b.max.y * .8f, b.center.z), 75);
                go.GetComponent<LODGroup>().ForceLOD(-1);   // the LODGroup picks the level from here on
                foreach (var dist in new[] { 20f, 60f })
                    Shot($"{id}-eye-{dist:0}m-lodgroup", new Vector3(b.center.x, 1.7f, b.center.z - dist), new Vector3(b.center.x, dist < 30 ? b.max.y * .5f : 3f, b.center.z), 60);
                UnityEngine.Object.DestroyImmediate(ruler); UnityEngine.Object.DestroyImmediate(go);
            }
            Report.Add($"INFO renders written to art/previews/{Pkg}/unity");
        }

        static GameObject Ruler(Vector3 at)
        {
            var r = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            UnityEngine.Object.DestroyImmediate(r.GetComponent<Collider>());
            r.transform.position = at + Vector3.up * .875f; r.transform.localScale = new Vector3(.42f, .875f, .42f);
            r.GetComponent<Renderer>().sharedMaterial = rulerMat; return r;
        }

        static void Frame(string file, Bounds b, Vector3 dir, float pad = 1.05f)
        {
            float radius = b.extents.magnitude * pad, dist = radius / Mathf.Sin(30 * .5f * Mathf.Deg2Rad);
            Shot(file, b.center + dir.normalized * dist, b.center, 30);
        }

        static void Shot(string file, Vector3 from, Vector3 at, float fov)
        {
            cam.fieldOfView = fov; cam.transform.position = from; cam.transform.LookAt(at); cam.Render(); cam.Render(); cam.Render();   // a few frames so shaders and shadows settle (the first 3/4 shot had a white ground)
            RenderTexture.active = target;
            var image = new Texture2D(target.width, target.height, TextureFormat.RGB24, false);
            image.ReadPixels(new Rect(0, 0, target.width, target.height), 0, 0); image.Apply();
            var path = Path.Combine(Out, file + ".png"); Directory.CreateDirectory(Path.GetDirectoryName(path));
            File.WriteAllBytes(path, image.EncodeToPNG());
            RenderTexture.active = null; UnityEngine.Object.DestroyImmediate(image);
        }

        static Material Flat(string name, Color color)
        {
            var path = $"{Models}/{name}.mat"; var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) { mat = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(mat, path); }
            mat.SetColor("_BaseColor", color); mat.SetFloat("_Smoothness", .1f); return mat;
        }
    }
}
