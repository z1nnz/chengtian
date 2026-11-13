using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace YunJing.Editor
{
    // joshsu54's VL01–VL05 village houses (art/exports/village-houses-b, PR #85 and #89) for scene placements.
    // A placement names "Assets/YunJing/Models/VillageHousesB/<id>/<id>_v001.fbx"; the delivered FBX and its textures
    // are copied there (gitignored), the four material slots (Main, Stone, Wood, RoofTiles) get URP materials, the
    // three LODs are grouped and the delivered collision shells become the colliders. Source art stays untouched.
    public static class QingxiVillageHouseKit
    {
        const string Root = "Assets/YunJing/Models/VillageHousesB";
        // #101: the same pipeline also made the VH houses and LT01 (village-houses-b) and the re-skinned Dondon
        // buildings RS01–RS03 (village-reskin-b, their roof slot is "Tile" with its own texture).
        const string Reskin = "Assets/YunJing/Models/VillageReskinB";
        static readonly string[] Slots = { "Main", "Stone", "Wood", "RoofTiles", "Tile" };
        static string RootOf(string model) => model.StartsWith(Reskin + "/") ? Reskin : Root;
        static string ExportsOf(string model) => model.StartsWith(Reskin + "/") ? "art/exports/village-reskin-b" : "art/exports/village-houses-b";
        static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ".."));

        public static bool Owns(string model) => !string.IsNullOrEmpty(model) && (model.StartsWith(Root + "/") || model.StartsWith(Reskin + "/"));

        static string Id(string model) => Path.GetFileName(Path.GetDirectoryName(model));

        public static void Ensure(string model)
        {
            string id = Id(model);
            string src = Path.Combine(Repo, ExportsOf(model), id);
            string root = RootOf(model);
            string dst = Path.Combine(Repo, "apps/game", root, id);
            Directory.CreateDirectory(Path.Combine(dst, "Textures"));
            bool copied = false;
            foreach (var file in new[] { Path.Combine(src, Path.GetFileName(model)) }.Concat(Directory.GetFiles(Path.Combine(src, "Textures"), "*.png")))
            {
                // The game's material needs colour, normal and the packed mask; the separate maps stay in art/.
                if (file.EndsWith("_Roughness.png") || file.EndsWith("_Metallic.png")) continue;
                if (!File.Exists(file)) throw new FileNotFoundException("Delivered house file missing", file);
                if (new FileInfo(file).Length < 1024) throw new InvalidDataException("Still a Git LFS pointer: " + file);
                string to = Path.Combine(dst, file.Substring(src.Length + 1));
                if (File.Exists(to) && new FileInfo(to).Length == new FileInfo(file).Length) continue;
                File.Copy(file, to, true); copied = true;
            }
            if (copied) AssetDatabase.Refresh();
            var importer = AssetImporter.GetAtPath(model) as ModelImporter;
            if (importer == null) throw new FileNotFoundException("House FBX did not import", model);
            if (!importer.bakeAxisConversion || importer.materialImportMode != ModelImporterMaterialImportMode.ImportViaMaterialDescription || importer.importAnimation)
            {
                importer.bakeAxisConversion = true;
                importer.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription;   // keeps the FBX slot names to map onto
                importer.materialLocation = ModelImporterMaterialLocation.InPrefab;
                importer.importAnimation = false; importer.importCameras = false; importer.importLights = false; importer.addCollider = false;
                importer.importNormals = ModelImporterNormals.Import;
                importer.SaveAndReimport();
            }
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { $"{root}/{id}/Textures" }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var ti = AssetImporter.GetAtPath(path) as TextureImporter; if (ti == null) continue;
                bool normal = path.EndsWith("_Normal.png"), data = path.EndsWith("_MetallicSmoothness.png");
                var type = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
                var wrap = path.Contains("VL_RoofTiles_") ? TextureWrapMode.Repeat : TextureWrapMode.Clamp;
                if (ti.textureType == type && ti.sRGBTexture == (!normal && !data) && ti.wrapMode == wrap && ti.maxTextureSize == 2048) continue;
                ti.textureType = type; ti.sRGBTexture = !normal && !data; ti.wrapMode = wrap; ti.maxTextureSize = 2048; ti.mipmapEnabled = true;
                ti.SaveAndReimport();
            }
        }

        // null when the house has no texture set for that slot (LT01 is one material; VL has no "Tile").
        static Material Mat(string root, string id, string slot)
        {
            string prefix = slot == "Main" ? id : slot == "RoofTiles" ? "VL_RoofTiles" : $"{id}_{slot}";
            Texture2D Tex(string kind) => AssetDatabase.LoadAssetAtPath<Texture2D>($"{root}/{id}/Textures/{prefix}_{kind}.png");
            var colour = Tex("BaseColor");
            if (colour == null) return null;
            string path = $"{root}/{id}/{id}_{slot}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) { mat = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(mat, path); }
            mat.SetTexture("_BaseMap", colour); mat.SetColor("_BaseColor", Color.white);
            var normal = Tex("Normal");
            if (normal != null) { mat.SetTexture("_BumpMap", normal); mat.EnableKeyword("_NORMALMAP"); }
            var mask = Tex("MetallicSmoothness");
            if (mask != null) { mat.SetTexture("_MetallicGlossMap", mask); mat.EnableKeyword("_METALLICSPECGLOSSMAP"); mat.SetFloat("_Smoothness", 1); }
            var glow = Tex("Emission");   // lantern flames, forge embers: lit at night by QingxiDayNight through nightGlows where wired
            if (glow != null) { mat.SetTexture("_EmissionMap", glow); mat.SetColor("_EmissionColor", Color.white * .9f); mat.EnableKeyword("_EMISSION"); }
            EditorUtility.SetDirty(mat);
            return mat;
        }

        public static void Prepare(GameObject go, string model)
        {
            string id = Id(model), root = RootOf(model);
            var mats = Slots.ToDictionary(s => s, s => Mat(root, id, s));
            if (mats["Main"] == null) throw new FileNotFoundException("House colour texture missing", $"{root}/{id}/Textures/{id}_BaseColor.png");
            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
            {
                if (r.name.EndsWith("_Collision")) { r.enabled = false; continue; }
                r.sharedMaterials = r.sharedMaterials.Select(m =>
                {
                    string name = m != null ? m.name : "";
                    string slot = Slots.FirstOrDefault(s => name.EndsWith("_" + s));
                    return (slot != null ? mats[slot] : null) ?? mats["Main"];
                }).ToArray();
            }
            var cut = new[] { .1f, .035f, .006f };
            var group = go.GetComponent<LODGroup>(); if (group == null) group = go.AddComponent<LODGroup>();
            group.SetLODs(Enumerable.Range(0, 3).Select(i => new LOD(cut[i],
                go.GetComponentsInChildren<Renderer>(true).Where(r => r.name.EndsWith("_LOD" + i)).ToArray())).ToArray());
            foreach (var shell in go.GetComponentsInChildren<MeshFilter>(true).Where(m => m.name.EndsWith("_Collision")))
                if (shell.GetComponent<MeshCollider>() == null) shell.gameObject.AddComponent<MeshCollider>().sharedMesh = shell.sharedMesh;
        }
    }
}
