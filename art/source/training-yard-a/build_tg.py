"""青溪 · 11/14 A 包 A 批：演武場重做（TG01–TG06，Johnnnny0823），先交 TG01 木人樁樣品。
Exports go to art/exports/training-yard-a. Package: docs/execution/2026-11-14/A-120h-roads-yard-and-mountain-street.md,
placed in A1 (the yard east of the square, concept views art/references/blocks/A1 V1 and V3).

Village (river-valley) language as the 11/11 valley commons: old dark timber, grey-blue river stone, hemp rope, dark iron;
no mountain-city granite white, no bronze. One shared 2048 sheet T_TrainingYard_* (M_TrainingYard_Trim) in the MC01 strip
layout, so the MC01 helpers (box, beam, tube, lathe, chisel ...) work unchanged; strips repainted for the yard:
granite* = river stone, plank / beam / oldwood = weathered wood, tile = wood polished dark by hands (arm ends, grips),
tile_moss = straw (targets), cloth = twisted hemp rope, paper = faded plain banner cloth, bronze = dark iron.
Origin: footprint centre, z = 0 on the ground, Blender -Y = front. LOD1 <= 50 %, LOD2 <= 15 %. Groups: main, Detail_Moss.
Each module is modelled after its picked AI three-view in art/references/<ID>/ ("選用：" in prompt.txt).

    blender -b --factory-startup -P art/source/training-yard-a/build_tg.py -- sheet TG01
"""
import bpy, bmesh, json, math, sys, random, zlib
from pathlib import Path
from mathutils import Vector, Matrix
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'art/source/mountain-street-houses-a'))
import build_mc01 as mc
from build_mc01 import box, beam, lathe, tube, chisel, bevel, apply, moss_tuft

PKG = 'training-yard-a'; OUT = ROOT / 'art/exports' / PKG; TEX = ROOT / 'art/textures' / PKG
for p in (OUT, TEX): p.mkdir(parents=True, exist_ok=True)
PACKAGE = 'docs/execution/2026-11-14/A-120h-roads-yard-and-mountain-street.md'
SHEET_NAME = 'T_TrainingYard'; MAT_NAMES = ('M_TrainingYard_Trim', 'M_TrainingYard_Glow')
LIMITS = {'TG01': (1.0, 1.0, 2.0)}

# ------------------------------------------------------------------ yard sheet (MC01 strip layout, village colours)
def sources():
    S = mc.sources(); fbm, lerp, X, Y = mc.fbm, mc.lerp, mc.X, mc.Y
    def recolour(name, lo, hi, keep=.35):
        a, h, s, r, m, g = S[name]; lum = a.mean(2, keepdims=True); lum = (lum - lum.min()) / max(1e-6, lum.max() - lum.min())
        new = np.asarray(lo)[None, None, :] * (1 - lum) + np.asarray(hi)[None, None, :] * lum
        S[name] = (new * (1 - keep) + a * keep * (np.asarray(hi) / np.maximum(a.mean((0, 1)), 1e-3)).clip(0, 2) * .5 + new * keep * .5, h, s, r, m, g)
    recolour('granite', (.26, .28, .28), (.52, .55, .53))          # river stone, same as the valley sheet (#113)
    recolour('granite_moss', (.20, .23, .20), (.42, .45, .40))
    recolour('granite_top', (.32, .34, .33), (.56, .58, .55))
    recolour('plank', (.17, .13, .10), (.40, .33, .26), keep=.5)   # weathered dark old wood
    recolour('beam', (.15, .11, .085), (.34, .27, .21), keep=.5)
    recolour('oldwood', (.24, .21, .18), (.46, .41, .35), keep=.5)
    soft, warp = fbm(2, 3), fbm(2, 2)
    # polished wood: the same grain, darker and warmer, much smoother (hands rub the arm ends and grips)
    a, h, s, r, m, g = S['beam']
    S['tile'] = (lerp((.12, .075, .05), (.30, .19, .11), np.clip(a.mean(2) / max(1e-3, a.mean()) * .5, 0, 1)), h * .4, 1.0, .42, 0, 0)
    # straw: long golden-grey strands along U, a few dark ones
    strand = (.5 + .5 * np.sin(math.tau * (Y * 60 + warp * 2))) ** 3; dk = np.clip((fbm(20, 2, aniso=1 / 10) - .7) * 4, 0, 1)
    S['tile_moss'] = (lerp((.36, .30, .17), (.66, .57, .36), np.clip(.4 + .4 * strand + .2 * soft - .4 * dk, 0, 1)), strand + .5 * dk, 2.2, .9, 0, 0)
    # hemp rope: plies twisting diagonally (16 per 0.25 m), dark grooves between them, fibre fuzz
    ply = .5 + .5 * np.sin(math.tau * (X * 16 + Y * 4)); groove = np.clip(1 - ply * 3, 0, 1)
    S['cloth'] = (lerp((.30, .25, .17), (.58, .50, .36), np.clip(ply * .8 + .2 * fbm(30, 2), 0, 1)) * (1 - .45 * groove)[..., None], ply, 1.8, .92, 0, 0)
    # faded plain banner cloth: off-white going ochre, a little grime toward the lower edge, no marks of any kind
    S['paper'] = (lerp((.62, .56, .45), (.80, .75, .64), np.clip(.6 * soft + .4 * fbm(8, 2), 0, 1)) * (1 - .2 * Y ** 2)[..., None], .3 * fbm(16, 2), .6, .95, 0, 0)
    # dark iron instead of bronze
    S['bronze'] = (lerp((.07, .07, .07), (.17, .16, .15), fbm(6, 3)) + np.clip((fbm(8, 3) - .62) * 2.5, 0, 1)[..., None] * np.array([.12, .05, .01]), S['bronze'][1], S['bronze'][2], .62, .55, 0)
    return S

def make_sheet():
    S = sources(); R = mc.R; SH = mc.SHEET
    A = np.zeros((SH, SH, 3), np.float32); N = np.zeros((SH, SH, 3), np.float32); MS = np.zeros((SH, SH, 4), np.float32); EM = np.zeros((SH, SH, 3), np.float32)
    for name, h in mc.STRIPS:
        alb, hgt, s, r, m, glow = S[name]; k = R // h
        alb = np.broadcast_to(alb, (R, R, 3)); hgt = np.broadcast_to(hgt, (R, R))
        a = alb.reshape(h, k, h, k, 3).mean((1, 3)); hh = hgt.reshape(h, k, h, k).mean((1, 3))
        dx = (np.roll(hh, -1, 1) - np.roll(hh, 1, 1)) * s; dy = (np.roll(hh, -1, 0) - np.roll(hh, 1, 0)) * s
        n = np.dstack([-dx, -dy, np.ones_like(hh)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
        reps = SH // h; v0 = mc.V0[name][0]
        A[v0:v0 + h] = np.tile(a, (1, reps, 1)); N[v0:v0 + h] = np.tile(n * .5 + .5, (1, reps, 1))
        MS[v0:v0 + h, :, 0] = m; MS[v0:v0 + h, :, 3] = 1 - r
        if glow: EM[v0:v0 + h] = np.tile(a, (1, reps, 1))
    for nm, arr, data in (('Albedo', A, False), ('Normal', N, True), ('MetallicSmoothness', MS, True), ('Emission', EM, False)):
        im = bpy.data.images.new(f'{SHEET_NAME}_{nm}', SH, SH, alpha=arr.shape[2] == 4)
        if data: im.colorspace_settings.name = 'Non-Color'
        px = np.ones((SH, SH, 4), np.float32); px[..., :arr.shape[2]] = np.clip(arr, 0, 1); im.pixels.foreach_set(px.ravel())
        im.filepath_raw = str(TEX / f'{SHEET_NAME}_{nm}.png'); im.file_format = 'PNG'; im.save()

def load_sheet():
    ims = {k: bpy.data.images.load(str(TEX / f'{SHEET_NAME}_{n}.png')) for k, n in
           (('alb', 'Albedo'), ('nrm', 'Normal'), ('ms', 'MetallicSmoothness'), ('em', 'Emission'))}
    for k in ('nrm', 'ms'): ims[k].colorspace_settings.name = 'Non-Color'
    for nm, glow in zip(MAT_NAMES, (0, 1)):
        mat = bpy.data.materials.new(nm); mat.use_nodes = True; nt = mat.node_tree; bs = nt.nodes['Principled BSDF']
        def tex(im): t = nt.nodes.new('ShaderNodeTexImage'); t.image = im; return t
        nt.links.new(tex(ims['alb']).outputs['Color'], bs.inputs['Base Color'])
        ms = tex(ims['ms']); sep = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(ms.outputs['Color'], sep.inputs['Color'])
        inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1
        nt.links.new(ms.outputs['Alpha'], inv.inputs[1]); nt.links.new(inv.outputs[0], bs.inputs['Roughness']); nt.links.new(sep.outputs['Red'], bs.inputs['Metallic'])
        nm_ = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(tex(ims['nrm']).outputs['Color'], nm_.inputs['Color']); nt.links.new(nm_.outputs['Normal'], bs.inputs['Normal'])
        if glow:
            nt.links.new(tex(ims['em']).outputs['Color'], bs.inputs['Emission Color']); bs.inputs['Emission Strength'].default_value = 4.0
        mc.MAT[glow] = mat

SOCKETS = []
def socket(name, loc, rot=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); e.empty_display_type = 'ARROWS'; e.empty_display_size = .2
    e.location = loc; e.rotation_euler = rot; bpy.context.scene.collection.objects.link(e); SOCKETS.append(e); return e

def tuft(name, rg, at, scale=1.0):
    o = moss_tuft(name, rg); o.data.transform(Matrix.Translation(at) @ Matrix.Scale(scale, 4)); return o

def rubble_block(name, size, c, strip, seed, amt=.03, rot=0.0):
    o = box(name, size, (0, 0, 0), strip, 'Main', bev=0, cuts=1 if max(size) > .3 else 0)
    chisel(o, amt, 2.4, seed, keep_bed=True); bevel(o, min(.035, min(size) * .22), 2, 30)
    o.data.transform(Matrix.Translation(c) @ Matrix.Rotation(rot, 4, 'Z')); return o

# ------------------------------------------------------------------ TG01 wooden training dummy (three-view option 3)
def TG01():
    """木人樁 (picked three-view option 3): a thick round hardwood post set in a ring of eight rough river stones; two upper
    arms angled forward and out, one straight middle arm, one bent leg near the foot, all through square mortises with dark
    iron plates; a band of hemp rope round the arm zone with a knot and a hanging tail; dents and splinters on the struck
    front, a split from the top, a lashed splint repair on the side; the arm ends polished dark by hands; moss at the foot.
    Front (the side you stand to train) is -Y."""
    rg = random.Random(1401); R0, H = .155, 1.74
    # post: lathe with many rings (cracks, dents), slightly irregular radius, rounded top
    zs = list(np.linspace(.02, H - .03, 40))   # foot 2 cm up inside the core, not flush with the stones' beds
    prof = [(R0 * (1.03 - .03 * z / H) * (1 + .015 * math.sin(z * 7.3)), z) for z in zs] + [(R0 * .96, H - .012), (R0 * .9, H), (R0 * .45, H + .004)]   # flat sawn top, worn edge
    post = lathe('TG01_post', prof, 'beam', 'Main', seg=40)
    me = post.data; co = np.array([v.co[:] for v in me.vertices]); ang = np.arctan2(co[:, 1], co[:, 0]); rr = np.hypot(co[:, 0], co[:, 1])
    d = np.zeros(len(co))
    for a0, z0, z1, depth in ((1.9, .2, 1.1, .03), (-.6, .45, 1.15, .024), (2.9, 1.25, H + .01, .05), (-2.3, .85, H + .01, .032)):   # vertical splits, two from the top
        w = np.exp(-((np.angle(np.exp(1j * (ang - a0)))) / .085) ** 2); d += depth * w * ((co[:, 2] > z0) & (co[:, 2] < z1)) * np.clip((co[:, 2] - z0) / .1, 0, 1)
    for q in range(9):   # dents on the struck front (-Y), between knee and chest height
        a0 = -math.pi / 2 + rg.uniform(-.9, .9); z0 = rg.uniform(.75, 1.5); s = rg.uniform(.035, .06)
        da = np.angle(np.exp(1j * (ang - a0))) * R0; dz = co[:, 2] - z0
        d += rg.uniform(.012, .022) * np.exp(-(da ** 2 + dz ** 2) / s ** 2)
    chip = np.exp(-((np.angle(np.exp(1j * (ang + 1.2)))) / .35) ** 4) * np.clip((co[:, 2] - (H - .09)) / .03, 0, 1)   # a chunk split off the top edge
    d += .045 * chip
    k = np.where(rr > 1e-4, (rr - d) / np.maximum(rr, 1e-4), 1)
    co[:, 0] *= k; co[:, 1] *= k; me.vertices.foreach_set('co', co.ravel()); me.update(); mc.reuv(post, 'beam', (0, 0, 1))
    def surf(a, z): return Vector((math.cos(a) * R0, math.sin(a) * R0, z))
    # arms: two upper ones angled forward / out and slightly up, a straight middle one; polished ends
    arms = [(-math.pi / 2 - .38, 1.36, .40, .06), (-math.pi / 2 + .38, 1.36, .40, .06), (-math.pi / 2, 1.13, .36, 0.0)]
    for i, (a, z, L, up) in enumerate(arms):
        dvec = Vector((math.cos(a), math.sin(a), up)).normalized(); P0 = Vector((math.cos(a) * .05, math.sin(a) * .05, z))
        mid = P0 + dvec * (R0 - .05 + L * .55); P1 = P0 + dvec * (R0 - .05 + L)
        tube(f'TG01_arm{i}', [P0, P0 + dvec * (R0 - .04), mid], .036, 'beam', 'Main', sides=10, radii=[.036, .036, .034])
        tube(f'TG01_armend{i}', [mid - dvec * .01, P1 - dvec * .02, P1], .033, 'tile', 'Main', sides=10, radii=[.034, .03, .018])
        n_ = Vector((math.cos(a), math.sin(a), 0)); t_ = Vector((-math.sin(a), math.cos(a), 0))
        plate = box(f'TG01_plate{i}', (.012, .085, .085), (0, 0, 0), 'bronze', 'Main', bev=.002, segs=1)
        plate.data.transform(Matrix.Translation(surf(a, z) + n_ * .002) @ Matrix(((n_.x, t_.x, 0, 0), (n_.y, t_.y, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))))
        for sg in (-1, 1):   # iron wedge either side of the arm
            wd = box(f'TG01_wedge{i}{sg:+d}', (.03, .018, .022), (0, 0, 0), 'bronze', 'Main', bev=.002, segs=1)
            wd.data.transform(Matrix.Translation(surf(a, z) + n_ * .012 + Vector((0, 0, sg * .05))) @ Matrix(((n_.x, t_.x, 0, 0), (n_.y, t_.y, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))))
    # leg: out from the post, then bending down toward the ground
    a = -math.pi / 2 + .12; n_ = Vector((math.cos(a), math.sin(a), 0)); z = .62
    pts = [Vector((n_.x * .05, n_.y * .05, z)), surf(a, z) + n_ * .02, surf(a, z) + n_ * .17 + Vector((0, 0, -.03)), surf(a, z) + n_ * .25 + Vector((0, 0, -.14)), surf(a, z) + n_ * .27 + Vector((0, 0, -.34))]
    tube('TG01_leg', pts[:4], .045, 'beam', 'Main', sides=10, radii=[.046, .046, .044, .042])
    tube('TG01_legend', [pts[3] - (pts[3] - pts[2]).normalized() * .02, pts[4]], .04, 'tile', 'Main', sides=10, radii=[.041, .03])
    t_ = Vector((-math.sin(a), math.cos(a), 0))
    plate = box('TG01_plateL', (.012, .1, .1), (0, 0, 0), 'bronze', 'Main', bev=.002, segs=1)
    plate.data.transform(Matrix.Translation(surf(a, z) + n_ * .002) @ Matrix(((n_.x, t_.x, 0, 0), (n_.y, t_.y, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))))
    # rope band round the arm zone: a rope-textured sleeve, single turns at its edges, a knot with a hanging tail
    zr0, zr1, Rr = 1.17, 1.33, R0 + .012
    lathe('TG01_rope', [(R0 - .01, zr0), (Rr, zr0 + .006), (Rr + .004, (zr0 + zr1) / 2), (Rr, zr1 - .006), (R0 - .01, zr1)], 'cloth', 'Main', seg=28)
    for j, zz in enumerate((zr0 + .008, zr1 - .008)):
        ring = [Vector((math.cos(t) * (Rr + .006), math.sin(t) * (Rr + .006), zz + .004 * math.sin(3 * t))) for t in np.linspace(0, math.tau, 29)]
        tube(f'TG01_turn{j}', ring, .013, 'cloth', 'Main', sides=6, caps=False)
    ka = math.radians(-20); kn = Vector((math.cos(ka), math.sin(ka), 0)); kc = Vector((math.cos(ka) * (Rr + .02), math.sin(ka) * (Rr + .02), zr0 + .03))
    lathe('TG01_knot', [(.008, -.03), (.024, -.02), (.03, 0), (.024, .02), (.008, .03)], 'cloth', 'Main', seg=10, center=(0, 0, 0)); kno = mc.parts[-1]
    kno.data.transform(Matrix.Translation(kc) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))
    tail = [kc + kn * .01, kc + kn * .035 + Vector((0, 0, -.06)), kc + kn * .04 + Vector((.01, 0, -.16)), kc + kn * .03 + Vector((.02, .01, -.24))]
    tube('TG01_tail', tail, .011, 'cloth', 'Main', sides=6, radii=[.012, .011, .01, .007])
    # splint repair on the +X side: two slats lashed with rope
    for j, da in enumerate((-.2, .2)):
        aa = 0.0 + da; n_ = Vector((math.cos(aa), math.sin(aa), 0)); t_ = Vector((-math.sin(aa), math.cos(aa), 0))
        sl = box(f'TG01_slat{j}', (.018, .055, .5), (0, 0, 0), 'oldwood', 'Main', bev=.004, segs=1)
        sl.data.transform(Matrix.Translation(surf(aa, .72 + .02 * j) + n_ * .006) @ Matrix(((n_.x, t_.x, 0, 0), (n_.y, t_.y, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))))
    for j, zz in enumerate((.55, .89)):
        arc = [Vector((math.cos(t) * (R0 + .022), math.sin(t) * (R0 + .022), zz)) for t in np.linspace(-.55, .55, 11)]
        arc = [Vector((math.cos(-.6) * (R0 - .01), math.sin(-.6) * (R0 - .01), zz))] + arc + [Vector((math.cos(.6) * (R0 - .01), math.sin(.6) * (R0 - .01), zz))]
        tube(f'TG01_lash{j}', arc, .009, 'cloth', 'Main', sides=6)
    # stone collar: eight rough stones in a ring round the foot, a dark core and packed earth between them
    for j in range(8):
        t = j / 8 * math.tau + rg.uniform(-.08, .08); rc = .27 + rg.uniform(-.01, .01); hh = .17 + rg.uniform(-.02, .03)
        rubble_block(f'TG01_stone{j}', (.17 + rg.uniform(-.02, .02), .23 + rg.uniform(-.02, .03), hh), (math.cos(t) * rc, math.sin(t) * rc, hh / 2 - .012),   # sunk 12 mm: the chisel lifts the bed corners
                     'granite_moss' if rg.random() < .5 else 'granite', 14000 + j, amt=.045, rot=t)
    lathe('TG01_core', [(.30, .04), (.30, .105)], 'dark', 'Main', seg=16)   # bottom 1 cm up
    for q in range(5):
        t = rg.uniform(0, math.tau); tuft(f'Detail_Moss_TG01_{q}', rg, (math.cos(t) * .3, math.sin(t) * .3, .04), .9)   # against the stones
    socket('Socket_Front', (0, -.6, 0), (0, 0, 0))
    cols = [('box', (0, 0, H / 2), (2 * R0 + .02, 2 * R0 + .02, H)), ('box', (0, 0, .1), (.72, .72, .2))]
    return {'collision': cols, 'postHeight_m': H, 'postDiameter_m': round(2 * R0, 3),
            'mount': 'origin at the post centre, z = 0 on the ground; the arms point to -Y (the trainee stands there, Socket_Front)'}

# ------------------------------------------------------------------ build / LOD / export / info
def build(mid):
    mc.clear(); load_sheet(); SOCKETS.clear()
    meta = globals()[mid]() or {}; parts = mc.parts; tag = mid; lim = LIMITS[mid]
    groups = {}
    for o in parts: groups.setdefault(o['grp'], []).append(o)
    lod0 = {}
    for g, objs in groups.items():
        lod0[g] = mc.join(objs, f'{tag}_LOD0' if g == 'Main' else f'{tag}_{g}_LOD0'); bpy.ops.object.select_all(action='DESELECT')
    T = {g: mc.tris(o) for g, o in lod0.items()}; tot = sum(T.values()); out = {}
    for lv, frac in ((1, .5), (2, .15)):
        for g, o in lod0.items():
            tgt = max(T[g] * frac, 12)
            c = o.copy(); c.data = o.data.copy(); c.name = o.name.replace('_LOD0', f'_LOD{lv}'); bpy.context.scene.collection.objects.link(c)
            m = c.modifiers.new('d', 'DECIMATE'); m.ratio = min(1.0, tgt / max(T[g], 1)); m.use_collapse_triangulate = True; mc.apply(c, m)
            out.setdefault(lv, {})[g] = c
    cols = []
    for i, (kind, c, s) in enumerate(meta.get('collision', [])):
        bm = mc.box_bm(s, c); me = bpy.data.meshes.new(f'{tag}_Collision{i}'); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new(me.name, me); bpy.context.scene.collection.objects.link(o); cols.append(o)
    if cols: mc.join(cols, f'{tag}_Collision')
    vs = np.array([v.co[:] for o in lod0.values() for v in o.data.vertices]); mn, mx = vs.min(0), vs.max(0); dims = mx - mn
    assert all(dims[i] <= lim[i] + .005 for i in range(3)), f'{mid} over limit {tuple(round(float(d), 3) for d in dims)} > {lim}'
    assert mn[2] > -.005, f'{mid} bottom below 0: {mn[2]}'
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / f'{tag}.blend'))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=str(OUT / f'{tag}.fbx'), use_selection=True, object_types={'MESH', 'EMPTY'}, global_scale=1.0, apply_unit_scale=True,
                             apply_scale_options='FBX_SCALE_ALL', bake_space_transform=True, axis_forward='-Z', axis_up='Y', use_mesh_modifiers=True,
                             mesh_smooth_type='FACE', use_tspace=False, add_leaf_bones=False, bake_anim=False, path_mode='STRIP', embed_textures=False)
    lods = [{'lod': lv, 'triangles': sum(mc.tris(o) for o in d.values()), 'objects': len(d), 'materials': len({m.name for o in d.values() for m in o.data.materials})}
            for lv, d in ((0, lod0), (1, out[1]), (2, out[2]))]
    info = {'id': mid, 'package': PACKAGE, 'author': 'A (Johnnnny0823)', 'version': 'v001',
            'status': 'Exported; Imported: see README (Unity 6000.3.28f1 check); In-game Verified: 未驗',
            'block': 'A1 演武場（設定圖 V1、V3）',
            'dimensions_m': [round(float(d), 3) for d in dims], 'bounds_min_m': [round(float(v), 3) for v in mn], 'bounds_max_m': [round(float(v), 3) for v in mx],
            'limit_m': list(lim), 'origin': meta.get('mount', ''), 'minTier': 'low', 'lods': lods,
            'objectsLOD0': [o.name for o in lod0.values()], 'detailObjects': [o.name for g, o in lod0.items() if g.startswith('Detail_')],
            'materials': sorted({m.name for o in lod0.values() for m in o.data.materials}),
            'textures': {f'{SHEET_NAME}_{n}': '2048x2048' for n in ('Albedo', 'Normal', 'MetallicSmoothness', 'Emission')},
            'textureNote': 'one training-yard trim sheet shared by TG01-TG06 (art/textures/training-yard-a, MC01 strip layout), 256 px/m',
            'sockets': [{'name': e.name, 'location_m': [round(x, 3) for x in e.location]} for e in SOCKETS],
            'collision': f'{tag}_Collision ({len(cols)} boxes)', 'extra': {k: v for k, v in meta.items() if k not in ('collision', 'mount')},
            'fbx': f'art/exports/{PKG}/{tag}.fbx', 'fps': '不寫（手機未實測）'}
    (OUT / f'{tag}.model_info.json').write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
    print(mid, 'LOD tris', [l['triangles'] for l in lods], 'objects', [l['objects'] for l in lods], 'mats', info['materials'], 'dims', info['dimensions_m'],
          'min', info['bounds_min_m'], flush=True)

if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    for a in args:
        if a == 'sheet': mc.clear(); make_sheet(); print('training-yard sheet saved', flush=True)
        else: build(a)
