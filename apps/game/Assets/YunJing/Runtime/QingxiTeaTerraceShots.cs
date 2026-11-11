using System;
using System.Collections;
using System.Linq;
using QingxiWorld;
using UnityEngine;

namespace YunJing
{
    // Review shots of A4 東坡茶田 (--tea-shots): streams the block in, then a separate camera takes the blueprint's five
    // views (tools/qingxi-terrain/world-blueprint.json, A4-S1..S5) into <build>/tea-shots/, and the build quits.
    public sealed class QingxiTeaTerraceShots : MonoBehaviour
    {
        static readonly (string name, Vector3 eye, Vector3 look, float up, float hour)[] Views =
        {
            ("A4-S5-from-the-village", new Vector3(48, 0, -8), new Vector3(100, 0, -12), 1.7f, 10f),
            ("A4-S1-tea-and-stair", new Vector3(80, 0, -33), new Vector3(104, 0, -8), 1.7f, 10f),
            ("A4-S4-stair-landing", new Vector3(100, 0, -20.5f), new Vector3(116, 0, 4), 1.7f, 11f),
            ("A4-S2-from-the-pavilion", new Vector3(122, 0, 22), new Vector3(70, 0, -20), 1.9f, 11f),
            ("A4-S3-north-east", new Vector3(122, 0, 22), new Vector3(160, 0, 60), 1.9f, 11f),
            ("A4-overview", new Vector3(70, 0, -45), new Vector3(100, 0, -8), 26f, 10f),
        };

        IEnumerator Start()
        {
            if (Array.IndexOf(Environment.GetCommandLineArgs(), "--tea-shots") < 0) yield break;
            string dir = System.IO.Path.Combine(System.IO.Path.GetDirectoryName(Application.dataPath), "tea-shots");
            System.IO.Directory.CreateDirectory(dir);
            yield return new WaitForSecondsRealtime(3);
            var walker = QingxiFirstPerson.Current;
            var streamer = QingxiBlockStreamer.Current;
            if (walker == null || streamer == null) { Debug.LogError("QINGXI_TEA_SHOTS no walker or streamer"); Application.Quit(1); yield break; }
            var body = walker.GetComponent<CharacterController>();
            body.enabled = false; walker.transform.position = new Vector3(90, 12, -15); body.enabled = true;
            float until = Time.realtimeSinceStartup + 40;
            while (!streamer.IsLoaded("A4") && Time.realtimeSinceStartup < until) yield return null;
            if (!streamer.IsLoaded("A4")) Debug.LogError("QINGXI_TEA_SHOTS A4 did not stream in");
            yield return new WaitForSecondsRealtime(2);
            var cam = new GameObject("TeaShotsCamera").AddComponent<Camera>();
            cam.fieldOfView = 60; cam.nearClipPlane = .05f; cam.farClipPlane = 600; cam.depth = 50;
            UnityEngine.Rendering.Universal.CameraExtensions.GetUniversalAdditionalCameraData(cam).renderPostProcessing = true;
            foreach (var (name, eye, look, up, hour) in Views)
            {
                QingxiDayNight.Current?.SetHour(hour);
                float Ground(Vector3 p) => Physics.RaycastAll(new Vector3(p.x, 80, p.z), Vector3.down, 200f, ~0, QueryTriggerInteraction.Ignore)
                    .Where(h => !h.collider.isTrigger && h.collider.GetComponentInParent<CharacterController>() == null).Select(h => h.point.y).DefaultIfEmpty(0).Max();
                var e = new Vector3(eye.x, Ground(eye) + up, eye.z);
                var l = new Vector3(look.x, Ground(look) + 1f, look.z);
                cam.transform.SetPositionAndRotation(e, Quaternion.LookRotation(l - e));
                yield return new WaitForSecondsRealtime(.8f);
                yield return new WaitForEndOfFrame();
                var tex = new Texture2D(Screen.width, Screen.height, TextureFormat.RGB24, false);
                tex.ReadPixels(new Rect(0, 0, Screen.width, Screen.height), 0, 0); tex.Apply();
                System.IO.File.WriteAllBytes(System.IO.Path.Combine(dir, name + ".png"), tex.EncodeToPNG());
                Destroy(tex);
            }
            Debug.Log("QINGXI_TEA_SHOTS saved to " + dir);
            Application.Quit(0);
        }
    }
}
