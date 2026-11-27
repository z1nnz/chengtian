# TR20 傘頂松（D2 設定圖 V1–V6 背景裡的高松）：高直幹、下半段光禿、頂上 2–4 層平展雲片狀樹冠
#   blender -b --factory-startup -P umbrella_pine.py -- <tag> [quick] [seed]
#   與 pine_gen.py（11/16 定版的圓團松）分開，不動定版。
import os, sys, math, random
from mathutils import Vector, noise

os.environ.setdefault('GT_BARK', 'pine_bark')
BASE = 'D:/chengtian/4-素材與快取/bark-sample/godtree_base.py'
src = open(BASE, encoding='utf-8').read()
exec(compile(src.split('# ---------------- 樹幹')[0], BASE, 'exec'))
SEED = int([a for a in ARGS if a.isdigit()][0]) if any(a.isdigit() for a in ARGS) else 5
R = random.Random(SEED)
noise.seed_set(SEED)
tail = src[src.index('# ---------------- 地面'):]
TH = float(os.environ.get('UP_H', 25.0))          # 樹高（z1nnz 11/21：30 m 有一點點太高 → 25 m）
CS = float(os.environ.get('UP_CS', 1.0))
BEND = float(os.environ.get('UP_BEND', 1.0))       # 0＝11/21 打勾版的直枝；1＝枝幹彎曲（場景用）          # 樹冠與枝幹的絕對尺寸倍率（1＝v4 的大小，樹變矮時樹冠不跟著縮）
CR = float(os.environ.get('UP_CR', .36))          # 樹冠佔樹高比例（頂上這一段才有枝）
PAD = float(os.environ.get('UP_PAD', 1.35))        # 枝長倍率（樹冠寬）
UP = Vector((0, 0, 1))


def gh(x, y):
    return fb((x, y, 0), .05, 3) * .4


# ---------------- 樹幹：直、微傾、上段輕輕一彎 ----------------
lean = R.uniform(0, 2 * math.pi)
lx, ly = math.cos(lean), math.sin(lean)


def toff(z):
    u = max(0.0, z) / TH
    return .35 * math.sin(u * 4.0 + SEED) * u + 1.4 * u ** 3


tp = []
for k in range(13):
    z = -0.6 + k * (TH + .6) / 12
    o = toff(z)
    tp.append((lx * o, ly * o, z))
RB = .55 * CS
trunk = tube('Trunk', tp, radius=lambda t: RB * (1 - .82 * t) + .05 + RB * .9 * max(0, .06 - t) * 10,
             flat=lambda t: 1.0, seed=SEED * 1.7, rib=.08, twist=.04)
objs.append(trunk)

# ---------------- 樹冠：tree_gen 枝梢流，枝在水平面展開成一片片平台 ----------------
_TG = 'C:/Users/User/AppData/Local/Temp/claude/5b1d5a1d6e0ced79/95010672-bf02-4e75-99c7-37774fc10d08/scratchpad/lifetree/tree_gen.py'
code = open(_TG, encoding='utf-8').read()
lm_src = code[code.index('def leaf_material'):code.index('def scene_and_render')]
code = code[:code.index('def bark_material')] + lm_src
code = code.replace("elif level == 1: trop = UP * (.20 - .36 * t)", "elif level == 1: trop = UP * (.03 + .06 * t)")
code = code.replace("elif level == 2: trop = UP * (.10 - .2 * t)", "elif level == 2: trop = UP * (.05 + .06 * t)")
code = code.replace("else: trop = UP * (-.05 - .22 * t)", "else: trop = UP * (.06 + .04 * t)")
code = code.replace("        if level >= 1 and cd.z < -.15: cd.z = -.15; cd.normalize()", "        if level >= 1: cd.z = cd.z * FLAT + .05; cd.normalize()")
code = code.replace("half = R.uniform(*LEAF_LEN); w = half * R.uniform(.42, .56)", "half = R.uniform(*LEAF_LEN); w = half * R.uniform(*LEAF_W)")
code = code.replace("(.02 if level == 4 else .045)", "(LEAF_SP4 if level == 4 else LEAF_SP3)")
sv = sys.argv
sys.argv = ['x', '--', '.', str(SEED)]
TG = {}
exec(compile(code, _TG, 'exec'), TG)
sys.argv = sv
TG['noise'].seed_set(SEED)
TG['R'].seed(SEED)
TG.update(FLAT=.10, LEAF_LEN=(.11, .15), LEAF_W=(.06, .09), LEAF_SP3=.010, LEAF_SP4=.006)
TG['RINGS'] = {0: 10, 1: 8, 2: 6, 3: 4, 4: 3}
TG['PALETTE'] = ((.016, .036, .020), (.026, .055, .030), (.045, .080, .040), (.075, .110, .055), (.11, .14, .07))

Z0 = TH * (1 - CR)
def pad(c, hd, rp, kk):
    """一片雲片：扁橢球體積內塞滿短的針葉梢（水平、略往上），頂面圓鼓、底面平。"""
    for m in range(int(70 * (rp / 2.8) ** 2)):
        while True:
            u, v = R.uniform(-1, 1), R.uniform(-1, 1)
            if u * u + v * v < 1:
                break
        w = R.uniform(-.25, 1.0) * math.sqrt(max(0.0, 1 - u * u - v * v))
        p = c + Vector((u * rp, v * rp, w * rp * .38))
        a = math.atan2(v, u) + R.uniform(-.9, .9)
        out = Vector((math.cos(a), math.sin(a), 0))
        dd = (out * .8 + hd * .2 + UP * R.uniform(.05, .45)).normalized()
        TG['grow'](p, dd, R.uniform(.55, 1.0) * CS, .014, 4, 20000 + kk * 300 + m)
    # 雲片內幾根細枝當骨架
    for m in range(5):
        a = R.uniform(0, 6.283)
        TG['grow'](c, Vector((math.cos(a), math.sin(a), .08)).normalized(), rp * .8, .04, 3, 30000 + kk * 10 + m)


z = Z0
k = 0
AZ = R.uniform(0, 2 * math.pi)
tier = 0
while z < TH - 1.2:
    f = (z - Z0) / (TH - Z0 - 1.2)
    o = toff(z)
    tpos = Vector((lx * o, ly * o, z))
    nb = R.choice([2, 3, 3])
    for j in range(nb):
        az = AZ + j * 2 * math.pi / nb + R.uniform(-.35, .35)
        bias = 1 + .3 * math.cos(az - lean)
        L = (5.2 - 2.8 * f) * PAD * CS * bias * R.uniform(.8, 1.15)
        hd = Vector((math.cos(az), math.sin(az), 0))
        sd = Vector((-hd.y, hd.x, 0))
        # 主枝：近水平伸出、中段微垂、末端微翹（自己畫，不交給 tree_gen 往上長）
        pts = []
        for i in range(13):
            t = i / 12
            p = tpos + hd * (L * t) + sd * (math.sin(t * 3 + k) * .35 * t) + UP * (L * (.08 * t - .10 * math.sin(t * math.pi) + .03 * t * t))
            if BEND:   # z1nnz 11/21：樹枝太僵硬 → 枝幹左右擺、上下起伏，像真的松枝一段段轉折
                p += sd * (BEND * L * .10 * (math.sin(t * 7.0 + k * 1.7) * t + .6 * math.sin(t * 13 + k) * t * t))
                p += UP * (BEND * L * .06 * math.sin(t * 9.0 + k * 2.3) * t)
            pts.append(tuple(p))
        r0 = (.20 - .07 * f) * CS
        objs.append(tube(f'Limb{k}', pts, radius=lambda t, r0=r0: r0 * (1 - .75 * t) + .02, flat=lambda t: 1.0, seed=k * 1.3, rib=.04, twist=.02))
        # 枝梢一片平展的雲片：後 45% 段落往水平四周長出短枝與針葉
        pad(Vector(pts[8]).lerp(Vector(pts[12]), .6), hd, R.uniform(2.4, 3.2) * PAD * CS * (1 - .25 * f), k)
        k += 1
    AZ += 2.39996
    tier += 1
    z += R.uniform(1.7, 2.5) * CS
# 樹頂：一片平頂雲片，不留尖梢
pad(Vector(tp[-1]) - UP * .3, Vector((lx, ly, 0)), 2.6 * PAD * CS, 999)
# 下段幾根枯枝殘樁（設定圖裡光幹上的斷枝）
for i in range(R.randint(3, 5)):
    zz = R.uniform(TH * .35, Z0 - 1)
    o = toff(zz)
    a = R.uniform(0, 6.283)
    p0 = Vector((lx * o, ly * o, zz))
    d = Vector((math.cos(a), math.sin(a), R.uniform(-.1, .2))).normalized()
    L = R.uniform(.5, 1.6) * (.45 if BEND else 1.0)   # 斷枝短一點，不像插著的木棍
    objs.append(tube(f'Stub{i}', [tuple(p0), tuple(p0 + d * L * .5), tuple(p0 + d * L)],
                     radius=lambda t: .09 * (1 - .7 * t) + .02, flat=lambda t: 1.0, seed=i * 3.1, rib=.0, twist=.0))

wood = TG['tube_mesh']()
wo = bpy.data.objects.new('Branches', wood)
bpy.context.scene.collection.objects.link(wo)
wo.data.materials.append(MAT)
lm, nleaf = TG['leaf_mesh']()
lo = bpy.data.objects.new('Needles', lm)
bpy.context.scene.collection.objects.link(lo)
lo.data.materials.append(TG['leaf_material']())
for o in objs:
    if not o.data.materials:
        o.data.materials.append(MAT)
print('NEEDLES', nleaf, 'TIERS', tier, 'TRIS', sum(len(p.vertices) - 2 for o in objs + [wo, lo] for p in o.data.polygons))

if 'save' in ARGS:
    bpy.ops.wm.save_as_mainfile(filepath=S_ + f'umbrella_pine_{TAG}.blend') if 'S_' in globals() else \
        bpy.ops.wm.save_as_mainfile(filepath=f'D:/chengtian/4-素材與快取/bark-sample/umbrella_pine_{TAG}.blend')
if 'norender' in ARGS:
    raise SystemExit
tail = tail[:tail.index('# 1.75 m 人形尺')]
tail = tail.replace("primitive_grid_add(x_subdivisions=400, y_subdivisions=400, size=130)", "primitive_grid_add(x_subdivisions=200, y_subdivisions=200, size=120)")
tail = tail.replace("vol.inputs['Density'].default_value = .0055", "vol.inputs['Density'].default_value = .003")
exec(compile(tail, BASE, 'exec'))
hm = bpy.data.materials.new('Human')
hm.use_nodes = True
next(n for n in hm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.75, .72, .66, 1)
bpy.ops.mesh.primitive_cylinder_add(radius=.22, depth=1.75, location=(3.5, -2.5, .875))
bpy.context.object.data.materials.append(hm)


def shot(n, loc, tgt, lens, res=(1000, 1400)):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.data.lens = lens
    c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = c
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = OUT + f'upine_{TAG}_{n}.png'
    bpy.ops.render.render(write_still=True)


s = TH / 30
shot('full', (0, -62 * s, 6 * s), (0, 0, 15 * s), 30)
shot('crown', (0, -30 * s, 16 * s), (0, 0, 24 * s), 35, (1400, 1000))
