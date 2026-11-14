using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using QingxiWorld;
using UnityEngine;
using UnityEngine.Rendering;

namespace YunJing
{
    // Same-camera review shots for the key art (--keyart-shots): for each key art, stand where its parts.md says
    // (world position, yaw with 0 = north, eye 1.6 m, 55 degrees horizontal), at its hour, with the UI hidden, and
    // save <build>/keyart-shots/<KA>.png to put beside art/references/keyart/<KA>/chosen.png. Blocks are streamed
    // in first. Requested by the scene plan (docs/execution/world-plan/code-requests.md).
    public sealed class QingxiKeyArtShots : MonoBehaviour
    {
        // id, block to wait for ("" = the village itself), x, z, yaw, hour
        static readonly (string id, string block, float x, float z, float yaw, float hour)[] Views =
        {
            ("KA00", "", 0, -8, 0, 10f),
            ("KA01", "A2", 0, -46, 0, 22f),
            ("KA02", "A2", 0, -118, 0, 17.5f),
            ("KA03", "A3", -90, 2, 315, 6.5f),
            ("KA04-1", "A4", 70, -15, 45, 10f),
            ("KA04-2", "A4", 125, 30, 225, 11f),
            ("KA07", "D3", -80, 75, 315, 15.5f),
            ("D2-V1", "D2", 42, 129, 320, 10f),
            ("D2-V2", "D2", 10, 152, 0, 10f),
            ("D2-V3", "D2", 8, 178, 350, 10f),
            ("D2-V4", "D2", 7, 205, 180, 10f),
            ("D2-V5", "D2", 25, 210, 55, 10f),
            ("D2-V6", "D2", 17, 186, 220, 10f),
        };
        static readonly Dictionary<string, (float eye, float pitch, bool absolute)> D2Camera = new Dictionary<string, (float, float, bool)> {
            ["D2-V1"] = (72f, 45f, true), ["D2-V2"] = (9.5f, 0f, true),
            ["D2-V3"] = (7.5f, -8f, true), ["D2-V4"] = (1.6f, 0f, false),
            ["D2-V5"] = (8.6f, 0f, true), ["D2-V6"] = (1.6f, 12f, false)
        };

        IEnumerator Start()
        {
            if (Array.IndexOf(Environment.GetCommandLineArgs(), "--keyart-shots") < 0) yield break;
            string dir = System.IO.Path.Combine(System.IO.Path.GetDirectoryName(Application.dataPath), "keyart-shots");
            System.IO.Directory.CreateDirectory(dir);
            yield return new WaitForSecondsRealtime(3);
            var walker = QingxiFirstPerson.Current;
            var streamer = QingxiBlockStreamer.Current;
            if (walker == null || streamer == null) { Debug.LogError("QINGXI_KEYART_SHOTS no walker or streamer"); Application.Quit(1); yield break; }
            var body = walker.GetComponent<CharacterController>();
            var cam = new GameObject("KeyArtShotsCamera").AddComponent<Camera>();
            // 55 degrees across a 16:9 frame is 32.6 degrees up and down
            cam.fieldOfView = 2 * Mathf.Atan(Mathf.Tan(27.5f * Mathf.Deg2Rad) * 9f / 16f) * Mathf.Rad2Deg;
            cam.nearClipPlane = .05f; cam.farClipPlane = 600; cam.depth = 50;
            UnityEngine.Rendering.Universal.CameraExtensions.GetUniversalAdditionalCameraData(cam).renderPostProcessing = true;
            foreach (var (id, block, x, z, yaw, hour) in Views)
            {
                // the walker goes there too (hidden behind the camera), so the blocks around the view stream in
                var dirv = Quaternion.Euler(0, yaw, 0) * Vector3.forward;
                body.enabled = false; walker.transform.position = new Vector3(x, 30, z) - dirv * 3; body.enabled = true;
                float until = Time.realtimeSinceStartup + 40;
                while (block != "" && !streamer.IsLoaded(block) && Time.realtimeSinceStartup < until) yield return null;
                yield return new WaitForSecondsRealtime(2.5f);
                QingxiDayNight.Current?.SetHour(hour);
                float ground = Physics.RaycastAll(new Vector3(x, 80, z), Vector3.down, 200f, ~0, QueryTriggerInteraction.Ignore)
                    .Where(h => !h.collider.isTrigger && h.collider.GetComponentInParent<CharacterController>() == null).Select(h => h.point.y).DefaultIfEmpty(0).Max();
                var shot = D2Camera.TryGetValue(id, out var d2) ? d2 : (1.6f, 0f, false);
                float y = shot.Item3 ? shot.Item1 : ground + shot.Item1;
                if (id == "D2-V2") y = Mathf.Max(y, ground + 1.6f);
                cam.transform.SetPositionAndRotation(new Vector3(x, y, z), Quaternion.Euler(shot.Item2, yaw, 0));
                Debug.Log($"QINGXI_KEYART_CAMERA {id}: ({x:F1}, {y:F1}, {z:F1}), terrain ray={ground:F1}, yaw={yaw:F0}, pitch={shot.Item2:F0}");
                foreach (var canvas in FindObjectsByType<Canvas>(FindObjectsInactive.Exclude, FindObjectsSortMode.None)) canvas.enabled = false;
                foreach (var r in walker.GetComponentsInChildren<Renderer>()) r.enabled = false;
                yield return new WaitForSecondsRealtime(.8f);
                yield return new WaitForEndOfFrame();
                var target = RenderTexture.GetTemporary(Screen.width, Screen.height, 24, RenderTextureFormat.ARGB32);
                cam.targetTexture = target;
                cam.Render();
                var readback = AsyncGPUReadback.Request(target, 0, TextureFormat.RGB24);
                while (!readback.done) yield return null;
                if (readback.hasError) { Debug.LogError("QINGXI_KEYART_SHOTS readback failed: " + id); Application.Quit(1); yield break; }
                var tex = new Texture2D(Screen.width, Screen.height, TextureFormat.RGB24, false);
                tex.LoadRawTextureData(readback.GetData<byte>()); tex.Apply();
                System.IO.File.WriteAllBytes(System.IO.Path.Combine(dir, id + ".png"), tex.EncodeToPNG());
                Destroy(tex);
                cam.targetTexture = null;
                RenderTexture.ReleaseTemporary(target);
            }
            Debug.Log("QINGXI_KEYART_SHOTS saved to " + dir);
            Application.Quit(0);
        }
    }
}
