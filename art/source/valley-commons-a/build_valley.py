"""青溪 · 11/11 A 包 河谷公共建築（Johnnnny0823）：CB01 西溪風雨橋（樣品），之後 OS01 戲台、MH01 議事堂、AW01 坊市布棚。
Exports go to art/exports/valley-commons-a.

River-valley language (package §3, modeling-style-spec §11.2 A): rough grey river stone, old dark timber, dark grey tiles
#3A4048; no mountain-city granite white, no bronze. All modules share ONE 2048 sheet, T_ValleyCommons_* (M_ValleyCommons_Trim
/ _Glow), painted here with the same strip layout as the MC01 trim sheet so the MC01 geometry helpers (box, beam, tube, lathe,
prism_xz, chisel ...) work unchanged; only the colours differ: river stone instead of granite white, a weathered dark wood,
VL-like grey tiles, dark iron instead of bronze.
Origin: footprint centre, bottom z = 0 (CB01: pier bottoms), Blender -Y = front / upstream side. LOD0 = modelled detail;
LOD1 <= 50 %, LOD2 <= 15 %. Groups: main mesh, Detail_Moss (removable).
Each module is modelled after its picked AI three-view in art/references/<ID>/ ("選用：" in prompt.txt).

    blender -b --factory-startup -P art/source/valley-commons-a/build_valley.py -- sheet CB01
"""
import bpy, bmesh, json, math, sys, random
from pathlib import Path
from mathutils import Vector, Matrix
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'art/source/mountain-street-houses-a'))
import build_mc01 as mc
sys.path.insert(0, str(ROOT / 'art/source/tx04-branch-court'))
import build_tx04 as tx   # hipgable(): the RF01 / TX04 hip-and-gable roof (approved on #80 / #90)
from build_mc01 import box, beam, lathe, tube, prism_xz, rotz, chisel, bevel, apply, moss_tuft

PKG = 'valley-commons-a'; OUT = ROOT / 'art/exports' / PKG; TEX = ROOT / 'art/textures' / PKG
for p in (OUT, TEX): p.mkdir(parents=True, exist_ok=True)
PACKAGE = 'docs/execution/2026-11-11/A-40h-village-gathering-buildings.md'
SHEET_NAME = 'T_ValleyCommons'; MAT_NAMES = ('M_ValleyCommons_Trim', 'M_ValleyCommons_Glow')

# ------------------------------------------------------------------ valley sheet (MC01 strip layout, valley colours)
def sources():
    S = mc.sources(); fbm, lerp, X, Y = mc.fbm, mc.lerp, mc.X, mc.Y
    def recolour(name, lo, hi, keep=.35):
        a, h, s, r, m, g = S[name]; lum = a.mean(2, keepdims=True); lum = (lum - lum.min()) / max(1e-6, lum.max() - lum.min())
        new = np.asarray(lo)[None, None, :] * (1 - lum) + np.asarray(hi)[None, None, :] * lum
        S[name] = (new * (1 - keep) + a * keep * (np.asarray(hi) / np.maximum(a.mean((0, 1)), 1e-3)).clip(0, 2) * .5 + new * keep * .5, h, s, r, m, g)
    # river stone: blue-grey with a little brown, darker and rougher than the mountain-city granite white (VL stone ~#6B7A7C)
    recolour('granite', (.26, .28, .28), (.52, .55, .53))
    recolour('granite_moss', (.20, .23, .20), (.42, .45, .40))
    recolour('granite_top', (.32, .34, .33), (.56, .58, .55))
    # weathered dark old wood: brown going silver-grey where the rain reaches it
    recolour('plank', (.17, .13, .10), (.40, .33, .26), keep=.5)
    recolour('beam', (.15, .11, .085), (.34, .27, .21), keep=.5)
    recolour('oldwood', (.24, .21, .18), (.46, .41, .35), keep=.5)
    # grey tiles between the package's #3A4048 and the VL roof grey-green
    recolour('tile', (.17, .19, .21), (.36, .40, .41))
    recolour('tile_moss', (.15, .18, .16), (.33, .38, .34))
    # dark iron instead of bronze (spec §11.2 A: no bronze in the valley)
    a, h, s, r, m, g = S['bronze']
    S['bronze'] = (lerp((.07, .07, .07), (.17, .16, .15), fbm(6, 3)) + np.clip((fbm(8, 3) - .62) * 2.5, 0, 1)[..., None] * np.array([.12, .05, .01]), h, s, .62, .55, g)
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
    e = bpy.data.objects.new(name, None); e.empty_display_type = 'ARROWS'; e.empty_display_size = .3
    e.location = loc; e.rotation_euler = rot; bpy.context.scene.collection.objects.link(e); SOCKETS.append(e); return e

def tuft(name, rg, at, scale=1.0):
    o = moss_tuft(name, rg); o.data.transform(Matrix.Translation(at) @ Matrix.Scale(scale, 4)); return o

def log(name, a, b, r, strip='oldwood', grp='Main'):
    """a peeled round log from a to b with a slight irregular radius, end grain caps"""
    a, b = Vector(a), Vector(b); n = max(2, int((b - a).length / .5) + 1); rg = random.Random(hash(name) & 0xffff)
    pts = [a.lerp(b, t) for t in np.linspace(0, 1, n)]; rad = [r * (1 + rg.uniform(-.06, .06)) for _ in pts]
    return tube(name, pts, r, strip, grp, sides=10, radii=rad)

# ------------------------------------------------------------------ shared roof: TX04 gableroof with plank gables, open truss
def gable_roof(pre, Ex, Ey, zr, base_z, wx, wy, ze=.3, p=1.25, seed=0, res=1.0, cx=0.0, ends=(-1, 1), curl=1.0):
    """two-slope 懸山 roof (TX04 gableroof, approved on #90) for the valley: concave pans with modelled cover tiles and eave
    caps, a main ridge, verge ridges / bargeboards / scroll ornaments only on the gable ends listed in `ends`, rafters, purlins,
    a ridge purlin, plank gable boards (no plaster) and no ceiling, so the roof timbers show from the walkway. cx shifts it along X."""
    rg = random.Random(seed); n0 = len(mc.parts); sp = .24
    def z_fb(y): t = max(0.0, min(1.0, (Ey - abs(y)) / Ey)); return ze + (zr - ze) * t ** p
    nx, ny = int(2 * Ex / (.06 * res)), int(2 * Ey / (.06 * res)) + 1; bm = bmesh.new(); vs = {}
    for i in range(nx + 1):
        for j in range(ny + 1):
            x = -Ex + 2 * Ex * i / nx; y = -Ey + 2 * Ey * j / ny
            vs[i, j] = bm.verts.new((x, y, z_fb(y) - .018 * (.5 + .5 * math.cos(x / sp * math.tau))))
    for i in range(nx):
        for j in range(ny): bm.faces.new((vs[i, j], vs[i + 1, j], vs[i + 1, j + 1], vs[i, j + 1]))
    pan = mc.finish(f'{pre}_pan', bm, 'tile', 'Main', axis=(1, 0, 0), smooth=True)
    m = pan.modifiers.new('t', 'SOLIDIFY'); m.thickness = .05; m.offset = -1; apply(pan, m); mc.reuv(pan, 'tile', (1, 0, 0))
    k = 0
    for sgn in (-1, 1):
        for x in np.arange(-Ex + sp / 2 + .06, Ex - .06, sp):
            n = max(12, int(Ey / (.07 * res))); pts, rad = [], []
            for q in range(n + 1):
                s_ = q / n * .97; y = sgn * (Ey + .015 - s_ * (Ey + .015)); pts.append((x, y, z_fb(y) + .02)); rad.append(.05 + .01 * (((q * .5) % 1) < .18))
            tube(f'{pre}_cov{k}', pts, .05, 'tile' if rg.random() > .3 else 'tile_moss', 'Main', sides=8, radii=rad)
            c = Vector(pts[0]) + Vector((0, sgn * .008, -.004)); lathe(f'{pre}_cap{k}', [(.004, -.015), (.062, -.015), (.062, .015), (.004, .015)], 'tile', 'Main', seg=12)
            o = mc.parts[-1]; t = Vector((0, sgn, 0)); u = Vector((0, 0, 1)); s = u.cross(t)
            o.data.transform(Matrix(((s.x, u.x, t.x, c.x), (s.y, u.y, t.y, c.y), (s.z, u.z, t.z, c.z), (0, 0, 0, 1)))); k += 1
    tube(f'{pre}_ridge', [Vector((-Ex - .02, 0, zr + .05)), Vector((Ex + .02, 0, zr + .05))], .11, 'tile', 'Main', sides=10)
    for sx in ends:
        c = Vector((sx * (Ex - .01), 0, zr + .05))
        cv = [c + Vector((sx * .05 * curl * math.sin(a) * (1 - a / 6), 0, .1 * curl * (1 - math.cos(a)) * (1 - a / 8))) for a in np.linspace(0, 4.0, 12)]
        tube(f'{pre}_ornament{sx:+d}', cv, .06, 'tile', 'Main', sides=10, radii=list(np.linspace(.075, .035, 12)))
        for sy in (-1, 1):
            tube(f'{pre}_verge{sx:+d}{sy:+d}', [Vector((sx * (Ex - .05), sy * yy, z_fb(yy) + .07)) for yy in np.linspace(.06, Ey + .01, 14)], .055, 'tile', 'Main', sides=10)
            tube(f'{pre}_barge{sx:+d}{sy:+d}', [Vector((sx * (Ex - .03), sy * yy, z_fb(yy) - .07)) for yy in np.linspace(0, Ey - .02, 14)], .045, 'beam', 'Main', sides=6)
    for sgn in (-1, 1):
        for x in np.arange(-Ex + .12, Ex - .1, .22):
            if abs(abs(x) - wx) < .14: continue
            y0, y1 = sgn * .05, sgn * (Ey - .06)
            tube(f'{pre}_raft{sgn:+d}{x:+.2f}', [(x, y0, z_fb(y0) - .10), (x, y1, z_fb(y1) - .08)], .04, 'beam', 'Main', sides=8)
    zpf = z_fb(wy) - .22
    for sgn in (-1, 1):
        beam(f'{pre}_purlin{sgn:+d}', (-Ex + .04, sgn * wy, zpf), (Ex - .04, sgn * wy, zpf), .16, .16, 'beam', 'Main', bev=.012)
        zm = z_fb(wy / 2) - .2
        beam(f'{pre}_midpurlin{sgn:+d}', (-Ex + .04, sgn * wy / 2, zm), (Ex - .04, sgn * wy / 2, zm), .14, .14, 'beam', 'Main', bev=.01)
    beam(f'{pre}_ridgepurlin', (-Ex + .04, 0, zr - .2), (Ex - .04, 0, zr - .2), .18, .18, 'beam', 'Main', bev=.012)
    for sx in (-1, 1):   # plank gable boards on the gable lines x = +-wx (vertical boards, a cover batten on each joint)
        poly = [(yy, min(z_fb(yy) - .14, zr - .3)) for yy in np.linspace(-wy - .06, wy + .06, 21)] + [(wy + .06, zpf - .06), (-wy - .06, zpf - .06)]
        bm = bmesh.new(); v = [bm.verts.new((sx * wx, y, z)) for y, z in poly]; bm.faces.new(v if sx > 0 else list(reversed(v)))
        g = mc.finish(f'{pre}_gable{sx:+d}', bm, 'plank', 'Main', axis=(0, 0, 1))
        m = g.modifiers.new('t', 'SOLIDIFY'); m.thickness = .05; m.offset = 0; apply(g, m); mc.reuv(g, 'plank', (0, 0, 1))
        for yy in np.arange(-wy + .1, wy, .24):
            ztop = min(z_fb(yy) - .16, zr - .32)
            if ztop - zpf < .1: continue
            box(f'{pre}_batten{sx:+d}{yy:+.2f}', (.07, .045, ztop - zpf + .02), (sx * (wx + .04), yy, (zpf + ztop) / 2), 'beam', 'Main', bev=.006, axis=(0, 0, 1))
        beam(f'{pre}_tie{sx:+d}', (sx * wx, -wy - .02, zpf - .02), (sx * wx, wy + .02, zpf - .02), .14, .16, 'beam', 'Main', bev=.01)
    for o in mc.parts[n0:]: o.data.transform(Matrix.Translation((cx, 0, base_z)))
    return {'ridge_z': base_z + zr + .05, 'eave_z': base_z + ze}

# ------------------------------------------------------------------ CB01 West Creek covered bridge (three-view option 2)
LIMITS = {'CB01': (16.0, 4.5, 6.5)}
CB = dict(L=16.0, W=4.5, piers=(-4.4, 4.4), post_y=1.75, clear=2.62, zr=1.3)

def rubble_pier(pre, cx, rg, seed):
    """a battered rubble-masonry pier: four courses, shell blocks of random length and slight setbacks, corners bonded
    alternately, a hidden core, a cap of big flat slabs; mossy lower courses, moss on the ledges"""
    hx, hy, top, nC, bat = 1.3, 2.0, 1.0, 3, .05; zc = 0.0; ch = top / nC
    for j in range(nC):
        z0, z1 = zc - (.03 if j else 0), zc + ch;   # courses overlap 3 cm: the rough chisel sinks block tops up to ~2 cm
        ix, iy = hx - j * bat, hy - j * bat; d = .42
        strip = 'granite_moss' if j < 2 else 'granite'
        for side in range(4):
            along_x = side in (1, 3)          # +-Y faces run along X
            corner_here = (j % 2 == 0) != along_x
            L0 = (ix if along_x else iy) - (0 if corner_here else d)
            xs = [-L0]
            while L0 - xs[-1] > .8: xs.append(xs[-1] + rg.uniform(.35, .75))
            xs.append(L0)
            if len(xs) > 2 and xs[-1] - xs[-2] < .3: del xs[-2]   # no slivers at the end of a run
            for k, (a, b) in enumerate(zip(xs, xs[1:])):
                g = .02; L = b - a - g; out = rg.uniform(-.035, .02); hh = z1 - z0
                if along_x:
                    sy = 1 if side == 1 else -1; size = (L, d, hh); c = (cx + (a + b) / 2, sy * (iy - d / 2 + out), z0 + hh / 2)
                else:
                    sx = 1 if side == 0 else -1; size = (d, L, hh); c = (cx + sx * (ix - d / 2 + out), (a + b) / 2, z0 + hh / 2)
                o = box(f'{pre}_c{j}s{side}b{k}', size, c, strip, 'Main', bev=0, cuts=1 if L > .6 else 0)
                chisel(o, .05, 1.8, seed + j * 97 + side * 13 + k, keep_bed=True); bevel(o, .06, 2, 30)
        box(f'{pre}_core{j}', (2 * (ix - .12), 2 * (iy - .12), z1 - z0 - .13), (cx, 0, (z0 + .07 + z1 - .06) / 2), 'dark', 'Main', bev=0)   # every shell block reaches it; dark in the joints
        if j < nC - 1:
            for q in range(3): tuft(f'Detail_Moss_{pre}_{j}{q}', rg, (cx + rg.uniform(-ix + .2, ix - .2), rg.choice((-1, 1)) * (iy - bat - .05), z1 - .004), 1.1)
        zc = z1
    ix, iy = hx - nC * bat + .08, hy - nC * bat + .08; xs = [-iy]
    while iy - xs[-1] > .9: xs.append(xs[-1] + rg.uniform(.6, .9))
    xs.append(iy)
    for k, (a, b) in enumerate(zip(xs, xs[1:])):   # cap: slabs across the pier
        o = box(f'{pre}_cap{k}', (2 * ix, b - a - .01, .14), (cx, (a + b) / 2, top - .03 + .07), 'granite_top', 'Main', bev=0, cuts=1)
        chisel(o, .012, 2.5, seed + 500 + k, keep_bed=True); bevel(o, .03, 2, 30)
    for q in range(4): tuft(f'Detail_Moss_{pre}_base{q}', rg, (cx + rg.uniform(-hx + .3, hx - .3), rg.choice((-1, 1)) * (hy - .15), .02), 1.2)
    return top + .11

def CB01():
    """西溪風雨橋 16 x 4.5 x 6.5 m (picked three-view option 2): two battered rubble piers; on each, two layers of cantilever logs
    (伸臂木) stepping out; six long log beams over the whole length; a plank deck across them with edge boards; nine bays of
    posts each side with tie beams, plates and knee braces; plain railings with balusters on the outside of the posts and a
    built-in bench along the inside of the middle bays; a gallery of three gable roofs: the two end sections lower, the middle
    section raised on taller posts as the landmark silhouette, dark grey tiles. Walkway 2.6 m clear between the benches,
    2.62 m clear under the tie beams; deck at about +1.91 m (deckTop_m in model_info), level from end to end."""
    rg = random.Random(1101); L, PY = CB['L'], CB['post_y']; half = L / 2
    for i, px in enumerate(CB['piers']): ptop = rubble_pier(f'CB01_pier{i}', px, rg, 9100 + i * 300)
    ys = np.linspace(-1.9, 1.9, 6); r = .13
    for i, px in enumerate(CB['piers']):   # cantilever logs: two layers stepping out from each pier
        for lay, (zc, hl) in enumerate(((ptop - .01 + r, 2.0), (ptop - .01 + r + .24, 3.0))):
            for j, y in enumerate(ys):
                log(f'CB01_cant{i}{lay}{j}', (px - hl, y + rg.uniform(-.02, .02), zc), (px + hl, y, zc), r)
    zb = ptop - .01 + r + .48
    for j, y in enumerate(ys): log(f'CB01_beam{j}', (-half + .02, y, zb), (half - .02, y, zb), r, 'beam')
    for i, px in enumerate(CB['piers']):   # raking struts from the pier shoulders up to the outer beams (picked view)
        for sx in (-1, 1):
            for y in (ys[0], ys[-1]):
                log(f'CB01_strut{i}{sx:+d}{y:+.1f}', (px + sx * .9, y, ptop - .35), (px + sx * 3.4, y, zb - r * .6), .1, 'beam')
    for sx in (-1, 1):
        box(f'CB01_endboard{sx:+d}', (.04, 4.36, zb + r - (zb - r) + .01), (sx * (half - .025), 0, zb), 'plank', 'Main', bev=.006, axis=(0, 1, 0))
    # deck: planks across, gaps 1 cm, a few replaced lighter boards; edge boards hide the log ends along the sides
    xs = np.arange(-half + .01, half - .01, .26); top_b = zb + r - .006; DT = round(top_b + .08, 3); CB['DT'] = DT
    for k, x in enumerate(xs):
        w = min(.25, half - .01 - x); strip = 'oldwood' if rg.random() < .12 else 'plank'
        o = box(f'CB01_plank{k}', (w, 4.38, DT - top_b), (x + w / 2, rg.uniform(-.02, .02), (top_b + DT) / 2), strip, 'Main', bev=.006, axis=(0, 1, 0))
    for sy in (-1, 1):
        box(f'CB01_edge{sy:+d}', (L - .02, .05, .34), (0, sy * 2.215, DT - .17 + .01), 'plank', 'Main', bev=.008, axis=(1, 0, 0))
    # posts, tie beams, plates, knee braces
    px_ = np.linspace(-half + .3, half - .3, 9); mid = 2.45; tie0 = DT + CB['clear']; zr = CB['zr']
    base_end = tie0 + .09
    zpf = .34 + (zr - .34) * (.44 / 2.19) ** 1.3 - .22                  # purlin height over the roof base (hipgable, wy = PY)
    zt_end = zt_mid = base_end + zpf - .06                                 # post tops reach 2 cm into the purlins
    for sy in (-1, 1):
        for k, x in enumerate(px_):
            ztop = zt_mid if abs(x) < mid else zt_end
            box(f'CB01_post{sy:+d}{k}', (.2, .2, ztop - .03 - DT + .006), (x, sy * PY, (DT - .006 + ztop - .03) / 2), 'beam', 'Main', bev=.014, axis=(0, 0, 1))
            box(f'CB01_base{sy:+d}{k}', (.26, .26, .05), (x, sy * PY, DT + .024), 'beam', 'Main', bev=.01)
            for sx in (-1, 1):   # knee braces under the plate
                if (k == 0 and sx < 0) or (k == len(px_) - 1 and sx > 0): continue
                beam(f'CB01_knee{sy:+d}{k}{sx:+d}', (x + sx * .09, sy * PY, tie0 - .5), (x + sx * .5, sy * PY, tie0 + .06), .08, .1, 'beam', 'Main', bev=.008, up=(0, 1, 0))
        box(f'CB01_plate{sy:+d}', (L - .5, .17, .16), (0, sy * PY, zt_end - .08), 'beam', 'Main', bev=.012, axis=(1, 0, 0))
    for k, x in enumerate(px_):
        box(f'CB01_tie{k}', (.16, 2 * PY + .14, .2), (x, 0, tie0 + .1), 'beam', 'Main', bev=.012, axis=(0, 1, 0))
    # railings on the outside of the posts, benches along the inside of the middle bays
    for sy in (-1, 1):
        yr = sy * (PY + .1 + .035)
        beam(f'CB01_rtop{sy:+d}', (-half + .2, yr, DT + .95), (half - .2, yr, DT + .95), .09, .07, 'oldwood', 'Main', bev=.012)
        beam(f'CB01_rbot{sy:+d}', (-half + .2, yr, DT + .12), (half - .2, yr, DT + .12), .07, .07, 'beam', 'Main', bev=.008)
        for x in np.arange(-half + .4, half - .3, .21):
            if min(abs(x - p) for p in px_) < .16: continue
            box(f'CB01_bal{sy:+d}{x:+.2f}', (.04, .04, .78 + .02), (x, yr, DT + .155 + .39), 'beam', 'Main', bev=.005, axis=(0, 0, 1))
        for k in range(1, len(px_) - 2):
            a, b = px_[k] + .1, px_[k + 1] - .1; yb = sy * (PY - .1 - .18)
            box(f'CB01_seat{sy:+d}{k}', (b - a + .02, .36, .06), ((a + b) / 2, yb, DT + .45), 'oldwood', 'Main', bev=.012, axis=(1, 0, 0))
            for x in (a + .35, b - .35):
                box(f'CB01_leg{sy:+d}{k}{x:+.1f}', (.07, .3, .42 + .006), (x, yb, DT + .21), 'beam', 'Main', bev=.008, axis=(0, 0, 1))
    # gallery roof (picked view option 2): one long gable roof over the whole bridge, and on its ridge a small raised roof
    # over the middle bays on short posts with a slatted clerestory band: the landmark silhouette
    Ey = 2.19
    tx.hipgable('CB01_roof', half - .14, Ey, zr, base_end, half - .14 - 1.1 - .1, PY, hip_run=1.1, lift_h=.22, seed=1110, res=2.0)   # wx inside the hip zone start: rafters stay on the purlins
    mEx, mEy, mzr, mze, mwy = 2.6, 1.35, .62, .14, 1.0; zmain = lambda y: base_end + .34 + (zr - .34) * (max(0, Ey - abs(y)) / Ey) ** 1.3
    base_m = base_end + zr + .05 + .11 + .1 - mzr                       # its pans clear the main ridge by ~10 cm
    tx.hipgable('CB01_roofTop', mEx, mEy, mzr, base_m, mEx - .6 - .1, mwy, ze=mze, hip_run=.6, lift_h=.12, seed=1120, res=1.2)
    zpm = base_m + mze + (mzr - mze) * ((mEy - mwy) / mEy) ** 1.3 - .22   # its purlin height
    for o in [o for o in mc.parts if o.name.startswith('CB01_roofTop_frieze')]:   # too low a roof for friezes (negative height): the slat band replaces them
        mc.parts.remove(o); bpy.data.objects.remove(o)
    for sy in (-1, 1):
        z0 = zmain(mwy) - .12
        for k, x in enumerate(np.linspace(-mEx + .35, mEx - .35, 5)):
            box(f'CB01_cpost{sy:+d}{k}', (.12, .12, zpm - z0 + .02), (x, sy * mwy, (z0 + zpm + .02) / 2), 'beam', 'Main', bev=.01, axis=(0, 0, 1))
        box(f'CB01_csill{sy:+d}', (2 * mEx - .5, .1, .08), (0, sy * mwy, z0 + .1), 'beam', 'Main', bev=.008, axis=(1, 0, 0))
        for x in np.arange(-mEx + .45, mEx - .4, .12):   # slatted clerestory band
            box(f'CB01_slat{sy:+d}{x:+.2f}', (.035, .03, zpm - z0 - .2), (x, sy * (mwy + .01), (z0 + .14 + zpm - .06) / 2), 'oldwood', 'Main', bev=.004, axis=(0, 0, 1))
    for o in mc.parts:   # hipgable rafters sit tangent on the purlins; near the lifted corners they lose contact: sink them 2.5 cm
        if o.name.startswith('CB01_roof') and '_raftfb' in o.name: o.data.transform(Matrix.Translation((0, 0, -.025)))
    socket('Socket_EndA', (-half, 0, DT)); socket('Socket_EndB', (half, 0, DT))
    cols = [('box', (0, 0, DT - .1), (L, 4.4, .2))]
    for px in CB['piers']: cols.append(('box', (px, 0, ptop / 2), (2.6, 4.0, ptop)))
    for sy in (-1, 1):
        cols.append(('box', (0, sy * (PY + .1), DT + .55), (L, .12, 1.1)))                           # railing: chest-high guard
        cols.append(('box', (0, sy * (PY - .1 - .18), DT + .24), (px_[-2] - px_[1] - .2, .36, .48)))  # benches
        for x in px_: cols.append(('box', (x, sy * PY, (DT + zt_end) / 2), (.2, .2, zt_end - DT)))
    cols.append(('box', (0, 0, base_end + .3 + (zr - .3) / 2), (L, 4.4, zr - .3)))                                                   # roof mass
    return {'collision': cols, 'deckTop_m': DT, 'ridgeTop_m': round(base_m + mzr + .16, 3), 'clearWidth_m': round(2 * (PY - .1 - .36), 2), 'clearHeight_m': round(tie0 - DT, 2),
            'mount': f'origin at the footprint centre, z = 0 at the pier bottoms (river bed); the deck is level at +{DT} m and runs along X; '
                     'Socket_EndA / Socket_EndB are the deck ends (x = -8 / +8) for the river banks'}

# ------------------------------------------------------------------ build / LOD / export / info
def build(mid):
    mc.clear(); load_sheet(); SOCKETS.clear()
    meta = globals()[mid]() or {}; parts = mc.parts; tag = f'{mid}'; lim = LIMITS[mid]
    groups = {}
    for o in parts: groups.setdefault(o['grp'], []).append(o)
    lod0 = {}
    for g, objs in groups.items():
        lod0[g] = mc.join(objs, f'{tag}_LOD0' if g == 'Main' else f'{tag}_{g}_LOD0'); bpy.ops.object.select_all(action='DESELECT')
    T = {g: mc.tris(o) for g, o in lod0.items()}; tot = sum(T.values()); out = {}
    for lv, frac, cap in ((1, .5, 100_000), (2, .15, 25_000)):
        budget = min(tot * frac, cap); w = {g: math.sqrt(t) for g, t in T.items()}; tw = sum(w.values())
        for g, o in lod0.items():
            tgt = max(min(T[g] * (.5 if lv == 1 else .15), budget * w[g] / tw), 12)
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
            'dimensions_m': [round(float(d), 3) for d in dims], 'bounds_min_m': [round(float(v), 3) for v in mn], 'bounds_max_m': [round(float(v), 3) for v in mx],
            'limit_m': list(lim), 'origin': meta.get('mount', ''), 'minTier': 'low', 'lods': lods,
            'objectsLOD0': [o.name for o in lod0.values()], 'detailObjects': [o.name for g, o in lod0.items() if g.startswith('Detail_')],
            'materials': sorted({m.name for o in lod0.values() for m in o.data.materials}),
            'textures': {f'{SHEET_NAME}_{n}': '2048x2048' for n in ('Albedo', 'Normal', 'MetallicSmoothness', 'Emission')},
            'textureNote': 'one valley trim sheet shared by every 11/11 module (art/textures/valley-commons-a, same strip layout as the MC01 sheet), 256 px/m',
            'sockets': [{'name': e.name, 'location_m': [round(x, 3) for x in e.location]} for e in SOCKETS],
            'collision': f'{tag}_Collision ({len(cols)} boxes)', 'extra': {k: v for k, v in meta.items() if k not in ('collision', 'mount')},
            'fbx': f'art/exports/{PKG}/{tag}.fbx', 'fps': '不寫（手機未實測）'}
    (OUT / f'{tag}.model_info.json').write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
    print(mid, 'LOD tris', [l['triangles'] for l in lods], 'objects', [l['objects'] for l in lods], 'mats', info['materials'], 'dims', info['dimensions_m'],
          'min', info['bounds_min_m'], flush=True)

if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    for a in args:
        if a == 'sheet': mc.clear(); make_sheet(); print('valley sheet saved', flush=True)
        else: build(a)
