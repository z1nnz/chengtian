"""AL01 root altar terrace (D2 ancient tree block, placement (7, 207) in docs/execution/world-plan/D2.md).

A low square terrace of big dry-laid slabs among the roots of the great tree: two courses of wall blocks, a paved top of
uneven slabs (two cracked through, one corner slab sunk and tilted), three wide worn steps on the front (-Y), and a plain
round plinth in the middle with a shallow worn hollow. Roots grip and lift the back right corner. Nothing on the plinth:
no figure, no offerings, no writing (story rule: the old shrine places are empty).

Built the way the village houses are (core-modelling-bar-v1): every stone is its own rbox with chisel facets and chips, roots
are fr_parts.sweep, growth is fr_parts moss, ferns and grass; materials are cr_mats / fr_mats; atlas, bake, LODs, export and
previews run through the village-houses-b build driver (build_core_d2.py).
Reference: art/references/core-d2-v1/AL01_RootAltarTerrace/turnaround.png (proportions from the sizes below, not measured off it).
Origin: footprint centre of the terrace, bottom z = 0, front (steps) -Y.
"""
import math, random
from mathutils import Vector
import cr_mats as cm
import fr_parts as FP
from cr_parts import rbox
from ti_core import S, lathe, socket

TW = 5.2                    # terrace width and depth
C0, C1 = .46, .42           # course heights
SLAB = .16                  # paving thickness
TOP = C0 + C1 + SLAB - .06  # walking surface (slabs sit 6 cm into the top course)
STEP_W = 3.0; TREAD = .42
STEPS = [(.30, 0), (.60, 1), (.90, 2)]   # (top z, index): three steps up to the paving
PLINTH_R = .62; PLINTH_H = .30


def palette():
    P = FP.palette()
    P['wall'] = [cm.stone(f'Altar_Wall_{i}', light=l, dark=d, ochre=(.22, .185, .125), moss=1.7, lichen=1.1, crack=.9, wet_z=.5)
                 for i, (l, d) in enumerate((((.15, .14, .118), (.055, .052, .044)), ((.135, .13, .115), (.05, .048, .043)), ((.16, .145, .115), (.06, .054, .043))))]
    P['pave'] = [cm.stone(f'Altar_Paving_{i}', light=l, dark=d, ochre=(.23, .195, .13), moss=1.3, lichen=1.2, crack=1.1)
                 for i, (l, d) in enumerate((((.165, .155, .13), (.062, .058, .05)), ((.15, .143, .125), (.056, .053, .047))))]
    P['plinth'] = cm.stone('Altar_Plinth', light=(.17, .16, .138), dark=(.064, .06, .052), ochre=(.24, .2, .135), moss=1.1, lichen=1.2, crack=.9)
    return P


def _course(P, R, z0, h, inset, tag, gap_front):
    """One ring of wall blocks round the terrace; block lengths vary, joints do not line up with the course below."""
    half = TW / 2 - inset; depth = .62
    for side in range(4):
        pos = -half + (R.uniform(.0, .5) if tag == 'B' else 0.)
        k = 0
        while pos < half - .05:
            L = min(R.uniform(.85, 1.55), half - pos)
            if half - (pos + L) < .45: L = half - pos
            mid = pos + L / 2
            x, y, rz = {0: (mid, -half + depth / 2, 0.), 1: (half - depth / 2, mid, math.pi / 2), 2: (-mid, half - depth / 2, math.pi), 3: (-half + depth / 2, -mid, -math.pi / 2)}[side]
            rbox(f'Wall_{tag}_{side}_{k}', (x + R.uniform(-.045, .045) * (side % 2 == 1), y + R.uniform(-.045, .045) * (side % 2 == 0), z0 + h / 2 + R.uniform(-.012, .012)), (L - R.uniform(.02, .06), depth, h - .006), R.choice(P['wall']), r=.03, amp=.028, freq=1.7,
                 hew=R.randint(4, 7), chips=R.randint(2, 5), seed=R.randint(0, 9999), div=.09,
                 rot=(math.radians(R.uniform(-1.8, 1.8)), math.radians(R.uniform(-1.8, 1.8)), rz + math.radians(R.uniform(-2.5, 2.5))), group='Main')
            pos += L; k += 1


def _paving(P, R):
    """Top slabs: four uneven rows; two slabs broken in two, the back right corner slab sunk and tilted by the root under it."""
    half = TW / 2 - .1; rows = [1.15, 1.4, 1.25, 1.2]
    y = -half; n = 0
    for ri, d in enumerate(rows):
        x = -half
        while x < half - .05:
            w = min(R.uniform(.95, 1.6), half - x)
            if half - (x + w) < .5: w = half - x
            cx, cy = x + w / 2, y + d / 2
            corner = cx > half - 1.5 and cy > half - 1.4
            z = TOP - SLAB / 2 + R.uniform(-.03, .03)
            rot = (math.radians(R.uniform(-1.6, 1.6)), math.radians(R.uniform(-1.6, 1.6)), math.radians(R.uniform(-1.8, 1.8)))
            if corner: z += .07; rot = (math.radians(-6.5), math.radians(5.), math.radians(3.))
            broken = n in (2, 9) and not corner
            pieces = [(cx, w)] if not broken else [(x + w * .29, w * .58 - .035), (x + w * .79, w * .42 - .035)]
            for pi, (px, pw) in enumerate(pieces):
                rbox(f'Paving_{ri}_{n}_{pi}', (px, cy, z - (.018 * pi if broken else 0.)), (pw - R.uniform(.02, .05), d - R.uniform(.022, .05), SLAB), R.choice(P['pave']), r=.026, amp=.02, freq=1.9,
                     hew=R.randint(3, 6), chips=R.randint(2, 4) + 2 * broken, seed=R.randint(0, 9999), div=.085,
                     rot=(rot[0], rot[1] + math.radians(2.2 * (pi * 2 - 1)) * broken, rot[2] + math.radians(4. * pi) * broken), group='Main')
            x += w; n += 1
        y += d


def _surf(x, y):
    """Height a root rests on at (x, y): the paving inside the terrace, the ground outside."""
    return TOP if abs(x) < TW / 2 - .05 and abs(y) < TW / 2 - .05 else 0.


def _root(name, pts, r0, bark, seed, forks=2, level=0):
    """A real root, not a hose: the path wanders, the girth swells at knuckles and flares where it leaves the trunk, the section
    is flattened where it lies on stone, the bark is deeply fissured, and it breaks into side roots that break again into feeders."""
    R = random.Random(seed * 7 + level)
    P = [Vector(p) for p in pts]
    # wander: subdivide each span and push the new points sideways and up or down by a share of the girth
    path = [P[0]]
    for a, b in zip(P, P[1:]):
        t = (b - a); side = Vector((-t.y, t.x, 0.)); side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
        for f in (.33, .66):
            path.append(a.lerp(b, f) + side * R.uniform(-.45, .45) * r0 + Vector((0, 0, R.uniform(-.2, .3) * r0)))
        path.append(b)
    if max(p.z for p in path) < .08: return                               # wholly in the ground: nothing to show
    n = len(path); ph = R.uniform(0, 6.28); radii = []
    for i in range(n):
        u = i / (n - 1)
        r = r0 * (.06 + .94 * (1 - u) ** 1.15)
        r *= 1 + .42 * math.exp(-u * 7.)                                  # flare at the trunk end
        r *= 1 + .2 * math.sin(u * 11. + ph) * (1 - u) + .12 * math.sin(u * 27. + ph * 2)   # knuckles
        radii.append(max(.012, r))
    FP.sweep(name, [tuple(p) for p in path], radii, bark[(seed + level) % len(bark)], aspect=(.72 if level == 0 else .8), fiss=.36 if level < 2 else .2,
             twist=R.uniform(.5, 1.1) * R.choice((-1, 1)), plates=3.6, worn=.4, lump=.2 if level == 0 else .14, crack=.4, seed=seed * 31 + level,
             detail=min(level, 2), group='Main')
    if level >= 2 or forks <= 0: return
    for k in range(forks):
        i = int(n * (.22 + .6 * (k + R.uniform(.1, .9)) / forks)); i = max(2, min(n - 3, i))
        o = path[i]; t = (path[i + 1] - path[i - 1]); t.z = 0; t.normalize()
        turn = math.radians(R.uniform(28, 62)) * (1 if (k + seed) % 2 else -1)
        d = Vector((t.x * math.cos(turn) - t.y * math.sin(turn), t.x * math.sin(turn) + t.y * math.cos(turn), 0.))
        rc = radii[i] * R.uniform(.42, .6); L = max(.7, radii[i] * R.uniform(6., 11.))
        child = [tuple(o)]
        for j in range(1, 6):
            f = j / 5; q = o + d * L * f + Vector((-d.y, d.x, 0.)) * math.sin(f * 3.1 + seed) * .18 * L * .3
            rest = _surf(q.x, q.y) + rc * (1 - f) * .55
            z = max(rest, o.z + (rest - o.z) * min(1., f * 1.6)) if j < 5 else _surf(q.x, q.y) - .1
            child.append((q.x, q.y, z))
        _root(f'{name}_{"abcdef"[k]}', child, rc, bark, seed * 5 + k + 1, forks=max(1, forks - 1), level=level + 1)


def build_al01(P):
    R = random.Random('AL01')
    # the packed core under the paving, so no joint shows daylight
    rbox('Core_Fill', (0., 0., (TOP - SLAB) / 2 - .02), (TW - 1.0, TW - 1.0, TOP - SLAB - .02), P['earth'], r=.02, div=.4, group='Main')
    _course(P, R, 0., C0, 0., 'A', False)
    _course(P, R, C0 - .004, C1, .05, 'B', True)
    _paving(P, R)
    # three steps: each a row of two or three long worn blocks, the top one level with the paving
    for top, k in STEPS:
        yc = -TW / 2 - TREAD * (2 - k) + TREAD / 2 - .03
        x = -STEP_W / 2
        for j, share in enumerate(((.38, .62), (.55, .45), (.3, .4, .3))[k]):
            L = STEP_W * share
            rbox(f'Step_{k}_{j}', (x + L / 2, yc, top / 2), (L - .02, TREAD + .16, top), P['pave'][j % 2], r=.04, amp=.026, freq=1.6, hew=6, chips=4,
                 seed=300 + k * 10 + j, div=.09, rot=(math.radians(R.uniform(-1.5, 1.5)), math.radians(R.uniform(-1.2, 1.2)), math.radians(R.uniform(-2., 2.))),
                 group='Main')
            x += L
    # the plinth: a low drum with a worn rim and a shallow hollow, on a slightly wider foot ring
    z = TOP - .01
    lathe('Plinth_Foot', [(0., z), (PLINTH_R + .1, z), (PLINTH_R + .11, z + .05), (PLINTH_R + .07, z + .09), (0., z + .09)], (0., .15, 0.), P['plinth'], seg=40, group='Main')
    lathe('Plinth_Drum', [(0., z + .07), (PLINTH_R, z + .07), (PLINTH_R + .015, z + PLINTH_H * .55), (PLINTH_R - .01, z + PLINTH_H - .03), (PLINTH_R - .05, z + PLINTH_H),
                          (PLINTH_R - .2, z + PLINTH_H - .005), (PLINTH_R - .34, z + PLINTH_H - .045), (0., z + PLINTH_H - .06)], (0., .15, 0.), P['plinth'], seg=40, group='Main')
    # roots: buttress roots from the tree behind the right back corner, humping over the wall and breaking into side roots
    # and fine feeders that creep across the paving into the joints (see _root)
    bark = P['bark']
    _root('Root_Corner_A', [(4.75, 4.6, -.4), (4.3, 4.15, .7), (3.85, 3.7, 1.3), (3.2, 3.05, 1.5), (2.6, 2.45, TOP + .32), (1.9, 1.95, TOP + .13), (1.2, 1.7, TOP + .03), (.7, 1.8, TOP - .1)], .58, bark, 11, forks=4)
    _root('Root_Corner_B', [(3.3, 4.85, -.4), (3.2, 4.3, .55), (3.1, 3.7, 1.08), (2.98, 2.8, 1.12), (2.92, 1.8, .8), (3.0, .8, .45), (3.12, -.1, .16), (3.3, -.9, -.12)], .5, bark, 12, forks=3)
    _root('Root_Corner_C', [(5.0, 3.2, -.4), (4.45, 2.88, .45), (3.8, 2.5, .9), (3.05, 2.1, 1.08), (2.4, 1.35, TOP + .12), (2.1, .5, TOP + .02), (2.05, -.2, TOP - .1)], .36, bark, 13, forks=3)
    _root('Root_Right_Wall', [(4.6, .95, -.3), (4.1, .72, .25), (3.5, .45, .52), (2.9, -.3, .62), (2.84, -1.4, .36), (3.0, -2.4, -.1)], .26, bark, 14, forks=2)
    _root('Root_Back_Left', [(-4.1, 4.75, -.35), (-3.6, 4.2, .35), (-3.0, 3.5, .75), (-2.3, 2.85, 1.0), (-1.6, 2.5, TOP + .1), (-.8, 2.2, TOP - .1)], .36, bark, 15, forks=3)
    _root('Root_Back_Mid', [(.55, 4.9, -.35), (.48, 4.3, .3), (.35, 3.5, .68), (.15, 2.8, 1.0), (-.15, 2.3, TOP + .08), (-.3, 1.6, TOP - .1)], .3, bark, 16, forks=2)
    _root('Root_Front_Left', [(-4.5, -.7, -.3), (-3.95, -1.1, .18), (-3.3, -1.6, .36), (-2.88, -2.5, .3), (-3.05, -3.5, -.1)], .2, bark, 17, forks=2)
    # stones fallen at the foot
    for j, (x, y, s) in enumerate(((-3.0, -2.95, .34), (2.2, -3.25, .26), (3.15, -1.0, .22), (-3.05, 1.4, .3), (-1.9, 3.0, .24), (.6, 3.05, .28))):
        FP.pebble(f'Foot_Stone_{j}', (x, y, s * .22), s, P['stone'][j % 2], seed=70 + j, detail=1, group='Main')
    # growth: moss on the shaded back and left walls, in the paving joints and on the step ends; ferns and grass at the foot
    for j in range(120):
        side = R.choice((1, 2, 2, 3, 3, 0)); t = R.uniform(-TW / 2 + .2, TW / 2 - .2); zz = R.uniform(.12, C0 + C1 - .05)
        q, n = {0: ((t, -TW / 2, zz), (0, -1, 0)), 1: ((TW / 2, t, zz), (1, 0, 0)), 2: ((t, TW / 2, zz), (0, 1, 0)), 3: ((-TW / 2, t, zz), (-1, 0, 0))}[side]
        if side == 0 and abs(t) < STEP_W / 2: continue
        FP.moss_patch('Wall_Moss', q, n, R.uniform(.14, .34), P['moss'], seed=100 + j, flat=.75, snap_each=True)
    for j in range(110):
        x, y = R.uniform(-TW / 2 + .15, TW / 2 - .15), R.uniform(-TW / 2 + .15, TW / 2 - .15)
        if (x * x + (y - .15) ** 2) ** .5 < PLINTH_R + .15: continue
        FP.moss_patch('Paving_Moss', (x, y, TOP + .01), (0, 0, 1), R.uniform(.1, .26) * (1.6 if y > .4 else 1.), P['moss'], seed=200 + j, flat=.55, snap_each=True)
    for j in range(8):
        a = R.uniform(0, math.tau)
        FP.moss_patch('Plinth_Moss', (math.cos(a) * PLINTH_R, .15 + math.sin(a) * PLINTH_R, TOP + R.uniform(.08, .22)), (math.cos(a), math.sin(a), .2), R.uniform(.05, .11), P['moss'], seed=260 + j, flat=.7, snap_each=True)
    for top, k in STEPS:
        for sx in (-1, 1):
            FP.moss_patch('Step_Moss', (sx * (STEP_W / 2 - R.uniform(.1, .45)), -TW / 2 - TREAD * (2 - k) + R.uniform(.05, .3), top + .005), (0, 0, 1), R.uniform(.09, .18), P['moss'], seed=280 + k * 2 + sx, flat=.6, snap_each=True)
    foot = [(-2.78, .5), (.2, 2.82), (2.82, -.8), (-.6, -3.9), (.9, -3.95), (-2.8, -1.9), (2.1, 2.85), (-2.75, -2.75), (-2.8, -.6), (-2.78, 1.9), (-1.2, 2.78), (1.3, 2.8), (2.8, -1.9), (2.4, -2.8), (-1.75, -3.1), (1.7, -3.2), (-2.75, 2.7)]
    for j, (x, y) in enumerate(foot):
        out = Vector((x, y, 0)).normalized()
        FP.fern('Foot_Fern', (x, y, .02), P['fern'], R, n=R.randint(6, 9), L=R.uniform(.38, .66), out=(out.x, out.y, 0), detail=1, up_bias=.25)
    for j in range(48):
        side = R.randrange(4); t = R.uniform(-TW / 2 - .1, TW / 2 + .1); off = TW / 2 + R.uniform(.03, .22)
        x, y = {0: (t, -off), 1: (off, t), 2: (t, off), 3: (-off, t)}[side]
        if side == 0 and abs(t) < STEP_W / 2 + .1: y -= TREAD * 3
        FP.grass_tuft('Foot_Grass', (x, y, 0.), R.randint(10, 18), R.uniform(.14, .32), P['grass'], R, lean=.3, detail=2, spread=.04)
    for j in range(5):       # small ferns in the widest paving joints, back half
        FP.fern('Joint_Fern', (R.uniform(-2.2, 2.2), R.uniform(.9, 2.3), TOP + .005), P['fern'], R, n=5, L=R.uniform(.14, .22), out=(R.uniform(-1, 1), R.uniform(-1, 1), 0), detail=2, up_bias=.5)
    for j in range(60):      # fallen leaves on the paving and steps
        x, y = R.uniform(-2.4, 2.4), R.uniform(-3.6, 2.4)
        zz = TOP + .02 if y > -TW / 2 else (.92 if y > -TW / 2 - TREAD else .62 if y > -TW / 2 - 2 * TREAD else .32)
        if abs(x) > STEP_W / 2 - .1 and y < -TW / 2: continue
        FP.grass_tuft('Leaf_Litter', (x, y, zz), R.randint(2, 4), R.uniform(.03, .06), P['litter'], R, lean=1.4, detail=2, spread=.09)
    socket('Socket_Plinth_Top', (0., .15, TOP + PLINTH_H - .06))
    S['collision_mesh'] = collision()
    S['part_notes'] = {'terrace_m': [TW, TW, round(TOP, 3)], 'steps_top_z_m': [s[0] for s in STEPS], 'step_width_m': STEP_W, 'tread_m': TREAD,
                       'plinth_radius_height_m': [PLINTH_R, PLINTH_H], 'walk_surface_z_m': round(TOP, 3),
                       'plinth': 'empty on purpose: no figure, no offerings, no writing'}


def collision():
    V, F = [], []
    def prism(x0, x1, y0, y1, z0, z1):
        FP.hull_loft(V, F, [[(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)] for z in (z0, z1)])
    h = TW / 2
    prism(-h, h, -h, h, 0., TOP)
    for top, k in STEPS:
        y1 = -h - TREAD * (2 - k) + TREAD; prism(-STEP_W / 2, STEP_W / 2, y1 - TREAD, y1 + .02, 0., top)
    sec = lambda z: [(math.cos(a) * PLINTH_R, .15 + math.sin(a) * PLINTH_R, z) for a in (i * math.tau / 10 for i in range(10))]
    FP.hull_loft(V, F, [sec(TOP - .02), sec(TOP + PLINTH_H)])
    return V, F


NOTE = ('Stone offering terrace among the great tree roots in D2 (placement (7, 207); walking surface at z = %.2f m above its base). '
        'Three steps on -Y, a plain empty round plinth. Walkable: terrace, steps and plinth are in the collision mesh; roots and growth are not.' % TOP)


def register(ASSETS):
    ASSETS['AL01_RootAltarTerrace'] = dict(
        zh='樹根下祭壇台石', kind='altar', palette=palette, build=build_al01, limit=(10.4, 10.0, 2.2), tex=2048, ver='v001',
        box=((-4.8, -4.7, -.2), (5.6, 5.3, 2.0)), ref='core-d2-v1/AL01_RootAltarTerrace/turnaround', slot='D2_AncientTree_RootAltar', minTier='standard',
        clamp_max=.06, uv_shape='CONVEX', uv_detach_zero=True, base_z=-.18,
        atlases={'Main': ['Main', 'Detail_Small']},
        origin='footprint centre of the terrace, bottom z = 0, front (steps) -Y',
        method='procedural mesh construction (art/source/core-d2-v1/al_altar.py with village-houses-b cr_parts / fr_parts: chiselled blocks and slabs, '
               'lathed plinth, swept roots); procedural stone, bark, moss and leaf shaders baked to one 2048 atlas',
        based_on='new piece for the D2 block design (docs/execution/world-plan/D2.md, missing-piece list)',
        note=NOTE)
