
ns['os'] = os

# ======================================================================== v029 檔尾
# 三、T1 後段：v028 往右後斜伸到 y 0.82，俯視超出參考後緣 → 前段維持斜向（與 A 交叉），後段彎回中段（梢端 y 0.36），長度、高度不變
ns['T1_27']['c'] = [(-.64, .02, .22), (-.44, .09, .33), (-.22, .17, .45), (-.02, .25, .56), (.20, .32, .67), (.45, .37, .77), (.66, .39, .85), (.82, .38, .90), (.96, .36, .945)]
# 五、A 左端裂片：透鏡形截面（中間厚、兩側薄、側緣略低於樹皮）只在這組裂片上，用 scope 明確標記（T1 末端裂片不標記 → 原截面）
# 一、v027 補在斷口下方的兩片短裂片（用來遮圓團）拿掉：下半部改由斷口本體自己劈裂
ns['STAVES_A'] = [dict(_st, lens=.78, edge=.06, scope=('A', 0)) for _st in ns['STAVES_A'][:-2]]
if os.environ.get('DR9NOSTAVE'):                       # 驗證用：隱藏 A 左端附加裂片，只看斷口本體
    ns['STAVES_A'] = []

# 一＋二、A 左端斷口本體（取代外張唇緣＋中心扇形的蓋子）。th：0＝下、π/2＝後、−π/2＝前、π＝上（與裂片同一框架）。
#   tongues：(方位, 比基底多出的長度 m, 半寬 rad) —— 下半部的殘片長短不一、之間是沿木紋的凹口；上半部短（上方由長裂片負責）。
#   tip_thk：殘片末端厚度（倍半徑；短片厚、長片薄）；core_*：中央撕裂木芯面（內凹、前後錯落）
ns['BRK29_A'] = dict(
    seed=29011, base=.035, jag=.030,
    tongues=[(-.62, .22, .50, .45), (.22, .12, .40, -.35), (1.00, .27, .46, -.50), (-1.48, .09, .34, .30), (1.78, .16, .40, .40),
             (-2.30, .07, .36, -.30), (2.62, .09, .40, .35), (3.08, .05, .30, 0.)],
    tip_thk=(.44, .20), core_r=.50, core_a=.015, core_j=.030, core_fill=.50, cen_a=.008, droop=.020, gap_dark=.32)


def BRK29(mb, rec, lv, e, i, C, T, rings, Ne, Be, rr, nsd, sr_uv, circ, k_):
    if rec.get('name') != 'A' or rec.get('kind') != 'branch' or e != 0 or os.environ.get('DR9BRK29') == '0':
        return False
    bk = BRK29_A
    Te = -np.array(T[i], float)
    Te /= np.linalg.norm(Te)
    c0 = np.array(C[i], float)
    ring0 = rings[i][0]
    rad0, fib0 = [], []
    for v in ring0:
        q = np.array(mb.V[v]) - c0
        rad0.append(float(np.linalg.norm(q - Te * (q @ Te))))
        fib0.append(mb.fib[v])
    m = (3, 2, 1)[lv]
    nb = nsd * m
    K = (5, 3, 2)[lv]
    crk = mb.__dict__.setdefault('crk', {})
    hj = lambda k: math.sin(k * 12.9898 + bk['seed'] * .0137) * .5 + .5

    def angd(a, b):
        return abs((a - b + math.pi) % (2 * math.pi) - math.pi)

    Lmax = max(t[1] for t in bk['tongues'])
    cols = []
    for jb in range(nb):
        th = 2 * math.pi * jb / nb
        Lj, tongue = bk['base'], 0.0
        for tc, Lk, wk, sl in bk['tongues']:
            sx = ((th - tc + math.pi) % (2 * math.pi) - math.pi) / wk
            x = abs(sx)
            if x < 1:
                v_ = Lk * (1 - x ** 3.0) ** .35 * (1 + sl * sx)                  # 寬平頂、兩側陡（劈裂面）、末端斜撕（一側長一側短），不是指狀尖頭
                if v_ > tongue:
                    tongue = v_
        _jg = .6 * (hj(jb * 3.1) - .5) + .4 * (hj((jb // 2) * 3.1 + 9) - .5)          # 參差（兩格一組，不是逐格鋸齒）
        Lj += tongue + bk['jag'] * _jg * (.4 + .6 * min(1.0, tongue / .08))
        Lj = max(Lj, .018)
        jf = jb / m
        j0 = int(jf) % nsd
        j1 = (j0 + 1) % nsd
        fr = jf - int(jf)
        rb = rad0[j0] * (1 - fr) + rad0[j1] * fr
        fb = fib0[j0] * (1 - fr) + fib0[j1] * fr
        d = Ne * math.cos(th) + Be * math.sin(th)
        cols.append((th, Lj, tongue, rb, fb, d))

    # 鄰近殘片長度的平滑值（±0.6 rad）：木芯面跟著殘片往外長，內部是實木，不是挖空的殼
    Ls = []
    for jb in range(nb):
        acc = wsum = 0.0
        for kk in range(-nb // 2, nb // 2):
            dth = 2 * math.pi * kk / nb
            wgt = math.exp(-(dth / .6) ** 2)
            acc += wgt * cols[(jb + kk) % nb][1]
            wsum += wgt
        Ls.append(acc / wsum)
    Lmean = sum(Ls) / nb

    def P(col, a, rad, f=0.0):
        th, Lj, tongue, rb, fb, d = col
        p = c0 + Te * a + d * rad
        p[2] -= bk['droop'] * f * f * max(0.0, math.cos(th)) * min(1.0, tongue / .15)   # 下側長殘片末端略往下垂（撕裂方向）
        return p

    def uv_out(jb, a):
        return (sr_uv[i] - a * k_, circ(i, jb / m))

    def uv_in(p):
        q = p - c0
        return (float(q @ Be) * k_ * 1.6, float(q @ Ne) * k_ * 1.6 + float(q @ Te) * k_)

    # 外表面：O_0 … O_K（O_0 貼在主幹最後一圈外 4 mm）
    S, UVS = [], []
    for k in range(K + 1):
        f = k / K
        ring, uvr = [], []
        for jb, col in enumerate(cols):
            th, Lj, tongue, rb, fb, d = col
            a = max(.004, f * Lj)
            lng = min(1.0, tongue / .10)
            rad = rb * (1 + .03 * f - .12 * f * f * lng)                       # 長殘片末端略往內收（不外張）
            p = P(col, a, rad, f)
            crk[len(mb.V)] = 0.0
            ring.append(mb.v(p, fib=min(1.0, fb + .55 * f * f * lng), mk=0))
            uvr.append(uv_out(jb, a))
        S.append(ring)
        UVS.append(uvr)
    # 撕裂面：TI（殘片末端內緣）→ CO（中央木芯面外圈）→ MI（木芯內圈）→ 中心
    tip_in, core, mid = [], [], []
    for jb, col in enumerate(cols):
        th, Lj, tongue, rb, fb, d = col
        lr = min(1.0, tongue / Lmax)
        tt = rr * (bk['tip_thk'][0] + (bk['tip_thk'][1] - bk['tip_thk'][0]) * lr)   # 短片厚、長片薄
        rad_tip = rb * (1 + .03 - .12 * min(1.0, tongue / .10))
        a_ti = Lj - .30 * tt
        wav = .55 * math.sin(2 * th + 1.1) + .30 * math.sin(3 * th + 2.3) + .15 * math.sin(5 * th + .4)   # 木芯面低頻起伏（不是逐格亂跳的星形摺）
        a_co = min(bk['core_a'] + bk['core_fill'] * Ls[jb] + bk['core_j'] * wav, a_ti - .006)
        r_co = rr * (bk['core_r'] + .10 * (hj(jb * 1.7 + 2) - .5))
        r_ti = max(rad_tip - tt, r_co + .004)
        a_mi = bk['core_a'] + .75 * bk['core_fill'] * (.5 * Ls[jb] + .5 * Lmean) + bk['core_j'] * .5 * math.sin(3 * th + 4.0)
        for lst, a, rad, f, dk in ((tip_in, a_ti, r_ti, 1.0, bk['gap_dark'] * lr), (core, a_co, r_co, 0.0, bk['gap_dark'] * (.4 + .6 * lr)), (mid, a_mi, rr * .22, 0.0, .15)):
            p = P(col, a, rad, f)
            crk[len(mb.V)] = dk
            lst.append(mb.v(p, fib=1.0, mk=0))
    _am = [float((np.array(mb.V[x]) - c0) @ Te) for x in mid]
    cp = c0 + Te * (sum(_am) / len(_am) + bk['cen_a'])                    # 中心與內圈平均同深（不是內凹錐，避免星形摺）
    crk[len(mb.V)] = .35
    cen = mb.v(cp, fib=1.0, mk=0)

    def face(idx, uvs):
        mb.f(tuple(idx), uvs)

    # 主幹最後一圈（nsd 點）→ O_0（nb 點）：每段一組扇形三角形，方向與原斷口蓋相同
    for j in range(nsd):
        j1 = (j + 1) % nsd
        o = [S[0][(m * j + t) % nb] for t in range(m + 1)]
        ou = [UVS[0][(m * j + t) % nb] for t in range(m + 1)]
        u0, u1 = (sr_uv[i], circ(i, j)), (sr_uv[i], circ(i, j + 1))
        ou[-1] = (ou[-1][0], circ(i, j + 1))
        face((ring0[j], o[0], o[1]), [u0, ou[0], ou[1]])
        face((ring0[j1], ring0[j], o[1]), [u1, u0, ou[1]])
        for t in range(1, m):
            face((ring0[j1], o[t], o[t + 1]), [u1, ou[t], ou[t + 1]])
    # 外表面各圈
    for k in range(K):
        for jb in range(nb):
            jb1 = (jb + 1) % nb
            uva, uvb = UVS[k], UVS[k + 1]
            u_ = [uva[jb1], uva[jb], uvb[jb], uvb[jb1]]
            if jb1 == 0:
                u_[0] = (u_[0][0], circ(i, nb / m))
                u_[3] = (u_[3][0], circ(i, nb / m))
            face((S[k][jb1], S[k][jb], S[k + 1][jb], S[k + 1][jb1]), u_)
    # 撕裂面
    seq = [S[K], tip_in, core, mid]
    for k in range(len(seq) - 1):
        A_, B_ = seq[k], seq[k + 1]
        for jb in range(nb):
            jb1 = (jb + 1) % nb
            q = (A_[jb1], A_[jb], B_[jb], B_[jb1])
            face(q, [uv_in(np.array(mb.V[x])) for x in q])
    for jb in range(nb):
        jb1 = (jb + 1) % nb
        q = (mid[jb1], mid[jb], cen)
        face(q, [uv_in(np.array(mb.V[x])) for x in q])
    for v in ring0:
        mb.fib[v] = max(mb.fib[v], .35)
    return True


ns['BRK29'] = types.FunctionType(BRK29.__code__, ns, 'BRK29')
_a = "        # 撕裂的斷口：一圈參差往外伸（撕裂那側長）、收到中心一點；整片纖維色\n"
assert _tb18.count(_a) == 1, 'brk29 hook'
_tb29 = _tb18.replace(_a, "        if not col and BRK29(mb, rec, lv, e, i, C, T, rings, Ne, Be, rr, ns, sr_uv, circ, k_):   # v029：A 左端斷口本體\n            continue\n" + _a)
_w29 = ns['tube']
exec(compile(_tb29, HERE + '/game_dr09v29.py::tube', 'exec'), ns)
ns['_tube1'] = ns['tube']
ns['tube'] = _w29

# 四、參考比例研究版（DR9STUDY=1，另存檔，不覆蓋正式版）：只改主要枝幹（A、B、T1、R1、T2）的控制點高度，
#   z' = z + k·z²（越高的點抬越多，保留曲線形狀；低處、著地端幾乎不動），不是整個模型沿 Z 拉伸；其餘構件照常依接觸疊放。
#   正式版維持 ≤ 1.1 m 的規格。
if os.environ.get('DR9STUDY'):
    _k = float(os.environ.get('DR9STUDYK', '.19'))
    _T2c = [(.55, .12, .16), (.78, .07, .36), (1.02, .03, .56), (1.22, -.03, .66), (1.40, -.08, .72), (1.56, -.12, .78)]
    for _nm, _c in (('A', ns['A27']['c']), ('B', ns['B27']['c']), ('T1', ns['T1_27']['c']), ('R1', ns['R27']['c']), ('T2', _T2c)):
        LAYOUT.setdefault(_nm, {})['c'] = [(x, y, z + _k * z * z) for x, y, z in _c]
    ns['STUDY_H'] = 1.14
    ns['VER'] = 'v029_study'                         # 研究版：匯出檔、存檔名稱都另取，不覆蓋正式版
    print('STUDY k', _k)
