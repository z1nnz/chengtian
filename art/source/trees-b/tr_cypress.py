"""TR02 old-forest cypress, built the way the golden spirit tree was built (art/source/golden-spirit-tree/v001; 2026-11-12 user
direction: 全部打掉重做，參考剛剛做的金黃樹，不要再雲團了).

What is taken from the golden spirit tree:
- wood: an S-curved trunk and a real branch hierarchy, main limb -> mid branch -> twig -> tip, all fused by the Skin modifier
  (tr_skin.py), so the wood is visible and every fork grows out of its parent;
- leaves: no masses, no clouds. Leaves grow in small clusters on the tips of the twigs, each cluster a short twiglet with 4-9
  separate leaves at their own angle. The cypress "leaf" is one flat spray of scale leaves (35-55 cm), drawn big enough to read;
- colour: one tone per leaf, picked from where it sits (high, outer and facing up = light sage-green; low, inner and hanging =
  deep teal), with a little spread per leaf, like the golden tree's per-leaf palette. Each tone is its own atlas cell, so URP Lit
  needs no change.
Game budget: every leaf is one card of two triangles (about 7,000 leaves at LOD0); LOD1 and LOD2 draw a whole cluster per card.
Kept from the work pack: 9-11 m, thick twisted trunk with burls and moss from the roots, deep green leaning teal, crown narrowing
upward (lower limbs long, upper limbs short, a leader to the top).
A  upright, S-curved trunk, two burls.   B  leaning trunk, low wide crown, one big burl.
C  very twisted and lean, one side died back (two bare dead limbs), narrow and tall.
Atlas: cell 0 = 4 x 4 single sprays (8 tones x 2 shapes); cell 1 top = four cluster cells (4 tones) for LOD1 / LOD2; cell 1
bottom = moss strip.
"""
import math
import numpy as np
from mathutils import Vector
from tr_tree import Branch, catmull
from tr_tex import hexc, to_lin

# eight leaf tones, dark (inner, hanging) -> light (outer top), sRGB; deep green leaning teal, never neon
PALETTE = [hexc(h) for h in ('#0F2426', '#15302C', '#1C3C33', '#24493A', '#2E5642', '#3B634A', '#4B7253', '#5E825E')]
M_DARK, M_LIGHT = hexc('#2E3D2A'), hexc('#4A5A34')
STEM = hexc('#2A3A30')
NT = len(PALETTE)
CLUSTER_TONES = (1, 3, 4, 6)     # tone of each LOD1 / LOD2 cluster cell on the 8-step scale

CELL_RECTS = {2: (.5, .5, 1., .625)}
CELL_ASPECT = {2: 4.}
for _t in range(NT):
    for _s in range(2):
        _k = _t * 2 + _s; _c, _r = _k % 4, _k // 4
        CELL_RECTS[('L', _t, _s)] = (_c * .125, 1 - (_r + 1) * .125, (_c + 1) * .125, 1 - _r * .125); CELL_ASPECT[('L', _t, _s)] = 1.
for _k in range(4):
    _c, _r = _k % 2, _k // 2
    CELL_RECTS[('C', _k)] = (.5 + _c * .25, .625 + _r * .1875, .5 + (_c + 1) * .25, .625 + (_r + 1) * .1875); CELL_ASPECT[('C', _k)] = .25 / .1875
CELL_AO = .012
CELL_M = 1.0
BARK = 'cypress'
WOOD = 'skin'
SKIN_WOOD = {0: ((0, 1, 2, 3), 2, 9000), 1: ((0, 1, 2), 1, 2600), 2: ((0, 1), 1, 750)}     # levels kept, subdivision, wood triangle target
BARK_PAINTED = dict(src='bark_src/elder_tree_bark_v1.png', sat=.5, gain=.9, tint=(.9, .88, .9), contrast=2.1, crack=1., normal=16., smooth_val=.07, blur_n=(0, 2))


def _mix(a, b, t): return a * (1 - t) + b * t


# ------------------------------------------------------------------ atlas drawing
def leaf(st, p, d, L, w, c0, c1, z, rim=.003):
    """One leaflet folded along its midrib (lit half / shaded half), raised midrib, thin dark rim underneath; c0 at the stem, c1 at the tip."""
    p = np.array(p[:2], np.float32); d = np.array(d, np.float32); d /= np.linalg.norm(d) + 1e-9; s = np.array([-d[1], d[0]], np.float32)
    prof = [0., .5, .88, 1., .82, .5, .2, 0.]; n = len(prof)
    c = [p + d * L * i / (n - 1) for i in range(n)]
    st.strip([(c[i][0], c[i][1], z - .0006) for i in range(n)], [w * x + rim for x in prof], [tuple(to_lin(c0 * .45))] * n, ridge=0.)
    k0 = len(st.v)
    for i in range(n):
        t = i / (n - 1); lit = _mix(c0, c1, t); shd = lit * .72; hw = w * prof[i] + 1e-4; zz = z + .0003 * i
        for (x, col) in ((-1, lit), (0, lit * 1.06), (0, shd), (1, shd)):
            q = c[i] + s * hw * x
            st.v.append((float(q[0]), float(q[1]), zz + (w * .35 if x == 0 else 0.))); st.c.append(tuple(to_lin(np.clip(col, 0, 1))))
    for i in range(n - 1):
        a = k0 + i * 4
        st.f.append((a, a + 1, a + 5, a + 4)); st.f.append((a + 2, a + 3, a + 7, a + 6))


def spray(st, rng, base, d, L, tone, shape, z0=0.):
    """One flat cypress spray from `base` along d, length L: a stem with alternating chunky leaflets that shrink to a tip leaflet.
    shape 0: a single plume; shape 1: a plume with two side plumes from the base (a small fan)."""
    col = PALETTE[tone]; c0, c1 = col * .82, np.clip(col * 1.18 + .015, 0, 1)
    d = np.array(d, np.float32); d /= np.linalg.norm(d) + 1e-9; side = np.array([-d[1], d[0]]); base = np.array(base[:2], np.float32)
    def plume(b0, dd, LL, zz):
        bend = rng.normal(0, .1)
        def at(s): return b0 + (dd + side * bend * s) * LL * s
        st.strip([tuple(at(s)) + (zz,) for s in (0., .35, .7, .95)], [.02 * LL, .016 * LL, .011 * LL, .006 * LL], [tuple(to_lin(STEM))] * 4, ridge=.5)
        n = 4; sgn = 1 if rng.random() < .5 else -1
        for i in range(n * 2):
            s = (i + .8) / (n * 2 + .6); q = at(s); sgn = -sgn
            ang = sgn * rng.uniform(.45, .7); ca, sa = math.cos(ang), math.sin(ang)
            ld = (dd[0] * ca - dd[1] * sa, dd[0] * sa + dd[1] * ca)
            ll = LL * .36 * (1 - .45 * s) * rng.uniform(.9, 1.1)
            leaf(st, q, ld, ll, ll * .3, c0, _mix(c0, c1, .5 + .5 * s), z=zz + .002 + .0015 * i)
        leaf(st, at(.86), dd, LL * .24, LL * .24 * .3, c0, c1, z=zz + .016)
    if shape == 1:
        for sgn in (-1, 1):
            a = sgn * rng.uniform(.42, .55); ca, sa = math.cos(a), math.sin(a)
            plume(base + d * .05 * L, np.array((d[0] * ca - d[1] * sa, d[0] * sa + d[1] * ca)), L * .62, z0)
        plume(base, d, L * .9, z0 + .02)
    else:
        plume(base, d, L * .95, z0)


def cell_leaves(st, rng, cell):
    """Cell 0: 4 x 4 single sprays, two per tone (shape 0 and 1), each pointing up its sub-cell from a stem at the bottom."""
    S = cell / 4
    for t in range(NT):
        for s in range(2):
            k = t * 2 + s; cx = -cell / 2 + S * (k % 4 + .5); cy = cell / 2 - S * (k // 4 + .5)
            spray(st, rng, (cx, cy - .46 * S), (rng.normal(0, .04), 1.), S * .92, t, s)


def cell_clusters(st, rng, cell):
    """Cell 1 top (y -0.25..0.5): four cluster cells (2 x 2, 0.5 wide x 0.375 tall), tone dark -> light: a fan of 7 sprays from a
    base at the bottom middle, the upper sprays a tone lighter. Bottom (y -0.5..-0.25): the moss strip."""
    for k, tone in enumerate(CLUSTER_TONES):
        c, r = k % 2, k // 2
        x0, y0 = -cell / 2 + c * cell / 2, -cell / 4 + r * cell * .375; w, h = cell / 2, cell * .375
        base = np.array([x0 + w / 2, y0 + h * .06])
        for j in range(7):
            a = math.pi / 2 + (j / 6 - .5) * 2.1 + rng.normal(0, .06); L = h * (.86 - .3 * abs(j / 6 - .5) * 2)
            L = min(L, (w / 2 - .02) / max(.2, abs(math.cos(a))) if abs(math.cos(a)) > .3 else L)
            tt = min(NT - 1, max(0, tone + (1 if abs(j - 3) <= 0 else -1 if abs(j - 3) == 3 else 0)))
            spray(st, rng, base, (math.cos(a), math.sin(a)), L, tt, j % 2, z0=.004 * (3 - abs(j - 3)))
    yc = -.375 * cell
    for k in range(13):
        x = (k / 12 - .5) * .76 * cell + rng.normal(0, .012) * cell
        r = rng.uniform(.05, .075) * cell
        st.blob((x, yc + rng.normal(0, .01) * cell), r, tuple(to_lin(M_LIGHT * rng.uniform(.9, 1.05))), tuple(to_lin(M_DARK)), rng, rough=.22, z=.002 * k)


CELLS = [cell_leaves, cell_clusters]


# ------------------------------------------------------------------ skeleton (golden-spirit-tree hierarchy)
def _angdiff(a, b): return (a - b + math.pi) % (2 * math.pi) - math.pi


VARIANTS = {
    # trunk: S-curve control points (x, y, z as a fraction of H, radius as a fraction of r0)
    'A': dict(H=9.6, seed=5, r0=.66, twist=.11, mains=16, Lb=3.1, t0=.27, leaves=1.,
              trunk=[(0, 0, -.03, 1.), (0, 0, 0, .96), (.1, .04, .07, .7), (.34, .14, .17, .55), (.46, .2, .3, .45), (.3, .12, .44, .37),
                     (-.04, -.04, .58, .3), (-.2, -.12, .72, .22), (-.1, -.05, .86, .13), (0, 0, .98, .04)],
              burls=[(1.0, 1.6, .6), (3.6, 2.5, .48)], stubs=[(.1, 60), (.165, 210)], dead=None),
    'B': dict(H=9.7, seed=17, r0=.7, twist=-.09, mains=15, Lb=3.4, t0=.24, leaves=1.,
              trunk=[(0, 0, -.03, 1.), (0, 0, 0, .96), (.18, -.05, .08, .7), (.55, -.15, .2, .55), (.9, -.24, .34, .45), (1.05, -.25, .48, .37),
                     (.95, -.18, .62, .29), (1.1, -.2, .76, .21), (1.35, -.3, .88, .12), (1.45, -.35, .98, .04)],
              burls=[(2.3, 1.8, .7), (5.0, 1.0, .35)], stubs=[(.115, 140), (.18, 20)], dead=None),
    'C': dict(H=9.9, seed=29, r0=.66, twist=.17, mains=12, Lb=2.6, t0=.3, leaves=.85,
              trunk=[(0, 0, -.03, 1.), (0, 0, 0, .96), (.22, .1, .07, .7), (.6, .35, .18, .55), (.72, .5, .3, .45), (.45, .4, .43, .37),
                     (.25, .2, .56, .3), (.5, .35, .7, .22), (.85, .62, .84, .13), (.95, .7, .98, .04)],
              burls=[(.4, 1.3, .5), (4.2, 2.2, .55), (2.0, 3.1, .4)], stubs=[(.1, 300), (.165, 40)], dead=(200, 95)),
}
NAMES = {'A': 'Cypress', 'B': 'Cypress', 'C': 'OldCypress'}
ZH = {'A': '柏（S 形直幹、兩個樹瘤、下枝長上枝短收成尖頂）', 'B': '柏（斜幹、樹冠低而寬、一個大樹瘤）', 'C': '老柏（大扭大斜、一側枯枝、樹冠窄高）'}
_NODES = {}         # var -> leaf nodes: dict(q, t (twig direction), phase, wind)
last_extra_cards = 0


def _trunk(cfg):
    H = cfg['H']; r0 = cfg['r0']; zt = H * cfg['trunk'][-1][2]
    ctrl = [Vector((x, y, -.3 if z < 0 else z * H)) for x, y, z, r in cfg['trunk']]
    dense = catmull(ctrl, 20); zz = np.array([p.z for p in dense])
    rr = np.interp(np.linspace(0, 1, len(dense)), np.linspace(0, 1, len(ctrl)), [r ** .75 * r0 for x, y, z, r in cfg['trunk']])     # thick old trunk
    xs = np.array([p.x for p in dense]); ys = np.array([p.y for p in dense])
    def P(t):
        z = -.3 + (zt + .3) * min(1., max(0., t)); return Vector((float(np.interp(z, zz, xs)), float(np.interp(z, zz, ys)), z))
    def R(t):
        z = -.3 + (zt + .3) * min(1., max(0., t)); return float(np.interp(z, zz, rr))
    return P, R, zt


def _grow(rng, p, d, L, r0, r1, droop=0., upturn=.35, wander=.14, step=.32, zmin=2.35):
    """golden-spirit-tree grow(): a branch that wanders, sags by `droop`, then its last fifth turns up. Returns points and radii."""
    n = max(3, int(round(L / step))); d = Vector(d).normalized(); pts = [Vector(p)]; rads = [r0]
    for k in range(1, n + 1):
        s = k / n
        lift = -droop * (.25 + .9 * s) if s < .8 else upturn
        d = (d + Vector(rng.normal(0, wander, 3)) + Vector((0, 0, lift * .3))).normalized()
        q = pts[-1] + d * (L / n)
        if q.z < zmin: d = (d + Vector((0, 0, .7))).normalized(); q = pts[-1] + d * (L / n)      # turn up instead of a flat clamp
        q.z = max(q.z, zmin); pts.append(q); rads.append(r0 + (r1 - r0) * s ** .8)
    return pts, rads


def _at(pts, s):
    x = max(0., min(1., s)) * (len(pts) - 1); i = min(int(x), len(pts) - 2); return pts[i].lerp(pts[i + 1], x - i), i


def skeleton(var):
    cfg = VARIANTS[var]; rng = np.random.default_rng(cfg['seed']); H = cfg['H']
    P, R, zt = _trunk(cfg)
    ts = np.linspace(0, 1., 24)
    trunk = Branch([P(t) for t in ts], [max(.025, R(t)) for t in ts], 0, 0., 0., 0., 'trunk', _section(cfg['seed'] * .7, cfg['twist'], cfg['burls']))
    trunk.twist = cfg['twist']
    branches = [trunk]; nodes = []
    dead = cfg['dead']; az = rng.uniform(0, 6.3); nm = cfg['mains']
    for i in range(nm):
        u = i / (nm - 1); t = cfg['t0'] + (.93 - cfg['t0']) * u ** .95 + rng.normal(0, .012)
        az += 2.4 + rng.normal(0, .25)
        if dead and abs(_angdiff(az, math.radians(dead[0]))) < math.radians(dead[1]) / 2 and u < .7: continue
        L = cfg['Lb'] * (1 - u) ** 1.05 + .45; start = P(t); out = Vector((math.cos(az), math.sin(az), 0)); phase = rng.random()
        # main limb: leaves the trunk climbing, runs out, the outer third sags and the tip turns up (golden tree's arch)
        rise = L * (.07 + .45 * u)
        cp = [start, start + out * .3 * L + Vector((0, 0, rise * .55)), start + out * .66 * L + Vector((0, 0, rise)),
              start + out * L + Vector((0, 0, rise * .7 - .2 * L * (1 - u)))]
        cp = [c + Vector((*rng.normal(0, .08 * L, 2), 0)) * float(k > 0) for k, c in enumerate(cp)]
        pts = catmull(cp, 3); pts = [pts[0]] + pts[2:]
        # keep moving limb wood above 2.4 m by lifting the limb smoothly (a hard clamp left a kink where it kicked in)
        D = max(0., max(2.4 - p.z for p in pts[1:]))
        for k, p in enumerate(pts[1:], 1): p.z += D * min(1., 2. * k / (len(pts) - 1))
        r0 = max(.05, R(t) * .4)        # well under the trunk: its own Skin island, no lumpy fused collar
        rads = [r0 * (1 - .82 * (k / (len(pts) - 1)) ** .8) + .012 for k in range(len(pts))]
        branches.append(Branch(pts, rads, 1, .02, .3, phase, 'limb'))
        # mid branches along the outer two thirds, alternating sides
        nmid = 2 + int(L * .7); sgn = 1 if rng.random() < .5 else -1; owners = [(pts, rads, 1)]
        for k in range(nmid):
            s = .32 + .6 * (k + rng.uniform(.2, .8)) / nmid; q, j = _at(pts, s); sgn = -sgn
            tdir = (pts[j + 1] - pts[j]).normalized(); side = tdir.cross(Vector((0, 0, 1))).normalized()
            ang = rng.uniform(.6, 1.1); d = tdir * math.cos(ang) + side * sgn * math.sin(ang) + Vector((0, 0, rng.uniform(.05, .45)))
            Lm = L * rng.uniform(.3, .42) * (1.15 - .4 * s); rq = float(np.interp(s, np.linspace(0, 1, len(rads)), rads))
            mp, mr = _grow(rng, q, d, Lm, rq * .5, .02, droop=.35 if s > .6 else .08, upturn=.4)
            branches.append(Branch(mp, mr, 2, .3, .5, phase, 'twig')); owners.append((mp, mr, 2))
        # twigs on the mids and on the outer part of the main; tips (leaf carriers, no wood) on every twig
        for (bp, br_, dep) in owners:
            nt_ = 3 if dep == 1 else 2; sg = 1
            for k in range(nt_):
                s = (.62 if dep == 1 else .4) + (.34 if dep == 1 else .55) * (k + rng.uniform(.2, .8)) / nt_; q, j = _at(bp, s); sg = -sg
                tdir = (bp[j + 1] - bp[j]).normalized(); side = tdir.cross(Vector((0, 0, 1))).normalized()
                ang = rng.uniform(.6, 1.1); d = tdir * math.cos(ang) + side * sg * math.sin(ang) + Vector((0, 0, rng.uniform(-.15, .35)))
                tp, tr = _grow(rng, q, d, rng.uniform(.7, 1.2), max(.014, float(np.interp(s, np.linspace(0, 1, len(br_)), br_)) * .5), .01,
                               droop=rng.uniform(.1, .45), upturn=.45, step=.28)
                branches.append(Branch(tp, tr, 3, .5, .7, phase, 'twig'))
                for s2 in (.3, .5, .7, .88, 1.):
                    q2, j2 = _at(tp, s2); nodes.append(dict(q=q2, t=(tp[min(j2 + 1, len(tp) - 1)] - tp[j2]).normalized(), phase=phase))
            # the branch's own outer end carries leaves too
            for s2 in (.8, 1.):
                q2, j2 = _at(bp, s2); nodes.append(dict(q=q2, t=(bp[min(j2 + 1, len(bp) - 1)] - bp[j2]).normalized(), phase=phase))
    # leader: the thin top of the trunk carries leaves up to the point
    for t in (.84, .9, .95, 1.):
        nodes.append(dict(q=P(t), t=Vector((rng.normal(0, .3), rng.normal(0, .3), 1.)).normalized(), phase=rng.random()))
    if dead:                                                              # dead limbs (C): bare, broken ends
        for (t, L) in ((.36, 2.3), (.5, 1.7)):
            a = math.radians(dead[0]) + rng.normal(0, .2); s = P(t)
            dp, dr = _grow(rng, s, Vector((math.cos(a), math.sin(a), .25)), L, R(t) * .38, .03, droop=.05, upturn=.1, wander=.1)
            branches.append(Branch(dp, dr, 1, .02, .15, 0., 'limb', cap=True))
            q, j = _at(dp, .55); sp_, sr = _grow(rng, q, Vector((math.cos(a + .8), math.sin(a + .8), .6)), .8, dr[j] * .5, .02, upturn=0.)
            branches.append(Branch(sp_, sr, 2, .05, .1, 0., 'twig', cap=True))
    for (t, az_) in cfg['stubs']:
        a = math.radians(az_); s = P(t); dd = Vector((math.cos(a), math.sin(a), -.1)).normalized(); L = rng.uniform(.3, .6)
        branches.append(Branch([s - dd * R(t) * .4, s + dd * L * .5, s + dd * L], [R(t) * .2, R(t) * .16, R(t) * .12], 3, 0., 0., 0., 'stub', cap=True))
    _NODES[var] = [n for n in nodes if n['q'].z > 2.4]
    return branches, [], H, P, R


# ------------------------------------------------------------------ leaves
def _light(q, H, zc0, hr, envr, leafdir, rng):
    """golden tree light: high, outer and facing up = light; low, inner and hanging = dark."""
    hn = min(1., max(0., (q.z - zc0) / max(H - zc0, 1e-3))); rim = min(1., hr / max(envr, .3))
    return .3 * hn + .44 * rim + .3 * (.5 + .5 * leafdir.z) - .1 + rng.normal(0, .06)


def _envelope(nodes, P, H):
    """Crown radius per height band (how far out the leaves go at each height) -> function z -> radius."""
    zs = np.array([n['q'].z for n in nodes]); hr = np.array([(n['q'] - P(0)).to_2d().length for n in nodes])
    bands = np.arange(2., H + 1.2, .8); env = []
    for b in bands:
        m = np.abs(zs - b) < .8
        env.append(np.percentile(hr[m], 90) if m.sum() > 3 else .5)
    return lambda z: float(np.interp(z, bands, env))


def _foliage(buf, var, lod, P, R, rng):
    cfg = VARIANTS[var]; H = cfg['H']; nodes = _NODES[var]; zc0 = P(cfg['t0']).z
    def axis(z): return P(min(1., max(0., (z + .3) / (H * cfg['trunk'][-1][2] + .3))))
    def hrad(q): a = axis(q.z); return math.hypot(q.x - a.x, q.y - a.y), Vector((q.x - a.x, q.y - a.y, 0))
    envf = _envelope([dict(q=Vector((n['q'].x - axis(n['q'].z).x, n['q'].y - axis(n['q'].z).y, n['q'].z)) + P(0) * 0) for n in nodes], lambda t: Vector((0, 0, 0)), H)
    n_cards = 0
    if lod == 0:
        per = 6200 * cfg['leaves'] / len(nodes)
        for nd in nodes:
            q = nd['q']; hr, outv = hrad(q); out = outv.normalized() if hr > 1e-3 else Vector((1, 0, 0))
            rim = min(1., hr / max(envf(q.z), .3)); hang = .15 + .5 * max(0., rim - .4)
            ax = (out * .5 + nd['t'] * .6 + Vector((0, 0, .15 - hang)) + Vector(rng.normal(0, .35, 3))).normalized()
            nl = int(per) + (1 if rng.random() < per - int(per) else 0); Lt = rng.uniform(.45, .7)
            perp0 = ax.orthogonal().normalized()
            base_light = None
            for k in range(nl):
                s = (k + rng.uniform(.1, .9)) / max(nl, 1)
                stem = q + ax * Lt * s
                az = rng.uniform(0, 2 * math.pi); pv = (perp0 * math.cos(az) + ax.cross(perp0) * math.sin(az)).normalized()
                oa = rng.uniform(.5, 1.15) * (1 - .45 * s)
                ld = (ax * math.cos(oa) + pv * math.sin(oa)).normalized()
                ll = rng.uniform(.36, .52) * (1.12 - .25 * s)
                c = stem + ld * ll * .5
                if c.z < 2.3: continue
                n = ld.cross(pv).normalized()
                n = (n + Vector(rng.normal(0, .25, 3))).normalized()
                light = _light(c, H, zc0, hrad(c)[0], envf(c.z), ld, rng)
                tone = int(min(NT - 1, max(0, round(light * (NT - 1)))))
                key = ('L', tone, int(rng.random() < .45))
                shade = (out * .55 + Vector((0, 0, .25 + .9 * (light - .45))) + n * .2).normalized()
                buf.card(c, n, ll / .92, CELL_RECTS[key], ld, (2, 2), 0., (lambda p, v=shade: v), .6 + .4 * s, nd['phase'] + rng.uniform(0, .05), aspect=1.)
                n_cards += 1
    else:
        room = {1: 2050, 2: 720}[lod]; size = {1: (.95, 1.18), 2: (1.16, 1.42)}[lod]     # same leaf coverage on screen as LOD0 (measured in Unity)
        idx = rng.permutation(len(nodes))[:room] if len(nodes) > room else range(len(nodes))
        for i in idx:
            nd = nodes[int(i)]; q = nd['q']; hr, outv = hrad(q); out = outv.normalized() if hr > 1e-3 else Vector((1, 0, 0))
            rim = min(1., hr / max(envf(q.z), .3))
            ax = (out * .6 + nd['t'] * .5 + Vector((0, 0, .25 - .4 * max(0., rim - .4))) + Vector(rng.normal(0, .2, 3))).normalized()
            sz = rng.uniform(*size); c = q + ax * sz * .3
            n = ax.cross(Vector((0, 0, 1))); n = (n.normalized() if n.length > 1e-3 else Vector((1, 0, 0))) + Vector((0, 0, .5)) + Vector(rng.normal(0, .25, 3)); n.normalize()
            light = _light(c, H, zc0, hrad(c)[0], envf(c.z), Vector((ax.x, ax.y, 0.)), rng)     # a cluster's twiglet is not a leaf facing the sky
            t8 = light * (NT - 1) - .6; tone = int(np.argmin([abs(t8 - x) for x in CLUSTER_TONES]))
            shade = (out * .55 + Vector((0, 0, .25 + .9 * (light - .45))) + n * .2).normalized()
            buf.card(c, n, sz, CELL_RECTS[('C', tone)], ax, (2, 2), 0., (lambda p, v=shade: v), .8, nd['phase'], aspect=CELL_ASPECT[('C', tone)])
            n_cards += 1
    return n_cards


def _section(seed, twist, burls):
    """Root lobes and flare, uneven spiral ridges turning with height (two frequencies, so it is not a regular fluted column),
    round burls (each a cluster of three bumps)."""
    def fn(th, s, p):
        z = p.z + .3
        root = .8 * math.exp(-z / .8) * max(0., math.cos(5 * th + seed)) ** 2
        flare = .5 * math.exp(-z / .85)
        tw = th - 2 * math.pi * twist * z
        # bark plates: wide rounded ridges split by narrow deep furrows (|cos|^0.6 shape), turning with height; two frequencies so
        # it is not a fluted column (2026-11-12 "樹幹像塑膠": the old soft cosine ribs read as moulded plastic)
        def ridge(x): return abs(math.cos(x / 2)) ** .6 - .62
        rib = (.16 * ridge(6 * tw + seed) + .08 * ridge(11 * tw + 2.1 * seed + .7 * z) + .04 * math.cos(2 * th + .9 * z + seed)) * (.65 + .35 * math.exp(-z / 4))
        burl = 0.
        for (tb, zb, a) in burls:
            for k, (dt, dz, f) in enumerate(((0, 0, 1.), (.35, .22, .7), (-.3, .28, .6))):
                burl += a * f * math.exp(-(_angdiff(th, tb + dt) / .4) ** 2 - ((z - zb - dz) / .3) ** 2)
        return 1 + root + flare + rib + burl
    return fn
def _moss(buf, var, lod, P, R, rng, trunk_range):
    """Moss pads on the trunk from the roots up to ~1.5 m, conforming to the built trunk surface (sampled from its vertices),
    leaf material, moss cell, wind 0 (they sit on the bark). LOD0 and LOD1 only."""
    n = {0: 75, 1: 22}.get(lod, 0)
    if not n: return 0
    H = VARIANTS[var]['H']; zt = H * VARIANTS[var]['trunk'][-1][2]
    def tz(z): return min(1., max(0., (z + .3) / (zt + .3)))
    # trunk surface samples in (angle, z) -> radius about the trunk axis
    vs = np.array([tuple(v) for v in buf.v[trunk_range[0]:trunk_range[1]]], np.float32)
    vs = vs[vs[:, 2] < 2.2]
    ax = np.array([tuple(P(tz(z))) for z in vs[:, 2]], np.float32)
    ang = np.arctan2(vs[:, 1] - ax[:, 1], vs[:, 0] - ax[:, 0]); rad = np.hypot(vs[:, 0] - ax[:, 0], vs[:, 1] - ax[:, 1])
    def surf(a, z):
        # inverse-distance blend of the nearest trunk vertices in (arc length, height); never empty, so coarse LODs work too
        da = np.abs((ang - a + np.pi) % (2 * np.pi) - np.pi); dist = da * np.maximum(rad, .2) + np.abs(vs[:, 2] - z)
        m = np.argsort(dist)[:6]
        w = 1 / (dist[m] + .03)
        return float((rad[m] * w).sum() / w.sum())
    u0, v0, u1, v1 = CELL_RECTS[2]; gu, gv = 5, 3; tris = 0
    for k in range(n):
        z = .05 + 1.8 * rng.random() ** 1.8; a = rng.uniform(-math.pi, math.pi)
        h = rng.uniform(.3, .46) * (1.15 - .35 * (z - .1) / 1.3); wdt = h * CELL_ASPECT[2] * rng.uniform(.75, 1.0)     # metres along the surface
        c = P(tz(z)); r0 = max(surf(a, z), .2); span = wdt / r0
        # a random horizontal slice of the moss strip, so pads differ
        su = rng.uniform(0, .25); uu0 = u0 + (u1 - u0) * su; uu1 = uu0 + (u1 - u0) * .75
        base = len(buf.v)
        for j in range(gv):
            y = j / (gv - 1) - .5; zz = z + y * h
            for i in range(gu):
                x = i / (gu - 1) - .5; aa = a + x * span
                cc = P(tz(zz)); rr = surf(aa, zz) + .012
                p = Vector((cc.x + rr * math.cos(aa), cc.y + rr * math.sin(aa), zz))
                buf.v.append(p); buf.nrm.append(Vector((math.cos(aa), math.sin(aa), .15)).normalized()); buf.col.append(buf.wind(0., 0., p.z))
        for j in range(gv - 1):
            for i in range(gu - 1):
                q = base + j * gu + i
                buf.f.append((q, q + 1, q + gu + 1, q + gu)); buf.fmat.append(1)
                uv = lambda ii, jj: (uu0 + (uu1 - uu0) * ii / (gu - 1), v0 + (v1 - v0) * jj / (gv - 1))
                buf.fuv.append((uv(i, j), uv(i + 1, j), uv(i + 1, j + 1), uv(i, j + 1))); tris += 2
    return tris


def extra_geometry(buf, var, lod, P, R, rng, trunk_range):
    """Trunk moss pads (LOD0, LOD1) and all the leaf cards (LOD0-2), both on the leaf material; returns their triangle count."""
    global last_extra_cards
    t = _moss(buf, var, lod, P, R, rng, trunk_range); n = _foliage(buf, var, lod, P, R, rng); last_extra_cards = n
    return t + 2 * n
