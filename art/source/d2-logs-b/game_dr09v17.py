# DR09 斷枝堆 v017（L 樣品）：以 v016 另存（v016 及以前全部保留）。這輪只修形體與主要材質分區：
#   一、左端斷口：改成沿木紋撕裂的長纖維（50 條鋪滿斷面、順木紋大致平行、撕裂側長對側短、末端鈍而參差），不用厚板狀尖片；A 左端最後一段改水平，斷面朝左不再下垂；
#       裸木換暖米黃（DR09_FreshWood_v017_Albedo，tex_dr09v17.py 產生），裂縫記在頂點上、用 Inner 層保留深色。
#   二、前景主幹 A：維持拱形，隆起段軸心再抬 3–4 cm，並把隆起段的下緣往上收（UND，只收下半圈、不整體縮細），拱下空隙變大。
#   三、右上主要枝 T1／T2：控制點改成連續彎曲、梢端漸細（tp 0.64），各加一根不對稱的外張分叉；梢端改長斜撕裂＋細纖維，不再是平截圓木端。
#   四、苔：A 頂面成厚苔區（薄層幾何 1–3 cm、順著表面起伏、邊緣收薄破碎），拱頂次之；地衣改成側面與頂面可辨識的灰白斑（不在苔上）。
#   五、蘑菇：前景主菌蓋放大，兩張十字卡轉 45°，正面與斜 45° 都看得到菌傘。
#   六、落葉卡：逐片檢查中心下方 2.5 cm 內有沒有木頭或地面，沒有依附的刪掉；細枝 55→32、不長到 0.8 m 以上（不擋主輪廓）。
# DR09 斷枝堆 v016（L 樣品）：以 v015 另存，保留枝量、主要堆疊、斷口去刺束、中後方粗枝上伸（v015 及以前全部保留）。只精修三部位＋苔：
#   一、前側粗木 A：左段到中段明顯隆起（軸心 .24→.40→.13）、粗細不對稱（knots 有正有負）、截面扭轉加大；
#       墊木 C2 移到 x≈-0.9 加粗，A 底下形成左高右低、兩段不等的低矮空隙（不是單一規整拱）。
#   二、中央拱枝 B：控制點曲率不均（陡升→平頂→折下）、粗細起伏、偏心截面加大；新增根部外張的側分枝 Bc（crotch 連續過渡）。
#   三、左端斷口：木芯＋三塊長裂片＋一塊短片，各自繞木紋軸轉不同角度（rot，不再平行疊板）、埋入深度不同（emb），
#       兩道順紋深裂縫切進同一塊木芯（cracks），樹皮邊局部保留。
#   苔：只在 A 頂面與拱枝 B 頂部成主要覆蓋區（依離軸線距離限定），邊緣破碎；斷口 0.6 m 內不長苔；薄層幾何沿用 v005 finish_body。
# DR09 斷枝堆 v015（L 樣品）：以 v014 為基礎另存，保留拱枝連續彎曲與蘑菇；不做全面重排，只修三項（v014 及以前全部保留）：
#   一、A 左端斷口：移除刺束狀細長裂片；改為斜向撕裂面（cap tilt）＋寬厚殘留木芯＋五塊長短寬窄厚薄不同的寬裂片（splinter slab 模式：
#       基部從斷面內部接入木芯、前段保持寬厚、只有末段收尖），只在撕裂那一側，上緣保留樹皮邊與對側缺角。
#   二、前側主幹 A：abs 設計軸心——左端低、在蘑菇處局部隆起、往右下沉，截面扭轉（twr／twk）與局部扁鼓（ek），底部留不規則空隙。
#   三、中後層主斜枝：T1（粗 20 cm）從中央後方 B2 上斜伸到右上主峰（約 x 1.0）、T2 往右上到第二峰（約 x 1.6）；B2／B3 放低讓 T1 通過。
#   總高 ≤ 1.1 m：V['H'] = 1.00（分叉 ≤ 1.05、細枝 ≤ 1.08），實測見 previews/v015/*_measure.json。
# DR09 斷枝堆 v014（L 樣品）：以 v013 為基礎另存，保留 v013 的整體交疊結構（v013 及以前全部保留）。
# v014 修正：一、高度限制在 1.1 m 內（LOD0 木質網格實測，見 previews/v014/*_measure.json）；
#   二、中央拱下洞口（B 改成兩腳落地的全拱）與前側低洞（A 左段架在 C2／C 上，後方 G／L2／L3／N8 右移讓出視線）；
#   三、A 左端斷口改為順木紋、長短錯落、往外散開的不規則薄片木刺＋較厚木芯（splinter 重寫為 6 點截面、多段、扭轉、鋸齒收尖）；
#   四、中層枝加彎度與局部分叉（B3／R1／R2／M6／N2 bow、R2b／M6b／R1c）；五、蘑菇改為每叢 2–3 張卡、主菌蓋放大。
#   每根枝依名稱各自重設亂數，改一根不會牽動其他根。
# 以下為 v013 原說明：
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
#   blender -b --python art/source/d2-logs-b/game_dr09v17.py -- L 1   （灰模：blend/…_v017_greybox.blend）
#   blender -b --python art/source/d2-logs-b/game_dr09v17.py -- L 2   （完整：匯出 FBX／GLB、存 blend/…_v017.blend）
import sys, os, math, types, random, traceback, json, zlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
H5 = {'__name__': 'dr09_v5_for_v17', '__file__': HERE + '/game_dr09v5.py'}
exec(compile(open(H5['__file__'], encoding='utf-8').read(), H5['__file__'], 'exec'), H5)
ns = H5['ns']
ns['VER'] = 'v017'
ns['VARIANTS']['L'].update(twigs=32, litter=10, seed=91313)
LAYOUT = json.loads(os.environ.get('DR9LAYOUT', '{}'))       # 迭代用：覆寫個別構件的參數（不改程式）
# v014：中層最像直棍的幾根（B3、R1、R2、M6、N2）給明確、各不相同的弓彎與 S 彎（不套同一種圓弧），環境變數可再覆寫
for _k, _bw in (('B3', (.09, .0)), ('R1', (.12, -.05)), ('R2', (-.11, .04)), ('M6', (-.12, .06)), ('N2', (.10, -.04))):
    LAYOUT.setdefault(_k, {}).setdefault('bow', _bw)


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
    assert v == 'L', 'v017 先做 L 樣品'
    V = dict(VARIANTS[v], v=v)
    V['H'] = 1.00          # v015：分叉頂端上限 H×1.05、細枝 H×1.08（總高 1.1 m 內）
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
        R.seed(V['seed'] * 7919 + zlib.crc32(name.encode()))
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
        R.seed(V['seed'] * 7919 + zlib.crc32(key.encode()))
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
    C = log('C', [(-.70, .36, 0), (-.64, .00, 0), (-.58, -.40, 0), (-.51, -.78, 0)], .040, .35, sink=.30, lumps=2, e=(.06, .12))
    C2 = log('C2', [(-1.02, -.06, 0), (-.96, -.34, 0), (-.90, -.62, 0), (-.84, -.88, 0)], .070, .30, sink=.26, lumps=2, e=(.10, .16))   # v016：A 中段下的粗墊木（A 底下分成兩段不等的低空隙）
    G = log('G', [(-.85, .64, 0), (-.42, .74, .03), (0.0, .80, 0)], .090, .35, sink=.18, lumps=2)
    D = log('D', [(.20, .82, 0), (.80, .74, .03), (1.40, .64, 0), (1.85, .52, 0)], .085, .40, sink=.16, lumps=2)
    E = log('E', [(.55, -.80, 0), (1.10, -.68, .02), (1.75, -.50, 0)], .065, .45, sink=.12)
    L1 = log('L1', [(-.45, .40, 0), (-.20, .50, .04), (.05, .56, .02)], .045, .55, e=(.05, .10))
    L2 = log('L2', [(-1.30, .94, 0), (-.80, .99, .03), (-.25, .99, .04), (.25, .93, 0)], .042, .55, e=(.05, .10))
    F1 = log('F1', [(-1.00, -.93, 0), (-.55, -.85, .03), (-.15, -.82, .02), (.12, -.88, 0)], .048, .55, e=(.05, .10))
    F2 = log('F2', [(.75, -.99, 0), (1.20, -.93, .02), (1.70, -.86, 0)], .040, .55, e=(.05, .10))
    # ------------------------------------------------------------------ 前側主木 A（最粗，左端大斷口朝左前；左段搭在 C 上離地，下面一道縫）
    A = log('A', [(-1.80, -.53, .21), (-1.64, -.49, .23), (-1.46, -.44, .34), (-1.28, -.40, .44), (-1.10, -.36, .45), (-.86, -.30, .37), (-.55, -.23, .24), (-.20, -.15, .18), (.25, -.03, .13), (.85, .12, .09)],
            .165, .42, sink=.20, knots=((.12, .10), (.24, .12), (.36, -.07), (.50, .07), (.66, -.05)), lumps=3, e=(.12, .18), main=True, mode='abs')   # v016：左段到中段隆起、粗細不對稱
    A['xs']['twr'] = .95                                                   # 截面扭轉加大
    A['xs']['twk'] = [(.55, 1.1, .10), (1.20, -.9, .12), (1.85, .6, .14)]
    A['xs']['ek'] = [(.45, .55, .22), (1.05, -.30, .22), (1.60, .40, .25)]  # 扁、鼓交替，底緣不規則
    A['und'] = [(.68, .26, .36), (1.06, .16, .16)]                      # v017：隆起段下緣往上收（s 中心、寬、收的比例），上緣不動
    # v014：A 左端斷口重做（參考近景 a）：撕裂面朝左前上方；長短錯落的順紋裂片集中在撕裂那一側（約 120°，不是整圈）、
    #   一截厚木芯從斷面中央伸出、斷口往枝身延伸一長條剝皮裸木（約 0.5 m），形成一片連續的淺色木區。
    tcA = 2.05
    A['tear'][0] = tcA
    A['peel'][0] = 1.7
    # 斷面：斜向撕裂面（撕裂那側長、對側短），缺角在對側，殘留樹皮唇在側邊凸出；不加高齒（tooth 很小，避免一圈尖刺）
    A['cap'][0] = dict(tilt=.14, notch=tcA + math.pi * .95, nw=.55, tooth=.10, lip=tcA - 1.9, lw=.55, lipl=.20)   # v017：斷面縮短，主要由纖維條構成
    thS = tcA + .35                      # v016：裂片改在撕裂長邊那側（從斜撕裂面上沿伸出，看得到基部接木芯）
    # v017：斷口改沿木紋撕裂的長纖維（掃帚狀）：50 條寬 6–11 cm、厚約寬一半的纖維條，基部散佈在整個斷面（離軸 0–0.78 倍半徑）、
    #   順木紋大致平行（同一個抬升角 ±0.08，外張很小）；撕裂那側長（0.22–0.48 m）、對側短（0.05–0.14 m），長短參差蓋掉平整切面。
    #   末段才收尖（keep 0.5–0.75），不是細針、也不是厚板。固定亂數，不動共用亂數。
    _rs = random.Random(91717)
    _sp = []
    for _k in range(50):
        _th = thS + U(_rs, -math.pi, math.pi)
        _c = math.cos(_th - thS)
        _long = .5 + .5 * _c
        _sp.append(dict(th=_th, len=(.05 + .08 * _rs.random()) + (.12 + .22 * _rs.random() ** .8) * _long ** 1.6, w=U(_rs, .060, .110),
                        out=U(_rs, .00, .06), tk=.6, thk=U(_rs, .40, .60), rad=.80 * XS(A, 0.0, _th) * _rs.random() ** .5, slab=True, keep=U(_rs, .45, .70), tipw=U(_rs, .35, .55),
                        emb=U(_rs, .02, .06), rot=U(_rs, -.4, .4), lift=.34 + U(_rs, -.08, .08)))
    A['splint'][0] = _sp
    A['cracks'] = [(0, thS + .22, .70, .09), (0, thS - .35, .50, .08), (0, thS + .80, .36, .07), (0, thS - 1.2, .30, .07)]   # 順紋深裂縫切進同一塊木芯
    # 中下層補量（參考圖正面下半部是實的、俯視也很密）
    N1 = log('N1', [(.20, -.55, .10), (.55, -.40, .14), (.90, -.25, .15), (1.25, -.14, .10), (1.60, -.05, .04)], .045, .55)
    N2 = log('N2', [(.45, .35, .10), (.75, .28, .14), (1.05, .20, .15), (1.40, .12, .10), (1.75, .05, .04)], .042, .55)
    N3 = log('N3', [(-.20, .26, .04), (.10, .36, .10), (.40, .44, .12), (.70, .52, .08), (.98, .60, .03)], .048, .55)
    N4 = log('N4', [(-.10, .82, .06), (.15, .64, .18), (.40, .47, .26)], .045, .55)
    N5 = log('N5', [(1.30, .40, .25), (1.50, .25, .20), (1.70, .07, .12), (1.92, -.15, .02)], .040, .60)
    N6 = log('N6', [(.15, -.98, .02), (.45, -.92, .08), (.75, -.86, .04)], .040, .55)
    N7 = log('N7', [(-.60, .72, .08), (-.30, .68, .14), (.00, .63, .18), (.30, .57, .14), (.60, .50, .06)], .045, .55)
    L3 = log('L3', [(-.85, .30, .05), (-.65, .42, .10), (-.45, .54, .08)], .052, .55, e=(.05, .11))
    X2 = log('X2', [(-.30, .95, .03), (-.18, .66, .08), (-.04, .40, .12), (.10, .20, .08)], .055, .55)
    # ------------------------------------------------------------------ 拱形枝（本身彎，跨過 A 上方，拱下透空）
    B2 = log('B2', [(-.25, .10, .26), (.05, .20, .36), (.35, .30, .34), (.60, .42, .22), (.88, .52, .06)],
             .080, .50, knots=((.45, .05),), e=(.10, .15), mode='shift')
    B3 = log('B3', [(-.06, .92, .06), (.14, .64, .26), (.40, .40, .38), (.72, .14, .38), (1.02, -.04, .27), (1.28, -.18, .12), (1.45, -.28, .05)],   # v017：拱頂降 8 cm 讓 T1 通過
             .090, .52, knots=((.30, .06), (.55, .05)), e=(.10, .16), mode='shift')
    B = log('B', [(-1.66, .13, .11), (-1.52, .10, .22), (-1.38, .06, .44), (-1.18, .02, .62), (-.92, -.02, .70), (-.64, -.05, .75), (-.38, -.04, .74), (-.14, -.10, .64),
                  (.10, -.22, .52), (.30, -.36, .36), (.50, -.50, .18), (.66, -.60, .08)], .100, .50,
            knots=((.18, .12), (.34, -.08), (.48, .07), (.70, -.06), (.80, .06)), lumps=3, e=(.16, .22), splint=(), mode='abs')   # v016：陡升→平頂→折下、粗細起伏
    B['xs']['twr'] = -.80
    B['xs']['twk'] = [(.9, -1.0, .12), (2.0, .8, .12)]
    B['xs']['ek'] = [(.7, .45, .25), (1.6, -.25, .22), (2.3, .40, .25)]    # 偏心截面（扁、鼓交替）
    # ------------------------------------------------------------------ 右側往下落地、斜跨
    R1 = log('R1', [(1.06, .06, .57), (1.32, .01, .45), (1.60, -.04, .27), (1.92, -.08, .03)], .072, .60, knots=((.45, .06),), mode='abs')
    R2 = log('R2', [(1.00, .62, .32), (1.30, .55, .24), (1.60, .45, .12), (1.86, .32, .02)], .066, .60, knots=((.40, .06),))
    M5 = log('M5', [(.75, -.40, .36), (1.05, -.47, .30), (1.35, -.55, .18), (1.65, -.62, .05)], .060, .55, mode='shift')
    M6 = log('M6', [(.30, .95, .05), (.70, .80, .30), (1.10, .70, .40), (1.50, .62, .30), (1.85, .55, .08)], .068, .55, knots=((.50, .06),))
    # ------------------------------------------------------------------ 斜挑枝（最高點），梢端撕裂斷口
    T1 = log('T1', [(-.20, .30, .36), (.04, .33, .53), (.28, .37, .70), (.50, .35, .81), (.70, .29, .89), (.88, .24, .95), (1.04, .25, .98)], .104, .64,
             knots=((.22, .06), (.46, -.05), (.68, .05)), e=(.10, .15), mode='abs')        # v017：先陡後緩的連續彎、側向 S 彎、漸細
    T2 = log('T2', [(.50, -.30, .30), (.80, -.26, .43), (1.08, -.17, .53), (1.32, -.13, .58), (1.54, -.14, .60), (1.72, -.10, .57)], .078, .64, knots=((.30, .05), (.62, -.04)), mode='abs')   # v017：拱起再略垂、漸細
    for _rec, _n in ((T1, 5), (T2, 4)):                                   # v017：梢端改長斜撕裂＋細纖維（去平截圓木端）
        _tc = _rec['tear'][1]
        _rec['cap'][1] = dict(tilt=.85, notch=_tc + math.pi, nw=.85, tooth=.45, lip=_tc - 1.8, lw=.40, lipl=.22)
        _rr = float(_rec['r'][-1])
        _rs2 = random.Random(7700 + _n)
        _rec['splint'][1] = [dict(th=_tc + U(_rs2, -.6, .6), len=_rr * U(_rs2, 2.0, 4.2), w=_rr * U(_rs2, .35, .60), out=U(_rs2, .0, .10), tk=.6,
                                  thk=.5, rad=U(_rs2, .2, .6), slab=True, keep=U(_rs2, .2, .4), emb=_rr * .6, rot=U(_rs2, -.8, .8)) for _ in range(_n)]
        _rec['cracks'] = [(1, _tc + .3, _rr * 6, .12)]
    # 俯視 X 形交叉：左後→右前、右後→左前兩根中型彎枝，跨在中層上（補俯視空白、中層體積）
    N8 = log('N8', [(-.98, .98, .02), (-.80, .82, .06), (-.62, .66, .10)], .055, .55, mode='rest')
    N9 = log('N9', [(1.62, .92, .05), (1.38, .80, .15), (1.15, .62, .22), (.95, .50, .20)], .052, .55, mode='rest')
    # ------------------------------------------------------------------ 分叉（大的用連續外張的 crotch，小的用 add_fork）
    fork_any('Aa', A, (.58, .52, .64), 1, .70, .22, .45, swing=(.50, .75))
    fork_any('Ba', B, (.70, .64, .76), -1, .45, -.08, .50)
    fork_any('Bb', B, (.30, .36), 1, .35, .15, .42, big=False)
    fork_any('Bc', B, (.42, .38, .48), 1, .42, .02, .52, swing=(.55, .80), flare=.80)   # v016：拱頂往後的自然側分枝，根部外張連續過渡
    fork_any('B2a', B2, (.55, .48, .62), 1, .50, -.04, .50)
    fork_any('B3a', B3, (.45, .40, .52), -1, .45, -.02, .50)
    fork_any('T1a', T1, (.55, .50, .60), -1, .40, -.06, .48, swing=(.50, .70))   # v014：往上翹得少一點（總高 1.1 m 內）
    fork_any('T1c', T1, (.78, .74, .82, .70), 1, .32, .10, .58, swing=(.35, .55), flare=.82)   # v017：梢端前的不對稱分叉（短、粗、外張）
    fork_any('T2b', T2, (.58, .52, .64), -1, .36, .08, .55, swing=(.45, .70), flare=.80)     # v017
    fork_any('T1b', T1, (.35, .30), 1, .30, .10, .40, big=False)
    fork_any('T2a', T2, (.50, .45, .58), 1, .30, .15, .45, big=False)
    fork_any('R1a', R1, (.45, .40, .52), -1, .40, -.06, .50)
    fork_any('R1b', R1, (.75, .70), 1, .28, .05, .40, big=False)
    fork_any('R2a', R2, (.60, .55), 1, .30, .05, .45, big=False)
    fork_any('R2b', R2, (.35, .30, .42), -1, .40, .12, .50)                  # v014：中層補外張分叉
    fork_any('M6b', M6, (.42, .36, .50), 1, .42, .10, .50)
    fork_any('R1c', R1, (.30, .25, .36), 1, .36, .10, .48)
    for nm_, rec_ in (('X2a', X2), ('Ea', E), ('F1a', F1), ('F2a', F2), ('Da', D), ('Ga', G), ('L3a', L3), ('N1a', N1), ('N2a', N2), ('N3a', N3), ('N4a', N4), ('N6a', N6), ('N7a', N7), ('M5a', M5), ('M6a', M6), ('N8a', N8)):   # v017：N5a、N9a（右上碎枝）不長
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
        twigs(R, [x for x in RECS if x['kind'] == 'fork' and x.get('name') not in ('T1c', 'T2b', 'Bc', 'T1a')] + [L1, L2, R2, F1, F2, E, D, G, M5, N1, N2, N6, N7, N8])   # v017：右上主枝不長細枝（輪廓乾淨）
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
    exec(compile(body, path + f'::{fname}@v017', 'exec'), ns)


_redef(HERE + '/game_dr09v5.py', 'finish_body_base', [
    ("    patch = sm(nzA + .45 * nzB, -.04, .18) * sm(nz15 + .45, 0, .35)",
     "    ZM = MOSSZONE(co)\n    patch = sm(nzA + .45 * nzB + .40 * ZM, -.22, .02) * sm(nz15 + .45 + .25 * ZM, -.10, .25)"),   # v017：A 頂面核心連成一片，邊緣仍破碎
    ("    moss_top = thick * sm(up, .28, .68) * patch",
     "    moss_top = ZM * sm(up, -.05, .38) * patch"),          # v016：苔只在 A 頂面、拱枝 B 頂部成主要覆蓋區
    ("    moss = np.clip(np.maximum(moss_top, .80 * moss_wet), 0, 1) * bark",
     "    moss = np.clip(np.maximum(moss_top, .30 * moss_wet), 0, 1) * bark"),   # 其他枝只留零星濕苔，不整根鋪綠
    ("    lich = .55 * sm(r0, .020, .045) * sm(up, -.55, -.05) * sm(nz7 + .45 * nz15, .22, .36) * bark * (1 - sm(moss, .2, .6))",
     "    lich = sm(r0, .024, .055) * sm(up, -.50, .05) * sm(nz7 + .55 * nz15, .16, .27) * bark * (1 - sm(moss, .08, .35)) * sm(co[:, 2], .04, .10)"),   # v017：側面、頂面的灰白斑（不在苔上、不貼地）
    ("    W[:, 1] = lich * .90\n", "    W[:, 1] = lich\n"),
    ("    W[:, 2] = fib\n", "    W[:, 2] = fib\n    _ck = np.array([getattr(mb, 'crk', {}).get(i, 0.0) for i in range(n)])\n    W[:, 3] = sm(_ck, .12, .55) * .95   # v017：裂縫用 Inner（深褐）層\n"),
])


def MOSSZONE(co):
    """v016：苔的主要覆蓋區＝ A（斷口 0.6 m 之後、中段偏左最濃）與拱枝 B（軸心離地 0.5 m 以上的拱頂）表面附近。"""
    out = np.zeros(len(co))
    for nm, wt, s0, zmin in (('A', 1.0, .60, -1.0), ('B', .70, 0.0, .50), ('B3', .30, 0.0, .38)):   # v017：A 頂面最明顯，拱頂次之
        rec = next((x for x in RECS if x.get('name') == nm and not x.get('dead')), None)
        if rec is None:
            continue
        P, r, s_ = rec['P'], rec['r'], rec['s']
        k = (s_ > s0) & (P[:, 2] > zmin)
        if nm == 'A':
            fall = np.clip(1.25 - .45 * (s_ - s0), .35, 1.0)      # 左中段最濃、往右漸淡
        else:
            fall = np.ones(len(s_))
        P, r, fall = P[k][::2], r[k][::2], fall[k][::2]
        if not len(P):
            continue
        for i0 in range(0, len(co), 20000):
            c = co[i0:i0 + 20000]
            d = np.linalg.norm(c[:, None, :] - P[None], axis=2) - r[None]
            j = d.argmin(1)
            dm = d[np.arange(len(c)), j]
            out[i0:i0 + 20000] = np.maximum(out[i0:i0 + 20000], wt * fall[j] * sm(.10 - dm, 0, .06))   # 截面扁鼓、節瘤讓表面離軸線 ±3–5 cm，範圍放寬
    return out


ns['MOSSZONE'] = types.FunctionType(MOSSZONE.__code__, ns, 'MOSSZONE')
_SPL_SRC = """
def splinter(mb, c, Te, Ne, Be, rr, sp, lv):
    # v014：撕裂木刺改成順木紋的不規則薄片（6 點截面、多段、微彎、扭轉、鋸齒收尖、尖端偏一側），不再是方正木板
    th = sp['th']
    h = lambda k: math.sin(th * 12.9898 + sp['len'] * 78.233 + k * 37.719) * .5 + .5      # 固定雜訊，不動共用亂數
    rd0 = Ne * math.cos(th) + Be * math.sin(th)
    wv0 = np.cross(Te, rd0)
    wv0 /= np.linalg.norm(wv0) + 1e-12
    if sp.get('lift'):                     # v016：A 左端切線朝下，寬裂片改朝水平／略上方伸出（各片不同）
        Te = Te + np.array((0, 0, sp['lift']))
        Te = Te / np.linalg.norm(Te)
    _ro = sp.get('rot', 0.0)
    if _ro:
        rd0, wv0 = rd0 * math.cos(_ro) + wv0 * math.sin(_ro), wv0 * math.cos(_ro) - rd0 * math.sin(_ro)
        rp_ = Ne * math.cos(th) + Be * math.sin(th)
    else:
        rp_ = rd0
    ln, w = sp['len'], sp['w']
    tk = max(.004, w * sp.get('thk', .22))
    base = c - Te * ln * .25 + rd0 * rr * sp.get('rad', .82)
    slab = sp.get('slab', False)
    segs = (7 if lv == 0 else 3)
    tw = (h(1) - .5) * (.35 if slab else 1.1)          # 沿長度扭轉（寬片幾乎不扭）
    sway = (h(2) - .5) * (.04 if slab else .10) * ln   # 側向彎
    prof = ([(-1, -.35), (-.70, -1), (.45, -.85), (1, -.05), (.80, .90), (-.55, 1)] if slab else
            [(-1, 0), (-.55, -.9), (.35, -1), (1, -.25), (.70, .85), (-.30, .70)])     # 寬片：塊狀不規則截面；細片：不對稱薄片
    if slab:
        base = c - Te * sp.get('emb', .08) + rp_ * rr * sp.get('rad', .5)   # 基部從斷面內部長出，連續接入木芯
    rings, cen = [], []
    for k in range(segs + 1):
        t = k / segs
        a = tw * t
        rd = rd0 * math.cos(a) + wv0 * math.sin(a)
        wv = wv0 * math.cos(a) - rd0 * math.sin(a)
        p = base + Te * ln * t + rp_ * (rr * sp['out'] * t * t) + wv0 * sway * math.sin(t * math.pi * .9)
        jag = 1 + .22 * math.sin(t * 9.0 + th * 5.0) * t
        if slab:                                   # 前段保持寬厚，只有末段 35% 逐漸變尖（尖端偏一側、斜收）
            f_ = 1 - sp.get('tipw', .80) * float(np.clip((t - sp.get('keep', .62)) / (1 - sp.get('keep', .62)), 0, 1)) ** 1.3   # v017：tipw 小 = 末端鈍、參差
            ww = w * .5 * (1 - .12 * t) * f_ * (1 + .12 * math.sin(t * 6.0 + th * 3.0))
            tt = tk * .5 * (1 - .25 * t) * (.45 + .55 * f_)
        else:
            ww = w * (1 - .78 * t ** 1.25) * .5 * jag
            tt = tk * (1 - .60 * t) * .5
        cen.append(p)
        rings.append([mb.v(p + wv * u * ww * (1 + .18 * (h(10 + k * 6 + j) - .5)) + rd * v_ * tt, fib=1.0, kind=2) for j, (u, v_) in enumerate(prof)])
    tipv = mb.v(cen[-1] + Te * ln * ((.03 + .04 * h(3)) if slab else (.10 + .10 * h(3))) + wv0 * w * .18 * (h(4) - .5) + rd0 * rr * sp['out'] * .2, fib=1.0, kind=2)
    n = len(prof)
    for k in range(segs):
        a, b = rings[k], rings[k + 1]
        for j in range(n):
            j1 = (j + 1) % n
            mb.f((a[j], a[j1], b[j1], b[j]), [(ln * k / segs, j * w / n), (ln * k / segs, (j + 1) * w / n), (ln * (k + 1) / segs, (j + 1) * w / n), (ln * (k + 1) / segs, j * w / n)])
    a = rings[-1]
    for j in range(n):
        j1 = (j + 1) % n
        mb.f((a[j], a[j1], tipv), [(ln, j * w / n), (ln, (j + 1) * w / n), (ln * 1.15, (j + .5) * w / n)])
"""
exec(compile(_SPL_SRC, HERE + '/game_dr09v17.py::splinter', 'exec'), ns)
_redef(HERE + '/game_dr09v4.py', 'make_cards', [
    ("spots = [(A, .14, 'top'), (B, .06, 'ground')]", "spots = [(A, .16, 'top'), (A, .24, 'top'), (B, .06, 'ground')]"),
    ("        for _ in range(R.randint(3, 4)):", "        for _ in range(R.randint(2, 3)):"),
    ("C.upright(base, U(R, .06, .11), U(R, .06, .10), R.choice(mush), U(R, 0, math.pi), tag)", "C.upright(base, *((U(R, .31, .34), U(R, .30, .33)) if _ == 0 else (U(R, .17, .21), U(R, .16, .19))), (mush[0] if _ == 0 else R.choice(mush[:2])), math.pi / 4 + U(R, -.15, .15), tag)"),   # v017：主菌蓋放大；十字卡轉 45°
    ("            q = p + np.array((U(R, -.10, .10), U(R, -.10, .10), 0))", "            q = p + np.array((U(R, -.10, .10), U(R, -.10, .10), 0)) * (.45 if _ == 0 else 1.0)"),   # v014：每叢一朵大的主菌蓋、其餘小而高低錯落
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


# ================================================================== v017 追加
def UND(rec, s, d):
    """v017：下緣上收——只收朝下的半圈（d.z < 0），上緣不動；rec['und'] = [(s 中心, 寬, 比例)]。"""
    u = rec.get('und')
    if not u or d[2] >= 0:
        return 1.0
    a = sum(k * math.exp(-((s - c) / w) ** 2) for c, w, k in u)
    return 1 - min(a, .6) * (-d[2]) ** 1.3


ns['UND'] = types.FunctionType(UND.__code__, ns, 'UND')
# tube 重新編譯（同 v005 的補丁鏈），加兩處：裂縫權重記在 mb.crk（頂點編號 → 權重）、下緣上收 UND
_H4 = H5['H4']
_H3 = _H4['H3']
_tsrc = H5['_v5_patch'](_H4['_v4_patch'](_H3['_v3_patch'](_H3['G']['_src'])))
_i = _tsrc.index('def tube(')
_tb = _tsrc[_i:_tsrc.index('\ndef ', _i + 10)]
for _a, _b in (("                _ck = CRACK(rec, sr[i], Ls, th)\n",
                "                _ck = CRACK(rec, sr[i], Ls, th)\n                mb.__dict__.setdefault('crk', {})[len(mb.V)] = _ck\n"),
               ("            ring.append(mb.v(C[i] + d * rj, fib=fib, mk=mk))",
                "            ring.append(mb.v(C[i] + d * (rj * UND(rec, sr[i], d)), fib=fib, mk=mk))")):
    assert _tb.count(_a) == 1, _a
    _tb = _tb.replace(_a, _b)
_wrap = ns['tube']
exec(compile(_tb, HERE + '/game_dr09v17.py::tube', 'exec'), ns)
ns['_tube1'] = ns['tube']
ns['tube'] = _wrap
# 細枝不長到 0.8 m 以上（不擋主輪廓）
_redef(HERE + '/game_dr09v4.py', 'twigs', [("(Pt[:, 2] + rt).max() < V['H'] * 1.08", "(Pt[:, 2] + rt).max() < V['H'] * .80")])
ns['_layer_mat_v002'] = ns['layer_mat']


def layer_mat():
    """M_DR09_Layered_v017：v002 的複本，只把纖維槽的顏色換成暖米黃 DR09_FreshWood_v017_Albedo（法線沿用）。"""
    m = bpy.data.materials.get('M_DR09_Layered_v017')
    if m:
        return m
    m0 = _layer_mat_v002()
    m = m0.copy()
    m.name = 'M_DR09_Layered_v017'
    for n in m.node_tree.nodes:
        if n.type == 'TEX_IMAGE' and n.image and n.image.name == 'DR09_FreshWood_Albedo.png':
            n.image = bpy.data.images.load(f'{TEXD9}/DR09_FreshWood_v017_Albedo.png', check_existing=True)
    if m0.users == 0:
        bpy.data.materials.remove(m0)
    u = dict(m['unity'].to_dict()) if hasattr(m['unity'], 'to_dict') else dict(m['unity'])
    u['textures'] = str(u.get('textures', '')).replace('DR09_FreshWood_{Albedo,Normal} (fibre)', 'DR09_FreshWood_v017_Albedo + DR09_FreshWood_Normal (fibre)')
    m['unity'] = u
    return m


def finish_body(o, mb, lv):
    """v017 厚苔：苔權重高、朝上的面複製一層往外推 1–3 cm（雜訊起伏、順著表面），邊界收到 0.15 倍（邊緣薄、破碎）。LOD0、LOD1。"""
    finish_body_base(o, mb, lv)
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
    sel = [f for f in bm.faces if f.normal.z > .10 and sum(mv.get(v.index, 0) for v in f.verts) / len(f.verts) > .50
           and min(mv.get(v.index, 0) for v in f.verts) > .22]
    if not sel:
        bm.free()
        return
    area = sum(f.calc_area() for f in sel)
    ret = bmesh.ops.duplicate(bm, geom=sel)
    nf = [g for g in ret['geom'] if isinstance(g, bmesh.types.BMFace)]
    nv = {v for f in nf for v in f.verts}
    old = {}
    for a, b in ret['vert_map'].items():
        if b in nv:
            old[b] = a
        elif a in nv:
            old[a] = b
    sf = set(nf)
    edge = set()
    for f in nf:
        for e in f.edges:
            if len([x for x in e.link_faces if x in sf]) < 2:
                edge |= set(e.verts)
    for v in nv:
        n = v.normal.copy() if v.normal.length > .1 else Vector((0, 0, 1))
        m = mv.get(old[v].index, 0) if v in old else .6
        th = (.010 + .020 * (.5 + .5 * noise.noise(v.co * 5.0)) + .006 * noise.noise(v.co * 16.0 + Vector((3, 1, 7)))) * sm(m, .35, .85)
        th = max(th, 0.0) * (.15 if v in edge else 1.0)
        v.co += n * (th + .0015)
    for f in nf:
        for l in f.loops:
            l[cl] = (1.0, 0.0, 0.0, 0.0)
    nfc = len(nf)
    bm.to_mesh(me)
    bm.free()
    print('MOSS_SHELL lod', lv, 'faces', nfc, 'area_m2', round(area, 3))


for _f in (layer_mat, finish_body):
    ns[_f.__name__] = types.FunctionType(_f.__code__, ns, _f.__name__, _f.__defaults__)


def _make_cards_v17(body0):
    """v017：落葉卡逐片檢查依附——葉中心離地 3 cm 內算貼地；否則中心正下方 3.5 cm 內要打到木頭，
    或葉面頂點離木頭 < 8 mm 且中心離木頭 < 2 cm（斜貼在側面）。都不符合的刪掉（蘑菇十字卡不檢查）。"""
    from mathutils.bvhtree import BVHTree
    from mathutils import Vector as V3
    C = _make_cards_A_first(body0)
    me = body0.data
    co = [body0.matrix_world @ v.co for v in me.vertices]
    tree = BVHTree.FromPolygons(co, [tuple(p.vertices) for p in me.polygons])
    groups = {}
    for f, t in zip(C.F, C.tag):
        groups.setdefault(t, []).append(f)
    drop, nleaf = set(), 0
    for t, fs in groups.items():
        vs = sorted({i for f in fs for i in f})
        if len(vs) != 6:
            continue
        nleaf += 1
        P = [V3(C.V[i]) for i in vs]
        c = (P[2] + P[3]) / 2
        if c.z < .03:
            continue
        h = tree.ray_cast(c + V3((0, 0, .01)), V3((0, 0, -1)), .045)
        if h[0] is not None:
            continue
        if min(tree.find_nearest(p)[3] for p in P) < .008 and tree.find_nearest(c)[3] < .02:
            continue
        drop.add(t)
    keep = [k for k, t in enumerate(C.tag) if t not in drop]
    C.F = [C.F[k] for k in keep]
    C.tag = [C.tag[k] for k in keep]
    print('LEAF_CHECK leaves', nleaf, 'removed_floating', len(drop))
    ns['LEAF_CHECK'] = dict(leaves=nleaf, removed_floating=len(drop))
    return C


ns['make_cards'] = _make_cards_v17
ns['LAYOUT'] = LAYOUT
ns['zlib'] = zlib


def run(v, phase):
    ns['PHASE'] = phase
    import bpy
    asset = ns['NAMES'][v]
    if phase == 2:
        ns['run'](v)
        rep = ns['contact_report']()
        bpy.context.scene['dr09_v17_contacts'] = json.dumps(rep)
        bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_v017.blend', copy=True)
        print('CONTACT_SUMMARY', rep)
        return
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    ns['plan'](v)
    ns['cleanup']()
    R_ = ns['RECS']
    print('DEAD', [(x['kind'], x.get('name', ''), np.round(x['P'][len(x['P']) // 2], 2).tolist()) for x in R_ if x.get('dead')])
    if os.environ.get('DR9DUMP'):
        json.dump([dict(id=x['id'], parent=x.get('parent'), name=x.get('name', ''), kind=x['kind'], P=np.round(x['P'][::2], 3).tolist(), r=np.round(x['r'][::2], 3).tolist())
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
    out = os.environ.get('DR9OUT', f'{HERE}/blend/{asset}_v017_greybox.blend')
    bpy.ops.wm.save_as_mainfile(filepath=out, copy=True)
    print('GREYBOX_DONE', out)


if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    try:
        run(a[0] if a else 'L', int(a[1]) if len(a) > 1 else 2)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
