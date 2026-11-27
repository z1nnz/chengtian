using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace YunJing.Editor
{
    // D2 古樹神木 Unity v1（Claude Code, 11/26）。
    // Blender（bark-sample/d2_plan.py + d2_unity_export.py）匯出：
    //   Assets/YunJing/Models/D2/D2P_*.fbx  重複擺放的原型（蕨、草、石頭、樹…），每種最多三級 LOD
    //   Assets/YunJing/Models/D2/D2C_*.fbx  獨立物件，每 50 m 一格合併（世界座標）
    //   Assets/YunJing/Models/D2/D2B_*.fbx  超過 40 萬面、單獨減面的大物件（神木樹幹…）
    //   Assets/YunJing/Models/D2/D2_layout.json  原型擺放、六個鏡頭、太陽方向、霧色（座標已換成 Unity：Blender (x,y,z) → (x,z,y)）
    // 顏色在 Blender 烘進頂點色，材質全部用 YunJing/D2VertexColour。
    // 批次：Unity.exe -batchmode -projectPath apps/game -executeMethod YunJing.Editor.D2SceneBuilder.BuildAndCapture -quit -logFile <log>
    public static class D2SceneBuilder
    {
        const string Root = "Assets/YunJing/Models/D2";
        const string ScenePath = "Assets/YunJing/Generated/D2_GodTreeGrove.unity";
        const string MatPath = "Assets/YunJing/Models/D2/D2_VertexColour.mat";
        const string CaptureDir = "Captures/D2";   // apps/game/Captures/D2（不進 Assets、不進 git）
        const bool OldFog = false;
        const bool OldPost = true;   // 11/28 專案的 Renderer 沒有 postProcessData（全隊共用）→ 後製不生效；改在 shader 調色（_Grade）   // true = 11/28 以前：沒有後製調色（Blender 是 AgX 中高對比 → Unity 看起來灰、平）
        const float PostExposure = .35f, PostContrast = 18f, PostSaturation = 8f, PostWarm = 8f;
        const bool OldLod = false;   // true = 11/26 版的原型 LOD 切換距離   // true = 11/26 版的霧（指數平方 .011）

        [Serializable] class Proto { public string name; public string fbx; public string[] lods; public int tris; public int count; }
        [Serializable] class Inst { public string proto; public float[] pos; public float[] rot; public float[] scl; }
        [Serializable] class Cell { public string fbx; public int tris; public int objects; }
        [Serializable] class Hero { public string fbx; public string[] lods; public string mode; public string albedo; public string normal; public string[] albedos; public string[] normals; public float[] triObj; public float[] triScale; public float triBlend; public float normalStrength; public float[] barkMean; public float barkLift; public int tris; public int objects; }
        [Serializable] class Cam { public string name; public float[] pos; public float[] target; public float vfov; }
        [Serializable] class Layout { public Proto[] prototypes; public Inst[] instances; public Cell[] cells; public Hero[] heroes; public Cam[] cameras; public float[] sunDir; public float[] fogColour; }

        // FBX 匯入後網格還是 Blender 的 Z 朝上，靠模型裡的節點旋轉擺正 → 連節點的相對變換一起帶出來
        struct Part { public Mesh mesh; public Matrix4x4 local; }

        static string AssetPath(string fbx) => (Root + "/" + fbx);

        public static void Diag()
        {
            FixImporters();
            foreach (var f in new[] { "D2C_0_0.fbx", "D2P_STC0.fbx", "D2P_UG_fern0.fbx", "D2B_GT01_GodTree_Wood_LOD0.fbx" })
            {
                var go = AssetDatabase.LoadAssetAtPath<GameObject>(AssetPath(f));
                Debug.Log($"D2_DIAG root {f} rot={go.transform.localEulerAngles} scale={go.transform.localScale} children={go.transform.childCount}");
                foreach (var mf in go.GetComponentsInChildren<MeshFilter>(true))
                    Debug.Log($"D2_DIAG   mf {mf.name} localPos={mf.transform.localPosition} localRot={mf.transform.localEulerAngles} localScale={mf.transform.localScale} meshBounds={mf.sharedMesh.bounds}");
            }
            EditorSceneManager.OpenScene(ScenePath);
            foreach (var r in UnityEngine.Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None))
                if (r.name.StartsWith("D2C_0_0") || r.name.StartsWith("D2B_GT01_GodTree_Wood") || (r.transform.parent && r.transform.parent.name == "STC0" && UnityEngine.Random.value < .002f))
                    Debug.Log($"D2_DIAG world {r.name} bounds={r.bounds}");
        }

        [MenuItem("YunJing/D2/Build scene")]
        public static void Build() => BuildScene();

        [MenuItem("YunJing/D2/Build scene and capture six views")]
        public static void BuildAndCapture()
        {
            var layout = BuildScene();
            Capture(layout);
        }

        static Layout BuildScene()
        {
            FixImporters();
            var layout = JsonUtility.FromJson<Layout>(File.ReadAllText(AssetPath("D2_layout.json")));
            var mat = AssetDatabase.LoadAssetAtPath<Material>(MatPath);
            if (mat == null)
            {
                mat = new Material(Shader.Find("YunJing/D2VertexColour")) { enableInstancing = true };
                AssetDatabase.CreateAsset(mat, MatPath);
            }

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("D2_GodTreeGrove").transform;

            long cellTris = 0;
            var cells = new GameObject("Cells").transform; cells.SetParent(root, false);
            foreach (var c in layout.cells)
                foreach (var part in Meshes(c.fbx))
                {
                    Make(cells, Path.GetFileNameWithoutExtension(c.fbx), part, mat, true);
                    cellTris += part.mesh.GetIndexCount(0) / 3;
                }

            // 主角物件（拱門、神木樹幹、祭壇、LG01）：自己的底色＋法線貼圖
            if (layout.heroes != null)
            {
                var heroes = new GameObject("Heroes").transform; heroes.SetParent(root, false);
                foreach (var hero in layout.heroes)
                {
                    var hname = Path.GetFileNameWithoutExtension(hero.fbx);
                    var albs = hero.albedos != null && hero.albedos.Length > 0 ? hero.albedos : new[] { hero.albedo };
                    var nrms = hero.normals != null && hero.normals.Length > 0 ? hero.normals : new[] { hero.normal };
                    var hms = new Material[albs.Length];
                    for (int k = 0; k < albs.Length; k++)   // 拱門：一個材質槽（子網格）一組貼圖
                    {
                        var hm = new Material(Shader.Find("YunJing/D2VertexColour"));
                        hm.SetTexture("_MainTex", AssetDatabase.LoadAssetAtPath<Texture2D>(AssetPath(albs[k])));
                        hm.SetTexture("_BumpMap", AssetDatabase.LoadAssetAtPath<Texture2D>(AssetPath(nrms[k])));
                        if (hero.mode == "tri" || hero.mode == "tile")   // 神木：跟 Blender 一樣的盒投影樹皮；V6 拱門：同一張樹皮用自己的 UV 鋪
                        {
                            if (hero.mode == "tri") { hm.EnableKeyword("_TRI"); hm.SetFloat("_Tri", 1); }
                            else { hm.EnableKeyword("_TILE"); hm.SetFloat("_Tile", 1); }
                            for (int r = 0; r < 3; r++)   // 材質不會存矩陣 → 三列向量
                                hm.SetVector("_TriRow" + r, new Vector4(hero.triObj[r * 4], hero.triObj[r * 4 + 1], hero.triObj[r * 4 + 2], hero.triObj[r * 4 + 3]));
                            hm.SetVector("_TriScale", new Vector4(hero.triScale[0], hero.triScale[1], hero.triScale[2], 0));
                            hm.SetFloat("_TriBlend", hero.triBlend); hm.SetFloat("_BumpScale", hero.normalStrength);
                            hm.SetVector("_BarkMean", new Vector4(hero.barkMean[0], hero.barkMean[1], hero.barkMean[2], 0));
                            hm.SetFloat("_BarkLift", hero.barkLift);
                        }
                        else { hm.EnableKeyword("_HERO"); hm.SetFloat("_Hero", 1); }
                        var mp = AssetPath(hname + (albs.Length > 1 ? "_" + k : "") + ".mat");
                        AssetDatabase.DeleteAsset(mp); AssetDatabase.CreateAsset(hm, mp);
                        hms[k] = hm;
                    }
                    if (hero.lods == null || hero.lods.Length <= 1)
                    {
                        foreach (var part in Meshes(hero.fbx)) Make(heroes, hname, part, hms[0], true, hms);
                    }
                    else   // 神木：近看高面數、遠處換減面版（同一套貼圖）
                    {
                        var hold = new GameObject(hname).transform; hold.SetParent(heroes, false);
                        float[] th = { .25f, .08f, .01f };
                        var la = new LOD[hero.lods.Length];
                        for (int li = 0; li < hero.lods.Length; li++)
                        {
                            var rs = new List<Renderer>();
                            foreach (var part in Meshes(hero.lods[li])) rs.Add(Make(hold, "LOD" + li, part, hms[0], true, hms));
                            la[li] = new LOD(th[Mathf.Min(li, th.Length - 1)], rs.ToArray());
                        }
                        var lg = hold.gameObject.AddComponent<LODGroup>(); lg.SetLODs(la); lg.RecalculateBounds();
                    }
                }
            }

            // 每種原型最多三級（LOD0 原模型、LOD1 約 12%、LOD2 約 3%）
            var protoLods = new Dictionary<string, List<List<Part>>>();
            foreach (var p in layout.prototypes)
            {
                var lods = new List<List<Part>>();
                foreach (var f in (p.lods != null && p.lods.Length > 0 ? p.lods : new[] { p.fbx }))
                {
                    var parts = Meshes(f);
                    if (parts.Count > 0) lods.Add(parts);
                }
                protoLods[p.name] = lods;
            }
            var inst = new GameObject("Instances").transform; inst.SetParent(root, false);
            var groups = new Dictionary<string, Transform>();
            int n = 0;
            float[] h = OldLod ? new[] { .12f, .03f, .004f } : new[] { .06f, .015f, .002f };   // 11/28 晚一點才換減面版（V1 遠處樹冠、V5 灰色十字樹）
            foreach (var i in layout.instances)
            {
                if (!protoLods.TryGetValue(i.proto, out var lods) || lods.Count == 0) continue;
                if (!groups.TryGetValue(i.proto, out var g)) { g = new GameObject(i.proto).transform; g.SetParent(inst, false); groups[i.proto] = g; }
                var holder = new GameObject(i.proto).transform; holder.SetParent(g, false);
                holder.SetPositionAndRotation(new Vector3(i.pos[0], i.pos[1], i.pos[2]), new Quaternion(i.rot[0], i.rot[1], i.rot[2], i.rot[3]));
                holder.localScale = new Vector3(i.scl[0], i.scl[1], i.scl[2]);
                if (lods.Count == 1)
                {
                    foreach (var m in lods[0]) Make(holder, "LOD0", m, mat, false);
                }
                else
                {
                    var lodArr = new LOD[lods.Count];
                    for (int li = 0; li < lods.Count; li++)
                    {
                        var rs = new List<Renderer>();
                        foreach (var m in lods[li]) rs.Add(Make(holder, "LOD" + li, m, mat, false));
                        lodArr[li] = new LOD(h[Mathf.Min(li, h.Length - 1)], rs.ToArray());
                    }
                    var lg = holder.gameObject.AddComponent<LODGroup>(); lg.SetLODs(lodArr); lg.RecalculateBounds();
                }
                n++;
            }

            // 光：太陽（Blender d2_plan 的方向）、霧天的天光環境色、URP 指數霧
            var sunGo = new GameObject("Sun"); sunGo.transform.SetParent(root, false);
            var sun = sunGo.AddComponent<Light>(); sun.type = LightType.Directional; sun.intensity = 1.6f;
            sun.color = new Color(1f, .96f, .9f); sun.shadows = LightShadows.Soft;
            sunGo.transform.rotation = Quaternion.LookRotation(new Vector3(layout.sunDir[0], layout.sunDir[1], layout.sunDir[2]));
            RenderSettings.sun = sun;
            var fogC = new Color(layout.fogColour[0], layout.fogColour[1], layout.fogColour[2]);
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = fogC * 1.05f;
            RenderSettings.ambientEquatorColor = fogC * .8f;
            RenderSettings.ambientGroundColor = new Color(.18f, .17f, .14f);
            RenderSettings.fog = true; RenderSettings.fogColor = fogC;
            if (OldFog) { RenderSettings.fogMode = FogMode.ExponentialSquared; RenderSettings.fogDensity = .011f; }
            else { RenderSettings.fogMode = FogMode.Exponential; RenderSettings.fogDensity = .003f; }   // 11/27 照 Blender 的體積霧（密度 .003／m）；指數平方在 Linear 下太濃
            RenderSettings.skybox = null;
            if (!OldPost)   // 11/28 只作用在 D2 場景的後製：色調映射＋對比＋微暖（對照 Blender AgX Medium High Contrast）
            {
                const string pp = "Assets/YunJing/Generated/D2_Post.asset";
                AssetDatabase.DeleteAsset(pp);
                var prof = ScriptableObject.CreateInstance<VolumeProfile>();
                AssetDatabase.CreateAsset(prof, pp);
                var tm = prof.Add<Tonemapping>(true); tm.mode.Override(TonemappingMode.ACES);
                var ca = prof.Add<ColorAdjustments>(true);
                ca.postExposure.Override(PostExposure); ca.contrast.Override(PostContrast); ca.saturation.Override(PostSaturation);
                var wb = prof.Add<WhiteBalance>(true); wb.temperature.Override(PostWarm);
                foreach (var c in prof.components) AssetDatabase.AddObjectToAsset(c, prof);
                AssetDatabase.SaveAssets();
                var vgo = new GameObject("D2_PostVolume"); vgo.transform.SetParent(root, false);
                var vol = vgo.AddComponent<Volume>(); vol.isGlobal = true; vol.sharedProfile = prof;
            }

            var camRoot = new GameObject("Cameras").transform; camRoot.SetParent(root, false);
            foreach (var c in layout.cameras)
            {
                var go = new GameObject("Cam_" + c.name); go.transform.SetParent(camRoot, false);
                var cam = go.AddComponent<Camera>();
                go.transform.position = new Vector3(c.pos[0], c.pos[1], c.pos[2]);
                go.transform.LookAt(new Vector3(c.target[0], c.target[1], c.target[2]));
                cam.fieldOfView = c.vfov; cam.nearClipPlane = .1f; cam.farClipPlane = 3000;
                cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = GradeBg(fogC);   // 天空背景也套 shader 的調色，地平線才接得起來
                if (!OldPost) { var cd = go.AddComponent<UniversalAdditionalCameraData>(); cd.renderPostProcessing = true; cam.allowHDR = true; }
                go.SetActive(c.name == "V3");
            }

            Directory.CreateDirectory(Path.GetDirectoryName(ScenePath));
            EditorSceneManager.SaveScene(scene, ScenePath);
            Debug.Log($"D2_BUILT cells={layout.cells.Length} cellTris={cellTris} protos={layout.prototypes.Length} instances={n} -> {ScenePath}");
            return layout;
        }

        // 跟 D2VertexColour.shader 的 _Grade 同一套（預設值也要一致）
        static Color GradeBg(Color c)
        {
            var l = c.linear; var v = new Vector3(l.r, l.g, l.b) * Mathf.Pow(2, .25f);
            for (int k = 0; k < 3; k++) v[k] = .18f * Mathf.Pow(Mathf.Max(v[k], 1e-5f) / .18f, 1.15f);
            float lum = Vector3.Dot(v, new Vector3(.2126f, .7152f, .0722f));
            v = Vector3.Max(Vector3.zero, Vector3.LerpUnclamped(new Vector3(lum, lum, lum), v, 1.05f));
            v = Vector3.Scale(v, new Vector3(1.03f, 1, .97f));
            for (int k = 0; k < 3; k++) v[k] = v[k] / (1 + Mathf.Max(0, v[k] - .8f) * .5f);
            return new Color(v.x, v.y, v.z).gamma;
        }

        static void Capture(Layout layout)
        {
            Directory.CreateDirectory(CaptureDir);
            var rt = new RenderTexture(1536, 1024, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            var camRoot = GameObject.Find("D2_GodTreeGrove")?.transform.Find("Cameras");   // 關著的物件 GameObject.Find 找不到 → 從根往下找
            foreach (var c in layout.cameras)
            {
                var camT = camRoot != null ? camRoot.Find("Cam_" + c.name) : null;
                if (camT == null) continue;
                var go = camT.gameObject;
                go.SetActive(true);
                var cam = go.GetComponent<Camera>();
                cam.targetTexture = rt; cam.Render();
                RenderTexture.active = rt;
                var tex = new Texture2D(rt.width, rt.height, TextureFormat.RGB24, false);
                tex.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0); tex.Apply();
                File.WriteAllBytes(Path.Combine(CaptureDir, $"D2_unity_{c.name}.png"), tex.EncodeToPNG());
                RenderTexture.active = null; cam.targetTexture = null;
                UnityEngine.Object.DestroyImmediate(tex);
                go.SetActive(c.name == "V3");
                Debug.Log("D2_CAPTURED " + c.name);
            }
            rt.Release();
        }

        static Renderer Make(Transform parent, string name, Part part, Material mat, bool isStatic, Material[] matArr = null)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = part.local.GetColumn(3);
            go.transform.localRotation = part.local.rotation;
            go.transform.localScale = part.local.lossyScale;
            go.AddComponent<MeshFilter>().sharedMesh = part.mesh;
            var r = go.AddComponent<MeshRenderer>();
            // 合併網格有多個子網格（Blender 每個材質一個）；每個子網格都要給材質，不然只畫第一個
            var mats = new Material[Mathf.Max(1, part.mesh.subMeshCount)];
            for (int k = 0; k < mats.Length; k++) mats[k] = matArr != null && k < matArr.Length ? matArr[k] : mat;
            r.sharedMaterials = mats;
            r.shadowCastingMode = ShadowCastingMode.On; r.receiveShadows = true;
            if (isStatic) GameObjectUtility.SetStaticEditorFlags(go, StaticEditorFlags.BatchingStatic | StaticEditorFlags.OccluderStatic);
            return r;
        }

        static List<Part> Meshes(string fbx)
        {
            var list = new List<Part>();
            var go = AssetDatabase.LoadAssetAtPath<GameObject>(AssetPath(fbx));
            if (go != null)
                foreach (var mf in go.GetComponentsInChildren<MeshFilter>(true))
                    if (mf.sharedMesh != null)
                        list.Add(new Part { mesh = mf.sharedMesh, local = mf.transform.localToWorldMatrix });
            if (list.Count == 0) Debug.LogWarning("D2 no mesh in " + fbx);
            return list;
        }

        static void FixImporters()
        {
            AssetDatabase.Refresh();
            foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { Root }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                if (!(AssetImporter.GetAtPath(path) is ModelImporter im)) continue;
                bool dirty = !im.bakeAxisConversion || im.materialImportMode != ModelImporterMaterialImportMode.None || im.importAnimation
                             || im.indexFormat != ModelImporterIndexFormat.UInt32 || im.importBlendShapes || im.importCameras || im.importLights;
                if (!dirty) continue;
                im.bakeAxisConversion = true;   // 所有 D2 模型都要一樣（擺放的座標換算以此為準）
                im.materialImportMode = ModelImporterMaterialImportMode.None;
                im.importAnimation = false; im.animationType = ModelImporterAnimationType.None;
                im.indexFormat = ModelImporterIndexFormat.UInt32; im.importBlendShapes = false; im.importCameras = false; im.importLights = false;
                im.SaveAndReimport();
            }
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { Root }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                if (!(AssetImporter.GetAtPath(path) is TextureImporter ti)) continue;
                bool nrm = path.EndsWith("_Normal.png");
                var want = nrm ? TextureImporterType.NormalMap : TextureImporterType.Default;
                if (ti.textureType == want && ti.maxTextureSize == 4096 && ti.sRGBTexture == !nrm) continue;
                ti.textureType = want; ti.sRGBTexture = !nrm; ti.maxTextureSize = 4096; ti.mipmapEnabled = true;
                ti.SaveAndReimport();
            }
        }
    }
}
