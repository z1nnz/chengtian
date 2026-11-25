# DR09 斷枝堆 v012（L 樣品）：以 v011 為底稿另存（v011 保留）。枝量、粗細層級、右上枝群（W2、Q4、E、P2…）與底層主幹不動，
# 只改左上突出的粗枝 W1 與它下方的中層：
#   1. W1 往堆中央收、局部轉向，縮短孤立外伸的跨度（保留往上挑的輪廓）；根部改到 P3 抬起那段的正下方，
#      讓 P3 壓在 W1 根部上（自動搜尋根部位置：不穿插、P3 與 W1 間隙 2 cm 內、P3 在上）。
#   2. 把現有中型枝 Q3 移到 W1 外伸段的下方、方向錯開，W1 搭在它上面（錯位疊壓），分隔原本的大空白；不搭成三角架。
#   3. 沒有為了加高而拉長任何一根；W1、Q3 的分叉數量照舊重建。材質、落葉、光線不動。
# 用法：
#   blender -b --python art/source/d2-logs-b/game_dr09v12.py -- L 1   （灰模＋只有 W1、Q3 的單獨灰模）
#   blender -b --python art/source/d2-logs-b/game_dr09v12.py -- L 2   （完整：匯出 FBX／GLB、存 blend/…_v012.blend）
import sys, os, math, types, random, traceback, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
H5 = {'__name__': 'dr09_v5_for_v12', '__file__': HERE + '/game_dr09v5.py'}
exec(compile(open(H5['__file__'], encoding='utf-8').read(), H5['__file__'], 'exec'), H5)
ns = H5['ns']
ns['VER'] = 'v012'
ns['VARIANTS']['L'].update(twigs=8, litter=4, seed=9606)


def CAPC(rec):
    """斷面中心（木芯）凸出量；個別斷口可用 rec['capc'] 指定。"""
    return rec.get('capc', .16 if rec.get('heavy') else .50)


def smooth_r(r, n=15):
    """沿長度把節瘤鼓脹抹平一些，讓粗細自然過渡（不改亂數）。"""
    k = np.hanning(n)
    k /= k.sum()
    return np.convolve(np.pad(r, n // 2, mode='edge'), k, 'valid')


def XS(rec, s, th):
    """v011：截面加上局部扭轉（twk：平滑 S 形）與局部扁度變化（ek），其餘同 v004。"""
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
    assert v == 'L', 'v012 先做 L 樣品'
    V = dict(VARIANTS[v], v=v)
    SEG, OWN, RECS, CONTACTS = np.zeros((0, 8)), np.zeros(0, int), [], []
    R = random.Random(V['seed'])
    R2 = random.Random(9707)

    def put(name, ctrl, r0, taper, mode, sink, k=.3, shape=None, lumps=2, ends=('break', 'break'), e=(.06, .12), main=False, twr=None,
            settle=False, RR=None, smooth=False):
        RR = RR or R
        Q, s = spline_path(ctrl)
        r = heavy_radius(RR, s, r0, taper, lumps)
        if smooth:
            r = smooth_r(r)
        t = s / s[-1]
        if mode == 'rigid':
            P = _place_rigid1(Q, s, r, set(), sink, shape(t, s) if shape else None)
            if settle:
                P = settle_ends(P, s, r, sink)
        else:
            P = drape(Q, s, r, set(), sink, k, shape(t, s) if shape else None)
        rec = new_rec(RR, 'branch', P, s, r, ends, main=main)
        rec['xs'] = xs_params(RR, e)
        if twr is not None:
            rec['xs']['twr'] = twr
        rec['heavy'] = r0 > .06
        rec['name'] = name
        rec['ext'] = [1.0, 1.0]
        rec['splint'] = [[], []]
        cap_params(RR, rec)
        add_seg(rec)
        return rec

    # ---- v006 原有木頭（順序、亂數不變；只改 B 的形、F 的擺法）
    C = put('C', [(-1.45, -.95), (-.95, -.35), (-.45, .25), (.05, .85)], .13, .36, 'drape', .22, k=.3, lumps=3, twr=.7)
    C0 = put('C0', [(-1.85, .62), (-1.30, .50), (-.75, .52)], .11, .35, 'drape', .20, k=.3, lumps=2)
    D = put('D', [(.55, .62), (1.20, .48), (1.85, .40)], .10, .38, 'drape', .14, k=.3, lumps=2, twr=.9)
    A = put('A', [(-2.00, -.42), (-1.20, -.32), (-.40, -.10), (.40, .14), (1.15, .26)], .19, .36, 'rigid', .24,
            shape=lambda t, s: .18 * np.exp(-((t - .26) / .15) ** 2) + kink(t, .46, -.16, .03) + kink(t, .62, .14, .03),
            lumps=4, main=True, twr=.65, settle=True)
    # B：較直的一根，只在 t≈0.6 處明顯折一次往下（不是平滑波浪）；粗細抹順
    B = put('B', [(-1.45, .82), (-.60, .52), (.20, .24), (.90, -.03), (1.45, -.28)], .145, .40, 'rigid', .18,
            shape=lambda t, s: kink(t, .60, -.34, .018), lumps=3, twr=-.8, settle=True, smooth=True)
    # F：順著 A 的拱背搭過去，尾端落到後方的 C0／M2 一帶（drape，彎曲上限 k 大一點才會貼著 A 下來）
    F = put('F', [(-.12, -.80), (-.42, -.42), (-.72, -.04), (-.98, .30), (-1.12, .56)], .068, .42, 'drape', .08, k=1.0,
            lumps=1, e=(.04, .09))
    E = put('E', [(.30, -.58), (.78, -.38), (1.24, -.12), (1.58, .10)], .078, .40, 'rigid', .10,
            shape=lambda t, s: kink(t, .58, .14, .04), lumps=2)
    M1 = put('M1', [(.80, -.74), (1.22, -.70), (1.66, -.54)], .052, .45, 'drape', .08, k=.4, lumps=1, e=(.04, .08))
    M2 = put('M2', [(-1.20, .90), (-.65, .86), (-.15, .80)], .046, .45, 'drape', .08, k=.4, lumps=1, e=(.04, .08))
    heavy_splinters(R, A, 0, 3, .30)
    for rec in (B, C, E):
        e_ = R.choice((0, 1))
        if rec['ends'][e_] == 'break':
            heavy_splinters(R, rec, e_, 1, .12)
    for rec, t, side, fl, zr in ((A, .70, -1, .70, .16), (B, .78, 1, .65, .20), (C, .35, -1, .50, .12), (E, .70, 1, .40, .15)):
        f = add_fork(R, rec, t, side, fl, zr, (.48, .58))
        if f is None:
            add_fork(R, rec, t + .06, -side, fl * .85, zr, (.48, .58))
    for rec, n in ((A, 2), (B, 2), (C, 1), (D, 1)):
        add_stubs(R, rec, n)

    # ---- v007 新增（全部用 R2）
    # 中層兩根中型腐木：長度、粗細不同
    N1 = put('N1', [(1.00, .86), (.50, .56), (.00, .30), (-.42, .06)], .088, .40, 'rigid', .12,
             shape=lambda t, s: kink(t, .45, .06, .03), lumps=2, settle=True, RR=R2, e=(.05, .10))
    N2 = put('N2', [(1.30, -.58), (1.02, -.22), (.70, .16), (.38, .50)], .072, .42, 'rigid', .10,
             shape=None, lumps=1, settle=True, RR=R2, e=(.04, .09))
    heavy_splinters(R2, N1, 1, 2, .14)
    heavy_splinters(R2, N2, 0, 1, .10)
    # 前方最醒目的斷口（C 的前端，正對斜視鏡頭）：深淺落差大、一處大缺角、木芯厚、少量沿木紋的厚裂片
    tc = C['tear'][0]
    C['cap'][0] = dict(tilt=.60, notch=tc + math.pi * .85, nw=1.05, tooth=.80, lip=tc - math.pi * .55, lw=.60, lipl=.35)
    C['capc'] = .42
    C['cracks'] = [cr for cr in C['cracks'] if cr[0] != 0] + [(0, tc + .5, C['r0'] * 4.2, .20), (0, tc - 2.2, C['r0'] * 2.8, .16)]
    C['splint'][0] = [dict(th=tc + .35, len=.30, w=.046, out=.03, tk=.62), dict(th=tc - .30, len=.18, w=.038, out=.05, tk=.58),
                      dict(th=tc + 1.10, len=.07, w=.030, out=.02, tk=.50)]
    # 主幹與中型木上的小分岔（不只外緣，比 v006 的分岔細）
    small = 0
    for rec, t, side, fl, zr in ((N1, .62, 1, .34, .10), (N2, .35, -1, .28, .12), (B, .30, -1, .32, .14), (F, .40, 1, .28, .08),
                                 ):
        f = add_fork(R2, rec, t, side, fl, zr, (.30, .40))
        if f is None:
            f = add_fork(R2, rec, t + .08, -side, fl * .85, zr, (.30, .40))
        small += f is not None
    # 卡在木縫裡的斷枝（細、短，兩頭搭在不同的木頭上）
    wedged = 0
    wlog = []
    for (x0, y0, x1, y1, r0) in ((-.98, -.42, -.58, -.02, .022), (.02, -.18, .34, .24, .020), (-.38, .38, .14, .62, .024),
                                 (1.18, .18, 1.56, -.14, .018), (-1.62, .08, -1.30, .46, .021), (.50, .30, .88, .02, .017)):
        Q, s = spline_path([(x0, y0), ((x0 + x1) / 2 + .02, (y0 + y1) / 2 - .015), (x1, y1)])
        r = r0 * (1 - .35 * s / s[-1]) + .002
        # 直的斷枝：取前後兩半各自最高的支點，兩點連成直線搭上去（drape 會把細枝彎成鉤，rigid 會立成竿）
        sup = np.maximum(r * .95, support(Q, r, set()))
        h = len(s) // 2
        i, j = int(sup[:h].argmax()), h + int(sup[h:].argmax())
        z = sup[i] + (sup[j] - sup[i]) * (s - s[i]) / (s[j] - s[i])
        z = np.maximum(z, r * .95)
        P = np.c_[Q, z]
        for _ in range(8):
            c = clearance(P, r, set())
            if c.min() > -.002:
                break
            P[:, 2] += max(0., -c.min()) + .003
        slope = abs(P[-1, 2] - P[0, 2]) / s[-1]
        if (P[:, 2] - r).max() < .08 or slope > .9:
            wlog.append(('skip', x0, y0, round(float(slope), 2)))
            continue                                   # 平躺在地上的不算卡在木縫；太陡的像竿子，不要
        w = new_rec(R2, 'twig', P, s, r, ('break', 'break'))
        add_seg(w, 2)
        wedged += 1
        wlog.append(('ok', x0, y0, round(float(P[:, 2].min()), 2), round(float(P[:, 2].max()), 2)))
    print('WEDGE', wlog)

    # ---- v008 新增（只加不刪，全部用 R3）
    R3 = random.Random(9808)

    REST_EXCL = set()                 # v010：從某根木頭下方穿過時，支撐不算那一根（穿插仍照常檢查）
    def rest_line(Q, s, r, mode, bend=None):
        """直枝擺在已放好的木頭上：z 一律不低於底下的支撐（support）。
        lean：起點落地，取剛好壓在最關鍵支點上的最小斜率（之後的段落自然往上挑）；
        span：在所有不穿入支撐的直線裡取平均高度最低的一條（兩點搭靠或一端落地）。
        之後只做局部抬升避開穿插（不整根平移，避免整根被頂到半空）。"""
        g = r * .95
        sup = np.maximum(g, support(Q, r, REST_EXCL))
        def touches(z):
            on = np.nonzero(z - sup < .008)[0]
            if not len(on):
                return 0
            return 1 + int((np.diff(s[on]) > .25).sum())
        z = None
        if isinstance(mode, tuple) and mode[0] == 'poke':
            # 固定斜率往上挑：壓在最關鍵的支點上；低的那一端若懸空，之後由 settle_ends 折到地面（局部彎折）
            zi = float((sup - mode[1] * (s - s[0])).max())
            z = np.maximum(zi + mode[1] * (s - s[0]), g)
        if mode == 'lean':
            zi = float(sup[0])
            far = s - s[0] > .30
            m = float(((sup[far] - zi) / (s[far] - s[0])).max())
            if 0 < m < .85:
                z = np.maximum(zi + m * (s - s[0]), g)
        if z is None:
            k = int(sup.argmax())
            best = None
            cands = [sup[k] + m * (s - s[k]) for m in np.linspace(-1.2, 1.2, 241)]
            for e in (0, len(s) - 1):
                if abs(s[e] - s[k]) > .2:
                    cands.append(sup[k] + (g[e] - sup[k]) * (s - s[k]) / (s[e] - s[k]))
            for z0 in cands:
                z1 = np.maximum(z0, g)
                if (z1 >= sup - 1e-4).all() and touches(z1) >= 2 and (best is None or z1.mean() < best.mean()):
                    best = z1
            z = best if best is not None else np.maximum(sup.max() + 0 * s, g)
        if bend:
            for (bt, ba) in (bend if isinstance(bend, list) else [bend]):
                z = z + kink(s / s[-1], bt, ba, .11)   # v011：折彎過渡加寬（原 .04 是硬折角）
            z = np.maximum(z, sup)
        if isinstance(mode, tuple) and mode[0] == 'poke':
            on = np.nonzero(z - sup < .01)[0]
            k = int(on[0]) if len(on) else 0
            if k > 2 and z[0] - g[0] > .02:
                u = ((s[k] - s[:k]) / (s[k] - s[0])) ** 1.6
                z[:k] = np.maximum(z[:k] - (z[0] - g[0]) * u, sup[:k])
        P = np.c_[Q, z]
        for _ in range(25):
            c = clearance(P, r, set())
            if c.min() > -.002:
                break
            up = np.maximum(-c + .003, 0)
            kk = 9
            P[:, 2] += np.convolve(np.pad(up, kk // 2, mode='edge'), np.ones(kk) / kk, 'valid') * 1.6
        return P

    R4 = random.Random(9909)          # v009 的形態變化另用一組亂數，v008 的 R3 流程（每一根的位置、分岔）不受影響

    def profile(r_orig, s, r0_old, taper_old, r0n, tp):
        """根粗梢細：保留原本的節瘤／起伏比例，換成更強的收細（梢端約剩 3 成）＋根部外張。"""
        t = s / s[-1]
        base_old = r0_old * (1 - taper_old * t)
        lump = r_orig / base_old
        return r0n * (1 - tp * t ** .85) * (1 + .16 * np.exp(-t / .05)) * lump

    def end_caps(rec, e_list):
        """端點混合：斜斷面＋缺角＋少量沿木紋的厚纖維；有的只有斜斷面，不是每根都尖或平切。"""
        for e in e_list:
            tc = rec['tear'][e]
            rr = float(rec['r'][0 if e == 0 else -1])
            kind_ = R4.choice(('notch', 'fiber', 'slant'))
            rec['cap'][e] = dict(tilt=U(R4, .25, .50), notch=tc + math.pi * U(R4, .6, 1.1), nw=U(R4, .6, 1.0) if kind_ != 'slant' else .2,
                                 tooth=U(R4, .3, .6), lip=tc - math.pi * U(R4, .4, .7), lw=U(R4, .4, .6), lipl=U(R4, .15, .30))
            n = {'notch': 1, 'fiber': 3, 'slant': 0}[kind_]
            rec['splint'][e] = [dict(th=tc + U(R4, -.7, .7), len=rr * U(R4, 1.2, 2.6), w=max(.012, rr * U(R4, .30, .48)),
                                     out=U(R4, 0, .06), tk=U(R4, .50, .65)) for _ in range(n)]

    def lay(name, ctrl, r0, mode, taper=.45, lumps=1, bend=None, ends=('break', 'break'), style=None, attach=None):
        """lean：一端落地、靠在路徑後段最高的支點上往上挑；span：前後兩半各取最高支點，直直搭過去。
        bend=(t, 斜率)：在 t 之後局部折彎（公尺），讓枝不是一根直管。
        style（v009）：dict(r0=根部半徑, tp=收細量, side=各控制點的側向偏移, bends=[(t, 斜率), …])，改成根粗梢細、有側彎和多處折彎。
        attach（v009）：從這根主幹長出（根部埋進主幹、主幹在分枝處鼓起），保留遠離主幹那一段。
        R3 的抽取次數與 v008 完全一樣（半徑、new_rec 都先用原本的參數抽），之後才換成新的形體。"""
        if style and style.get('side'):
            c = np.array(ctrl, float)
            d = c[-1] - c[0]
            nrm = np.array((-d[1], d[0])) / (np.linalg.norm(d) + 1e-9)
            ctrl = [tuple(p + nrm * o) for p, o in zip(c, style['side'])]
        Q, s = spline_path(ctrl)
        r = heavy_radius(R3, s, r0, taper, lumps)
        rn = profile(r, s, r0, taper, style['r0'], style['tp']) if style else r
        P = rest_line(Q, s, rn, mode, style['bends'] if style and style.get('bends') else bend)
        rec = new_rec(R3, 'branch', P, s, r, ends)
        rec['xs'] = xs_params(R3, (.04, .10))
        rec['name'] = name
        rec['ext'] = [1.0, 1.0]
        rec['splint'] = [[], []]
        cap_params(R3, rec)
        if style:
            rec['r'] = rn
            rec['r0'] = float(rn[0])
        if attach is not None:
            par = attach
            Pp, rp = par['P'], par['r']
            d = np.linalg.norm(rec['P'][:, None] - Pp[None], axis=2) - rp[None]
            c, j = np.unravel_index(d.argmin(), d.shape)
            seg = rec['P'][c:] if len(rec['P']) - c >= c else rec['P'][:c + 1][::-1]
            out = seg[0] - Pp[j]
            out /= np.linalg.norm(out) + 1e-9
            root = Pp[j] + out * float(rp[j]) * .35
            Pn = np.vstack([root, seg])
            sn = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Pn, axis=0), axis=1))]
            tn = sn / sn[-1]
            r0n = min(float(rp[j]) * .62, style['r0'] if style else float(rec['r'][0]))
            rec['P'], rec['s'] = Pn, sn
            rec['r'] = r0n * (1 - .62 * tn ** .85) * (1 + .10 * np.exp(-tn / .06))
            rec['r0'] = float(rec['r'][0])
            rec['kind'], rec['parent'] = 'fork', par['id']
            rec['ends'][0] = 'open'
            par['bulge'].append((float(par['s'][j]), .10))
            print('ATTACH', name, 'to', par.get('name'), 'kept_len', round(float(sn[-1]), 2), 'at', np.round(Pp[j], 2))
        rec['heavy'] = rec['r0'] > .06
        if style or attach is not None:
            end_caps(rec, [e for e in (0, 1) if rec['ends'][e] == 'break'])
        add_seg(rec)
        return rec

    # 中後方斜向上挑（高度、長度、傾角錯開）
    P1 = lay('P1', [(-1.80, .86), (-1.26, .64), (-.72, .44), (-.32, .24)], .060, ('poke', .36), bend=(.78, .16),
             style=dict(r0=.082, tp=.66, side=(0, .05, .08, 0), bends=[(.50, .05), (.76, -.18)]))
    P2 = lay('P2', [(1.82, .84), (1.38, .68), (.92, .52), (.52, .40)], .055, 'lean', bend=(.70, -.06))
    P3 = lay('P3', [(-.55, 1.00), (-.05, .84), (.45, .66), (.88, .52)], .050, 'lean', bend=(.60, .10),
             style=dict(r0=.072, tp=.66, side=(0, .07, -.05, .06), bends=[(.45, -.08), (.70, .18)]))
    P4 = lay('P4', [(.12, 1.00), (-.50, .66), (-1.10, .42), (-1.56, .26)], .058, ('poke', .36), bend=(.74, .10),
             style=dict(r0=.078, tp=.68, side=(0, .08, -.06, .07), bends=[(.45, -.06), (.66, .12), (.84, -.16)]))
    # 中層前後疊壓（正面看得到）、後方與右側補量
    Q1 = lay('Q1', [(-.70, -.94), (-.38, -.62), (.02, -.44), (.42, -.32)], .048, 'lean', bend=(.55, -.28),
             style=dict(r0=.070, tp=.65, side=(0, -.05, .06, 0), bends=[(.40, .08), (.58, -.30)]))
    Q2 = lay('Q2', [(1.14, -.56), (.80, -.33), (.44, -.12), (.10, .06)], .045, 'lean', bend=(.70, -.08),
             style=dict(r0=.075, tp=.60), attach=A)
    Q3 = lay('Q3', [(-1.86, .18), (-1.62, .48), (-1.32, .76), (-.98, .96)], .050, 'lean', bend=(.65, -.06))
    Q4 = lay('Q4', [(1.82, .74), (1.55, .46), (1.28, .18), (1.02, -.08)], .044, 'lean', bend=(.66, -.08),
             style=dict(r0=.070, tp=.60), attach=B)
    MED = (P1, P2, P3, P4, Q1, Q2, Q3, Q4)
    # 中型枝的自然分叉（至少 4 根）
    forked = []
    for rec, t, side, fl, zr in ((P1, .62, 1, .48, .16), (P2, .58, -1, .42, .18), (P3, .66, 1, .40, .14), (P4, .60, -1, .45, .16),
                                 (Q1, .50, 1, .34, .10), (Q3, .55, -1, .36, .12)):
        f = add_fork(R3, rec, t, side, fl, zr, (.50, .62))
        if f is None:
            f = add_fork(R3, rec, t - .10, -side, fl * .85, zr, (.50, .62))
        if f is not None:
            forked.append(rec['name'])
    # 細枝成組：從主幹、中型枝長出的小分岔（末端斷口、尖端混著）
    groups = ((P1, (.35, .80, .88)), (P2, (.40, .85)), (P4, (.38, .86)), (P3, (.82,)), (B, (.52, .66)), (N1, (.30, .80)),
              (A, (.82,)), (Q2, (.62,)), (E, (.45,)), (Q4, (.55,)))
    small2 = 0
    for rec, ts in groups:
        for t in ts:
            side = R3.choice((-1, 1))
            f = add_fork(R3, rec, t, side, U(R3, .18, .34), U(R3, .10, .30), (.26, .36))
            if f is None:
                f = add_fork(R3, rec, t + .05, -side, U(R3, .16, .28), U(R3, .10, .25), (.26, .36))
            if f is not None:
                small2 += 1
                if R3.random() < .55:
                    f['ends'] = ('open', 'break')
    # 卡在木縫、搭靠、落地的短斷枝
    sticks = 0
    for ctrl, r0 in (([(-.20, -.30), (-.02, -.10), (.16, .12)], .018), ([(.62, .70), (.86, .58), (1.10, .50)], .016),
                     ([(-1.10, .02), (-.92, .22), (-.74, .44)], .017), ([(1.30, -.42), (1.52, -.30), (1.74, -.22)], .015),
                     ([(-1.55, -.55), (-1.30, -.70), (-1.05, -.78)], .016), ([(.20, -.78), (.45, -.86), (.70, -.88)], .014)):
        Q, s = spline_path(ctrl)
        r = r0 * (1 - .3 * s / s[-1]) + .002
        sup = np.maximum(r * .95, support(Q, r, set()))
        h = len(s) // 2
        i, j = int(sup[:h].argmax()), h + int(sup[h:].argmax())
        z = np.maximum(sup[i] + (sup[j] - sup[i]) * (s - s[i]) / (s[j] - s[i]), r * .95)
        P = np.c_[Q, z]
        for _ in range(8):
            c = clearance(P, r, set())
            if c.min() > -.002:
                break
            P[:, 2] += max(0., -c.min()) + .003
        if abs(P[-1, 2] - P[0, 2]) / s[-1] > .9:
            continue
        w = new_rec(R3, 'twig', P, s, r, ('break', 'break'))
        add_seg(w, 2)
        sticks += 1
    print('V8ADD med', len(MED), 'forked', forked, 'small_forks', small2, 'sticks', sticks)
    # v009：最醒目的幾根再加一根不對稱分叉（一粗一細、角度不同），分叉根部由 add_fork 的鼓起過渡
    asym = []
    for rec, t, side, fl, zr, fr in ((P4, .45, 1, .55, .22, (.55, .65)), (P4, .82, -1, .22, .30, (.30, .38)), (P1, .50, -1, .45, .18, (.50, .60)),
                                     (P3, .55, 1, .40, .20, (.50, .60)), (Q1, .70, -1, .30, .25, (.40, .50))):
        f = add_fork(R4, rec, t, side, fl, zr, fr)
        if f is None:
            f = add_fork(R4, rec, t - .08, -side, fl * .85, zr, fr)
        if f is not None:
            asym.append(rec['name'])
            if R4.random() < .6:
                f['ends'][1] = 'break'
    print('V9ASYM', asym)

    def blanks(tag, n=4):
        """俯視空白：5 cm 格點上到最近木頭表面的平面距離，列出堆內最大的幾個空洞（中心、半徑）。"""
        pts, rr = [], []
        for x in RECS:
            if x['kind'] in ('branch', 'fork', 'stub', 'twig') and not x.get('dead'):
                pts.append(x['P'][::2, :2]); rr.append(x['r'][::2])
        pts, rr = np.vstack(pts), np.concatenate(rr)
        gx, gy = np.meshgrid(np.arange(-1.5, 1.51, .05), np.arange(-.75, .76, .05))
        G = np.c_[gx.ravel(), gy.ravel()]
        d = np.full(len(G), 9.)
        for k in range(0, len(pts), 400):
            dd = np.linalg.norm(G[:, None] - pts[None, k:k + 400], axis=2) - rr[None, k:k + 400]
            d = np.minimum(d, dd.min(1))
        out = []
        for _ in range(n):
            i = int(d.argmax())
            out.append((round(float(G[i, 0]), 2), round(float(G[i, 1]), 2), round(float(d[i]), 2)))
            d[np.linalg.norm(G - G[i], axis=1) < max(d[i], .1) * 1.6] = -1
        print('BLANKS', tag, out)
    blanks('before')
    R5 = random.Random(91010)

    def mid_log(name, ctrl, mode, r0, side, bends, forks):
        rec = lay(name, ctrl, .05, mode, style=dict(r0=r0, tp=.70, side=side, bends=bends))
        rec['xs']['e'] = U(R5, .12, .17)            # 截面明顯不圓
        rec['xs']['h3'] = U(R5, .06, .09)           # 三瓣起伏，腐木的棱
        made = 0
        for t, sd, fl, zr, fr in forks:
            f = add_fork(R5, rec, t, sd, fl, zr, fr)
            if f is None:
                f = add_fork(R5, rec, t + .07, -sd, fl * .85, zr, fr)
            if f is not None:
                made += 1
                f['ends'][1] = 'break'
        top = rec['P'][:, 2] + rec['r']
        print('  NEW', name, 'd_cm', round(rec['r0'] * 200, 1), 'len', round(float(rec['s'][-1]), 2), 'ends',
              round(float(rec['P'][0, 2] - rec['r'][0]), 2), round(float(rec['P'][-1, 2] - rec['r'][-1]), 2), 'top', round(float(top.max()), 2), 'forks', made)
        return rec
    # N3：分叉木，斜跨俯視左中段最大的空白（約 -1.3, 0.1），一根分叉伸向另一側，把空白切成大小不一的兩三塊
    REST_EXCL.update({P4['id']} | {x['id'] for x in RECS if x.get('parent') == P4['id']})
    N3 = mid_log('N3', [(-1.02, .66), (-1.18, .38), (-1.34, .10), (-1.50, -.14)], 'span', .100,
                 (0, .05, -.04, 0), [(.35, -.04), (.62, -.16)], ((.45, -1, .42, .12, (.50, .60)), (.72, 1, .26, .18, (.38, .46))))
    REST_EXCL.clear()
    # N4：中央，從前中斜向後方，壓過 A、B、N1 往上挑，正面在 A 後面露出本體
    N4 = mid_log('N4', [(.24, .86), (.16, .45), (.08, .05), (.02, -.32)], ('poke', .22), .092,
                 (0, -.05, .05, 0), [(.40, .08), (.70, -.12)], ((.62, -1, .38, .16, (.50, .60)),))
    # N5：中後右，從右後地面斜向中央，搭在 D、P2、N2、B 上
    N5 = mid_log('N5', [(1.30, .92), (1.00, .64), (.70, .38), (.40, .12)], ('poke', .26), .096,
                 (0, .06, -.04, .03), [(.50, -.10), (.78, .12)], ((.55, 1, .40, .14, (.50, .60)), (.80, -1, .22, .22, (.36, .44))))
    blanks('after')

    # ================= v011：中上層最醒目的 3 根（P4、N4、N5）連同它們的分叉換成有份量的分叉腐木 W1–W3 =================
    # 先照 v010 原樣擺完（其他木頭的位置、亂數完全不變），再把這三根整組拿掉、重建支撐表，最後擺新的三根。
    kill = {P4['id'], N4['id'], N5['id'], Q3['id']}      # v012：Q3 也拿掉，之後移到 W1 下方重擺
    q3_forks = sum(1 for x in RECS if x['parent'] == Q3['id'])
    while True:
        more = {x['id'] for x in RECS if x['parent'] in kill and x['id'] not in kill}
        if not more:
            break
        kill |= more
    n_kill = dict(branch=sum(1 for x in RECS if x['id'] in kill and x['kind'] == 'branch'),
                  fork=sum(1 for x in RECS if x['id'] in kill and x['kind'] == 'fork'))
    keep = [x for x in RECS if x['id'] not in kill]
    mp = {x['id']: k for k, x in enumerate(keep)}
    for x in keep:
        x['id'] = mp[x['id']]
        x['parent'] = mp[x['parent']] if x['parent'] is not None else None
    RECS[:] = keep
    SEG, OWN = np.zeros((0, 8)), np.zeros(0, int)
    for x in RECS:
        add_seg(x, 2 if x['kind'] in ('twig', 'litter') else 3)
    print('V12KILL', n_kill)
    V['H'] = 1.32                       # 新的粗枝本體要突破上緣，分叉的高度上限跟著放寬
    R6 = random.Random(91111)
    R6_ = R6
    W_IDS = set()

    def gbump(t, spec):
        """平滑起伏：每個 (t, 振幅 m, 寬) 是一個高斯鼓起，曲率在轉折前後漸變（不是折角）。"""
        z = np.zeros_like(t)
        for c, a, w in spec:
            z += a * np.exp(-((t - c) / w) ** 2)
        return z

    def rest_smooth(Q, s, r, mode, bumps=(), top=None, excl=()):
        """平滑擺放：z = a + m·s + c·s² + 平滑起伏，全段不低於支撐、至少兩處接觸。
        lean：起點落地，取最高點最接近 top 的那組；span：兩處以上搭靠、平均高度最低。最後只做寬幅的局部抬升。"""
        g = r * .92
        thin = {x['id'] for x in RECS if x['kind'] in ('twig', 'litter')}   # 粗木不靠細斷枝撐（細枝之後可能被清掉）
        sup = np.maximum(g, support(Q, r, set(excl) | thin))
        t = s / s[-1]
        bz = gbump(t, bumps)
        # 每一根木頭各自撐得到的高度（地面 = -1），用來確認搭靠點分屬不同的木頭
        owners = [o for o in sorted(set(OWN.tolist())) if o not in set(excl) | thin]
        SO = {-1: g}
        for o in owners:
            h = support(Q, r, (set(owners) - {o}) | thin | set(excl))
            if (h > -1).any():
                SO[o] = h
        def touches(z):
            got = {o for o, h in SO.items() if (z - h < .010).any()}
            on = np.nonzero(z - sup < .010)[0]
            runs = 0 if not len(on) else 1 + int((np.diff(s[on]) > .30).sum())    # 搭靠點沿枝要分開（不是同一處）
            return min(len(got), runs)
        best, bkey = None, None
        far = s - s[0] > .30
        for c in np.linspace(-.22, .22, 23):
            if mode == 'lean':     # 起點落地：斜率取剛好壓在最關鍵支點上的那個（解析解，不靠格點）
                q = sup - (sup[0] - bz[0]) - c * s ** 2 - bz
                ms = [float((q[far] / s[far]).max())]
            else:                  # 兩處搭靠、平均高度最低：q 的上凸包上、跨過中點的那一段（線性規劃的解）
                q = sup - c * s ** 2 - bz
                hh = upper_hull(list(s), list(q))
                sm_ = float(s.mean())
                ms = [(y1 - y0) / (x1 - x0) for (x0, y0), (x1, y1) in zip(hh, hh[1:]) if x1 - x0 > .3]
            for m in ms:
                base = m * s + c * s ** 2 + bz
                a = float((sup - base).max())
                z = a + base
                if touches(z) < 2:
                    continue
                if mode == 'lean':
                    if z[0] - sup[0] > .012 or m > 1.1:
                        continue
                    key = abs(float((z + r).max()) - top) + .15 * abs(c)
                else:
                    key = float(z.mean()) + .05 * abs(c)
                if bkey is None or key < bkey:
                    best, bkey = z, key
        if best is None:
            print('  REST_FAIL', mode, 'sup0', round(float(sup[0]), 3), 'supmax', round(float(sup.max()), 3))
            best = np.maximum(sup, g)
        P = np.c_[Q, best]
        print('  REST', mode, 'zmax_rest', round(float(best.max()), 3), 'sup_max', round(float(sup.max()), 3), 'at_s', round(float(s[int(sup.argmax())]), 2))
        for _ in range(30):
            cc = clearance(P, r, set(excl))
            if cc.min() > -.002:
                break
            up = np.maximum(-cc + .003, 0)
            kk = 21
            P[:, 2] += np.convolve(np.pad(up, kk // 2, mode='edge'), np.hanning(kk) / np.hanning(kk).sum(), 'valid') * 2.2
        cc = clearance(P, r, set(excl))
        tch = ((P[:, 2] - r) < .012) | (cc < .012)
        print('  CONTACT_RUNS', int(np.sum(np.diff(np.r_[0, tch.astype(int)]) == 1)), 'c_min_by_quarter', [round(float(q.min()), 3) for q in np.array_split(cc, 4)])
        return P

    def rot_log(name, ctrl, r0, tp, mode, bumps=(), top=None, knots=(), twk=(), ek=(), excl=(), dry=False, lump_seed=None):
        """有份量的腐木主枝：根粗梢細（梢端約剩 3 成）、根部外張、節瘤處略鼓、截面扁且有棱、局部扭轉。"""
        Q, s = spline_path(ctrl)
        t = s / s[-1]
        lump = heavy_radius(random.Random(lump_seed) if lump_seed else R6, s, 1.0, 0, 2)            # 只取節瘤／起伏比例
        r = r0 * (1 - tp * t ** .85) * (1 + .18 * np.exp(-t / .05)) * lump
        for c, a in knots:                                # 彎折處的節瘤（曲率最大的地方略鼓）
            r = r * (1 + a * np.exp(-((t - c) / .06) ** 2))
        r = smooth_r(r, 9)
        P = rest_smooth(Q, s, r, mode, bumps, top, excl)
        if dry:
            return P, s, r
        rec = new_rec(R6, 'branch', P, s, r, ('break', 'break'))
        rec['name'] = name
        rec['xs'] = xs_params(R6, (.11, .16))
        rec['xs']['h3'] = U(R6, .06, .09)
        rec['xs']['twr'] = U(R6, .25, .45) * R6.choice((-1, 1))
        rec['xs']['twk'] = [(c * float(s[-1]), a, .10) for c, a in twk]     # 局部扭轉（平滑的 S 形，不是一刀扭）
        rec['xs']['ek'] = [(c * float(s[-1]), a, .25) for c, a in ek]       # 局部截面變扁／變圓
        rec['ext'] = [1.0, 1.0]
        rec['splint'] = [[], []]
        rec['heavy'] = True
        cap_params(R6, rec)
        end_caps(rec, (0, 1))
        add_seg(rec)
        W_IDS.add(rec['id'])
        top_ = P[:, 2] + r
        print('  W', name, 'd_cm', round(float(r[0]) * 200, 1), 'len', round(float(s[-1]), 2), 'ends',
              round(float(P[0, 2] - r[0]), 2), round(float(P[-1, 2] - r[-1]), 2), 'top', round(float(top_.max()), 2),
              'at', np.round(P[int(top_.argmax())], 2).tolist(), 'r_at_top', round(float(r[int(top_.argmax())]), 3))
        return rec

    def crotch(rec, t, side, fl, up, frac, swing=(.55, .80), wob=.10, name='', tip='break', rng=None, flare=.95):
        """不對稱側枝：從母枝切線方向慢慢轉出去（過渡長約 3 倍母枝半徑），根部外張到接近母枝粗細，母枝分叉處鼓起，
        看起來是同一塊木頭長出來，不是插上去的棍子。"""
        R6 = rng or R6_
        P, s, r = rec['P'], rec['s'], rec['r']
        i = int(len(P) * t)
        T, N0, B0 = frame_at(P, i)
        rp = float(r[i])
        a = math.atan2(T[1], T[0]) + side * U(R6, *swing)
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
        Pf += lat[None] * (np.sin(sf / fl * math.pi * U(R6, .9, 1.4)) * fl * U(R6, -wob, wob) * w)[:, None]
        tf = sf / fl
        rf = rp * frac * (1 - .58 * tf ** .9) + .002
        rf = rf * (1 + (min(flare, frac * 1.55) / frac - 1) * np.exp(-sf / (rp * 1.3)))   # 根部外張：從接近母枝粗細漸收
        Pf = bend_up(Pf, rf, {rec['id']})
        far = sf >= 0                             # 整段都檢查（外張的根部也不能壓進別根；母枝本身不算）
        cmin = float(clearance(Pf[far], rf[far], {rec['id']}).min())
        if cmin < .002 or (Pf[:, 2] + rf).max() > V['H'] * 1.05 or not inside(Pf, .1) or (Pf[:, 2] - rf).min() < -.01:
            print('  CROTCH_FAIL', name, round(cmin, 3), round(float((Pf[:, 2] + rf).max()), 2), inside(Pf, .1))
            return None
        f = new_rec(R6, 'fork', Pf, sf, rf, ('open', tip), parent=rec['id'])
        f['name'] = name
        f['xs'] = xs_params(R6, (.08, .14))
        f['ext'] = [1.0, 1.0]
        f['heavy'] = float(rf[0]) > .05
        if tip == 'break':
            cap_params(R6, f)
            end_caps(f, (1,))
        rec['bulge'].append((float(s[i]) + L0 * .35, .14))      # 分叉處的木頭鼓起（枝領）
        add_seg(f)
        W_IDS.add(f['id'])
        print('  CROTCH', name, 'on', rec.get('name') or rec['id'], 'r_root', round(float(rf[0]), 3), 'r_mid', round(float(rf[len(rf) // 2]), 3),
              'len', fl, 'top', round(float((Pf[:, 2] + rf).max()), 2))
        return f

    # W1：中後層左，最高。後方中央地面 → 斜向左上，搭在 P1／C0／N3 上，粗的本體（直徑 10 cm 以上）伸出上緣
    # ---- v012：Q3 移到 W1 外伸段的下方，兩端搭在 N3 與 B／P1 上（中層），方向和 W1 錯開
    st6 = R6.getstate()                    # Q3 用 rot_log 擺，但不能吃掉 R6（W2、W3 和右上枝群要跟 v011 完全一樣）
    Q3C = eval(os.environ.get('DR9Q3', '[[-.80,.10],[-.68,.35],[-.55,.60],[-.43,.85],[-.30,1.10]]'))
    Q3 = rot_log('Q3', [tuple(c) for c in Q3C], .047, .55, 'span',
                 bumps=((.40, .03, .12), (.70, -.02, .12)), knots=((.42, .05),), twk=((.45, .6),), ek=((.5, .3),), lump_seed=7333)
    R6.setstate(st6)
    W_IDS.discard(Q3['id'])
    # ---- v012：W1 收進中央、縮短外伸；根部放到 P3 抬起那段的下方，讓 P3 壓在根部上。自動搜尋根部與梢端位置
    P3ids = {P3['id']} | {x['id'] for x in RECS if x['parent'] == P3['id']}
    W1K = dict(r0=.100, tp=.52, bumps=((.36, .05, .12), (.62, -.04, .10), (.86, .015, .14)), top=1.08,
               knots=((.38, .07), (.63, .06)), twk=((.38, .9), (.62, -.7)), ek=((.30, .5), (.70, -.4)))

    def w1_ctrl(root, tip):
        a_, b_ = np.array(root), np.array(tip)
        d = b_ - a_
        n = np.array((-d[1], d[0])) / np.linalg.norm(d)
        return [tuple(a_ + d * f + n * o) for f, o in zip((0, .25, .5, .75, 1), (0, .03, -.02, .02, 0))]
    best = None
    thin_ = {x['id'] for x in RECS if x['kind'] in ('twig', 'litter')}
    big_ = [x for x in RECS if x['kind'] in ('branch', 'fork') and x['r0'] > .03]

    def root_lock(P_, r_, s_, part=(0, .7)):
        """某一段（預設根部前 0.7 m）跟哪些木頭貼著（1.5 cm 內），哪些蓋在上面。"""
        near = (s_ >= part[0]) & (s_ < part[1])
        Pn, rn = P_[near], r_[near]
        touch, above = set(), set()
        for o in big_:
            d = np.linalg.norm(Pn[:, None] - o['P'][None, ::2], axis=2) - rn[:, None] - o['r'][None, ::2]
            i, j = np.unravel_index(d.argmin(), d.shape)
            if d[i, j] < .015:
                touch.add(o.get('name') or o['id'])
                if o['P'][::2][j, 2] > Pn[i, 2] + rn[i] * .4:
                    above.add(o.get('name') or o['id'])
        return touch, above
    def q3_cross(P_, r_, s_):
        """W1 跟 Q3 最近的一點：W1 的弧長、落在 Q3 全長的幾成、間隙、Q3 是否在下面。"""
        d = np.linalg.norm(P_[:, None] - Q3['P'][None], axis=2) - r_[:, None] - Q3['r'][None]
        i, j = np.unravel_index(d.argmin(), d.shape)
        return float(s_[i]), j / (len(Q3['P']) - 1), float(d[i, j]), Q3['P'][j, 2] < P_[i, 2]
    best = None
    stat = dict(tried=0, no_pen=0, runs_top=0, low_root=0, rise=0, rootlock=0, locked=0, qmiss=[])
    for ex_name, ex_ in (('P3下穿', P3ids), ('一般', set())):
        for tip in ((-.95, .38), (-.88, .48), (-1.02, .30), (-.80, .30), (-1.00, .48), (-.92, .58), (-.80, .56)):
            for rx in np.arange(.30, 1.01, .05):
                for ry in np.arange(.62, 1.01, .04):
                    ctrl = w1_ctrl((rx, ry), tip)
                    P_, s_, r_ = rot_log('W1', ctrl, W1K['r0'], W1K['tp'], 'lean', W1K['bumps'], W1K['top'], W1K['knots'],
                                         excl=ex_, dry=True, lump_seed=7121)
                    L_ = float(s_[-1])
                    if not 1.35 <= L_ <= 1.95:
                        continue
                    stat['tried'] += 1
                    call = clearance(P_, r_, thin_)
                    if call.min() < -.003:
                        continue
                    stat['no_pen'] += 1
                    tch = ((P_[:, 2] - r_) < .012) | (call < .012)
                    runs = int(np.sum(np.diff(np.r_[0, tch.astype(int)]) == 1))
                    topz = float((P_[:, 2] + r_).max())
                    if runs < 2 or not .98 <= topz <= 1.16:
                        continue
                    stat['runs_top'] += 1
                    zb = P_[:, 2]
                    k6 = int(np.searchsorted(s_, .6))
                    if zb[0] - r_[0] > .20 or zb[0] > zb[1:k6].min() + .01:       # 根部要低、根端不能往上翹成鉤
                        continue
                    stat['low_root'] += 1
                    if (zb[-1] - zb[0]) / L_ < .30 or zb[-1] + r_[-1] < topz - .08:      # 保留往上挑的輪廓（最高點在梢端附近）
                        continue
                    stat['rise'] += 1
                    touch, above = root_lock(P_, r_, s_)
                    if not above and len(touch) < 2:
                        continue
                    stat['rootlock'] += 1
                    qs, qf, qg, qbelow = q3_cross(P_, r_, s_)       # 外伸段橫壓在 Q3 身上（不是頂在 Q3 端頭，像支柱）
                    if len(stat['qmiss']) < 400:
                        stat['qmiss'].append((round(qs, 2), round(qf, 2), round(qg, 3), bool(qbelow)))
                    if qg > .015 or qs < .6 or not .20 <= qf <= .82 or not qbelow:
                        continue
                    stat['locked'] += 1
                    sc = abs(topz - 1.08) + .3 * abs(L_ - 1.65) - (.06 if above else 0) - .02 * min(len(touch), 3) + .1 * abs(qf - .55)
                    if best is None or sc < best[0]:
                        best = (sc, ctrl, topz, L_, ex_, runs, (round(float(rx), 2), round(float(ry), 2)), tip, sorted(map(str, touch)), sorted(map(str, above)), ex_name, (round(qs, 2), round(qf, 2)))
    qm = stat.pop('qmiss'); print('QMISS', sorted(qm, key=lambda q: q[2])[:25])
    print('W1SEARCH', stat, None if best is None else dict(score=round(best[0], 3), mode=best[10], root=best[6], tip=best[7], top=round(best[2], 2),
                                                           len=round(best[3], 2), runs=best[5], root_touch=best[8], root_above=best[9], q3_at=best[11]))
    if os.environ.get('DR9SEARCHONLY'):
        sys.stdout.flush(); os._exit(0)
    heavy_radius(R6, np.linspace(0, 1, 10), 1.0, 0, 2)    # 照 v011 消耗 R6（W1 的節瘤改用固定亂數），W2、W3 才會跟 v011 一樣
    W1 = rot_log('W1', best[1], W1K['r0'], W1K['tp'], 'lean', W1K['bumps'], W1K['top'], W1K['knots'], W1K['twk'], W1K['ek'],
                 excl=best[4], lump_seed=7121)
    # W2：中後層右，第二高。右後地面 → 往右前方斜上（和 W1 的方向差約 90°），搭在 E 翹起的那一端上；梢端是粗的斷口
    W2 = rot_log('W2', [(1.06, .98), (1.20, .70), (1.35, .42), (1.50, .14), (1.63, -.10)], .094, .50, 'lean',
                 bumps=((.32, -.03, .10), (.56, .05, .12), (.80, -.02, .12)), top=1.02,
                 knots=((.34, .06), (.57, .07)), twk=((.34, -.8), (.58, .6)), ek=((.45, .4),))
    # W3：中層，從右前（粗頭、較低）橫到左中段（細頭），在 B 的前面、和 B 幾乎同向，不交成 X；搭在 N2／E 與 A 上
    W3 = rot_log('W3', [(1.02, -.30), (.68, -.17), (.30, -.10), (-.12, -.05), (-.55, .00), (-.95, .06)], .088, .55, 'span',
                 bumps=((.24, .04, .10), (.48, -.03, .10), (.72, .04, .10)),
                 knots=((.25, .06), (.73, .06)), twk=((.25, .7), (.73, -.8)), ek=((.48, .5),))
    made = {}
    def try_crotch(key, par, ts, *a, **k):
        for t_ in ts:
            made[key] = crotch(par, t_, *a, name=key, **k)
            if made[key] is not None:
                return
    R7 = random.Random(91212)
    q3f = []
    for t_, sd, fl, up, fr in ((.58, 1, .34, -.08, .55), (.40, -1, .28, -.06, .5), (.72, -1, .24, -.04, .5)):   # 側伸，不直立
        if len(q3f) >= max(1, q3_forks):
            break
        f_ = crotch(Q3, t_, sd, fl, up, fr, name='Q3f', rng=R7)
        if f_ is not None:
            q3f.append(f_)
            W_IDS.discard(f_['id'])
    print('Q3FORKS', len(q3f), 'of', q3_forks)
    try_crotch('W1a', W1, (.48, .42, .54), -1, .90, .40, .70, swing=(.45, .65), flare=.72)     # 粗側枝：往後上方，長
    try_crotch('W1b', W1, (.74, .68, .80), -1, .38, .22, .42, swing=(.55, .75), flare=.72)      # 細側枝：往後上方斜出（不正對鏡頭）
    try_crotch('W2a', W2, (.46, .40, .54, .34, .60), -1, .72, -.06, .66, swing=(.60, .85))   # 往堆中央側伸，不直立
    try_crotch('W2b', W2, (.72, .66, .78, .60), 1, .30, .02, .40, swing=(.75, 1.0))
    try_crotch('W3a', W3, (.40, .34, .46, .52), 1, .66, .06, .62, swing=(.60, .85))  # 往前，蓋住前中段的空白一部分
    try_crotch('W3b', W3, (.66, .60, .72), -1, .52, .14, .56, swing=(.55, .80))     # 往後
    for k, (t, sd, fl, up, fr) in (('W3a', (.62, -1, .30, .10, .55)), ('W3b', (.62, 1, .26, .12, .55)), ('W1a', (.66, 1, .30, .12, .55))):
        if made.get(k) is not None:
            try_crotch(k + '1', made[k], (t, t - .1, t + .1), sd, fl, up, fr, swing=(.55, .85), wob=.14)
    for k, v_ in list(made.items()):
        if v_ is None:
            print('  MISSING', k)
    # 新粗枝會壓到中段 3 根卡縫的短斷枝（cleanup 會拿掉），在新粗枝與舊木的交接處補回同樣數量，維持枝量
    sticks6 = 0
    for ctrl, r0 in (([(-.42, -.34), (-.24, -.22), (-.06, -.12)], .017), ([(.52, .12), (.72, .04), (.92, -.04)], .016),
                     ([(-1.06, .52), (-.90, .40), (-.72, .30)], .016), ([(1.18, -.02), (1.34, -.14), (1.50, -.24)], .015),
                     ([(-.20, .46), (-.02, .38), (.16, .30)], .015)):
        if sticks6 >= 3:
            break
        Q, s_ = spline_path(ctrl)
        r_ = r0 * (1 - .3 * s_ / s_[-1]) + .002
        thin = {x['id'] for x in RECS if x['kind'] in ('twig', 'litter')}
        sup = np.maximum(r_ * .95, support(Q, r_, thin))
        h = len(s_) // 2
        i, j = int(sup[:h].argmax()), h + int(sup[h:].argmax())
        z = np.maximum(sup[i] + (sup[j] - sup[i]) * (s_ - s_[i]) / (s_[j] - s_[i]), r_ * .95)
        Pw = np.c_[Q, z]
        for _ in range(8):
            c = clearance(Pw, r_, set())
            if c.min() > .001:
                break
            Pw[:, 2] += max(0., -c.min()) + .003
        if abs(Pw[-1, 2] - Pw[0, 2]) / s_[-1] > .9 or Pw[:, 2].max() < .15:
            continue
        w = new_rec(R6, 'twig', Pw, s_, r_, ('break', 'break'))
        add_seg(w, 2)
        sticks6 += 1
        print('  STICK6', np.round(Pw[len(Pw) // 2], 2).tolist())
    print('V12STICKS', sticks6)
    print('V12ADD', {k: v_ is not None for k, v_ in made.items()}, 'W_parts', len(W_IDS))
    blanks('v012')
    foc = {W1['id'], Q3['id']}
    while True:
        more = {x['id'] for x in RECS if x['parent'] in foc and x['id'] not in foc and x['kind'] == 'fork'}
        if not more:
            break
        foc |= more
    globals()['W_IDS_OUT'] = foc          # 近景單獨灰模：W1、Q3 與它們的分叉

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
        twigs(R, [x for x in RECS if x['kind'] == 'fork'] + [E, F, M1, M2])
        litter(R)
    print('PLAN', v, 'phase', PHASE, {k: sum(1 for x in RECS if x['kind'] == k) for k in ('branch', 'fork', 'stub', 'twig', 'litter')},
          'contacts', len(CONTACTS), 'small_forks', small, 'wedged', wedged)
    for x in RECS:
        if x['kind'] == 'branch':
            top = x['P'][:, 2] + x['r']
            print('  MAIN', x['name'], 'd_cm', round(x['r0'] * 200, 1), 'len', round(float(x['s'][-1]), 2),
                  'ends', round(float(x['P'][0, 2] - x['r'][0]), 2), round(float(x['P'][-1, 2] - x['r'][-1]), 2),
                  'top', round(float(top.max()), 3), 'at_x', round(float(x['P'][top.argmax(), 0]), 2))
    return RECS


for _f in (plan, CAPC, smooth_r, XS):
    ns[_f.__name__] = types.FunctionType(_f.__code__, ns, _f.__name__, _f.__defaults__)


def run(v, phase):
    ns['PHASE'] = phase
    import bpy
    asset = ns['NAMES'][v]
    if phase == 2:
        ns['run'](v)
        rep = ns['contact_report']()
        bpy.context.scene['dr09_v12_contacts'] = json.dumps(rep)
        bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_v012.blend', copy=True)
        print('CONTACT_SUMMARY', rep)
        return
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    ns['plan'](v)
    if os.environ.get('DR9DBG'):
        R_ = ns['RECS']
        q = next(x for x in R_ if x.get('name') == os.environ['DR9DBG'])
        ex = ns['_excl'](q)
        keep = q['s'] > float(R_[q['parent']]['r'].max()) * 1.1 if q['ends'][0] == 'open' else np.ones(len(q['P']), bool)
        for o in R_:
            if o['id'] in ex:
                continue
            d = np.linalg.norm(q['P'][keep][:, None] - o['P'][None], axis=2) - q['r'][keep][:, None] - o['r'][None]
            if d.min() < .01:
                print('DBG', q['name'], 'vs', o['kind'], o.get('name', ''), o['id'], round(float(d.min()), 4))
    ns['cleanup']()
    R_ = ns['RECS']
    print('DEAD', [(x['kind'], x.get('name', ''), R_[x['parent']].get('name', x['parent']) if x['parent'] is not None else None,
                    np.round(x['P'][len(x['P']) // 2], 2).tolist()) for x in R_ if x.get('dead')])
    print('PLANCHECK', json.dumps(ns['plan_checks']()))
    print('CONTACT_SUMMARY', ns['contact_report']())
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
    bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_v012_greybox.blend', copy=True)
    # 只有 W1–W3（含側枝）的單獨灰模：同一個座標、同一個物件名稱，方便用同一組固定鏡頭渲染
    W = ns['W_IDS_OUT']
    bpy.data.objects.remove(o, do_unlink=True)
    mb = ns['MB']()
    for rec in ns['RECS']:
        if not rec.get('dead') and rec['id'] in W:
            ns['tube'](mb, rec, 0)
    o = ns['to_object'](mb, f'{asset}_LOD0', ns['layer_mat']())
    ns['_triangulate'](o)
    from mathutils import Matrix, Vector
    o.data.transform(Matrix.Translation(-Vector(bpy.context.scene['dr_pivot'])))
    o.parent = root
    print('TRIO tris', ns['_tri'](o))
    bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_v012_focus_greybox.blend', copy=True)
    print('GREYBOX_DONE')


if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    try:
        run(a[0] if a else 'L', int(a[1]) if len(a) > 1 else 2)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
