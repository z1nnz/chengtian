using QingxiWorld;
using UnityEngine;

namespace YunJing
{
    // A newcomer's first arrival: on the road south of the tea pavilion instead of at the village gate. The road is in
    // the streamed A2 block, so the player is held still until its ground is under them.
    public sealed class QingxiNoviceArrival : MonoBehaviour
    {
        public Vector3 arrival = new Vector3(2, 0, -124);
        public float yaw = -20;

        System.Collections.IEnumerator Start()
        {
            string args = string.Join(" ", System.Environment.GetCommandLineArgs()) + " " + Application.absoluteURL;
            if (args.Contains("smoke") || args.Contains("shots") || QingxiNoviceDays.Has("arrived")) yield break;
            var walker = GetComponent<QingxiFirstPerson>();
            var body = GetComponent<CharacterController>();
            if (walker == null || body == null) yield break;
            body.enabled = false;
            walker.SetMenuOpen(true);
            transform.position = arrival + Vector3.up * 2f;
            transform.rotation = Quaternion.Euler(0, yaw, 0);
            float give = Time.realtimeSinceStartup + 20f;
            while (Time.realtimeSinceStartup < give && !Physics.Raycast(arrival + Vector3.up * 200, Vector3.down, out _, 400)) yield return null;
            if (Physics.Raycast(arrival + Vector3.up * 200, Vector3.down, out var hit, 400)) transform.position = hit.point + Vector3.up * .05f;
            body.enabled = true;
            walker.SetMenuOpen(false);
            QingxiNoviceDays.Mark("arrived");
        }
    }
}
