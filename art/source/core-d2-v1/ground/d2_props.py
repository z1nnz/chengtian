# D2 前景大件：AL02 石砌祭壇（重做）、RK01 大苔石 A–E
#   blender -b --factory-startup -P d2_props.py -- <tag> [norender]
#   存 props_lib.blend（物件名 AL02_Altar*、RK01_Boulder_*），原點在底部中心、z=0 是地面
import bpy, bmesh, sys, math, random
from mathutils import Vector, noise

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
TAG = argv[0] if argv else 'p1'
S_ = 'D:/chengtian/4-素材與快取/bark-sample/'
GT = 'D:/chengtian/4-素材與快取/polyhaven-ground/'
R = random.Random(8)
noise.seed_set(8)
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene


def stone_material(name, base=(1, 1, 1), moss=.55):
    """掃描苔石貼圖（三面投影）＋朝上的面長苔、凹處暗。"""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = next(x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (.7, .7, .7)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])

    def im(fn, cs):
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = bpy.data.images.load(GT + fn)
        t.image.colorspace_settings.name = cs
        t.projection, t.projection_blend = 'BOX', .3
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
        return t.outputs['Color']
    d = im('mossy_rock_diff_2k.png', 'sRGB')
    hs = nt.nodes.new('ShaderNodeHueSaturation')   # 掃描貼圖本身偏綠 → 去綠，石頭本色是灰褐
    hs.inputs['Saturation'].default_value = .35
    nt.links.new(d, hs.inputs['Color'])
    tint = nt.nodes.new('ShaderNodeMixRGB')
    tint.blend_type = 'MULTIPLY'
    tint.inputs[0].default_value = 1
    tint.inputs[2].default_value = (*base, 1)
    nt.links.new(hs.outputs[0], tint.inputs[1])
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    sp = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['Normal'], sp.inputs[0])
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 1.6
    nz.inputs['Detail'].default_value = 8
    nt.links.new(geo.outputs['Position'], nz.inputs['Vector'])
    ma = nt.nodes.new('ShaderNodeMath')
    ma.operation = 'MULTIPLY_ADD'
    nt.links.new(sp.outputs['Z'], ma.inputs[0])
    ma.inputs[1].default_value = moss
    nt.links.new(nz.outputs['Fac'], ma.inputs[2])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = .78, .95
    nt.links.new(ma.outputs[0], mr.inputs['Value'])
    mn = nt.nodes.new('ShaderNodeTexNoise')
    mn.inputs['Scale'].default_value = 40
    nt.links.new(geo.outputs['Position'], mn.inputs['Vector'])
    mc = nt.nodes.new('ShaderNodeValToRGB')
    mc.color_ramp.elements[0].color = (.035, .05, .014, 1)
    mc.color_ramp.elements[1].color = (.13, .16, .05, 1)
    nt.links.new(mn.outputs['Fac'], mc.inputs[0])
    mx = nt.nodes.new('ShaderNodeMixRGB')
    nt.links.new(mr.outputs[0], mx.inputs[0])
    nt.links.new(tint.outputs[0], mx.inputs[1])
    nt.links.new(mc.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], b.inputs['Base Color'])
    nm = nt.nodes.new('ShaderNodeNormalMap')
    nt.links.new(im('mossy_rock_nor_gl_2k.png', 'Non-Color'), nm.inputs['Color'])
    nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    nt.links.new(im('mossy_rock_rough_2k.png', 'Non-Color'), b.inputs['Roughness'])
    return m


def rough_block(bm, cx, cy, cz, sx, sy, sz, wear=.06, seed=0):
    """一塊風化石塊：細分的方塊，邊角磨圓、表面起伏、略歪。"""
    r = bmesh.ops.create_cube(bm, size=1.0)
    vs = r['verts']
    bmesh.ops.subdivide_edges(bm, edges=list({e for v in vs for e in v.link_edges}), cuts=4, use_grid_fill=True)
    vs = list({v for v in bm.verts if v.tag is False})
    return r


def make_block(name, sx, sy, sz, wear, seed, mat):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)   # ±1，乘上半寬就是實際大小
    bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts), offset=.22, segments=3, affect='EDGES')
    bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=2, use_grid_fill=True)
    rr = random.Random(seed)
    tilt = (rr.uniform(-.02, .02), rr.uniform(-.02, .02))
    for v in bm.verts:
        p = v.co.copy()
        n = noise.noise(Vector((p.x * 2.1 + seed, p.y * 2.1, p.z * 2.1))) * wear * 1.4 + noise.noise(Vector((p.x * 6 + seed, p.y * 6, p.z * 6))) * wear * .5
        q = p.normalized() * n
        v.co = Vector((p.x * sx, p.y * sy, p.z * sz)) + Vector((q.x * sx, q.y * sy, q.z * sz)) * .6
        v.co.z += v.co.x * tilt[0] + v.co.y * tilt[1]
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    return o


ALT_MAT = stone_material('AL02_Stone', (.52, .50, .45), .55)
# ---------------- AL02 祭壇：三層退台，每層由一塊塊石塊砌成，正面中央一道三階石階 ----------------
parts = []
TIERS = [(7.2, 5.2, .45), (5.6, 3.9, .40), (4.0, 2.8, .38)]   # 寬、深、層高
z = 0.0
k = 0
for ti, (W, D, H) in enumerate(TIERS):
    # 外圈一圈石塊（中間用一塊大填心）
    bw = 1.1 - ti * .12
    nx = max(2, round(W / bw))
    ny = max(2, round(D / bw))
    for side in range(4):
        n_ = nx if side % 2 == 0 else ny
        L = W if side % 2 == 0 else D
        for i in range(n_):
            t = (i + .5) / n_ - .5
            if side == 0:
                x, y = t * W, -D / 2 + .35
            elif side == 1:
                x, y = W / 2 - .35, t * D
            elif side == 2:
                x, y = t * W, D / 2 - .35
            else:
                x, y = -W / 2 + .35, t * D
            if side == 0 and ti == 0 and abs(x) < .9:
                continue    # 正面中央留給石階
            sx = (L / n_ * .5 - .02) if side % 2 == 0 else .36
            sy = .36 if side % 2 == 0 else (L / n_ * .5 - .02)
            o = make_block(f'AL02_Altar_b{k}', sx, sy, H / 2 * R.uniform(.95, 1.06), .07, k * 7 + 3, ALT_MAT)
            o.location = (x + R.uniform(-.03, .03), y + R.uniform(-.03, .03), z + H / 2)
            o.rotation_euler.z = R.uniform(-.03, .03)
            parts.append(o)
            k += 1
    core = make_block(f'AL02_Altar_core{ti}', W / 2 - .7, D / 2 - .7, H / 2, .03, ti * 13, ALT_MAT)
    core.location = (0, 0, z + H / 2 - .01)
    parts.append(core)
    z += H
# 頂面：一塊大石板，中央一圈圓形石井（設定圖頂上的圓）
top = make_block('AL02_Altar_top', 1.9, 1.35, .09, .03, 91, ALT_MAT)
top.location = (0, 0, z + .08)
parts.append(top)
for i in range(12):
    a = i / 12 * 6.283
    o = make_block(f'AL02_Altar_ring{i}', .24, .14, .12, .05, 100 + i, ALT_MAT)
    o.location = (math.cos(a) * .75, math.sin(a) * .75, z + .27)
    o.rotation_euler.z = a + math.pi / 2
    parts.append(o)
# 正面石階：三階，每階兩三塊
for s in range(3):
    for j, (dx, w) in enumerate(((-.55, .42), (0, .36), (.55, .42))):
        o = make_block(f'AL02_Altar_step{s}_{j}', w, .26, .14 + s * .0, .06, 200 + s * 5 + j, ALT_MAT)
        o.location = (dx * 1.2, -TIERS[0][1] / 2 - .55 + s * .45 + .1, .14 + s * .28)
        parts.append(o)
# 幾塊崩落的石塊散在旁邊
for i in range(6):
    a = R.uniform(0, 6.283)
    rr = R.uniform(4.2, 5.2)
    o = make_block(f'AL02_Altar_fall{i}', R.uniform(.25, .4), R.uniform(.2, .32), R.uniform(.12, .2), .1, 300 + i, ALT_MAT)
    o.location = (math.cos(a) * rr * .9, math.sin(a) * rr * .7, .08)
    o.rotation_euler = (R.uniform(-.3, .3), R.uniform(-.3, .3), R.uniform(0, 6.28))
    parts.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
alt = bpy.context.object
alt.name = 'AL02_Altar'
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
print('ALTAR tris', sum(len(p.vertices) - 2 for p in alt.data.polygons), 'height', round(z + .2, 2))

# ---------------- RK01 大苔石 A–E ----------------
RK_MAT = stone_material('RK01_Stone', (.55, .56, .52), .45)
# 大石頭不能用碎石堆的掃描貼圖（會變一堆碎石）：底色、法線改成整塊岩面的雜訊
_nt = RK_MAT.node_tree
_b = next(x for x in _nt.nodes if x.type == 'BSDF_PRINCIPLED')
_geo = next(x for x in _nt.nodes if x.type == 'NEW_GEOMETRY')
_tint = [x for x in _nt.nodes if x.type == 'MIX_RGB' and x.blend_type == 'MULTIPLY'][0]
_n1 = _nt.nodes.new('ShaderNodeTexNoise')
_n1.inputs['Scale'].default_value = 3.0
_n1.inputs['Detail'].default_value = 10
_n1.inputs['Roughness'].default_value = .6
_nt.links.new(_geo.outputs['Position'], _n1.inputs['Vector'])
_cr = _nt.nodes.new('ShaderNodeValToRGB')
_cr.color_ramp.elements[0].color = (.07, .065, .055, 1)
_cr.color_ramp.elements[1].color = (.22, .21, .18, 1)
_nt.links.new(_n1.outputs['Fac'], _cr.inputs[0])
_nt.links.new(_cr.outputs[0], _tint.inputs[1])
_bp = _nt.nodes.new('ShaderNodeBump')
_bp.inputs['Strength'].default_value = .8
_bp.inputs['Distance'].default_value = .03
_nt.links.new(_n1.outputs['Fac'], _bp.inputs['Height'])
_nt.links.new(_bp.outputs['Normal'], _b.inputs['Normal'])
_ln = _nt.nodes.new('ShaderNodeTexNoise')   # 灰白地衣斑
_ln.inputs['Scale'].default_value = 6
_ln.inputs['Detail'].default_value = 8
_nt.links.new(_geo.outputs['Position'], _ln.inputs['Vector'])
_lr = _nt.nodes.new('ShaderNodeMapRange')
_lr.inputs['From Min'].default_value, _lr.inputs['From Max'].default_value = .57, .7
_lr.inputs['To Max'].default_value = .6
_nt.links.new(_ln.outputs['Fac'], _lr.inputs['Value'])
_lm = _nt.nodes.new('ShaderNodeMixRGB')
_lm.inputs[2].default_value = (.27, .28, .25, 1)
_nt.links.new(_lr.outputs[0], _lm.inputs[0])
_src = _b.inputs['Base Color'].links[0].from_socket
_nt.links.new(_src, _lm.inputs[1])
_nt.links.new(_lm.outputs[0], _b.inputs['Base Color'])
_b.inputs['Roughness'].default_value = .85
for _l in list(_b.inputs['Roughness'].links):
    _nt.links.remove(_l)
SIZES = [('A', 2.4, 1.6), ('B', 1.8, 1.2), ('C', 1.3, .9), ('D', .9, .55), ('E', 3.0, 1.4)]
for i, (nm, w, h) in enumerate(SIZES):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=5, radius=1.0)
    rr = random.Random(500 + i)
    off = Vector((rr.uniform(-50, 50), rr.uniform(-50, 50), 0))
    kx, ky = rr.uniform(.9, 1.1), rr.uniform(.65, .85)   # 每顆石頭一個比例（之前誤放在每個頂點裡，石頭變成碎石堆）
    for v in bm.verts:
        p = v.co.copy()
        n = noise.noise(p * .9 + off) * .2 + noise.noise(p * 2.0 + off * 2) * .07 + noise.noise(p * 5 + off) * .02
        p = p * (1 + n)
        # 扁、底平，一側較陡（風化石）
        p.x *= w / 2 * kx
        p.y *= w / 2 * ky
        p.z = p.z * h * .62 + h * .12   # 下半埋進土裡（場景再往下壓）
        v.co = p
    # 削幾刀：風化石有幾個平切面和稜角（不是圓饅頭）
    for c_ in range(rr.randint(3, 5)):
        a_ = rr.uniform(0, 6.283)
        nrm_ = Vector((math.cos(a_), math.sin(a_), rr.uniform(-.1, .9))).normalized()
        far = max(v.co.dot(nrm_) for v in bm.verts)
        co_ = nrm_ * far * rr.uniform(.72, .88)
        res = bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), plane_co=co_, plane_no=nrm_, clear_outer=True)
        edges = [e for e in res['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
        if edges:
            try:
                bmesh.ops.holes_fill(bm, edges=edges, sides=0)
            except Exception:
                pass
    bmesh.ops.triangulate(bm, faces=[f_ for f_ in bm.faces if len(f_.verts) > 4])
    me = bpy.data.meshes.new(f'RK01_Boulder_{nm}')
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(RK_MAT)
    o = bpy.data.objects.new(f'RK01_Boulder_{nm}', me)
    sc.collection.objects.link(o)
    o.location = (-6 + i * 3.2, 6, 0)
    print('BOULDER', nm, len(me.polygons))

bpy.ops.wm.save_as_mainfile(filepath=S_ + 'props_lib.blend')
if 'norender' in argv:
    raise SystemExit
for o in bpy.data.objects:
    if o.name.startswith('RK01'):
        o.location.x -= 0
bpy.ops.mesh.primitive_plane_add(size=60)
g = bpy.context.object
gm = bpy.data.materials.new('g')
gm.use_nodes = True
next(n for n in gm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.08, .065, .045, 1)
g.data.materials.append(gm)
w = bpy.data.worlds.new('W')
sc.world = w
w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND').inputs['Strength'].default_value = 1.6
sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN'))
sun.data.energy = 2.5
sun.rotation_euler = (.9, 0, .7)
sc.collection.objects.link(sun)
sc.render.engine = 'CYCLES'
sc.cycles.samples = 48
sc.cycles.use_denoising = True
sc.cycles.device = 'GPU'
sc.view_settings.view_transform = 'AgX'
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
cd = bpy.data.cameras.new('c')
cd.lens = 30
c = bpy.data.objects.new('c', cd)
sc.collection.objects.link(c)
c.location = (5.5, -13, 4.5)
c.rotation_euler = (Vector((1.5, 2, .8)) - c.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = c
sc.render.filepath = S_ + f'props_{TAG}.png'
bpy.ops.render.render(write_still=True)
