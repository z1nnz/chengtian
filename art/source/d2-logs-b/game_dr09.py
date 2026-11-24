# DR09 斷枝堆（S 1.5 m／M 2.5 m／L 4 m 三種大小）的遊戲模型：直接建遊戲用網格（不烘焙），沿用 DR08 的兩個材質和貼圖。
#   - 本體：M_DR08_Layered（Unity：YunJing/D2LayeredWood，DR08_Shared/Textures 的六層 1024 手繪平鋪貼圖）。UV0 公尺（沿枝長 = u，
#     樹皮木紋左右向），頂點色 RGBA = 苔、褐腐、撕裂纖維、內壁的權重，UV1 = (土, AO)。斷口、剝皮處、木刺 = 纖維層；腳下落葉土堆 = 土層。
#   - Detail_DR09_Leaves：手繪植物卡（落葉、小褐蕈、蕨；DR08_Plants_Albedo 圖集），M_DR08_Plants（雙面、alpha 裁切）。
#   - 擺法像真的倒下來堆起來：粗的先放（最粗的主枝躺在最下面、略陷進落葉土），之後每一根照它的平面路徑，量「底下已經有的枝／地面」
#     撐得到的高度，取上凸包、在重心那一段的兩個支點上靠著（所以兩點支撐、一頭可以翹起來），再檢查 3D 有沒有穿進別根、有就整根抬高。
#     分岔跟著母枝、尾段碰到東西就往上彎；短斷枝樁、細枝條、地上的小枝都檢查不碰到別根才留。
#   - LOD 每級用同一份擺法重建（環距、每圈點數變粗，細枝條、木刺、地上小枝在 LOD2 拿掉）；植物卡照組抽掉。
# 用法（背景）：blender -b --python art/source/d2-logs-b/game_dr09.py -- M
import bpy, bmesh, sys, os, json, math, random, time, traceback
import numpy as np
from mathutils import Vector, Matrix, noise
from mathutils.bvhtree import BVHTree

ROOT = 'D:/yun-jing-d2-logs'
HERE = ROOT + '/art/source/d2-logs-b'
ROOTS = ROOT + '/art/source/d2-roots-b'
VER = 'v001'
DET = 'Detail_DR09_Leaves'
NAMES = {v: f'DR09_BranchPile_{v}' for v in 'SML'}
# L 長、W 寬、H 目標高；n 根數；r 半徑範圍（不含主枝）；main 主枝半徑；forks 分岔數；twigs 細枝條數；litter 地上小枝數；mound 落葉土堆高
VARIANTS = {
    'S': dict(L=1.5, W=1.0, H=.40, n=(6, 7), r=(.025, .050), main=.055, forks=8, twigs=10, litter=7, mound=.035, seed=9101, lean=2, margin=.11),
    'M': dict(L=2.5, W=1.6, H=.70, n=(10, 11), r=(.030, .080), main=.095, forks=18, twigs=18, litter=11, mound=.045, seed=9202, lean=3, margin=.24),
    'L': dict(L=4.0, W=2.2, H=1.10, n=(15, 16), r=(.030, .090), main=.140, forks=32, twigs=28, litter=16, mound=.055, seed=9303, lean=4, margin=.40),
}
LODMUL = {0: 1.0, 1: 1.55, 2: 3.4}
PLANT_KEEP = {0: 1.0, 1: .5, 2: .15}
STEP = .03                                   # 擺放時沿枝取樣間距

V = None
SEG = np.zeros((0, 8))                       # 已擺好的枝段：ax ay az bx by bz ra rb
OWN = np.zeros(0, int)
RECS = []
CONTACTS = []


def U(R, a, b):
    return a + (b - a) * R.random()


def sm(x, e0, e1):
    t = np.clip((np.asarray(x, float) - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def _ns(lib):
    ns = {'__name__': lib}
    return ns


def _exec(path, name):
    ns = {'__name__': name, '__file__': path}
    exec(compile(open(path, encoding='utf-8').read(), path, 'exec'), ns)
    return ns


_LIB = None


def lib8():
    """DR08 的材質（M_DR08_Layered、M_DR08_Plants）和圖集分格。"""
    global _LIB
    if _LIB is None:
        _LIB = _exec(HERE + '/game_dr08t.py', 'dr08t_lib')
    return _LIB


TEXD9 = f'{ROOT}/art/exports/d2-logs-b/DR09_Shared/Textures'
LAYER_MAT9 = 'M_DR09_Layered'


def layer_mat():
    """M_DR09_Layered：DR08 的六層材質，撕裂纖維那層換成 DR09_FreshWood（淺奶油色的新斷口），其餘五層共用 DR08_Shared。"""
    m = bpy.data.materials.get(LAYER_MAT9)
    if m:
        return m
    m = lib8()['layer_material']().copy()
    m.name = LAYER_MAT9
    for n in m.node_tree.nodes:
        if n.type == 'TEX_IMAGE' and n.image and n.image.name.startswith('DR08_Fibre_'):
            kind = 'Normal' if 'Normal' in n.image.name else 'Albedo'
            n.image = bpy.data.images.load(f'{TEXD9}/DR09_FreshWood_{kind}.png', check_existing=True)
            if kind == 'Normal':
                n.image.colorspace_settings.name = 'Non-Color'
        if n.type == 'TEX_IMAGE' and n.image and n.image.name == 'DR08_Bark_Albedo.png':
            n.image = bpy.data.images.load(f'{TEXD9}/DR09_Bark_Albedo.png', check_existing=True)   # 斷枝的樹皮：偏橄欖深灰褐（法線沿用 DR08）
    u = dict(m['unity'].to_dict()) if hasattr(m['unity'], 'to_dict') else dict(m['unity'])
    u['textures'] = 'DR08_Shared/Textures/DR08_{Moss,Rot,Inner,Soil}_{Albedo,Normal}.png + DR08_Bark_Normal.png + DR09_Shared/Textures/DR09_Bark_Albedo.png (bark slot) + DR09_FreshWood_{Albedo,Normal}.png (fibre slot)'
    m['unity'] = u
    return m


# ---------------------------------------------------------------- 擺放
def support(Q, r, excl):
    """Q (n,2) 平面點、r (n,) 這根的半徑：底下已擺好的枝撐得到的軸心高度（撐不到 = -inf）。"""
    if not len(SEG):
        return np.full(len(Q), -1e9)
    m = ~np.isin(OWN, list(excl))
    S = SEG[m]
    if not len(S):
        return np.full(len(Q), -1e9)
    a, b = S[:, :2], S[:, 3:5]
    ab = b - a
    L2 = (ab ** 2).sum(1) + 1e-12
    d = Q[:, None, :] - a[None]
    u = np.clip((d * ab[None]).sum(2) / L2[None], 0, 1)
    cp = a[None] + u[..., None] * ab[None]
    dxy = np.linalg.norm(Q[:, None, :] - cp, axis=2)
    rr = r[:, None] + S[None, :, 6] + (S[None, :, 7] - S[None, :, 6]) * u
    zs = S[None, :, 2] + (S[None, :, 5] - S[None, :, 2]) * u
    h = np.where(dxy < rr, zs + np.sqrt(np.maximum(rr ** 2 - dxy ** 2, 0)) + .003, -1e9)
    return h.max(1)


def clearance(P, r, excl, idx=False):
    """P (n,3)、r (n,)：到其他枝表面的最小距離（負 = 穿進去）。"""
    if not len(SEG):
        return np.full(len(P), 1e9)
    m = ~np.isin(OWN, list(excl))
    S = SEG[m]
    if not len(S):
        return np.full(len(P), 1e9)
    a, b = S[:, :3], S[:, 3:6]
    ab = b - a
    L2 = (ab ** 2).sum(1) + 1e-12
    u = np.clip(((P[:, None, :] - a[None]) * ab[None]).sum(2) / L2[None], 0, 1)
    cp = a[None] + u[..., None] * ab[None]
    dist = np.linalg.norm(P[:, None, :] - cp, axis=2)
    c = dist - r[:, None] - (S[None, :, 6] + (S[None, :, 7] - S[None, :, 6]) * u)
    return c.min(1)


def upper_hull(xs, ys):
    h = []
    for p in sorted(zip(xs, ys)):
        while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) >= 0:
            h.pop()
        h.append(p)
    return h


def add_seg(rec, every=3):
    global SEG, OWN
    P, r = rec['P'], rec['r']
    idx = list(range(0, len(P), every))
    if idx[-1] != len(P) - 1:
        idx.append(len(P) - 1)
    rows = [np.r_[P[i], P[j], r[i], r[j]] for i, j in zip(idx, idx[1:])]
    if rows:
        SEG = np.vstack([SEG, np.array(rows)])
        OWN = np.r_[OWN, np.full(len(rows), rec['id'])]


def xy_path(R, c, ang, length, crook):
    n = max(6, int(round(length / STEP)))
    nodes = R.randint(2, 4)
    knots = sorted(U(R, .15, .85) for _ in range(nodes))
    turns = [U(R, -crook, crook) for _ in range(nodes)]
    ds = length / n
    p = np.zeros(2)
    pts = [p.copy()]
    for i in range(n):
        t = (i + .5) / n
        a = ang + sum(tr * float(sm(t, k - .025, k + .025)) for tr, k in zip(turns, knots))
        p = p + np.array((math.cos(a), math.sin(a))) * ds
        pts.append(p.copy())
    pts = np.array(pts)
    return pts - pts.mean(0) + np.asarray(c), np.arange(n + 1) * ds


def radius_profile(R, s, r0, tip_kind):
    t = s / s[-1]
    taper = U(R, .40, .62)
    r = r0 * (1 - taper * t)
    if tip_kind == 'tip':
        r = r * (1 - .80 * sm(t, .75, 1.0)) + .002
    r = r * (1 + .10 * sm(.10 - t, 0, .10))                # 斷下來的粗頭略粗（枝領）
    return r


def new_rec(R, kind, P, s, r, ends, parent=None, main=False):
    rec = dict(id=len(RECS), kind=kind, P=P, s=s, r=r, ends=list(ends), parent=parent, main=main, r0=float(r[0]),
               tear=[U(R, 0, 2 * math.pi), U(R, 0, 2 * math.pi)], peel=[U(R, 1.2, 3.5), U(R, 1.2, 3.5)],
               ext=[U(R, .7, 1.3), U(R, .7, 1.3)], seed=R.randint(0, 10 ** 6), bulge=[], splint=[[], []])
    for e in (0, 1):
        if rec['ends'][e] == 'break' and r[0 if e == 0 else -1] > .018:
            k = R.randint(5, 8) if r[0 if e == 0 else -1] > .05 else (R.randint(3, 5) if r[0 if e == 0 else -1] > .03 else R.randint(1, 2))
            for _ in range(k):
                rr = float(r[0 if e == 0 else -1])
                rec['splint'][e].append(dict(th=rec['tear'][e] + U(R, -1.0, 1.0), len=min(.36, rr * U(R, 1.0, 2.8)),
                                             w=max(.012, rr * U(R, .35, .65)), out=U(R, .0, .18)))
    RECS.append(rec)
    return rec


def place_rigid(Q, s, r, excl, sink, shape=None):
    """shape：這根本身上下的彎（相對於直線，公尺）；照 h − shape 取凸包，擺好的 z = 直線 + shape，一樣靠在兩個支點上。"""
    shape = np.zeros(len(s)) if shape is None else shape
    g = r * (1 - sink)
    h = np.maximum(g, support(Q, r, excl)) - shape
    hull = upper_hull(s, h)
    w = r ** 2
    sc = float((w * s).sum() / w.sum())
    seg = None
    for (x0, y0), (x1, y1) in zip(hull, hull[1:]):
        if x0 - 1e-9 <= sc <= x1 + 1e-9:
            seg = (x0, y0, x1, y1)
            break
    if seg is None:
        x0, y0 = hull[0]
        x1, y1 = hull[-1]
        seg = (x0, y0, x1, y1)
    x0, y0, x1, y1 = seg
    z = y0 + (y1 - y0) * (s - x0) / max(x1 - x0, 1e-6) + shape
    P = np.c_[Q, z]
    for _ in range(6):                                     # 3D 檢查：斜放的枝用平面近似會差一點，穿進去就整根抬高
        c = clearance(P, r, excl)
        if c.min() > -.002:
            break
        P[:, 2] += -c.min() + .003
    return P


def bend_up(P, r, excl):
    """分岔、細枝：碰到東西或地面的點往上推，再順一順。"""
    for _ in range(5):
        c = clearance(P, r, excl)
        g = r - P[:, 2]
        lift = np.maximum(np.maximum(-c + .003, g + .002), 0)
        if lift.max() < .001:
            break
        lift = np.convolve(np.pad(lift, 3, mode='edge'), np.ones(7) / 7, 'valid')
        lift = np.maximum.accumulate(lift) if P[-1, 2] >= P[0, 2] else lift
        P[:, 2] += lift
    return P


def inside(P, pad=0.0):
    """分岔、細枝、地上小枝不要伸出工作包外框（長 L × 寬 W，以堆中心為原點）。"""
    return bool((np.abs(P[:, 0]) <= V['L'] * .47 + pad).all() and (np.abs(P[:, 1]) <= V['W'] * .47 + pad).all())


def frame_at(P, i):
    T = P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]
    T /= np.linalg.norm(T) + 1e-12
    N0 = np.cross(T, (0, 0, 1.0))
    if np.linalg.norm(N0) < 1e-3:
        N0 = np.array((1.0, 0, 0))
    N0 /= np.linalg.norm(N0)
    B0 = np.cross(N0, T)
    return T, N0, B0


def plan(v):
    global V, SEG, OWN, RECS, CONTACTS
    V = dict(VARIANTS[v], v=v)
    SEG, OWN, RECS, CONTACTS = np.zeros((0, 8)), np.zeros(0, int), [], []
    R = random.Random(V['seed'])
    L, W = V['L'], V['W']
    n = R.randint(*V['n'])
    r1, r2 = V['r']
    radii = [V['main']] + sorted((r1 + (r2 - r1) * R.random() ** 1.5 for _ in range(n - 1)), reverse=True)
    bases = []
    props = set(R.sample(range(2, n), {'S': 1, 'M': 2, 'L': 3}[v]))
    for k, r0 in enumerate(radii):
        main = k == 0
        prop = k in props
        best = None
        for tries in range(8):                                 # 太陡（整根快站起來）就換位置重擺；最多試 8 次，取最平的
            for attempt in range(30):
                if main:
                    ang = U(R, -.10, .10)
                    length = L * U(R, .80, .88)
                    c = (U(R, -.05, .05) * L, U(R, -.08, .08) * W)
                else:
                    cross = R.random() < .55
                    ang = (U(R, .40, 1.15) if cross else U(R, 0, .35)) * R.choice((-1, 1))
                    length = min(r0 * U(R, 17, 26) + U(R, .15, .45), L * .78)
                    ca, sa = abs(math.cos(ang)), abs(math.sin(ang))
                    length = min(length, .86 * W / max(sa, 1e-3), .86 * L / max(ca, 1e-3))      # 彎了以後外框會變大，留餘量
                    bx = max(0, L / 2 - length / 2 * ca) * .85
                    by = max(0, W / 2 - length / 2 * sa) * .85
                    if k <= V['lean'] + 1:                         # 前幾根粗的壓在主枝上（堆起來）
                        bx *= .55
                        by *= .35
                    c = (U(R, -bx, bx), U(R, -by, by))
                if length > .35:
                    break
            Q, s = xy_path(R, c, ang, length, U(R, .30, .62) if main else U(R, .38, .75))
            tip = 'tip' if r0 * .5 < .016 else 'break'
            r = radius_profile(R, s, r0, tip)
            if R.random() < .5:                                   # 粗頭朝哪邊隨機
                Q = Q[::-1].copy()
            t_ = s / s[-1]
            bow = U(R, -.03, .09) * s[-1] if not main else U(R, .0, .03) * s[-1]
            shape = min(bow, .18) * np.sin(math.pi * t_) + U(R, -.05, .05) * s[-1] * np.sin(2 * math.pi * t_)
            P = place_rigid(Q, s, r, set(), .28 if main else .10, shape)
            grade = float(np.max(np.abs(np.diff(P[:, 2]) / np.maximum(np.diff(s), 1e-6))))
            over = max(0.0, float((P[:, 2] + r).max()) - V['H'] * .95)     # 比目標高就換位置（不要疊成柴塔）
            score = (abs(grade - .58) if prop else grade) + 10 * over
            if best is None or score < best[0]:
                best = (score, Q, s, r, P, tip)
            if (abs(grade - .58) < .15 if prop else grade < .50) and over == 0:
                break
        score, Q, s, r, P, tip = best
        rec = new_rec(R, 'branch', P, s, r, ('break', tip), main=main)
        add_seg(rec)
        bases.append(rec)
        # 分岔（參考圖每根枝都有一兩個 Y 形側枝）
        nf = 3 if r0 > .065 else (2 if r0 > .040 else 1)
        for _f in range(nf):
            if (main or r0 > .028) and sum(1 for x in RECS if x['kind'] == 'fork') < V['forks']:
                i = int(len(P) * U(R, .15 + .70 * _f / nf, .15 + .70 * (_f + 1) / nf))
                T, N0, B0 = frame_at(P, i)
                a = math.atan2(T[1], T[0]) + R.choice((-1, 1)) * U(R, .40, .70)
                fl = min(s[-1] * U(R, .30, .55), 1.5)
                nn = max(5, int(fl / STEP))
                sf = np.linspace(0, fl, nn + 1)
                d3 = np.array((math.cos(a), math.sin(a), T[2] * .45 + U(R, -.04, .08)))
                d3 /= np.linalg.norm(d3)
                Pf = P[i][None] + sf[:, None] * d3[None]
                Pf[:, :2] += np.c_[-d3[1], d3[0]] * (np.sin(sf / fl * math.pi * U(R, .8, 1.5)) * fl * U(R, -.20, .20))[:, None]
                rf = float(r[i]) * U(R, .58, .72) * (1 - .55 * sf / fl) + .002
                Pf = bend_up(Pf, rf, {rec['id']})
                if clearance(Pf[sf > float(r[i]) * 1.1], rf[sf > float(r[i]) * 1.1], {rec['id']}).min() < -.004:
                    continue                                       # 往上彎還是碰到別根：不要這個分岔
                if (Pf[:, 2] + rf).max() > V['H'] * 1.02 or not inside(Pf):
                    continue                                       # 比整堆目標高：不要（翹頭的枝上不再往上長叉）
                f = new_rec(R, 'fork', Pf, sf, rf, ('open', 'tip' if rf[-1] < .014 else 'break'), parent=rec['id'])
                rec['bulge'].append((float(s[i]), .22))
                add_seg(f)
    # 斷枝樁、細枝條
    big = [x for x in RECS if x['kind'] in ('branch', 'fork') and x['r0'] > .024]
    for rec in big:
        P, s, r = rec['P'], rec['s'], rec['r']
        for _ in range(int(round(s[-1] * U(R, .6, 1.4)))):
            i = int(len(P) * U(R, .12, .88))
            T, N0, B0 = frame_at(P, i)
            for _try in range(6):
                ph = U(R, 0, 2 * math.pi)
                rd = N0 * math.cos(ph) + B0 * math.sin(ph)
                if rd[2] > -.2:
                    break
            d = rd * .80 + T * .60
            d /= np.linalg.norm(d)
            ln = min(.22, U(R, .04, .15) * (rec['r0'] / .05) ** .5) + float(r[i])
            ss = np.linspace(0, ln, 4)
            Ps = P[i][None] + ss[:, None] * d[None]
            rs = float(r[i]) * U(R, .30, .46) * (1 - .25 * ss / ln)
            out = ss > float(r[i]) * 1.05
            ok = clearance(Ps[out], rs[out], {rec['id']}).min() > .004 if out.any() else False
            if ok and (Ps[:, 2] - rs).min() > .004:
                x = new_rec(R, 'stub', Ps, ss, rs, ('open', 'break'), parent=rec['id'])
                rec['bulge'].append((float(s[i]), .16))
                add_seg(x, 1)
    thin = [x for x in RECS if x['kind'] in ('branch', 'fork') and .018 < x['r0'] < .075]
    tw = 0
    for _ in range(V['twigs'] * 6):
        if tw >= V['twigs'] or not thin:
            break
        rec = R.choice(thin)
        P, s, r = rec['P'], rec['s'], rec['r']
        i = int(len(P) * (U(R, .55, .95) if R.random() < .6 else U(R, .25, .55)))
        T, N0, B0 = frame_at(P, i)
        ph = U(R, -.45, .55) + (math.pi if R.random() < .5 else 0)      # 往兩側長（參考圖的細枝是橫的、彎的，不是往上戳）
        rd = N0 * math.cos(ph) + B0 * abs(math.sin(ph))
        d = rd * .50 + T * .85 + np.array((0, 0, .05))
        d /= np.linalg.norm(d)
        ln = U(R, .12, .32)
        nn = max(5, int(ln / .03))
        ss = np.linspace(0, ln, nn + 1)
        Pt = P[i][None] + ss[:, None] * d[None]
        side = np.cross(d, (0, 0, 1.0))
        side /= np.linalg.norm(side) + 1e-9
        Pt += side[None] * (np.sin(ss / ln * math.pi * U(R, .8, 1.6)) * ln * U(R, -.22, .22))[:, None]
        Pt[:, 2] += (ss / ln) ** 2 * ln * U(R, -.05, .20)
        rt = U(R, .008, .014) * (1 - .6 * ss / ln) + .002
        out = ss > float(r[i]) * 1.1
        if clearance(Pt[out], rt[out], {rec['id']}).min() > .004 and (Pt[:, 2] - rt).min() > .01 and (Pt[:, 2] + rt).max() < V['H'] * 1.02 and inside(Pt):
            x = new_rec(R, 'twig', Pt, ss, rt, ('open', 'tip'), parent=rec['id'])
            add_seg(x, 2)
            tw += 1
            k = int(len(Pt) * U(R, .45, .65))                      # 枝梢分一個小叉（Y 形）
            dd = Pt[min(k + 1, len(Pt) - 1)] - Pt[k]
            dd /= np.linalg.norm(dd) + 1e-9
            a = R.choice((-1, 1)) * U(R, .45, .75)
            dd = np.array((dd[0] * math.cos(a) - dd[1] * math.sin(a), dd[0] * math.sin(a) + dd[1] * math.cos(a), dd[2] + .08))
            dd /= np.linalg.norm(dd)
            l2 = ln * U(R, .30, .50)
            s2 = np.linspace(0, l2, 5)
            P2 = Pt[k][None] + s2[:, None] * dd[None]
            r2 = float(rt[k]) * .75 * (1 - .6 * s2 / l2) + .0015
            if clearance(P2[1:], r2[1:], {x['id']}).min() > .004 and (P2[:, 2] - r2).min() > .01 and inside(P2):
                y = new_rec(R, 'twig', P2, s2, r2, ('open', 'tip'), parent=x['id'])
                add_seg(y, 2)
    # 交叉處（夾落葉的位置）
    br = [x for x in RECS if x['kind'] in ('branch', 'fork')]
    for a in range(len(br)):
        for b in range(a + 1, len(br)):
            A, B = br[a], br[b]
            if A.get('parent') == B['id'] or B.get('parent') == A['id']:
                continue
            Pa, Pb = A['P'][::2], B['P'][::2]
            d = np.linalg.norm(Pa[:, None] - Pb[None], axis=2) - A['r'][::2][:, None] - B['r'][::2][None]
            i, j = np.unravel_index(d.argmin(), d.shape)
            if d[i, j] < .03:
                CONTACTS.append(((Pa[i] + Pb[j]) / 2).tolist())
    # 地上小枝
    allP = np.vstack([x['P'] for x in br])
    lo, hi = allP[:, :2].min(0) - V['margin'] * .6, allP[:, :2].max(0) + V['margin'] * .6
    lt = 0
    for _ in range(V['litter'] * 8):
        if lt >= V['litter']:
            break
        c = np.array((U(R, lo[0], hi[0]), U(R, lo[1], hi[1])))
        if ((c[0] / (V['L'] / 2 + V['margin'] * .4)) ** 2 + (c[1] / (V['W'] / 2 + V['margin'] * .4)) ** 2) > 1:
            continue
        ln = U(R, .14, .40)
        Q, ss = xy_path(R, c, U(R, 0, math.pi), ln, .25)
        rl = U(R, .005, .011) * (1 - .4 * ss / ln) + .001
        Pl = np.c_[Q, rl * .75 + V['mound'] * .35]
        if clearance(Pl, rl, set()).min() > .01 and inside(Pl, .05):
            x = new_rec(R, 'litter', Pl, ss, rl, ('break', 'tip'))
            add_seg(x, 2)
            lt += 1
    print('PLAN', v, {k: sum(1 for x in RECS if x['kind'] == k) for k in ('branch', 'fork', 'stub', 'twig', 'litter')},
          'contacts', len(CONTACTS), 'top', round(float(max(x['P'][:, 2].max() + x['r'].max() for x in RECS)), 3))
    return RECS


def _excl(rec):
    ex = {rec['id']}
    if rec['parent'] is not None:
        ex.add(rec['parent'])
    ex |= {x['id'] for x in RECS if x['parent'] == rec['id']}
    return ex


def cleanup():
    """最後一輪：還有穿進別根超過 4 mm 的，找出是哪兩件，拿掉比較小的那件（細枝、斷枝樁、分岔，連同它的子件）。"""
    global SEG, OWN
    dead = set()
    for _ in range(4):
        live = [x for x in RECS if x['id'] not in dead]
        SEG, OWN = np.zeros((0, 8)), np.zeros(0, int)
        for x in live:
            add_seg(x, 1 if x['kind'] == 'stub' else (2 if x['kind'] in ('twig', 'litter') else 3))
        bad = set()
        for rec in live:
            P, r = rec['P'], rec['r']
            keep = np.ones(len(P), bool)
            if rec['ends'][0] == 'open':
                keep = rec['s'] > float(RECS[rec['parent']]['r'].max()) * 1.1
            if not keep.any():
                continue
            ex = _excl(rec)
            for o in set(OWN.tolist()) - ex:
                m = OWN == o
                S = SEG[m]
                a_, b_ = S[:, :3], S[:, 3:6]
                ab = b_ - a_
                u = np.clip(((P[keep][:, None] - a_[None]) * ab[None]).sum(2) / ((ab ** 2).sum(1) + 1e-12)[None], 0, 1)
                d = np.linalg.norm(P[keep][:, None] - (a_[None] + u[..., None] * ab[None]), axis=2) - r[keep][:, None] - (S[None, :, 6] + (S[None, :, 7] - S[None, :, 6]) * u)
                if d.min() < -.004:
                    x, y = rec, RECS[o]
                    rank = lambda z: (z['kind'] in ('branch',), z['r0'])
                    bad.add(min((x, y), key=rank)['id'])
        bad -= {x['id'] for x in RECS if x['kind'] == 'branch'}
        if not bad:
            break
        while True:
            more = {x['id'] for x in RECS if x['parent'] in bad | dead and x['id'] not in bad | dead}
            if not more:
                break
            bad |= more
        dead |= bad
    for x in RECS:
        x['dead'] = x['id'] in dead
    print('CLEANUP removed', len(dead), sorted(RECS[i]['kind'] for i in dead))


def plan_checks():
    """各根之間的 3D 穿插（解析：軸線 + 半徑）。分岔、樁、細枝和自己的母枝不算。"""
    worst = []
    for rec in RECS:
        if rec.get('dead'):
            continue
        excl = _excl(rec)
        P, r = rec['P'], rec['r']
        keep = np.ones(len(P), bool)
        if rec['ends'][0] == 'open':
            par = RECS[rec['parent']]
            keep = rec['s'] > float(par['r'].max()) * 1.1
        if not keep.any():
            continue
        c = clearance(P[keep], r[keep], excl)
        worst.append(float(c.min()))
        if c.min() < -.005:
            print('OVERLAP', rec['id'], rec['kind'], 'parent', rec['parent'], round(float(c.min()), 4))
    pen = [w for w in worst if w < -.005]
    return dict(pieces=len(worst), penetrating_over_5mm=len(pen), worst_m=round(min(worst), 4) if worst else None)


# ---------------------------------------------------------------- 網格
class MB:
    def __init__(self):
        self.V, self.F, self.UV, self.fib, self.mk, self.kind, self.fz = [], [], [], [], [], [], []

    def v(self, p, fib=0.0, mk=0.0, kind=0):
        self.V.append(tuple(float(x) for x in p))
        self.fib.append(fib)
        self.mk.append(mk)
        self.kind.append(kind)
        return len(self.V) - 1

    def f(self, idx, uvs, kind=0):
        self.F.append(tuple(idx))
        self.UV.append([tuple(map(float, u)) for u in uvs])
        self.fz.append(kind)


def nside(r0, lv):
    if lv == 0:
        return int(np.clip(round(5 + r0 * 68), 5, 14))
    if lv == 1:
        return int(np.clip(round(4 + r0 * 50), 5, 11))
    return int(np.clip(round(3 + r0 * 24), 4, 6))


def tube(mb, rec, lv, col=False):
    P, s, r = rec['P'], rec['s'], rec['r']
    r0 = rec['r0']
    Ls = float(s[-1])
    if col:
        ds, ns = .30, 6
    else:
        ds = float(np.clip(r0 * 1.3, .03, .12)) * LODMUL[lv]
        ds = min(ds, .45)
        ns = nside(r0, lv)
        if rec['kind'] in ('twig', 'litter'):
            ns = 5 if lv == 0 else 4
            ds = (.05 if lv == 0 else .10)
        if rec['kind'] == 'stub':
            ns = max(4, int(nside(r0, lv) * .7))
    nr = max(2, int(math.ceil(Ls / ds)) + 1)
    sr = np.linspace(0, Ls, nr)
    C = np.stack([np.interp(sr, s, P[:, k]) for k in range(3)], -1)
    Rr = np.interp(sr, s, r)
    rs = random.Random(rec['seed'])
    off = rs.random() * 100
    mk = float(sm(r0, .025, .06)) if rec['kind'] in ('branch', 'fork') else 0.0
    # 平行移動的框架；起點 N 朝下（接縫在底下）
    T = np.gradient(C, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-12
    N =np.array((0, 0, -1.0)) - T[0] * np.dot((0, 0, -1.0), T[0])
    if np.linalg.norm(N) < 1e-3:
        N = np.array((0, 1.0, 0)) - T[0] * T[0, 1]
    N /= np.linalg.norm(N)
    rings = []
    for i in range(nr):
        if i:
            N = N - T[i] * np.dot(N, T[i])
            N /= np.linalg.norm(N) + 1e-12
        B = np.cross(T[i], N)
        rr = Rr[i]
        for (sb, amp) in rec['bulge']:
            rr *= 1 + amp * math.exp(-((sr[i] - sb) / max(r0 * 1.4, .02)) ** 2)
        if not col:
            rr *= 1 + .07 * noise.noise(Vector(C[i] * 7 + off))
        ring = []
        for j in range(ns):
            th = 2 * math.pi * j / ns
            d = N * math.cos(th) + B * math.sin(th)
            fib = 0.0
            rj = rr
            if not col:
                rj *= 1 + .035 * noise.noise(Vector(C[i] * 13 + d * .3 + off * 1.7))
                for e in (0, 1):
                    if rec['ends'][e] != 'break':
                        continue
                    de = sr[i] if e == 0 else Ls - sr[i]
                    dp = rec['peel'][e] * r0
                    ang = math.cos(th - rec['tear'][e])
                    w = float(sm(dp - de, 0, dp * .35)) * float(sm(ang, -.05, .35))
                    w *= float(sm(noise.noise(Vector(C[i] * 9 + d + off)) + .5, .2, .5))
                    fib = max(fib, w)
                rj *= 1 - .07 * fib
            ring.append(mb.v(C[i] + d * rj, fib=fib, mk=mk))
        rings.append((ring, rr, N.copy(), B.copy()))
    k_ = float(np.clip(.10 / max(r0, 1e-3), 1.0, 2.6))       # 細枝的樹皮紋縮小（鱗片大小跟著枝粗細）
    circ = lambda i, j: 2 * math.pi * Rr[i] * j / ns * k_
    sr_uv = sr * k_
    for i in range(nr - 1):
        a, b = rings[i][0], rings[i + 1][0]
        for j in range(ns):
            j1 = (j + 1) % ns
            mb.f((a[j], a[j1], b[j1], b[j]), [(sr_uv[i], circ(i, j)), (sr_uv[i], circ(i, j + 1)), (sr_uv[i + 1], circ(i + 1, j + 1)), (sr_uv[i + 1], circ(i + 1, j))])
    # 兩頭
    for e in (0, 1):
        i = 0 if e == 0 else nr - 1
        ring, rr, Ne, Be = rings[i]
        sg = -1 if e == 0 else 1
        Te = T[i] * sg
        kind = rec['ends'][e]
        if kind == 'open':
            continue
        if col or kind == 'tip':
            c = mb.v(C[i] + Te * rr * (1.5 if kind == 'tip' and not col else 0), fib=0.0, mk=mk)
            for j in range(ns):
                j1 = (j + 1) % ns
                q = (ring[j], ring[j1], c) if e == 1 else (ring[j1], ring[j], c)
                mb.f(q, [(sr_uv[i], circ(i, j)), (sr_uv[i], circ(i, j + 1)), (sr_uv[i] + sg * rr, circ(i, j + .5))])
            continue
        # 撕裂的斷口：一圈參差往外伸（撕裂那側長）、收到中心一點；整片纖維色
        ext = []
        rng = random.Random(rec['seed'] + e)
        for j in range(ns):
            th = 2 * math.pi * j / ns
            d = Ne * math.cos(th) + Be * math.sin(th)
            ln = rr * (.10 + .55 * max(0, math.cos(th - rec['tear'][e])) ** 2 * rng.uniform(.5, 1.3) + .10 * rng.random()) * rec['ext'][e]
            ext.append((mb.v(C[i] + Te * ln + d * rr * .80, fib=1.0, mk=0), ln))
        cen = mb.v(C[i] + Te * rr * .22 * rec['ext'][e], fib=1.0, mk=0)
        # 斷口的 UV 用平面投影（沿撕裂方向 × 跟它垂直的方向），纖維順著撕裂方向排成平行條紋；
        # 不再用「沿枝 × 繞圈」收到中心一點，那樣每個三角扇各自拉長，會排成 V 字形。
        Tn = T[i] / (np.linalg.norm(T[i]) + 1e-12)
        rdT = Ne * math.cos(rec['tear'][e]) + Be * math.sin(rec['tear'][e])
        wvT = np.cross(Tn, rdT)
        Ci = C[i]
        v0 = circ(i, ns / 2)

        def cuv(vid):
            q = np.array(mb.V[vid]) - Ci
            return (sr_uv[i] + (float(q @ Tn) + .8 * float(q @ rdT)) * k_, v0 + float(q @ wvT) * k_)
        for j in range(ns):
            j1 = (j + 1) % ns
            if e == 1:
                qa, qb = (ring[j], ring[j1], ext[j1][0], ext[j][0]), (ext[j][0], ext[j1][0], cen)
            else:
                qa, qb = (ring[j1], ring[j], ext[j][0], ext[j1][0]), (ext[j1][0], ext[j][0], cen)
            mb.f(qa, [cuv(x) for x in qa])
            mb.f(qb, [cuv(x) for x in qb])
        for k, j in enumerate(ring):
            mb.fib[j] = max(mb.fib[j], .55)
        if lv <= 1:
            for sp in rec['splint'][e][: (None if lv == 0 else 2)]:
                splinter(mb, C[i], Te, Ne, Be, rr, sp, lv)


def splinter(mb, c, Te, Ne, Be, rr, sp, lv):
    """斷口上一條撕開的木刺：扁長條、尖端收尖，根部埋進枝裡。"""
    th = sp['th']
    rd = Ne * math.cos(th) + Be * math.sin(th)
    wv = np.cross(Te, rd)
    wv /= np.linalg.norm(wv) + 1e-12
    ln, w = sp['len'], sp['w']
    tk = max(.004, w * .22)
    base = c - Te * ln * .25 + rd * rr * .82
    segs = 3 if lv == 0 else 2
    rings = []
    for k in range(segs + 1):
        t = k / segs
        p = base + Te * ln * t + rd * (rr * sp['out'] * t * t)
        ww, tt = w * (1 - .70 * t ** 1.5) * .5, tk * (1 - .55 * t) * .5
        rings.append([mb.v(p + wv * a * ww + rd * b * tt, fib=1.0, kind=2) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    tipv = mb.v(base + Te * ln * 1.12 + rd * rr * sp['out'] * 1.2, fib=1.0, kind=2)
    for k in range(segs):
        a, b = rings[k], rings[k + 1]
        for j in range(4):
            j1 = (j + 1) % 4
            mb.f((a[j], a[j1], b[j1], b[j]), [(ln * k / segs, j * w / 2), (ln * k / segs, (j + 1) * w / 2), (ln * (k + 1) / segs, (j + 1) * w / 2), (ln * (k + 1) / segs, j * w / 2)])
    a = rings[-1]
    for j in range(4):
        j1 = (j + 1) % 4
        mb.f((a[j], a[j1], tipv), [(ln, j * w / 2), (ln, (j + 1) * w / 2), (ln * 1.12, (j + .5) * w / 2)])


def mound(mb, lv):
    """腳下一層落葉土：只在枝底下附近隆起一點，外緣鑽進地面（不留邊）。"""
    br = [x for x in RECS if x['kind'] in ('branch', 'fork') and not x.get('dead')]
    pts = np.vstack([np.c_[x['P'][::2, :2], x['r'][::2]] for x in br])
    low = np.vstack([x['P'][::2] for x in br])[:, 2] - pts[:, 2] < .16
    pts = pts[low]
    lo, hi = pts[:, :2].min(0) - V['margin'], pts[:, :2].max(0) + V['margin']
    sp = {0: .08, 1: .15, 2: .30}[lv]
    nx, ny = int((hi[0] - lo[0]) / sp) + 1, int((hi[1] - lo[1]) / sp) + 1
    H = V['mound']
    grid = {}
    hs = np.zeros((nx, ny))
    for ix in range(nx):
        for iy in range(ny):
            x, y = lo[0] + ix * sp, lo[1] + iy * sp
            d = np.min(np.hypot(pts[:, 0] - x, pts[:, 1] - y) - pts[:, 2])
            d += V['margin'] * .30 * noise.noise(Vector((x * .55, y * .55, 9.7)))       # 外緣不規則（不要沿枝等距一圈，看起來像一塊墊子）
            f = float(sm(V['margin'] * .8 - d, 0, V['margin'] * .7)) ** 1.3
            n = .65 + .35 * noise.noise(Vector((x * 2.3, y * 2.3, 5.1)))
            hs[ix, iy] = H * f * n - .022
    for ix in range(nx - 1):
        for iy in range(ny - 1):
            q = [(ix, iy), (ix + 1, iy), (ix + 1, iy + 1), (ix, iy + 1)]
            if max(hs[a, b] for a, b in q) < -.004:
                continue
            ids = []
            for a, b in q:
                if (a, b) not in grid:
                    x, y = lo[0] + a * sp, lo[1] + b * sp
                    grid[(a, b)] = mb.v((x, y, max(hs[a, b], -.022)), kind=1)
                ids.append(grid[(a, b)])
            mb.f(ids, [(lo[0] + a * sp, lo[1] + b * sp) for a, b in q], kind=1)


def to_object(mb, name, mat):
    me = bpy.data.meshes.new(name)
    me.from_pydata(mb.V, [], mb.F)
    me.validate(clean_customdata=False)
    uvl = me.uv_layers.new(name='UVMap')
    uv = np.array([u for f in mb.UV for u in f], np.float32)
    uvl.data.foreach_set('uv', uv.ravel())
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    return o


def _loops(me):
    vi = np.empty(len(me.loops), np.int32)
    me.loops.foreach_get('vertex_index', vi)
    return vi


def vertex_ao(o, rays=12, dist=.28):
    me = o.data
    co = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    vn = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get('normal', vn)
    vn = vn.reshape(-1, 3)
    tree = BVHTree.FromPolygons([Vector(p) for p in co], [tuple(p.vertices) for p in me.polygons])
    rs = np.random.RandomState(3)
    dirs = rs.randn(rays, 3)
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    ao = np.ones(len(co))
    gt = None
    for i in range(len(co)):
        n = vn[i]
        hit = 0
        for d in dirs:
            if d @ n < 0:
                d = -d
            dd = Vector(d * .85 + n * .15).normalized()
            if tree.ray_cast(Vector(co[i] + n * .004), dd, dist)[0] is not None:
                hit += 1
            elif co[i][2] + dd.z * dist < -.01:
                hit += .5                                    # 地面也遮
        ao[i] = 1 - .62 * hit / rays
    return ao


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
    nz = np.array([noise.noise(Vector(p * 2.2)) for p in co])
    nz2 = np.array([noise.noise(Vector(p * 5.0 + 11.0)) for p in co])
    W = np.zeros((n, 5))
    moss = mk * sm(vn[:, 2], .10, .60) * sm(nz + .25 * nz2, -.38, .08) * (1 - fib)
    soil = sm(.09 - co[:, 2], 0, .09) * .75 * (kind == 0)
    W[:, 0] = moss
    W[:, 2] = fib
    W[:, 4] = soil * (1 - moss)
    m1 = kind == 1
    W[m1, 4] = 1.0
    W[m1, 0] = .75 * sm(nz[m1] + .3 * nz2[m1], .18, .45)
    W[m1, 1] = .35 * sm(nz2[m1], .25, .6)                   # 爛葉碎木屑
    s = W.sum(1, keepdims=True)
    W = np.where(s > 1, W / np.maximum(s, 1e-6), W)
    ao = vertex_ao(o) if lv < 2 else np.ones(n)
    ao = ao * (.62 + .38 * sm(co[:, 2], -.02, .16))
    vi = _loops(me)
    ca = me.color_attributes.new('Layers', 'FLOAT_COLOR', 'CORNER')
    ca.data.foreach_set('color', W[vi, :4].astype(np.float32).ravel())
    me.color_attributes.active_color = ca
    me.uv_layers.new(name='Extra').data.foreach_set('uv', np.stack([W[vi, 4], ao[vi]], -1).astype(np.float32).ravel())
    me.uv_layers.active_index = 0
    for l in me.uv_layers:
        l.active_render = l.name == 'UVMap'


def hidden_faces(o, mb):
    """枝根埋進母枝裡的面（分岔、樁、細枝的起點）：每個頂點都在別根裡面就刪。"""
    me = o.data
    co = np.array(mb.V)
    inside = np.zeros(len(co), bool)
    a, b = SEG[:, :3], SEG[:, 3:6]
    ab = b - a
    L2 = (ab ** 2).sum(1) + 1e-12
    for k in range(0, len(co), 2000):
        P = co[k:k + 2000]
        u = np.clip(((P[:, None] - a[None]) * ab[None]).sum(2) / L2[None], 0, 1)
        d = np.linalg.norm(P[:, None] - (a[None] + u[..., None] * ab[None]), axis=2)
        rr = SEG[None, :, 6] + (SEG[None, :, 7] - SEG[None, :, 6]) * u
        inside[k:k + 2000] = (d < rr * .90 - .002).any(1)
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


def body(lv, col=False):
    mb = MB()
    for rec in RECS:
        if rec.get('dead'):
            continue
        if lv == 2 and rec['kind'] in ('twig', 'litter') and not col:
            continue
        if lv == 1 and rec['kind'] == 'litter' and rec['id'] % 2:
            continue
        if col and (rec['kind'] not in ('branch', 'fork') or rec['r0'] < .03):
            continue
        tube(mb, rec, lv, col)
    if not col:
        mound(mb, lv)
    nm = f'{NAMES[V["v"]]}_{"Collision" if col else "LOD%d" % lv}'
    o = to_object(mb, nm, layer_mat())
    if col:
        o.data.materials.clear()
        while o.data.uv_layers:
            o.data.uv_layers.remove(o.data.uv_layers[0])
        return o
    gone = hidden_faces(o, mb)
    print('LOD', lv, 'hidden faces removed', gone)
    finish_body(o, mb, lv)
    return o


# ---------------------------------------------------------------- 植物卡
class Cards:
    def __init__(self):
        self.V, self.F, self.UV, self.tag = [], [], [], []

    def quad(self, pts, uvs, tag):
        o = len(self.V)
        self.V += [tuple(map(float, p)) for p in pts]
        self.UV += uvs
        self.F.append((o, o + 1, o + 2, o + 3))
        self.tag.append(tag)

    def leaf(self, p, n, yaw, w, h, rect, tag, curl=.012):
        n = Vector(n).normalized()
        a = n.orthogonal().normalized()
        a = (Matrix.Rotation(yaw, 3, n) @ a).normalized()
        b = n.cross(a)
        u0, v0, u1, v1 = rect
        p = Vector(p)
        rows = [p - a * h * .5, p, p + a * h * .5]
        lift = [n * curl, n * 0, n * curl * 1.4]
        o = len(self.V)
        for k, (c, l) in enumerate(zip(rows, lift)):
            for sgn in (-.5, .5):
                q = c + l + b * (w * sgn) + n * (abs(sgn) * curl * .6)
                self.V.append(tuple(q))
                self.UV.append((u0 + (u1 - u0) * (sgn + .5), v0 + (v1 - v0) * k / 2))
        for k in range(2):
            i = o + 2 * k
            self.F.append((i, i + 1, i + 3, i + 2))
            self.tag.append(tag)

    def upright(self, base, h, w, rect, yaw, tag, lean=(0, 0, 0)):
        u0, v0, u1, v1 = rect
        base = Vector(base)
        up = (Vector((0, 0, 1)) + Vector(lean)).normalized()
        for k in range(2):
            a = yaw + k * math.pi / 2
            side = Vector((math.cos(a), math.sin(a), 0))
            self.quad([base - side * w / 2, base + side * w / 2, base + side * w / 2 + up * h, base - side * w / 2 + up * h],
                      [(u0, v0), (u1, v0), (u1, v1), (u0, v1)], tag)

    def obj(self, name, keep, seed):
        rs = random.Random(seed)
        tags = sorted(set(self.tag))
        kept = {t for t in tags if rs.random() < keep}
        F = [f for f, t in zip(self.F, self.tag) if t in kept]
        used = sorted({i for f in F for i in f})
        mp = {v: k for k, v in enumerate(used)}
        me = bpy.data.meshes.new(name)
        me.from_pydata([self.V[i] for i in used], [], [tuple(mp[i] for i in f) for f in F])
        uvl = me.uv_layers.new(name='UVMap')
        for lp in me.loops:
            uvl.data[lp.index].uv = self.UV[used[lp.vertex_index]]
        me.materials.append(lib8()['plant_material']())
        o = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(o)
        return o


def make_cards(body0):
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
        h = U(R, .075, .13) * big
        w = h * asp
        for lift in (.006, .014, .024):
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
    lo, hi = allP[:, :2].min(0) - .45, allP[:, :2].max(0) + .45
    area = (hi[0] - lo[0]) * (hi[1] - lo[1])
    nl = int(area * {'S': 15, 'M': 13, 'L': 11}[V['v']])
    placed = 0
    for _ in range(nl * 3):
        if placed >= nl:
            break
        x, y = U(R, lo[0], hi[0]), U(R, lo[1], hi[1])
        h = tree.ray_cast(Vector((x, y, 3)), Vector((0, 0, -1)), 6)
        if h[0] is None:                                          # 落葉土外面的地上也撒一些（蓋掉土堆的邊，不像一塊墊子）
            near = tree.find_nearest(Vector((x, y, 0)), .30)
            if near[0] is None or R.random() < .35:
                continue
            h = (Vector((x, y, .002)), Vector((0, 0, 1)), 0, 0)
        if h[1].z < .45:
            continue
        if h[0].z > .06 and R.random() < .55:                     # 枝頂上的葉少一點
            continue
        n = (h[1] + Vector((U(R, -.25, .25), U(R, -.25, .25), 0))).normalized()
        if put_leaf(h[0], n):
            placed += 1
    tl = 0
    for c in CONTACTS:                                            # 夾在交叉處的落葉（高處的交叉不放，不然頂上一團葉）
        if c[2] > V['H'] * .45:
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
    # 主枝旁地上的小褐蕈、堆邊的蕨
    nm = 0
    if V['v'] in ('M', 'L'):
        main = RECS[0]
        for _ in range({'M': 2, 'L': 3}[V['v']]):
            i = int(len(main['P']) * U(R, .15, .85))
            T, N0, B0 = frame_at(main['P'], i)
            sd = N0 * R.choice((-1, 1))
            for k in range(R.randint(2, 3)):
                b = main['P'][i] + sd * (main['r'][i] + U(R, .03, .08)) + T * U(R, -.08, .08)
                h = tree.ray_cast(Vector((b[0], b[1], 2)), Vector((0, 0, -1)), 4)
                if h[0] is None or h[0].z > .10:
                    continue
                q0 = len(C.V)
                C.upright(h[0] - Vector((0, 0, .01)), U(R, .055, .10), U(R, .06, .10), R.choice(mush), U(R, 0, math.pi), tag)
                if ok_pts(C.V[q0 + 2:q0 + 4] + C.V[q0 + 6:q0 + 8]):
                    tag += 1
                    nm += 1
                else:
                    del C.V[q0:], C.UV[q0:]
                    del C.F[-2:], C.tag[-2:]
    nf = 0
    if V['v'] == 'L':
        for sx in (-1, 1):
            b = Vector((sx * (V['L'] / 2 - .05), U(R, -.3, .3) * V['W'] / 2, 0))
            h = tree.ray_cast(b + Vector((0, 0, 2)), Vector((0, 0, -1)), 4)
            if h[0] is None or h[0].z > .09:
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
    print('CARDS leaves', placed, 'trapped', tl, 'mush', nm, 'fern', nf)
    return C


# ---------------------------------------------------------------- 匯出
def _tri(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def _triangulate(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
    dead = [f for f in bm.faces if f.calc_area() < 1e-10]
    if dead:
        bmesh.ops.delete(bm, geom=dead, context='FACES')
    bm.to_mesh(o.data)
    bm.free()


def _select(objs, active):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active


def run(v):
    t0 = time.time()
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    asset = NAMES[v]
    plan(v)
    cleanup()
    pc = plan_checks()
    print('PLANCHECK', json.dumps(pc))
    lods, bodies = {}, {}
    for lv in (0, 1, 2):
        b = body(lv)
        _triangulate(b)
        bodies[lv] = b
        print('LOD', lv, 'body', _tri(b), round(time.time() - t0), 's')
    cards = make_cards(bodies[0])
    for lv in (0, 1, 2):
        d = cards.obj(f'{DET}_LOD{lv}', PLANT_KEEP[lv], lv)
        _triangulate(d)
        lods[lv] = [bodies[lv], d]
        print('LOD', lv, 'detail', _tri(d))
    col = body(0, col=True)
    _triangulate(col)
    col.hide_render = True
    col.display_type = 'WIRE'
    root = bpy.data.objects.new(asset, None)
    bpy.context.scene.collection.objects.link(root)
    for o in [o for lst in lods.values() for o in lst] + [col]:
        o.data.name = o.name
        o.parent = root
    piv = _exec(ROOTS + '/dr_pivot.py', 'dr_pivot')
    c = piv['to_bottom_centre'](root, bodies[0])
    bpy.context.scene['dr09_plan'] = json.dumps(dict(variant=v, plan_check=pc, contacts=len(CONTACTS),
                                                     pieces={k: sum(1 for x in RECS if x['kind'] == k and not x.get('dead')) for k in ('branch', 'fork', 'stub', 'twig', 'litter')},
                                                     axes=[dict(kind=x['kind'], r0=round(x['r0'], 4), P=np.round(x['P'][::4] - np.array(c), 4).tolist()) for x in RECS if x['kind'] in ('branch', 'fork')]))
    exp = f'{ROOT}/art/exports/d2-logs-b/{asset}'
    os.makedirs(exp, exist_ok=True)
    allm = [o for lst in lods.values() for o in lst] + [col]
    col.hide_render = False
    _select(allm + [root], root)
    bpy.ops.export_scene.fbx(filepath=f'{exp}/{asset}_{VER}.fbx', use_selection=True, object_types={'MESH', 'EMPTY'},
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', bake_space_transform=True,
                             axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE', use_mesh_modifiers=True, colors_type='LINEAR',
                             add_leaf_bones=False, bake_anim=False, path_mode='STRIP', embed_textures=False)
    try:
        _select(lods[0] + [root], root)
        bpy.ops.export_scene.gltf(filepath=f'{exp}/{asset}_{VER}.glb', use_selection=True, export_format='GLB', export_yup=True)
    except Exception as e:
        print('glb', e)
    col.hide_render = True
    info = {lv: {o.name: _tri(o) for o in lst} for lv, lst in lods.items()}
    info['collision'] = _tri(col)
    print('TRIS', json.dumps(info))
    os.makedirs(HERE + '/blend', exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_{VER}.blend', copy=True)
    print('GAME_DONE', asset, round(time.time() - t0), 's')


if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    try:
        run(a[0] if a else 'M')
    except Exception:
        traceback.print_exc()
        sys.exit(1)
