# D2 古樹區域 總平面＋六角度方塊模型（給 ChatGPT 照著畫設定圖用）
#   blender -b --factory-startup -P d2_plan.py -- [only=V1,V3] [quick]
#   座標：x 東、y 北，單位公尺；區塊 200×200（x,y ∈ -100..100）
import bpy, sys, math, random, json
import numpy as np
from mathutils import Vector, noise

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
QUICK = 'quick' in argv
ONLY = next((a[5:].split(',') for a in argv if a.startswith('only=')), None)
S_ = 'D:/chengtian/4-素材與快取/bark-sample/'
EXP = 'D:/chengtian/1-進行中/core-d2-altar/art/exports/core-d2-v1/'
OUT = S_ + 'plan/'
noise.seed_set(5)
R = random.Random(5)
sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# ---------------- 平面配置（總圖，所有角度都照這個） ----------------
TREE = (-24.0, 30.0)          # 神木
ALT = (7.0, 7.0)              # 祭壇
PIT = (11.0, -4.5)            # 被挖的坑
ARCH_S = (2.0, -84.0)         # 南入口（Josh 的根拱）
ARCH_N = (-6.0, 86.0)         # 北入口（核心組根拱）
CLEAR = (-4.0, 10.0, 38.0)    # 林中空地：中心、半徑
VIEW_E = (38.0, 4.0)          # 東側開口（看向 B 區山）方向的 y 範圍中心、半寬
# 主路：南入口 → 祭壇前 → 繞神木東側 → 北入口
PATH = [(2, -100), (2, -84), (-3, -62), (4, -40), (2, -20), (4, -6), (9, 1), (18, 14), (20, 32), (14, 52), (2, 70), (-6, 86), (-6, 100)]


def seg_d(px, py, a, b):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def path_d(x, y):
    return min(seg_d(x, y, PATH[i], PATH[i + 1]) for i in range(len(PATH) - 1))


def fb(x, y, s, o=3):
    return noise.fractal(Vector((x * s, y * s, 0)), .5, 2.0, o)


def gh(x, y):
    h = fb(x, y, .02) * 2.2 + fb(x, y, .12) * .25
    h += max(0.0, x - 40) * -.06                       # 東側往下斜，看出去是谷地
    h += max(0.0, -x - 50) * .05 + max(0.0, y - 60) * .03   # 西、北緩升
    h -= max(0.0, 1 - path_d(x, y) / 2.2) * .18
    rp = math.hypot(x - PIT[0], y - PIT[1])
    h -= 1.1 * max(0.0, 1 - rp / 2.7) ** .6
    return h


def mat(name, col, rough=.9, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    return m


M_GROUND = mat('ground', (.13, .15, .07))
M_PATH = mat('path', (.30, .20, .12))
M_TRUNK = mat('trunk', (.22, .16, .11))
M_PINE = mat('pine', (.06, .14, .07))
M_BROAD = mat('broad', (.32, .36, .08))
M_ROUND = mat('round', (.10, .22, .07))
M_GIANT = mat('giant', (.14, .20, .07))
M_ROCK = mat('rock', (.30, .31, .27))
M_MOSS = mat('moss', (.12, .22, .05))
M_ROOT = mat('root', (.20, .15, .10))
M_MTN = mat('mtn', (.35, .38, .40))

# ---------------- 地面 ----------------
X0, X1, RES = -130, 130, 1.0
n = int((X1 - X0) / RES)
xs = np.linspace(X0, X1, n + 1)
V = [(x, y, gh(x, y)) for y in xs for x in xs]
F = [(j * (n + 1) + i, j * (n + 1) + i + 1, (j + 1) * (n + 1) + i + 1, (j + 1) * (n + 1) + i) for j in range(n) for i in range(n)]
me = bpy.data.meshes.new('Ground')
me.from_pydata(V, [], F)
me.materials.append(M_GROUND)
me.materials.append(M_PATH)
for p in me.polygons:
    c = p.center
    p.material_index = 1 if path_d(c.x, c.y) < 1.4 + .4 * math.sin(c.y * .3) else 0
    p.use_smooth = True
g = bpy.data.objects.new('Ground', me)
sc.collection.objects.link(g)

# 遠方 B 區山（世界地圖上真實存在、之後可到達；東方 600 m 外，只在霧裡露輪廓）
bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=420, radius2=40, depth=260, location=(640, 60, 60))
mt = bpy.context.object
mt.name = 'B_Mountain_real'
mt.scale = (1.0, 1.6, 1.0)
mt.data.materials.append(M_MTN)
# 東側谷地地面延伸到山腳（不留假背景板）
bpy.ops.mesh.primitive_plane_add(size=1, location=(380, 40, -9))
pl = bpy.context.object
pl.scale = (520, 700, 1)
pl.data.materials.append(M_GROUND)


def put(o, m):
    o.data.materials.append(m)
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def blob(loc, r, m, sq=(1, 1, 1), sub=2):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r, location=loc)
    o = bpy.context.object
    o.scale = sq
    return put(o, m)


def cyl(loc, r1, r2, h, m, v=12):
    bpy.ops.mesh.primitive_cone_add(vertices=v, radius1=r1, radius2=r2, depth=h, location=(loc[0], loc[1], loc[2] + h / 2))
    return put(bpy.context.object, m)


# ---------------- 真實模型：神木、祭壇、坑、兩座根拱 ----------------
def append(path, want, offset, dz):
    with bpy.data.libraries.load(path, link=False) as (s, d):
        d.objects = [nm for nm in s.objects if want(nm)]
    got = [o for o in d.objects if o is not None]
    for o in got:
        sc.collection.objects.link(o)
    for o in got:
        if o.parent is None or o.parent not in got:
            o.location = Vector(o.location) + Vector((offset[0], offset[1], dz))


def glb(path, at, dz, rotz=0.0):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = list(set(bpy.data.objects) - before)
    bpy.context.view_layer.update()
    keep = []
    for o in new:      # 先把網格的世界座標固定下來、解除父子，再刪空物件
        if o.type == 'MESH':
            mw = o.matrix_world.copy()
            o.parent = None
            o.matrix_world = mw
    for o in new:
        if o.type != 'MESH' or 'Collision' in o.name or 'UCX' in o.name or '_LOD1' in o.name or '_LOD2' in o.name:
            bpy.data.objects.remove(o, do_unlink=True)
        else:
            keep.append(o)
    for o in keep:
        o.location = Vector((o.location.x + at[0], o.location.y + at[1], o.location.z + gh(*at) + dz))
    print('GLB', path.split('/')[-1], len(keep))


append(S_ + 'GT01_out/GT01_GodTree_v003.blend', lambda nm: nm.endswith('_LOD1'), TREE, gh(*TREE) - .6)
glb(EXP + 'AL01_RootAltarTerrace/AL01_RootAltarTerrace_v001.glb', ALT, -.05)
glb(EXP + 'CO01_ExcavatedPit/CO01_ExcavatedPit_v002.glb', PIT, -.02 - gh(*PIT))
glb('D:/chengtian/4-素材與快取/josh-dr01/DR01_RootArch_v006.glb', ARCH_S, -.15)
append(S_ + 'root_arch_lib.blend', lambda nm: not (nm in ('Grid', 'Cube') or nm.startswith(('Cylinder', 'Camera', 'Sun', 'Ground', 'Floor'))),
       ARCH_N, gh(*ARCH_N) - .15)
for o in list(bpy.data.objects):     # 根拱庫裡若有非網格物件就拿掉
    if o.type not in ('MESH', 'EMPTY'):
        bpy.data.objects.remove(o, do_unlink=True)

# ---------------- 神木的地上根：往祭壇、往外放射 ----------------
def root_ridge(a, b, r0, r1, m=M_ROOT):
    ax, ay = a; bx, by = b
    L = math.hypot(bx - ax, by - ay)
    N = max(3, int(L / 1.2))
    for i in range(N + 1):
        t = i / N
        x = ax + (bx - ax) * t + math.sin(t * 5 + ax) * 1.2
        y = ay + (by - ay) * t + math.cos(t * 4 + ay) * 1.2
        r = r0 + (r1 - r0) * t
        blob((x, y, gh(x, y) + r * .1), r, m, sq=(1, 1, .55), sub=1)


ROOTS = []
for k in range(9):
    ang = -1.25 + k * .55 + R.uniform(-.15, .15)
    L = R.uniform(14, 24)
    ROOTS.append(((TREE[0] + math.cos(ang) * 6, TREE[1] - math.sin(ang) * 6), (TREE[0] + math.cos(ang) * L, TREE[1] - math.sin(ang) * L)))
ROOTS.append(((TREE[0] + 6, TREE[1] - 5), (ALT[0] - 4, ALT[1] + 2)))           # 兩條長根延伸到祭壇邊
ROOTS.append(((TREE[0] + 4, TREE[1] - 7), (ALT[0] - 2, ALT[1] - 4)))
for a, b in ROOTS:
    root_ridge(a, b, 1.5, .45)

# ---------------- 樹（三種新樹種＋古林巨木），依分區散佈 ----------------
# P 傘頂松：直幹 26–36 m，頂上 2–3 層平展樹冠（深綠）→ 東側坡、北側高處
# B 黃綠闊葉：12–20 m，團狀樹冠（黃綠）→ 空地邊緣、東側開口兩旁
# M 圓冠中樹：8–13 m，圓團樹冠 → 林下、遠處成片
# G 古林巨木：22–30 m，粗幹大冠 → 西側、北側深林
TREES = []


def pine(x, y, s):
    z = gh(x, y)
    H = 30 * s
    cyl((x, y, z - .3), .55 * s, .28 * s, H, M_TRUNK)
    for i in range(R.choice((2, 3))):
        zz = z + H * (.82 + i * .08)
        ox, oy = R.uniform(-1.5, 1.5) * s, R.uniform(-1.5, 1.5) * s
        rr = (6.5 - i * 1.6) * s
        blob((x + ox, y + oy, zz), rr, M_PINE, sq=(1, R.uniform(.8, 1.1), .32))


def broad(x, y, s):
    z = gh(x, y)
    H = 16 * s
    cyl((x, y, z - .3), .6 * s, .35 * s, H * .62, M_TRUNK)
    for i in range(6):
        a = R.uniform(0, 6.28)
        d = R.uniform(0, 4.2) * s
        blob((x + math.cos(a) * d, y + math.sin(a) * d, z + H * R.uniform(.62, .95)), R.uniform(2.8, 4.2) * s, M_BROAD, sq=(1, 1, .75))


def roundt(x, y, s):
    z = gh(x, y)
    H = 10 * s
    cyl((x, y, z - .3), .35 * s, .2 * s, H * .6, M_TRUNK)
    blob((x, y, z + H * .72), 3.6 * s, M_ROUND, sq=(1, 1, .9))


def giant(x, y, s):
    z = gh(x, y)
    H = 26 * s
    cyl((x, y, z - .5), 1.6 * s, .9 * s, H * .6, M_TRUNK, v=16)
    for i in range(7):
        a = R.uniform(0, 6.28)
        d = R.uniform(2, 8) * s
        blob((x + math.cos(a) * d, y + math.sin(a) * d, z + H * R.uniform(.6, .92)), R.uniform(4.5, 6.5) * s, M_GIANT, sq=(1, 1, .7))


KIND = {'P': pine, 'B': broad, 'M': roundt, 'G': giant}
GAP = {'P': 9.0, 'B': 9.0, 'M': 6.5, 'G': 14.0}


def zone_kind(x, y):
    dc = math.hypot(x - CLEAR[0], y - CLEAR[1])
    if x > 30 and -30 < y < 60:
        return R.choice('PPBM')            # 東坡：松為主
    if dc < CLEAR[2] + 12:
        return R.choice('BBMMG')           # 空地邊緣：黃綠闊葉
    if x < -40 or y > 55:
        return R.choice('GGPMM')           # 西、北深林：巨木
    return R.choice('MMBPG')


def ok(x, y):
    if math.hypot(x - CLEAR[0], y - CLEAR[1]) < CLEAR[2]:
        return False
    if math.hypot(x - TREE[0], y - TREE[1]) < 34:
        return False
    if path_d(x, y) < 5.5:
        return False
    if x > 34 and abs(y - VIEW_E[0] * 0 - 20) < 18 and x < 110:   # 東側看向 B 區山的開口
        return R.random() < .15
    return True


tries = 0
while len(TREES) < (260 if not QUICK else 120) and tries < 60000:
    tries += 1
    x, y = R.uniform(-125, 125), R.uniform(-125, 125)
    if not ok(x, y):
        continue
    k = zone_kind(x, y)
    if any(math.hypot(x - tx, y - ty) < max(GAP[k], GAP[tk]) * R.uniform(.85, 1.1) for tx, ty, tk, _ in TREES):
        continue
    TREES.append((x, y, k, R.uniform(.85, 1.15)))
for x, y, k, s in TREES:
    KIND[k](x, y, s)

# ---------------- 大苔石、板根牆、倒木 ----------------
ROCKS = [(-6, -10, 1.6), (12, -14, 2.0), (-12, -2, 1.3), (22, 2, 1.8), (-2, -30, 1.2), (8, -48, 1.5), (-10, 52, 1.7), (24, 44, 1.4)]
for x, y, r in ROCKS:
    blob((x, y, gh(x, y) + r * .2), r, M_ROCK, sq=(1.2, 1, .7))
    blob((x, y, gh(x, y) + r * .55), r * .8, M_MOSS, sq=(1.2, 1, .35))
WALLS = [((22, 4), (30, 16)), ((-14, 4), (-22, -6)), ((-36, 20), (-46, 30))]
for a, b in WALLS:
    root_ridge(a, b, 1.1, .8)
LOGS = [((-30, -20), (-22, -26)), ((30, -34), (36, -24))]
for (ax, ay), (bx, by) in LOGS:
    L = math.hypot(bx - ax, by - ay)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=.7, depth=L, location=((ax + bx) / 2, (ay + by) / 2, gh(ax, ay) + .5),
                                        rotation=(math.pi / 2, 0, math.atan2(by - ay, bx - ax) - math.pi / 2))
    put(bpy.context.object, M_TRUNK)

# 被挖的坑：坑邊翻出來的土堆（方塊模型用，讓每個角度都看得出坑在哪）
M_DIRT = mat('dirt', (.36, .22, .12))
for i in range(14):
    a = i / 14 * 6.283 + R.uniform(-.2, .2)
    rr = 3.2 + R.uniform(-.3, .6)
    x, y = PIT[0] + math.cos(a) * rr, PIT[1] + math.sin(a) * rr
    blob((x, y, gh(x, y) + .1), R.uniform(.6, 1.1), M_DIRT, sq=(1.3, 1, .5), sub=1)
bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=2.6, depth=.05, location=(PIT[0], PIT[1], gh(*PIT) + .15))
put(bpy.context.object, mat('hole', (.06, .04, .03)))

# 1.75 m 人形尺（祭壇前）
cyl((4, -6, gh(4, -6)), .22, .18, 1.75, mat('human', (.8, .1, .1))).hide_render = True

# ---------------- 燈光、霧、相機 ----------------
w = bpy.data.worlds.new('W')
sc.world = w
w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (.55, .6, .65, 1)
bg.inputs['Strength'].default_value = 1.6
sun = bpy.data.lights.new('Sun', 'SUN')
sun.energy = 3.2
sun.angle = .2
so = bpy.data.objects.new('Sun', sun)
so.rotation_euler = (math.radians(50), 0, math.radians(150))
sc.collection.objects.link(so)
bpy.ops.mesh.primitive_cube_add(size=1, location=(200, 50, 40))
fog = bpy.context.object
fog.name = 'Fog'
fog.scale = (1200, 1200, 140)
fm = bpy.data.materials.new('fog')
fm.use_nodes = True
nt = fm.node_tree
for nd in list(nt.nodes):
    if nd.type == 'BSDF_PRINCIPLED':
        nt.nodes.remove(nd)
vs = nt.nodes.new('ShaderNodeVolumePrincipled')
vs.inputs['Density'].default_value = .005
vs.inputs['Color'].default_value = (.85, .88, .9, 1)
nt.links.new(vs.outputs['Volume'], next(nd for nd in nt.nodes if nd.type == 'OUTPUT_MATERIAL').inputs['Volume'])
fog.data.materials.append(fm)

sc.render.engine = 'CYCLES'
try:
    bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'OPTIX'
    bpy.context.preferences.addons['cycles'].preferences.get_devices()
    for d in bpy.context.preferences.addons['cycles'].preferences.devices:
        d.use = True
    sc.cycles.device = 'GPU'
except Exception as e:
    print('GPU?', e)
sc.cycles.samples = 24 if QUICK else 64
sc.cycles.use_denoising = True
sc.cycles.volume_step_rate = 4
sc.view_settings.view_transform = 'AgX'
sc.render.resolution_x, sc.render.resolution_y = 1536, 1024
SHOTS = {
    'V1': ((70, -105, 62), (-6, 18, 0), 24, '俯瞰全景（東南高處）'),
    'V2': ((2.5, -97, 1.7), (1.5, -60, 4.5), 22, '南入口（Josh 根拱）往北看'),
    'V3': ((6, -13, 1.9), (1, 18, 5.0), 16, '祭壇前（神木左、祭壇中右、坑右前）'),
    'V4': ((15, -10.5, 2.4), (10, -3, -.6), 24, '坑邊近景'),
    'V5': ((-6, 12, 2.4), (12, -30, 2.0), 20, '神木根旁回頭看（往南看祭壇與小路）'),
    'V6': ((4, 64, 1.7), (-6, 100, 5.0), 22, '北入口（核心組根拱）往外看'),
}
for k, (loc, tgt, lens, _) in SHOTS.items():
    if ONLY and k not in ONLY:
        continue
    cd = bpy.data.cameras.new(k)
    cd.lens = lens
    cd.clip_end = 3000
    co = bpy.data.objects.new(k, cd)
    sc.collection.objects.link(co)
    if k != 'V1':      # 地面視角：高度以腳下地面為準
        loc = (loc[0], loc[1], gh(loc[0], loc[1]) + loc[2])
        tgt = (tgt[0], tgt[1], gh(tgt[0], tgt[1]) + tgt[2])
    co.location = loc
    co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = co
    sc.render.filepath = OUT + f'D2_plan_{k}.png'
    bpy.ops.render.render(write_still=True)
    print('SHOT', k)

# 俯視總圖（正交，霧關掉）
if not ONLY or 'TOP' in ONLY:
    fog.hide_render = True
    cd = bpy.data.cameras.new('TOP')
    cd.type = 'ORTHO'
    cd.ortho_scale = 230
    cd.clip_end = 3000
    co = bpy.data.objects.new('TOP', cd)
    sc.collection.objects.link(co)
    co.location = (0, 0, 400)
    sc.camera = co
    sc.render.resolution_x = sc.render.resolution_y = 2048
    sc.render.filepath = OUT + 'D2_plan_TOP.png'
    bpy.ops.render.render(write_still=True)

json.dump({'TREE': TREE, 'ALT': ALT, 'PIT': PIT, 'ARCH_S': ARCH_S, 'ARCH_N': ARCH_N, 'PATH': PATH,
           'trees': TREES, 'rocks': ROCKS, 'shots': {k: [list(v[0]), list(v[1]), v[2], v[3]] for k, v in SHOTS.items()}},
          open(OUT + 'D2_plan.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('DONE', len(TREES))
