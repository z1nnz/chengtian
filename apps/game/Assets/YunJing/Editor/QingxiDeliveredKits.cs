using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace YunJing.Editor
{
    // Core group: two delivered kits placed through the block slots (tools/qingxi-terrain/blocks/*.json).
    //   Day34C: Eli-0731's day 3-4 models (PR #62, art/exports/qingxi-day34-c). Import, materials, LOD and collision
    //           follow his own check (art/source/qingxi-day34-c/unity/QingxiDay34Verify.cs).
    //   RuinsB: joshsu54's ruins kit (PR #57, art/exports/qingxi-world-ruins-b/<asset>/<asset>_v001.fbx).
    // Both are copied into gitignored Assets folders on the first placement that uses them.
    public static class QingxiDeliveredKits
    {
        public const string Day34 = "Assets/YunJing/Models/Day34C", Ruins = "Assets/YunJing/Models/RuinsB";
        static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ".."));
        static bool day34Copied, ruinsCopied;

        public static bool Owns(string model) => model != null && (model.StartsWith(Day34 + "/") || model.StartsWith(Ruins + "/"));

        public static void Ensure(string model)
        {
            if (model.StartsWith(Day34 + "/") && !day34Copied) { CopyDay34(); day34Copied = true; }
            if (model.StartsWith(Ruins + "/") && !ruinsCopied) { CopyRuins(); ruinsCopied = true; }
        }

        // Materials, LOD groups and collision on a placed instance; collision shells are hidden and become mesh colliders.
        public static void Prepare(GameObject go, string model)
        {
            string id = Path.GetFileNameWithoutExtension(model);
            bool day34 = model.StartsWith(Day34 + "/");
            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
            {
                if (r.name.Contains("_Collision") || r.name.StartsWith("UCX_")) { r.enabled = false; continue; }
                if (day34)
                {
                    var group = Regex.Match(r.name, @"^(.+)_LOD\d$");
                    if (group.Success) r.sharedMaterials = Enumerable.Repeat(Day34Mat(id, group.Groups[1].Value), r.sharedMaterials.Length).ToArray();
                }
            }
            foreach (var parent in go.GetComponentsInChildren<Renderer>(true).Where(r => r.name.EndsWith("_LOD0")).Select(r => r.transform.parent).Distinct().ToArray())
            {
                if (parent.GetComponentsInParent<LODGroup>(true).Any(g => g.GetLODs().Any(l => l.renderers.Any(x => x && x.transform.parent == parent)))) continue;
                float[] cut = { .25f, .08f, .015f };
                var kids = parent.Cast<Transform>().Select(t => t.GetComponent<Renderer>()).Where(r => r && r.enabled).ToArray();
                parent.gameObject.AddComponent<LODGroup>().SetLODs(Enumerable.Range(0, 3).Select(i => new LOD(cut[i], kids.Where(r => r.name.EndsWith("_LOD" + i)).ToArray())).ToArray());
            }
            foreach (var col in go.GetComponentsInChildren<MeshFilter>(true).Where(m => m.name.Contains("_Collision") || m.name.StartsWith("UCX_")))
                if (col.GetComponent<MeshCollider>() == null) col.gameObject.AddComponent<MeshCollider>().sharedMesh = col.sharedMesh;
        }

        // ------------------------------------------------------------------ Day34C (Eli-0731)
        static readonly string[] Day34Ids = { "UP01", "UP02_01", "UP02_02", "UP02_03", "UP03", "UP04", "UP05_CushionNew", "UP05_CushionOld", "UP05_Table", "UP05_Burner", "UP06" };

        static void CopyDay34()
        {
            foreach (var id in Day34Ids)
            {
                Copy(Path.Combine(Repo, "art/exports/qingxi-day34-c"), Path.Combine(Repo, "apps/game", Day34, id), id + ".fbx");
                Copy(Path.Combine(Repo, "art/textures/qingxi-day34-c"), Path.Combine(Repo, "apps/game", Day34, id, "Textures"), id + "_*.png");
            }
            AssetDatabase.Refresh();
            ImportModels(Day34, materials: false);
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { Day34 }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var ti = (TextureImporter)AssetImporter.GetAtPath(path);
                bool normal = path.EndsWith("_Normal.png"), linear = normal || path.EndsWith("_MaskURP.png") || path.EndsWith("_ORM.png") || path.EndsWith("_WarmthMask.png");
                var type = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
                bool alpha = path.EndsWith("_Drawing_Albedo.png");
                if (ti.textureType == type && ti.sRGBTexture == !linear && ti.alphaIsTransparency == alpha) continue;
                ti.textureType = type; ti.sRGBTexture = !linear; ti.mipmapEnabled = true; ti.alphaIsTransparency = alpha; ti.SaveAndReimport();
            }
        }

        // One URP Lit per group: Albedo, Normal, MaskURP (R metal, G AO, A smoothness), + Emission; the drawing decal is transparent.
        static Material Day34Mat(string id, string name)
        {
            var dir = $"{Day34}/{id}/Materials"; Directory.CreateDirectory(Path.Combine(Repo, "apps/game", dir));
            var path = $"{dir}/{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) { mat = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(mat, path); }
            Texture2D Tex(string kind) => AssetDatabase.LoadAssetAtPath<Texture2D>($"{Day34}/{id}/Textures/{name}_{kind}.png");
            var albedo = Tex("Albedo"); var mask = Tex("MaskURP"); var normal = Tex("Normal"); var glow = Tex("Emission");
            if (albedo == null) throw new FileNotFoundException("Day34C texture missing", $"{Day34}/{id}/Textures/{name}_Albedo.png");
            mat.SetTexture("_BaseMap", albedo); mat.SetColor("_BaseColor", Color.white);
            if (normal) { mat.SetTexture("_BumpMap", normal); mat.EnableKeyword("_NORMALMAP"); }
            if (mask) { mat.SetTexture("_MetallicGlossMap", mask); mat.EnableKeyword("_METALLICSPECGLOSSMAP"); mat.SetFloat("_Smoothness", 1); mat.SetTexture("_OcclusionMap", mask); mat.EnableKeyword("_OCCLUSIONMAP"); }
            if (glow)
            {
                mat.SetTexture("_EmissionMap", glow); mat.SetColor("_EmissionColor", Color.black); mat.EnableKeyword("_EMISSION");
                mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.RealtimeEmissive;
            }
            if (name.EndsWith("_Drawing"))
            {
                mat.SetFloat("_Surface", 1); mat.SetFloat("_Blend", 0); mat.SetFloat("_ZWrite", 0);
                mat.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha); mat.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
                mat.EnableKeyword("_SURFACE_TYPE_TRANSPARENT"); mat.renderQueue = (int)RenderQueue.Transparent;
            }
            EditorUtility.SetDirty(mat);
            return mat;
        }

        // ------------------------------------------------------------------ RuinsB (joshsu54)
        // Materials are named M_WRB_<asset>_<slot>; textures T_<asset>_<slot>_BaseColor / Normal / ORM (R AO, G roughness).
        static void CopyRuins()
        {
            string kit = Path.Combine(Repo, "art/exports/qingxi-world-ruins-b");
            foreach (var dir in Directory.GetDirectories(kit))
            {
                string asset = Path.GetFileName(dir);
                Copy(dir, Path.Combine(Repo, "apps/game", Ruins, asset), "*.fbx");
                if (Directory.Exists(Path.Combine(dir, "Textures"))) Copy(Path.Combine(dir, "Textures"), Path.Combine(Repo, "apps/game", Ruins, asset, "Textures"), "*.png");
            }
            AssetDatabase.Refresh();
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { Ruins }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var ti = (TextureImporter)AssetImporter.GetAtPath(path);
                bool normal = path.EndsWith("_Normal.png"), linear = normal || path.EndsWith("_ORM.png");
                var type = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
                if (ti.textureType == type && ti.sRGBTexture == !linear && ti.maxTextureSize == 2048) continue;
                ti.textureType = type; ti.sRGBTexture = !linear; ti.maxTextureSize = 2048; ti.SaveAndReimport();
            }
            ImportModels(Ruins, materials: true);
        }

        static Material RuinsMat(string asset, string material)
        {
            string slot = material.Substring($"M_WRB_{asset}_".Length);
            var dir = $"{Ruins}/{asset}/Materials"; Directory.CreateDirectory(Path.Combine(Repo, "apps/game", dir));
            var path = $"{dir}/{material}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) { mat = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(mat, path); }
            var baseColor = AssetDatabase.LoadAssetAtPath<Texture2D>($"{Ruins}/{asset}/Textures/T_{asset}_{slot}_BaseColor.png");
            var normal = AssetDatabase.LoadAssetAtPath<Texture2D>($"{Ruins}/{asset}/Textures/T_{asset}_{slot}_Normal.png");
            if (baseColor) mat.SetTexture("_BaseMap", baseColor);
            mat.SetColor("_BaseColor", Color.white); mat.SetFloat("_Smoothness", .18f);
            if (normal) { mat.SetTexture("_BumpMap", normal); mat.EnableKeyword("_NORMALMAP"); }
            EditorUtility.SetDirty(mat);
            return mat;
        }

        // ------------------------------------------------------------------ shared
        static void ImportModels(string folder, bool materials)
        {
            foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { folder }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var importer = (ModelImporter)AssetImporter.GetAtPath(path);
                importer.bakeAxisConversion = true; importer.importCameras = false; importer.importLights = false;
                importer.addCollider = false; importer.importAnimation = false;
                if (!materials) importer.materialImportMode = ModelImporterMaterialImportMode.None;
                else
                {
                    string asset = Path.GetFileName(Path.GetDirectoryName(path));
                    importer.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription;
                    importer.materialLocation = ModelImporterMaterialLocation.InPrefab;
                    foreach (var name in AssetDatabase.LoadAllAssetsAtPath(path).OfType<Material>().Select(m => m.name).Distinct().ToArray())
                        if (name.StartsWith($"M_WRB_{asset}_"))
                            importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material), name), RuinsMat(asset, name));
                }
                importer.SaveAndReimport();
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
                if (!File.Exists(target) || new FileInfo(target).Length != new FileInfo(file).Length) File.Copy(file, target, true);
            }
        }
    }
}
