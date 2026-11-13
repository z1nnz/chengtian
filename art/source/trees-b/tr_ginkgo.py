"""TR05 old ginkgo (銀杏) in autumn, broadleaf engine tr_broad (golden-spirit-tree method: real wood, leaves on the twig tips).

17-19 m, one landmark tree in A1 and a few in D3. Work pack: the gold must be old (dark gold, yellow-brown, never lemon yellow), the
tree tall and straight, the crown made of fan-shaped leaf clusters. Codex three-view TR05 cand-3 (chosen): a tall straight grey trunk
running up through the crown as a leader, limbs reaching up at 45-60 deg, a tall oval crown of separate gold clusters with sky and
limbs showing between them. Leaf: the two-lobed fan leaf on a long stalk, three to five in a rosette on a short spur shoot.
A  18 m    straight leader, six limbs spiralling up, tall oval crown.
B  17.4 m  the top leans a little, the crown pushed out to one side, fewer and longer limbs.
C  18.6 m  the old landmark: thicker flared trunk with burls, broader crown, a couple of broken stubs.
Atlas: cell 0 = 4 x 4 single sprays (8 tones x 2 slots); cell 1 top = four cluster cells (4 tones) for LOD1 / LOD2.
"""
import math
import numpy as np
from tr_tex import hexc, to_lin
from tr_broad import install, std_cells, blade, cluster_cells, _mix

# dark olive-brown in the shade -> old gold on the sunlit tops; no lemon yellow. Unity lights these brighter and warmer than Blender,
# so the ramp stays dark and low in saturation (judge colour from the Unity shots)
PALETTE = [hexc(h) for h in ('#2E2317', '#3A2C19', '#48371C', '#55411F', '#614B22', '#6C5426', '#765D2A', '#7E652F')]
# a quarter of the clusters a browner, older gold (late leaves)
BROWN = [hexc(h) for h in ('#2C2016', '#362717', '#43301A', '#4F391D', '#5A4120', '#634924', '#6B5029', '#72572E')]
CLUSTER_ALT = .26
STEM = hexc('#4A4032')
NT = len(PALETTE)
CLUSTER_TONES = (1, 3, 4, 6)
CELL_RECTS, CELL_ASPECT = std_cells(NT, CLUSTER_TONES)
BARK = 'ginkgo'
# ginkgo bark: grey, deep long vertical furrows (same hand-painted source, cooled to grey)
BARK_PAINTED = dict(src='bark_src/elder_tree_bark_v1.png', sat=.22, gain=.95, tint=(.92, .92, .9), contrast=2.0, crack=1., normal=16., smooth_val=.07, blur_n=(0, 2))
# half a fan leaf: narrow at the stalk, widening to a broad, slightly wavy outer edge that rounds off fast
WEDGE = [0., .1, .18, .26, .34, .43, .52, .61, .7, .79, .87, .94, .99, 1., .9, 0.]


def IMPOSTOR_LEAFY(c):
    """gold leaves (red and green well over blue) vs the grey bark"""
    return (c[..., 0] > c[..., 2] * 1.35) & (c[..., 1] > c[..., 2] * 1.15) & (c[..., 0] > .08)


def fan(st, p, d, L, c0, c1, z):
    """A ginkgo fan leaf from p along d: two half-fans splayed +-0.36 rad leave the notch in the middle of the outer edge."""
    d = np.array(d, np.float32); d /= np.linalg.norm(d) + 1e-9
    for i, a in enumerate((-.36, .36)):
        ca, sa = math.cos(a), math.sin(a); ld = np.array((d[0] * ca - d[1] * sa, d[0] * sa + d[1] * ca))
        blade(st, p, ld, L, L * .5, c0, c1, z + .0005 * i, prof=WEDGE, fold=.03, shade=.84)


def spray(st, rng, base, d, L, tone, shape, z0=0.):
    """slot 0 gold, slot 1 browner gold. Form: a twig with three short spurs, each a rosette of fan leaves, or one spur rosette of
    five leaves at the end of a short twig."""
    col = (BROWN if shape == 1 else PALETTE)[tone]; c0, c1 = col * .8, np.clip(col * 1.15 + .01, 0, 1)
    shape = int(rng.random() < .4)
    d = np.array(d, np.float32); d /= np.linalg.norm(d) + 1e-9; side = np.array([-d[1], d[0]]); b0 = np.array(base[:2], np.float32)
    bend = rng.normal(0, .1)
    def at(s, Ls): return b0 + (d + side * bend * s) * Ls * s
    def rosette(q, angles, size, k0):
        for k, a in enumerate(angles):
            a += rng.normal(0, .07); ca, sa = math.cos(a), math.sin(a); ld = np.array((d[0] * ca - d[1] * sa, d[0] * sa + d[1] * ca))
            stalk = size * .55
            st.strip([tuple(q) + (z0 + .001,), tuple(q + ld * stalk) + (z0 + .001,)], [.004 * L, .003 * L], [tuple(to_lin(STEM * 1.15))] * 2, ridge=.3)
            fan(st, q + ld * stalk, ld, size * rng.uniform(.9, 1.08), c0, c1, z0 + .003 + .002 * (k0 + k))
    if shape == 0:
        Ls = L * .62
        st.strip([tuple(at(s, Ls)) + (z0,) for s in (0., .5, 1.)], [.014 * L, .01 * L, .007 * L], [tuple(to_lin(STEM))] * 3, ridge=.5)
        rosette(at(.4, Ls), (1.15, .55), L * .2, 0)
        rosette(at(.7, Ls), (-1.1, -.5), L * .2, 2)
        rosette(at(1., Ls), (-.4, 0., .45), L * .23, 4)
    else:
        Ls = L * .38
        st.strip([tuple(at(s, Ls)) + (z0,) for s in (0., .5, 1.)], [.014 * L, .01 * L, .007 * L], [tuple(to_lin(STEM))] * 3, ridge=.5)
        rosette(at(1., Ls), (-1.15, 1.15, -.55, .55, 0.), L * .27, 0)


def cell_leaves(st, rng, cell):
    S = cell / 4
    for t in range(NT):
        for s in range(2):
            k = t * 2 + s; cx = -cell / 2 + S * (k % 4 + .5); cy = cell / 2 - S * (k // 4 + .5)
            spray(st, rng, (cx, cy - .46 * S), (rng.normal(0, .04), 1.), S * .92, t, s)


def cell_clusters(st, rng, cell): cluster_cells(st, rng, cell, spray, CLUSTER_TONES, NT, spread=2.2)


CELLS = [cell_leaves, cell_clusters]

GROW = dict(cards=7400, card_len=(.55, .85), leaf_len=(.6, .8), up_bias=.25, step=.32, d_inf=2.6, d_kill=.5, pipe=.5, r_tip=.011, tip_back=1.2,
            pull=.55, smooth=6, squash=.7, trop=(0., 0., .2), room={1: 2050, 2: 790}, csize={1: (1.05, 1.3), 2: (1.35, 1.7)})
VARIANTS = {
    'A': dict(H=18., seed=113, r0=.56, twist=.03, zmin=5.0, leaves=1.,
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .95), (0, 0, .06, .76), (.03, .01, .2, .64), (.04, 0, .4, .55), (.03, -.01, .62, .46)],
              burls=[(1.4, 1.2, .3)],
              crown=(0., 0., 11.6, 5.0, 4.8, 6.4, .12), clumps=(22, (1.7, 2.3), 120, .25),
              scaffolds=[(1., 0, 88, 3.0), (.5, 20, 48, 3.0), (.58, 145, 46, 3.2), (.66, 255, 50, 2.9), (.76, 75, 54, 2.6), (.85, 320, 57, 2.4), (.93, 195, 60, 2.2)]),
    'B': dict(H=17.4, seed=127, r0=.54, twist=-.04, zmin=5.4, leaves=1.,
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .95), (.02, 0, .06, .76), (.06, .02, .2, .64), (.14, .04, .4, .55), (.3, .06, .6, .46)],
              burls=[(2.2, 2.0, .3)],
              crown=(1.0, .1, 11.2, 5.6, 4.6, 6.0, .14), clumps=(20, (1.7, 2.3), 120, .25),
              scaffolds=[(1., 10, 82, 2.8), (.55, 0, 44, 3.6), (.64, 160, 50, 2.8), (.74, 270, 52, 2.8), (.86, 60, 56, 2.6), (.95, 220, 62, 2.0)],
              stubs=[(.35, 120)]),
    'C': dict(H=18.1, seed=139, r0=.7, twist=.06, zmin=4.6, leaves=1.05,
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .95), (.04, -.02, .05, .78), (.05, -.04, .18, .66), (.02, -.03, .38, .57), (0, 0, .6, .47)],
              burls=[(.8, 1.0, .45), (3.0, 2.3, .4), (5.2, 1.4, .3)],
              crown=(0., -.1, 10.9, 6.2, 5.8, 6.2, .15), clumps=(25, (1.8, 2.4), 115, .25),
              scaffolds=[(1., 0, 86, 3.2), (.45, 40, 42, 3.6), (.52, 200, 40, 3.8), (.62, 300, 48, 3.2), (.72, 120, 50, 3.0), (.83, 10, 56, 2.6), (.92, 240, 60, 2.4)],
              stubs=[(.3, 260), (.42, 90)]),
}
NAMES = {'A': 'Ginkgo', 'B': 'Ginkgo', 'C': 'OldGinkgo'}
ZH = {'A': '銀杏（直立主幹穿過樹冠、六根大枝螺旋向上、高橢圓樹冠）', 'B': '銀杏（樹頂微斜、樹冠偏向一側、大枝較少較長）', 'C': '老銀杏（地標樹：樹幹較粗、基部外擴、樹瘤、樹冠較寬、兩處斷枝）'}

install(globals())
