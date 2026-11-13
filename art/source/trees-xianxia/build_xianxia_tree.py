"""XT01 xianxia great tree (仙俠風格大型綠樹) for 承天, with a gold-leaf version on the same mesh and textures.

  blender --background --factory-startup --python art/source/trees-xianxia/build_xianxia_tree.py

A big old broadleaf for grassland, mountain woods and sect courtyards: a short thick leaning trunk on a soft root flare, a few heavy
limbs reaching out under a WIDE, LOW UMBRELLA CROWN (about 25 m across, 15 m high) of soft overlapping foliage masses: a dome of five
on top, a ring of eight, and an outer ring of eleven flattened masses that hangs out over the ground (stylised open-world look: bright,
between anime and natural, soft hand-painted feel). Original design; the user's reference shots only set the direction.

v002 (2026-11-13): the v001 look was rejected ("全部都不對"): big drawn leaves, a crown like a pile of balls each lit on its own, dark
teal shade, busy bark. v002 changes all of it: small-leaf foliage clumps in the atlas (xt_leaves v002), a wide flat umbrella of
masses, card normals from ONE smooth field over all masses (the crown lights as one soft volume with gentle lumps, the way stylised
game trees are shaded), a brighter yellow-green / pure gold ramp with a light mid-green shade, calmer bark, shorter roots.

v003 (2026-11-13): v002 was rejected too ("還是一坨，為什麼都是一團的"): the one smooth field wiped out the clump structure the
reference trees are made of. v003 builds the crown in three levels, masses -> florets (cauliflower clumps 2.5-4 m across) ->
cards, and shades every floret as its own ball (bright top, deep teal underside, dark cavities between florets); the limbs show
through the gaps; cards under a floret face down to the viewer on the ground; every LOD keeps the LOD0 outline.

Method
- wood: the tr_broad engine of the TR series (trunk with root lobes, ridges and burls; seeded limbs; space colonisation towards the
  masses; pipe-model radii; one fused Skin mesh, decimated to the LOD budget) plus surface roots running out over the ground.
- leaves: foliage-clump cards from a grey hand-painted atlas over every mass (lumpy flattened ellipsoids). The vertex colour carries the
  wind and a light mask (top / height / how deep inside the crown); the leaf shader turns the grey texture into colour with a
  deep / mid / tip ramp along that mask, so the green and the gold tree are two materials, nothing else.

Output (art/exports/trees-xianxia/XT01_XianxiaGreatTree/):
  XT01_XianxiaGreatTree_v003.fbx / .glb   root empty, children _LOD0.._LOD3 and _Collision
  Textures/XT01_Bark_{BaseColor,Normal,MetallicSmoothness}.png (1024), XT01_Leaves_BaseColor.png (2048, RGBA)
  model_info.json, validation.json; art/source/trees-xianxia/blend/XT01_XianxiaGreatTree_v003.blend
  (v001 and v002 files are kept next to it)
Vertex colour 'Wind' (linear float): R sway weight (trunk 0, limbs 0.02-0.25, twigs to 0.55, leaves 0.55-1), G phase,
B light mask 0..1 (leaves: deep inside / underneath -> sunlit tops and rim; wood: height), A cluster tint variation 0..1.
"""
import bpy, sys, json, math, time, hashlib
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'trees-b'))
import numpy as np
from mathutils import Vector, noise
import tr_tex as TX
import tr_tree as TT
import tr_skin as TS
from tr_broad import install
import xt_leaves as XL

AID = 'XT01_XianxiaGreatTree'; VER = 'v003'; SP = 'XT01'
ART = HERE.parents[1]
EXP = ART / 'exports' / 'trees-xianxia' / AID
TEX = EXP / 'Textures'
CAPS = {0: 25000, 1: 8000, 2: 2500, 3: 200}
LOD_SWITCH_M = [60, 110, 280, 1500]
HEIGHT_RANGE = (14., 17.)

# leaf colour ramps (sRGB, as set on the Unity material; the project renders in gamma space, Blender previews convert).
# Green: sunlit yellow-green tops, a fresh mid green, a light teal-green shade (never near black). Gold: pure gold, amber-orange shade.
LOOKS = {
    'green': dict(deep='#2F6A58', mid='#77B046', tip='#B7DA58', var_a='#C2C25A', var_b='#64A07E', var_amount=.35, midpoint=.48),
    'gold':  dict(deep='#C47528', mid='#EDAE22', tip='#FFE35E', var_a='#CFC948', var_b='#E5843A', var_amount=.4, midpoint=.46),
}
DETAIL = .55           # how far the painted leaf value pushes the light mask (sprig-by-sprig light inside a clump)
GRAZE = (.3, .66)      # |card normal . view|: below the first value a card is clipped away, above the second it is whole
VALUE = .3               # how much of the painted value multiplies the colour (shaded hearts between the sprigs)


def _masses(seed=7):
    """The crown: (x, y, z, radius) of every foliage mass. A dome of five on top, a ring of eight, an outer ring of ten, a low
    inner ring of six round the top of the trunk (hides the bare limbs, gives the crown its depth) and five lower masses that hang
    out under the outer ring (an uneven skirt); all flattened by SQ. The limbs grow towards these, the leaf cards cover them."""
    rng = np.random.default_rng(seed); out = [(.3, .2, 13.0, 3.8)]
    def ring(n, d, z, r, off=0., ja=.18):
        for k in range(n):
            a = 2 * math.pi * k / n + off + rng.uniform(-ja, ja); dd = rng.uniform(*d)
            out.append((dd * math.cos(a), dd * math.sin(a), rng.uniform(*z), rng.uniform(*r)))
    ring(4, (2.8, 3.6), (11.9, 12.7), (3.0, 3.5), .4, .3)
    ring(8, (6.0, 7.2), (9.7, 11.0), (2.9, 3.6), .15, .3)
    ring(10, (9.0, 10.8), (7.7, 9.2), (2.4, 3.2), 0., .3)
    ring(6, (3.4, 4.4), (7.9, 8.6), (2.6, 3.0), .3, .3)
    ring(5, (9.6, 10.8), (6.8, 7.3), (1.9, 2.4), .9, .4)
    # lopsided like a real old tree: the crown leans out over the side the trunk leans to (+x), bigger and a little higher there,
    # and the lumps differ more in size, so the outline is a few big soft bulges, not an even ring
    def lop(m):
        x, y, z, r = m; f = math.cos(math.atan2(y, x) - .2) if (x or y) else 0.
        return (x * (1 + .1 * f), y * (1 + .1 * f), z + .45 * f, r * (1 + .12 * f) * rng.uniform(.9, 1.1))
    out = [out[0]] + [lop(m) for m in out[1:]]
    return [tuple(round(float(x), 3) for x in m) for m in out]


MASSES = _masses()
# written to model_info.json; set after the Unity check and the review of the shots, never before
STATUS = ('已驗：Unity 6000.3.28f1 匯入，自動檢查 38 項 PASS', '已驗：Blender 與 Unity 截圖已逐張目視', '部分：臨時放進 Qingxi.unity 截圖（場景未存檔），沒有正式擺進遊戲')

# ------------------------------------------------------------------ tree shape (tr_broad species namespace)
NS = dict(
    PALETTE=[(0, 0, 0)] * 8, CELL_RECTS={}, CELL_ASPECT={}, CLUSTER_TONES=(1, 3, 4, 6),
    GROW=dict(step=.42, d_inf=3.6, d_kill=.85, trop=(0., 0., .1), iters=90, r_tip=.022, pipe=.42, top_r=.9, smooth=14,
              tip_back=2.2, squash=.78),
    SKIN_WOOD={0: ((0, 1, 2, 3), 3, 10800), 1: ((0, 1, 2), 1, 3000), 2: ((0, 1), 1, 820)},
    VARIANTS={'A': dict(
        H=16., seed=411, r0=1.6, twist=.035, zmin=6.6,
        trunk=[(0, 0, -.02, 1.), (0, 0, 0, .93), (.1, .04, .08, .74), (.3, .1, .17, .66), (.46, .12, .26, .62), (.52, .08, .33, .6)],
        burls=[(3.4, 3.4, .18), (5.1, 4.6, .15)],
        crown=(.3, .1, 10.2, 12.5, 12.5, 4.8, .12), clumps=(0, (2.6, 3.4), 150, .55), squash=.66,
        extra_clumps=[(x, y, z, r * .75) for (x, y, z, r) in MASSES],      # the wood grows to the inner three quarters of each mass: no twig reaches the leaf surface
        scaffolds=[(1., 15, 34, 5.0), (1., 100, 38, 4.6), (1., 195, 32, 5.2), (1., 285, 36, 4.8), (1., 50, 62, 3.6), (1., 235, 58, 3.4)],
        stubs=[])},
)
install(NS)
VAR = NS['VARIANTS']['A']
ROOTS = [(15, .4, 1.9), (78, .25, 1.3), (140, .45, 2.1), (205, .3, 1.5), (262, .45, 2.2), (318, .25, 1.2)]      # (azimuth deg, buttress on the trunk x radius, surface root run m)


def _section(seed, burls):
    """Trunk cross-section: six uneven root buttresses that run out over the ground (the roots are part of the trunk surface, so
    the bark maps over them without seams), a wide flare, broad soft bark ridges turning slowly with height (stylised: calm, not
    deep cracks), and a couple of low burls."""
    from tr_cypress import _angdiff
    lobes = [(az, run) for az, run, _ in ROOTS]
    def fn(th, s, p):
        z = p.z + .3
        root = 0.
        for az, run in lobes:
            w = math.exp(-(_angdiff(th, math.radians(az) + .12 * math.sin(2.3 * z + az)) / .26) ** 2)      # roots wander a little as they rise
            root += run * w * math.exp(-z / (.8 + .25 * run))
        flare = .55 * math.exp(-z / 1.1)
        tw = th - 2 * math.pi * .035 * z
        rib = (.07 * math.cos(7 * tw + seed) + .04 * math.cos(12 * tw + 2.1 * seed + .6 * z)) * (.6 + .4 * math.exp(-z / 4))
        burl = 0.
        for (tb, zb, a) in burls:
            burl += a * math.exp(-(_angdiff(th, tb) / .4) ** 2 - ((z - zb) / .35) ** 2)
        return 1 + root + flare + rib + burl
    return fn


def skeleton():
    branches, puffs, H, P, R = NS['skeleton']('A')
    branches[0].section = _section(1.7, VAR['burls'])
    return branches, H, P, R


# ------------------------------------------------------------------ foliage
# Three levels, like the reference trees: big crown MASSES -> medium FLORETS (a cauliflower floret of foliage, 2.5-4 m across at
# LOD0) packed over each mass -> leaf CARDS over each floret. Every floret is lit as its own little ball (bright top, darker
# underside, darker where it turns into the crown), so the crown reads as many stacked clumps with dark cavities between them,
# not as one smooth lump (the first v002 take was rejected for exactly that).
FOL = {0: dict(kind='S', rf=(1.25, 1.95), size=(1.0, 1.4), cover=1.7, inner=.12),
       1: dict(kind='B', rf=(1.9, 2.6), size=(1.9, 2.5), cover=1.4, inner=.1),
       2: dict(kind='B', rf=(2.7, 3.4), size=(3.0, 3.6), cover=1.3, inner=.06)}
SQ = .66          # masses are flattened: tiers of foliage, flat underneath
FIELD_K = .95     # width of the smooth field over the masses (only used for how deep a point sits in the crown)
FLORET_SQ = .82   # florets are a little flatter than balls


def clusters():
    """The crown masses (centres N x 3, radii N)."""
    m = np.array(MASSES, float); return m[:, :3], m[:, 3]


def field(p):
    """Smooth field over all masses at p (3,): -> (value, outward normal). value ~0.5 on the surface of a lone mass, more inside
    where masses overlap; used for the depth shading (occlusion) of the crown."""
    cs, rr = clusters()
    d = p[None, :] - cs; sc = np.stack([rr, rr, rr * SQ], 1)
    e = d / sc; q2 = (e ** 2).sum(1) / FIELD_K ** 2
    w = np.exp(-q2)
    g = (w[:, None] * e / sc).sum(0)
    n = g / (np.linalg.norm(g) + 1e-9)
    return float(w.sum()), n


def florets(lod, rng):
    """Florets over every mass -> list of (mass k, centre (3,), radius, outward dir of the mass (3,)). The floret's outer surface
    sits on the mass surface whatever its size, so every LOD keeps the same outline. One in five pokes out a little (a bumpy rim);
    florets on a bit of mass surface buried inside a neighbouring mass are dropped."""
    cs, rr = clusters(); cfg = FOL[lod]; out = []; sc3 = np.stack([rr, rr, rr * SQ], 1)
    rf_mean = np.mean(cfg['rf']); ga = math.pi * (3 - math.sqrt(5))
    for k in range(len(cs)):
        c = cs[k]; r = rr[k]
        area = 4 * math.pi * r * r * (1 + 2 * SQ) / 3
        n = max(4, int(area / (math.pi * rf_mean * rf_mean * .85)))
        for i in range(n):
            zf = 1 - 2 * (i + .5) / n; rad = math.sqrt(max(0., 1 - zf * zf)); th = ga * i + k * 1.7
            u = np.array([math.cos(th) * rad, math.sin(th) * rad, zf]) + rng.normal(0, .12, 3); u /= np.linalg.norm(u)
            lump = 1 + .12 * noise.noise(Vector(u * 1.7 + k * 3.3))
            surf = c + u * sc3[k] * lump
            rf = rng.uniform(*cfg['rf']) * (r / 3.) ** .3
            fc = surf - u * rf * (rng.uniform(.45, .7) if rng.random() < .2 else rng.uniform(.8, .95))
            fc = fc - u * (np.mean(cfg['size']) - np.mean(FOL[0]['size'])) * .55      # bigger far cards sit deeper: same outline at every LOD
            if fc[2] < VAR['zmin'] + .2: continue
            e = np.sqrt((((surf - cs) / sc3) ** 2).sum(1)); e[k] = 9
            if e.min() < .9: continue
            out.append((k, fc, rf, u))
    return out


def foliage(buf, lod, rng, room, tips=()):
    """Cards over every floret (+ a card on each twig tip near the crown surface, + a few dark inner cards). Returns the count."""
    cs, rr = clusters(); N = len(cs); cfg = FOL[lod]; sc3 = np.stack([rr, rr, rr * SQ], 1)
    zlo = float((cs[:, 2] - rr * SQ).min()); zhi = float((cs[:, 2] + rr * SQ).max())
    tint = np.random.default_rng(91).random(N); phase = np.random.default_rng(92).random(N)
    fl = florets(lod, rng); cand = []
    ga = math.pi * (3 - math.sqrt(5)); s_mean = np.mean(cfg['size'])
    for j, (k, fc, rf, u) in enumerate(fl):
        nc = max(3, int(2 * math.pi * rf * rf * 1.25 * cfg['cover'] / (s_mean * s_mean * .8)))
        ftint = (tint[k] + rng.normal(0, .12)) % 1.
        for i in range(nc):
            zf = 1 - 1.2 * (i + .5) / nc; rad = math.sqrt(max(0., 1 - zf * zf)); th = ga * i + j
            v = np.array([math.cos(th) * rad, math.sin(th) * rad, zf])
            # turn the cap of directions towards the outside of the mass: the cards cover the floret's visible side
            v = v + u * .75 + rng.normal(0, .15, 3); v /= np.linalg.norm(v)
            p = fc + v * np.array([rf, rf, rf * FLORET_SQ]) * rng.uniform(.72, 1.)
            cand.append(dict(k=k, p=p, v=v, u=u, fc=fc, rf=rf, size=rng.uniform(*cfg['size']), inner=False, tint=ftint, pri=1))
    # a card on every twig tip that reaches the outer part of the crown: the wood never pokes through the foliage as dark specks
    trng = np.random.default_rng(93)
    for t in tips:
        p = np.array(t); e = np.sqrt((((p - cs) / sc3) ** 2).sum(1)); k = int(np.argmin(e))
        if not (.6 < e[k] < 1.3) or p[2] < VAR['zmin'] - .4: continue
        u = (p - cs[k]) / sc3[k]; u /= np.linalg.norm(u) + 1e-9
        p = p + u * (trng.uniform(.1, .3) - (np.mean(cfg['size']) - np.mean(FOL[0]['size'])) * .55)
        cand.append(dict(k=k, p=p, v=u, u=u, fc=p - u * 1.2, rf=1.2, size=trng.uniform(*cfg['size']), inner=False, tint=tint[k], pri=0))
    # dark inner cards: the crown is not see-through between the florets
    n_in = int(len(cand) * cfg['inner'])
    for _ in range(n_in):
        k = int(rng.integers(N)); u = rng.normal(size=3); u /= np.linalg.norm(u)
        p = cs[k] + u * sc3[k] * rng.uniform(.4, .7)
        if p[2] < VAR['zmin']: continue
        cand.append(dict(k=k, p=p, v=u, u=u, fc=cs[k], rf=float(rr[k]), size=min(2.0, rng.uniform(*cfg['size']) * 1.2), inner=True, tint=tint[k], pri=2))
    if len(cand) > room:          # over budget: drop floret cards at random, keep the tip cards and the inner fill
        keep = [c for c in cand if c['pri'] != 1]; fcs = [c for c in cand if c['pri'] == 1]
        idx = rng.permutation(len(fcs))[:max(0, room - len(keep))]; cand = keep + [fcs[i] for i in sorted(idx)]
    cells = [XL.cell_rect(cfg['kind'], i) for i in range(8 if cfg['kind'] == 'S' else 4)]
    for c in cand:
        v = Vector(c['v']); u = Vector(c['u'])
        # the lower half of a floret faces out and down: seen from the ground (looking up at the crown) the cards face the eye
        n = Vector(v * .55 + u * .25 + Vector(rng.normal(0, .22, 3)) + Vector((0, 0, -.7 * max(0., .35 - v.z)))).normalized()
        up = Vector(np.array([0, 0, 1.]) + rng.normal(0, .3, 3))
        rect = cells[int(rng.integers(len(cells)))]
        _card(buf, Vector(c['p']), n, up, c['size'], rect, zlo, zhi, c, phase[c['k']], rng)
    return len(cand)


def _card(buf, c, n, up, size, rect, zlo, zhi, cd, phase, rng):
    """One leaf card. Light mask (vertex colour B) per corner: the floret's own ball shading (top bright, underside and the side
    turned into the crown dark), a little of the crown's overall shape and height, minus how deep the corner sits in the crown."""
    up = up - n * up.dot(n)
    if up.length < 1e-4: up = n.orthogonal()
    up.normalize(); side = up.cross(n).normalized(); hs = size * .5
    u0, v0, u1, v1 = rect; base = len(buf.v)
    jit = rng.normal(0, .03); fc = np.array(cd['fc']); rf = cd['rf']; um = np.array(cd['u']); inner = cd['inner']
    top = max((c + side * (x * hs) + up * (y * hs)).z for x in (-1, 1) for y in (-1, 1))
    if top > zhi + .35: c = c - Vector((0, 0, top - zhi - .35))       # no card stands above the crown top (big far cards)
    for (x, y, uv) in ((-1, -1, (u0, v0)), (1, -1, (u1, v0)), (1, 1, (u1, v1)), (-1, 1, (u0, v1))):
        p = c + side * (x * hs) + up * (y * hs)
        F, fn = field(np.array(p))
        d = np.array(p) - fc; dl = np.linalg.norm(d) + 1e-9; vf = d / dl
        hc = min(1., max(0., (p.z - zlo) / (zhi - zlo)))
        occl = min(1., max(0., (F - .45) / 1.1))
        rim = min(1.2, dl / rf)                               # inside the floret (between its sprigs) is darker
        m = (.42 + .42 * vf[2] + .12 * float(vf @ um) + .08 * fn[2] + .16 * hc - .36 * occl + .18 * (rim - .9) + jit
             - (.25 if inner else 0.))
        sn = Vector(vf * .6 + fn * .3 + np.array([0, 0, .1])).normalized()
        reach = min(1., math.hypot(p.x, p.y) / 11.)
        w = .55 + .45 * reach
        buf.v.append(p); buf.nrm.append(sn); buf.col.append((w, (phase + .03 * rng.random()) % 1., min(1., max(0., m)), cd['tint']))
    buf.f.append((base, base + 1, base + 2, base + 3)); buf.fmat.append(1)
    buf.fuv.append(((u0, v0), (u1, v0), (u1, v1), (u0, v1)))


# ------------------------------------------------------------------ materials (Blender preview; Unity builds its own)
def _lin(h): return tuple(TX.to_lin(TX.hexc(h))) + (1.,)


def S(node, name, out=False):
    """Socket by name among the enabled ones (Mix nodes carry one A / B / Result per data type)."""
    return [x for x in (node.outputs if out else node.inputs) if x.name == name and x.enabled][0]


def material_bark(tex):
    m = bpy.data.materials.new(f'M_{SP}_Bark'); m.use_nodes = True; nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    ic = nt.nodes.new('ShaderNodeTexImage'); ic.image = bpy.data.images.load(str(tex['BaseColor']), check_existing=True)
    inn = nt.nodes.new('ShaderNodeTexImage'); inn.image = bpy.data.images.load(str(tex['Normal']), check_existing=True); inn.image.colorspace_settings.name = 'Non-Color'
    nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(inn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs[0], bs.inputs['Normal'])
    nt.links.new(ic.outputs['Color'], bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = .85; bs.inputs['Specular IOR Level'].default_value = .25
    return m


def material_leaves(atlas, look):
    """Preview of the Unity leaf shader: m = mask + (painted value - mid) * DETAIL -> deep/mid/tip ramp, tint variation, x value."""
    L = LOOKS[look]; m = bpy.data.materials.new(f'M_{SP}_Leaves_{look.capitalize()}'); m.use_nodes = True; nt = m.node_tree
    N = nt.nodes; Lk = nt.links.new; bs = N['Principled BSDF']; out = N['Material Output']
    im = N.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(str(atlas), check_existing=True)
    vc = N.new('ShaderNodeVertexColor'); vc.layer_name = 'Wind'
    sep = N.new('ShaderNodeSeparateColor'); Lk(vc.outputs['Color'], sep.inputs[0])
    g = N.new('ShaderNodeMath'); g.operation = 'POWER'; g.inputs[1].default_value = 1 / 2.2; Lk(im.outputs['Color'], g.inputs[0])      # grey value back to sRGB
    d = N.new('ShaderNodeMath'); d.operation = 'SUBTRACT'; d.inputs[1].default_value = MEAN[0]; Lk(g.outputs[0], d.inputs[0])
    d2 = N.new('ShaderNodeMath'); d2.operation = 'MULTIPLY_ADD'; d2.inputs[1].default_value = DETAIL; Lk(d.outputs[0], d2.inputs[0]); Lk(sep.outputs['Blue'], d2.inputs[2])
    d2.use_clamp = True
    rp = N.new('ShaderNodeValToRGB'); e = rp.color_ramp.elements
    e[0].position = 0.; e[0].color = TX.hexc(L['deep']).tolist() + [1.]; e[1].position = 1.; e[1].color = TX.hexc(L['tip']).tolist() + [1.]
    em = e.new(L['midpoint']); em.color = TX.hexc(L['mid']).tolist() + [1.]
    Lk(d2.outputs[0], rp.inputs[0])
    # variation: A < 0.5 -> var_a, A > 0.5 -> var_b, strength |2A - 1| * amount; tint colour x2 multiplies (0.5 grey = no change)
    ta = N.new('ShaderNodeMix'); ta.data_type = 'RGBA'; S(ta, 'A').default_value = TX.hexc(L['var_a']).tolist() + [1.]; S(ta, 'B').default_value = TX.hexc(L['var_b']).tolist() + [1.]
    st = N.new('ShaderNodeMath'); st.operation = 'GREATER_THAN'; st.inputs[1].default_value = .5; Lk(vc.outputs['Alpha'], st.inputs[0]); Lk(st.outputs[0], S(ta, 'Factor'))
    a2 = N.new('ShaderNodeMath'); a2.operation = 'MULTIPLY_ADD'; a2.inputs[1].default_value = 2.; a2.inputs[2].default_value = -1.; Lk(vc.outputs['Alpha'], a2.inputs[0])
    ab = N.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; Lk(a2.outputs[0], ab.inputs[0])
    am = N.new('ShaderNodeMath'); am.operation = 'MULTIPLY'; am.inputs[1].default_value = L['var_amount']; Lk(ab.outputs[0], am.inputs[0])
    tw = N.new('ShaderNodeMix'); tw.data_type = 'RGBA'; tw.blend_type = 'MULTIPLY'; Lk(rp.outputs['Color'], S(tw, 'A')); Lk(S(ta, 'Result', True), S(tw, 'B')); S(tw, 'Factor').default_value = 1.
    t2 = N.new('ShaderNodeMix'); t2.data_type = 'RGBA'; t2.blend_type = 'MULTIPLY'; Lk(S(tw, 'Result', True), S(t2, 'A')); S(t2, 'B').default_value = (2., 2., 2., 1.); S(t2, 'Factor').default_value = 1.
    vm = N.new('ShaderNodeMix'); vm.data_type = 'RGBA'; Lk(am.outputs[0], S(vm, 'Factor')); Lk(rp.outputs['Color'], S(vm, 'A')); Lk(S(t2, 'Result', True), S(vm, 'B'))
    # value: colour x lerp(1, value / mid, VALUE)
    vv = N.new('ShaderNodeMath'); vv.operation = 'DIVIDE'; vv.inputs[1].default_value = MEAN[0]; Lk(g.outputs[0], vv.inputs[0])
    vl = N.new('ShaderNodeMix'); vl.data_type = 'FLOAT'; S(vl, 'Factor').default_value = VALUE; S(vl, 'A').default_value = 1.; Lk(vv.outputs[0], S(vl, 'B'))
    mul = N.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; S(mul, 'Factor').default_value = 1.; Lk(S(vm, 'Result', True), S(mul, 'A'))
    cv = N.new('ShaderNodeCombineColor'); [Lk(S(vl, 'Result', True), cv.inputs[i]) for i in range(3)]; Lk(cv.outputs[0], S(mul, 'B'))
    lin = N.new('ShaderNodeGamma'); lin.inputs[1].default_value = 2.2; Lk(S(mul, 'Result', True), lin.inputs[0])
    _leafy_out(nt, lin.outputs[0], im.outputs['Alpha'], bs, out)
    # like the Unity shader: both faces of a card are lit with the card's own crown normal (Blender turns the normal of a
    # back face towards the viewer, so neighbouring cards seen from front and back lit differently and the crown read as flakes)
    for l in [l for l in nt.links if l.from_node.bl_idname == 'ShaderNodeNewGeometry' and l.from_socket.name == 'Backfacing'
              and l.to_node.bl_idname == 'ShaderNodeMixShader']: nt.links.remove(l)
    geo = next(n for n in N if n.bl_idname == 'ShaderNodeNewGeometry')
    sg = N.new('ShaderNodeMath'); sg.operation = 'MULTIPLY_ADD'; sg.inputs[1].default_value = -2.; sg.inputs[2].default_value = 1.
    Lk(geo.outputs['Backfacing'], sg.inputs[0])
    un = N.new('ShaderNodeVectorMath'); un.operation = 'SCALE'; Lk(geo.outputs['Normal'], un.inputs[0]); Lk(sg.outputs[0], un.inputs['Scale'])
    Lk(un.outputs[0], bs.inputs['Normal'])
    for n in N:
        if n.bl_idname == 'ShaderNodeMixShader' and not n.inputs[0].is_linked: n.inputs[0].default_value = 0.
    return m


def material_impostor(atlas, look):
    m = bpy.data.materials.new(f'M_{SP}_Impostor_{look.capitalize()}'); m.use_nodes = True; nt = m.node_tree
    im = nt.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(str(atlas), check_existing=True)
    mp = nt.nodes.new('ShaderNodeMapping'); tc = nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(tc.outputs['UV'], mp.inputs['Vector'])
    mp.inputs['Location'].default_value = (.5 if look == 'gold' else 0., 0, 0); nt.links.new(mp.outputs[0], im.inputs['Vector'])
    _leafy_out(nt, im.outputs['Color'], im.outputs['Alpha'], nt.nodes['Principled BSDF'], nt.nodes['Material Output'])
    # the impostor is a picture of the lit crown: both faces of both crossed quads shaded alike (normal up, no back-face
    # translucency), or the quad turned from the sun reads as a dark half
    for l in [l for l in nt.links if l.from_node.bl_idname == 'ShaderNodeNewGeometry' and l.from_socket.name == 'Backfacing']: nt.links.remove(l)
    up = nt.nodes.new('ShaderNodeCombineXYZ'); up.inputs['Z'].default_value = 1.; nt.links.new(up.outputs[0], nt.nodes['Principled BSDF'].inputs['Normal'])
    for n in nt.nodes:
        if n.bl_idname == 'ShaderNodeMixShader' and not n.inputs[0].is_linked: n.inputs[0].default_value = 0.
    return m


def _leafy_out(nt, col, alpha, bs, out):
    N = nt.nodes; Lk = nt.links.new
    Lk(col, bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = .9; bs.inputs['Specular IOR Level'].default_value = .15
    geo = N.new('ShaderNodeNewGeometry'); tr = N.new('ShaderNodeBsdfTranslucent'); Lk(col, tr.inputs['Color'])
    mx = N.new('ShaderNodeMixShader'); Lk(geo.outputs['Backfacing'], mx.inputs[0]); Lk(bs.outputs[0], mx.inputs[1]); Lk(tr.outputs[0], mx.inputs[2])
    tm = N.new('ShaderNodeMixShader'); trn = N.new('ShaderNodeBsdfTransparent'); Lk(trn.outputs[0], tm.inputs[1]); Lk(mx.outputs[0], tm.inputs[2])
    # cards seen edge-on thin out (the Unity shader does the same): no smeared slivers on the crown rim
    dt = N.new('ShaderNodeVectorMath'); dt.operation = 'DOT_PRODUCT'; Lk(geo.outputs['True Normal'], dt.inputs[0]); Lk(geo.outputs['Incoming'], dt.inputs[1])
    ab = N.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; Lk(dt.outputs['Value'], ab.inputs[0])
    gz = N.new('ShaderNodeMapRange'); gz.inputs['From Min'].default_value = GRAZE[0]; gz.inputs['From Max'].default_value = GRAZE[1]
    gz.inputs['To Min'].default_value = .97; gz.inputs['To Max'].default_value = .5; Lk(ab.outputs[0], gz.inputs['Value'])
    gt = N.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; Lk(alpha, gt.inputs[0]); Lk(gz.outputs['Result'], gt.inputs[1]); Lk(gt.outputs[0], tm.inputs[0])
    Lk(tm.outputs[0], out.inputs['Surface'])
    m = next(mm for mm in bpy.data.materials if mm.node_tree == nt); m.use_backface_culling = False
    try: m.surface_render_method = 'DITHERED'
    except Exception: pass


MEAN = [.65]


# ------------------------------------------------------------------ build
def _roots(buf, P, R, sides, step):
    rng = np.random.default_rng(17)
    for az, _, run in ROOTS:
        a = math.radians(az + 9); d = Vector((math.cos(a), math.sin(a), 0)); sd = Vector((-d.y, d.x, 0)); b = P(.02); r0 = R(.05)
        pts = []; rads = []
        for k in range(9):
            s = k / 8; x = r0 * .55 + (run + r0 * .5) * s
            z = 1.15 * (1 - s) ** 1.9 + .1 * math.sin(math.pi * s) - .38 * s ** 4
            pts.append(Vector((b.x, b.y, 0)) + d * x + sd * (.22 * math.sin(2.4 * s + az)) + Vector((0, 0, z)))
            rads.append(r0 * .42 * (1 - .8 * s) + .03)
        buf.tube(TT.Branch(pts, rads, 1, 0., 0., 0., 'limb'), sides, step, seed=az)


def build_lod(lod, mats, branches, H, P, R):
    buf = TT.Buf(H)
    levels, subdiv, target = NS['SKIN_WOOD'][lod]
    wood, b0, b1 = TS.skin_wood(buf, branches, levels, subdiv, target, trunk_below=H * VAR['trunk'][-1][2] - .25, seal=True, face_uv=True)
    for i in range(len(buf.col)):          # wood: B = height (unused by the bark shader), A = 0
        w, ph, z, a = buf.col[i]; buf.col[i] = (w, ph, z, 0.)
    zlow = min(v.z for v in buf.v)            # the Skin end cap rounds the buried base up: stretch the part below ground to reach -0.3
    if -.3 < zlow < -.02:
        for v in buf.v:
            if v.z < 0: v.z *= .3 / -zlow
    if lod < 2:      # surface roots: their own bark tubes, born inside the buttresses, arching over the ground and diving in
        n0 = len(buf.v); _roots(buf, P, R, 12 if lod == 0 else 7, .22 if lod == 0 else .45)
        for i in range(n0, len(buf.v)):
            buf.v[i].z = max(buf.v[i].z, -.3); w, ph, z, a = buf.col[i]; buf.col[i] = (0., ph, z, 0.)
    rng = np.random.default_rng(500 + lod)
    room = int((CAPS[lod] * .96 - buf.tris()) // 2)
    tips = [b.pts[-1] for b in branches if b.level in levels and b.kind not in ("trunk", "stub") and b.level >= 1]
    cards = foliage(buf, lod, rng, room, tips)
    o = buf.build(f'{AID}_LOD{lod}', mats)
    tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
    return o, dict(tris=tris, wood=wood, cards=cards)


def impostor_render(objs, look, mats_by_look, tmp):
    """Front (looking +Y) orthographic render of LOD0 under a uniform white sky (albedo x occlusion), in the given look."""
    scene = bpy.context.scene
    o0 = objs[0]; keep = list(o0.data.materials)
    o0.data.materials[1] = mats_by_look[look]
    # Cycles renders a back face whose shading normal points away from the camera black: for this bake the cards use
    # Blender's own (viewer-facing) normal, the white sky lights both faces alike anyway
    nt = mats_by_look[look].node_tree; bs = nt.nodes['Principled BSDF']
    unflip = [(l.from_socket, l.to_socket) for l in nt.links if l.to_socket == bs.inputs['Normal']]
    for l in [l for l in nt.links if l.to_socket == bs.inputs['Normal']]: nt.links.remove(l)
    for o in scene.objects: o.hide_render = o not in objs
    ws = [o0.matrix_world @ Vector(c) for c in o0.bound_box]
    lo = Vector([min(v[i] for v in ws) for i in range(3)]); hi = Vector([max(v[i] for v in ws) for i in range(3)])
    half = max(abs(lo.x), abs(hi.x)) * 1.01; z0, z1 = -.3, hi.z + .05
    W = 1024; Hh = max(64, int(W * (z1 - z0) / (2 * half)))
    cam = bpy.data.objects.new('ImpCam', bpy.data.cameras.new('ImpCam')); scene.collection.objects.link(cam); scene.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = 2 * half; cam.data.clip_end = 300
    cam.location = (0, -80, (z0 + z1) / 2); cam.rotation_euler = (math.pi / 2, 0, 0)
    w = bpy.data.worlds.new('Imp'); w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (1, 1, 1, 1); bg.inputs[1].default_value = 1.
    kw = scene.world; scene.world = w
    scene.render.engine = 'CYCLES'; scene.cycles.samples = 48; scene.cycles.use_denoising = True
    scene.render.film_transparent = True; scene.render.resolution_x = W; scene.render.resolution_y = Hh; scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'Standard'
    fp = tmp / f'imp_{look}.png'; scene.render.filepath = str(fp); bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(str(fp)); c = np.array(im.pixels[:], np.float32).reshape(Hh, W, 4)[::-1].copy(); bpy.data.images.remove(im)
    c[..., :3] = np.clip(c[..., :3], 0, 1)          # the 8-bit PNG already holds sRGB values (Standard view): no second gamma
    c[..., 3] = (c[..., 3] > .5).astype(np.float32)
    # the deep inside of the crown seen through the gaps renders near black under the white sky: lift every texel to at least
    # 80 % of its neighbourhood (12 px box, opaque texels only), so the far tree reads as one soft lit crown, not a spotted one
    a = c[..., 3:4]; k = 12
    def box(x):
        s = np.pad(x, ((k + 1, k), (k + 1, k), (0, 0)), mode='edge').cumsum(0).cumsum(1)
        return s[2 * k + 1:, 2 * k + 1:] - s[:-2 * k - 1, 2 * k + 1:] - s[2 * k + 1:, :-2 * k - 1] + s[:-2 * k - 1, :-2 * k - 1]
    nb = box(c[..., :3] * a) / np.maximum(box(a), 1e-6)
    c[..., :3] = np.where(a > 0, np.maximum(c[..., :3], nb * .8), c[..., :3])
    scene.world = kw; bpy.data.objects.remove(cam)
    for o in scene.objects: o.hide_render = False
    for a, b in unflip: nt.links.new(a, b)
    for i, m in enumerate(keep): o0.data.materials[i] = m
    return c, (-half, half, z0, z1)


def save_atlas(atlas, path):
    rgb = XL.dilate_rgb(atlas[..., :3], atlas[..., 3])
    out = np.concatenate([rgb, atlas[..., 3:]], -1)
    o = bpy.data.images.new('atlas', XL.SIZE, XL.SIZE, alpha=True); o.alpha_mode = 'STRAIGHT'
    o.pixels = out[::-1].ravel(); o.filepath_raw = str(path); o.file_format = 'PNG'; o.save(); bpy.data.images.remove(o)


def export(root, kids, fbx):
    bpy.ops.object.select_all(action='DESELECT'); root.select_set(True)
    for o in kids: o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, object_types={'MESH', 'EMPTY'}, apply_unit_scale=True,
                             apply_scale_options='FBX_SCALE_ALL', bake_space_transform=True, axis_forward='-Z', axis_up='Y',
                             mesh_smooth_type='FACE', use_mesh_modifiers=True, add_leaf_bones=False, bake_anim=False,
                             path_mode='STRIP', embed_textures=False, colors_type='LINEAR', prioritize_active_color=True)
    bpy.ops.export_scene.gltf(filepath=str(fbx.with_suffix('.glb')), use_selection=True, export_format='GLB', export_yup=True,
                              export_apply=True, export_vertex_color='ACTIVE', export_attributes=False)


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    TEX.mkdir(parents=True, exist_ok=True)
    tmp = Path(bpy.app.tempdir or '.') / 'xt01'; tmp.mkdir(parents=True, exist_ok=True)
    bark = TX.painted_bark(TEX, SP, HERE.parent / 'trees-b' / 'bark_src' / 'elder_tree_bark_v1.png', sat=.55, gain=1.24,
                           tint=(1.0, .93, .86), contrast=.9, crack=.12, normal=5., smooth_val=.1, blur_n=(1, 3))
    atlas, cells, mean = XL.paint_atlas(); MEAN[0] = mean
    atlas_path = TEX / f'{SP}_Leaves_BaseColor.png'; save_atlas(atlas, atlas_path)
    mats_leaf = {lk: material_leaves(atlas_path, lk) for lk in LOOKS}
    mats_imp = {lk: material_impostor(atlas_path, lk) for lk in LOOKS}
    mbark = material_bark(bark)
    branches, H, P, R = skeleton()
    col = bpy.data.collections.new(AID); bpy.context.scene.collection.children.link(col)
    lods = {}; stats = {}
    for lod in (0, 1, 2):
        o, st = build_lod(lod, [mbark, mats_leaf['green']], branches, H, P, R); col.objects.link(o); lods[lod] = o; stats[lod] = st
        print('LOD', lod, st, flush=True)
    frames = {}
    for lk in LOOKS:
        img, fr = impostor_render([lods[0]], lk, mats_leaf, tmp); XL.place_impostor(atlas, lk, img); frames[lk] = fr
    save_atlas(atlas, atlas_path)
    for im in bpy.data.images:
        if im.filepath and Path(bpy.path.abspath(im.filepath)).name == atlas_path.name: im.reload()
    x0, x1, z0, z1 = frames['green']; u0, v0, u1, v1 = XL.IMPOSTOR_RECT['green']
    b3 = TT.Buf(H)
    for ax in (0, 1):
        def Pq(a, z): return (a, 0, z) if ax == 0 else (0, a, z)
        nrm = (0, -.25, 1) if ax == 0 else (.25, 0, 1)
        b3.quad([Pq(x0, z0), Pq(x1, z0), Pq(x1, z1), Pq(x0, z1)], [(u0, v0), (u1, v0), (u1, v1), (u0, v1)], nrm, 0,
                [(0, 0, .5, 0), (0, 0, .5, 0), (.5, 0, .5, 0), (.5, 0, .5, 0)])
    o3 = b3.build(f'{AID}_LOD3', [mats_imp['green']]); col.objects.link(o3); lods[3] = o3; stats[3] = dict(tris=b3.tris(), wood=0, cards=2)
    cpos = P(.1)       # collider: the trunk's real girth at 0.9-1.5 m (above the root buttresses), from the LOD0 bark
    me0 = lods[0].data; wv = set(v for p in me0.polygons if p.material_index == 0 for v in p.vertices)
    rr_ = [math.hypot(me0.vertices[i].co.x - cpos.x, me0.vertices[i].co.y - cpos.y) for i in wv if .9 < me0.vertices[i].co.z < 1.5]
    rc = float(np.percentile(rr_, 55))
    co = TT.collision_prism(f'{AID}_Collision', rc, 0., 3.5, sides=10, centre=(cpos.x, cpos.y)); col.objects.link(co)
    root = bpy.data.objects.new(AID, None); col.objects.link(root)
    kids = [lods[l] for l in range(4)] + [co]
    for o in kids: o.parent = root
    # gold preview copy of the mesh set (same meshes, gold materials) for the Blender file and the previews
    colg = bpy.data.collections.new(AID + '_GoldPreview'); bpy.context.scene.collection.children.link(colg)
    for l in range(4):
        og = lods[l].copy(); og.data = lods[l].data.copy(); og.name = f'{AID}_Gold_LOD{l}'
        og.data.materials[-1] = mats_imp['gold'] if l == 3 else mats_leaf['gold']
        og.location.x = 40; colg.objects.link(og)
    fbx = EXP / f'{AID}_{VER}.fbx'; export(root, kids, fbx)
    # FBX round trip
    before = set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=str(fbx)); new = [o for o in bpy.data.objects if o not in before]
    rt = {}
    for o in new:
        if o.type == 'MESH':
            ws_ = [o.matrix_world @ Vector(c) for c in o.bound_box]
            rt[o.name.split('.')[0]] = dict(tris=sum(len(p.vertices) - 2 for p in o.data.polygons), max_z=round(max(v.z for v in ws_), 3), min_z=round(min(v.z for v in ws_), 3),
                                            colour_layers=[a.name for a in o.data.color_attributes], materials=[m.name.split('.')[0] for m in o.data.materials if m])
    for o in new: bpy.data.objects.remove(o, do_unlink=True)
    ws = [Vector(c) for c in lods[0].bound_box]; lo = Vector([min(v[i] for v in ws) for i in range(3)]); hi = Vector([max(v[i] for v in ws) for i in range(3)])
    texres = {}
    for p in sorted(TEX.glob('*.png')):
        im = bpy.data.images.load(str(p), check_existing=True); texres[p.name] = list(im.size)
    budget = {f'LOD{l}': dict(triangles=stats[l]['tris'], cap=CAPS[l], objects=1, materials=len(lods[l].data.materials),
                              wood_triangles=stats[l]['wood'], leaf_cards=stats[l]['cards']) for l in range(4)}
    info = dict(asset=AID, version=VER, game='承天', name_zh='仙俠風格大型綠樹（另有金黃葉版本，共用模型與貼圖）', minTier='low',
                use='宗門庭院、山林、草原的地標大樹（多年古樹，不是世界樹）',
                height_m=round(hi.z, 3), crown_width_m=[round(hi.x - lo.x, 3), round(hi.y - lo.y, 3)], dimensions_m=[round(x, 3) for x in hi - lo],
                bounds_min_m=[round(x, 3) for x in lo], bounds_max_m=[round(x, 3) for x in hi],
                origin='trunk base centre, z = 0 on the ground; roots go down to z = -0.3', unit='1 Blender unit = 1 m; front = -Y',
                collision_capsule=dict(radius=round(rc, 3), height=3.5, centre=[round(cpos.x, 3), round(cpos.y, 3), 1.75]),
                collision_note=f'{AID}_Collision: 10-sided prism round the trunk (radius {rc:.2f} m, 0-3.5 m). Hide its renderer, use it as a MeshCollider. The crown and roots do not block.',
                looks={k: v for k, v in LOOKS.items()}, leaf_shader=dict(detail=DETAIL, value=VALUE, mean_value=round(mean, 4), graze_min=GRAZE[0], graze_max=GRAZE[1]),
                materials_per_look=[f'M_{SP}_Bark', f'M_{SP}_Leaves_<Look>', f'M_{SP}_Impostor_<Look>'],
                wind_vertex_colour='Wind (linear): R sway weight, G phase, B light mask (leaves), A tint variation (leaves)',
                lod_switch_distance_m=LOD_SWITCH_M, budget_per_lod=budget, texture_resolution_px=texres,
                status=dict(Exported=True, Imported=STATUS[0], Visually_Verified=STATUS[1], In_game_Verified=STATUS[2]))
    (EXP / 'model_info.json').write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
    checks = dict(lod_caps=all(budget[f'LOD{l}']['triangles'] <= CAPS[l] for l in range(4)), height_in_range=HEIGHT_RANGE[0] <= hi.z <= HEIGHT_RANGE[1],
                  roots_to_minus_0p3=abs(lo.z + .3) < .05, fbx_objects=sorted(rt) == sorted(o.name for o in kids),
                  fbx_height_err_m=round(abs(rt.get(f'{AID}_LOD0', {}).get('max_z', 0) - hi.z), 4),
                  fbx_wind_colour=all('Wind' in rt.get(o.name, {}).get('colour_layers', []) for o in kids[:4]))
    (EXP / 'validation.json').write_text(json.dumps(dict(asset=AID, version=VER, built=time.strftime('%Y-%m-%d %H:%M'), blender=bpy.app.version_string,
                                                         checks=checks, fbx_roundtrip=rt, files={p.name: sha(p) for p in sorted(EXP.glob('*.*')) if p.suffix in ('.fbx', '.glb')}),
                                                    ensure_ascii=False, indent=2), encoding='utf-8')
    print('CHECKS', checks, 'height', round(hi.z, 2), 'size', [round(x, 2) for x in hi - lo], flush=True)
    out = HERE / 'blend' / f'{AID}_{VER}.blend'; out.parent.mkdir(exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out), compress=True)
    print('DONE', round(time.time() - t0, 1), 's', flush=True)


if __name__ == '__main__':
    main()
