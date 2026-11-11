using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace YunJing.Editor
{
    // A4 東坡茶田 from joshsu54's tea terraces (art/exports/tea-terraces-b, PR #66/#74): six rows of TE01 terrace walls
    // climbing north-east, TE02 tea hedges on each tread, TE03 stairs up the middle and the TE05 pavilion on the
    // knoll above. Import, materials, LODs and collision follow his own check (TeaTerracesModelCheck); the models are
    // copied into a gitignored folder. The terrain under each row is levelled by the `flats` in blocks/A4.json, which
    // tools/qingxi-terrain/make-a4.py writes from the same numbers as Rows below; change both together.
    public static class QingxiTeaTerraceKit
    {
        const string Root = "Assets/YunJing/Models/TeaTerracesB";
        static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ".."));
        static string Exports => Path.Combine(Repo, "art", "exports", "tea-terraces-b");

        // Row k: modules from x = X0 + Shift*k, eight metres each, fronts at Z0 + 4k, lower soil at Base + k (TE01: origin on
        // the lower soil at the footprint centre, the wall's front 2 m south of it, the tread 1 m up).
        public const int Rows = 6, Modules = 5;
        public const float X0 = 64f, Shift = 4f, Z0 = -26f, Base = 1.2f; public const int StairX = 3;   // StairX: which module (0-based) carries the stair
        public static float Front(int row) => Z0 + 4 * row;
        public static float Lower(int row) => Base + row;
        public static float ModuleX(int row, int i) => X0 + Shift * row + 8 * i + 4;
        public static readonly Vector3 Pavilion = new Vector3(122f, 0, 22f);
        public const float PavilionHeight = 8.6f;

        static readonly Dictionary<string, string> ver = new Dictionary<string, string>();
        static string Ver(string id)
        {
            if (ver.TryGetValue(id, out var v)) return v;
            var txt = File.ReadAllText(Path.Combine(Exports, id, "model_info.json")); int at = txt.IndexOf("\"version\""); v = "v001";
            if (at >= 0) { int q1 = txt.IndexOf('"', txt.IndexOf(':', at) + 1), q2 = txt.IndexOf('"', q1 + 1); v = txt.Substring(q1 + 1, q2 - q1 - 1); }
            return ver[id] = v;
        }
        static string Fbx(string id) => $"{Root}/{id}/{id}_{Ver(id)}.fbx";
        static readonly HashSet<string> ready = new HashSet<string>();

        static void Ensure(string id)
        {
            if (ready.Contains(id)) return;
            var src = Path.Combine(Exports, id); var dst = Path.Combine(Repo, "apps", "game", Root, id);
            if (!Directory.Exists(src)) throw new DirectoryNotFoundException(src);
            Directory.CreateDirectory(Path.Combine(dst, "Textures"));
            bool copied = false;
            foreach (var file in Directory.GetFiles(src, $"{id}_{Ver(id)}.fbx").Concat(Directory.GetFiles(Path.Combine(src, "Textures"), "*.png")))
            {
                if (file.EndsWith("_Roughness.png") || file.EndsWith("_Metallic.png")) continue;
                if (new FileInfo(file).Length < 1024) throw new InvalidDataException("Still a Git LFS pointer: " + file);
                var to = Path.Combine(dst, file.Substring(src.Length + 1));
                if (File.Exists(to) && new FileInfo(to).Length == new FileInfo(file).Length) continue;
                File.Copy(file, to, true); copied = true;
            }
            if (copied) AssetDatabase.Refresh();
            var importer = AssetImporter.GetAtPath(Fbx(id)) as ModelImporter;
            if (importer == null) throw new FileNotFoundException("Tea terrace FBX did not import", Fbx(id));
            if (!importer.bakeAxisConversion || importer.materialImportMode != ModelImporterMaterialImportMode.None)
            {
                importer.bakeAxisConversion = true; importer.materialImportMode = ModelImporterMaterialImportMode.None;
                importer.importAnimation = false; importer.importCameras = false; importer.importLights = false; importer.addCollider = false;
                importer.importNormals = ModelImporterNormals.Import; importer.SaveAndReimport();
            }
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { $"{Root}/{id}/Textures" }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var ti = AssetImporter.GetAtPath(path) as TextureImporter; if (ti == null) continue;
                bool normal = path.EndsWith("_Normal.png"), data = path.EndsWith("_MetallicSmoothness.png");
                bool leaf = path.EndsWith("TE02_LeafCards_BaseColor.png");
                var type = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
                if (ti.textureType == type && ti.sRGBTexture == (!normal && !data) && ti.maxTextureSize == 2048 && (!leaf || ti.mipMapsPreserveCoverage)) continue;
                ti.textureType = type; ti.sRGBTexture = !normal && !data; ti.maxTextureSize = 2048;
                if (leaf) { ti.alphaSource = TextureImporterAlphaSource.FromInput; ti.alphaIsTransparency = true; ti.mipMapsPreserveCoverage = true; ti.alphaTestReferenceValue = .5f; }
                ti.SaveAndReimport();
            }
            ready.Add(id);
        }

        static Texture2D Tex(string id, string file) => AssetDatabase.LoadAssetAtPath<Texture2D>($"{Root}/{id}/Textures/{file}");

        static Material Mat(string id)
        {
            var path = $"{Root}/{id}/{id}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) { mat = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(mat, path); }
            mat.SetTexture("_BaseMap", Tex(id, id + "_BaseColor.png")); mat.SetColor("_BaseColor", Color.white);
            var n = Tex(id, id + "_Normal.png"); if (n != null) { mat.SetTexture("_BumpMap", n); mat.EnableKeyword("_NORMALMAP"); }
            var m = Tex(id, id + "_MetallicSmoothness.png"); if (m != null) { mat.SetTexture("_MetallicGlossMap", m); mat.EnableKeyword("_METALLICSPECGLOSSMAP"); mat.SetFloat("_Smoothness", 1); }
            EditorUtility.SetDirty(mat); return mat;
        }

        static Material LeafMat(string id)
        {
            var path = $"{Root}/{id}/{id}_LeafCards.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) { mat = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(mat, path); }
            mat.SetTexture("_BaseMap", Tex(id, "TE02_LeafCards_BaseColor.png"));
            mat.SetColor("_BaseColor", new Color(.8f, .84f, .78f));   // a little less vivid than the paint, like the valley trees (11/11)
            var n = Tex(id, "TE02_LeafCards_Normal.png"); if (n != null) { mat.SetTexture("_BumpMap", n); mat.EnableKeyword("_NORMALMAP"); }
            mat.SetFloat("_AlphaClip", 1); mat.SetFloat("_Cutoff", .5f); mat.EnableKeyword("_ALPHATEST_ON");
            mat.SetFloat("_Cull", (float)CullMode.Off); mat.SetFloat("_Smoothness", .2f); mat.SetFloat("_Metallic", 0);
            mat.SetOverrideTag("RenderType", "TransparentCutout"); mat.renderQueue = (int)RenderQueue.AlphaTest;
            EditorUtility.SetDirty(mat); return mat;
        }

        static GameObject Place(Transform parent, string id, Vector3 at, float yaw, bool mirror = false)
        {
            Ensure(id);
            var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Fbx(id)));
            PrefabUtility.UnpackPrefabInstance(go, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            go.name = id + " (joshsu54, tea-terraces-b)";
            go.transform.SetParent(parent, false);
            go.transform.position = at; go.transform.rotation = Quaternion.Euler(0, yaw, 0);
            if (mirror) go.transform.localScale = new Vector3(-1, 1, 1);
            var mat = Mat(id); var leaf = id.StartsWith("TE02") ? LeafMat(id) : null;
            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
            {
                if (r.name.EndsWith("_Collision")) { r.enabled = false; continue; }
                var m = r.name.Contains("_Leaves_LOD") ? leaf : mat;
                r.sharedMaterials = Enumerable.Repeat(m, r.sharedMaterials.Length).ToArray();
            }
            if (go.GetComponent<LODGroup>() == null)
            {
                float[] cut = id.StartsWith("TE01") || id.StartsWith("TE05") ? new[] { .2f, .06f, .01f } : new[] { .12f, .04f, .008f };
                go.AddComponent<LODGroup>().SetLODs(Enumerable.Range(0, 3).Select(i => new LOD(cut[i], go.GetComponentsInChildren<Renderer>(true).Where(r => r.name.EndsWith("_LOD" + i)).ToArray())).ToArray());
            }
            foreach (var col in go.GetComponentsInChildren<MeshFilter>(true).Where(m => m.name.EndsWith("_Collision")))
                if (col.GetComponent<MeshCollider>() == null) col.gameObject.AddComponent<MeshCollider>().sharedMesh = col.sharedMesh;
            return go;
        }

        public static void Build(Transform parent)
        {
            var root = new GameObject("TeaTerraces (joshsu54 tea-terraces-b)").transform; root.SetParent(parent, false);
            var rng = new System.Random(20261111);
            string[] bushes = { "TE02_Round", "TE02_Wide", "TE02_Tall" };
            for (int row = 0; row < Rows; row++)
            {
                float z = Front(row) + 2, y = Lower(row);
                for (int i = 0; i < Modules; i++)
                {
                    float x = ModuleX(row, i);
                    // the east end tapers down to the ground (TE01_End); the west end is the same piece mirrored
                    string id = i == Modules - 1 ? "TE01_End" : i == 0 ? "TE01_End" : (row + i) % 3 == 0 ? "TE01_Broken" : (row + i) % 2 == 0 ? "TE01_StraightA" : "TE01_StraightB";
                    if (row == 0 && i == 2) id = "TE01_StraightA";   // the first wall seen from the village stays whole
                    Place(root, id, new Vector3(x, y, z), 0, mirror: i == 0);
                    // tea on the planting ridge, 0.95 m behind the wall line; a gap where the stair comes up from the row below
                    for (int k = 0; k < 4; k++)
                    {
                        float bx = x - 3 + 2 * k;
                        float gapX = row < Rows - 1 ? ModuleX(row + 1, StairX) : ModuleX(row, StairX);   // the top row lets the path out to the pavilion
                        if (Mathf.Abs(bx - gapX) < 1.6f) continue;
                        if ((i == 0 && k == 0) || (i == Modules - 1 && k == 3)) continue;   // the tapered ends carry no hedge
                        bool single = rng.NextDouble() < .18;
                        if (single) Place(root, bushes[rng.Next(bushes.Length)], new Vector3(bx + (float)rng.NextDouble() * .4f - .2f, y + 1.17f, z + .95f), (float)rng.NextDouble() * 360);
                        else Place(root, "TE02_Hedge", new Vector3(bx, y + 1.17f, z + .95f), 0);
                    }
                }
                // a stair up the front of every row but the first, on the same module column
                if (row > 0) Place(root, "TE03_Stair", new Vector3(ModuleX(row, StairX), y, Front(row)), 0);
            }
            Place(root, "TE03_Stair", new Vector3(ModuleX(0, StairX), Lower(0), Front(0)), 0);
            // baskets and a drying tray left on the treads
            Place(root, "TE04_Basket", new Vector3(ModuleX(1, 1) + 1.3f, Lower(1) + 1.02f, Front(1) + 3.3f), 30);
            Place(root, "TE04_Basket", new Vector3(ModuleX(3, 2) - 2.1f, Lower(3) + 1.02f, Front(3) + 3.4f), -50);
            Place(root, "TE04_Tray", new Vector3(ModuleX(2, 3) + 2.4f, Lower(2) + 1.02f, Front(2) + 3.3f), 10);
            // the pavilion on the knoll, open to the south-west (back to the village and the creek)
            Place(root, "TE05_Pavilion", new Vector3(Pavilion.x, PavilionHeight, Pavilion.z), 225);
        }
    }
}
