# D2 林床拼塊 DS01 試做（核心組範本）：4×4 m 真幾何地面——濕泥＋腐葉層＋苔墊＋細根＋斷枝＋小石＋落葉
#   blender -b --factory-startup -P floor_tile.py -- <tag> [quick] [seed]
import os, sys, math, random
import numpy as np
from mathutils import Vector, noise, Matrix

BASE = 'D:/chengtian/4-素材與快取/bark-sample/godtree_base.py'
src = open(BASE, encoding='utf-8').read()
exec(compile(src.split('# ---------------- 樹幹')[0], BASE, 'exec'))   # tube(), fb(), MAT（掃描樹皮）, bpy
SEED = int([a for a in ARGS if a.isdigit()][0]) if any(a.isdigit() for a in ARGS) else 1
R = random.Random(SEED)
noise.seed_set(SEED)
GT = 'D:/chengtian/4-素材與快取/polyhaven-ground/'
S = 4.0            # 拼塊邊長
RES = 0.02 if not QUICK else 0.03


def gimg(name, cs='Non-Color'):
    i = bpy.data.images.load(GT + name)
    i.colorspace_settings.name = cs
    return i


# ---------- 底面：泥與腐葉兩張掃描混合，凹凸做進幾何 ----------
def loadgray(name):
    im = gimg(name)
    w, h = im.size
    a = np.array(im.pixels[:], np.float32).reshape(h, w, -1)[:, :, 0]
    return a, w, h


mud_d, mw, mh = loadgray('brown_mud_02_disp_2k.png')
lf_d, lw, lh = loadgray('forest_leaves_02_disp_2k.png')
TILE_M = 2.0      # 掃描圖覆蓋 2 m


def samp(a, w, h, u, v):
    return a[int((v % 1) * (h - 1)), int((u % 1) * (w - 1))]


def edge_fade(x, y):
    # 邊緣 15 cm 內起伏收回到 0，讓拼塊可以無縫互拼
    d = min(x + S / 2, S / 2 - x, y + S / 2, S / 2 - y)
    return max(0.0, min(1.0, d / .15))


def leafmask(x, y):
    m = fb((x, y, 3.3), .55, 3) * .9 + .5
    return max(0.0, min(1.0, (m - .35) / .3))


def height(x, y):
    e = edge_fade(x, y)
    macro = fb((x, y, 0), .35, 3) * .18 + fb((x, y, 1), 1.2, 2) * .04
    u, v = x / TILE_M, y / TILE_M
    lm = leafmask(x, y)
    micro = (samp(mud_d, mw, mh, u, v) - .5) * .045 * (1 - lm) + (samp(lf_d, lw, lh, u, v) - .5) * .06 * lm
    return (macro + micro) * e, lm


N = int(S / RES)
bpy.ops.mesh.primitive_grid_add(x_subdivisions=N, y_subdivisions=N, size=S)
g = bpy.context.object
g.name = 'DS01_Ground'
me = g.data
lmv = []
for v in me.vertices:
    z, lm = height(v.co.x, v.co.y)
    v.co.z = z
    lmv.append(lm)
ca = me.color_attributes.new('Mask', 'FLOAT_COLOR', 'POINT')
ca.data.foreach_set('color', np.array([[l, 0, 0, 1] for l in lmv], np.float32).ravel())
for p in me.polygons:
    p.use_smooth = True
uv = me.uv_layers.active
for lp in me.loops:
    co = me.vertices[lp.vertex_index].co
    uv.data[lp.index].uv = (co.x / TILE_M, co.y / TILE_M)

gm = bpy.data.materials.new('DS01_Ground')
gm.use_nodes = True
Nn, Ln = gm.node_tree.nodes, gm.node_tree.links
bs = next(n for n in Nn if n.type == 'BSDF_PRINCIPLED')


def tex(name, cs='Non-Color'):
    t = Nn.new('ShaderNodeTexImage')
    t.image = gimg(name, cs)
    return t


vc = Nn.new('ShaderNodeVertexColor')
vc.layer_name = 'Mask'
sp = Nn.new('ShaderNodeSeparateColor')
Ln.new(vc.outputs[0], sp.inputs[0])
md, ld = tex('brown_mud_02_diff_2k.png', 'sRGB'), tex('forest_leaves_02_diffuse_2k.png', 'sRGB')
mn, ln_ = tex('brown_mud_02_nor_gl_2k.png'), tex('forest_leaves_02_nor_gl_2k.png')
mr, lr = tex('brown_mud_02_rough_2k.png'), tex('forest_leaves_02_rough_2k.png')
mixc = Nn.new('ShaderNodeMixRGB')
Ln.new(sp.outputs[0], mixc.inputs[0])
Ln.new(md.outputs[0], mixc.inputs[1])
Ln.new(ld.outputs[0], mixc.inputs[2])
hsv = Nn.new('ShaderNodeHueSaturation')     # 偏冷、偏暗、濕
hsv.inputs['Saturation'].default_value = .78
hsv.inputs['Value'].default_value = .62
Ln.new(mixc.outputs[0], hsv.inputs['Color'])
Ln.new(hsv.outputs[0], bs.inputs['Base Color'])
mixn = Nn.new('ShaderNodeMixRGB')
Ln.new(sp.outputs[0], mixn.inputs[0])
Ln.new(mn.outputs[0], mixn.inputs[1])
Ln.new(ln_.outputs[0], mixn.inputs[2])
nm = Nn.new('ShaderNodeNormalMap')
Ln.new(mixn.outputs[0], nm.inputs['Color'])
Ln.new(nm.outputs[0], bs.inputs['Normal'])
mixr = Nn.new('ShaderNodeMixRGB')
Ln.new(sp.outputs[0], mixr.inputs[0])
Ln.new(mr.outputs[0], mixr.inputs[1])
Ln.new(lr.outputs[0], mixr.inputs[2])
wet = Nn.new('ShaderNodeMath')               # 泥比較濕、較亮的反光
wet.operation = 'MULTIPLY'
wet.inputs[1].default_value = .8
Ln.new(mixr.outputs[0], wet.inputs[0])
Ln.new(wet.outputs[0], bs.inputs['Roughness'])
me.materials.append(gm)


def ground_z(x, y):
    return height(x, y)[0]


# ---------- 苔墊：低矮的苔丘，用 mossy_rock 掃描的綠苔部分 ----------
mm = bpy.data.materials.new('DS01_Moss')
mm.use_nodes = True
MN, ML = mm.node_tree.nodes, mm.node_tree.links
mb = next(n for n in MN if n.type == 'BSDF_PRINCIPLED')
nz = MN.new('ShaderNodeTexNoise')       # 細：一根根苔的毛絨
nz.inputs['Scale'].default_value = 900
nz.inputs['Detail'].default_value = 4
nz2 = MN.new('ShaderNodeTexNoise')      # 粗：苔的一叢叢與顏色變化
nz2.inputs['Scale'].default_value = 28
nz2.inputs['Detail'].default_value = 6
mcr = MN.new('ShaderNodeValToRGB')
mcr.color_ramp.elements[0].position = .35
mcr.color_ramp.elements[0].color = (.028, .038, .010, 1)
mcr.color_ramp.elements[1].position = .7
mcr.color_ramp.elements[1].color = (.085, .105, .026, 1)
ML.new(nz2.outputs[0], mcr.inputs[0])
cm2 = MN.new('ShaderNodeMixRGB')
cm2.blend_type = 'MULTIPLY'
cm2.inputs[0].default_value = .3
ML.new(mcr.outputs[0], cm2.inputs[1])
ML.new(nz.outputs[0], cm2.inputs[2])
ML.new(cm2.outputs[0], mb.inputs['Base Color'])
hsum = MN.new('ShaderNodeMath')
hsum.operation = 'ADD'
ML.new(nz.outputs[0], hsum.inputs[0])
ML.new(nz2.outputs[0], hsum.inputs[1])
bp = MN.new('ShaderNodeBump')
bp.inputs['Strength'].default_value = 1.0
bp.inputs['Distance'].default_value = .012
ML.new(hsum.outputs[0], bp.inputs['Height'])
ML.new(bp.outputs[0], mb.inputs['Normal'])
mb.inputs['Roughness'].default_value = .95

objs_moss = []
for i in range(R.randint(5, 8)):
    cx, cy = R.uniform(-1.6, 1.6), R.uniform(-1.6, 1.6)
    rx, ry = R.uniform(.18, .55), R.uniform(.15, .45)
    hgt = R.uniform(.05, .16)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=1, location=(cx, cy, 0))
    o = bpy.context.object
    for v in o.data.vertices:
        p = v.co.copy()
        n = fb((p.x * 2 + i, p.y * 2, p.z * 2), 1, 2)
        r = 1 + .18 * n
        top = max(-.4, p.z)
        # 圓鈍的丘，頂上一小叢一小叢鼓起（苔叢），邊緣貼地
        tuft = .5 + .5 * fb((p.x * 14 + i, p.y * 14, 0), 1, 2)
        v.co = Vector((p.x * rx * r, p.y * ry * r, (top ** .7 if top > 0 else top) * hgt * (1 + .25 * n) + max(0, top) * .018 * tuft))
    o.location.z = ground_z(cx, cy) - hgt * .2
    for p in o.data.polygons:
        p.use_smooth = True
    o.data.materials.append(mm)
    objs_moss.append(o)

# ---------- 細根：半埋、蜿蜒，邊緣鑽進土裡（掃描樹皮） ----------
for i in range(R.randint(3, 5)):
    a = R.uniform(0, 2 * math.pi)
    L = R.uniform(1.5, 3.2)
    x0, y0 = R.uniform(-1.4, 1.4), R.uniform(-1.4, 1.4)
    pts = []
    for k in range(9):
        t = k / 8
        ww = math.sin(t * 5 + i) * .18
        x = x0 + math.cos(a) * L * (t - .5) - math.sin(a) * ww
        y = y0 + math.sin(a) * L * (t - .5) + math.cos(a) * ww
        r0 = R.uniform(.04, .09)
        pts.append((x, y, ground_z(x, y) + r0 * .2 - .08 * (abs(t - .5) * 2) ** 3))
    rr = R.uniform(.025, .06)
    o = tube(f'Root{i}', pts, radius=lambda t, rr=rr: rr * (1 - .5 * abs(t - .5) * 2) + .015, flat=lambda t: 1.0,
             seed=10 + i, rib=.18, twist=.2, NU=24)
    o.data.materials.append(MAT)

# ---------- 斷枝與小石 ----------
twm = MAT
for i in range(R.randint(8, 14)):
    x, y = R.uniform(-1.8, 1.8), R.uniform(-1.8, 1.8)
    a = R.uniform(0, 2 * math.pi)
    L = R.uniform(.25, .9)
    rr = R.uniform(.008, .025)
    p0 = Vector((x, y, 0))
    d = Vector((math.cos(a), math.sin(a), 0))
    pts = [tuple(p0 + d * L * t + Vector((0, 0, ground_z(*(p0 + d * L * t).xy) + rr * .6))) for t in (0, .35, .7, 1)]
    o = tube(f'Twig{i}', pts, radius=lambda t, rr=rr: rr * (1 - .4 * t), flat=lambda t: 1.0, seed=40 + i, rib=.1, twist=.3, NU=10)
    o.data.materials.append(twm)

stm = bpy.data.materials.new('DS01_Stone')
stm.use_nodes = True
SN = stm.node_tree.nodes
sb = next(n for n in SN if n.type == 'BSDF_PRINCIPLED')
st = SN.new('ShaderNodeTexImage')
st.image = gimg('mossy_rock_diff_2k.png', 'sRGB')
hs = SN.new('ShaderNodeHueSaturation')
hs.inputs['Value'].default_value = .7
stm.node_tree.links.new(st.outputs[0], hs.inputs['Color'])
stm.node_tree.links.new(hs.outputs[0], sb.inputs['Base Color'])
sb.inputs['Roughness'].default_value = .8
for i in range(R.randint(10, 18)):
    x, y = R.uniform(-1.8, 1.8), R.uniform(-1.8, 1.8)
    s = R.uniform(.03, .14)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1, location=(x, y, 0))
    o = bpy.context.object
    for v in o.data.vertices:
        n = fb((v.co.x * 2 + i, v.co.y * 2, v.co.z * 2), 1, 2)
        v.co *= 1 + .3 * n
        v.co.z *= .6
        v.co *= s
    o.location.z = ground_z(x, y) - s * .25
    o.rotation_euler.z = R.uniform(0, 6.3)
    bpy.ops.object.shade_smooth()
    o.data.materials.append(stm)


# ---------- 落葉（單片，有葉脈、捲邊、乾濕深淺）＋大蕨叢＋心形葉植物 ----------
PL = 'D:/chengtian/4-素材與快取/bark-sample/plants.py'
exec(compile(open(PL, encoding='utf-8').read(), PL, 'exec'))
litter_mat = _leaf_material('DS01_LitterLeaf', (.55, .5, .45, 1), (.85, .8, .72, 1), (.9, .85, .7, 1), gloss=.6)
fern_mat = _leaf_material('UG01_Fern', (.035, .060, .022, 1), (.075, .11, .035, 1), (.10, .14, .05, 1), gloss=.55)
heart_mat = _leaf_material('UG02_Heart', (.025, .050, .020, 1), (.060, .095, .035, 1), (.11, .15, .07, 1), gloss=.35)
stem_mat = bpy.data.materials.new('UG_Stem')
stem_mat.use_nodes = True
next(n for n in stem_mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.05, .06, .025, 1)


def _place():
    x, y = R.uniform(-S / 2 + .06, S / 2 - .06), R.uniform(-S / 2 + .06, S / 2 - .06)
    if R.random() > .1 + .9 * leafmask(x, y):
        return None
    return (x, y), ground_z(x, y)


lo, count = litter('DS01_Litter', R, 700 if QUICK else 1100, _place, litter_mat)
# 植物：蕨叢沿根邊、心形葉成片
spots_f = [(-1.3, .9, 1.1), (1.2, 1.3, .9), (-.4, -1.4, .8), (1.5, -.6, 1.0)]
for i, (x, y, s_) in enumerate(spots_f):
    fern(f'UG01_Fern{i}', Vector((x, y, ground_z(x, y) - .02)), R, s_, fern_mat, stem_mat)
for i in range(9):
    x, y = R.uniform(-1.7, 1.7), R.uniform(-1.7, 1.7)
    heart_plant(f'UG02_Heart{i}', Vector((x, y, ground_z(x, y))), R, R.uniform(.8, 1.2), heart_mat, stem_mat)
print('LEAVES', count, 'GROUND', len(me.polygons))

# ---------- 燈光、霧、相機（照 D2 V6 的近景感覺） ----------
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 64 if QUICK else 160
sc.cycles.use_denoising = True
try:
    pr = bpy.context.preferences.addons['cycles'].preferences
    pr.compute_device_type = 'OPTIX'
    pr.get_devices()
    for d in pr.devices:
        d.use = True
    sc.cycles.device = 'GPU'
except Exception as e:
    print(e)
w = bpy.data.worlds.new('W')
w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs[0].default_value = (.58, .64, .70, 1)
bg.inputs[1].default_value = 1.4
sc.world = w
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(45), math.radians(10), math.radians(-30)))
s = bpy.context.object
s.data.energy = 1.6
s.data.angle = math.radians(30)
try:
    sc.view_settings.view_transform = 'AgX'
except Exception:
    pass
# 1.75 m 人形尺
bpy.ops.mesh.primitive_cylinder_add(radius=.22, depth=1.75, location=(1.5, 1.6, .875))


def shot(n, loc, tgt, lens, res=(1536, 1024)):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.data.lens = lens
    c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = c
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = OUT + f'floor_{TAG}_{n}.png'
    bpy.ops.render.render(write_still=True)


shot('eye', (-.3, -3.4, 1.6), (0, .2, 0), 28)
shot('low', (-.8, -2.2, .45), (.2, .6, .05), 24)
shot('top', (0, -.01, 6.5), (0, 0, 0), 35, (1200, 1200))
