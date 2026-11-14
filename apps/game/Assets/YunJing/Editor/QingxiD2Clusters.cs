using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace YunJing.Editor
{
    // Expands authored D2 cluster counts into stable terrain placements before scene generation.
    public static class QingxiD2Clusters
    {
        public static int Expand(QingxiVillageTerrain.Layout layout)
        {
            if (layout.clusters == null || layout.clusters.Length == 0) return 0;
            var expanded = new List<QingxiVillageTerrain.Placement>(layout.placements ?? Array.Empty<QingxiVillageTerrain.Placement>());
            var anchors = layout.nodes.ToDictionary(n => n.id, n => new Vector2(n.x, n.z));
            var trees = new List<Vector2>();
            int count = 0;
            foreach (var cluster in layout.clusters)
            {
                if (cluster.radius <= 0 || cluster.items == null || cluster.items.Length == 0)
                    throw new InvalidOperationException("Invalid D2 cluster: " + cluster.id);
                foreach (var item in cluster.items)
                {
                    if (item.count < 0 || item.scaleMin <= 0 || item.scaleMax < item.scaleMin)
                        throw new InvalidOperationException("Invalid D2 cluster item: " + cluster.id + "/" + item.modelCode);
                    var random = new System.Random(Seed(layout.clusterSeed, cluster.id + "/" + item.modelCode));
                    bool tree = item.modelCode.StartsWith("Elder", StringComparison.Ordinal) || item.modelCode == "JianmuSapling";
                    for (int i = 0; i < item.count; i++)
                    {
                        Vector2 point = default;
                        bool found = false;
                        for (int attempt = 0; attempt < 500; attempt++)
                        {
                            float angle = (float)random.NextDouble() * Mathf.PI * 2f;
                            float distance = Mathf.Sqrt((float)random.NextDouble()) * cluster.radius;
                            point = new Vector2(cluster.x + Mathf.Cos(angle) * distance, cluster.z + Mathf.Sin(angle) * distance);
                            if (point.x < layout.bounds.minX + 1 || point.x > layout.bounds.minX + layout.bounds.sizeX - 1 ||
                                point.y < layout.bounds.minZ + 1 || point.y > layout.bounds.minZ + layout.bounds.sizeZ - 1) continue;
                            if (cluster.avoidPath && QingxiVillageTerrain.RoadDistance(layout, point.x, point.y, out _) < (tree ? 2.4f : .55f)) continue;
                            if (QingxiVillageTerrain.PadDistance(layout, point.x, point.y, out _) < (tree ? 2.0f : .35f)) continue;
                            if (tree && trees.Any(t => Vector2.Distance(t, point) < 1.5f)) continue;
                            found = true; break;
                        }
                        if (!found) throw new InvalidOperationException("Could not place D2 cluster item: " + cluster.id + "/" + item.modelCode + "/" + i);
                        if (tree) trees.Add(point);
                        float yaw = (float)random.NextDouble() * 360f;
                        if (cluster.yaw == "outward") yaw = Mathf.Atan2(point.x - cluster.x, point.y - cluster.z) * Mathf.Rad2Deg;
                        else if (cluster.yaw == "alongPath") yaw = PathYaw(layout, anchors, point);
                        float scale = Mathf.Lerp(item.scaleMin, item.scaleMax, (float)random.NextDouble());
                        expanded.Add(new QingxiVillageTerrain.Placement {
                            id = cluster.id + "_" + item.modelCode + "_" + (i + 1).ToString("D3"),
                            zone = "d2-tree", role = cluster.note, model = item.model,
                            x = point.x, z = point.y, yaw = yaw, scale = scale,
                            collider = "none", status = item.status, author = "既有交付或待製作"
                        });
                        count++;
                    }
                }
            }
            layout.placements = expanded.ToArray();
            return count;
        }

        static int Seed(int basis, string id)
        {
            unchecked
            {
                uint hash = 2166136261;
                foreach (char c in id) hash = (hash ^ c) * 16777619;
                return (int)(hash ^ (uint)basis);
            }
        }

        static float PathYaw(QingxiVillageTerrain.Layout layout, Dictionary<string, Vector2> anchors, Vector2 point)
        {
            float best = float.MaxValue, yaw = 0;
            foreach (var edge in layout.edges)
            {
                Vector2 a = anchors[edge.from], b = anchors[edge.to], d = b - a;
                float t = Mathf.Clamp01(Vector2.Dot(point - a, d) / Mathf.Max(.001f, d.sqrMagnitude));
                float dist = (point - (a + d * t)).sqrMagnitude;
                if (dist < best) { best = dist; yaw = Mathf.Atan2(d.x, d.y) * Mathf.Rad2Deg; }
            }
            return yaw;
        }
    }
}
