"""TR01 Chinese pine: needle-tuft atlas cells and the three variants.

Reference: art/references/TR01/TR01-cand-4.png (limb order, cloud masses, colours, bark); proportions from the work pack, not the sheet
(the sheets are bonsai-like): 12-14 m, trunk ~0.6 m across at chest height, first limb at ~5 m.
A  13.2 m  S-curved trunk, five limbs in tiers and a flat-topped crown (the common pine for A1 / A2 / A4).
B  12.6 m  trunk leaning one way then back, one long low limb sweeping out, wider crown.
C  12.2 m  cliff pine for B1: thinner trunk leaning hard to one side, fewer and smaller masses, one long reaching limb, broken stubs.
"""
import math
import numpy as np
from mathutils import Vector
from tr_tree import Branch, Puff
from tr_tex import hexc, to_lin

# needle colours (sRGB): muted blue-green, a little warmth only at the sunlit tips
N_DARK, N_MID, N_LIGHT, N_TIP = hexc('#253F3B'), hexc('#3B5E57'), hexc('#628676'), hexc('#8B9E74')
TWIG = hexc('#3A2A22')


def _needle_col(t_tone, v):
    base = N_DARK * (1 - t_tone) + N_MID * t_tone
    tip = N_LIGHT * (1 - t_tone) + N_TIP * t_tone
    return tuple(to_lin(base * (1 - v) + tip * v))


def tuft(st, p, d, rng, L, n, spread, tone, lift=.25):
    """A fascicle burst: needles fanning around direction d (in the card plane, z toward the viewer)."""
    p = np.array(p, np.float32); d = np.array(d, np.float32); d /= np.linalg.norm(d) + 1e-9
    for i in range(n):
        a = (i / max(n - 1, 1) - .5) * 2 * spread + rng.normal(0, .07)
        ca, sa = math.cos(a), math.sin(a)
        dd = np.array([d[0] * ca - d[1] * sa, d[0] * sa + d[1] * ca, 0.], np.float32)
        ln = L * rng.uniform(.55, 1.12) * (1 - .3 * abs(a) / max(spread, 1e-3))
        side = np.array([-dd[1], dd[0], 0.], np.float32); curve = rng.normal(0, .14)
        pts = []; ws = []; cs = []
        start = p + dd * L * rng.uniform(0, .12)
        tn = min(1., max(0., tone + rng.normal(0, .08)))
        for k in range(5):
            v = k / 4
            q = start + dd * ln * v + side * curve * ln * v * v + np.array([0, 0, lift * ln * v * (1 - .5 * v)], np.float32)
            pts.append(tuple(q)); ws.append(.0042 * (1 - .75 * v) + .0005); cs.append(_needle_col(tn, v))
        st.strip(pts, ws, cs, ridge=.35)


def twig(st, pts, w0, w1):
    cs = [tuple(to_lin(TWIG))] * len(pts)
    st.strip(pts, list(np.linspace(w0, w1, len(pts))), cs, ridge=.6)


def cell_clump(st, rng, cell):
    """Cell 0: a dense rounded clump of tufts seen from outside, ragged needle edge, lit top layer."""
    R = .44 * cell; lobes = [(rng.uniform(0, 6.3), rng.uniform(.05, .1) * cell) for _ in range(3)]
    def inside(x, y):
        r = math.hypot(x, y); a = math.atan2(y, x)
        rr = R * (1 + sum(.12 * math.cos(a - b) ** 9 for b, _ in lobes) - .05 * math.cos(3 * a + 1))
        return r < rr * .82
    # dark body under the tufts so the clump reads as one mass (no holes in the middle), several overlapping discs
    body_in, body_out = tuple(to_lin(N_MID * 1.1)), tuple(to_lin(N_MID))
    st.blob((0, 0), R * .62, body_in, body_out, rng, rough=.12, z=-.02)
    for k in range(6):
        a = rng.uniform(0, 6.3); r = R * rng.uniform(.25, .45)
        st.blob((r * math.cos(a), r * math.sin(a)), R * rng.uniform(.28, .4), body_in, body_out, rng, rough=.2, z=-.015)
    # main twigs radiating from the centre, tufts along them
    for k in range(9):
        a = k / 9 * 2 * math.pi + rng.normal(0, .2); pts = []; p = np.array([rng.normal(0, .02), rng.normal(0, .02), 0.])
        d = np.array([math.cos(a), math.sin(a), 0.])
        for s in range(7):
            pts.append(tuple(p)); d = d + np.array([rng.normal(0, .18), rng.normal(0, .18), 0.]); d /= np.linalg.norm(d)
            p = p + d * .055 * cell
            if not inside(p[0], p[1]): break
        if len(pts) > 1: twig(st, pts, .009 * cell, .004 * cell)
        for q in pts[1:]:
            tuft(st, (q[0], q[1], .01 + .02 * len(pts)), d, rng, .11 * cell, 15, 1.2, rng.uniform(.25, .55))
    # fill: tufts layered toward the viewer, lighter on top
    for k in range(150):
        r = R * .86 * math.sqrt(rng.random()); a = rng.uniform(0, 2 * math.pi)
        x, y = r * math.cos(a), r * math.sin(a)
        if not inside(x, y): continue
        outward = np.array([x, y, 0.]) + rng.normal(0, .05, 3) * cell; outward[2] = 0
        z = .05 + .1 * (1 - r / R) + rng.uniform(0, .04)
        tone = min(1., .35 + .55 * (1 - r / R) + rng.normal(0, .1))
        tuft(st, (x, y, z * cell), outward, rng, .115 * cell, 13, rng.uniform(1.2, 2.4), tone)


def cell_spray(st, rng, cell):
    """Cell 1: an open branchlet spray growing up the cell (+v), used on the mass edges and undersides."""
    p = np.array([0., -.47 * cell, 0.]); d = np.array([0., 1., 0.]); main = [tuple(p)]
    for s in range(9):
        d = d + np.array([rng.normal(0, .08) - p[0] / cell * .6, 0, 0]); d /= np.linalg.norm(d); p = p + d * .095 * cell; main.append(tuple(p))
    twig(st, main, .012 * cell, .005 * cell)
    for i, q in enumerate(main[2:], 2):
        t = i / len(main)
        for sgn in (-1, 1):
            if rng.random() < .15: continue
            a = math.pi / 2 + sgn * rng.uniform(.6, 1.0)
            dd = np.array([math.cos(a), math.sin(a), 0.]); ln = min((.2 - .12 * t) * cell, (.36 * cell - abs(q[0])) / max(abs(dd[0]), .2))
            sp = [q, tuple(np.array(q) + dd * ln * .5), tuple(np.array(q) + dd * ln)]
            twig(st, sp, .006 * cell, .003 * cell)
            for r_ in (.5, 1.):
                c = np.array(q) + dd * ln * r_
                tuft(st, (c[0], c[1], .02 * cell), dd + np.array([0, .4, 0]), rng, .1 * cell, 15, 1.0, rng.uniform(.3, .7))
        tuft(st, (q[0], q[1], .03 * cell), d, rng, .11 * cell, 16, 1.3, .3 + .5 * t)


CELLS = [cell_clump, cell_spray]
CELL_M = 1.0          # one atlas cell covers 1 m of card
BARK = 'pine'


# ------------------------------------------------------------------ skeleton
def _trunk_fn(H, lean, wob, r0, top_frac):
    """Return (point(t), radius(t)) for a trunk from z = -0.3 to H * top_frac."""
    zt = H * top_frac
    def P(t):
        z = -.3 + (zt + .3) * t
        x = lean[0] * t ** 1.3 + wob[0] * math.sin(math.pi * t * wob[2] + wob[3])
        y = lean[1] * t ** 1.3 + wob[1] * math.sin(math.pi * t * wob[2] * .8 + wob[3] + 1.)
        return Vector((x, y, z))
    def R(t): return r0 * ((1 - t) ** 1.1 * .78 + .22)
    return P, R


def _section(seed, lobes=5, amp=.95, reach=1.0):
    def fn(th, s, p):
        z = p.z + .3
        root = amp * math.exp(-z / reach) * max(0., math.cos(lobes * th + seed)) ** 2
        flare = .55 * math.exp(-z / .9)
        ribs = .06 * math.cos(3 * th + seed * 2 + s * .4)
        return 1 + root + flare + ribs * math.exp(-z / 3)
    return fn


def _limb(P, R, t, az, L, rise, droop, wig, rng, r_mul=.68):
    start = P(t); d = Vector((math.cos(az), math.sin(az), 0)); side = Vector((-d.y, d.x, 0))
    pts = []
    kinks = [Vector((0, 0, 0))] + [side * rng.normal(0, .05 * L) + Vector((0, 0, rng.normal(0, .035 * L))) for _ in range(6)]
    for k in range(7):
        s = k / 6
        # pine limb: leaves the trunk climbing, elbows out level, sags, then the tip turns up under its pad; a few kinks
        climb = .25 * L * (1 - math.exp(-s * 5.5))
        dz = climb + L * (rise * s - droop * s * s + .9 * droop * s ** 3) - .25 * L * s * s * (1 - s)
        pts.append(start + d * (L * s) + side * (wig * L * math.sin(math.pi * s * 1.6)) + Vector((0, 0, dz)) + kinks[k] * min(1., s * 3))
    pts[0] = start - d * R(t) * .5
    rads = [R(t) * r_mul * (1 - .82 * (k / 6) ** .9) for k in range(7)]
    return pts, rads


def _mass(end, d, rng, size, mass_id, phase, n=5, flat=.52):
    """A cloud mass: a big dome puff, smaller domes around it (along and across the limb), a little lower; flat-ish undersides."""
    side = Vector((-d.y, d.x, 0)); puffs = []
    size *= 1.3
    c0 = end + Vector((0, 0, .32 * size))
    puffs.append(Puff(c0, (1.3 * size, 1.2 * size, flat * 1.3 * size), mass_id, phase, bottom=.55))
    for k in range(n - 1):
        a = (k + .5) / (n - 1) * 2 * math.pi + rng.uniform(-.5, .5)
        off = d * (math.cos(a) * 1.05 * size) + side * (math.sin(a) * .95 * size) + Vector((0, 0, rng.uniform(-.28, .02) * size))
        s = rng.uniform(.6, .8)
        puffs.append(Puff(c0 + off, (s * 1.2 * size, s * 1.1 * size, flat * s * 1.35 * size), mass_id, phase, bottom=.55))
    return puffs


VARIANTS = {
    'A': dict(H=13.2, seed=11, r0=.58, lean=(.7, .25), wob=(.85, .35, 1.7, .3), top=.84,
              limbs=[(.37, 200, 4.0, .10, .28, 1.2), (.45, 330, 3.6, .12, .25, 1.15), (.55, 90, 3.3, .14, .22, 1.1),
                     (.64, 250, 2.9, .16, .2, 1.0), (.73, 30, 2.5, .2, .2, .95)],
              top_size=1.35, stubs=[(.16, 40), (.22, 150), (.3, 290)]),
    'B': dict(H=12.6, seed=23, r0=.6, lean=(-1.1, .4), wob=(.9, .3, 1.4, 2.1), top=.83,
              limbs=[(.33, 10, 5.0, .08, .3, 1.25), (.43, 140, 3.4, .12, .24, 1.1), (.52, 260, 3.6, .12, .24, 1.15),
                     (.6, 60, 3.0, .15, .2, 1.0), (.68, 190, 2.8, .16, .2, 1.0), (.76, 310, 2.3, .2, .2, .9)],
              top_size=1.45, stubs=[(.18, 220), (.25, 80)]),
    'C': dict(H=12.6, seed=37, r0=.43, lean=(4.2, -.9), wob=(.9, .3, 1.1, .8), top=.86,
              limbs=[(.45, 30, 4.6, .14, .22, 1.0), (.58, 200, 2.6, .16, .2, .85), (.7, 340, 2.2, .2, .18, .8)],
              top_size=1.15, stubs=[(.2, 120), (.28, 250), (.36, 160), (.5, 100)]),
}
NAMES = {'A': 'Pine', 'B': 'Pine', 'C': 'CliffPine'}
ZH = {'A': '松（S 形主幹、五層葉團）', 'B': '松（斜幹、一條低長枝、樹冠較寬）', 'C': '崖松（細幹大斜、葉團少而小）'}


def skeleton(var):
    cfg = VARIANTS[var]; rng = np.random.default_rng(cfg['seed']); H = cfg['H']
    P, R = _trunk_fn(H, cfg['lean'], cfg['wob'], cfg['r0'], cfg['top'])
    ts = np.linspace(0, 1, 12)
    branches = [Branch([P(t) for t in ts], [R(t) for t in ts], 0, 0., 0., 0., 'trunk', _section(cfg['seed'] * .7))]      # trunk wind 0
    puffs = []; mass = 0
    for (t, az, L, rise, droop, size) in cfg['limbs']:
        azr = math.radians(az + rng.normal(0, 4)); phase = rng.random()
        pts, rads = _limb(P, R, t, azr, L, rise, droop, rng.uniform(-.06, .06), rng)
        branches.append(Branch(pts, rads, 1, .02, .3, phase, 'limb'))
        end = pts[-1]; d = Vector((math.cos(azr), math.sin(azr), 0))
        ps = _mass(end, d, rng, size, mass, phase); puffs += ps; mass += 1
        for pf in ps[1:]:      # sub-branches from the limb into each side puff
            a = pts[4]; b = pf.c - Vector((0, 0, pf.r.z * .4)); mid = (a + b) / 2 + Vector((0, 0, .15))
            branches.append(Branch([a, mid, b], [rads[4] * .6, rads[4] * .4, .025], 2, .3, .5, phase, 'twig'))
        if L > 3.4:            # a smaller pad half way along a long limb
            m = pts[3]; ps2 = _mass(m + Vector((0, 0, -.05)), d, rng, size * .62, mass, phase + .3, n=3); puffs += ps2; mass += 1
    # crown on top
    top = P(1.); phase = rng.random()
    ps = _mass(top, Vector((1, 0, 0)), rng, cfg['top_size'], mass, phase, n=5, flat=.55); puffs += ps; mass += 1
    for pf in ps[1:]:
        a = P(.93); b = pf.c - Vector((0, 0, pf.r.z * .4))
        branches.append(Branch([a, (a + b) / 2 + Vector((0, 0, .2)), b], [R(.93) * .5, R(.93) * .35, .03], 2, .2, .5, phase, 'twig'))
    # dead stubs below the first limb (pines shed their lower limbs)
    for (t, az) in cfg['stubs']:
        a = math.radians(az); s = P(t); d = Vector((math.cos(a), math.sin(a), -.15)).normalized(); L = rng.uniform(.35, .8)
        branches.append(Branch([s - d * R(t) * .4, s + d * L * .5, s + d * L], [R(t) * .22, R(t) * .17, R(t) * .12], 3, 0., 0., 0., 'stub', cap=True))
    return branches, puffs, H, P, R
