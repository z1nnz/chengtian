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


def tube(acc, path, radii, sides, wind, phase=0.0, shape=None, ao=None, tip=True, vscale=1.0, u0=0.0, colf=None, spin=0.0):
    """Ring tube along path. radii per point; shape(i, theta) -> radius multiplier; wind = (w_start, w_end).
    UV: u around (seam duplicated), v = arc length / circumference (square texels), times vscale."""
    F = frames(path); n = len(path); verts, uv, uv2, col, faces = [], [], [], [], []
    v = 0.0
    for i in range(n):
        if i: v += (path[i] - path[i - 1]).length / max(2 * math.pi * max(radii[i - 1], .01), 1e-3) * vscale
        t, nn, bb = F[i]; w = wind[0] + (wind[1] - wind[0]) * i / (n - 1); a = 1.0 if ao is None else ao(i)
        for j in range(sides + 1):
            th = 2 * math.pi * j / sides + spin; r = radii[i] * (shape(i, th) if shape else 1.0)
            verts.append(path[i] + (nn * math.cos(th) + bb * math.sin(th)) * r)
            uv.append((u0 + j / sides, v)); uv2.append((w, phase)); col.append(colf(i, th, a) if colf else (1, 1, 1, a))
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


def leaf(acc, at, d, side, L, W, colour, wind, phase, cup=.16, sa=.42, lift=0.0):
    """Five-vertex leaf: petiole at `at`, tip along d, outline points at `sa` of the length, raised midrib point (cup)."""
    d = d.normalized(); s = (side - d * side.dot(d)).normalized(); nrm = d.cross(s); at = at + nrm * lift   # lift: neighbours never share a plane
    p0 = at; p2 = at + d * L; p1 = at + d * L * sa + s * W * .5; p3 = at + d * L * sa - s * W * .5
    pc = at + d * L * (sa + .04) + nrm * W * cup
    acc.add([p0, p1, p2, p3, pc], [(4, 0, 1), (4, 1, 2), (4, 2, 3), (4, 3, 0)],
            [(.5, 0), (1, sa), (.5, 1), (0, sa), (.5, sa + .04)], [(wind, phase)] * 5, [colour] * 5)


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


def bamboo_material():
    m = bpy.data.materials.new('M_TreeV2_Bamboo'); m.use_nodes = True; nt = m.node_tree; bs = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bs.inputs['Roughness'].default_value = .5; bs.inputs['Metallic'].default_value = 0
    vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Col'; nt.links.new(vc.outputs['Color'], bs.inputs['Base Color'])
    return m


def materials(sp=None):
    sp = sp or SPECIES['TR06']; tint = sp.get('bark_tint', (1, 1, 1))
    bark = bpy.data.materials.new(sp.get('bark_mat', 'M_TreeV2_Bark')); bark.use_nodes = True; nt = bark.node_tree; bs = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bs.inputs['Roughness'].default_value = .92; bs.inputs['Metallic'].default_value = 0
    ia = nt.nodes.new('ShaderNodeTexImage'); ia.image = bpy.data.images.load(str(TEX / 'T_TreeV2_Bark_Albedo.png'), check_existing=True)
    inn = nt.nodes.new('ShaderNodeTexImage'); inn.image = bpy.data.images.load(str(TEX / 'T_TreeV2_Bark_Normal.png'), check_existing=True); inn.image.colorspace_settings.name = 'Non-Color'
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = .8
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1
    mx.inputs[7].default_value = (*tint, 1)   # species bark tint (Unity: _BaseColor); the hollow / crotch darkening rides on the vertex colour
    vcb = nt.nodes.new('ShaderNodeVertexColor'); vcb.layer_name = 'Col'; mx2 = nt.nodes.new('ShaderNodeMix'); mx2.data_type = 'RGBA'; mx2.blend_type = 'MULTIPLY'; mx2.inputs['Factor'].default_value = 1
    nt.links.new(ia.outputs['Color'], mx.inputs[6]); nt.links.new(mx.outputs[2], mx2.inputs[6]); nt.links.new(vcb.outputs['Color'], mx2.inputs[7])
    nt.links.new(mx2.outputs[2], bs.inputs['Base Color']); nt.links.new(inn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], bs.inputs['Normal'])
    lf = bpy.data.materials.new('M_TreeV2_Leaf'); lf.use_nodes = True; nt = lf.node_tree; bs = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bs.inputs['Roughness'].default_value = .86; bs.inputs['Metallic'].default_value = 0; lf.use_backface_culling = False
    vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Col'; nt.links.new(vc.outputs['Color'], bs.inputs['Base Color'])
    return bark, lf


# ------------------------------------------------------------------ species
PALETTE = [(.034, .062, .030), (.062, .108, .044), (.118, .178, .060), (.205, .262, .085), (.315, .350, .125)]   # willow green
SPECIES = {
    # stream: how the twig streams grow from the anchors ('hang' willow curtains, 'spray' maple tiers, 'shoot' plum
    # zig-zag shoots, 'twig' leafless dead-tree twigs); leaf: length range m, width / length, angle to the twig (deg),
    # where the outline points sit along the leaf, droop, flat (blade faces up); flowers: fraction of leaves drawn as blossoms
    'TR06': dict(name='垂柳', h=(8, 12), block='A1 溪邊、A3', palette=PALETTE, stream='hang', ns=(10, 14), leaf=((.24, .34), (.19, .25), (28, 55), .42, .25, False),
                 leaves=12400, twig_r=(.008, .003), bark_tint=(1, 1, 1)),
    'TR04': dict(name='楓', h=(8, 12), block='D3、A3', bark_mat='M_TreeV2_Bark_Maple', palette=[(.050, .008, .010), (.105, .014, .014), (.175, .026, .016), (.255, .050, .020), (.330, .095, .030)],
                 stream='spray', ns=(10, 14), reach=.88, leaf=((.19, .28), (.8, .95), (35, 75), .55, .1, False), leaves=12500, twig_r=(.012, .004), bark_tint=(.92, .92, .95)),
    'TR07': dict(name='梅', h=(4, 6), block='A1 院子', bark_mat='M_TreeV2_Bark_Plum', palette=[(.050, .085, .030), (.085, .130, .045), (.130, .185, .060), (.185, .240, .080), (.240, .300, .110)],
                 stream='shoot', ns=(7, 11), leaf=((.05, .08), (.45, .6), (30, 60), .45, .0, False), leaves=4200, twig_r=(.010, .004),
                 flowers=.55, zig=.75, flower_col=[(.80, .55, .58), (.90, .74, .76), (.95, .92, .90)], bark_tint=(.42, .36, .34)),
    'TR09': dict(name='竹叢', h=(6, 8), block='A1 北側、A8 竹海', stream='bamboo', palette=[(.030, .068, .030), (.055, .115, .045), (.095, .175, .060), (.160, .245, .080), (.245, .315, .110)], ns=(0, 1), leaf=((.12, .2), (.12, .16), (60, 80), .35, .7, True),
                 leaves=6000, twig_r=(.006, .002), bark_tint=(.55, .46, .36), bark_mat='M_TreeV2_Bark_Bamboo'),
    'TR08': dict(name='枯樹', h=(6, 9), block='A1、A9', bark_mat='M_TreeV2_Bark_Dead', palette=PALETTE, stream='twig', ns=(8, 12), leaf=None, leaves=0, twig_r=(.03, .006), bark_tint=(1.0, 1.22, 1.5)),
}


def leaf_colour(expo, occl, pal=PALETTE):
    t = max(0, min(3.999, expo * 4)); lo = int(t); m = t - lo
    c = [pal[lo][k] * (1 - m) + pal[lo + 1][k] * m for k in range(3)]
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
    # TR04 maple (option 3): slight lean, splits at ~2.5 m into 5-6 ascending limbs, wide tiered crown
    'TR04_A': dict(
        trunk=[(0, 0, -.30), (.02, 0, .5), (.08, -.10, 1.2), (.12, -.25, 1.9), (.06, -.38, 2.5), (-.04, -.42, 2.9), (-.02, -.40, 3.2)],
        tr=[.24, .21, .195, .185, .175, .16, .13],
        limbs=[(.80, -100, 40, 5.0, .10, .1), (.86, 20, 48, 4.4, .095, .1), (1.0, 175, 70, 5.4, .09, .0),
               (.70, 120, 44, 4.0, .085, .1), (.92, 70, 58, 4.2, .08, .05), (.76, -40, 52, 3.9, .08, .1)],
        roots=6, burl=(1.4, .8)),
    'TR04_B': dict(   # taller, narrower, upright leader
        trunk=[(0, 0, -.30), (-.02, .02, .6), (.03, -.05, 1.5), (.10, -.12, 2.4), (.08, -.15, 3.2), (.0, -.12, 3.8), (-.02, -.10, 4.2)],
        tr=[.22, .195, .18, .17, .16, .145, .12],
        limbs=[(.72, -90, 55, 4.2, .09, .05), (.82, 40, 60, 4.0, .085, .05), (1.0, 160, 78, 5.6, .085, .0),
               (.64, 150, 50, 3.6, .08, .1), (.90, -20, 66, 3.9, .075, .05)],
        roots=5, burl=(2.2, -1.2)),
    'TR04_C': dict(   # low, broad and leaning, one long side limb
        trunk=[(0, 0, -.30), (.03, -.02, .4), (.12, -.20, 1.0), (.18, -.45, 1.6), (.12, -.70, 2.1), (.0, -.80, 2.45), (-.05, -.80, 2.7)],
        tr=[.26, .23, .21, .195, .18, .165, .14],
        limbs=[(.75, -95, 28, 5.8, .11, .2), (.85, 15, 42, 4.6, .10, .1), (1.0, 170, 74, 5.8, .095, .0),
               (.62, 130, 36, 4.2, .09, .15), (.94, 75, 54, 3.8, .085, .05), (.70, -45, 40, 4.0, .085, .15)],
        roots=7, burl=(1.0, 2.0)),
    # TR08 dead tree (option 1): thick trunk, hollow facing the front, a long limb leaning to one side, two snapped limbs
    'TR08_A': dict(
        trunk=[(0, 0, -.30), (.03, 0, .5), (.10, -.05, 1.3), (.06, -.12, 2.1), (-.06, -.10, 2.9), (-.10, .0, 3.6), (-.05, .05, 4.1)],
        tr=[.34, .29, .26, .235, .21, .18, .14],
        limbs=[(.55, -95, 22, 4.4, .13, .3), (1.0, 170, 74, 2.9, .11, .0), (.80, 40, 52, 3.2, .10, .1),
               (.70, 140, 46, 2.8, .09, .1), (.92, -40, 60, 3.0, .085, .05), (.86, 95, 58, 2.6, .08, .1)],
        roots=8, burl=(2.4, 2.0), hollow=(1.0, 180), salt=1, broken=[(.62, (.5, .7, .45)), (.85, (-.6, -.3, .5))]),
    'TR08_B': dict(   # taller and twisted, split top
        trunk=[(0, 0, -.30), (-.04, .03, .6), (.06, -.04, 1.5), (.14, -.10, 2.5), (.06, -.18, 3.4), (-.08, -.12, 4.2), (-.06, -.05, 4.8)],
        tr=[.31, .27, .24, .22, .195, .17, .13],
        limbs=[(1.0, 160, 72, 2.4, .10, .0), (.94, -30, 66, 2.4, .095, .0), (.70, 70, 40, 3.0, .09, .15),
               (.62, -120, 36, 2.8, .085, .2), (.82, 120, 50, 2.6, .08, .1)],
        roots=7, burl=(3.0, -1.0), hollow=(1.1, 200), salt=3, broken=[(.5, (-.4, .8, .3)), (.78, (.7, -.5, .4))]),
    'TR08_C': dict(   # short, squat and heavily leaning, mostly broken
        trunk=[(0, 0, -.30), (.04, -.02, .4), (.18, -.15, 1.0), (.28, -.40, 1.6), (.20, -.65, 2.2), (.05, -.78, 2.7), (-.02, -.80, 3.0)],
        tr=[.37, .32, .29, .26, .235, .2, .16],
        limbs=[(.60, -100, 20, 4.0, .13, .4), (1.0, 175, 66, 3.6, .11, .0), (.82, 30, 44, 2.8, .10, .1),
               (.92, -60, 54, 2.6, .09, .05), (.74, 120, 38, 2.6, .085, .15)],
        roots=9, burl=(1.6, 1.0), hollow=(.95, 170), broken=[(.45, (.4, .6, .5)), (.7, (-.7, .2, .4)), (.9, (.1, -.8, .5))]),
    # TR09 bamboo clump (option 5): culms tight at the root, splaying upward, foliage in the upper half
    'TR09_A': dict(salt=1, culms=11, height=8.3, clump_r=.30, rad=(.024, .042), leaves=9000),
    'TR09_B': dict(culms=9, height=7.9, clump_r=.28, rad=(.026, .044), lean=7, leaves=8500),
    'TR09_C': dict(culms=13, height=9.0, clump_r=.34, rad=(.018, .032), branch_from=.42, leaves=9000),
    # TR07 plum (option 2): short, strongly twisted trunk forking into two leaders, kinked limbs
    'TR07_A': dict(
        trunk=[(0, 0, -.30), (.05, .0, .35), (.22, -.10, .85), (.06, -.18, 1.35), (-.16, -.06, 1.75), (-.10, .06, 2.1), (.04, .02, 2.35)],
        tr=[.20, .17, .15, .14, .13, .115, .095],
        limbs=[(.62, -80, 40, 2.6, .075, .1), (1.0, 150, 70, 2.8, .08, .0), (.80, 30, 55, 2.3, .065, .1),
               (.90, -150, 60, 2.2, .06, .05), (.70, 100, 48, 2.1, .055, .1)],
        roots=6, burl=(.9, 1.6)),
    'TR07_B': dict(   # leaning, one long low limb
        trunk=[(0, 0, -.30), (.04, .02, .3), (.25, -.05, .7), (.42, -.20, 1.1), (.30, -.42, 1.5), (.10, -.50, 1.85), (.05, -.45, 2.05)],
        tr=[.21, .18, .16, .145, .13, .115, .095],
        limbs=[(.55, -100, 25, 3.0, .08, .3), (1.0, 170, 72, 2.6, .075, .0), (.85, 40, 58, 2.2, .065, .1),
               (.75, -160, 50, 2.1, .06, .1), (.95, 90, 64, 2.0, .055, .05)],
        roots=5, burl=(1.2, -2.0), broken=[(.45, (-.5, .6, .4))]),
    'TR07_C': dict(   # upright, narrow, two tall leaders
        trunk=[(0, 0, -.30), (-.03, .03, .4), (.10, -.06, 1.0), (-.04, -.12, 1.55), (-.14, .02, 2.0), (-.06, .10, 2.4), (.02, .06, 2.7)],
        tr=[.19, .165, .15, .135, .12, .105, .088],
        limbs=[(1.0, 160, 78, 2.6, .075, .0), (.85, -40, 70, 2.5, .07, .0), (.70, 60, 50, 2.0, .06, .1),
               (.60, -130, 45, 2.0, .055, .1), (.92, 110, 62, 1.9, .05, .05)],
        roots=5, burl=(1.5, 2.6)),
}


def mode_of(vid):
    return SPECIES[vid[:4]]['stream']


def build_tree(vid, cfg):
    rg = np.random.default_rng(seed(vid, cfg['salt']) if 'salt' in cfg else seed(vid)); wood, twigs, leaves, collide = Acc(), Acc(), Acc(), []
    H = cfg.get('height', 0)
    # 1. trunk: S curve, ridges (5 + 9 lobes, strongest low), lobed root flare, a burl
    tp = catmull(cfg['trunk'], 46); trs = np.interp(np.linspace(0, 1, 46), np.linspace(0, 1, len(cfg['tr'])), cfg['tr'])
    tw = rg.uniform(0, 6.28); bz, bth = cfg['burl']; hol = cfg.get('hollow')
    if hol:
        Fh = frames(tp); ih = min(range(len(tp)), key=lambda i: abs(tp[i].z - hol[0])); _, nn_, bb_ = Fh[ih]
        dv = Vector((math.cos(math.radians(hol[1])), math.sin(math.radians(hol[1])), 0)); hol = (hol[0], math.atan2(dv.dot(bb_), dv.dot(nn_)))
    def hk(z, th):   # hollow weight: an upright oval opening
        hz, hth = hol; return math.exp(-((z - hz) / .45) ** 4 - (math.atan2(math.sin(th - hth), math.cos(th - hth)) / .6) ** 4)
    def tcol(i, th, a):
        if not hol: return (1, 1, 1, a)
        d = 1 - .92 * hk(tp[i].z, th); return (d, d, d, a * d)
    def tshape(i, th):
        z = tp[i].z; lowk = math.exp(-max(z, 0) / 2.2)
        m = 1 + (.11 * math.cos(5 * th + tw + z * .9) + .05 * math.cos(9 * th - tw * 1.7 + z * 1.6)) * (.45 + .55 * lowk)   # twisted ridges
        if z < .9: m *= 1 + .55 * math.exp(-max(z + .05, 0) / .32) * (.55 + .45 * math.cos(5 * th + tw))
        m *= 1 + .32 * math.exp(-((z - bz) / .26) ** 2 - (math.atan2(math.sin(th - bth), math.cos(th - bth)) / .55) ** 2)
        if hol: m *= 1 - .78 * hk(z, th)   # hollow: a deep inset cavity
        return m
    tF = tube(wood, tp, list(trs), 24 if hol else 20, (0, .04), shape=tshape, ao=lambda i: .55 + .45 * min(1, max(tp[i].z, 0) / 1.2), tip=False, colf=tcol)
    TS = 24 if hol else 20
    # the trunk top is hidden inside the limb fork: cap it with a small dome
    top = tp[-1]; c = len(wood.v); wood.add([top + tF[-1][0] * trs[-1] * .6], [], [(.5, 1)], [(.05, 0)], [(1, 1, 1, 1)])
    base = (len(tp) - 1) * (TS + 1); wood.f += [(base + j, base + j + 1, c) for j in range(TS)]

    def on_trunk(t):
        k = t * (len(tp) - 1); i = min(int(k), len(tp) - 2); f = k - i
        return tp[i].lerp(tp[i + 1], f), tF[i][0], float(trs[i] * (1 - f) + trs[i + 1] * f)

    # surface roots: out from the flare, into the ground (ends at -0.25 m)
    for k in range(cfg['roots']):
        a = 2 * math.pi * k / cfg['roots'] + rg.uniform(-.35, .35) + tw; dvec = Vector((math.cos(a), math.sin(a), 0)); L = rg.uniform(.35, .8) * min(1, float(trs[0]) / .35)   # smaller trees, shorter roots
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
        us = (0, .16, .3, .45, .6, .74, .88, 1.0) if mode_of(vid) == 'shoot' else (0, .28, .55, .8, 1.0)   # plum: more control points = sharper kinks
        pts = [start + out * L * u * (.45 + .55 * math.cos(e)) + UP * L * (math.sin(e) * (1.3 * u - .45 * u * u) - .22 * droop * u ** 3) for u in us]
        zig = SPECIES[vid[:4]].get('zig', .2)   # plum: much stronger kinks in the limbs
        pts = [p + Vector((rg.normal(0, .08), rg.normal(0, .08), rg.normal(0, .05))) * L * zig * (i > 0) for i, p in enumerate(pts)]
        lp = catmull(pts, 22 if len(pts) > 5 else 16); lr = list(np.linspace(r0, r0 * .22, len(lp)) ** 1.0)
        lr = [r * (1 + .25 * math.exp(-i / 2.0)) for i, r in enumerate(lr)]   # swelling at the fork
        tube(wood, lp, lr, 10, (.05, .3), phase=li / 8, spin=0.0 if mode_of(vid) == 'hang' else rg.uniform(0, .6))
        anchors.append((lp[-1], (lp[-1] - lp[-4]).normalized(), lr[-1], li, lp))
        nsec = (3 if L > 4.6 else 2) if mode_of(vid) == 'spray' else (2 if L > 2.0 else 1) if mode_of(vid) == 'shoot' else (2 if L > 2.5 else 1) if mode_of(vid) == 'twig' else (2 if L > 3.8 else 1)
        for si in range(nsec):
            ts = .42 + .5 * (si + rg.uniform(-.15, .15)) / nsec; k = int(ts * (len(lp) - 1)); sp = lp[k]; sd = (lp[k + 1] - lp[k]).normalized()
            side = sd.cross(UP).normalized() * (1 if (si + li) % 2 else -1)
            sdir = (sd * .55 + side * rg.uniform(.55, .9) + UP * rg.uniform(.25, .55)).normalized(); SL = L * rg.uniform(.32, .46)
            spts = [sp, sp + sdir * SL * .4 + UP * SL * .1, sp + sdir * SL * .8 + UP * SL * .05, sp + sdir * SL + (sdir * .3 - UP * .4).normalized() * SL * .18]
            sq = catmull(spts, 9); sr = list(np.linspace(lr[k] * .55, lr[k] * .16, 9))
            tube(wood, sq, sr, 6, (.3, .55), phase=li / 8 + si * .03, spin=0.0 if mode_of(vid) == 'hang' else rg.uniform(0, 1.0))   # turned section: not parallel to the limb
            anchors.append((sq[-1], (sq[-1] - sq[-3]).normalized(), sr[-1], li, sq))
    brk = cfg.get('broken')
    for (bt, bdir) in ([(.62, (.55, .6, .55))] if brk is True else (brk or [])):   # snapped limb stubs with a ragged end
        p0, td, rt = on_trunk(bt); d0 = Vector(bdir).normalized()
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
    sp = SPECIES[vid[:4]]; mode = sp['stream']
    nleaf = 0; nflower = 0; streams = []
    for ai, (ap, ad, ar, li, bp) in enumerate(anchors):
        layer = 'Front' if ap.y < cy else 'Back'; ns = int(rg.integers(*sp['ns'])); twist = ai * .83 + (.4 if layer == 'Front' else 0)
        for si in range(ns):
            nb = 3; heading = (si % nb) * 2.0944 + twist + rg.normal(0, .22); side = Vector((math.cos(heading), math.sin(heading), 0))   # 3 bundles per anchor: gaps between
            if mode == 'hang': d = (ad * .55 + side * .55 + UP * rg.uniform(.35, .8)).normalized()   # (drawn first: keeps the TR06 random sequence)
            reach = .72 if mode == 'hang' else sp.get('reach', .6)
            u = 1 - reach * (si / max(ns - 1, 1)) ** .8 * rg.uniform(.7, 1.0); k = min(int(u * (len(bp) - 1)), len(bp) - 1)   # along the outer part of the branch
            p = bp[k] + side * rg.uniform(.02, .12); path = [p.copy()]; ds = .16
            if mode == 'hang':   # willow: arch up and out, then hang down in curtains
                hem = max(rg.uniform(.3, 1.9) + (.0 if layer == 'Front' else .3), .3)   # where the curtain ends above the ground
                g = rg.uniform(1.2, 2.0); sway = Vector((rg.normal(0, .02), rg.normal(0, .02), 0)); Lmax = rg.uniform(2.2, 5.0)
                while len(path) * ds < Lmax and p.z > hem:
                    d = (d + Vector((0, 0, -g * ds)) + sway).normalized(); p = p + d * ds; path.append(p.copy())
            elif mode == 'spray':   # maple: broad, nearly level sprays that fan out in tiers, slight lift then droop at the tip
                d = (ad * .45 + side * .7 + UP * rg.uniform(-.3, .55)).normalized(); Lmax = rg.uniform(1.0, 2.2); curl = rg.normal(0, .6)
                while len(path) * ds < Lmax:
                    d = (Quaternion(UP, curl * ds) @ d + Vector((0, 0, -.25 * ds))).normalized(); p = p + d * ds; path.append(p.copy())
            elif mode == 'shoot':   # plum: short angular zig-zag shoots, mostly upward, a few straight whips
                d = (ad * .4 + side * .5 + UP * rg.uniform(.5, 1.0)).normalized(); Lmax = rg.uniform(.4, 1.2); ds = .12
                while len(path) * ds < Lmax:
                    if rg.random() < .3: d = (Quaternion(Vector(rg.normal(size=3)).normalized(), rg.uniform(.35, .7)) @ d + UP * .25).normalized()   # a sharp turn
                    p = p + d * ds; path.append(p.copy())
            else:   # 'twig': dead tree, outward and up with jitter (geometry only)
                d = (ad * .6 + side * .5 + UP * rg.uniform(.15, .55)).normalized(); Lmax = rg.uniform(.6, 1.6); ds = .14
                while len(path) * ds < Lmax:
                    d = (d + Vector(rg.normal(0, .12, 3))).normalized(); p = p + d * ds; path.append(p.copy())
            if len(path) < 3: continue
            streams.append((path, ai, layer))
    total_len = sum(len(s[0]) for s in streams) * .16
    lb = cfg.get('leaves', sp['leaves']); per_m = lb / total_len if lb else 0
    pal = sp['palette']; r0t, r1t = sp['twig_r']
    for path, ai, layer in streams:
        n = len(path); step = 6 if mode == 'hang' else 2
        gp = path[::step] + ([path[-1]] if (n - 1) % step else [])   # twig geometry; the leaves sit on this polyline
        cum = np.concatenate([[0], np.cumsum([(gp[j + 1] - gp[j]).length for j in range(len(gp) - 1)])])
        tube(twigs, gp, list(np.linspace(r0t, r1t, len(gp))), 4 if mode == 'twig' else 3, (.55, .9), phase=ai / 20, spin=rg.uniform(0, 1.5) if mode == 'twig' else 0.0)
        if mode == 'twig':   # dead tree: each twig forks twice more (dendritic third tier), the forks curve upward
            def fork(start, dirv, length, r, depth):
                pts = [start]; dv = dirv
                for j in range(3):
                    dv = (dv + UP * .12 + Vector(rg.normal(0, .1, 3))).normalized(); pts.append(pts[-1] + dv * length / 3)
                tube(twigs, pts, list(np.linspace(r, max(r * .45, .0025), len(pts))), 3, (.7, .95), phase=ai / 20, spin=rg.uniform(.4, 1.7))   # turned section: no faces parallel to the parent twig
                if depth:
                    tw0 = rg.uniform(0, 6.28)   # both children share the fork plane, one each side: they never coincide
                    for sgn in (-1, 1):
                        ax = dv.cross(UP if abs(dv.z) < .9 else Vector((1, 0, 0))).normalized()
                        cd = (Quaternion(ax, sgn * rg.uniform(.35, .7)) @ dv); cd = (Quaternion(dv, tw0) @ cd).normalized()
                        fork(pts[2] + (pts[3] - pts[2]) * rg.uniform(.2, .8), cd, length * rg.uniform(.5, .7), r * .55, depth - 1)
            mid = gp[len(gp) // 2]; dd = (gp[-1] - gp[0]).normalized()
            fork(gp[-1], (dd + UP * .2).normalized(), (n - 1) * .14 * .48, r1t * 1.4, 2)
            if len(gp) > 2: fork(mid, (Quaternion(dd, rg.uniform(0, 6.28)) @ (dd.cross(UP).normalized() if abs(dd.z) < .9 else Vector((1, 0, 0))) + dd).normalized(), (n - 1) * .14 * .45, r1t * 1.2, 1)
            continue
        Lr, Wr, Ar, sa, droop, flat = sp['leaf']
        L = (n - 1) * .16; k = int(per_m * L * rg.uniform(.85, 1.15))
        for q in range(k):
            t = .06 + .94 * (q + rg.uniform(0, 1)) / k; sl = t * cum[-1]; i = min(int(np.searchsorted(cum, sl)) - 1, len(gp) - 2); i = max(i, 0)
            f = (sl - cum[i]) / max(cum[i + 1] - cum[i], 1e-6); at = gp[i].lerp(gp[i + 1], f); tg = (gp[i + 1] - gp[i]).normalized()
            ph = q * 2.39996 + ai; around = tg.cross(UP if abs(tg.z) < .9 else Vector((1, 0, 0))).normalized()
            around = Quaternion(tg, ph) @ around
            aa = math.radians(rg.uniform(*Ar)); ld = (tg * math.cos(aa) + around * math.sin(aa)).normalized()
            ld = (ld + Vector((0, 0, -droop))).normalized()
            Ll = rg.uniform(*Lr); Wl = Ll * rg.uniform(*Wr)
            h = (at.z - zmin_c) / (zmax_c - zmin_c); o = min(1, Vector((at.x - cx, at.y - cy, 0)).length / rmax)
            expo = max(0, min(1, .5 * h + .38 * o + .12 * t + rg.uniform(-.06, .06)))
            occl = .45 + .55 * max(expo, o * .9)
            if sp.get('flowers') and rg.random() < sp['flowers']:   # plum blossom: a small pale five-point disc facing out
                Fl = rg.uniform(.045, .07); fc = sp['flower_col'][int(rg.integers(0, 3))]
                leaf(leaves, at, ld, around.cross(ld), Fl, Fl * .95, (*fc, occl), .9 + .1 * t, ai / 20, cup=.25, sa=.5); nflower += 1
                continue
            side_v = ld.cross(UP).normalized() if flat and abs(ld.z) < .95 else around.cross(ld)
            if mode != 'hang': side_v = Quaternion(ld, rg.uniform(-.35, .35)) @ side_v   # no two leaves share a plane (the petiole stays on the twig)
            leaf(leaves, at, ld, side_v, Ll, Wl, leaf_colour(expo, occl, pal), .9 + .1 * t, ai / 20, sa=sa, lift=0.0 if mode == 'hang' else ((q % 3) - 1) * .0025)
            nleaf += 1
    return wood, twigs, leaves, collide, anchors, streams, (nleaf, nflower)


BAMBOO_PAL = [(.030, .068, .030), (.055, .115, .045), (.095, .175, .060), (.160, .245, .080), (.245, .315, .110)]


def build_bamboo(vid, cfg):
    """TR09 bamboo clump: culms of uneven thickness with node rings and an outward arch, branches from the upper nodes, drooping
    leaf fans at each spray joint. Returns the same tuple as build_tree; the culms go in `twigs` so they take the bamboo
    (vertex-colour) material, the branches and the root mound go in `wood` (bark)."""
    rg = np.random.default_rng(seed(vid, cfg['salt']) if 'salt' in cfg else seed(vid)); wood, culms, leaves, collide = Acc(), Acc(), Acc(), []
    n = cfg['culms']; Hmax = cfg['height']; R = cfg.get('clump_r', .34)
    mound = [Vector((0, 0, -.3)), Vector((0, 0, -.05)), Vector((0, 0, .06)), Vector((0, 0, .13))]   # low root mound, buried to -0.3 m
    tube(wood, mound, [R + .2, R + .16, R + .02, .12], 16, (0, 0), ao=lambda i: .5, tip=True)
    streams, anchors = [], []; nleaf = 0
    order = rg.permutation(n)
    bases = []
    for ci in range(n):
        for _try in range(60):   # culm feet keep >= 0.1 m apart, so neighbouring culms never pass through each other
            a = 2 * math.pi * ci / n + rg.normal(0, .3); r = R * math.sqrt(rg.uniform(.05, 1)); base = Vector((r * math.cos(a), r * math.sin(a), -.25))
            if all((base - b).length >= .10 for b in bases): break
        bases.append(base)
        out = Vector((math.cos(a), math.sin(a), 0)); H = Hmax * (1 - .28 * r / R) * rg.uniform(.82, 1.0)
        tilt = math.radians(rg.uniform(2, 9) + cfg.get('lean', 0) * (out.x > 0)); arch = rg.uniform(.04, .12)
        rad = rg.uniform(*cfg.get('rad', (.016, .034))); age = rg.random()   # older culms are yellower
        nodes, z = [], .0
        while z < H:
            nodes.append(z); z += rg.uniform(.25, .35) * (1 + .4 * z / H)
        def P(zz, base=base, out=out, H=H, tilt=tilt, arch=arch):
            u = zz / H; return base + UP * (zz + .25) + out * H * (math.sin(tilt) * u + arch * u * u)
        path, radii, nodeflag = [], [], []
        for zz in nodes:
            for dz, bulge in ((0, 1.07), (.025, 1.0)):   # the node ring, then the internode just above it
                path.append(P(zz + dz)); radii.append(rad * (1 - .72 * (zz / H) ** 1.6) * bulge); nodeflag.append(dz == 0)
        g0 = (.16 + .10 * age, .30 + .06 * age, .09 + .02 * age)
        def ccol(i, th, aa, nodeflag=nodeflag, path=path, g0=g0):
            zz = path[i].z; dry = max(0, 1 - zz / .6)   # dry sheath colour at the foot
            c = [g0[k] * (1 - dry) + (.30, .24, .14)[k] * dry for k in range(3)]
            if nodeflag[i]: c = [x * .78 for x in c]
            return (*c, .6 + .4 * min(1, max(zz, 0) / 2))
        tube(culms, path, radii, 8, (0, .6), phase=float(order[ci]) / n, colf=ccol, spin=rg.uniform(0, .78))
        m = max(4, len(path) // 3); collide.append(('culm', path[:m], radii[:m]))
        for k, zz in enumerate(nodes):   # branches from the upper nodes, alternating sides
            if zz < H * cfg.get('branch_from', .5): continue
            side = Quaternion(UP, (k % 2) * math.pi + rg.normal(0, .5)) @ out
            for b in range(1 if rg.random() < .3 else 2):
                side_b = Quaternion(UP, b * rg.uniform(1.2, 2.2)) @ side
                d = (side_b + UP * rg.uniform(.3, .7) + Vector(rg.normal(0, .25, 3))).normalized(); L = rg.uniform(.7, 1.6) * (1 - .35 * zz / H)
                p = P(zz); bp = [p.copy()]
                for j in range(5):
                    d = (d + Vector((0, 0, -.18))).normalized(); p = p + d * L / 5; bp.append(p.copy())
                tube(wood, bp, list(np.linspace(.006, .002, len(bp))), 3, (.6, .8), phase=float(order[ci]) / n)
                streams.append((bp, ci, 'Front' if p.y < 0 else 'Back'))
                if len(anchors) < 20 and b == 0 and k % 3 == 0: anchors.append((p, d, .004, ci, bp))
    zs = [s[0][-1].z for s in streams]; zmin_c, zmax_c = min(zs) - 1.0, max(zs) + .5
    rmax = max(Vector((s[0][-1].x, s[0][-1].y, 0)).length for s in streams) + .5
    per = cfg.get('leaves', 6000) / max(len(streams) * 5, 1)
    for bp, ci, layer in streams:   # leaf fans: 5 joints per spray, narrow leaves hanging from each
        for jt in (.2, .4, .6, .8, 1.0):
            at = bp[min(len(bp) - 1, int(jt * (len(bp) - 1)))]; base_d = (bp[-1] - bp[0]).normalized()
            nq = max(2, int(round(per * rg.uniform(.7, 1.3))))
            for q in range(nq):
                ang = -1.6 + 3.2 * (q + rg.uniform(.15, .85)) / nq; ld = ((Quaternion(UP, ang) @ base_d) * .7 + Vector((0, 0, -1)) * rg.uniform(.35, .9)).normalized()
                Ll = rg.uniform(.22, .32); Wl = Ll * rg.uniform(.13, .17)   # enlarged like the willow leaves: reads as a leaf mass at game distance
                h = (at.z - zmin_c) / (zmax_c - zmin_c); o = min(1, Vector((at.x, at.y, 0)).length / rmax)
                expo = max(0, min(1, .55 * h + .35 * o + rg.uniform(-.08, .08))); occl = .45 + .55 * max(expo, o * .9)
                sv = ld.cross(UP).normalized() if abs(ld.z) < .98 else Vector((1, 0, 0))
                kk = min(len(bp) - 1, int(jt * (len(bp) - 1))); back = (bp[kk - 1] - bp[kk]).normalized()
                sv = Quaternion(ld, (.3 if q % 2 else -.3) + rg.uniform(-.2, .2)) @ sv; atj = at + back * rg.uniform(0, .04)   # fan leaves: own plane and petiole each, still on the spray
                leaf(leaves, atj, ld, sv, Ll, Wl, leaf_colour(expo, occl, BAMBOO_PAL), .95, ci / n, cup=.12, sa=.35, lift=((q % 3) - 1) * .0025)
                nleaf += 1
    return wood, culms, leaves, collide, anchors, streams, (nleaf, 0)


def lod_leaves(vid, streams, anchors, frac, scale, budget):
    """LOD1/2 leaves: fewer, larger leaves on the same streams (same colours)."""
    rg = np.random.default_rng(seed(vid, 'lod', frac)); acc = Acc(); sp = SPECIES[vid[:4]]
    if not sp['leaf']: return acc
    Lr, Wr, Ar, sa, droop, flat = sp['leaf']; pal = sp['palette']
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
            ld = ((tg * .8 + around * .5).normalized() + Vector((0, 0, -droop))).normalized()
            Ll = rg.uniform(*Lr) * scale ** .75; Wl = Ll * rg.uniform(Wr[0] - .01, Wr[1] + .01) * scale ** .25
            h = (at.z - zmin_c) / (zmax_c - zmin_c); o = min(1, Vector((at.x - cx, at.y - cy, 0)).length / rmax)
            expo = max(0, min(1, .5 * h + .38 * o + .12 * t)); occl = .45 + .55 * max(expo, o * .9)
            if sp.get('flowers') and rg.random() < sp['flowers']:
                Fl = .06 * scale ** .75; leaf(acc, at, ld, around.cross(ld), Fl, Fl * .95, (*sp['flower_col'][q % 3], occl), .9 + .1 * t, ai / 20, cup=.25, sa=.5); continue
            side_v = ld.cross(UP).normalized() if flat and abs(ld.z) < .95 else around.cross(ld)
            leaf(acc, at, ld, side_v, Ll, Wl, leaf_colour(expo, occl, pal), .9 + .1 * t, ai / 20, sa=sa)
    return acc


def resolve_coplanar(acc, leaf_start, eps=.003, passes=10):
    """Find overlapping parallel triangles (the QA z-fighting test) and break them. Leaves (5 vertices each, the leaf Acc holds
    only leaves) turn 0.15 rad about their own petiole-tip line, so they stay on the twig; bark faces move 1.5 mm along their normal."""
    from mathutils.bvhtree import BVHTree
    fixed = 0
    for _ in range(passes):
        V = [Vector(p) for p in acc.v]; T = []; own = []
        for fi, f in enumerate(acc.f):
            for k in range(1, len(f) - 1): T.append((f[0], f[k], f[k + 1])); own.append(fi)
            if len(f) == 4: T += [(f[1], f[2], f[3]), (f[1], f[3], f[0])]; own += [fi, fi]   # quads: both diagonals (the importer may split the other way)
        bvh = BVHTree.FromPolygons(V, T, epsilon=0.0); N = [(V[b] - V[a]).cross(V[c] - V[a]) for a, b, c in T]
        hit = set()
        for ti, (a, b, c) in enumerate(T):
            if N[ti].length < 1e-12: continue
            n = N[ti].normalized(); cen = (V[a] + V[b] + V[c]) / 3
            for q in (cen, cen.lerp(V[a], .6), cen.lerp(V[b], .6), cen.lerp(V[c], .6)):
                for _, _, tj, _ in bvh.find_nearest_range(q, eps):
                    if tj is None or tj <= ti or set(T[ti]) & set(T[tj]): continue
                    if N[tj].length > 1e-12 and abs(n.dot(N[tj].normalized())) > .995: hit.add(own[tj])   # wider than the QA test (.999, 1 mm): FBX round-trip margin
        if not hit: break
        for L0 in {leaf_start + (min(acc.f[fi]) - leaf_start) // 5 * 5 for fi in hit if min(acc.f[fi]) >= leaf_start}:   # leaves: turn
            p0 = Vector(acc.v[L0]); ax = (Vector(acc.v[L0 + 2]) - p0).normalized(); R = Matrix.Rotation(.15, 3, ax)
            for i in range(L0, L0 + 5): acc.v[i] = p0 + R @ (Vector(acc.v[i]) - p0)
            fixed += 1
        for fi in hit:   # bark faces: push out
            f = acc.f[fi]
            if min(f) >= leaf_start: continue
            a, b, c = (Vector(acc.v[i]) for i in f[:3]); n = (b - a).cross(c - a)
            if n.length > 1e-12:
                for i in f: acc.v[i] = Vector(acc.v[i]) + n.normalized() * .0015
            fixed += 1
    return fixed


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
    bpy.ops.wm.read_factory_settings(use_empty=True); sp = SPECIES[vid[:4]]; bark, lfm = materials(sp); cfg = VARIANTS[vid]
    bam = vid.startswith('TR09')
    wood, twigs, leaves, collide, anchors, streams, (nleaf, nflower) = (build_bamboo if bam else build_tree)(vid, cfg)
    tw_mat = bamboo_material() if bam else bark
    lb = cfg.get('leaves', sp['leaves']); l1 = lod_leaves(vid, streams, anchors, .25, 1.9, lb); l2 = lod_leaves(vid, streams, anchors, .0625, 3.6, lb)
    col = Acc()
    if bam:   # one simple cylinder round the clump base (dense planting: cheap collision)
        Rc = cfg.get('clump_r', .34) + .08; tube(col, [Vector((0, 0, 0)), Vector((0, 0, 1)), Vector((0, 0, 2.2))], [Rc, Rc, Rc * .9], 8, (0, 0), tip=False)
    else:
        for _, path, radii in collide: tube(col, path, list(np.asarray(radii) * 1.05), 8, (0, 0), tip=False)
    if not vid.startswith('TR06'):   # (TR06 is the reviewed sample and already passes: left untouched)
        al = Acc(); al.add(wood.v, wood.f, wood.uv, wood.uv2, wood.col); nw = len(wood.v); al.add(twigs.v, twigs.f, twigs.uv, twigs.uv2, twigs.col); nt = len(al.v)
        al.add(leaves.v, leaves.f, leaves.uv, leaves.uv2, leaves.col)
        fx = resolve_coplanar(al, nt); wood.v = al.v[:nw]; twigs.v = al.v[nw:nt]; leaves.v = al.v[nt:]
        print('COPLANAR fixed', fx, flush=True)
    for a in (wood, twigs, leaves, l1, l2, col): place(a)
    src = wood
    if not sp['leaf'] or bam:   # leafless twigs / bamboo culms carry the silhouette: LOD1/2 decimate wood + twigs together
        src = Acc(); src.add(twigs.v, twigs.f, twigs.uv, twigs.uv2, twigs.col); src.add(wood.v, wood.f, wood.uv, wood.uv2, wood.col)
    wood_o = wood.obj(f'{vid}_Wood', bark); srcm = tw_mat if bam else bark
    w1 = src.obj('w1', srcm); w2 = src.obj('w2', srcm); wt = src.tris()
    print("PARTS wood", wood.tris(), "twigs", twigs.tris(), "leaves", leaves.tris(), "streams", len(streams), "anchors", len(anchors), flush=True)
    lod0 = join([wood_o, twigs.obj(f'{vid}_Twigs', tw_mat)] + ([leaves.obj(f'{vid}_Leaves', lfm)] if leaves.f else []), f'{vid}_LOD0')
    if l1.f:
        lo1 = l1.obj('l1', lfm); decimate(w1, (14600 - tris(lo1)) / wt); lod1 = join([w1, lo1], f'{vid}_LOD1')
        lo2 = l2.obj('l2', lfm); decimate(w2, (3900 - tris(lo2)) / wt); lod2 = join([w2, lo2], f'{vid}_LOD2')
    else:
        decimate(w1, min(14600, wt * .45) / wt); lod1 = w1; lod1.name = lod1.data.name = f'{vid}_LOD1'
        decimate(w2, 3900 / wt); lod2 = w2; lod2.name = lod2.data.name = f'{vid}_LOD2'
    co = col.obj(f'{vid}_Collision', bark, smooth=False); co.data.materials.clear()
    vs = np.array([v.co[:] for v in lod0.data.vertices]); mn, mx = Vector(vs.min(0)), Vector(vs.max(0)); dims = mx - mn
    for o in (lod1, lod2, co): o.hide_render = True
    lod3 = far_card(vid, (mn, mx))
    for o in (lod1, lod2, co): o.hide_render = False
    T = [tris(o) for o in (lod0, lod1, lod2, lod3)]
    assert T[0] <= 60000 and T[1] <= 15000 and T[2] <= 4000 and T[3] <= 200, f'{vid} over budget {T}'
    h0, h1 = sp['h']; assert h0 <= mx.z <= h1, f'{vid} height {mx.z:.2f} m outside {h0}-{h1} m'
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
            'block': sp['block'], 'species': sp['name'], 'heightRange_m': list(sp['h']), 'windBaseMax': .13 if bam else .05, 'leanSide': '+X（樹幹和長枝斜向 +X）' + ('，擺放時 +X 朝水面' if vid.startswith('TR06') else ''),
            'dimensions_m': [round(float(d), 3) for d in dims], 'bounds_min_m': [round(float(v), 3) for v in mn], 'bounds_max_m': [round(float(v), 3) for v in mx],
            'origin': '樹幹底部中心，z = 0 是地面；根往下埋 0.3 m',
            'lods': [{'lod': i, 'triangles': T[i], 'materials': sorted({m.name for m in o.data.materials})} for i, o in enumerate((lod0, lod1, lod2, lod3))],
            'structure': {'culms': cfg.get('culms', 0), 'mainLimbs': len(cfg.get('limbs', [])), 'canopyAnchors': len(anchors), 'anchorsFrontWaterSide': front, 'anchorsBack': len(anchors) - front,
                          'twigStreams': len(streams), 'leavesLOD0': nleaf, 'blossomsLOD0': nflower, 'leafVertices': 5},
            'vertexData': {'colour': 'RGB = 葉色（依樹冠內高度與內外連續混色），A = 樹冠遮蔽；樹皮 RGB 白、A = 根部遮蔽',
                           'uv2': 'x = 風權重（主幹 0、主枝 0.05–0.3、次枝 0.3–0.55、垂枝 0.55–0.9、葉 0.9–1.0），y = 葉冠錨點相位'},
            'materials': sorted({m.name for o in (lod0, lod1, lod2, lod3) for m in o.data.materials}), 'barkTint': list(sp.get('bark_tint', (1, 1, 1))),
            'textures': {'T_TreeV2_Bark_Albedo': '1024x1024', 'T_TreeV2_Bark_Normal': '1024x1024', f'T_{vid}_Far': '1024x512 (LOD3 only, alpha)'},
            'seedSalt': cfg.get('salt'), 'collision': f'{vid}_Collision（樹幹下段，8 邊管）', 'seed': f'zlib.crc32("{vid}")',
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
