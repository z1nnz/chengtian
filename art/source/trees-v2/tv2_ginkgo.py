"""TR05 v002 ginkgo (銀杏), 2026-11-14 work pack 「樹木重做 v2」, built 2026-11-15 from the chosen three-view
art/references/TR05/v002-r3/TR05-cand-4.png: tall and straight, a single trunk to the top, short climbing limbs, a narrow cone of
crown; fan leaves on short spur shoots; old gold (dark gold, yellow-brown), not bright. Built by tv2_grow (leaf kind 'fan').
A  15.1 m  straight, crown from 2.2 m, even pointed cone (crown mode).
B  13.6 m  broader below, the crown leaning right.
C  15.9 m  the most slender, the trunk bends a little near the top.
"""
from tv2_grow import make

SP = 'TR05'
REFERENCE = 'art/references/TR05/v002-r3/TR05-cand-4.png（prompt.txt 同資料夾）'
PALETTE = ['#6B5424', '#93702A', '#B88A30', '#D19E38', '#E0B244', '#EDC966']     # old gold: brown-gold inside -> dull gold outside
OCCL_LO = .72
LOD_CAP = {0: 120000, 1: 15000, 2: 4000}      # 2026-11-16 使用者同意放寬（原 LOD0 6 萬）
BARK_PAINTED = dict(src='bark_src/elder_tree_bark_v1.png', sat=.3, gain=1.25, tint=(1.0, .94, .88), contrast=1.2, crack=.35, normal=10., smooth_val=.07, blur_n=(1, 3))
WOOD = {0: {0: (14, .3), 1: (6, .7), 2: (5, .9), 3: (3, 2.), 8: (5, .5), 9: (8, .3)},
        1: {0: (9, .8), 1: (5, 1.), 2: (3, 1.4), 3: None, 8: (4, 1.), 9: (4, .5)},
        2: {0: (6, 1.6), 1: (4, 2.), 2: None, 3: None, 8: None, 9: (3, 1.)}}
LEAF = {0: dict(L=(.2, .24), aspect=(.95, 1.2), shape=((-.12, .5), (.32, 1.)), tip=.38, per=(3, 5), cone=(.8, 1.7), widest=.3, rib=.15, t0=.1),
        1: dict(L=(.4, .5), aspect=(.9, 1.15), per=(3, 4), cone=(.6, 1.35), widest=.3, rib=.15, t0=.25),
        2: dict(L=(.75, .95), aspect=(.9, 1.15), per=(2, 3), cone=(.6, 1.35), widest=.3, rib=.15, t0=.3)}
SPEC = dict(leaf_kind='fan', mass_light=(.45, .4), t_lo=.15, up0=(.8, .2), sag=.02, wiggle=.06, taper=(1.4, .2), limb_r=(.45, .38), sec=.42, sec_s0=.12, sec_ang=(.6, 1.1),
            sec_up=(.3, .6), sec_len=(.35, .55), sec_tip=.15, ntw=(7, 10), tw_up=(.2, .5), tw_len=(.45, .75), tw_tip=.15, leader=4)
LEAF_GEOMETRY = ('fan leaves: seven-vertex solid leaves (6 outline points: narrow stalk end, widest near the tip, truncated tip edge + a raised midrib, 6 triangles; rules relaxed 2026-11-16 with LOD0 up to 120,000), 0.20-0.24 m long, about as wide, at LOD0 (0.65 x the leaf budget, so the branches show); 3-5 on a short spur shoot along each tip twig from 10 % of its length; LOD1 0.40-0.50 m five-vertex, 3-4 per spur; LOD2 0.75-0.95 m, 2-3; LOD3 impostor')
CROWN = dict(clumps=(30, 1.2, .12), shell=1.6, core=.35, bowl=.4, lobes=.3, step=.35, di=1.8, dk=.5, trop=.3, r_tip=.012, r_max=.14, trunk_seed=.2,    # crown mode (tv2_grow._colonize): an even cone from cand-4
             prof=[(0, .55), (.1, .85), (.24, 1.), (.42, .88), (.6, .68), (.78, .45), (.92, .2), (1, 0.)])
VARIANTS = {
    'A': dict(H=13.6, seed=601, r0=.55, twist=.02, section=dict(rib=.1, lobes=5, root=.7, flare=.45, burls=[(3.0, .08, 0.)]),
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .95), (.02, .01, .12, .82), (.05, .02, .26, .72), (.04, .01, .4, .62), (0, 0, .55, .52),
                     (-.03, 0, .7, .4), (-.02, .01, .85, .26), (0, .01, .985, .08)],
              sil=[(.18, 200, 3.3, .42), (.26, 30, 3.1, .44), (.4, 120, 2.7, .46)],
              fill=dict(n=25, t0=.18, t1=.96, L0=3.3, L1=.9, rise0=.5, rise1=.3), stubs=[(.1, 70), (.14, 250)], crown=dict(z0=2.2, z1=15.4, rx=3.6, ry=3.4, nseed=21, **CROWN), leaves=.65),
    'B': dict(H=12.3, seed=631, r0=.55, twist=-.02, section=dict(rib=.1, lobes=5, root=.7, flare=.45, burls=[(2.4, .1, 1.)]),
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .95), (-.04, .02, .12, .82), (-.08, .03, .26, .72), (-.06, .02, .4, .62), (0, 0, .55, .52),
                     (.05, -.01, .7, .4), (.04, 0, .85, .26), (0, .01, .985, .08)],
              sil=[(.21, 10, 4.6, .26), (.24, 190, 3.6, .38), (.36, 280, 3.0, .42)],
              fill=dict(n=23, t0=.19, t1=.96, L0=3.7, L1=1.0, rise0=.48, rise1=.3), stubs=[(.12, 120)], crown=dict(z0=2.2, z1=13.9, rx=3.9, ry=3.5, cx=.3, nseed=22, **CROWN), leaves=.65),
    'C': dict(H=14.6, seed=661, r0=.5, twist=.025, section=dict(rib=.1, lobes=5, root=.7, flare=.45, burls=[(3.4, .08, 2.)]),
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .95), (.02, .01, .12, .82), (.03, .02, .26, .72), (.02, .01, .4, .62), (.05, 0, .55, .52),
                     (.15, 0, .7, .4), (.3, .02, .85, .26), (.4, .03, .985, .08)],
              sil=[(.2, 160, 2.8, .44), (.28, 340, 2.7, .46), (.44, 70, 2.4, .48)],
              fill=dict(n=28, t0=.16, t1=.96, L0=3.0, L1=.8, rise0=.52, rise1=.3), stubs=[(.11, 200), (.16, 330)], crown=dict(z0=2.3, z1=16.4, rx=3.2, ry=3.1, cx=.15, nseed=23, **CROWN), leaves=.65),
}
NAMES = {'A': 'Ginkgo', 'B': 'Ginkgo', 'C': 'Ginkgo'}
ZH = {'A': '銀杏（直幹、2.5 m 起冠、勻稱錐形）', 'B': '銀杏（下冠較寬、右側一條低長枝）', 'C': '銀杏（最瘦高、近頂端微彎）'}

skeleton, wood, foliage = make(globals())
