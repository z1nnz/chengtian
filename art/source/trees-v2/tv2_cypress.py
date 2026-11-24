"""TR02 v002 cypress (柏), 2026-11-14 work pack 「樹木重做 v2」, built 2026-11-15 from the chosen three-view
art/references/TR02/v002-r3/TR02-cand-3.png: a thick, twisted old trunk with burls and a dead snag, the crown narrowing upward,
dense dark fronds. Built by tv2_grow (the world-tree steps); leaves are flat scale-leaf fronds (leaf kind 'frond').
A  13.7 m  twisted trunk, crown from a quarter of the height, one dead snag on the left.
B  13.0 m  the trunk leans and turns back, a narrower crown, two snags.
C  12.3 m  squat and broad, the biggest burls, the crown wider at the bottom.
"""
from tv2_grow import make

SP = 'TR02'
REFERENCE = 'art/references/TR02/v002-r3/TR02-cand-3.png（prompt.txt 同資料夾）'
PALETTE = ['#2A3D36', '#365042', '#44634F', '#577A5E', '#70936E', '#90AC80']     # deep, slightly cold greens (old cypress)
OCCL_LO = .72
LOD_CAP = {0: 120000, 1: 15000, 2: 4000}      # 2026-11-16 使用者同意放寬（原 LOD0 6 萬）
BARK_PAINTED = dict(src='bark_src/elder_tree_bark_v1.png', sat=.25, gain=1.3, tint=(1.0, .95, .88), contrast=1.2, crack=.3, normal=6., smooth_val=.07, blur_n=(1, 3))
WOOD = {0: {0: (24, .25), 1: (6, .9), 2: (4, 1.2), 3: (3, 2.), 8: (5, .5), 9: (8, .3)},
        1: {0: (14, .7), 1: (5, 1.), 2: (3, 1.4), 3: None, 8: (4, 1.), 9: (4, .5)},
        2: {0: (7, 1.4), 1: (4, 2.), 2: None, 3: None, 8: None, 9: (3, 1.)}}
LEAF = {0: dict(L=(.44, .56), W=(.19, .24), per=(9, 12), spread=(.8, 1.3), widest=0., t0=.15, roll=.4, span=(.3, .55)),
        1: dict(L=(.8, 1.0), W=(.42, .52), per=(5, 6), spread=(.55, 1.1), widest=0., t0=.2),
        2: dict(L=(1.0, 1.3), W=(.55, .7), per=(3, 4), spread=(.55, 1.1), widest=0., t0=.25)}
SPEC = dict(leaf_kind='frond', mass_light=(.5, .45, .72), dead_r=.18, t_lo=.2, up0=(.95, .25), sag=.06, wiggle=.1, taper=(1.6, .2), limb_r=(.5, .42), sec=.42, sec_s0=.12, sec_ang=(.6, 1.1),
            sec_up=(.2, .55), sec_len=(.32, .48), sec_tip=.18, ntw=(4, 7), tw_up=(0., .3), tw_len=(.45, .7), tw_tip=.1, leader=8)
LEAF_GEOMETRY = ('flat scale-leaf sprays (feather mode): five-vertex solid leaves (4 outline points + a raised midrib, 4 triangles), 0.44-0.56 m x 0.19-0.24 m at LOD0 (LOD0 up to 120,000 from 2026-11-16, about 27,000 leaves), 9-12 per spray set alternately along a 0.3-0.55 m spray axis, shrinking and swinging forward toward the spray tip, the spray rolled about its axis and drooping, along each tip twig from 15 % of its length; LOD1 0.80-1.0 m, 5-6 per point (star frond); LOD2 1.0-1.3 m, 3-4; LOD3 impostor')
_SEC = dict(rib=.22, lobes=6, root=.6, flare=.5, strands=(4, .75, 8.))
CROWN = dict(n_att=4800, max_nodes=12000, clumps=(22, 1.3, .1), shell=1.3, core=.2, bowl=.8, lobes=.2, step=.35, di=1.8, dk=.5, trop=.22, r_tip=.014, r_max=.16, trunk_seed=.3,   # crown mode (tv2_grow._colonize): a tall pointed column from cand-3
             prof=[(0, .6), (.1, .9), (.25, 1.), (.45, .96), (.65, .82), (.82, .58), (.94, .3), (1, 0.)])
VARIANTS = {
    'A': dict(H=12.0, seed=401, r0=.8, twist=.11, section=dict(_SEC, burls=[(2.0, .65, 0.), (3.4, .48, 2.4), (1.2, .34, 4.1)]),
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .97), (.15, .05, .12, .86), (.3, .08, .26, .74), (.2, .04, .4, .64), (0, 0, .55, .6),
                     (-.12, -.02, .7, .5), (-.08, 0, .85, .34), (.02, .02, .985, .1)],
              sil=[(.3, 200, 2.6, .5), (.4, 25, 2.9, .48), (.52, 115, 2.7, .5)],
              fill=dict(n=19, t0=.22, t1=.95, L0=1.7, Lm=2.9, Lu=.38, L1=1.1, rise0=.4, rise1=.35), stubs=[(.16, 60), (.22, 290)],
              dead=[(.42, 160, 4.6, .35)], crown=dict(z0=2.2, z1=13.8, rx=3.3, ry=3.0, nseed=31, **CROWN), leaves=1.),
    'B': dict(H=11.0, seed=433, r0=.7, twist=-.12, section=dict(_SEC, burls=[(2.6, .58, 1.), (1.6, .42, 3.3)]),
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .96), (.25, -.05, .12, .84), (.6, -.1, .28, .72), (.7, -.08, .44, .6), (.5, -.02, .6, .56),
                     (.25, .03, .75, .46), (.15, .05, .88, .31), (.2, .05, .985, .09)],
              sil=[(.32, 20, 2.5, .5), (.44, 210, 2.5, .48), (.56, 290, 2.3, .5)],
              fill=dict(n=20, t0=.22, t1=.95, L0=1.5, Lm=2.5, Lu=.38, L1=.9, rise0=.4, rise1=.35), stubs=[(.18, 140)],
              dead=[(.4, 120, 4.2, .3), (.6, 300, 3.6, .35)], crown=dict(z0=2.2, z1=12.8, rx=2.8, ry=2.6, cx=.3, nseed=32, **CROWN), leaves=1.),
    'C': dict(H=10.0, seed=467, r0=.92, twist=.13, section=dict(_SEC, strands=(5, .8, 7.), burls=[(1.8, .7, .5), (2.9, .58, 2.9), (1.0, .4, 4.4)]),
              trunk=[(0, 0, -.02, 1.), (0, 0, 0, .97), (-.1, .04, .12, .87), (-.25, .06, .26, .76), (-.2, .02, .4, .66), (0, -.02, .55, .61),
                     (.15, 0, .7, .51), (.1, .02, .85, .35), (0, .03, .985, .11)],
              sil=[(.28, 170, 3.0, .45), (.36, 350, 3.2, .45), (.46, 80, 3.0, .48)],
              fill=dict(n=17, t0=.22, t1=.94, L0=1.9, Lm=3.2, Lu=.38, L1=1.2, rise0=.38, rise1=.33), stubs=[(.14, 220), (.2, 20), (.26, 120)],
              dead=[(.48, 250, 4.4, .35)], crown=dict(z0=2.2, z1=12.2, rx=3.2, ry=2.9, nseed=33, **CROWN), leaves=1.),
}
NAMES = {'A': 'Cypress', 'B': 'Cypress', 'C': 'Cypress'}
ZH = {'A': '柏（扭幹、冠往上收、左側一枝枯杈）', 'B': '柏（幹先斜再回、冠較窄、兩枝枯杈）', 'C': '柏（矮壯、樹瘤最大、下冠寬）'}

skeleton, wood, foliage = make(globals())
