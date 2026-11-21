# 神木下半段重做（z1nnz 11/22「紋理跟流暢性沒有做好，很像蜘蛛腳」）
# 原本：圓柱樹幹 + 幾塊扁平板根（頂面整片苔）→ 改成二十幾股扭轉的樹筋，從樹幹中段一路流下來、在地面分成大小樹根（設定圖 V3）
# 每股記下自己的方向，熔接後每個頂點照最近那股算 UV → 樹皮紋路順著股走
import bpy, bmesh, math, random, sys, time
import numpy as np
from mathutils import Vector, kdtree, noise
S = 'D:/chengtian/4-素材與快取/bark-sample/GT01_out/'
try:
    VS = float(sys.argv[-1])
except ValueError:
    VS = .1
ZCUT = 16.0
R = random.Random(11)
t0 = time.time()
with bpy.data.libraries.load(S + 'GT01_GodTree_v004_fused.blend', link=False) as (s, d):
    d.objects = [n for n in s.objects if n.endswith('_LOD0')]
for o in d.objects:
    bpy.context.scene.collection.objects.link(o)
w = bpy.data.objects['GT01_GodTree_Wood_LOD0']

# 1) 原本樹幹切掉 z<16 的部分（樹幹下段 + 板根）
bm = bmesh.new(); bm.from_mesh(w.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < ZCUT], context='VERTS')
bd = [e for e in bm.edges if e.is_boundary]
bmesh.ops.holes_fill(bm, edges=bd, sides=0)
print('CUT', len(bm.verts))


def lerp(a, b, t): return a + (b - a) * t
def smooth(t): return t * t * (3 - 2 * t)


STR = []   # 每股：[(point, radius, zsquash)]


def main_strand(th0, Rg, Rend, rA, twist, seed):
    pts = []
    n = 160
    # s 0→.45 樹幹段（z 24→6），.45→.7 外擴下彎（z 6→.4），.7→1 貼地延伸變細
    for k in range(n + 1):
        s_ = k / n
        if s_ < .45:
            u = s_ / .45
            z = lerp(24, 9, u)
            rad = lerp(1.6, rA, smooth(min(1, u * 1.4)))
            # z≥16：股的外緣貼著原本樹幹（半徑約 8.3）→ 接縫處不會凸出一圈；16 以下才慢慢鼓出來
            r = lerp(8.3 - rad * .9, 8.8 - rA * .5, smooth(min(1, max(0, (16 - z) / 7))))
            th = th0 + twist * u
            sq = 1.0
        elif s_ < .7:
            u = (s_ - .45) / .25
            z = 9 - 8.1 * math.sin(u * math.pi / 2)
            r9 = 8.8 - rA * .5
            r = r9 + (Rg - r9) * (1 - math.cos(u * math.pi / 2))
            rad = lerp(rA, rA * .55, u)
            th = th0 + twist + twist * .35 * u
            sq = lerp(1.0, .75, u)
        else:
            u = (s_ - .7) / .3
            z = .9 - .5 * u if u < .7 else .55 - 1.6 * ((u - .7) / .3) ** 1.5
            r = lerp(Rg, Rend, u)
            rad = rA * .55 * (1 - .85 * u ** 1.2)
            th = th0 + twist * 1.35 + twist * .25 * u
            sq = .7
        wob = Vector((noise.noise(Vector((s_ * 6, seed, 0))), noise.noise(Vector((s_ * 6, seed, 7))), 0)) * (.6 if s_ > .4 else .25)
        pts.append((Vector((math.cos(th) * r, math.sin(th) * r, z)) + wob, rad, sq))
    return pts


N = 16   # 11/22：股少一點、粗細差大一點，地面的根才分得開（22 股會黏成一整圈裙子）
TW = 1.0
roots = []
for i in range(N):
    th0 = 2 * math.pi * i / N + R.uniform(-.08, .08)
    long_ = R.random() < .55
    Rg = R.uniform(16, 21) if long_ else R.uniform(13, 16)
    Rend = Rg + (R.uniform(14, 24) if long_ else R.uniform(5, 10))
    big = R.random() < .55
    pts = main_strand(th0, Rg + (2 if big else -1), Rend, R.uniform(2.4, 2.9) if big else R.uniform(1.4, 1.9), TW * R.uniform(.8, 1.15), i * 3.1)
    STR.append(pts)
    roots.append(pts)

# 支根：從主根外擴段分岔出去
for i, pts in enumerate(roots):
    for _ in range(R.choice((1, 1, 2))):
        k0 = R.randint(95, 125)
        p0, r0, _s = pts[k0]
        dirv = pts[k0 + 6][0] - p0
        dirv.z = 0
        dirv.normalize()
        side = Vector((-dirv.y, dirv.x, 0)) * R.choice((-1, 1))
        L = R.uniform(6, 14)
        sub = []
        n = 60
        for k in range(n + 1):
            u = k / n
            q = p0 + dirv * (L * u) + side * (L * .45 * u ** .8)
            q.z = lerp(p0.z, -.8, u ** 1.3)
            q += Vector((noise.noise(Vector((u * 5, i, 3))), noise.noise(Vector((u * 5, i, 9))), 0)) * .4
            sub.append((q, r0 * .55 * (1 - .85 * u), .7))
        STR.append(sub)

# 樹幹表面細筋：主筋之間的溝裡，像一束束扭在一起
for i in range(0):   # 11/22 表面細筋拿掉：頂端變成一顆顆香腸頭
    th0 = 2 * math.pi * (i + .5) / N
    pts = []
    n = 80
    z_top = R.uniform(12, 17)
    z_bot = R.uniform(5, 8)
    for k in range(n + 1):
        u = k / n
        z = lerp(z_top, z_bot, u)
        uu = min(1, max(0, (24 - z) / 15))
        r = lerp(7.6, 9.0, smooth(uu) ** .8) + 1.2
        th = th0 + TW * uu * 1.05
        rad = 1.1 * math.sin(math.pi * u) ** .6 + .05
        pts.append((Vector((math.cos(th) * r, math.sin(th) * r, z)), rad, 1.0))
    STR.append(pts)
print('STRANDS', len(STR))

SEG = 20


def tube(bm_, pts):
    rings = []
    prev_n = None
    frames = []
    for k, (p, rad, sq) in enumerate(pts):
        a = pts[max(0, k - 1)][0]
        b = pts[min(len(pts) - 1, k + 1)][0]
        tng = (b - a).normalized()
        if prev_n is None:
            nrm = tng.cross(Vector((0, 0, 1)))
            if nrm.length < 1e-3:
                nrm = tng.cross(Vector((1, 0, 0)))
            nrm.normalize()
        else:
            nrm = (prev_n - tng * prev_n.dot(tng)).normalized()
        prev_n = nrm
        bnm = tng.cross(nrm)
        frames.append((tng, nrm, bnm))
        ring = []
        for j in range(SEG):
            a_ = 2 * math.pi * j / SEG
            off = nrm * math.cos(a_) + bnm * math.sin(a_)
            off.z *= sq
            ring.append(bm_.verts.new(p + off * rad))
        rings.append(ring)
    for k in range(len(rings) - 1):
        r1, r2 = rings[k], rings[k + 1]
        for j in range(SEG):
            bm_.faces.new((r1[j], r1[(j + 1) % SEG], r2[(j + 1) % SEG], r2[j]))
    for ring, p in ((rings[0], pts[0][0]), (rings[-1], pts[-1][0])):
        c = bm_.verts.new(p)
        for j in range(SEG):
            try:
                bm_.faces.new((ring[j], ring[(j + 1) % SEG], c))
            except ValueError:
                pass
    return frames


FR = [tube(bm, pts) for pts in STR]
core = bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=7.4, radius2=6.0, depth=21)
bmesh.ops.translate(bm, verts=core['verts'], vec=Vector((0, 0, 8.5)))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(w.data)
bm.free()
print('PRE-REMESH', len(w.data.vertices), round(time.time() - t0))

bpy.context.view_layer.objects.active = w
m = w.modifiers.new('R', 'REMESH'); m.mode = 'VOXEL'; m.voxel_size = VS; m.adaptivity = 0; m.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier='R')
cs = w.modifiers.new('S', 'CORRECTIVE_SMOOTH'); cs.factor = .5; cs.iterations = 8; cs.smooth_type = 'SIMPLE'; cs.use_only_smooth = True
bpy.ops.object.modifier_apply(modifier='S')
dsp = w.modifiers.new('D', 'DISPLACE')   # 表面低頻小瘤：股不要像水管
tx = bpy.data.textures.new('BraidLumps', 'CLOUDS'); tx.noise_scale = 1.4
dsp.texture = tx; dsp.strength = .25; dsp.mid_level = .5; dsp.texture_coords = 'GLOBAL'
bpy.ops.object.modifier_apply(modifier='D')
print('REMESH', len(w.data.vertices), round(time.time() - t0))

# 順著股的 UV
samp = []
meta = []
for si, (pts, frs) in enumerate(zip(STR, FR)):
    acc = 0.0
    for k, ((p, rad, sq), (tg, nr, bn)) in enumerate(zip(pts, frs)):
        if k:
            acc += (p - pts[k - 1][0]).length
        samp.append(p)
        meta.append((si, rad, acc, nr, bn))
kd = kdtree.KDTree(len(samp))
for i, p in enumerate(samp):
    kd.insert(p, i)
kd.balance()
# v003 原模型（有 TileUV：V 沿枝管方向、約 0.38/m）→ 三角化後做 BVH，上段頂點取最近面的 UV
with bpy.data.libraries.load(S + 'GT01_GodTree_v003.blend', link=False) as (s3, d3):
    d3.objects = ['GT01_GodTree_Wood_LOD0']
_o3 = d3.objects[0]
_b3 = bmesh.new(); _b3.from_mesh(_o3.data)
bmesh.ops.triangulate(_b3, faces=_b3.faces)
_tl = _b3.loops.layers.uv['TileUV']
tris = []
for f_ in _b3.faces:
    tris.append(([l_.vert.co.copy() for l_ in f_.loops], [tuple(l_[_tl].uv) for l_ in f_.loops]))
from mathutils.bvhtree import BVHTree
bvh = BVHTree.FromBMesh(_b3)
_b3.free()


def barycentric(p, a, b, c):
    v0, v1, v2 = b - a, c - a, p - a
    d00, d01, d11 = v0.dot(v0), v0.dot(v1), v1.dot(v1)
    d20, d21 = v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-12:
        return (1, 0, 0)
    v = (d11 * d20 - d01 * d21) / den
    w_ = (d00 * d21 - d01 * d20) / den
    return (1 - v - w_, v, w_)


me = w.data
nv = len(me.vertices)
co = np.zeros(nv * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
U = np.zeros(nv); V = np.zeros(nv)
for i in range(nv):
    x, y, z = co[i]
    best = None
    if z < ZCUT + 9:
        pv = Vector((x, y, z))
        for (q, idx, dist) in kd.find_n(pv, 6):
            sd = dist - meta[idx][1]
            if best is None or sd < best[0]:
                best = (sd, idx)
    if best is not None and best[0] < 1.2:
        si, rad, acc, nr, bn = meta[best[1]]
        dv = pv - samp[best[1]]
        ang = math.atan2(dv.dot(bn), dv.dot(nr))
        U[i] = ang * max(rad, .6) + si * 37.0
        V[i] = acc
    else:   # 上段原本的樹幹/枝：從 v003 原模型的 TileUV（沿著每根枝管走）轉過來
        hit = bvh.find_nearest(Vector((x, y, z)))
        if hit[0] is None:
            U[i] = 1000.0; V[i] = -z
        else:
            loc, _n, fi, _d = hit
            tri = tris[fi]
            bc = barycentric(loc, *tri[0])
            uvt = tri[1]
            U[i] = 1000.0 + (uvt[0][0] * bc[0] + uvt[1][0] * bc[1] + uvt[2][0] * bc[2]) / .344
            V[i] = (uvt[0][1] * bc[0] + uvt[1][1] * bc[1] + uvt[2][1] * bc[2]) / .379
uvl = me.uv_layers.new(name='Flow')
li = np.zeros(len(me.loops), dtype=np.int64); me.loops.foreach_get('vertex_index', li)
uv = np.stack([U[li], V[li]], 1)
ls = np.zeros(len(me.polygons), dtype=np.int64); me.polygons.foreach_get('loop_start', ls)
lt = np.zeros(len(me.polygons), dtype=np.int64); me.polygons.foreach_get('loop_total', lt)
PER = 2 * math.pi * 8
for f in np.nonzero(np.array([np.ptp(uv[a:a + n, 0]) > 3 for a, n in zip(ls, lt)]))[0]:
    a, n = ls[f], lt[f]
    u = uv[a:a + n, 0].copy()
    med = np.median(u)
    u[:] = med   # 跨股或跨 UV 島接縫的面：壓成同一個 u（面很小，看不出來）
    uv[a:a + n, 0] = u
for f in np.nonzero(np.array([np.ptp(uv[a:a + n, 1]) > 3 for a, n in zip(ls, lt)]))[0]:
    a, n = ls[f], lt[f]
    uv[a:a + n, 1] = np.median(uv[a:a + n, 1])
uvl.data.foreach_set('uv', uv.ravel())
print('UV', round(time.time() - t0))
w.name = 'GT01_GodTree_Wood_LOD0'
bpy.data.objects.remove(_o3, do_unlink=True)
for o in list(bpy.data.objects):
    if o.type != 'MESH' or not o.name.endswith('_LOD0'):
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=S + 'GT01_GodTree_v005_braid.blend')
print('SAVED', round(time.time() - t0))
