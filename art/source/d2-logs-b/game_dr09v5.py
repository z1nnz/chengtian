# DR09 斷枝堆 v005（L 樣品）：在 v004 上去掉「拱橋、三角支架、放射排列」的人工感，收成緊密但不規則的腐木堆。
# v004 的腳本、模型都不動。主幹粗度沿用 v004（不再加粗），細枝不加量，不靠細分。
# 做法：載入 game_dr09v4.py（它再載 v3、v2、v1），在 v001 原始碼執行前再改斷口與裂縫，擺法 plan() 換掉。
#
# 灰模
#   1. 只留一根主要拱形木（A，拱頂偏左、不對稱）；其他改成較平直、局部折彎（折點各不相同）、偏心扭轉，最高點錯開。
#      v004 用「包絡披掛」擺的 B、F、G 會長成同心的弧線，v005 除了貼地的 C0 以外都改成剛性擺放＋局部折彎。
#   2. 正面中央洞口：中型木 G 從前方斜靠進 A 的拱下，遮住洞口左半；拱後方的 C0 也露出一段，空隙大小不一、不對稱。
#   3. 右上三角支架：D 從 2.5 m 縮到約 1.5 m、轉成順著倒伏方向，低角度搭在 A 的尾段上，不再從高處斜插到地面。
#   4. 俯視：大部分木頭順著同一個倒伏方向（約 x 軸、±20°），E、F 兩根斜向木打破規律，交叉點沿 x 方向錯開；
#      外圍的中枝收回堆邊；分岔改成順著倒伏方向長（不往四面放射），數量 7 → 4。
#   5. 斷口：斜的斷裂面（深淺不一）＋缺角（一段齒收到幾乎貼平）＋一側殘留樹皮（樹皮色、凸出斷面一截）；
#      靠近斷口沿木紋的裂縫（往內凹、露出木色）；木刺 A 粗頭 3 根（1 長 2 短），其他 0～1 根短的。
# 苔
#   打散成不連續的小塊（雜訊頻率約 v004 的 2 倍、門檻提高），塊之間露出樹皮；薄層幾何只長在苔最濃的地方（門檻 0.72），厚 0.4～1.2 cm。
# 用法：
#   blender -b --python art/source/d2-logs-b/game_dr09v5.py -- L 1   （灰模：blend/…_v005_greybox.blend，不匯出）
#   blender -b --python art/source/d2-logs-b/game_dr09v5.py -- L 2   （完整：匯出 FBX／GLB、存 blend/…_v005.blend）
import sys, os, math, types, random, traceback, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')


def _v5_patch(src):
    R = [
        # 斷口外圈：殘留樹皮那段貼齊樹皮面、樹皮色
        ("ext.append((mb.v(C[i] + Te * ln + d * rr * CAPW(rec) * XS(rec, sr[i], th), fib=1.0, mk=0), ln))",
         "ext.append((mb.v(C[i] + Te * ln + d * rr * CAPW2(rec, e, th) * XS(rec, sr[i], th), fib=CAPF(rec, e, th), mk=0), ln))"),
        # 靠近斷口、沿木紋的裂縫
        ("                rj *= 1 - .07 * fib\n",
         "                _ck = CRACK(rec, sr[i], Ls, th)\n                fib = max(fib, _ck)\n                rj *= 1 - .07 * fib - .22 * _ck\n"),
    ]
    for a, b in R:
        assert src.count(a) == 1, a[:80]
        src = src.replace(a, b)
    return src


_v4 = open(HERE + '/game_dr09v4.py', encoding='utf-8').read()
for a, b in (("_v4_patch(_v3_patch(_src))", "_v5_patch(_v4_patch(_v3_patch(_src)))"),
             ("'_v3_patch': _v3_patch, '_v4_patch': _v4_patch}\")", "'_v3_patch': _v3_patch, '_v4_patch': _v4_patch, '_v5_patch': _v5_patch}\")"),
             ("'/game_dr09v3.py', '_v4_patch': _v4_patch}", "'/game_dr09v3.py', '_v4_patch': _v4_patch, '_v5_patch': _v5_patch}")):
    assert _v4.count(a) == 1, a
    _v4 = _v4.replace(a, b)
H4 = {'__name__': 'dr09_v4_for_v5', '__file__': HERE + '/game_dr09v4.py', '_v5_patch': _v5_patch}
exec(compile(_v4, H4['__file__'], 'exec'), H4)
ns = H4['ns']
ns['VER'] = 'v005'
ns['VARIANTS']['L'].update(twigs=8, litter=5, seed=9505)


def _angd(a, b):
    return abs((a - b + math.pi) % (2 * math.pi) - math.pi)


def CAPLN(rec, e, th, rng):
    cp = rec.get('cap')
    c = math.cos(th - rec['tear'][e])
    if not cp:
        return (.04 + .26 * max(0, c) ** 2 * rng.uniform(.3, 1.2) + .16 * rng.random() ** 2) * min(rec['ext'][e], 1.1)
    p = cp[e]
    j = rng.random()
    if _angd(th, p['notch']) < p['nw']:                        # 缺角：這段幾乎貼平、比旁邊低一截
        return .01 + .03 * j
    ln = .03 + p['tilt'] * (1 + c) + .14 * j ** 1.5            # 斜的斷裂面，深淺不一
    if c > .75 and j > .70:
        ln += p['tooth']                                         # 撕裂那側偶爾一根高齒
    if _angd(th, p['lip']) < p['lw']:
        ln += p['lipl']                                          # 殘留樹皮凸出斷面一截
    return ln


def CAPW2(rec, e, th):
    cp = rec.get('cap')
    if not cp:
        return .80
    return 1.0 if _angd(th, cp[e]['lip']) < cp[e]['lw'] else .93


def CAPF(rec, e, th):
    cp = rec.get('cap')
    if not cp:
        return 1.0
    return 0.0 if _angd(th, cp[e]['lip']) < cp[e]['lw'] * .8 else 1.0


def CRACK(rec, s, Ls, th):
    w = 0.0
    for (e, thc, Lc, aw) in rec.get('cracks', ()):
        de = s if e == 0 else Ls - s
        a = float(sm(Lc - de, 0, Lc * .6)) * math.exp(-(_angd(th, thc) / aw) ** 2)
        w = max(w, a)
    return w


def kink(t, tk, a, w=.05):
    """局部折彎：t = tk 之前是直的，之後以斜率 a 轉向（圓角寬 w）。"""
    return a * w * np.logaddexp(0, (t - tk) / w)


def cap_params(R, rec):
    rec['cap'] = [dict(tilt=U(R, .06, .22), notch=rec['tear'][e] + math.pi + U(R, -1.2, 1.2), nw=U(R, .35, .75),
                       tooth=U(R, .25, .55), lip=rec['tear'][e] + math.pi * U(R, .55, .85) * R.choice((-1, 1)), lw=U(R, .35, .60),
                       lipl=U(R, .10, .30)) for e in (0, 1)]
    rec['cracks'] = []
    for e in (0, 1):
        if rec['ends'][e] != 'break':
            continue
        for _ in range(R.randint(1, 2) if rec['r0'] > .08 else R.randint(0, 1)):
            rec['cracks'].append((e, U(R, 0, 2 * math.pi), rec['r0'] * U(R, 2.5, 5.0), U(R, .14, .22)))


def plan(v):
    global V, SEG, OWN, RECS, CONTACTS
    assert v == 'L', 'v005 先做 L 樣品'
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

    # 倒伏方向約沿 x 軸（略往 +y 偏）。C0 貼地躺在後方，從 A 的拱下看得到它的一段。
    C0 = put('C0', [(-1.75, .40), (-1.05, .28), (-.35, .14), (-.05, .12)], .12, .35, 'drape', .22, k=.3, lumps=3)
    # 唯一的拱：A，拱頂偏左（t≈0.30）、右段平、尾端微微翹（不對稱，不是規整的橋）
    A = put('A', [(-2.05, -.10), (-1.20, -.38), (-.15, -.10), (.85, .12), (1.70, -.05)], .19, .36, 'rigid', .24,
            shape=lambda t, s: .50 * np.exp(-((t - .30) / .18) ** 2) + kink(t, .80, .10), lumps=4, main=True, twr=.55, settle=True)
    # B：較平直，順倒伏方向躺在 A 後方；左端貼地，右段搭在 D 上微微抬起（高點在右、和 A 的拱頂錯開，正面看是往右上的一條斜線，不和 A 的拱平行）
    D = put('D', [(1.98, .12), (1.58, .44), (1.20, .80)], .10, .38, 'rigid', .12, shape=lambda t, s: kink(t, .45, .06), lumps=2, twr=.9)
    B = put('B', [(-1.30, .80), (-.50, .64), (.30, .46), (1.05, .22), (1.62, .02)], .14, .40, 'rigid', .18,
            shape=lambda t, s: kink(t, .58, .10, .03), lumps=3, twr=-.75)
    # G：中型木平躺在 A 拱下的前緣地面（擋住洞口下緣）
    G = put('G', [(-1.40, -.80), (-.90, -.68), (-.40, -.82)], .060, .42, 'drape', .10, k=.3, lumps=1, e=(.04, .09))
    # 斜向木（打破同向）：都跨在兩根以上的木頭上、接近水平，不一頭著地一頭戳高
    # F：在正面洞口前方斜跨 A 的拱、C0、B（交叉點 x≈-0.3），遮住洞口的一部分
    F = put('F', [(-.48, -.52), (-.30, -.12), (-.10, .32), (.06, .80)], .066, .42, 'drape', .10, k=.85, lumps=1, e=(.04, .09))
    # E：左側斜跨 C0 與 A 粗頭（交叉點 x≈-1.6）
    E = put('E', [(-2.00, .78), (-1.75, .25), (-1.55, -.22), (-1.47, -.46)], .075, .40, 'drape', .10, k=.32, lumps=2)
    # 中枝收回堆邊、順倒伏方向躺
    M1 = put('M1', [(.55, -.70), (1.05, -.80), (1.55, -.72)], .052, .45, 'rigid', .08, shape=lambda t, s: kink(t, .5, .06), lumps=1, e=(.04, .08))
    M2 = put('M2', [(-1.05, 1.10), (-.40, 1.04), (.20, 1.00)], .046, .45, 'rigid', .08, shape=lambda t, s: kink(t, .4, -.05), lumps=1, e=(.04, .08))
    # 木刺：A 粗頭 3 根（1 長 2 短），其他斷口 0～1 根短的
    heavy_splinters(R, A, 0, 3, .30)
    for rec in (B, C0, D):
        e_ = R.choice((0, 1))
        if rec['ends'][e_] == 'break':
            heavy_splinters(R, rec, e_, 1, .10)
    # 分岔：順倒伏方向（側角小）、4 根
    for rec, t, side, fl, zr in ((A, .64, 1, .85, .14), (B, .74, -1, .75, .12), (C0, .30, 1, .55, .10), (E, .62, -1, .45, .12)):
        f = add_fork(R, rec, t, side, fl, zr, (.48, .58))
        if f is None:
            f = add_fork(R, rec, t + .06, -side, fl * .85, zr, (.48, .58))
    for rec, n in ((A, 2), (B, 2), (C0, 1), (D, 1)):
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
        twigs(R, [x for x in RECS if x['kind'] == 'fork'] + [E, F, G, M1, M2])
        litter(R)
    print('PLAN', v, 'phase', PHASE, {k: sum(1 for x in RECS if x['kind'] == k) for k in ('branch', 'fork', 'stub', 'twig', 'litter')},
          'contacts', len(CONTACTS))
    for x in RECS:
        if x['kind'] == 'branch':
            top = x['P'][:, 2] + x['r']
            print('  MAIN', x['name'], 'd_cm', round(x['r0'] * 200, 1), 'len', round(float(x['s'][-1]), 2),
                  'zmin', round(float((x['P'][:, 2] - x['r']).min()), 3), 'ends', round(float(x['P'][0, 2] - x['r'][0]), 2), round(float(x['P'][-1, 2] - x['r'][-1]), 2), 'top', round(float(top.max()), 3), 'at_x', round(float(x['P'][top.argmax(), 0]), 2))
    return RECS


def settle_ends(P, s, r, sink):
    """剛性擺放只用重心兩側的兩個支點，超出的末段會懸在半空。從最後一個接觸點往外，末段往下折到地面（碰到別根就少折一點）。"""
    P = P.copy()
    g = r * (1 - sink)
    c = clearance(P, r, set())
    touch = (P[:, 2] - g < .012) | (c < .012)
    if not touch.any():
        return P
    idx = np.nonzero(touch)[0]
    for e in (0, 1):
        k = idx[0] if e == 0 else idx[-1]
        seg = np.arange(0, k + 1) if e == 0 else np.arange(k, len(P))
        if len(seg) < 4:
            continue
        L = abs(s[seg[-1]] - s[seg[0]])
        if L < .25:
            continue
        u = np.abs(s[seg] - s[k]) / L
        d0 = float(P[seg[0] if e == 0 else seg[-1], 2] - g[seg[0] if e == 0 else seg[-1]])
        if d0 < .02:
            continue
        for f in (1.0, .7, .45, .25):
            Q = P.copy()
            Q[seg, 2] -= d0 * f * u ** 1.6
            if clearance(Q, r, set()).min() > -.002:
                P = Q
                break
    return P


def finish_body_base(o, mb, lv):
    """苔：不連續小塊（約 0.4 m 一塊、塊間露樹皮），朝上面＋潮濕凹處；地衣、落葉土同 v003。"""
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
    nzA = np.array([noise.noise(Vector(p * 2.4)) for p in co])
    nzB = np.array([noise.noise(Vector(p * 6.0 + 7.0)) for p in co])
    nz7 = np.array([noise.noise(Vector(p * 9.0 + 37.0)) for p in co])
    nz15 = np.array([noise.noise(Vector(p * 22.0 + 5.0)) for p in co])
    up = vn[:, 2]
    bark = (kind == 0) * (1 - fib)
    ao = vertex_ao(o, rays=14, dist=.30) if lv < 2 else np.ones(n)
    crev = sm(.78 - ao, 0, .25)
    if CONTACTS:
        Cc = np.array(CONTACTS)
        dcon = np.min(np.linalg.norm(co[:, None, :] - Cc[None], axis=2), axis=1)
    else:
        dcon = np.full(n, 9.0)
    near = sm(.18 - dcon, 0, .12)
    thick = sm(r0 / V['main'], .30, .70)
    patch = sm(nzA + .45 * nzB, -.04, .18) * sm(nz15 + .45, 0, .35)            # 小塊、塊內再有破洞
    moss_top = thick * sm(up, .28, .68) * patch
    moss_wet = sm(r0, .02, .05) * sm(up, -.30, .25) * np.maximum(crev, near) * sm(nzB, -.2, .2)
    moss = np.clip(np.maximum(moss_top, .80 * moss_wet), 0, 1) * bark
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


def finish_body(o, mb, lv):
    """苔的薄層幾何：只在苔最濃（> 0.72）、朝上的小塊，邊緣貼平、中間 0.4～1.2 cm。"""
    finish_body_base(o, mb, lv)
    if lv > 1:
        return
    import bmesh
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    cl = bm.loops.layers.float_color['Layers']
    bm.normal_update()
    mv = {}
    for f in bm.faces:
        for l in f.loops:
            mv[l.vert.index] = max(mv.get(l.vert.index, 0), l[cl][0])
    sel = [f for f in bm.faces if f.normal.z > .35 and all(mv.get(v.index, 0) > .66 for v in f.verts)]
    if not sel:
        bm.free()
        return
    ret = bmesh.ops.duplicate(bm, geom=sel)
    nf = [g for g in ret['geom'] if isinstance(g, bmesh.types.BMFace)]
    sf = set(nf)
    edge = set()
    for f in nf:
        for e in f.edges:
            if len([x for x in e.link_faces if x in sf]) < 2:
                edge |= set(e.verts)
    for v in {v for f in nf for v in f.verts}:
        n = v.normal if v.normal.length > .1 else Vector((0, 0, 1))
        th = .004 + .008 * (.5 + .5 * noise.noise(v.co * 7.0))
        v.co += n * (th * (.08 if v in edge else 1.0) + .0012)
    for f in nf:
        for l in f.loops:
            c = l[cl]
            l[cl] = (1.0, 0.0, 0.0, c[3])
    bm.to_mesh(me)
    bm.free()
    print('MOSS_SHELL lod', lv, 'faces', len(nf))


for f in (settle_ends, _angd, CAPLN, CAPW2, CAPF, CRACK, kink, cap_params, plan, finish_body_base, finish_body):
    ns[f.__name__] = types.FunctionType(f.__code__, ns, f.__name__, f.__defaults__, f.__closure__)


def run(v, phase):
    ns['PHASE'] = phase
    import bpy
    asset = ns['NAMES'][v]
    if phase == 2:
        ns['run'](v)
        rep = ns['contact_report']()
        bpy.context.scene['dr09_v5_contacts'] = json.dumps(rep)
        bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_v005.blend', copy=True)
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
    bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_v005_greybox.blend', copy=True)
    print('GREYBOX_DONE')


if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    try:
        run(a[0] if a else 'L', int(a[1]) if len(a) > 1 else 2)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
