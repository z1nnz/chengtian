"""TR06 weeping willow (垂柳), broadleaf engine tr_broad for the wood, its own hanging-strand foliage.

12-13 m, A3 and the A1 creek side. Work pack: the hanging branches are bundles of long strip leaf cards that sway in the wind; the
trunk leans out over the water. Codex three-view TR06 cand-3 (chosen): a thick gnarled trunk leaning to one side, a few big limbs
arching up and out into a dome, and from every twig end a bundle of long thin strands falling almost to the ground, muted
grey-green, lit outer strands warmer, inner strands blue-grey.
A  12.5 m  trunk leaning gently one way, four limbs, a round dome of curtains.
B  12.2 m  trunk leaning hard out over the water, the crown pushed out over the lean (the creek-side tree).
C  12.8 m  old willow: thick, burled, split into two leads at 3 m, the widest dome, a broken stub.
Foliage: each bundle = 3-6 strands (LOD0) / 2 (LOD1) hanging from a twig end; each strand a chain of tall strip cards (atlas cell 0:
16 strands, 8 tones x 2 forms), lower cards sway more (wind weight in the vertex colour). LOD2: one curtain card per bundle per
4 m (atlas cell 1 top: four curtain cells). Wood from tr_broad (space colonisation, pipe-model radii) as for TR03-TR05.
Origin trunk base centre, the lean goes to +X (towards the water when placed).
"""
import math
import numpy as np
from mathutils import Vector
from tr_tex import hexc, to_lin
from tr_broad import install, blade, _mix

# blue-grey green inside -> muted warm sage on the lit outer strands; never neon
PALETTE = [hexc(h) for h in ('#24332F', '#2B3B34', '#334438', '#3C4D3C', '#465741', '#506045', '#5B6A49', '#66734D')]
STEM = hexc('#5A5238')
NT = len(PALETTE)
CLUSTER_TONES = (1, 3, 4, 6)
BARK = 'willow'
# willow bark: grey-brown, deep criss-cross ridges (the team's hand-painted source, rougher)
BARK_PAINTED = dict(src='bark_src/elder_tree_bark_v1.png', sat=.36, gain=.9, tint=(.94, .92, .88), contrast=2.2, crack=1., normal=18., smooth_val=.07, blur_n=(0, 2))
LANCE = [0., .35, .62, .82, .94, 1., .98, .92, .83, .72, .6, .47, .34, .22, .11, 0.]    # narrow willow leaf, pointed at both ends

# atlas rects: cell 0 (u 0-.5, v .5-1) = 8 columns x 2 rows of tall strand cells; cell 1 top (u .5-1, v .625-1) = 4 curtain columns
CELL_RECTS, CELL_ASPECT = {}, {}
for _t in range(NT):
    for _s in range(2):
        _k = _t * 2 + _s; _c, _r = _k % 8, _k // 8
        CELL_RECTS[('L', _t, _s)] = (_c * .0625, 1 - (_r + 1) * .25, (_c + 1) * .0625, 1 - _r * .25); CELL_ASPECT[('L', _t, _s)] = .25
for _k in range(4):
    CELL_RECTS[('C', _k)] = (.5 + _k * .125, .625, .5 + (_k + 1) * .125, 1.); CELL_ASPECT[('C', _k)] = .125 / .375


def strand(st, rng, x, ytop, Lh, W, tone, kind, z0=0.):
    """One hanging strand drawn top-down in the cell: a thin twig from (x, ytop) falling Lh, narrow leaves alternating along it,
    pointing down and out; kind 1 = a fuller strand (a second twig beside the first)."""
    col = PALETTE[tone]; c0, c1 = col * .8, np.clip(col * 1.15 + .01, 0, 1)
    twigs = [(0., 1.)] if kind == 0 else [(-.12, 1.), (.14, .82)]
    for j, (dx, f) in enumerate(twigs):
        amp = W * rng.uniform(.04, .09); ph = rng.uniform(0, 6.28); L = Lh * f
        def at(s): return np.array((x + dx * W + amp * math.sin(ph + s * 5.), ytop - L * s), np.float32)
        st.strip([tuple(at(s)) + (z0,) for s in np.linspace(0, .97, 7)], list(np.linspace(.03 * W, .012 * W, 7)), [tuple(to_lin(STEM))] * 7, ridge=.4)
        n = 34 if kind == 0 else 26; sg = 1
        for i in range(n):
            s = .03 + .93 * i / (n - 1); q = at(s); sg = -sg
            a = sg * rng.uniform(.3, .6); ll = W * .47 * (1 - .25 * s) * rng.uniform(.85, 1.1)
            ld = np.array((math.sin(a), -math.cos(a)), np.float32)
            tn = _mix(c0, c1, .35 + .5 * (1 - s) * rng.uniform(.7, 1.))
            blade(st, q, ld, ll, ll * .14, c0, tn, z0 + .002 + .0004 * i + .01 * j, prof=LANCE, fold=.05, shade=.82, rim=.0005, rim_col=.62)
        for a in (-.12, .14):                         # the strand ends in two small leaves
            ld = np.array((math.sin(a), -math.cos(a)), np.float32)
            blade(st, at(.97), ld, W * .28, W * .28 * .14, c0, c1, z0 + .02 + .01 * j, prof=LANCE, fold=.05, shade=.82, rim=.0005, rim_col=.62)


def cell_leaves(st, rng, cell):
    W = cell / 8; Hc = cell / 2
    for t in range(NT):
        for s in range(2):
            k = t * 2 + s; c, r = k % 8, k // 8
            strand(st, rng, -cell / 2 + W * (c + .5), cell / 2 - Hc * r - Hc * .01, Hc * .97, W, t, s)


def cell_clusters(st, rng, cell):
    """four curtain cells (dark -> light): four or five strands side by side, staggered lengths."""
    for k, tone in enumerate(CLUSTER_TONES):
        x0 = -cell / 2 + k * cell / 4; Wc = cell / 4; Hc = cell * .75
        m = 5
        for j in range(m):
            tt = min(NT - 1, max(0, tone + (1 if j in (1, 3) else 0) - (1 if j == 0 else 0)))
            x = x0 + Wc * (.12 + .76 * j / (m - 1)) + rng.normal(0, Wc * .02)
            strand(st, rng, x, cell / 2 - rng.uniform(0, Hc * .08), Hc * rng.uniform(.8, .97), Wc * .36, tt, 0, z0=.001 * j)


CELLS = [cell_leaves, cell_clusters]

GROW = dict(cards=7400, step=.3, d_inf=2.4, d_kill=.45, pipe=.6, r_tip=.007, tip_back=1.4, trop=(0., 0., .06), squash=.55, smooth=5, up_bias=.1,
            seg=(1.0, 1.2), bundle=(4, 7), dmin=.75, zend=(.5, 2.4), lmax=7.5)
VARIANTS = {
    'A': dict(H=12.5, seed=151, r0=.56, twist=.08, zmin=6.2, leaves=1.,
              trunk=[(0, 0, -.03, 1.), (0, 0, 0, .95), (.12, 0, .06, .8), (.45, .04, .16, .7), (.85, .06, .26, .63), (1.15, .05, .34, .58)],
              burls=[(1.0, 1.3, .35), (3.2, 1.8, .3)],
              crown=(1.2, 0., 9.6, 5.6, 5.2, 3.0, .12), clumps=(18, (1.5, 2.0), 110, .25),
              scaffolds=[(1., 20, 62, 3.2), (1., 130, 52, 3.0), (1., 245, 50, 3.0), (.85, 330, 40, 2.6), (1., 70, 78, 2.4)]),
    'B': dict(H=12.2, seed=163, r0=.58, twist=-.1, zmin=5.8, leaves=1.,
              trunk=[(0, 0, -.03, 1.), (0, 0, 0, .95), (.25, 0, .05, .8), (.9, .05, .13, .7), (1.7, .1, .21, .63), (2.4, .12, .28, .57)],
              burls=[(2.2, 1.6, .4)],
              crown=(3.0, .2, 9.2, 5.8, 4.8, 3.0, .14), clumps=(17, (1.5, 2.0), 110, .25),
              scaffolds=[(1., 0, 45, 3.4), (1., 110, 58, 2.8), (1., 250, 60, 2.6), (.9, 180, 70, 2.4), (1., 40, 75, 2.2)]),
    'C': dict(H=12.8, seed=177, r0=.68, twist=.1, zmin=6.0, leaves=1.05,
              trunk=[(0, 0, -.03, 1.), (0, 0, 0, .95), (.1, -.05, .05, .8), (.3, -.08, .14, .74), (.55, -.05, .23, .7)],
              burls=[(.7, 1.0, .45), (2.4, 2.2, .45), (3.5, 1.2, .35)],
              crown=(.9, -.1, 9.7, 6.4, 5.9, 3.1, .15), clumps=(21, (1.5, 2.1), 105, .25),
              scaffolds=[(1., 15, 50, 3.6), (1., 195, 48, 3.4), (1., 100, 58, 3.0), (1., 290, 55, 3.0), (.8, 60, 40, 2.6)],
              stubs=[(.55, 240)]),
}
NAMES = {'A': 'Willow', 'B': 'Willow', 'C': 'OldWillow'}
ZH = {'A': '垂柳（主幹微斜、四大枝、圓頂垂簾）', 'B': '垂柳（主幹大幅斜出水面、樹冠偏向斜的那側；溪邊用）', 'C': '老垂柳（粗幹多樹瘤、3 m 分成兩股、樹冠最寬、一處斷枝）'}

install(globals())
_BUNDLES = {}


def _bundles(var):
    """Bundle origins (twig ends) and their strands, fixed per variant so every LOD hangs from the same places."""
    if var in _BUNDLES: return _BUNDLES[var]
    cfg = VARIANTS[var]; G = dict(GROW); G.update(cfg); rng = np.random.default_rng(cfg['seed'] + 5)
    cr = _CROWN[var]; ax = Vector((cr.cx, cr.cy, 0.)) if hasattr(cr, 'cx') else Vector((cfg['crown'][0], cfg['crown'][1], 0.))
    nodes = list(_NODES[var]); order = rng.permutation(len(nodes)); picked = []
    for i in order:
        nd = dict(nodes[int(i)])
        if rng.random() < .65: nd['q'] = nd['tip']        # most bundles hang from the twig end itself, hiding it
        q = nd['q']
        if all((q - p['q']).length > G['dmin'] for p in picked): picked.append(nd)
    out = []
    for nd in picked:
        q = nd['q']; h = Vector((q.x - ax.x, q.y - ax.y, 0.)); h = h.normalized() if h.length > 1e-3 else Vector((1, 0, 0))
        t = Vector((nd['t'].x, nd['t'].y, 0.)); t = t.normalized() if t.length > 1e-3 else h
        out_dir = (h * .65 + t * .35).normalized()
        zend = rng.uniform(*G['zend']); Ls = min(G['lmax'], max(1.4, q.z - zend)) * rng.uniform(.55, 1.)
        strands = []
        for k in range(int(rng.integers(G['bundle'][0], G['bundle'][1] + 1))):
            off = Vector((rng.normal(0, .14), rng.normal(0, .14), rng.normal(0, .1)))
            az = math.atan2(out_dir.y, out_dir.x) + rng.normal(0, .7)
            strands.append(dict(o=q + off, L=Ls * rng.uniform(.8, 1.05), reach=rng.uniform(.5, 1.1), face=az, ph=nd['phase'] + rng.uniform(0, .08)))
        out.append(dict(q=q, out=out_dir, strands=strands))
    _BUNDLES[var] = (out, ax)
    return _BUNDLES[var]


def _path(o, out_dir, reach, L, seg):
    """A strand: a short arc out and slightly up from the twig end, then falling straight under gravity; points every seg metres."""
    pts = [Vector(o)]; d = (out_dir * .75 + Vector((0, 0, .55))).normalized(); s = 0.
    while s < L - 1e-3:
        st_ = min(seg, L - s); d = (d + Vector((0, 0, -1.0 * st_ / max(reach, .2)))).normalized(); pts.append(pts[-1] + d * st_); s += st_
    return pts


def _light(c, ax, cr_R, H):
    r = min(1., Vector((c.x - ax.x, c.y - ax.y, 0.)).length / cr_R)
    return .38 * r ** 1.4 + .32 * min(1., c.z / H) + .12


def extra_geometry(buf, var, lod, P, R, rng, trunk_range):
    cfg = VARIANTS[var]; G = dict(GROW); G.update(cfg); H = cfg['H']; bundles, ax = _bundles(var); crR = cfg['crown'][3]
    t0 = buf.tris(); n_cards = 0
    if lod == 2:
        for j in (0, 1):                     # a second, crossed curtain per bundle while the LOD2 cap allows
          for b in bundles:
            if buf.tris() > 2400: break
            s0 = b['strands'][j % len(b['strands'])]; L = max(x['L'] for x in b['strands']) * (1. if j == 0 else .85)
            m = max(1, math.ceil(L / 4.)); pts = _path(s0['o'], b['out'], s0['reach'], L, L / m)
            face = s0['face'] + (0. if j == 0 else 1.35)
            for k in range(m):
                p0, p1 = pts[k], pts[k + 1]; c = (p0 + p1) * .5; up = p0 - p1; size = up.length * 1.08
                n = Vector((math.cos(face), math.sin(face), 0.))
                light = _light(c, ax, crR, H) + rng.normal(0, .04); tone = int(np.argmin([abs(light * (NT - 1) - .3 - x) for x in CLUSTER_TONES]))
                rad = Vector((c.x - ax.x, c.y - ax.y, 0.)); rad = rad.normalized() if rad.length > 1e-3 else n
                shade = (rad * .55 + Vector((0, 0, .1 + .6 * (light - .45))) + n * .15).normalized()
                buf.card(c, n, size, CELL_RECTS[('C', tone)], up, (2, 2), 0., (lambda p, v=shade: v), .55 + .45 * (k + 1) / m, s0['ph'], aspect=CELL_ASPECT[('C', tone)])
                n_cards += 1
    else:
        budget = G['cards'] * cfg.get('leaves', 1.) if lod == 0 else 1e9
        segL = rng.uniform(*G['seg']) if lod == 0 else 2.3
        for b in bundles:
            sts = b['strands'] if lod == 0 else b['strands'][:3]
            for s in sts:
                if n_cards >= budget or (lod == 1 and buf.tris() > 7700): break
                pts = _path(s['o'], b['out'], s['reach'], s['L'], segL if lod else rng.uniform(*G['seg'])); m = len(pts) - 1
                n = Vector((math.cos(s['face']), math.sin(s['face']), 0.)); sl = int(rng.random() < .4)
                for k in range(m):
                    p0, p1 = pts[k], pts[k + 1]; c = (p0 + p1) * .5; up = p0 - p1; size = up.length * 1.12
                    if c.z < .35: continue
                    light = _light(c, ax, crR, H) + rng.normal(0, .045); tone = int(min(NT - 1, max(0, round(light * (NT - 1)))))
                    rad = Vector((c.x - ax.x, c.y - ax.y, 0.)); rad = rad.normalized() if rad.length > 1e-3 else n
                    shade = (rad * .55 + Vector((0, 0, .1 + .6 * (light - .45))) + n * .15).normalized()
                    key = ('L', tone, sl); nn = n
                    if k == 0 and abs(up.normalized().z) < .75:     # the arc over the dome: card lies across it, seen from above
                        sd = Vector((-b['out'].y, b['out'].x, 0.)); nn = up.cross(sd).normalized()
                        if nn.z < 0: nn = -nn
                        nn = (nn + n * .25).normalized()
                    buf.card(c, nn, size, CELL_RECTS[key], up, (2, 2), 0., (lambda p, v=shade: v), .5 + .5 * (k + 1) / m, s['ph'] + .02 * k, aspect=CELL_ASPECT[key])
                    n_cards += 1
    globals()['last_extra_cards'] = n_cards
    return buf.tris() - t0
