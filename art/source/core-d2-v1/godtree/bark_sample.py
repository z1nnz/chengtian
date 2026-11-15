import bpy, bmesh, math, sys, os, numpy as np
from mathutils import Vector, noise

TEX = 'D:/chengtian/4-素材與快取/polyhaven-bark/'
OUT = 'D:/chengtian/4-素材與快取/bark-sample/'
SET = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else 'bark_brown_02'
A = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
TILE = float(A[1]) if len(A) > 1 else 1.5
AMP = float(A[2]) if len(A) > 2 else 0.07
TAG = A[3] if len(A) > 3 else ''
bpy.ops.wm.read_factory_settings(use_empty=True)


def img(n, cs='Non-Color'):
    i = bpy.data.images.load(TEX + f'{SET}_{n}_2k.png')
    i.colorspace_settings.name = cs
    return i


disp = img('disp')
W, H = disp.size
dp = np.array(disp.pixels[:], dtype=np.float32).reshape(H, W, -1)[:, :, 0]


def sdisp(u, v):
    x = (u % 1) * W
    y = (v % 1) * H
    x0 = int(x) % W
    y0 = int(y) % H
    x1 = (x0 + 1) % W
    y1 = (y0 + 1) % H
    fx = x - int(x)
    fy = y - int(y)
    return (dp[y0, x0] * (1 - fx) + dp[y0, x1] * fx) * (1 - fy) + (dp[y1, x0] * (1 - fx) + dp[y1, x1] * fx) * fy


def fb(p, s, o=4):
    return noise.fractal(Vector(p) * s, 1.0, 2.0, o, noise_basis='PERLIN_ORIGINAL')


def cr(p0, p1, p2, p3, t):
    return .5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)


def root(name, pts, r0, r1, seed, NU=144, flat=.8):
    P = [Vector(p) for p in pts]
    n = len(P)
    spl = []
    for i in range(n - 1):
        a = P[max(i - 1, 0)]
        b = P[i]
        c = P[i + 1]
        d = P[min(i + 2, n - 1)]
        for k in range(24):
            spl.append(cr(a, b, c, d, k / 24))
    spl.append(P[-1])
    L = [0]
    for i in range(1, len(spl)):
        L.append(L[-1] + (spl[i] - spl[i - 1]).length)
    tot = L[-1]
    NV = int(tot / 0.02)
    rings = []
    j = 0
    for k in range(NV + 1):
        s = tot * k / NV
        while j < len(L) - 2 and L[j + 1] < s:
            j += 1
        f = (s - L[j]) / max(L[j + 1] - L[j], 1e-6)
        rings.append((spl[j].lerp(spl[j + 1], f), s))
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new('UV')
    col = bm.loops.layers.color.new('Mask')
    up = Vector((0, 0, 1))
    V = []
    UVs = []
    M = []
    rmid = (r0 + r1) / 2
    rep = max(1, round(2 * math.pi * rmid / TILE))
    for k, (c, s) in enumerate(rings):
        t = k / NV
        a = rings[min(k + 1, NV)][0] - rings[max(k - 1, 0)][0]
        a.normalize()
        side = a.cross(up).normalized()
        nu = side.cross(a).normalized()
        r = r0 + (r1 - r0) * t ** 1.3
        tw = s * 0.35 + seed
        row = []
        ruv = []
        rm = []
        for i in range(NU):
            th = 2 * math.pi * i / NU
            rib = fb((math.cos(th + tw) * 2.2, math.sin(th + tw) * 2.2, s * .18 + seed), 1.0, 3)
            rib2 = abs(fb((math.cos(th + tw * 1.3) * 5, math.sin(th + tw * 1.3) * 5, s * .4 + seed * 2), 1.0, 2))
            lump = fb((c.x, c.y + th, c.z + seed), .9, 2)
            rr = r * (1 + .20 * rib - .16 * rib2 + .10 * lump)
            u = i / NU * rep
            v = s / TILE
            d = sdisp(u, v) - .5
            rr += d * AMP * min(1.0, r / .25 + .35)
            d3 = side * math.cos(th) * rr + nu * math.sin(th) * rr * flat
            p = c + d3
            nz = (side * math.cos(th) + nu * math.sin(th) * 1.25).normalized().z
            mo = nz * .62 + fb(p, 1.3, 3) * .75 + fb(p, 7.0, 3) * .30 - d * .45
            mo = max(0, min(1, (mo - .50) / .22))
            mo = mo * mo * (3 - 2 * mo)
            p += d3.normalized() * mo * .012
            row.append(bm.verts.new(p))
            ruv.append((u, v))
            rm.append((mo, max(0, min(1, d * 2 + .5)), 0, 1))
        V.append(row)
        UVs.append(ruv)
        M.append(rm)
    for k in range(NV):
        for i in range(NU):
            i2 = (i + 1) % NU
            f = bm.faces.new((V[k][i], V[k][i2], V[k + 1][i2], V[k + 1][i]))
            idx = [(k, i, False), (k, i2, i2 == 0), (k + 1, i2, i2 == 0), (k + 1, i, False)]
            for lp, (kk, ii, wrap) in zip(f.loops, idx):
                u, v = UVs[kk][ii]
                if wrap:
                    u = rep
                lp[uvl].uv = (u, v)
                lp[col] = M[kk][ii]
            f.smooth = True
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


m = bpy.data.materials.new('Bark')
m.use_nodes = True
nt = m.node_tree
N = nt.nodes
Lk = nt.links
b = next(n for n in N if n.type == 'BSDF_PRINCIPLED')


def tx(n, cs='Non-Color'):
    t = N.new('ShaderNodeTexImage')
    t.image = img(n, cs)
    return t


def ramp(p0, p1, c0=None, c1=None):
    r = N.new('ShaderNodeValToRGB')
    r.color_ramp.elements[0].position = p0
    r.color_ramp.elements[1].position = p1
    if c0:
        r.color_ramp.elements[0].color = c0
    if c1:
        r.color_ramp.elements[1].color = c1
    return r


def mix(kind='MIX', fac=None):
    x = N.new('ShaderNodeMixRGB')
    x.blend_type = kind
    if fac is not None:
        x.inputs[0].default_value = fac
    return x


dif = tx('diff', 'sRGB')
nor = tx('nor_gl')
rgh = tx('rough')
ao = tx('ao')
vc = N.new('ShaderNodeVertexColor')
vc.layer_name = 'Mask'
sep = N.new('ShaderNodeSeparateColor')
Lk.new(vc.outputs['Color'], sep.inputs[0])
hsv = N.new('ShaderNodeHueSaturation')
hsv.inputs['Saturation'].default_value = .85
hsv.inputs['Value'].default_value = .60
Lk.new(dif.outputs[0], hsv.inputs['Color'])
tint = mix('MULTIPLY', 1.0)
tint.inputs[2].default_value = (1.0, .86, .72, 1)
Lk.new(hsv.outputs[0], tint.inputs[1])
aom = mix('MULTIPLY', .85)
Lk.new(tint.outputs[0], aom.inputs[1])
Lk.new(ao.outputs[0], aom.inputs[2])
nz = N.new('ShaderNodeTexNoise')
nz.inputs['Scale'].default_value = 38
nz.inputs['Detail'].default_value = 6
lr = ramp(.62, .70)
Lk.new(nz.outputs[0], lr.inputs[0])
lm = N.new('ShaderNodeMath')
lm.operation = 'MULTIPLY'
Lk.new(lr.outputs[0], lm.inputs[0])
Lk.new(sep.outputs[1], lm.inputs[1])
lmx = mix()
lmx.inputs[2].default_value = (.42, .45, .40, 1)
Lk.new(lm.outputs[0], lmx.inputs[0])
Lk.new(aom.outputs[0], lmx.inputs[1])
mn = N.new('ShaderNodeTexNoise')
mn.inputs['Scale'].default_value = 90
mn.inputs['Detail'].default_value = 8
mc = ramp(.3, .75, (.018, .028, .008, 1), (.075, .095, .022, 1))
Lk.new(mn.outputs[0], mc.inputs[0])
mr = ramp(.45, .62)
Lk.new(sep.outputs[0], mr.inputs[0])
mx = mix()
Lk.new(mr.outputs[0], mx.inputs[0])
Lk.new(lmx.outputs[0], mx.inputs[1])
Lk.new(mc.outputs[0], mx.inputs[2])
Lk.new(mx.outputs[0], b.inputs['Base Color'])
nm = N.new('ShaderNodeNormalMap')
nm.inputs['Strength'].default_value = 1.4
Lk.new(nor.outputs[0], nm.inputs['Color'])
bp = N.new('ShaderNodeBump')
bp.inputs['Strength'].default_value = .6
bp.inputs['Distance'].default_value = .01
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

obs = [root('RootMain', [(-2.8, -.3, -.15), (-1.6, .1, .34), (-.3, -.15, .46), (1.0, .3, .26), (2.2, .1, .30), (3.2, -.2, -.12)], .46, .22, 1.0, flat=.9),
       root('RootFork', [(-.1, -.05, .25), (.6, -.75, .16), (1.5, -1.35, .05), (2.3, -1.6, -.1)], .24, .10, 5.0, NU=96),
       root('RootSmall', [(-1.4, .2, .2), (-1.0, 1.0, .1), (-.3, 1.7, .0), (.5, 2.1, -.08)], .16, .06, 9.0, NU=72)]
for o in obs:
    o.data.materials.append(m)
print('TRIS', sum(len(o.data.polygons) * 2 for o in obs))
bpy.ops.mesh.primitive_plane_add(size=30)
g = bpy.context.object
gm = bpy.data.materials.new('Mud')
gm.use_nodes = True
gb = next(n for n in gm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
gb.inputs['Base Color'].default_value = (.045, .033, .024, 1)
gb.inputs['Roughness'].default_value = .8
g.data.materials.append(gm)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 96
sc.cycles.use_denoising = True
try:
    bpy.ops.preferences.addon_enable(module='cycles')
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
bg.inputs[0].default_value = (.50, .56, .62, 1)
bg.inputs[1].default_value = .9
sc.world = w
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(52), 0, math.radians(35)))
s = bpy.context.object
s.data.energy = 2.2
s.data.angle = math.radians(25)
try:
    sc.view_settings.view_transform = 'AgX'
except Exception as e:
    print(e)


def shot(n, loc, tgt, lens, res=(1500, 1000)):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.data.lens = lens
    c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = c
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = OUT + f'{SET}{TAG}_{n}.png'
    bpy.ops.render.render(write_still=True)


shot('wide', (.4, -4.6, 1.5), (.2, 0, .25), 32)
shot('close', (-.2, -1.9, .9), (.3, -.1, .3), 50)
