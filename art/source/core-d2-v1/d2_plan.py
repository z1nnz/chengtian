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
ARCH_N = (-4.0, 108.0)         # 北入口（核心組根拱）
CLEAR = (-4.0, 10.0, 38.0)    # 林中空地：中心、半徑
VIEW_E = (38.0, 4.0)          # 東側開口（看向 B 區山）方向的 y 範圍中心、半寬
# 主路：南入口 → 祭壇前 → 繞神木東側 → 北入口
PATH = [(2, -100), (2, -84), (-3, -62), (4, -40), (2, -20), (4, -6), (9, 1), (18, 14), (20, 32), (14, 52), (2, 70), (-2, 86), (-4, 108), (-4, 125)]


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
    if REAL:
        h += pit_h(x - PIT[0], y - PIT[1], rp)
    else:
        h -= 1.1 * max(0.0, 1 - rp / 2.7) ** .6
    return h


REAL = 'real' in argv


def pit_h(dx, dy, r):
    """被挖的坑（設定圖 V4）：陡壁深坑、坑底不平，坑緣一圈翻出來的鬆土堆（不均勻、一側堆得高）。"""
    a = math.atan2(dy, dx)
    rw = 2.6 + .35 * noise.noise(Vector((math.cos(a) * 1.3, math.sin(a) * 1.3, 7.1)))   # 坑口不圓
    h = 0.0
    if r < rw:
        u = r / rw
        h -= 1.25 * (1 - u ** 3.2) + .12 * noise.noise(Vector((dx * 1.4, dy * 1.4, 3.3)))
    # 坑緣土堆：在坑口外 0.3–2.0 m，幾坨鬆土，朝東北那側堆得最高
    m = .5 + .5 * noise.noise(Vector((math.cos(a) * 1.8, math.sin(a) * 1.8, 2.2)))
    side = .55 + .45 * math.cos(a - .7)
    ring = math.exp(-((r - rw - .9) / .75) ** 2)
    h += ring * (.25 + .75 * m) * side * .6
    h += ring * (.10 * noise.noise(Vector((dx * 2.5, dy * 2.5, 9.0))) + .06 * noise.noise(Vector((dx * 6, dy * 6, 4.0))))                  # 土塊顆粒
    # 壁面陡、往上接土堆
    if rw <= r < rw + .5:
        h -= .35 * (1 - (r - rw) / .5) ** 2
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
M_BARKR = mat('barkr', (.20, .15, .10))
if 'real' in argv:   # 方塊材質換成掃描材質（腐葉林床、泥路、苔石）
    _GT = 'D:/chengtian/4-素材與快取/polyhaven-ground/'

    def texmat(m, diff, nor, rough, scale, tint=(1, 1, 1), box=False):
        nt = m.node_tree
        b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
        tc = nt.nodes.new('ShaderNodeTexCoord')
        mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (1 / scale,) * 3
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])

        def im(fn, cs):
            t = nt.nodes.new('ShaderNodeTexImage')
            t.image = bpy.data.images.load(_GT + fn)
            t.image.colorspace_settings.name = cs
            if box:
                t.projection, t.projection_blend = 'BOX', .3
            nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
            return t
        d = im(diff, 'sRGB')
        mx = nt.nodes.new('ShaderNodeMixRGB')
        mx.blend_type = 'MULTIPLY'
        mx.inputs[0].default_value = 1
        mx.inputs[2].default_value = (*tint, 1)
        nt.links.new(d.outputs['Color'], mx.inputs[1])
        nt.links.new(mx.outputs['Color'], b.inputs['Base Color'])
        nm = nt.nodes.new('ShaderNodeNormalMap')
        nt.links.new(im(nor, 'Non-Color').outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
        nt.links.new(im(rough, 'Non-Color').outputs['Color'], b.inputs['Roughness'])

    texmat(M_GROUND, 'forest_leaves_02_diffuse_2k.png', 'forest_leaves_02_nor_gl_2k.png', 'forest_leaves_02_rough_2k.png', 2.5, (.85, .9, .75))
    texmat(M_PATH, 'brown_mud_02_diff_2k.png', 'brown_mud_02_nor_gl_2k.png', 'brown_mud_02_rough_2k.png', 2.0)
    texmat(M_ROCK, 'mossy_rock_diff_2k.png', 'mossy_rock_nor_gl_2k.png', 'mossy_rock_rough_2k.png', 1.5, box=True)
    texmat(M_MOSS, 'mossy_rock_diff_2k.png', 'mossy_rock_nor_gl_2k.png', 'mossy_rock_rough_2k.png', 1.5, (.6, 1.0, .5), box=True)
    texmat(M_BARKR, '../polyhaven-bark/bark_brown_02_diff_2k.png', '../polyhaven-bark/bark_brown_02_nor_gl_2k.png', '../polyhaven-bark/bark_brown_02_rough_2k.png', .9, (.26, .30, .17), box=True)
    texmat(M_ROOT, 'mossy_rock_diff_2k.png', 'mossy_rock_nor_gl_2k.png', 'mossy_rock_rough_2k.png', 1.2, (.7, .55, .4), box=True)

# ---------------- 地面 ----------------
X0, X1, RES = (-175, 175, 1.0) if 'real' in argv else (-130, 130, 1.0)
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
if 'real' in argv:   # 泥路用平滑遮罩混材質（不要方塊鋸齒邊）；林床偏綠、帶苔
    pm = np.array([max(0.0, min(1.0, 1 - (path_d(v[0], v[1]) - (1.3 + .4 * math.sin(v[1] * .3))) / 1.1)) for v in V], np.float32)
    ca = me.color_attributes.new('Mask', 'FLOAT_COLOR', 'POINT')
    ca.data.foreach_set('color', np.stack([pm, pm, pm, np.ones_like(pm)], 1).ravel())
    for p in me.polygons:
        p.material_index = 0
    GM = bpy.data.materials.new('GroundReal')
    GM.use_nodes = True
    nt = GM.node_tree
    b = next(x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED')
    tc = nt.nodes.new('ShaderNodeTexCoord')

    def gimg(fn, cs, sc_):
        mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (1 / sc_,) * 3
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = bpy.data.images.load(_GT + fn)
        t.image.colorspace_settings.name = cs
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
        return t.outputs['Color']
    at = nt.nodes.new('ShaderNodeVertexColor')
    at.layer_name = 'Mask'
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = .6
    nz.inputs['Detail'].default_value = 6
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    mk = nt.nodes.new('ShaderNodeMath')
    mk.operation = 'MULTIPLY_ADD'
    nt.links.new(nz.outputs['Fac'], mk.inputs[0])
    mk.inputs[1].default_value = .7
    nt.links.new(at.outputs['Color'], mk.inputs[2])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = .75, 1.05
    nt.links.new(mk.outputs[0], mr.inputs['Value'])
    # 林床：腐葉掃描 × 苔綠斑塊
    leaf = gimg('forest_leaves_02_diffuse_2k.png', 'sRGB', 2.5)
    mz = nt.nodes.new('ShaderNodeTexNoise')
    mz.inputs['Scale'].default_value = .25
    mz.inputs['Detail'].default_value = 4
    nt.links.new(tc.outputs['Object'], mz.inputs['Vector'])
    mrz = nt.nodes.new('ShaderNodeMapRange')
    mrz.inputs['From Min'].default_value, mrz.inputs['From Max'].default_value = .42, .62
    nt.links.new(mz.outputs['Fac'], mrz.inputs['Value'])
    tintA = nt.nodes.new('ShaderNodeMixRGB')
    tintA.inputs[1].default_value = (.62, .62, .46, 1)    # 濕腐葉（壓暗、去橘）
    tintA.inputs[2].default_value = (.30, .48, .16, 1)    # 苔綠
    nt.links.new(mrz.outputs[0], tintA.inputs[0])
    lf = nt.nodes.new('ShaderNodeMixRGB')
    lf.blend_type = 'MULTIPLY'
    lf.inputs[0].default_value = 1
    nt.links.new(leaf, lf.inputs[1])
    nt.links.new(tintA.outputs[0], lf.inputs[2])
    mud0 = gimg('brown_mud_02_diff_2k.png', 'sRGB', 2.0)
    mt_ = nt.nodes.new('ShaderNodeMixRGB')   # 泥土偏暖棕、濕（設定圖的土色），不要灰水泥色
    mt_.blend_type = 'MULTIPLY'
    mt_.inputs[0].default_value = 1
    mt_.inputs[2].default_value = (1.05, .72, .46, 1)
    nt.links.new(mud0, mt_.inputs[1])
    mud = mt_.outputs[0]
    cm = nt.nodes.new('ShaderNodeMixRGB')
    nt.links.new(mr.outputs[0], cm.inputs[0])
    nt.links.new(lf.outputs[0], cm.inputs[1])
    nt.links.new(mud, cm.inputs[2])
    nt.links.new(cm.outputs[0], b.inputs['Base Color'])
    nmx = nt.nodes.new('ShaderNodeMixRGB')
    nt.links.new(mr.outputs[0], nmx.inputs[0])
    n1 = gimg('forest_leaves_02_nor_gl_2k.png', 'Non-Color', 2.5)
    n2 = gimg('brown_mud_02_nor_gl_2k.png', 'Non-Color', 2.0)
    nt.links.new(n1, nmx.inputs[1])
    nt.links.new(n2, nmx.inputs[2])
    nmn = nt.nodes.new('ShaderNodeNormalMap')
    nt.links.new(nmx.outputs[0], nmn.inputs['Color'])
    nt.links.new(nmn.outputs['Normal'], b.inputs['Normal'])
    rmx = nt.nodes.new('ShaderNodeMapRange')
    nt.links.new(mr.outputs[0], rmx.inputs['Value'])
    rmx.inputs['To Min'].default_value, rmx.inputs['To Max'].default_value = .85, .45   # 泥路濕、反光
    nt.links.new(rmx.outputs[0], b.inputs['Roughness'])
    me.materials[0] = GM
    # 坑：主地面在坑周圍壓低藏起來，另外疊一塊 8 cm 細網格的地面（同材質），坑壁土堆才有細節
    for v in me.vertices:
        if math.hypot(v.co.x - PIT[0], v.co.y - PIT[1]) < 6.0:
            v.co.z -= 1.6
    PS, PRs = 7.5, .08
    pn = int(2 * PS / PRs)
    pxs = np.linspace(-PS, PS, pn + 1)
    PV = [(PIT[0] + x, PIT[1] + y, gh(PIT[0] + x, PIT[1] + y) + (.015 if math.hypot(x, y) > 5.5 else 0)) for y in pxs for x in pxs]
    PF = [(j * (pn + 1) + i, j * (pn + 1) + i + 1, (j + 1) * (pn + 1) + i + 1, (j + 1) * (pn + 1) + i) for j in range(pn) for i in range(pn)]
    pme = bpy.data.meshes.new('PitGround')
    pme.from_pydata(PV, [], PF)
    soil = []
    for vx, vy, vz in PV:
        rr_ = math.hypot(vx - PIT[0], vy - PIT[1])
        s1 = max(0.0, min(1.0, (4.4 - rr_) / 1.2))                       # 坑與土堆：泥土
        s2 = max(0.0, min(1.0, 1 - (path_d(vx, vy) - (1.3 + .4 * math.sin(vy * .3))) / 1.1))
        soil.append(max(s1, s2))
    sa = np.array(soil, np.float32)
    pca = pme.color_attributes.new('Mask', 'FLOAT_COLOR', 'POINT')
    pca.data.foreach_set('color', np.stack([sa, sa, sa, np.ones_like(sa)], 1).ravel())
    for p in pme.polygons:
        p.use_smooth = True
    pme.materials.append(GM)
    po = bpy.data.objects.new('PitGround', pme)
    sc.collection.objects.link(po)
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


append(S_ + 'GT01_out/GT01_GodTree_v003.blend', lambda nm: nm.endswith('_LOD0' if 'real' in argv else '_LOD1'), TREE, gh(*TREE) - .6)
glb(EXP + 'AL01_RootAltarTerrace/AL01_RootAltarTerrace_v001.glb', ALT, -.05)
_rim = sum(gh(PIT[0] + 3.3 * math.cos(a_), PIT[1] + 3.3 * math.sin(a_)) for a_ in (0, 1.57, 3.14, 4.71)) / 4
if not REAL:   # 真模型模式的坑直接挖在地形裡（CO01 v002 是平板狀，不像設定圖）
    glb(EXP + 'CO01_ExcavatedPit/CO01_ExcavatedPit_v002.glb', PIT, _rim - gh(*PIT) - .05)
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
    if REAL:   # 真模型模式：一整條漸細、半埋在土裡的樹根（掃描樹皮），不是一顆顆石頭
        cu = bpy.data.curves.new('RootRidge', 'CURVE')
        cu.dimensions = '3D'
        cu.bevel_depth = 1.0
        cu.bevel_resolution = 4
        sp = cu.splines.new('NURBS')
        sp.points.add(N)
        for i in range(N + 1):
            t = i / N
            x = ax + (bx - ax) * t + math.sin(t * 5 + ax) * 1.2
            y = ay + (by - ay) * t + math.cos(t * 4 + ay) * 1.2
            r = (r0 + (r1 - r0) * t) * .55
            sp.points[i].co = (x, y, gh(x, y) + r * .15 - .05 * t, 1)
            sp.points[i].radius = r * (1 - .6 * t ** 2)
        sp.use_endpoint_u = True
        sp.order_u = 3
        o = bpy.data.objects.new('RootRidge', cu)
        sc.collection.objects.link(o)
        o.scale.z = 1.0
        cu.materials.append(M_BARKR)
        return
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
if 'real' in argv:     # 換成真的樹模型（collection instance）
    _LIB = {'P': ['umbrella_pine_lib'], 'B': ['broadleaf_B_lib'], 'M': ['broadleaf_M_lib'], 'G': ['godtree_t10a', 'godtree_t10b', 'godtree_t10c']}
    _SK = lambda nm: nm in ('Grid', 'Cube') or nm.startswith(('Cylinder', 'Camera', 'Sun', 'Human'))
    _COLS = {}
    for _k, _fs in _LIB.items():
        _COLS[_k] = []
        for _fn in _fs:
            _c = bpy.data.collections.new('T_' + _fn)
            with bpy.data.libraries.load(S_ + _fn + '.blend', link=False) as (_s, _d):
                _d.objects = [nm for nm in _s.objects if not _SK(nm)]
            for _o in _d.objects:
                if _o is not None and _o.type == 'MESH':
                    _c.objects.link(_o)
            _COLS[_k].append(_c)

    def _inst(k):
        def f(x, y, s):
            e = bpy.data.objects.new(f'Tree_{k}', None)
            e.instance_type = 'COLLECTION'
            e.instance_collection = R.choice(_COLS[k])
            s = s * (.62 if k == 'G' else 1.0)    # 巨木庫是神木做法、樹冠很寬；縮到設定圖裡的比例
            e.scale = (s, s, s * R.uniform(.94, 1.06))
            e.rotation_euler.z = R.uniform(0, 6.283)
            e.location = (x, y, gh(x, y) - .25)
            sc.collection.objects.link(e)
        return f
    KIND = {k: _inst(k) for k in KIND}
GAP = {'P': 9.0, 'B': 9.0, 'M': 6.5, 'G': 14.0}


def zone_kind(x, y):
    dc = math.hypot(x - CLEAR[0], y - CLEAR[1])
    if x > 30 and -30 < y < 60:
        return R.choice('PPPBM')           # 東坡：松為主
    if dc < CLEAR[2] + 12:
        return R.choice('PPBBM')           # 空地邊緣：松與黃綠闊葉（照設定圖 V3）
    if x < -40 or y > 55:
        return R.choice('GPPMM')           # 西、北深林：巨木與松
    return R.choice('PPMBG')


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


import os as _os2
_LOCK = OUT + 'D2_plan_locked.json'   # 樹位置鎖定（六張設定圖就是照這份畫的），改路線也不重洗整片森林
if _os2.path.exists(_LOCK):
    TREES = [tuple(t_) for t_ in json.load(open(_LOCK, encoding='utf-8'))['trees'] if path_d(t_[0], t_[1]) > 4.0]
tries = 0 if not TREES else 10 ** 9
while len(TREES) < (260 if not QUICK else 120) and tries < 60000:
    tries += 1
    x, y = R.uniform(-125, 125), R.uniform(-125, 125)
    if not ok(x, y):
        continue
    k = zone_kind(x, y)
    if any(math.hypot(x - tx, y - ty) < max(GAP[k], GAP[tk]) * R.uniform(.85, 1.1) for tx, ty, tk, _ in TREES):
        continue
    TREES.append((x, y, k, R.uniform(.85, 1.15)))
_CAMS = [(2.5, -97), (6, -13), (15, -10.5), (-6, 12), (1, 91)]
for x, y, k, s in TREES:
    if 'real' in argv and any(math.hypot(x - cx, y - cy) < (16 if k == 'G' else 8) for cx, cy in _CAMS):
        continue   # 真樹的樹冠比方塊寬，相機旁邊的樹拿掉，免得鏡頭被擋
    KIND[k](x, y, s)
if 'real' in argv:   # 區塊外（鄰近區塊）的林子也種上，遠景才不會空掉；用另一個亂數，不動區塊內的樹
    FR = random.Random(99)
    extra = []
    for _ in range(40000):
        x, y = FR.uniform(-172, 172), FR.uniform(-172, 172)
        if max(abs(x), abs(y)) < 126 or path_d(x, y) < 5 or (x > 40 and -10 < y < 50):
            continue
        if any(math.hypot(x - a_, y - b_) < 10 for a_, b_ in extra):
            continue
        extra.append((x, y))
        KIND[FR.choice('PPBMMG')](x, y, FR.uniform(.85, 1.15))
        if len(extra) >= 320:
            break
    print('EXTRA', len(extra))

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
if 'real' in argv:
    texmat(M_DIRT, 'brown_mud_02_diff_2k.png', 'brown_mud_02_nor_gl_2k.png', 'brown_mud_02_rough_2k.png', .6, (1.05, .72, .46), box=True)
for i in range(0 if 'real' in argv else 14):   # 真模型模式用核心組的 CO01 坑模型，不放方塊土堆
    a = i / 14 * 6.283 + R.uniform(-.2, .2)
    rr = 3.2 + R.uniform(-.3, .6)
    x, y = PIT[0] + math.cos(a) * rr, PIT[1] + math.sin(a) * rr
    blob((x, y, gh(x, y) + .05), R.uniform(.7, 1.2), M_DIRT, sq=(1.5, 1.1, .38), sub=3 if 'real' in argv else 1)
if 'real' not in argv:
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=2.6, depth=.05, location=(PIT[0], PIT[1], gh(*PIT) + .15))
    put(bpy.context.object, mat('hole', (.06, .04, .03)))

# ---------------- 林下植物（真模型模式）：蕨叢、心形葉，做幾個樣板再用 instance 鋪滿路旁與空地 ----------------
if 'real' in argv:
    from mathutils import Matrix
    exec(compile(open(S_ + 'plants.py', encoding='utf-8').read(), S_ + 'plants.py', 'exec'))
    fern_mat = _leaf_material('UG01_Fern', (.040, .085, .022, 1), (.085, .16, .040, 1), (.12, .19, .06, 1), gloss=.5)
    heart_mat = _leaf_material('UG02_Heart', (.030, .070, .022, 1), (.070, .13, .040, 1), (.13, .19, .08, 1), gloss=.35)
    stem_mat = bpy.data.materials.new('UG_Stem')
    stem_mat.use_nodes = True
    next(x for x in stem_mat.node_tree.nodes if x.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.05, .07, .02, 1)
    PR = random.Random(17)
    UG = []
    for i in range(8):
        before = set(bpy.data.objects)
        if i < 5:
            fern(f'UGF{i}', Vector((0, 0, 0)), PR, 1.0, fern_mat, stem_mat)
        else:
            heart_plant(f'UGH{i}', Vector((0, 0, 0)), PR, 1.0, heart_mat, stem_mat)
        col = bpy.data.collections.new(f'UG{i}')
        for o in set(bpy.data.objects) - before:
            for c_ in list(o.users_collection):
                c_.objects.unlink(o)
            col.objects.link(o)
        UG.append(col)
    nug = 0
    for i in range(60000):
        x, y = PR.uniform(-70, 70), PR.uniform(-105, 95)
        pdist = path_d(x, y)
        near = min(math.hypot(x - cx, y - cy) for cx, cy in _CAMS)
        if pdist < 2.2 or math.hypot(x - PIT[0], y - PIT[1]) < 4.2 or math.hypot(x - ALT[0], y - ALT[1]) < 6.5:
            continue
        # 鏡頭附近、路旁最密，往外變稀
        p = max(.9 * math.exp(-near / 18), .5 * math.exp(-(pdist - 2) / 6), .06)
        if PR.random() > p:
            continue
        e = bpy.data.objects.new('UG', None)
        e.instance_type = 'COLLECTION'
        e.instance_collection = PR.choice(UG)
        s_ = PR.uniform(.7, 1.6) * (1.25 if pdist < 6 else 1.0)
        e.scale = (s_, s_, s_)
        e.rotation_euler.z = PR.uniform(0, 6.283)
        e.location = (x, y, gh(x, y) - .04)
        sc.collection.objects.link(e)
        nug += 1
        if nug >= 9000:
            break
    print('UNDERGROWTH', nug)
    # 坑：土塊、被挖斷的細根、坑底積水
    CR_ = random.Random(23)
    for i in range(70):
        a = CR_.uniform(0, 6.283)
        rr_ = CR_.uniform(1.8, 4.6)
        x, y = PIT[0] + math.cos(a) * rr_, PIT[1] + math.sin(a) * rr_
        r_ = CR_.uniform(.06, .22)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r_, location=(x, y, gh(x, y) + r_ * .3))
        o = bpy.context.object
        o.scale = (CR_.uniform(1.0, 1.6), CR_.uniform(.8, 1.3), CR_.uniform(.35, .55))
        o.rotation_euler = (CR_.uniform(0, 3), CR_.uniform(0, 3), CR_.uniform(0, 6))
        o.data.materials.append(M_DIRT)
    for i in range(9):   # 斷根：從坑壁伸出來
        a = CR_.uniform(-1.2, 2.4)
        p0 = Vector((PIT[0] + math.cos(a) * 2.9, PIT[1] + math.sin(a) * 2.9, 0))
        p0.z = gh(p0.x, p0.y) - .25
        d = Vector((-math.cos(a), -math.sin(a), CR_.uniform(-.3, .2))).normalized()
        L = CR_.uniform(.5, 1.3)
        pts = [p0, p0 + d * L * .5 + Vector((0, 0, CR_.uniform(-.1, .1))), p0 + d * L]
        cu = bpy.data.curves.new(f'PitRoot{i}', 'CURVE')
        cu.dimensions = '3D'
        cu.bevel_depth = CR_.uniform(.025, .06)
        cu.bevel_resolution = 3
        sp = cu.splines.new('NURBS')
        sp.points.add(len(pts) - 1)
        for j, pp in enumerate(pts):
            sp.points[j].co = (pp.x, pp.y, pp.z, 1)
        sp.use_endpoint_u = True
        co_ = bpy.data.objects.new(f'PitRoot{i}', cu)
        sc.collection.objects.link(co_)
        cu.materials.append(M_ROOT)
    wm = bpy.data.materials.new('PuddleWater')
    wm.use_nodes = True
    wb = next(x for x in wm.node_tree.nodes if x.type == 'BSDF_PRINCIPLED')
    wb.inputs['Base Color'].default_value = (.03, .025, .02, 1)
    wb.inputs['Roughness'].default_value = .04
    bpy.ops.mesh.primitive_circle_add(vertices=40, radius=1.0, fill_type='NGON',
                                      location=(PIT[0] + .3, PIT[1] - .2, gh(PIT[0] + .3, PIT[1] - .2) + .12))
    pu = bpy.context.object
    pu.scale = (1.2, .8, 1)
    pu.data.materials.append(wm)

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
if 'real' in argv:   # 霧壓低：林間一層低霧，樹冠露出來（設定圖 V1）
    fog.location.z, fog.scale.z = 4, 26
fm = bpy.data.materials.new('fog')
fm.use_nodes = True
nt = fm.node_tree
for nd in list(nt.nodes):
    if nd.type == 'BSDF_PRINCIPLED':
        nt.nodes.remove(nd)
vs = nt.nodes.new('ShaderNodeVolumePrincipled')
vs.inputs['Density'].default_value = .0045 if 'real' in argv else .005
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
if 'real' in argv:
    sc.view_settings.exposure = 1.1
    bg.inputs['Strength'].default_value = 2.4
sc.render.resolution_x, sc.render.resolution_y = 1536, 1024
SHOTS = {
    'V1': ((70, -105, 62), (-6, 18, 0), 24, '俯瞰全景（東南高處）'),
    'V2': ((2.5, -97, 1.7), (1.5, -60, 4.5), 22, '南入口（Josh 根拱）往北看'),
    'V3': ((6, -13, 1.9), (1, 18, 5.0), 16, '祭壇前（神木左、祭壇中右、坑右前）'),
    'V4': ((15, -10.5, 2.4), (10, -3, -.6), 24, '坑邊近景'),
    'V5': ((-6, 12, 2.4), (12, -30, 2.0), 20, '神木根旁回頭看（往南看祭壇與小路）'),
    'V6': ((1, 91, 1.7), (-5, 135, 5.0), 24, '北入口（核心組根拱）往外看'),
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
    sc.render.filepath = OUT + (f'D2_real_{k}.png' if 'real' in argv else f'D2_plan_{k}.png')
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
