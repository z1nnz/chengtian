# D2 林下雜草（z1nnz 11/21：地上的草重複率太高、要別的雜草）——由場景腳本在 plants.py 之後 exec
#   需要 bpy, math, Vector, LeafBuf, _frame, _leaf_material
#   每種都是一片片立體葉/草葉，不用貼圖卡；做成多個隨機變體給場景輪流用


def grass_tuft(name, pos, R, size=1.0, mat=None, dry=.0):
    """草叢：40–90 片細長草葉，從一點放射、往外彎垂；葉尖部分枯黃。"""
    buf = LeafBuf()
    n = R.randint(90, 160)
    for i in range(n):
        az = R.uniform(0, 6.283)
        lean = R.uniform(.1, .7)
        d = Vector((math.cos(az) * lean, math.sin(az) * lean, 1)).normalized()
        L = size * R.uniform(.22, .55)
        d, side, nrm = _frame(d)
        g = R.uniform(.8, 1.15)
        yel = dry * R.random()
        buf.leaf(pos + Vector((R.uniform(-.04, .04), R.uniform(-.04, .04), 0)), d, side, nrm, L, L * R.uniform(.025, .04),
                 shape=lambda u: (1 - u) ** .7, fold=.25, curl=0, droop=R.uniform(.25, .7),
                 tint=(g * (1 + yel * .9), g * (1 + yel * .4), g * (1 - yel * .5)), nu=7, nv=1, twist=R.uniform(-.6, .6))
    return buf.build(name, mat)


def sedge(name, pos, R, size=1.0, mat=None):
    """莎草：較高較挺的三稜葉，叢狀直立，葉尖下垂。"""
    buf = LeafBuf()
    n = R.randint(32, 52)
    for i in range(n):
        az = R.uniform(0, 6.283)
        lean = R.uniform(.05, .35)
        d = Vector((math.cos(az) * lean, math.sin(az) * lean, 1)).normalized()
        L = size * R.uniform(.45, .85)
        d, side, nrm = _frame(d)
        g = R.uniform(.85, 1.1)
        buf.leaf(pos + Vector((R.uniform(-.05, .05), R.uniform(-.05, .05), 0)), d, side, nrm, L, L * .035,
                 shape=lambda u: (1 - u) ** .5, fold=.45, curl=0, droop=R.uniform(.35, .8), tint=(g * .9, g, g * .8), nu=8, nv=1)
    return buf.build(name, mat)


def clover(name, pos, R, size=1.0, mat=None):
    """地被小草（酢漿草／三葉草類）：貼地的一片，細柄頂三片小圓心葉。"""
    buf = LeafBuf()
    n = R.randint(60, 100)
    for i in range(n):
        a = R.uniform(0, 6.283)
        r = size * .45 * R.uniform(0, 1) ** .6
        base = pos + Vector((math.cos(a) * r, math.sin(a) * r, size * R.uniform(.05, .15)))
        rot = R.uniform(0, 6.283)
        g = R.uniform(.85, 1.15)
        for k in range(3):
            az = rot + k * 2.094
            d = Vector((math.cos(az), math.sin(az), R.uniform(-.1, .15)))
            d, side, nrm = _frame(d)
            L = size * R.uniform(.055, .085)
            buf.leaf(base, d, side, nrm, L, L * .55, shape=lambda u: math.sin(math.pi * min(1, u)) ** .5 * (1 - .35 * max(0, u - .8) / .2),
                     fold=.25, curl=.05, droop=0, tint=(g, g, g), nu=5, nv=3)
    return buf.build(name, mat)


def rosette(name, pos, R, size=1.0, mat=None):
    """寬葉蓮座草（車前草類）：6–12 片橢圓寬葉貼地展開，中間抽一兩根細穗。"""
    buf = LeafBuf()
    n = R.randint(6, 12)
    for i in range(n):
        az = i / n * 6.283 + R.uniform(-.2, .2)
        d = Vector((math.cos(az), math.sin(az), R.uniform(.35, .8)))
        d, side, nrm = _frame(d)
        L = size * R.uniform(.18, .3)
        g = R.uniform(.85, 1.1)
        buf.leaf(pos, d, side, nrm, L, L * .42, shape=lambda u: math.sin(math.pi * min(1, u * 1.02)) ** .8,
                 fold=.2, curl=.1, droop=.25, tint=(g, g, g * .9), nu=8, nv=4, twist=R.uniform(-.3, .3))
    for k in range(R.randint(0, 2)):
        d = Vector((R.uniform(-.15, .15), R.uniform(-.15, .15), 1)).normalized()
        d, side, nrm = _frame(d)
        L = size * R.uniform(.25, .4)
        buf.leaf(pos, d, side, nrm, L, .006 * size, shape=lambda u: 1 if u < .6 else 2.2, fold=0, curl=0, droop=.05,
                 tint=(.7, .65, .45), nu=6, nv=1)
    return buf.build(name, mat)


def sapling(name, pos, R, size=1.0, mat=None, stem_mat=None):
    """小樹苗：一根細莖、幾段互生的卵形葉。"""
    buf = LeafBuf()
    H = size * R.uniform(.45, .9)
    lean = Vector((R.uniform(-.15, .15), R.uniform(-.15, .15), 1)).normalized()
    pts = [pos + lean * H * t + Vector((math.sin(t * 5) * .02, 0, 0)) for t in [i / 8 for i in range(9)]]
    nl = R.randint(7, 14)
    for k in range(nl):
        t = .3 + .7 * k / nl
        p = pts[int(t * 8)]
        az = k * 2.4
        d = Vector((math.cos(az), math.sin(az), .3))
        d, side, nrm = _frame(d)
        L = size * R.uniform(.13, .2) * (1.2 - t * .4)
        g = R.uniform(.85, 1.1)
        buf.leaf(p, d, side, nrm, L, L * .45, shape=lambda u: math.sin(math.pi * min(1, u)) ** .7 * (1 - u * .3),
                 fold=.15, curl=.1, droop=.3, tint=(g, g, g), nu=7, nv=3)
    o = buf.build(name, mat)
    if stem_mat:
        sv, sf = [], []
        for i, q in enumerate(pts):
            for j in range(3):
                a = j * 2.094
                sv.append(tuple(q + Vector((math.cos(a), math.sin(a), 0)) * .006 * size * (1 - i / 10)))
        for i in range(len(pts) - 1):
            for j in range(3):
                a = i * 3 + j
                sf.append((a, i * 3 + (j + 1) % 3, (i + 1) * 3 + (j + 1) % 3, (i + 1) * 3 + j))
        sm = bpy.data.meshes.new(name + '_stem')
        sm.from_pydata(sv, [], sf)
        sm.materials.append(stem_mat)
        so = bpy.data.objects.new(name + '_stem', sm)
        bpy.context.scene.collection.objects.link(so)
    return o


def weed_materials():
    return {
        'grass': _leaf_material('UG10_Grass', (.045, .075, .020, 1), (.12, .16, .05, 1), (.13, .17, .06, 1), gloss=.55),
        'sedge': _leaf_material('UG11_Sedge', (.035, .065, .025, 1), (.09, .14, .05, 1), (.10, .15, .06, 1), gloss=.5),
        'clover': _leaf_material('UG12_Clover', (.030, .075, .020, 1), (.075, .15, .045, 1), (.10, .17, .06, 1), gloss=.4),
        'rosette': _leaf_material('UG13_Rosette', (.040, .070, .022, 1), (.10, .15, .05, 1), (.14, .19, .08, 1), gloss=.4),
        'sapling': _leaf_material('UG14_Sapling', (.050, .085, .020, 1), (.13, .18, .05, 1), (.14, .19, .07, 1), gloss=.45),
    }
