"""Broadleaf engine for TR03-TR07 (work pack 2026-11-11 B-64h, batch B), the same method as TR01 / TR02 (golden-spirit-tree way:
real wood, leaves on the twig tips, no cloud masses), with a broadleaf habit grown by space colonisation:

- crown: a lumpy envelope (ellipsoid, radius modulated by low-frequency noise per direction) holds a number of leaf clusters
  (balls of target points, farthest-point spread, mostly near the surface). The clusters are what reads from a distance: big
  overlapping bunches with sky and shade between them, each lit on top and dark underneath.
- wood: the trunk splits into a few seeded scaffold limbs; from their ends the branches grow towards the cluster points (space
  colonisation), forking wherever the points pull two ways, so every cluster is reached by a real branch. Radii by the pipe model
  (thicker where more tips are carried). The branch graph is cut into chains (each continues into its biggest child); forks of
  similar thickness fuse in the Skin mesh (smooth crotches), thin side shoots are their own Skin island (tr_skin `parent` hook).
- leaves: leaf-spray cards (one twiglet with its leaves drawn in the atlas) around the last metre of every branch tip; one tone per
  card from where it sits: top / outer / facing up / top of its own cluster = light, under / inner = dark. Card normals blend the
  envelope normal and the cluster's own normal, so each cluster has its own light and dark in Unity too.

A species module defines the drawing (CELLS, PALETTE, ...) and VARIANTS, then calls install(globals()).
VARIANTS[v]: H, seed, r0, twist, trunk (control points, last z = split height as a fraction of H), burls, crown (cx, cy, cz, Rx, Ry,
Rz, lump), zmin, clumps (count, radius range, points per clump, shell 0..1), scaffolds [(t, az deg, elev deg, seed length m)],
leaves (card share), and any GROW key to override.
"""
import math
import numpy as np
from mathutils import Vector, Matrix, noise
from tr_tree import Branch, catmull
from tr_cypress import _at, _angdiff, _mix, _section as cy_section

GROW = dict(step=.38, d_inf=3.2, d_kill=.75, trop=(0., 0., .12), iters=90, r_tip=.014, pipe=.5, top_r=.95, smooth=3,
            tip_back=1.1, cards=7000, card_len=(.5, .7), leaf_len=(.5, .64), hang=0., up_bias=.2,
            room={1: 2050, 2: 720}, csize={1: (1.0, 1.25), 2: (1.2, 1.5)}, t8_off=-.3, sag=.0, pull=0., squash=.8)


def _rot(v, axis, ang): return (Matrix.Rotation(ang, 3, axis.normalized()) @ v).normalized()


class Crown:
    """Lumpy ellipsoid envelope: val(q) < 1 inside. The lump modulates the radius by direction (low-frequency noise)."""
    def __init__(self, cx, cy, cz, Rx, Ry, Rz, lump, seed):
        self.c = Vector((cx, cy, cz)); self.R = Vector((Rx, Ry, Rz)); self.lump = lump; self.o = Vector((seed * 3.1, seed * 1.7, seed * .9))

    def rel(self, q):
        d = q - self.c; return Vector((d.x / self.R.x, d.y / self.R.y, d.z / self.R.z))

    def rad(self, q):
        r = self.rel(q); n = r.normalized() if r.length > 1e-6 else Vector((0, 0, 1))
        return 1. + self.lump * noise.noise(n * 1.6 + self.o) + .5 * self.lump * noise.noise(n * 3.4 + self.o * 2.)

    def val(self, q): return self.rel(q).length / self.rad(q)

    def normal(self, q):
        d = q - self.c; g = Vector((d.x / self.R.x ** 2, d.y / self.R.y ** 2, d.z / self.R.z ** 2))
        return g.normalized() if g.length > 1e-6 else Vector((0, 0, 1))


def clumps_in(cr, rng, count, rad, per, shell, zmin, extra=None, squash=.8):
    """Cluster centres spread by farthest-point sampling over envelope points biased to the surface (shell 0..1), then `per` target
    points in a ball of radius rad[0..1] round each. Returns (centres N x 3, radii N, points M x 3, clump index per point)."""
    cand = []
    while len(cand) < 3000:
        u = rng.normal(size=3); u /= np.linalg.norm(u); r = rng.uniform(shell, 1.) ** .5
        q = cr.c + Vector((u[0] * cr.R.x, u[1] * cr.R.y, u[2] * cr.R.z)) * r * .82
        q = cr.c + (q - cr.c) * cr.rad(q)
        if q.z > zmin + .6: cand.append(tuple(q))
    cand = np.array(cand)
    cs = [cand[int(rng.integers(len(cand)))]] if count else []
    for _ in range(count - 1):
        d2 = np.min([((cand - c) ** 2).sum(1) for c in cs], 0); cs.append(cand[int(d2.argmax())])
    cs = np.array(cs, float).reshape(-1, 3); rr = rng.uniform(*rad, len(cs))
    if extra is not None:        # given clusters (x, y, z, radius), e.g. the maple's tiers
        ex = np.array(extra, float); cs = np.concatenate([cs, ex[:, :3]]); rr = np.concatenate([rr, ex[:, 3]])
    pts = []; who = []
    for k, (c, r) in enumerate(zip(cs, rr)):
        for _ in range(per):
            u = rng.normal(size=3); u /= np.linalg.norm(u); p = c + u * r * rng.random() ** .5 * np.array([1, 1, squash])
            if p[2] > zmin: pts.append(p); who.append(k)
    return cs, rr, np.array(pts), np.array(who)


def colonize(seed_pts, seed_par, nosprout, A, step, d_inf, d_kill, trop, iters):
    """Space colonisation. seed_pts / seed_par: the starting graph (parent -1 = attached to the trunk). Returns positions, parents."""
    P = [np.array(p, float) for p in seed_pts]; par = list(seed_par); ns_ = set(nosprout); A = np.array(A, float); trop = np.array(trop, float)
    for it in range(iters):
        if len(A) == 0: break
        Pm = np.array(P); ok = np.array([i not in ns_ for i in range(len(P))])
        d2 = (A ** 2).sum(1)[:, None] + (Pm ** 2).sum(1)[None, :] - 2 * A @ Pm.T; d2[:, ~ok] = 1e9
        j = d2.argmin(1); dm = np.sqrt(np.maximum(d2[np.arange(len(A)), j], 0))
        m = dm < d_inf
        if not m.any(): break
        v = A[m] - Pm[j[m]]; v /= np.linalg.norm(v, axis=1)[:, None] + 1e-9
        acc = np.zeros_like(Pm); np.add.at(acc, j[m], v); cnt = np.bincount(j[m], minlength=len(Pm))
        new = []
        for i in np.nonzero(cnt)[0]:
            d = acc[i] / (np.linalg.norm(acc[i]) + 1e-9) + trop; d /= np.linalg.norm(d) + 1e-9
            q = Pm[i] + d * step
            if np.min(((Pm - q) ** 2).sum(1)) < (step * .45) ** 2: continue     # an oscillating tip: skip
            new.append((q, i))
        if not new: break
        for q, i in new: P.append(q); par.append(int(i))
        Q = np.array([q for q, _ in new])
        dk = (A ** 2).sum(1)[:, None] + (Q ** 2).sum(1)[None, :] - 2 * A @ Q.T
        A = A[np.sqrt(np.maximum(dk.min(1), 0)) > d_kill]
    return np.array(P), np.array(par)


def install(ns):
    """Fill a species module's namespace with skeleton(), extra_geometry() and the bookkeeping build_trees_b expects."""
    VAR = ns['VARIANTS']; G = dict(GROW); G.update(ns.get('GROW', {}))
    NT = len(ns['PALETTE']); CT = ns.get('CLUSTER_TONES', (1, 3, 4, 6))
    NODES = {}; CROWN = {}; CLUMPS = {}

    def g(cfg, k): return cfg.get(k, G[k])

    def trunk_fn(cfg):
        H = cfg['H']; r0 = cfg['r0']; zt = H * cfg['trunk'][-1][2]
        ctrl = [Vector((x, y, -.3 if z < 0 else z * H)) for x, y, z, r in cfg['trunk']]
        dense = catmull(ctrl, 20); zz = np.array([p.z for p in dense])
        rr = np.interp(np.linspace(0, 1, len(dense)), np.linspace(0, 1, len(ctrl)), [r ** .85 * r0 for x, y, z, r in cfg['trunk']])
        xs = np.array([p.x for p in dense]); ys = np.array([p.y for p in dense])
        def P(t):
            z = -.3 + (zt + .3) * min(1., max(0., t)); return Vector((float(np.interp(z, zz, xs)), float(np.interp(z, zz, ys)), z))
        def R(t):
            z = -.3 + (zt + .3) * min(1., max(0., t)); return float(np.interp(z, zz, rr))
        return P, R, zt

    def skeleton(var):
        cfg = VAR[var]; rng = np.random.default_rng(cfg['seed']); H = cfg['H']; zmin = cfg['zmin']
        P, R, zt = trunk_fn(cfg)
        cr = Crown(*cfg['crown'], seed=cfg['seed']); CROWN[var] = cr
        ts = np.linspace(0, 1., 22)
        trunk = Branch([P(t) for t in ts], [max(.03, R(t)) for t in ts], 0, 0., 0., 0., 'trunk', cy_section(cfg['seed'] * .7, cfg['twist'], cfg.get('burls', [])))
        trunk.twist = cfg['twist']; trunk.uv_tile = .8; tc = min(1., 1.6 / (zt + .3)); trunk.uv_k = max(2, round(2 * math.pi * R(tc) * 1.06 / trunk.uv_tile))
        branches = [trunk]
        cn, crad, cper, shell = cfg['clumps']
        cs, rr, A, who = clumps_in(cr, rng, cn, crad, cper, shell, zmin, cfg.get('extra_clumps'), g(cfg, 'squash'))
        CLUMPS[var] = (cs, rr)
        # seeds: each scaffold a gently curved run from the trunk; only its last node may sprout
        sp, spar, nos, roots = [], [], [], []
        step = g(cfg, 'step')
        for (t, az, el, L) in cfg['scaffolds']:
            a = math.radians(az + rng.normal(0, 3)); e = math.radians(el)
            d = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))); p = P(t)
            n = max(2, int(L / step)); prev = -1
            for k in range(n + 1):
                s = k / n; dd = (d + Vector((0, 0, -.25 * s * math.cos(e)))).normalized() if k else d
                q = p + dd * (L * s) + Vector((0, 0, .15 * L * math.sin(math.pi * s)))
                sp.append(tuple(q)); spar.append(prev)
                if k == 0: roots.append((len(sp) - 1, t))
                if k < n - 1: nos.append(len(sp) - 1)
                prev = len(sp) - 1
        Pn, par = colonize(sp, spar, nos, A, step, g(cfg, 'd_inf'), g(cfg, 'd_kill'), g(cfg, 'trop'), g(cfg, 'iters'))
        M = len(Pn); kids = [[] for _ in range(M)]
        for i in range(M):
            if par[i] >= 0: kids[par[i]].append(i)
        # tips carried (pipe model) -> radius
        tips = np.zeros(M)
        for i in range(M - 1, -1, -1):
            tips[i] += 1 if not kids[i] else 0
            if par[i] >= 0: tips[par[i]] += tips[i]
        rt = g(cfg, 'r_tip'); top = R(1.) * g(cfg, 'top_r'); tmax = max(tips[i] for i, _ in roots)
        rad = rt + (top - rt) * (tips / tmax) ** g(cfg, 'pipe')
        for i, t in roots: rad[i] = min(rad[i] * 1.0, R(t) * (.8 if t > .97 else .45))
        # sag: long thin horizontal runs droop a little under their own weight
        if g(cfg, 'sag'):
            for i in range(M):
                if par[i] >= 0:
                    Pn[i] = Pn[i] - np.array([0, 0, g(cfg, 'sag') * step / max(rad[i], .02) * .01])
        # chains: follow the child that carries the most tips
        rootset = {i for i, _ in roots}; chains = []
        def chain_from(i, level, parent_bi, start=None):
            pts = [start] if start is not None else []
            j = i
            while True:
                pts.append(j)
                if not kids[j]: break
                ks = sorted(kids[j], key=lambda k: -tips[k])
                for k in ks[1:]: chains.append((k, j))
                j = ks[0]
            return pts
        stack = [(i, 1, 'T', None) for i, _ in roots]; out = []
        while stack:
            i, level, pbi, st = stack.pop()
            chains.clear(); pts = chain_from(i, level, pbi, st)
            oi = len(out); out.append((pts, level, pbi))
            for k, j in list(chains): stack.append((k, level + 1, oi, j))
        nodes = []; bmap = {'T': 0}
        for oi, (pts, level, pbi) in enumerate(out):
            if len(pts) < 2: bmap[oi] = bmap[pbi]; continue
            bmap[oi] = len(branches); pbi = bmap[pbi]
            X = np.array([Pn[k] for k in pts]); rr_ = np.array([rad[k] for k in pts])
            for _ in range(g(cfg, 'smooth')):
                X[1:-1] = .5 * X[1:-1] + .25 * (X[:-2] + X[2:])
            w = {1: (.02, .25), 2: (.2, .4)}.get(level, (.4, .55))
            b = Branch([Vector(p) for p in X], list(rr_), min(level, 3), w[0], w[1], float(rng.random()), 'limb' if level <= 1 else 'twig')
            b.parent = pbi; branches.append(b)
            if not kids[pts[-1]]:       # a tip: leaf nodes along its last metre
                L = 0.; k = len(X) - 1; tipq = Vector(X[-1]); cc = int(np.argmin(((cs - X[-1]) ** 2).sum(1)))
                while k > 0 and L < g(cfg, 'tip_back'):
                    q = Vector(X[k]); tdir = (Vector(X[k]) - Vector(X[k - 1])).normalized()
                    nodes.append(dict(q=q, t=tdir, phase=b.phase, cc=Vector(cs[cc]), cl=float(rr[cc]), tip=tipq, sq=g(cfg, 'squash')))
                    L += (Vector(X[k]) - Vector(X[k - 1])).length; k -= 1
        for (t, az_) in cfg.get('stubs', []):
            a = math.radians(az_); s = P(t); dd = Vector((math.cos(a), math.sin(a), .1)).normalized(); L = R(t) + rng.uniform(.15, .3)
            branches.append(Branch([s, s + dd * L * .55, s + dd * L], [R(t) * .32, R(t) * .27, R(t) * .22], 3, 0., 0., 0., 'stub', cap=True))
        NODES[var] = [n for n in nodes if n['q'].z > zmin - .4]
        print('SKEL', var, 'nodes', M, 'branches', len(branches), 'leafnodes', len(NODES[var]), 'clumps', len(cs), flush=True)
        return branches, [], H, P, R

    def light_of(c, cr, nd, leafdir, rng):
        rel = cr.rel(c); hn = min(1., max(0., .5 + .5 * rel.z / max(.2, rel.length))) if rel.length > 1e-3 else .5
        rim = min(1., cr.val(c)); above = min(1., max(-1., (c.z - nd['cc'].z) / (nd['cl'] * nd.get('sq', 1.))))
        return .14 * hn + .2 * rim ** 1.2 + .1 * (.5 + .5 * leafdir.z) + .5 * (.5 + .5 * above) ** 1.3 + .08 + rng.normal(0, .04)

    def foliage(buf, var, lod, rng):
        cfg = VAR[var]; nodes = NODES[var]; cr = CROWN[var]; zmin = cfg['zmin']; CR = ns['CELL_RECTS']; CA = ns['CELL_ASPECT']
        n_cards = 0
        if lod == 0:
            per = g(cfg, 'cards') * cfg.get('leaves', 1.) / len(nodes)
            for nd in nodes:
                q = nd['q']; out = cr.normal(q); cn0 = (q - nd['cc']); cn0 = cn0.normalized() if cn0.length > 1e-3 else out
                hang = g(cfg, 'hang')
                ax = (out * .3 + cn0 * .35 + nd['t'] * .45 + Vector((0, 0, g(cfg, 'up_bias') - hang)) + Vector(rng.normal(0, .35, 3))).normalized()
                nl = int(per) + (1 if rng.random() < per - int(per) else 0); Lt = rng.uniform(*g(cfg, 'card_len'))
                perp0 = ax.orthogonal().normalized()
                for k in range(nl):
                    s = (k + rng.uniform(.1, .9)) / max(nl, 1); stem = q + ax * Lt * s
                    az = rng.uniform(0, 2 * math.pi); pv = (perp0 * math.cos(az) + ax.cross(perp0) * math.sin(az)).normalized()
                    oa = rng.uniform(.45, 1.2) * (1 - .4 * s); ld = (ax * math.cos(oa) + pv * math.sin(oa)).normalized()
                    ll = rng.uniform(*g(cfg, 'leaf_len')) * (1.1 - .2 * s); c = stem + ld * ll * .5
                    pull = g(cfg, 'pull')
                    if pull:     # part of the way out to the cluster's surface: clusters read as full bunches, still on their twigs
                        rel = c - nd['cc']; sq = g(cfg, 'squash'); L0 = Vector((rel.x, rel.y, rel.z / sq)).length     # the cluster's own (flattened) shape
                        if L0 > 1e-3: c = nd['cc'] + rel * ((1 - pull) + pull * nd['cl'] * rng.uniform(.8, 1.) / L0)
                    if c.z < zmin - .6: continue
                    n = ld.cross(pv).normalized(); n = (n + Vector(rng.normal(0, .25, 3))).normalized()
                    light = light_of(c, cr, nd, ld, rng)
                    tone = int(min(NT - 1, max(0, round(light * (NT - 1)))))
                    alt = ns.get('CLUSTER_ALT')       # species with a second colour ramp in slot 1 (TR04 ochre): one ramp per cluster
                    if alt: sl = int((int(abs(nd['cc'].x * 73.1 + nd['cc'].y * 31.7 + nd['cc'].z * 57.3)) % 100) < alt * 100)
                    else: sl = int(rng.random() < .45)
                    key = ('L', tone, sl)
                    cn = (c - nd['cc']); cn = cn.normalized() if cn.length > 1e-3 else out
                    shade = (cr.normal(c) * .35 + cn * .6 + Vector((0, 0, .15 + .6 * (light - .45) + ns.get('SHADE_UP', 0.))) + n * .1).normalized()     # SHADE_UP: translucent petals (TR07) never go dark
                    buf.card(c, n, ll / .92, CR[key], ld, (2, 2), 0., (lambda p, v=shade: v), .6 + .4 * s, nd['phase'] + rng.uniform(0, .05), aspect=CA[key])
                    n_cards += 1
        else:
            room = g(cfg, 'room')[lod]; size = g(cfg, 'csize')[lod]
            idx = rng.permutation(len(nodes))[:room] if len(nodes) > room else range(len(nodes))
            for i in idx:
                nd = nodes[int(i)]; q = nd['q']; out = cr.normal(q); cn0 = (q - nd['cc']); cn0 = cn0.normalized() if cn0.length > 1e-3 else out
                ax = (out * .35 + cn0 * .35 + nd['t'] * .35 + Vector((0, 0, g(cfg, 'up_bias'))) + Vector(rng.normal(0, .2, 3))).normalized()
                sz = rng.uniform(*size); c = q + ax * sz * .3
                n = ax.cross(Vector((0, 0, 1))); n = (n.normalized() if n.length > 1e-3 else Vector((1, 0, 0))) + Vector((0, 0, .5)) + Vector(rng.normal(0, .25, 3)); n.normalize()
                light = light_of(c, cr, nd, Vector((ax.x, ax.y, 0.)), rng)
                t8 = light * (NT - 1) + g(cfg, 't8_off'); tone = int(np.argmin([abs(t8 - x) for x in CT]))
                cn = (c - nd['cc']); cn = cn.normalized() if cn.length > 1e-3 else out
                shade = (out * .45 + cn * .35 + Vector((0, 0, .2 + .8 * (light - .45) + ns.get('SHADE_UP', 0.))) + n * .15).normalized()
                buf.card(c, n, sz, CR[('C', tone)], ax, (2, 2), 0., (lambda p, v=shade: v), .8, nd['phase'], aspect=CA[('C', tone)])
                n_cards += 1
        return n_cards

    def extra_geometry(buf, var, lod, P, R, rng, trunk_range):
        n = foliage(buf, var, lod, rng); ns['last_extra_cards'] = n
        return 2 * n

    ns.update(skeleton=skeleton, extra_geometry=extra_geometry, last_extra_cards=0, WOOD='skin', _NODES=NODES, _CROWN=CROWN, _CLUMPS=CLUMPS)
    ns.setdefault('SKIN_WOOD', {0: ((0, 1, 2, 3), 2, 9000), 1: ((0, 1, 2), 1, 2600), 2: ((0, 1), 1, 750)})
    ns.setdefault('CELL_AO', .012); ns.setdefault('CELL_M', 1.0)


def std_cells(NT, cluster_tones=(1, 3, 4, 6)):
    """Atlas layout shared by every TR species: cell 0 = 4 x 4 single sprays (NT tones x 2 shapes); cell 1 top = four cluster cells."""
    CR = {}; CA = {}
    for t in range(NT):
        for s in range(2):
            k = t * 2 + s; c, r = k % 4, k // 4
            CR[('L', t, s)] = (c * .125, 1 - (r + 1) * .125, (c + 1) * .125, 1 - r * .125); CA[('L', t, s)] = 1.
    for k in range(4):
        c, r = k % 2, k // 2
        CR[('C', k)] = (.5 + c * .25, .625 + r * .1875, .5 + (c + 1) * .25, .625 + (r + 1) * .1875); CA[('C', k)] = .25 / .1875
    return CR, CA


# ------------------------------------------------------------------ atlas drawing helpers
# widest about 40 % up, rounded shoulders, drawn-out tip (camphor, plum); 16 points so the rim reads as a curve, not a polygon
OVATE = [round(math.sin(math.pi * (i / 15) ** .82) ** .75 * (1 - .12 * i / 15), 4) for i in range(16)]


def blade(st, p, d, L, w, c0, c1, z, prof=OVATE, rim=.003, shade=.78, rim_col=.42, fold=.1):
    """One leaf folded along its midrib: lit half / shaded half, raised midrib, thin dark rim underneath; c0 at the base, c1 at the tip."""
    from tr_tex import to_lin
    p = np.array(p[:2], np.float32); d = np.array(d, np.float32); d /= np.linalg.norm(d) + 1e-9; s = np.array([-d[1], d[0]], np.float32)
    n = len(prof); c = [p + d * L * i / (n - 1) for i in range(n)]
    st.strip([(c[i][0], c[i][1], z - .0006) for i in range(n)], [w * x + rim for x in prof], [tuple(to_lin(c0 * rim_col))] * n, ridge=0.)
    k0 = len(st.v)
    for i in range(n):
        t = i / (n - 1); lit = _mix(c0, c1, t); shd = lit * shade; hw = w * prof[i] + 1e-4; zz = z + .0003 * i
        for (x, col) in ((-1, lit), (0, lit * 1.07), (0, shd), (1, shd)):
            q = c[i] + s * hw * x
            st.v.append((float(q[0]), float(q[1]), zz + (w * fold if x == 0 else 0.))); st.c.append(tuple(to_lin(np.clip(col, 0, 1))))
    for i in range(n - 1):
        a = k0 + i * 4
        st.f.append((a, a + 1, a + 5, a + 4)); st.f.append((a + 2, a + 3, a + 7, a + 6))


def cluster_cells(st, rng, cell, draw, cluster_tones, NT, spread=2.1, n=7):
    """Cell 1 top (y -0.25..0.5): four cluster cells (0.5 wide x 0.375 tall), dark -> light: a fan of n sprays from the bottom middle."""
    for k, tone in enumerate(cluster_tones):
        c, r = k % 2, k // 2
        x0, y0 = -cell / 2 + c * cell / 2, -cell / 4 + r * cell * .375; w, h = cell / 2, cell * .375
        base = np.array([x0 + w / 2, y0 + h * .06])
        for j in range(n):
            a = math.pi / 2 + (j / (n - 1) - .5) * spread + rng.normal(0, .06); L = h * (.86 - .3 * abs(j / (n - 1) - .5) * 2)
            L = min(L, (w / 2 - .02) / max(.2, abs(math.cos(a))) if abs(math.cos(a)) > .3 else L)
            mid = (n - 1) / 2
            tt = min(NT - 1, max(0, tone + (1 if abs(j - mid) < .6 else -1 if abs(j - mid) >= mid - .1 else 0)))
            draw(st, rng, base, (math.cos(a), math.sin(a)), L, tt, j % 2, z0=.004 * (mid - abs(j - mid)))
