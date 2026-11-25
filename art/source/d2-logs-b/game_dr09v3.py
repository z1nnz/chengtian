# DR09 斷枝堆 v003（工作副本，先做 L 當樣品）：照「自然堆疊、輪廓清楚的林地枯木堆」修整。v002 的腳本、模型都不動。
# 做法：載入 game_dr09v2.py（它再載 game_dr09.py），在 v001 原始碼送進去執行前再改幾處，最後換掉幾個函式。
#
# 第一階段（灰模）
#   1. 2～3 根主要粗木（L：主枝直徑 28 cm＋21、17 cm 兩根），其餘明顯細一級（4.4～12 cm），視覺重心清楚。
#   2. 細枝約減三分之一以上：分岔、斷枝樁、細枝條、地上小枝都減量，中央不再交織成網。
#   3. 底層貼地（主木略陷），上層靠兩點支撐；L 懸空的段往下垂到接觸為止（沿用 v002）。翹頭的枝 7 → 4 根。
#   4. 懸空與穿插：檢查每根的接觸點（地面或別根 1.2 cm 內），報告沒有接觸的件；穿插沿用 v001／v002 的檢查。
#   5. 端點：斷口改成低矮不規則的斷裂面（齒高約 0.3 r），木刺只留粗枝 1～3 根、短；細枝枝梢收成鈍頭，不再是尖錐。
#   6. 粗細、長短、彎度拉開：長度範圍加寬，每根彎度隨機分直、微彎、彎三種。
# 第二階段（材質與接地）
#   1. 樹皮 UV：沿枝長 = u（木紋方向）；斷口側面改用沿軸＋繞圈展開（v002 用斜投影會拉伸），端面平面投影。
#   2. 斷面另外一圈頂點（不和樹皮共用），斷口是整片纖維色、硬邊，樹皮不會漫進斷口；剝皮只在撕裂那側一小段。
#   3. 苔：只在朝上的面、成塊（低頻雜訊切塊，不沿整根連成色帶），加上縫隙（AO 低、交叉點附近）積濕處。
#   4. 落葉：集中在木頭底部和交叉凹處，往外遞減；落葉土只沿貼地的粗木底下一窄條，不再是一整塊底座。
# 用法：blender -b --python art/source/d2-logs-b/game_dr09v3.py -- L
import sys, os, math, types, traceback
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')


def _v3_patch(src):
    """v001 原始碼（已套過 v002 的取代）再改幾處。每個取代都要找得到，找不到就停（避免靜悄悄沒改到）。"""
    R = [
        # 1. 主要粗木：主枝之後先放 V['big'] 指定的幾根，其餘照範圍
        ("radii = [V['main']] + sorted((r1 + (r2 - r1) * R.random() ** 1.5 for _ in range(n - 1)), reverse=True)",
         "radii = [V['main']] + list(V.get('big', ())) + sorted((r1 + (r2 - r1) * R.random() ** 1.5 for _ in range(n - 1 - len(V.get('big', ())))), reverse=True)"),
        # 6. 長短拉開
        ("length = min(r0 * U(R, 17, 26) + U(R, .15, .45), L * .78)", "length = min(r0 * U(R, 11, 30) + U(R, .08, .60), L * .80)"),
        # 2. 分岔、斷枝樁減量
        ("nf = 3 if r0 > .065 else (2 if r0 > .040 else 1)", "nf = 2 if r0 > .065 else (1 if r0 > .035 else 0)"),
        ("for _ in range(int(round(s[-1] * U(R, .6, 1.4)))):", "for _ in range(int(round(s[-1] * U(R, .25, .70)))):"),
        # 3. 翹頭的枝 L 7 → 4
        ("{'S': 3, 'M': 5, 'L': 7}[v]", "{'S': 3, 'M': 5, 'L': 4}[v]"),
        # 5. 木刺：只留粗枝 1～3 根、短
        ("k = R.randint(5, 8) if r[0 if e == 0 else -1] > .05 else (R.randint(3, 5) if r[0 if e == 0 else -1] > .03 else R.randint(1, 2))",
         "k = R.randint(1, 3) if r[0 if e == 0 else -1] > .06 else (R.randint(0, 1) if r[0 if e == 0 else -1] > .035 else 0)"),
        ("len=min(.36, rr * U(R, 1.0, 2.8)),", "len=min(.16, rr * U(R, .5, 1.3)),"),
        # 剝皮只一小段
        ("peel=[U(R, 1.2, 3.5), U(R, 1.2, 3.5)]", "peel=[U(R, .4, 1.1), U(R, .4, 1.1)]"),
        # 5. 斷口：低矮、不規則的齒（v001 的齒最高 0.65 r，像一圈尖刺）
        ("ln = rr * (.10 + .55 * max(0, math.cos(th - rec['tear'][e])) ** 2 * rng.uniform(.5, 1.3) + .10 * rng.random()) * rec['ext'][e]",
         "ln = rr * (.04 + .26 * max(0, math.cos(th - rec['tear'][e])) ** 2 * rng.uniform(.3, 1.2) + .16 * rng.random() ** 2) * min(rec['ext'][e], 1.1)"),
        # 5. 枝梢收成鈍頭
        ("c = mb.v(C[i] + Te * rr * (1.5 if kind == 'tip' and not col else 0), fib=0.0, mk=mk)",
         "c = mb.v(C[i] + Te * rr * (.45 if kind == 'tip' and not col else 0), fib=0.0, mk=mk)"),
        # 第二階段 2. 斷面另外一圈頂點（硬邊、整片纖維色），樹皮那圈不再被染成纖維色
        ("        ext = []\n        rng = random.Random(rec['seed'] + e)",
         "        ring = [mb.v(mb.V[j], fib=1.0, mk=0) for j in ring]          # v003：斷面自己的一圈點\n        ext = []\n        rng = random.Random(rec['seed'] + e)"),
        # 第二階段 1. 斷口側面（齒的外側）用沿軸＋繞圈展開；端面平面投影（不再斜投影）
        ("            return (sr_uv[i] + (float(q @ Tn) + .8 * float(q @ rdT)) * k_, v0 + float(q @ wvT) * k_)",
         "            return (sr_uv[i] + float(q @ rdT) * k_, v0 + float(q @ wvT) * k_)\n\n"
         "        def cuvs(ids):\n"
         "            out = []\n"
         "            for vid in ids:\n"
         "                q = np.array(mb.V[vid]) - Ci\n"
         "                out.append([sr_uv[i] + float(q @ Tn) * k_, math.atan2(float(q @ Be), float(q @ Ne)) * rr * k_])\n"
         "            vs = [o[1] for o in out]\n"
         "            if max(vs) - min(vs) > math.pi * rr * k_:\n"
         "                for o in out:\n"
         "                    if o[1] < 0:\n"
         "                        o[1] += 2 * math.pi * rr * k_\n"
         "            return [tuple(o) for o in out]"),
        ("            mb.f(qa, [cuv(x) for x in qa])", "            mb.f(qa, cuvs(qa))"),
    ]
    for a, b in R:
        assert a in src, a[:80]
        src = src.replace(a, b)
    return src


_v2 = open(HERE + '/game_dr09v2.py', encoding='utf-8').read()
_hook = "exec(compile(_src, ns['__file__'], 'exec'), ns)"
assert _hook in _v2
_v2 = _v2.replace(_hook, "exec(compile(_v3_patch(_src), ns['__file__'], 'exec'), ns)")
G = {'__name__': 'dr09_v2_for_v3', '__file__': HERE + '/game_dr09v2.py', '_v3_patch': _v3_patch}
exec(compile(_v2, G['__file__'], 'exec'), G)
ns = G['ns']
ns['VER'] = 'v003'
ns['VARIANTS']['L'].update(n=(12, 13), r=(.022, .060), main=.140, big=(.105, .085), twigs=14, litter=7, seed=9303)
ns['_xy_path2'] = ns['xy_path']
ns['_finish_body2'] = ns['finish_body']


def xy_path(R, c, ang, length, crook):
    """6. 彎度拉開：每根隨機直（0.35×）、微彎（0.8×）或彎（1.5×）。"""
    return _xy_path2(R, c, ang, length, crook * R.choice((.35, .8, .8, 1.5)))


def new_rec(R, kind, P, s, r, ends, parent=None, main=False):
    """v002 給主枝加了一大束長木刺；v003 不加（斷口只留少量撕裂纖維）。"""
    return _new_rec1(R, kind, P, s, r, ends, parent, main)


def finish_body(o, mb, lv):
    """第二階段 3. 苔：朝上的面成塊＋縫隙積濕處；不沿整根連成一條色帶。其他權重同 v002。"""
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
    nzA = np.array([noise.noise(Vector(p * 1.1)) for p in co])           # 塊（約 1 m 一個起伏）
    nzB = np.array([noise.noise(Vector(p * 3.3 + 7.0)) for p in co])     # 塊邊緣打散
    nz7 = np.array([noise.noise(Vector(p * 9.0 + 37.0)) for p in co])
    nz15 = np.array([noise.noise(Vector(p * 22.0 + 5.0)) for p in co])
    up = vn[:, 2]
    bark = (kind == 0) * (1 - fib)
    ao = vertex_ao(o, rays=14, dist=.30) if lv < 2 else np.ones(n)
    crev = sm(.78 - ao, 0, .25)                                           # 被遮住的縫隙
    if CONTACTS:
        Cc = np.array(CONTACTS)
        dcon = np.min(np.linalg.norm(co[:, None, :] - Cc[None], axis=2), axis=1)
    else:
        dcon = np.full(n, 9.0)
    near = sm(.22 - dcon, 0, .14)                                         # 交叉點附近
    thick = sm(r0 / V['main'], .30, .70)
    patch = sm(nzA + .35 * nzB, -.05, .25)                                # 成塊、塊和塊之間有空
    moss_top = thick * sm(up, .20, .65) * patch
    moss_wet = sm(r0, .02, .05) * sm(up, -.30, .25) * np.maximum(crev, near) * sm(nzB, -.4, .1)
    moss = np.clip(np.maximum(moss_top, .85 * moss_wet), 0, 1) * bark
    lich = .55 * sm(r0, .020, .045) * sm(up, -.55, -.05) * sm(nz7 + .45 * nz15, .22, .36) * bark * (1 - sm(moss, .2, .6))
    soil = sm(.06 - co[:, 2], 0, .06) * .70 * (kind == 0)
    W = np.zeros((n, 5))
    W[:, 0] = moss
    W[:, 1] = lich * .90
    W[:, 2] = fib
    W[:, 4] = soil * (1 - moss)
    m1 = kind == 1
    W[m1] = 0
    W[m1, 4] = 1.0
    W[m1, 0] = .25 * sm(nzA[m1] + .3 * nzB[m1], .35, .60)
    s = W.sum(1, keepdims=True)
    W = np.where(s > 1, W / np.maximum(s, 1e-6), W)
    ao2 = ao * (.72 + .28 * sm(co[:, 2], -.02, .16))
    vi = _loops(me)
    ca = me.color_attributes.new('Layers', 'FLOAT_COLOR', 'CORNER')
    ca.data.foreach_set('color', W[vi, :4].astype(np.float32).ravel())
    me.color_attributes.active_color = ca
    me.uv_layers.new(name='Extra').data.foreach_set('uv', np.stack([W[vi, 4], ao2[vi]], -1).astype(np.float32).ravel())
    me.uv_layers.active_index = 0
    for l in me.uv_layers:
        l.active_render = l.name == 'UVMap'
    print('LAYERS lod', lv, 'moss', round(float((moss > .5).mean()), 3), 'wet', round(float((moss_wet > .5).mean()), 3), 'lichen', round(float((lich > .5).mean()), 3))


def mound(mb, lv):
    """第二階段 4. 落葉土只沿貼地粗木的底下一窄條（不是一整塊底座），外緣埋進地面。"""
    br = [x for x in RECS if x['kind'] in ('branch', 'fork') and not x.get('dead') and x['r0'] > .03]
    pts = np.vstack([np.c_[x['P'][::2], x['r'][::2]] for x in br])
    pts = pts[pts[:, 2] - pts[:, 3] < .05]                                 # 只有貼地那段
    if not len(pts):
        return
    pad = .18
    lo, hi = pts[:, :2].min(0) - pad, pts[:, :2].max(0) + pad
    sp = {0: .07, 1: .14, 2: .28}[lv]
    nx, ny = int((hi[0] - lo[0]) / sp) + 1, int((hi[1] - lo[1]) / sp) + 1
    H = V['mound']
    grid = {}
    hs = np.zeros((nx, ny))
    for ix in range(nx):
        for iy in range(ny):
            x, y = lo[0] + ix * sp, lo[1] + iy * sp
            d = np.min(np.hypot(pts[:, 0] - x, pts[:, 1] - y) - pts[:, 3])
            d += .06 * noise.noise(Vector((x * 2.0, y * 2.0, 9.7)))
            f = float(sm(.07 - d, 0, .10)) * float(sm(noise.noise(Vector((x * 1.7, y * 1.7, 2.3))), -.25, .15))   # 只在木頭邊、斷續
            nn = .65 + .35 * noise.noise(Vector((x * 3.1, y * 3.1, 5.1)))
            hs[ix, iy] = H * .7 * f * nn - .012
    for ix in range(nx - 1):
        for iy in range(ny - 1):
            q = [(ix, iy), (ix + 1, iy), (ix + 1, iy + 1), (ix, iy + 1)]
            if max(hs[a, b] for a, b in q) < -.004:
                continue
            ids = []
            for a, b in q:
                if (a, b) not in grid:
                    x, y = lo[0] + a * sp, lo[1] + b * sp
                    grid[(a, b)] = mb.v((x, y, max(hs[a, b], -.012)), kind=1)
                ids.append(grid[(a, b)])
            mb.f(ids, [(lo[0] + a * sp, lo[1] + b * sp) for a, b in q], kind=1)


def make_cards(body0):
    """第二階段 4. 落葉：靠木頭底部（貼地段）和交叉凹處，離木頭越遠越稀；不鋪滿。"""
    R = random.Random(V['seed'] + 7)
    rects = lib8()['rects']()
    cat = lambda c: [r['uv'] for r in rects if r['cat'] == c]
    leaves, mush, fern = cat('leaf'), cat('mush'), cat('fern')
    me = body0.data
    co = [body0.matrix_world @ v.co for v in me.vertices]
    tree = BVHTree.FromPolygons(co, [tuple(p.vertices) for p in me.polygons])
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
        h = U(R, .09, .15) * big
        w = h * asp
        base = U(R, .004, .020)
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
    low = np.vstack([np.c_[x['P'][::2], x['r'][::2]] for x in br])
    low = low[low[:, 2] - low[:, 3] < .06]                                # 貼地的木頭底部
    allP = np.vstack([x['P'] for x in br])
    lo, hi = allP[:, :2].min(0) - .35, allP[:, :2].max(0) + .35
    nl = int((hi[0] - lo[0]) * (hi[1] - lo[1]) * 22)
    placed = 0
    for _ in range(nl * 6):
        if placed >= nl:
            break
        x, y = U(R, lo[0], hi[0]), U(R, lo[1], hi[1])
        d = float(np.min(np.hypot(low[:, 0] - x, low[:, 1] - y) - low[:, 3])) if len(low) else 9.0
        if R.random() > .015 + .985 * math.exp(-max(d, 0) / .09):           # 木頭邊最密，往外遞減
            continue
        h = tree.ray_cast(Vector((x, y, 3)), Vector((0, 0, -1)), 6)
        if h[0] is None:
            h = (Vector((x, y, .004)), Vector((0, 0, 1)), 0, 0)
        elif h[0].z > .10:                                                # 打到上層的木頭：葉子落到它底下的地面
            g = tree.ray_cast(Vector((x, y, .25)), Vector((0, 0, -1)), .5)
            if g[0] is None or g[0].z > .06 or g[1].z < .5:
                continue
            h = g
        if h[1].z < .40:
            continue
        p = Vector((h[0].x, h[0].y, max(h[0].z, .004)))
        n = (h[1] + Vector((U(R, -.30, .30), U(R, -.30, .30), 0))).normalized()
        if put_leaf(p, n):
            placed += 1
    tl = 0
    for c in CONTACTS:                                                     # 交叉的凹處卡幾片
        if c[2] > V['H'] * .55:
            continue
        for _ in range(R.randint(1, 3)):
            q = Vector(c) + Vector((U(R, -.08, .08), U(R, -.08, .08), 0))
            h = tree.ray_cast(q + Vector((0, 0, .5)), Vector((0, 0, -1)), 1.2)
            if h[0] is None or h[1].z < .3:
                continue
            tow = Vector(c) - h[0]
            tow.z = 0
            n = (h[1] + tow.normalized() * .6 if tow.length > 1e-3 else h[1]).normalized()
            if put_leaf(h[0], n, 1.0, .02):
                tl += 1
    nm = 0
    mainr = RECS[0]
    for k in range(2):                                                     # 主枝貼地那側的小褐蕈（積濕處）
        i = int(len(mainr['P']) * U(R, .2 + .35 * k, .45 + .35 * k))
        T, N0, B0 = frame_at(mainr['P'], i)
        sd = N0 * R.choice((-1, 1))
        for _ in range(R.randint(2, 3)):
            b = mainr['P'][i] + sd * (mainr['r'][i] + U(R, .02, .06)) + T * U(R, -.06, .06)
            h = tree.ray_cast(Vector((b[0], b[1], 1.5)), Vector((0, 0, -1)), 3)
            if h[0] is None or h[0].z > .10:
                continue
            q0 = len(C.V)
            C.upright(Vector((h[0].x, h[0].y, max(h[0].z, 0) - .008)), U(R, .07, .11), U(R, .07, .10), R.choice(mush), U(R, 0, math.pi), tag)
            if ok_pts(C.V[q0 + 2:q0 + 4] + C.V[q0 + 6:q0 + 8]):
                tag += 1
                nm += 1
            else:
                del C.V[q0:], C.UV[q0:]
                del C.F[-2:], C.tag[-2:]
    print('CARDS leaves', placed, 'trapped', tl, 'mush', nm)
    return C


def contact_report():
    """第一階段 4. 每根粗枝的接觸點：地面（底面離地 1.2 cm 內）或別根（表面距離 1.2 cm 內）。沒有接觸 = 懸空。"""
    out = []
    for rec in RECS:
        if rec.get('dead') or rec['kind'] != 'branch':
            continue
        P, r = rec['P'], rec['r']
        ground = (P[:, 2] - r) < .012
        c = clearance(P, r, _excl(rec))
        touch = ground | (c < .012)
        runs = int(np.sum(np.diff(np.r_[0, touch.astype(int)]) == 1))   # 接觸段數
        out.append(dict(id=rec['id'], d_cm=round(rec['r0'] * 200, 1), contacts=runs, ground=bool(ground.any())))
    float_ = [o for o in out if o['contacts'] == 0]
    one = [o for o in out if o['contacts'] == 1 and not o['ground']]
    print('CONTACTS', out)
    print('FLOATING', float_, 'ONE_CONTACT_NOT_GROUND', one)
    return dict(branches=len(out), floating=len(float_), single_contact_off_ground=len(one))


for f in (xy_path, new_rec, finish_body, mound, make_cards, contact_report):
    ns[f.__name__] = types.FunctionType(f.__code__, ns, f.__name__, f.__defaults__, f.__closure__)

_run = ns['run']


def run(v):
    _run(v)
    rep = ns['contact_report']()
    import bpy as _b
    _b.context.scene['dr09_v3_contacts'] = __import__('json').dumps(rep)
    _b.ops.wm.save_as_mainfile(filepath=f"{HERE}/blend/{ns['NAMES'][v]}_v003.blend", copy=True)
    print('CONTACT_SUMMARY', rep)


if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    try:
        run(a[0] if a else 'L')
    except Exception:
        traceback.print_exc()
        sys.exit(1)
