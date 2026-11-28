"""VH04 street shop house (work pack 2026-11-28 B-150h, batch A): a shop on the road from the village entry to the square.

Concept: docs/execution/2026-11-28/images/A1_concept_2_entry.png (the shop on the right of the road, the main subject) and
A1_concept_1_overview.png. Three-view: art/references/VH04/ (AI, Codex image_gen; proportions from the work pack's written sizes).
Size limit 7 x 6 x 6.5 m. Origin: centre of the lot at ground level, front (the street) -Y.

One tall storey (wall plates at 3.6 m) with a storage loft under the roof, the ridge along the street so the long eave faces it.
The street front is open from post to post: four square posts (three bays) carry a heavy front beam, a strip of boards closes the gap
from the beam up to the roof boards. The removable shop-front boards (a groove in the beam above, a grooved timber sill below) are
taken down and stand leaning against the right gable by the front corner. Inside: a raised floor (one 0.3 m step on a stone edge),
a counter across the middle bay, a low display table in the left bay, four-tier shelves along the back wall and two-tier shelves
on the side walls, holding jars, baskets and cloth bolts; the loft floor joists show overhead. Under the front eave a faded canvas
awning runs out to a bamboo bar on two poles, sagging between them, a darker patch sewn on. Gables: lime plaster over a rubble
dado, corner posts and a middle rail square-on (no braces), a lattice window low and a small loft window high in each gable. Back:
plaster wall, a plank back door (closed), one lattice window.
Shared with VL01-05 and VH01-03: the material set (vl_mats 'elderly' palette, vh_wood timber), the VL roof tiles and their shared
1024 texture on the VH roof curve (vh_roof.py), the three-atlas scheme (Main, Stone, Wood) of the export pipeline.
"""
import math, random
import bmesh
from mathutils import Vector
from ti_core import S, box, cyl, mesh, torus, lathe, socket, xf, T, RZ, RX, RY
from cr_parts import rbox, sheet, rope, set_float, set_attr_list
import mk_mats as mm
import fr_parts as FP
import vl_mats
import vl_roof as RF
import vh_roof as VR
import vh_wood as vw
from vh_court import along, slab, window, door, plinth_rect, clay_jar, bamboo_basket, bamboo_tray, PROP_UVW

# ------------------------------------------------------------------ layout (metres, world; front -Y = the street)
WT = .3                                   # wall thickness
XW = 3.0                                  # side (gable) walls' outer faces
YF, YB = -1.35, 2.25                      # front post line (posts' street face), back wall outer face
YC = .45                                  # ridge line
PL, WTOP = .3, 3.6                        # floor (top of the plinth), top of the wall plates and of the front beam
POSTS = (-2.85, -.95, .95, 2.85)          # front posts' centres
PY = YF + .12                             # front posts' centre line
ROOF = dict(z0=3.5, rise=2.0, depth_front=2.8, depth_back=2.4, xh=3.1, lift_eave=.12, lift_end=.05)
LOFT = 3.47                               # top of the loft floor boards (on joists from the front beam to the back wall)
COUNTER = (-.85, .85, YF + .32, YF + .86, PL + .9)    # x0, x1, y0, y1, top
TABLE = (-2.6, -1.15, YF + .3, YF + .9, PL + .62)
AWN_X = (-2.65, 2.25)                      # awning width (x); poles under its outer corners
AWN_Y0, AWN_Z0 = YF - .06, 3.3           # where it is fixed under the front beam
AWN_Y1, AWN_Z1 = -2.85, 2.62              # its outer bar
BOARDS = (-2.98, -2.3)                    # the shop-front boards lean on the left corner post and the beam, feet out in the street

# wall specs: ((x, y), angle, length, openings (cx, w, sill, head, kind) in wall-local x, posts at ends (a, b))
YM = (YF + YB) / 2
WALLS = {
    'East': ((XW, YM), math.pi / 2, YB - YF, [(.35, .8, 1.35, 2.15, 'window')], (1, 1)),
    'West': ((-XW, YM), -math.pi / 2, YB - YF, [(-.35, .8, 1.35, 2.15, 'window')], (1, 1)),
    'Rear': ((0., YB), math.pi, 2 * XW - 2 * WT - .02, [(0., 1.0, PL, 2.3, 'door'), (-1.5, .6, 2.62, 3.12, 'window')], (0, 0)),
}


def palette():
    P = vl_mats.palette('elderly')
    vw.apply(P, 'elderly')                                   # weathered timber, plank doors (vh_wood.py)
    P['roof'] = RF.roof_material()
    cm = __import__('cr_mats')
    P['wall_stone'] = P['stone'] + [cm.stone('Dado_Stone_Warm', light=(.2, .19, .165), dark=(.085, .08, .07), ochre=(.24, .2, .14), moss=.8, lichen=.6, crack=.6)]
    P['floor'] = cm.packed_earth('Shop_Floor', dark=(.075, .06, .045), light=(.2, .155, .105), moss=0.)
    P['awning'] = cm.canvas('Awning_Canvas', base=(.5, .41, .26), stain=(.2, .14, .07), faded=.55, dirt=.7, seams=(.34, .67))
    P['patch'] = cm.canvas('Awning_Patch', base=(.33, .22, .14), stain=(.15, .09, .05), faded=.3, dirt=.5)
    P['weave_tray'] = mm.weave('Tray_Weave', (.38, .28, .14), (.1, .07, .036), reed=.012, block=.036, green_cast=.12, wobble=.006, strip_var=.42)
    P['weave_basket'] = mm.weave('Basket_Weave', (.3, .22, .11), (.11, .078, .04), reed=.016, block=.03, plain=True, green_cast=.04, wobble=.004)
    P['hoop'] = mm.bamboo('Split_Bamboo_Hoop', green=(.08, .078, .05), straw=(.27, .22, .13))
    P['pole'] = mm.bamboo('Bamboo_Pole', green=(.09, .085, .045), straw=(.3, .23, .12))
    P['twine'] = mm.hemp('Hemp_Twine', (.18, .13, .065), twist=220.0)
    P['bolt_indigo'] = mm.cloth('Cloth_Bolt_Indigo', (.05, .07, .12), dirt=.4, worn=.25)
    P['bolt_plain'] = mm.cloth('Cloth_Bolt_Undyed', (.42, .37, .28), dirt=.45, worn=.15)
    P['bolt_red'] = mm.cloth('Cloth_Bolt_Madder', (.26, .09, .06), dirt=.4, worn=.3)
    P['glaze_green'] = cm.clay('Clay_Celadon', body=(.2, .13, .08), glaze=(.13, .155, .12))
    tm = __import__('ti_mats')
    P['potato'] = tm.plain('Produce_Potato', (.3, .21, .11), rough=.8, noise=.35, scale=40.)
    P['chili'] = tm.plain('Produce_Dried_Chili', (.2, .035, .02), rough=.45, noise=.4, scale=60.)      # dark red, not bright (work pack YP08 note)
    P['greens'] = tm.plain('Produce_Greens', (.09, .17, .05), rough=.6, noise=.4, scale=25.)
    P['beans'] = tm.plain('Produce_Beans', (.2, .13, .06), rough=.55, noise=.5, scale=120.)
    return P


# ------------------------------------------------------------------ the roof in world coordinates (frame T(0, YC))
def under_world(wx, wy):
    return VR.under(wx, wy - YC)


def wframe(name):
    (wx, wy), a, L, ops, posts = WALLS[name]
    return T(wx, wy, 0) @ RZ(a), L, ops, posts


def walls(P, R):
    for wname in WALLS:
        M, L, ops, posts = wframe(wname)
        long_wall = any(posts)
        with xf(M):
            slab(f'Wall_{wname}', L - .02, ops, PL - .02, WTOP - .14, .0, WT, P['plaster'], P['plaster_in'])
            box(f'Wall_Plate_{wname}', (0., .1, WTOP - .07), (L + (.14 if long_wall else -.2), .26, .14), P['timber'], bevel=.012, seg=2, group='Wood', grain='x')
            box(f'Wall_Sill_Beam_{wname}', (0., -.06, PL + .05), (L - .02 - (.5 if long_wall else 0.), .08, .1), P['timber'], bevel=.01, seg=2, group='Wood', grain='x', uvw=.6)
            blocked = [(cx - w / 2 - .08, cx + w / 2 + .08) for cx, w, sill, head, kind in ops if kind.startswith('door')]
            z = PL; zs = []
            while z < PL + .68:
                h = R.uniform(.2, .27); zs.append((z, min(z + h, PL + .72))); z += h
            for c, (za, zb) in enumerate(zs):
                x = -L / 2 + .12 + (.16 if c % 2 else 0.) + (.18 if long_wall else 0.)
                while x < L / 2 - .14 - (.18 if long_wall else 0.):
                    Ls = min(R.uniform(.32, .62), L / 2 - .12 - x - (.18 if long_wall else 0.))
                    if Ls < .14: break
                    if not any(a < x + Ls / 2 < b for a, b in blocked):
                        rbox(f'Dado_Stone_{wname}', (x + Ls / 2, -.04, (za + zb) / 2), (Ls - .02, .12, zb - za - .02), R.choice(P['wall_stone']),
                             r=.025, amp=.008, freq=2.4, hew=2, chips=1, seed=int(x * 50 + c * 7 + len(wname)), div=.3, group='Stone')
                    x += Ls
            for end, on in zip((-1, 1), posts):
                if on:
                    box(f'Wall_Post_{wname}', (end * (L / 2 - .12), .095, (PL - .03 + WTOP) / 2), (.24, .45, WTOP - PL + .03), P['timber'], bevel=.014, seg=2, group='Wood', grain='z')
            for cx, w, sill, head, kind in ops:
                box(f'Lintel_{wname}', (cx, -.03, head + .06), (w + .3, .16, .16), P['timber'], bevel=.01, seg=2, group='Wood', grain='x')
                if kind == 'window': window(P, R, f'Window_{wname}_{cx:+.1f}', cx, sill, w, head - sill)
                else: door(P, cx, w, head, PL, ajar=False)
            if long_wall:
                box(f'Wall_Mid_Rail_{wname}', (0., -.02, WTOP - .45), (L - .24, .12, .1), P['timber'], bevel=.01, seg=2, group='Wood', grain='x')


def infill(P, name, p0, p1, z0, mat, n=16, inset=.08, t=.1):
    """Board or plaster infill from z0 up to the roof boards along the wall line p0 -> p1 (world), inset from its outer face (right of p0 -> p1)."""
    (ax, ay), (bx, by) = p0, p1
    L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L; nx, ny = uy, -ux
    V, F = [], []
    for q in range(n + 1):
        x, y = ax + (bx - ax) * q / n, ay + (by - ay) * q / n
        zt = under_world(x, y) + .005
        for s in (inset - t / 2, inset + t / 2):
            V.append((x - nx * s, y - ny * s, z0 - .01)); V.append((x - nx * s, y - ny * s, max(zt, z0 + .02)))
    for q in range(n):
        a = q * 4; b = a + 4
        F += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a + 1, b + 1, b + 3, a + 3), (a, a + 2, b + 2, b)]
    F += [(0, 1, 3, 2), (n * 4, n * 4 + 2, n * 4 + 3, n * 4 + 1)]
    o = mesh(name, V, F, mat, group='Wood' if mat is P['timber'] else 'Main', grain='x', uvw=.5)
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(o.data); bm.free()
    return o


def loft_window(P, name, x_face, y, z, w=.55, h=.42):
    """Small loft window in a gable: a frame proud of the plaster, plain bars, a dark recess behind (the loft is unlit)."""
    s = 1 if x_face > 0 else -1
    with xf(T(x_face, y, z) @ RZ(s * math.pi / 2)):
        box(name + '_Recess', (0., .06, 0.), (w, .08, h), P['mortar'], bevel=0., uvw=.2)
        for xx in (-w / 2 - .04, w / 2 + .04):
            box(name + '_Jamb', (xx, -.03, 0.), (.08, .1, h + .16), P['timber'], bevel=.008, seg=2, group='Wood', grain='z')
        for zz in (-h / 2 - .04, h / 2 + .04):
            box(name + '_Rail', (0., -.03, zz), (w + .16, .1, .08), P['timber'], bevel=.008, seg=2, group='Wood', grain='x')
        for j in range(1, 5):
            box(name + '_Bar', (-w / 2 + j * w / 5, -.02, 0.), (.025, .035, h), P['timber'], bevel=0., group='Wood', grain='z')


def roof_fill(P):
    """Plaster gables with a king post and a rake board; boards above the back wall plate; the front board strip over the beam."""
    infill(P, 'Gable_East', (XW, YF + .02), (XW, YB - .02), WTOP - .012, P['plaster'], n=24, t=.16, inset=.1)
    infill(P, 'Gable_West', (-XW, YB - .02), (-XW, YF + .02), WTOP - .012, P['plaster'], n=24, t=.16, inset=.1)
    infill(P, 'Eave_Infill_Rear', (XW - .06, YB), (-XW + .06, YB), WTOP, P['timber'], n=24)
    infill(P, 'Front_Board_Strip', (-XW + .02, PY), (XW - .02, PY), WTOP - .01, P['boards'], n=28, inset=0., t=.06)
    for x in (-XW - .07, XW + .07):
        zk = under_world(x, YC) - .1
        box('Gable_King_Post', (x, YC, (WTOP + zk) / 2), (.08, .16, zk - WTOP), P['timber'], bevel=.01, seg=2, group='Wood', grain='z')
        box('Gable_Collar', (x, YC, WTOP + .78), (.08, 2.4, .14), P['timber'], bevel=.01, seg=2, group='Wood', grain='y')
        RF.sweep_box('Gable_Rake', [(x, y, under_world(x, y) - .001) for y in [YF + (YB - YF) * j / 18 for j in range(19)]], .16, .14, P['timber'], group='Wood', grain='y')
        loft_window(P, f'Loft_Window_{"E" if x > 0 else "W"}', x - (.01 if x > 0 else -.01), YC, WTOP + 1.18)


# ------------------------------------------------------------------ the shop front: posts, beam, grooved sill, floor, edge stones
def front(P, R):
    for i, x in enumerate(POSTS):
        rbox('Post_Base_Stone', (x, PY, PL + .06), (.36, .36, .12), P['stone'][i % 2], r=.02, amp=.004, freq=3., hew=1, chips=1, seed=90 + i, div=.25, flat='zZ', group='Stone')
        box('Front_Post', (x, PY, (PL + .12 + WTOP - .25) / 2), (.24, .24, WTOP - .25 - PL - .12), P['timber'], bevel=.016, seg=2, group='Wood', grain='z')
    # heavy front beam over the posts with the board groove underneath (the shop boards slide up into it)
    box('Front_Beam', (0., PY, WTOP - .14), (2 * XW + .14, .28, .28), P['timber'], bevel=.016, seg=2, group='Wood', grain='x')
    box('Front_Beam_Groove_Lip', (0., PY - .095, WTOP - .3), (2 * XW - .2, .05, .06), P['timber'], bevel=.006, seg=1, group='Wood', grain='x', uvw=.6)
    box('Front_Beam_Groove_Lip', (0., PY + .095, WTOP - .3), (2 * XW - .2, .05, .06), P['timber'], bevel=.006, seg=1, group='Wood', grain='x', uvw=.6)
    # beam ends: short brackets (plain, square-cut) under the beam at each post
    for x in POSTS:
        for s in (-1, 1):
            if abs(x + s * .3) > XW - .05: continue
            box('Beam_Bracket', (x + s * .27, PY, WTOP - .36), (.3, .16, .12), P['timber'], bevel=.01, seg=2, group='Wood', grain='x')
    # grooved timber sill between the posts (worn in the middle of each bay)
    for a, b in zip(POSTS, POSTS[1:]):
        L = b - a - .24
        box('Front_Sill', ((a + b) / 2, PY, PL + .045), (L, .2, .09), P['plank'], bevel=.01, seg=2, group='Wood', grain='x')
    # floor: packed earth inside, a stone edge course to the street; a step stone in front of the right bay (the way in)
    box('Shop_Floor', (0., (YF + .3 + YB - WT) / 2, PL - .01), (2 * XW - 2 * WT, YB - WT - YF - .3, .02), P['floor'], bevel=0., uvw=.25)
    plinth_rect(P, R, 'Footing', -XW - .12, XW + .12, YF - .3, YB + .12, PL, 'FBLR')
    rbox('Step_Stone', ((POSTS[2] + POSTS[3]) / 2, YF - .48, PL / 4), (1.1, .36, PL / 2), P['stone'][0], r=.02, amp=.004, freq=3., hew=1, chips=1, seed=331, div=.25,
         flat='zZ', group='Stone')
    # loft: joists from the front beam to the back wall plate, boards on them (seen from the street as the shop's ceiling)
    for i in range(12):
        x = -XW + .45 + i * (2 * XW - .9) / 11
        box('Loft_Joist', (x, (PY + YB - WT) / 2, LOFT - .1), (.11, YB - WT - PY + .1, .14), P['timber'], bevel=.008, seg=1, group='Wood', grain='y', uvw=.5)
    box('Loft_Boards', (0., (PY + .15 + YB - WT) / 2, LOFT - .015), (2 * XW - 2 * WT - .02, YB - WT - PY - .15, .03), P['plank'], bevel=.003, seg=1, grain='x', uvw=.35, group='Wood')
    # a ladder up to the loft hatch at the left back corner
    lx, ly = -2.35, YB - WT - .32
    for s in (-1, 1):
        along('Ladder_Rail', (lx + s * .2, ly - .45, PL), (lx + s * .2, ly, LOFT - .05), .028, P['pole'], verts=8, group='Main', grain='z')
    for k in range(1, 9):
        t = k / 9; y = ly - .45 * (1 - t); zz = PL + (LOFT - .05 - PL) * t
        along('Ladder_Rung', (lx - .2, y, zz), (lx + .2, y, zz), .017, P['pole'], verts=6, group='Main', grain='x', detail=1)


def shop_boards(P, R):
    """The removable shop-front boards, taken down and stood on end in a row against the left corner post and the front beam, feet
    out in the street (as in the three-quarter reference); battens on every third board."""
    n = 5; x0, x1 = BOARDS
    for i in range(n):
        x = x0 + (x1 - x0) * (i + .5) / n + R.uniform(-.01, .01)
        h = 2.62 + R.uniform(-.03, .02); foot = .4 + R.uniform(-.03, .05)
        top = Vector((x + R.uniform(-.03, .03), YF - .03 - .04 * (i % 2), h * .985)); bot = Vector((x, YF - foot, .0))
        d = top - bot; L = d.length; c = (top + bot) / 2
        tilt = -math.atan2(d.y, d.z)
        box('Shop_Board', tuple(c), (.142, .035, L), P['door'], bevel=.006, seg=1, rot=(tilt, 0, math.atan2(-d.x, d.z) * .0 + R.uniform(-.03, .03)), group='Wood', grain='z', uvw=1.2)
        for zb in (.45, 2.1):
            q = bot + d * (zb / d.z)
            box('Shop_Board_Batten', (q.x, q.y - .028 * math.cos(tilt), q.z), (.13, .022, .05), P['timber'], bevel=.004, seg=1, rot=(tilt, 0, 0),
                group='Wood', grain='x', detail=1)


# ------------------------------------------------------------------ goods: light versions for the shelves (a shop holds many of them)
GOODS_UVW = 3.0


def jar_s(P, name, p, s, mat=None, cover=False, seed=0.):
    """Small storage jar, 14 sides: glazed body, bare foot and lip; cover: a red cloth tied over the mouth (as on the reference shelves)."""
    prof = [(0., 0.), (.2, 0.), (.29, .08), (.34, .3), (.3, .52), (.2, .64), (.17, .7), (.19, .74), (.14, .74), (0., .66)]
    o = lathe(name, [(r * s, z * s) for r, z in prof], p, mat or P['clay'], seg=14, uvw=GOODS_UVW)
    foot = .1 + .03 * math.sin(seed)
    set_float(o, 'gmask', lambda co: 1. if foot * s < co.z < .72 * s and math.hypot(co.x, co.y) > .1 * s else 0.)
    if cover:
        cp = [(.0, .82), (.12, .8), (.2, .76), (.23, .7), (.24, .64), (.215, .62)]
        lathe(name + '_Cover', [(r * s, z * s) for r, z in cp][::-1], p, P['bolt_red'], seg=14, uvw=GOODS_UVW, detail=1, grain='z')
        torus(name + '_Tie', (p[0], p[1], p[2] + .66 * s), .2367 * s - .003, .006,      # on the cloth, cutting 3 mm into it
          P['twine'], major=14, minor=4, detail=1, grain='z', uvw=GOODS_UVW)
    return o


def bowls(P, name, p, n, r=.11):
    """A stack of n coarse bowls, glazed inside and out."""
    prof = [(0., 0.), (.42, 0.), (.5, .1), (.8, .45), (1., .62), (.94, .62), (.74, .44), (.44, .16), (0., .14)]
    for i in range(n):
        o = lathe(f'{name}_{i}', [(a * r, z * r + i * .155 * r) for a, z in prof], p, P['glaze_green'], seg=16, uvw=GOODS_UVW, detail=1)
        set_float(o, 'gmask', lambda co: 1. if co.z > .02 * r else 0.)


def basket_s(P, name, p, s=1., fill=None, R=None):
    """Plain split-bamboo basket, 18 sides, one rim hoop; fill: produce heaped in it."""
    prof = [(0., .008), (.15, .008), (.17, .025), (.197, .085), (.21, .16), (.205, .21), (.195, .21), (.198, .16), (.186, .088), (.158, .032), (0., .026)]
    with xf(T(*p) @ RZ((R.random() if R else 0.) * 6.)):
        o = lathe(name, [(r * s, z * s) for r, z in prof], (0., 0., 0.), P['weave_basket'], seg=18, grain='z', uvw=PROP_UVW)
        set_attr_list(o, 'wuv', [((math.atan2(v.co.y, v.co.x) * .2 * s, v.co.z, 0.) if math.hypot(v.co.x, v.co.y) > .155 * s or v.co.z > .03 * s else
                                  (v.co.x, v.co.y, 0.)) for v in o.data.vertices])
        torus(name + '_Rim', (0., 0., .21 * s), .203 * s, .008, P['hoop'], major=18, minor=4, detail=1, grain='z', uvw=PROP_UVW)
        if fill is not None:
            heap(P, name + '_Fill', (0., 0., .15 * s), .17 * s, fill, R)


def heap(P, name, c, rad, kind, R):
    """Produce heaped in a basket or on a tray: a domed bed plus loose pieces on top."""
    mat, size, flat = {'potato': (P['potato'], .035, .8), 'chili': (P['chili'], .025, .5), 'greens': (P['greens'], .06, .55),
                       'beans': (P['beans'], .02, 1.)}[kind]
    from ti_core import sphere
    sphere(name + '_Bed', (c[0], c[1], c[2]), rad * .95, mat, scale=(1, 1, .45), seg=12, ring=5, uvw=GOODS_UVW)
    n = 7 if kind != 'beans' else 0
    for i in range(n):
        a = i / n * math.tau + (R.random() if R else 0.); rr = rad * (.25 + .5 * ((i * 7) % 5) / 5)
        sphere(name, (c[0] + rr * math.cos(a), c[1] + rr * math.sin(a), c[2] + rad * .38 - rr * .3), size * (.85 + .3 * ((i * 3) % 4) / 4), mat,
               scale=(1.25 if kind == 'chili' else 1., flat, flat), seg=7, ring=4, detail=1, uvw=GOODS_UVW)


def bundle(P, name, p, size, mat, rz=0.):
    """A cloth-wrapped parcel tied with hemp cord both ways."""
    w, d, h = size
    rbox(name, p, size, mat, r=min(.025, h * .3), amp=.004, freq=6., seed=int(p[0] * 97 + p[1] * 31), div=.06, rot=(0, 0, rz), uvw=GOODS_UVW)
    with xf(T(*p) @ RZ(rz)):
        box(name + '_Cord', (0., 0., 0.), (w + .004, .012, h + .004), P['twine'], bevel=0., detail=1, grain='x', uvw=GOODS_UVW)
        box(name + '_Cord', (0., 0., 0.), (.012, d + .007, h + .007), P['twine'], bevel=0., detail=1, grain='y', uvw=GOODS_UVW)


def fill_shelf(P, R, name, x0, x1, y, z, top=False, depth=.36):
    """One shelf board's goods from x0 to x1 along x (frame: shelf back at +y), packed: rows of jars, bundles, baskets, bowls."""
    x = x0 + .04
    k = 0
    while x < x1 - .12:
        kind = R.choices(('jars', 'bundles', 'basket', 'bowls', 'bolts'), (4, 3, 2, 1.2, 1.5 if not top else 0.))[0]
        if kind == 'jars':
            s = R.uniform(.26, .36) if not top else R.uniform(.4, .5); n = R.randint(2, 3)
            mat = P['clay'] if R.random() < .65 else P['glaze_green']
            for j in range(n):
                if x + .7 * s > x1: break
                jar_s(P, f'{name}_Jar_{k}_{j}', (x + .34 * s, y + R.uniform(-.03, .03), z), s * R.uniform(.92, 1.06), mat, cover=R.random() < .35, seed=k + j)
                x += .7 * s + .02
        elif kind == 'bundles':
            w = R.uniform(.22, .3)
            if x + w > x1: break
            zc = z
            for j in range(R.randint(1, 3)):          # stacked on the one below (each its own height), cords clear of the next parcel
                h = R.uniform(.09, .13)
                bundle(P, f'{name}_Bundle_{k}_{j}', (x + w / 2, y + R.uniform(-.02, .02), zc + h / 2), (w, min(.26, depth - .06), h),
                       R.choice((P['bolt_plain'], P['bolt_plain'], P['bolt_indigo'], P['bolt_red'])), rz=R.uniform(-.06, .06))
                zc += h + .009
            x += w + .03
        elif kind == 'basket':
            s = R.uniform(.7, .85)
            if x + .42 * s > x1: break
            basket_s(P, f'{name}_Basket_{k}', (x + .21 * s, y, z), s, fill=R.choice((None, 'potato', 'chili', 'beans')), R=R); x += .42 * s + .03
        elif kind == 'bowls':
            if x + .26 > x1: break
            bowls(P, f'{name}_Bowls_{k}', (x + .12, y, z), R.randint(3, 5)); x += .27
        else:
            if x + .36 > x1: break
            m = R.choice((P['bolt_indigo'], P['bolt_plain'], P['bolt_red']))
            for j in range(R.randint(2, 3)):
                cyl(f'{name}_Bolt_{k}_{j}', (x + .17, y + R.uniform(-.02, .02), z + .05 + j * .095), .05, .3, m, axis='y', verts=10, bevel=.004, rot=(math.pi / 2, 0, R.uniform(-.1, .1)),
                    group='Main', grain='x', uvw=GOODS_UVW)
            x += .38
        k += 1


# ------------------------------------------------------------------ counter, table, shelves
def counter(P, R):
    x0, x1, y0, y1, zt = COUNTER
    box('Counter_Top', ((x0 + x1) / 2, (y0 + y1) / 2, zt - .03), (x1 - x0 + .08, y1 - y0 + .06, .06), P['plank'], bevel=.008, seg=2, group='Wood', grain='x', uvw=1.1)
    n = 9
    for i in range(n):           # front panel: vertical boards
        x = x0 + (x1 - x0) * (i + .5) / n
        box('Counter_Board', (x + R.uniform(-.003, .003), y0 + .02, (PL + zt - .06) / 2), ((x1 - x0) / n - .008, .03, zt - .06 - PL - .02), P['door'], bevel=.004, seg=1,
            group='Wood', grain='z', uvw=1.)
    for x in (x0 + .04, x1 - .04):
        box('Counter_Post', (x, (y0 + y1) / 2, (PL + zt - .06) / 2), (.07, y1 - y0 - .02, zt - .06 - PL), P['timber'], bevel=.008, seg=2, group='Wood', grain='z')
    box('Counter_Kick', ((x0 + x1) / 2, y0 + .05, PL + .05), (x1 - x0, .05, .1), P['timber'], bevel=.006, seg=1, group='Wood', grain='x')
    box('Counter_Shelf', ((x0 + x1) / 2, (y0 + y1) / 2 + .05, PL + .4), (x1 - x0 - .1, y1 - y0 - .12, .025), P['plank'], bevel=.003, seg=1, group='Wood', grain='x', uvw=.5)
    fill_shelf(P, R, 'Counter_Under', x0 + .1, x1 - .1, (y0 + y1) / 2 + .06, PL + .415, depth=.4)
    # on top: two baskets of produce at the street edge, a stack of bowls, a folded cloth at the back
    basket_s(P, 'Counter_Basket_0', (x0 + .3, y0 + .2, zt), .85, fill='potato', R=R)
    basket_s(P, 'Counter_Basket_1', (x0 + .75, y0 + .2, zt), .8, fill='chili', R=R)
    bowls(P, 'Counter_Bowls', (x1 - .45, y1 - .2, zt), 4)
    bundle(P, 'Counter_Cloth', (x1 - .18, y0 + .2, zt + .02), (.3, .24, .04), P['bolt_plain'], rz=.08)


def table(P, R):
    x0, x1, y0, y1, zt = TABLE
    box('Table_Top', ((x0 + x1) / 2, (y0 + y1) / 2, zt - .025), (x1 - x0, y1 - y0, .05), P['plank'], bevel=.008, seg=2, group='Wood', grain='x', uvw=1.)
    for x in (x0 + .06, x1 - .06):
        for y in (y0 + .06, y1 - .06):
            box('Table_Leg', (x, y, (PL + zt - .05) / 2), (.07, .07, zt - .05 - PL), P['timber'], bevel=.008, seg=1, group='Wood', grain='z')
        box('Table_Stretcher', (x, (y0 + y1) / 2, PL + .14), (.05, y1 - y0 - .12, .05), P['timber'], bevel=.005, seg=1, group='Wood', grain='y')
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    # a shallow round tray of beans and baskets of greens and potatoes; jars of pickles under the table
    lathe('Table_Tray', [(0., .0), (.26, .0), (.29, .045), (.275, .05), (.25, .012), (0., .012)], (xm - .45, ym, zt), P['weave_tray'], seg=24, detail=1, uvw=PROP_UVW)
    heap(P, 'Table_Tray_Beans', (xm - .45, ym, zt + .02), .22, 'beans', R)
    basket_s(P, 'Table_Basket_0', (xm + .08, ym - .02, zt), .95, fill='greens', R=R)
    basket_s(P, 'Table_Basket_1', (xm + .5, ym + .08, zt), .8, fill='potato', R=R)
    for i, x in enumerate((x0 + .3, x0 + .62, x1 - .35)):
        jar_s(P, f'Table_Under_Jar_{i}', (x, ym + .05, PL), .42, P['clay'] if i != 1 else P['glaze_green'], cover=i == 1, seed=i)


def shelf_unit(P, name, x0, x1, y_back, depth, levels, top, R, face=1):
    """Open shelves against a wall: uprights at the ends and every 1.1 m, a board per level. face = +1: the shelves face -y (back wall)."""
    n_up = max(2, int(round((x1 - x0) / 1.1)) + 1)
    ys = y_back - face * depth / 2
    for i in range(n_up):
        x = x0 + (x1 - x0) * i / (n_up - 1)
        for yy in (y_back - face * .04, y_back - face * (depth - .04)):
            box(name + '_Upright', (x, yy, (PL + top) / 2), (.06, .06, top - PL), P['timber'], bevel=.006, seg=1, group='Wood', grain='z')
    zs = [PL + .18 + (top - PL - .2) * k / (levels - 1) for k in range(levels)]
    for z in zs:
        box(name + '_Board', ((x0 + x1) / 2, ys, z), (x1 - x0 + .06, depth, .03), P['plank'], bevel=.004, seg=1, group='Wood', grain='x', uvw=.8)
    return zs


BACK_SHELVES = ((-2.0, -.66), (.66, 2.65))       # either side of the back door
WEST_SHELF = (-.35, 1.0)                          # y range on the west wall (the ladder is behind it, the table in front)
EAST_SHELF = (.05, 1.45)


def shelves(P, R):
    """Back wall: four tiers either side of the back door; the side walls: three-tier shelves; goods packed on every board."""
    yb = YB - WT - .01
    zs = []
    for i, (a, b) in enumerate(BACK_SHELVES):
        zs = shelf_unit(P, f'Back_Shelf_{i}', a, b, yb, .42, 4, 2.45, R)
        for li, z in enumerate(zs):
            fill_shelf(P, R, f'Back_{i}_{li}', a + .02, b - .02, yb - .21, z + .015, top=li == len(zs) - 1, depth=.42)
    for sx, (ya, yb2) in ((-1, WEST_SHELF), (1, EAST_SHELF)):
        x_back = sx * (XW - WT - .01)
        with xf(T(x_back, (ya + yb2) / 2, 0.) @ RZ(-sx * math.pi / 2)):
            zz = shelf_unit(P, f'Side_Shelf_{sx}', -(yb2 - ya) / 2, (yb2 - ya) / 2, 0., .36, 3, 1.75, R)
            for j, z in enumerate(zz):
                fill_shelf(P, R, f'Side_{sx}_{j}', -(yb2 - ya) / 2 + .02, (yb2 - ya) / 2 - .02, -.18, z + .015, top=j == len(zz) - 1)
    # big storage jars on the floor by the east wall
    clay_jar(P, 'Floor_Jar_0', (2.55, -.95, PL), .85, lid=True, seed=2.3)
    clay_jar(P, 'Floor_Jar_1', (2.6, -.27, PL), .66, lid=False, seed=4.1)
    return zs


# ------------------------------------------------------------------ the awning under the front eave
def awning(P, R):
    """Canvas from a batten under the front beam out to a bamboo bar on two poles, sagging between the supports and down the slope,
    a short valance hanging at the outer edge; a darker patch sewn on; the bar lashed to the poles, the batten nailed under the beam."""
    xa, xb = AWN_X
    def surf(u, v):
        x = xa + (xb - xa) * u
        y = AWN_Y0 + (AWN_Y1 - AWN_Y0) * v
        z = AWN_Z0 + (AWN_Z1 - AWN_Z0) * v
        sag = .13 * math.sin(math.pi * v) * (.75 + .25 * math.sin(math.pi * u))       # down the slope, deeper in the middle
        side = .06 * math.sin(math.pi * u) * v                                          # between the poles at the bar
        ripple = .012 * math.sin(u * 23. + v * 4.) * math.sin(math.pi * v)
        return (x + .01 * math.sin(v * 9.), y, z - sag - side + ripple)
    sheet('Awning_Canvas', 40, 16, surf, P['awning'], solid=.004, grain='x')
    # valance at the outer edge, scalloped hem
    def val(u, v):
        x = xa + (xb - xa) * u
        zt = AWN_Z1 - .06 * math.sin(math.pi * u) + .004
        hem = .17 + .028 * math.cos(u * 2 * math.pi * 7) + .018 * math.sin(u * 13.1 + 1.) + .01 * math.sin(u * 37.)   # worn scallops, not even
        return (x, AWN_Y1 - .012 - .02 * v - .015 * v * v * math.sin(u * 9.) + .008 * math.sin(u * 31.), zt - hem * v)
    sheet('Awning_Valance', 40, 4, val, P['awning'], solid=.004, grain='x')
    # the patch: a darker square sewn on, following the canvas
    def patch(u, v):
        uu, vv = .58 + .13 * u, .34 + .26 * v
        x, y, z = surf(uu, vv)
        return (x, y, z + .006)
    sheet('Awning_Patch', 6, 6, patch, P['patch'], solid=.002, grain='x', detail=1)
    # batten under the beam, the bar at the outer edge, two poles with a lashing each, guy ropes from the poles' tops to pegs
    box('Awning_Batten', ((xa + xb) / 2, AWN_Y0 + .02, AWN_Z0 + .03), (xb - xa + .1, .06, .06), P['timber'], bevel=.006, seg=1, group='Wood', grain='x')
    along('Awning_Bar', (xa - .12, AWN_Y1 - .02, AWN_Z1 + .02), (xb + .12, AWN_Y1 - .02, AWN_Z1 + .02), .03, P['pole'], verts=10, group='Main', grain='x')
    for i, x in enumerate((xa + .05, xb - .05)):
        rbox('Pole_Stone', (x, AWN_Y1 - .02, .07), (.22, .22, .14), P['stone'][i], r=.03, amp=.01, freq=2.5, hew=2, chips=1, seed=700 + i, div=.25, flat='z', group='Stone')
        along('Awning_Pole', (x, AWN_Y1 - .02, .0), (x + R.uniform(-.02, .02), AWN_Y1 - .02, AWN_Z1 + .16), .035, P['pole'], verts=10, group='Main', grain='z')
        for k in range(4):
            torus('Pole_Lash', (x, AWN_Y1 - .02, AWN_Z1 - .02 + k * .018), .04, .006, P['twine'], major=12, minor=4, detail=1, group='Main', grain='z')
    # the canvas tied to the bar at each pole and in the middle (short cords)
    for u in (.02, .5, .98):
        x = xa + (xb - xa) * u
        rope('Awning_Tie', [(x, AWN_Y1 - .01, AWN_Z1 + .045), (x, AWN_Y1 + .03, AWN_Z1 - .0), (x, AWN_Y1 - .04, AWN_Z1 - .01)], .008, P['twine'], detail=1)


# ------------------------------------------------------------------ hung under the eave, a few things by the walls
def hung(P, R):
    """A bamboo tray and a basket hung from pegs on the front beam ends, a straw hat on the right post (as in the concept)."""
    for i, (x, s) in enumerate(((-3.02, .26), (3.02, .22))):
        cyl('Beam_Peg', (x, PY - .16, WTOP - .4), .015, .1, P['timber'], axis='y', verts=8, detail=1, group='Wood')
        with xf(T(x, PY - .175, WTOP - .4 - s - .02)):
            bamboo_tray(P, (0., 0., 0.), R=s, tilt=math.radians(88))
    # goods set out on the ground in front of the counter bay (as in concept 2): baskets of produce, a pickle jar, a tray leaning on the edge stones
    basket_s(P, 'Ground_Basket_0', (-.62, YF - .62, 0.), 1.15, fill='greens', R=R)
    basket_s(P, 'Ground_Basket_1', (-.12, YF - .56, 0.), 1.0, fill='potato', R=R)
    jar_s(P, 'Ground_Jar', (.38, YF - .55, 0.), .55, P['clay'], cover=True, seed=3.)
    with xf(T(.85, YF - .39, .265)):
        bamboo_tray(P, (0., 0., 0.), R=.27, tilt=math.radians(74))
    # a lidded jar outside the right front corner
    clay_jar(P, 'Corner_Jar', (XW - .2, YF - .62, 0.), .62, lid=True, seed=5.5)


def growth(P, R):
    for _ in range(36):
        side = R.random()
        if side < .35: x, y = -XW - .22, R.uniform(YF - .3, YB + .1)
        elif side < .6: x, y = R.uniform(-XW, XW), YB + .3
        elif side < .8: x, y = XW + .22, R.uniform(YF + 2.2, YB + .1)
        else: x, y = R.uniform(-XW, XW), YF - .45
        if y < YF - .3 and -.5 < x < 3.2: continue                    # the way in and the step
        if y < YF - .3 and abs(x - AWN_X[0]) < .25: continue
        FP.grass_tuft('Base_Weed', (x, y, 0.), R.randint(4, 8), R.uniform(.12, .3), P['grass'] if R.random() < .7 else P['dry'], R, lean=.3, detail=1, spread=.025)


# ------------------------------------------------------------------ collision
def collision():
    V, F = [], []
    def prism(x0, x1, y0, y1, z0, z1):
        FP.hull_loft(V, F, [[(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)] for z in (z0, z1)])
    prism(-XW - .12, XW + .12, YF - .3, YB + .12, 0., PL)                          # plinth and floor: one step up from the street
    prism(-XW - .12, -XW + WT, YF - .1, YB + .12, PL, WTOP)                        # west gable wall (with its corner post)
    prism(XW - WT, XW + .12, YF - .1, YB + .12, PL, WTOP)                          # east gable wall
    prism(-XW + WT, XW - WT, YB - WT, YB + .12, PL, WTOP)                          # back wall (door closed)
    prism(-XW - .12, XW + .12, YF - .1, YB + .12, WTOP - .45, WTOP)                # beam and loft: out of reach
    # roof mass: six stacked boxes stepping up under the curved roof to the ridge (along x at y = YC); each box spans the depth where
    # the underside of the roof boards (VR.under) is still 3 cm above its top, so nothing sticks out through the tiles and anything
    # landing on the roof stops at most one step (about 0.27 m) below it
    zr = VR.under(0., 0.) - .06
    ysam = sorted([YF - .1 + (YB + .12 - YF + .1) * i / 200 for i in range(201)] + [YC])
    n = 6
    for k in range(n):
        za, zb = WTOP + (zr - WTOP) * k / n, WTOP + (zr - WTOP) * (k + 1) / n
        inside = [y for y in ysam if VR.under(0., y - YC) - .03 >= zb]
        if inside:
            prism(-XW - .12, XW + .12, min(inside), max(inside), za, zb)
    for x in POSTS[1:3]:
        prism(x - .18, x + .18, PY - .18, PY + .18, PL, WTOP)                      # the two middle posts (the corner ones are in the walls)
    x0, x1, y0, y1, zt = COUNTER; prism(x0 - .04, x1 + .04, y0 - .03, y1 + .03, PL, zt)
    x0, x1, y0, y1, zt = TABLE; prism(x0, x1, y0, y1, PL, zt)
    for a, b in BACK_SHELVES:
        prism(a - .03, b + .03, YB - WT - .46, YB - WT, PL, 2.5)                   # back shelves
    prism(-XW + WT, -XW + WT + .4, WEST_SHELF[0] - .03, WEST_SHELF[1] + .03, PL, 1.8)   # west side shelves
    prism(XW - WT - .4, XW - WT, EAST_SHELF[0] - .03, EAST_SHELF[1] + .03, PL, 1.8)     # east side shelves
    prism(2.2, 2.95, -1.3, -.02, PL, .85)                                          # floor jars
    prism(-.9, 1.15, YF - .9, YF - .3, 0., .45)                                    # goods on the ground in front of the counter
    prism(-2.6, -2.1, YB - WT - .8, YB - WT - .3, PL, 3.3)                         # ladder
    prism(BOARDS[0] - .08, BOARDS[1] + .04, YF - .5, YF - .02, 0., 1.6)              # the shop boards against the left post
    for x in AWN_X:
        prism(x - .12, x + .12, AWN_Y1 - .14, AWN_Y1 + .1, 0., AWN_Z1 + .16)        # awning poles on their stones
    prism(XW - .45, XW + .05, YF - .9, YF - .34, 0., .62)                          # corner jar
    xs = (POSTS[2] + POSTS[3]) / 2
    prism(xs - .55, xs + .55, YF - .66, YF - .3, 0., PL / 2)                       # the step stone in front of the right bay
    return V, F


# ------------------------------------------------------------------ build
def build_vh04(P):
    R = random.Random('VH04')
    VR.configure(**ROOF)
    front(P, R); walls(P, R); roof_fill(P)
    def cell(kind, side, x, k, r):          # old roof, kept up: old and dark-fired tiles, moss low on the back slope and near the gables
        if side == 1 and k < 5 and r < .35: return 2 + (4 if kind == 'roll' else 0)
        if abs(x) > 2.6 and k < 6 and r < .3: return 2 + (4 if kind == 'roll' else 0)
        if side == -1 and (k < 4 and r < .4 or k < 8 and r < .2 or r < .07): return 2 + (4 if kind == 'roll' else 0)   # street slope: moss low down, thinning upwards (concept 2)
        if r > .93: return 3 + (4 if kind == 'roll' else 0)
        return (0 if r < .6 else 1) + (4 if kind == 'roll' else 0)
    with xf(T(0., YC, 0.)):
        VR.build(P, cell=cell)
    shop_boards(P, R); counter(P, R); table(P, R)
    zs = shelves(P, R)
    awning(P, R); hung(P, R); growth(P, R)
    socket('Socket_ShopFront', (1.98, YF - .7, 0.), rot=(0, 0, math.pi))
    socket('Socket_Counter', (0., (COUNTER[2] + COUNTER[3]) / 2, COUNTER[4]))
    socket('Socket_Table', ((TABLE[0] + TABLE[1]) / 2, (TABLE[2] + TABLE[3]) / 2, TABLE[4]))
    for i, z in enumerate(zs):
        socket(f'Socket_Shelf_{i}', (1.6, YB - WT - .22, z + .015))
    socket('Socket_BackDoor', (0., YB, PL))
    socket('Socket_Awning_Under', ((AWN_X[0] + AWN_X[1]) / 2, (AWN_Y0 + AWN_Y1) / 2, 0.))
    S['collision_mesh'] = collision()
    S['prop'] = dict(kind='vshop')
    __import__('vl_house').occluded_uvw()


NOTE = ('臨街店屋（概念圖 2 右邊的主角、概念圖 1）：7 × 6 m 地塊上的單層高屋加閣樓，屋脊順著街，長邊屋簷朝街，兩側是山牆。'
        '臨街一面整面敞開：四根方柱（三開間）托一根粗額枋，枋下有插門板的槽、地上一道有槽的木門檻，枋上到屋面用木板封起。'
        '拆下的門板（5 片）一排立在左前角柱和額枋前，下端往街外撇。店內地面比街高一級（0.3 m，石砌邊），中間一間是櫃台，左間一張矮貨桌，'
        '後牆四層貨架、兩側山牆各一座兩層貨架，放陶罐、竹籃、布匹和木盒；頭頂看得到閣樓樓板的楞木，左後角一把竹梯上閣樓。'
        '前簷下伸出一片褪色帆布篷，前端綁在竹竿橫桿上、由兩根竹竿撐著，中間下垂，外緣一道花邊垂簾，縫了一塊深色補丁。'
        '山牆是石灰泥加亂石牆腳、轉角木柱與腰枋橫平豎直（沒有斜撐），下面一扇直欞窗、上面一扇閣樓小窗；後牆一扇木板門（關著）和一扇窗。'
        '屋頂用 VL 的筒瓦與板瓦，屋脊兩端低調起翹，後坡和山牆邊長苔。'
        '碰撞：石基與店內地面（比街高一級）、兩側山牆、後牆、額枋以上整塊、兩根中柱、櫃台、貨桌、貨架、地上的大缸、竹梯、門板、布篷竹竿、牆角陶缸；店面敞開可以走進去。')


def register(ASSETS):
    ASSETS['VH04_StreetShop'] = dict(
        zh='臨街店屋', kind='vshop', cond='elderly', palette=palette, build=build_vh04, limit=(7., 6., 6.5), tex=2048, ver='v001',
        box=((-3.5, -3., 0.), (3.5, 3., 6.5)), ref='VH04/VH04-threeview', slot='A1_QingxiVillage_StreetShop', minTier='standard', clamp_max=.03, uv_shape='CONVEX',
        atlases={'Main': ['Main', 'Detail_Small'], 'Stone': ['Stone'], 'Wood': ['Wood']},
        origin='centre of the lot at ground level, front (the street, the open shop front) -Y',
        method='procedural mesh construction (art/source/village-houses-b/vh_shop.py, vh_roof.py, props from vh_court.py); procedural shaders baked to three 2048 atlases (Main, Stone, Wood); roof tiles on the shared 1024 VL tile texture (VL_Shared)',
        based_on='new outline (work pack 2026-11-28 VH04, concept A1_concept_2_entry); materials and roof tiles shared with VL01-05 and VH01-03',
        note=NOTE)


# ------------------------------------------------------------------ measured checks
def vshop_checks(aid, check, cfg):
    from vl_checks import _bvh
    body = _bvh([o for g, o in S['lods'][0].items() if not g.startswith('Detail_')])
    col = _bvh([S['collision_obj']]) if S.get('collision_obj') else None
    down = lambda x, y, z=12., f=body: (lambda h: round(h[0].z, 3) if h else None)(f((x, y, z), (0, 0, -1)))   # z: start under the loft / eave
    hit = lambda p, d, ax, f=body: (lambda h: round(h[0][ax], 3) if h else None)(f(p, d))
    # ridge along the street: high over the ridge line, low over the front and back walls
    ridge = [down(x, YC) for x in (-2.5, 0., 2.5)]
    eaves = [down(0., y) for y in (YF + .1, YB)]
    check('ridge_along_street', all(ridge) and all(eaves) and min(ridge) > max(eaves) + 1.5 and max(ridge) <= 6.5,
          {'ridge_top_m': ridge, 'roof_over_front_and_back_m': eaves})
    # open front: a ray at 1.6 m through the right bay and above the counter goes past the post line deep into the shop
    rb = hit(((POSTS[2] + POSTS[3]) / 2, -12., 1.6), (0, 1, 0), 1); mid = hit((.25, -12., 1.7), (0, 1, 0), 1)   # off the back door's centre seam
    beside = hit((-XW + .1, -12., 1.6), (0, 1, 0), 1)
    check('shop_front_open', rb is not None and mid is not None and rb > YF + 1.5 and mid > YF + 1.5 and beside is not None and beside < YF + .1,
          {'right_bay_first_hit_y_m': rb, 'over_counter_first_hit_y_m': mid, 'corner_post_y_m': beside, 'post_line_y_m': YF})
    # counter height above the floor, the floor one step up
    ct = down(.25, (COUNTER[2] + COUNTER[3]) / 2, 2.5)          # from under the loft boards
    fl = down((POSTS[2] + POSTS[3]) / 2, YF + 1.2, 2.5)
    check('counter_and_raised_floor', ct is not None and fl is not None and .85 < ct - fl < 1.0 and abs(fl - PL) < .03,
          {'counter_top_m': ct, 'floor_m': fl, 'counter_over_floor_m': round(ct - fl, 3) if ct and fl else None})
    # awning under the front eave, outside the post line, lower than the eave
    aw = [down(x, -2.3, 3.4) for x in (-1.5, 0., 1.5)]          # from under the front eave
    eave = down(-1.5, -2.6)
    check('awning_under_eave', all(aw) and all(2.2 < a < 3.1 for a in aw) and eave is not None,
          {'awning_top_at_y-2.3_m': aw, 'first_hit_at_y-2.6_m': eave})
    # shop boards stood against the left corner post, out in front of the post line
    bd = hit(((BOARDS[0] + BOARDS[1]) / 2, -12., 1.0), (0, 1, 0), 1)
    check('shop_boards_stacked', bd is not None and YF - .45 < bd < YF - .05, {'board_face_y_m_at_1m': bd, 'post_line_y_m': YF})
    out = {'ridge_m': ridge, 'counter_top_m': ct, 'awning_m': aw}
    if col:
        walk = col(((POSTS[2] + POSTS[3]) / 2, YF + .6, 2.2), (0, 0, -1))
        cg = {'west': hit((-12., .5, 1.5), (1, 0, 0), 0, col), 'east': hit((12., 1.8, 1.5), (-1, 0, 0), 0, col), 'back': hit((0., 12., 1.5), (0, -1, 0), 1, col)}
        into = hit(((POSTS[2] + POSTS[3]) / 2, -12., 1.2), (0, 1, 0), 1, col)
        check('collision_walls_closed_front_open', all(v is not None for v in cg.values()) and walk is not None and abs(walk[0].z - PL) < .01 and into is not None and into > YF + .6,
              {'collision_faces_m': cg, 'floor_inside_right_bay_m': round(walk[0].z, 3) if walk else None, 'right_bay_first_collision_y_m': into})
        out['collision'] = cg
    return out
