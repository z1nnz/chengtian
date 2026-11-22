# 神木 A（v004 熔接版）補細緻建模（z1nnz 11/22：「應該是缺一點比較細緻的建模，所以改良就好」）
# 一次只改一件：把掃描樹皮的凹凸真的推進幾何（跟 Josh 拱門同做法），形狀、顏色不動
# 下半段（看得到的樹幹與板根）細分一次 → 約 5 cm 一格；用跟材質一樣的盒投影取樣 bark_brown_02_disp，沿法線推出去
import bpy, bmesh, sys, time
import numpy as np
S = 'D:/chengtian/4-素材與快取/bark-sample/GT01_out/'
B = 'D:/chengtian/4-素材與快取/polyhaven-bark/'
AMP = float(sys.argv[-1]) if sys.argv[-1].replace('.', '').isdigit() else .16
ZMAX = 24.0
t0 = time.time()
with bpy.data.libraries.load(S + 'GT01_GodTree_v004_fused.blend', link=False) as (s, d):
    d.objects = [n for n in s.objects if n.endswith('_LOD0')]
for o in d.objects:
    bpy.context.scene.collection.objects.link(o)
w = bpy.data.objects['GT01_GodTree_Wood_LOD0']
bm = bmesh.new(); bm.from_mesh(w.data)
faces = [f for f in bm.faces if f.calc_center_median().z < ZMAX]
edges = list({e for f in faces for e in f.edges})
bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True)
bm.normal_update()
print('SUBDIV', len(bm.verts), round(time.time() - t0))
bm.to_mesh(w.data); bm.free()
me = w.data
nv = len(me.vertices)
co = np.zeros(nv * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
nr = np.zeros(nv * 3); me.vertices.foreach_get('normal', nr); nr = nr.reshape(-1, 3)
img = bpy.data.images.load(B + 'bark_brown_02_disp_2k.png')
W, H = img.size
px = np.zeros(W * H * 4, dtype=np.float32); img.pixels.foreach_get(px)
D = px.reshape(H, W, 4)[:, :, 0]


def samp(u, v):
    x = (np.mod(u, 1.0) * (W - 1)).astype(np.int64)
    y = (np.mod(v, 1.0) * (H - 1)).astype(np.int64)
    return D[y, x]


# 跟場景材質同一套盒投影：Object 座標 × (1/1.1, 1/1.1, 1/2.0)，blend .35
q = co * np.array([1 / 1.1, 1 / 1.1, 1 / 2.0])
hx = samp(q[:, 1], q[:, 2]); hy = samp(q[:, 0], q[:, 2]); hz = samp(q[:, 0], q[:, 1])
a = np.abs(nr) ** 4
a /= a.sum(1, keepdims=True) + 1e-9
h = hx * a[:, 0] + hy * a[:, 1] + hz * a[:, 2]
fade = np.clip((ZMAX - co[:, 2]) / 3.0, 0, 1)   # 上緣 3 m 漸淡，接回沒細分的部分
co += nr * ((h - .5) * AMP * fade)[:, None]
me.vertices.foreach_set('co', co.ravel())
me.update()
print('DISP', nv, round(time.time() - t0))
for o in list(bpy.data.objects):
    if o.type != 'MESH' or not o.name.endswith('_LOD0'):
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=S + 'GT01_GodTree_v004b_detail.blend')
print('SAVED', round(time.time() - t0))
