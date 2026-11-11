"""AN01 cattle shed and feeding trough (work pack 2026-11-11 B-40h, batch B, AN01). No animals.

Chosen sheet AN01-cand-2 (backup cand-3): a lean-to shed of rough round timber, 6 m along x and 4 m deep. Eight posts on rough stone
footings carry a front and a back plate log; seven rafters run from the high back down to the low front, battens across them, a thick
straw thatch on top that ends in a ragged eave fringe; a ridge log and two holding poles lie on the thatch, tied down with rope.
The back (+Y, the weather side) is closed by a vertical plank wall; both sides have three rails between the corner posts and a short
middle post; the front is open except for rails in the left bay. A long plank feeding trough on trestles stands inside along the back
wall with hay in it; the floor is packed earth with straw scattered on it. Old grey timber, moss on the thatch. No writing.

Frame: ground z = 0, front (open side) -Y, centre of the footprint on the origin; the roof falls from +Y to -Y.
"""
import math, random
from mathutils import Vector
from ti_core import S, box, socket, mesh
from cr_parts import rbox, lash
import fr_parts as FP
import vl_mats, cr_mats as cm, ti_mats as tm, mk_mats as mm
import cw_parts as CP
import cw_wall as CW
import gn_granary as GN

W, D, H = 6.0, 4.0, 3.2
PX = (-2.62, -.88, .88, 2.62)        # post rows along x
FY, BY = -1.45, 1.5                  # front and back post lines
FOOT_TOP = .12                       # top of the stone footings
RX = 2.92                            # thatch along x to +-RX
EAVE_Y, BACK_Y = -1.8, 1.84         # thatch from the front eave to the back edge
SLOPE = .22                          # fall of the roof per metre towards the front (about 12 degrees)
THATCH = .24                         # thatch thickness
RAFTER_R, PLATE_R = .055, .08
RAFTER_X = (-2.78, -1.84, -.92, 0., .92, 1.84, 2.78)
TROUGH = dict(x=2.1, y=1.0, w=.62, top=.52)


def zr(y):
    """Top of the thatch at y (before the course steps and lumps)."""
    return 3.09 + (y - 1.72) * SLOPE


def z_rafter(y): return zr(y) - THATCH - .05 - RAFTER_R + .01
def z_plate(y): return z_rafter(y) - RAFTER_R - PLATE_R + .02


def shed_thatch(name, dark, light, slot='Main'):
    """Straw laid down a lean-to slope: streaks run along y (down the slope), bundles in soft patches (cr_mats.thatch runs around Z)."""
    m, g = tm._new(name, slot)
    P = g.geo('Position'); sep = g.node('ShaderNodeSeparateXYZ'); g.link(P, sep.inputs[0])
    X, Y, Z = sep.outputs['X'], sep.outputs['Y'], sep.outputs['Z']
    q = g.node('ShaderNodeCombineXYZ'); g.link(g.math('MULTIPLY', X, 12.0), q.inputs[0]); g.link(g.math('MULTIPLY', Y, .55), q.inputs[1])
    g.link(g.math('MULTIPLY', Z, .55), q.inputs[2])
    Q = q.outputs[0]
    strand = g.noise(Q, 34.0, 4, .6); bundle = g.noise(Q, 6.0, 3, .55); big = g.noise(P, 1.6, 3, .5)
    t = g.math('ADD', g.math('ADD', g.math('MULTIPLY', strand, .5), g.math('MULTIPLY', bundle, .28)), g.math('MULTIPLY', big, .22))
    col = g.ramp(t, [(.3, tuple(c * .6 for c in dark)), (.46, dark), (.66, light)])
    grey = g.maprange(big, .45, .62)
    col = g.mix(g.math('MULTIPLY', grey, .18), col, (.17, .155, .12))
    ao = g.ao(.08)
    col = g.mul(1.0, col, g.ramp(ao, [(0, (.3, .28, .26)), (1, (1, 1, 1))]))
    tm._finish(g, col, .92, 0.0, g.bump(strand, .9, .012), spec=.12)
    return m


def palette():
    P = CW.palette()
    P['log'] = cm.wood('Shed_Log', (.05, .03, .016), (.2, .12, .06), grey=.55, ground_h=.25, moss=True, moss_amt=.4)
    P['rafter'] = cm.wood('Shed_Rafter', (.045, .027, .014), (.18, .105, .05), grey=.4, ground_h=0., moss=False)
    P['plank'] = cm.wood('Shed_Plank', (.055, .033, .017), (.22, .13, .066), grey=.6, ground_h=.2, moss=False, grey_grain=True)
    P['trough'] = cm.wood('Trough_Plank', (.06, .038, .02), (.24, .15, .078), grey=.45, ground_h=.12, moss=False, polish=.2)
    P['patch'] = cm.wood('Shed_Patch', (.07, .045, .024), (.27, .17, .09), grey=.25, ground_h=.0)
    P['thatch'] = shed_thatch('Shed_Thatch', (.1, .068, .028), (.42, .3, .12))
    P['hay'] = shed_thatch('Trough_Hay', (.12, .09, .045), (.42, .34, .17))
    P['stalk'] = tm.plain('Straw_Stalk', (.42, .33, .16), rough=.75, noise=.35, scale=60.)
    P['floor'] = cm.packed_earth('Shed_Floor', dark=(.1, .075, .045), light=(.22, .165, .1), rough=.95, crumb=.6, wet_top=.0, wet_low=-.1, dry_low=3.,
                                 dry_top=4., strata_amt=0.)
    P['hemp'] = mm.hemp('Shed_Rope', (.2, .15, .075), twist=150.)
    P['iron'] = vl_mats.iron('Shed_Iron')
    return P


def pole(name, a, b, size, mat, seed, r=None, grain='y'):
    """A rough round timber between a and b (rbox rounded to a log, rotated in its own plane)."""
    a, b = Vector(a), Vector(b); d = b - a; L = d.length
    rot = Vector((0, 1, 0)).rotation_difference(d.normalized()).to_euler()
    return rbox(name, tuple((a + b) / 2), (size, L, size), mat, r=r or size * .42, amp=size * .05, freq=2.2, hew=0, seed=seed, div=.09, rot=tuple(rot),
                group='Wood', grain=grain)


# ------------------------------------------------------------------ frame
def frame(P, R):
    posts = [(x, y) for y in (FY, BY) for x in PX]
    for k, (x, y) in enumerate(posts):
        rbox('Footing', (x, y, FOOT_TOP / 2 - .01), (.4 + R.uniform(-.05, .05), .36 + R.uniform(-.04, .04), FOOT_TOP + .02), P['stone'][k % 3], r=.04, amp=.018,
             freq=2.5, chips=3, hew=3, seed=10 + k, div=.05, flat='z', taper=(.85, .85), rot=(0, 0, R.uniform(-.3, .3)), group='Stone')
        top = z_plate(y) + .03
        lean = (R.uniform(-.015, .015), R.uniform(-.015, .015))
        rbox('Post', (x + lean[0] / 2, y + lean[1] / 2, (FOOT_TOP + top) / 2), (.2, .2, top - FOOT_TOP + .02), P['log'], r=.085, amp=.01, freq=1.6, hew=0,
             seed=20 + k, div=.08, skew=lean, taper=(.92, .92), group='Wood', grain='z')
        lash('Post_Lash', (x, y, top - .22), (0, 0, 1), .1, .07, .009, P['hemp'], turns=3, seg=6, step=.025, group='Detail_Small')
    # side middle posts (short, carry the rails)
    for sx in (-1, 1):
        x = sx * PX[3]
        rbox('Footing', (x, 0., FOOT_TOP / 2 - .01), (.32, .3, FOOT_TOP + .02), P['stone'][1], r=.04, amp=.016, chips=2, hew=2, seed=30 + sx, div=.05, flat='z',
             taper=(.85, .85), group='Stone')
        rbox('Rail_Post', (x, 0., (FOOT_TOP + 1.32) / 2), (.15, .15, 1.32 - FOOT_TOP), P['log'], r=.06, amp=.008, freq=1.6, seed=34 + sx, div=.08,
             taper=(.9, .9), group='Wood', grain='z')
    # plates: front and back logs along x on the post tops
    for k, y in enumerate((FY, BY)):
        z = z_plate(y)
        rbox('Plate', (R.uniform(-.03, .03), y, z), (2 * RX - .22, 2 * PLATE_R, 2 * PLATE_R), P['log'], r=PLATE_R * .85, amp=.008, freq=1.2, seed=40 + k,
             div=.1, warp=None, group='Wood', grain='x')
    # rafters from the back edge down past the front plate
    for k, x in enumerate(RAFTER_X):
        a = (x, BACK_Y - .02, z_rafter(BACK_Y - .02)); b = (x, EAVE_Y + .22, z_rafter(EAVE_Y + .22))
        pole('Rafter', a, b, 2 * RAFTER_R, P['rafter'], 50 + k)
        for y in (FY, BY):
            lash('Rafter_Lash', (x, y, z_rafter(y) - .02), (1, 0, 0), RAFTER_R, .09, .008, P['hemp'], turns=2.5, seg=6, step=.025, group='Detail_Small')
    # battens across the rafters, just under the thatch
    for k, y in enumerate((-1.75, -1.15, -.55, .05, .65, 1.25)):
        z = z_rafter(y) + RAFTER_R + .022
        rbox('Batten', (R.uniform(-.02, .02), y, z), (2 * RX - .06, .05, .045), P['rafter'], r=.018, amp=.004, seed=60 + k, div=.12, group='Wood', grain='x')
    # knee braces: outer posts to the plates, both rows; the end posts to the side rafter
    for y in (FY, BY):
        for sx in (-1, 1):
            for x0, dx in ((sx * PX[3], -sx * .55), (sx * PX[2], sx * .5), (sx * PX[2], -sx * .5)):
                z = z_plate(y)
                pole('Knee_Brace', (x0 + math.copysign(.06, dx), y, z - .62), (x0 + dx, y, z - .06), .09, P['log'], 70 + int(x0 * 10), grain='z')
    for sx in (-1, 1):
        x = sx * PX[3]
        for y0, dy in ((FY, .6), (BY, -.6)):
            pole('Side_Brace', (x, y0 + math.copysign(.06, dy), z_plate(y0) - .6), (x, y0 + dy, z_rafter(y0 + dy) - .04), .09, P['log'], 80, grain='z')


# ------------------------------------------------------------------ thatch
def thatch(P, R):
    """Thick straw laid in lapped courses: each course thickens to its butt end, the next one starts above it, so the slope reads as
    steps; a cut eave edge as thick as the thatch with strands hanging out of it; thinner, ragged gable edges."""
    n, m = 60, 30
    Rt = random.Random('AN01-thatch')
    jag = [Rt.uniform(-.045, .045) + .03 * math.sin(i * 1.7) for i in range(n + 1)]
    side_jag = [(Rt.uniform(-.035, .035), Rt.uniform(-.035, .035)) for _ in range(m + 1)]
    courses = 7
    def top_z(x, y, tv, v):
        c = (tv * courses) % 1.
        calm = min(1., (BACK_Y - y) / .45)                                # flatter under the ridge log
        step = .055 * c ** 1.5 * calm
        lump = (.028 * math.sin(x * 2.3 + v * .7) + .014 * math.sin(x * 6.1 - v * 1.9) + .012 * math.sin(y * 4.3 + x * 1.1)) * calm
        return zr(y) + step + lump
    rows, eave = [], []
    for v in range(m + 1):
        tv = v / m
        top, bot = [], []
        for u in range(n + 1):
            tu = u / n
            x = -RX + 2 * RX * tu + (side_jag[v][0] if u == 0 else side_jag[v][1] if u == n else 0.)
            y = BACK_Y + (EAVE_Y + jag[u] - BACK_Y) * tv
            droop = .05 * max(0., (tv - .85) / .15) ** 2
            edge = 1. if 0 < u < n else .7
            zt = top_z(x, y, tv, v) - droop
            zb = zr(y) - THATCH * edge - droop + .012 * math.sin(x * 4.1 + v)
            if v == 0: zt = zr(y) + .01
            top.append((x, y, zt)); bot.append((x, y, zb))
            if v == m: eave.append((x, y, zt, zb))
        rows.append(top + bot[::-1])
    acc = CP.Acc()
    b = acc.grid(rows, closed=True)
    k2 = 2 * (n + 1)
    for end in (0, m):
        base = b + end * k2
        for u in range(n):
            acc.cap((base + u, base + u + 1, base + k2 - 1 - (u + 1), base + k2 - 1 - u))
    acc.make('Thatch', P['thatch'], smooth=True, group='Main', grain='y')
    # a ragged straw skirt under the cut eave: the butt ends of the last course hang out and down unevenly
    fr = CP.Acc(); nf = 220
    ys = [e[1] for e in eave]
    def eave_at(x):
        f = (x + RX) / (2 * RX) * n; i = max(0, min(n - 1, int(f))); t = f - i
        a, c = eave[i], eave[i + 1]
        return a[1] + (c[1] - a[1]) * t, a[2] + (c[2] - a[2]) * t, a[3] + (c[3] - a[3]) * t
    rows = [[], [], []]
    for i in range(nf + 1):
        x = -RX + .04 + (2 * RX - .08) * i / nf
        y, zt, zb = eave_at(x)
        L = Rt.uniform(.03, .1) + Rt.uniform(.02, .1) * (1 if i % 3 else .5)
        rows[0].append((x, y - .004, zt - .035))
        rows[1].append((x + Rt.uniform(-.015, .015), y - .03, zb - L * .35))
        rows[2].append((x + Rt.uniform(-.03, .03), y - .04 - L * .25, zb - L))
    fr.grid(rows)
    fr.make('Thatch_Fringe', P['thatch'], smooth=True, group='Main', grain='y', solid=.03)
    # ridge log on the back edge, two holding poles across the slope, tied down to the rafters
    zl = zr(1.7) - .02
    rbox('Ridge_Log', (0., 1.7, zl), (2 * RX + .06, .17, .17), P['log'], r=.075, amp=.008, freq=1.2, seed=90, div=.1, group='Wood', grain='x')
    for k, y in enumerate((.35, -1.05)):
        z = zr(y) + .07
        rbox('Hold_Pole', (0., y, z), (2 * RX - .3, .08, .08), P['rafter'], r=.034, amp=.004, freq=1.4, seed=95 + k, div=.12, group='Wood', grain='x')
        for x in RAFTER_X[1:-1]:
            lash('Hold_Lash', (x + .03, y, z), (1, 0, 0), .04, .06, .008, P['hemp'], turns=2, seg=6, step=.025, group='Detail_Small')
    for x in (-2.2, -.6, 1.0, 2.4):
        lash('Ridge_Lash', (x, 1.7, zl), (1, 0, 0), .085, .07, .009, P['hemp'], turns=2.5, seg=6, step=.025, group='Detail_Small')
    # moss lies along the slope
    nrm = Vector((0., SLOPE, 1.)).normalized()
    for k in range(12):
        x, y = R.uniform(-2.6, 2.6), R.uniform(-1.2, 1.5)               # more towards the shaded back, less on the sunny eave
        FP.moss_patch('Thatch_Moss', (x, y, zr(y) + .07), tuple(nrm), R.uniform(.18, .32), P['moss'], seed=600 + k, flat=.7, snap_each=True)


# ------------------------------------------------------------------ walls, rails, trough, floor
def walls(P, R):
    ztop = lambda s: z_plate(BY) - PLATE_R + .02
    GN.plank_wall(P, R, 'Back_Wall', -PX[3] + .1, PX[3] - .1, FOOT_TOP - .06, ztop, 'y', BY + .13, P['plank'], w=.24, th=.04, seed=7)
    for z in (.55, 1.65):
        rbox('Back_Wall_Batten', (0., BY + .17, z + R.uniform(-.02, .02)), (2 * PX[3] - .1, .05, .1), P['rafter'], r=.01, amp=.003, hew=2, seed=100 + int(z * 10),
             div=.1, group='Wood', grain='x')
    rbox('Wall_Patch', (-1.3, BY + .205, 1.15), (.5, .02, .16), P['patch'], r=.004, amp=.002, chips=1, seed=105, div=.06, rot=(0, .07, 0), group='Wood', grain='x')
    # side rails: three between the corner posts and the middle post
    for sx in (-1, 1):
        x = sx * (PX[3] + .1)
        for j, z in enumerate((.42, .8, 1.18)):
            for y0, y1 in ((FY, 0.), (0., BY)):
                a = (x, y0 + .03, z + R.uniform(-.02, .02)); b = (x, y1 - .03, z + R.uniform(-.02, .02))
                pole('Rail', a, b, .085, P['log'], 110 + j + int(y0 * 3) + sx, grain='y')
            for yp in (FY, BY):
                lash('Rail_Lash', (sx * (PX[3] + .055), yp, z), (0, 0, 1), .13, .06, .008, P['hemp'], turns=2, seg=6, step=.025, group='Detail_Small')
            lash('Rail_Lash', (sx * (PX[3] + .045), 0., z), (0, 0, 1), .1, .06, .008, P['hemp'], turns=2, seg=6, step=.025, group='Detail_Small')
    # front rails in the left bay only (the rest of the front stays open)
    y = FY - .1
    for j, z in enumerate((.42, .8, 1.18)):
        pole('Front_Rail', (PX[0] + .03, y, z + R.uniform(-.02, .02)), (PX[1] - .03, y, z + R.uniform(-.02, .02)), .085, P['log'], 120 + j, grain='x')
        for x in (PX[0], PX[1]):
            lash('Rail_Lash', (x, FY - .055, z), (0, 0, 1), .125, .06, .008, P['hemp'], turns=2, seg=6, step=.025, group='Detail_Small')


def trough(P, R):
    hx, y, w, top = TROUGH['x'], TROUGH['y'], TROUGH['w'], TROUGH['top']
    bot = .2
    # trestles: a cross piece on two short legs at both ends and the middle
    for k, x in enumerate((-hx + .35, 0., hx - .35)):
        rbox('Trestle_Bar', (x, y, bot - .05), (.1, w + .2, .08), P['rafter'], r=.012, amp=.004, hew=2, seed=130 + k, div=.08, group='Wood', grain='y')
        for sy in (-1, 1):
            rbox('Trestle_Leg', (x, y + sy * (w / 2 + .02), (bot - .09) / 2), (.09, .09, bot - .07), P['rafter'], r=.012, amp=.004, hew=2, seed=134 + k + sy,
                 div=.08, group='Wood', grain='z')
    # the box: a bottom board, two side boards leaning out a little, two thick end boards
    rbox('Trough_Bottom', (0., y, bot + .025), (2 * hx - .1, w - .12, .05), P['trough'], r=.008, amp=.003, seed=140, div=.1, group='Wood', grain='x')
    for sy in (-1, 1):
        lean = sy * .12
        rbox('Trough_Side', (0., y + sy * (w / 2 - .05), (bot + top) / 2 + .01), (2 * hx - .02, .05, top - bot + .02), P['trough'], r=.008, amp=.003, chips=2,
             seed=142 + sy, div=.1, rot=(-lean, 0, 0), group='Wood', grain='x')
        rbox('Trough_Rim', (0., y + sy * (w / 2 - .02), top + .02), (2 * hx + .02, .07, .04), P['trough'], r=.01, amp=.003, seed=146 + sy, div=.1,
             group='Wood', grain='x')
    for sx in (-1, 1):
        rbox('Trough_End', (sx * (hx - .02), y, (bot + top) / 2 + .02), (.07, w + .04, top - bot + .06), P['trough'], r=.01, amp=.003, chips=1, seed=150 + sx,
             div=.08, group='Wood', grain='z')
    # a split board nailed over the front side, two iron cramps at the end joints
    rbox('Trough_Patch', (-.55, y - w / 2 - .02, .36), (.42, .02, .13), P['patch'], r=.004, amp=.002, chips=1, seed=155, div=.06, rot=(.12, .08, 0),
         group='Wood', grain='x')
    for sx in (-1, 1):
        box('Trough_Cramp', (sx * (hx - .07), y - w / 2 - .03, top - .06), (.12, .012, .03), P['iron'], bevel=.002, group='Main')
    # hay heaped in the trough
    acc = CP.Acc(); rows = []
    for v in range(6):
        yy = y - (w / 2 - .1) + (w - .2) * v / 5
        rows.append([(-hx + .08 + (2 * hx - .16) * u / 30, yy, top - .1 + .07 * math.sin(math.pi * v / 5) + .03 * math.sin(u * 1.3 + v) + .02 * math.sin(u * .4))
                     for u in range(31)])
    acc.grid(rows)
    acc.make('Trough_Hay', P['hay'], smooth=True, group='Main', grain='y', solid=.06)
    socket('Socket_Trough', (0., y, top))


def floor(P, R):
    """Packed earth inside the shed: a grid pad 3 cm proud that feathers out to the ground over its last 0.3 m, straw scattered on it."""
    nx, ny = 32, 22
    X0, X1, Y0, Y1 = -2.9, 2.9, -1.92, 1.88
    Rf = random.Random('AN01-floor')
    jx = [(Rf.uniform(-.05, .05), Rf.uniform(-.05, .05)) for _ in range(ny + 1)]
    jy = [(Rf.uniform(-.05, .04), Rf.uniform(-.04, .05)) for _ in range(nx + 1)]
    rows = []
    for j in range(ny + 1):
        row = []
        for i in range(nx + 1):
            x = X0 + (X1 - X0) * i / nx; y = Y0 + (Y1 - Y0) * j / ny
            if i == 0: x += jx[j][0]
            if i == nx: x += jx[j][1]
            if j == 0: y += jy[i][0]
            if j == ny: y += jy[i][1]
            # square grid to a rounded rectangle (superellipse), so the pad has no sharp corners
            cx, cy = (X0 + X1) / 2, (Y0 + Y1) / 2; hx, hy = (X1 - X0) / 2, (Y1 - Y0) / 2
            u, w_ = (x - cx) / hx, (y - cy) / hy
            rs = max(abs(u), abs(w_)); re_ = (abs(u) ** 5 + abs(w_) ** 5) ** .2
            if re_ > 1e-6: x, y = cx + u * hx * rs / re_, cy + w_ * hy * rs / re_
            d = min(x - X0, X1 - x, y - Y0, Y1 - y)
            f = max(0., min(1., d / .3)); f = f * f * (3 - 2 * f)
            z = (.026 + .006 * math.sin(x * 5.1 + y * 3.3) + .004 * math.sin(x * 13.7 - y * 9.1)) * f
            row.append((x, y, z))
        rows.append(row)
    acc = CP.Acc(); acc.grid(rows)
    acc.make('Floor_Earth', P['floor'], smooth=True, group='Stone', grain='x', solid=.02)
    # straw: thin stalks, thick near the trough and the front, sparse elsewhere
    for k in range(260):
        if k < 140:
            x, y = R.uniform(-2.2, 2.2), R.uniform(.2, .62)
        elif k < 200:
            x, y = R.uniform(-2.6, 2.6), R.uniform(-1.6, .2)
        else:
            x, y = R.uniform(-2.7, 2.7), R.uniform(-1.82, -1.4)
        a = R.uniform(0, math.pi)
        box('Straw', (x, y, .042), (R.uniform(.12, .26), .006, .004), P['stalk'], bevel=0., rot=(0, R.uniform(-.1, .1), a), group='Detail_Small')
    for k in range(40):
        x, y = R.uniform(-1.9, 1.9), R.uniform(TROUGH['y'] - .2, TROUGH['y'] + .2)
        box('Straw', (x, y, TROUGH['top'] + .01), (R.uniform(.12, .22), .006, .004), P['stalk'], bevel=0., rot=(R.uniform(-.3, .3), 0, R.uniform(0, math.pi)),
            group='Detail_Small')


def growth(P, R):
    for _ in range(30):
        x, y = R.uniform(-2.95, 2.95), R.uniform(-1.95, 1.95)
        if abs(x) < 2.7 and abs(y) < 1.75: continue                    # nothing grows on the trodden floor
        FP.grass_tuft('Grass', (x, y, 0.), R.randint(5, 10), R.uniform(.1, .28), P['grass'] if R.random() < .7 else P['dry'], R, lean=.3, detail=1, spread=.03)
    for k, (x, y) in enumerate([(x, y) for y in (FY, BY) for x in PX]):
        a = R.uniform(0, math.tau)
        FP.grass_tuft('Post_Grass', (x + .25 * math.cos(a), y + .2 * math.sin(a), 0.), R.randint(5, 9), R.uniform(.12, .22), P['grass'], R, lean=.25,
                      detail=1, spread=.02)
        FP.moss_patch('Post_Moss', (x + R.choice((-.1, .1)), y, .3), (R.choice((-1, 1)), 0, .2), .06, P['moss'], seed=700 + k, flat=.6, snap_each=True)


def build(P):
    R = random.Random('AN01')
    frame(P, R); thatch(P, R); walls(P, R); trough(P, R); floor(P, R); growth(P, R)
    socket('Socket_Entrance', (0., FY - .3, 0.))
    S['collision_mesh'] = collision()
    S['part_notes'] = {'front_plate_underside_m': round(z_plate(FY) - PLATE_R, 3), 'back_plate_m': round(z_plate(BY), 3), 'roof_slope': SLOPE,
                       'thatch_m': {'x': 2 * RX, 'y': [EAVE_Y, BACK_Y]}, 'posts': 8, 'trough': TROUGH, 'animals': 'none (the pack forbids them)'}


def collision():
    V, F = [], []
    def prism(x0, x1, y0, y1, z0, z1):
        FP.hull_loft(V, F, [[(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)] for z in (z0, z1)])
    for y in (FY, BY):
        for x in PX:
            prism(x - .12, x + .12, y - .12, y + .12, 0., z_plate(y))
    prism(-PX[3] - .1, PX[3] + .1, BY + .08, BY + .2, 0., z_plate(BY))                    # back wall
    for sx in (-1, 1):
        prism(sx * (PX[3] + .1) - .06, sx * (PX[3] + .1) + .06, FY, BY, 0., 1.25)         # side rails
    prism(PX[0], PX[1], FY - .16, FY - .04, 0., 1.25)                                     # front rails, left bay
    prism(-TROUGH['x'], TROUGH['x'], TROUGH['y'] - TROUGH['w'] / 2 - .04, TROUGH['y'] + TROUGH['w'] / 2 + .04, 0., TROUGH['top'] + .04)
    # the roof: plates, rafters and thatch as one slab
    FP.hull_loft(V, F, [[(x, EAVE_Y, zr(EAVE_Y) - .1), (x, EAVE_Y, zr(EAVE_Y) + .05), (x, BACK_Y, zr(BACK_Y) + .05), (x, BACK_Y, z_plate(BY) - PLATE_R),
                          (x, FY, z_plate(FY) - PLATE_R)] for x in (-RX, RX)])
    return V, F


REG = dict(kind='shed', zh='牛棚與食槽（不含牛）', palette=palette, build=build, tex=2048, ver='v001',
           # the round timber (posts, rails, rafters, battens, back wall planks) covers about 93 m2: at 2048 that was 159 px/m, so wood bakes at 4096
           atlases={'Main': ['Main', 'Detail_Small'], 'Stone': ['Stone'], 'Wood': ['Wood']}, tex_atlas={'Wood': 4096},
           limit=[W, D, H], box=((-W / 2, -D / 2, 0.), (W / 2, D / 2, H)), slot='A1_VillageEdge_or_A6_Granary', ref='AN01/AN01-cand-2', clamp_max=.03,
           uv_detach_zero=True, origin='centre of the footprint on the ground, open front -Y, roof falls from +Y to -Y',
           method='procedural mesh construction (art/source/village-yards-b/an_shed.py, cw_parts.py, gn_granary.plank_wall); procedural shaders baked to three '
                  'atlases (Main, Stone 2048; Wood 4096)',
           based_on='original (Blender procedural); stone footings from the CW01 stone set; grass, moss, iron and rope from the VL set',
           note=('牛棚與食槽（三視圖 AN01-cand-2，備選 cand-3）：粗圓木搭的單坡棚，東西 6 m、進深 4 m。八根木柱立在粗石礎上，前後各一根橫樑木，'
                 '七根椽木從高的後簷斜到低的前簷，上面橫掛條、鋪厚稻草頂，前簷草尾參差下垂；草頂上壓一根脊木和兩根壓草杆，用麻繩綁在椽上，'
                 '一處補了新草。後面（迎風面）是直木板牆；兩側在角柱和中間短柱之間各三道橫欄；前面敞開，只在左邊一間有欄杆。'
                 '棚內沿後牆放一條木板長食槽，下墊三副木架，槽裡有乾草；地面是夯土，散著稻草。舊木發灰，草頂長青苔。不放牛，不寫字。'))


def register(ASSETS):
    ASSETS['AN01_CattleShed'] = dict(REG)


def shed_checks(aid, check, cfg):
    from vl_checks import _bvh
    lod0 = S['lods'][0]
    body = _bvh([o for g, o in lod0.items()])
    out = {}
    hb = body((0., 1.2, 6.), (0, 0, -1)); hf = body((0., -1.2, 6.), (0, 0, -1))
    check('lean_to_roof_falls_to_the_front', hb and hf and hb[0].z - hf[0].z > .4,
          {'roof_z_back_front_m': [round(hb[0].z, 3) if hb else None, round(hf[0].z, 3) if hf else None]})
    up = [body((x, FY, .5), (0, 0, 1)) for x in (-1.75, 0., 1.75)]
    zs = [round(h[0].z, 3) if h else None for h in up]
    check('front_headroom_over_1.8m', all(z is not None and z >= 1.8 for z in zs), {'underside_z_m': zs})
    # a 1.75 m capsule (r 0.3) walks in through the open front at x = 0 and stops at the trough
    hits = []
    for x in (-.3, 0., .3):
        for z in (.1, .45, .9, 1.3, 1.6, 1.75):
            h = body((x, -3., z), (0, 1, 0)); hits.append(round(h[0].y, 3) if h else None)
    first = min(y for y in hits if y is not None) if any(y is not None for y in hits) else None
    check('walk_in_1.75m_capsule_to_the_trough', first is not None and first > TROUGH['y'] - TROUGH['w'] / 2 - .1,
          {'first_hit_y_m': first, 'trough_front_y_m': round(TROUGH['y'] - TROUGH['w'] / 2, 3)})
    hy = body((0., TROUGH['y'], 1.5), (0, 0, -1))
    check('trough_with_hay_along_the_back', hy and .3 < hy[0].z < TROUGH['top'] + .1, {'hay_top_z_m': round(hy[0].z, 3) if hy else None})
    sides = [body((-4., y, 1.6), (1, 0, 0)) for y in (-.6, .6)]
    check('sides_open_above_the_rails', all(h is None for h in sides), {'hits': [tuple(round(c, 3) for c in h[0]) if h else None for h in sides]})
    bw = body((0., 4., 1.), (0, -1, 0))
    check('back_closed_by_the_plank_wall', bw and abs(bw[0].y - (BY + .15)) < .1, {'first_hit_y_m': round(bw[0].y, 3) if bw else None})
    out['first_hit_y_m'] = first
    return out
