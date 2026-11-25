# DR09 斷枝堆 v006（L 樣品）：停止前幾輪「減枝、收攏、統一方向」的趨勢，回到最初 DR09 參考圖：
# 多根粗細不同的腐木交錯堆積，有前後厚度、局部挑出的斷枝、不規則透空。v005 的腳本、模型都不動。
# 本輪只改主要形體與擺放；材質、UV、斷口、苔的做法全部沿用 v005（載入 game_dr09v5.py，只換 plan()）。
#
#   A（最粗，直徑約 38 cm）：拱高從 0.82 m 降到約 0.6 m，拱後有一個往下的折點，不再是一條連續的平滑弧；
#      長度縮到約 3.2 m（v005 3.9 m），只佔堆的左半到中段，不再從左到右擋住其他主幹。
#   B（第二粗，約 29 cm）：從左後方地面斜向右前方，依序壓過 C 與 A 的局部（A×B 交叉點在 x≈0.45），
#      最高點在右側（和 A 的拱頂錯開），正面與斜視都看得到它疊在 A 上。
#   C（約 26 cm）：放最低，從左前方斜到後方中段，以約 50° 從 A、B 底下穿過，撐出前後厚度。
#      三個交叉點錯開：A×C 在 x≈-0.65、B×C 在 x≈-0.3、A×B 在 x≈0.45。
#   次要木頭：F（左、挑出約 0.8 m）、E（右、挑出約 0.65 m）兩根中型木不同高度局部挑出，打破平滑的上緣；
#      D、C0 墊在右後與左後撐厚度；外圍短木（M1、M2）收回堆邊；不加細枝填充。
# 用法：
#   blender -b --python art/source/d2-logs-b/game_dr09v6.py -- L 1   （灰模：blend/…_v006_greybox.blend，不匯出）
#   blender -b --python art/source/d2-logs-b/game_dr09v6.py -- L 2   （完整：匯出 FBX／GLB、存 blend/…_v006.blend）
import sys, os, math, types, random, traceback, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
H5 = {'__name__': 'dr09_v5_for_v6', '__file__': HERE + '/game_dr09v5.py'}
exec(compile(open(H5['__file__'], encoding='utf-8').read(), H5['__file__'], 'exec'), H5)
ns = H5['ns']
ns['VER'] = 'v006'
ns['VARIANTS']['L'].update(twigs=8, litter=4, seed=9606)


def plan(v):
    global V, SEG, OWN, RECS, CONTACTS
    assert v == 'L', 'v006 先做 L 樣品'
    V = dict(VARIANTS[v], v=v)
    SEG, OWN, RECS, CONTACTS = np.zeros((0, 8)), np.zeros(0, int), [], []
    R = random.Random(V['seed'])

    def put(name, ctrl, r0, taper, mode, sink, k=.3, shape=None, lumps=2, ends=('break', 'break'), e=(.06, .12), main=False, twr=None, settle=False):
        Q, s = spline_path(ctrl)
        r = heavy_radius(R, s, r0, taper, lumps)
        t = s / s[-1]
        if mode == 'rigid':
            P = _place_rigid1(Q, s, r, set(), sink, shape(t, s) if shape else None)
            if settle:
                P = settle_ends(P, s, r, sink)
        else:
            P = drape(Q, s, r, set(), sink, k, shape(t, s) if shape else None)
        rec = new_rec(R, 'branch', P, s, r, ends, main=main)
        rec['xs'] = xs_params(R, e)
        if twr is not None:
            rec['xs']['twr'] = twr
        rec['heavy'] = r0 > .06
        rec['name'] = name
        rec['ext'] = [1.0, 1.0]
        rec['splint'] = [[], []]
        cap_params(R, rec)
        add_seg(rec)
        return rec

    # 底層（貼地）：C 從左前斜到後方中段；C0 墊在左後；D 墊在右後
    C = put('C', [(-1.45, -.95), (-.95, -.35), (-.45, .25), (.05, .85)], .13, .36, 'drape', .22, k=.3, lumps=3, twr=.7)
    C0 = put('C0', [(-1.85, .62), (-1.30, .50), (-.75, .52)], .11, .35, 'drape', .20, k=.3, lumps=2)
    D = put('D', [(.55, .62), (1.20, .48), (1.85, .40)], .10, .38, 'drape', .14, k=.3, lumps=2, twr=.9)
    # A：拱降低、拱後往下折一次（不是連續平滑弧），只佔左半到中段；扭轉保留
    A = put('A', [(-2.00, -.22), (-1.20, -.20), (-.40, -.05), (.40, .14), (1.15, .26)], .19, .36, 'rigid', .24,
            shape=lambda t, s: .26 * np.exp(-((t - .26) / .15) ** 2) + kink(t, .46, -.20, .03) + kink(t, .62, .16, .03),
            lumps=4, main=True, twr=.65, settle=True)
    # B：左後地面 → 壓過 C、A 的局部 → 右前；最高點在右側
    B = put('B', [(-1.45, .82), (-.60, .50), (.20, .22), (.90, -.05), (1.45, -.30)], .145, .40, 'rigid', .18,
            shape=lambda t, s: kink(t, .40, .08, .03), lumps=3, twr=-.8, settle=True)
    # 中型木局部挑出（高度不同）：F 搭在 A 的拱上往左上挑；E 搭在 D 與 B 上往左前挑
    F = put('F', [(-.20, -.72), (-.50, -.38), (-.80, -.04), (-1.02, .20)], .068, .42, 'rigid', .08,
            shape=lambda t, s: kink(t, .62, -.18), lumps=1, e=(.04, .09))
    E = put('E', [(.30, -.58), (.78, -.38), (1.24, -.12), (1.58, .10)], .078, .40, 'rigid', .10,
            shape=lambda t, s: kink(t, .66, -.14), lumps=2)
    # 外圍短木收回堆邊（前右、後左），順著主體邊緣
    M1 = put('M1', [(.80, -.74), (1.22, -.70), (1.66, -.54)], .052, .45, 'drape', .08, k=.4, lumps=1, e=(.04, .08))
    M2 = put('M2', [(-1.20, .90), (-.65, .86), (-.15, .80)], .046, .45, 'drape', .08, k=.4, lumps=1, e=(.04, .08))
    heavy_splinters(R, A, 0, 3, .30)
    for rec in (B, C, E):
        e_ = R.choice((0, 1))
        if rec['ends'][e_] == 'break':
            heavy_splinters(R, rec, e_, 1, .12)
    # 分岔：少量、往外挑（參考圖每根粗枝都有短叉），不往中央長
    for rec, t, side, fl, zr in ((A, .70, -1, .70, .16), (B, .78, 1, .65, .20), (C, .35, -1, .50, .12), (E, .70, 1, .40, .15)):
        f = add_fork(R, rec, t, side, fl, zr, (.48, .58))
        if f is None:
            add_fork(R, rec, t + .06, -side, fl * .85, zr, (.48, .58))
    for rec, n in ((A, 2), (B, 2), (C, 1), (D, 1)):
        add_stubs(R, rec, n)
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
    print('PLAN', v, 'phase', PHASE, {k: sum(1 for x in RECS if x['kind'] == k) for k in ('branch', 'fork', 'stub', 'twig', 'litter')}, 'contacts', len(CONTACTS))
    for x in RECS:
        if x['kind'] == 'branch':
            top = x['P'][:, 2] + x['r']
            print('  MAIN', x['name'], 'd_cm', round(x['r0'] * 200, 1), 'len', round(float(x['s'][-1]), 2),
                  'ends', round(float(x['P'][0, 2] - x['r'][0]), 2), round(float(x['P'][-1, 2] - x['r'][-1]), 2),
                  'top', round(float(top.max()), 3), 'at_x', round(float(x['P'][top.argmax(), 0]), 2))
    return RECS


ns['plan'] = types.FunctionType(plan.__code__, ns, 'plan')


def run(v, phase):
    ns['PHASE'] = phase
    import bpy
    asset = ns['NAMES'][v]
    if phase == 2:
        ns['run'](v)
        rep = ns['contact_report']()
        bpy.context.scene['dr09_v6_contacts'] = json.dumps(rep)
        bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_v006.blend', copy=True)
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
    bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_v006_greybox.blend', copy=True)
    print('GREYBOX_DONE')


if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    try:
        run(a[0] if a else 'L', int(a[1]) if len(a) > 1 else 2)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
