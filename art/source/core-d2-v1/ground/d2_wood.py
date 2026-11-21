# D2 根與木頭大件（核心組）：板根牆 DR02 A/B/C、倒伏巨木 DR06、巨樹樁 DR07
#   blender -b --factory-startup -P d2_wood.py -- <tag> [quick]
import sys, math, random
from mathutils import Vector, noise

BASE = 'D:/chengtian/4-素材與快取/bark-sample/godtree_base.py'
src = open(BASE, encoding='utf-8').read()
exec(compile(src.split('# ---------------- 樹幹')[0], BASE, 'exec'))
noise.seed_set(9)
R = random.Random(9)
tail = src[src.index('# ---------------- 地面'):]
PL = 'D:/chengtian/4-素材與快取/bark-sample/plants.py'
exec(compile(open(PL, encoding='utf-8').read(), PL, 'exec'))


def gh(x, y):
    return fb((x, y, 0), .05, 3) * .4 + fb((x, y, 1), .5, 3) * .06


fern_mat = _leaf_material('UG01_Fern', (.035, .060, .022, 1), (.075, .11, .035, 1), (.10, .14, .05, 1), gloss=.55)
heart_mat = _leaf_material('UG02_Heart', (.025, .050, .020, 1), (.060, .095, .035, 1), (.11, .15, .07, 1), gloss=.35)
moss_mat = _leaf_material('MossTuft', (.030, .050, .012, 1), (.085, .12, .03, 1), (.10, .14, .04, 1), gloss=.8)
mush_mat = mushroom_material()
stem_mat = bpy.data.materials.new('UG_Stem')
stem_mat.use_nodes = True
next(n for n in stem_mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.05, .06, .025, 1)
objs = []


def add(o):
    o.data.materials.append(MAT)
    objs.append(o)
    return o


def moss_on(name, pts_fn, n, spread=.5, Lr=(.03, .07)):
    """沿一條脊線（pts_fn(t) → 頂面點, 朝上法線）撒短苔。"""
    mb = LeafBuf()
    for i in range(n):
        t = R.uniform(.04, .96)
        p, up = pts_fn(t)
        side = up.cross(Vector((1, 0, 0)))
        if side.length < .1:
            side = up.cross(Vector((0, 1, 0)))
        side.normalize()
        q = p + side * R.gauss(0, spread) + up * R.uniform(-.08, .03)
        dd = (up + Vector((R.uniform(-.5, .5), R.uniform(-.5, .5), .3))).normalized()
        dd, s2, u2 = _frame(dd)
        L = R.uniform(*Lr)
        g = R.uniform(.7, 1.15)
        mb.leaf(q, dd, s2, u2, L, L * .22, shape=lambda u: (1 - u) ** .6, fold=.3, droop=R.uniform(0, .5), tint=(g, g, g * .8), nu=2, nv=1)
    return mb.build(name, moss_mat)


# ---------------- 板根牆：從土裡拱出來、像牆一樣立著、再鑽回土裡 ----------------
def root_wall(name, origin, yaw, L, H, seed, fork=False):
    rr = random.Random(seed)
    ca, sa = math.cos(yaw), math.sin(yaw)

    def W(u, v, z):          # 區域座標（沿牆 u、橫向 v）→ 世界
        x, y = origin.x + ca * u - sa * v, origin.y + sa * u + ca * v
        return Vector((x, y, gh(x, y) + z))

    wob = rr.uniform(.8, 1.6)
    ph = rr.uniform(0, 6.3)

    def ridge(t):            # 牆的中心線
        u = (t - .5) * L
        v = math.sin(t * 4.2 + ph) * wob + .5 * math.sin(t * 11 + ph)
        prof = math.sin(math.pi * t) ** .55 * (1 - .32 * math.sin(t * 8 + ph) ** 2)
        return u, v, prof

    th = H * .27
    nst = 3 if H > 2.5 else 2
    tw = rr.uniform(.7, 1.1)
    for k in range(nst):     # 幾股粗根絞在一起，貼著地面起伏；每股粗細不同、兩端鑽進土裡
        pts = []
        n = 22
        ph0 = k * 2 * math.pi / nst + ph
        thk = th * [1.15, .75, .9][k]
        for i in range(n + 1):
            t = i / n
            u, v, prof = ridge(t)
            a2 = ph0 + t * 2 * math.pi * tw
            off = H * .2 * prof
            z = H * .42 * prof + math.sin(a2) * off + thk * .2
            e = min(1, min(i, n - i) / 2.5)
            z = z * e - 1.3 * (1 - e)
            pts.append(tuple(W(u, v + math.cos(a2) * off, z)))
        add(tube(f'{name}_s{k}', pts,
                 radius=lambda t, thk=thk: thk * (.2 + .8 * math.sin(math.pi * t) ** .5) * (1 + .1 * math.sin(t * 21)),
                 flat=lambda t: 1.0, seed=seed + k * 3.3, rib=.24, twist=.08))
    # 從牆上撇出去落地的支根
    for j in range(rr.randint(7, 10)):
        t0 = rr.uniform(.12, .88)
        u, v, prof = ridge(t0)
        sgn = rr.choice([-1, 1])
        Lr = rr.uniform(3, 6.5)
        r0 = rr.uniform(.2, .45)
        h0 = H * prof * rr.uniform(.3, .7)
        fwd = rr.uniform(-.6, .6)
        pts = []
        for i in range(10):
            t = i / 9
            pts.append(tuple(W(u + fwd * Lr * t, v + sgn * (Lr * t + .1), h0 * max(0, 1 - t / .5) ** 2 + r0 * .3 * (1 - t) - (r0 * 2.5 * ((t - .8) / .2) ** 1.3 if t > .8 else 0))))
        add(tube(f'{name}_b{j}', pts, radius=lambda t, r0=r0: r0 * (1 - .85 * t ** .7) + .04, flat=lambda t: 1.0, seed=seed + 10 + j, rib=.24, twist=.1))
    if fork:
        u, v, prof = ridge(.55)
        pts = []
        for i in range(12):
            t = i / 11
            pts.append(tuple(W(u + 5.5 * t, v + 4.5 * t ** 1.3, H * .55 * prof * max(0, 1 - t) ** 1.2 * .5 + .3 * (1 - t) - (1.2 if i == 11 else 0))))
        add(tube(f'{name}_fork', pts, radius=lambda t: th * .7 * (1 - .7 * t) + .08, flat=lambda t: 1.0 + 1.2 * (1 - t), seed=seed + 30, rib=.22, twist=.06))

    def top(t):
        u, v, prof = ridge(t)
        return W(u, v, H * prof * .88), Vector((0, 0, 1))
    moss_on(name + '_moss', top, int(L * H * (260 if QUICK else 520)), spread=H * .14)
    for j in range(int(L / 2.2)):
        t = rr.uniform(.2, .8)
        p, _ = top(t)
        fern(f'{name}_fern{j}', p + Vector((0, rr.uniform(-.2, .2), -.05)), R, rr.uniform(.6, 1.0), fern_mat, stem_mat)
    for j in range(int(L / 1.6)):
        u = rr.uniform(-L * .45, L * .45)
        v = rr.choice([-1, 1]) * rr.uniform(.9, 2.2)
        fern(f'{name}_gf{j}', W(u, v, -.02), R, rr.uniform(.8, 1.3), fern_mat, stem_mat)
    for j in range(4):
        u = rr.uniform(-L * .4, L * .4)
        v = rr.choice([-1, 1]) * rr.uniform(.6, 1.2)
        q = W(u, v, 0)
        mushrooms(f'{name}_mush{j}', q, R, rr.randint(4, 9), rr.uniform(1.0, 1.6), mush_mat, ground=gh)


# ---------------- 倒伏巨木：帶翻起的根盤、另一頭斷裂、上面長苔蕨 ----------------
def fallen_log(name, origin, yaw, L, r, seed):
    rr = random.Random(seed)
    ca, sa = math.cos(yaw), math.sin(yaw)

    def W(u, v, z):
        x, y = origin.x + ca * u - sa * v, origin.y + sa * u + ca * v
        return Vector((x, y, gh(x, y) + z))
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        pts.append(tuple(W((t - .5) * L, math.sin(t * 2.2) * 1.4, r * (.78 - .25 * t) + .25 * math.sin(t * 3) + .9 * t ** 3)))
    add(tube(name, pts, radius=lambda t: r * (1 - .32 * t) * (1 + .06 * math.sin(t * 17)) * (1 - .5 * max(0, (t - .96) / .04)),
             flat=lambda t: .92, seed=seed, rib=.18, twist=.04))
    # 根盤：粗的一頭，根往四面張開
    base = W(-.5 * L, 0, r * .8)
    ax = Vector((ca, sa, 0))
    for j in range(11):
        a = j * 2 * math.pi / 11 + rr.uniform(-.2, .2)
        rad = Vector((-sa * math.cos(a), ca * math.cos(a), math.sin(a)))
        Lr = rr.uniform(1.8, 3.6)
        r0 = rr.uniform(.22, .5)
        pp = []
        for i in range(8):
            t = i / 7
            q = base + ax * (.6 - 1.6 * t ** .7) + rad * (r * .5 + Lr * t) + Vector((0, 0, -.5 * t * t * Lr * .3))
            q.z = max(q.z, gh(q.x, q.y) + r0 * (1 - t) * .5 - .1 * t)
            pp.append(tuple(q))
        add(tube(f'{name}_rp{j}', pp, radius=lambda t, r0=r0: r0 * (1 - .8 * t ** .8) + .04, flat=lambda t: 1.0, seed=seed + 5 + j, rib=.24, twist=.12))

    def top(t):
        return W((t - .5) * L, math.sin(t * 2.2) * 1.4, r * (.78 - .25 * t) + .25 * math.sin(t * 3) + .9 * t ** 3 + r * (1 - .32 * t) * .9), Vector((0, 0, 1))
    moss_on(name + '_moss', top, int(L * (420 if QUICK else 900)), spread=r * .32)
    for j in range(int(L / 2.5)):
        p, _ = top(rr.uniform(.1, .9))
        fern(f'{name}_fern{j}', p + Vector((0, 0, -.08)), R, rr.uniform(.6, 1.0), fern_mat, stem_mat)
    for j in range(5):
        t = rr.uniform(.1, .9)
        q = W((t - .5) * L, math.sin(t * 2.2) * .8 + rr.choice([-1, 1]) * (r * .9 + .2), 0)
        mushrooms(f'{name}_mush{j}', q, R, rr.randint(4, 10), rr.uniform(1.0, 1.7), mush_mat, ground=gh)


# ---------------- 巨樹樁：根頸張開抓地、頂端朽空 ----------------
def stump(name, origin, r, h, seed):
    rr = random.Random(seed)
    g0 = gh(origin.x, origin.y)
    lean = (rr.uniform(-.15, .15), rr.uniform(-.15, .15))
    pts = [(origin.x + lean[0] * z, origin.y + lean[1] * z, g0 + z) for z in (-.8, 0, h * .35, h * .7, h)]
    nroot = rr.randint(6, 8)
    angs = [j * 2 * math.pi / nroot + rr.uniform(-.25, .25) for j in range(nroot)]

    def lobes(phi, z):
        e = 0
        for a in angs:
            d = (phi - a + math.pi) % (2 * math.pi) - math.pi
            e += r * .55 * max(0, 1 - max(0, z - g0) / (h * .6)) ** 1.5 * math.exp(-(d / .28) ** 2)
        # 頂端參差：越靠近頂越依角度內縮
        topf = max(0, (z - g0 - h * .8) / (h * .2))
        return e - r * .25 * topf * (.5 + .5 * math.sin(phi * 3 + seed))
    add(tube(name, pts, radius=lambda t: r * (1 - .12 * t), flat=lambda t: 1.0, seed=seed, rib=.2, twist=.04, extra=lobes))
    for j, a in enumerate(angs):
        Lr = rr.uniform(2.5, 5)
        r0 = r * rr.uniform(.28, .4)
        pp = []
        for i in range(10):
            t = i / 9
            x = origin.x + math.cos(a) * (r * .6 + Lr * t) - math.sin(a) * math.sin(t * 4 + j) * .4 * t
            y = origin.y + math.sin(a) * (r * .6 + Lr * t) + math.cos(a) * math.sin(t * 4 + j) * .4 * t
            pp.append((x, y, gh(x, y) + h * .45 * max(0, 1 - t / .45) ** 2 + r0 * .35 * (1 - t) - (r0 * 2.5 * ((t - .8) / .2) ** 1.3 if t > .8 else 0)))
        add(tube(f'{name}_r{j}', pp, radius=lambda t, r0=r0: r0 * (1 - .85 * t ** .7) + .04, flat=lambda t: 1.0 + .5 * max(0, 1 - t / .3), seed=seed + 3 + j, rib=.24, twist=.1))
    # 朽空的芯：頂面下凹的深色圓盤
    bpy.ops.mesh.primitive_circle_add(vertices=40, radius=r * .82, fill_type='TRIFAN', location=(origin.x + lean[0] * h, origin.y + lean[1] * h, g0 + h * .82))
    c = bpy.context.object
    cm = bpy.data.materials.new(name + '_core')
    cm.use_nodes = True
    b = next(n for n in cm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (.022, .017, .012, 1)
    b.inputs['Roughness'].default_value = .9
    c.data.materials.append(cm)

    def top(t):
        a = t * 2 * math.pi
        return Vector((origin.x + lean[0] * h + math.cos(a) * r * .8, origin.y + lean[1] * h + math.sin(a) * r * .8, g0 + h * .95)), Vector((0, 0, 1))
    moss_on(name + '_moss', top, 1500 if QUICK else 3200, spread=.2)
    for j in range(5):
        p, _ = top(rr.random())
        fern(f'{name}_fern{j}', p + Vector((0, 0, -.1)), R, rr.uniform(.6, 1.0), fern_mat, stem_mat)
    for j in range(5):
        a = rr.uniform(0, 6.3)
        q = Vector((origin.x + math.cos(a) * (r + .5), origin.y + math.sin(a) * (r + .5), 0))
        mushrooms(f'{name}_mush{j}', q, R, rr.randint(4, 10), rr.uniform(1.0, 1.8), mush_mat, ground=gh)


root_wall('DR02_A', Vector((-17, 9, 0)), math.radians(20), 13, 4.0, 11)
root_wall('DR02_B', Vector((-1, 14, 0)), math.radians(-8), 11, 2.0, 22)
root_wall('DR02_C', Vector((15, 9, 0)), math.radians(-30), 12, 3.0, 33, fork=True)
fallen_log('DR06_A', Vector((-8, -6, 0)), math.radians(12), 16, 1.0, 44)
stump('DR07_A', Vector((10, -5, 0)), 1.5, 2.6, 55)
print('TRIS', sum(len(o.data.polygons) * 2 for o in objs))

tail = tail[:tail.index('# 1.75 m 人形尺')].replace("vol.inputs['Density'].default_value = .0055", "vol.inputs['Density'].default_value = .0025")
exec(compile(tail, BASE, 'exec'))
for hx, hy in ((0, -1), (-13, 5.5), (13.5, -2), (12, 5.5)):
    bpy.ops.mesh.primitive_cylinder_add(radius=.22, depth=1.75, location=(hx, hy, gh(hx, hy) + .875))


def shot(n, loc, tgt, lens, res=(1536, 1024)):
    if 'norender' in ARGS:
        return
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.data.lens = lens
    c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = c
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = OUT + f'wood_{TAG}_{n}.png'
    bpy.ops.render.render(write_still=True)


shot('all', (0, -27, 5), (0, 4, 1.5), 22)
shot('wallA', (-11, -1, 1.7), (-17, 9, 2.0), 24)
shot('log', (-4, -17, 1.7), (-8, -6, 1.0), 26)
shot('stump', (15, -13, 1.7), (10, -5, 1.2), 28)
shot('wallC', (11, -2, 1.7), (15, 9, 1.5), 24)

if 'save' in ARGS:
    bpy.ops.wm.save_as_mainfile(filepath=OUT + 'd2_wood_' + TAG + '.blend')
    print('SAVED')
