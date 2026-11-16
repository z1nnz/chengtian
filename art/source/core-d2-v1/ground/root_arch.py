# D2 入口大根拱 DR01（核心組）：三股粗根絞成拱，淨跨約 8 m、淨高約 5 m；兩腳散成根鑽進土裡；頂上長蕨、垂藤
#   blender -b --factory-startup -P root_arch.py -- <tag> [quick]
import sys, math, random
from mathutils import Vector, noise

BASE = 'D:/chengtian/4-素材與快取/bark-sample/godtree_base.py'
src = open(BASE, encoding='utf-8').read()
exec(compile(src.split('# ---------------- 樹幹')[0], BASE, 'exec'))
noise.seed_set(5)
R = random.Random(5)
tail = src[src.index('# ---------------- 地面'):]
PL = 'D:/chengtian/4-素材與快取/bark-sample/plants.py'
exec(compile(open(PL, encoding='utf-8').read(), PL, 'exec'))

AX, AZ = 5.4, 6.3      # 拱中心線半寬、高（扣掉根粗後淨跨約 8 m、淨高約 5 m）


def gh(x, y):
    return fb((x, y, 0), .06, 3) * .35 + fb((x, y, 1), .5, 3) * .06


def centre(t):
    """t 0..1：左腳 → 拱頂 → 右腳；不對稱（頂點偏左、右肩較低）。"""
    a = math.pi * (1 - t)
    x = AX * math.cos(a) + .5 * math.sin(a * 2)
    z = AZ * math.sin(a) ** .85 * (1 - .10 * t) + .3
    y = .9 * math.sin(t * math.pi * 1.3) - .3
    return Vector((x, y, z))


def frame(t):
    d = (centre(min(1, t + .01)) - centre(max(0, t - .01))).normalized()
    side = Vector((0, 1, 0))
    nrm = d.cross(side).normalized()
    return d, side, nrm


NSTR = 3
objs = []
for k in range(NSTR):
    ph0 = k * 2 * math.pi / NSTR + .4
    r_off = [.8, .95, .9][k]
    thick = [1.2, .7, .92][k]
    pts = []
    # 左腳的根：往外、往下鑽
    fa = math.pi + (k - 1) * .75 + R.uniform(-.2, .2)
    c0 = centre(0)
    L = R.uniform(7, 11)
    for f in (1.0, .7, .42, .2):
        x = c0.x + math.cos(fa) * L * f
        y = c0.y + math.sin(fa) * L * f
        pts.append((x, y, gh(x, y) + (-1.3 if f == 1.0 else .25 * (1 - f))))
    n = 16
    for i in range(n + 1):
        t = i / n
        c = centre(t)
        d, side, nrm = frame(t)
        ph = ph0 + t * 2 * math.pi * 1.15
        w = r_off * (.55 + .45 * math.sin(t * math.pi))       # 腳邊三股靠攏，拱頂分開一點看得出是絞的
        p = c + side * math.cos(ph) * w + nrm * math.sin(ph) * w
        pts.append((p.x, p.y, max(p.z, gh(p.x, p.y) + .2)))
    fa = (k - 1) * .75 + R.uniform(-.2, .2)
    c1 = centre(1)
    L = R.uniform(7, 11)
    for f in (.2, .42, .7, 1.0):
        x = c1.x + math.cos(fa) * L * f
        y = c1.y + math.sin(fa) * L * f
        pts.append((x, y, gh(x, y) + (-1.3 if f == 1.0 else .25 * (1 - f))))
    objs.append(tube(f'Arch{k}', pts,
                     radius=lambda t, th=thick: th * (.22 + .78 * min(1, min(t, 1 - t) / .22) ** .8) * (1 + .12 * math.sin(t * 23)),
                     flat=lambda t: 1.0, seed=20 + k * 4.1, rib=.24, twist=.09))

# 腳邊的小根
for foot, c in ((0, centre(0)), (1, centre(1))):
    for j in range(7):
        a = (math.pi if foot == 0 else 0) + R.uniform(-1.5, 1.5)
        L = R.uniform(3, 7)
        th = R.uniform(.18, .42)
        pts = []
        for i in range(8):
            t = i / 7
            ww = math.sin(t * 5 + j) * .5 * t
            x = c.x + math.cos(a) * L * t - math.sin(a) * ww
            y = c.y + math.sin(a) * L * t + math.cos(a) * ww
            z = gh(x, y) + th * .3 + (1.4 * (1 - t / .25) if t < .25 else 0) - (th * 2.5 * ((t - .8) / .2) ** 1.3 if t > .8 else 0)
            pts.append((x, y, z))
        objs.append(tube(f'Foot{foot}_{j}', pts, radius=lambda t, th=th: th * (1 - .85 * t ** .7) + .04, flat=lambda t: 1.0,
                         seed=60 + foot * 10 + j, rib=.24, twist=.1))
# 嵌在三股之間凹溝裡的小根（跟著大根一起扭），以及半埋在樹皮上斜繞的中等根；兩頭都鑽進木頭裡
def _fac(t):
    return .55 + .45 * math.sin(t * math.pi)


for k in range(NSTR):
    ph0 = k * 2 * math.pi / NSTR + .4 + math.pi / NSTR      # 兩股之間
    r0 = R.uniform(.2, .34)
    pts = []
    for i in range(26):
        t = .05 + .9 * i / 25
        c = centre(t)
        d, side, nrm = frame(t)
        ph = ph0 + t * 2 * math.pi * 1.15 + .12 * math.sin(i * .9 + k)
        e = min(1, min(i, 25 - i) / 3)                       # 兩端收進木頭
        w = (1.18 * _fac(t) + .12) * (.45 + .55 * e)
        q = c + side * math.cos(ph) * w + nrm * math.sin(ph) * w
        pts.append(tuple(q))
    objs.append(tube(f'Groove{k}', pts, radius=lambda t, r0=r0: r0 * (.7 + .3 * math.sin(t * math.pi)) * (1 + .15 * math.sin(t * 31)),
                     flat=lambda t: 1.0, seed=90 + k, rib=.22, twist=.12))
for j in range(2):
    ph0 = R.uniform(0, 6.3)
    r0 = R.uniform(.32, .46)
    sgn = -1 if j else 1
    t0, t1 = (.12, .62) if j == 0 else (.4, .9)
    pts = []
    for i in range(22):
        t = t0 + (t1 - t0) * i / 21
        c = centre(t)
        d, side, nrm = frame(t)
        ph = ph0 + sgn * (i / 21) * 2 * math.pi * .8
        e = min(1, min(i, 21 - i) / 3)
        w = (1.5 * _fac(t) + .2) * (.4 + .6 * e)
        q = c + side * math.cos(ph) * w + nrm * math.sin(ph) * w
        pts.append(tuple(q))
    objs.append(tube(f'Wrap{j}', pts, radius=lambda t, r0=r0: r0 * (.6 + .4 * math.sin(t * math.pi)) * (1 + .12 * math.sin(t * 19)),
                     flat=lambda t: 1.0, seed=96 + j, rib=.24, twist=.1))
for o in objs:
    o.data.materials.append(MAT)
print('TRIS', sum(len(o.data.polygons) * 2 for o in objs))

# 植物：拱頂與肩上的蕨、垂下的藤葉、腳邊的蕨與心形葉
fern_mat = _leaf_material('UG01_Fern', (.035, .060, .022, 1), (.075, .11, .035, 1), (.10, .14, .05, 1), gloss=.55)
heart_mat = _leaf_material('UG02_Heart', (.025, .050, .020, 1), (.060, .095, .035, 1), (.11, .15, .07, 1), gloss=.35)
moss_mat = _leaf_material('MossTuft', (.030, .050, .012, 1), (.085, .12, .03, 1), (.10, .14, .04, 1), gloss=.8)
stem_mat = bpy.data.materials.new('UG_Stem')
stem_mat.use_nodes = True
next(n for n in stem_mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.05, .06, .025, 1)
for i in range(16):
    t = R.uniform(.18, .82)
    c = centre(t)
    d, side, nrm = frame(t)
    p = c + nrm * 1.85 + side * R.uniform(-.7, .7)
    fern(f'ArchFern{i}', p, R, R.uniform(.7, 1.2), fern_mat, stem_mat)
# 頂面一層短苔（沿拱頂撒）
mb = LeafBuf()
for i in range(26000 if not QUICK else 12000):
    t = R.uniform(.05, .95)
    c = centre(t)
    d, side, nrm = frame(t)
    ang = R.gauss(0, .55)
    out = (nrm * math.cos(ang) + side * math.sin(ang)).normalized()
    if out.z < .25:
        continue
    p = c + out * (1.9 + R.uniform(-.3, .05))
    dd = (out + Vector((R.uniform(-.5, .5), R.uniform(-.5, .5), .3))).normalized()
    dd, s2, u2 = _frame(dd)
    L = R.uniform(.06, .14)
    g = R.uniform(.7, 1.15)
    mb.leaf(p, dd, s2, u2, L, L * .22, shape=lambda u: (1 - u) ** .6, fold=.3, droop=R.uniform(0, .5), tint=(g, g, g * .8), nu=2, nv=1)
mb.build('ArchMoss', moss_mat)
# 垂藤：從拱底垂下，帶小葉
vb = LeafBuf()
for i in range(34):
    t = R.uniform(.22, .78)
    c = centre(t)
    d, side, nrm = frame(t)
    p0 = c - nrm * 1.3 + side * R.uniform(-1.0, 1.0)
    L = R.uniform(.8, 2.6)
    n = int(L / .09)
    sway = R.uniform(-.25, .25)
    for k in range(n):
        q = p0 + Vector((sway * (k / n) ** 2, math.sin(k * .5 + i) * .05, -L * k / n))
        dq, sq, uq = _frame(Vector((0.05, 0, -1)))
        vb.leaf(q, dq, sq, uq, .1, .004, shape=lambda u: 1.0, fold=0, tint=(.6, .7, .5), nu=1, nv=1)
        if k % 2 == 0:
            a = R.uniform(0, 6.3)
            ld = Vector((math.cos(a), math.sin(a), -.5))
            ld, ls, ln = _frame(ld)
            Ll = R.uniform(.10, .18)
            g = R.uniform(.8, 1.1)
            vb.leaf(q, ld, ls, ln, Ll, Ll * .42, shape=lambda u: math.sin(math.pi * (u * .9 + .1)) ** .7 * (1 - .6 * u ** 3), fold=.15,
                    droop=.3, tint=(g, g, g), nu=5, nv=3)
vb.build('ArchVines', heart_mat)
for foot, c in ((0, centre(0)), (1, centre(1))):
    for j in range(6):
        x, y = c.x + R.uniform(-4, 4), c.y + R.uniform(-3.5, 3.5)
        fern(f'FootFern{foot}_{j}', Vector((x, y, gh(x, y) - .02)), R, R.uniform(.8, 1.3), fern_mat, stem_mat)
    for j in range(8):
        x, y = c.x + R.uniform(-4, 4), c.y + R.uniform(-3.5, 3.5)
        heart_plant(f'FootHeart{foot}_{j}', Vector((x, y, gh(x, y))), R, R.uniform(.9, 1.4), heart_mat, stem_mat)

tail = tail[:tail.index('# 1.75 m 人形尺')]
exec(compile(tail, BASE, 'exec'))
bpy.ops.mesh.primitive_cylinder_add(radius=.22, depth=1.75, location=(1.2, 1.0, gh(1.2, 1.0) + .875))


def shot(n, loc, tgt, lens, res=(1536, 1024)):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.data.lens = lens
    c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = c
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = OUT + f'arch_{TAG}_{n}.png'
    bpy.ops.render.render(write_still=True)


shot('V2', (.5, -15, 1.7), (0, 0, 3.4), 22)
shot('tq', (-13, -13, 4), (0, 0, 3.2), 28)
