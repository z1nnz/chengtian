"""Tree redo v2, package A (docs/execution/2026-11-14/樹木重做-v2-分工.md on feature/qingxi-creek-chapter): TR06 weeping willow
v002, variants A/B/C, built in the world-tree order (tree-method/天空島世界樹建模歷程與精修方法.md, sections 2, 4 and 7):

  1. S-shaped trunk from 7 control points, low-frequency ridges, lobed root flare, one burl, surface roots sunk 0.3 m;
  2. 3 silhouette limbs (far reach over the water, the width on the other side, the top), then supporting limbs to 6-7;
  3. secondaries on every limb (three thickness tiers: limb / secondary / streamer);
  4. 12-20 canopy anchors in two layers (front = water side, back) at the secondary and limb tips;
  5. 7-13 twig streams per anchor: thin twigs that arch up and out, then hang down in curtains (willow);
  6. five-vertex lance leaves along each stream parameter t (four outline points + raised midrib);
  7. vertex colour: height / outer blend from a 5-step willow palette (top outer light warm, low inner dark cool),
     alpha = canopy occlusion; wind weight in UV2.x (trunk 0, limbs low, streamers and leaves high), UV2.y = anchor phase;
  8. bark last: a low-contrast, stretched bark texture (made here with numpy) on the geometry ridges.

No leaf cards on LOD0-2 (LOD2 keeps fewer, larger solid leaves); LOD3 is the far card the package allows (<= 200 tris).
Fixed seeds (zlib.crc32), so a rebuild gives the same tree.

    blender -b --factory-startup -P build_tr.py -- bark            (bark texture -> art/textures/trees-v2-a)
    blender -b --factory-startup -P build_tr.py -- TR06_A TR06_B TR06_C
"""
import bpy, bmesh, json, math, sys, zlib
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PKG = 'trees-v2-a'
OUT = REPO / 'art' / 'exports' / PKG
TEX = REPO / 'art' / 'textures' / PKG
OUT.mkdir(parents=True, exist_ok=True); TEX.mkdir(parents=True, exist_ok=True)
PACKAGE = 'docs/execution/2026-11-14/樹木重做-v2-分工.md（A：TR04／06／07／08／09 v002，TR06 先交樣品）'
UP = Vector((0, 0, 1))


def seed(*k):
    return zlib.crc32('|'.join(map(str, k)).encode())


# ------------------------------------------------------------------ mesh accumulator
class Acc:
    """Collects verts / faces with per-vertex UV0, UV1 (wind weight, phase) and RGBA colour; one material per Acc."""
    def __init__(s):
        s.v, s.f, s.uv, s.uv2, s.col = [], [], [], [], []

    def add(s, verts, faces, uv, uv2, col):
        b = len(s.v); s.v += verts; s.uv += uv; s.uv2 += uv2; s.col += col
        s.f += [tuple(b + i for i in f) for f in faces]

    def tris(s):
        return sum(len(f) - 2 for f in s.f)

    def obj(s, name, mat, smooth=True):
        me = bpy.data.meshes.new(name); me.from_pydata([tuple(p) for p in s.v], [], s.f)
        me.validate(clean_customdata=False)
        l0 = me.uv_layers.new(name='UVMap'); l1 = me.uv_layers.new(name='UV2_Wind')
        lv = np.array([l.vertex_index for l in me.loops], dtype=np.int64)
        l0.data.foreach_set('uv', np.asarray(s.uv, dtype=np.float32)[lv].ravel())
        l1.data.foreach_set('uv', np.asarray(s.uv2, dtype=np.float32)[lv].ravel())
        ca = me.color_attributes.new(name='Col', type='FLOAT_COLOR', domain='POINT')
        ca.data.foreach_set('color', np.asarray(s.col, dtype=np.float32).ravel())
        me.polygons.foreach_set('use_smooth', [smooth] * len(me.polygons))
        me.materials.append(mat)
        o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
        return o


# ------------------------------------------------------------------ curves and tubes
def catmull(pts, n):
    """Centripetal Catmull-Rom through pts, n samples (positions)."""
    P = [Vector(p) for p in pts]; P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    segs = len(P) - 3; out = []
    for k in range(n):
        u = k / (n - 1) * segs; i = min(int(u), segs - 1); t = u - i
        p0, p1, p2, p3 = P[i:i + 4]
        def tj(ti, a, b): return ti + max((b - a).length, 1e-4) ** .5
        t0 = 0; t1 = tj(t0, p0, p1); t2 = tj(t1, p1, p2); t3 = tj(t2, p2, p3); tt = t1 + (t2 - t1) * t
        a1 = p0 * ((t1 - tt) / (t1 - t0)) + p1 * ((tt - t0) / (t1 - t0)); a2 = p1 * ((t2 - tt) / (t2 - t1)) + p2 * ((tt - t1) / (t2 - t1))
        a3 = p2 * ((t3 - tt) / (t3 - t2)) + p3 * ((tt - t2) / (t3 - t2))
        b1 = a1 * ((t2 - tt) / (t2 - t0)) + a2 * ((tt - t0) / (t2 - t0)); b2 = a2 * ((t3 - tt) / (t3 - t1)) + a3 * ((tt - t1) / (t3 - t1))
        out.append(b1 * ((t2 - tt) / (t2 - t1)) + b2 * ((tt - t1) / (t2 - t1)))
    return out


def frames(path):
    """Parallel-transport frames along a polyline: (tangent, normal, binormal) per point."""
    T = []
    for i in range(len(path)):
        d = path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]; T.append(d.normalized())
    n = T[0].cross(Vector((0.3, 0.1, 1)) if abs(T[0].z) < .95 else Vector((1, 0, 0))).normalized(); F = []
    for i, t in enumerate(T):
        if i:
            ax = T[i - 1].cross(t)
            if ax.length > 1e-6: n = Quaternion(ax.normalized(), T[i - 1].angle(t)) @ n
            n = (n - t * n.dot(t)).normalized()
        F.append((t, n, t.cross(n)))
    return F


def tube(acc, path, radii, sides, wind, phase=0.0, shape=None, ao=None, tip=True, vscale=1.0, u0=0.0):
    """Ring tube along path. radii per point; shape(i, theta) -> radius multiplier; wind = (w_start, w_end).
    UV: u around (seam duplicated), v = arc length / circumference (square texels), times vscale."""
    F = frames(path); n = len(path); verts, uv, uv2, col, faces = [], [], [], [], []
    v = 0.0
    for i in range(n):
        if i: v += (path[i] - path[i - 1]).length / max(2 * math.pi * max(radii[i - 1], .01), 1e-3) * vscale
        t, nn, bb = F[i]; w = wind[0] + (wind[1] - wind[0]) * i / (n - 1); a = 1.0 if ao is None else ao(i)
        for j in range(sides + 1):
            th = 2 * math.pi * j / sides; r = radii[i] * (shape(i, th) if shape else 1.0)
            verts.append(path[i] + (nn * math.cos(th) + bb * math.sin(th)) * r)
            uv.append((u0 + j / sides, v)); uv2.append((w, phase)); col.append((1, 1, 1, a))
    for i in range(n - 1):
        for j in range(sides):
            a = i * (sides + 1) + j; b = a + sides + 1
            faces.append((a, a + 1, b + 1, b))
    if tip:   # close the thin end with a short cone (the last ring already has a small radius)
        c = len(verts); t = F[-1][0]; verts.append(path[-1] + t * radii[-1] * 1.5); uv.append((u0 + .5, v + .05)); uv2.append((wind[1], phase)); col.append((1, 1, 1, 1))
        base = (n - 1) * (sides + 1)
        for j in range(sides): faces.append((base + j, base + j + 1, c))
    acc.add(verts, faces, uv, uv2, col)
    return F


def leaf(acc, at, d, side, L, W, colour, wind, phase, cup=.16):
    """Five-vertex leaf: petiole at `at`, tip along d, outline points at 40 % length, raised midrib point (cup)."""
    d = d.normalized(); s = (side - d * side.dot(d)).normalized(); nrm = d.cross(s)
    p0 = at; p2 = at + d * L; p1 = at + d * L * .42 + s * W * .5; p3 = at + d * L * .42 - s * W * .5
    pc = at + d * L * .46 + nrm * W * cup
    acc.add([p0, p1, p2, p3, pc], [(4, 0, 1), (4, 1, 2), (4, 2, 3), (4, 3, 0)],
            [(.5, 0), (1, .42), (.5, 1), (0, .42), (.5, .46)], [(wind, phase)] * 5, [colour] * 5)


# ------------------------------------------------------------------ materials and bark
def bark_texture():
    """1024 tileable bark: furrows stretched along v (the trunk), low contrast, normal from height."""
    N = 1024; rg = np.random.default_rng(seed('bark'))
    def noise(ax, ay, octv):
        f = np.fft.fft2(rg.standard_normal((N, N))); ky = np.fft.fftfreq(N)[:, None]; kx = np.fft.fftfreq(N)[None, :]
        k = np.sqrt((kx * ax) ** 2 + (ky * ay) ** 2) + 1e-6; g = np.real(np.fft.ifft2(f * np.exp(-(k * octv) ** 2) / k ** .9))
        return (g - g.mean()) / g.std()
    # rows = v (along the trunk): long in v, narrow in u -> furrows
    ridge = noise(1.0, 6.0, 14); ridge2 = noise(1.0, 4.0, 9); fine = noise(1.0, 2.5, 3); blot = noise(1.0, 1.0, 40)
    plates = np.minimum(np.abs(ridge), np.abs(ridge2) * 1.2)   # interlaced furrow network (willow bark), plates between
    h = np.clip(plates / 1.1, 0, 1) ** .6 * .82 + fine * .05 + blot * .05; h = (h - h.min()) / (h.max() - h.min())
    base = np.array([.195, .158, .122]); dark = np.array([.060, .048, .040]); lic = np.array([.22, .22, .19])
    alb = dark[None, None] * (1 - h[..., None]) + base[None, None] * h[..., None]
    lichen = (np.clip((blot - 1.2) * .5, 0, .18) * h)[..., None]; alb = alb * (1 - lichen) + lic * lichen
    gy, gx = np.gradient(h * 9.0); nrm = np.dstack([-gx, gy, np.ones_like(h)]); nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
    def save(name, arr, srgb):
        img = bpy.data.images.new(name, N, N, alpha=True, float_buffer=False)
        if not srgb: img.colorspace_settings.name = 'Non-Color'
        rgba = np.dstack([arr, np.ones((N, N))]).astype(np.float32); img.pixels.foreach_set(rgba[::-1].ravel())
        img.filepath_raw = str(TEX / f'{name}.png'); img.file_format = 'PNG'; img.save(); return img
    save('T_TreeV2_Bark_Albedo', np.clip(alb, 0, 1) ** (1 / 2.2), True); save('T_TreeV2_Bark_Normal', nrm * .5 + .5, False)


def materials():
    bark = bpy.data.materials.new('M_TreeV2_Bark'); bark.use_nodes = True; nt = bark.node_tree; bs = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bs.inputs['Roughness'].default_value = .92; bs.inputs['Metallic'].default_value = 0
    ia = nt.nodes.new('ShaderNodeTexImage'); ia.image = bpy.data.images.load(str(TEX / 'T_TreeV2_Bark_Albedo.png'), check_existing=True)
    inn = nt.nodes.new('ShaderNodeTexImage'); inn.image = bpy.data.images.load(str(TEX / 'T_TreeV2_Bark_Normal.png'), check_existing=True); inn.image.colorspace_settings.name = 'Non-Color'
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = .8
    nt.links.new(ia.outputs['Color'], bs.inputs['Base Color']); nt.links.new(inn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], bs.inputs['Normal'])
    lf = bpy.data.materials.new('M_TreeV2_Leaf'); lf.use_nodes = True; nt = lf.node_tree; bs = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bs.inputs['Roughness'].default_value = .86; bs.inputs['Metallic'].default_value = 0; lf.use_backface_culling = False
    vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Col'; nt.links.new(vc.outputs['Color'], bs.inputs['Base Color'])
    return bark, lf


# ------------------------------------------------------------------ the willow
PALETTE = [(.034, .062, .030), (.062, .108, .044), (.118, .178, .060), (.205, .262, .085), (.315, .350, .125)]


def leaf_colour(expo, occl):
    t = max(0, min(3.999, expo * 4)); lo = int(t); m = t - lo
    c = [PALETTE[lo][k] * (1 - m) + PALETTE[lo + 1][k] * m for k in range(3)]
    return (*c, occl)


VARIANTS = {
    # trunk control points (x, y, z); the water side is -Y. limbs: (trunk t, azimuth deg, elevation deg, length m, start radius, droop)
    'TR06_A': dict(
        height=10.0,
        trunk=[(0, 0, -.30), (.02, -.04, .55), (.10, -.40, 1.55), (.04, -.95, 2.55), (-.18, -1.30, 3.35), (-.14, -1.42, 4.05), (.05, -1.40, 4.6)],
        tr=[.40, .355, .32, .29, .26, .22, .17],
        limbs=[(.93, -95, 38, 5.6, .15, 1.0), (.70, 10, 50, 4.4, .13, .6), (1.0, -170, 76, 5.0, .13, .3),
               (.58, 140, 52, 3.6, .10, .5), (.84, 70, 62, 4.0, .10, .4), (.64, -45, 55, 3.6, .095, .55), (.96, -135, 50, 4.2, .10, .7)],
        roots=7, burl=(1.9, 2.4)),
    'TR06_B': dict(
        height=11.5,
        trunk=[(0, 0, -.30), (-.03, .02, .6), (.05, -.22, 1.7), (.20, -.55, 2.9), (.12, -.75, 4.0), (-.10, -.80, 4.9), (-.06, -.78, 5.5)],
        tr=[.37, .33, .30, .27, .245, .21, .16],
        limbs=[(1.0, -85, 66, 5.0, .14, .4), (.74, 30, 58, 4.4, .12, .5), (.95, 160, 72, 4.8, .12, .35),
               (.58, -150, 52, 3.6, .10, .6), (.66, 100, 48, 3.9, .10, .6), (.88, -30, 74, 4.2, .095, .3)],
        roots=6, burl=(3.1, -.8)),
    'TR06_C': dict(
        height=8.5,
        trunk=[(0, 0, -.30), (.04, -.06, .45), (.18, -.55, 1.2), (.15, -1.20, 1.9), (-.05, -1.70, 2.55), (-.25, -1.95, 3.2), (-.22, -2.05, 3.75)],
        tr=[.43, .39, .35, .32, .29, .25, .19],
        limbs=[(.98, -95, 28, 5.0, .16, 1.0), (.70, 20, 46, 4.0, .13, .7), (1.0, 170, 76, 5.2, .125, .3),
               (.52, 120, 42, 3.2, .11, .7), (.86, 60, 60, 3.6, .10, .5), (.64, -50, 40, 3.4, .10, .8)],
        roots=8, burl=(1.3, 1.1), broken=True),
}


def build_tree(vid, cfg):
    rg = np.random.default_rng(seed(vid)); wood, twigs, leaves, collide = Acc(), Acc(), Acc(), []
    H = cfg['height']
    # 1. trunk: S curve, ridges (5 + 9 lobes, strongest low), lobed root flare, a burl
    tp = catmull(cfg['trunk'], 46); trs = np.interp(np.linspace(0, 1, 46), np.linspace(0, 1, len(cfg['tr'])), cfg['tr'])
    tw = rg.uniform(0, 6.28); bz, bth = cfg['burl']
    def tshape(i, th):
        z = tp[i].z; lowk = math.exp(-max(z, 0) / 2.2)
        m = 1 + (.11 * math.cos(5 * th + tw + z * .9) + .05 * math.cos(9 * th - tw * 1.7 + z * 1.6)) * (.45 + .55 * lowk)   # twisted ridges
        if z < .9: m *= 1 + .55 * math.exp(-max(z + .05, 0) / .32) * (.55 + .45 * math.cos(5 * th + tw))
        m *= 1 + .32 * math.exp(-((z - bz) / .26) ** 2 - (math.atan2(math.sin(th - bth), math.cos(th - bth)) / .55) ** 2)
        return m
    tF = tube(wood, tp, list(trs), 20, (0, .04), shape=tshape, ao=lambda i: .55 + .45 * min(1, max(tp[i].z, 0) / 1.2), tip=False)
    # the trunk top is hidden inside the limb fork: cap it with a small dome
    top = tp[-1]; c = len(wood.v); wood.add([top + tF[-1][0] * trs[-1] * .6], [], [(.5, 1)], [(.05, 0)], [(1, 1, 1, 1)])
    base = (len(tp) - 1) * 21; wood.f += [(base + j, base + j + 1, c) for j in range(20)]

    def on_trunk(t):
        k = t * (len(tp) - 1); i = min(int(k), len(tp) - 2); f = k - i
        return tp[i].lerp(tp[i + 1], f), tF[i][0], float(trs[i] * (1 - f) + trs[i + 1] * f)

    # surface roots: out from the flare, into the ground (ends at -0.25 m)
    for k in range(cfg['roots']):
        a = 2 * math.pi * k / cfg['roots'] + rg.uniform(-.35, .35) + tw; dvec = Vector((math.cos(a), math.sin(a), 0)); L = rg.uniform(.35, .8)
        r0 = float(trs[0]); pts = [Vector((0, 0, .56)) + dvec * r0 * .18,   # starts well inside the trunk (no coplanar faces with the flare)
                Vector((0, 0, .2)) + dvec * (r0 + L * .25), Vector((0, 0, .04)) + dvec * (r0 + L * .65), Vector((0, 0, -.26)) + dvec * (r0 + L)]
        tube(wood, catmull(pts, 9), list(np.linspace(r0 * .6, .04, 9) * rg.uniform(.85, 1.1)), 8, (0, 0), ao=lambda i: .5 + .05 * i)
    collide.append(('trunk', tp[:24], trs[:24]))

    anchors = []   # (point, outward direction, radius, layer)
    # 2-3. limbs and secondaries
    for li, (t0, az, el, L, r0, droop) in enumerate(cfg['limbs']):
        p0, td, rt = on_trunk(t0); a = math.radians(az); e = math.radians(el)
        out = Vector((math.cos(a), math.sin(a), 0)); d0 = (out * math.cos(e) + UP * math.sin(e)).normalized()
        start = p0 - d0 * rt * .5
        # arch: rises at the elevation angle, then levels and droops at the tip (willow limbs bow over)
        pts = [start + out * L * u * (.45 + .55 * math.cos(e)) + UP * L * (math.sin(e) * (1.3 * u - .45 * u * u) - .22 * droop * u ** 3) for u in (0, .28, .55, .8, 1.0)]
        pts = [p + Vector((rg.normal(0, .08), rg.normal(0, .08), rg.normal(0, .05))) * L * .2 * (i > 0) for i, p in enumerate(pts)]
        lp = catmull(pts, 16); lr = list(np.linspace(r0, r0 * .22, 16) ** 1.0)
        lr = [r * (1 + .25 * math.exp(-i / 2.0)) for i, r in enumerate(lr)]   # swelling at the fork
        tube(wood, lp, lr, 10, (.05, .3), phase=li / 8)
        anchors.append((lp[-1], (lp[-1] - lp[-4]).normalized(), lr[-1], li, lp))
        nsec = 2 if L > 3.8 else 1
        for si in range(nsec):
            ts = .42 + .5 * (si + rg.uniform(-.15, .15)) / nsec; k = int(ts * 15); sp = lp[k]; sd = (lp[k + 1] - lp[k]).normalized()
            side = sd.cross(UP).normalized() * (1 if (si + li) % 2 else -1)
            sdir = (sd * .55 + side * rg.uniform(.55, .9) + UP * rg.uniform(.25, .55)).normalized(); SL = L * rg.uniform(.32, .46)
            spts = [sp, sp + sdir * SL * .4 + UP * SL * .1, sp + sdir * SL * .8 + UP * SL * .05, sp + sdir * SL + (sdir * .3 - UP * .4).normalized() * SL * .18]
            sq = catmull(spts, 9); sr = list(np.linspace(lr[k] * .55, lr[k] * .16, 9))
            tube(wood, sq, sr, 6, (.3, .55), phase=li / 8 + si * .03)
            anchors.append((sq[-1], (sq[-1] - sq[-3]).normalized(), sr[-1], li, sq))
    if cfg.get('broken'):   # one snapped limb stub with a ragged end
        p0, td, rt = on_trunk(.62); d0 = Vector((.55, .6, .55)).normalized()
        sp = catmull([p0 - d0 * rt * .5, p0 + d0 * .45, p0 + d0 * .8 + UP * .08], 6)
        b0 = len(wood.v); tube(wood, sp, [.1, .095, .09, .085, .08, .072], 10, (.03, .08), tip=False)
        F = frames(sp); c0 = len(wood.v); end = sp[-1]; rim = b0 + (len(sp) - 1) * 11
        wood.add([end + F[-1][0] * .03], [], [(.5, .5)], [(.08, 0)], [(.6, .6, .6, .7)]); wood.f += [(rim + j, rim + j + 1, c0) for j in range(10)]

    # 4. anchors: keep 12-20; layer by depth (front = water side, -Y of the crown centre)
    cy = sum(a[0].y for a in anchors) / len(anchors)
    assert 12 <= len(anchors) <= 20, f'{vid}: {len(anchors)} canopy anchors (12-20 wanted)'
    zs = [a[0].z for a in anchors]; zmin_c, zmax_c = min(zs) - 2.5, max(zs) + .8
    cx = sum(a[0].x for a in anchors) / len(anchors); rmax = max((Vector((a[0].x - cx, a[0].y - cy, 0))).length for a in anchors) + 1.0
    # 5-6. twig streams and leaves
    nleaf = 0; streams = []
    for ai, (ap, ad, ar, li, bp) in enumerate(anchors):
        layer = 'Front' if ap.y < cy else 'Back'; ns = int(rg.integers(7, 14)); twist = ai * .83 + (.4 if layer == 'Front' else 0)
        for si in range(ns):
            nb = 3; heading = (si % nb) * 2.0944 + twist + rg.normal(0, .22); side = Vector((math.cos(heading), math.sin(heading), 0))   # 3 bundles per anchor: curtains with gaps
            d = (ad * .55 + side * .55 + UP * rg.uniform(.35, .8)).normalized()
            u = 1 - .45 * (si / max(ns - 1, 1)) ** .8 * rg.uniform(.7, 1.0); k = min(int(u * (len(bp) - 1)), len(bp) - 1)   # along the last 45 % of the branch, the tip included
            p = bp[k] + side * rg.uniform(.02, .12); path = [p.copy()]
            hem = max(rg.uniform(.35, 2.6) + (.0 if layer == 'Front' else .4), .3)   # where the curtain ends above the ground
            ds = .16; g = rg.uniform(1.2, 2.0); sway = Vector((rg.normal(0, .02), rg.normal(0, .02), 0))
            Lmax = rg.uniform(2.2, 5.0)
            while len(path) * ds < Lmax and p.z > hem:
                d = (d + Vector((0, 0, -g * ds)) + sway).normalized(); p = p + d * ds; path.append(p.copy())
            if len(path) < 4: continue
            streams.append((path, ai, layer))
    total_len = sum(len(s[0]) for s in streams) * .16
    budget = cfg.get('leaves', 11500); per_m = budget / total_len
    for path, ai, layer in streams:
        n = len(path); gp = path[::4] + ([path[-1]] if (n - 1) % 4 else [])   # twig geometry every 0.64 m; the leaves sit on this polyline
        cum = np.concatenate([[0], np.cumsum([(gp[j + 1] - gp[j]).length for j in range(len(gp) - 1)])])
        tube(twigs, gp, list(np.linspace(.008, .003, len(gp))), 3, (.55, .9), phase=ai / 20)
        L = (n - 1) * .16; k = int(per_m * L * rg.uniform(.85, 1.15))
        for q in range(k):
            t = .06 + .94 * (q + rg.uniform(0, 1)) / k; sl = t * cum[-1]; i = min(int(np.searchsorted(cum, sl)) - 1, len(gp) - 2); i = max(i, 0)
            f = (sl - cum[i]) / max(cum[i + 1] - cum[i], 1e-6); at = gp[i].lerp(gp[i + 1], f); tg = (gp[i + 1] - gp[i]).normalized()
            ph = q * 2.39996 + ai; around = tg.cross(UP if abs(tg.z) < .9 else Vector((1, 0, 0))).normalized()
            around = Quaternion(tg, ph) @ around
            aa = math.radians(rg.uniform(28, 55)); ld = (tg * math.cos(aa) + around * math.sin(aa)).normalized()
            ld = (ld + Vector((0, 0, -.25))).normalized()
            Ll = rg.uniform(.20, .30); Wl = Ll * rg.uniform(.17, .23)   # enlarged so ~10k leaves read as full curtains at game distance
            h = (at.z - zmin_c) / (zmax_c - zmin_c); o = min(1, Vector((at.x - cx, at.y - cy, 0)).length / rmax)
            expo = max(0, min(1, .5 * h + .38 * o + .12 * t + rg.uniform(-.06, .06)))
            occl = .45 + .55 * max(expo, o * .9)
            leaf(leaves, at, ld, around.cross(ld), Ll, Wl, leaf_colour(expo, occl), .9 + .1 * t, ai / 20)
            nleaf += 1
    return wood, twigs, leaves, collide, anchors, streams, nleaf


def lod_leaves(vid, streams, anchors, frac, scale, budget):
    """LOD1/2 leaves: fewer, larger leaves on the same streams (same colours)."""
    rg = np.random.default_rng(seed(vid, 'lod', frac)); acc = Acc()
    cy = sum(a[0].y for a in anchors) / len(anchors); cx = sum(a[0].x for a in anchors) / len(anchors)
    zs = [a[0].z for a in anchors]; zmin_c, zmax_c = min(zs) - 2.5, max(zs) + .8
    rmax = max((Vector((a[0].x - cx, a[0].y - cy, 0))).length for a in anchors) + 1.0
    total_len = sum(len(s[0]) for s in streams) * .16; per_m = budget * frac / total_len
    for path, ai, layer in streams:
        n = len(path); L = (n - 1) * .16; k = max(1, int(round(per_m * L)))
        for q in range(k):
            t = .06 + .94 * (q + rg.uniform(0, 1)) / k; u = t * (n - 1); i = min(int(u), n - 2); f = u - i
            at = path[i].lerp(path[i + 1], f); tg = (path[i + 1] - path[i]).normalized()
            around = Quaternion(tg, q * 2.39996 + ai) @ tg.cross(UP if abs(tg.z) < .9 else Vector((1, 0, 0))).normalized()
            ld = ((tg * .8 + around * .5).normalized() + Vector((0, 0, -.25))).normalized()
            Ll = rg.uniform(.20, .30) * scale ** .75; Wl = Ll * rg.uniform(.18, .26) * scale ** .25
            h = (at.z - zmin_c) / (zmax_c - zmin_c); o = min(1, Vector((at.x - cx, at.y - cy, 0)).length / rmax)
            expo = max(0, min(1, .5 * h + .38 * o + .12 * t)); occl = .45 + .55 * max(expo, o * .9)
            leaf(acc, at, ld, around.cross(ld), Ll, Wl, leaf_colour(expo, occl), .9 + .1 * t, ai / 20)
    return acc


ROT = Matrix.Rotation(math.radians(90), 4, 'Z')   # built with the water side at -Y, delivered with it at +X (matches the picked front view)


def place(acc):
    acc.v = [ROT @ Vector(p) for p in acc.v]
    return acc


def far_card(vid, bounds):
    """LOD3: two crossed cards with an orthographic render of LOD0 (front = looking along +Y, side = looking along -X)."""
    mn, mx = bounds; ctr = (mn + mx) / 2; size = max(mx.x - mn.x, mx.y - mn.y, mx.z - mn.z) * 1.02
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 48; sc.cycles.use_denoising = True
    try:
        pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = 'OPTIX'; pr.get_devices()
        for d in pr.devices: d.use = True
        sc.cycles.device = 'GPU'
    except Exception: pass
    sc.render.film_transparent = True; sc.render.resolution_x = sc.render.resolution_y = 512; sc.view_settings.view_transform = 'Standard'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Strength'].default_value = .9
    sun = bpy.data.objects.new('bb_sun', bpy.data.lights.new('bb_sun', 'SUN')); sun.data.energy = 2.6; sun.rotation_euler = (math.radians(40), 0, math.radians(-30)); sc.collection.objects.link(sun)
    cam = bpy.data.objects.new('bb_cam', bpy.data.cameras.new('bb_cam')); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = size; cam.data.clip_end = 500
    cz = mn.z + size / 2   # the card bottom sits at the lowest point
    halves = []
    for k, (loc, rot) in enumerate((((ctr.x, ctr.y - 100, cz), (math.radians(90), 0, 0)), ((ctr.x + 100, ctr.y, cz), (math.radians(90), 0, math.radians(90))))):
        cam.location = loc; cam.rotation_euler = rot; sun.rotation_euler = (math.radians(50), 0, rot[2] - math.radians(25)); f = Path(bpy.app.tempdir) / f'bb{k}.png'; sc.render.filepath = str(f)
        bpy.ops.render.render(write_still=True); im = bpy.data.images.load(str(f)); halves.append(np.array(im.pixels[:], dtype=np.float32).reshape(512, 512, 4))
    for o in (sun, cam): bpy.data.objects.remove(o)
    full = np.concatenate(halves, axis=1)   # 1024 x 512 (rows bottom-up, as Blender stores them)
    rgb = full[..., :3] / np.maximum(full[..., 3:], 1e-4); full = np.dstack([np.clip(rgb, 0, 1), (full[..., 3] > .35).astype(np.float32)])
    img = bpy.data.images.new(f'T_{vid}_Far', 1024, 512, alpha=True); img.pixels.foreach_set(full.ravel())
    img.filepath_raw = str(TEX / f'T_{vid}_Far.png'); img.file_format = 'PNG'; img.save()
    m = bpy.data.materials.new(f'M_{vid}_Far'); m.use_nodes = True; nt = m.node_tree; bs = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = img; nt.links.new(ti.outputs['Color'], bs.inputs['Base Color']); nt.links.new(ti.outputs['Alpha'], bs.inputs['Alpha'])
    bs.inputs['Roughness'].default_value = .9; m.use_backface_culling = False
    h = size / 2; acc = Acc(); z0, z1 = cz - h, cz + h
    acc.add([(ctr.x - h, ctr.y, z0), (ctr.x + h, ctr.y, z0), (ctr.x + h, ctr.y, z1), (ctr.x - h, ctr.y, z1)], [(0, 1, 2, 3)],
            [(0, 0), (.5, 0), (.5, 1), (0, 1)], [(.6, 0)] * 4, [(1, 1, 1, 1)] * 4)
    acc.add([(ctr.x, ctr.y + h, z0), (ctr.x, ctr.y - h, z0), (ctr.x, ctr.y - h, z1), (ctr.x, ctr.y + h, z1)], [(0, 1, 2, 3)],
            [(.5, 0), (1, 0), (1, 1), (.5, 1)], [(.6, 0)] * 4, [(1, 1, 1, 1)] * 4)
    return acc.obj(f'{vid}_LOD3', m, smooth=False)


def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); o = bpy.context.view_layer.objects.active; o.name = name; o.data.name = name
    return o


def decimate(o, ratio):
    m = o.modifiers.new('d', 'DECIMATE'); m.ratio = max(.02, min(1, ratio)); m.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier=m.name)


def tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def build(vid):
    bpy.ops.wm.read_factory_settings(use_empty=True); bark, lfm = materials(); cfg = VARIANTS[vid]
    wood, twigs, leaves, collide, anchors, streams, nleaf = build_tree(vid, cfg)
    l1 = lod_leaves(vid, streams, anchors, .25, 1.9, cfg.get('leaves', 11500)); l2 = lod_leaves(vid, streams, anchors, .0625, 3.6, cfg.get('leaves', 11500))
    col = Acc()
    for _, path, radii in collide: tube(col, path, list(np.asarray(radii) * 1.05), 8, (0, 0), tip=False)
    for a in (wood, twigs, leaves, l1, l2, col): place(a)
    wood_o = wood.obj(f'{vid}_Wood', bark); wt = tris(wood_o)
    w1 = wood_o.copy(); w1.data = wood_o.data.copy(); bpy.context.scene.collection.objects.link(w1)
    w2 = wood_o.copy(); w2.data = wood_o.data.copy(); bpy.context.scene.collection.objects.link(w2)
    print("PARTS wood", wt, "twigs", twigs.tris(), "leaves", leaves.tris(), "streams", len(streams), "anchors", len(anchors), flush=True)
    lod0 = join([wood_o, twigs.obj(f'{vid}_Twigs', bark), leaves.obj(f'{vid}_Leaves', lfm)], f'{vid}_LOD0')
    lo1 = l1.obj('l1', lfm); decimate(w1, (14600 - tris(lo1)) / wt); lod1 = join([w1, lo1], f'{vid}_LOD1')
    lo2 = l2.obj('l2', lfm); decimate(w2, (3900 - tris(lo2)) / wt); lod2 = join([w2, lo2], f'{vid}_LOD2')
    co = col.obj(f'{vid}_Collision', bark, smooth=False); co.data.materials.clear()
    vs = np.array([v.co[:] for v in lod0.data.vertices]); mn, mx = Vector(vs.min(0)), Vector(vs.max(0)); dims = mx - mn
    for o in (lod1, lod2, co): o.hide_render = True
    lod3 = far_card(vid, (mn, mx))
    for o in (lod1, lod2, co): o.hide_render = False
    T = [tris(o) for o in (lod0, lod1, lod2, lod3)]
    assert T[0] <= 60000 and T[1] <= 15000 and T[2] <= 4000 and T[3] <= 200, f'{vid} over budget {T}'
    assert 8.0 <= mx.z <= 12.0, f'{vid} height {mx.z:.2f} m outside 8-12 m'
    assert abs(mn.z + .3) < .06, f'{vid} roots should end 0.3 m below ground, lowest {mn.z:.3f}'
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / f'{vid}.blend'))
    bpy.ops.object.select_all(action='DESELECT')
    for o in (lod0, lod1, lod2, lod3, co): o.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(OUT / f'{vid}.fbx'), use_selection=True, object_types={'MESH'}, global_scale=1.0, apply_unit_scale=True,
                             apply_scale_options='FBX_SCALE_ALL', bake_space_transform=True, axis_forward='-Z', axis_up='Y', use_mesh_modifiers=True,
                             mesh_smooth_type='FACE', use_tspace=False, colors_type='SRGB', add_leaf_bones=False, bake_anim=False, path_mode='STRIP', embed_textures=False)
    cyy = sum(b[0].y for b in anchors) / len(anchors); front = sum(1 for a in anchors if a[0].y < cyy)
    info = {'id': vid, 'package': PACKAGE, 'author': 'A (Johnnnny0823)', 'version': 'v002',
            'status': 'Exported; Imported: see README (Unity 6000.3.28f1 check); In-game Verified: 未驗',
            'block': 'A1 溪邊、A3', 'species': '垂柳', 'waterSide': '+X（樹幹和長枝斜向 +X，擺放時 +X 朝水面）',
            'dimensions_m': [round(float(d), 3) for d in dims], 'bounds_min_m': [round(float(v), 3) for v in mn], 'bounds_max_m': [round(float(v), 3) for v in mx],
            'origin': '樹幹底部中心，z = 0 是地面；根往下埋 0.3 m',
            'lods': [{'lod': i, 'triangles': T[i], 'materials': sorted({m.name for m in o.data.materials})} for i, o in enumerate((lod0, lod1, lod2, lod3))],
            'structure': {'mainLimbs': len(cfg['limbs']), 'canopyAnchors': len(anchors), 'anchorsFrontWaterSide': front, 'anchorsBack': len(anchors) - front,
                          'twigStreams': len(streams), 'leavesLOD0': nleaf, 'leafVertices': 5},
            'vertexData': {'colour': 'RGB = 葉色（依樹冠內高度與內外連續混色），A = 樹冠遮蔽；樹皮 RGB 白、A = 根部遮蔽',
                           'uv2': 'x = 風權重（主幹 0、主枝 0.05–0.3、次枝 0.3–0.55、垂枝 0.55–0.9、葉 0.9–1.0），y = 葉冠錨點相位'},
            'materials': ['M_TreeV2_Bark', 'M_TreeV2_Leaf', f'M_{vid}_Far'],
            'textures': {'T_TreeV2_Bark_Albedo': '1024x1024', 'T_TreeV2_Bark_Normal': '1024x1024', f'T_{vid}_Far': '1024x512 (LOD3 only, alpha)'},
            'collision': f'{vid}_Collision（樹幹下段，8 邊管）', 'seed': f'zlib.crc32("{vid}")',
            'fbx': f'art/exports/{PKG}/{vid}.fbx', 'fps': '不寫（手機未實測）'}
    (OUT / f'{vid}.model_info.json').write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
    print(vid, 'LOD tris', T, 'dims', info['dimensions_m'], 'min', info['bounds_min_m'], 'anchors', len(anchors), 'streams', len(streams), 'leaves', nleaf, flush=True)


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    for a in args:
        if a == 'bark':
            bpy.ops.wm.read_factory_settings(use_empty=True); bark_texture(); print('bark saved', flush=True)
        else:
            build(a)
