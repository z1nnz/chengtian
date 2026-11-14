"""TR01 v002 pine (松), 2026-11-14 work pack 「樹木重做 v2」, rebuilt 2026-11-15 from the chosen three-view
art/references/TR01/v002-r3/TR01-cand-1.png (full, layered crown; branches seen between the tiers; one long low limb).

Built the sky-island world-tree way (docs/execution/2026-11-14/tree-method), in its order:
  trunk (S curve, 9 control points) -> 3 silhouette limbs, then the rest (unequal, never mirrored) -> secondary branches ->
  tip twigs (the sprays) -> crown anchors = the twig groups of each limb (7-13 sprays each, front / back layer) ->
  needle tufts along each spray's parameter t -> vertex colour (height, rim, inside, occlusion in A) -> bark last.
Wood: one tube per branch, each child starting inside its parent (no Skin modifier, so no seams along a limb).
Needles: pine fascicles (tv2_core.Buf2.needle_pair: five vertices, two triangles, two needles from one base); 9-12 open
forward round a point of a tip twig as a brush (a pine shoot), brushes follow the twig from 30 % of its length to the tip.
A  15 m  broad crown from 6 m up; one long low limb to the left (-X) sets the silhouette, tiers to the top.
B  14.5 m  trunk leaning a little right, taller and narrower crown, its long limb to the right-back.
C  13.5 m  cliff pine for B1: thin trunk leaning hard, one long reaching limb, short limbs, a sparse crown, three stubs.
"""
import math
import numpy as np
from mathutils import Vector
from tr_tree import Branch, catmull
from tv2_core import at, tangent, Anchor, envelope_fn, palette_colour

SP = 'TR01'
REFERENCE = 'art/references/TR01/v002-r3/TR01-cand-1.png（prompt.txt 同資料夾）'
# needle tones dark (inside / under a tier) -> light (top / outside), sRGB; muted blue-green after cand-1, never neon
PALETTE = ['#2E4244', '#3B574F', '#4E6D5E', '#66876F', '#87A184', '#B2C49E']
OCCL_LO = .55
BARK_PAINTED = dict(src='bark_src/elder_tree_bark_v1.png', sat=.8, gain=.95, tint=(1.16, .86, .72), contrast=1.25, crack=.35, normal=10., smooth_val=.07, blur_n=(1, 3))
LOD_CAP = {0: 60000, 1: 15000, 2: 4000}
# tube sides / ring step (m) per level and LOD; None = that level is not built at this LOD (its needles still are)
WOOD = {0: {0: (14, .36), 1: (6, .7), 2: (5, .9), 3: (3, 2.), 9: (8, .3)},
        1: {0: (9, .8), 1: (5, 1.0), 2: (3, 1.4), 3: None, 9: (4, .5)},
        2: {0: (6, 1.6), 1: (4, 2.0), 2: None, 3: None, 9: (3, 1.)}}
# needle bundle size per LOD (length, width m) and how many bundles per rosette
NEEDLE = {0: dict(L=(.52, .7), W=(.1, .13), per=(9, 12), body=0, BL=(.55, .75), BW=(.2, .27)), 1: dict(L=(.75, .95), W=(.16, .21), per=(6, 8), body=0, BL=(.8, 1.0), BW=(.32, .4)), 2: dict(L=(1.2, 1.5), W=(.34, .44), per=(4, 5), body=0, BL=(1.3, 1.6), BW=(.6, .75))}
LEAF_GEOMETRY = ('pine fascicles: five vertices, two triangles - two needles leave one base and open 16-34 deg (a V in 3D); LOD0 '
                 '0.52-0.70 m x 0.10-0.13 m, 9-12 per brush; a brush sweeps forward along its shoot (a pine shoot brush, a little '
                 'flattened), brushes follow each tip twig from 30 % of its length to the tip; LOD1 0.75-0.95 m x 0.16-0.21 m, 6-8 per brush; '
                 'LOD2 1.2-1.5 m x 0.34-0.44 m, 4-5 per brush; LOD3: two crossed impostor cards')

VARIANTS = {
    # trunk: control points (x, y, z as a fraction of H, radius as a fraction of r0)
    # sil: the silhouette limbs (t along the trunk, azimuth deg [0 = +X right, 90 = +Y back, 270 = -Y front], length m, end rise / L)
    # fill: how many more limbs, from t0 to t1, their length at the bottom and at the top
    'A': dict(H=15.0, seed=131, r0=.6, twist=.02,
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .96), (.2, .04, .12, .8), (.7, .08, .26, .7), (.85, .06, .4, .6), (.45, .02, .55, .5),
                     (-.1, -.04, .7, .38), (-.3, 0, .85, .24), (-.15, .04, .985, .08)],
              sil=[(.4, 183, 8.4, .02), (.47, 8, 6.8, .08), (.53, 98, 5.8, .12)],
              fill=dict(n=16, t0=.43, t1=.97, L0=6.8, L1=3.4), stubs=[(.16, 40), (.27, 250)], leaves=1.),
    'B': dict(H=14.5, seed=227, r0=.45, twist=-.025,
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .95), (.16, -.03, .12, .78), (.48, -.06, .28, .66), (.6, -.04, .44, .55), (.5, .02, .6, .44),
                     (.3, .05, .75, .32), (.2, .06, .88, .2), (.24, .06, .985, .07)],
              sil=[(.45, 30, 6.4, .04), (.5, 200, 4.2, .1), (.6, 120, 4.0, .14)],
              fill=dict(n=16, t0=.46, t1=.96, L0=4.6, L1=2.2), stubs=[(.14, 300), (.25, 110)], leaves=1., sec=.5),
    'C': dict(H=13.5, seed=313, r0=.32, twist=.04,
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .94), (.3, -.04, .12, .72), (1.0, -.14, .28, .6), (1.7, -.26, .44, .5), (2.2, -.34, .6, .4),
                     (2.5, -.38, .76, .3), (2.66, -.4, .89, .18), (2.72, -.4, .985, .06)],
              sil=[(.52, 345, 6.2, .02), (.66, 170, 3.0, .16), (.78, 75, 2.8, .2)],
              fill=dict(n=12, t0=.5, t1=.95, L0=3.0, L1=1.4), stubs=[(.13, 130), (.21, 250), (.3, 170)], leaves=.8, sec=.34),
}
NAMES = {'A': 'Pine', 'B': 'Pine', 'C': 'CliffPine'}
ZH = {'A': '松（寬冠分層、左側低長枝定剪影）', 'B': '松（幹微右傾、冠較高較窄、長枝往右後）', 'C': '崖松（細幹大斜、一條長枝外伸、冠疏、斷樁三處）'}
UP = Vector((0, 0, 1))


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
    def axis(z):
        return Vector((float(np.interp(z, zz, xs)), float(np.interp(z, zz, ys)), z))
    return P, R, zt, axis


def _section(seed, twist):
    """Mid / low frequency only: root flare with five lobes, long bark ridges turning slowly with height, two broad burls."""
    def fn(th, s, p):
        z = p.z + .3
        root = .75 * math.exp(-z / .7) * max(0., math.cos(5 * th + seed)) ** 2
        flare = .5 * math.exp(-z / .85)
        tw = th - 2 * math.pi * twist * z
        def ridge(x): return abs(math.cos(x / 2)) ** .6 - .62
        rib = (.12 * ridge(7 * tw + seed + .5 * math.sin(1.1 * z)) + .05 * ridge(13 * tw + 2.1 * seed + .9 * z)) * (.75 + .25 * math.exp(-z / 4))
        burl = .14 * math.exp(-((z - 2.8) / .45) ** 2) * max(0., math.cos(th - seed)) ** 6 + .1 * math.exp(-((z - 5.4) / .35) ** 2) * max(0., math.cos(th - seed - 2.4)) ** 6
        return 1 + root + flare + rib + burl
    return fn


def _curve(cp, per=4):
    pts = catmull(cp, per); return pts


def _limb_list(cfg, rng):
    """The silhouette limbs first, then the fill limbs: heights spread over the crown, azimuths by the golden angle with jitter
    (never mirrored), lengths shorter toward the top, longer where the crown is thin."""
    limbs = [dict(t=t, az=az, L=L, rise=rise, sil=True) for t, az, L, rise in cfg['sil']]
    f = cfg['fill']; az0 = rng.uniform(0, 360)
    for k in range(f['n']):
        u = (k + rng.uniform(.2, .8)) / f['n']; t = f['t0'] + (f['t1'] - f['t0']) * u
        az = (az0 + k * 137.5 + rng.normal(0, 14)) % 360
        L = (f['L0'] + (f['L1'] - f['L0']) * u ** .85) * rng.uniform(.82, 1.12)
        rise = .06 + .34 * u ** 1.5 + rng.normal(0, .03)
        limbs.append(dict(t=t, az=az, L=L, rise=rise, sil=False))
    return limbs


def skeleton(var):
    """Branches (tr_tree.Branch: level 0 trunk, 1 limb, 2 secondary, 3 tip twig = spray), crown anchors, helpers."""
    cfg = VARIANTS[var]; rng = np.random.default_rng(cfg['seed']); H = cfg['H']
    P, R, zt, axis = _trunk(cfg)
    ts = np.linspace(0, 1., 34)
    trunk = Branch([P(t) for t in ts], [max(.03, R(t)) for t in ts], 0, 0., 0., 0., 'trunk', _section(cfg['seed'] * .37 % 6.28, cfg['twist']))
    trunk.twist = cfg['twist']
    branches = [trunk]; sprays = []; groups = []
    for li, lb in enumerate(_limb_list(cfg, rng)):
        t, L, rise = lb['t'], lb['L'], lb['rise']
        az = math.radians(lb['az']); start = P(t); out = Vector((math.cos(az), math.sin(az), 0)); side0 = Vector((-out.y, out.x, 0))
        phase = float(rng.random()); u = (t - .35) / .65
        # leaves the trunk climbing, runs out nearly level, the outer part sags a little and the tip turns up
        up0 = .32 + .25 * u
        cp = [start, start + out * .22 * L + UP * (up0 * .22 * L), start + out * .55 * L + UP * ((up0 * .3 + rise * .4) * L),
              start + out * .82 * L + UP * ((rise * .75 - .03) * L), start + out * L + UP * (rise * L + .1 * L)]
        cp = [c + (side0 * rng.normal(0, .07 * L) + UP * rng.normal(0, .025 * L)) * float(k > 1) for k, c in enumerate(cp)]
        pts = _curve(cp)
        r0 = max(.06, R(t) * (.62 if lb['sil'] else .5) * (.75 + .25 * min(1., L / 5.)))
        rads = [r0 * (1 - .8 * (k / (len(pts) - 1)) ** 1.1) + .012 for k in range(len(pts))]
        limb = Branch(pts, rads, 1, .03, .3, phase, 'limb'); branches.append(limb)
        grp = []
        # secondary branches, alternating sides, nearly level, a few climbing; shorter toward the limb's tip
        nsec = max(2, int(round(L / cfg.get('sec', .62))))
        sg = 1 if rng.random() < .5 else -1
        for k in range(nsec):
            s = .2 + .78 * (k + rng.uniform(.3, .7)) / nsec; q, _ = at(pts, s); sg = -sg
            td = tangent(pts, s); side = td.cross(UP); side = side.normalized() if side.length > 1e-3 else side0
            ang = rng.uniform(.75, 1.15); d = td * math.cos(ang) + side * sg * math.sin(ang) + UP * rng.uniform(.05, .22)
            Ls = max(.8, L * rng.uniform(.3, .42) * (1.2 - .5 * s))
            rq = float(np.interp(s, np.linspace(0, 1, len(rads)), rads))
            d = d.normalized(); mid = q + d * Ls * .5 + UP * (.04 * Ls); end = q + d * Ls + UP * (.16 * Ls) + side * sg * rng.normal(0, .1 * Ls)
            sp = _curve([q, mid, end], 4); sr = [rq * .62 * (1 - .75 * (i / (len(sp) - 1))) + .006 for i in range(len(sp))]
            branches.append(Branch(sp, sr, 2, .3, .5, phase, 'twig'))
            # tip twigs (the sprays) along the outer part of the secondary
            ntw = int(rng.integers(3, 5))
            for kk in range(ntw):
                s2 = .3 + .7 * (kk + rng.uniform(.2, .8)) / ntw; q2, _ = at(sp, s2); td2 = tangent(sp, s2)
                sd = td2.cross(UP); sd = sd.normalized() if sd.length > 1e-3 else side
                sgn = 1 if (kk + li) % 2 else -1
                d2 = (td2 * .8 + sd * sgn * rng.uniform(.4, .8) + UP * rng.uniform(.0, .12)).normalized()
                Lt = rng.uniform(.45, .75) * (1.15 - .3 * s2)
                tw = _curve([q2, q2 + d2 * Lt * .5 + UP * .02, q2 + d2 * Lt + UP * (.18 * Lt)], 3)
                rt = max(.008, float(np.interp(s2, np.linspace(0, 1, len(sr)), sr)) * .7)
                br = Branch(tw, [rt, rt * .7, .006], 3, .5, .75, phase, 'twig'); branches.append(br); grp.append(br)
        # the limb's own tip carries a fan of sprays
        tip = pts[-1]; tdl = (pts[-1] - pts[-3]).normalized()
        for kk in range(3):
            a = (kk - 1) * .7 + rng.normal(0, .12); ca, sa = math.cos(a), math.sin(a)
            d2 = Vector((tdl.x * ca - tdl.y * sa, tdl.x * sa + tdl.y * ca, tdl.z * .3 + .1)).normalized(); Lt = rng.uniform(.7, 1.0)
            tw = _curve([tip, tip + d2 * Lt * .5, tip + d2 * Lt + UP * (.2 * Lt)], 3)
            br = Branch(tw, [rads[-1] * .9, rads[-1] * .6, .006], 3, .5, .8, phase, 'twig'); branches.append(br); grp.append(br)
        groups.append(dict(sprays=grp, phase=phase, out=out, w=(3. if lb['sil'] else 2.) * L, n=nsec + 1, sil=lb['sil']))
    # the leader: the trunk tip ends among a few short climbing shoots
    top = P(1.); grp = []
    for kk in range(7):
        a = kk * 2.4 + rng.normal(0, .2); d = Vector((math.cos(a) * .8, math.sin(a) * .8, .6)).normalized(); Lt = rng.uniform(.6, 1.0)
        q = P(rng.uniform(.93, 1.)); tw = _curve([q, q + d * Lt * .5, q + d * Lt + UP * .15 * Lt], 3)
        br = Branch(tw, [.025, .015, .006], 3, .5, .8, .5, 'twig'); branches.append(br); grp.append(br)
    groups.append(dict(sprays=grp, phase=.5, out=Vector((1, 0, 0)), w=5., n=7, sil=True))
    for (t, az_) in cfg['stubs']:
        a = math.radians(az_); s = P(t); dd = Vector((math.cos(a), math.sin(a), .15)).normalized(); L = R(t) + rng.uniform(.18, .32)
        branches.append(Branch([s, s + dd * L * .55, s + dd * L + Vector((0, 0, .04))], [R(t) * .3, R(t) * .24, R(t) * .18], 2, 0., 0., 0., 'stub', cap=True))
    # crown anchors: one per limb, its sprays = the limb's secondaries (each with its tip twigs) and its tip fan; a limb with fewer
    # than 7 sprays joins its nearest neighbour (by the centre of its twig ends), so every anchor carries 7-13 sprays
    for g in groups:
        g['c'] = sum((b.pts[-1] for b in g['sprays']), Vector()) / len(g['sprays'])
    while True:
        small = [g for g in groups if g['n'] < 7 and not g.get('done')]
        if not small: break
        g = min(small, key=lambda x: x['n'])
        others = [h for h in groups if h is not g and h['n'] + g['n'] <= 13]
        if not others: g['done'] = True; continue
        h = min(others, key=lambda x: (x['c'] - g['c']).length)
        h['sprays'] = h['sprays'] + g['sprays']; h['n'] += g['n']; h['c'] = sum((b.pts[-1] for b in h['sprays']), Vector()) / len(h['sprays'])
        h['w'] = max(h['w'], g['w']); groups.remove(g)
    anchors = []
    for g in groups:
        for ch in [g['sprays']]:
            ends = [b.pts[-1] for b in ch]; c = sum(ends, Vector()) / len(ends)
            r = max(.8, max((e - c).length for e in ends))
            rel = c - axis(c.z); layer = 'front' if rel.y < 0 else 'back'
            an = Anchor(c, r, g['out'], layer, twist=0., phase=g['phase'], idx=len(anchors), sprays=g['n']); an.branches = ch
            for b in ch: b.anchor = an
            anchors.append(an)
    return dict(branches=branches, anchors=anchors, H=H, P=P, R=R, axis=axis, zt=zt, rng_seed=cfg['seed'], main_limbs=len(cfg['sil']) + cfg['fill']['n'])


def wood(buf, sk, lod):
    """Tubes: trunk, limbs, secondaries, tip twigs and stubs at the sides / ring step of WOOD[lod]. Each child starts on its
    parent's axis (inside it), so the joint grows out of the parent. Returns triangles."""
    n0 = buf.tris(); spec = WOOD[lod]
    for br in sk['branches']:
        lv = 9 if br.kind == 'stub' else br.level
        s = spec.get(lv)
        if s is None: continue
        sides, step = s
        if br.kind != 'trunk' and br.level < 3:      # a little flare where a limb or secondary leaves its parent
            br = Branch(br.pts, [br.rads[0] * 1.25] + list(br.rads[1:]), br.level, br.w0, br.w1, br.phase, br.kind, br.section, br.cap)
        buf.tube(br, sides, step, seed=br.phase * 7, nmin=2 if br.level == 3 else 3)
    return buf.tris() - n0


def foliage(buf, sk, lod, var, rng):
    """Rosettes of needle bundles along every spray (tip twig), from t 0.25 to the tip, spaced so the bundles fill the LOD budget.
    Returns (bundles, 0)."""
    cfg = VARIANTS[var]; anchors = sk['anchors']; axis = sk['axis']; nd = NEEDLE[lod]
    sprays = [b for b in sk['branches'] if b.kind == 'twig' and b.level == 3]
    dense = {id(b): _curve(b.pts, 6) for b in sprays}
    env = envelope_fn([p for b in sprays for p in dense[id(b)][2:]], axis)
    zc0 = min(a.c.z for a in anchors) - .8; ztop = max(a.c.z for a in anchors) + .6
    cap = int(min(LOD_CAP[lod] * .985 - buf.tris(), 1e9) / 2 * cfg['leaves'])      # a fascicle (needle pair) is 2 triangles
    per = sum(nd['per']) / 2 * (1 + nd['body'])     # in fascicles (2 triangles each)
    total = sum(sum((d[i + 1] - d[i]).length for i in range(len(d) - 1)) for d in dense.values())
    rosettes = cap / per; gap = total * .78 / max(rosettes, 1)
    bundles = 0
    for b in sprays:
        pts = dense[id(b)]; L = sum((pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)); an = b.anchor
        n = int(L * .78 / gap + rng.random())      # may be 0 on a short spray at LOD1-2: the budget spreads over the whole crown
        for j in range(n):
            if bundles >= cap: break
            t = .3 + .7 * ((j + rng.uniform(.25, .75)) / n) ** .75
            q, _ = at(pts, t); td = tangent(pts, t)
            a = axis(q.z); radial = Vector((q.x - a.x, q.y - a.y, 0)); hr = radial.length; outv = radial.normalized() if hr > 1e-3 else an.out
            hn = min(1., max(0., (q.z - zc0) / max(ztop - zc0, .1))); rim = min(1., hr / max(env(q.z), .5))
            local = max(-1., min(1., (q.z - an.c.z) / max(an.r * .35, .2)))
            expo = .26 * hn + .3 * rim + .24 * (.5 + .5 * local) + .2 * t + rng.normal(0, .04)
            expo = min(1., max(0., expo * 1.1 - .06))
            axis_r = (td * .85 + UP * .4 + outv * .2).normalized()          # the brush sweeps forward along the shoot          # the brush opens up and forward along the shoot
            e1 = axis_r.orthogonal().normalized(); e2 = axis_r.cross(e1).normalized()
            k = int(rng.integers(nd['per'][0], nd['per'][1] + 1)); a0 = rng.uniform(0, 2 * math.pi)
            tipb = 1.12 if t > .92 else 1.
            for m in range(k):
                if bundles >= cap: break
                ph = a0 + m * 2 * math.pi / k + rng.normal(0, .25); cone = rng.uniform(.5, 1.35)
                d = (axis_r * math.cos(cone) + (e1 * math.cos(ph) + e2 * math.sin(ph)) * math.sin(cone)); d.z *= .8; d = d.normalized()   # a pine shoot's brush is a little flattened: the crown reads as layered pads
                ln = rng.uniform(*nd['L']) * tipb; wd = rng.uniform(*nd['W'])
                sd = d.cross(UP); sd = sd.normalized() if sd.length > 1e-3 else e1
                nr = sd.cross(d).normalized()
                if nr.z < 0: nr = -nr
                c = q + d * ln * .45
                tone = min(1., max(0., expo * .75 + .45 * (d.z - .3) + .1 + rng.normal(0, .03)))    # each brush lit on top, dark below: pads read as cushions
                occl = min(1., max(.15, .4 + .6 * expo + .15 * (d.z - .5)))
                col = palette_colour(PALETTE, tone, occl, OCCL_LO)
                bias_dir = ((q - an.c) * (.6 / max(an.r, .3)) + outv * .45 + UP * .8).normalized()
                # a fascicle: two needles from one base, opening a little (a V in 3D); every LOD, larger and fewer further out
                sp_ = rng.uniform(.14, .3); tw_ = nr * rng.normal(0, .12)
                d1 = (d * math.cos(sp_) + sd * math.sin(sp_) + tw_).normalized(); d2 = (d * math.cos(sp_) - sd * math.sin(sp_) - tw_).normalized()
                buf.needle_pair(q + d * .02, d1, d2, ln, wd, col, occl, tone, .62 + .38 * t, an.phase + rng.uniform(0, .06), bias_dir)
                bundles += 1
            # the pad's body: a few broad, nearly level bundles under the brush, darker; seen from below / the side they close the pad
            kb = int(k * nd['body'] + rng.random())
            hd = Vector((td.x, td.y, 0)); hd = hd.normalized() if hd.length > 1e-3 else outv
            for m in range(kb):
                if bundles >= cap: break
                a2 = rng.uniform(-1.3, 1.3); ca, sa = math.cos(a2), math.sin(a2)
                d = Vector((hd.x * ca - hd.y * sa, hd.x * sa + hd.y * ca, rng.uniform(.04, .2))).normalized()
                ln = rng.uniform(*nd['BL']); wd = rng.uniform(*nd['BW'])
                sd = d.cross(UP).normalized(); nr = sd.cross(d).normalized()
                if nr.z < 0: nr = -nr
                c = q + d * ln * .38 - UP * rng.uniform(.02, .08)
                tone = min(1., max(0., expo * .6 + rng.normal(0, .035)))
                occl = min(1., max(.15, .3 + .5 * expo))
                col = palette_colour(PALETTE, tone, occl, OCCL_LO)
                buf.leaf(c, (d, sd, nr), ln, wd, wd * .18, col, occl, tone, .62 + .38 * t, an.phase + rng.uniform(0, .06),
                         nrm_bias=(outv * .3 + UP).normalized(), bias=.5, widest=.3)
                bundles += 1
    return bundles, 0
