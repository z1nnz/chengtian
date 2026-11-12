"""TR01 Chinese pine, built the same way as TR02 (golden-spirit-tree method, 2026-11-12 user direction: 全部打掉重做，參考剛剛做的金黃樹，
不要再雲團了; then 柏樹定版, 用同樣做法開始做松樹).

- wood: an S-curved trunk and a real branch hierarchy, limb -> mid branch -> twig -> tip, fused by the Skin modifier (tr_skin.py).
  Pine habit: the lower trunk is bare (stubs of shed limbs), the first limb at about 5 m; limbs leave the trunk nearly level in
  tiers, run out, sag a little and turn their ends up; mid branches spread sideways in the horizontal plane, so each limb carries
  a flat pad; the upper limbs stay fairly long, so the old tree has a flat-ish top.
- leaves: no masses, no clouds. Needle tufts (fascicle brushes, 30-45 cm) grow in clusters on the twig tips, pointing up and
  out, each tuft its own card at its own angle.
- colour: one tone per tuft from where it sits (top of a pad, outer, facing up = light; under a pad, inner = dark), 8 tones of
  muted blue-green. Each tone is its own atlas cell, so URP Lit needs no change.
A  13 m    S-curved trunk, ten tiers of limbs, flat-ish top (the common pine for A1 / A2 / A4).
B  12.6 m  trunk leaning one way then back, one long low limb sweeping out the other way.
C  12.5 m  cliff pine for B1: thinner trunk leaning hard, one long reaching limb, few short limbs, many stubs.
Atlas: cell 0 = 4 x 4 single tufts (8 tones x 2 shapes); cell 1 top = four cluster cells (4 tones) for LOD1 / LOD2.
"""
import math
import numpy as np
from mathutils import Vector
from tr_tree import Branch, catmull
from tr_tex import hexc, to_lin
from tr_cypress import _grow, _at, _angdiff, _envelope, _mix

# eight needle tones, dark (under a pad) -> light (pad top), sRGB; muted blue-green, never neon
PALETTE = [hexc(h) for h in ('#152B2C', '#1C3734', '#24433E', '#2E5049', '#3A5D54', '#486B5F', '#5A7A6A', '#728D78')]
STEM = hexc('#3A2C24')
NT = len(PALETTE)
CLUSTER_TONES = (1, 3, 4, 6)

CELL_RECTS = {}
CELL_ASPECT = {}
for _t in range(NT):
    for _s in range(2):
        _k = _t * 2 + _s; _c, _r = _k % 4, _k // 4
        CELL_RECTS[('L', _t, _s)] = (_c * .125, 1 - (_r + 1) * .125, (_c + 1) * .125, 1 - _r * .125); CELL_ASPECT[('L', _t, _s)] = 1.
for _k in range(4):
    _c, _r = _k % 2, _k // 2
    CELL_RECTS[('C', _k)] = (.5 + _c * .25, .625 + _r * .1875, .5 + (_c + 1) * .25, .625 + (_r + 1) * .1875); CELL_ASPECT[('C', _k)] = .25 / .1875
CELL_AO = .012
CELL_M = 1.0
BARK = 'pine'
WOOD = 'skin'
SKIN_WOOD = {0: ((0, 1, 2, 3), 2, 9000), 1: ((0, 1, 2), 1, 2600), 2: ((0, 1), 1, 750)}
# same hand-painted source as TR02, pushed toward the pine's warmer grey-brown plates (kept low in saturation: v1 went brick red in Unity)
BARK_PAINTED = dict(src='bark_src/elder_tree_bark_v1.png', sat=.55, gain=.95, tint=(.97, .9, .86), contrast=2.0, crack=1., normal=16., smooth_val=.07, blur_n=(0, 2))


# ------------------------------------------------------------------ atlas drawing
def tuft(st, rng, base, d, L, tone, z0=0., n=34):
    """One needle fascicle brush from `base` along d (length L): a short woody stem, then needles fanning from its upper half,
    each a thin tapered strip, dark at the base and lighter at the tip; the right half lit, the left half shaded."""
    col = PALETTE[tone]; d = np.array(d, np.float32); d /= np.linalg.norm(d) + 1e-9; side = np.array([-d[1], d[0]], np.float32)
    base = np.array(base[:2], np.float32)
    st.strip([tuple(base + d * L * s) + (z0,) for s in (0., .22, .42)], [.022 * L, .016 * L, .011 * L], [tuple(to_lin(STEM))] * 3, ridge=.5)
    # a dark core so the brush reads as one tuft and keeps its coverage in the mips
    st.blob(tuple(base + d * L * .52), L * .17, tuple(to_lin(col * .55)), tuple(to_lin(col * .45)), rng, rough=.25, z=z0 + .001)
    for i in range(n):
        u = (i + rng.uniform(.1, .9)) / n; a = (u - .5) * 2.3 + rng.normal(0, .05)     # fan of +-66 deg around d
        ca, sa = math.cos(a), math.sin(a); dd = d * ca + side * sa
        root = base + d * L * rng.uniform(.3, .46)
        ln = L * rng.uniform(.5, .62) * (1 - .32 * abs(a) / 1.15)
        bend = rng.normal(0, .08); lit = 1.08 if a < 0 else .78           # a < 0 = right side of the stem (lit)
        c0 = col * .62 * lit; c1 = np.clip(col * 1.22 * lit + .012, 0, 1)
        pts = [tuple(root + dd * ln * v + side * bend * ln * v * v) + (z0 + .003 + .0004 * i,) for v in (0., .4, .75, 1.)]
        st.strip(pts, [.0034, .003, .0022, .0008], [tuple(to_lin(_mix(c0, c1, v))) for v in (0., .4, .75, 1.)], ridge=.3)


def brush(st, rng, base, d, L, tone, shape, z0=0.):
    """shape 0: one brush; shape 1: a forked twig end with three brushes (the middle one longer)."""
    d = np.array(d, np.float32); d /= np.linalg.norm(d) + 1e-9
    if shape == 1:
        for sgn in (-1, 1):
            a = sgn * rng.uniform(.42, .55); ca, sa = math.cos(a), math.sin(a)
            tuft(st, rng, np.array(base[:2]) + d * .08 * L, (d[0] * ca - d[1] * sa, d[0] * sa + d[1] * ca), L * .62, tone, z0, n=24)
        tuft(st, rng, base, d, L * .9, tone, z0 + .02, n=30)
    else:
        tuft(st, rng, base, d, L * .97, tone, z0)


def cell_leaves(st, rng, cell):
    """Cell 0: 4 x 4 single tufts, two per tone (shape 0 and 1), each pointing up its sub-cell from a stem at the bottom."""
    S = cell / 4
    for t in range(NT):
        for s in range(2):
            k = t * 2 + s; cx = -cell / 2 + S * (k % 4 + .5); cy = cell / 2 - S * (k // 4 + .5)
            brush(st, rng, (cx, cy - .46 * S), (rng.normal(0, .04), 1.), S * .94, t, s)


def cell_clusters(st, rng, cell):
    """Cell 1 top (y -0.25..0.5): four cluster cells (0.5 wide x 0.375 tall), tone dark -> light: a fan of 7 brushes from a base at
    the bottom middle, the upright ones a tone lighter (they are the top of the pad)."""
    for k, tone in enumerate(CLUSTER_TONES):
        c, r = k % 2, k // 2
        x0, y0 = -cell / 2 + c * cell / 2, -cell / 4 + r * cell * .375; w, h = cell / 2, cell * .375
        base = np.array([x0 + w / 2, y0 + h * .06])
        for j in range(7):
            a = math.pi / 2 + (j / 6 - .5) * 2.0 + rng.normal(0, .06); L = h * (.88 - .28 * abs(j / 6 - .5) * 2)
            L = min(L, (w / 2 - .02) / max(.2, abs(math.cos(a))) if abs(math.cos(a)) > .3 else L)
            tt = min(NT - 1, max(0, tone + (1 if j == 3 else -1 if abs(j - 3) == 3 else 0)))
            brush(st, rng, base, (math.cos(a), math.sin(a)), L, tt, j % 2, z0=.004 * (3 - abs(j - 3)))


CELLS = [cell_leaves, cell_clusters]


# ------------------------------------------------------------------ skeleton
VARIANTS = {
    # trunk: S-curve control points (x, y, z as a fraction of H, radius as a fraction of r0);
    # limbs: (t along the trunk, azimuth deg, length m, end rise as a fraction of the length)
    'A': dict(H=12.2, seed=11, r0=.56, twist=.03, zmin=4.1, leaves=1.,
              trunk=[(0, 0, -.03, 1.), (0, 0, 0, .95), (.15, .06, .08, .68), (.6, .22, .2, .58), (.85, .3, .34, .5), (.55, .2, .48, .42),
                     (.05, 0, .62, .34), (-.25, -.1, .76, .26), (-.12, -.05, .88, .16), (0, 0, .97, .06)],
              limbs=[(.42, 200, 4.5, .2), (.46, 335, 4.1, .24), (.55, 85, 3.9, .24), (.59, 250, 3.6, .26),
                     (.68, 20, 3.4, .28), (.72, 150, 3.1, .28), (.81, 290, 2.8, .26), (.88, 60, 2.4, .22)],
              stubs=[(.12, 40), (.18, 150), (.24, 290), (.3, 100), (.35, 230)]),
    'B': dict(H=12.1, seed=23, r0=.56, twist=-.03, zmin=3.6, leaves=1.,
              trunk=[(0, 0, -.03, 1.), (0, 0, 0, .95), (-.2, .05, .08, .66), (-.7, .15, .2, .56), (-1.1, .25, .34, .48), (-1.2, .3, .48, .4),
                     (-.95, .3, .62, .32), (-.7, .25, .76, .24), (-.65, .2, .88, .14), (-.7, .2, .97, .05)],
              limbs=[(.37, 8, 5.8, .1), (.47, 150, 3.8, .26), (.53, 262, 3.9, .24), (.59, 62, 3.4, .28), (.65, 200, 3.2, .28),
                     (.71, 320, 3.0, .3), (.77, 100, 2.7, .28), (.83, 232, 2.4, .26), (.89, 12, 2.1, .22)],
              stubs=[(.14, 220), (.2, 80), (.27, 300)]),
    'C': dict(H=12.1, seed=37, r0=.46, twist=.05, zmin=4.0, leaves=.82,
              trunk=[(0, 0, -.03, 1.), (0, 0, 0, .95), (.25, -.04, .08, .68), (.8, -.16, .2, .57), (1.45, -.3, .34, .48), (1.95, -.42, .48, .4),
                     (2.3, -.5, .62, .32), (2.5, -.54, .76, .24), (2.6, -.55, .88, .15), (2.65, -.56, .97, .06)],
              limbs=[(.47, 345, 4.7, .06), (.6, 170, 2.6, .3), (.67, 62, 2.4, .3), (.74, 250, 2.3, .3), (.81, 10, 2.5, .26),
                     (.88, 130, 1.9, .22)],
              stubs=[(.12, 120), (.19, 250), (.26, 160), (.33, 40), (.4, 200)]),
}
NAMES = {'A': 'Pine', 'B': 'Pine', 'C': 'CliffPine'}
ZH = {'A': '松（S 形主幹、十層枝、平頂）', 'B': '松（斜幹回正、一條低長枝往另一側伸）', 'C': '崖松（細幹大斜、一條長枝外伸、斷樁多）'}
_NODES = {}
last_extra_cards = 0


def _trunk(cfg):
    H = cfg['H']; r0 = cfg['r0']; zt = H * cfg['trunk'][-1][2]
    ctrl = [Vector((x, y, -.3 if z < 0 else z * H)) for x, y, z, r in cfg['trunk']]
    dense = catmull(ctrl, 20); zz = np.array([p.z for p in dense])
    rr = np.interp(np.linspace(0, 1, len(dense)), np.linspace(0, 1, len(ctrl)), [r ** .9 * r0 for x, y, z, r in cfg['trunk']])
    xs = np.array([p.x for p in dense]); ys = np.array([p.y for p in dense])
    def P(t):
        z = -.3 + (zt + .3) * min(1., max(0., t)); return Vector((float(np.interp(z, zz, xs)), float(np.interp(z, zz, ys)), z))
    def R(t):
        z = -.3 + (zt + .3) * min(1., max(0., t)); return float(np.interp(z, zz, rr))
    return P, R, zt


def _section(seed, twist):
    """Root flare and lobes; pine bark: scaly plates split by furrows (two frequencies, slight turn with height)."""
    def fn(th, s, p):
        z = p.z + .3
        root = .6 * math.exp(-z / .7) * max(0., math.cos(5 * th + seed)) ** 2
        flare = .4 * math.exp(-z / .8)
        tw = th - 2 * math.pi * twist * z
        def ridge(x): return abs(math.cos(x / 2)) ** .55 - .62
        rib = (.17 * ridge(9 * tw + seed + .6 * math.sin(1.3 * z)) + .09 * ridge(15 * tw + 2.1 * seed + 1.1 * z)
               + .05 * ridge(23 * tw + 3.3 * seed + 2.7 * z)) * (.7 + .3 * math.exp(-z / 4))
        return 1 + root + flare + rib
    return fn


def skeleton(var):
    cfg = VARIANTS[var]; rng = np.random.default_rng(cfg['seed']); H = cfg['H']; zmin = cfg['zmin']
    P, R, zt = _trunk(cfg)
    ts = np.linspace(0, 1., 24)
    trunk = Branch([P(t) for t in ts], [max(.025, R(t)) for t in ts], 0, 0., 0., 0., 'trunk', _section(cfg['seed'] * .7, cfg['twist']))
    trunk.twist = cfg['twist']
    # bark scale: 0.8 m tiles, as many round the trunk as fit at chest height (one tile round the whole trunk stretched the plates
    # 3x sideways at the base and read as moulded plastic)
    trunk.uv_tile = .8; tc = min(1., (1.3 + .3) / (zt + .3)); trunk.uv_k = max(2, round(2 * math.pi * R(tc) * 1.06 / trunk.uv_tile))
    branches = [trunk]; nodes = []
    # two short crown limbs at the very top, so the trunk tip ends inside the top pad (a lone leader tuft floated above the crown)
    a0 = rng.uniform(0, 360); crown = [(.95, a0, 1.6, .25), (.985, a0 + 150, 1.25, .25)]
    for (t, az_d, L, rise) in list(cfg['limbs']) + crown:
        az = math.radians(az_d + rng.normal(0, 4)); start = P(t); out = Vector((math.cos(az), math.sin(az), 0)); phase = rng.random()
        u = min(1., (t - cfg['limbs'][0][0]) / max(.01, cfg['limbs'][-1][0] - cfg['limbs'][0][0]))
        # pine limb: leaves the trunk climbing a little, runs out nearly level, the outer third sags, the end turns up under its pad
        cp = [start, start + out * .3 * L + Vector((0, 0, .1 * L + .1)), start + out * .68 * L + Vector((0, 0, rise * .6 * L - .05 * L)),
              start + out * L + Vector((0, 0, rise * L - .08 * L * (1 - u)))]
        side0 = Vector((-out.y, out.x, 0))     # sideways wobble only, so a short upper limb cannot fold back over itself
        cp = [c + (side0 * rng.normal(0, .06 * L) + Vector((0, 0, rng.normal(0, .03 * L)))) * float(k > 1) for k, c in enumerate(cp)]
        pts = catmull(cp, 3); pts = [pts[0]] + pts[2:]
        D = max(0., max(zmin - p.z for p in pts[1:]))
        for k, p in enumerate(pts[1:], 1): p.z += D * min(1., 2. * k / (len(pts) - 1))
        r0 = max(.03, R(t) * .38)     # under 1/1.9 of the trunk: its own Skin island (fused limbs pinched the thin upper trunk)
        rads = [r0 * (1 - .78 * (k / (len(pts) - 1)) ** .8) + .006 for k in range(len(pts))]
        branches.append(Branch(pts, rads, 1, .02, .3, phase, 'limb'))
        # mid branches spread sideways, nearly level: the flat pad of a pine limb
        nmid = 2 + int(L * .8); sgn = 1 if rng.random() < .5 else -1; owners = [(pts, rads, 1)]
        for k in range(nmid):
            s = .3 + .62 * (k + rng.uniform(.2, .8)) / nmid; q, j = _at(pts, s); sgn = -sgn
            tdir = (pts[j + 1] - pts[j]).normalized(); side = tdir.cross(Vector((0, 0, 1))).normalized()
            ang = rng.uniform(.75, 1.25); d = tdir * math.cos(ang) + side * sgn * math.sin(ang) + Vector((0, 0, rng.uniform(.0, .2)))
            Lm = L * rng.uniform(.3, .42) * (1.15 - .4 * s); rq = float(np.interp(s, np.linspace(0, 1, len(rads)), rads))
            mp, mr = _grow(rng, q, d, Lm, rq * .5, .02, droop=.2, upturn=.3, wander=.1, zmin=zmin - .4)
            branches.append(Branch(mp, mr, 2, .3, .5, phase, 'twig')); owners.append((mp, mr, 2))
        # twigs on the mids and the outer part of the limb, turning up; tufts on every twig
        for (bp, br_, dep) in owners:
            nt_ = 3 if dep == 1 else 2; sg = 1
            for k in range(nt_):
                s = (.6 if dep == 1 else .4) + (.36 if dep == 1 else .55) * (k + rng.uniform(.2, .8)) / nt_; q, j = _at(bp, s); sg = -sg
                tdir = (bp[j + 1] - bp[j]).normalized(); side = tdir.cross(Vector((0, 0, 1))).normalized()
                ang = rng.uniform(.6, 1.1); d = tdir * math.cos(ang) + side * sg * math.sin(ang) + Vector((0, 0, rng.uniform(.1, .45)))
                tp, tr = _grow(rng, q, d, rng.uniform(.6, 1.05), max(.014, float(np.interp(s, np.linspace(0, 1, len(br_)), br_)) * .5), .01,
                               droop=rng.uniform(.05, .25), upturn=.35, step=.26, zmin=zmin - .5)
                branches.append(Branch(tp, tr, 3, .5, .7, phase, 'twig'))
                for s2 in (.35, .6, .82, 1.):
                    q2, j2 = _at(tp, s2); nodes.append(dict(q=q2, t=(tp[min(j2 + 1, len(tp) - 1)] - tp[j2]).normalized(), phase=phase, lz=q.z))
            for s2 in (.8, 1.):
                q2, j2 = _at(bp, s2); nodes.append(dict(q=q2, t=(bp[min(j2 + 1, len(bp) - 1)] - bp[j2]).normalized(), phase=phase, lz=q2.z))
    # stubs of shed lower limbs, broken off
    for (t, az_) in cfg['stubs']:
        # a short thick broken stump (thin long spikes read as skewers): its own Skin island, bent down a little, ragged end
        a = math.radians(az_); s = P(t); dd = Vector((math.cos(a), math.sin(a), -.12)).normalized(); L = R(t) + rng.uniform(.18, .34)
        dn = Vector((0, 0, -.06))
        branches.append(Branch([s, s + dd * L * .55, s + dd * L + dn], [R(t) * .3, R(t) * .25, R(t) * .2], 3, 0., 0., 0., 'stub', cap=True))
    _NODES[var] = [n for n in nodes if n['q'].z > zmin - .6]
    return branches, [], H, P, R


# ------------------------------------------------------------------ leaves
def _light(q, H, zc0, hr, envr, leafdir, above, rng):
    """high, outer, facing up and on top of its pad = light; low, inner, under the pad = dark."""
    hn = min(1., max(0., (q.z - zc0) / max(H - zc0, 1e-3))); rim = min(1., hr / max(envr, .3))
    return .22 * hn + .36 * rim + .24 * (.5 + .5 * leafdir.z) + .3 * min(1., max(0., above / .55)) - .02 + rng.normal(0, .06)


def _foliage(buf, var, lod, P, R, rng):
    cfg = VARIANTS[var]; H = cfg['H']; nodes = _NODES[var]; zc0 = P(cfg['limbs'][0][0]).z; zmin = cfg['zmin']
    def axis(z): return P(min(1., max(0., (z + .3) / (H * cfg['trunk'][-1][2] + .3))))
    def hrad(q): a = axis(q.z); return math.hypot(q.x - a.x, q.y - a.y), Vector((q.x - a.x, q.y - a.y, 0))
    envf = _envelope([dict(q=Vector((n['q'].x - axis(n['q'].z).x, n['q'].y - axis(n['q'].z).y, n['q'].z))) for n in nodes], lambda t: Vector((0, 0, 0)), H)
    n_cards = 0
    if lod == 0:
        per = 6200 * cfg['leaves'] / len(nodes)
        for nd in nodes:
            q = nd['q']; hr, outv = hrad(q); out = outv.normalized() if hr > 1e-3 else Vector((1, 0, 0))
            # pine tufts point up and out from the twig ends
            ax = (out * .45 + nd['t'] * .3 + Vector((0, 0, .7)) + Vector(rng.normal(0, .28, 3))).normalized()
            nl = int(per) + (1 if rng.random() < per - int(per) else 0); Lt = rng.uniform(.3, .5)
            perp0 = ax.orthogonal().normalized()
            for k in range(nl):
                s = (k + rng.uniform(.1, .9)) / max(nl, 1)
                stem = q + ax * Lt * s
                az = rng.uniform(0, 2 * math.pi); pv = (perp0 * math.cos(az) + ax.cross(perp0) * math.sin(az)).normalized()
                oa = rng.uniform(.35, 1.1) * (1 - .4 * s)
                ld = (ax * math.cos(oa) + pv * math.sin(oa)).normalized()
                ll = rng.uniform(.32, .46) * (1.1 - .2 * s)
                c = stem + ld * ll * .5
                if c.z < zmin - .7: continue
                n = ld.cross(pv).normalized(); n = (n + Vector(rng.normal(0, .25, 3))).normalized()
                light = _light(c, H, zc0, hrad(c)[0], envf(c.z), ld, c.z - nd['lz'], rng)
                tone = int(min(NT - 1, max(0, round(light * (NT - 1)))))
                key = ('L', tone, int(rng.random() < .45))
                shade = (out * .5 + Vector((0, 0, .3 + .9 * (light - .45))) + n * .2).normalized()
                buf.card(c, n, ll / .92, CELL_RECTS[key], ld, (2, 2), 0., (lambda p, v=shade: v), .6 + .4 * s, nd['phase'] + rng.uniform(0, .05), aspect=1.)
                n_cards += 1
    else:
        room = {1: 2050, 2: 720}[lod]; size = {1: (.88, 1.1), 2: (1.02, 1.25)}[lod]     # leaf coverage on screen close to LOD0 (measured in Unity)
        idx = rng.permutation(len(nodes))[:room] if len(nodes) > room else range(len(nodes))
        for i in idx:
            nd = nodes[int(i)]; q = nd['q']; hr, outv = hrad(q); out = outv.normalized() if hr > 1e-3 else Vector((1, 0, 0))
            ax = (out * .5 + nd['t'] * .4 + Vector((0, 0, .55)) + Vector(rng.normal(0, .2, 3))).normalized()
            sz = rng.uniform(*size); c = q + ax * sz * .3
            n = ax.cross(Vector((0, 0, 1))); n = (n.normalized() if n.length > 1e-3 else Vector((1, 0, 0))) + Vector((0, 0, .5)) + Vector(rng.normal(0, .25, 3)); n.normalize()
            light = _light(c, H, zc0, hrad(c)[0], envf(c.z), Vector((ax.x, ax.y, 0.)), c.z - nd['lz'], rng)
            t8 = light * (NT - 1) - .2; tone = int(np.argmin([abs(t8 - x) for x in CLUSTER_TONES]))
            shade = (out * .5 + Vector((0, 0, .3 + .9 * (light - .45))) + n * .2).normalized()
            buf.card(c, n, sz, CELL_RECTS[('C', tone)], ax, (2, 2), 0., (lambda p, v=shade: v), .8, nd['phase'], aspect=CELL_ASPECT[('C', tone)])
            n_cards += 1
    return n_cards


def extra_geometry(buf, var, lod, P, R, rng, trunk_range):
    """All the tuft cards (LOD0-2) on the leaf material; returns their triangle count."""
    global last_extra_cards
    n = _foliage(buf, var, lod, P, R, rng); last_extra_cards = n
    return 2 * n
