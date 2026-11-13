"""TR07 plum blossom (梅), broadleaf engine tr_broad (golden-spirit-tree method: real wood, blossoms on the twig tips). Half budget.

6-8 m, A1 courtyards. Work pack: the trunk and limbs crooked and black-brown, the flowers small pale white clusters with a faint pink,
dotted along the twigs, never covering the tree. Codex three-view TR07 cand-1 (chosen), corrected away from bonsai: a slimmer, less
twisted trunk with a crooked lean, angular limbs that zig-zag up and out, long straight young shoots, and small blossom clusters
spaced along them with dark wood showing everywhere between. In flower (late winter): no leaf canopy, only an odd young leaf.
A  7.0 m   trunk leaning then turning back up, three angular limbs, a wide open crown.
B  6.6 m   old plum: leans hard, one burl and broken stubs, the crown thrown out to one side.
C  7.6 m   more upright, the trunk forking into two leads at about 2 m, a taller, narrower crown.
Atlas: cell 0 = 4 x 4 single blossom sprays (8 tones x 2 forms); cell 1 top = four cluster cells (4 tones) for LOD1 / LOD2.
"""
import math
import numpy as np
from tr_tex import hexc, to_lin
from tr_broad import install, std_cells, blade, cluster_cells, _mix

# petal ramp: shaded pinkish grey -> lit warm white with a faint pink; Unity lights these brighter, so the top stays below pure white
PALETTE = [hexc(h) for h in ('#9A8C8F', '#A29497', '#AB9D9F', '#B4A6A7', '#BDAFAF', '#C5B8B6', '#CDC0BD', '#D4C8C3')]
BUD = hexc('#8E4F58')          # closed buds: muted deep pink
STAMEN = hexc('#A08A55')
LEAF = hexc('#5E6B45')         # an odd young leaf, muted
STEM = hexc('#2B221D')         # black-brown twig
NT = len(PALETTE)
CLUSTER_TONES = (1, 3, 4, 6)
CELL_RECTS, CELL_ASPECT = std_cells(NT, CLUSTER_TONES)
BARK = 'plum'
# plum bark: black-brown, rough, flaking (the team's hand-painted source, darkened)
BARK_PAINTED = dict(src='bark_src/elder_tree_bark_v1.png', sat=.3, gain=.55, tint=(.92, .86, .84), contrast=2.2, crack=1., normal=18., smooth_val=.07, blur_n=(0, 2))
ROUND = [round(math.sin(math.pi * i / 11) ** .55, 4) for i in range(12)]       # a round petal
SHADE_UP = 1.1          # petals are thin and let light through: the shading normal leans up so shaded flowers stay pale
ATLAS_BLANK = 'mean'   # empty atlas area filled with the mean flower colour, so the small blossoms stay pale in the lower mips
SKIN_WOOD = {0: ((0, 1, 2, 3), 2, 6400), 1: ((0, 1, 2), 1, 2300), 2: ((0, 1), 1, 650)}


def IMPOSTOR_LEAFY(c):
    """pale blossoms vs the black-brown wood"""
    return (c[..., 0] > .22) & (c[..., 1] > .17)


def flower(st, p, r, col, z, rng, open_=1.):
    """five round petals round a stamen dot; open_ < 1 = half-open (smaller, petals closer)."""
    p = np.array(p, np.float32); a0 = rng.uniform(0, 2 * math.pi); r = r * open_
    c0, c1 = col * .86, np.clip(col * 1.08 + .01, 0, 1)
    for k in range(5):
        a = a0 + 2 * math.pi * k / 5; d = np.array((math.cos(a), math.sin(a)), np.float32)
        blade(st, p + d * r * .12, d, r, r * .42, _mix(c0, BUD, .18), c1, z + .0004 * k, prof=ROUND, fold=.02, shade=.9, rim=.0006, rim_col=.75)
    st.strip([tuple(p - np.array((r * .16, 0))) + (z + .004,), tuple(p + np.array((r * .16, 0))) + (z + .004,)], [r * .3, r * .3], [tuple(to_lin(STAMEN))] * 2, ridge=.2)


def bud(st, p, r, z):
    p = np.array(p, np.float32)
    st.strip([tuple(p - np.array((0, r * .5))) + (z,), tuple(p + np.array((0, r * .5))) + (z,)], [r * .7, r * .5], [tuple(to_lin(BUD))] * 2, ridge=.4)


def spray(st, rng, base, d, L, tone, shape, z0=0.):
    """A thin black-brown shoot with blossoms sitting close along it: shape 0 = a long straight shoot, three flowers and two buds
    spaced along it; shape 1 = a short spur with a tight cluster of three flowers and a bud (and now and then one young leaf)."""
    col = PALETTE[tone]
    d = np.array(d, np.float32); d /= np.linalg.norm(d) + 1e-9; side = np.array([-d[1], d[0]]); b0 = np.array(base[:2], np.float32)
    kink = rng.normal(0, .12)
    def at(s, Ls): return b0 + (d + side * kink * (s > .5) * (s - .5)) * Ls * s
    fr = L * .1
    if shape == 0:
        Ls = L * .95
        st.strip([tuple(at(s, Ls)) + (z0,) for s in (0., .35, .7, 1.)], [.022 * L, .018 * L, .013 * L, .008 * L], [tuple(to_lin(STEM))] * 4, ridge=.5)
        for k, s in enumerate((.3, .55, .8)):
            q = at(s, Ls) + side * fr * .55 * (1 if k % 2 else -1)
            flower(st, q, fr * rng.uniform(.9, 1.1), col, z0 + .01 + .006 * k, rng, open_=1. if k < 2 else .8)
        bud(st, at(.42, Ls) - side * fr * .4, fr * .38, z0 + .006); bud(st, at(.98, Ls), fr * .34, z0 + .006)
    else:
        Ls = L * .5
        st.strip([tuple(at(s, Ls)) + (z0,) for s in (0., .5, 1.)], [.022 * L, .016 * L, .011 * L], [tuple(to_lin(STEM))] * 3, ridge=.5)
        top = at(1., Ls)
        if rng.random() < .35:
            blade(st, at(.6, Ls), (d + side * .8) / np.linalg.norm(d + side * .8), L * .2, L * .2 * .3, LEAF * .85, LEAF * 1.1, z0 + .003)
        for k, (dx, dy) in enumerate(((-.9, .1), (.85, .35), (0., 1.05))):
            flower(st, top + side * fr * dx + d * fr * dy, fr * rng.uniform(.9, 1.1), col, z0 + .01 + .006 * k, rng)
        bud(st, top + d * fr * 2.1 + side * fr * .3, fr * .36, z0 + .006)


def cell_leaves(st, rng, cell):
    S = cell / 4
    for t in range(NT):
        for s in range(2):
            k = t * 2 + s; cx = -cell / 2 + S * (k % 4 + .5); cy = cell / 2 - S * (k // 4 + .5)
            spray(st, rng, (cx, cy - .46 * S), (rng.normal(0, .04), 1.), S * .92, t, s)


def cell_clusters(st, rng, cell): cluster_cells(st, rng, cell, spray, CLUSTER_TONES, NT, spread=2.4, n=6)


CELLS = [cell_leaves, cell_clusters]

GROW = dict(cards=1900, card_len=(.25, .4), leaf_len=(.32, .44), up_bias=.35, step=.26, d_inf=2.0, d_kill=.42, pipe=.55, r_tip=.007, top_r=.8,
            tip_back=1.0, pull=0., smooth=4, squash=.8, trop=(0., 0., .12), room={1: 640, 2: 225}, csize={1: (.7, .9), 2: (.9, 1.15)})
VARIANTS = {
    'A': dict(H=7.0, seed=191, r0=.24, twist=.1, zmin=2.6, leaves=1.,
              trunk=[(0, 0, -.04, 1.), (0, 0, 0, .95), (.12, .02, .08, .8), (.42, .08, .18, .7), (.55, .05, .28, .64), (.4, -.02, .36, .58)],
              burls=[(.9, 1.2, .3)],
              crown=(.4, 0., 4.5, 3.4, 3.1, 2.3, .18), clumps=(10, (1.0, 1.4), 70, .3),
              scaffolds=[(1., 20, 48, 1.8), (1., 160, 40, 2.0), (1., 270, 55, 1.6), (.8, 90, 35, 1.4)],
              stubs=[(.55, 330)]),
    'B': dict(H=6.6, seed=203, r0=.27, twist=-.14, zmin=2.2, leaves=1.,
              trunk=[(0, 0, -.04, 1.), (0, 0, 0, .95), (.25, 0, .07, .82), (.75, .1, .15, .72), (1.15, .15, .26, .64), (1.25, .1, .36, .57)],
              burls=[(1.7, 1.0, .45), (.5, .9, .3)],
              crown=(1.8, .2, 4.0, 3.6, 2.8, 2.2, .2), clumps=(9, (1.0, 1.4), 70, .3),
              scaffolds=[(1., 0, 38, 2.2), (1., 120, 50, 1.6), (1., 230, 52, 1.5), (1., 60, 30, 1.4)],
              stubs=[(.45, 200), (.62, 300)]),
    'C': dict(H=7.6, seed=217, r0=.23, twist=.12, zmin=2.6, leaves=1.,
              trunk=[(0, 0, -.04, 1.), (0, 0, 0, .95), (.1, -.04, .07, .8), (.34, -.14, .14, .72), (.12, -.06, .21, .67), (.28, .04, .29, .62)],
              burls=[(1.1, 1.0, .3)],
              crown=(.1, -.1, 4.5, 2.9, 2.7, 2.3, .18), clumps=(10, (1.0, 1.3), 70, .3),
              scaffolds=[(1., 40, 70, 2.2), (1., 210, 64, 2.2), (1., 300, 42, 1.4), (.85, 130, 38, 1.3)],
              stubs=[(.5, 80)]),
}
NAMES = {'A': 'Plum', 'B': 'OldPlum', 'C': 'Plum'}
ZH = {'A': '梅（主幹先斜再轉回向上、三根有轉折的大枝、樹冠開展）', 'B': '老梅（大幅斜出、樹瘤與斷枝、樹冠偏向一側）', 'C': '梅（較直立、約 2 m 分成兩股主枝、樹冠較高較窄）'}

install(globals())
