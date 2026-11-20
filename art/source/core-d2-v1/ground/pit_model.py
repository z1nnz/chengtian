# CO02 被挖的坑（獨立模型，z1nnz 11/21：坑另外建模；四周平坦、往下凹，不是凸起的土堆）
#   blender -b --factory-startup -P pit_model.py -- <tag> [norender]
#   原點＝坑中心，z=0＝周圍地面高度；模型外緣 4.5 m 處高度回到 0，鋪在平地上就接得起來
import bpy, bmesh, sys, math, random
import numpy as np
from mathutils import Vector, noise

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
TAG = argv[0] if argv else 'p1'
S_ = 'D:/chengtian/4-素材與快取/bark-sample/'
GT = 'D:/chengtian/4-素材與快取/polyhaven-ground/'
BK = 'D:/chengtian/4-素材與快取/polyhaven-bark/'
R = random.Random(4)
noise.seed_set(4)
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
RW, DEP, OUTR = 2.3, 1.35, 4.6     # 坑口半徑、深度、模型外緣


def nz(x, y, s, z=0.0):
    return noise.noise(Vector((x * s, y * s, z)))


def rim(a):
    """坑口半徑隨角度起伏（挖出來的坑不會是正圓）。"""
    return RW * (1 + .14 * nz(math.cos(a), math.sin(a), 1.4, 3.0) + .06 * nz(math.cos(a), math.sin(a), 3.5, 5.0))


def height(x, y):
    r = math.hypot(x, y)
    a = math.atan2(y, x)
    rw = rim(a)
    h = 0.0
    if r < rw:
        u = r / rw
        # 坑壁陡（鏟子挖的），坑底不平、有一塊塊鏟痕
        wall = 1 - u ** 4.5
        h = -DEP * wall
        h += .10 * nz(x, y, 1.6, 1.0) * wall + .05 * nz(x, y, 4.0, 2.0) * wall
        # 鏟痕：坑壁上一條條斜面
        h += .04 * math.sin(a * 9 + r * 3) * (1 - abs(u - .8) * 3) if .5 < u < 1 else 0
    else:
        # 坑口外：一圈薄薄的鬆土（最高 0.18 m，一側多），往外很快回到平地
        d = r - rw
        side = .5 + .5 * math.cos(a - 2.2)
        spill = math.exp(-(d / (.55 + .5 * side)) ** 2) * (.06 + .12 * side) * (.7 + .6 * (.5 + .5 * nz(x, y, 1.8, 7.0)))
        h = spill + .03 * nz(x, y, 5.0, 8.0) * math.exp(-d / 1.2)
        # 坑口邊緣一圈被踩實、略塌
        h -= .06 * math.exp(-(d / .12) ** 2)
    # 外緣淡出到 0
    f = max(0.0, min(1.0, (OUTR - r) / .8))
    return h * f


def soil(x, y):
    """泥土遮罩：1 = 裸土，0 = 林床腐葉。"""
    r = math.hypot(x, y)
    a = math.atan2(y, x)
    rw = rim(a)
    if r < rw:
        return 1.0
    side = .5 + .5 * math.cos(a - 2.2)
    reach = .5 + .9 * side + .25 * nz(x, y, 2.2, 9.0)
    return max(0.0, min(1.0, 1 - (r - rw - reach) / .5))


# ---------------- 地面網格（4 cm） ----------------
RES = .04
n = int(2 * OUTR / RES)
xs = np.linspace(-OUTR, OUTR, n + 1)
V, keep = [], []
for y in xs:
    for x in xs:
        V.append((x, y, height(x, y)))
F = []
for j in range(n):
    for i in range(n):
        cx, cy = xs[i] + RES / 2, xs[j] + RES / 2
        if math.hypot(cx, cy) > OUTR:
            continue
        a = j * (n + 1) + i
        F.append((a, a + 1, a + n + 2, a + n + 1))
me = bpy.data.meshes.new('CO02_Pit')
me.from_pydata(V, [], F)
for p in me.polygons:
    p.use_smooth = True
# 沒用到的頂點清掉
bm = bmesh.new()
bm.from_mesh(me)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
bm.to_mesh(me)
bm.free()
sm = np.array([soil(v.co.x, v.co.y) for v in me.vertices], np.float32)
wet = np.array([max(0.0, min(1.0, -v.co.z / DEP * 1.3)) for v in me.vertices], np.float32)
ca = me.color_attributes.new('Mask', 'FLOAT_COLOR', 'POINT')
ca.data.foreach_set('color', np.stack([sm, wet, np.zeros_like(sm), np.ones_like(sm)], 1).ravel())
pit = bpy.data.objects.new('CO02_Pit', me)
sc.collection.objects.link(pit)


# ---------------- 材質：林床腐葉 ↔ 泥土（坑底越濕越深） ----------------
def ground_material():
    m = bpy.data.materials.new('CO02_PitGround')
    m.use_nodes = True
    nt = m.node_tree
    b = next(x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED')
    tc = nt.nodes.new('ShaderNodeTexCoord')

    def img(fn, cs, s):
        mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (1 / s,) * 3
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = bpy.data.images.load(fn)
        t.image.colorspace_settings.name = cs
        t.projection, t.projection_blend = 'BOX', .35
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
        return t.outputs['Color']

    def mul(a, col):
        x = nt.nodes.new('ShaderNodeMixRGB')
        x.blend_type = 'MULTIPLY'
        x.inputs[0].default_value = 1
        nt.links.new(a, x.inputs[1])
        x.inputs[2].default_value = (*col, 1)
        return x.outputs[0]

    def mix(f, a, b_):
        x = nt.nodes.new('ShaderNodeMixRGB')
        nt.links.new(f, x.inputs[0])
        nt.links.new(a, x.inputs[1])
        nt.links.new(b_, x.inputs[2])
        return x.outputs[0]
    vc = nt.nodes.new('ShaderNodeVertexColor')
    vc.layer_name = 'Mask'
    sp = nt.nodes.new('ShaderNodeSeparateColor')
    nt.links.new(vc.outputs['Color'], sp.inputs[0])
    # 土與腐葉交界不規則
    nzz = nt.nodes.new('ShaderNodeTexNoise')
    nzz.inputs['Scale'].default_value = 2.5
    nzz.inputs['Detail'].default_value = 8
    nt.links.new(tc.outputs['Object'], nzz.inputs['Vector'])
    ma = nt.nodes.new('ShaderNodeMath')
    ma.operation = 'MULTIPLY_ADD'
    nt.links.new(nzz.outputs['Fac'], ma.inputs[0])
    ma.inputs[1].default_value = .8
    nt.links.new(sp.outputs[0], ma.inputs[2])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = .75, 1.1
    nt.links.new(ma.outputs[0], mr.inputs['Value'])
    leaf = mul(img(GT + 'forest_leaves_02_diffuse_2k.png', 'sRGB', 2.5), (.62, .62, .46))
    mud = mul(img(GT + 'brown_mud_02_diff_2k.png', 'sRGB', .9), (1.05, .72, .46))
    mudw = mul(mud, (.55, .5, .45))                         # 坑底濕泥較深
    mud2 = mix(sp.outputs[1], mud, mudw)
    col = mix(mr.outputs[0], leaf, mud2)
    nt.links.new(col, b.inputs['Base Color'])
    nl = img(GT + 'forest_leaves_02_nor_gl_2k.png', 'Non-Color', 2.5)
    nm_ = img(GT + 'brown_mud_02_nor_gl_2k.png', 'Non-Color', .9)
    nmix = mix(mr.outputs[0], nl, nm_)
    nmap = nt.nodes.new('ShaderNodeNormalMap')
    nmap.inputs['Strength'].default_value = 1.4
    nt.links.new(nmix, nmap.inputs['Color'])
    nt.links.new(nmap.outputs['Normal'], b.inputs['Normal'])
    rr = nt.nodes.new('ShaderNodeMapRange')
    nt.links.new(sp.outputs[1], rr.inputs['Value'])
    rr.inputs['To Min'].default_value, rr.inputs['To Max'].default_value = .8, .35
    nt.links.new(rr.outputs[0], b.inputs['Roughness'])
    return m


GM = ground_material()
me.materials.append(GM)

# 泥土顆粒的細凹凸：用 displace 修改器加一層小土塊感（只在土的地方）
tex = bpy.data.textures.new('PitClumps', 'VORONOI')
tex.noise_scale = .09
vg = pit.vertex_groups.new(name='soil')
for i, s in enumerate(sm):
    if s > .05:
        vg.add([i], float(s), 'REPLACE')
dm = pit.modifiers.new('Clumps', 'DISPLACE')
dm.texture = tex
dm.strength = .035
dm.vertex_group = 'soil'
dm.texture_coords = 'OBJECT'

# ---------------- 土塊、碎石、斷根、積水、落葉 ----------------
mud_mat = bpy.data.materials.new('CO02_Clod')
mud_mat.use_nodes = True
_nt = mud_mat.node_tree
_b = next(x for x in _nt.nodes if x.type == 'BSDF_PRINCIPLED')
_t = _nt.nodes.new('ShaderNodeTexImage')
_t.image = bpy.data.images.get('brown_mud_02_diff_2k.png') or bpy.data.images.load(GT + 'brown_mud_02_diff_2k.png')
_t.projection = 'BOX'
_tc = _nt.nodes.new('ShaderNodeTexCoord')
_mp = _nt.nodes.new('ShaderNodeMapping')
_mp.inputs['Scale'].default_value = (2.5, 2.5, 2.5)
_nt.links.new(_tc.outputs['Object'], _mp.inputs['Vector'])
_nt.links.new(_mp.outputs['Vector'], _t.inputs['Vector'])
_mx = _nt.nodes.new('ShaderNodeMixRGB')
_mx.blend_type = 'MULTIPLY'
_mx.inputs[0].default_value = 1
_mx.inputs[2].default_value = (.95, .65, .42, 1)
_nt.links.new(_t.outputs['Color'], _mx.inputs[1])
_nt.links.new(_mx.outputs[0], _b.inputs['Base Color'])
_b.inputs['Roughness'].default_value = .85

clods = bmesh.new()
for i in range(110):
    a = R.uniform(0, 6.283)
    side = .5 + .5 * math.cos(a - 2.2)
    if R.random() > .35 + .65 * side:
        continue
    r = rim(a) + R.uniform(-.1, 1.3)
    x, y = math.cos(a) * r, math.sin(a) * r
    rad = R.uniform(.04, .16)
    m_ = bmesh.ops.create_icosphere(clods, subdivisions=2, radius=rad)
    vs = m_['verts']
    sx, sy, sz = R.uniform(1, 1.7), R.uniform(.8, 1.3), R.uniform(.45, .7)
    rot = R.uniform(0, 6.283)
    for v in vs:
        p = v.co
        p.x *= sx; p.y *= sy; p.z *= sz
        p += Vector((nz(p.x + i, p.y, 9.0), nz(p.y, p.z + i, 9.0), nz(p.z, p.x + i, 9.0))) * rad * .35
        c_, s_ = math.cos(rot), math.sin(rot)
        v.co = Vector((p.x * c_ - p.y * s_ + x, p.x * s_ + p.y * c_ + y, p.z + height(x, y) + rad * .2))
cm = bpy.data.meshes.new('CO02_Clods')
clods.to_mesh(cm)
clods.free()
for p in cm.polygons:
    p.use_smooth = True
cm.materials.append(mud_mat)
co = bpy.data.objects.new('CO02_Clods', cm)
sc.collection.objects.link(co)

# 斷根：從坑壁伸出、被鏟斷的根（有斷面），粗細不一
bark = bpy.data.materials.new('CO02_RootBark')
bark.use_nodes = True
_nt = bark.node_tree
_b = next(x for x in _nt.nodes if x.type == 'BSDF_PRINCIPLED')
_t = _nt.nodes.new('ShaderNodeTexImage')
_t.image = bpy.data.images.load(BK + 'bark_brown_02_diff_2k.png')
_t.projection = 'BOX'
_tc = _nt.nodes.new('ShaderNodeTexCoord')
_mp = _nt.nodes.new('ShaderNodeMapping')
_mp.inputs['Scale'].default_value = (4, 4, 4)
_nt.links.new(_tc.outputs['Object'], _mp.inputs['Vector'])
_nt.links.new(_mp.outputs['Vector'], _t.inputs['Vector'])
_mx = _nt.nodes.new('ShaderNodeMixRGB')
_mx.blend_type = 'MULTIPLY'
_mx.inputs[0].default_value = 1
_mx.inputs[2].default_value = (.55, .42, .30, 1)
_nt.links.new(_t.outputs['Color'], _mx.inputs[1])
_nt.links.new(_mx.outputs[0], _b.inputs['Base Color'])
for i in range(14):
    a = R.uniform(0, 6.283)
    rw = rim(a)
    zz = -R.uniform(.15, .9) * DEP
    u = (1 - (-zz / DEP)) ** (1 / 4.5)
    p0 = Vector((math.cos(a) * rw * u * 1.08, math.sin(a) * rw * u * 1.08, zz))
    d = Vector((-math.cos(a) + R.uniform(-.4, .4), -math.sin(a) + R.uniform(-.4, .4), R.uniform(-.5, .3))).normalized()
    L = R.uniform(.25, .9)
    cu = bpy.data.curves.new(f'CO02_Root{i}', 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = R.uniform(.012, .05)
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    sp = cu.splines.new('NURBS')
    pts = [p0 - d * .2, p0 + d * L * .5 + Vector((0, 0, R.uniform(-.08, .06))), p0 + d * L]
    sp.points.add(len(pts) - 1)
    for j, pp in enumerate(pts):
        sp.points[j].co = (pp.x, pp.y, pp.z, 1)
        sp.points[j].radius = 1 - .35 * j / 2
    sp.use_endpoint_u = True
    cu.materials.append(bark)
    ro = bpy.data.objects.new(f'CO02_Root{i}', cu)
    sc.collection.objects.link(ro)

# 坑底積水：小而不規則
wm = bpy.data.materials.new('CO02_Water')
wm.use_nodes = True
wb = next(x for x in wm.node_tree.nodes if x.type == 'BSDF_PRINCIPLED')
wb.inputs['Base Color'].default_value = (.035, .028, .02, 1)
wb.inputs['Roughness'].default_value = .08
bw = bmesh.new()
cv = bw.verts.new((0, 0, 0))
ring = []
for k in range(36):
    a = k / 36 * 6.283
    rr = .5 * (1 + .3 * nz(math.cos(a), math.sin(a), 1.8, 11.0))
    ring.append(bw.verts.new((math.cos(a) * rr * 1.3 + .25, math.sin(a) * rr * .85 - .1, 0)))
for k in range(36):
    bw.faces.new((cv, ring[k], ring[(k + 1) % 36]))
wme = bpy.data.meshes.new('CO02_Water')
bw.to_mesh(wme)
bw.free()
wme.materials.append(wm)
wo = bpy.data.objects.new('CO02_Water', wme)
wo.location.z = -DEP + .10
sc.collection.objects.link(wo)

# 小石頭：從土裡翻出來的
stone = bpy.data.materials.new('CO02_Stone')
stone.use_nodes = True
_b = next(x for x in stone.node_tree.nodes if x.type == 'BSDF_PRINCIPLED')
_b.inputs['Base Color'].default_value = (.10, .095, .08, 1)
_b.inputs['Roughness'].default_value = .7
sb = bmesh.new()
for i in range(26):
    a = R.uniform(0, 6.283)
    r = rim(a) * R.uniform(.3, 1.4)
    x, y = math.cos(a) * r, math.sin(a) * r
    rad = R.uniform(.03, .1)
    m_ = bmesh.ops.create_icosphere(sb, subdivisions=1, radius=rad)
    for v in m_['verts']:
        v.co = Vector((v.co.x * 1.3 + x, v.co.y + y, v.co.z * .6 + height(x, y)))
sme = bpy.data.meshes.new('CO02_Stones')
sb.to_mesh(sme)
sb.free()
sme.materials.append(stone)
so = bpy.data.objects.new('CO02_Stones', sme)
sc.collection.objects.link(so)
print('PIT_TRIS', sum(len(p.vertices) - 2 for p in me.polygons))

bpy.ops.wm.save_as_mainfile(filepath=S_ + f'pit_lib.blend')
if 'norender' in argv:
    raise SystemExit

# ---------------- 預覽 ----------------
bpy.ops.mesh.primitive_grid_add(x_subdivisions=80, y_subdivisions=80, size=40, location=(0, 0, -.002))
pl = bpy.context.object
_bm = bmesh.new()
_bm.from_mesh(pl.data)
bmesh.ops.delete(_bm, geom=[f_ for f_ in _bm.faces if f_.calc_center_median().length < OUTR - .3], context='FACES')
_bm.to_mesh(pl.data)
_bm.free()
pl.data.materials.append(GM)
w = bpy.data.worlds.new('W')
sc.world = w
w.use_nodes = True
bg = next(x for x in w.node_tree.nodes if x.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (.6, .64, .68, 1)
bg.inputs['Strength'].default_value = 1.6
sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN'))
sun.data.energy = 2.5
sun.rotation_euler = (math.radians(50), 0, math.radians(140))
sc.collection.objects.link(sun)
sc.render.engine = 'CYCLES'
try:
    pr = bpy.context.preferences.addons['cycles'].preferences
    pr.compute_device_type = 'OPTIX'
    pr.get_devices()
    for d in pr.devices:
        d.use = True
    sc.cycles.device = 'GPU'
except Exception:
    pass
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'AgX'
sc.render.resolution_x, sc.render.resolution_y = 1500, 1000
for nm_, loc, tgt, lens in (('side', (0, -7.5, 2.4), (0, 0, -.5), 28), ('top', (.01, -2.5, 9), (0, 0, -.6), 28)):
    cd = bpy.data.cameras.new(nm_)
    cd.lens = lens
    c = bpy.data.objects.new(nm_, cd)
    sc.collection.objects.link(c)
    c.location = loc
    c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = c
    sc.render.filepath = S_ + f'pit_{TAG}_{nm_}.png'
    bpy.ops.render.render(write_still=True)
