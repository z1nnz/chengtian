# DR09 斷枝堆 v004（L 樣品）：照參考圖改成「粗壯腐木堆」——主幹厚重、盤曲、互相跨過，空隙清楚。
# v002、v003 的腳本和模型都不動（v003 是上一輪的修整稿，版號已用掉，這輪另存 v004）。
# 做法：載入 game_dr09v3.py（它再載 v2、v1），在 v001 原始碼執行前再改幾處（截面、扭轉、斷口），擺法 plan() 整個換掉。
#
# 第一階段（主體灰模）
#   1. 落葉、細枝、蘑菇、苔都不做（phase 1 只出主體）。
#   2. 主幹分三級：粗 A（直徑 38 cm）、中 B（28）、C0（24）、細 D（20）、E（15）；另 3 根 9～11 cm 的中枝。不是平均分布的一堆同粗圓管。
#   3. 主幹半徑沿長度有局部鼓脹（2～4 個節瘤段）、整根截面是不正的橢圓＋三瓣起伏，而且沿長度扭轉；
#      規劃用的半徑取外包（截面只往內縮），所以不會因為截面變形而穿進別根。
#   4. 拱：A 自己是彎的（往上拱，搭在底下的 C0 和地上）；B 用「彎曲上限」的包絡搭過 A 和 C0、兩側落地；
#      D 一頭著地、一頭搭在 A/B 上翹起（斷口朝上）。不靠細枝在上面搭三角架。
#   5. 每根主要木頭都要有兩處以上支撐（地面或別根），報告列出接觸段數。
#   6. 空隙：A 拱下（C0 兩側）、B 拱下、D 翹起段下方各一個，大小不同；中央不放細枝。
#   7. 斷口：粗木保留寬厚的斷面（斷面外緣 0.93 r、中心只微凸），撕裂纖維只在撕裂那側、長短不一（A 粗頭 6 根，其他 0～3 根）。
# 第二階段（次要細節）
#   1. 細枝只加在外圍、枝的遠端（輪廓上），中央方框內不加；地上小枝 5 根。
#   2. 樹皮 UV 跟著截面扭轉（紋理順著扭轉方向繞），沿枝長方向 = 木紋。
#   3. 斷面另外一圈頂點（沿用 v003），樹皮不包斷口。
#   4. 苔：朝上面成塊＋潮濕凹處（沿用 v003 的權重）；苔最厚的地方另外長一層薄殼幾何（邊緣貼平、中間厚 0.6～1.8 cm）。
#   5. 落葉：接地處和縫隙，往外遞減（沿用 v003）。
#   6. 蘑菇：只兩叢——A 粗頭頂上的苔裡一叢、B 落地那頭一叢。
# 用法：
#   blender -b --python art/source/d2-logs-b/game_dr09v4.py -- L 1   （第一階段：只存灰模 blend/…_v004_greybox.blend，不匯出）
#   blender -b --python art/source/d2-logs-b/game_dr09v4.py -- L 2   （完整：匯出 FBX／GLB、存 blend/…_v004.blend）
import sys, os, math, types, random, traceback, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')


def _v4_patch(src):
    R = [
        # 截面：不正的橢圓＋三瓣、沿長度扭轉（XS ≤ 1，只往內縮）
        ("            rj = rr\n", "            rj = rr * XS(rec, sr[i], th)\n"),
        # 樹皮 UV 跟著扭轉
        ("    circ = lambda i, j: 2 * math.pi * Rr[i] * j / ns * k_",
         "    circ = lambda i, j: (2 * math.pi * j / ns - TW(rec, sr[i])) * Rr[i] * k_"),
        # 粗枝多一點邊數（不規則截面才看得出來）
        ("        return int(np.clip(round(5 + r0 * 68), 5, 14))", "        return int(np.clip(round(5 + r0 * 68), 5, 16))"),
        ("        return int(np.clip(round(4 + r0 * 50), 5, 11))", "        return int(np.clip(round(4 + r0 * 50), 5, 12))"),
        # 斷口：粗木寬厚斷面
        ("ln = rr * (.04 + .26 * max(0, math.cos(th - rec['tear'][e])) ** 2 * rng.uniform(.3, 1.2) + .16 * rng.random() ** 2) * min(rec['ext'][e], 1.1)",
         "ln = rr * CAPLN(rec, e, th, rng)"),
        ("ext.append((mb.v(C[i] + Te * ln + d * rr * .80, fib=1.0, mk=0), ln))",
         "ext.append((mb.v(C[i] + Te * ln + d * rr * CAPW(rec) * XS(rec, sr[i], th), fib=1.0, mk=0), ln))"),
        ("cen = mb.v(C[i] + Te * rr * .50 * rec['ext'][e]", "cen = mb.v(C[i] + Te * rr * CAPC(rec) * rec['ext'][e]"),
        # 木刺厚度可調（粗木的木刺是楔形塊）
        ("    tk = max(.004, w * .22)", "    tk = max(.004, w * sp.get('tk', .22))"),
    ]
    for a, b in R:
        assert src.count(a) == 1, a[:80]
        src = src.replace(a, b)
    return src


_v3 = open(HERE + '/game_dr09v3.py', encoding='utf-8').read()
for a, b in (("\"exec(compile(_v3_patch(_src), ns['__file__'], 'exec'), ns)\"", "\"exec(compile(_v4_patch(_v3_patch(_src)), ns['__file__'], 'exec'), ns)\""),
             ("'_v3_patch': _v3_patch}", "'_v3_patch': _v3_patch, '_v4_patch': _v4_patch}")):
    assert _v3.count(a) == 1, a
    _v3 = _v3.replace(a, b)
H3 = {'__name__': 'dr09_v3_for_v4', '__file__': HERE + '/game_dr09v3.py', '_v4_patch': _v4_patch}
exec(compile(_v3, H3['__file__'], 'exec'), H3)
ns = H3['ns']
ns['VER'] = 'v004'
ns['VARIANTS']['L'].update(L=4.4, W=2.6, H=1.15, main=.19, mound=.09, margin=.22, twigs=10, litter=5, seed=9404)
ns['_make_cards3'] = ns['make_cards']
ns['_finish_body3'] = ns['finish_body']
ns['PHASE'] = 2


def XS(rec, s, th):
    x = rec.get('xs')
    if not x:
        return 1.0
    ph = th - x['tw0'] - x['twr'] * s
    return 1 - x['e'] * (1 - math.cos(2 * ph)) - x['h3'] * .5 * (1 - math.cos(3 * ph + x['p3']))


def TW(rec, s):
    x = rec.get('xs')
    return 0.0 if not x else x['tw0'] + x['twr'] * s


def CAPLN(rec, e, th, rng):
    c = max(0, math.cos(th - rec['tear'][e]))
    if rec.get('heavy'):
        return .06 + .55 * c ** 2 * rng.uniform(.35, 1.25) + .18 * rng.random() ** 2
    return (.04 + .26 * c ** 2 * rng.uniform(.3, 1.2) + .16 * rng.random() ** 2) * min(rec['ext'][e], 1.1)


def CAPW(rec):
    return .93 if rec.get('heavy') else .80


def CAPC(rec):
    return .16 if rec.get('heavy') else .50


# ---------------------------------------------------------------- 擺法
def spline_path(ctrl):
    """控制點（平面）→ Catmull-Rom 曲線，每 STEP 公尺取一點。"""
    C = np.array(ctrl, float)
    C = np.vstack([2 * C[0] - C[1], C, 2 * C[-1] - C[-2]])
    pts = []
    for k in range(1, len(C) - 2):
        p0, p1, p2, p3 = C[k - 1], C[k], C[k + 1], C[k + 2]
        for t in np.linspace(0, 1, 40, endpoint=False):
            t2, t3 = t * t, t * t * t
            pts.append(.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    pts.append(C[-2])
    pts = np.array(pts)
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    s = np.arange(0, seg[-1], STEP)
    s = np.r_[s, seg[-1]] if seg[-1] - s[-1] > STEP * .3 else np.r_[s[:-1], seg[-1]]
    Q = np.stack([np.interp(s, seg, pts[:, 0]), np.interp(s, seg, pts[:, 1])], -1)
    return Q, s


def heavy_radius(R, s, r0, taper, lumps):
    """粗木半徑：整體收細＋2～4 段節瘤鼓脹＋低頻起伏＋粗頭根部略張開。"""
    t = s / s[-1]
    r = r0 * (1 - taper * t)
    for _ in range(lumps):
        c = U(R, .12, .88) * s[-1]
        r = r * (1 + U(R, .05, .12) * np.exp(-((s - c) / (r0 * U(R, 1.4, 2.6))) ** 2))
    off = U(R, 0, 50)
    r = r * (1 + .06 * np.array([noise.noise(Vector((x * 1.3 + off, 3.1, 0))) for x in s]))
    r = r * (1 + .10 * sm(.08 - t, 0, .08))
    return r


def drape(Q, s, r, excl, sink, k, lift=None):
    """搭在底下的東西上：軸心 z = 支撐高度的包絡，彎曲不超過 k（z 落差 = k·距離²）；跨過別根、兩側落地。"""
    sup = np.maximum(r * (1 - sink), support(Q, r, excl))
    z = (sup[None, :] - k * (s[:, None] - s[None, :]) ** 2).max(1)
    if lift is not None:
        z = z + lift
    P = np.c_[Q, z]
    for _ in range(8):
        c = clearance(P, r, excl)
        if c.min() > -.002:
            break
        up = np.maximum(-c + .003, 0)
        kk = 9
        up = np.convolve(np.pad(up, kk // 2, mode='edge'), np.ones(kk) / kk, 'valid') * 1.6
        P[:, 2] += up
    return P


def xs_params(R, e=(.06, .12)):
    return dict(e=U(R, *e), tw0=U(R, 0, math.pi), twr=U(R, .35, .9) * R.choice((-1, 1)), h3=U(R, .03, .07), p3=U(R, 0, 6.28))


def heavy_splinters(R, rec, e, n, lmax):
    rr = float(rec['r'][0 if e == 0 else -1])
    out = []
    for k in range(n):
        long_ = k < max(1, n // 3)
        out.append(dict(th=rec['tear'][e] + U(R, -.75, .75), len=min(lmax, rr * (U(R, 1.1, 2.1) if long_ else U(R, .30, .80))),
                        w=max(.016, rr * U(R, .22, .42)), out=U(R, 0, .10), tk=U(R, .40, .65)))
    rec['splint'][e] = out


def add_fork(R, rec, t, side, fl, zr, frac=(.50, .62)):
    P, s, r = rec['P'], rec['s'], rec['r']
    i = int(len(P) * t)
    T, N0, B0 = frame_at(P, i)
    a = math.atan2(T[1], T[0]) + side * U(R, .45, .70)
    nn = max(5, int(fl / STEP))
    sf = np.linspace(0, fl, nn + 1)
    d3 = np.array((math.cos(a), math.sin(a), T[2] * .45 + zr))
    d3 /= np.linalg.norm(d3)
    Pf = P[i][None] + sf[:, None] * d3[None]
    Pf[:, :2] += np.c_[-d3[1], d3[0]] * (np.sin(sf / fl * math.pi * U(R, .8, 1.4)) * fl * U(R, -.18, .18))[:, None]
    rf = float(r[i]) * U(R, *frac) * (1 - .50 * sf / fl) + .002
    Pf = bend_up(Pf, rf, {rec['id']})
    far = sf > float(r[i]) * 1.1
    if clearance(Pf[far], rf[far], {rec['id']}).min() < -.004:
        return None
    if (Pf[:, 2] + rf).max() > V['H'] * 1.05 or not inside(Pf, .1):
        return None
    f = new_rec(R, 'fork', Pf, sf, rf, ('open', 'tip' if rf[-1] < .014 else 'break'), parent=rec['id'])
    rec['bulge'].append((float(s[i]), .08))
    add_seg(f)
    return f


def add_stubs(R, rec, n):
    P, s, r = rec['P'], rec['s'], rec['r']
    made = 0
    for _ in range(n * 6):
        if made >= n:
            break
        i = int(len(P) * U(R, .15, .85))
        T, N0, B0 = frame_at(P, i)
        ph = U(R, 0, 2 * math.pi)
        rd = N0 * math.cos(ph) + B0 * math.sin(ph)
        if rd[2] < -.1:
            continue
        d = rd * .85 + T * .45
        d /= np.linalg.norm(d)
        ln = U(R, .06, .16) + float(r[i])
        ss = np.linspace(0, ln, 4)
        Ps = P[i][None] + ss[:, None] * d[None]
        rs = float(r[i]) * U(R, .22, .36) * (1 - .25 * ss / ln)
        out = ss > float(r[i]) * 1.05
        if out.any() and clearance(Ps[out], rs[out], {rec['id']}).min() > .004 and (Ps[:, 2] - rs).min() > .004:
            x = new_rec(R, 'stub', Ps, ss, rs, ('open', 'break'), parent=rec['id'])
            rec['bulge'].append((float(s[i]), .05))
            add_seg(x, 1)
            made += 1


def plan(v):
    global V, SEG, OWN, RECS, CONTACTS
    assert v == 'L', 'v004 先做 L 樣品'
    V = dict(VARIANTS[v], v=v)
    SEG, OWN, RECS, CONTACTS = np.zeros((0, 8)), np.zeros(0, int), [], []
    R = random.Random(V['seed'])

    def put(name, ctrl, r0, taper, mode, sink, k=.3, shape=None, lumps=3, ends=('break', 'break'), e=(.06, .12), main=False):
        Q, s = spline_path(ctrl)
        r = heavy_radius(R, s, r0, taper, lumps)
        t = s / s[-1]
        if mode == 'rigid':
            P = _place_rigid1(Q, s, r, set(), sink, shape(t, s) if shape else None)
        else:
            P = drape(Q, s, r, set(), sink, k, shape(t, s) if shape else None)
        rec = new_rec(R, 'branch', P, s, r, ends, main=main)
        rec['xs'] = xs_params(R, e)
        rec['heavy'] = r0 > .06
        rec['name'] = name
        add_seg(rec)
        return rec

    # 底層：C0 斜躺地上（A 的拱搭在它上面）
    C0 = put('C0', [(-1.55, .62), (-1.0, .18), (-.35, -.38), (.25, -.80)], .12, .35, 'drape', .22, k=.3, lumps=3)
    # 粗主幹 A：本身往上拱（粗頭著地在左），搭在 C0 和地上
    A = put('A', [(-2.05, -.12), (-1.15, -.34), (-.05, -.16), (.95, .14), (1.80, .02)], .19, .36, 'rigid', .24,
            shape=lambda t, s: .40 * np.exp(-((t - .40) / .24) ** 2) + .06 * np.sin(2 * math.pi * t), lumps=4, main=True)
    # 中主幹 B：從前左斜到後右，跨過 C0 與 A，兩頭落地
    B = put('B', [(-1.70, -1.00), (-.75, -.62), (.35, .02), (1.25, .70), (1.95, .86)], .14, .40, 'drape', .18, k=.22, lumps=3)
    # 交織（先擺，D 再搭上來）的中枝兩根：緩彎（k 0.3）跨過主幹、兩頭落地，讓俯視收成一團（參考圖的粗枝之間有中枝穿插）
    F = put('F', [(-.95, -1.00), (-.35, -.42), (.30, .28), (.85, .98)], .066, .42, 'drape', .10, k=.55, lumps=1, e=(.04, .09))
    G = put('G', [(-1.35, 1.02), (-.95, .42), (-.62, -.20), (-.25, -.88)], .060, .42, 'drape', .10, k=.55, lumps=1, e=(.04, .09))
    # 細主幹 D：粗頭在右前著地，往左後搭上 A/B、斷口翹起
    D = put('D', [(1.95, -.70), (1.30, -.62), (.70, -.25), (.25, .30), (-.05, .62)], .10, .38, 'rigid', .12,
            shape=lambda t, s: .12 * np.sin(math.pi * t) + .35 * t ** 3, lumps=2)
    # 細主幹 E：在 A 粗頭那側，彎著跨過 A
    E = put('E', [(-2.15, .55), (-1.75, .20), (-1.45, -.35), (-1.20, -.95)], .075, .40, 'drape', .10, k=.55, lumps=2)
    # 中枝：外圍三根，沿著主幹外側躺地上（M2 一頭搭在 B 上）；不在主幹上方搭架子
    M1 = put('M1', [(.85, -1.12), (1.40, -1.00), (2.05, -.98)], .052, .45, 'rigid', .08, shape=lambda t, s: .05 * np.sin(math.pi * t), lumps=1, e=(.04, .08))
    M2 = put('M2', [(-.55, 1.05), (.05, .78), (.75, .62), (1.25, .30)], .046, .45, 'drape', .08, k=.60, lumps=1, e=(.04, .08))
    M3 = put('M3', [(-2.25, .92), (-1.70, 1.06), (-1.10, 1.00)], .044, .45, 'rigid', .08, shape=lambda t, s: .04 * np.sin(math.pi * t), lumps=1, e=(.04, .08))
    # 斷口
    for rec, ns_ in ((A, (6, 3)), (B, (2, 1)), (C0, (1, 2)), (D, (0, 3)), (E, (1, 0))):
        rec['ext'] = [1.0, 1.0]
        for e_ in (0, 1):
            if rec['ends'][e_] == 'break':
                heavy_splinters(R, rec, e_, ns_[e_], .42 if rec is A and e_ == 0 else .22)
    for rec in (M1, M2, M3, F, G):
        rec['splint'] = [[], []]
    # Y 形分岔：只在主幹上、往外長（參考圖的粗枝都有一兩個分岔），不往中央長
    forks = []
    for rec, t, side, fl, zr in ((A, .62, 1, 1.05, .20), (A, .86, -1, .70, .10), (B, .70, -1, .95, .16), (B, .35, 1, .80, .18), (D, .80, 1, .55, .22), (D, .55, -1, .60, .18), (E, .60, 1, .55, .15), (C0, .25, 1, .60, .12)):
        f = add_fork(R, rec, t, side, fl, zr)
        if f is None:
            f = add_fork(R, rec, t + .05, -side, fl * .85, zr)
        if f is not None:
            forks.append(f)
    for rec, n in ((A, 3), (B, 2), (C0, 1), (D, 1)):
        add_stubs(R, rec, n)
    # 交叉處（夾落葉、潮濕苔的位置）
    br = [x for x in RECS if x['kind'] in ('branch', 'fork')]
    for a in range(len(br)):
        for b in range(a + 1, len(br)):
            Ar, Br = br[a], br[b]
            if Ar.get('parent') == Br['id'] or Br.get('parent') == Ar['id']:
                continue
            Pa, Pb = Ar['P'][::2], Br['P'][::2]
            d = np.linalg.norm(Pa[:, None] - Pb[None], axis=2) - Ar['r'][::2][:, None] - Br['r'][::2][None]
            i, j = np.unravel_index(d.argmin(), d.shape)
            if d[i, j] < .03:
                CONTACTS.append(((Pa[i] + Pb[j]) / 2).tolist())
    if PHASE >= 2:
        twigs(R, [x for x in RECS if x['kind'] == 'fork'] + [D, E, F, G, M1, M2, M3])
        litter(R)
    print('PLAN', v, 'phase', PHASE, {k: sum(1 for x in RECS if x['kind'] == k) for k in ('branch', 'fork', 'stub', 'twig', 'litter')},
          'contacts', len(CONTACTS), 'top', round(float(max(x['P'][:, 2].max() + x['r'].max() for x in RECS)), 3))
    for x in RECS:
        if x['kind'] == 'branch':
            print('  MAIN', x['name'], 'd_cm', round(x['r0'] * 200, 1), 'len', round(float(x['s'][-1]), 2), 'z', round(float(x['P'][:, 2].min()), 3), '-', round(float(x['P'][:, 2].max()), 3))
    return RECS


def twigs(R, parents):
    """第二階段 1：細枝只長在枝的遠端、往外（輪廓上），中央方框（|x|<0.8、|y|<0.45）不長。"""
    tw = 0
    for _ in range(V['twigs'] * 10):
        if tw >= V['twigs']:
            break
        rec = R.choice(parents)
        P, s, r = rec['P'], rec['s'], rec['r']
        i = int(len(P) * U(R, .60, .95))
        T, N0, B0 = frame_at(P, i)
        if R.random() < .5 and rec['kind'] == 'branch':
            T = -T if i < len(P) / 2 else T
        ph = U(R, -.5, .5) + (math.pi if R.random() < .5 else 0)
        rd = N0 * math.cos(ph) + B0 * abs(math.sin(ph))
        d = rd * .45 + T * .85 + np.array((0, 0, .18))
        d /= np.linalg.norm(d)
        ln = U(R, .18, .40)
        ss = np.linspace(0, ln, max(5, int(ln / .03)) + 1)
        Pt = P[i][None] + ss[:, None] * d[None]
        side = np.cross(d, (0, 0, 1.0))
        side /= np.linalg.norm(side) + 1e-9
        Pt += side[None] * (np.sin(ss / ln * math.pi * U(R, .8, 1.5)) * ln * U(R, -.20, .20))[:, None]
        rt = U(R, .009, .016) * (1 - .55 * ss / ln) + .002
        if (np.abs(Pt[:, 0]) < .8).all() and (np.abs(Pt[:, 1]) < .45).all():
            continue
        out = ss > float(r[i]) * 1.1
        if clearance(Pt[out], rt[out], {rec['id']}).min() > .004 and (Pt[:, 2] - rt).min() > .01 and (Pt[:, 2] + rt).max() < V['H'] * 1.08 and inside(Pt, .1):
            x = new_rec(R, 'twig', Pt, ss, rt, ('open', 'tip'), parent=rec['id'])
            add_seg(x, 2)
            tw += 1
            k = int(len(Pt) * U(R, .45, .65))
            dd = Pt[min(k + 1, len(Pt) - 1)] - Pt[k]
            dd /= np.linalg.norm(dd) + 1e-9
            a = R.choice((-1, 1)) * U(R, .45, .75)
            dd = np.array((dd[0] * math.cos(a) - dd[1] * math.sin(a), dd[0] * math.sin(a) + dd[1] * math.cos(a), dd[2] + .10))
            dd /= np.linalg.norm(dd)
            l2 = ln * U(R, .30, .50)
            s2 = np.linspace(0, l2, 5)
            P2 = Pt[k][None] + s2[:, None] * dd[None]
            r2 = float(rt[k]) * .75 * (1 - .6 * s2 / l2) + .0015
            if clearance(P2[1:], r2[1:], {x['id']}).min() > .004 and (P2[:, 2] - r2).min() > .01 and inside(P2, .1):
                y = new_rec(R, 'twig', P2, s2, r2, ('open', 'tip'), parent=x['id'])
                add_seg(y, 2)


def litter(R):
    br = [x for x in RECS if x['kind'] in ('branch', 'fork')]
    allP = np.vstack([x['P'] for x in br])
    lo, hi = allP[:, :2].min(0) - .15, allP[:, :2].max(0) + .15
    lt = 0
    for _ in range(V['litter'] * 12):
        if lt >= V['litter']:
            break
        c = np.array((U(R, lo[0], hi[0]), U(R, lo[1], hi[1])))
        ln = U(R, .18, .45)
        Q, ss = xy_path(R, c, U(R, 0, math.pi), ln, .25)
        rl = U(R, .006, .012) * (1 - .4 * ss / ln) + .001
        Pl = np.c_[Q, rl * .8]
        if clearance(Pl, rl, set()).min() > .01 and inside(Pl, .05):
            x = new_rec(R, 'litter', Pl, ss, rl, ('break', 'tip'))
            add_seg(x, 2)
            lt += 1


# ---------------------------------------------------------------- 第二階段：苔的薄殼、蘑菇
def finish_body(o, mb, lv):
    _finish_body3(o, mb, lv)
    if lv > 1:
        return
    import bmesh
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    cl = bm.loops.layers.float_color['Layers']
    bm.verts.ensure_lookup_table()
    bm.normal_update()
    mv = {}
    for f in bm.faces:
        for l in f.loops:
            mv[l.vert.index] = max(mv.get(l.vert.index, 0), l[cl][0])
    sel = [f for f in bm.faces if f.normal.z > .25 and all(mv.get(v.index, 0) > .55 for v in f.verts)]
    if not sel:
        bm.free()
        return
    ret = bmesh.ops.duplicate(bm, geom=sel)
    nf = [g for g in ret['geom'] if isinstance(g, bmesh.types.BMFace)]
    nvs = {v for f in nf for v in f.verts}
    edge = set()
    for f in nf:
        for e in f.edges:
            if len([x for x in e.link_faces if x in set(nf)]) < 2:
                edge |= set(e.verts)
    for v in nvs:
        n = v.normal if v.normal.length > .1 else Vector((0, 0, 1))
        th = .006 + .012 * (.5 + .5 * noise.noise(v.co * 6.0))
        v.co += n * (th * (.08 if v in edge else 1.0) + .0015)
    for f in nf:
        for l in f.loops:
            c = l[cl]
            l[cl] = (1.0, 0.0, 0.0, c[3])
    bm.to_mesh(me)
    bm.free()
    print('MOSS_SHELL lod', lv, 'faces', len(nf))


def make_cards(body0):
    C = _make_cards3(body0)
    R = random.Random(V['seed'] + 99)
    rects = lib8()['rects']()
    mush = [r['uv'] for r in rects if r['cat'] == 'mush']
    me = body0.data
    co = [body0.matrix_world @ v.co for v in me.vertices]
    tree = BVHTree.FromPolygons(co, [tuple(p.vertices) for p in me.polygons])
    A = next(x for x in RECS if x.get('name') == 'A')
    B = next(x for x in RECS if x.get('name') == 'B')
    nm = 0
    tag = max(C.tag) + 1 if C.tag else 0
    spots = [(A, .14, 'top'), (B, .06, 'ground')]
    for rec, t, where in spots:
        i = int(len(rec['P']) * t)
        p = rec['P'][i]
        for _ in range(R.randint(3, 4)):
            q = p + np.array((U(R, -.10, .10), U(R, -.10, .10), 0))
            if where == 'ground':
                T, N0, B0 = frame_at(rec['P'], i)
                q = p + N0 * (rec['r'][i] + U(R, .03, .08)) * R.choice((-1, 1))
            h = tree.ray_cast(Vector((q[0], q[1], 2.0)), Vector((0, 0, -1)), 4)
            if h[0] is None or h[1].z < .55:
                continue
            base = Vector((h[0].x, h[0].y, h[0].z - .006))
            if where == 'ground' and base.z > .06:
                continue
            C.upright(base, U(R, .06, .11), U(R, .06, .10), R.choice(mush), U(R, 0, math.pi), tag)
            tag += 1
            nm += 1
    print('MUSH clusters 2, caps', nm)
    return C


for f in (XS, TW, CAPLN, CAPW, CAPC, spline_path, heavy_radius, drape, xs_params, heavy_splinters, add_fork, add_stubs, plan, twigs, litter, finish_body, make_cards):
    ns[f.__name__] = types.FunctionType(f.__code__, ns, f.__name__, f.__defaults__, f.__closure__)


def run(v, phase):
    ns['PHASE'] = phase
    import bpy, time
    if phase == 2:
        ns['run'](v)
        rep = ns['contact_report']()
        bpy.context.scene['dr09_v4_contacts'] = json.dumps(rep)
        bpy.ops.wm.save_as_mainfile(filepath=f"{HERE}/blend/{ns['NAMES'][v]}_v004.blend", copy=True)
        print('CONTACT_SUMMARY', rep)
        return
    # 第一階段：只做主體 LOD0（沒有細枝、落葉、蘑菇、苔），存灰模 blend，不匯出
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    asset = ns['NAMES'][v]
    ns['plan'](v)
    ns['cleanup']()
    print('PLANCHECK', json.dumps(ns['plan_checks']()))
    rep = ns['contact_report']()
    print('CONTACT_SUMMARY', rep)
    mb = ns['MB']()
    for rec in ns['RECS']:
        if not rec.get('dead'):
            ns['tube'](mb, rec, 0)
    o = ns['to_object'](mb, f'{asset}_LOD0', ns['layer_mat']())
    ns['hidden_faces'](o, mb)
    ns['_triangulate'](o)
    root = bpy.data.objects.new(asset, None)
    bpy.context.scene.collection.objects.link(root)
    o.parent = root
    piv = ns['_exec'](ns['ROOTS'] + '/dr_pivot.py', 'dr_pivot')
    piv['to_bottom_centre'](root, o)
    print('GREYBOX tris', ns['_tri'](o))
    bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_v004_greybox.blend', copy=True)
    print('GREYBOX_DONE')


if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    try:
        run(a[0] if a else 'L', int(a[1]) if len(a) > 1 else 2)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
