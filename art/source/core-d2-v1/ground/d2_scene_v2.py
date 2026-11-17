# D2 設定圖 V2（南入口）構圖組裝：根拱在前、神木在後、兩側板根牆、泥路、踏石、大苔石、蕨與蕈
#   blender -b --factory-startup -P d2_scene_v2.py -- <tag> [quick]
import sys, math, random
import numpy as np
from mathutils import Vector, noise, Matrix

S_ = 'D:/chengtian/4-素材與快取/bark-sample/'
BASE = S_ + 'godtree_base.py'
src = open(BASE, encoding='utf-8').read()
exec(compile(src.split('# ---------------- 樹幹')[0], BASE, 'exec'))
noise.seed_set(3)
R = random.Random(3)
tail = src[src.index('# ---------------- 燈光'):]
tail = tail[:tail.index('# 1.75 m 人形尺')]
exec(compile(open(S_ + 'plants.py', encoding='utf-8').read(), S_ + 'plants.py', 'exec'))
GT = 'D:/chengtian/4-素材與快取/polyhaven-ground/'
sc = bpy.context.scene
TREE_Y = 60.0


def path_x(y):
    return 1.2 * math.sin(y * .11) + .6 * math.sin(y * .29 + 1)


def pmask(x, y):          # 1＝泥路中心
    d = abs(x - path_x(y))
    w = 1.6 + .5 * math.sin(y * .4)
    return max(0.0, min(1.0, 1 - (d - w * .5) / 1.0))


def gh(x, y):
    base = fb((x, y, 0), .05, 3) * .45 + fb((x, y, 1), .35, 3) * .10
    side = min(1, abs(x - path_x(y)) / 9) ** 1.5 * .9          # 路兩側微微高起
    return base + side - pmask(x, y) * .16 + max(0, y - 14) * .02


def append(path, want, offset=(0, 0, 0), dz=0.0):
    with bpy.data.libraries.load(path, link=False) as (s, d):
        d.objects = [n for n in s.objects if want(n)]
    out = []
    for o in d.objects:
        if o is None:
            continue
        sc.collection.objects.link(o)
        o.location = Vector(o.location) + Vector(offset) + Vector((0, 0, dz))
        out.append(o)
    return out


SKIP = lambda n: n in ('Grid', 'Cube') or n.startswith(('Cylinder', 'Camera', 'Sun'))
# 根拱（原點）
append(S_ + 'root_arch_lib.blend', lambda n: not SKIP(n), dz=-.25)
# 神木遊戲版 LOD0
append(S_ + 'GT01_out/GT01_GodTree_v003.blend', lambda n: n.endswith('_LOD0'), offset=(2, TREE_Y, 0), dz=gh(2, TREE_Y) - .6)
# 板根牆：A 放左後、C 放右後、B 放左前；倒木放右遠處；樹樁放左遠處
append(S_ + 'd2_wood_lib.blend', lambda n: n.startswith('DR02_A'), offset=(1, 9, 0), dz=gh(-16, 18) - .1)
append(S_ + 'd2_wood_lib.blend', lambda n: n.startswith('DR02_C'), offset=(3, 5, 0), dz=gh(18, 14) - .1)
append(S_ + 'd2_wood_lib.blend', lambda n: n.startswith('DR07_A'), offset=(-34, 30, 0), dz=gh(-24, 25) - .1)
append(S_ + 'd2_wood_lib.blend', lambda n: n.startswith('DR06_A'), offset=(34, 34, 0), dz=gh(26, 28) - .1)

# ---------------- 地面：泥路＋腐葉林床（掃描材質，路面下凹、濕） ----------------
X0, X1, Y0, Y1, RES = -45, 45, -24, 95, .22
nx, ny = int((X1 - X0) / RES), int((Y1 - Y0) / RES)
xs = np.linspace(X0, X1, nx + 1)
ys = np.linspace(Y0, Y1, ny + 1)
V = [(x, y, gh(x, y)) for y in ys for x in xs]
F = [(j * (nx + 1) + i, j * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i) for j in range(ny) for i in range(nx)]
gm_ = bpy.data.meshes.new('Ground')
gm_.from_pydata(V, [], F)
for p in gm_.polygons:
    p.use_smooth = True
ca = gm_.color_attributes.new('Mask', 'FLOAT_COLOR', 'POINT')
ca.data.foreach_set('color', np.array([[pmask(v[0], v[1]), 0, 0, 1] for v in V], np.float32).ravel())
uvl = gm_.uv_layers.new(name='UVMap')
idx = np.empty(len(gm_.loops), np.int32)
gm_.loops.foreach_get('vertex_index', idx)
uvl.data.foreach_set('uv', (np.array([(v[0] / 2.5, v[1] / 2.5) for v in V], np.float32)[idx]).ravel())
go = bpy.data.objects.new('Ground', gm_)
sc.collection.objects.link(go)
m = bpy.data.materials.new('GroundMat')
m.use_nodes = True
N, L = m.node_tree.nodes, m.node_tree.links
bs = next(n for n in N if n.type == 'BSDF_PRINCIPLED')


def tex(name, cs='Non-Color'):
    t = N.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(GT + name)
    t.image.colorspace_settings.name = cs
    return t


vc = N.new('ShaderNodeVertexColor'); vc.layer_name = 'Mask'
sp = N.new('ShaderNodeSeparateColor'); L.new(vc.outputs[0], sp.inputs[0])
ld, md = tex('forest_leaves_02_diffuse_2k.png', 'sRGB'), tex('brown_mud_02_diff_2k.png', 'sRGB')
ln, mn = tex('forest_leaves_02_nor_gl_2k.png'), tex('brown_mud_02_nor_gl_2k.png')
mc = N.new('ShaderNodeMixRGB'); L.new(sp.outputs[0], mc.inputs[0]); L.new(ld.outputs[0], mc.inputs[1]); L.new(md.outputs[0], mc.inputs[2])
hs = N.new('ShaderNodeHueSaturation'); hs.inputs['Saturation'].default_value = .55; hs.inputs['Value'].default_value = .40
L.new(mc.outputs[0], hs.inputs['Color'])
# 大尺度的苔綠斑，打散重複感
nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = .35; nz.inputs['Detail'].default_value = 5
rr = N.new('ShaderNodeMapRange'); rr.inputs['From Min'].default_value = .5; rr.inputs['From Max'].default_value = .7
L.new(nz.outputs['Fac'], rr.inputs['Value'])
inv = N.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1; L.new(sp.outputs[0], inv.inputs[1])
mm_ = N.new('ShaderNodeMath'); mm_.operation = 'MULTIPLY'; L.new(rr.outputs[0], mm_.inputs[0]); L.new(inv.outputs[0], mm_.inputs[1])
gmx = N.new('ShaderNodeMixRGB'); gmx.inputs[2].default_value = (.035, .06, .016, 1)
mf = N.new('ShaderNodeMath'); mf.operation = 'MULTIPLY'; mf.inputs[1].default_value = .75; L.new(mm_.outputs[0], mf.inputs[0])
L.new(mf.outputs[0], gmx.inputs[0]); L.new(hs.outputs[0], gmx.inputs[1])
L.new(gmx.outputs[0], bs.inputs['Base Color'])
mnm = N.new('ShaderNodeMixRGB'); L.new(sp.outputs[0], mnm.inputs[0]); L.new(ln.outputs[0], mnm.inputs[1]); L.new(mn.outputs[0], mnm.inputs[2])
nm = N.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 1.6; L.new(mnm.outputs[0], nm.inputs['Color']); L.new(nm.outputs[0], bs.inputs['Normal'])
rg = N.new('ShaderNodeMapRange'); rg.inputs['To Min'].default_value = .85; rg.inputs['To Max'].default_value = .35     # 路面濕、反光
L.new(sp.outputs[0], rg.inputs['Value']); L.new(rg.outputs[0], bs.inputs['Roughness'])
gm_.materials.append(m)

# ---------------- 石頭：路上的踏石、兩側的大苔石 ----------------
stm = bpy.data.materials.new('MossRock')
stm.use_nodes = True
SN, SL = stm.node_tree.nodes, stm.node_tree.links
sb = next(n for n in SN if n.type == 'BSDF_PRINCIPLED')
tc = SN.new('ShaderNodeTexCoord')
mp = SN.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (.5, .5, .5); SL.new(tc.outputs['Object'], mp.inputs[0])
st = SN.new('ShaderNodeTexImage'); st.image = bpy.data.images.load(GT + 'mossy_rock_diff_2k.png'); st.projection = 'BOX'; st.projection_blend = .3
SL.new(mp.outputs[0], st.inputs[0])
sn_ = SN.new('ShaderNodeTexImage'); sn_.image = bpy.data.images.load(GT + 'mossy_rock_nor_gl_2k.png'); sn_.image.colorspace_settings.name = 'Non-Color'
sn_.projection = 'BOX'; sn_.projection_blend = .3; SL.new(mp.outputs[0], sn_.inputs[0])
h2 = SN.new('ShaderNodeHueSaturation'); h2.inputs['Saturation'].default_value = .45; h2.inputs['Value'].default_value = .85
SL.new(st.outputs[0], h2.inputs['Color'])
geo = SN.new('ShaderNodeNewGeometry'); sx = SN.new('ShaderNodeSeparateXYZ'); SL.new(geo.outputs['Normal'], sx.inputs[0])
tr = SN.new('ShaderNodeMapRange'); tr.inputs['From Min'].default_value = .35; tr.inputs['From Max'].default_value = .8; SL.new(sx.outputs['Z'], tr.inputs['Value'])
mo = SN.new('ShaderNodeMixRGB'); mo.inputs[2].default_value = (.03, .058, .016, 1); SL.new(tr.outputs[0], mo.inputs[0]); SL.new(h2.outputs[0], mo.inputs[1])
SL.new(mo.outputs[0], sb.inputs['Base Color'])
nmp = SN.new('ShaderNodeNormalMap'); SL.new(sn_.outputs[0], nmp.inputs['Color']); SL.new(nmp.outputs[0], sb.inputs['Normal'])
sb.inputs['Roughness'].default_value = .7
moss_mat = _leaf_material('MossTuftBright', (.045, .085, .016, 1), (.13, .20, .04, 1), (.15, .22, .06, 1), gloss=.8)
mossbuf = LeafBuf()


def rock(x, y, sx_, sy_, sz_, seed, sink=.3, moss=True):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5 if sx_ > .8 else 4, radius=1, location=(x, y, gh(x, y) + sz_ * (1 - sink) - sz_ * .5))
    o = bpy.context.object
    rz = R.uniform(0, 6.3)
    for v in o.data.vertices:
        p = v.co.copy()
        n1 = fb((p.x * 1.2 + seed, p.y * 1.2, p.z * 1.2), 1, 3)
        n2 = fb((p.x * 4 + seed, p.y * 4, p.z * 4), 1, 2)
        # 幾個平切面：像風化的山石，不是圓球
        k = 1 + .28 * n1 + .06 * n2
        q = Vector((p.x * sx_, p.y * sy_, p.z * sz_ * .5)) * k
        for a in range(4):
            nrm = Vector((math.cos(a * 1.7 + seed), math.sin(a * 1.7 + seed), .35 + .2 * a)).normalized()
            dlim = (.62 + .1 * a) * min(sx_, sy_)
            dd = q.dot(nrm)
            if dd > dlim:
                q -= nrm * (dd - dlim) * .85
        v.co = q
    o.rotation_euler.z = rz
    bpy.ops.object.shade_smooth()
    o.data.materials.append(stm)
    if moss:
        mw = o.matrix_world.copy()
        cnt = int(900 * sx_ * sy_)
        for i in range(cnt):
            v = o.data.vertices[R.randrange(len(o.data.vertices))]
            if v.normal.z < .45:
                continue
            p = Matrix.Rotation(rz, 4, 'Z') @ v.co + Vector(o.location)
            dd = (Vector((0, 0, 1)) + Vector((R.uniform(-.5, .5), R.uniform(-.5, .5), 0))).normalized()
            dd, s2, u2 = _frame(dd)
            Lm = R.uniform(.03, .07)
            g = R.uniform(.7, 1.15)
            mossbuf.leaf(p + Vector((R.uniform(-.05, .05), R.uniform(-.05, .05), -.01)), dd, s2, u2, Lm, Lm * .22, shape=lambda u: (1 - u) ** .6,
                         fold=.3, droop=R.uniform(0, .5), tint=(g, g, g * .8), nu=2, nv=1)
    return o


# 踏石：沿路每隔幾步一塊
y = -12.0
k = 0
while y < 30:
    x = path_x(y) + R.uniform(-.5, .5)
    rock(x, y, R.uniform(.35, .6), R.uniform(.3, .5), R.uniform(.2, .3), 10 + k, sink=.35, moss=False)
    y += R.uniform(1.6, 2.8)
    k += 1
# 大苔石：前景右、左，以及遠處幾塊
for (x, y, s1, s2, s3) in [(6.5, -9.5, 2.0, 1.5, 1.5), (9.2, -7.2, 1.1, .9, .8), (-7.5, -8, 1.5, 1.2, 1.0), (-10.5, -4.5, .9, .8, .6),
                             (12, 6, 1.6, 1.3, 1.1), (-13, 12, 1.8, 1.4, 1.2), (7, 20, 1.2, 1.0, .8), (-6, 24, 1.3, 1.0, .9), (3.5, -11, .6, .5, .4)]:
    rock(x, y, s1, s2, s3, 100 + int(x * 7 + y), sink=.3)
mossbuf.build('RockMoss', moss_mat)

# ---------------- 植物：蕨、心形葉、蕈、落葉（避開泥路） ----------------
fern_mat = _leaf_material('UG01_Fern', (.040, .085, .022, 1), (.085, .16, .040, 1), (.12, .19, .06, 1), gloss=.5)
heart_mat = _leaf_material('UG02_Heart', (.030, .070, .022, 1), (.070, .13, .040, 1), (.13, .19, .08, 1), gloss=.35)
litter_mat = _leaf_material('Litter', (.55, .5, .45, 1), (.85, .8, .72, 1), (.9, .85, .7, 1), gloss=.6)
mush_mat = mushroom_material()
stem_mat = bpy.data.materials.new('UG_Stem'); stem_mat.use_nodes = True
next(n for n in stem_mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.05, .06, .025, 1)
QK = QUICK


def free(x, y):
    return pmask(x, y) < .15


# 前景大蕨（設定圖左下、右下）
for (x, y, s) in [(-4.5, -11.5, 1.7), (-6.2, -9.8, 1.5), (-3.2, -9.2, 1.2), (5.0, -12.2, 1.6), (7.8, -11.5, 1.4), (4.2, -9.5, 1.1), (-8.5, -11, 1.3)]:
    fern(f'FG{x}', Vector((x, y, gh(x, y) - .03)), R, s, fern_mat, stem_mat)
n = 0
for i in range(5000):
    x, y = R.uniform(-22, 22), R.uniform(-13, 34)
    if not free(x, y) or abs(x - path_x(y)) > 16 + R.uniform(-4, 4):
        continue
    dens = 1 / (1 + max(0, y + 2) * .035)
    if R.random() > dens:
        continue
    if R.random() < .55:
        fern(f'F{i}', Vector((x, y, gh(x, y) - .03)), R, R.uniform(.7, 1.4), fern_mat, stem_mat)
    else:
        heart_plant(f'H{i}', Vector((x, y, gh(x, y))), R, R.uniform(.9, 1.5), heart_mat, stem_mat)
    n += 1
    if n > (620 if QK else 800):
        break
for i in range(60):
    x, y = R.uniform(-11, 11), R.uniform(-13, 10)
    if free(x, y):
        mushrooms(f'M{i}', Vector((x, y, 0)), R, R.randint(4, 10), R.uniform(1.0, 1.8), mush_mat, ground=gh)


def _place():
    x, y = R.uniform(-9, 9), R.uniform(-14, 6)
    return (x, y), gh(x, y)


litter('Litter', R, 1500 if QK else 3000, _place, litter_mat)


# ---------------- 補強：地面苔毯、根腳邊的蕨與成排的蕈、背景古林、苔換亮 ----------------
gmoss = LeafBuf()
for i in range(140000 if QK else 220000):
    x, y = R.uniform(-16, 16), R.uniform(-14, 24)
    if pmask(x, y) > .35 or fb((x, y, 5), .45, 2) < .02:
        continue
    dd = (Vector((0, 0, 1)) + Vector((R.uniform(-.6, .6), R.uniform(-.6, .6), 0))).normalized()
    dd, s2, u2 = _frame(dd)
    Lm = R.uniform(.06, .14)
    g = R.uniform(.7, 1.15)
    gmoss.leaf(Vector((x, y, gh(x, y) - .005)), dd, s2, u2, Lm, Lm * .25, shape=lambda u: (1 - u) ** .6, fold=.3, droop=R.uniform(0, .6),
               tint=(g, g, g * .8), nu=2, nv=1)
gmoss.build('GroundMoss', moss_mat)
# 根腳（左約 x=-8.5、右約 x=8.5，y≈0）：蕨、心形葉、成排褐蕈
for sx_ in (-1, 1):
    for j in range(16):
        x, y = sx_ * R.uniform(5.5, 12.5), R.uniform(-4.5, 3.5)
        if R.random() < .6:
            fern(f'Foot{sx_}{j}', Vector((x, y, gh(x, y) - .03)), R, R.uniform(.9, 1.6), fern_mat, stem_mat)
        else:
            heart_plant(f'FootH{sx_}{j}', Vector((x, y, gh(x, y))), R, R.uniform(1.0, 1.7), heart_mat, stem_mat)
    for j in range(9):
        x, y = sx_ * R.uniform(4.8, 9.5), R.uniform(-5.5, -1.5)
        mushrooms(f'FootM{sx_}{j}', Vector((x, y, 0)), R, R.randint(5, 11), R.uniform(1.3, 2.2), mush_mat, ground=gh)
# 背景古林：用神木的遠景版縮小、轉向，當外圈的古林巨木與中型老樹（同一種樹）
spots = [(-30, 28, .42), (-44, 50, .5), (-26, 62, .36), (-52, 78, .5), (-34, 92, .45), (30, 26, .4), (46, 46, .5), (27, 66, .36),
         (54, 80, .5), (36, 96, .44), (-60, 30, .45), (62, 28, .45), (-14, 100, .4), (16, 104, .4), (-22, 44, .3), (24, 44, .3)]
for k, (x, y, sc_) in enumerate(spots):
    lod = '_LOD1' if math.hypot(x, y + 15) < 75 else '_LOD2'
    for o in append(S_ + 'GT01_out/GT01_GodTree_v003.blend', lambda n, lod=lod: n.endswith(lod)):
        o.scale = (sc_, sc_, sc_ * R.uniform(.9, 1.15))
        o.rotation_euler.z = R.uniform(0, 6.3)
        o.location = (x, y, gh(x, y) - .4 * sc_)
# 之前做的苔（根拱、板根牆上）換成亮一點的苔
for o in bpy.data.objects:
    if o.type == 'MESH' and ('moss' in o.name.lower()) and o.data.materials:
        o.data.materials[0] = moss_mat

# ---------------- 光、霧、相機 ----------------
exec(compile(tail.replace("fog.scale = (160, 160, 50)", "fog.scale = (260, 260, 110)").replace("vol.inputs['Density'].default_value = .0055", "vol.inputs['Density'].default_value = .0026"), BASE, 'exec'))
# 低霧：貼地一層較濃
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 35, 1.6))
lf = bpy.context.object
lf.scale = (200, 150, 3.2)
fm2 = bpy.data.materials.new('LowFog'); fm2.use_nodes = True
FN = fm2.node_tree.nodes
for nd in list(FN):
    if nd.type == 'BSDF_PRINCIPLED':
        FN.remove(nd)
v2 = FN.new('ShaderNodeVolumePrincipled'); v2.inputs['Density'].default_value = .0045; v2.inputs['Color'].default_value = (.8, .84, .88, 1)
fm2.node_tree.links.new(v2.outputs[0], next(n for n in FN if n.type == 'OUTPUT_MATERIAL').inputs['Volume'])
lf.data.materials.append(fm2)
sc.cycles.samples = 64 if QK else 192
sc.view_settings.exposure = 1.0


def shot(nm_, loc, tgt, lens, res=(1820, 1024)):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.data.lens = lens
    c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = c
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = OUT + f'd2v2_{TAG}_{nm_}.png'
    bpy.ops.render.render(write_still=True)


shot('V2', (.6, -15.5, 1.7), (.3, 0, 3.3), 21)
