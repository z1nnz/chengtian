using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;

namespace YunJing.Editor
{
    // Imports only the delivered model requested by a scene placement. Source art stays untouched.
    public static class QingxiScenePropKits
    {
        const string World = "Assets/YunJing/Models/WorldPropsA";
        const string Day12 = "Assets/YunJing/Models/Day12C";
        const string Creek = "Assets/YunJing/Models/CreekRepairB";
        const string Basics = "Assets/YunJing/Models/ModellingBasicsC";
        const string Creekside = "Assets/YunJing/Models/CreeksideC";   // Eli-0731 #88, #93: WL washing and FI fishing props, one material each
        const string Core = "Assets/YunJing/Models/CoreRuins";   // core team: art/exports/core-ruins-v1/<id>/, textures in art/textures/core-ruins-v1
        static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ".."));

        public static bool Owns(string model) => !string.IsNullOrEmpty(model) &&
            (model.StartsWith(World + "/") || model.StartsWith(Day12 + "/") || model.StartsWith(Creek + "/") || model.StartsWith(Basics + "/") || model.StartsWith(Core + "/") || model.StartsWith(Creekside + "/"));

        public static void Ensure(string model)
        {
            string id = Path.GetFileName(Path.GetDirectoryName(model));
            string folder = model.StartsWith(World + "/") ? World : model.StartsWith(Day12 + "/") ? Day12 :
                model.StartsWith(Basics + "/") ? Basics : model.StartsWith(Core + "/") ? Core : model.StartsWith(Creekside + "/") ? Creekside : Creek;
            string target = Path.Combine(Repo, "apps/game", folder, id);
            string source = folder == World ? Path.Combine(Repo, "art/exports/world-props-a") :
                folder == Day12 ? Path.Combine(Repo, "art/exports/qingxi-day12-c") :
                folder == Basics ? Path.Combine(Repo, "art/exports/modelling-basics-c") :
                folder == Core ? Path.Combine(Repo, "art/exports/core-ruins-v1", id) :
                folder == Creekside ? Path.Combine(Repo, "art/exports/creekside-life-c") :
                Path.Combine(Repo, "art/exports/creek-repair-b", id);
            Copy(Path.Combine(source, Path.GetFileName(model)), Path.Combine(target, Path.GetFileName(model)));
            string textures = folder == World ? Path.Combine(Repo, "art/textures/world-props-a") :
                folder == Day12 ? Path.Combine(Repo, "art/textures/qingxi-day12-c") :
                folder == Basics ? Path.Combine(Repo, "art/textures/modelling-basics-c") :
                folder == Core ? Path.Combine(Repo, "art/textures/core-ruins-v1") :
                folder == Creekside ? Path.Combine(Repo, "art/textures/creekside-life-c") : Path.Combine(source, "Textures");
            if (Directory.Exists(textures))
                foreach (string file in Directory.GetFiles(textures, folder == World && (id.StartsWith("TY05") || id.StartsWith("TY10")) ? "T_" + id + "_*.png" : id + "_*.png"))
                    Copy(file, Path.Combine(target, "Textures", Path.GetFileName(file)));
            AssetDatabase.Refresh();
            var importer = AssetImporter.GetAtPath(model) as ModelImporter;
            if (importer == null) throw new FileNotFoundException("Model did not import", model);
            if (!importer.bakeAxisConversion || importer.materialImportMode != ModelImporterMaterialImportMode.None)
            {
                importer.bakeAxisConversion = true; importer.importCameras = false; importer.importLights = false;
                importer.importAnimation = false; importer.addCollider = false;
                importer.materialImportMode = ModelImporterMaterialImportMode.None; importer.SaveAndReimport();
            }
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { folder + "/" + id }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var ti = AssetImporter.GetAtPath(path) as TextureImporter;
                bool normal = path.EndsWith("_Normal.png"), linear = normal || path.EndsWith("_MaskURP.png") || path.EndsWith("_MetallicSmoothness.png");
                if (ti.textureType == (normal ? TextureImporterType.NormalMap : TextureImporterType.Default) && ti.sRGBTexture == !linear) continue;
                ti.textureType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
                ti.sRGBTexture = !linear; ti.mipmapEnabled = true; ti.SaveAndReimport();
            }
        }

        static void Copy(string source, string target)
        {
            if (!File.Exists(source)) throw new FileNotFoundException("Delivered model or texture missing", source);
            if (new FileInfo(source).Length < 1024 && File.ReadAllText(source).StartsWith("version https://git-lfs"))
                throw new InvalidOperationException("Asset is still a Git LFS pointer: " + source);
            Directory.CreateDirectory(Path.GetDirectoryName(target));
            if (!File.Exists(target) || new FileInfo(target).Length != new FileInfo(source).Length) File.Copy(source, target, true);
        }

        static Material Material(string model, string group)
        {
            string id = Path.GetFileName(Path.GetDirectoryName(model));
            string dir = Path.GetDirectoryName(model).Replace('\\', '/') + "/Materials";
            Directory.CreateDirectory(Path.Combine(Repo, "apps/game", dir));
            string path = dir + "/" + group + ".mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (!mat) { mat = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(mat, path); }
            string prefix = model.StartsWith(World + "/") ?
                (group == id ? "T_" + id : group.StartsWith("Detail_") ? id + "_" + group : group) : group;
            string texDir = Path.GetDirectoryName(model).Replace('\\', '/') + "/Textures/";
            Texture2D Tex(string kind) => AssetDatabase.LoadAssetAtPath<Texture2D>(texDir + prefix + "_" + kind + ".png");
            var albedo = Tex(model.StartsWith(Creek + "/") ? "BaseColor" : "Albedo");
            if (!albedo) throw new FileNotFoundException("Delivered color texture missing", texDir + prefix);
            mat.SetTexture("_BaseMap", albedo); mat.SetColor("_BaseColor", Color.white);
            var normal = Tex("Normal");
            if (normal) { mat.SetTexture("_BumpMap", normal); mat.EnableKeyword("_NORMALMAP"); }
            var mask = Tex(model.StartsWith(Creek + "/") ? "MetallicSmoothness" : "MaskURP");
            if (mask) { mat.SetTexture("_MetallicGlossMap", mask); mat.EnableKeyword("_METALLICSPECGLOSSMAP"); mat.SetFloat("_Smoothness", 1); }
            if (group.Contains("_Detail_Ferns") || id.StartsWith("CO04") || (model.StartsWith(Creekside + "/") && id == "FI03"))   // alpha-cut cards (ferns; the hand net's far LOD), seen from both sides
            {
                mat.SetFloat("_AlphaClip", 1); mat.SetFloat("_Cutoff", .45f); mat.EnableKeyword("_ALPHATEST_ON"); mat.SetFloat("_Cull", 0);
                mat.renderQueue = (int)UnityEngine.Rendering.RenderQueue.AlphaTest; mat.SetFloat("_Smoothness", 0);
            }
            var glow = Tex("Emission");
            if (glow) { mat.SetTexture("_EmissionMap", glow); mat.SetColor("_EmissionColor", Color.black); mat.EnableKeyword("_EMISSION"); }
            EditorUtility.SetDirty(mat);
            return mat;
        }

        public static void Prepare(GameObject go, string model)
        {
            bool creek = model.StartsWith(Creek + "/");
            string id = Path.GetFileName(Path.GetDirectoryName(model));
            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
            {
                if (r.name.Contains("_Collision") || r.name.StartsWith("UCX_")) { r.enabled = false; continue; }
                var match = Regex.Match(r.name, @"^(.+)_LOD\d$");
                string group = creek || model.StartsWith(Creekside + "/") ? id : match.Success ? match.Groups[1].Value : null;
                if (group != null) r.sharedMaterials = Enumerable.Repeat(Material(model, group), r.sharedMaterials.Length).ToArray();
            }
            var levels = go.GetComponentsInChildren<Renderer>(true).Where(r => r.enabled && Regex.IsMatch(r.name, @"_LOD[012]$")).ToArray();
            if (levels.Length > 0 && !go.GetComponentsInChildren<LODGroup>(true).Any())
            {
                float[] cuts = { .25f, .08f, .015f };
                go.AddComponent<LODGroup>().SetLODs(Enumerable.Range(0, 3)
                    .Select(i => new LOD(cuts[i], levels.Where(r => r.name.EndsWith("_LOD" + i)).ToArray())).ToArray());
            }
            foreach (var shell in go.GetComponentsInChildren<MeshFilter>(true).Where(m => m.name.Contains("_Collision") || m.name.StartsWith("UCX_")))
                if (!shell.GetComponent<MeshCollider>()) shell.gameObject.AddComponent<MeshCollider>().sharedMesh = shell.sharedMesh;
        }
    }
}
