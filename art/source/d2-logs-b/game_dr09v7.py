# DR09 斷枝堆 v007（L 樣品）：以 v006 為底稿另存，不重建、不重新隨機散佈（同一個種子 9606，
# v006 的每一根木頭照原來的順序、原來的亂數放下去；新加的東西一律用另一個亂數 R2，排在 v006 的分岔／殘枝之後）。
# 本輪修改（形體與疊壓，不加裝飾、不動落葉數量、材質解析度、光線）：
#   1. F（正面中央的長直斜枝）：從「一端落地、一端挑高」的硬桿改成順著 A 的拱背搭過去、尾端落到後方，
#      傾角降低、和 A 有明確接觸；右側 E 的分叉挑出保留。
#   2. 中層補兩根中型腐木（N1、N2，粗度介於主幹與細枝之間，長度不同）：
#      N1 在中後方，從右後斜向左前搭在 D、B、A 上，正面露出一段上緣；N2 斜向疊壓在 E、B、D 上，打斷俯視右半的空白。
#   3. B 改成較直、帶一處局部折轉（不再是平滑波浪），粗細沿長度平順過渡；A 的位置與粗細不動。
#   4. 前方最醒目的斷口（C 的前端）：斷面加大深淺落差、一處大缺角、木芯保留厚度略凸、少量沿木紋的厚裂片。
#   5. 細枝：主幹與中型木各長幾根小分岔（不只長在外緣），再加幾根卡在木縫裡的斷枝；長短粗細方向不同，有疏有密。
# 用法：
#   blender -b --python art/source/d2-logs-b/game_dr09v7.py -- L 1   （灰模：blend/…_v007_greybox.blend，不匯出）
#   blender -b --python art/source/d2-logs-b/game_dr09v7.py -- L 2   （完整：匯出 FBX／GLB、存 blend/…_v007.blend）
import sys, os, math, types, random, traceback, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
H5 = {'__name__': 'dr09_v5_for_v7', '__file__': HERE + '/game_dr09v5.py'}
exec(compile(open(H5['__file__'], encoding='utf-8').read(), H5['__file__'], 'exec'), H5)
ns = H5['ns']
ns['VER'] = 'v007'
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
    assert v == 'L', 'v007 先做 L 樣品'
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
        bpy.context.scene['dr09_v7_contacts'] = json.dumps(rep)
        bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_v007.blend', copy=True)
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
    bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_v007_greybox.blend', copy=True)
    print('GREYBOX_DONE')


if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    try:
        run(a[0] if a else 'L', int(a[1]) if len(a) > 1 else 2)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
