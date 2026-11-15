# D2 神木 v3：照神木設定圖（godtree-concept-1）——六股粗木絞成樹幹，往下散成板根，往上分成主枝
import sys, math, random
from pathlib import Path
from mathutils import Vector

BASE = str(Path(__file__).resolve().parent / 'godtree_base.py')
src = open(BASE, encoding='utf-8').read()
lib = src.split('# ---------------- 樹幹')[0]
exec(compile(lib, BASE, 'exec'))          # tube(), fb(), MAT, R, objs, TAG/QUICK...

tail = src[src.index('# ---------------- 地面'):]


def gh(x, y):
    rr = math.hypot(x, y)
    return fb((x, y, 0), .04, 3) * .9 + fb((x, y, 1), .5, 3) * .08 + 2.2 * max(0, 1 - rr / 24) ** 1.6


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


# ---------------- 六股主幹 ----------------
NS = 6
TW = .055          # 每公尺扭轉的弧度
ZS = 30.0          # 分枝高度
SR = 3.3           # 每股粗（半徑）
strand_ang = [i * 2 * math.pi / NS + R.uniform(-.25, .25) for i in range(NS)]


def _ss(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def strand_r(c, t):
    d = math.hypot(c.x, c.y)
    if c.z > ZS - 1.5:                            # 主枝
        return (SR * .88 * (1 - .9 * clamp((d - 5) / 30) ** .9) + .12) * (1 - .75 * _ss((t - .9) / .1))
    rt = SR * (1 - .12 * clamp((c.z - 7) / (ZS - 7)))
    rr = .4 + (SR * .95 - .4) * clamp((38 - d) / 28) ** 1.6
    w = _ss((d - 6.8) / 6.0)
    return rt * (1 - w) + rr * w


def strand_f(c, t):
    d = math.hypot(c.x, c.y)
    if c.z > ZS - 1.5:
        return 1.0
    w = _ss((d - 6.8) / 6.0)
    return 1 + 1.0 * w * clamp((20 - d) / 8)


LIMBS = []
TIPS = []
for i, a in enumerate(strand_ang):
    pts = []
    # 根端（地下）→ 拱起的板根 → 緩緩轉上來接樹幹（轉彎半徑要大於股粗，否則會摺疊）
    L = R.uniform(32, 42)
    w = R.uniform(-1, 1)
    arch = R.uniform(1.0, 2.6)
    for d, zf in [(L, -1.6), (L * .8, .2), (L * .62, arch * .7), (L * .47, arch), (16, arch + 1.6), (12.5, 4.6), (9.6, 7.6), (7.6, 11.0)]:
        aa = a + w * .10 * (d / L)
        x, y = d * math.cos(aa), d * math.sin(aa)
        pts.append((x, y, gh(x, y) + zf))
    for z in [15, 20, 25, 29]:
        rr = 6.0 - 1.6 * (z - 15) / 14
        aa = a + TW * (z - 11)
        pts.append((rr * math.cos(aa), rr * math.sin(aa), z))
    # 主枝：往外往上伸，彎曲多節
    a_end = a + TW * (ZS - 11) + R.uniform(-.3, .3)
    reach = R.uniform(26, 36)
    limb = []
    for k, f in enumerate([.2, .38, .55, .72, .87, 1.0]):
        d = 5 + (reach - 5) * f
        aa = a_end + math.sin(k * 1.7 + i) * .12 + R.uniform(-.06, .06)
        dz = 14 * math.sin(f * 2.2) + R.uniform(-1.5, 1.5) - 3 * f * f
        limb.append((d * math.cos(aa), d * math.sin(aa), ZS + dz))
    pts += limb
    LIMBS.append(limb)
    objs.append(tube(f'Strand{i}', pts, radius=None, flat=None, rpos=strand_r, fpos=strand_f,
                     seed=200 + i * 7.3, rib=.16, twist=.05))

# 次枝與三級枝：從主枝上長出，往外往上散開（樹冠之後掛在這些枝梢上）
def branch(name, p0, dirv, L, r0, seed, depth):
    pts = [p0]
    p = Vector(p0)
    dv = Vector(dirv).normalized()
    n = 5
    for k in range(1, n + 1):
        dv = (dv + Vector((R.uniform(-.25, .25), R.uniform(-.25, .25), R.uniform(-.08, .18)))).normalized()
        p = p + dv * (L / n)
        pts.append(tuple(p))
    objs.append(tube(name, pts, radius=lambda t, r0=r0: r0 * (1 - .85 * t) + .05, flat=lambda t: 1.0,
                     seed=seed, rib=.12, twist=.08))
    TIPS.append((Vector(pts[-1]), dv.copy(), r0 * .15 + .05))
    TIPS.append((Vector(pts[len(pts) // 2]), (dv + Vector((0, 0, .3))).normalized(), r0 * .5))
    if depth > 0:
        for j in range(R.choice([2, 3])):
            tt = R.uniform(.35, .85)
            idx = int(tt * n)
            q = Vector(pts[idx])
            sd = (dv + Vector((R.uniform(-1, 1), R.uniform(-1, 1), R.uniform(0, .6)))).normalized()
            branch(name + f'_{j}', tuple(q), tuple(sd), L * R.uniform(.45, .6), r0 * (1 - .85 * tt) * .65, seed + j * 3.3, depth - 1)


for i, limb in enumerate(LIMBS):
    for j, k in enumerate([1, 2, 3, 4]):
        if R.random() < .25:
            continue
        p0 = Vector(limb[k])
        prev = Vector(limb[k - 1])
        out = (p0 - prev).normalized()
        side = out.cross(Vector((0, 0, 1))).normalized() * R.choice([-1, 1])
        dv = (out * .6 + side * .7 + Vector((0, 0, R.uniform(.2, .6)))).normalized()
        rr = strand_r(p0, 0) * .55
        branch(f'Br{i}_{j}', tuple(p0), tuple(dv), R.uniform(10, 16), rr, 500 + i * 11 + j, 1)

# 中心芯：補滿六股之間的洞（大多被遮住）
objs.append(tube('Core', [(0, 0, -1), (0, 0, 10), (.2, 0, 22), (.4, .1, ZS + 2)],
                 radius=lambda t: 5.4 - 1.6 * t, flat=lambda t: 1.0, seed=7.0, rib=.12, twist=.06))


# ---------------- 次級板根與地表細根 ----------------
def snake(name, a, L, thick, start, seed, wig=1.2, z0=None):
    dirv = Vector((math.cos(a), math.sin(a), 0))
    perp = Vector((-dirv.y, dirv.x, 0))
    rad = lambda t: thick * (1.0 - .9 * t ** .6) + .06
    pts = []
    N = 10
    for k in range(N + 1):
        t = k / N
        ww = (math.sin(t * 5.0 + seed) * (.2 + t) + fb((seed, t * 3, 0), 1, 2)) * wig * min(1, t * 4)
        p = dirv * (start + L * t) + perp * ww
        zs = gh(p.x, p.y) + rad(t) * .3
        if z0 is not None and t < .2:
            zs = z0 * (1 - t / .2) + zs * (t / .2)
        if t > .8:
            zs -= rad(t) * 2.4 * ((t - .8) / .2) ** 1.3
        pts.append((p.x, p.y, zs))
    return tube(name, pts, radius=rad, flat=lambda t: 1.0 + .6 * max(0, 1 - t / .25) ** 2, seed=seed, rib=.22, twist=.07)


for n in range(20):
    a = strand_ang[n % NS] + math.pi / NS + R.uniform(-.25, .25) if n < NS else R.uniform(0, 2 * math.pi)
    L = R.uniform(20, 36)
    th = R.uniform(1.0, 2.0)
    objs.append(snake(f'Root{n}', a, L, th, start=10.5, seed=300 + n, z0=3.2))
    for f in range(2):
        st = 10.5 + L * R.uniform(.3, .6)
        fa = a + R.choice([-1, 1]) * R.uniform(.35, .8)
        objs.append(snake(f'Root{n}f{f}', fa, R.uniform(8, 15), th * R.uniform(.3, .45), start=st, seed=330 + n * 3 + f))
for n in range(40):
    a = R.uniform(0, 2 * math.pi)
    objs.append(snake(f'Small{n}', a, R.uniform(6, 13), R.uniform(.18, .4), start=R.uniform(12, 30), seed=400 + n))


# ---------------- 樹冠：照天空島世界樹做法（一片片立體小葉沿枝梢排）----------------
import sys as _sys
_TG = str(Path(__file__).resolve().parent / 'tree_gen.py')
_code = open(_TG, encoding='utf-8').read()
_lm = _code[_code.index('def leaf_material'):_code.index('def scene_and_render')]
_code = _code[:_code.index('def bark_material')].replace("(.02 if level == 4 else .045)", "(LEAF_SP4 if level == 4 else LEAF_SP3)") + _lm
_argv = _sys.argv
_sys.argv = ['x', '--', '.', '11']
TG = {}
exec(compile(_code, _TG, 'exec'), TG)
_sys.argv = _argv
TG['LEAF_LEN'] = (.16, .24)
TG['LEAF_SP3'] = .16
TG['LEAF_SP4'] = .075
TG['RINGS'] = {0: 10, 1: 8, 2: 6, 3: 4, 4: 3}
# 深綠為主、夾舊金色（設定圖的樹冠）
TG['PALETTE'] = ((.020, .050, .025), (.035, .085, .035), (.07, .13, .045), (.20, .19, .06), (.36, .29, .09))
nt = 0
for k, (p0, dv, rr) in enumerate(TIPS):
    d = Vector((dv.x, dv.y, max(dv.z, .15))).normalized()
    TG['grow'](p0, d, R.uniform(8, 12), max(.12, min(rr, .35)), 1, 1000 + k)
wood = TG['tube_mesh']()
wo = bpy.data.objects.new('CrownWood', wood)
bpy.context.scene.collection.objects.link(wo)
wo.data.materials.append(MAT)
lm, nleaf = TG['leaf_mesh']()
lo = bpy.data.objects.new('CrownLeaves', lm)
bpy.context.scene.collection.objects.link(lo)
lo.data.materials.append(TG['leaf_material']())
print('LEAVES', nleaf, 'TWIGTRIS', len(wood.polygons) * 2)

for o in objs:
    o.data.materials.append(MAT)
print('TRIS', sum(len(o.data.polygons) * 2 for o in objs))

# 地面、霧、光、相機：沿用 base 的設定，改相機與人
tail = tail.replace("primitive_grid_add(x_subdivisions=300, y_subdivisions=300, size=90)", "primitive_grid_add(x_subdivisions=500, y_subdivisions=500, size=200)")
tail = tail.replace("primitive_grid_add(x_subdivisions=400, y_subdivisions=400, size=130)", "primitive_grid_add(x_subdivisions=500, y_subdivisions=500, size=200)")
tail = tail.replace("fog.scale = (160, 160, 50)", "fog.scale = (240, 240, 90)").replace("vol.inputs['Density'].default_value = .0055", "vol.inputs['Density'].default_value = .0028")
cam_part = tail[tail.index('# 1.75 m 人形尺'):]
tail = tail[:tail.index('# 1.75 m 人形尺')]
exec(compile(tail, BASE, 'exec'))

hmat = bpy.data.materials.new('Human')
hmat.use_nodes = True
next(n for n in hmat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.75, .72, .66, 1)
for hx, hy in [(2.0, -17), (3.0, -17.4), (4.1, -17.1)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=.22, depth=1.75, location=(hx, hy, gh(hx, hy) + .875))
    bpy.context.object.data.materials.append(hmat)


def shot(n, loc, tgt, lens, res=(1536, 1024)):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.data.lens = lens
    c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = c
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = OUT + f'godtree3_{TAG}_{n}.png'
    bpy.ops.render.render(write_still=True)


shot('full', (0, -82, 4), (0, 0, 24), 22)
shot('base', (6, -40, 2.2), (0, 0, 9), 24)
