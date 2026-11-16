# D2 外圈松（定版：z1nnz 11/16 打勾那一棵＝不帶任何環境變數、種子 3；其他設定都不採用）
# D2 外圈松（TR01 核心組樣品）：層狀松——彎幹、水平分層的枝、枝梢一簇簇針葉往上翹
#   GT_BARK=pine_bark blender -b --factory-startup -P pine_gen.py -- <tag> [quick] [seed]
import os, sys, math, random
from mathutils import Vector, noise

os.environ.setdefault('GT_BARK', 'pine_bark')
BASE = 'D:/chengtian/4-素材與快取/bark-sample/godtree_base.py'
src = open(BASE, encoding='utf-8').read()
lib = src.split('# ---------------- 樹幹')[0]
exec(compile(lib, BASE, 'exec'))
SEED = int([a for a in ARGS if a.isdigit()][0]) if any(a.isdigit() for a in ARGS) else 3   # z1nnz 11/16：只有種子 3（打勾那棵）可用
R = random.Random(SEED)
noise.seed_set(SEED)
TIDY = float(os.environ.get('PINE_TIDY', 0))   # 0＝打勾原版；1＝不過度扭曲、葉子只聚在枝梢
tail = src[src.index('# ---------------- 地面'):]
TH = 16.0
UP = Vector((0, 0, 1))


def gh(x, y):
    return fb((x, y, 0), .05, 3) * .4


# ---------------- 樹幹：S 形、上部偏一邊 ----------------
lean = R.uniform(0, 2 * math.pi)
lx, ly = math.cos(lean), math.sin(lean)
tp = []
for k in range(9):
    z = -0.6 + k * (TH + .6) / 8
    off = (1 - .5 * TIDY) * (1.6 * math.sin(z / TH * 3.0 + SEED) * (z / TH) + 3.0 * (z / TH) ** 2)
    tp.append((lx * off, ly * off, z))
trunk = tube('Trunk', tp, radius=lambda t: .62 * (1 - .9 * t) + .05 + .45 * max(0, .08 - t) * 10,
             flat=lambda t: 1.0, seed=SEED * 1.7, rib=.10, twist=.05)
objs.append(trunk)

# ---------------- 樹冠：照 tree_gen 的枝梢流做法，改成松的分層與針葉 ----------------
_TG = 'C:/Users/User/AppData/Local/Temp/claude/5b1d5a1d6e0ced79/95010672-bf02-4e75-99c7-37774fc10d08/scratchpad/lifetree/tree_gen.py'
code = open(_TG, encoding='utf-8').read()
lm_src = code[code.index('def leaf_material'):code.index('def scene_and_render')]
code = code[:code.index('def bark_material')] + lm_src
ROUND = os.environ.get('PINE_STYLE', 'round') == 'round'   # z1nnz 11/16 選定：圓團狀（p2）
if TIDY:
    code = code.replace("* (.16 if level == 0 else .3 if level == 1 else .38)", "* (.16 if level == 0 else .3 if level == 1 else .38) * (1 - .55 * TIDY)")
    code = code.replace("        first = 1 if level == 4 else n // 3", "        first = ((n // 2) if level == 4 else (n * 2 // 3)) if TIDY_TIPS else (1 if level == 4 else n // 3)")
# 松：主枝近水平、梢端微翹；細枝往上翹成一簇簇
code = code.replace("elif level == 1: trop = UP * (.20 - .36 * t)", "elif level == 1: trop = UP * (PINE_T1 + .10 * t)")
code = code.replace("elif level == 2: trop = UP * (.10 - .2 * t)", "elif level == 2: trop = UP * (.12 + .12 * t)" if ROUND else "elif level == 2: trop = UP * (.02 + .03 * t)")
code = code.replace("else: trop = UP * (-.05 - .22 * t)", "else: trop = UP * (.18 + .1 * t)")
# 層狀松：子枝在水平面上展開（壓平 z），形成一片片平台
if not ROUND:
    code = code.replace("        if level >= 1 and cd.z < -.15: cd.z = -.15; cd.normalize()", "        if level >= 1: cd.z = cd.z * FLAT + .04; cd.normalize()")
    code = code.replace("        else: trop = UP * (.18 + .1 * t)", "        else: trop = UP * (.03 + .02 * t)")
# 針葉：細長、間距密
code = code.replace("half = R.uniform(*LEAF_LEN); w = half * R.uniform(.42, .56)", "half = R.uniform(*LEAF_LEN); w = half * R.uniform(*LEAF_W)")
code = code.replace("(.02 if level == 4 else .045)", "(LEAF_SP4 if level == 4 else LEAF_SP3)")
sv = sys.argv
sys.argv = ['x', '--', '.', str(SEED)]
TG = {}
exec(compile(code, _TG, 'exec'), TG)
sys.argv = sv
TG['noise'].seed_set(SEED)
TG['R'].seed(SEED)
TG.update(TIDY=TIDY, TIDY_TIPS=bool(TIDY), FLAT=.12, PINE_T1=-.02, LEAF_LEN=(.10, .14), LEAF_W=(.06, .09), LEAF_SP3=.011, LEAF_SP4=.006)
PINE_L0 = float(os.environ.get('PINE_L0', 8.5))
PINE_L1 = float(os.environ.get('PINE_L1', 5.5))
if ROUND:
    TG.update(PINE_T1=-.03, LEAF_SP3=float(os.environ.get('PINE_SP3', .014)), LEAF_SP4=float(os.environ.get('PINE_SP4', .008)),
              LEAF_LEN=(float(os.environ.get('PINE_LL', .10)), float(os.environ.get('PINE_LL', .10)) + .04))
TG['RINGS'] = {0: 10, 1: 8, 2: 6, 3: 4, 4: 3}
TG['PALETTE'] = ((.016, .036, .020), (.026, .055, .030), (.045, .080, .040), (.075, .110, .055), (.11, .14, .07))

# 分層主枝：從 4.5 m 起，每層 2–3 根，層與層間隔 1.2–1.8 m，上層越短
Z0 = 4.5 if ROUND else 6.0
z = Z0
k = 0
AZ = R.uniform(0, 2 * math.pi)
while z < TH - 1.0:
    f = (z - Z0) / (TH - Z0 - 1.0)
    _o = (1 - .5 * TIDY) * (1.6 * math.sin(z / TH * 3.0 + SEED) * (z / TH) + 3.0 * (z / TH) ** 2)
    tpos = Vector((lx * _o, ly * _o, z))
    nb = R.choice([3, 3, 4] if ROUND else [2, 3, 3])
    for j in range(nb):
        if os.environ.get('PINE_SPIRAL'):
            # 同一層平均分開，層與層之間再轉黃金角：前後左右斜向都會有枝
            az = AZ + j * 2 * math.pi / nb + R.uniform(-.25, .25)
        else:
            az = R.uniform(0, 2 * math.pi)
        # 往傾斜那一側的枝長一點（不對稱剪影）
        bias = 1 + .35 * math.cos(az - lean)
        d = Vector((math.cos(az), math.sin(az), R.uniform(-.05, .12))).normalized()
        L = ((PINE_L0 - PINE_L1 * f) if ROUND else (9.5 - 6.0 * f)) * bias * R.uniform(.85, 1.1)
        TG['grow'](tpos, d, L, .16 - .07 * f, 1, 100 + k)
        k += 1
    AZ += 2.39996
    z += R.uniform(.9, 1.4) if ROUND else R.uniform(1.7, 2.4)
# 樹頂一叢
TG['grow'](Vector(tp[-1]), Vector((lx * .3, ly * .3, 1)).normalized(), 2.5, .07, 2, 999)

wood = TG['tube_mesh']()
wo = bpy.data.objects.new('Branches', wood)
bpy.context.scene.collection.objects.link(wo)
wo.data.materials.append(MAT)
lm, nleaf = TG['leaf_mesh']()
lo = bpy.data.objects.new('Needles', lm)
bpy.context.scene.collection.objects.link(lo)
lo.data.materials.append(TG['leaf_material']())
for o in objs:
    o.data.materials.append(MAT)
print('NEEDLES', nleaf, 'TRIS', sum(len(p.vertices) - 2 for o in objs + [wo, lo] for p in o.data.polygons))

tail = tail[:tail.index('# 1.75 m 人形尺')]
tail = tail.replace("primitive_grid_add(x_subdivisions=400, y_subdivisions=400, size=130)", "primitive_grid_add(x_subdivisions=200, y_subdivisions=200, size=80)")
tail = tail.replace("vol.inputs['Density'].default_value = .0055", "vol.inputs['Density'].default_value = .004")
exec(compile(tail, BASE, 'exec'))
hm = bpy.data.materials.new('Human')
hm.use_nodes = True
next(n for n in hm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.75, .72, .66, 1)
bpy.ops.mesh.primitive_cylinder_add(radius=.22, depth=1.75, location=(3.5, -2.5, .875))
bpy.context.object.data.materials.append(hm)


def shot(n, loc, tgt, lens, res=(1200, 1400)):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.data.lens = lens
    c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = c
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = OUT + f'pine_{TAG}_{n}.png'
    bpy.ops.render.render(write_still=True)


shot('full', (0, -34, 4), (0, 0, 8.5), 30)
shot('under', (2, -6, 1.6), (1, 0, 9), 22)
shot('top', (0.01, 0, 60), (0, 0, 8), 35, (1200, 1200))
shot('tq', (24, -24, 9), (0, 0, 8.5), 30)
