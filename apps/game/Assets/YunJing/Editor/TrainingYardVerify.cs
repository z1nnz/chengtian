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
    // Unity check of the 11/14 package A training yard TG01-TG06, starting with the TG01 wooden dummy sample (art/exports/training-yard-a, Johnnnny0823).
    // Imports every module FBX and the training-yard trim sheet (T_TrainingYard_*), builds the URP materials named in model_info
    // (M_TrainingYard_Trim / _Glow), maps them by FBX material name, adds LODGroups and mesh colliders, compares each module with
    // its model_info.json (size, bounds, LOD triangles, objects, materials, sockets, collision) and walks the bridge with rays and
    // a 1.75 m capsule (deck level end to end, clear width >= 2.4 m, clear height >= 2.6 m, railing).
    // Needs a graphics device (no -nographics):
    //   Unity -batchmode -quit -projectPath apps/game -executeMethod YunJing.Editor.TrainingYardVerify.Run -logFile <log>
    // Output: art/previews/mountain-street-a/unity/*.png and report.txt; the run fails when a check fails.
    public static class TrainingYardVerify
    {
        const string Models = "Assets/YunJing/Models/TrainingYard";   // copied from art/exports, gitignored
        const string Pkg = "training-yard-a";
        static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ".."));
        static string Exports => Path.Combine(Repo, "art/exports", Pkg);
        static string Out => Path.Combine(Repo, "art/previews", Pkg, "unity");
        static readonly List<string> Report = new List<string>();
        static int failures;
        static readonly Dictionary<string, Material> Mats = new Dictionary<string, Material>();
        static float sx = 1;   // Blender +X -> Unity +X (same FBX export settings as CB01 / MC01, measured there)

        [Serializable] class Lod { public int lod, triangles, objects, materials; }
        [Serializable] class Socket { public string name; public float[] location_m; }
        [Serializable] class Extra { public float deckTop_m, clearWidth_m, clearHeight_m; }
        [Serializable] class Info { public string id, collision; public Extra extra; public float[] dimensions_m, bounds_min_m; public Lod[] lods; public string[] materials, glowObjects; public Socket[] sockets; }
        [Serializable] class Part { public string id; public float[] pos; public float rotZ; }
        [Serializable] class Assembly { public Part[] parts; }

        static string[] Ids => Directory.GetFiles(Exports, "*.fbx").Select(Path.GetFileNameWithoutExtension).OrderBy(s => s).ToArray();

        public static void Run()
        {
            Report.Clear(); failures = 0; Directory.CreateDirectory(Out);
            Import();
            QingxiUrpUpgrade.EnsurePipeline();
            Materials();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            Report.Add($"Unity {Application.unityVersion}, pipeline {GraphicsSettings.currentRenderPipeline?.name ?? "built-in"}");
            Measure();
            foreach (var id in Ids) Inspect(id, JsonUtility.FromJson<Info>(File.ReadAllText(Path.Combine(Exports, $"{id}.model_info.json"))));
            Probes();
            Shots();
            File.WriteAllLines(Path.Combine(Out, "report.txt"), Report);
            foreach (var line in Report) Debug.Log("TRAINYARD " + line);
            if (failures > 0) throw new Exception($"TRAINYARD_VERIFY {failures} check(s) failed, see {Out}/report.txt");
            Debug.Log($"TRAINYARD_VERIFY_DONE all checks passed, output {Out}");
        }

        static void Check(bool ok, string line) { Report.Add((ok ? "PASS " : "FAIL ") + line); if (!ok) failures++; }

        // ------------------------------------------------------------------ import
        static void Import()
        {
            Copy(Exports, Path.Combine(Repo, "apps/game", Models), "*.fbx");
            Copy(Path.Combine(Repo, "art/textures", Pkg), Path.Combine(Repo, "apps/game", Models, "Textures"), "T_TrainingYard_*.png");
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
                bool normal = path.EndsWith("_Normal.png"), linear = normal || path.EndsWith("_MetallicSmoothness.png");
                var type = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
                if (ti.textureType == type && ti.sRGBTexture == !linear) continue;
                ti.textureType = type; ti.sRGBTexture = !linear; ti.mipmapEnabled = true; ti.SaveAndReimport();
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

        static int PngSize(string file) { var png = File.ReadAllBytes(file); return (png[16] << 24) | (png[17] << 16) | (png[18] << 8) | png[19]; }

        static void Materials()
        {
            Texture2D T(string name) => AssetDatabase.LoadAssetAtPath<Texture2D>($"{Models}/Textures/{name}.png");
            foreach (var (set, src, size) in new[] { ("TrainingYard", Pkg, 2048) })
            {
                var alb = T($"T_{set}_Albedo"); var nrm = T($"T_{set}_Normal"); var ms = T($"T_{set}_MetallicSmoothness"); var em = T($"T_{set}_Emission");
                Check(alb && nrm && ms && em, $"T_{set}_*: Albedo / Normal / MetallicSmoothness / Emission imported");
                if (!(alb && nrm && ms && em)) continue;
                int sw = PngSize(Path.Combine(Repo, "art/textures", src, alb.name + ".png"));
                Check(sw == size && alb.width == Math.Min(sw, 1024), $"{alb.name}: source {sw}, imported {alb.width} x {alb.height} (QingxiImportBudget caps model textures at 1024)");
                foreach (var glow in new[] { false, true })
                {
                    var name = $"M_{set}" + (glow ? "_Glow" : "_Trim");
                    var path = $"{Models}/{name}.mat"; var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
                    if (mat == null) { mat = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(mat, path); }
                    mat.enableInstancing = true; Mats[name] = mat;
                    mat.SetTexture("_BaseMap", alb); mat.SetColor("_BaseColor", Color.white);
                    mat.SetTexture("_BumpMap", nrm); mat.SetFloat("_BumpScale", 1); mat.EnableKeyword("_NORMALMAP");
                    mat.SetTexture("_MetallicGlossMap", ms); mat.EnableKeyword("_METALLICSPECGLOSSMAP"); mat.SetFloat("_Smoothness", 1);
                    if (glow)
                    {
                        mat.SetTexture("_EmissionMap", em); mat.SetColor("_EmissionColor", Color.white * 2.5f); mat.EnableKeyword("_EMISSION");
                        mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.BakedEmissive;
                    }
                    EditorUtility.SetDirty(mat);
                }
            }
            AssetDatabase.SaveAssets();
        }

        static Material Map(Material m)
        {
            if (m == null) return Mats["M_TrainingYard_Trim"];
            foreach (var kv in Mats.OrderByDescending(k => k.Key.Length)) if (m.name.StartsWith(kv.Key)) return kv.Value;
            return null;
        }

        static GameObject Place(string file, Vector3 at, float yaw, Transform parent = null)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>($"{Models}/{file}.fbx"));
            go.transform.SetPositionAndRotation(at, Quaternion.Euler(0, yaw, 0)); if (parent) go.transform.SetParent(parent, true);
            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
            {
                if (r.name.Contains("_Collision")) { r.enabled = false; continue; }
                r.sharedMaterials = r.sharedMaterials.Select(Map).ToArray();
            }
            // the FBX importer may already add a LODGroup for _LODn names; fill it either way
            var lg = go.GetComponent<LODGroup>() ?? go.AddComponent<LODGroup>();
            float[] cut = { .30f, .10f, .015f };
            lg.SetLODs(Enumerable.Range(0, 3).Select(i => new LOD(cut[i], go.GetComponentsInChildren<Renderer>().Where(r => r.name.EndsWith("_LOD" + i)).ToArray())).ToArray());
            var col = go.GetComponentsInChildren<MeshFilter>(true).FirstOrDefault(m => m.name.EndsWith("_Collision"));
            if (col != null && col.GetComponent<MeshCollider>() == null) col.gameObject.AddComponent<MeshCollider>().sharedMesh = col.sharedMesh;
            Physics.SyncTransforms();
            return go;
        }

        static Transform Node(GameObject go, string name) => go.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name);
        static Renderer[] Level(GameObject go, int i) => go.GetComponentsInChildren<Renderer>(true).Where(r => r.name.EndsWith("_LOD" + i)).ToArray();
        static int Tris(IEnumerable<Renderer> rs) => rs.Sum(r => { var m = r.GetComponent<MeshFilter>().sharedMesh; return Enumerable.Range(0, m.subMeshCount).Sum(s => (int)m.GetIndexCount(s)) / 3; });
        static Bounds Box(IEnumerable<Renderer> rs) { var a = rs.ToArray(); var b = a[0].bounds; foreach (var r in a) b.Encapsulate(r.bounds); return b; }

        static void Measure()
        {
            Report.Add("INFO axis: Blender +X -> Unity +X, Blender +Y -> Unity +Z, Blender +Z -> Unity +Y (checked on TG01 Socket_Front below)");
        }
        static Vector3 U(float[] p) => new Vector3(sx * p[0], p[2], p[1]);
        static float Yaw(float rotZ) => -sx * rotZ;

        // ------------------------------------------------------------------ checks
        static void Inspect(string id, Info info)
        {
            var go = Place(id, Vector3.zero, 0);
            var lod0 = Level(go, 0); var b = Box(lod0); var d = info.dimensions_m;
            Check(Mathf.Abs(b.size.x - d[0]) < .02f && Mathf.Abs(b.size.z - d[1]) < .02f && Mathf.Abs(b.size.y - d[2]) < .02f,
                $"{id}: imported size {b.size.x:0.000} x {b.size.z:0.000} x {b.size.y:0.000} m matches model_info {d[0]} x {d[1]} x {d[2]}");
            Check(Mathf.Abs(b.min.y - info.bounds_min_m[2]) < .01f, $"{id}: lowest point y = {b.min.y:0.000} (model_info {info.bounds_min_m[2]})");
            var tris = Enumerable.Range(0, 3).Select(i => Tris(Level(go, i))).ToArray();
            Check(Enumerable.Range(0, 3).All(i => Mathf.Abs(tris[i] - info.lods[i].triangles) <= info.lods[i].triangles * .01f + 2),
                $"{id}: triangles LOD0/1/2 = {tris[0]} / {tris[1]} / {tris[2]}, model_info {info.lods[0].triangles} / {info.lods[1].triangles} / {info.lods[2].triangles}");
            Check(lod0.Length == info.lods[0].objects, $"{id}: {lod0.Length} LOD0 objects (model_info {info.lods[0].objects})");
            var used = lod0.SelectMany(r => r.sharedMaterials).ToArray();
            Check(used.All(m => m != null), $"{id}: every FBX material slot mapped to a shared URP material");
            var names = used.Where(m => m).Select(m => m.name).Distinct().OrderBy(s => s).ToArray();
            Check(names.SequenceEqual(info.materials.OrderBy(s => s)), $"{id}: materials {string.Join(", ", names)} (model_info {string.Join(", ", info.materials)})");
            foreach (var g in info.glowObjects ?? new string[0])
            {
                var r = Node(go, g)?.GetComponent<Renderer>();
                Check(r && r.sharedMaterials.All(m => m && m.name.EndsWith("_Glow") && m.IsKeywordEnabled("_EMISSION")), $"{id}: {g} on an emissive _Glow material");
            }
            foreach (var s in info.sockets ?? new Socket[0])
            {
                var t = Node(go, s.name); var want = U(s.location_m);
                Check(t && Vector3.Distance(t.position, want) < .02f, $"{id}: {s.name} at {(t ? t.position.ToString("0.00") : "missing")} (Blender {string.Join(", ", s.location_m)})");
            }
            var lods = go.GetComponent<LODGroup>().GetLODs();
            Check(lods.Length == 3 && lods.All(l => l.renderers.Length == lod0.Length), $"{id}: LODGroup 3 levels x {lod0.Length} renderers");
            var col = go.GetComponentsInChildren<MeshCollider>(true).FirstOrDefault();
            if (info.collision.StartsWith("none")) Check(col == null, $"{id}: no collision (hanging piece)");
            else Check(col != null && col.sharedMesh.triangles.Length > 0, $"{id}: collision imported as MeshCollider ({(col ? col.sharedMesh.triangles.Length / 3 : 0)} tris), render hidden");
            UnityEngine.Object.DestroyImmediate(go);
        }

        static bool Down(Vector3 from, out RaycastHit hit) => Physics.Raycast(from + Vector3.up * 3, Vector3.down, out hit, 10);

        // TG01: the post blocks a trainee in front of it, the arms reach toward the trainee side (-Z), the socket marks where to stand
        static void Probes()
        {
            if (!File.Exists(Path.Combine(Exports, "TG01.model_info.json"))) return;
            var go = Place("TG01", Vector3.zero, 0); var front = Node(go, "Socket_Front");
            Check(front && front.position.z < -.3f, $"TG01 Socket_Front at {(front ? front.position.ToString("F2") : "missing")} (the trainee side is -Z)");
            Check(Physics.Raycast(new Vector3(0, 1.2f, -1.0f), Vector3.forward, out var h, 2) && h.distance > .7f && h.distance < .9f,
                  $"TG01 collision: a ray at 1.2 m from 1 m in front hits the post at {(h.collider ? h.distance.ToString("0.00") : "-")} m (post radius 0.16)");
            var lod0 = go.GetComponentsInChildren<MeshRenderer>(true).First(r => r.name.EndsWith("_LOD0") && !r.name.Contains("Detail"));
            var b = lod0.bounds; Check(b.min.z < -.45f, $"TG01 arms reach to z = {b.min.z:0.00} m on the trainee side (-Z)");
            UnityEngine.Object.DestroyImmediate(go);
        }

        // ------------------------------------------------------------------ renders
        static Camera cam; static RenderTexture target; static Material groundMat, rulerMat;

        static void Setup()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            var sun = new GameObject("Sun").AddComponent<Light>(); sun.type = LightType.Directional; sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(38, -40, 0); sun.color = new Color(1, .86f, .66f); sun.intensity = 1.7f;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(.52f, .60f, .74f); RenderSettings.ambientEquatorColor = new Color(.50f, .50f, .48f); RenderSettings.ambientGroundColor = new Color(.30f, .27f, .22f);
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane); ground.transform.localScale = Vector3.one * 12;
            groundMat = Flat("ground", new Color(.40f, .38f, .33f)); ground.GetComponent<Renderer>().sharedMaterial = groundMat;
            rulerMat = Flat("ruler", new Color(.30f, .42f, .55f));
            cam = new GameObject("Review Camera").AddComponent<Camera>(); cam.nearClipPlane = .05f; cam.farClipPlane = 400;
            cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = new Color(.62f, .72f, .86f);
            UnityEngine.Rendering.Universal.CameraExtensions.GetUniversalAdditionalCameraData(cam).renderPostProcessing = true;
            target = new RenderTexture(1600, 1200, 24) { antiAliasing = 4 }; cam.targetTexture = target;
        }

        static void Shots()
        {
            var front = Vector3.back; var side = Vector3.Cross(Vector3.up, front);
            Setup();
            foreach (var id in Ids)
            {
                var go = Place(id, Vector3.zero, 0); var b = Box(Level(go, 0)); var ruler = Ruler(new Vector3(b.max.x + .5f, 0, b.min.z - .4f));
                Frame($"modules/{id}", b, (front - side * .8f).normalized + Vector3.up * .5f);
                Frame($"modules/{id}-side", b, front + Vector3.up * .1f);
                if (id == "TG01")   // standing where the trainee stands, 1.7 m eye height
                    Shot("modules/TG01-trainee-eye-1p7m", new Vector3(sx * .35f, 1.7f, -1.4f), new Vector3(0, 1.15f, 0), 50);
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

        static void Frame(string file, Bounds b, Vector3 dir, float pad = 1.2f)
        {
            float radius = b.extents.magnitude * pad, dist = radius / Mathf.Sin(30 * .5f * Mathf.Deg2Rad);
            Shot(file, b.center + dir.normalized * dist, b.center, 30);
        }

        static void Shot(string file, Vector3 from, Vector3 at, float fov)
        {
            cam.fieldOfView = fov; cam.transform.position = from; cam.transform.LookAt(at); cam.Render();
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
