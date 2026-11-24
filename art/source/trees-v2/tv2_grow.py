"""trees-v2 shared grower (2026-11-15), for TR02 cypress, TR03 camphor, TR05 ginkgo. TR01 keeps its own tv2_pine.py (same steps).

The sky-island world-tree order (docs/execution/2026-11-14/tree-method):
  trunk (S curve, 9 control points; ridges, twist, burls in the geometry) -> 3 silhouette limbs, then the rest (golden angle with
  jitter, never mirrored) -> secondaries (alternating sides) -> tip twigs (the sprays) -> crown anchors (one per limb, 7-13 sprays;
  small limbs join their nearest neighbour) -> leaves along each spray's parameter t -> vertex colour (height, rim, inside;
  occlusion in A) -> bark last.
Wood: one tube per branch, each child starting on its parent's axis (no Skin modifier, no seams). Dead branches are bare.
A species module holds only its data (SPEC, VARIANTS, PALETTE ...) and calls make(globals()) to get skeleton / wood / foliage.

Leaf kinds (all of them the method's five-vertex solid leaf: 4 outline points + a raised midrib, 4 triangles):
  'frond'  cypress: flat scale-leaf fronds - leaves set pinnately along the spray in its own (nearly level) plane, tips drooping
  'cluster' camphor: ovate leaves, 5-8 in a loose whorl round a point of the spray (camphor leaves crowd near the shoot tips)
  'fan'    ginkgo: fan leaves (widest near the tip), 3-6 on a short spur shoot along the spray
"""
import math
import numpy as np
from mathutils import Vector
from tr_tree import Branch, catmull
from tv2_core import at, tangent, Anchor, envelope_fn, palette_colour

UP = Vector((0, 0, 1))
LOD_CAP = {0: 60000, 1: 15000, 2: 4000}
COLLAR_A = .8          # largest collar swell (x the branch radius)
UNION_R0 = .35         # limbs thicker than this x the trunk radius start to grow as a union (fully at +0.3)
UNION_DEPTH = 1.6      # union limbs start this many trunk radii below the split, on the trunk axis
UNION_SWELL = .45      # trunk swelling toward a union limb, x the limb / trunk radius ratio
COLLAR_MIN_R = .08     # secondaries thinner than this keep the plain 1.25 x base


def _trunk(cfg):
    H = cfg['H']; r0 = cfg['r0']; zt = H * cfg['trunk'][-1][2]
    ctrl = [Vector((x, y, -.3 if z < 0 else z * H)) for x, y, z, r in cfg['trunk']]
    dense = catmull(ctrl, 20); zz = np.array([p.z for p in dense])
    rr = np.interp(np.linspace(0, 1, len(dense)), np.linspace(0, 1, len(ctrl)), [r * r0 for x, y, z, r in cfg['trunk']])
    xs = np.array([p.x for p in dense]); ys = np.array([p.y for p in dense])
    def P(t):
        z = -.3 + (zt + .3) * min(1., max(0., t)); return Vector((float(np.interp(z, zz, xs)), float(np.interp(z, zz, ys)), z))
    def R(t):
        z = -.3 + (zt + .3) * min(1., max(0., t)); return float(np.interp(z, zz, rr))
    def axis(z):
        return Vector((float(np.interp(z, zz, xs)), float(np.interp(z, zz, ys)), z))
    return P, R, zt, axis


def _section(seed, twist, sec):
    """Mid / low frequency only: root lobes, long ridges turning with height (twist turns per metre), broad burls."""
    lobes = sec.get('lobes', 5); rib_a = sec.get('rib', .12); burls = sec.get('burls', [(2.8, .14, 0.), (5.4, .1, 2.4)])
    def fn(th, s, p):
        z = p.z + .3
        root = sec.get('root', .75) * math.exp(-z / .7) * max(0., math.cos(lobes * th + seed)) ** 2
        flare = sec.get('flare', .5) * math.exp(-z / .85)
        tw = th - 2 * math.pi * twist * z
        def ridge(x): return abs(math.cos(x / 2)) ** .6 - .62
        rib = (rib_a * ridge(7 * tw + seed + .5 * math.sin(1.1 * z)) + rib_a * .42 * ridge(13 * tw + 2.1 * seed + .9 * z)) * (.75 + .25 * math.exp(-z / 4))
        st = sec.get('strands')     # (n, depth, top m): a few broad rope strands with deep grooves, turning with the twist
        if st:
            rib += st[1] * (abs(math.cos(st[0] * tw / 2 + seed)) ** .7 - .7) * min(1., max(0., (st[2] - z) / 1.5))
        burl = sum(a * math.exp(-((z - zb) / .45) ** 2) * max(0., math.cos(th - seed - ph)) ** 6 for zb, a, ph in burls)
        return 1 + root + flare + rib + burl
    return fn


def _crown_env(cw, rng):
    """Crown volume for 'crown' mode: a lobed dome. cw: z0, z1 (m), prof [(f, r/rmax)], rx, ry (m, plan ellipse), cx, cy, lobes.
    Returns (inside(p), depth(p), centre)."""
    from mathutils import noise
    z0, z1 = cw['z0'], cw['z1']; pf = np.array(cw['prof']); rx, ry = cw['rx'], cw['ry']; cx, cy = cw.get('cx', 0.), cw.get('cy', 0.)
    lob = cw.get('lobes', .1); r_ = np.random.default_rng(cw.get('nseed', 7)); off = Vector((float(r_.uniform(0, 50)), float(r_.uniform(0, 50)), 0.))
    C = Vector((cx, cy, z0 + cw.get('zc', .38) * (z1 - z0)))
    def R(az, z):
        f = (z - z0) / (z1 - z0)
        if f < 0 or f > 1: return 0.
        e = 1 / math.sqrt((math.cos(az) / rx) ** 2 + (math.sin(az) / ry) ** 2)
        n = noise.noise(Vector((math.cos(az) * 2.4, math.sin(az) * 2.4, z * .45)) + off)
        return float(np.interp(f, pf[:, 0], pf[:, 1])) * e * (1 + lob * n)
    ub = cw.get('bowl', 0.)     # the underside is a bowl: open in the middle (the limbs show), hanging low at the rim
    def inside(p):
        dx, dy = p.x - cx, p.y - cy; az = math.atan2(dy, dx); h = math.hypot(dx, dy)
        if ub:
            e = 1 / math.sqrt((math.cos(az) / rx) ** 2 + (math.sin(az) / ry) ** 2)
            if p.z < z0 + ub * max(0., 1 - (h / e) ** 2): return False
        return h < R(az, p.z)
    def depth(p):
        d = p - C
        if not inside(p): return -1.
        lo, hi = 1., 3.
        while inside(C + d * hi) and hi < 40: hi *= 2
        for _ in range(18):
            m = (lo + hi) / 2
            if inside(C + d * m): lo = m
            else: hi = m
        return d.length * (lo - 1)
    return inside, depth, C


def _colonize(cw, seeds, rng):
    """Space colonisation: attraction points fill the outer shell of the crown; shoots grow from the seed nodes (points along
    the limbs and the upper trunk) toward them. Returns nodes [(pos, parent, group)] and the envelope test."""
    from mathutils.kdtree import KDTree
    inside, depth, C = _crown_env(cw, rng)
    z0, z1 = cw['z0'], cw['z1']; rm = max(cw['rx'], cw['ry']) * 1.15
    att = []; shell = cw.get('shell', 1.1); n_att = cw.get('n_att', 2600); tries = 0
    def rnd(): return Vector((C.x + rng.uniform(-rm, rm), C.y + rng.uniform(-rm, rm), rng.uniform(z0, z1)))
    cl = cw.get('clumps')        # (count, sigma m, floor): foliage gathers into lobes on the shell (cumulus masses, dark gaps between)
    cc = []
    if cl:
        for _ in range(4000):
            if len(cc) >= cl[0]: break
            p = rnd(); dp = depth(p)
            if 0 <= dp < .8 and all((p - q).length > cl[1] * 1.6 for q in cc): cc.append(p)
    while len(att) < n_att and tries < n_att * 80:
        tries += 1
        p = rnd(); dp = depth(p)
        if dp < 0: continue
        pr = math.exp(-dp / shell) + cw.get('core', .04)
        if cc: pr *= cl[2] + (1 - cl[2]) * max(math.exp(-(p - q).length_squared / (2 * cl[1] ** 2)) for q in cc)
        if rng.random() < pr: att.append(p)
    D = cw.get('step', .42); di = cw.get('di', 2.4); dk = cw.get('dk', .75); trop = cw.get('trop', .18)
    nodes = [(Vector(p), -1, g) for p, g in seeds]
    alive = list(range(len(att)))
    for it in range(cw.get('iters', 90)):
        kd = KDTree(len(nodes))
        for i, (p, _, _) in enumerate(nodes): kd.insert(p, i)
        kd.balance()
        acc = {}
        for a in alive:
            q = att[a]; co, idx, dist = kd.find(q)
            if dist < di:
                v = (q - co); v.normalize(); acc.setdefault(idx, Vector()); acc[idx] += v
        if not acc: break
        new = []
        for idx, v in acc.items():
            p, par_, g = nodes[idx]
            mom = (p - nodes[par_][0]).normalized() * cw.get('momentum', .9) if par_ >= 0 else Vector()     # shoots keep their heading: no zigzag
            d = (v.normalized() + mom + UP * trop + Vector((rng.normal(0, .12), rng.normal(0, .12), rng.normal(0, .06))))
            if d.length < 1e-6: continue
            q = p + d.normalized() * D
            new.append((q, idx, g))
        if not new: break
        nodes += new
        kd2 = KDTree(len(new))
        for i, (p, _, _) in enumerate(new): kd2.insert(p, i)
        kd2.balance()
        alive = [a for a in alive if not kd2.find_range(att[a], dk)]
        if len(nodes) > cw.get('max_nodes', 7000): break
    cw['_cc'] = [Vector(q) for q in cc]       # leaf-mass centres, for the per-mass light in foliage
    return nodes, inside


def _crown_wood(cw, seeds, groups, branches, rng):
    """Turn the colonised nodes into branches: pipe-model radii, chains following the heaviest child, smoothed; the thin
    ends of every chain become the level-3 tip twigs that carry the leaves."""
    nodes, inside = _colonize(cw, seeds, rng)
    ns = len(seeds); n = len(nodes); kids = [[] for _ in range(n)]
    for i in range(ns, n): kids[nodes[i][1]].append(i)
    rt = cw.get('r_tip', .011); rad = [0.] * n; w = [0] * n
    for i in range(n - 1, ns - 1, -1):
        rad[i] = math.sqrt(rt * rt + sum(rad[c] ** 2 for c in kids[i])) if kids[i] else rt
        w[i] = 1 + sum(w[c] for c in kids[i])
    r_tw = cw.get('r_twig', .03); rmax = cw.get('r_max', .16)
    starts = [(c, i) for i in range(ns) for c in kids[i]]
    while starts:
        c, par = starts.pop()
        chain = [par, c]; cur = c
        while kids[cur]:
            ks = sorted(kids[cur], key=lambda k: -w[k])
            for k in ks[1:]: starts.append((k, cur))
            cur = ks[0]; chain.append(cur)
        P = [Vector(nodes[k][0]) for k in chain]
        for _ in range(6):      # smooth what is left of the growth steps, ends fixed
            P = [P[0]] + [(P[k - 1] + P[k] * 2 + P[k + 1]) / 4 for k in range(1, len(P) - 1)] + [P[-1]]
        rr = [min(rmax, rad[chain[1]] if k == 0 else rad[chain[k]]) for k in range(len(chain))]
        g = groups[nodes[c][2]]; ph = g['phase']
        cut = next((k for k in range(len(rr)) if rr[k] < r_tw), len(rr))
        if cut >= 2:
            b = Branch(catmull(P[:cut + 1], 3), [], 2, .3, .5, ph, 'twig')
            b.rads = [float(x) + .004 for x in np.interp(np.linspace(0, 1, len(b.pts)), np.linspace(0, 1, cut + 1), rr[:cut + 1])]
            b.parent_r = rr[0] * 1.3; branches.append(b)
        k0 = max(0, cut - 1) if cut >= 2 else 0
        if len(P) - k0 >= 2:
            tp = P[k0:]
            if len(tp) == 2: tp = [tp[0], (tp[0] + tp[1]) / 2, tp[1]]
            r0_ = max(.008, rr[min(k0, len(rr) - 1)])
            trs = [r0_ + (.006 - r0_) * k / (len(tp) - 1) for k in range(len(tp))]
            b = Branch(tp, trs, 3, .5, .75, ph, 'twig')
            branches.append(b); g['sprays'].append(b)
    # crown anchors: k-means of the tip twigs into cw['anchors'] lobes (one wind phase each), not one per limb
    tw = [b for g in groups for b in g['sprays']]
    X = np.array([[b.pts[-1].x, b.pts[-1].y, b.pts[-1].z] for b in tw]); k = min(cw.get('anchors', 16), len(tw))
    Cn = X[rng.choice(len(X), k, replace=False)]
    for _ in range(25):
        lab = np.argmin(((X[:, None, :] - Cn[None]) ** 2).sum(-1), 1)
        Cn = np.array([X[lab == j].mean(0) if (lab == j).any() else Cn[j] for j in range(k)])
    groups.clear()
    for j in range(k):
        sp_ = [tw[i] for i in np.nonzero(lab == j)[0]]
        if not sp_: continue
        o = Vector((Cn[j][0], Cn[j][1], 0)); o = o.normalized() if o.length > 1e-3 else Vector((1, 0, 0))
        ph = float(rng.random())
        for b in sp_: b.phase = ph
        groups.append(dict(sprays=sp_, phase=ph, out=o, n=13, sil=True))


def make(G):
    """Bind skeleton / wood / foliage for the species module whose globals() is G."""
    SPEC = G['SPEC']; VARIANTS = G['VARIANTS']; PALETTE = G['PALETTE']; OCCL_LO = G['OCCL_LO']; WOOD = G['WOOD']; LEAF = G['LEAF']

    def limb_list(cfg, rng):
        limbs = [dict(t=t, az=az, L=L, rise=rise, sil=True) for t, az, L, rise in cfg['sil']]
        f = cfg['fill']; az0 = rng.uniform(0, 360)
        for k in range(f['n']):
            u = (k + rng.uniform(.2, .8)) / f['n']; t = f['t0'] + (f['t1'] - f['t0']) * u
            az = (az0 + k * 137.5 + rng.normal(0, 14)) % 360
            L = (float(np.interp(u, (0., f.get('Lu', .4), 1.), (f['L0'], f['Lm'], f['L1']))) if 'Lm' in f else f['L0'] + (f['L1'] - f['L0']) * u ** .85) * rng.uniform(.82, 1.12)
            rise = f.get('rise0', .06) + f.get('rise1', .34) * u ** 1.5 + rng.normal(0, .03)
            limbs.append(dict(t=t, az=az, L=L, rise=rise, sil=False))
        return limbs

    def skeleton(var):
        cfg = VARIANTS[var]; rng = np.random.default_rng(cfg['seed']); H = cfg['H']; sp = SPEC
        P, R, zt, axis = _trunk(cfg)
        ts = np.linspace(0, 1., 40)
        trunk = Branch([P(t) for t in ts], [max(.03, R(t)) for t in ts], 0, 0., 0., 0., 'trunk',
                       _section(cfg['seed'] * .37 % 6.28, cfg['twist'], cfg.get('section', {})))
        trunk.twist = cfg['twist']; trunk.bulges = []
        branches = [trunk]; groups = []; leads = []
        fork = sp.get('fork', 0.); taper = sp.get('taper'); crown = cfg.get('crown'); seeds = []
        for li, lb in enumerate(limb_list(cfg, rng)):
            t, L, rise = lb['t'], lb['L'], lb['rise']
            az = math.radians(lb['az']); start = P(t); out = Vector((math.cos(az), math.sin(az), 0)); side0 = Vector((-out.y, out.x, 0))
            parent_r = R(t); host = None
            if fork and not lb['sil'] and leads and rng.random() < fork:
                # decurrent crowns (camphor): this limb grows out of one of the big silhouette leads, not out of the trunk,
                # so the crown branches in steps (trunk -> leads -> limbs) instead of every limb fanning from one point
                hp, hr, hout = leads[int(rng.integers(len(leads)))]
                sh = float(rng.uniform(*sp.get('fork_s', (.25, .6)))); start, _ = at(hp, sh); td = tangent(hp, sh)
                parent_r = float(np.interp(sh, np.linspace(0, 1, len(hr)), hr))
                hz = Vector((td.x, td.y, 0)); hz = hz.normalized() if hz.length > 1e-3 else hout
                a = rng.uniform(.5, 1.0) * (1 if rng.random() < .5 else -1); ca, sa = math.cos(a), math.sin(a)
                out = Vector((hz.x * ca - hz.y * sa, hz.x * sa + hz.y * ca, 0)); side0 = Vector((-out.y, out.x, 0))
                L *= sp.get('fork_len', .75); host = parent_r
            phase = float(rng.random()); u = (t - sp['t_lo']) / (1 - sp['t_lo'])
            up0 = sp['up0'][0] + sp['up0'][1] * u
            r0 = max(.05, R(t) * (sp['limb_r'][0] if lb['sil'] else sp['limb_r'][1]) * (.75 + .25 * min(1., L / 5.)))
            if host: r0 = min(r0, host * sp.get('fork_r', .7))
            cp = [start, start + out * .22 * L + UP * (up0 * .22 * L), start + out * .55 * L + UP * ((up0 * .45 + rise * .4) * L),
                  start + out * .82 * L + UP * ((rise * .75 + up0 * .2 - sp['sag']) * L), start + out * L + UP * (rise * L + (.1 + up0 * .2 - sp['sag']) * L)]
            cp = [c + (side0 * rng.normal(0, sp['wiggle'] * L) + UP * rng.normal(0, sp.get('wiggle_up', .025) * L)) * float(k > 1) for k, c in enumerate(cp)]
            # a thick limb (codominant union) does not leave the trunk surface at an angle: it starts lower inside the trunk,
            # runs up along the trunk axis and peels away, while the trunk swells toward it just below the split
            ratio = r0 / max(parent_r, 1e-3); union = 0. if host else min(1., max(0., (ratio - UNION_R0) / .3))
            if union > 0:
                Rt = parent_r; zs = start.z
                cp = [axis(zs - UNION_DEPTH * Rt * union), start + out * (.35 * Rt) + UP * (.45 * Rt * union)] + cp[1:]
                trunk.bulges.append((zs - .35 * Rt, az, UNION_SWELL * ratio * union, .9 * Rt + .25))
            pts = catmull(cp, 4)
            if crown:       # crown mode: a limb whose tip leaves the crown volume is shortened about its start (never stretched)
                c_in, c_dep, _ = _crown_env(crown, rng)
                def ok_(sc_): return c_dep(start + (pts[-1] - start) * sc_) > crown.get('limb_depth', .5)
                if not ok_(1.):
                    fit_ = next((f_ for f_ in np.arange(.97, .5, -.03) if ok_(f_)), None)     # the longest length that ends inside
                    if fit_ is None:
                        if not lb['sil']:
                            if union > 0: trunk.bulges.pop()
                            continue     # a limb that would end below / outside the crown is left out
                        fit_ = 1.        # silhouette limbs stay (they carry the crotch)
                    pts = [start + (q_ - start) * fit_ for q_ in pts]; L *= fit_
            fu = 0.     # the share of the limb that runs inside / along the trunk: side branches keep to the free part
            if union > 0:
                fu = min(.35, UNION_DEPTH * parent_r * union * 1.1 / sum((pts[i] - pts[i - 1]).length for i in range(1, len(pts))))
            if taper:      # fast loss of girth near the base (each secondary takes its share), then a slow thin run to the tip
                a_, b_ = taper; rads = [r0 * (b_ + (1 - b_) * (1 - k / (len(pts) - 1)) ** a_) + .012 for k in range(len(pts))]
            else:
                rads = [r0 * (1 - .8 * (k / (len(pts) - 1)) ** 1.1) + .012 for k in range(len(pts))]
            limb = Branch(pts, rads, 1, .03, .3, phase, 'limb'); limb.parent_r = parent_r; limb.union = union; branches.append(limb)
            if lb['sil']: leads.append((pts, rads, out))
            grp = []
            if crown:
                for k_ in range(len(pts)):
                    s_ = k_ / (len(pts) - 1)
                    if s_ > max(fu + .15, crown.get('seed_s', .5)) and (k_ % 2 == 0 or k_ == len(pts) - 1) and pts[k_].z > crown['z0'] - .3:
                        seeds.append((pts[k_], len(groups)))
                groups.append(dict(sprays=grp, phase=phase, out=out, n=7, sil=lb['sil']))
                continue
            nsec = max(2, int(round(L / sp['sec'])))
            sg = 1 if rng.random() < .5 else -1
            for k in range(nsec):
                s = sp['sec_s0'] + (.98 - sp['sec_s0']) * (k + rng.uniform(.3, .7)) / nsec; s = fu + (1 - fu) * s; q, _ = at(pts, s); sg = -sg
                td = tangent(pts, s); side = td.cross(UP); side = side.normalized() if side.length > 1e-3 else side0
                ang = rng.uniform(*sp['sec_ang']); d = td * math.cos(ang) + side * sg * math.sin(ang) + UP * rng.uniform(*sp['sec_up'])
                Ls = max(.6, L * rng.uniform(*sp['sec_len']) * (1.2 - .5 * s))
                rq = float(np.interp(s, np.linspace(0, 1, len(rads)), rads))
                d = d.normalized(); mid = q + d * Ls * .5 + UP * (.04 * Ls); end = q + d * Ls + UP * (sp['sec_tip'] * Ls) + side * sg * rng.normal(0, .1 * Ls)
                spts = catmull([q, mid, end], 4); sr = [rq * .62 * (1 - .75 * (i / (len(spts) - 1))) + .006 for i in range(len(spts))]
                sb = Branch(spts, sr, 2, .3, .5, phase, 'twig'); sb.parent_r = rq; branches.append(sb)
                ntw = int(rng.integers(*sp['ntw']))
                for kk in range(ntw):
                    s2 = .3 + .7 * (kk + rng.uniform(.2, .8)) / ntw; q2, _ = at(spts, s2); td2 = tangent(spts, s2)
                    sd = td2.cross(UP); sd = sd.normalized() if sd.length > 1e-3 else side
                    sgn = 1 if (kk + li) % 2 else -1
                    d2 = (td2 * .8 + sd * sgn * rng.uniform(.4, .8) + UP * rng.uniform(*sp['tw_up'])).normalized()
                    Lt = rng.uniform(*sp['tw_len']) * (1.15 - .3 * s2)
                    tw = catmull([q2, q2 + d2 * Lt * .5 + UP * .02, q2 + d2 * Lt + UP * (sp['tw_tip'] * Lt)], 3)
                    rt = max(.008, float(np.interp(s2, np.linspace(0, 1, len(sr)), sr)) * .7)
                    br = Branch(tw, [rt, rt * .7, .006], 3, .5, .75, phase, 'twig'); branches.append(br); grp.append(br)
            tip = pts[-1]; tdl = (pts[-1] - pts[-3]).normalized()
            for kk in range(3):
                a = (kk - 1) * .7 + rng.normal(0, .12); ca, sa = math.cos(a), math.sin(a)
                d2 = Vector((tdl.x * ca - tdl.y * sa, tdl.x * sa + tdl.y * ca, tdl.z * .3 + .1)).normalized(); Lt = rng.uniform(*sp['tw_len']) * 1.3
                tw = catmull([tip, tip + d2 * Lt * .5, tip + d2 * Lt + UP * (sp['tw_tip'] * Lt)], 3)
                br = Branch(tw, [rads[-1] * .9, rads[-1] * .6, .006], 3, .5, .8, phase, 'twig'); branches.append(br); grp.append(br)
            groups.append(dict(sprays=grp, phase=phase, out=out, n=nsec + 1, sil=lb['sil']))
        if crown:
            for t_ in np.linspace(crown.get('trunk_seed', .55), 1., 10):
                seeds.append((P(float(t_)), len(groups)))
            groups.append(dict(sprays=[], phase=.5, out=Vector((1, 0, 0)), n=7, sil=True))
            _crown_wood(crown, seeds, groups, branches, rng)
            sp = dict(sp, leader=0)
        # the leader
        top = P(1.); grp = []
        for kk in range(sp['leader']):
            a = kk * 2.4 + rng.normal(0, .2); d = Vector((math.cos(a) * .7, math.sin(a) * .7, .7)).normalized(); Lt = rng.uniform(.7, 1.2)
            q = P(rng.uniform(.9, 1.)); tw = catmull([q, q + d * Lt * .5, q + d * Lt + UP * .2 * Lt], 3)
            br = Branch(tw, [.03, .018, .006], 3, .5, .8, .5, 'twig'); branches.append(br); grp.append(br)
        if grp: groups.append(dict(sprays=grp, phase=.5, out=Vector((1, 0, 0)), n=7, sil=True))
        groups = [g for g in groups if g['sprays']]
        for (t, az_) in cfg['stubs']:
            a = math.radians(az_); s = P(t); dd = Vector((math.cos(a), math.sin(a), .15)).normalized(); L = R(t) + rng.uniform(.18, .32)
            branches.append(Branch([s, s + dd * L * .55, s + dd * L + Vector((0, 0, .04))], [R(t) * .3, R(t) * .24, R(t) * .18], 2, 0., 0., 0., 'stub', cap=True))
        # dead branches: bare, a little twisted, two or three short forks, broken ends (cypress snags)
        for (t, az_, L, rise) in cfg.get('dead', []):
            a = math.radians(az_); s = P(t); out = Vector((math.cos(a), math.sin(a), 0))
            cp = [s, s + out * .3 * L + UP * .35 * L, s + out * .6 * L + UP * (rise + .3) * L, s + out * L + UP * (rise + .45) * L]
            pts = catmull(cp, 4); r0 = max(.05, R(t) * SPEC.get('dead_r', .35))
            rads = [r0 * (1 - .75 * k / (len(pts) - 1)) + .01 for k in range(len(pts))]
            db = Branch(pts, rads, 1, .03, .2, 0., 'dead', cap=True); db.parent_r = R(t); branches.append(db)
            for f_ in (.55, .8):
                q, _ = at(pts, f_); dd = (tangent(pts, f_) + out.cross(UP) * rng.choice([-1, 1]) * .9 + UP * .4).normalized(); Lf = L * .28
                branches.append(Branch([q, q + dd * Lf * .5, q + dd * Lf + UP * .1 * Lf], [r0 * .4, r0 * .3, r0 * .2], 2, .2, .3, 0., 'dead', cap=True))
        # anchors: one per limb; groups under 7 sprays join their nearest neighbour while the sum stays <= 13
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
            groups.remove(g)
        anchors = []
        for g in groups:
            ch = g['sprays']; ends = [b.pts[-1] for b in ch]; c = sum(ends, Vector()) / len(ends)
            r = max(.8, max((e - c).length for e in ends)); rel = c - axis(c.z); layer = 'front' if rel.y < 0 else 'back'
            an = Anchor(c, r, g['out'], layer, twist=0., phase=g['phase'], idx=len(anchors), sprays=g['n']); an.branches = ch
            for b in ch: b.anchor = an
            anchors.append(an)
        return dict(branches=branches, anchors=anchors, H=H, P=P, R=R, axis=axis, zt=zt, rng_seed=cfg['seed'],
                    main_limbs=len(cfg['sil']) + cfg['fill']['n'])

    def wood(buf, sk, lod):
        n0 = buf.tris(); spec = WOOD[lod]; buf.surface_normals = True; buf.still_below = 2.05
        for br in sk['branches']:
            lv = 9 if br.kind == 'stub' else (8 if br.kind == 'dead' else br.level)
            s = spec.get(lv)
            if s is None: continue
            sides, step = s
            if br.kind not in ('trunk', 'stub') and br.level < 3:
                pr = getattr(br, 'parent_r', None); r = br.rads[0]
                nb = Branch(br.pts, list(br.rads), br.level, br.w0, br.w1, br.phase, br.kind, br.section, br.cap)
                if getattr(br, 'union', 0.) > .5:
                    pass        # grows out of the trunk swelling; no collar ring needed
                elif pr and lod < 2 and (br.level == 1 or r > COLLAR_MIN_R):
                    # branch collar: swell to at most 0.8 x the parent radius (ridged parents dip below their mean radius), ease back over about one branch diameter
                    nb.collar = (max(0., min(COLLAR_A, .8 * pr / r - 1)), .85 * pr, 1.1 * r + .25 * pr,
                                 (4 if br.level == 1 else 2) if lod == 0 else 2)
                else:
                    nb.rads[0] *= 1.25
                br = nb
            buf.tube(br, sides, step, seed=br.phase * 7, nmin=2 if br.level == 3 else 3)
        return buf.tris() - n0

    def foliage(buf, sk, lod, var, rng):
        """Leaves along every spray from t0 to the tip, spaced so they fill the LOD budget (4 triangles each). Returns (leaves, 0)."""
        cfg = VARIANTS[var]; anchors = sk['anchors']; axis = sk['axis']; lf = LEAF[lod]
        sprays = [b for b in sk['branches'] if b.kind == 'twig' and b.level == 3]
        dense = {id(b): catmull(b.pts, 6) for b in sprays}
        env = envelope_fn([p for b in sprays for p in dense[id(b)][2:]], axis)
        zc0 = min(a.c.z for a in anchors) - .8; ztop = max(a.c.z for a in anchors) + .6
        lt = 2 + 2 * len(lf['shape']) if lf.get('shape') else 4      # triangles per leaf
        cw_ = cfg.get('crown') or {}; mw = SPEC.get('mass_light')
        mc = np.array([[c.x, c.y, c.z] for c in cw_.get('_cc', [])]) if (mw and cw_.get('_cc')) else None
        msig = cw_['clumps'][1] if mc is not None else 1.
        cap = int(min(G.get('LOD_CAP', LOD_CAP)[lod] * .985 - buf.tris(), 1e9) / lt * cfg.get('leaves', 1.) * lf.get('fill', 1.))
        per = sum(lf['per']) / 2
        t0 = lf.get('t0', .3)
        total = sum(sum((d[i + 1] - d[i]).length for i in range(len(d) - 1)) for d in dense.values())
        gap = total * (1 - t0) / max(cap / per, 1)
        n_leaf = 0
        order = list(range(len(sprays))); rng.shuffle(order)
        for bi in order:
            b = sprays[bi]; pts = dense[id(b)]; L = sum((pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)); an = b.anchor
            n = int(L * (1 - t0) / gap + rng.random())
            for j in range(n):
                if n_leaf >= cap: break
                t = t0 + (1 - t0) * ((j + rng.uniform(.25, .75)) / n) ** .8
                q, _ = at(pts, t); td = tangent(pts, t)
                a = axis(q.z); radial = Vector((q.x - a.x, q.y - a.y, 0)); hr = radial.length; outv = radial.normalized() if hr > 1e-3 else an.out
                hn = min(1., max(0., (q.z - zc0) / max(ztop - zc0, .1))); rim = min(1., hr / max(env(q.z), .5))
                local = max(-1., min(1., (q.z - an.c.z) / max(an.r * .35, .2)))
                if mc is not None:      # 2026-11-16 leaf masses: each mass lit as its own dome (top / outside bright, underside and gaps dark)
                    j = int(np.argmin(((mc - np.array((q.x, q.y, q.z))) ** 2).sum(1))); mcj = Vector(mc[j]); v = q - mcj
                    Ld = (UP * .85 + outv * .5).normalized()
                    lit = .5 + .5 * max(-1., min(1., v.dot(Ld) / (1.2 * msig)))
                    edge = min(1., v.length / (1.9 * msig))
                    mass = min(mw[2] if len(mw) > 2 else 1., .22 + .95 * lit * (1 - mw[1] * edge * edge))
                    expo = (1 - mw[0]) * (.26 * hn + .3 * rim + .24 * (.5 + .5 * local) + .2 * t) + mw[0] * mass + rng.normal(0, .04)
                else:
                    expo = .26 * hn + .3 * rim + .24 * (.5 + .5 * local) + .2 * t + rng.normal(0, .04)
                expo = min(1., max(0., expo * 1.1 - .06)); ek = SPEC.get('expo_k', 1.)
                if ek != 1.: expo = min(1., max(0., .5 + (expo - .5) * ek))
                k = int(rng.integers(lf['per'][0], lf['per'][1] + 1))
                for (d, sd, nr, ln, wd, c) in _leaves(SPEC['leaf_kind'], lf, q, td, outv, t, k, rng):
                    if n_leaf >= cap: break
                    tone = min(1., max(0., expo * .78 + .3 * (nr.z - .5) + .1 + rng.normal(0, .035)))
                    occl = min(1., max(.15, .4 + .6 * expo))
                    col = palette_colour(PALETTE, tone, occl, OCCL_LO)
                    if mc is not None: bias_dir = ((q - mcj) * (.7 / msig) + outv * .35 + UP * .7).normalized()
                    else: bias_dir = ((q - an.c) * (.6 / max(an.r, .3)) + outv * .45 + UP * .8).normalized()
                    buf.leaf(c, (d, sd, nr), ln, wd, wd * lf.get('rib', .2), col, occl, tone, .62 + .38 * t, an.phase + rng.uniform(0, .06),
                             nrm_bias=bias_dir, bias=.55, widest=lf['widest'], shape=lf.get('shape'), tip=lf.get('tip', .5))
                    n_leaf += 1
        return n_leaf, 0

    def _frame(d, rng, roll=0.):
        sd = d.cross(UP); sd = sd.normalized() if sd.length > 1e-3 else d.orthogonal().normalized()
        nr = sd.cross(d).normalized()
        if nr.z < 0: nr = -nr
        if roll:
            ca, sa = math.cos(roll), math.sin(roll); sd, nr = (sd * ca + nr * sa).normalized(), (nr * ca - sd * sa).normalized()
            if nr.z < 0: nr = -nr
        return sd, nr

    def _leaves(kind, lf, q, td, outv, t, k, rng):
        """Yield (along, side, normal, length, width, centre) for k leaves at spray point q."""
        out = []
        if kind == 'frond' and lf.get('span'):
            # scale-leaf spray (cypress): k narrow leaflets set alternately ALONG a short axis that runs on from q, angled
            # forward, shorter toward the tip, the axis drooping a little - a feather, not a star of leaves round one point
            hd = Vector((td.x, td.y, td.z * .35)); hd = hd.normalized() if hd.length > 1e-3 else outv
            side = hd.cross(UP).normalized() if hd.cross(UP).length > 1e-3 else outv.cross(UP).normalized()
            span = rng.uniform(*lf['span']); droop = rng.uniform(.05, .3); sg = 1 if rng.random() < .5 else -1
            for m in range(k):
                f = m / max(k - 1, 1); sg = -sg
                base = q + hd * (span * f) - UP * (droop * span * f * f)
                ang = rng.uniform(*lf['spread']) * (1 - .35 * f)
                d = (hd * math.cos(ang) + side * sg * math.sin(ang) - UP * rng.uniform(.05, .35)).normalized()
                ln = rng.uniform(*lf['L']) * (1 - .45 * f); wd = rng.uniform(*lf['W']) * (1 - .3 * f)
                sd, nr = _frame(d, rng, rng.normal(0, lf.get('roll', .55)))
                out.append((d, sd, nr, ln, wd, base + d * ln * .48))
        elif kind == 'frond':
            # pinnate in the frond's own plane (nearly level), leaves sweeping forward, tips drooping; one terminal leaf
            hd = Vector((td.x, td.y, td.z * .35)); hd = hd.normalized() if hd.length > 1e-3 else outv
            side = hd.cross(UP).normalized() if hd.cross(UP).length > 1e-3 else outv.cross(UP).normalized()
            for m in range(k):
                sg = 1 if m % 2 else -1; ang = rng.uniform(*lf['spread'])
                d = (hd * math.cos(ang) + side * sg * math.sin(ang) - UP * rng.uniform(.1, .55)).normalized()
                ln = rng.uniform(*lf['L']) * (1.15 if m == 0 else 1.); wd = rng.uniform(*lf['W'])
                sd, nr = _frame(d, rng, rng.normal(0, lf.get('roll', .55)))
                base = q + hd * rng.uniform(-.06, .06)
                out.append((d, sd, nr, ln, wd, base + d * ln * .48))
        elif kind == 'cluster':
            ax = (td * lf.get('ax', (.45, .75, .25))[0] + UP * lf.get('ax', (.45, .75, .25))[1] + outv * lf.get('ax', (.45, .75, .25))[2]).normalized(); e1 = ax.orthogonal().normalized(); e2 = ax.cross(e1).normalized()
            a0 = rng.uniform(0, 2 * math.pi)
            for m in range(k):
                ph = a0 + m * 2 * math.pi / k + rng.normal(0, .3); cone = rng.uniform(*lf['cone'])
                d = (ax * math.cos(cone) + (e1 * math.cos(ph) + e2 * math.sin(ph)) * math.sin(cone)); d.z *= .7; d = d.normalized()
                ln = rng.uniform(*lf['L']); wd = rng.uniform(*lf['W'])
                sd, nr = _frame(d, rng, rng.normal(0, .35))
                out.append((d, sd, nr, ln, wd, q + d * (ln * .5 + .03)))
        else:   # 'fan': ginkgo spur - fans on short stalks, faces turned up and out
            ax = (td * .3 + UP * .7 + outv * .4).normalized(); e1 = ax.orthogonal().normalized(); e2 = ax.cross(e1).normalized()
            a0 = rng.uniform(0, 2 * math.pi)
            for m in range(k):
                ph = a0 + m * 2 * math.pi / k + rng.normal(0, .35); cone = rng.uniform(*lf['cone'])
                d = (ax * math.cos(cone) + (e1 * math.cos(ph) + e2 * math.sin(ph)) * math.sin(cone)); d.z *= .75; d = d.normalized()
                ln = rng.uniform(*lf['L']); wd = ln * rng.uniform(*lf['aspect'])
                sd, nr = _frame(d, rng, rng.normal(0, .4))
                out.append((d, sd, nr, ln, wd, q + d * (ln * .5 + rng.uniform(.03, .08))))
        return out

    return skeleton, wood, foliage
