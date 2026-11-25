# DR09 斷枝堆 v013（L 樣品）：整體重構。原始參考（三視圖 L 列、情境圖、近景圖）為主，v012 只當工具來源（v012 及以前全部保留）。
# 不再沿用 v006–v012 的擺法；以參考圖可辨識的構件重新排：
#   底層：C（A 下面的支撐木，A 左段因此離地留一道縫）、後方倒木 G／D、右前低木 E、外圍中細枝（前 F1／F2、後 L1／L2）。
#   前側主木 A：最粗（直徑約 33 cm）、左端大撕裂斷口朝左前、上面成片的苔與一叢蘑菇。
#   拱形枝 B／B2／B3：本身彎曲的枝，從後左跨過 A 上方再落到右前／右側，正面看是一層層的拱，拱下透空。
#   斜挑枝 T1／T2：從堆中段往右後上方斜挑，梢端是撕裂斷口（T1 為最高點，約 1.2 m）。
#   往右下落地的枝 R1／R2、M5／M6，斜跨的中型枝 X2，左後填量 L3，中下層補量 N1–N7，俯視左後／右後補量 N8／N9。
#   材質：苔集中在粗木頂面、成片但邊緣破碎（重定義 finish_body_base 的門檻）；蘑菇在 A 左段頂面兩叢、尺寸放大（重定義 make_cards）。
# 擺放：每根用 3D 控制點（x, y, 彎曲高度）描述自己的彎曲；整根剛體落下到第一個支點，再繞它朝重心那側倒到第二個支點
#  （保留枝本身的弧度，不是被地形捏成波浪）；最後只做局部抬升避開穿插。
# 用法：
#   blender -b --python art/source/d2-logs-b/game_dr09v13.py -- L 1   （灰模：blend/…_v013_greybox.blend）
#   blender -b --python art/source/d2-logs-b/game_dr09v13.py -- L 2   （完整：匯出 FBX／GLB、存 blend/…_v013.blend）
import sys, os, math, types, random, traceback, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
H5 = {'__name__': 'dr09_v5_for_v13', '__file__': HERE + '/game_dr09v5.py'}
exec(compile(open(H5['__file__'], encoding='utf-8').read(), H5['__file__'], 'exec'), H5)
ns = H5['ns']
ns['VER'] = 'v013'
ns['VARIANTS']['L'].update(twigs=55, litter=16, seed=91313)
LAYOUT = json.loads(os.environ.get('DR9LAYOUT', '{}'))       # 迭代用：覆寫個別構件的參數（不改程式）


def CAPC(rec):
    return rec.get('capc', .16 if rec.get('heavy') else .50)


def smooth_r(r, n=15):
    k = np.hanning(n)
    k /= k.sum()
    return np.convolve(np.pad(r, n // 2, mode='edge'), k, 'valid')


def XS(rec, s, th):
    x = rec.get('xs')
    if not x:
        return 1.0
    ph = th - x['tw0'] - x['twr'] * s
    for c, a, w in x.get('twk', ()):
        ph -= a / (1 + math.exp(-(s - c) / w))
    e = x['e']
    for c, a, w in x.get('ek', ()):
        e *= 1 + a * math.exp(-((s - c) / w) ** 2)
    return 1 - e * (1 - math.cos(2 * ph)) - x['h3'] * .5 * (1 - math.cos(3 * ph + x['p3']))


def plan(v):
    global V, SEG, OWN, RECS, CONTACTS
    assert v == 'L', 'v013 先做 L 樣品'
    V = dict(VARIANTS[v], v=v)
    V['H'] = 1.30
    SEG, OWN, RECS, CONTACTS = np.zeros((0, 8)), np.zeros(0, int), [], []
    R = random.Random(V['seed'])
    NAMED = {}

    def end_caps(rec, e_list):
        for e in e_list:
            tc = rec['tear'][e]
            rr = float(rec['r'][0 if e == 0 else -1])
            kind_ = R.choice(('notch', 'fiber', 'slant', 'fiber'))
            rec['cap'][e] = dict(tilt=U(R, .25, .55), notch=tc + math.pi * U(R, .6, 1.1), nw=U(R, .6, 1.0) if kind_ != 'slant' else .2,
                                 tooth=U(R, .3, .6), lip=tc - math.pi * U(R, .4, .7), lw=U(R, .4, .6), lipl=U(R, .15, .30))
            n = {'notch': 1, 'fiber': 3, 'slant': 0}[kind_]
            rec['splint'][e] = [dict(th=tc + U(R, -.7, .7), len=rr * U(R, 1.0, 2.6), w=max(.012, rr * U(R, .30, .48)),
                                     out=U(R, 0, .06), tk=U(R, .50, .65)) for _ in range(n)]

    def zpath(ctrl3):
        C3 = np.array(ctrl3, float)
        Q, s = spline_path(C3[:, :2].tolist())
        idx = [int(np.argmin(np.linalg.norm(Q - c[:2], axis=1))) for c in C3]
        sc = np.array([s[i] for i in idx], float)
        sc[0], sc[-1] = 0.0, float(s[-1])
        sc = np.maximum.accumulate(sc)
        z = np.interp(s, sc, C3[:, 2])
        k = max(5, int(.30 / STEP)) | 1
        w = np.hanning(k)
        w /= w.sum()
        z = np.convolve(np.pad(z, k // 2, mode='edge'), w, 'valid')
        return Q, s, z

    def rest3(Q, s, r, zs, mode, sink, excl, maxtilt=.9):
        thin = {x['id'] for x in RECS if x['kind'] in ('twig', 'litter')}
        g = r * (1 - sink)
        sup = np.maximum(g, support(Q, r, set(excl) | thin))
        if mode == 'abs':
            z = zs.copy()
        elif mode == 'never':
            z = zs
        elif mode == 'shift':
            # 盡量保留設計：z = 設計 + a + b·s，(a, b) 取（支撐 − 設計）上凸包的某一段（兩點搭靠），
            # 在各段裡挑「和設計差最少」的；重心不在兩個支點之間的加罰（會翻倒）。
            h = sup - zs
            hull = upper_hull(list(s), list(h))
            w = r ** 2
            sc = float((w * s).sum() / w.sum())
            best_, bk = None, None
            cand = list(zip(hull, hull[1:])) + [(p_, p_) for p_ in hull]
            for (x0, y0), (x1, y1) in cand:
                if x1 - x0 > 1e-6:
                    b_ = (y1 - y0) / (x1 - x0)
                    a_ = y0 - b_ * x0
                    stable = x0 - .05 <= sc <= x1 + .05
                else:                                # 只有一個支點：平移（設計斜率）
                    b_, a_ = 0.0, y0 - 0 * x0
                    stable = False
                if abs(b_) > maxtilt:
                    continue
                z_ = zs + a_ + b_ * s
                if (z_ < sup - 1e-4).any():
                    continue
                key = float(np.abs(a_ + b_ * s).mean()) + (0 if stable else .15)
                if bk is None or key < bk:
                    best_, bk = z_, key
            z = best_ if best_ is not None else zs + float(h.max())
        else:
            # 剛體靜置：枝本身的彎（zs 去掉線性部分）不變；在（支撐 − 彎）的上凸包上取重心所在那一段，
            # 等於兩個支點夾住重心、重心最低的擺法（不會因為壓到某個高點就整根被抬高）。
            A_ = np.c_[s, np.ones_like(s)]
            shape = zs - A_ @ np.linalg.lstsq(A_, zs, rcond=None)[0]
            hull = upper_hull(list(s), list(sup - shape))
            w = r ** 2
            sc = float((w * s).sum() / w.sum())
            seg = (*hull[0], *hull[-1])
            for (x0, y0), (x1, y1) in zip(hull, hull[1:]):
                if x0 - 1e-9 <= sc <= x1 + 1e-9:
                    seg = (x0, y0, x1, y1)
            x0, y0, x1, y1 = seg
            slope = (y1 - y0) / max(x1 - x0, 1e-6)
            z = y0 + float(np.clip(slope, -maxtilt, maxtilt)) * (s - x0) + shape
            z = z + max(0.0, float((sup - z).max()))
            z = np.maximum(z, g)
        P = np.c_[Q, z]
        for _ in range(40):
            cc = clearance(P, r, set(excl))
            if cc.min() > -.002:
                break
            up = np.maximum(-cc + .003, 0)
            kk = 21
            P[:, 2] += np.convolve(np.pad(up, kk // 2, mode='edge'), np.hanning(kk) / np.hanning(kk).sum(), 'valid') * 2.2
        cc = clearance(P, r, set(excl))
        tch = ((P[:, 2] - g) < .012) | (cc < .012)
        runs = int(np.sum(np.diff(np.r_[0, tch.astype(int)]) == 1))
        # 接觸點分別落在哪幾根上（地面 = ground），方便調整設計高度
        who = []
        for i in np.nonzero(tch)[0][::4]:
            if P[i, 2] - g[i] < .012:
                nm = 'ground'
            else:
                d_ = np.linalg.norm(SEG[:, None, :3] * 0 + 0, axis=2) if False else None
                a_, b_ = SEG[:, :3], SEG[:, 3:6]
                ab = b_ - a_
                u = np.clip(((P[i] - a_) * ab).sum(1) / ((ab ** 2).sum(1) + 1e-12), 0, 1)
                dd = np.linalg.norm(P[i] - (a_ + u[:, None] * ab), axis=1) - r[i] - (SEG[:, 6] + (SEG[:, 7] - SEG[:, 6]) * u)
                o = RECS[int(OWN[int(dd.argmin())])]
                nm = o.get('name') or f"{o['kind']}{o['id']}"
            if not who or who[-1][0] != nm:
                who.append((nm, round(float(s[i]), 2)))
        print('    REST_ON', who)
        return P, runs

    def log(name, ctrl3, r0, tp=.50, mode='rest', sink=.10, knots=(), lumps=2, e=(.10, .16), ends=('break', 'break'),
            excl=(), main=False, splint=()):
        o = LAYOUT.get(name, {})
        ctrl3 = o.get('c', ctrl3)
        r0, mode, tp = o.get('r0', r0), o.get('mode', mode), o.get('tp', tp)
        Q, s, zs = zpath(ctrl3)
        t = s / s[-1]
        Lc = float(s[-1])
        bw = o.get('bow', (U(R, .06, .13) * R.choice((-1, 1)) * min(1.0, Lc / 1.6), U(R, -.045, .045) * min(1.0, Lc / 1.6)))
        dch = Q[-1] - Q[0]
        nrm = np.array((-dch[1], dch[0])) / (np.linalg.norm(dch) + 1e-9)
        Q = Q + nrm[None] * (bw[0] * np.sin(math.pi * t) + bw[1] * np.sin(2 * math.pi * t))[:, None]      # 側向弓彎＋S 彎
        s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q, axis=0), axis=1))]
        t = s / s[-1]
        if mode == 'rest':
            zs = zs + U(R, .0, .05) * np.sin(math.pi * t) ** 1.5                                         # 貼地木略拱，下面留縫
        lump = heavy_radius(R, s, 1.0, 0, lumps)
        r = r0 * (1 - tp * t ** .85) * (1 + .16 * np.exp(-t / .05)) * lump
        for c, a in knots:
            r = r * (1 + a * np.exp(-((t - c) / .06) ** 2))
        r = smooth_r(r, 9)
        P, runs = rest3(Q, s, r, zs, mode, sink, excl)
        rec = new_rec(R, 'branch', P, s, r, ends, main=main)
        rec['name'] = name
        L = float(s[-1])
        rec['xs'] = xs_params(R, e)
        rec['xs']['h3'] = U(R, .05, .09)
        rec['xs']['twr'] = U(R, .20, .50) * R.choice((-1, 1))
        rec['xs']['twk'] = [(U(R, .2, .8) * L, U(R, .5, .9) * R.choice((-1, 1)), .10) for _ in range(R.randint(1, 2))]
        rec['xs']['ek'] = [(U(R, .2, .8) * L, U(R, -.4, .5), .25)]
        rec['ext'] = [1.0, 1.0]
        rec['heavy'] = r0 > .06
        cap_params(R, rec)
        end_caps(rec, [k for k in (0, 1) if ends[k] == 'break'])
        for e_, n_, l_ in splint:
            heavy_splinters(R, rec, e_, n_, l_)
        add_seg(rec)
        NAMED[name] = rec
        top = P[:, 2] + r
        print('  LOG', name, 'd_cm', round(r0 * 200, 1), 'len', round(L, 2), 'ends', round(float(P[0, 2] - r[0]), 2),
              round(float(P[-1, 2] - r[-1]), 2), 'top', round(float(top.max()), 2), 'at_x', round(float(P[int(top.argmax()), 0]), 2), 'contact_runs', runs)
        return rec

    def crotch(rec, t, side, fl, up, frac, swing=(.55, .80), wob=.10, name='', tip='break', flare=.72):
        P, s, r = rec['P'], rec['s'], rec['r']
        i = int(len(P) * t)
        T, N0, B0 = frame_at(P, i)
        rp = float(r[i])
        a = math.atan2(T[1], T[0]) + side * U(R, *swing)
        d1 = np.array((math.cos(a), math.sin(a), T[2] * .45 + up))
        d1 /= np.linalg.norm(d1)
        n = max(8, int(fl / STEP))
        sf = np.linspace(0, fl, n + 1)
        L0 = min(rp * 3.2, fl * .45)
        w = np.clip(sf / L0, 0, 1)
        w = w * w * (3 - 2 * w)
        Pf = [P[i].copy()]
        for k in range(1, n + 1):
            d = (1 - w[k]) * T + w[k] * d1
            d /= np.linalg.norm(d)
            Pf.append(Pf[-1] + d * (sf[k] - sf[k - 1]))
        Pf = np.array(Pf)
        lat = np.cross(d1, (0, 0, 1.0))
        lat /= np.linalg.norm(lat) + 1e-9
        Pf += lat[None] * (np.sin(sf / fl * math.pi * U(R, .9, 1.4)) * fl * U(R, -wob, wob) * w)[:, None]
        tf = sf / fl
        rf = rp * frac * (1 - .58 * tf ** .9) + .002
        rf = rf * (1 + (min(flare, frac * 1.55) / frac - 1) * np.exp(-sf / (rp * 1.3)))
        Pf = bend_up(Pf, rf, {rec['id']})
        cmin = float(clearance(Pf, rf, {rec['id']}).min())
        if cmin < .002 or (Pf[:, 2] + rf).max() > V['H'] * 1.05 or not inside(Pf, .1) or (Pf[:, 2] - rf).min() < -.01:
            print('  CROTCH_FAIL', name, round(cmin, 3), round(float((Pf[:, 2] + rf).max()), 2), inside(Pf, .1))
            return None
        f = new_rec(R, 'fork', Pf, sf, rf, ('open', tip), parent=rec['id'])
        f['name'] = name
        f['xs'] = xs_params(R, (.08, .14))
        f['ext'] = [1.0, 1.0]
        f['heavy'] = float(rf[0]) > .05
        if tip == 'break':
            cap_params(R, f)
            end_caps(f, (1,))
        rec['bulge'].append((float(s[i]) + L0 * .35, .14))
        add_seg(f)
        return f

    def fork_any(key, rec, ts, side, fl, up, frac, big=True, **k):
        for t_ in ts:
            for sd in (side, -side):
                f = crotch(rec, t_, sd, fl, up, frac, name=key, **k) if big else add_fork(R, rec, t_, sd, fl, up, (frac * .9, frac * 1.1))
                if f is not None:
                    if not big:
                        f['name'] = key
                        if R.random() < .6:
                            f['ends'][1] = 'break'
                    return f
        print('  FORK_MISSING', key)
        return None

    # ------------------------------------------------------------------ 底層（先擺，後面的木頭搭在上面）
    # 高度欄是設計的軸心高度（依參考正面圖量的），擺放時整根上下平移到剛好接觸；只有一處接觸才會繞支點傾倒。
    C = log('C', [(-.74, .36, 0), (-.68, .00, 0), (-.62, -.40, 0), (-.55, -.78, 0)], .100, .35, sink=.18, lumps=2, e=(.06, .12))
    G = log('G', [(-1.90, .30, 0), (-1.40, .42, .03), (-.85, .58, 0)], .090, .35, sink=.18, lumps=2)
    D = log('D', [(.20, .82, 0), (.80, .74, .03), (1.40, .64, 0), (1.85, .52, 0)], .085, .40, sink=.16, lumps=2)
    E = log('E', [(.55, -.80, 0), (1.10, -.68, .02), (1.75, -.50, 0)], .065, .45, sink=.12)
    L1 = log('L1', [(-1.92, -.05, 0), (-1.70, .30, .05), (-1.40, .70, .08), (-1.10, .95, .02)], .045, .55, e=(.05, .10))
    L2 = log('L2', [(-1.60, .94, 0), (-1.05, .99, .03), (-.45, .99, .04), (.10, .93, 0)], .042, .55, e=(.05, .10))
    F1 = log('F1', [(-1.00, -.93, 0), (-.55, -.85, .03), (-.15, -.82, .02), (.12, -.88, 0)], .048, .55, e=(.05, .10))
    F2 = log('F2', [(.75, -.99, 0), (1.20, -.93, .02), (1.70, -.86, 0)], .040, .55, e=(.05, .10))
    # ------------------------------------------------------------------ 前側主木 A（最粗，左端大斷口朝左前；左段搭在 C 上離地，下面一道縫）
    A = log('A', [(-1.95, -.52, .17), (-1.40, -.43, .27), (-.85, -.31, .33), (-.30, -.18, .30), (.25, -.03, .20), (.85, .12, .10)],
            .165, .42, sink=.20, knots=((.30, .06), (.55, .05)), lumps=3, e=(.10, .15), main=True, splint=((0, 11, .55), (1, 2, .14)))
    # 中下層補量（參考圖正面下半部是實的、俯視也很密）
    N1 = log('N1', [(.20, -.55, .10), (.55, -.40, .14), (.90, -.25, .15), (1.25, -.14, .10), (1.60, -.05, .04)], .045, .55)
    N2 = log('N2', [(.45, .35, .10), (.75, .28, .14), (1.05, .20, .15), (1.40, .12, .10), (1.75, .05, .04)], .042, .55)
    N3 = log('N3', [(-.35, -.55, .08), (-.10, -.35, .16), (.15, -.15, .20), (.40, .06, .18), (.65, .28, .12), (.95, .55, .04)], .048, .55)
    N4 = log('N4', [(-1.75, .55, .08), (-1.50, .38, .18), (-1.25, .20, .26), (-.98, .00, .32)], .045, .55)
    N5 = log('N5', [(1.30, .40, .25), (1.50, .25, .20), (1.70, .07, .12), (1.92, -.15, .02)], .040, .60)
    N6 = log('N6', [(-1.62, -.86, .04), (-1.35, -.76, .10), (-1.10, -.70, .12), (-.85, -.66, .10), (-.60, -.62, .06)], .040, .55)
    N7 = log('N7', [(-.60, .72, .08), (-.30, .68, .14), (.00, .63, .18), (.30, .57, .14), (.60, .50, .06)], .045, .55)
    L3 = log('L3', [(-1.65, .10, .10), (-1.25, .28, .16), (-.85, .42, .18), (-.45, .55, .10)], .052, .55, e=(.05, .11))
    X2 = log('X2', [(-.35, .92, .06), (-.10, .46, .25), (.15, .00, .36), (.40, -.42, .22), (.62, -.80, .05)], .055, .55)
    # ------------------------------------------------------------------ 拱形枝（本身彎，跨過 A 上方，拱下透空）
    B2 = log('B2', [(-.80, -.05, .30), (-.45, .08, .42), (-.05, .12, .45), (.30, .25, .38), (.60, .40, .20), (.85, .50, .06)],
             .080, .50, knots=((.45, .05),), e=(.10, .15), mode='shift')
    B3 = log('B3', [(-.32, .78, .10), (.02, .58, .40), (.38, .36, .62), (.72, .14, .56), (1.02, -.04, .38), (1.28, -.18, .15), (1.45, -.28, .05)],
             .075, .52, knots=((.55, .05),), e=(.10, .15), mode='shift')
    B = log('B', [(-1.00, -.18, .40), (-.85, -.10, .50), (-.65, -.04, .57), (-.40, -.02, .60), (-.10, -.06, .56), (.20, -.22, .44), (.45, -.42, .26), (.66, -.60, .08)], .100, .50, knots=((.25, .06), (.62, .05)), lumps=3, e=(.11, .16),
            splint=((0, 3, .16),), mode='shift')
    # ------------------------------------------------------------------ 右側往下落地、斜跨
    R1 = log('R1', [(.30, .10, .55), (.75, .00, .45), (1.20, -.12, .30), (1.60, -.24, .13), (1.88, -.32, .02)], .065, .60, mode='shift')
    R2 = log('R2', [(.65, .55, .45), (1.05, .48, .34), (1.48, .40, .20), (1.86, .30, .02)], .055, .60)
    M5 = log('M5', [(.75, -.40, .36), (1.05, -.47, .30), (1.35, -.55, .18), (1.65, -.62, .05)], .060, .55, mode='shift')
    M6 = log('M6', [(.30, .95, .05), (.70, .80, .30), (1.10, .70, .40), (1.50, .62, .30), (1.85, .55, .08)], .055, .55)
    # ------------------------------------------------------------------ 斜挑枝（最高點），梢端撕裂斷口
    T1 = log('T1', [(-.05, -.62, .10), (.25, -.45, .32), (.55, -.25, .55), (.82, -.05, .78), (1.05, .12, .98), (1.20, .24, 1.12)], .085, .45,
             knots=((.40, .05), (.70, .05)), e=(.10, .15), splint=((1, 4, .26),), mode='shift')
    T2 = log('T2', [(1.00, -.48, .26), (1.18, -.33, .42), (1.36, -.17, .58), (1.55, -.02, .75), (1.66, .07, .84)], .065, .48, splint=((1, 3, .18),), mode='shift')
    # 俯視 X 形交叉：左後→右前、右後→左前兩根中型彎枝，跨在中層上（補俯視空白、中層體積）
    N8 = log('N8', [(-1.60, .88, .05), (-1.25, .60, .18), (-.92, .34, .30), (-.62, .10, .38)], .055, .55, mode='rest')
    N9 = log('N9', [(1.62, .88, .05), (1.32, .66, .18), (1.02, .46, .30), (.75, .28, .36)], .052, .55, mode='rest')
    # ------------------------------------------------------------------ 分叉（大的用連續外張的 crotch，小的用 add_fork）
    fork_any('Aa', A, (.58, .52, .64), 1, .70, .22, .45, swing=(.50, .75))
    fork_any('Ba', B, (.70, .64, .76), -1, .45, -.08, .50)
    fork_any('Bb', B, (.30, .36), 1, .35, .15, .42, big=False)
    fork_any('B2a', B2, (.55, .48, .62), 1, .50, .18, .50)
    fork_any('B3a', B3, (.45, .40, .52), -1, .45, .12, .50)
    fork_any('T1a', T1, (.62, .56, .68), -1, .45, .35, .50, swing=(.50, .70))
    fork_any('T1b', T1, (.35, .30), 1, .30, .10, .40, big=False)
    fork_any('T2a', T2, (.50, .45, .58), 1, .30, .15, .45, big=False)
    fork_any('R1a', R1, (.45, .40, .52), -1, .40, -.06, .50)
    fork_any('R1b', R1, (.75, .70), 1, .28, .05, .40, big=False)
    fork_any('R2a', R2, (.60, .55), 1, .30, .05, .45, big=False)
    for nm_, rec_ in (('X2a', X2), ('Ea', E), ('F1a', F1), ('F2a', F2), ('Da', D), ('Ga', G), ('L3a', L3), ('N1a', N1), ('N2a', N2), ('N3a', N3), ('N4a', N4), ('N5a', N5), ('N6a', N6), ('N7a', N7), ('M5a', M5), ('M6a', M6), ('N8a', N8), ('N9a', N9)):
        fork_any(nm_, rec_, (.60, .50, .70), R.choice((-1, 1)), U(R, .28, .40), U(R, .05, .18), .45, big=False)
    for nm_, rec_ in (('L1a', L1), ('L1b', L1), ('L2a', L2), ('L2b', L2)):
        fork_any(nm_, rec_, (U(R, .35, .80),), R.choice((-1, 1)), U(R, .25, .40), U(R, .05, .15), .50, big=False)
    for rec_, n_ in ((A, 3), (B, 2), (T1, 2), (B2, 1), (B3, 1), (D, 1), (G, 1), (C, 1), (R1, 1)):
        add_stubs(R, rec_, n_)

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
        twigs(R, [x for x in RECS if x['kind'] == 'fork'] + [L1, L2, R1, R2, F1, F2, E, D, G, M5, M6, N1, N2, N5, N6, N7, N8, N9, T1, T2])
        litter(R)
    print('PLAN', v, 'phase', PHASE, {k: sum(1 for x in RECS if x['kind'] == k) for k in ('branch', 'fork', 'stub', 'twig', 'litter')},
          'contacts', len(CONTACTS))
    return RECS


for _f in (plan, CAPC, smooth_r, XS):
    ns[_f.__name__] = types.FunctionType(_f.__code__, ns, _f.__name__, _f.__defaults__)

# v013 材質分區：依參考圖，苔集中在主木 A 頂面與拱枝上緣、成片但邊緣破碎；蘑菇在 A 左段頂面成一叢、尺寸放大到參考比例。
#   做法：取 v5 的 finish_body_base、v4 的 make_cards 原始碼，只改門檻與尺寸常數後在同一命名空間重新定義（不改舊檔）。
import re as _re


def _redef(path, fname, reps):
    src = open(path, encoding='utf-8').read()
    i = src.index(f'def {fname}(')
    j = src.index('\ndef ', i + 10)
    k = src.find('\nfor f in (', i + 10)
    if 0 < k < j:
        j = k
    body = src[i:j]
    for x, y in reps:
        assert body.count(x) == 1, (fname, x)
        body = body.replace(x, y)
    exec(compile(body, path + f'::{fname}@v013', 'exec'), ns)


_redef(HERE + '/game_dr09v5.py', 'finish_body_base', [
    ("    patch = sm(nzA + .45 * nzB, -.04, .18) * sm(nz15 + .45, 0, .35)",
     "    patch = sm(nzA + .45 * nzB, -.22, .02) * sm(nz15 + .45, -.10, .25)"),
    ("    moss_top = thick * sm(up, .28, .68) * patch",
     "    moss_top = sm(r0 / V['main'], .22, .55) * sm(up, .12, .50) * patch"),
])
_redef(HERE + '/game_dr09v4.py', 'make_cards', [
    ("spots = [(A, .14, 'top'), (B, .06, 'ground')]", "spots = [(A, .16, 'top'), (A, .24, 'top'), (B, .06, 'ground')]"),
    ("C.upright(base, U(R, .06, .11), U(R, .06, .10),", "C.upright(base, U(R, .09, .15), U(R, .08, .13),"),
])
_mc_orig = ns['make_cards']


def _make_cards_A_first(body0):
    """v3 的蘑菇／貼地小蕈取 RECS[0] 當主木；v013 的 A 不是第一個擺的，暫時把 A 排到最前面（id 不變）。"""
    saved = ns['RECS']
    A = next(x for x in saved if x.get('name') == 'A')
    ns['RECS'] = [A] + [x for x in saved if x is not A]
    try:
        return _mc_orig(body0)
    finally:
        ns['RECS'] = saved


ns['make_cards'] = _make_cards_A_first
ns['LAYOUT'] = LAYOUT


def run(v, phase):
    ns['PHASE'] = phase
    import bpy
    asset = ns['NAMES'][v]
    if phase == 2:
        ns['run'](v)
        rep = ns['contact_report']()
        bpy.context.scene['dr09_v13_contacts'] = json.dumps(rep)
        bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_v013.blend', copy=True)
        print('CONTACT_SUMMARY', rep)
        return
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    ns['plan'](v)
    ns['cleanup']()
    R_ = ns['RECS']
    print('DEAD', [(x['kind'], x.get('name', ''), np.round(x['P'][len(x['P']) // 2], 2).tolist()) for x in R_ if x.get('dead')])
    if os.environ.get('DR9DUMP'):
        json.dump([dict(name=x.get('name', ''), kind=x['kind'], P=np.round(x['P'][::2], 3).tolist(), r=np.round(x['r'][::2], 3).tolist())
                   for x in R_ if not x.get('dead') and x['kind'] in ('branch', 'fork', 'stub')], open(os.environ['DR9DUMP'], 'w'))
    print('PLANCHECK', json.dumps(ns['plan_checks']()))
    print('CONTACT_SUMMARY', ns['contact_report']())
    mb = ns['MB']()
    for rec in R_:
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
    out = os.environ.get('DR9OUT', f'{HERE}/blend/{asset}_v013_greybox.blend')
    bpy.ops.wm.save_as_mainfile(filepath=out, copy=True)
    print('GREYBOX_DONE', out)


if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    try:
        run(a[0] if a else 'L', int(a[1]) if len(a) > 1 else 2)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
