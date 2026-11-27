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
    // DR11 翻起的倒樹根盤 B 的 Unity 檢查（不改 apps/game：run_unity_dr11.sh 只在這次批次執行時複製進專案，跑完刪掉）。
    // 匯入交付的 FBX 與貼圖（DR11_VER，預設 v002：Textures_v002），建一個 URP Lit 本體材質（Albedo、Normal、MaskURP）
    // 和一個雙面植物材質，檢查尺寸、原點、LOD 面數與物件數、材質數、碰撞殼，用 1.75 m 的走路膠囊撞根盤，最後出圖。
    // 期望值由 Blender 從遊戲 blend 量好寫進 DR11_EXPECT（JSON 檔路徑）。
    // 輸出：art/previews/d2-logs-b/DR11_RootPlate_B/unity_<版本>/*.png、report.txt
    public static class DR11Verify
    {
        const string Id = "DR11_RootPlate_B", Models = "Assets/YunJing/Models/D2LogsB";
        static string Ver => Environment.GetEnvironmentVariable("DR11_VER") ?? "v002";
        static string TexDir => Ver == "v001" ? "Textures" : "Textures_" + Ver;
        static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ".."));
        static string Exports => Path.Combine(Repo, "art/exports/d2-logs-b", Id);
        static string Out => Path.Combine(Repo, "art/previews/d2-logs-b", Id, "unity_" + Ver);
        static string Dst => $"{Models}/{Id}";
        static readonly List<string> Report = new List<string>();
        static int failures;

        [Serializable] class Expect { public float[] dims; public float[] min; public int[] tris; public int col; }

        static void Check(bool ok, string line) { Report.Add((ok ? "PASS " : "FAIL ") + line); if (!ok) failures++; }

        public static void Run()
        {
            Report.Clear(); failures = 0;
            var ex = JsonUtility.FromJson<Expect>(File.ReadAllText(Environment.GetEnvironmentVariable("DR11_EXPECT")));
            Directory.CreateDirectory(Out);
            Import();
            QingxiUrpUpgrade.EnsurePipeline();
            Report.Add($"Unity {Application.unityVersion}, pipeline {GraphicsSettings.currentRenderPipeline?.name ?? "built-in"}, {Id} {Ver}");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            Inspect(ex);
            Shots();
            File.WriteAllLines(Path.Combine(Out, "report.txt"), Report);
            foreach (var l in Report) Debug.Log("DR11 " + l);
            if (failures > 0) throw new Exception($"DR11_VERIFY {failures} check(s) failed, see report.txt");
            Debug.Log("DR11_VERIFY_DONE all checks passed");
        }

        static void Import()
        {
            var dst = Path.Combine(Repo, "apps/game", Dst);
            Directory.CreateDirectory(Path.Combine(dst, "Textures"));
            File.Copy(Path.Combine(Exports, $"{Id}_{Ver}.fbx"), Path.Combine(dst, $"{Id}_{Ver}.fbx"), true);
            foreach (var f in Directory.GetFiles(Path.Combine(Exports, TexDir), "*.png")) File.Copy(f, Path.Combine(dst, "Textures", Path.GetFileName(f)), true);
            AssetDatabase.Refresh();
            var mi = (ModelImporter)AssetImporter.GetAtPath($"{Dst}/{Id}_{Ver}.fbx");
            mi.bakeAxisConversion = true; mi.importCameras = false; mi.importLights = false; mi.addCollider = false; mi.importAnimation = false;
            mi.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription; mi.SaveAndReimport();
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { Dst }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var ti = (TextureImporter)AssetImporter.GetAtPath(path);
                bool normal = path.EndsWith("_Normal.png"), linear = normal || path.EndsWith("_MaskURP.png") || path.EndsWith("_ORM.png");
                ti.textureType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default; ti.sRGBTexture = !linear; ti.mipmapEnabled = true; ti.maxTextureSize = 2048;
                ti.SaveAndReimport();
            }
        }

        static Texture2D Tex(string kind) => AssetDatabase.LoadAssetAtPath<Texture2D>($"{Dst}/Textures/{Id}_A_{kind}.png");
        static Material body, plants;
        static Material Mat(bool leaf)
        {
            if (leaf ? plants : body) return leaf ? plants : body;
            Directory.CreateDirectory(Path.Combine(Repo, "apps/game", Dst, "Materials"));
            var path = $"{Dst}/Materials/M_{Id}_{(leaf ? "Leaf" : "A")}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null) { m = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(m, path); }
            m.SetTexture("_BaseMap", Tex("Albedo")); m.SetColor("_BaseColor", Color.white);
            m.SetTexture("_BumpMap", Tex("Normal")); m.EnableKeyword("_NORMALMAP");
            m.SetTexture("_MetallicGlossMap", Tex("MaskURP")); m.EnableKeyword("_METALLICSPECGLOSSMAP"); m.SetFloat("_Smoothness", 1);
            m.SetTexture("_OcclusionMap", Tex("MaskURP")); m.EnableKeyword("_OCCLUSIONMAP");
            if (leaf)
            {
                m.SetFloat("_AlphaClip", 1); m.SetFloat("_Cutoff", .5f); m.EnableKeyword("_ALPHATEST_ON");
                m.SetFloat("_Cull", (float)CullMode.Off); m.doubleSidedGI = true;
                m.renderQueue = (int)RenderQueue.AlphaTest; m.SetOverrideTag("RenderType", "TransparentCutout");
                plants = m;
            }
            else body = m;
            EditorUtility.SetDirty(m);
            return m;
        }

        static bool IsDetail(Renderer r) => r.name.StartsWith("Detail_");
        static bool IsCollision(Component r) => r.name.EndsWith("_Collision");
        static Renderer[] Level(GameObject go, int i, bool detail = true) =>
            go.GetComponentsInChildren<Renderer>(true).Where(r => r.name.EndsWith("_LOD" + i) && (detail || !IsDetail(r))).ToArray();
        static int Tris(IEnumerable<Renderer> rs) => rs.Sum(r => { var m = r.GetComponent<MeshFilter>().sharedMesh; return Enumerable.Range(0, m.subMeshCount).Sum(s => (int)m.GetIndexCount(s)) / 3; });
        static Bounds Box(IEnumerable<Renderer> rs) { var a = rs.ToArray(); var b = a[0].bounds; foreach (var r in a) b.Encapsulate(r.bounds); return b; }

        static GameObject Place()
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>($"{Dst}/{Id}_{Ver}.fbx"));
            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
            {
                r.sharedMaterials = r.sharedMaterials.Select(_ => Mat(IsDetail(r))).ToArray();
                if (IsCollision(r)) { r.enabled = false; r.gameObject.AddComponent<MeshCollider>().sharedMesh = r.GetComponent<MeshFilter>().sharedMesh; }
            }
            float[] cut = { .25f, .08f, .015f };
            var kids = go.GetComponentsInChildren<Renderer>(true).Where(r => !IsCollision(r)).ToArray();
            var lg = go.GetComponent<LODGroup>(); if (lg == null) lg = go.AddComponent<LODGroup>();
            lg.SetLODs(Enumerable.Range(0, 3).Select(i => new LOD(cut[i], kids.Where(r => r.name.EndsWith("_LOD" + i)).ToArray())).ToArray());
            return go;
        }

        static void Inspect(Expect ex)
        {
            var go = Place();
            var b = Box(Level(go, 0, false));
            var d = ex.dims;   // Blender x, y, z → Unity x, z, y
            Check(Mathf.Abs(b.size.x - d[0]) <= .02f && Mathf.Abs(b.size.z - d[1]) <= .02f && Mathf.Abs(b.size.y - d[2]) <= .02f,
                $"{Id}: imported size {b.size.x:0.000} x {b.size.z:0.000} x {b.size.y:0.000} m matches Blender {d[0]} x {d[1]} x {d[2]} within 2 cm");
            Check(Mathf.Abs(b.min.y - ex.min[2]) <= .02f && b.min.y < 0, $"{Id}: lowest point y = {b.min.y:0.000} m (Blender {ex.min[2]}; roots and pit go below the ground)");
            Check(Mathf.Abs(b.center.x) <= .02f && Mathf.Abs(b.center.z) <= .02f, $"{Id}: origin at the bottom centre (footprint centre {b.center.x:0.000}, {b.center.z:0.000})");
            var tris = Enumerable.Range(0, 3).Select(i => Tris(Level(go, i))).ToArray();
            Check(Enumerable.Range(0, 3).All(i => Mathf.Abs(tris[i] - ex.tris[i]) <= ex.tris[i] * .01f),
                $"{Id}: triangles LOD0/1/2 = {tris[0]} / {tris[1]} / {tris[2]} ({100f * tris[1] / tris[0]:0}% / {100f * tris[2] / tris[0]:0}%), Blender {ex.tris[0]} / {ex.tris[1]} / {ex.tris[2]}");
            var objs = Enumerable.Range(0, 3).Select(i => Level(go, i).Length).ToArray();
            Check(objs.All(n => n == 2), $"{Id}: objects per LOD {string.Join(" / ", objs)} (body + Detail_DR11_Plants)");
            var mats = go.GetComponentsInChildren<Renderer>(true).Where(r => !IsCollision(r)).SelectMany(r => r.sharedMaterials).Distinct().Count();
            Check(mats == 2, $"{Id}: {mats} materials (body, two-sided plants)");
            var tex = new[] { "Albedo", "Normal", "ORM", "MaskURP" }.Select(Tex).ToArray();
            Check(tex.All(t => t != null), $"{Id}: Albedo / Normal / ORM / MaskURP found in {TexDir}");
            var src = tex.Where(t => t).Select(t => { ((TextureImporter)AssetImporter.GetAtPath(AssetDatabase.GetAssetPath(t))).GetSourceTextureWidthAndHeight(out int w, out int h); return $"{w}x{h}"; }).Distinct().ToArray();
            Check(src.Length == 1 && src[0] == "2048x2048", $"{Id}: delivered textures {string.Join(", ", src)}");
            foreach (var mf in Level(go, 0).Select(r => r.GetComponent<MeshFilter>().sharedMesh))
                Check(mf.uv.Length == mf.vertexCount && mf.normals.Length == mf.vertexCount, $"{Id}: {mf.name} has UV0 and normals ({mf.vertexCount} vertices)");
            var col = go.GetComponentsInChildren<MeshCollider>(true);
            Check(col.Length == 1, $"{Id}: one collision shell (MeshCollider, renderer off)");
            if (col.Length == 1) Check(Mathf.Abs(Tris(new[] { col[0].GetComponent<Renderer>() }) - ex.col) <= ex.col * .01f, $"{Id}: collision {Tris(new[] { col[0].GetComponent<Renderer>() })} triangles (Blender {ex.col})");
            UnityEngine.Object.DestroyImmediate(go);
            // 1.75 m 走路膠囊（半徑 0.35）從四個方向往中心走：根盤要擋住（在外框內撞到），不能穿過去
            go = Place(); Physics.SyncTransforms();
            float R = Mathf.Max(b.extents.x, b.extents.z) + 3;
            foreach (var dir in new[] { Vector3.right, Vector3.left, Vector3.forward, Vector3.back })
            {
                int hits = 0; string where = "";
                foreach (float s in new[] { -.6f, 0f, .6f })
                {
                    var side = Vector3.Cross(Vector3.up, dir) * s;
                    var p0 = -dir * R + side + Vector3.up * .35f + new Vector3(b.center.x, 0, b.center.z);
                    bool hit = Physics.CapsuleCast(p0, p0 + Vector3.up * 1.05f, .35f, dir, out var h, 2 * R);
                    if (hit && Vector3.Dot(h.point - b.center, dir) < 0) hits++;
                    where += hit ? $" {Vector3.Dot(h.point - b.center, dir):0.00}" : " miss";
                }
                Check(hits == 3, $"{Id}: walker from {(-dir).ToString("0")} blocked on {hits}/3 lines (hit at{where} m from the centre)");
            }
            bool top = Physics.Raycast(new Vector3(b.center.x, 10, b.center.z), Vector3.down, out var ht, 12);
            Report.Add($"INFO {Id}: straight down onto the plate centre hits {(top ? ht.point.y.ToString("0.00") + " m" : "nothing")}");
            UnityEngine.Object.DestroyImmediate(go);
        }

        static Camera cam; static RenderTexture target;
        static void Shots()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            var sun = new GameObject("Sun").AddComponent<Light>(); sun.type = LightType.Directional; sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(50, -35, 0); sun.intensity = 1.25f;
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane); ground.transform.localScale = Vector3.one * 30;
            ground.GetComponent<Renderer>().sharedMaterial = Flat("ground", new Color(.17f, .15f, .12f));
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(.62f, .7f, .78f); RenderSettings.ambientEquatorColor = new Color(.55f, .58f, .52f); RenderSettings.ambientGroundColor = new Color(.32f, .3f, .26f);
            cam = new GameObject("Review Camera").AddComponent<Camera>(); cam.nearClipPlane = .05f; cam.farClipPlane = 600;
            UnityEngine.Rendering.Universal.CameraExtensions.GetUniversalAdditionalCameraData(cam).renderPostProcessing = true;
            target = new RenderTexture(1536, 864, 24) { antiAliasing = 4 }; cam.targetTexture = target;
            cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = new Color(.66f, .70f, .74f);
            var go = Place();
            var ruler = GameObject.CreatePrimitive(PrimitiveType.Capsule); UnityEngine.Object.DestroyImmediate(ruler.GetComponent<Collider>());
            ruler.transform.position = new Vector3(0, .875f, -3.6f); ruler.transform.localScale = new Vector3(.42f, .875f, .42f);
            ruler.GetComponent<Renderer>().sharedMaterial = Flat("ruler", new Color(.85f, .85f, .85f));
            var lg = go.GetComponent<LODGroup>();
            var at = new Vector3(0, 1.1f, 0);
            var views = new (string n, Vector3 from, Vector3 at)[] {
                ("xneg", new Vector3(-9, 1.7f, 0), at), ("xpos", new Vector3(9, 1.7f, 0), at),
                ("zneg", new Vector3(0, 1.7f, -9), at), ("zpos", new Vector3(0, 1.7f, 9), at),
                ("tq", new Vector3(-6.5f, 2.6f, -6.5f), at), ("tq2", new Vector3(-6.5f, 2.6f, 6.5f), at),
                ("top", new Vector3(-.01f, 12, 0), Vector3.zero),
                ("close", new Vector3(-4.6f, 1.3f, -1.2f), new Vector3(-1.2f, .9f, 0)), ("close2", new Vector3(4.6f, 1.3f, 1.2f), new Vector3(1.2f, .9f, 0)) };
            lg.ForceLOD(0);
            foreach (var v in views) Shot(v.n + "-lod0", v.from, v.at, 35);
            for (int i = 1; i < 3; i++) { lg.ForceLOD(i); Shot($"tq-lod{i}", views[4].from, at, 35); Shot($"tq2-lod{i}", views[5].from, at, 35); }
            lg.ForceLOD(1); foreach (var r in go.GetComponentsInChildren<Renderer>(true).Where(IsDetail)) r.enabled = false;
            Shot("tq-lod1-nodetail", views[4].from, at, 35);
            Report.Add($"INFO renders written to art/previews/d2-logs-b/{Id}/unity_{Ver}");
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
