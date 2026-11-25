# DR09 斷枝堆 v009（L 樣品）：以 v008 為底稿另存，v008 的枝量與布局全部保留（亂數流程照舊），本輪不減枝，只改新增枝條的形態：
#   1. 最醒目的 4 根（P4 左上挑出、P1、P3、前方 Q1）改成有份量的中型枯枝：根部加粗、末端漸細（不是整根均勻加粗），
#      各自不同的局部彎折（含平面上的側彎），再加一根不對稱的分叉；P4 保留約 1.1 m 的挑出高度，但不再是一條直線。
#   2. Q2、Q4 改成從主幹長出來的側枝（Q2 出自 A、Q4 出自 B），根部埋進主幹、主幹在分枝處鼓起一圈過渡，末端落地撐住。
#   3. 端點混合：斜的斷面、缺角、少量沿木紋的厚纖維；不是每根都尖或平切。
#   苔、落葉、光線不動（落葉卡仍是依枝幹自動撒的）。
# 用法：
#   blender -b --python art/source/d2-logs-b/game_dr09v9.py -- L 1   （灰模）
#   blender -b --python art/source/d2-logs-b/game_dr09v9.py -- L 2   （完整：匯出 FBX／GLB、存 blend/…_v009.blend）
import sys, os, math, types, random, traceback, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
H5 = {'__name__': 'dr09_v5_for_v9', '__file__': HERE + '/game_dr09v5.py'}
exec(compile(open(H5['__file__'], encoding='utf-8').read(), H5['__file__'], 'exec'), H5)
ns = H5['ns']
ns['VER'] = 'v009'
ns['VARIANTS']['L'].update(twigs=8, litter=4, seed=9606)


def CAPC(rec):
    """斷面中心（木芯）凸出量；個別斷口可用 rec['capc'] 指定。"""
    return rec.get('capc', .16 if rec.get('heavy') else .50)


def smooth_r(r, n=15):
    """沿長度把節瘤鼓脹抹平一些，讓粗細自然過渡（不改亂數）。"""
    k = np.hanning(n)
    k /= k.sum()
    return np.convolve(np.pad(r, n // 2, mode='edge'), k, 'valid')


def plan(v):
    global V, SEG, OWN, RECS, CONTACTS
    assert v == 'L', 'v009 先做 L 樣品'
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
    A = put('A', [(-2.00, -.22), (-1.20, -.20), (-.40, -.05), (.40, .14), (1.15, .26)], .19, .36, 'rigid', .24,
            shape=lambda t, s: .26 * np.exp(-((t - .26) / .15) ** 2) + kink(t, .46, -.20, .03) + kink(t, .62, .16, .03),
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

    def rest_line(Q, s, r, mode, bend=None):
        """直枝擺在已放好的木頭上：z 一律不低於底下的支撐（support）。
        lean：起點落地，取剛好壓在最關鍵支點上的最小斜率（之後的段落自然往上挑）；
        span：在所有不穿入支撐的直線裡取平均高度最低的一條（兩點搭靠或一端落地）。
        之後只做局部抬升避開穿插（不整根平移，避免整根被頂到半空）。"""
        g = r * .95
        sup = np.maximum(g, support(Q, r, set()))
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
                z = z + kink(s / s[-1], bt, ba, .04)
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


for _f in (plan, CAPC, smooth_r):
    ns[_f.__name__] = types.FunctionType(_f.__code__, ns, _f.__name__, _f.__defaults__)


def run(v, phase):
    ns['PHASE'] = phase
    import bpy
    asset = ns['NAMES'][v]
    if phase == 2:
        ns['run'](v)
        rep = ns['contact_report']()
        bpy.context.scene['dr09_v9_contacts'] = json.dumps(rep)
        bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_v009.blend', copy=True)
        print('CONTACT_SUMMARY', rep)
        return
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    ns['plan'](v)
    ns['cleanup']()
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
    bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_v009_greybox.blend', copy=True)
    print('GREYBOX_DONE')


if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    try:
        run(a[0] if a else 'L', int(a[1]) if len(a) > 1 else 2)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
