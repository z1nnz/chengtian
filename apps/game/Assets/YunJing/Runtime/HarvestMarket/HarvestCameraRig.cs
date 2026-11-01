using System.Collections;
using UnityEngine;

namespace YunJing.HarvestMarket
{
    /// Two fixed views of the test scene (field, stall) with a smooth move between them.
    /// Own file: a scene-serialised MonoBehaviour must live in a file of its name, or the player cannot load the scene.
    public sealed class HarvestCameraRig : MonoBehaviour
    {
        public Transform[] views;
        public IEnumerator MoveTo(int view, float seconds)
        {
            Vector3 p0 = transform.position; Quaternion r0 = transform.rotation; float t = 0;
            while (t < seconds)
            {
                t += Time.deltaTime; float k = Mathf.SmoothStep(0, 1, t / seconds);
                transform.SetPositionAndRotation(Vector3.Lerp(p0, views[view].position, k), Quaternion.Slerp(r0, views[view].rotation, k));
                yield return null;
            }
        }
    }
}
