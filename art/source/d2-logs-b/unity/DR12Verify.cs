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
    // DR12 地上的大片剝落樹皮 L 的 Unity 檢查（不改 apps/game：run_unity_dr12.sh 只在這次批次執行時複製進專案，跑完刪掉）。
    // 匯入交付的 FBX 和共用分層貼圖（DR08_Shared、DR09_Shared），本體配 YunJing/D2LayeredWood（和 DR09 斷枝堆同一個材質 M_DR09_Layered），
    // 檢查尺寸、原點、LOD 面數與物件數、材質、UV0／UV1／頂點色、貼圖大小、碰撞殼（小腿高橫掃擋住、平段踩得上去、捲起處的高度），最後出圖。
    // 期望值讀 art/exports/d2-logs-b/DR12_BarkSheet_L/model_info.json（report_dr12.py 寫的）。
    // 輸出：art/previews/d2-logs-b/DR12_BarkSheet_L/unity/*.png、report.txt
    public static class DR12Verify
    {
        const string Id = "DR12_BarkSheet_L", Ver = "v001", Models = "Assets/YunJing/Models/D2LogsB";
        static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ".."));
        static string ExportRoot => Path.Combine(Repo, "art/exports/d2-logs-b");
        static string Out => Path.Combine(Repo, "art/previews/d2-logs-b", Id, "unity");
        static string Dst => $"{Models}/{Id}";
        static readonly List<string> Report = new List<string>();
        static int failures;

        [Serializable] class Lods { public int LOD0, LOD1, LOD2, collision; public int[] All => new[] { LOD0, LOD1, LOD2 }; }
        [Serializable] class Cam { public string name; public float[] from; public float[] at; public float lens_mm; }
        [Serializable] class Info { public float[] dimensions_m, bounds_min_m, bounds_max_m, ruler_build_xy; public Lods lods; public Cam[] review_cams_build_xyz; public string minTier; }

        static void Check(bool ok, string line) { Report.Add((ok ? "PASS " : "FAIL ") + line); if (!ok) failures++; }

        public static void Run()
        {
            Report.Clear(); failures = 0;
            var info = JsonUtility.FromJson<Info>(File.ReadAllText(Path.Combine(ExportRoot, Id, "model_info.json")));
            Directory.CreateDirectory(Out);
            Import();
            QingxiUrpUpgrade.EnsurePipeline();
            Report.Add($"Unity {Application.unityVersion}, pipeline {GraphicsSettings.currentRenderPipeline?.name ?? "built-in"}, {Id} {Ver}");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            Inspect(info);
            Shots(info);
            File.WriteAllLines(Path.Combine(Out, "report.txt"), Report);
            foreach (var l in Report) Debug.Log("DR12 " + l);
            if (failures > 0) throw new Exception($"DR12_VERIFY {failures} check(s) failed, see report.txt");
            Debug.Log("DR12_VERIFY_DONE all checks passed");
        }

        static void CopyDir(string src, string dst, string pattern)
        {
            Directory.CreateDirectory(dst);
            foreach (var f in Directory.GetFiles(src, pattern)) File.Copy(f, Path.Combine(dst, Path.GetFileName(f)), true);
        }

        static void Import()
        {
            var game = Path.Combine(Repo, "apps/game");
            CopyDir(Path.Combine(ExportRoot, Id), Path.Combine(game, Dst), $"{Id}_{Ver}.fbx");
            CopyDir(Path.Combine(ExportRoot, "DR08_Shared", "Textures"), Path.Combine(game, Models, "DR08_Shared", "Textures"), "*.png");
            CopyDir(Path.Combine(ExportRoot, "DR09_Shared", "Textures"), Path.Combine(game, Models, "DR09_Shared", "Textures"), "*.png");
            AssetDatabase.Refresh();
            var mi = (ModelImporter)AssetImporter.GetAtPath($"{Dst}/{Id}_{Ver}.fbx");
            mi.bakeAxisConversion = true; mi.importCameras = false; mi.importLights = false; mi.addCollider = false; mi.importAnimation = false;
            mi.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription; mi.SaveAndReimport();
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { $"{Models}/DR08_Shared", $"{Models}/DR09_Shared" }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var ti = (TextureImporter)AssetImporter.GetAtPath(path);
                bool normal = path.EndsWith("_Normal.png");
                ti.textureType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default; ti.sRGBTexture = !normal && !path.Contains("Mask"); ti.mipmapEnabled = true;
                ti.wrapMode = TextureWrapMode.Repeat; ti.SaveAndReimport();
            }
        }

        static readonly string[] Layers = { "Bark", "Moss", "Rot", "Fibre", "Inner", "Soil" };
        static Material body;
        static Material Layered()
        {
            if (body) return body;
            var dir = $"{Models}/DR09_Shared/Materials"; Directory.CreateDirectory(Path.Combine(Repo, "apps/game", dir));
            var path = $"{dir}/M_DR09_Layered.mat";
            var shader = Shader.Find("YunJing/D2LayeredWood");
            Check(shader != null, $"{Id}: shader YunJing/D2LayeredWood found");
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) { mat = new Material(shader); AssetDatabase.CreateAsset(mat, path); } else mat.shader = shader;
            var sizes = new List<string>();
            foreach (var l in Layers)
            {
                bool fresh = l == "Fibre", bark9 = l == "Bark";
                var al = AssetDatabase.LoadAssetAtPath<Texture2D>(fresh ? $"{Models}/DR09_Shared/Textures/DR09_FreshWood_Albedo.png" : bark9 ? $"{Models}/DR09_Shared/Textures/DR09_Bark_Albedo.png" : $"{Models}/DR08_Shared/Textures/DR08_{l}_Albedo.png");
                var nm = AssetDatabase.LoadAssetAtPath<Texture2D>(fresh ? $"{Models}/DR09_Shared/Textures/DR09_FreshWood_Normal.png" : $"{Models}/DR08_Shared/Textures/DR08_{l}_Normal.png");
                Check(al != null && nm != null, $"{Id}: {l} slot albedo / normal found");
                mat.SetTexture($"_{l}Map", al); mat.SetTexture($"_{l}Nrm", nm);
                foreach (var t in new[] { al, nm }.Where(t => t))
                {
                    ((TextureImporter)AssetImporter.GetAtPath(AssetDatabase.GetAssetPath(t))).GetSourceTextureWidthAndHeight(out int w, out int h);
                    sizes.Add($"{w}x{h}");
                }
            }
            var src = sizes.Distinct().ToArray();
            Check(src.Length == 1 && src[0] == "1024x1024", $"{Id}: shared tiling layers delivered at {string.Join(", ", src)}");
            EditorUtility.SetDirty(mat);
            return body = mat;
        }

        static bool IsCollision(Component r) => r.name.EndsWith("_Collision");
        static Renderer[] Level(GameObject go, int i) => go.GetComponentsInChildren<Renderer>(true).Where(r => r.name.EndsWith("_LOD" + i)).ToArray();
        static int Tris(IEnumerable<Renderer> rs) => rs.Sum(r => { var m = r.GetComponent<MeshFilter>().sharedMesh; return Enumerable.Range(0, m.subMeshCount).Sum(s => (int)m.GetIndexCount(s)) / 3; });
        static Bounds Box(IEnumerable<Renderer> rs) { var a = rs.ToArray(); var b = a[0].bounds; foreach (var r in a) b.Encapsulate(r.bounds); return b; }

        static GameObject Place()
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>($"{Dst}/{Id}_{Ver}.fbx"));
            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
            {
                r.sharedMaterials = r.sharedMaterials.Select(_ => Layered()).ToArray();
                if (IsCollision(r)) { r.enabled = false; r.gameObject.AddComponent<MeshCollider>().sharedMesh = r.GetComponent<MeshFilter>().sharedMesh; }
            }
            float[] cut = { .12f, .04f, .008f };
            var kids = go.GetComponentsInChildren<Renderer>(true).Where(r => !IsCollision(r)).ToArray();
            var lg = go.GetComponent<LODGroup>(); if (lg == null) lg = go.AddComponent<LODGroup>();
            lg.SetLODs(Enumerable.Range(0, 3).Select(i => new LOD(cut[i], kids.Where(r => r.name.EndsWith("_LOD" + i)).ToArray())).ToArray());
            return go;
        }

        static void Inspect(Info info)
        {
            var go = Place();
            var b = Box(Level(go, 0));
            var d = info.dimensions_m;   // Blender x, y, z → Unity x, z, y
            Check(Mathf.Abs(b.size.x - d[0]) <= .02f && Mathf.Abs(b.size.z - d[1]) <= .02f && Mathf.Abs(b.size.y - d[2]) <= .02f,
                $"{Id}: imported size {b.size.x:0.000} x {b.size.z:0.000} x {b.size.y:0.000} m matches Blender {d[0]} x {d[1]} x {d[2]} within 2 cm");
            Check(Mathf.Max(b.size.x, b.size.z) <= 1.5f && Mathf.Max(b.size.x, b.size.z) >= .3f, $"{Id}: longest side {Mathf.Max(b.size.x, b.size.z):0.00} m within the work pack's 0.3–1.5 m");
            Check(Mathf.Abs(b.min.y - info.bounds_min_m[2]) <= .02f && b.min.y <= 0 && b.min.y > -.03f, $"{Id}: lowest point y = {b.min.y:0.000} m (sunk about 1 cm into the ground)");
            Check(Mathf.Abs(b.center.x) <= .02f && Mathf.Abs(b.center.z) <= .02f, $"{Id}: origin at the bottom centre (footprint centre {b.center.x:0.000}, {b.center.z:0.000})");
            var ex = info.lods.All;
            var tris = Enumerable.Range(0, 3).Select(i => Tris(Level(go, i))).ToArray();
            Check(Enumerable.Range(0, 3).All(i => Mathf.Abs(tris[i] - ex[i]) <= ex[i] * .01f),
                $"{Id}: triangles LOD0/1/2 = {tris[0]} / {tris[1]} / {tris[2]} ({100f * tris[1] / tris[0]:0}% / {100f * tris[2] / tris[0]:0}%), Blender {ex[0]} / {ex[1]} / {ex[2]}");
            var objs = Enumerable.Range(0, 3).Select(i => Level(go, i).Length).ToArray();
            Check(objs.All(n => n == 1), $"{Id}: objects per LOD {string.Join(" / ", objs)} (one body, no Detail_)");
            var mats = go.GetComponentsInChildren<Renderer>(true).Where(r => !IsCollision(r)).SelectMany(r => r.sharedMaterials).Distinct().ToArray();
            Check(mats.Length == 1 && mats[0].shader.name == "YunJing/D2LayeredWood", $"{Id}: {mats.Length} material ({string.Join(", ", mats.Select(m => m.name + " / " + m.shader.name))})");
            Check(info.minTier == "standard", $"{Id}: minTier = {info.minTier}");
            foreach (var r in Enumerable.Range(0, 3).SelectMany(i => Level(go, i)))
            {
                var m = r.GetComponent<MeshFilter>().sharedMesh;
                Check(m.uv.Length == m.vertexCount && m.uv2.Length == m.vertexCount && m.colors.Length == m.vertexCount && m.normals.Length == m.vertexCount,
                    $"{Id}: {r.name} has UV0 (metres), UV1 (soil, AO), vertex colours (layer weights) and normals ({m.vertexCount} vertices)");
            }
            var m0 = Level(go, 0)[0].GetComponent<MeshFilter>().sharedMesh;
            var c = m0.colors; var u2 = m0.uv2;
            Report.Add($"INFO {Id}: mean layer weights moss {c.Average(q => q.r):0.00}, rot {c.Average(q => q.g):0.00}, fibre {c.Average(q => q.b):0.00}, inner {c.Average(q => q.a):0.00}, soil {u2.Average(q => q.x):0.00}; AO {u2.Min(q => q.y):0.00}–{u2.Max(q => q.y):0.00}");
            Check(c.Average(q => q.b) > .3f && c.Average(q => q.r) > .02f, $"{Id}: the pale inner fibre covers the upper face (fibre weight {c.Average(q => q.b):0.00}) and moss is present (moss {c.Average(q => q.r):0.00})");
            var col = go.GetComponentsInChildren<MeshCollider>(true);
            Check(col.Length == 1, $"{Id}: one collision shell (MeshCollider, renderer off)");
            if (col.Length == 1) Check(Mathf.Abs(Tris(new[] { col[0].GetComponent<Renderer>() }) - info.lods.collision) <= info.lods.collision * .01f, $"{Id}: collision {Tris(new[] { col[0].GetComponent<Renderer>() })} triangles (Blender {info.lods.collision})");
            UnityEngine.Object.DestroyImmediate(go);
            // 碰撞：小腿高（0.06–0.20 m、半徑 0.05）沿 Unity z 橫掃，平段到捲起端每 0.2 m 都擋住；從上往下打，平段是低矮可踩的面、捲起端高 0.45 m 以上
            go = Place(); Physics.SyncTransforms();
            int n = 0, hit = 0;
            for (float x = -.35f * b.size.x; x <= .40f * b.size.x; x += .2f, n++)
                if (Physics.CapsuleCast(new Vector3(x, .06f, -3), new Vector3(x, .20f, -3), .05f, Vector3.forward, 6)) hit++;
            Check(hit == n, $"{Id}: a shin-high sweep across the sheet is stopped at {hit} of {n} places (every 0.2 m along its length)");
            bool flat = Physics.Raycast(new Vector3(-.2f * b.size.x, 5, 0), Vector3.down, out var hf, 6);
            Check(flat && hf.point.y < .2f, $"{Id}: the flat part is a low surface underfoot (y = {(flat ? hf.point.y : -1):0.00} m at x = {-.2f * b.size.x:0.00})");
            float best = 0;
            for (float x = .1f * b.size.x; x <= .5f * b.size.x; x += .05f)
                for (float z = -.3f; z <= .3f; z += .1f)
                    if (Physics.Raycast(new Vector3(x, 5, z), Vector3.down, out var hc, 6)) best = Mathf.Max(best, hc.point.y);
            Check(best > .45f && best < .8f, $"{Id}: the curl rises to y = {best:0.00} m in the collision (Blender top {info.bounds_max_m[2]:0.00} m)");
            UnityEngine.Object.DestroyImmediate(go);
        }

        static Camera cam; static RenderTexture target;
        static void Shots(Info info)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            var sun = new GameObject("Sun").AddComponent<Light>(); sun.type = LightType.Directional; sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(50, -35, 0); sun.intensity = 1.25f;
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane); ground.transform.localScale = Vector3.one * 30;
            ground.GetComponent<Renderer>().sharedMaterial = Flat("ground", new Color(.17f, .15f, .12f));
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(.62f, .7f, .78f); RenderSettings.ambientEquatorColor = new Color(.55f, .58f, .52f); RenderSettings.ambientGroundColor = new Color(.32f, .3f, .26f);
            cam = new GameObject("Review Camera").AddComponent<Camera>(); cam.nearClipPlane = .03f; cam.farClipPlane = 600;
            UnityEngine.Rendering.Universal.CameraExtensions.GetUniversalAdditionalCameraData(cam).renderPostProcessing = true;
            target = new RenderTexture(1536, 864, 24) { antiAliasing = 4 }; cam.targetTexture = target;
            cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = new Color(.66f, .70f, .74f);
            var go = Place();
            var ruler = GameObject.CreatePrimitive(PrimitiveType.Capsule); UnityEngine.Object.DestroyImmediate(ruler.GetComponent<Collider>());
            ruler.transform.position = new Vector3(info.ruler_build_xy[0], .875f, info.ruler_build_xy[1]); ruler.transform.localScale = new Vector3(.42f, .875f, .42f);
            ruler.GetComponent<Renderer>().sharedMaterial = Flat("ruler", new Color(.85f, .85f, .85f));
            var lg = go.GetComponent<LODGroup>();
            var cams = info.review_cams_build_xyz.ToDictionary(k => k.name);
            void S(string file, Cam k) => Shot(file, new Vector3(k.from[0], k.from[2], k.from[1]), new Vector3(k.at[0], k.at[2], k.at[1]), k.lens_mm);
            lg.ForceLOD(0);
            foreach (var k in new[] { "tq", "side", "curl", "teeth", "end", "top", "back" }) if (cams.ContainsKey(k)) S(k + "-lod0", cams[k]);
            Shot("ref-lod0", new Vector3(.55f, 1.30f, 3.15f), new Vector3(-.05f, .22f, 0), 42);           // 參考圖 DR12-threequarter 的方向（vs_dr12.py 同一個鏡位）
            for (int i = 1; i < 3; i++) { lg.ForceLOD(i); S($"tq-lod{i}", cams["tq"]); S($"side-lod{i}", cams["side"]); }
            lg.ForceLOD(-1);
            Report.Add($"INFO renders written to art/previews/d2-logs-b/{Id}/unity");
        }

        static void Shot(string file, Vector3 from, Vector3 at, float lens)
        {
            float h = 2 * Mathf.Atan(18f / lens);
            cam.fieldOfView = 2 * Mathf.Atan(Mathf.Tan(h / 2) * 864f / 1536f) * Mathf.Rad2Deg;
            cam.transform.position = from; cam.transform.LookAt(at); cam.Render();
            RenderTexture.active = target;
            var image = new Texture2D(target.width, target.height, TextureFormat.RGB24, false);
            image.ReadPixels(new Rect(0, 0, target.width, target.height), 0, 0); image.Apply();
            File.WriteAllBytes(Path.Combine(Out, $"{Id}-{file}.png"), image.EncodeToPNG());
            RenderTexture.active = null; UnityEngine.Object.DestroyImmediate(image);
        }

        static Material Flat(string name, Color color)
        {
            var path = $"{Dst}/{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) { mat = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(mat, path); }
            mat.SetColor("_BaseColor", color); mat.SetFloat("_Smoothness", .1f);
            return mat;
        }
    }
}
