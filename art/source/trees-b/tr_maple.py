"""TR04 Chinese maple (楓) in autumn, broadleaf engine tr_broad (golden-spirit-tree method: real wood, leaves on the twig tips).

8-9 m, D3 upstream and A3. Work pack: the red must be deep (dark ochre-red, rust red, never bright orange-red), the crown in several
layers, the twigs thin. Codex three-view TR04 cand-1 (chosen) and the user's maple sheet: a slim dark trunk running up as a leader,
thin limbs, and the leaves in flat tiers (each tier a few wide, flat-bottomed clusters, lit on top, dark and redder underneath, sky
between the tiers). Leaf: a deeply cut seven-lobed palm leaf on a long stalk, three to four per spray card.
A  8.6 m   straight leader, four tiers stepping in towards the top.
B  8.4 m   the user's sheet: trunk sweeping out in an S and back, tiers spreading wide on the lean side.
C  8.8 m   twisted trunk, narrower and taller, tiers offset round the leader like a stair.
Atlas: cell 0 = 4 x 4 single sprays (8 tones x 2 shapes); cell 1 top = four cluster cells (4 tones) for LOD1 / LOD2.
"""
import math
import numpy as np
from tr_tex import hexc, to_lin
from tr_broad import install, std_cells, blade, cluster_cells, _mix

# dark maroon under the tiers -> rust red -> dark ochre on the sunlit tops; no orange-red, no neon
PALETTE = [hexc(h) for h in ('#28151A', '#32181A', '#3E1D1D', '#4A2320', '#542923', '#5C2E25', '#643428', '#6B3A2C')]
# a third of the clusters are dark ochre instead (red and ochre bunches side by side, as in the chosen three-view); Unity lights these
# brighter and warmer than Blender, so both ramps stay dark and low in saturation
OCHRE = [hexc(h) for h in ('#2E1D16', '#3A2418', '#48301C', '#573B20', '#654625', '#71522B', '#7C5D32', '#87683A')]
CLUSTER_ALT = .34
STEM = hexc('#3B2A26')
NT = len(PALETTE)
CLUSTER_TONES = (1, 3, 4, 6)
CELL_RECTS, CELL_ASPECT = std_cells(NT, CLUSTER_TONES)
BARK = 'maple'
# maple bark: smooth, dark grey-brown, fine shallow fissures (same hand-painted source, darker and flatter)
BARK_PAINTED = dict(src='bark_src/elder_tree_bark_v1.png', sat=.32, gain=.78, tint=(.95, .9, .9), contrast=1.6, crack=.6, normal=10., smooth_val=.09, blur_n=(0, 2))
LOBE = [0., .42, .7, .88, 1., .96, .84, .66, .46, .26, .1, 0.]       # a long pointed lobe, widest a third of the way out


def IMPOSTOR_LEAFY(c):
    """red leaves (red well over green and blue) vs the grey-brown bark"""
    return (c[..., 0] > c[..., 1] * 1.25) & (c[..., 0] > c[..., 2] * 1.2) & (c[..., 0] > .08)


def palm(st, p, d, L, c0, c1, z):
    """A seven-lobed palm leaf from p along d (L = middle lobe): lobes fan out to +-80 deg, each folded on its own midrib."""
    d = np.array(d, np.float32); d /= np.linalg.norm(d) + 1e-9
    for i, (a, f) in enumerate(((-1.4, .45), (1.4, .45), (-.95, .72), (.95, .72), (-.48, .92), (.48, .92), (0., 1.))):
        ca, sa = math.cos(a), math.sin(a); ld = np.array((d[0] * ca - d[1] * sa, d[0] * sa + d[1] * ca))
        blade(st, p, ld, L * f, L * f * .3, c0, _mix(c0, c1, .5 + .5 * f), z + .0005 * i, prof=LOBE, fold=.06, shade=.8)


def spray(st, rng, base, d, L, tone, shape, z0=0.):
    """slot 0 red, slot 1 ochre. Form: a thin red-brown twig with three palm leaves on long stalks (left, right, tip), or a short
    twig ending in a fan of four leaves (the end of a tier)."""
    col = (OCHRE if shape == 1 else PALETTE)[tone]; c0, c1 = col * .82, np.clip(col * 1.14 + .01, 0, 1)
    shape = int(rng.random() < .45)        # the slot picks the colour ramp; the spray form is drawn at random
    d = np.array(d, np.float32); d /= np.linalg.norm(d) + 1e-9; side = np.array([-d[1], d[0]]); b0 = np.array(base[:2], np.float32)
    bend = rng.normal(0, .1)
    def at(s, Ls): return b0 + (d + side * bend * s) * Ls * s
    def leaf_on(q, a, stalk, size, k):
        ca, sa = math.cos(a), math.sin(a); ld = np.array((d[0] * ca - d[1] * sa, d[0] * sa + d[1] * ca))
        st.strip([tuple(q) + (z0 + .001,), tuple(q + ld * stalk) + (z0 + .001,)], [.004 * L, .003 * L], [tuple(to_lin(STEM * 1.2))] * 2, ridge=.3)
        palm(st, q + ld * stalk, ld, size, c0, c1, z0 + .003 + .003 * k)
    if shape == 0:
        Ls = L * .62
        st.strip([tuple(at(s, Ls)) + (z0,) for s in (0., .5, 1.)], [.012 * L, .009 * L, .006 * L], [tuple(to_lin(STEM))] * 3, ridge=.5)
        leaf_on(at(.45, Ls), .95 + rng.normal(0, .08), L * .12, L * .27, 0)
        leaf_on(at(.7, Ls), -.9 + rng.normal(0, .08), L * .12, L * .27, 1)
        leaf_on(at(1., Ls), rng.normal(0, .08), L * .06, L * .32, 2)
    else:
        Ls = L * .4
        st.strip([tuple(at(s, Ls)) + (z0,) for s in (0., .5, 1.)], [.012 * L, .009 * L, .006 * L], [tuple(to_lin(STEM))] * 3, ridge=.5)
        for k, a in enumerate((-1.05, 1.05, -.35, .35)):
            leaf_on(at(1., Ls), a + rng.normal(0, .06), L * .1, L * (.27 if abs(a) > .5 else .31), k)


def cell_leaves(st, rng, cell):
    S = cell / 4
    for t in range(NT):
        for s in range(2):
            k = t * 2 + s; cx = -cell / 2 + S * (k % 4 + .5); cy = cell / 2 - S * (k // 4 + .5)
            spray(st, rng, (cx, cy - .46 * S), (rng.normal(0, .04), 1.), S * .92, t, s)


def cell_clusters(st, rng, cell): cluster_cells(st, rng, cell, spray, CLUSTER_TONES, NT, spread=2.3)


CELLS = [cell_leaves, cell_clusters]


def tiers(seed, axis, levels):
    """Flat clusters in tiers: levels [(z, ring radius, count, cluster radius, azimuth offset deg)] round axis(z) -> [(x, y, z, r)]."""
    rng = np.random.default_rng(seed); out = []
    for (z, R, n, r, a0) in levels:
        ax, ay = axis(z)
        if n == 1: out.append((ax, ay, z, r)); continue
        for k in range(n):
            a = math.radians(a0) + 2 * math.pi * k / n + rng.normal(0, .18); rr = R * rng.uniform(.9, 1.15)
            out.append((ax + rr * math.cos(a), ay + rr * math.sin(a), z + rng.normal(0, .22), .87 * r * rng.uniform(.8, 1.15)))
    return out


GROW = dict(cards=5000, card_len=(.3, .45), leaf_len=(.44, .58), up_bias=.05, step=.24, d_inf=2.0, d_kill=.38, pipe=.5, r_tip=.009, top_r=.8,
            tip_back=.8, pull=.6, smooth=5, squash=.4, trop=(0., 0., .08), room={1: 2050, 2: 790}, csize={1: (.85, 1.05), 2: (1.05, 1.3)})
VARIANTS = {
    'A': dict(H=8.6, seed=71, r0=.24, twist=.03, zmin=2.3, leaves=1.,
              trunk=[(0, 0, -.03, 1.), (0, 0, 0, .95), (.04, .02, .1, .78), (.1, .04, .22, .68), (.08, .02, .32, .62), (.05, 0, .4, .56)],
              crown=(0., 0., 5.4, 3.6, 3.4, 3.2, .1), clumps=(0, (1., 1.), 70, .5),
              extra_clumps=tiers(71, lambda z: (.05, 0.), [(3.3, 2.4, 5, 1.55, 20), (4.6, 2.1, 4, 1.45, 65), (5.9, 1.7, 4, 1.3, 10), (7.1, .9, 3, 1.1, 90), (7.9, 0., 1, .85, 0)]),
              scaffolds=[(1., 0, 86, 2.6), (1., 30, 40, 1.4), (1., 210, 42, 1.4), (.8, 120, 30, 1.2)]),
    'B': dict(H=8.4, seed=83, r0=.26, twist=-.06, zmin=2.1, leaves=1.,
              trunk=[(0, 0, -.03, 1.), (0, 0, 0, .95), (.25, .05, .08, .8), (.75, .12, .18, .7), (1.05, .15, .28, .64), (.95, .1, .36, .58), (.7, .05, .44, .52)],
              crown=(1.2, .1, 5.1, 4.4, 3.4, 3.1, .12), clumps=(0, (1., 1.), 70, .5),
              extra_clumps=tiers(83, lambda z: (.9 + .25 * (z - 3.7), .05), [(3.1, 3.0, 5, 1.6, 0), (4.4, 2.5, 4, 1.5, 50), (5.7, 1.9, 4, 1.3, 15), (6.9, .9, 3, 1.05, 80)]),
              scaffolds=[(1., 15, 70, 2.4), (1., 350, 22, 2.2), (1., 170, 35, 1.5), (.85, 60, 30, 1.3)]),
    'C': dict(H=8.8, seed=97, r0=.23, twist=.12, zmin=2.6, leaves=1.,
              trunk=[(0, 0, -.03, 1.), (0, 0, 0, .95), (.12, -.08, .1, .78), (.05, -.2, .2, .68), (-.12, -.1, .3, .62), (-.05, .05, .42, .56)],
              crown=(-.1, .1, 5.9, 3.1, 2.9, 3.0, .1), clumps=(0, (1., 1.), 70, .5),
              extra_clumps=tiers(97, lambda z: (-.05 + .3 * math.sin(z), .05), [(3.6, 2.0, 4, 1.4, 0), (4.8, 1.9, 4, 1.35, 60), (6.0, 1.6, 3, 1.25, 120), (7.2, 1.1, 3, 1.05, 30), (8.1, 0., 1, .8, 0)]),
              scaffolds=[(1., 0, 85, 3.0), (1., 300, 38, 1.3), (.75, 140, 32, 1.2)]),
}
NAMES = {'A': 'Maple', 'B': 'Maple', 'C': 'Maple'}
ZH = {'A': '楓（直立主幹、四層葉團往上收）', 'B': '楓（主幹 S 形往一側掃出再回正、葉層往斜的那側展開）', 'C': '楓（扭幹、樹形較窄較高、葉層繞主幹錯開像階梯）'}

install(globals())
