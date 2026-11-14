"""GN01 raised granary (work pack 2026-11-11 B-40h, batch B, GN01; the batch sample).

Chosen sheet GN01-cand-2 (backup cand-3): a timber plank storehouse on six short posts that stand on rough stone pads; a flat stone
slab on each post top (the rat guard, 防鼠石板) under the sills, so the floor's underside is 0.6 m above the ground. Plank walls between
square corner and door posts with two horizontal girts outside; the floor runs out 0.3 m in front of the door as a ledge. Gable front
(-Y) with a small plank door, a wooden bar and an iron hasp; a woven bamboo vent in both gable triangles. A steep gable roof of the
pack's dark grey (#3A4048) pan-and-roll tiles on purlins and rafters, deep eaves on the long sides, barge boards at both gables.
A short wooden ladder leans on the ledge. Old weathered wood, two board patches, a woven patch on one side. No writing.

Frame: ground z = 0, front -Y, centre of the footprint on the origin; ridge along y.
"""
import math, random
from mathutils import Matrix, Vector
from ti_core import S, box, cyl, torus, socket, mesh, xf, T
from cr_parts import rbox, lash
import fr_parts as FP
import vl_mats, cr_mats as cm, ti_mats as tm, mk_mats as mm
import vl_roof as RF
import cw_parts as CP
import cw_wall as CW

W, D, H = 4.0, 4.0, 5.0
WX, WY = 1.24, 1.14                 # outer faces of the plank walls (x, y)
POST = .17
PAD_Z = .3                          # top of the stone pads
GUARD_Z = (.53, .6)                 # rat-guard slab on each post top
SILL = (.6, .8)                     # sills along y under the floor: their underside is the 0.6 m clearance
FLOOR_TOP = .98
PLATE_TOP = 3.4                     # wall plates (top of the walls)
LEDGE_Y = -1.46                     # front edge of the floor ledge before the door
ROOF = dict(half=1.92, z_eave=3.02, z_ridge=4.56)
RY = 1.74                           # roof (tiles) along y to +-1.74
DOOR = dict(half=.37, z0=FLOOR_TOP + .02, z1=2.36)
STILTS = [(sx * 1.08, y) for sx in (-1, 1) for y in (-1.0, 0., 1.0)]


def palette():
    P = CW.palette()
    P['timber'] = cm.wood('Granary_Timber', (.05, .028, .014), (.19, .108, .052), grey=.45, ground_h=.15, moss=False)
    P['plank'] = cm.wood('Granary_Plank', (.055, .033, .017), (.22, .13, .066), grey=.6, ground_h=.0, moss=False, grey_grain=True)
    P['door'] = cm.wood('Granary_Door', (.045, .026, .013), (.2, .115, .056), grey=.5, ground_h=.0)
    P['patch'] = cm.wood('Granary_Patch', (.07, .045, .024), (.27, .17, .09), grey=.25, ground_h=.0)
    P['ladder'] = cm.wood('Ladder_Pole', (.06, .036, .018), (.23, .14, .07), grey=.4, ground_h=.12, polish=.25)
    P['pad'] = [cm.stone(f'Pad_Stone_{i}', light=l, dark=d, ochre=(.22, .19, .14), moss=1.0, lichen=.6, crack=.5)
                for i, (l, d) in enumerate((((.23, .22, .2), (.1, .096, .088)), ((.21, .2, .185), (.09, .087, .08)), ((.25, .235, .21), (.11, .1, .09))))]
    P['guard'] = cm.stone('Rat_Guard', light=(.24, .23, .21), dark=(.1, .095, .088), ochre=(.2, .18, .14), moss=.35, lichen=.4, crack=.4)
    P['weave'] = tm.straw('Vent_Weave', light=(.32, .25, .13), dark=(.1, .072, .036), reed=.009, block=.05)
    P['iron'] = vl_mats.iron('Granary_Iron')
    P['hemp'] = mm.hemp('Granary_Rope', (.2, .15, .075), twist=150.)
    P['grain'] = tm.plain('Spilt_Grain', (.36, .27, .1), rough=.8, noise=.4, scale=40.)
    return P


# ------------------------------------------------------------------ helpers
def plank_wall(P, R, name, a, b, z0, ztop, normal, offset, mat, w=.19, th=.034, skip=None, seed=0, group='Wood'):
    """Vertical planks along one wall: the wall plane is at `offset` on the axis of `normal` ('x' or 'y'); planks run from a to b along the
    other axis. ztop(s) gives the top at position s (sloped for a gable). skip(s0, s1) -> True leaves a plank out (the door)."""
    n = max(1, int(round((b - a) / w))); step = (b - a) / n
    for k in range(n):
        s0, s1 = a + k * step + .003, a + (k + 1) * step - .003
        if skip and skip(s0, s1): continue
        t0, t1 = ztop(s0), ztop(s1)
        bot = z0 + R.uniform(0., .01)
        out = R.uniform(-.004, .004)
        acc = CP.Acc()
        def P3(s, z, d):
            return (offset + d, s, z) if normal == 'x' else (s, offset + d, z)
        sgn = 1.
        ring_out = [P3(s0, bot, out + th / 2), P3(s1, bot, out + th / 2), P3(s1, t1, out + th / 2), P3(s0, t0, out + th / 2)]
        ring_in = [P3(s0, bot, out - th / 2), P3(s1, bot, out - th / 2), P3(s1, t1, out - th / 2), P3(s0, t0, out - th / 2)]
        # subdivide the long sides so the bake and the bevel normals have something to hold
        m = max(2, int((max(t0, t1) - bot) / .3))
        rows = []
        for j in range(m + 1):
            f = j / m
            ro = [Vector(ring_out[0]).lerp(Vector(ring_out[3]), f), Vector(ring_out[1]).lerp(Vector(ring_out[2]), f)]
            ri = [Vector(ring_in[1]).lerp(Vector(ring_in[2]), f), Vector(ring_in[0]).lerp(Vector(ring_in[3]), f)]
            rows.append([tuple(p) for p in ro + ri])
        bb = acc.grid(rows, closed=True)
        acc.cap([bb + i for i in range(4)][::-1]); acc.cap([bb + m * 4 + i for i in range(4)])
        o = acc.make(f'{name}_Plank', mat, group=group, grain='z')
        if o is not None:
            md = o.modifiers.new('Bevel', 'BEVEL'); md.width = .005; md.segments = 1; md.limit_method = 'ANGLE'


def brace(name, a, b, mat, w=.08, h=.09, up=(1, 0, 0), group='Wood'):
    RF.sweep_box(name, [a, b], w, h, mat, up=up, group=group, grain='y')


# ------------------------------------------------------------------ base: stone pads, posts, rat guards, sills, floor
def base(P, R):
    for k, (x, y) in enumerate(STILTS):
        rbox('Pad', (x, y, PAD_Z / 2), (.52 + R.uniform(-.04, .04), .5 + R.uniform(-.04, .04), PAD_Z), P['pad'][k % 3], r=.05, amp=.022, freq=2.5,
             chips=4, hew=3, seed=100 + k, div=.05, flat='z', taper=(.86, .86), skew=(R.uniform(-.02, .02), R.uniform(-.02, .02)), group='Stone')
        rbox('Stilt', (x, y, (PAD_Z + GUARD_Z[0]) / 2), (.2, .2, GUARD_Z[0] - PAD_Z + .02), P['timber'], r=.012, amp=.004, hew=4, seed=110 + k, div=.06,
             group='Wood', grain='z')
        rbox('Rat_Guard', (x, y, sum(GUARD_Z) / 2), (.46, .46, GUARD_Z[1] - GUARD_Z[0]), P['guard'], r=.012, amp=.004, chips=2, hew=2, seed=120 + k,
             div=.06, flat='zZ', rot=(0, 0, R.uniform(-.12, .12)), group='Stone')
    for sx in (-1, 1):
        rbox('Sill', (sx * 1.08, 0., sum(SILL) / 2), (.22, 2 * WY + .14, SILL[1] - SILL[0]), P['timber'], r=.014, amp=.004, hew=4, seed=130 + sx, div=.07,
             group='Wood', grain='y')
    # floor joists across the sills and the floor boards on them; the boards run out front as a ledge
    for k, y in enumerate((-WY + .06, -.38, .38, WY - .06)):
        rbox('Floor_Joist', (0., y, SILL[1] + .07), (2 * WX + .14, .14, .14), P['timber'], r=.01, amp=.003, hew=3, seed=140 + k, div=.07, group='Wood', grain='x')
    zb = SILL[1] + .14
    nb = 14; wb = (2 * WX + .1) / nb
    for k in range(nb):
        x = -WX - .05 + (k + .5) * wb
        y0 = LEDGE_Y + R.uniform(-.015, .01) if abs(x) < .72 else -WY - .04
        rbox('Floor_Board', (x, (y0 + WY + .04) / 2, zb + .02), (wb - .008, WY + .04 - y0, .04), P['plank'], r=.006, amp=.003, chips=1, seed=150 + k, div=.12,
             group='Wood', grain='y')
    # the ledge is carried on two short beams run out from the front joist
    for sx in (-1, 1):
        rbox('Ledge_Beam', (sx * .62, (LEDGE_Y + .04 - WY) / 2, SILL[1] + .07), (.12, -WY - LEDGE_Y + .06, .14), P['timber'], r=.01, amp=.003, hew=2,
             seed=160 + sx, div=.07, group='Wood', grain='y')


# ------------------------------------------------------------------ walls, door, gables
def walls(P, R):
    t = P['timber']
    corners = [(sx * (WX - POST / 2), sy * (WY - POST / 2)) for sx in (-1, 1) for sy in (-1, 1)]
    for k, (x, y) in enumerate(corners):
        rbox('Corner_Post', (x, y, (SILL[1] + PLATE_TOP) / 2), (POST, POST, PLATE_TOP - SILL[1]), t, r=.012, amp=.004, freq=2., hew=4, seed=200 + k, div=.08,
             group='Wood', grain='z')
    for sx in (-1, 1):
        x = sx * (DOOR['half'] + .06)
        rbox('Door_Post', (x, -WY + .07, (FLOOR_TOP + PLATE_TOP) / 2), (.12, .14, PLATE_TOP - FLOOR_TOP), t, r=.01, amp=.003, hew=3, seed=210 + sx, div=.08,
             group='Wood', grain='z')
        rbox('Back_Mid_Post', (sx * .45, WY - .07, (FLOOR_TOP + PLATE_TOP) / 2), (.12, .14, PLATE_TOP - FLOOR_TOP), t, r=.01, amp=.003, hew=3, seed=214 + sx,
             div=.08, group='Wood', grain='z')
        rbox('Side_Mid_Post', (sx * (WX - .07), 0., (FLOOR_TOP + PLATE_TOP) / 2), (.14, .12, PLATE_TOP - FLOOR_TOP), t, r=.01, amp=.003, hew=3, seed=218 + sx,
             div=.08, group='Wood', grain='z')
    # wall plates on the long sides, tie beams over the gables
    for sx in (-1, 1):
        rbox('Wall_Plate', (sx * (WX - .08), 0., PLATE_TOP - .08), (.18, 2 * WY + .3, .16), t, r=.012, amp=.004, hew=3, seed=230 + sx, div=.08, group='Wood', grain='y')
    for sy in (-1, 1):
        rbox('Tie_Beam', (0., sy * (WY - .08), PLATE_TOP - .08), (2 * WX + .34, .18, .16), t, r=.012, amp=.004, hew=3, seed=234 + sy, div=.08, group='Wood', grain='x')
    # plank walls: planks sit in the wall plane, set back 2 cm from the post faces
    flat = lambda s: PLATE_TOP - .16
    dp = DOOR['half'] + .12                                  # outer face of the door posts
    plank_wall(P, R, 'Front', -WX + POST, -dp + .01, FLOOR_TOP, flat, 'y', -WY + .04, P['plank'], seed=1)
    plank_wall(P, R, 'Front', dp - .01, WX - POST, FLOOR_TOP, flat, 'y', -WY + .04, P['plank'], seed=11)
    plank_wall(P, R, 'Front_Over_Door', -dp + .01, dp - .01, DOOR['z1'] + .1, flat, 'y', -WY + .04, P['plank'], w=.2, seed=12)
    plank_wall(P, R, 'Back', -WX + POST, WX - POST, FLOOR_TOP, flat, 'y', WY - .04, P['plank'], seed=2)
    for sx in (-1, 1):
        plank_wall(P, R, f'Side_{sx}', -WY + POST, WY - POST, FLOOR_TOP, flat, 'x', sx * (WX - .04), P['plank'], seed=3 + sx)
    # girts outside the planks, at a third and two thirds of the wall
    for z in (1.62, 2.62):
        for sy in (-1, 1):
            for a, b in (((-WX + .02, -DOOR['half'] - .12), (DOOR['half'] + .12, WX - .02)) if sy < 0 else ((-WX + .02, WX - .02),)):
                rbox('Girt', ((a + b) / 2, sy * (WY + .005), z + R.uniform(-.01, .01)), (b - a, .05, .1), t, r=.008, amp=.003, hew=2, seed=240, div=.1, group='Wood', grain='x')
        for sx in (-1, 1):
            rbox('Girt', (sx * (WX + .005), 0., z + R.uniform(-.01, .01)), (.05, 2 * WY - .04, .1), t, r=.008, amp=.003, hew=2, seed=244, div=.1, group='Wood', grain='y')
    # patches: two boards nailed over splits, a woven mat on the right side
    rbox('Wall_Patch', (-.85, -WY - .022, 1.25), (.42, .02, .14), P['patch'], r=.004, amp=.002, chips=1, seed=250, div=.06, rot=(0, .06, 0), group='Wood', grain='x')
    rbox('Wall_Patch', (WX + .022, .55, 2.05), (.02, .5, .16), P['patch'], r=.004, amp=.002, chips=1, seed=251, div=.06, rot=(-.08, 0, 0), group='Wood', grain='y')
    box('Side_Mat', (-WX - .024, -.45, 2.05), (.016, .5, .46), P['weave'], bevel=.004, group='Main')
    rbox('Side_Mat_Lath', (-WX - .036, -.45, 2.3), (.02, .56, .04), P['patch'], r=.004, amp=.002, seed=252, div=.06, group='Wood', grain='y')
    rbox('Side_Mat_Lath', (-WX - .036, -.45, 1.8), (.02, .56, .04), P['patch'], r=.004, amp=.002, seed=253, div=.06, group='Wood', grain='y')


def gables(P, R):
    zt = CP.cap_profile(ROOF['half'], ROOF['z_eave'], ROOF['z_ridge'])
    for sy in (-1, 1):
        y = sy * (WY - .08)
        top = lambda s: zt(s) - .07
        # boards from the tie beam to under the roof boards, a square vent in the middle
        vent = (.32, PLATE_TOP + .18, PLATE_TOP + .62)
        plank_wall(P, R, f'Gable_{sy}', -WX + .02, WX - .02, PLATE_TOP, top, 'y', y + sy * .04, P['plank'], w=.2,
                   skip=lambda a, b: b > -vent[0] and a < vent[0], seed=20 + sy)
        # plank stubs over the vent
        plank_wall(P, R, f'Gable_Top_{sy}', -vent[0], vent[0], vent[2] + .06, top, 'y', y + sy * .04, P['plank'], w=.2, seed=24 + sy)
        plank_wall(P, R, f'Gable_Low_{sy}', -vent[0], vent[0], PLATE_TOP, lambda s: vent[1] - .06, 'y', y + sy * .04, P['plank'], w=.2, seed=26 + sy)
        cz = (vent[1] + vent[2]) / 2
        box('Vent_Weave', (0., y + sy * .03, cz), (2 * vent[0], .016, vent[2] - vent[1] + .04), P['weave'], bevel=.004, group='Main')
        for z in (vent[1] - .03, vent[2] + .03):
            rbox('Vent_Frame', (0., y + sy * .065, z), (2 * vent[0] + .1, .05, .06), P['timber'], r=.006, amp=.002, seed=270, div=.08, group='Wood', grain='x')
        for sx in (-1, 1):
            rbox('Vent_Frame', (sx * (vent[0] + .02), y + sy * .065, cz), (.06, .05, vent[2] - vent[1] + .12), P['timber'], r=.006, amp=.002, seed=272, div=.08,
                 group='Wood', grain='z')
        # king post from the tie beam to the ridge purlin
        rbox('King_Post', (0., y, (PLATE_TOP + zt(0.) - .2) / 2), (.12, .12, zt(0.) - .2 - PLATE_TOP), P['timber'], r=.01, amp=.003, hew=2, seed=274, div=.08,
             group='Wood', grain='z')


def door(P, R):
    z0, z1, hw = DOOR['z0'], DOOR['z1'], DOOR['half']
    y = -WY + .02
    # frame: lintel over the opening, sill board under it
    rbox('Door_Lintel', (0., y - .03, z1 + .07), (2 * hw + .4, .1, .14), P['timber'], r=.01, amp=.003, hew=2, seed=300, div=.08, group='Wood', grain='x')
    rbox('Door_Sill', (0., y - .02, z0 - .01), (2 * hw + .22, .12, .06), P['timber'], r=.008, amp=.003, seed=301, div=.08, group='Wood', grain='x')
    n = 4; wb = 2 * hw / n
    for k in range(n):
        x = -hw + (k + .5) * wb
        rbox('Door_Plank', (x, y, (z0 + z1) / 2 + .005), (wb - .002, .04, z1 - z0 - .01), P['door'], r=.006, amp=.003, chips=1 if k == 2 else 0, seed=310 + k,
             div=.1, group='Wood', grain='z')
    for z in (z0 + .25, z1 - .25):
        rbox('Door_Batten', (0., y - .032, z), (2 * hw - .06, .026, .11), P['door'], r=.006, amp=.002, seed=320, div=.08, group='Wood', grain='x')
    # a bar across the door in two iron staples, a hasp and a ring
    rbox('Door_Bar', (.05, y - .075, 1.66), (2 * hw + .34, .05, .07), P['patch'], r=.006, amp=.002, seed=330, div=.08, rot=(0, .015, 0), group='Wood', grain='x')
    for sx in (-1, 1):
        box('Bar_Staple', (sx * (hw + .1), y - .075, 1.66), (.03, .07, .1), P['iron'], bevel=.004, group='Main')
    box('Door_Hasp', (hw - .12, y - .046, 1.42), (.16, .008, .04), P['iron'], bevel=.002, group='Main')
    torus('Door_Ring', (-hw + .14, y - .05, 1.34), .045, .007, P['iron'], rot=(math.pi / 2, 0, 0), major=18, minor=6, group='Main')


# ------------------------------------------------------------------ roof
def tile_roof(P, name, x0, x1, half, z_eave, z_ridge, pitch=.24, roll_r=.055, courses=8, seed=0, group='Stone'):
    """Like cw_parts.tile_cap but sized for a house roof: the ridge runs along local x, pans and rolls run down both slopes in `courses`
    lapped courses, a ridge body and a round ridge tile with end discs. Boards are built by the caller (timber)."""
    Rt = random.Random(f'{name}:{seed}')
    zt = CP.cap_profile(half, z_eave, z_ridge)
    pans, rolls, discs = CP.Acc(), CP.Acc(), CP.Acc()
    n = max(2, int(round((x1 - x0) / pitch))); step = (x1 - x0) / n
    nv = courses * 2
    for side in (-1, 1):
        for i in range(n + 1):
            xc = x0 + i * step; xr = xc + step / 2
            jit = Rt.uniform(-.006, .006) if 0 < i < n else 0.
            xp = xc + jit; w = step * .5
            ua, ub = max(-1., (x0 - xp) / w), min(1., (x1 - xp) / w)
            rows = []
            for v in range(nv + 1):
                tt = v / nv; y = side * (.05 + (half + .02 - .05) * tt)
                lift = .008 * math.sin(tt * math.pi * courses) ** 2
                rows.append([(xp + (ua + (ub - ua) * u / 5) * w, y, zt(y) - .008 + .024 * (ua + (ub - ua) * u / 5) ** 2 + lift) for u in range(6)])
            pans.grid(rows)
            if i < n:
                rows = []
                ylen = half + .03
                for v in range(nv + 1):
                    tt = v / nv; y = side * (.04 + (ylen - .04) * tt)
                    r = roll_r * (1 + .08 * ((tt * courses) % 1.))
                    rows.append([(xr + jit + r * math.cos(math.pi * u / 6), y, zt(y) + .004 + r * math.sin(math.pi * u / 6) * .92) for u in range(7)])
                rolls.grid(rows)
                ye = side * ylen; rd = roll_r + .008
                discs.grid([[(xr + jit + rd * math.cos(math.tau * u / 12), ye, zt(ye) + .006 + rd * math.sin(math.tau * u / 12)) for u in range(12)],
                            [(xr + jit + rd * math.cos(math.tau * u / 12), ye + side * .016, zt(ye) + .006 + rd * math.sin(math.tau * u / 12)) for u in range(12)]],
                           closed=True)
                b = len(discs.V) - 24
                discs.cap([b + u for u in range(12)][::(-1 if side > 0 else 1)]); discs.cap([b + 12 + u for u in range(12)][::(1 if side > 0 else -1)])
    pans.make(name + '_Pans', P['captile'], smooth=True, group=group, grain='y', solid=.016)
    rolls.make(name + '_Rolls', P['captile'], smooth=True, group=group, grain='y', solid=.014)
    discs.make(name + '_EaveDiscs', P['captile'], smooth=False, group=group, grain='y')
    # ridge: a body of stacked tiles and a round ridge tile, end discs at both gables
    rbox(name + '_Ridge_Body', ((x0 + x1) / 2, 0., z_ridge + .03), (x1 - x0 + .04, .24, .14), P['captile'], r=.02, amp=.004, seed=seed, div=.1, flat='xX',
         group=group, grain='x')
    cyl(name + '_Ridge_Roll', ((x0 + x1) / 2, 0., z_ridge + .11), .075, x1 - x0 + .06, P['captile'], axis='x', verts=18, group=group, grain='x')
    for x in (x0 - .03, x1 + .03):
        cyl(name + '_Ridge_End', (x, 0., z_ridge + .11), .09, .03, P['captile'], axis='x', verts=18, group=group)


def roof(P, R):
    t = P['timber']
    zt = CP.cap_profile(ROOF['half'], ROOF['z_eave'], ROOF['z_ridge'])
    # boards across both slopes (ridge along y), 4 cm thick; rafters and purlins under them
    xs = [-(ROOF['half'] - .01) + 2 * (ROOF['half'] - .01) * i / 24 for i in range(25)]
    prof = [(x, zt(x) - .02) for x in xs] + [(x, zt(x) - .06) for x in xs[::-1]]
    with xf(Matrix.Rotation(math.pi / 2, 4, 'Z')):
        # in this frame local x is world y and local y is world -x
        CP.extrude_x('Roof_Boards', [(-x, z) for x, z in prof][::-1], -RY, RY, t, group='Wood', grain='x')
        tile_roof(P, 'Roof', -RY, RY, ROOF['half'], ROOF['z_eave'], ROOF['z_ridge'], seed=3, group='Tiles')
    for k, x in enumerate((-1.72, -.95, 0., .95, 1.72)):
        zz = zt(x) - .06
        rbox('Purlin', (x, 0., zz - .07), (.14, 2 * RY - .04, .14), t, r=.01, amp=.003, hew=2, seed=400 + k, div=.1, group='Wood', grain='y')
    # rafters: under the boards, seen in the eaves
    nr = 9
    for k in range(nr):
        y = -RY + .1 + (2 * RY - .2) * k / (nr - 1)
        for sx in (-1, 1):
            pts = [(sx * ROOF['half'] * q / 6, y, zt(ROOF['half'] * q / 6) - .06 - .04) for q in range(7)]
            RF.sweep_box('Rafter', pts, .06, .08, t, up=(0, 0, 1), group='Wood', grain='x')
    # barge boards at both gables
    for sy in (-1, 1):
        yb = sy * (RY + .03)
        for sx in (-1, 1):
            pts = [(sx * ROOF['half'] * q / 10, yb, zt(ROOF['half'] * q / 10) - .02) for q in range(11)]
            RF.sweep_box('Barge_Board', pts, .035, .16, t, up=(0, 0, 1), group='Wood', grain='x')
    # corner brackets: from each corner post up to the eave purlin
    for sx in (-1, 1):
        for sy in (-1, 1):
            a = (sx * (WX - .02), sy * (WY - POST / 2), PLATE_TOP - .5)
            b = (sx * 1.6, sy * (WY - POST / 2), zt(1.6) - .2)
            brace('Eave_Bracket', a, b, t, up=(0, 1, 0))
    # a plain hanging board (懸魚) under the apex of each gable, covering where the barge boards meet
    for sy in (-1, 1):
        yb = sy * (RY + .05)
        acc = CP.Acc(); zt0 = zt(0.) - .02
        outline = [(-.2, zt0 - .02), (0., zt0 + .04), (.2, zt0 - .02), (.11, zt0 - .42), (0., zt0 - .5), (-.11, zt0 - .42)]
        b0 = acc.grid([[(x, yb - .015, z) for x, z in outline], [(x, yb + .015, z) for x, z in outline]], closed=True)
        acc.cap([b0 + i for i in range(6)]); acc.cap([b0 + 6 + i for i in range(6)][::-1])
        acc.make('Gable_Board', t, group='Wood', grain='z')


# ------------------------------------------------------------------ ladder, ground, growth
def ladder(P, R):
    foot_y, top_y = -1.9, LEDGE_Y + .02
    top_z = FLOOR_TOP + .32
    for sx in (-1, 1):
        a = Vector((sx * .22, foot_y, 0.)); b = Vector((sx * .22 + sx * .01, top_y, top_z))
        L = (b - a).length; c = (a + b) / 2
        ang = math.atan2(b.y - a.y, b.z - a.z)
        cyl(f'Ladder_Rail_{sx}', tuple(c), .036, L, P['ladder'], verts=10, rot=(-ang, 0, 0), group='Wood', grain='z')
    for k in range(4):
        f = (k + .7) / 5.
        z = top_z * f; y = foot_y + (top_y - foot_y) * f
        cyl('Ladder_Rung', (0., y, z), .026, .52, P['ladder'], axis='x', verts=10, group='Wood', grain='x')
        for sx in (-1, 1):
            lash('Rung_Lash', (sx * .22, y, z), (0, -.45, .9), .04, .07, .007, P['hemp'], turns=3, seg=6, group='Detail_Small')


def growth(P, R):
    for _ in range(26):
        x, y = R.uniform(-1.8, 1.8), R.uniform(-1.8, 1.8)
        if any(abs(x - sx) < .32 and abs(y - sy) < .32 for sx, sy in STILTS): continue
        FP.grass_tuft('Grass', (x, y, 0.), R.randint(5, 10), R.uniform(.1, .26), P['grass'] if R.random() < .7 else P['dry'], R, lean=.3, detail=1, spread=.03)
    for k, (x, y) in enumerate(STILTS):
        for _ in range(2):
            a = R.uniform(0, math.tau)
            FP.grass_tuft('Pad_Grass', (x + .3 * math.cos(a), y + .3 * math.sin(a), 0.), R.randint(5, 9), R.uniform(.12, .24), P['grass'], R, lean=.25, detail=1,
                          spread=.02)
        FP.moss_patch('Pad_Moss', (x + R.choice((-.24, .24)), y, .1), (R.choice((-1, 1)), 0, .3), .09, P['moss'], seed=500 + k, flat=.6, snap_each=True)
    zt = CP.cap_profile(ROOF['half'], ROOF['z_eave'], ROOF['z_ridge'])
    for k in range(5):
        sx = R.choice((-1, 1)); x = sx * R.uniform(1.1, 1.75)
        sl = (zt(abs(x) - .05) - zt(abs(x) + .05)) / .1                 # the slope here: moss lies along the tiles, not flat
        nrm = Vector((sx * sl, 0., 1.)).normalized()
        FP.moss_patch('Roof_Moss', (x, R.uniform(-1.5, 1.5), zt(x) + .06), tuple(nrm), R.uniform(.08, .14), P['moss'], seed=520 + k, flat=.7, snap_each=True)
    # a few flat stones to step on at the ladder foot, spilt grain under the door
    for k, (x, y) in enumerate(((.1, -1.76), (-.38, -1.66), (.44, -1.62))):
        rbox('Step_Flag', (x, y, .025), (.34, .3, .05), P['pad'][k], r=.02, amp=.008, chips=2, hew=2, seed=540 + k, div=.05, flat='z', rot=(0, 0, R.uniform(-.4, .4)),
             group='Stone')
    for k in range(40):
        a = R.uniform(0, math.tau); r = R.uniform(0., .5)
        box('Grain', (r * math.cos(a) * 1.3, -1.6 + r * math.sin(a) * .4, .006), (.012, .007, .006), P['grain'], bevel=0., group='Detail_Small')
    for k in range(18):
        box('Grain', (R.uniform(-.5, .5), R.uniform(LEDGE_Y + .03, -WY - .06), FLOOR_TOP + .03), (.012, .007, .006), P['grain'], bevel=0., group='Detail_Small')


def build(P):
    R = random.Random('GN01')
    base(P, R); walls(P, R); gables(P, R); door(P, R); roof(P, R); ladder(P, R); growth(P, R)
    socket('Socket_Door', (0., LEDGE_Y + .1, FLOOR_TOP))
    socket('Socket_LadderFoot', (0., -1.9, 0.))
    S['collision_mesh'] = collision()
    S['part_notes'] = {'floor_underside_m': SILL[0], 'floor_top_m': FLOOR_TOP, 'wall_plate_top_m': PLATE_TOP, 'roof': ROOF, 'roof_along_y_m': RY,
                       'walls_m': {'x': 2 * WX, 'y': 2 * WY}, 'door': DOOR, 'stilts': len(STILTS),
                       'rat_guard': 'flat stone slab on every post top, under the sills (防鼠石板)'}


def collision():
    V, F = [], []
    def prism(x0, x1, y0, y1, z0, z1):
        FP.hull_loft(V, F, [[(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)] for z in (z0, z1)])
    for x, y in STILTS:
        prism(x - .26, x + .26, y - .25, y + .25, 0., PAD_Z)
        prism(x - .1, x + .1, y - .1, y + .1, PAD_Z, SILL[0])
    prism(-WX - .05, WX + .05, -WY - .05, WY + .05, SILL[0], PLATE_TOP)              # the store, from the 0.6 m underside up
    prism(-.75, .75, LEDGE_Y, -WY, SILL[1], FLOOR_TOP)                                 # the ledge
    prism(-.28, .28, -1.94, LEDGE_Y, 0., FLOOR_TOP + .3)                               # the ladder: not climbed, it stops you
    zt = CP.cap_profile(ROOF['half'], ROOF['z_eave'], ROOF['z_ridge'])
    FP.hull_loft(V, F, [[(-ROOF['half'], y, ROOF['z_eave'] - .1), (ROOF['half'], y, ROOF['z_eave'] - .1), (0., y, zt(0.))] for y in (-RY, RY)])
    return V, F


REG = dict(kind='granary', zh='穀倉（架高的糧囤）', palette=palette, build=build, tex=2048, ver='v001',
           # the plank walls (inside and out) and the tiles cover far more area than a 2048 holds at 256 px/m: wood bakes at 4096,
           # the tiles get their own 2048 atlas (one 2048 shared with the stone pads gave 145 px/m, wood 116 px/m)
           atlases={'Main': ['Main', 'Detail_Small'], 'Stone': ['Stone'], 'Wood': ['Wood'], 'Tiles': ['Tiles']}, tex_atlas={'Wood': 4096},
           limit=[W, D, H], box=((-W / 2, -D / 2, 0.), (W / 2, D / 2, H)), slot='A1_VillageEdge_or_A6_Granary', ref='GN01/GN01-cand-2', clamp_max=.03,
           uv_detach_zero=True, origin='centre of the footprint on the ground, front (door, ladder) -Y, ridge along y',
           method='procedural mesh construction (art/source/village-yards-b/gn_granary.py, cw_parts.py); procedural shaders baked to four atlases '
                  '(Main, Stone, Tiles 2048; Wood 4096)',
           based_on='original (Blender procedural); tiles the same #3A4048 pan-and-roll as CW01 / CW02; grass, moss, iron and rope from the VL set',
           note=('穀倉（三視圖 GN01-cand-2，備選 cand-3）：六根短木柱立在粗石礎上，每根柱頂墊一塊平石板（防鼠石板），上面是地檩和地板，地板底離地 0.6 m；'
                 '板牆夾在方木角柱、門柱之間，外面兩道橫帶；前山牆開一扇小木板門，門上一根橫閂、鐵扣和門環，門前地板外伸 0.3 m 當踏台，斜靠一把短木梯；'
                 '兩面山尖各一塊竹編通風窗。懸山瓦頂，瓦和 CW01／CW02 同一種黛瓦 #3A4048，兩側深出簷，檁條、椽子、博風板、角上斜撐。'
                 '舊木發灰，牆上釘兩塊補板、一面掛一張草蓆。不寫字。架高、有梯、方而高，遠看和民居的輪廓不同。'))


def register(ASSETS):
    ASSETS['GN01_RaisedGranary'] = dict(REG)


def granary_checks(aid, check, cfg):
    from vl_checks import _bvh
    lod0 = S['lods'][0]
    body = _bvh([o for g, o in lod0.items()])
    out = {}
    # the floor's underside is about 0.6 m up: look up from under the middle of the store
    hits = [body((x, y, .05), (0, 0, 1)) for x, y in ((-1.08, -.5), (-1.08, .5), (1.08, -.5), (1.08, .5))]   # under the sills, between the stilts
    zs = [round(h[0].z, 3) if h else None for h in hits]
    check('floor_raised_about_0.6m', all(z is not None and .55 <= z <= .68 for z in zs), {'underside_z_m': zs})
    # under the store you can see through between the posts
    thru = [body((-3., y, .45), (1, 0, 0)) for y in (-.5, .5)]
    check('open_under_the_floor', all(h is None or abs(h[0].x) > 1.9 for h in thru), {'first_hit_x_m': [round(h[0].x, 3) if h else None for h in thru]})
    ridge = [body((0., y, 6.), (0, 0, -1)) for y in (-1.2, 0., 1.2)]
    rz = [round(h[0].z, 3) if h else None for h in ridge]
    check('ridge_along_y_and_under_5m', all(z is not None and 4.4 < z <= H for z in rz) and max(rz) - min(rz) < .05, {'ridge_top_m': rz})
    eaves = [body((x, 0., 6.), (0, 0, -1)) for x in (-1.85, 1.85)]
    check('deep_eaves_on_both_sides', all(h and h[0].z > 2.8 for h in eaves), {'eave_z_m': [round(h[0].z, 3) if h else None for h in eaves]})
    dr = body((.15, -3., 1.9), (0, 1, 0))
    check('door_in_the_front_gable', dr and abs(dr[0].y - (-WY - .02)) < .12, {'first_hit_y_m': round(dr[0].y, 3) if dr else None})
    ld = [body((x, -3., .5), (0, 1, 0)) for x in (-.22, .22)]
    check('ladder_stands_in_front', all(h and h[0].y < LEDGE_Y for h in ld), {'first_hit_y_m': [round(h[0].y, 3) if h else None for h in ld]})
    out['underside_z_m'] = zs
    return out
