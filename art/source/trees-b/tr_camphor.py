"""TR03 village camphor (樟), broadleaf engine tr_broad (golden-spirit-tree method: real wood, leaves on the twig tips, no clouds).

The village's big tree (A1 village centre, courtyards), 14-16 m: a stout grey-brown trunk that splits low into a few big limbs,
the limbs forking again and again; a very wide, thick, rounded crown made of big overlapping clusters of glossy sage-green leaves,
deep shade underneath (it has to shade a small square). Leaves: camphor's ovate, pointed, glossy leaves, crowded towards the shoot
tips; one leaf spray per card (stem with 6-7 alternate leaves, or a tip rosette of 5). Colour from the work pack and the user's
ref-45 (hand-painted old broadleaf): sunlit tops warm sage / yellow-green, shade blue-teal, never neon.
A  15 m    slightly S-curved trunk, four big limbs from about 4 m, a broad round dome.
B  15 m    trunk leaning one way, three limbs, the crown pushed out over the lean, one big burl.
C  14.6 m  old camphor: splits into two thick stems at about 3 m, very wide low dome, burls and broken stubs.
Atlas: cell 0 = 4 x 4 single sprays (8 tones x 2 shapes); cell 1 top = four cluster cells (4 tones) for LOD1 / LOD2.
"""
import math
import numpy as np
from tr_tex import hexc, to_lin
from tr_broad import install, std_cells, blade, cluster_cells, OVATE, _mix

PALETTE = [hexc(h) for h in ('#1F3B3C', '#244440', '#2C4F45', '#355A48', '#43664B', '#54734E', '#688252', '#7E9157')]
STEM = hexc('#4A3F30')
NT = len(PALETTE)
CLUSTER_TONES = (1, 3, 4, 6)
CELL_RECTS, CELL_ASPECT = std_cells(NT, CLUSTER_TONES)
BARK = 'camphor'
# the team's hand-painted bark, cooled to camphor's grey-brown with fine long furrows
BARK_PAINTED = dict(src='bark_src/elder_tree_bark_v1.png', sat=.42, gain=1.0, tint=(.93, .9, .86), contrast=2.0, crack=1., normal=16., smooth_val=.07, blur_n=(0, 2))


def spray(st, rng, base, d, L, tone, shape, z0=0.):
    """shape 0: a shoot with alternate leaves on short stalks, shrinking to a tip leaf; shape 1: a short shoot ending in a rosette
    of five leaves (camphor leaves crowd at the shoot tips)."""
    col = PALETTE[tone]; c0, c1 = col * .8, np.clip(col * 1.16 + .012, 0, 1)
    d = np.array(d, np.float32); d /= np.linalg.norm(d) + 1e-9; side = np.array([-d[1], d[0]]); b0 = np.array(base[:2], np.float32)
    bend = rng.normal(0, .12)
    def at(s, Ls): return b0 + (d + side * bend * s) * Ls * s
    if shape == 0:
        Ls = L * .9
        st.strip([tuple(at(s, Ls)) + (z0,) for s in (0., .35, .7, .92)], [.018 * L, .014 * L, .01 * L, .006 * L], [tuple(to_lin(STEM))] * 4, ridge=.5)
        n = 6; sg = 1 if rng.random() < .5 else -1
        for i in range(n):
            s = .2 + .68 * i / (n - 1); q = at(s, Ls); sg = -sg
            a = sg * rng.uniform(.6, .9); ca, sa = math.cos(a), math.sin(a)
            ld = np.array((d[0] * ca - d[1] * sa, d[0] * sa + d[1] * ca)); ll = L * .4 * (1 - .3 * s) * rng.uniform(.92, 1.08)
            st.strip([tuple(q) + (z0 + .001,), tuple(q + ld * ll * .14) + (z0 + .001,)], [.005 * L, .004 * L], [tuple(to_lin(STEM * 1.1))] * 2, ridge=.3)
            blade(st, q + ld * ll * .12, ld, ll, ll * .4, c0, _mix(c0, c1, .55 + .45 * s), z=z0 + .003 + .0015 * i)
        blade(st, at(.9, Ls), d, L * .3, L * .3 * .4, c0, c1, z=z0 + .015)
    else:
        Ls = L * .45
        st.strip([tuple(at(s, Ls)) + (z0,) for s in (0., .5, 1.)], [.018 * L, .014 * L, .01 * L], [tuple(to_lin(STEM))] * 3, ridge=.5)
        top = at(1., Ls)
        for i, a in enumerate((-1.25, 1.2, -.62, .6, 0.)):
            a += rng.normal(0, .08); ca, sa = math.cos(a), math.sin(a)
            ld = np.array((d[0] * ca - d[1] * sa, d[0] * sa + d[1] * ca)); ll = L * (.42 if abs(a) > 1 else .5 if abs(a) > .3 else .54) * rng.uniform(.93, 1.07)
            blade(st, top + ld * L * .03, ld, ll, ll * .4, c0, _mix(c0, c1, .6 + .3 * (1 - abs(a))), z=z0 + .004 + .002 * i)
        for sg in (-1, 1):                                  # two older leaves lower on the shoot
            q = at(.35, Ls); a = sg * 1.0; ca, sa = math.cos(a), math.sin(a)
            ld = np.array((d[0] * ca - d[1] * sa, d[0] * sa + d[1] * ca)); ll = L * .34
            blade(st, q, ld, ll, ll * .4, c0 * .95, _mix(c0, c1, .45), z=z0 + .002)


def cell_leaves(st, rng, cell):
    S = cell / 4
    for t in range(NT):
        for s in range(2):
            k = t * 2 + s; cx = -cell / 2 + S * (k % 4 + .5); cy = cell / 2 - S * (k // 4 + .5)
            spray(st, rng, (cx, cy - .46 * S), (rng.normal(0, .04), 1.), S * .92, t, s)


def cell_clusters(st, rng, cell): cluster_cells(st, rng, cell, spray, CLUSTER_TONES, NT)


CELLS = [cell_leaves, cell_clusters]

GROW = dict(cards=6600, card_len=(.5, .8), leaf_len=(.66, .86), up_bias=.2, step=.32, d_inf=2.6, d_kill=.5, pipe=.34, r_tip=.016, tip_back=1.5, pull=.45, smooth=6, room={1: 2050, 2: 790}, csize={1: (1.15, 1.4), 2: (1.45, 1.8)})
VARIANTS = {
    'A': dict(H=15., seed=41, r0=.74, twist=.04, zmin=3.6, leaves=1.,
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .95), (.12, .05, .07, .78), (.32, .1, .15, .7), (.36, .06, .22, .66), (.3, 0, .28, .62)],
              burls=[(1.2, 1.4, .35), (4.0, 2.6, .3)],
              crown=(.3, 0., 9.0, 7.6, 7.2, 4.9, .12), clumps=(25, (1.5, 2.0), 115, .25),
              scaffolds=[(1., 15, 42, 2.6), (1., 105, 50, 2.4), (1., 200, 40, 2.8), (1., 290, 55, 2.2)],
              stubs=[(.55, 140)]),
    'B': dict(H=15., seed=53, r0=.72, twist=-.05, zmin=3.8, leaves=1.,
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .95), (.25, .05, .07, .78), (.75, .12, .15, .7), (1.2, .2, .23, .65), (1.55, .25, .3, .6)],
              burls=[(3.3, 1.9, .55)],
              crown=(2.4, .3, 9.6, 7.8, 6.6, 4.9, .14), clumps=(23, (1.5, 2.0), 115, .25),
              scaffolds=[(1., 10, 36, 3.0), (1., 135, 55, 2.2), (1., 250, 45, 2.6)],
              stubs=[(.5, 200), (.62, 60)]),
    'C': dict(H=14.6, seed=67, r0=.8, twist=.07, zmin=3.2, leaves=1.05,
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .95), (.1, -.08, .06, .8), (.2, -.12, .13, .74), (.18, -.1, .2, .7)],
              burls=[(.6, 1.0, .45), (2.6, 2.1, .5), (4.6, 1.5, .35)],
              crown=(0., -.2, 8.9, 8.4, 7.6, 4.7, .16), clumps=(27, (1.5, 2.1), 110, .25),
              scaffolds=[(1., 60, 44, 3.4), (1., 235, 38, 3.6), (1., 330, 30, 3.0), (1., 150, 34, 2.8)],
              stubs=[(.45, 20), (.62, 280), (.75, 120)]),
}
NAMES = {'A': 'Camphor', 'B': 'Camphor', 'C': 'OldCamphor'}
ZH = {'A': '樟（微 S 形主幹、四大枝、寬圓樹冠）', 'B': '樟（斜幹、三大枝、樹冠往斜的方向伸出、一個大樹瘤）', 'C': '老樟（3 m 分成兩股粗幹、樹冠最寬最低、樹瘤與斷枝）'}

install(globals())
