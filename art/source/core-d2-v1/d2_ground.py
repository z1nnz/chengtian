"""D2 ancient tree block: ground pieces redone to the AL01 bar (SS01 stepping stones, SR01 surface roots, CO01 dug pit).

SS01  half-buried stepping stones: blunt river / mountain stones, not cut blocks. The top is worn flat with a shallow dish and a
      polished walking patch, the sides roll down into the mud with no visible bottom (15 cm under z = 0), moss climbs the lower
      shaded side as thin colonies, grass and leaf litter at the foot. Three outlines: long (A), squarish (B), round (C).
SR01  surface roots: thick (0.25-0.45 m), flattened, half buried; thick at the trunk end, breaking into side roots that break
      again into feeders that dive into the soil; earth humps where they go under, moss on the shaded flank.
CO01  freshly dug pit, about 4 m across and 1 m deep: no rim wall; a wide earth apron that fades to exactly z = 0 at the edge so
      it meets the D2 ground, a spade-cut wall in layers (dark humus over yellow-brown clay, wet at the bottom), cut roots sticking
      out of the walls with fresh pale ends, the spoil thrown up on one side as an uneven heap of clods and stones, a puddle,
      fallen leaves and a few stones in the bottom.

Same kit and driver as AL01 (build_core_d2.py): fr_parts sweep / pebble / moss / fern / grass, cr_mats / fr_mats materials.
Origins: centre of the piece at ground level z = 0 (the pit: centre of the hole at ground level; its floor is below 0).
"""
import math, random
from mathutils import Vector, noise
import bmesh
import cr_mats as cm
import fr_mats as fm
import fr_parts as FP
from ti_core import S, mesh, surface


def palette():
    P = FP.palette()
    P['rock'] = [cm.stone(f'Step_Stone_{i}', light=l, dark=d, ochre=(.2, .175, .13), moss=.45, lichen=.7, crack=.5, wet_z=.12)
                 for i, (l, d) in enumerate((((.15, .145, .13), (.055, .052, .047)), ((.135, .133, .125), (.05, .05, .048)), ((.155, .142, .118), (.06, .054, .045))))]
    P['humus'] = fm.forest_earth('Pit_Humus')
    P['clay'] = cm.stone('Pit_Clay', light=(.13, .088, .05), dark=(.06, .04, .024), ochre=(.26, .17, .08), moss=0., lichen=0., crack=.25)
    P['mud'] = cm.stone('Pit_WetMud', light=(.055, .043, .032), dark=(.022, .018, .014), ochre=(.06, .045, .03), moss=0., lichen=0., crack=.1)
    P['cut'] = fm.root_tip('Root_CutEnd')
    return P


# ------------------------------------------------------------------ stones
def rock(name, c, L, W, H, mat, seed, dish=.025, sink=.15, group='Main', res=(56, 22), cleave=True):
    """A blunt stone: a superellipsoid shell, broken by layered noise into facets and lumps, the top pressed flat and dished by
    feet, the sides bellied and rolling under into the ground (the bottom is never seen: it ends `sink` below z = 0)."""
    R = random.Random(seed); so = Vector((R.uniform(-50, 50), R.uniform(-50, 50), seed * .61))
    rot = R.uniform(0, math.tau); cs, sn = math.cos(rot), math.sin(rot)
    nu, nv = res; verts = []
    planes = []                                     # cleavage planes: the stone broke along these once, edges since rounded by water
    for _ in range(R.randint(5, 8) if cleave else 0):
        a = R.uniform(0, math.tau); el = R.uniform(-.1, .55)
        n = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el)))
        planes.append((n, R.uniform(.72, .9)))
    for j in range(nv + 1):
        v = j / nv                                  # 0 = buried bottom ring, 1 = top centre
        for i in range(nu):
            t = math.tau * i / nu; ct, st = math.cos(t), math.sin(t)
            sx = math.copysign(abs(ct) ** .72, ct); sy = math.copysign(abs(st) ** .72, st)   # blunt oval-rectangle plan
            d = Vector((ct, st, v * 2 - 1))
            k = 1 + .13 * noise.noise(so + d * 1.1) + .06 * noise.noise(so + d * 2.7) + .025 * noise.noise(so + d * 6.5)
            if v < .62:                                 # flank: bellies out above ground, tucks under below
                f = v / .62; bulge = 1 + .07 * math.sin(f * math.pi)
                rr = (.82 + .18 * f) * bulge * k
                z = -sink + (H + sink) * .78 * f ** .9
            else:                                       # shoulder rolling onto the worn top
                f = (v - .62) / .38; rr = (1. - .9 * f ** 2.4) * k * (1 + .07 * math.sin(math.pi) * (1 - f))
                rr = max(rr, 0.)
                z = -sink + (H + sink) * (.78 + .22 * math.sin(f * math.pi / 2))
                z -= dish * f ** 3                      # dish worn in the middle
                z += .012 * noise.noise(so * 2 + Vector((ct * rr * L, st * rr * W, 0)) * 3.)
            x, y = sx * L / 2 * rr, sy * W / 2 * rr
            if z > 0:                                   # shave by the cleavage planes in unit space, softly (rounded edges)
                q = Vector((x / (L / 2), y / (W / 2), (z - H / 2) / max(H, .05) * 1.2))
                for n, dd in planes:
                    e = q.dot(n) - dd
                    if e > -.08: q -= n * (math.log1p(math.exp((e) / .04)) * .04)
                x, y = q.x * L / 2, q.y * W / 2; z = min(z, q.z / 1.2 * max(H, .05) + H / 2)
            verts.append((c[0] + x * cs - y * sn, c[1] + x * sn + y * cs, c[2] + z))
    verts.append((c[0], c[1], c[2] + H - dish * 1.05))
    faces = []
    for j in range(nv):
        for i in range(nu):
            a = j * nu + i; b = j * nu + (i + 1) % nu
            faces.append((a, b, b + nu, a + nu))
    top = len(verts) - 1; base = nv * nu
    for i in range(nu): faces.append((base + i, base + (i + 1) % nu, top))
    o = mesh(name, verts, faces, mat, smooth=True, grain='z', group=group, detail=0)
    return o, rot


def _stone_growth(P, R, c, L, W, H, rot, tag, seed):
    """Moss from the lower shaded flank upwards, never on the walked top; grass and leaves round the foot."""
    shade = R.uniform(0, math.tau)
    for k in range(9):
        a = shade + R.uniform(-1.1, 1.1); e = Vector((math.cos(a) * L / 2, math.sin(a) * W / 2, 0))
        e = Vector((e.x * math.cos(rot) - e.y * math.sin(rot), e.x * math.sin(rot) + e.y * math.cos(rot), 0))
        n = Vector((e.x, e.y, .35)).normalized()
        FP.moss_patch(f'{tag}_Moss', (c[0] + e.x * 1.1, c[1] + e.y * 1.1, H * R.uniform(.12, .5)), n, R.uniform(.09, .18), P['moss'], seed=seed + k, flat=.6, snap_each=True)
    for k in range(R.randint(4, 7)):
        a = R.uniform(0, math.tau); rr = 1.08 + R.uniform(0, .12)
        x, y = math.cos(a) * L / 2 * rr, math.sin(a) * W / 2 * rr
        x, y = x * math.cos(rot) - y * math.sin(rot), x * math.sin(rot) + y * math.cos(rot)
        FP.grass_tuft(f'{tag}_Grass', (c[0] + x, c[1] + y, 0.), R.randint(6, 12), R.uniform(.08, .2), P['grass'], R, lean=.45, detail=2, spread=.03)
    for k in range(R.randint(5, 9)):
        a = R.uniform(0, math.tau); rr = 1.0 + R.uniform(0, .25)
        x, y = math.cos(a) * L / 2 * rr, math.sin(a) * W / 2 * rr
        FP.grass_tuft(f'{tag}_Leaves', (c[0] + x * math.cos(rot) - y * math.sin(rot), c[1] + x * math.sin(rot) + y * math.cos(rot), .005), R.randint(2, 4), R.uniform(.03, .06), P['litter'], R, lean=1.4, detail=2, spread=.08)


SS = {'A': (.88, .6, .2, 21), 'B': (.66, .6, .18, 22), 'C': (.48, .46, .15, 23)}   # length, width, height above ground, seed


def build_ss(key):
    def build(P):
        L, W, H, seed = SS[key]; R = random.Random(f'SS01{key}')
        _, rot = rock('Stone', (0., 0., 0.), L, W, H, P['rock'][seed % 3], seed, dish=.02 + .01 * (key == 'A'))
        # two small chips of the same stone sunk beside it
        for k in range(R.randint(1, 2)):
            a = R.uniform(0, math.tau); s = R.uniform(.07, .12)
            rock('Chip', (math.cos(a) * (L / 2 + .1), math.sin(a) * (W / 2 + .1), 0.), s * 1.3, s, s * .4, P['rock'][(seed + 1) % 3], seed + 40 + k, dish=0., sink=.05, res=(24, 9))
        _stone_growth(P, R, (0., 0.), L, W, H, rot, 'Foot', seed * 10)
        def collar(u, v):                         # mud pressed up round the foot, fading out
            t = u * math.tau; ct, st = math.cos(t), math.sin(t)
            sx = math.copysign(abs(ct) ** .55, ct); sy = math.copysign(abs(st) ** .55, st)
            rr = .9 + .4 * v; x, y = sx * L / 2 * rr, sy * W / 2 * rr
            z = .035 * (1 - v) ** 1.5 + .006 * noise.noise(Vector((x * 9, y * 9, seed))) - .004
            return (x * math.cos(rot) - y * math.sin(rot), x * math.sin(rot) + y * math.cos(rot), z)
        surface('Mud_Collar', 56, 4, collar, P['earth'], closed_u=True, group='Main')
        S['collision_mesh'] = _stone_collision(L, W, H, rot)
        S['part_notes'] = {'stone_m': [L, W, H], 'buried_m': .15, 'walk_top_z_m': H}
    return build


def _stone_collision(L, W, H, rot):
    V, F = [], []
    def sec(z, s):
        out = []
        for i in range(10):
            t = math.tau * i / 10; x, y = math.cos(t) * L / 2 * s, math.sin(t) * W / 2 * s
            out.append((x * math.cos(rot) - y * math.sin(rot), x * math.sin(rot) + y * math.cos(rot), z))
        return out
    FP.hull_loft(V, F, [sec(-.15, .85), sec(H * .8, 1.0), sec(H, .7)])
    return V, F


# ------------------------------------------------------------------ roots on open ground
def root(name, pts, r0, bark, seed, surf, forks=3, level=0, maxlevel=2):
    """AL01's root, on any ground surf(x, y): wandering path, trunk flare, knuckles, flattened section, forks to feeders."""
    R = random.Random(seed * 7 + level)
    P = [Vector(p) for p in pts]; path = [P[0]]
    for a, b in zip(P, P[1:]):
        t = (b - a); side = Vector((-t.y, t.x, 0.)); side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
        for f in (.33, .66):
            path.append(a.lerp(b, f) + side * R.uniform(-.4, .4) * r0 + Vector((0, 0, R.uniform(-.15, .2) * r0)))
        path.append(b)
    if max(p.z for p in path) < .04: return
    n = len(path); ph = R.uniform(0, 6.28); radii = []
    for i in range(n):
        u = i / (n - 1)
        r = r0 * (.08 + .92 * (1 - u) ** 1.1)
        r *= 1 + .35 * math.exp(-u * 6.) * (level == 0)
        r *= 1 + .18 * math.sin(u * 10. + ph) * (1 - u) + .1 * math.sin(u * 23. + ph * 2)
        radii.append(max(.012, r))
    FP.sweep(name, [tuple(p) for p in path], radii, bark[(seed + level) % len(bark)], aspect=(.6 if level == 0 else .72), fiss=.38 if level < 2 else .22,
             twist=R.uniform(.6, 1.2) * R.choice((-1, 1)), plates=3.4, worn=.55, lump=.22 if level == 0 else .14, crack=.45, seed=seed * 31 + level,
             detail=min(level, 2), group='Main')
    if level >= maxlevel or forks <= 0: return
    for k in range(forks):
        i = int(n * (.2 + .65 * (k + R.uniform(.1, .9)) / forks)); i = max(2, min(n - 3, i))
        o = path[i]; t = (path[i + 1] - path[i - 1]); t.z = 0; t.normalize()
        turn = math.radians(R.uniform(25, 58)) * (1 if (k + seed) % 2 else -1)
        d = Vector((t.x * math.cos(turn) - t.y * math.sin(turn), t.x * math.sin(turn) + t.y * math.cos(turn), 0.))
        rc = radii[i] * R.uniform(.5, .68); L = max(.6, radii[i] * R.uniform(6., 11.))
        child = [tuple(o)]
        for j in range(1, 6):
            f = j / 5; q = o + d * L * f + Vector((-d.y, d.x, 0.)) * math.sin(f * 3.1 + seed) * .06 * L
            rest = surf(q.x, q.y) + rc * (1 - f) * .35
            z = max(rest, o.z + (rest - o.z) * min(1., f * 1.6)) if j < 5 else surf(q.x, q.y) - .12
            child.append((q.x, q.y, z))
        root(f'{name}_{"abcdef"[k]}', child, rc, bark, seed * 5 + k + 1, surf, forks=max(1, forks - 1), level=level + 1, maxlevel=maxlevel)


def _hump(name, pts, w, h, mat):
    """Low earth hump where a root dives under (heightfield, fades to 0 at its edge)."""
    cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
    def fn(u, v):
        t = u * math.tau; rr = w * v
        x, y = cx + math.cos(t) * rr * 1.4, cy + math.sin(t) * rr
        return (x, y, max(.003, h * (1 - v * v) ** 1.5 * (1 + .25 * noise.noise(Vector((x * 4, y * 4, 0)))) - .02))
    surface(name, 20, 5, fn, mat, closed_u=True, group='Main')


SR = {   # trunk-end start, the main run (plan), girth, seed, forks
    'A': ([(-2.15, .1, -.1), (-1.6, .02, .28), (-.8, -.1, .3), (.1, .05, .24), (.95, .2, .16), (1.7, .05, .06), (2.15, -.05, -.12)], .44, 31, 4),
    'B': ([(-1.6, -.05, -.1), (-1.05, 0., .22), (-.3, .1, .22), (.45, -.05, .15), (1.15, -.15, .05), (1.6, -.1, -.12)], .34, 32, 3),
    'C': ([(-1.05, 0., -.08), (-.6, .03, .16), (.0, -.04, .14), (.6, .06, .07), (1.05, 0., -.1)], .25, 33, 3),
}


def build_sr(key):
    def build(P):
        pts, r0, seed, forks = SR[key]; R = random.Random(f'SR01{key}')
        ground = lambda x, y: 0.
        root(f'Root_{key}', pts, r0, P['bark'], seed, ground, forks=forks)
        for p in (pts[0], pts[-1]):
            _hump('Earth_Hump', [p], r0 * .95, r0 * .6, P['earth'])
        for j in range(12):                      # moss on the shaded (+Y) flank
            u = R.uniform(.05, .85); i = u * (len(pts) - 1); a, b = pts[int(i)], pts[min(int(i) + 1, len(pts) - 1)]; f = i - int(i)
            x, y = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
            FP.moss_patch('Root_Moss', (x, y + r0 * .45, r0 * .25), (0, .8, .6), R.uniform(.06, .14), P['moss'], seed=500 + j, flat=.6, snap_each=True)
        for j in range(14):
            x = R.uniform(pts[0][0], pts[-1][0]); y = R.choice((-1, 1)) * R.uniform(r0 * .7, r0 * 1.6)
            FP.grass_tuft('Root_Leaves', (x, y, .005), R.randint(2, 4), R.uniform(.03, .06), P['litter'], R, lean=1.4, detail=2, spread=.1)
        for j in range(5):
            x = R.uniform(pts[0][0], pts[-1][0]); y = R.choice((-1, 1)) * R.uniform(r0 * .6, r0 * 1.2)
            FP.fern('Root_Fern', (x, y, .01), P['fern'], R, n=R.randint(4, 7), L=R.uniform(.22, .38), out=(0, math.copysign(1, y), 0), detail=2, up_bias=.3)
        V, F = [], []
        FP.hull_loft(V, F, [[(pts[0][0], -r0 * .6, 0.), (pts[-1][0], -r0 * .3, 0.), (pts[-1][0], r0 * .3, 0.), (pts[0][0], r0 * .6, 0.)],
                            [(pts[0][0], -r0 * .5, r0 * .7), (pts[-1][0], -r0 * .2, .1), (pts[-1][0], r0 * .2, .1), (pts[0][0], r0 * .5, r0 * .7)]])
        S['collision_mesh'] = (V, F)
        S['part_notes'] = {'girth_m': r0, 'length_m': round(pts[-1][0] - pts[0][0], 2), 'buried': 'both ends dive under z = 0'}
    return build


# ------------------------------------------------------------------ the pit
PIT_R = 2.0; PIT_D = 1.0; APRON = 3.3; SPOIL = (1.75, 1.3)   # hole radius at ground, depth, apron radius, spoil heap centre


def pit_h(x, y):
    """Ground height: 0 far out; the dug bowl with spade-cut terraces; a slightly raised trodden lip; the spoil heap on +X+Y."""
    r = math.hypot(x, y); a = math.atan2(y, x)
    rr = PIT_R * (1 + .08 * math.sin(a * 3 + 1.) + .05 * math.sin(a * 5 + 2.3))
    if r < rr:
        f = r / rr
        z = -PIT_D * (1 - f ** 2.6) ** .75
        cut = .07 * math.floor((z / -.22) % 1 * 3) / 3              # spade bites: the wall steps in shallow terraces
        z += cut * (f > .35) + .035 * noise.noise(Vector((x * 2.2, y * 2.2, 0)))
    else:
        f = (r - rr) / (APRON - rr); z = .05 * max(0., 1 - f) ** 2 * (1 + .5 * noise.noise(Vector((x * 1.5, y * 1.5, 3))))
    dx, dy = x - SPOIL[0], y - SPOIL[1]
    s = max(0., 1 - (dx * dx / 1.25 ** 2 + dy * dy / .85 ** 2)) ** 1.2
    z += .6 * s * (1 + .3 * noise.noise(Vector((x * 2.5, y * 2.5, 7))))
    edge = max(0., min(1., (APRON - r) / .5))                     # last half metre fades to exactly 0
    return z * edge if r < APRON else 0.


def build_co01(P):
    R = random.Random('CO01')
    # ground skin in three materials: the apron and spoil (humus), the cut wall (clay), the wet floor (mud)
    def ring_surface(name, r0, r1, mat, nu=96, nv=10, lift=0.):
        def fn(u, v):
            t = u * math.tau; r = r0 + (r1 - r0) * v
            x, y = math.cos(t) * r, math.sin(t) * r
            return (x, y, pit_h(x, y) + lift)
        surface(name, nu, nv, fn, mat, closed_u=True, group='Main')
    ring_surface('Pit_Floor', .0001, PIT_R * .42, P['mud'], nu=48, nv=5)
    ring_surface('Pit_Wall', PIT_R * .42, PIT_R * 1.04, P['clay'], nv=18)
    ring_surface('Pit_Apron', PIT_R * 1.04, APRON, P['humus'], nu=120, nv=22)
    # humus band: the dark topsoil layer showing at the top of the cut
    def band(u, v):
        t = u * math.tau; rr = PIT_R * (1 + .08 * math.sin(t * 3 + 1.) + .05 * math.sin(t * 5 + 2.3))
        r = rr * (.93 + .07 * v); x, y = math.cos(t) * r, math.sin(t) * r
        return (x, y, pit_h(x, y) + .012)
    surface('Topsoil_Band', 96, 3, band, P['humus'], closed_u=True, group='Main')
    # skirt under the apron so the piece has no open edge from below
    def skirt(u, v):
        t = u * math.tau; return (math.cos(t) * APRON, math.sin(t) * APRON, -.06 if v > .5 else 0.)
    surface('Skirt', 64, 1, skirt, P['humus'], closed_u=True, group='Main')
    # puddle in the bottom
    def puddle(u, v):
        t = u * math.tau; r = .5 * v * (1 + .2 * math.sin(t * 3))
        return (.2 + math.cos(t) * r * 1.3, -.15 + math.sin(t) * r, -PIT_D + .025)
    surface('Puddle', 24, 2, puddle, P['mud'], closed_u=True, group='Main')
    # cut roots: from inside the wall out into the hole, fresh pale stub ends
    for k in range(11):
        a = k / 11 * math.tau + R.uniform(-.2, .2); zz = -R.uniform(.12, .7)
        rr = PIT_R * (1 + .08 * math.sin(a * 3 + 1.) + .05 * math.sin(a * 5 + 2.3))
        inner = rr * ((1 - (-zz / PIT_D) ** (1 / .75)) ** (1 / 2.6))
        r = [.09, .06, .04][k % 3] * R.uniform(.8, 1.3); stick = R.uniform(.15, .45)
        p0 = (math.cos(a) * (inner + .45), math.sin(a) * (inner + .45), zz - .05)
        p1 = (math.cos(a) * (inner - stick * .5), math.sin(a) * (inner - stick * .5), zz + R.uniform(-.04, .06))
        p2 = (math.cos(a + R.uniform(-.2, .2)) * (inner - stick), math.sin(a) * (inner - stick), zz + R.uniform(-.1, .03))
        FP.sweep(f'Cut_Root_{k}', [p0, p1, p2], [r, r * .9, r * .8], P['bark'][k % 3], aspect=.85, fiss=.3, twist=.4, seed=600 + k, detail=1, group='Main', ground=None, cap=False)
        e = Vector(p2) - Vector(p1); e.normalize()
        FP.pebble(f'Cut_End_{k}', p2, r * .95, P['cut'], seed=640 + k, flat=.35, detail=1, group='Main')
    # spoil: clods and stones thrown on the heap and scattered on the apron
    for k in range(70):
        a = R.uniform(0, math.tau); rr = R.uniform(0, 1.) ** .7
        x, y = SPOIL[0] + math.cos(a) * rr * 1.4, SPOIL[1] + math.sin(a) * rr * .95
        if k > 45: x, y = (PIT_R + R.uniform(.1, .7)) * math.cos(a), (PIT_R + R.uniform(.1, .7)) * math.sin(a)
        s = R.uniform(.05, .16)
        rock('Clod', (x, y, pit_h(x, y) - .02), s * R.uniform(1.1, 1.6), s, s * .5, P['humus'] if k % 3 else P['clay'], 700 + k, dish=0., sink=.04, res=(14, 6), cleave=False)
    for k in range(12):
        a = R.uniform(0, math.tau); rr = R.uniform(.2, 1.)
        x, y = SPOIL[0] + math.cos(a) * rr * 1.2, SPOIL[1] + math.sin(a) * rr * .8
        s = R.uniform(.1, .24)
        rock('Spoil_Stone', (x, y, pit_h(x, y) - .02), s * 1.4, s, s * .55, P['rock'][k % 3], 800 + k, dish=0., sink=.06, res=(24, 9))
    for k in range(5):
        a = R.uniform(0, math.tau); rr = R.uniform(.2, .7); s = R.uniform(.08, .16)
        x, y = math.cos(a) * rr, math.sin(a) * rr
        rock('Floor_Stone', (x, y, pit_h(x, y) + .03), s * 1.3, s, s * .45, P['rock'][k % 3], 850 + k, dish=0., sink=.04, res=(24, 9))
    # leaves blown in, grass and ferns at the apron edge, moss only on the undisturbed side
    for k in range(40):
        a = R.uniform(0, math.tau); rr = R.uniform(0, .85) if k < 18 else R.uniform(1.05, 1.5)
        x, y = math.cos(a) * rr * PIT_R * (.5 if k < 18 else 1), math.sin(a) * rr * PIT_R * (.5 if k < 18 else 1)
        FP.grass_tuft('Leaves', (x, y, pit_h(x, y) + .005), R.randint(2, 4), R.uniform(.03, .06), P['litter'], R, lean=1.4, detail=2, spread=.1)
    for k in range(22):
        a = R.uniform(math.pi * .7, math.pi * 2.1); rr = R.uniform(APRON - .7, APRON - .1)
        x, y = math.cos(a) * rr, math.sin(a) * rr
        FP.grass_tuft('Edge_Grass', (x, y, pit_h(x, y)), R.randint(6, 12), R.uniform(.1, .25), P['grass'], R, lean=.4, detail=2, spread=.04)
    for k in range(6):
        a = R.uniform(math.pi * .8, math.pi * 1.9); rr = R.uniform(APRON - .8, APRON - .45)
        x, y = math.cos(a) * rr, math.sin(a) * rr; out = Vector((x, y, 0)).normalized()
        FP.fern('Edge_Fern', (x, y, pit_h(x, y) + .01), P['fern'], R, n=R.randint(5, 8), L=R.uniform(.3, .5), out=(out.x, out.y, 0), detail=1, up_bias=.3)
    for k in range(16):
        a = R.uniform(math.pi * .8, math.pi * 1.9); rr = R.uniform(PIT_R + .5, APRON - .3)
        x, y = math.cos(a) * rr, math.sin(a) * rr
        FP.moss_patch('Apron_Moss', (x, y, pit_h(x, y) + .01), (0, 0, 1), R.uniform(.1, .22), P['moss'], seed=900 + k, flat=.5, snap_each=True)
    V, F = [], []
    sec = lambda z, r: [(math.cos(t) * r, math.sin(t) * r, z) for t in (i * math.tau / 16 for i in range(16))]
    FP.hull_loft(V, F, [sec(-PIT_D, .5), sec(-PIT_D * .5, PIT_R * .8), sec(0., PIT_R * 1.02)])
    S['collision_mesh'] = (V, F)
    S['part_notes'] = {'hole_diameter_m': PIT_R * 2, 'depth_m': PIT_D, 'apron_radius_m': APRON, 'edge_z': 0.,
                       'placement': 'set the origin at D2 ground level; cut a ~4 m hole in the terrain or let the apron cover it'}


def register(ASSETS):
    common = dict(tex=1024, ver='v002', minTier='standard', uv_shape='CONVEX', uv_detach_zero=True, atlases={'Main': ['Main', 'Detail_Small']},
                  method='procedural mesh construction (art/source/core-d2-v1/d2_ground.py with village-houses-b fr_parts / cr_mats, the AL01 method); '
                         'procedural stone, earth, bark, moss and leaf shaders baked to one atlas',
                  based_on='Claude Code redo of Codex v001 (art/core-1113-co-ruins-v2), review docs/execution/2026-11-14/codex-v11-review-1.md')
    for k, (L, W, H, _) in SS.items():
        ASSETS[f'SS01_SteppingStone_{k}'] = dict(common, zh=f'半埋踏石 {k}', kind='stone', palette=palette, build=build_ss(k),
            limit=(L + .7, W + .7, H + .4), box=((-(L + .7) / 2, -(L + .7) / 2, -.15), ((L + .7) / 2, (L + .7) / 2, H + .3)), base_z=-.15, clamp_max=.06,
            ref=f'core-d2-models-v1/SS01/turnaround', slot='D2_AncientTree_SteppingStone',
            origin='centre of the stone at ground level z = 0; 15 cm buried below', note=f'Half-buried stepping stone {k} for the D2 mud paths; top {H} m above ground.')
    for k, (pts, r0, _, _) in SR.items():
        x0, x1 = pts[0][0] - r0 * 2.6, pts[-1][0] + r0 * 2.6; w = 1.6 + r0 * 4
        ASSETS[f'SR01_SurfaceRoot_{k}'] = dict(common, zh=f'地表盤根 {k}', kind='root', palette=palette, build=build_sr(k),
            limit=(x1 - x0, w * 2, 1.), box=((x0, -w, -.45), (x1, w, r0 * 2.4)), base_z={'A': -.073, 'B': -.074, 'C': -.082}[k], clamp_max=.5,
            ref=f'core-d2-models-v1/SR01/turnaround', slot='D2_AncientTree_SurfaceRoot',
            origin='centre at ground level z = 0; trunk end -X; both ends dive under the ground', note=f'Surface root {k}, girth {r0} m, half buried.')
    ASSETS['CO01_ExcavatedPit'] = dict(common, zh='被挖的坑', kind='pit', palette=palette, build=build_co01, tex=2048,
        limit=(APRON * 2, APRON * 2, 1.6), box=((-APRON, -APRON, -PIT_D - .05), (APRON, APRON, .7)), base_z=-1.018, clamp_max=.06,
        ref='core-d2-models-v1/CO01/turnaround', slot='D2_AncientTree_DugPit',
        origin='centre of the hole at ground level z = 0; edge of the apron at exactly z = 0', note='Freshly dug pit by the D2 altar, about 4 m across and 1 m deep, spoil heap on +X+Y.')
