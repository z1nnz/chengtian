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
sys.path.insert(0, str(HERE))
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

# ------------------------------------------------------------------ stones (core team's SS01 rock(), core-d2-v1/d2_ground.py, PR #118)
def rock_geo(c, L, W, H, seed, dish=.02, sink=.003, res=(28, 12), rot=None):   # sink 3 mm: TG01 sits on the yard floor (bottom >= 0)
    """The core team's SS01 half-buried stone, copied unchanged except for the resolution and an
    optional fixed rotation: a squircle body with noise, 5-8 soft cleavage planes for the broken faces, a slight dish on top."""
    from mathutils import noise
    R = random.Random(seed); so = Vector((R.uniform(-50, 50), R.uniform(-50, 50), seed * .61))
    rot = R.uniform(0, math.tau) if rot is None else rot; cs, sn = math.cos(rot), math.sin(rot)
    nu, nv = res; verts = []; planes = []
    for _ in range(R.randint(5, 8)):
        a = R.uniform(0, math.tau); el = R.uniform(-.1, .55)
        n = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el))); planes.append((n, R.uniform(.72, .9)))
    for j in range(nv + 1):
        v = j / nv
        for i in range(nu):
            t = math.tau * i / nu; ct, st = math.cos(t), math.sin(t)
            sx = math.copysign(abs(ct) ** .72, ct); sy = math.copysign(abs(st) ** .72, st); d = Vector((ct, st, v * 2 - 1))
            k = 1 + .13 * noise.noise(so + d * 1.1) + .06 * noise.noise(so + d * 2.7) + .025 * noise.noise(so + d * 6.5)
            if v < .62:
                f = v / .62; rr = (.82 + .18 * f) * (1 + .07 * math.sin(f * math.pi)) * k; z = -sink + (H + sink) * .78 * f ** .9
            else:
                f = (v - .62) / .38; rr = max((1. - .9 * f ** 2.4) * k, 0.); z = -sink + (H + sink) * (.78 + .22 * math.sin(f * math.pi / 2)) - dish * f ** 3
                z += .012 * noise.noise(so * 2 + Vector((ct * rr * L, st * rr * W, 0)) * 3.)
            x, y = sx * L / 2 * rr, sy * W / 2 * rr
            if z > 0:
                q = Vector((x / (L / 2), y / (W / 2), (z - H / 2) / max(H, .05) * 1.2))
                for n, dd in planes:
                    e = q.dot(n) - dd
                    if e > -.08: q -= n * (math.log1p(math.exp(e / .04)) * .04)
                x, y = q.x * L / 2, q.y * W / 2; z = min(z, q.z / 1.2 * max(H, .05) + H / 2)
            verts.append((c[0] + x * cs - y * sn, c[1] + x * sn + y * cs, c[2] + z))
    verts.append((c[0], c[1], c[2] + H - dish * 1.05)); faces = []
    for j in range(nv):
        for i in range(nu):
            a = j * nu + i; b = j * nu + (i + 1) % nu; faces.append((a, b, b + nu, a + nu))
    top = len(verts) - 1; base = nv * nu; faces += [(base + i, base + (i + 1) % nu, top) for i in range(nu)]
    # no bottom face: it would lie on the ground plane, coplanar with the neighbouring stones' bottoms in the tight collar
    return verts, faces


def rock(name, c, L, W, H, seed, rot=None):
    verts, faces = rock_geo(c, L, W, H, seed, rot=rot)
    bm = bmesh.new(); vs = [bm.verts.new(v) for v in verts]
    for f in faces: bm.faces.new([vs[i] for i in f])
    return mc.finish(name, bm, 'granite_moss', 'Main', smooth=True)


def tag(o, kind):   # baked surface: 0 wood, 1 polished grip, 2 stone (bake_tg.py)
    o['kind'] = kind; return o


# ------------------------------------------------------------------ TG01 wooden training dummy (three-view option 3)
def TG01():
    """木人樁 (picked three-view option 3), v002 after the PR #119 review: a thick round post of split old wood (deep lengthwise
    cracks and a split top as geometry; scanned old-wood surface baked on), set in a squat collar of fitted mossy stones; two
    upper arms angled forward, one middle arm, one long bent leg reaching down toward the collar, square mortises with dark
    iron plates; a wide band of hemp rope round the arm zone (many turns, knot and two tails at the back); a lashed patch of
    five slats on the -X side; the arm and leg ends polished dark by hands; moss at the foot. Front (the trainee) is -Y."""
    rg = random.Random(1401); R0, H = .165, 1.74
    zs = list(np.linspace(.02, H - .03, 58))
    prof = [(R0 * (1.03 - .03 * z / H) * (1 + .015 * math.sin(z * 7.3)), z) for z in zs] + [(R0 * .96, H - .012), (R0 * .9, H), (R0 * .45, H + .004)]
    post = tag(lathe('TG01_post', prof, 'beam', 'Main', seg=56), 0)
    me = post.data; co = np.array([v.co[:] for v in me.vertices]); ang = np.arctan2(co[:, 1], co[:, 0]); rr = np.hypot(co[:, 0], co[:, 1])
    d = np.zeros(len(co))
    # deep lengthwise cracks (the three-view's split old wood): some run most of the height, three open from the top
    cracks = [(1.9, .15, 1.15, .035), (-.6, .4, 1.2, .03), (2.9, 1.0, H + .01, .055), (-2.3, .8, H + .01, .04), (.5, .1, .9, .028),
              (-1.4, .25, 1.55, .032), (2.3, .3, .75, .025), (-2.9, .55, 1.4, .03), (1.2, 1.25, H + .01, .03)]
    for a0, z0, z1, depth in cracks:
        wdt = .06 + .03 * rg.random()
        w = np.exp(-((np.angle(np.exp(1j * (ang - a0 - .04 * np.sin(co[:, 2] * 3.1)))) / wdt) ** 2))   # cracks wander a little
        span = np.clip((co[:, 2] - z0) / .12, 0, 1) * np.clip((z1 - co[:, 2]) / .12, 0, 1)
        d += depth * w * span
    for q in range(11):   # dents on the struck front (-Y)
        a0 = -math.pi / 2 + rg.uniform(-.9, .9); z0 = rg.uniform(.75, 1.5); s = rg.uniform(.035, .06)
        da = np.angle(np.exp(1j * (ang - a0))) * R0; dz = co[:, 2] - z0; d += rg.uniform(.012, .022) * np.exp(-(da ** 2 + dz ** 2) / s ** 2)
    # split top: a V-shaped notch across the sawn face, plus a chunk off the edge
    top = co[:, 2] > H - .02; xr = co[:, 0] / R0
    co[top, 2] -= .06 * np.exp(-(xr[top] / .18) ** 2) * np.clip(1 - rr[top] / (R0 * 1.1), 0, 1) ** .3
    d += .045 * np.exp(-((np.angle(np.exp(1j * (ang + 1.2)))) / .35) ** 4) * np.clip((co[:, 2] - (H - .09)) / .03, 0, 1)
    k = np.where(rr > 1e-4, (rr - d) / np.maximum(rr, 1e-4), 1)
    co[:, 0] *= k; co[:, 1] *= k; me.vertices.foreach_set('co', co.ravel()); me.update(); mc.reuv(post, 'beam', (0, 0, 1))
    def surf(a, z): return Vector((math.cos(a) * R0, math.sin(a) * R0, z))
    def frame(a):
        n_ = Vector((math.cos(a), math.sin(a), 0)); t_ = Vector((-math.sin(a), math.cos(a), 0))
        return n_, t_, Matrix(((n_.x, t_.x, 0, 0), (n_.y, t_.y, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
    # arms
    arms = [(-math.pi / 2 - .38, 1.36, .42, .06), (-math.pi / 2 + .38, 1.36, .42, .06), (-math.pi / 2, 1.06, .38, 0.0)]
    for i, (a, z, L, up) in enumerate(arms):
        dvec = Vector((math.cos(a), math.sin(a), up)).normalized(); P0 = Vector((math.cos(a) * .05, math.sin(a) * .05, z))
        mid = P0 + dvec * (R0 - .05 + L * .55); P1 = P0 + dvec * (R0 - .05 + L)
        tag(tube(f'TG01_arm{i}', [P0, P0 + dvec * (R0 - .04), mid], .038, 'beam', 'Main', sides=12, radii=[.038, .038, .036]), 0)
        tag(tube(f'TG01_armend{i}', [mid - dvec * .01, P1 - dvec * .02, P1], .035, 'tile', 'Main', sides=12, radii=[.036, .032, .019]), 1)
        n_, t_, M = frame(a)
        plate = box(f'TG01_plate{i}', (.012, .09, .09), (0, 0, 0), 'bronze', 'Main', bev=.002, segs=1); plate.data.transform(Matrix.Translation(surf(a, z) + n_ * .002) @ M)
        for sg in (-1, 1):
            wd = box(f'TG01_wedge{i}{sg:+d}', (.03, .018, .022), (0, 0, 0), 'bronze', 'Main', bev=.002, segs=1)
            wd.data.transform(Matrix.Translation(surf(a, z) + n_ * .012 + Vector((0, 0, sg * .052))) @ M)
    # leg (three-view: long and thick, out from the post at knee height, then bending down to just above the stone collar)
    a = -math.pi / 2 + .12; n_, t_, M = frame(a); z = .66
    pts = [Vector((n_.x * .05, n_.y * .05, z)), surf(a, z) + n_ * .02, surf(a, z) + n_ * .16 + Vector((0, 0, -.02)), surf(a, z) + n_ * .27 + Vector((0, 0, -.12)),
           surf(a, z) + n_ * .31 + Vector((0, 0, -.30)), surf(a, z) + n_ * .32 + Vector((0, 0, -.40))]
    tag(tube('TG01_leg', pts[:5], .052, 'beam', 'Main', sides=12, radii=[.054, .054, .052, .05, .048]), 0)
    tag(tube('TG01_legend', [pts[4] - (pts[4] - pts[3]).normalized() * .02, pts[5]], .046, 'tile', 'Main', sides=12, radii=[.048, .034]), 1)
    plate = box('TG01_plateL', (.012, .11, .11), (0, 0, 0), 'bronze', 'Main', bev=.002, segs=1); plate.data.transform(Matrix.Translation(surf(a, z) + n_ * .002) @ M)
    # rope band: a wide wrap of hemp rope (eleven turns over a rope-textured sleeve), knot and two tails at the back (+Y)
    zr0, zr1, Rr = 1.12, 1.42, R0 + .012
    lathe('TG01_rope', [(R0 - .01, zr0), (Rr, zr0 + .006), (Rr + .004, (zr0 + zr1) / 2), (Rr, zr1 - .006), (R0 - .01, zr1)], 'cloth', 'Main', seg=32)
    for j, zz in enumerate(np.linspace(zr0 + .012, zr1 - .012, 11)):
        ring = [Vector((math.cos(t) * (Rr + .006), math.sin(t) * (Rr + .006), zz + .0035 * math.sin(3 * t + j))) for t in np.linspace(0, math.tau, 33)]
        tube(f'TG01_turn{j}', ring, .0125, 'cloth', 'Main', sides=6, caps=False)
    ka = math.radians(95); kn = Vector((math.cos(ka), math.sin(ka), 0)); kc = Vector((math.cos(ka) * (Rr + .022), math.sin(ka) * (Rr + .022), (zr0 + zr1) / 2 + .03))
    lathe('TG01_knot', [(.008, -.035), (.026, -.024), (.034, 0), (.026, .024), (.008, .035)], 'cloth', 'Main', seg=10, center=(0, 0, 0)); kno = mc.parts[-1]
    kno.data.transform(Matrix.Translation(kc) @ Matrix.Rotation(math.pi / 2, 4, 'X'))
    for j, side in enumerate((-.4, .4)):
        sv = Vector((-kn.y, kn.x, 0)) * side
        tail = [kc + kn * .012, kc + kn * .03 + sv * .03 + Vector((0, 0, -.07)), kc + kn * .035 + sv * .05 + Vector((0, 0, -.18)), kc + kn * .028 + sv * .055 + Vector((0, 0, -.27 - .05 * j))]
        tube(f'TG01_tail{j}', tail, .012, 'cloth', 'Main', sides=6, radii=[.013, .012, .011, .008])
    # patch: five slats on the -X side (left edge in the three-view's front view, right edge in its back view), tops staggered, two double lashings
    for j in range(5):
        aa = math.pi + (j - 2) * .22; n_, t_, M = frame(aa); hgt = .6 - abs(j - 2) * .05 + rg.uniform(-.03, .03)
        sl = tag(box(f'TG01_slat{j}', (.02, .062, hgt), (0, 0, 0), 'oldwood', 'Main', bev=.004, segs=1), 0)
        sl.data.transform(Matrix.Translation(surf(aa, .38 + hgt / 2 + rg.uniform(-.02, .02)) + n_ * .008) @ M)
    for j, zz in enumerate((.48, .86)):
        arc = [Vector((math.cos(t) * (R0 + .03), math.sin(t) * (R0 + .03), zz)) for t in np.linspace(math.pi - .6, math.pi + .6, 13)]
        arc = [Vector((math.cos(math.pi - .66) * (R0 - .01), math.sin(math.pi - .66) * (R0 - .01), zz))] + arc + [Vector((math.cos(math.pi + .66) * (R0 - .01), math.sin(math.pi + .66) * (R0 - .01), zz))]
        for q in range(2): tube(f'TG01_lash{j}{q}', [p + Vector((0, 0, q * .022)) for p in arc], .009, 'cloth', 'Main', sides=6)
    # stone collar: twelve fitted rough stones (the core team's SS01 stone) round the foot, packed earth core, moss
    for j in range(12):
        t = j / 12 * math.tau + rg.uniform(-.05, .05); rc = .285 + rg.uniform(-.012, .012); hh = .2 + rg.uniform(-.03, .04)
        tag(rock(f'TG01_stone{j}', (math.cos(t) * rc, math.sin(t) * rc, 0), .2 + rg.uniform(-.02, .03), .17 + rg.uniform(-.015, .02), hh, 14000 + j, rot=t + math.pi / 2), 2)
    lathe('TG01_core', [(.30, .04), (.30, .14)], 'dark', 'Main', seg=16)
    for q in range(7):
        t = rg.uniform(0, math.tau); tuft(f'Detail_Moss_TG01_{q}', rg, (math.cos(t) * (R0 + .03), math.sin(t) * (R0 + .03), .14), .9)   # at the post foot, on the collar
    # bake the scanned wood / stone onto the tagged parts (bake_tg.py)
    baked = [o for o in mc.parts if 'kind' in o.keys()]
    for o in baked:
        at = o.data.attributes.new('kind', 'FLOAT', 'POINT'); at.data.foreach_set('value', [float(o['kind'])] * len(o.data.vertices))
    for o in baked: mc.parts.remove(o)
    low = mc.join(baked, 'TG01_baked'); low['grp'] = 'Main'; mc.parts.append(low)
    import bake_tg
    hi = bake_tg.high_model(low); bake_tg.bake(low, hi, 'TG01', TEX, 1024); bpy.data.objects.remove(hi, do_unlink=True)
    low.data.attributes.remove(low.data.attributes['kind'])
    socket('Socket_Front', (0, -.6, 0), (0, 0, 0))
    cols = [('box', (0, 0, H / 2), (2 * R0 + .02, 2 * R0 + .02, H)), ('box', (0, 0, .11), (.74, .74, .22))]
    return {'collision': cols, 'postHeight_m': H, 'postDiameter_m': round(2 * R0, 3), 'bakedSurface': 'Poly Haven bark_willow_02 (wood), mossy_rock (stone), CC0',
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
    import bake_tg
    for o in lod0.values(): bake_tg.open_zero_uv(o)   # QA: no zero-area UV faces (2 mm bevel strips on the trim sheet)
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
    info = {'id': mid, 'package': PACKAGE, 'author': 'A (Johnnnny0823)', 'version': 'v002',
            'status': 'Exported; Imported: see README (Unity 6000.3.28f1 check); In-game Verified: 未驗',
            'block': 'A1 演武場（設定圖 V1、V3）',
            'dimensions_m': [round(float(d), 3) for d in dims], 'bounds_min_m': [round(float(v), 3) for v in mn], 'bounds_max_m': [round(float(v), 3) for v in mx],
            'limit_m': list(lim), 'origin': meta.get('mount', ''), 'minTier': 'low', 'lods': lods,
            'objectsLOD0': [o.name for o in lod0.values()], 'detailObjects': [o.name for g, o in lod0.items() if g.startswith('Detail_')],
            'materials': sorted({m.name for o in lod0.values() for m in o.data.materials}),
            'textures': {**{f'{SHEET_NAME}_{n}': '2048x2048' for n in ('Albedo', 'Normal', 'MetallicSmoothness', 'Emission')}, **({f'T_{tag}_Baked_Albedo': '1024x1024', f'T_{tag}_Baked_Normal': '1024x1024'} if (TEX / f'T_{tag}_Baked_Albedo.png').exists() else {})},
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
