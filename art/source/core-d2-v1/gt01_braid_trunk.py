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
ZCUT = 26.0   # 11/22：切在 16 m 會留一圈淺溝 → 切到分枝附近，下面整段都是新的股
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


def R_OLD(z):   # 原本樹幹在各高度的半徑（gt_probe2 量的中位數）
    zs = [14, 16, 20, 24, 28, 32, 40]
    rs = [8.6, 8.0, 7.8, 7.4, 6.9, 6.6, 6.2]
    return float(np.interp(z, zs, rs))


def main_strand(th0, Rg, Rend, rA, twist, seed, arch=0.0, ride=0.0):
    # v006（11/22 z1nnz「你講的都要改」）：粗細差三倍的粗繩、股之間留深縫、中段收腰、大根拱離地面
    pts = []
    n = 170
    for k in range(n + 1):
        s_ = k / n
        if s_ < .45:
            u = s_ / .45
            z = lerp(32, 9, u)
            rad = lerp(.6 * rA, rA, smooth(u))
            inset = lerp(1.0, .3, smooth(min(1, max(0, (32 - z) / 6))))
            c_top = R_OLD(z) - rad * inset
            waist = 5.4 + rad * .4 + ride
            r9 = 6.4 + rA * .35 + ride
            if z >= 24:   # 上段股貼著原本樹幹（切口在 26 m）→ 不會在交界留一圈屋簷
                r = c_top
            elif z >= 13:
                r = lerp(waist, c_top, smooth(max(0, (z - 19) / 5)))
            else:
                r = lerp(r9, waist, smooth((z - 9) / 4))
            th = th0 + twist * u
            sq = 1.0
        elif s_ < .68:
            u = (s_ - .45) / .23
            z = 9 - 8.1 * math.sin(u * math.pi / 2)
            r9 = 6.4 + rA * .35 + ride
            r = r9 + (Rg - r9) * (1 - math.cos(u * math.pi / 2))
            rad = lerp(rA, rA * .6, u)
            th = th0 + twist + twist * .3 * u
            sq = lerp(1.0, .85, u)
        else:
            u = (s_ - .68) / .32
            hump = arch * math.sin(math.pi * min(1, u / .6))   # 大根拱起來離開地面，看得到下面的陰影
            z = (.9 + hump) if u < .75 else (.9 - 2.2 * ((u - .75) / .25) ** 1.5)
            r = lerp(Rg, Rend, u)
            rad = rA * .6 * (1 - .85 * u ** 1.2)
            th = th0 + twist * 1.3 + twist * .2 * u
            sq = .85
        wob = Vector((noise.noise(Vector((s_ * 6, seed, 0))), noise.noise(Vector((s_ * 6, seed, 7))), 0)) * (.6 if s_ > .4 else .3)
        pts.append((Vector((math.cos(th) * r, math.sin(th) * r, z)) + wob, rad, sq))
    return pts


N = 8
TW = 1.1
roots = []
RADS = [3.6, 3.3, 3.0, 2.6, 2.2, 1.9, 1.6, 1.4]
R.shuffle(RADS)
for i in range(N):
    th0 = 2 * math.pi * i / N + R.uniform(-.12, .12)
    rA = RADS[i]
    big = rA > 2.4
    Rg = R.uniform(15, 19) if big else R.uniform(12, 15)
    Rend = Rg + (R.uniform(16, 26) if big else R.uniform(8, 14))
    pts = main_strand(th0, Rg, Rend, rA, TW * R.uniform(.85, 1.15), i * 3.1, arch=R.uniform(.9, 1.6) if big else R.uniform(.2, .6))
    STR.append(pts)
    roots.append(pts)
# 兩股反向扭的細繩：跨過別的股（設定圖有一股壓過另一股）
for i, (th0, rA) in enumerate(((.9, 1.4), (3.6, 1.2))):
    pts = main_strand(th0, 13, 24, rA, -1.0, 50 + i, arch=.4, ride=1.9)
    STR.append(pts)
    roots.append(pts)

# 兩條長根一路爬到祭壇邊（設定圖 V3、V4）
_ALT = math.atan2(7.0 - 30.0, 7.0 + 24.0)
for dth, Rend_, rA_ in ((-.07, 33, 2.4), (.09, 29, 2.0)):
    pts = main_strand(_ALT + dth - .24, 17, Rend_, rA_, .15, 77 + dth * 10, arch=1.0)
    STR.append(pts)
    roots.append(pts)

# 右邊低分叉：一根大枝在 7 m 高就從樹幹分出去往右上走，中間留空看得到天空（V3 右側；相機在 (+28,-45) 往北看 → 右邊是 +x）
_fk = [(5.5, 5), (7.5, 10), (10.0, 14.5), (13.5, 19), (16.0, 24.5), (19.5, 29), (21.5, 34)]
_fth = -.15
pts = []
for k in range(101):
    u = k / 100
    rr = float(np.interp(u * 6, range(7), [a for a, b in _fk])); zz = float(np.interp(u * 6, range(7), [b for a, b in _fk]))
    th = _fth + .25 * u + .12 * math.sin(u * 7)   # 彎彎曲曲，不要一根直棍
    pts.append((Vector((math.cos(th) * rr, math.sin(th) * rr, zz + .8 * math.sin(u * 9))), lerp(3.4, .9, u ** .8), 1.0))
STR.append(pts)

# 樹瘤：幾顆短胖的瘤長在股上
for i in range(0):   # 樹瘤拿掉：看起來像繩結
    th = R.uniform(0, 6.28); zc = R.uniform(4, 15)
    rc = 4.6 + 3.0 + (2.0 if zc < 9 else 0)
    c = Vector((math.cos(th) * rc, math.sin(th) * rc, zc))
    dv = Vector((-math.sin(th), math.cos(th), .6)).normalized()
    pts = [(c + dv * lerp(-1.0, 1.0, k / 10), 1.3 * math.sin(math.pi * k / 10) ** .5 + .05, 1.0) for k in range(11)]
    STR.append(pts)

# 支根：從主根外擴段分岔出去
for i, pts in enumerate(roots):
    for _ in range(R.choice((2, 3, 3))):   # 11/22 根要更多（設定圖往四面八方爬）
        k0 = R.randint(100, 130)
        p0, r0, _s = pts[k0]
        dirv = pts[k0 + 6][0] - p0
        dirv.z = 0
        dirv.normalize()
        side = Vector((-dirv.y, dirv.x, 0)) * R.choice((-1, 1))
        L = R.uniform(8, 20)
        sub = []
        n = 60
        for k in range(n + 1):
            u = k / n
            q = p0 + dirv * (L * u) + side * (L * .45 * u ** .8)
            q.z = lerp(p0.z, .55, min(1, u * 3)) if u < .75 else .55 - 1.4 * ((u - .75) / .25) ** 1.5   # 貼地爬、最後才鑽進土裡
            q += Vector((noise.noise(Vector((u * 5, i, 3))), noise.noise(Vector((u * 5, i, 9))), 0)) * .4
            sub.append((q, r0 * .6 * (1 - .85 * u), .7))
        STR.append(sub)

# 細根：從主根之間的樹幹底部冒出來、彎彎曲曲貼地爬出去（根與根之間不要只是平滑的面）
for i in range(20):
    th = 2 * math.pi * (i + .5) / 20 + R.uniform(-.1, .1)
    L = R.uniform(9, 24)
    r0 = R.uniform(.7, 1.2)
    p0 = Vector((math.cos(th) * 7.0, math.sin(th) * 7.0, 2.2))
    dirv = Vector((math.cos(th), math.sin(th), 0))
    side = Vector((-dirv.y, dirv.x, 0))
    sub = []
    n = 70
    curl = R.uniform(-.35, .35)
    for k in range(n + 1):
        u = k / n
        q = p0 + dirv * (L * u) + side * (L * curl * u * u)
        q += side * noise.noise(Vector((u * 4, i * 1.7, 5))) * 1.2
        q.z = lerp(2.2, .5, min(1, u * 4) ** .7) if u < .8 else .5 - 1.3 * ((u - .8) / .2) ** 1.5
        sub.append((q, r0 * (1 - .8 * u) + .08, .75))
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
# 11/22：場景地面在神木四周比 0 高 0.3–2 m → 根全被埋掉。照場景地形（樹的區域座標）把低處的點往上抬，根貼著實際地面爬
_GH = np.load(S + 'GT01_ground_rel.npy')


def gz(x, y):
    fx = min(99.999, max(0, x + 50)); fy = min(99.999, max(0, y + 50))
    ix, iy = int(fx), int(fy); tx, ty = fx - ix, fy - iy
    return (_GH[iy, ix] * (1 - tx) * (1 - ty) + _GH[iy, ix + 1] * tx * (1 - ty) + _GH[iy + 1, ix] * (1 - tx) * ty + _GH[iy + 1, ix + 1] * tx * ty)


for pts in STR:
    for k, (p, rad, sq) in enumerate(pts):
        wl = min(1.0, max(0.0, (7 - p.z) / 5))
        if wl > 0:
            pts[k] = (Vector((p.x, p.y, p.z + (gz(p.x, p.y) - .3) * wl)), rad, sq)
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
core = bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=5.5, radius2=4.2, depth=31)   # 核心細一點：股之間的縫要深、要暗
bmesh.ops.translate(bm, verts=core['verts'], vec=Vector((0, 0, 13.5)))
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
    if z < 36:
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
