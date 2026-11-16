"""TR03 v002 camphor (樟), 2026-11-14 work pack 「樹木重做 v2」, built 2026-11-15 from the chosen three-view
art/references/TR03/v002-r3/TR03-cand-2.png: a short thick trunk splitting into a few big climbing limbs, a wide thick crown with
holes and visible branch flow (never one ball), yellow-green new leaves on top. Built by tv2_grow; leaves are ovate, in loose
whorls near the shoot tips (leaf kind 'cluster').
A  ~15.8 m  broad dome (crown mode): thick trunk, three big limbs show under the open middle of the crown.
B  ~14.7 m  trunk leans, the crown heavier to one side.
C  ~15.0 m  the limbs leave higher, the most lobed crown edge.
"""
from tv2_grow import make

SP = 'TR03'
REFERENCE = 'art/references/TR03/v002-r3/TR03-cand-2.png（prompt.txt 同資料夾）'
PALETTE = ['#26402B', '#3A5A36', '#527741', '#6E9248', '#93B052', '#BFCB62']     # deep green inside -> yellow-green new growth
OCCL_LO = .5
LOD_CAP = {0: 120000, 1: 15000, 2: 4000}      # 2026-11-16 使用者同意放寬（原 LOD0 6 萬）
BARK_PAINTED = dict(src='bark_src/elder_tree_bark_v1.png', sat=.35, gain=1.25, tint=(.98, .93, .86), contrast=1.15, crack=.3, normal=10., smooth_val=.07, blur_n=(1, 3))
WOOD = {0: {0: (12, .4), 1: (6, 1.0), 2: (4, 1.6), 3: (3, 2.), 8: (5, .5), 9: (8, .3)},
        1: {0: (10, .7), 1: (6, .9), 2: (3, 1.4), 3: None, 8: (4, 1.), 9: (4, .5)},
        2: {0: (7, 1.4), 1: (4, 1.8), 2: None, 3: None, 8: None, 9: (3, 1.)}}
LEAF = {0: dict(L=(.56, .64), W=(.37, .42), shape=((-.18, .92), (.2, .74)), ax=(.2, .55, .75), per=(6, 9), cone=(.45, 1.5), widest=-.08, t0=.15),
        1: dict(L=(.75, .9), W=(.38, .46), per=(4, 5), cone=(.9, 1.45), widest=-.06, t0=.35),
        2: dict(L=(.95, 1.2), W=(.5, .62), per=(3, 4), cone=(.9, 1.45), widest=-.06, t0=.4)}
SPEC = dict(leaf_kind='cluster', mass_light=(.55, .5, .8), expo_k=1.8, t_lo=.25, up0=(.85, -.3), sag=.12, wiggle=.14, wiggle_up=.05, fork=.45, fork_s=(.25, .55), fork_len=.7, fork_r=.7, taper=(1.6, .18), limb_r=(.8, .55), sec=.45, sec_s0=.16, sec_ang=(.9, 1.4),
            sec_up=(.12, .42), sec_len=(.4, .58), sec_tip=.12, ntw=(5, 8), tw_up=(.2, .5), tw_len=(.45, .7), tw_tip=.15, leader=3)
LEAF_GEOMETRY = ('ovate leaves: seven-vertex solid leaves (6 outline points rounding the blade + a raised midrib, 6 triangles; rules relaxed 2026-11-16 with LOD0 up to 120,000), 0.56-0.64 m x 0.37-0.42 m at LOD0, 6-9 in a loose cluster opening up and outward round a point of a tip twig, from 15 % of the twig to the tip; LOD1 0.75-0.90 m five-vertex, 4-5 per whorl; LOD2 0.95-1.2 m, 3-4; LOD3 impostor')
CROWN = dict(n_att=5200, max_nodes=14000, clumps=(14, 2.4, .05), shell=1.0, core=.03, r_tip=.02, r_max=.3,     # crown mode (tv2_grow._colonize): twigs grow into a lobed dome from cand-2
             prof=[(0, .45), (.06, .74), (.14, .92), (.26, 1.), (.42, .98), (.6, .88), (.76, .7), (.88, .5), (.96, .28), (1, 0.)])
VARIANTS = {
    'A': dict(H=10.5, seed=503, r0=1.25, twist=.03, section=dict(rib=.14, lobes=5, root=.9, flare=.55, burls=[(2.2, .12, 0.)]),
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .95), (.05, .02, .12, .82), (.12, .03, .25, .72), (.1, .02, .3, .55), (0, 0, .46, .36),
                     (-.1, 0, .66, .27), (-.05, .02, .82, .18), (0, .02, .985, .06)],
              sil=[(.24, 195, 7.8, .34), (.27, 15, 7.4, .38), (.31, 105, 6.6, .46)],
              fill=dict(n=13, t0=.22, t1=.95, L0=6.4, L1=2.8, rise0=.15, rise1=.65), stubs=[(.18, 300)], crown=dict(z0=2.2, z1=15.2, bowl=4.0, rx=9.8, ry=7.0, cx=0., cy=0., lobes=.36, nseed=11, **CROWN), leaves=1.),
    'B': dict(H=10.0, seed=541, r0=1.2, twist=-.03, section=dict(rib=.14, lobes=5, root=.9, flare=.55, burls=[(1.9, .14, 1.4)]),
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .95), (.2, -.03, .12, .8), (.55, -.06, .25, .7), (.75, -.05, .34, .54), (.8, 0, .5, .36),
                     (.6, .03, .66, .26), (.45, .04, .82, .17), (.4, .04, .985, .06)],
              sil=[(.24, 10, 8.0, .32), (.28, 60, 6.4, .4), (.33, 230, 5.6, .46)],
              fill=dict(n=12, t0=.24, t1=.95, L0=6.0, L1=2.6, rise0=.15, rise1=.65), stubs=[(.16, 150), (.22, 260)], crown=dict(z0=2.1, z1=14.4, bowl=3.8, rx=8.9, ry=6.4, cx=.9, cy=-.2, lobes=.36, nseed=12, **CROWN), leaves=1.),
    'C': dict(H=9.8, seed=577, r0=1.2, twist=.04, section=dict(rib=.14, lobes=5, root=.9, flare=.55, burls=[(2.6, .12, 2.)]),
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .95), (-.05, .03, .12, .83), (-.15, .05, .27, .74), (-.12, .03, .38, .58), (0, 0, .52, .4),
                     (.12, 0, .68, .29), (.06, .02, .84, .19), (0, .02, .985, .06)],
              sil=[(.28, 165, 7.2, .36), (.32, 340, 6.8, .42), (.4, 80, 6.0, .5)],
              fill=dict(n=13, t0=.26, t1=.95, L0=6.2, L1=2.8, rise0=.15, rise1=.65), stubs=[(.2, 30)], crown=dict(z0=2.4, z1=14.8, bowl=4.2, rx=9.4, ry=7.0, cx=0., cy=0., lobes=.4, nseed=13, **CROWN), leaves=1.),
}
NAMES = {'A': 'Camphor', 'B': 'Camphor', 'C': 'Camphor'}
ZH = {'A': '樟（寬圓冠、三條大枝 3.5–4.5 m 分出）', 'B': '樟（幹斜、冠偏一側、另一側深洞）', 'C': '樟（較高、分枝較高、冠分兩團）'}

skeleton, wood, foliage = make(globals())
