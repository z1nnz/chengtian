# DR09 斷枝堆 v002：照審查（v001 像度約 60%）修顏色和表面，擺法、不穿插、斷口、碰撞、LOD 的做法沿用 v001（game_dr09.py）。
# 這個檔把 game_dr09.py 載進來，只換下面幾個函式（換掉的函式照樣在 game_dr09.py 的命名空間裡跑），v001 的輸出不動：
#   1. 顏色：M_DR09_Layered_v002 換用 tex_dr09v2.py 的暖灰褐樹皮、橄欖苔、淺灰綠地衣（放 Rot 槽）、橘褐落葉土。
#   2. 苔和地衣：粗枝朝上那面一大片苔（主枝幾乎蓋滿頂面），其他枝朝上、朝側面散一塊塊淺灰綠地衣；斷口、木刺不長。
#   3. 枝的彎：平面路徑改成寬弧（不是短短一段急轉），粗枝再加一個往上拱的弓（兩頭著地、中段拱起，像彎曲的手臂）。
#   4. 斷口不再像空心管：中心往外推，刪「埋進別根的面」時不再拿自己的枝段比（v001 會把斷口那圈刪掉）。
#   5. S、M 的枝加粗；主枝斷口一大束長木刺；L 懸空的枝往下垂、垂到碰到別根為止（不在堆中間空出帳篷似的大洞）。
#   6. 落葉：堆底整片落葉土（量全部枝的投影，不只低處），落葉卡集中鋪在堆底和堆內，不往外撒一圈；主枝頂上幾朵小褐蕈。
# 用法（背景）：blender -b --python art/source/d2-logs-b/game_dr09v2.py -- M
import sys, os, types, math, traceback
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
ns = {'__name__': 'dr09_v001', '__file__': HERE + '/game_dr09.py'}
_src = open(ns['__file__'], encoding='utf-8').read()
# 斷口中心往外推（v001 中心只伸出 .22r，比撕裂那圈還縮，正對斷口看像一根空心管）
_src = _src.replace("cen = mb.v(C[i] + Te * rr * .22 * rec['ext'][e]", "cen = mb.v(C[i] + Te * rr * .50 * rec['ext'][e]")
assert "rr * .50 * rec['ext']" in _src
# 枝都水平一層層疊（斜角看像柴架、一片片平面）：斜靠翹頭的枝 S 1→3、M 2→5、L 3→7 根（參考圖的枝多半一頭著地、一頭搭在堆上），細枝往上翹一點、可以高出目標高 15%（參考圖 S 有往上的 Y 形枝梢）
for a, b in (("{'S': 1, 'M': 2, 'L': 3}[v]", "{'S': 3, 'M': 5, 'L': 7}[v]"),
             ("d = rd * .50 + T * .85 + np.array((0, 0, .05))", "d = rd * .50 + T * .85 + np.array((0, 0, .30 if V['v'] == 'S' else .05))"),
             ("(Pt[:, 2] + rt).max() < V['H'] * 1.02 and inside(Pt)", "(Pt[:, 2] + rt).max() < V['H'] * (1.15 if V['v'] == 'S' else 1.02) and inside(Pt)")):
    assert a in _src, a
    _src = _src.replace(a, b)
exec(compile(_src, ns['__file__'], 'exec'), ns)
ns['VER'] = 'v002'
for k, d in {'S': dict(mound=.085, margin=.15, r=(.028, .055), main=.065, twigs=16, lean=1, seed=9133), 'M': dict(mound=.080, margin=.19, r=(.035, .085), main=.105, twigs=30),
             'L': dict(mound=.100, margin=.22, twigs=45, seed=9309)}.items():           # S、M 的枝加粗一點（參考圖的枝比 v001 粗）
    ns['VARIANTS'][k].update(d)
ns['_tube1'] = ns['tube']
ns['_place_rigid1'] = ns['place_rigid']
ns['_new_rec1'] = ns['new_rec']


def layer_mat():
    m = bpy.data.materials.get('M_DR09_Layered_v002')
    if m:
        return m
    m = lib8()['layer_material']().copy()
    m.name = 'M_DR09_Layered_v002'
    T = TEXD9
    swap = {'DR08_Bark_Albedo.png': 'DR09_Bark_v002_Albedo', 'DR08_Moss_Albedo.png': 'DR09_Moss_v002_Albedo',
            'DR08_Rot_Albedo.png': 'DR09_Lichen_v002_Albedo', 'DR08_Soil_Albedo.png': 'DR09_Soil_v002_Albedo',
            'DR08_Fibre_Albedo.png': 'DR09_FreshWood_Albedo', 'DR08_Fibre_Normal.png': 'DR09_FreshWood_Normal'}
    for n in m.node_tree.nodes:
        if n.type == 'TEX_IMAGE' and n.image and n.image.name in swap:
            nrm = 'Normal' in n.image.name
            n.image = bpy.data.images.load(f'{T}/{swap[n.image.name]}.png', check_existing=True)
            if nrm:
                n.image.colorspace_settings.name = 'Non-Color'
    u = dict(m['unity'].to_dict()) if hasattr(m['unity'], 'to_dict') else dict(m['unity'])
    u['textures'] = ('DR09_Shared/Textures: DR09_Bark_v002_Albedo (bark), DR09_Moss_v002_Albedo (moss), DR09_Lichen_v002_Albedo (rot slot = lichen), '
                     'DR09_FreshWood_{Albedo,Normal} (fibre), DR09_Soil_v002_Albedo (soil); normals DR08_Shared/Textures/DR08_{Bark,Moss,Rot,Inner,Soil}_Normal + DR08_Inner_Albedo')
    m['unity'] = u
    return m


def new_rec(R, kind, P, s, r, ends, parent=None, main=False):
    """主枝的斷口：參考圖是一大束淺色長木刺炸開，比別根的斷口長、多。"""
    rec = _new_rec1(R, kind, P, s, r, ends, parent, main)
    if main:
        for e in (0, 1):
            if rec['ends'][e] != 'break':
                continue
            rec['ext'][e] = max(rec['ext'][e], 1.0) * 1.45
            rr = float(r[0 if e == 0 else -1])
            for sp in rec['splint'][e]:
                sp['len'] = min(.60, sp['len'] * 1.7)
            for _ in range(5):
                rec['splint'][e].append(dict(th=rec['tear'][e] + U(R, -1.6, 1.6), len=min(.60, rr * U(R, 2.0, 4.0)),
                                             w=max(.014, rr * U(R, .30, .55)), out=U(R, .0, .25)))
    return rec


def xy_path(R, c, ang, length, crook):
    """平面路徑：2–3 個寬弧（每個彎佔枝長約 20%），比 v001 的短急轉順，看起來是彎的不是折的。"""
    n = max(6, int(round(length / STEP)))
    nodes = R.randint(2, 3)
    knots = sorted(U(R, .18, .82) for _ in range(nodes))
    turns = [U(R, -crook, crook) * (1.6 if length < V['L'] * .7 or V['v'] != 'L' else .6) for _ in range(nodes)]   # L 的主枝（最長那根）只微彎，不然像一條蛇
    ds = length / n
    p = np.zeros(2)
    pts = [p.copy()]
    for i in range(n):
        t = (i + .5) / n
        a = ang + sum(tr * float(sm(t, k - .10, k + .10)) for tr, k in zip(turns, knots))
        p = p + np.array((math.cos(a), math.sin(a))) * ds
        pts.append(p.copy())
    pts = np.array(pts)
    return pts - pts.mean(0) + np.asarray(c), np.arange(n + 1) * ds


def place_rigid(Q, s, r, excl, sink, shape=None):
    """枝（不含地上小枝）加一個往上拱的弓：兩頭靠在支點上、中段拱起（主枝拱小一點，貼地躺著）。"""
    if shape is not None and s[-1] > .4:
        rs = np.random.RandomState(int(abs(Q[0, 0] * 7919 + Q[0, 1] * 104729 + s[-1] * 1e4)) % (2 ** 31))
        t = s / s[-1]
        A = min(rs.uniform(.06, .12) * s[-1], .30) * (.55 if sink > .2 else 1.0) * {'S': .55, 'M': 1.0, 'L': .5}[V['v']]
        c0 = rs.uniform(.35, .65)
        shape = shape + A * np.exp(-((t - c0) / .30) ** 2) - A * np.exp(-(.35 / .30) ** 2)
    P = _place_rigid1(Q, s, r, excl, sink, shape)
    if V['v'] == 'L' and shape is not None and s[-1] > .4:
        # L 的枝兩頭架在高處、中間懸空，堆中間空出一個大洞（像帳篷）。枝是彎的，懸空那段往下垂、搭到底下的枝或地上，
        # 垂到碰到別根的地方為止。
        sup = np.maximum(r * (1 - sink), support(Q, r, excl))
        gap = np.maximum(P[:, 2] - sup, 0)
        k = max(3, int(.80 / STEP)) | 1                     # 垂得緩（太急的彎，枝段取樣的弦會切進別根）
        drop = np.minimum(np.convolve(np.pad(gap * .70, k // 2, mode='edge'), np.ones(k) / k, 'valid'), gap)
        P0 = P
        for _ in range(8):                                    # 垂到碰到別根的地方就少垂一點（局部），不往上推（往上推會頂到上面的枝）
            P = P0.copy()
            P[:, 2] -= drop
            c = clearance(P, r, excl)
            bad = (c < .004).astype(float)                    # 留 4 mm（別根看這根是用每 9 cm 一段的弦）
            if not bad.any():
                break
            bad = np.convolve(np.pad(bad, k // 2, mode='edge'), np.ones(k) / k, 'valid') > 0
            drop = np.where(bad, drop * .35, drop)
        else:
            P = P0
    return P


def tube(mb, rec, lv, col=False):
    """同 v001；樹皮頂點的 mk 改存「r0（主枝 +1）」給 finish_body 分苔和地衣用。"""
    n0 = len(mb.V)
    _tube1(mb, rec, lv, col)
    if col:
        return
    if not hasattr(mb, 'own'):
        mb.own = []
    mb.own += [-1] * (n0 - len(mb.own)) + [rec['id']] * (len(mb.V) - n0)
    code = rec['r0'] + (1.0 if rec['main'] else 0.0)
    for i in range(n0, len(mb.V)):
        if mb.kind[i] == 0 and mb.fib[i] < .99:
            mb.mk[i] = code


def finish_body(o, mb, lv):
    me = o.data
    n = len(me.vertices)
    co = np.empty(n * 3, np.float32)
    me.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    vn = np.empty(n * 3, np.float32)
    me.vertices.foreach_get('normal', vn)
    vn = vn.reshape(-1, 3)
    fib, mk, kind = np.array(mb.fib), np.array(mb.mk), np.array(mb.kind)
    main = mk >= 1
    r0 = np.where(main, mk - 1, mk)
    nzA = np.array([noise.noise(Vector(p * 1.5)) for p in co])
    nz2 = np.array([noise.noise(Vector(p * 5.0 + 11.0)) for p in co])
    nz7 = np.array([noise.noise(Vector(p * 9.0 + 37.0)) for p in co])
    nz15 = np.array([noise.noise(Vector(p * 22.0 + 5.0)) for p in co])
    up = vn[:, 2]
    bark = (kind == 0) * (1 - fib)
    W = np.zeros((n, 5))
    # 苔：粗枝朝上那面一塊塊（越粗越多），主枝頂面幾乎蓋滿
    moss = sm(r0 / V['main'], .35, .75) * sm(up, -.05, .40) * sm(nzA + .30 * nz2, *((-.22, .12) if V['v'] == 'S' else (-.52, -.12)))   # S 的苔少一點（參考圖只有幾塊）
    moss_main = main * sm(up, -.20, .30) * sm(nzA + .25 * nz2, -.85, -.35)
    moss = np.maximum(moss, moss_main) * bark
    # 地衣：淺灰綠一塊塊的殼，朝上和朝側面都有，細枝也有一點
    lich = sm(r0, .020, .045) * sm(up, -.55, -.05) * sm(nz7 + .45 * nz15, .08, .26) * bark * (1 - sm(moss, .2, .6))
    soil = sm(.07 - co[:, 2], 0, .07) * .70 * (kind == 0)
    W[:, 0] = moss
    W[:, 1] = lich * .95
    W[:, 2] = fib
    W[:, 4] = soil * (1 - moss)
    m1 = kind == 1
    W[m1] = 0
    W[m1, 4] = 1.0
    W[m1, 0] = .30 * sm(nzA[m1] + .3 * nz2[m1], .35, .60)       # 落葉土上零星一點苔
    s = W.sum(1, keepdims=True)
    W = np.where(s > 1, W / np.maximum(s, 1e-6), W)
    ao = vertex_ao(o) if lv < 2 else np.ones(n)
    ao = ao * (.72 + .28 * sm(co[:, 2], -.02, .16))
    vi = _loops(me)
    ca = me.color_attributes.new('Layers', 'FLOAT_COLOR', 'CORNER')
    ca.data.foreach_set('color', W[vi, :4].astype(np.float32).ravel())
    me.color_attributes.active_color = ca
    me.uv_layers.new(name='Extra').data.foreach_set('uv', np.stack([W[vi, 4], ao[vi]], -1).astype(np.float32).ravel())
    me.uv_layers.active_index = 0
    for l in me.uv_layers:
        l.active_render = l.name == 'UVMap'
    print('LAYERS lod', lv, 'moss', round(float((moss > .5).mean()), 3), 'lichen', round(float((lich > .5).mean()), 3))


def mound(mb, lv):
    """堆底整片落葉土：量全部粗枝、分岔的投影（不只低處），中間厚、外緣收進地面；不往外鋪一大圈。"""
    br = [x for x in RECS if x['kind'] in ('branch', 'fork') and not x.get('dead')]
    pts = np.vstack([np.c_[x['P'][::2, :2], x['r'][::2]] for x in br])
    lo, hi = pts[:, :2].min(0) - V['margin'], pts[:, :2].max(0) + V['margin']
    sp = {0: .07, 1: .14, 2: .28}[lv]
    nx, ny = int((hi[0] - lo[0]) / sp) + 1, int((hi[1] - lo[1]) / sp) + 1
    H = V['mound']
    cen = pts[:, :2].mean(0)
    ext = np.maximum(np.abs(pts[:, :2] - cen).max(0), .1)
    grid = {}
    hs = np.zeros((nx, ny))
    for ix in range(nx):
        for iy in range(ny):
            x, y = lo[0] + ix * sp, lo[1] + iy * sp
            d = np.min(np.hypot(pts[:, 0] - x, pts[:, 1] - y) - pts[:, 2])
            d += V['margin'] * .35 * noise.noise(Vector((x * .9, y * .9, 9.7)))
            f = float(sm(V['margin'] * .6 - d, 0, V['margin'] * .9)) ** 1.2
            core = 1 - .45 * min(1.0, math.hypot((x - cen[0]) / ext[0], (y - cen[1]) / ext[1]))
            nn = .70 + .30 * noise.noise(Vector((x * 3.1, y * 3.1, 5.1)))
            hs[ix, iy] = H * f * nn * core - .012
    for ix in range(nx - 1):
        for iy in range(ny - 1):
            q = [(ix, iy), (ix + 1, iy), (ix + 1, iy + 1), (ix, iy + 1)]
            if max(hs[a, b] for a, b in q) < -.004:
                continue
            ids = []
            for a, b in q:
                if (a, b) not in grid:
                    x, y = lo[0] + a * sp, lo[1] + b * sp
                    grid[(a, b)] = mb.v((x, y, max(hs[a, b], -.020)), kind=1)
                ids.append(grid[(a, b)])
            mb.f(ids, [(lo[0] + a * sp, lo[1] + b * sp) for a, b in q], kind=1)


def hidden_faces(o, mb):
    """v001 拿每個頂點去比「所有」枝段，斷口那圈（離自己軸心不到 0.9r）被當成埋在自己裡面刪掉，斷口變成空心管。
    v002 只比別根（自己的母枝、子件照算：分岔、樁的根部埋在母枝裡的面還是刪）。"""
    me = o.data
    co = np.array(mb.V)
    own = np.array(mb.own + [-1] * (len(co) - len(mb.own)))
    inside = np.zeros(len(co), bool)
    a, b = SEG[:, :3], SEG[:, 3:6]
    ab = b - a
    L2 = (ab ** 2).sum(1) + 1e-12
    for k in range(0, len(co), 2000):
        P = co[k:k + 2000]
        u = np.clip(((P[:, None] - a[None]) * ab[None]).sum(2) / L2[None], 0, 1)
        d = np.linalg.norm(P[:, None] - (a[None] + u[..., None] * ab[None]), axis=2)
        rr = SEG[None, :, 6] + (SEG[None, :, 7] - SEG[None, :, 6]) * u
        other = OWN[None, :] != own[k:k + 2000, None]
        inside[k:k + 2000] = ((d < rr * .90 - .002) & other).any(1)
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    dead = [f for f in bm.faces if all(inside[v.index] for v in f.verts) and mb.fz[f.index] == 0]
    bmesh.ops.delete(bm, geom=dead, context='FACES_ONLY')
    loose = [v for v in bm.verts if not v.link_faces]
    keep = np.ones(len(co), bool)
    for v in loose:
        keep[v.index] = False
    bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.to_mesh(me)
    bm.free()
    for nm in ('fib', 'mk', 'kind'):
        setattr(mb, nm, [x for x, k in zip(getattr(mb, nm), keep) if k])
    return len(dead)


def make_cards(body0):
    R = random.Random(V['seed'] + 7)
    rects = lib8()['rects']()
    cat = lambda c: [r['uv'] for r in rects if r['cat'] == c]
    leaves, mush, fern = cat('leaf'), cat('mush'), cat('fern')
    me = body0.data
    co = [body0.matrix_world @ v.co for v in me.vertices]
    tree = BVHTree.FromPolygons(co, [tuple(p.vertices) for p in me.polygons])
    kinds = np.array([0] * len(me.polygons))
    C = Cards()
    tag = 0

    def ok_pts(pts):
        for q in pts:
            loc, nrm, _, d = tree.find_nearest(Vector(q))
            if loc is not None and (Vector(q) - loc).dot(nrm) < -.002 and d < .2:
                return False
        return True

    def put_leaf(p, n, big=1.0, curl=.012):
        nonlocal tag
        rc = R.choice(leaves)
        asp = (rc[2] - rc[0]) / max(rc[3] - rc[1], 1e-6)
        h = U(R, .09, .15) * big * {'S': .75, 'M': .9, 'L': 1.0}[V['v']]
        w = h * asp
        base = U(R, .004, .022)                                 # 疊在一起的葉高低錯開，不要同一層閃爍
        for lift in (base, base + .010, base + .022):
            q0 = len(C.V)
            C.leaf(Vector(p) + Vector(n) * lift, n, U(R, 0, 2 * math.pi), w, h, rc, tag, curl)
            if ok_pts(C.V[q0:]):
                tag += 1
                return True
            del C.V[q0:], C.UV[q0:]
            del C.F[-2:], C.tag[-2:]
        return False

    br = [x for x in RECS if x['kind'] in ('branch', 'fork') and not x.get('dead')]
    allP = np.vstack([x['P'] for x in br])
    lo, hi = allP[:, :2].min(0) - V['margin'], allP[:, :2].max(0) + V['margin']
    area = (hi[0] - lo[0]) * (hi[1] - lo[1])
    nl = int(area * {'S': 110, 'M': 90, 'L': 55}[V['v']])
    placed = bed = 0
    for _ in range(nl * 4):
        if placed >= nl:
            break
        x, y = U(R, lo[0], hi[0]), U(R, lo[1], hi[1])
        h = tree.ray_cast(Vector((x, y, 3)), Vector((0, 0, -1)), 6)
        if h[0] is None:                                          # 落葉土邊緣（埋進地面那圈）：離枝投影不遠就貼地面放
            dd = np.min(np.hypot(allP[:, 0] - x, allP[:, 1] - y))
            if dd > V['margin'] * .8:
                continue
            h = (Vector((x, y, .004)), Vector((0, 0, 1)), 0, 0)
        if h[1].z < .40:                                          # 只鋪在落葉土和枝上（外面地上不撒）
            continue
        if h[0].z < .004:                                         # 落葉土邊緣埋在地面下：葉子貼地面放（不要放到地下看不到）
            h = (Vector((h[0].x, h[0].y, .004)), Vector((0, 0, 1)), h[2], h[3])
        low = h[0].z < min(.14, V['H'] * .16)
        if not low and R.random() < .95:                          # 枝頂上只留少數幾片；其餘改放到這根枝底下的地面（從枝縫看得到堆底的葉）
            g = tree.ray_cast(Vector((x, y, .30)), Vector((0, 0, -1)), .6)
            if g[0] is None or g[0].z > .06 or g[1].z < .5:
                continue
            h = (Vector((x, y, max(g[0].z, .004))), g[1], g[2], g[3])
            low = True
        n = (h[1] + Vector((U(R, -.30, .30), U(R, -.30, .30), 0))).normalized()
        if put_leaf(h[0], n, 1.0 if low else .85):
            placed += 1
            bed += low
    tl = 0
    for c in CONTACTS:                                            # 夾在交叉處的落葉
        if c[2] > V["H"] * .30:
            continue
        for _ in range(R.randint(2, 4)):
            q = Vector(c) + Vector((U(R, -.10, .10), U(R, -.10, .10), 0))
            h = tree.ray_cast(q + Vector((0, 0, .6)), Vector((0, 0, -1)), 1.5)
            if h[0] is None:
                continue
            tow = (Vector(c) - h[0])
            tow.z = 0
            n = (h[1] + tow.normalized() * .6 if tow.length > 1e-3 else h[1]).normalized()
            if put_leaf(h[0], n, 1.05, .02):
                tl += 1
    nm = 0
    main = RECS[0]
    spots = {'S': 0, 'M': 2, 'L': 2}[V['v']]
    for k in range(spots):                                        # 主枝頂上（苔上）一叢小褐蕈
        i = int(len(main['P']) * U(R, .20 + .30 * k, .40 + .30 * k))
        top = main['P'][i] + np.array((0, 0, main['r'][i] * .96))
        for _ in range(R.randint(2, 3)):
            b = top + np.array((U(R, -.06, .06), U(R, -.04, .04), 0))
            h = tree.ray_cast(Vector((b[0], b[1], b[2] + .3)), Vector((0, 0, -1)), .6)
            if h[0] is None or h[1].z < .55:
                continue
            q0 = len(C.V)
            C.upright(h[0] - Vector((0, 0, .008)), U(R, .09, .14), U(R, .09, .13), R.choice(mush), U(R, 0, math.pi), tag)
            if ok_pts(C.V[q0 + 2:q0 + 4] + C.V[q0 + 6:q0 + 8]):
                tag += 1
                nm += 1
            else:
                del C.V[q0:], C.UV[q0:]
                del C.F[-2:], C.tag[-2:]
    nf = 0
    if V['v'] == 'L':
        for sx in (-1, 1):
            b = Vector((sx * (V['L'] / 2 - .10), U(R, -.3, .3) * V['W'] / 2, 0))
            h = tree.ray_cast(b + Vector((0, 0, 2)), Vector((0, 0, -1)), 4)
            if h[0] is None or h[0].z > .12:
                continue
            q0 = len(C.V)
            C.upright(h[0] - Vector((0, 0, .02)), U(R, .32, .42), U(R, .45, .55), R.choice(fern), U(R, 0, math.pi), tag,
                      lean=(sx * .25, 0, 0))
            if ok_pts(C.V[q0 + 2:q0 + 4] + C.V[q0 + 6:q0 + 8]):
                tag += 1
                nf += 1
            else:
                del C.V[q0:], C.UV[q0:]
                del C.F[-2:], C.tag[-2:]
    print('CARDS leaves', placed, 'bed', bed, 'trapped', tl, 'mush', nm, 'fern', nf)
    return C


for f in (layer_mat, new_rec, xy_path, place_rigid, tube, finish_body, mound, hidden_faces, make_cards):
    ns[f.__name__] = types.FunctionType(f.__code__, ns, f.__name__, f.__defaults__, f.__closure__)

if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    try:
        ns['run'](a[0] if a else 'M')
    except Exception:
        traceback.print_exc()
        sys.exit(1)
