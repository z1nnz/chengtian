using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;

namespace YunJing.Editor
{
    // Maps D2's source-art paths to gitignored Unity imports; source deliveries are never edited.
    public static class QingxiD2Kit
    {
        const string Root = "Assets/YunJing/Models/D2";
        static readonly HashSet<string> Imported = new HashSet<string>();
        static bool elderCopied;
        static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ".."));

        public static bool Owns(string source) => !string.IsNullOrEmpty(source) && source.StartsWith("art/exports/", StringComparison.Ordinal);
        public static bool HasGroundOrigin(string source) => !string.IsNullOrEmpty(source)
            && source.StartsWith("art/exports/core-d2-v1/", StringComparison.Ordinal)
            && source.EndsWith("_v002.fbx", StringComparison.Ordinal);

        public static string Resolve(string source)
        {
            if (!Owns(source)) return source;
            string kit = source.Split('/')[2], file = Path.GetFileName(source), id = Path.GetFileNameWithoutExtension(source);
            if (kit == "modelling-basics-c") return $"Assets/YunJing/Models/ModellingBasicsC/{id}/{file}";
            if (kit == "core-ruins-v1") return $"Assets/YunJing/Models/CoreRuins/{Path.GetFileName(Path.GetDirectoryName(source))}/{file}";
            if (kit == "elder-trees-v1") return QingxiElderTrees.Models + "/" + file;
            string folder = kit == "qingxi-encounter-a" ? id : Path.GetFileName(Path.GetDirectoryName(source));
            return $"{Root}/{kit}/{folder}/{file}";
        }

        public static void Ensure(string source)
        {
            if (!Owns(source) || !Imported.Add(source)) return;
            string kit = source.Split('/')[2], target = Resolve(source);
            if (kit == "modelling-basics-c" || kit == "core-ruins-v1") { QingxiScenePropKits.Ensure(target); return; }
            if (kit == "elder-trees-v1")
            {
                if (!elderCopied) { QingxiElderTrees.Copy(); elderCopied = true; }
                return;
            }
            string src = Path.Combine(Repo, source), dst = Path.Combine(Repo, "apps/game", target);
            Copy(src, dst);
            string textureSource = kit == "qingxi-encounter-a"
                ? Path.Combine(Path.GetDirectoryName(src), "textures") : Path.Combine(Path.GetDirectoryName(src), "Textures");
            if (Directory.Exists(textureSource))
            {
                string pattern = kit == "qingxi-encounter-a" ? "T_" + Path.GetFileNameWithoutExtension(src) + "_*.png" : "*.png";
                foreach (string file in Directory.GetFiles(textureSource, pattern))
                    Copy(file, Path.Combine(Path.GetDirectoryName(dst), "Textures", Path.GetFileName(file)));
            }
            AssetDatabase.Refresh();
            var importer = AssetImporter.GetAtPath(target) as ModelImporter;
            if (importer == null) throw new FileNotFoundException("D2 model did not import", target);
            importer.bakeAxisConversion = true;
            importer.importAnimation = false; importer.importCameras = false; importer.importLights = false;
            importer.addCollider = false; importer.importNormals = ModelImporterNormals.Import;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
            importer.SaveAndReimport();
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { Path.GetDirectoryName(target).Replace('\\', '/') + "/Textures" }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var ti = AssetImporter.GetAtPath(path) as TextureImporter;
                if (ti == null) continue;
                bool normal = path.EndsWith("_Normal.png", StringComparison.Ordinal);
                bool linear = normal || path.EndsWith("_MetallicSmoothness.png", StringComparison.Ordinal) || path.EndsWith("_ORM.png", StringComparison.Ordinal);
                ti.textureType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
                ti.sRGBTexture = !linear; ti.mipmapEnabled = true; ti.maxTextureSize = 2048;
                ti.SaveAndReimport();
            }
        }

        static void Copy(string source, string target)
        {
            if (!File.Exists(source)) throw new FileNotFoundException("D2 delivery missing", source);
            if (new FileInfo(source).Length < 1024 && File.ReadAllText(source).StartsWith("version https://git-lfs", StringComparison.Ordinal))
                throw new InvalidOperationException("Git LFS pointer instead of D2 asset: " + source);
            Directory.CreateDirectory(Path.GetDirectoryName(target));
            if (!File.Exists(target) || new FileInfo(target).Length != new FileInfo(source).Length) File.Copy(source, target, true);
        }

        public static void Prepare(GameObject instance, string source)
        {
            string kit = source.Split('/')[2], target = Resolve(source);
            if (kit == "modelling-basics-c" || kit == "core-ruins-v1") { QingxiScenePropKits.Prepare(instance, target); return; }
            if (kit == "elder-trees-v1") return;
            string folder = Path.GetDirectoryName(target).Replace('\\', '/');
            string id = kit == "qingxi-encounter-a" ? "T_" + Path.GetFileNameWithoutExtension(source) : Path.GetFileName(Path.GetDirectoryName(source));
            Texture2D Tex(string suffix) => AssetDatabase.LoadAssetAtPath<Texture2D>($"{folder}/Textures/{id}_{suffix}.png");
            var colour = Tex("BaseColor");
            if (colour == null) throw new FileNotFoundException("D2 BaseColor missing", $"{folder}/Textures/{id}_BaseColor.png");
            string materialPath = folder + "/" + id + "_URP.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(materialPath);
            if (mat == null)
            {
                var shader = Shader.Find("Universal Render Pipeline/Lit");
                if (shader == null) throw new InvalidOperationException("URP Lit shader missing for " + source);
                mat = new Material(shader); AssetDatabase.CreateAsset(mat, materialPath);
            }
            mat.SetTexture("_BaseMap", colour); mat.SetColor("_BaseColor", Color.white);
            var normal = Tex("Normal");
            if (normal != null) { mat.SetTexture("_BumpMap", normal); mat.EnableKeyword("_NORMALMAP"); }
            var mask = Tex("MetallicSmoothness");
            if (mask != null) { mat.SetTexture("_MetallicGlossMap", mask); mat.EnableKeyword("_METALLICSPECGLOSSMAP"); mat.SetFloat("_Smoothness", 1); }
            var glow = Tex("Emission");
            if (glow != null) { mat.SetTexture("_EmissionMap", glow); mat.SetColor("_EmissionColor", Color.white * .7f); mat.EnableKeyword("_EMISSION"); }
            if (id.Contains("VineCurtain"))
            {
                mat.SetFloat("_AlphaClip", 1); mat.SetFloat("_Cutoff", .45f); mat.EnableKeyword("_ALPHATEST_ON");
                mat.SetFloat("_Cull", 0); mat.renderQueue = (int)UnityEngine.Rendering.RenderQueue.AlphaTest;
            }
            EditorUtility.SetDirty(mat);
            var renderers = instance.GetComponentsInChildren<Renderer>(true);
            foreach (var renderer in renderers)
            {
                if (renderer.name.Contains("_Collision") || renderer.name.StartsWith("UCX_")) { renderer.enabled = false; continue; }
                renderer.sharedMaterials = Enumerable.Repeat(mat, renderer.sharedMaterials.Length).ToArray();
            }
            var levels = renderers.Where(r => r.enabled && Regex.IsMatch(r.name, @"_LOD[012](\.\d+)?$")).ToArray();
            if (levels.Length > 0 && instance.GetComponent<LODGroup>() == null)
            {
                float[] cuts = { .24f, .07f, .012f };
                instance.AddComponent<LODGroup>().SetLODs(Enumerable.Range(0, 3).Select(i => new LOD(cuts[i],
                    levels.Where(r => Regex.IsMatch(r.name, "_LOD" + i + @"(\.\d+)?$")).ToArray())).ToArray());
            }
            foreach (var shell in instance.GetComponentsInChildren<MeshFilter>(true).Where(m => m.name.Contains("_Collision") || m.name.StartsWith("UCX_")))
                if (shell.GetComponent<MeshCollider>() == null) shell.gameObject.AddComponent<MeshCollider>().sharedMesh = shell.sharedMesh;
        }
    }
}
