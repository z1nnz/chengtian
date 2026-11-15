# D2 神木：樹幹下段 + 板根 試做（高模，渲染用；之後烘焙成遊戲用低模）
import bpy, bmesh, math, sys, random, numpy as np
from pathlib import Path
from mathutils import Vector, noise

HERE = Path(__file__).resolve().parent
TEX = str(HERE / 'tex') + '/'
OUT = str(HERE.parents[2] / 'previews' / 'core-d2-v1' / 'GT01_GodTree') + '/'
SET = 'bark_brown_02'
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
TAG = ARGS[0] if ARGS else 'v1'
QUICK = 'quick' in ARGS
TILE = 2.6          # 一張掃描圖覆蓋的實際尺寸 (m)
AMP = 0.16          # 掃描凹凸做進幾何的深度 (m)
STEP = 0.55 if 'game' in ARGS else (0.10 if QUICK else 0.05)
bpy.ops.wm.read_factory_settings(use_empty=True)


def img(n, cs='Non-Color'):
    i = bpy.data.images.load(TEX + f'{SET}_{n}_2k.png')
    i.colorspace_settings.name = cs
    return i


disp = img('disp')
W, H = disp.size
DP = np.array(disp.pixels[:], dtype=np.float32).reshape(H, W, -1)[:, :, 0]


def sdisp(u, v):
    x = (u % 1) * W
    y = (v % 1) * H
    x0 = int(x) % W
    y0 = int(y) % H
    x1 = (x0 + 1) % W
    y1 = (y0 + 1) % H
    fx = x - int(x)
    fy = y - int(y)
    return (DP[y0, x0] * (1 - fx) + DP[y0, x1] * fx) * (1 - fy) + (DP[y1, x0] * (1 - fx) + DP[y1, x1] * fx) * fy


def fb(p, s, o=4):
    return noise.fractal(Vector(p) * s, 1.0, 2.0, o, noise_basis='PERLIN_ORIGINAL')


def cr(p0, p1, p2, p3, t):
    return .5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)


def resample(pts, step):
    P = [Vector(p) for p in pts]
    n = len(P)
    spl = []
    for i in range(n - 1):
        a, b, c, d = P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, n - 1)]
        for k in range(32):
            spl.append(cr(a, b, c, d, k / 32))
    spl.append(P[-1])
    L = [0]
    for i in range(1, len(spl)):
        L.append(L[-1] + (spl[i] - spl[i - 1]).length)
    tot = L[-1]
    NV = max(2, int(tot / step))
    out = []
    j = 0
    for k in range(NV + 1):
        s = tot * k / NV
        while j < len(L) - 2 and L[j + 1] < s:
            j += 1
        f = (s - L[j]) / max(L[j + 1] - L[j], 1e-6)
        out.append((spl[j].lerp(spl[j + 1], f), s))
    return out, tot


def tube(name, pts, radius, flat, seed, rib=.22, twist=.12, NU=None, up_axis=None, cap_moss=True, extra=None, rpos=None, fpos=None):
    """radius(t), flat(t): t 0..1 along path. flat = 垂直/水平 比例 (>1 是立起來的板根)."""
    rings, tot = resample(pts, STEP)
    NV = len(rings) - 1
    rmax = max((rpos(rings[k][0], k / NV) if rpos else radius(k / NV)) for k in range(0, NV + 1, max(1, NV // 20)))
    if NU is None:
        NU = int(min(64, max(16, 2 * math.pi * rmax * 1.7))) if 'game' in ARGS else int(min(640, max(48, 2 * math.pi * rmax * max(1.0, (fpos(rings[0][0], 0) if fpos else flat(0))) / STEP * .8)))
    rep = max(1, round(2 * math.pi * rmax * .8 / TILE))
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new('UV')
    col = bm.loops.layers.color.new('Mask')
    V, UVs, M = [], [], []
    for k, (c, s) in enumerate(rings):
        t = k / NV
        a = rings[min(k + 1, NV)][0] - rings[max(k - 1, 0)][0]
        a.normalize()
        ref = Vector((0, 0, 1)) if abs(a.z) < .9 else Vector((1, 0, 0))
        side = a.cross(ref).normalized()
        nu = side.cross(a).normalized()
        r = rpos(c, t) if rpos else radius(t)
        fl = fpos(c, t) if fpos else flat(t)
        tw = s * twist + seed
        row, ruv, rm = [], [], []
        for i in range(NU):
            th = 2 * math.pi * i / NU
            # 大尺度：順著根扭轉的粗稜（樹皮下的木纖維束）
            r1 = fb((math.cos(th + tw) * 2.0, math.sin(th + tw) * 2.0, s * .10 + seed), 1.0, 3)
            r2 = abs(fb((math.cos(th + tw * 1.4) * 4.5, math.sin(th + tw * 1.4) * 4.5, s * .22 + seed * 3), 1.0, 2))
            lump = fb((c.x * .35, c.y * .35 + th * .3, c.z * .35 + seed), 1.0, 2)
            rr = r * (1 + (rib * r1 - rib * .8 * r2) / fl ** 1.5 + .08 * lump)
            if extra is not None:
                dv = side * math.cos(th) + nu * math.sin(th)
                rr += extra(math.atan2(dv.y, dv.x), c.z)
            u = i / NU * rep
            v = s / TILE
            d = sdisp(u, v) - .5
            rr += d * AMP * min(1.0, r / .4 + .3)
            d3 = side * math.cos(th) * rr + nu * math.sin(th) * rr * fl
            p = c + d3
            nrm = (side * math.cos(th) * fl + nu * math.sin(th)).normalized()
            mo = nrm.z * .55 + fb(p, .45, 3) * .65 + fb(p, 2.5, 3) * .30 - d * .5 - r2 * .25
            mo = max(0, min(1, (mo - .50) / .20))
            mo = mo * mo * (3 - 2 * mo)
            if cap_moss:
                p += nrm * mo * .02
            row.append(bm.verts.new(p))
            ruv.append((u, v))
            rm.append((mo, max(0, min(1, d * 2 + .5)), max(0, min(1, r2)), 1))
        V.append(row)
        UVs.append(ruv)
        M.append(rm)
    for k in range(NV):
        for i in range(NU):
            i2 = (i + 1) % NU
            f = bm.faces.new((V[k][i], V[k][i2], V[k + 1][i2], V[k + 1][i]))
            for lp, (kk, ii, wrap) in zip(f.loops, [(k, i, 0), (k, i2, i2 == 0), (k + 1, i2, i2 == 0), (k + 1, i, 0)]):
                u, v = UVs[kk][ii]
                lp[uvl].uv = (rep if wrap else u, v)
                lp[col] = M[kk][ii]
            f.smooth = True
    if 'game' in ARGS:
        # Close every game-mesh tube; most caps are buried inside the trunk or soil.
        for row, center, reverse in ((V[0], rings[0][0], True), (V[-1], rings[-1][0], False)):
            mid = bm.verts.new(center)
            for i in range(NU):
                j = (i + 1) % NU
                tri = (row[j], row[i], mid) if reverse else (row[i], row[j], mid)
                face = bm.faces.new(tri)
                for loop, uv in zip(face.loops, ((.4, .4), (.6, .4), (.5, .6))):
                    loop[uvl].uv = uv
                    loop[col] = (0, .5, 0, 1)
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


# ---------------- 材質：掃描樹皮＋灰化＋地衣＋苔 ----------------
def bark_material():
    m = bpy.data.materials.new('GodTreeBark')
    m.use_nodes = True
    N, Lk = m.node_tree.nodes, m.node_tree.links
    b = next(n for n in N if n.type == 'BSDF_PRINCIPLED')

    def tx(n, cs='Non-Color'):
        t = N.new('ShaderNodeTexImage')
        t.image = img(n, cs)
        return t

    def ramp(p0, p1, c0=None, c1=None):
        r = N.new('ShaderNodeValToRGB')
        e = r.color_ramp.elements
        e[0].position, e[1].position = p0, p1
        if c0:
            e[0].color = c0
        if c1:
            e[1].color = c1
        return r

    def mix(kind='MIX', fac=None):
        x = N.new('ShaderNodeMixRGB')
        x.blend_type = kind
        if fac is not None:
            x.inputs[0].default_value = fac
        return x

    dif, nor, rgh, ao = tx('diff', 'sRGB'), tx('nor_gl'), tx('rough'), tx('ao')
    vc = N.new('ShaderNodeVertexColor')
    vc.layer_name = 'Mask'
    sep = N.new('ShaderNodeSeparateColor')
    Lk.new(vc.outputs['Color'], sep.inputs[0])
    hsv = N.new('ShaderNodeHueSaturation')
    hsv.inputs['Saturation'].default_value = .55
    hsv.inputs['Value'].default_value = 1.0
    Lk.new(dif.outputs[0], hsv.inputs['Color'])
    tint = mix('MULTIPLY', 1.0)
    tint.inputs[2].default_value = (1.0, .94, .86, 1)
    Lk.new(hsv.outputs[0], tint.inputs[1])
    aom = mix('MULTIPLY', .9)
    Lk.new(tint.outputs[0], aom.inputs[1])
    Lk.new(ao.outputs[0], aom.inputs[2])
    # 裂溝更深更暗（幾何凹處 G 通道低）
    crev = ramp(.15, .55, (.35, .35, .35, 1), (1, 1, 1, 1))
    Lk.new(sep.outputs[1], crev.inputs[0])
    cm = mix('MULTIPLY', 1.0)
    Lk.new(aom.outputs[0], cm.inputs[1])
    Lk.new(crev.outputs[0], cm.inputs[2])
    # 地衣：灰白斑點，長在凸起處
    nz = N.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 7
    nz.inputs['Detail'].default_value = 8
    lr = ramp(.60, .66)
    Lk.new(nz.outputs[0], lr.inputs[0])
    lm = N.new('ShaderNodeMath')
    lm.operation = 'MULTIPLY'
    Lk.new(lr.outputs[0], lm.inputs[0])
    Lk.new(sep.outputs[1], lm.inputs[1])
    lmx = mix()
    lmx.inputs[2].default_value = (.36, .39, .36, 1)
    Lk.new(lm.outputs[0], lmx.inputs[0])
    Lk.new(cm.outputs[0], lmx.inputs[1])
    # 苔
    mn = N.new('ShaderNodeTexNoise')
    mn.inputs['Scale'].default_value = 25
    mn.inputs['Detail'].default_value = 10
    mc = ramp(.3, .75, (.014, .020, .007, 1), (.055, .068, .022, 1))
    Lk.new(mn.outputs[0], mc.inputs[0])
    mr = ramp(.40, .62)
    Lk.new(sep.outputs[0], mr.inputs[0])
    mx = mix()
    Lk.new(mr.outputs[0], mx.inputs[0])
    Lk.new(lmx.outputs[0], mx.inputs[1])
    Lk.new(mc.outputs[0], mx.inputs[2])
    Lk.new(mx.outputs[0], b.inputs['Base Color'])
    nm = N.new('ShaderNodeNormalMap')
    nm.inputs['Strength'].default_value = 1.5
    Lk.new(nor.outputs[0], nm.inputs['Color'])
    bp = N.new('ShaderNodeBump')
    bp.inputs['Strength'].default_value = .7
    bp.inputs['Distance'].default_value = .015
    mb = N.new('ShaderNodeMath')
    mb.operation = 'MULTIPLY'
    Lk.new(mn.outputs[0], mb.inputs[0])
    Lk.new(mr.outputs[0], mb.inputs[1])
    Lk.new(mb.outputs[0], bp.inputs['Height'])
    Lk.new(nm.outputs[0], bp.inputs['Normal'])
    Lk.new(bp.outputs[0], b.inputs['Normal'])
    rmx = mix()
    rmx.inputs[2].default_value = (.95, .95, .95, 1)
    Lk.new(mr.outputs[0], rmx.inputs[0])
    Lk.new(rgh.outputs[0], rmx.inputs[1])
    Lk.new(rmx.outputs[0], b.inputs['Roughness'])
    return m


MAT = bark_material()
R = random.Random(7)
objs = []

def gh(x, y):
    rr = math.hypot(x, y)
    return fb((x, y, 0), .05, 3) * .7 + fb((x, y, 1), .5, 3) * .08 + 1.6 * max(0, 1 - rr / 16) ** 1.5


# ---------------- 樹幹（底徑約 10 m，只做到 22 m 高）----------------
TR = 6.5
angles = [5, 24, 47, 66, 94, 113, 135, 158, 186, 205, 230, 252, 279, 297, 320, 342]
ROOTS = []
for n, a0 in enumerate(angles):
    ROOTS.append(dict(a=math.radians(a0 + R.uniform(-7, 7)), L=TR + R.uniform(18, 32), thick=R.choice([R.uniform(2.2, 3.4), R.uniform(1.1, 1.9)]),
                      wig=R.uniform(.8, 2.0), arch=R.choice([.3, .9, 1.6, 2.4]), seed=10 + n * 3.1))


def lobes(phi, z):
    e = 0.0
    for rt in ROOTS:
        d = (phi - rt['a'] + math.pi) % (2 * math.pi) - math.pi
        amp = rt['thick'] * 2.4 * max(0, 1 - max(0, z) / 11.0) ** 1.5
        d += math.sin(z * .45 + rt['seed']) * .12 * min(1, max(0, z) / 3)
        e += amp * math.exp(-(d / .17) ** 2)
    return e


trunk_pts = [(0, 0, -1.0), (0.3, 0.1, 6), (.9, -.4, 14), (1.8, -.3, 22), (2.4, .6, 32)]
objs.append(tube('Trunk', trunk_pts,
                 radius=lambda t: TR * (1.0 - .16 * min(1, t * 2.0)) + 1.8 * max(0, .22 - t) ** 1.5 * 10,
                 flat=lambda t: 1.0, seed=3.0, rib=.20, twist=.06, extra=lobes))


def snake_root(name, a, L, thick, z0, seed, wig=1.0, arch=0.0, start=0.0, origin=None, plank=True):
    o = origin if origin is not None else Vector((0, 0, 0))
    dirv = Vector((math.cos(a), math.sin(a), 0))
    perp = Vector((-dirv.y, dirv.x, 0))
    N = 12
    rad = lambda t: thick * (1.0 - .9 * t ** .6) + .06
    fl = (lambda t: 1.0 + .9 * max(0, 1 - t / .25) ** 2) if plank else (lambda t: 1.0)
    pts = []
    for k in range(N + 1):
        t = k / N
        dd = start + L * t
        ww = (math.sin(t * 5.0 + seed) * (.2 + t) + fb((seed, t * 3, 0), 1, 2)) * wig * min(1, t * 4)
        p = o + dirv * dd + perp * ww
        g = gh(p.x, p.y)
        hump = arch * math.sin(math.pi * min(1, max(0, (t - .2) / .45))) * (t < .65)
        zs = g + rad(t) * fl(t) * .25 + hump
        if z0 is not None and t < .22:
            w = (t / .22) ** 1.4
            zs = z0 * (1 - w) + zs * w
        if t > .8:
            zs -= rad(t) * 2.4 * ((t - .8) / .2) ** 1.3
        pts.append((p.x, p.y, zs))
    return tube(name, pts, radius=rad, flat=fl, seed=seed, rib=.24, twist=.07)


for n, rt in enumerate(ROOTS):
    a, L, thick = rt['a'], rt['L'], rt['thick']
    objs.append(snake_root(f'Root{n}', a, L, thick, z0=R.uniform(4.0, 7.0), seed=rt['seed'],
                           wig=rt['wig'], arch=rt['arch'], start=TR * .4))
    dirv = Vector((math.cos(a), math.sin(a), 0))
    for f in range(R.choice([1, 2, 2])):
        st = TR + (L - TR) * R.uniform(.2, .5)
        fa = a + R.choice([-1, 1]) * math.radians(R.uniform(25, 50))
        base = dirv * st
        objs.append(snake_root(f'Root{n}_f{f}', fa, R.uniform(5, 10), thick * R.uniform(.3, .42), z0=None,
                               seed=50 + n * 2.3 + f, wig=.7, start=0, origin=base, plank=False))
for n in range(16):
    a = R.uniform(0, 2 * math.pi)
    objs.append(snake_root(f'Small{n}', a, R.uniform(6, 12), R.uniform(.16, .30), z0=None, seed=90 + n, wig=1.2,
                           start=TR + R.uniform(1.5, 4), plank=False))

for o in objs:
    o.data.materials.append(MAT)
print('TRIS', sum(len(o.data.polygons) * 2 for o in objs))

# ---------------- 地面：濕泥起伏 ----------------
bpy.ops.mesh.primitive_grid_add(x_subdivisions=400, y_subdivisions=400, size=130)
g = bpy.context.object
for v in g.data.vertices:
    p = v.co
    rr = math.hypot(p.x, p.y)
    v.co.z = gh(p.x, p.y)
gm = bpy.data.materials.new('Mud')
gm.use_nodes = True
GN, GL = gm.node_tree.nodes, gm.node_tree.links
gb = next(n for n in GN if n.type == 'BSDF_PRINCIPLED')
gn = GN.new('ShaderNodeTexNoise')
gn.inputs['Scale'].default_value = 3
gn.inputs['Detail'].default_value = 10
gr = GN.new('ShaderNodeValToRGB')
gr.color_ramp.elements[0].color = (.030, .022, .016, 1)
gr.color_ramp.elements[1].color = (.075, .060, .040, 1)
GL.new(gn.outputs[0], gr.inputs[0])
GL.new(gr.outputs[0], gb.inputs['Base Color'])
gb.inputs['Roughness'].default_value = .75
g.data.materials.append(gm)
for pol in g.data.polygons:
    pol.use_smooth = True

# ---------------- 燈光：陰天、冷灰、霧 ----------------
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 48 if QUICK else 128
sc.cycles.use_denoising = True
try:
    pr = bpy.context.preferences.addons['cycles'].preferences
    pr.compute_device_type = 'OPTIX'
    pr.get_devices()
    for d in pr.devices:
        d.use = True
    sc.cycles.device = 'GPU'
except Exception as e:
    print('gpu', e)
w = bpy.data.worlds.new('W')
w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs[0].default_value = (.58, .64, .70, 1)
bg.inputs[1].default_value = 1.6
# 霧：限定範圍的體積盒（無限世界霧會把太陽光吃光）
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 14))
fog = bpy.context.object
fog.scale = (160, 160, 50)
fm = bpy.data.materials.new('Fog')
fm.use_nodes = True
FN = fm.node_tree.nodes
for nd in list(FN):
    if nd.type == 'BSDF_PRINCIPLED':
        FN.remove(nd)
vol = FN.new('ShaderNodeVolumePrincipled')
vol.inputs['Density'].default_value = .0055
vol.inputs['Color'].default_value = (.78, .82, .86, 1)
fo = next(n for n in FN if n.type == 'OUTPUT_MATERIAL')
fm.node_tree.links.new(vol.outputs[0], fo.inputs['Volume'])
fog.data.materials.append(fm)
sc.world = w
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(40), math.radians(10), math.radians(-30)))
s = bpy.context.object
s.data.energy = 2.0
s.data.angle = math.radians(40)
try:
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Base Contrast'
except Exception as e:
    print(e)


def shot(n, loc, tgt, lens, res=(1536, 1024)):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.data.lens = lens
    c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = c
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = OUT + f'godtree_{TAG}_{n}.png'
    bpy.ops.render.render(write_still=True)


# 1.75 m 人形尺
bpy.ops.mesh.primitive_cylinder_add(radius=.22, depth=1.75, location=(15, -18, 0))
hm = bpy.context.object
hm.location.z = gh(15, -18) + .875
hmat = bpy.data.materials.new('Human')
hmat.use_nodes = True
next(n for n in hmat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.6, .12, .08, 1)
hm.data.materials.append(hmat)
shot('V3', (21, -34, 1.8), (0, 0, 9), 20)
shot('near', (12, -21, 1.7), (4, -6, 3), 24)
