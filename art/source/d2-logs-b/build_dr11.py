# DR11 樹根翻起的倒樹根盤（高模）：大樹被風吹倒，整個根盤連泥帶石從地裡翻起，立成一面牆；後面接一小段倒下的樹幹（斷頭）；
#   根盤前面（原本樹站的地方）一個淺坑，坑邊翻起的土塊與幾顆滾落的石頭。
#   A：寬約 4 m、高約 3.5 m，幾乎直立（往後仰約 10°）；B：寬約 3 m、高約 2.6 m，往後仰約 30°，上半邊崩掉一塊、垂根多、上半長苔。
# 沿用 DR06 倒伏巨木的根盤零件（exec build_dr06.py）：泥丘 mud_plate、斷根 plate_roots／sinkers／dome_roots、卡在泥裡的石頭、根鬚、淺坑、斷口木刺。
# DR06 的根盤朝 -X（原本的根底）、樹幹沿 +X；這裡沿用同一座標：朝外的根面向 -X，正面審圖從 -X 看。z = 0 是地面。
# 參考：art/references/DR11/v001/（Codex 依 D2 設定圖 V4、V1、V5 畫）。
# 用法（背景，不要加 --factory-startup）：
#   blender -b --python build_dr11.py -- A quick <輸出資料夾> [鏡位,鏡位] [存檔.blend]
import bpy, math, os, sys, re
from mathutils import Matrix, Vector

_HERE11 = os.path.dirname(os.path.abspath(globals().get('__file__', 'D:/yun-jing-d2-logs/art/source/d2-logs-b/build_dr11.py')))
_p6 = os.path.join(_HERE11, 'build_dr06.py')
_nm11 = globals().get('__name__')
globals()['__name__'] = 'build_dr06_lib'            # 不要跑 DR06 的主程式
exec(compile(open(_p6, encoding='utf-8').read(), _p6, 'exec'), globals())
globals()['__name__'] = _nm11
__file__ = os.path.join(_HERE11, 'build_dr11.py')

# L 樹幹殘段長、R 樹幹半徑、RP 根盤半徑（泥丘寬約 1.7 RP，加上伸出去的斷根）、tilt 往後（+X）仰的角度
VARIANTS11 = {
    # 參考 A：一面薄圓盤（側面約 0.7 m 厚），正面粗根從中心放射、半埋在泥裡，邊緣只有幾根短斷根
    'A': dict(name='PlateA', L=2.4, R=.55, RP=2.00, seed=211, nroots=7, tilt=10.0,
              Tm=.30, Tp=.42, nface=0, nspike=0, nhair=70, nmain=1, spine_r=.34, nbranch=9, nsink=0, wide=1.10, nstone=5, lump=.45, groundroots=(), root_zmin=.45, stone_k=1.6, nfern_top=0, nmoss=0,
              stubs=(), fungi=((.45, -1.45, 3),), bend=.10),
    # 參考 B：寬約 3 m、高約 2.6 m，往後仰 30°，上半邊崩掉一塊，垂根多、上半長苔（做法照 A：一根粗主根往上分岔）
    # 第二版（使用者選「照參考」）：往前傾、下半一個拱形凹洞、上緣苔簷往前蓋、崩口移到右下
    # 第六版（灰模重塑，照參考 B 正面、側面）：不對稱弧形根板（左低、頂偏右隆起、右側崩口）、根面中央淺碗內凹、
    # 粗根從底部根頸往上、往兩側分流、前方往下挖的土坑（可嵌入場景的地形塊）、倒幹幹基後快降、尾段貼地、末端縱向劈裂
    'B': dict(name='PlateB', L=2.3, R=.40, RP=1.65, backflare=.30, topthin=.40, tflare=.45, trunk_base=.42, drop=.42, seed=223, nroots=0, tilt=-8.0, vz=.90,
              fanplate=True, curl=.75, bowl=(.62, .64, .60, .12), rootplan=True, exits=(-8, -113, 111, -73, -51, 61, -141), notches=(-30, -92, 22, 40, 84), dig=(-2.10, .95, 1.40, .55), pit_rim=.05, nclod=12,
              split_end=True, dents=True, trunk_x0=-.05, root_amp=0.0,
              Tm=1.15, Tp=.55, nface=0, nspike=0, nhair=110, nmain=0, spine_r=.30, nbranch=4, nsink=0, wide=1.26, nstone=0, lump=.22,
              groundroots=(), root_zmin=.40, stone_k=1.4, nfern_top=0, nmoss=0, nhang=95, ngrass=18, crumble=None, bite=.42, root_k=.85, over_k=.5, main_flat=.88, fit=True, collapse_face=.70, collar_k=(.66, .20), main_sink=.18, bridge_roots=(), cut_at_real=True, fit_bias={'M4': -.14, 'M2': -.12}, dive_skip=('RootM1',), fork_soft=('M2',), collapseclods=(('S7', .6, .20), ('M3', .70, .22), ('M3', .92, .15), ('S5', .85, .13), ('T2', .9, .10), ('M3', .50, .17), ('S1', .80, .12)), gaps=True, collapse=((102, 34, .50, .32), (158, 13, .52, .26), (-122, 20, .30, .12)), side_k=(.62, -.35, 1.10), bundles=True, trunk_cut=1.0, cap_k=1.5,
              stubs=(), fungi=(), bend=.06),
}
VARIANTS.update(VARIANTS11)


def plate_geom(V):
    """DR11：根盤比 DR06 薄（Tm／Tp 由變體給），其餘照 DR06。"""
    RP = V['RP']
    k = RP / 2.25
    return dict(k=k, xp=-.20 * k, zc=RP * .78, Re=RP * .86, Tm=V.get('Tm', .56) * k, Tp=V.get('Tp', .72) * k)


def face_prof(q):
    """DR11：朝外那面（原本的根底）幾乎是平的（參考圖正面像一面牆），中心只微凹，外圈一道唇再繞回邊緣。"""
    if q < .8:
        return .82 + .18 * _sm(q / .8)
    return math.sqrt(max(0.0, 1 - ((q - .8) / .2) ** 2))


def trunk_z(V, x):
    """DR11：樹幹從根盤中心高度出來，往後斜躺到地上（仰角已扣掉，轉完 tilt 後末端剛好貼地、陷進一點）。"""
    L, R = V['L'], V['R']
    r = trunk_r(V, x)
    g = plate_geom(V)
    th = math.radians(V.get('tilt', 0.0))
    if V.get('drop'):                                    # B 第六版：幹基後方很快降到貼地，尾段平平延伸
        rest = (r * .96 - .14 * R + (x - g['xp']) * math.sin(th)) / math.cos(th)
    else:
        rest = (r * .96 - .14 * R + (L - g['xp']) * math.sin(th)) / math.cos(th)
    base = g['zc'] * V.get('trunk_base', .62)
    u = _sm(max(0.0, x) / (L * V.get('drop', 1.0)))
    return base * (1 - u) + rest * u


# DR06 的 plate_roots／sinkers 原文照用，只換幾個數字（DR06 檔案不動）：外伸斷根少、短；正面放射根粗、多、浮在泥面上
_src6 = open(_p6, encoding='utf-8').read()


def _patched(name, reps):
    i0 = _src6.index(f'\ndef {name}(')
    i1 = _src6.index('\ndef ', i0 + 5)
    s = _src6[i0:i1]
    for a, b in reps:
        assert s.count(a) == 1, (name, a)
        s = s.replace(a, b)
    exec(compile(s, _p6 + f':{name}(DR11)', 'exec'), globals())


_patched('plate_roots', (
    ("spike = k % 3 != 2 and math.sin(ph) > -.25", "spike = k % 4 == 0 and math.sin(ph) > -.25"),
    ("R.uniform(1.15, 1.55) * (1 - .24 * math.cos(ph) ** 2)", "R.uniform(1.04, 1.20) * (1 - .10 * math.cos(ph) ** 2)"),
    ("for k, sg in enumerate((-1, 1, -1, 1)):", "for k, sg in enumerate(V.get('groundroots', (-1, 1, -1, 1))):"),          # 參考 A：底邊坐在坑裡，兩旁沒有貼地往外爬的長根
    ("if min(p.z for p, _ in P[2:]) < -.2:", "if min(p.z for p, _ in P[2:]) < V.get('root_zmin', -.2):"),          # 低處往兩旁平伸的根（會躺在地上）不做
))
_patched('sinkers', (
    ("nf = 11 if big else 9", "nf = V.get('nface', 11 if big else 9)"),
    ("r = g['k'] * (.045 + .17 * u * u)", "r = g['k'] * (.09 + .13 * u)"),
    ("lift0 = Rw.uniform(-.15, .40)", "lift0 = Rw.uniform(.05, .45)"),
    ("head += .30 * dh + Rw.gauss(0, .42)", "head += .50 * dh + Rw.gauss(0, .22)"),          # 參考：從中心清楚往外放射，只小幅彎

    ("ns = 15 if big else 11", "ns = V.get('nspike', 15 if big else 11)"),
    ("for k in range(5 if big else 4):", "for k in range(V.get('nsink', 5 if big else 4)):"),
))
_patched('mud_pt', (          # 根盤橫向加寬（參考 A 寬 4 m、高 3.5 m，不是正圓）
    ("p = Vector((g['xp'] + xx, d.y * Re, g['zc'] + d.z * Re))", "p = Vector((g['xp'] + xx, d.y * Re * V.get('wide', 1.0) * (1 - V.get('flare', 0.0) * d.z), g['zc'] + d.z * Re))"),
    ("xx = -g['Tm'] * face_prof(math.sqrt(max(0.0, 1 - d.x * d.x)))", "xx = -g['Tm'] * face_prof11(V, d)"),
    ("xx = g['Tp'] * d.x * (1 + .15 * fb(d * 2.6, 1.0, 3))", "xx = g['Tp'] * d.x * (1 + .15 * fb(d * 2.6, 1.0, 3)) * back11(V, d)"),
))


def back11(V, d):
    """背面（+X）的厚度倍率：B 上薄下厚——下半往樹幹那側鼓出來接樹幹（側面像一道浪：根盤頂往下流到倒樹幹），上半變薄。"""
    bf, tt = V.get('backflare', 0.0), V.get('topthin', 0.0)
    return (1 + bf * _sm((.3 - d.z) / 1.1)) * (1 - tt * _sm(d.z / .8))


def face_prof11(V, d):
    """根面剖面（d 是 -X 那半球的方向）：A 照 face_prof；B（cave）下半凹進一個拱形的洞、上緣往前伸出一道苔簷（參考 B 正面、側面）。"""
    q = math.sqrt(max(0.0, 1 - d.x * d.x))
    base = face_prof(q)
    cv = V.get('cave')
    if not cv:
        return base
    depth, wy, ztop, eave = cv
    yy, zz = d.y, d.z                                  # 根面圓盤上的位置（半徑 q）
    # 拱形洞：寬 ±wy、從底到 ztop，頂上是半圓拱；邊緣 0.15 內漸變
    top = ztop - (1 - math.sqrt(max(0.0, 1 - (yy / wy) ** 2))) * .35 if abs(yy) < wy else -9
    inside = min(_sm((wy - abs(yy)) / .15), _sm((top - zz) / .15))
    n = 1 + .25 * fb(Vector((yy * 3.0, zz * 3.0, 6.6)), 1.0, 2)
    base = base * (1 - depth * inside * n)
    # 苔簷：上緣（zz > ztop 以上）往前伸
    base *= 1 + eave * _sm((zz - (ztop + .05)) / .45) * (1 - .4 * abs(yy))
    return max(base, .04)
_patched('mud_plate', (          # 根面的土團起伏小一點（不要和根搶輪廓）
    ("v.co = v.co + d * (.045 * plate_geom(V)['k']", "v.co = v.co + d * (.045 * V.get('lump', 1.0) * plate_geom(V)['k']"),
))
_patched('pit', (          # 坑邊靠根盤那側的土壓低（DR06 那圈高到把根面下半擋住）
    ("rim = (.20 + .30 * near) * g['k'] * math.exp(-((rho - .95) / .17) ** 2)",
     "rim = V.get('pit_rim', .46) * (1 + .25 * near) * g['k'] * math.exp(-((rho - .97) / (.08 if rho < .97 else .32)) ** 2)"),
    ("z = .012 + rim + .035 * fb((x * 2.5, y * 2.5, 1.1), 1.0, 3) - .12 * _sm((rho - 1.08) / .2)",
     "z = (-.02 + rim + .025 * fb((x * 2.5, y * 2.5, 1.1), 1.0, 3)) * (1 - _sm((rho - 1.12) / .33)) - .03 * _sm((rho - 1.35) / .2)"),
    ("rho = 1.3 * i / nr", "rho = 1.55 * i / nr"),
    ("cv = bm.verts.new((cx, 0, .012))", "cv = bm.verts.new((cx, 0, -.02))"),
))
_patched('stones', (
    ("s = g['k'] * R.uniform(.10, .30)", "s = g['k'] * R.uniform(.10, .30) * V.get('stone_k', 1.0)"),
    ("q.co = P - N * (.40 * s) + pp * s", "q.co = P - N * (.25 * s) + pp * s"),          # 露出多一點（參考：石頭卡在泥面上很顯眼）
    ("for pl in (Vector((.6, .3, .74)), Vector((-.5, .7, -.5))):", "for pl in (Vector((.6, .3, .74)), Vector((-.5, .7, -.5)), Vector((.1, -.8, .4)), Vector((-.7, -.2, .6)), Vector((.8, -.3, -.4))):"),
    ("if dd > .62:", "if dd > .50:"),          # 參考：石頭有稜角（多幾個切面），不是蛋
))
_patched('build', (          # 樹幹斷口：一小束參差木刺（DR06 的長樹幹斷口是一大把，放在短殘段上像掃把）
    ("caps = [(trunk, tp, 1.7, 48, 40 if V['id'] == 'B' else 30, (.30, .95))]", "caps = [] if V.get('split_end') else [(trunk, tp, .9, 22, 8, (.18, .55))]"),
    ("moss_bias=trunk_moss, cap_end=bool(col))", "moss_bias=trunk_moss, cap_end=bool(col) or bool(V.get('split_end')))"),
    ("splay=.40 if o is trunk else .34", "splay=.16 if o is trunk else .30"),
    ("root_hairs(V, coll, R, mat, 230 if V['id'] == 'B' else 170", "root_hairs(V, coll, R, mat, V.get('nhair', 70)"),
    ("stones(V, coll, R, 9 if V['id'] == 'B' else 7,", "stones(V, coll, R, V.get('nstone', 7),"),
))


def trunk_r(V, x):
    """DR11：樹幹根部的喇叭口大小由變體給（B 的根部大幅張開，接上根盤下半）。"""
    L, R = V['L'], V['R']
    t = max(0.0, x) / L
    return R * (1 + V.get('tflare', .38) * math.exp(-max(0.0, x) / (.04 * L + .45))) * (1 - .15 * t)


def trunk_pts(V):
    """DR11：只剩根盤後面一小段樹幹（斷頭），不用 DR06 的長樹幹取樣點。"""
    L, R = V['L'], V['R']
    Lt = L - V.get('trunk_cut', 0.0)                      # B：完整木幹到 Lt 為止，之後是木束
    xs = ([-.6, -.2] if V.get('trunk_x0') is None else [V['trunk_x0']]) + [.25, .7] + [x for x in (1.2, 1.7, 2.2) if x < Lt - .25] + [Lt]     # B：起點收在根盤裡（淺碗底不能被幹頭穿出）
    pts = []
    for x in xs:
        t = max(0.0, x) / L
        y = V['bend'] * R * math.sin(t * 2.6 + V['seed'] * .37) * t
        pts.append((x, y, trunk_z(V, x), trunk_r(V, x), .96))
    return pts


# ---------------- B 第六版：灰模重塑 ----------------
GREY = False          # 灰模模式：不做苔、蕨、細垂根、地面裝飾，只留根盤、粗根、倒幹、地形


def _abump(a, c, w):
    d = (a - c + math.pi) % (2 * math.pi) - math.pi
    return math.exp(-(d / w) ** 2)


OUT_B = ((-180, 1.24), (-132, 1.18), (-100, .92), (-66, .80), (-30, .90), (0, 1.06), (32, 1.18), (64, 1.08), (92, .94), (116, .84), (144, 1.10), (180, 1.24))
# 方位角（度，從頂往右為正）→ 輪廓倍率：下緣兩角貼地撐開（半圓頂）、左上壓低、頂偏右最高、右側中段崩口另外咬


def outline_b11(V, a):
    """B 根板輪廓（相對 Re 的倍率）；a 從 +Z 往 -Y 量（正面看往右為正）。
    左邊低（左上壓下去）、頂偏右隆起、下半兩側內收、底部往下伸進坑；外緣再加參差。"""
    d = (math.degrees(a) + 180) % 360 - 180
    K = OUT_B[:-1]                                      # 週期：-180 與 180 是同一點
    n = len(K)
    for i in range(n):
        a0 = K[i][0]
        a1 = K[(i + 1) % n][0] + (360 if i == n - 1 else 0)
        if a0 <= d <= a1 or (i == n - 1 and d >= a0):
            t = (d - a0) / (a1 - a0)
            p0, p1, p2, p3 = K[(i - 1) % n][1], K[i][1], K[(i + 1) % n][1], K[(i + 2) % n][1]
            return .5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
    return K[0][1] * (1 + .055 * fb(Vector((math.cos(a) * 1.6, math.sin(a) * 1.6, 4.4)), 1.0, 3))


def mud_pt_b11(V, d, seed):
    """B 根板表面：d 是單位方向（-X 那半是根面）。
    正面：中央淺碗（不貫穿）、外圈一道根脊、底部根頸最厚、上緣往前覆出；背面：下厚（土＋接樹幹）上薄；頂緣整片往前彎。"""
    g = plate_geom(V)
    k, Re0, zc = g['k'], g['Re'], g['zc']
    d = Vector(d).normalized()
    a = math.atan2(-d.y, d.z)
    q = math.sqrt(max(0.0, 1 - d.x * d.x))
    lobe = sum(math.exp(-((((a - math.radians(e)) + math.pi) % (2 * math.pi) - math.pi) / .13) ** 2) for e in V.get('exits', ()))
    notch = sum(math.exp(-((((a - math.radians(e)) + math.pi) % (2 * math.pi) - math.pi) / .10) ** 2) for e in V.get('notches', ()))
    lobe, notch = min(1.0, lobe), min(1.0, notch) * (1 + .5 * fb(Vector((a * 2.0, 3.3, 1.1)), 1.0, 2))
    edge = _sm((q - .70) / .30)
    wf = _sm((-d.x + .10) / .50)                         # 只在正面那半：板緣凸凹不會繞到側面變成一圈圈橫帶
    Re = Re0 * outline_b11(V, a) * (1 + .035 * fb(d * 6.0 + Vector((0, 0, seed)), 1.0, 2) * _sm((q - .8) / .2)) * (1 + wf * (.07 * lobe - .10 * notch))
    thick = 1 + edge * wf * (.35 * lobe - .40 * notch)    # 主根出板緣處厚、根與根之間的缺口薄
    cz = 0.0
    if V.get('collapse') and not _NOGAP11[0]:            # 崩落區：從外輪廓往內切（前深後淺，全厚度都切，剪影真的斷開；中央碗後壁不動）
        for c_, hw, dep_f, dep_b in V['collapse']:
            da = math.degrees((a - math.radians(c_) + math.pi) % (2 * math.pi) - math.pi)
            hwe = hw * (1 + .30 * fb(d * 1.8 + Vector((c_ * .01, 2.2, 0)), 1.0, 2))     # 缺口邊不規則（3D 雜訊，不只隨方位角變）
            w_ = _sm((hwe - abs(da)) / (.40 * hw))
            dep = dep_b + (dep_f - dep_b) * _sm((.30 - d.x) / .9)
            dep *= 1 + .25 * fb(d * 3.2 + Vector((5.1, c_ * .02, 0)), 1.0, 2)
            cz = max(cz, w_ * dep)
        Re *= 1 - cz * _sm((q - .25) / .5)
    if V.get('gaps') and not _NOGAP11[0]:               # 右側、下緣邊框打斷：正面根脊局部退縮（露出跨過去的粗根）
        gp = sum(dp * math.exp(-(((d.y - gy) / ry) ** 2 + ((d.z - gz) / rz) ** 2)) for gy, gz, ry, rz, dp in GAPS_B)
        gp = min(.85, gp) * wf
        Re *= 1 - .20 * gp * edge
    else:
        gp = 0.0
    wd = V.get('wide', 1.0)
    py, pz = d.y * Re * wd, zc + d.z * Re * V.get('vz', 1.0)
    zn = d.z * Re / Re0
    yd, zd = d.y, d.z
    if d.x < 0:
        prof = 1.0 if q < .66 else math.sqrt(max(0.0, 1 - ((q - .66) / .34) ** 2))
        F = g['Tm'] * (.80 - .30 * _sm((zn + .1) / 1.0)) * prof                       # 上半薄
        bw = V.get('bowl', (.62, .64, .60, .12))                                    # 深度、半寬、半高、中心高
        e = math.hypot((yd + .04) / bw[1], (zd - bw[3]) / bw[2])
        inside = _sm((1 - e) / .45)
        F *= 1 - bw[0] * inside * (1 + .22 * fb(Vector((yd * 2.6, zd * 2.6, 8.8)), 1.0, 3))     # 淺碗，後壁不規則
        F *= 1 + .12 * math.exp(-((yd / .38) ** 2 + ((zd + .82) / .30) ** 2))       # 根頸：底部中央最厚
        F *= 1 + .16 * (math.exp(-((yd - .66) / .13) ** 2) + math.exp(-((yd + .70) / .13) ** 2)) * _sm((.75 - abs(zd - .05)) / .4)   # 兩側根脊
        F *= 1 + V.get('side_k', (0, 0, .45))[2] * _sm((zd - .45) / .35)            # 上緣往前覆出
        sv = zd * 3.0 + .65 * fb(Vector((yd * 1.4, zd * .8, 3.1)), 1.0, 2) + .6 * yd * yd + .35 * yd          # 內壁：傾斜、斷續的土層面（大中尺度）
        ledge = _sm((sv - math.floor(sv) - .55) / .30) - .5
        F *= 1 + inside * (.28 * ledge + .16 * fb(Vector((yd * 1.7, zd * 1.7, 5.5)), 1.0, 2))
        xx = -F * thick * (1 - gp) * (1 - V.get('collapse_face', 1.3) * cz) * (1 + .18 * fb(d * 2.6 + Vector((0, seed, 0)), 1.0, 3))
    else:
        tt_ = V['side_k'][1] if V.get('side_k') else V.get('topthin', .55)
        Bk = g['Tp'] * (1 + V.get('backflare', .9) * _sm((-.05 - zn) / .8)) * (1 - tt_ * _sm((zn - .1) / .7))     # 中上段：背面上半少收一點，撐住上方根板
        xx = Bk * d.x * thick * (1 + .12 * fb(d * 2.6, 1.0, 3))
    xx -= V.get('curl', .55) * V.get('side_k', (1.0,))[0] * k * _sm((zn + .1) / 1.1) ** 2.0                      # 頂緣往前（-X）彎覆
    p = Vector((g['xp'] + xx, py, pz))
    p += d * (.05 * k * fb(p * 3.0, 1.0, 3) + .025 * k * fb(p * 8.0, 1.0, 2) + .010 * k * fb(p * 19.0, 1.0, 2))
    if p.z < -.48:
        p.z = -.48 + (p.z + .48) * .1
    return p


_ROOTPTS = {}          # 粗根中心線（給崩落區土塊找支撐）
_ROOTINFO = {}         # 物件名 → 重建資料（中心線、埋深、外伸斷根從第幾點開始、tube 參數）
_NOGAP11 = [False]          # 粗根求泥面時用「沒打缺口」的面：缺口裡的根才會跨過去、露出來
GAPS_B = (                  # 正面位置 (d.y, d.z)（-y 是畫面右）、半寬、半高、退縮量
    (-.84, -.05, .20, .28, .85), (-.66, -.52, .20, .18, .85), (-.22, -.88, .24, .14, .80), (.36, -.86, .20, .13, .70), (-.80, .42, .14, .16, .55))


_mud_pt_a11 = mud_pt


def real_off11(V, y, z):
    """(y, z) 離真正泥盤外輪廓多遠（公尺；0 = 在泥盤上）。和 face_x 同一套反求，只多回傳殘差。"""
    g = plate_geom(V)
    d = Vector((-.8, y / g['Re'], (z - g['zc']) / g['Re']))
    p = None
    for _ in range(10):
        q = Vector((0, d.y, d.z))
        if q.length > .985:
            q *= .985 / q.length
        d = Vector((-math.sqrt(max(.0003, 1 - q.length_squared)), q.y, q.z))
        p = mud_pt(V, d, V['seed'])
        d.y += (y - p.y) / g['Re']
        d.z += (z - p.z) / g['Re']
    return math.hypot(y - p.y, z - p.z)


def mud_pt(V, d, seed):
    if V.get('fanplate'):
        return mud_pt_b11(V, d, seed)
    return _mud_pt_a11(V, d, seed)


def pit_frame11(V):
    """坑的中心 x、x 向半徑、y 向半徑。"""
    g = plate_geom(V)
    dg = V.get('dig')
    if dg:
        return g['xp'] + dg[0] * g['k'], dg[1], dg[2]
    RP = V['RP']
    return g['xp'] - g['Tm'] - RP * .42, RP * .52, RP * .82


PIT_RMAX = 1.85


def _pit_wob(t):
    return 1 + .18 * fb((math.cos(t) * 1.4, math.sin(t) * 1.4, 7.7), 1.0, 3) + .07 * fb((math.cos(t) * 4.0, math.sin(t) * 4.0, 2.9), 1.0, 2)


PIT_SLUMP = (2.35, 3.6, 5.3)          # 坑緣塌落的方位（弧度；0 朝根盤）


def _pit_slump(t):
    return min(1.0, sum(math.exp(-((((t - c) + math.pi) % (2 * math.pi) - math.pi) / .38) ** 2) for c in PIT_SLUMP))


def _pit_z(V, rho, t, x, y):
    """往下挖的坑：坑底平（-D）、坑壁三道斷裂土層台階（台階位置隨方位擺動）、坑口一圈翻起的薄唇；外圈回到地面 0。"""
    D = V['dig'][3]
    rr = rho / _pit_wob(t)
    n1 = fb((x * 2.2, y * 2.2, 1.1), 1.0, 3)
    S = _pit_slump(t)
    nst = 2.2 + .9 * fb((math.cos(t) * 1.7, math.sin(t) * 1.7, 6.1), 1.0, 2)       # 台階數隨方位變
    if rr < 1.0:
        u = _sm((rr - .60) / .40)
        sv = u * nst + .45 * fb((math.cos(t) * 2, math.sin(t) * 2, 3.3), 1.0, 2)
        st = max(0.0, min(1.0, (math.floor(sv) + _sm((sv % 1 - .55) / .45)) / nst))
        zt = -D * (1 - (.40 * u + .60 * st))
        ug = _sm((rr - .30) / .75)                       # 塌落處：一道緩的崩土坡，坑口低
        zs = -D * (1 - ug) - .06 * ug
        z = zt * (1 - S) + zs * S + .035 * n1 * (1 - .5 * u)
    else:
        lip = .10 * (.35 + .65 * abs(fb((math.cos(t) * 3.0, math.sin(t) * 3.0, 4.4), 1.0, 2)) * 1.6)
        z = (lip * math.exp(-((rr - 1.05) / .08) ** 2) * (1 + .6 * n1)) * (1 - S) - .06 * S * math.exp(-((rr - 1.0) / .15) ** 2) + .02 * n1
    return z * (1 - _sm((rho - 1.40) / .40))


def pit_height11(V, x, y):
    """(x, y) 處地形高（沒有挖坑的變體＝0）。"""
    if not V.get('dig'):
        return 0.0
    cx, ax_, ay = pit_frame11(V)
    rho = math.hypot((x - cx) / ax_, y / ay)
    if rho >= PIT_RMAX:
        return 0.0
    t = math.atan2(y / ay, (x - cx) / ax_)
    return _pit_z(V, rho, t, x, y)


def pit_b11(V, coll, R, nr=16, na=72):
    """B：根盤前方往下挖的拔根坑（地形塊）：外圈剛好回到地面 0，可直接嵌進場景地形（場景地面在這塊範圍挖洞）。
    坑壁斷裂土層、坑底與坑緣幾顆石頭、坑壁伸出幾截殘根（靠根盤那側多）。"""
    import bmesh
    g = plate_geom(V)
    k = g['k']
    cx, ax_, ay = pit_frame11(V)
    D = V['dig'][3]
    nr, na = nr * 3, int(na * 4 / 3)
    bm = bmesh.new()
    rows = []
    for i in range(1, nr + 1):
        rho = PIT_RMAX * i / nr
        row = []
        for j in range(na):
            t = 2 * math.pi * j / na
            x, y = cx + math.cos(t) * ax_ * rho, math.sin(t) * ay * rho
            row.append(bm.verts.new((x, y, _pit_z(V, rho, t, x, y))))
        rows.append(row)
    cv = bm.verts.new((cx, 0, _pit_z(V, 0.0, 0.0, cx, 0.0)))
    for i in range(nr - 1):
        for j in range(na):
            j2 = (j + 1) % na
            bm.faces.new((rows[i][j], rows[i][j2], rows[i + 1][j2], rows[i + 1][j]))
    for j in range(na):
        bm.faces.new((cv, rows[0][(j + 1) % na], rows[0][j]))
    bm.normal_update()
    for f in bm.faces:
        if f.normal.z < 0:
            f.normal_flip()
        f.smooth = True
    me = bpy.data.meshes.new('DR11_Pit')
    bm.to_mesh(me)
    bm.free()
    mm = []
    for v in me.vertices:
        rho = math.hypot((v.co.x - cx) / ax_, v.co.y / ay)
        mm.append(max(0.0, min(1.0, (rho - 1.10) * 3 + .4 * fb(v.co * 2, 1.0, 2))))
    at = me.attributes.new('MudMoss', 'FLOAT', 'POINT')
    at.data.foreach_set('value', np.array(mm, np.float32))
    me.materials.append(mud_material())
    ob = _obj('Pit', me, coll)
    low = nr < 40
    # 石頭：坑底兩三顆、坑口一顆
    sb = bmesh.new()
    for i in range(V.get('pit_stones', 4)):
        if i < 3:
            t, rr = R.uniform(.55, 1.45) * math.pi + (0 if i else .3), R.uniform(.15, .55)
        else:
            t, rr = R.uniform(.7, 1.3) * math.pi, 1.06
        x, y = cx + math.cos(t) * ax_ * rr, math.sin(t) * ay * rr
        z = pit_height11(V, x, y)
        sz = k * R.uniform(.16, .26) * (.7 if i == 3 else 1.0)
        b2 = bmesh.new()
        bmesh.ops.create_icosphere(b2, subdivisions=1 if low else 3, radius=1.0)
        sc = Vector((R.uniform(.8, 1.1), R.uniform(.8, 1.2), R.uniform(.55, .75)))
        off = Vector((R.uniform(-9, 9), R.uniform(-9, 9), R.uniform(-9, 9)))
        for qv in b2.verts:
            d2 = qv.co.copy()
            rr2 = 1 + .22 * fb(d2 * 1.3 + off, 1.0, 2) + .05 * fb(d2 * 5 + off, 1.0, 2)
            pp = Vector((d2.x * sc.x, d2.y * sc.y, d2.z * sc.z)) * rr2
            for pl in (Vector((.6, .3, .74)), Vector((-.5, .7, -.5)), Vector((.1, -.8, .4)), Vector((-.7, -.2, .6))):
                pl.normalize()
                dd = pp.dot(pl)
                if dd > .50:
                    pp -= pl * (dd - .50) * .85
            qv.co = Vector((x, y, z + sz * .42)) + pp * sz
        me2 = bpy.data.meshes.new('tmp11')
        b2.to_mesh(me2)
        b2.free()
        sb.from_mesh(me2)
        bpy.data.meshes.remove(me2)
    me3 = bpy.data.meshes.new('DR11_StonesPit')
    sb.to_mesh(me3)
    sb.free()
    for p_ in me3.polygons:
        p_.use_smooth = True
    me3.materials.append(stone_material())
    _obj('StonesPit', me3, coll)
    # 殘根：從坑壁伸出來、往坑中央略往下（靠根盤那側多）
    obs = list(coll.objects)
    tr = next((o for o in obs if o.name.split('.')[0].endswith('Trunk')), None)
    if tr is not None:
        mat = tr.data.materials[0]
        for i in range(V.get('pit_roots', 9)):
            t = R.uniform(-.45, .45) * math.pi if i < 4 else R.uniform(.45, 1.55) * math.pi
            rr = R.uniform(.82, 1.0)
            x, y = cx + math.cos(t) * ax_ * rr, math.sin(t) * ay * rr
            z = pit_height11(V, x, y)
            dv = Vector((cx - x, -y, 0)).normalized()
            dv.z = -R.uniform(.0, .30)
            dv.normalize()
            ln, r0 = R.uniform(.15, .40), k * R.uniform(.035, .075)
            p0 = Vector((x, y, z + r0 * .4))
            pts = [tuple(p0 - dv * .10) + (r0 * 1.1, 1.0), tuple(p0) + (r0, 1.0),
                   tuple(p0 + dv * ln * .5 + Vector((0, 0, -.02))) + (r0 * .8, 1.0), tuple(p0 + dv * ln + Vector((0, 0, -.05))) + (r0 * .6, 1.0)]
            o = tube('RootsPit', pts, V['seed'] + 1500 + i, rib=.18, twist=.10, collection=coll, moss_bias=-.6, cap_end=True)
            o.data.materials.append(mat)
    return ob


_pit_a11 = pit


def pit(V, coll, R, nr=16, na=72):
    if V.get('dig'):
        return pit_b11(V, coll, R, nr, na)
    return _pit_a11(V, coll, R, nr, na)


def collar11(V, coll, low, y0, z0):
    """根頸：根面底部中央一團扁的根結，粗根從這裡往上、往兩側分出去（半埋在泥裡）。"""
    import bmesh
    g = plate_geom(V)
    k = g['k']
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2 if low else 4, radius=1.0)
    x0 = face_x(V, y0, z0, V['seed'])
    for v in bm.verts:
        d = v.co.copy()
        lob = 1 + .25 * fb(d * 1.6 + Vector((V['seed'], 0, 0)), 1.0, 3) + .08 * fb(d * 4.5, 1.0, 2)
        sk = V.get('collar_k', (1.0, 0.0))
        v.co = Vector((x0 + (.04 + sk[1]) * k + d.x * .26 * k * lob * sk[0], y0 + d.y * .48 * k * lob * sk[0], z0 + d.z * .36 * k * lob * sk[0]))
    me = bpy.data.meshes.new('DR11_Crown')
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    obs = coll if isinstance(coll, list) else list(coll.objects)
    tr = next(o for o in obs if o.name.split('.')[0].endswith('Trunk'))
    me.materials.append(tr.data.materials[0])
    ob = bpy.data.objects.new(tr.name.split('.')[0].replace('Trunk', 'Crown'), me)
    tr.users_collection[0].objects.link(ob)
    if isinstance(coll, list):
        coll.append(ob)
    return ob


def fan_roots11(V, coll, low):
    """B：少量清楚的粗根，從底部根頸往上、往兩側扇形分流；貼著根面（含淺碗）走、半埋，
    中途分一兩叉；走到板緣（含右側崩口）後伸出不等長的斷端。"""
    g = plate_geom(V)
    k, Re0, zc = g['k'], g['Re'], g['zc']
    wd = V.get('wide', 1.0)
    R = random.Random(V['seed'] + 1201)
    obs = coll if isinstance(coll, list) else list(coll.objects)
    tr = next(o for o in obs if o.name.split('.')[0].endswith('Trunk'))
    mat, col_ = tr.data.materials[0], tr.users_collection[0]
    made = []
    cr = V.get('crumble')
    ang0, ang1 = [math.radians(x) for x in cr] if cr else (9.0, 9.0)
    bite = V.get('bite', .4)

    def rim(y, z):
        vz = V.get('vz', 1.0)                            # 根板垂直方向有壓扁
        a = math.atan2(-y / wd, (z - zc) / vz)
        lim = outline_b11(V, a)
        if cr and ang0 - .15 < a < ang1 + .15:
            lim *= 1 - bite * min(_sm((a - ang0 + .15) / .3), _sm((ang1 + .15 - a) / .3))
        return math.hypot(y / wd, (z - zc) / vz) / (Re0 * lim)

    def mk(name, p2, rs, emb, seed_, over):
        pts = [(face_x(V, y, z, V['seed']) - rr * emb, y, z, rr, 1.0) for (y, z), rr in zip(p2, rs)]
        if over > 0 and len(pts) >= 2:                   # 斷端：順著最後方向伸出板緣，略往前、往下垂
            x1, y1, z1, r1, _ = pts[-1]
            x0, y0, z0, _, _ = pts[-2]
            dv = Vector((x1 - x0, y1 - y0, z1 - z0)).normalized()
            for i in range(1, 4):
                t = over * i / 3
                pts.append((x1 + dv.x * t - .15 * t, y1 + dv.y * t, z1 + dv.z * t - .9 * t * t, r1 * (1 - .12 * i / 3), 1.0))
        if len(pts) < 3:
            return None
        o = tube(name, pts, seed_, rib=.20, twist=.10, collection=col_, moss_bias=-.6, cap_end=True)
        o.data.materials.append(mat)
        made.append(o)
        return pts

    def walk(p0, a0, a1, r0, r1, lim, seed_):
        Rw = random.Random(seed_)
        st = (.10 if low else .06) * k * 1.4
        p = Vector(p0)
        ps = [(p.x, p.y)]
        ph = Rw.uniform(0, 6.3)
        for i in range(140):
            t = min(1.0, i * st / (Re0 * 1.2))
            a = a0 + (a1 - a0) * _sm(t) + .13 * math.sin(i * .38 + ph)
            p = p + Vector((-math.sin(a), math.cos(a))) * st
            if rim(p.x, p.y) > lim:
                break
            ps.append((p.x, p.y))
        n = len(ps)
        rs = [r0 + (r1 - r0) * (i / max(1, n - 1)) ** 1.4 for i in range(n)]
        return ps, rs

    zcol = zc - .74 * Re0
    collar11(V, coll, low, .10 * Re0, zcol + .04 * Re0)
    mains = V.get('fan', (-132, -84, -38, 6, 48, 96))
    for j, ae in enumerate(mains):
        ae = math.radians(ae + R.uniform(-5, 5))
        a_s = ae * .45
        p0 = (.10 * Re0 - math.sin(a_s) * .22 * Re0, zcol + R.uniform(.0, .10) * Re0)
        r0 = k * R.uniform(.25, .31)
        up = abs(ae) < math.radians(55)
        ps, rs = walk(p0, a_s, ae, r0, k * .09, .90 if up else .96, V['seed'] + 1210 + 31 * j)
        if len(ps) < 4:
            continue
        rs[0] *= 1.25
        mk(f'FanRoot{j}', ps, rs, .50, V['seed'] + 1220 + 31 * j, 0 if up else R.uniform(.05, .32))
        nb = 1 if j in (0, len(mains) - 1) else 2
        for b in range(nb):
            i = max(1, min(len(ps) - 3, int(len(ps) * R.uniform(.30, .65))))
            dth = math.atan2(-(ps[i + 1][0] - ps[i - 1][0]), ps[i + 1][1] - ps[i - 1][1])
            side = (1 if ae >= 0 else -1) * (1 if b == 0 else -1)
            ab = dth + side * R.uniform(.35, .60)
            ps2, rs2 = walk(ps[i], ab, ab + side * .25, rs[i] * R.uniform(.62, .76), k * .06, .96, V['seed'] + 1300 + 31 * j + 7 * b)
            if len(ps2) >= 3:
                rs2[0] *= 1.2
                mk(f'FanRoot{j}k{b}', ps2, rs2, .55, V['seed'] + 1310 + 31 * j + 7 * b, R.uniform(.04, .22) if (R.random() < .7 and not up) else 0)
    # 根頸往下兩條鑽進坑底
    for j, ae in enumerate(V.get('fanfoot', ())):
        ae = math.radians(ae)
        ps, rs = walk((0.0, zcol), ae * .8, ae, k * .17, k * .09, .99, V['seed'] + 1400 + j)
        if len(ps) >= 3:
            mk(f'FanFoot{j}', ps, rs, .45, V['seed'] + 1410 + j, .25)
    print('DR11_FANROOTS', len(made))
    if isinstance(coll, list):
        coll.extend(made)
    return made


def root_section11(o, pts, seed, flat=1.0, soil=None):
    """粗根截面：不規則橢圓、帶兩三道稜；朝土那側壓扁，外露那側飽滿。soil：每個中心線點的朝土方向（預設 +X）。"""
    rings, _ = resample(pts, .03)
    C = np.array([tuple(p) for p, *_ in rings])
    P0 = np.array([(q[0], q[1], q[2]) for q in pts])
    Rr = np.array([r for _, r, *_ in rings])
    R = random.Random(seed)
    ph = R.uniform(0, 6.3)
    for v in o.data.vertices:
        c = Vector(v.co)
        i = int(np.argmin(((C - np.array(c)) ** 2).sum(1)))
        best = None
        for j0, j1 in ((max(0, i - 1), i), (i, min(len(C) - 1, i + 1))):
            a_, b_ = Vector(C[j0]), Vector(C[j1])
            ab = b_ - a_
            t = 0.0 if ab.length_squared < 1e-12 else max(0.0, min(1.0, (c - a_).dot(ab) / ab.length_squared))
            q_ = a_ + ab * t
            if best is None or (c - q_).length < (c - best[0]).length:
                best = (q_, j0 + t)
        ctr, fi = best
        dv = c - ctr
        if dv.length < 1e-6:
            continue
        nrm = dv.normalized()
        if soil is None:
            sd_ = Vector((1, 0, 0))
        else:
            sd_ = soil[int(np.argmin(((P0 - np.array(ctr)) ** 2).sum(1)))]
        a_s = nrm.dot(sd_)
        sq = 1 - .38 * _sm(a_s / .7)                         # 貼土那側漸漸壓扁（平滑，不用門檻：門檻遇到扭轉的頂點列會變斜向鋸齒）
        th = math.atan2(nrm.z, nrm.y)
        rid = 1 + .10 * math.cos(3 * th + ph + fi * .04) + .05 * math.cos(2 * th - ph)   # 兩三道稜、不規則橢圓（沿長度慢慢轉）
        dn = sd_ * dv.dot(sd_)
        dv = (dn * sq * flat + (dv - dn) * (2 - flat) ** .5) * rid     # flat < 1：朝土那向壓扁、兩側略放寬（壓平，不是變細）
        v.co = ctr + dv
    o.data.update()


ROOTPLAN_B = (
    # 名稱、母根、母根上位置、控制點 (u 往右, v 往上, 埋深)、起點半徑（主根：×k；分根：×母根半徑）、末端半徑（×k）、斷端長
    # 埋深 < 0.9 露出、≥ 0.9 埋進土層；實際深度由 fit_roots11 依泥面法線、所在位置再調
    ('M1', None, 0, ((-.06, -1.00, 1.3), (-.10, -.80, .5), (-.20, -.58, .45), (-.30, -.36, .4), (-.38, -.14, 1.45), (-.43, .08, 1.55), (-.43, .30, 1.5), (-.38, .52, .4), (-.26, .78, .45), (-.14, 1.05, .5)), .32, .10, 0),     # 主根：根頸偏左出土，中段沒入土層再露出
    ('M2', 'M1', .20, ((.05, -.30, .5), (.15, -.17, .5), (.24, -.04, .5), (.30, .08, .55), (.34, .18, 1.25)), .72, .08, 0),     # 次主根：從 M1 中段分出、斜過碗底往右上，碗緣前沒入（不走右側凹溝、不爬外凸土瓣、不在碗緣立成板）
    ('M3', None, 0, ((-.34, -.98, 1.3), (-.42, -.84, .5), (-.62, -.70, .5), (-.82, -.60, .95), (-1.02, -.50, .5)), .22, .10, .22),     # 左下：自己從土裡冒出（不從同一結點放射）
    ('M4', None, 0, ((.46, -1.04, 1.3), (.52, -.92, .5), (.58, -.82, .45), (.62, -.72, 1.25)), .26, .12, 0),     # 右下：從坑邊冒出、沿土瓣下緣一小段後沒入（右土瓣表面縫多，加長加粗都會碎成片或整條埋掉，g42 試過）
    ('S1', 'M1', .45, ((-.62, .02, .5), (-.72, -.06, 1.1), (-.84, -.18, 1.25)), .62, .06, 0),          # 往下彎進土（不在左緣橫伸）
    ('S2', 'M1', .74, ((-.55, .62, .5), (-.75, .70, .95), (-.92, .74, .45)), .60, .06, .10),
    ('S3', 'M2', .62, ((.30, .30, .5), (.20, .52, .55), (.12, .72, 1.05), (.06, .90, .5)), .65, .06, 0),
    ('S4', 'M2', .78, ((.66, .52, .5), (.74, .40, .55), (.80, .26, 1.1)), .45, .045, 0),          # 右上：細、往下彎進土（不再是水平橫桿）
    ('S6', 'M2', .55, ((.60, .10, .5), (.70, .02, .55), (.78, -.04, 1.2)), .45, .045, 0),          # 右上：細、往外下彎進土
    ('S7', 'M4', .35, ((.56, -.86, .5), (.62, -.93, 1.2)), .50, .045, 0),
    ('T2', 'S1', .50, ((-.90, .06, .5), (-1.00, -.04, 1.15), (-1.08, -.16, .45)), .55, .030, .06),          # 細根：埋入再露出
    ('T3', 'M2', .70, ((.66, .30, .5), (.72, .16, 1.10), (.76, .02, .5)), .40, .028, .04),
    ('T4', 'M1', .25, ((-.26, -.52, .5), (-.34, -.64, 1.15), (-.46, -.70, .45)), .35, .028, .05),
    ('T5', 'S2', .55, ((-.70, .86, .5), (-.80, .96, .45)), .50, .025, .05),
    ('T6', 'M2', .88, ((.40, .80, .5), (.30, .93, 1.10), (.22, 1.02, .45)), .45, .030, 0),
    ('S5', 'M3', .55, ((-.72, -.82, .5), (-.80, -.98, 1.1)), .55, .05, 0),
    ('T1', 'S3', .50, ((.30, .62, .5), (.36, .76, .45)), .60, .030, .06),
)


def _cr2(P, n):
    """控制點 Catmull-Rom 加密（每段 n 點）。"""
    out = []
    for i in range(len(P) - 1):
        a, b, c, d = P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, len(P) - 1)]
        for j in range(n):
            t = j / n
            out.append(tuple(.5 * ((2 * b[k]) + (-a[k] + c[k]) * t + (2 * a[k] - 5 * b[k] + 4 * c[k] - d[k]) * t * t + (-a[k] + 3 * b[k] - 3 * c[k] + d[k]) * t ** 3) for k in range(len(b))))
    out.append(tuple(P[-1]))
    return out


def plan_roots11(V, coll, low):
    """B 第七版：少數主根沿凹面彎曲上行、往兩側分流；次根從主根不同高度分出、粗細漸變；
    部分段落埋進土層再露出（埋深 > 1）；伸出板緣的留不等長斷端。不從同一點直線放射。"""
    g = plate_geom(V)
    k, Re0, zc = g['k'], g['Re'], g['zc']
    wd, vz = V.get('wide', 1.0), V.get('vz', 1.0)
    obs = coll if isinstance(coll, list) else list(coll.objects)
    tr = next(o for o in obs if o.name.split('.')[0].endswith('Trunk'))
    mat, col_ = tr.data.materials[0], tr.users_collection[0]
    cr = V.get('crumble')
    ang0, ang1 = [math.radians(x) for x in cr] if cr else (9.0, 9.0)
    bite = V.get('bite', .4)

    def rim(y, z):
        a = math.atan2(-y / wd, (z - zc) / vz)
        lim = outline_b11(V, a)
        if cr and ang0 - .15 < a < ang1 + .15:
            lim *= 1 - .85 * bite * min(_sm((a - ang0 + .15) / .3), _sm((ang1 + .15 - a) / .3))
        return math.hypot(y / wd, (z - zc) / vz) / (Re0 * lim)

    Re = Re0

    def fx(y, z):
        """泥面 x：崩口裡的泥面被徑向內縮過（crumble11 的 crumble_soft），反求原本的位置再算。"""
        if not (cr and V.get('crumble_soft')):
            return face_x(V, y, z, V['seed'])
        a = math.atan2(-y / wd, z - zc)
        r = math.hypot(y / wd, z - zc) / Re
        if not (ang0 - .25 < a < ang1 + .25) or r < .35:
            return face_x(V, y, z, V['seed'])
        e_ = min(_sm((a - ang0 + .25) / .5), _sm((ang1 + .25 - a) / .5))
        b = bite * (1 + .25 * fb(Vector((a * 3.0, 1.7, 0)), 1.0, 2))
        lo, hi = r, r * 2.5
        for _ in range(30):
            mid = (lo + hi) / 2
            if mid * (1 - .85 * b * e_ * _sm((mid - .35) / .55)) < r:
                lo = mid
            else:
                hi = mid
        s_ = lo / max(r, 1e-6)
        return face_x(V, y * s_, zc + (z - zc) * s_, V['seed'])

    made, dense = [], {}
    _ROOTINFO.clear()
    amp0 = CFG['amp']
    CFG['amp'] = V.get('root_amp', amp0)                 # 灰模：粗根不加樹皮掃描位移（它會在根身壓出一節節橫紋）
    collar11(V, coll, low, .02 * Re0, zc - .86 * Re0 * vz)
    for name, par, tpar, ctrl, rk0, rk1, over in ROOTPLAN_B:
        if par:                                          # 分岔：先順著母根方向走一小段再彎出去（不做直角接）
            if par not in dense or len(dense[par][0]) < 6:
                continue
            pd, prs = dense[par]
            i0 = max(1, min(len(pd) - 4, int(len(pd) * tpar)))
            a_, b_ = pd[i0], pd[i0 + 3]
            P = [(a_[0], a_[1], 1.3), (b_[0] + .25 * (ctrl[0][0] - b_[0]), b_[1] + .25 * (ctrl[0][1] - b_[1]), .4)] + list(ctrl)
            r0 = prs[i0] * rk0
            if name in V.get('fork_soft', ()):           # 主分岔：起點在母根身體裡（不埋土、不從旁邊冒出），先貼著母根往上走一段再斜斜岔開，分岔處粗
                e_ = pd[min(len(pd) - 1, i0 + 6)]
                P = [(a_[0], a_[1], .45), (b_[0], b_[1], .45), (e_[0] + .35 * (ctrl[0][0] - e_[0]), e_[1] + .35 * (ctrl[0][1] - e_[1]), .45)] + list(ctrl)
                r0 = prs[i0] * min(.92, rk0 * 1.2)
        else:
            P, r0 = list(ctrl), k * rk0 * V.get('root_k', 1.0)
        D = _cr2(P, 5 if low else 9)
        pts2 = []
        for u, v, emb in D:
            y, z = -u * Re0 * wd, zc + v * Re0 * vz
            if rim(y, z) > .97:
                break
            pts2.append((u, v, emb, y, z))
        dive = 0                                         # 崩落區、缺口把外輪廓往內切了：根走到真正泥盤外（空中）的點，沿徑向拉回泥盤裡（根順著崩口邊緣貼土走，不懸空斜出去）
        if V.get('cut_at_real', False):
            def exc_(y, z):
                _NOGAP11[0] = True
                o0_ = real_off11(V, y, z)
                _NOGAP11[0] = False
                return real_off11(V, y, z) - o0_       # 只算崩落／缺口造成的「在泥盤外」（底部 z 夾限不算）
            pull = []
            for j_, (u, v, emb, y, z) in enumerate(pts2):
                if exc_(y, z) > .03:
                    lo, hi = .3, 1.0
                    for _ in range(12):
                        mid = (lo + hi) / 2
                        if exc_(y * mid, zc + (z - zc) * mid) > .03:
                            hi = mid
                        else:
                            lo = mid
                    lo *= 1 - .10 / max(.3, math.hypot(y, z - zc))          # 再往裡 10 cm：根整條躺在土上，不騎在崩口邊上
                    y, z = y * lo, zc + (z - zc) * lo
                    pull.append(j_)
                pts2[j_] = (-y / (Re0 * wd), (z - zc) / (Re0 * vz), emb, y, z)
            if pull:
                dive = 1
                print('DR11_ROOTPULL', name, len(pull), len(pts2), pull)
                for _ in range(4):                       # 拉回的點和原本的點接起來（不折角）
                    pts2 = [pts2[0]] + [(pts2[j][0], pts2[j][1], pts2[j][2], (pts2[j - 1][3] + 2 * pts2[j][3] + pts2[j + 1][3]) / 4, (pts2[j - 1][4] + 2 * pts2[j][4] + pts2[j + 1][4]) / 4) for j in range(1, len(pts2) - 1)] + [pts2[-1]]
                pts2 = [(-y / (Re0 * wd), (z - zc) / (Re0 * vz), emb, y, z) for (u, v, emb, y, z) in pts2]
                if pull[-1] >= len(pts2) - 2:             # 末端整段都在泥盤外的根：在走出泥盤處收掉，最後幾點鑽進土裡（斷面不朝相機露出來）
                    t0 = len(pts2) - 1
                    while t0 - 1 in pull:
                        t0 -= 1
                    pts2 = pts2[:max(4, t0 + 3)]
                    m_ = len(pts2)
                    pts2 = [(u, v, (max(emb, .9 + 1.1 * (j_ - (m_ - 4)) / 3) if j_ >= m_ - 4 else emb), y, z) for j_, (u, v, emb, y, z) in enumerate(pts2)]
        n = len(pts2)
        if n < 3:
            continue
        rs = [r0 + (k * rk1 * V.get('root_k', 1.0) - r0) * (i / (n - 1)) ** 1.2 for i in range(n)]
        if par:                                          # 分岔處自然增厚
            rs[0] *= 1.35
            rs[1] *= 1.15
        dense[name] = ([(u, v, e) for u, v, e, _, _ in pts2], rs)
        _NOGAP11[0] = True
        xr_ = [fx(y, z) for (u, v, emb, y, z) in pts2]
        _NOGAP11[0] = False
        xg_ = [fx(y, z) for (u, v, emb, y, z) in pts2]                 # 真正的泥面（含崩落區、缺口）
        print('DR11_ROOTGAP', name, round(max(g_ - r_ for g_, r_ in zip(xg_, xr_)), 3))
        if name not in V.get('bridge_roots', ('S6', 'S7')):          # 只有刻意跨過缺口的根用「沒崩之前的泥面」；其他根貼真正的泥面（不在崩落區前面懸空斜出去）
            xr_ = xg_
        xs_ = list(xr_)
        for _ in range(6):                                # 泥面 x 先平滑（泥面台階會讓根一段一段折，看起來像分節），再扣埋深：埋入→露出不會被抹平
            xs_ = [xs_[0]] + [(xs_[j - 1] + 2 * xs_[j] + xs_[j + 1]) / 4 for j in range(1, len(xs_) - 1)] + [xs_[-1]]
        gap_ = max(r_ - s_ for r_, s_ in zip(xr_, xs_))
        xs_ = [max(s_, r_ - .02) for r_, s_ in zip(xr_, xs_)]          # 平滑會把凹面拉成直弦、根懸空斜出去：不准比泥面往外超過 2 cm（貼著凹面走）
        print('DR11_ROOTFLOAT', name, round(gap_, 3))
        pts = [((xs_[j] + rr * (.45 - .30 * emb + (V.get('main_sink', 0.0) if name.startswith('M') else 0.0))) if emb < .9 else (xs_[j] + rr * emb), y, z, rr, 1.0) for j, ((u, v, emb, y, z), rr) in enumerate(zip(pts2, rs))]     # 露出段中心在泥面下約 0.3–0.35 倍半徑（只露出約 0.65–0.7 倍半徑，不像貼在牆上的管子）；埋深 > 0.9 的段落中心往 +X（泥裡）沉 emb 倍半徑（根面朝 -X：減是往外，原式寫反，設越深反而浮越高）
        over *= V.get('over_k', 1.0) * (0 if dive else 1)                     # 板緣外伸的斷根短一點（不像一根根棍子戳出來）
        if over > 0:
            x1, y1, z1, r1, _ = pts[-1]
            x0, y0, z0, _, _ = pts[-2]
            dv = Vector((x1 - x0, y1 - y0, z1 - z0)).normalized()
            for i in range(1, 4):
                t = over * i / 3
                pts.append((x1 + dv.x * t - .15 * t, y1 + dv.y * t, z1 + dv.z * t - .9 * t * t, r1 * (1 - .12 * i / 3), 1.0))
        _ROOTPTS[name] = pts
        o = tube(f'FaceRoot{name}', pts, V['seed'] + 1700 + len(made), rib=.11, twist=0.0, collection=col_, moss_bias=-.6, cap_end=True)
        _ROOTINFO[o.name] = dict(key=name, pts=list(pts), embs=[e for (_, _, e, _, _) in pts2], nmain=len(pts2), seed=V['seed'] + 1700 + len(made), rib=.11, twist=0.0, moss=-.6,
                                 sec=(V['seed'] + len(made), V.get('main_flat', 1.0) if name.startswith('M') else 1.0), child=bool(par))
        root_section11(o, pts, V['seed'] + len(made), flat=V.get('main_flat', 1.0) if name.startswith('M') else 1.0)
        o.data.materials.append(mat)
        made.append(o)
    CFG['amp'] = amp0
    rim_clods11(V, coll, low)
    if not V.get('fit'):
        collapse_clods11(V, coll, low)
    stones_front11(V, coll, low)
    print('DR11_PLANROOTS', len(made))
    if isinstance(coll, list):
        coll.extend(made)
    return made


def rim_clods11(V, coll, low):
    """板緣夾帶的土塊：在主根出口之間、半埋在板緣上（外緣由粗根、土塊、斷根共同構成）。"""
    import bmesh
    g = plate_geom(V)
    k, Re0, zc = g['k'], g['Re'], g['zc']
    wd, vz = V.get('wide', 1.0), V.get('vz', 1.0)
    R = random.Random(V['seed'] + 1801)
    obs = coll if isinstance(coll, list) else list(coll.objects)
    mud = next(o for o in obs if re.sub(r'\.\d{3}$', '', o.name).endswith('Mud'))
    bm = bmesh.new()
    for a_deg in V.get('rimclods', (-112, -44, 18, 52, 150)):
        a = math.radians(a_deg + R.uniform(-4, 4))
        f = outline_b11(V, a) * R.uniform(.88, .95)
        y, z = -math.sin(a) * f * Re0 * wd, zc + math.cos(a) * f * Re0 * vz
        x = face_x(V, y, z, V['seed'])
        s_ = k * R.uniform(.08, .14)
        b2 = bmesh.new()
        bmesh.ops.create_icosphere(b2, subdivisions=1 if low else 3, radius=1.0)
        off = Vector((R.uniform(-9, 9), R.uniform(-9, 9), R.uniform(-9, 9)))
        out_ = Vector((0, -math.sin(a), math.cos(a)))
        for q in b2.verts:
            d = q.co.copy()
            rr = 1 + .30 * fb(d * 1.3 + off, 1.0, 2) + .12 * fb(d * 4.5 + off, 1.0, 2)
            q.co = Vector((x + .35 * s_, y, z)) + out_ * (-.3 * s_) + Vector((d.x * .6, d.y * 1.3, d.z * .7)) * s_ * rr
        me2 = bpy.data.meshes.new('tmp11')
        b2.to_mesh(me2)
        b2.free()
        bm.from_mesh(me2)
        bpy.data.meshes.remove(me2)
    me = bpy.data.meshes.new('DR11_ClodsRim')
    bm.to_mesh(me)
    bm.free()
    for p_ in me.polygons:
        p_.use_smooth = True
    at = me.attributes.new('MudMoss', 'FLOAT', 'POINT')
    at.data.foreach_set('value', np.zeros(len(me.vertices), np.float32))
    me.materials.append(mud.data.materials[0])
    ob = bpy.data.objects.new('ClodsRim', me)
    mud.users_collection[0].objects.link(ob)
    if isinstance(coll, list):
        coll.append(ob)


def _soil_bvh11(obs):
    """土（泥盤、坑面）與倒幹的 BVH。回傳 [(bvh, 名稱)]。"""
    from mathutils.bvhtree import BVHTree
    out = []
    for o in obs:
        nm = re.sub(r'\.\d{3}$', '', o.name)
        if o.type == 'MESH' and (nm.endswith(('Mud', 'Pit', 'Trunk')) and not nm.endswith('RootsPit')):
            vs = [o.matrix_world @ v.co for v in o.data.vertices]
            out.append((BVHTree.FromPolygons(vs, [tuple(p.vertices) for p in o.data.polygons]), nm))
    return out


def _sd11(S, p):
    """土的聯集的帶號距離（外正內負）、最近點、法線（朝外）。"""
    best = None
    for b, nm in S:
        q, n, _, d = b.find_nearest(p)
        if q is None:
            continue
        sg = 1.0 if n.dot(p - q) >= 0 else -1.0
        if best is None or sg * d < best[0]:
            best = (sg * d, q, n)
    return best


def _nrm11(S, p, r):
    """在根徑尺度上平均的泥面法線（不被小起伏帶著扭）。"""
    acc = Vector((0, 0, 0))
    for o_ in (Vector((0, 0, 0)), Vector((r, 0, 0)), Vector((-r, 0, 0)), Vector((0, r, 0)), Vector((0, -r, 0)), Vector((0, 0, r)), Vector((0, 0, -r))):
        b = _sd11(S, p + o_)
        if b:
            acc += b[2]
    return acc.normalized() if acc.length > 1e-6 else Vector((-1, 0, 0))


def fit_roots11(V, coll, low, M):
    """統一貼合：每條貼土根的中心線照最終泥面走（法線方向，不再只沿 X），
    露出段埋入約 1/3–1/2 根徑（沿長度隨位置變化），埋入段整段沒入；根兩側若離開泥面（懸空縫）就局部再沉。
    外伸斷根（板緣外）保留外露，只跟著接點移動。"""
    obs = coll if isinstance(coll, list) else list(coll.objects)
    S = _soil_bvh11(obs)
    rep_ = []
    Minv = M.inverted()
    for o in list(obs):
        info = _ROOTINFO.get(o.name)
        if not info or o.name not in bpy.data.objects:
            continue
        pts0 = info['pts']
        nm_ = info['nmain']
        embs = info['embs'] + [None] * (len(pts0) - nm_)
        P = [M @ Vector(q[:3]) for q in pts0]
        Rr = [q[3] for q in pts0]
        Pm = [Vector(p) for p in P[:nm_]]
        n_ = len(Pm)
        if not info['key'].startswith('B'):               # 正面根：先放到「從正面看第一層」泥面上（外凸土瓣下面的凹洞壁不算）
            dX = (M.to_3x3() @ Vector((1, 0, 0))).normalized()
            for i in range(n_):
                o_ = Pm[i] - dX * 4.0
                best_ = None
                for b_, nm__ in S:
                    if not nm__.endswith('Mud'):
                        continue
                    hl, hn, _, hd = b_.ray_cast(o_, dX, 8.0)
                    if hl is not None and (best_ is None or hd < best_[1]):
                        best_ = (hl, hd)
                if best_ and -.45 < (best_[0] - Pm[i]).dot(dX) < -.02:   # 前面還有一層土（土瓣蓋在根上，45 cm 內）→ 移到那層
                    Pm[i] = best_[0] + dX * .02
            for _ in range(2):
                Pm = [Pm[0]] + [(Pm[i - 1] + 2 * Pm[i] + Pm[i + 1]) / 4 for i in range(1, n_ - 1)] + [Pm[-1]]
        # 沿長度的弧長（給埋深變化用）
        sl = [0.0]
        for i in range(1, n_):
            sl.append(sl[-1] + (Pm[i] - Pm[i - 1]).length)
        ph = (info['seed'] % 97) * .37
        bias = V.get('fit_bias', {}).get(info['key'], 0.0)          # 個別根的露出偏移（右側保留的主要斜根多露一點）
        H = []
        for i in range(n_):
            e = embs[i]
            r = Rr[i]
            if e >= .9:
                H.append(r * (1.15 + .35 * min(1.0, e - .9)))          # 埋入段：整段沒進土層
            else:
                b = .40 + bias + .06 * math.sin(sl[i] * 4.3 + ph) + .04 * math.sin(sl[i] * 11.0 + 2 * ph)   # 埋入比例約 0.30–0.50 根徑，沿長度變
                H.append(r * (2 * b - 1))
        for _ in range(6):                                # 埋深沿長度平滑（出入土不突然截斷）
            H = [H[0]] + [(H[i - 1] + 2 * H[i] + H[i + 1]) / 4 for i in range(1, n_ - 1)] + [H[-1]]
        Hx = [0.0] * n_                                   # 懸空縫造成的局部加深
        soil = [Vector((1, 0, 0))] * n_
        NIT = 8
        for it in range(NIT):
            for i in range(n_):
                r = Rr[i]
                for _k in range(3):
                    b = _sd11(S, Pm[i])
                    if not b:
                        break
                    nn = _nrm11(S, b[1], max(.04, r))
                    sd_ = (Pm[i] - b[1]).dot(nn)
                    Pm[i] = Pm[i] - nn * (sd_ + H[i] + Hx[i])
                soil[i] = -nn
            if it < NIT - 1:                              # 平滑中心線（根徑尺度以下的泥面起伏不讓根一節節折）
                Q = [Pm[0]] + [(Pm[i - 1] + 2 * Pm[i] + Pm[i + 1]) / 4 for i in range(1, n_ - 1)] + [Pm[-1]]
                Pm = Q
            # 兩側、下側檢查懸空縫
            if it >= 2:
                for i in range(n_):
                    r = Rr[i]
                    t = (Pm[min(i + 1, n_ - 1)] - Pm[max(i - 1, 0)])
                    if t.length < 1e-6:
                        continue
                    t.normalize()
                    sd = soil[i]
                    sv = t.cross(sd).normalized()
                    worst = 0.0
                    for a_ in (-1.2, -.6, 0.0, .6, 1.2):       # 朝土那半圈（含兩側）
                        dd = (sd * math.cos(a_) + sv * math.sin(a_)) * r * .95
                        b = _sd11(S, Pm[i] + dd)
                        if b and b[0] > worst:
                            worst = b[0]
                    if worst > max(.015, .12 * r):              # 只處理根徑尺度的懸空縫（泥面小凹凸不算）
                        Hx[i] = min(Hx[i] + worst * .7, r * V.get('fit_sink', .55))
                for _ in range(3):
                    Hx = [Hx[0]] + [max(Hx[i], (Hx[i - 1] + 2 * Hx[i] + Hx[i + 1]) / 4) for i in range(1, n_ - 1)] + [Hx[-1]]
        # 跨溝、夾縫：根卡在兩個土瓣之間（兩側都是土、只剩一條薄片露出）或底下懸空 → 這段鑽進土裡，從另一側再露出（不留浮空、不成薄板）
        dive = [False] * n_
        dgap_ = [False] * n_
        for i in range(n_):
            r = Rr[i]
            t = (Pm[min(i + 1, n_ - 1)] - Pm[max(i - 1, 0)])
            if t.length < 1e-6 or (embs[i] is not None and embs[i] >= .9):
                continue
            t.normalize()
            sv = t.cross(soil[i]).normalized()
            w = 0.0
            for a_ in (-1.2, -.6, 0.0, .6, 1.2):
                b = _sd11(S, Pm[i] + (soil[i] * math.cos(a_) + sv * math.sin(a_)) * r * .95)
                if b and b[0] > w:
                    w = b[0]
            up_ = -soil[i] * r * .55                                 # 根腰以上的高度：兩側土牆若高過這裡，根只剩一條薄片
            bl, br = _sd11(S, Pm[i] + sv * r * 1.25 + up_), _sd11(S, Pm[i] - sv * r * 1.25 + up_)
            sliver = bl and br and bl[0] < -.10 * r and br[0] < -.10 * r
            if w > max(.06, .70 * r) or sliver:                    # 只有大懸空（跨溝）或夾縫才整段鑽土；小縫交給局部加深
                dive[i] = True
            dgap_[i] = w > max(.06, .70 * r)
        if sum(dive) > .25 * n_:                                 # 高解析泥面凹凸多、夾縫判定過度觸發（主根整條被埋掉）→ 只留真懸空段鑽土
            dive = dgap_
        if any(o.name.endswith(k_) for k_ in V.get('dive_skip', ())):   # 正面主根要露出：不整段鑽土，只靠局部加深貼土
            dive = [False] * n_
        if any(dive) and V.get('fit_dive', True):
            dv_ = list(dive)
            for _ in range(2):                                # 往前後擴幾點，出入土有過渡
                dv_ = [dv_[i] or (i > 0 and dv_[i - 1]) or (i < n_ - 1 and dv_[i + 1]) for i in range(n_)]
            i = 0
            while i < n_:                                     # 兩段入土之間只剩一小截露出（像一顆凸起的斷頭）→ 一起埋
                if not dv_[i]:
                    j = i
                    while j < n_ and not dv_[j]:
                        j += 1
                    ln = sum((Pm[k + 1] - Pm[k]).length for k in range(i, min(j, n_ - 1)))
                    if i > 0 and j < n_ and ln < 5 * max(Rr[i:j] or [Rr[i]]):
                        for k in range(i, j):
                            dv_[k] = True
                    i = j
                else:
                    i += 1
            for i in range(n_):
                if dv_[i]:
                    H[i] = max(H[i], Rr[i] * 1.2)
            for _ in range(3):
                H = [H[0]] + [max(H[i] if dv_[i] else 0.0, (H[i - 1] + 2 * H[i] + H[i + 1]) / 4) for i in range(1, n_ - 1)] + [H[-1]]
            for it in range(3):
                for i in range(n_):
                    r = Rr[i]
                    for _k in range(3):
                        b = _sd11(S, Pm[i])
                        if not b:
                            break
                        nn = _nrm11(S, b[1], max(.04, r))
                        sd_ = (Pm[i] - b[1]).dot(nn)
                        Pm[i] = Pm[i] - nn * (sd_ + H[i] + Hx[i])
                    soil[i] = -nn
                if it < 2:
                    Pm = [Pm[0]] + [(Pm[i - 1] + 2 * Pm[i] + Pm[i + 1]) / 4 for i in range(1, n_ - 1)] + [Pm[-1]]
            print('DR11_DIVE', o.name, sum(dive), sum(dv_))
        # 檢查：每點朝土半圈的最大懸空
        gaps = []
        for i in range(n_):
            r = Rr[i]
            t = (Pm[min(i + 1, n_ - 1)] - Pm[max(i - 1, 0)])
            if t.length < 1e-6:
                gaps.append(0.0)
                continue
            t.normalize()
            sv = t.cross(soil[i]).normalized()
            w = 0.0
            for a_ in (-1.2, -.6, 0.0, .6, 1.2):
                b = _sd11(S, Pm[i] + (soil[i] * math.cos(a_) + sv * math.sin(a_)) * r * .95)
                if b and b[0] > w:
                    w = b[0]
            gaps.append(w)
        ex = []
        for i in range(n_):                               # 露出量（中心在泥面外多少，負 = 埋入）
            b = _sd11(S, Pm[i])
            ex.append(b[0] / Rr[i] if b else 0)
        # 外伸斷根：跟著接點平移，不貼
        dlt = Pm[-1] - P[nm_ - 1]
        tail = [P[j] + dlt for j in range(nm_, len(P))]
        newp = [(p.x, p.y, p.z, Rr[i], 1.0) for i, p in enumerate(Pm)] + [(p.x, p.y, p.z, Rr[nm_ + j], 1.0) for j, p in enumerate(tail)]
        soil_all = soil + [soil[-1]] * len(tail)
        col_, mat = o.users_collection[0], o.data.materials[0]
        name = o.name
        if isinstance(coll, list):
            coll[:] = [x for x in coll if x is not o]
        bpy.data.objects.remove(o, do_unlink=True)
        o2 = tube(name, newp, info['seed'], rib=info['rib'], twist=info['twist'], collection=col_, moss_bias=info['moss'], cap_end=True)
        o2.name = name
        if info['sec']:
            root_section11(o2, newp, info['sec'][0], flat=info['sec'][1], soil=soil_all)
        o2.data.materials.append(mat)
        if isinstance(coll, list):
            coll.append(o2)
        _ROOTPTS[info['key']] = [tuple(Minv @ Vector(q[:3])) + (q[3], 1.0) for q in newp]
        ng = sum(1 for g_ in gaps if g_ > .015)
        if os.environ.get('DR11_MARKGAPS'):               # 檢查用：懸空縫位置放紅球（不進正式輸出）
            for i_, g_ in enumerate(gaps):
                if g_ > .015:
                    bpy.ops.mesh.primitive_uv_sphere_add(radius=.04, location=Pm[i_])
                    bpy.context.object.name = f'DbgGap_{name}_{i_}'
        rep_.append((name, n_, ng, round(max(gaps), 3), round(min(ex), 2), round(max(ex), 2), [i for i, g_ in enumerate(gaps) if g_ > .015]))
    for r_ in rep_:
        print('DR11_FIT', *r_)
    return rep_


def collapse_clods11(V, coll, low):
    """崩落區殘留土塊：有厚度、幾個平的斷裂面，卡在跨過缺口的粗根上（位置用沒崩之前的泥面）。"""
    import bmesh
    g = plate_geom(V)
    k, Re0, zc = g['k'], g['Re'], g['zc']
    wd, vz = V.get('wide', 1.0), V.get('vz', 1.0)
    R = random.Random(V['seed'] + 1811)
    obs = coll if isinstance(coll, list) else list(coll.objects)
    mud = next(o for o in obs if re.sub(r'\.\d{3}$', '', o.name).endswith('Mud'))
    bm = bmesh.new()
    _NOGAP11[0] = True
    for rn, tf, sz in V.get('collapseclods', (('S6', .55, .42), ('S6', .85, .26), ('M4', .80, .30), ('S7', .6, .20), ('M3', .70, .22), ('M3', .92, .15), ('S5', .85, .13), ('T2', .9, .10), ('M3', .50, .17), ('S1', .80, .12))):
        P_ = _ROOTPTS.get(rn)
        if not P_:
            continue
        x, y, z, rr_, _ = P_[min(len(P_) - 1, int(len(P_) * tf))]
        a = math.atan2(-y / wd, (z - zc) / vz)
        s_ = k * sz
        z += rr_ + .45 * s_                                # 坐在根上（土塊下緣包住根）
        b2 = bmesh.new()
        bmesh.ops.create_icosphere(b2, subdivisions=2 if low else 4, radius=1.0)
        off = Vector((R.uniform(-9, 9), R.uniform(-9, 9), R.uniform(-9, 9)))
        cuts = [(Vector((R.uniform(-1, 1), R.uniform(-1, 1), R.uniform(-1, 1))).normalized(), R.uniform(.35, .65)) for _ in range(3)]
        cuts.append((Vector((0, -math.sin(a), math.cos(a))), .30))       # 朝外那面是一片斷裂面
        for q in b2.verts:
            dd = q.co.copy()
            rr = 1 + .22 * fb(dd * 1.4 + off, 1.0, 2) + .07 * fb(dd * 5.0 + off, 1.0, 2)
            pp = dd * rr
            for n_, c0 in cuts:
                h = pp.dot(n_)
                if h > c0:
                    pp -= n_ * (h - c0) * .92
            q.co = Vector((x + .25 * s_, y, z)) + Vector((pp.x * .75, pp.y * 1.15, pp.z * .85)) * s_
        me2 = bpy.data.meshes.new('tmp11')
        b2.to_mesh(me2)
        b2.free()
        bm.from_mesh(me2)
        bpy.data.meshes.remove(me2)
    _NOGAP11[0] = False
    me = bpy.data.meshes.new('DR11_ClodsCollapse')
    bm.to_mesh(me)
    bm.free()
    for p_ in me.polygons:
        p_.use_smooth = True
    at = me.attributes.new('MudMoss', 'FLOAT', 'POINT')
    at.data.foreach_set('value', np.zeros(len(me.vertices), np.float32))
    me.materials.append(mud.data.materials[0])
    ob = bpy.data.objects.new('ClodsCollapse', me)
    mud.users_collection[0].objects.link(ob)
    if isinstance(coll, list):
        coll.append(ob)


def stones_front11(V, coll, low):
    """根面前的石塊（獨立建形，不是把泥團換材質）：一顆主石在左下、一顆次石在右下、兩三顆小陪襯石；
    多個平切面（有稜角）、下半埋進地面／坑坡。"""
    import bmesh
    g = plate_geom(V)
    R = random.Random(V['seed'] + 1871)
    obs = coll if isinstance(coll, list) else list(coll.objects)
    mud = next(o for o in obs if re.sub(r'\.\d{3}$', '', o.name).endswith('Mud'))
    bm = bmesh.new()
    bmc = bmesh.new()
    for y, rs, dx, bury, zs in V.get('fstones', ((.74, .30, -.10, .30, .62), (-.70, .22, -.65, .40, None), (1.00, .11, -.55, .35, None), (-.12, .09, -.75, .45, None), (.25, .07, -.95, .30, None))):
        z0 = .30 if zs is None else zs
        x = face_x(V, y, z0, V['seed']) + dx
        gz = pit_height11(V, x, y) if zs is None else zs - rs * .15          # zs：坐在根盤凹洞底（根頸上），不在地面
        b2 = bmesh.new()
        bmesh.ops.create_icosphere(b2, subdivisions=2 if low else 3, radius=1.0)
        off = Vector((R.uniform(-9, 9), R.uniform(-9, 9), R.uniform(-9, 9)))
        cuts = [(Vector((R.uniform(-1, 1), R.uniform(-1, 1), R.uniform(-.4, 1))).normalized(), R.uniform(.42, .70)) for _ in range(8)]       # 稜角多一點（不是圓球）
        sc = Vector((R.uniform(1.0, 1.35), R.uniform(.85, 1.2), R.uniform(.62, .82)))
        for q in b2.verts:
            dd = q.co.copy()
            pp = dd * (1 + .06 * fb(dd * 2.0 + off, 1.0, 2))
            for n_, c0 in cuts:
                h = pp.dot(n_)
                if h > c0:
                    pp -= n_ * (h - c0) * .95
            q.co = Vector((x, y, gz + rs * sc.z * (1 - 2 * bury))) + Vector((pp.x * sc.x, pp.y * sc.y, pp.z * sc.z)) * rs
        me2 = bpy.data.meshes.new('tmp11')
        b2.to_mesh(me2)
        b2.free()
        (bm if zs is None else bmc).from_mesh(me2)
        bpy.data.meshes.remove(me2)
    mec = bpy.data.meshes.new('DR11_StoneCave')
    bmc.to_mesh(mec)
    bmc.free()
    for p_ in mec.polygons:
        p_.use_smooth = False
    at = mec.attributes.new('MudMoss', 'FLOAT', 'POINT')
    at.data.foreach_set('value', np.zeros(len(mec.vertices), np.float32))
    mec.materials.append(stone_material())                   # 石塊用石材（不是泥）
    obc = bpy.data.objects.new('StoneCave', mec)            # 凹洞裡的主石：跟著根盤一起仰
    mud.users_collection[0].objects.link(obc)
    if isinstance(coll, list):
        coll.append(obc)
    me = bpy.data.meshes.new('DR11_StoneDebris')
    bm.to_mesh(me)
    bm.free()
    for p_ in me.polygons:
        p_.use_smooth = False
    at = me.attributes.new('MudMoss', 'FLOAT', 'POINT')
    at.data.foreach_set('value', np.zeros(len(me.vertices), np.float32))
    me.materials.append(stone_material())
    ob = bpy.data.objects.new('StoneDebris', me)          # 名稱以 Debris 結尾：不跟著根盤仰，留在地面上
    mud.users_collection[0].objects.link(ob)
    if isinstance(coll, list):
        coll.append(ob)


def back_roots11(V, coll, low):
    """B 第七版：根頸（背面）從根盤往下、再轉進後方倒幹的連續縱向根脊；取代原本一圈圈的鼓包。"""
    g = plate_geom(V)
    k = g['k']
    obs = coll if isinstance(coll, list) else list(coll.objects)
    tr = next(o for o in obs if o.name.split('.')[0].endswith('Trunk'))
    mat, col_ = tr.data.materials[0], tr.users_collection[0]
    R = random.Random(V['seed'] + 1901)
    made = []
    for j, ph0 in enumerate(V.get('backroots', (-125, -80, -35, 10, 42, 170))):          # 避開右側崩口（88–140°）：那裡泥面已內縮
        ph0 = math.radians(ph0 + R.uniform(-6, 6))
        ph1 = math.radians(180 - .45 * (180 - abs(math.degrees(ph0)))) * (1 if ph0 >= 0 else -1)
        r0 = k * R.uniform(.13, .19) * V.get('root_k', 1.0)
        pts = []
        m = 6
        for i in range(m):
            u = i / (m - 1)
            dx = .42 + .42 * u
            a = ph0 + (ph1 - ph0) * _sm(u)
            q = math.sqrt(max(0.0, 1 - dx * dx))
            d = Vector((dx, -q * math.sin(a), q * math.cos(a)))
            P = mud_pt(V, d, V['seed']) + mud_nrm(V, d, V['seed']) * r0 * (-.35 - .1 * u - .75 * max(0.0, math.cos(a)) ** 2)     # 靠近根盤頂的段落沉進泥裡（不頂出主體頂高）
            pts.append((P.x, P.y, P.z, r0 * (1 + .25 * u), 1.0))
        # 轉進倒幹：沿幹側往後走一段、慢慢沒入
        psi = ph1 * .55
        xa = pts[-1][0]
        for i, dxx in enumerate((.25, .6, 1.0)):
            x = xa + dxx * (1.0 + .3 * R.random())
            if x > V['L'] - .9:
                break
            rt = trunk_r(V, x)
            cz = trunk_z(V, x)
            pts.append((x, -math.sin(psi) * rt * (.92 - .1 * i), cz + math.cos(psi) * rt * (.92 - .1 * i), r0 * (1.2 - .25 * i), 1.0))
        if len(pts) < 4:
            continue
        o = tube(f'BackRoot{j}', pts, V['seed'] + 1950 + j, rib=.20, twist=.10, collection=col_, moss_bias=-.4, cap_end=True)
        pat = ((.5, 1.2, 1.2, .5, .5, 1.1), (1.1, .5, .5, 1.2, 1.2, .5), (.5, .5, 1.2, 1.2, 1.2, .5), (1.2, 1.2, .5, .5, 1.1, 1.1), (.5, 1.1, 1.2, .5, 1.2, 1.2), (.5, .5, .5, 1.1, 1.2, .5))[j % 6]
        _ROOTINFO[o.name] = dict(key=f'B{j}', pts=list(pts), embs=[pat[min(i_, 5)] for i_ in range(len(pts))], nmain=len(pts), seed=V['seed'] + 1950 + j, rib=.20, twist=.10, moss=-.4, sec=None, child=False)
        o.data.materials.append(mat)
        made.append(o)
    print('DR11_BACKROOTS', len(made))
    if isinstance(coll, list):
        coll.extend(made)
    return made



def trunk_shape11(V, coll, low):
    """B 倒幹：截面局部塌陷、粗細變化；末端長短不一的縱向劈裂（不是平切圓口外一圈尖刺）。仰角之前做。"""
    import bmesh
    obs = coll if isinstance(coll, list) else list(coll.objects)
    tr = next((o for o in obs if o.name.split('.')[0].endswith('Trunk')), None)
    if tr is None:
        return
    L, Rr = V['L'], V['R']
    rings, _ = resample(trunk_pts(V), .04)
    xs = np.array([p.x for p, *_ in rings])
    cs = [(p.y, p.z) for p, *_ in rings]
    R = random.Random(V['seed'] + 1601)
    bm = bmesh.new()
    bm.from_mesh(tr.data)
    if V.get('split_end') and not V.get('bundles'):
        ends = [f for f in bm.faces if len(f.verts) > 8]
        if ends:
            f = max(ends, key=lambda f_: f_.calc_center_median().x)
            for _ in range(2 if low else 4):
                res = bmesh.ops.inset_region(bm, faces=[f], thickness=Rr * (.30 if low else .17), depth=0)
            bmesh.ops.poke(bm, faces=[f])
    # 劈裂分區：7 片，長短不一
    nsec = 6
    ws = [R.uniform(.6, 1.6) for _ in range(nsec)]                   # 木束寬窄不一
    a0_ = R.uniform(0, 2 * math.pi)
    bnd, acc = [], a0_
    for w_ in ws:
        acc += w_ / sum(ws) * 2 * math.pi
        bnd.append(acc % (2 * math.pi))
    bnd.sort()
    ext = [R.uniform(.05, .50) for _ in range(nsec)]                  # 斷端長短錯落
    ext[R.randrange(nsec)] = .62
    bulge = [R.uniform(.88, 1.14) for _ in range(nsec)]                # 木束厚薄
    gdep = [R.uniform(.25, .70) for _ in range(nsec)]                  # 縱裂深淺

    def sec(th):
        th %= 2 * math.pi
        for i in range(nsec):
            if th < bnd[i]:
                return (i - 1) % nsec
        return nsec - 1

    def gap(th):
        return max(gdep[i] / .70 * math.exp(-((((th - b + math.pi) % (2 * math.pi)) - math.pi) / .10) ** 2) for i, b in enumerate(bnd))
    thc = R.uniform(0, 2 * math.pi)
    x0e = L - 1.05
    for v in bm.verts:
        x = v.co.x
        i = int(np.clip(np.searchsorted(xs, x), 0, len(xs) - 1))
        cy, cz = cs[i]
        ry, rz = v.co.y - cy, v.co.z - cz
        rho = math.hypot(ry, rz)
        if rho < 1e-5:
            th = 0.0
        else:
            th = math.atan2(rz, ry)
        f = 1.0
        if V.get('dents') and x > .55:
            w = _sm((x - .55) / .4) * (1 - _sm((x - (L - V.get('trunk_cut', 0.0) - .9)) / .4))     # 末端木束區不做塌陷（不要壓成扁板）
            f -= w * .14 * max(0.0, fb(Vector((x * 1.1, math.cos(th) * 1.3, math.sin(th) * 1.3)), 1.0, 2))
            f -= w * .22 * math.exp(-((((th - thc + math.pi) % (2 * math.pi)) - math.pi) / .7) ** 2) * math.exp(-((x - 1.35) / .45) ** 2)
            f *= 1 + .07 * math.sin(x * 2.4 + 1.0)
        dx = 0.0
        if V.get('split_end') and not V.get('bundles') and x > x0e:
            w = _sm((x - x0e) / (L - x0e))
            e = ext[sec(th)] * (.55 + .45 * _sm((rho / Rr - .40) / .45)) * (1 + .40 * fb(Vector((math.cos(th) * 4, math.sin(th) * 4, 2.2)), 1.0, 2))     # 外圈樹皮長、芯短、尖端參差
            gp = gap(th)
            sc_ = sec(th)
            f *= (1 - .45 * gp * w) * (1 + (bulge[sc_] - 1) * w) * (1 + .10 * e / .6 * w)
            dx = e * w - .20 * gp * w
        v.co = Vector((x + dx, cy + ry * f, cz + rz * f))
    bm.to_mesh(tr.data)
    bm.free()
    tr.data.update()
    if V.get('bundles'):
        wood_bundles11(V, tr, low, coll)


def _clip2(poly, n, c):
    """2D 多邊形被半平面 n·p <= c 裁切。"""
    out, m = [], len(poly)
    for i in range(m):
        P, Q = poly[i], poly[(i + 1) % m]
        dp = P[0] * n[0] + P[1] * n[1] - c
        dq = Q[0] * n[0] + Q[1] * n[1] - c
        if dp <= 0:
            out.append(P)
        if (dp < 0) != (dq < 0) and abs(dp - dq) > 1e-12:
            t = dp / (dp - dq)
            out.append((P[0] + (Q[0] - P[0]) * t, P[1] + (Q[1] - P[1]) * t))
    return out


def _perim_resample(poly, n):
    """沿周長等距取 n 點（每一列頂點數固定）。"""
    P = poly + [poly[0]]
    L_ = [0.0]
    for i in range(len(poly)):
        L_.append(L_[-1] + math.hypot(P[i + 1][0] - P[i][0], P[i + 1][1] - P[i][1]))
    out = []
    for k in range(n):
        s = L_[-1] * k / n
        j = max(0, min(len(poly) - 1, int(np.searchsorted(L_, s, side='right')) - 1))
        f = (s - L_[j]) / max(L_[j + 1] - L_[j], 1e-9)
        out.append((P[j][0] + (P[j + 1][0] - P[j][0]) * f, P[j][1] + (P[j + 1][1] - P[j][1]) * f))
    return out


def wood_bundles11(V, tr, low, coll):
    """B 倒幹斷端（第三版）：截面被幾道不平行的縱裂切成厚薄不一的劈裂木片（扁片、楔形、殘缺塊，不是圓心扇形）；
    縱裂從完整幹身裡開始（起點前後錯落）慢慢張開；每片末端是斜的斷面、長短不一；
    木片外緣再撕出幾條長木條、斷面上拉出細木絲，長短、彎曲、方向都不同。"""
    import bmesh
    L = V['L']
    Lt = L - V.get('trunk_cut', 0.0)
    tp = trunk_pts(V)
    (xa_, ya_, za_), (xb_, yb_, zb_) = tp[-2][:3], tp[-1][:3]
    dyx, dzx = (yb_ - ya_) / (xb_ - xa_), (zb_ - za_) / (xb_ - xa_)

    def ctr(x):
        x = min(x, L)                                    # 末端外不再沿幹軸往下（木條不插進地裡）
        return yb_ + dyx * (x - xb_), zb_ + dzx * (x - xb_)

    def rad(x):
        return trunk_r(V, min(x, L)) * (1 - .04 * _sm((x - Lt) / .8))
    R = random.Random(V['seed'] + 1667)
    mat, col_ = tr.data.materials[0], tr.users_collection[0]
    circ = [(math.cos(2 * math.pi * j / 96), math.sin(2 * math.pi * j / 96)) for j in range(96)]
    th0 = R.uniform(0, math.pi)
    cuts = []
    for c0 in (-.50, .08, .58):                              # 三道主裂（不平行、間距不等）
        a_ = th0 + R.uniform(-.28, .28)
        cuts.append(((math.cos(a_), math.sin(a_)), c0 + R.uniform(-.10, .10)))
    pieces = []
    for k in range(4):
        pg = circ
        if k > 0:
            n_, c_ = cuts[k - 1]
            pg = _clip2(pg, (-n_[0], -n_[1]), -c_)
        if k < 3:
            n_, c_ = cuts[k]
            pg = _clip2(pg, n_, c_)
        if len(pg) >= 3:
            pieces.append(pg)

    def area(pg):
        return abs(sum(pg[i][0] * pg[(i + 1) % len(pg)][1] - pg[(i + 1) % len(pg)][0] * pg[i][1] for i in range(len(pg)))) / 2
    big = max(range(len(pieces)), key=lambda i: area(pieces[i]))       # 最大那片再橫向裂開（楔形＋殘塊）
    a2 = th0 + math.pi / 2 + R.uniform(-.4, .4)
    n2 = (math.cos(a2), math.sin(a2))
    cx_ = sum(p[0] for p in pieces[big]) / len(pieces[big])
    cy_ = sum(p[1] for p in pieces[big]) / len(pieces[big])
    c2 = n2[0] * cx_ + n2[1] * cy_ + R.uniform(-.12, .12)
    pa, pb = _clip2(pieces[big], n2, c2), _clip2(pieces[big], (-n2[0], -n2[1]), -c2)
    pieces = pieces[:big] + [pa, pb] + pieces[big + 1:]
    exts = [.30, .52, .78, .95, .42][:len(pieces)]
    R.shuffle(exts)
    ns = 12 if low else 30
    npv = 16 if low else 40
    made = []
    for i, pg in enumerate(pieces):
        pg = _perim_resample(pg, npv)
        cxp = sum(p[0] for p in pg) / npv
        cyp = sum(p[1] for p in pg) / npv
        xs_c = Lt - R.uniform(.05, .35)                     # 縱裂起點：有的深入完整幹身
        gk = R.uniform(.05, .12)
        spl = R.uniform(.02, .07)                           # 木片往外撇
        sa = R.uniform(0, 2 * math.pi)
        sw = (math.cos(sa), math.sin(sa))
        sl = R.uniform(.12, .34)
        ends = []
        for (py, pz) in pg:
            pr = (py - cxp) * sw[0] + (pz - cyp) * sw[1]
            ends.append(Lt + exts[i] + sl * pr + .025 * R.uniform(-1, 1))
        x_a = Lt - .40
        mo = math.hypot(cxp, cyp) + 1e-6
        bm = bmesh.new()
        rows = []
        for kk in range(ns + 1):
            u = kk / ns
            row = []
            for j, (py, pz) in enumerate(pg):
                x = x_a + u * (ends[j] - x_a)
                r = rad(x)
                o_ = _sm((x - xs_c) / .40)
                sh = 1 - gk * o_                               # 裂縫張開：木片往自己中心收
                qy, qz = cxp + (py - cxp) * sh, cyp + (pz - cyp) * sh
                bump = 1 + .035 * fb(Vector((x * 2.2, py * 1.7 + i, pz * 1.7)), 1.0, 2)
                out_ = spl * _sm((x - Lt) / .7)
                ccy, ccz = ctr(x)
                row.append(bm.verts.new((x, ccy + r * (qy * bump + cxp / mo * out_), ccz + r * (qz * bump + cyp / mo * out_))))
            rows.append(row)
        for kk in range(ns):
            for j in range(npv):
                j2 = (j + 1) % npv
                bm.faces.new((rows[kk][j], rows[kk][j2], rows[kk + 1][j2], rows[kk + 1][j]))
        bm.faces.new(rows[0][::-1])
        bm.faces.new(rows[-1])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        _bundle_mesh(bm, f'Snap_TrunkBundle{i}', mat, col_, coll)
        made.append((pg, ends, cxp, cyp))
    _wood_strips11(V, made, ctr, rad, R, mat, col_, coll, low, Lt)


def _strip_mesh(bm, path, w0, t0, side0, taper=.25):
    """沿路徑的扁木條（矩形截面，尖端收薄）。"""
    rows = []
    n = len(path)
    for k, p in enumerate(path):
        tg = (path[min(k + 1, n - 1)] - path[max(k - 1, 0)]).normalized()
        sd = (side0 - tg * side0.dot(tg)).normalized()
        nm = tg.cross(sd).normalized()
        u = k / (n - 1)
        w = w0 * (1 - (1 - taper) * u ** 1.5)
        t = t0 * (1 - (1 - taper * .6) * u)
        rows.append([bm.verts.new(p + sd * (sy * w) + nm * (sz * t)) for sy, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    for k in range(n - 1):
        for j in range(4):
            j2 = (j + 1) % 4
            bm.faces.new((rows[k][j], rows[k][j2], rows[k + 1][j2], rows[k + 1][j]))
    bm.faces.new(rows[0][::-1])
    bm.faces.new(rows[-1])


def _wood_strips11(V, made, ctr, rad, R, mat, col_, coll, low, Lt):
    """次級長木條（從木片外緣撕出、往外彎）＋細木絲（從斷面拉出），長短、彎曲、方向都不同。"""
    import bmesh
    bm = bmesh.new()
    nseg = 8 if low else 16
    for kind, cnt in (('strip', 9), ('fiber', 16)):
        for _ in range(cnt):
            pg, ends, cxp, cyp = made[R.randrange(len(made))]
            if kind == 'strip':
                outer = [j for j, (py, pz) in enumerate(pg) if py * py + pz * pz > .85]
                if not outer:
                    continue
                j = R.choice(outer)
                py, pz = pg[j]
                x0 = ends[j] - R.uniform(.25, .55)
                ln = R.uniform(.35, .85)
                w0, t0 = R.uniform(.035, .07), R.uniform(.014, .03)
                rf = .99
            else:
                j = R.randrange(len(pg))
                f_ = R.uniform(.15, .85)
                py, pz = cxp + (pg[j][0] - cxp) * f_, cyp + (pg[j][1] - cyp) * f_
                x0 = ends[j] - .06
                ln = R.uniform(.12, .42)
                w0, t0 = R.uniform(.010, .022), R.uniform(.005, .011)
                rf = 1.0
            ang = math.atan2(pz, py)
            out_rate = R.uniform(.10, .45) if kind == 'strip' else R.uniform(-.15, .35)
            if pz < -.25:
                out_rate = R.uniform(-.10, .06)
            swirl = R.uniform(-.35, .35)
            droop = R.uniform(-.02, .07)
            path = []
            for k in range(nseg + 1):
                u = k / nseg
                x = x0 + ln * u
                r = rad(min(x, Lt + 1.0)) * (math.hypot(py, pz) * rf + out_rate * u * u)
                a = ang + swirl * u * u
                ccy, ccz = ctr(x)
                path.append(Vector((x, ccy + r * math.cos(a), ccz + r * math.sin(a) + droop * u * u)))
            side0 = Vector((0, -math.sin(ang), math.cos(ang)))
            _strip_mesh(bm, path, w0, t0, side0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    _bundle_mesh(bm, 'Snap_TrunkBundleStrips', mat, col_, coll)


def wood_bundles11_v2(V, tr, low, coll):
    """B 倒幹斷端：6 束有厚度的木束（扇形截面），從完整木幹裡面連續長出來；縱裂從幹內 0 寬慢慢張開、
    深淺不一；每束末端長短錯落、尖端收窄成劈裂的木片（不是平切圓口，也不是等距鋸齒）。"""
    import bmesh
    L, Rr = V['L'], V['R']
    Lt = L - V.get('trunk_cut', 0.0)
    tp = trunk_pts(V)
    (xa_, ya_, za_), (xb_, yb_, zb_) = tp[-2][:3], tp[-1][:3]
    dyx, dzx = (yb_ - ya_) / (xb_ - xa_), (zb_ - za_) / (xb_ - xa_)

    def ctr(x):
        return yb_ + dyx * (x - xb_), zb_ + dzx * (x - xb_)
    R = random.Random(V['seed'] + 1661)
    nb = 6
    ws = [R.uniform(.55, 1.5) for _ in range(nb)]
    a0 = R.uniform(0, 2 * math.pi)
    bnd, acc = [a0], a0
    for w_ in ws:
        acc += w_ / sum(ws) * 2 * math.pi
        bnd.append(acc)
    ext = [R.uniform(.08, .36) for _ in range(nb)]
    ext[R.randrange(nb)] = .52
    ext[R.randrange(nb)] = .04
    mat = tr.data.materials[0]
    col_ = tr.users_collection[0]
    ns = 10 if low else 26
    mo = 4 if low else 9
    for i in range(nb):
        t0, t1 = bnd[i], bnd[i + 1]
        tm = (t0 + t1) / 2
        gmax = R.uniform(.05, .16)                        # 縱裂張開角度（深淺不同）
        bul = R.uniform(.96, 1.0)                         # 木束厚薄（不往外鼓成方塊）
        rin = R.uniform(.40, .55)                         # 束的內緣：一圈環狀木束，不切到圓心（末端看不會收成星形扇面）
        x_a = Lt - .30
        sl, ph_ = R.uniform(.12, .32), R.random() < .5          # 末端：順著截面斜斷的劈面（長短在束與束之間錯落），不逐點亂跳成尖刺
        lens = []
        for j in range(mo):
            f_ = j / (mo - 1)
            f_ = 1 - f_ if ph_ else f_
            lens.append(Lt + ext[i] * (1 - sl * f_ + .06 * R.uniform(-1, 1)))
        lens += [Lt + ext[i] * (1 - sl) * .70, Lt + ext[i] * (1 - sl * .4) * .70]          # 內緣稍短
        sec = [(t0 + (t1 - t0) * j / (mo - 1), 1.0) for j in range(mo)] + [(t1 - (t1 - t0) * .3, rin), (t0 + (t1 - t0) * .3, rin)]
        bm = bmesh.new()
        rows = []
        for kk in range(ns + 1):
            u = kk / ns
            row = []
            for j, (th, rf) in enumerate(sec):
                x = x_a + u * (lens[j] - x_a)
                g = _sm((x - (Lt - .22)) / .45)                  # 裂縫從幹內慢慢張開
                th2 = tm + (th - tm) * (1 - g * gmax * 2 / max(.3, t1 - t0))
                tip = .25 * _sm((x - Lt - .25 * ext[i]) / max(.05, .75 * ext[i]))     # 尖端只略收（不收成尖瓣）
                r = trunk_r(V, min(x, Lt)) * (1 + (bul - 1) * _sm((x - (Lt - .25)) / .55)) * (1 + .03 * _sm((x - Lt) / .5))
                r *= 1 + .05 * fb(Vector((x * 1.4, math.cos(th) * 2.5, math.sin(th) * 2.5)), 1.0, 2)
                rr = r * rf if rf < 1 else r * (1 - .12 * tip)
                rm = r * (rin + .35 * (1 - rin))                 # 尖端：芯那側往外收薄（木片變薄，不收成尖）
                th3 = tm + (th2 - tm) * (1 - .22 * tip)          # 尖端只略收（劈裂木片），不往中心收成花苞
                cy, cz = ctr(x)
                row.append(bm.verts.new((x, cy + rr * math.cos(th3), cz + rr * math.sin(th3))) if rf >= 1 else
                           bm.verts.new((x, cy + (rr + (rm - rr) * tip) * math.cos(th3), cz + (rr + (rm - rr) * tip) * math.sin(th3))))
            rows.append(row)
        m = len(sec)
        for kk in range(ns):
            for j in range(m):
                j2 = (j + 1) % m
                bm.faces.new((rows[kk][j], rows[kk][j2], rows[kk + 1][j2], rows[kk + 1][j]))
        bm.faces.new(rows[0][::-1])
        bm.faces.new(rows[-1])
        bm.normal_update()
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        _bundle_mesh(bm, f'Snap_TrunkBundle{i}', mat, col_, coll)
    core11(V, Lt, ctr, R, mat, col_, coll, ns, low)


def _bundle_mesh(bm, name, mat, col_, coll):
    me = bpy.data.meshes.new('DR11_' + name)
    bm.to_mesh(me)
    bm.free()
    uv = me.uv_layers.new(name='UV')                     # 樹皮材質要 UV 與 Mask 頂點色（沒有時斷端會黑成一片）
    pa = me.uv_layers.new(name='Param')
    for lp in me.loops:
        c = me.vertices[lp.vertex_index].co
        uv.data[lp.index].uv = ((math.atan2(c.z - .3, c.y) / (2 * math.pi)) * 2.0, c.x / 2.6)          # 2.6 m：和 dr_core 的 TILE 一致
        pa.data[lp.index].uv = (math.atan2(c.z - .3, c.y) / (2 * math.pi) + .5, c.x)
    ca = me.color_attributes.new('Mask', 'FLOAT_COLOR', 'CORNER')
    for d_ in ca.data:
        d_.color = (0.0, .62, .30, 1.0)                  # R 苔＝0（斷面、木片不長苔）、G 中間高度、B 少量稜溝
    for p_ in me.polygons:
        p_.use_smooth = len(p_.vertices) <= 4           # 斷面（多邊形封口）平面著色：讀成劈開的木面，不是圓頂
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    col_.objects.link(ob)
    if isinstance(coll, list):
        coll.append(ob)


def core11(V, Lt, ctr, R, mat, col_, coll, ns, low):
    """木芯：環狀木束中間一根較短、參差斷開的芯（填滿中心，不留圓心扇面）。"""
    import bmesh
    m = 8 if low else 14
    ec = R.uniform(-.08, .02)                         # 芯比外圈木束短、略往內縮
    rc = R.uniform(.42, .52)
    phc = R.uniform(0, 6.3)
    lens = [Lt + ec * (.55 + .45 * math.cos(2 * math.pi * j / m - phc)) + .012 * R.uniform(-1, 1) for j in range(m)]      # 芯也是斜斷面，不是一圈尖刺
    bm = bmesh.new()
    rows = []
    x_a = Lt - .30
    for kk in range(ns + 1):
        u = kk / ns
        row = []
        for j in range(m):
            th = 2 * math.pi * j / m
            x = x_a + u * (lens[j] - x_a)
            r = trunk_r(V, min(x, Lt)) * rc * (1 + .08 * fb(Vector((x * 2.0, math.cos(th) * 2, math.sin(th) * 2)), 1.0, 2))
            cy, cz = ctr(x)
            row.append(bm.verts.new((x, cy + r * math.cos(th), cz + r * math.sin(th))))
        rows.append(row)
    for kk in range(ns):
        for j in range(m):
            j2 = (j + 1) % m
            bm.faces.new((rows[kk][j], rows[kk][j2], rows[kk + 1][j2], rows[kk + 1][j]))
    bm.faces.new(rows[0][::-1])
    bm.faces.new(rows[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    _bundle_mesh(bm, 'Snap_TrunkCore', mat, col_, coll)


def ground_hole11(V):
    """預覽地面：坑這塊地形塊的範圍挖掉（地形塊外圈剛好在 z = 0 接上）。"""
    g = bpy.data.objects.get('DR_Ground')
    if g is None or not V.get('dig'):
        return
    cx, ax_, ay = pit_frame11(V)
    na, S = 96, 120.0
    vs, fs = [], []
    for j in range(na):
        t = 2 * math.pi * j / na
        vs.append((cx + math.cos(t) * ax_ * PIT_RMAX, math.sin(t) * ay * PIT_RMAX, 0.0))
    for j in range(na):
        t = 2 * math.pi * j / na
        vs.append((cx + math.cos(t) * S, math.sin(t) * S, 0.0))
    for j in range(na):
        j2 = (j + 1) % na
        fs.append((j, j2, na + j2, na + j))
    me = bpy.data.meshes.new('DR_GroundHole')
    me.from_pydata(vs, [], fs)
    for m in g.data.materials:
        me.materials.append(m)
    g.data = me



_build6 = build


def crown(V, coll, low):
    """根面中心（原本樹幹正下方）一團扁的根結：粗根從這裡放射出去；也蓋住泥丘網格在中心收成一點的地方。"""
    import bmesh
    g = plate_geom(V)
    k = g['k']
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2 if low else 4, radius=1.0)
    x0 = face_x(V, 0.0, g['zc'], V['seed'])
    for v in bm.verts:
        d = v.co.copy()
        lob = 1 + .28 * fb(d * 1.6 + Vector((V['seed'], 0, 0)), 1.0, 3) + .10 * fb(d * 4.5, 1.0, 2)
        v.co = Vector((x0 + .05 * k + d.x * .26 * k * lob, d.y * .52 * k * lob, g['zc'] + d.z * .46 * k * lob))
    me = bpy.data.meshes.new('DR11_Crown')
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    obs = coll if isinstance(coll, list) else list(coll.objects)
    tr = next(o for o in obs if o.name.split('.')[0].endswith('Trunk'))
    me.materials.append(tr.data.materials[0])
    ob = bpy.data.objects.new(tr.name.replace('Trunk', 'Crown'), me)
    tr.users_collection[0].objects.link(ob)
    if isinstance(coll, list):
        coll.append(ob)
    return ob


def face_roots11(V, coll, low):
    """參考 A 正面：一條很粗的主根從盤底往上、微微 S 形貫穿盤面（原本樹幹正下方的主根），頂上分成兩三叉；
    枝根沿主根兩側長出去，一邊往外一邊往上或往下彎，再分叉，像一棵樹貼在泥牆上。
    根的中心離泥面約半徑的 0.3–0.55（半埋），位置用 face_x 反求實際泥面（高低模一樣）。"""
    g = plate_geom(V)
    k, Re, zc = g['k'], g['Re'], g['zc']
    wd = V.get('wide', 1.0)
    R = random.Random(V['seed'] + 901)
    obs = coll if isinstance(coll, list) else list(coll.objects)
    tr = next(o for o in obs if o.name.split('.')[0].endswith('Trunk'))
    mat = tr.data.materials[0]
    col_ = tr.users_collection[0]
    made = []

    def inside(y, z, lim):
        return (y / (Re * wd)) ** 2 + ((z - zc) / Re) ** 2 < lim * lim

    def mk(name, p2, rs, emb, seed_, tail=True, head_in=False):
        """p2：泥面上的 (y, z) 折線；rs：每點半徑；emb：根中心離泥面（×半徑）。"""
        pts = []
        for (y, z), rr in zip(p2, rs):
            pts.append((face_x(V, y, z, V['seed']) - rr * emb, y, z, rr, 1.0))
        if head_in:          # 起點埋進母根（不然是一截懸空的管口）
            x, y, z, rr, fl = pts[0]
            pts[0] = (x + rr * 1.3, y, z, rr * .75, fl)
        if tail:             # 末端捲過唇口、鑽進泥裡
            x, y, z, rr, fl = pts[-1]
            pts.append((x + rr * 2.0 + .10 * k, y * 1.02, z + (z - zc) * .02, rr * .7, fl))
        if len(pts) < 3 or min(p[2] for p in pts) < -.05:
            return None
        o = tube(name, pts, seed_, rib=.20, twist=.10, collection=col_, moss_bias=-.6, cap_end=True)
        o.data.materials.append(mat)
        made.append(o)
        return pts

    def walk(p0, th, r0, r1, lim, bend, seed_):
        """從 p0 往 th 方向走到盤邊（橢圓 lim），方向慢慢轉（bend：每步轉角，帶小擺動），回傳折線與半徑。"""
        Rw = random.Random(seed_)
        st = (.09 if low else .06) * k * 1.6
        p = Vector((p0[0], p0[1]))
        ps = [(p.x, p.y)]
        ph = Rw.uniform(0, 6.3)
        for i in range(80):
            th += bend + .06 * math.sin(i * .7 + ph)
            p = p + Vector((math.cos(th), math.sin(th))) * st
            if not inside(p.x, p.y, lim):
                break
            ps.append((p.x, p.y))
        n = len(ps)
        rs = [r0 + (r1 - r0) * (i / max(1, n - 1)) ** .9 for i in range(n)]
        return ps, rs

    def branch(p0, th, r0, depth, seed_, tag, lim):
        Rb = random.Random(seed_)
        side = 1 if math.cos(th) >= 0 else -1
        up = 1 if math.sin(th) >= -.05 else -1
        bend = side * up * Rb.uniform(.006, .014)          # 往上斜的越走越往上、往下的越走越往下（像樹枝和根），不會互相交叉成籠子
        ps, rs = walk(p0, th, r0, max(.02, r0 * .48), lim, bend, seed_)
        if len(ps) < 3:
            return
        rs[0] *= 1.30          # 接合處喇叭口：起點在母根中心、比枝根粗一點，和母根圓順接上
        rs[1] *= 1.12
        pts = mk(f'{tag}', ps, rs, .55 if depth else .45, seed_, head_in=False)
        if not pts or depth >= 2:
            return
        nk = 2 if depth == 0 else 1
        for j in range(nk):
            i = int(len(ps) * Rb.uniform(.30, .65) if j == 0 else len(ps) * Rb.uniform(.55, .80))
            i = max(1, min(len(ps) - 2, i))
            dth = math.atan2(ps[i + 1][1] - ps[i - 1][1], ps[i + 1][0] - ps[i - 1][0])
            sg = side * up          # 分叉往外張（往盤邊），不往主根那側折回來
            branch(ps[i], dth + sg * Rb.uniform(.30, .52), rs[i] * Rb.uniform(.66, .80), depth + 1, seed_ + 37 * (j + 1), f'{tag}k{j}', lim)

    # 主根：盤底中間往上，S 形，頂上分叉
    zb, zt = zc - .92 * Re, zc + .62 * Re
    sp, rs = [], []
    ns = 10 if low else 22
    r0 = k * V.get('spine_r', .34)
    for i in range(ns + 1):
        u = i / ns
        z = zb + (zt - zb) * u
        y = Re * (.16 * math.sin(u * 3.6 + .6) - .05)
        sp.append((y, z))
        rs.append(r0 * (1.25 - .50 * u))
    spine = mk('FaceSpine', sp, rs, .40, V['seed'] + 905, tail=False)
    for t_ in range(V.get('ntwine', 2) if spine else 0):          # 參考：主根有扭轉的紋路——兩條細根螺旋纏上去
        tw = twine(spine, R, r0 * R.uniform(.20, .28), R.uniform(1.1, 1.6) * k)
        if tw:
            o = tube(f'FaceSpineTw{t_}', tw, V['seed'] + 990 + t_, rib=.12, twist=.06, collection=col_, moss_bias=-.6, cap_end=True)
            o.data.materials.append(mat)
            made.append(o)
    # 頂上兩三叉：往上、往左右上斜伸到盤邊
    top = sp[-1]
    for j, th in enumerate((math.pi / 2 + .55, math.pi / 2 - .45, math.pi / 2 + .05)):
        branch(sp[-3], th, rs[-3] * (.88 if j < 2 else .65), 1 if j == 2 else 0, V['seed'] + 930 + j, f'FaceTop{j}', .95)
    # 兩側枝根：沿主根交錯長出，下段往外往下彎、上段往外往上斜
    nb = V.get('nbranch', 9)
    for b in range(nb):
        u = .10 + .74 * (b + R.uniform(-.25, .25)) / (nb - 1)
        i = max(1, min(ns - 1, int(u * ns)))
        sg = 1 if b % 2 == 0 else -1
        lift = (u - .45) * 1.15 + R.uniform(-.10, .10)          # 下段往下、上段往上（參考：像樹枝往上斜、像根往下彎）
        th = (0.0 if sg > 0 else math.pi) + sg * lift
        branch(sp[i], th, rs[i] * R.uniform(.66, .80), 0, V['seed'] + 960 + 41 * b, f'FaceBr{b:02d}', R.uniform(.92, .97))
    # 根腳：主根底部左右各兩條，斜著往兩側伸、再往下彎進盤底（補左下、右下的空區；參考圖底部的根往兩旁攤開）
    for j, (ub, th, rk) in enumerate(((.13, -.55, .74), (.13, math.pi + .55, .74), (.27, -.22, .60), (.27, math.pi + .22, .60))):
        i = max(1, int(ub * ns))
        th += R.uniform(-.08, .08)
        branch(sp[i], th, rs[i] * rk, 0, V['seed'] + 1100 + 17 * j, f'FaceFoot{j}', R.uniform(.93, .97))
    print('DR11_FACEROOTS', len(made))
    if isinstance(coll, list):
        coll.extend(made)
    return made


def cave_clear11(V, coll):
    """B：洞口前（洞的寬度、高度內，離洞底牆超過 25 cm）的根鬚、細枝根拿掉，洞口才看得出是開的；主根（FaceSpine）留著。"""
    g = plate_geom(V)
    depth, wy, ztop, eave = V['cave']
    Re, zc, wd = g['Re'], g['zc'], V.get('wide', 1.0)
    obs = coll if isinstance(coll, list) else list(coll.objects)
    dead = []
    for o in obs:
        nm = re.sub(r'\.\d{3}$', '', o.name)
        if o.type != 'MESH' or not nm.startswith(('Hair', 'FaceBr', 'FaceTw', 'FaceSpineTw', 'Sink', 'FaceRoot')):
            continue
        n_in = n = 0
        for v in list(o.data.vertices)[::5]:
            n += 1
            yy, zz = v.co.y / (Re * wd), (v.co.z - zc) / Re
            if abs(yy) < wy * .92 and zz < ztop - .05:
                n_in += 1
        if n and n_in / n > .45:
            dead.append(o)
    for o in dead:
        if isinstance(coll, list):
            coll.remove(o)
        bpy.data.objects.remove(o, do_unlink=True)
    print('CAVE cleared', len(dead), 'parts')


def crumble11(V, coll, low):
    """B：上半邊（從正面看右上，-Y 那側）崩掉一塊——泥丘輪廓往內咬一口、咬口表面粗糙；咬口裡的根面粗根拿掉，
    斷口留幾截短根頭；崩下來的土塊、碎根堆在下面地上。仰角之前做（根盤本身的座標）。"""
    import bmesh
    g = plate_geom(V)
    k, Re, zc, xp = g['k'], g['Re'], g['zc'], g['xp']
    wd = V.get('wide', 1.0)
    ang0, ang1 = [math.radians(a) for a in V['crumble']]           # 咬口在根盤圓周上的角度範圍（從 +Z 往 -Y 量）
    bite = V.get('bite', .42)
    R = random.Random(V['seed'] + 55)
    obs = coll if isinstance(coll, list) else list(coll.objects)

    def polar(y, z):
        return math.atan2(-y / wd, z - zc), math.hypot(y / wd, z - zc) / Re

    def amount(a, r):
        if a < ang0 - .25 or a > ang1 + .25:
            return 0.0
        e = min(_sm((a - ang0 + .25) / .5), _sm((ang1 + .25 - a) / .5))
        b = bite * (1 + .25 * fb(Vector((a * 3.0, 1.7, 0)), 1.0, 2))
        return e * _sm((r - (1 - b)) / max(b, 1e-3))                 # 0 = 不動，1 = 落在原本輪廓上
    mud = next(o for o in obs if re.sub(r'\.\d{3}$', '', o.name).endswith('Mud'))
    me = mud.data
    for v in me.vertices:
        a, r = polar(v.co.y, v.co.z)
        w = amount(a, r)
        b = bite * (1 + .25 * fb(Vector((a * 3.0, 1.7, 0)), 1.0, 2))
        if V.get('crumble_soft'):                        # B 第七版：整條徑向等比往內縮（單調，不會擠出一層層水平摺痕）
            e_ = min(_sm((a - ang0 + .25) / .5), _sm((ang1 + .25 - a) / .5)) if ang0 - .25 < a < ang1 + .25 else 0.0
            if e_ <= 0:
                continue
            w = e_ * _sm((r - .35) / .55)
            r2 = r * (1 - .85 * b * w * (1 + V.get('crumble_n', .35) * fb(v.co * 1.6, 1.0, 2)))
        else:
            if w <= 0:
                continue
            r2 = r - w * b * (1.0 + V.get('crumble_n', .35) * fb(v.co * 3.5, 1.0, 3))       # 往內咬，邊緣參差
        d = Vector((0, -math.sin(a) * wd, math.cos(a)))
        q = Vector((v.co.x, 0, zc)) + d * (r2 * Re)
        q.x += w * V.get('crumble_x', .10) * k * fb(v.co * 6.0, 1.0, 2)                 # 斷面粗糙
        v.co = q
    me.update()
    # 咬口裡的根面粗根、根鬚、石頭拿掉
    dead = []
    for o in obs:
        nm = re.sub(r'\.\d{3}$', '', o.name)
        if o.type != 'MESH' or o is mud or nm.endswith(('Pit', 'Clods', 'Trunk')):
            continue
        cs = [Vector(c) for c in o.bound_box]
        c = sum(cs, Vector()) / 8
        a, r = polar(c.y, c.z)
        if nm.endswith('Stones'):                        # 石頭是一整個物件：只刪咬口裡那幾顆（連通的一塊一塊）
            import bmesh as _bm
            b_ = _bm.new()
            b_.from_mesh(o.data)
            gone = set()
            for f in b_.faces:
                pass
            seen = set()
            for v in b_.verts:
                if v in seen:
                    continue
                isl, st = [], [v]
                seen.add(v)
                while st:
                    q = st.pop()
                    isl.append(q)
                    for e in q.link_edges:
                        w_ = e.other_vert(q)
                        if w_ not in seen:
                            seen.add(w_)
                            st.append(w_)
                cc = sum((q.co for q in isl), Vector()) / len(isl)
                if amount(*polar(cc.y, cc.z)) > .15:
                    gone.update(isl)
            _bm.ops.delete(b_, geom=list(gone), context='VERTS')
            b_.to_mesh(o.data)
            b_.free()
            continue
        mx = 0.0
        for v in list(o.data.vertices)[::7]:
            mx = max(mx, amount(*polar(v.co.y, v.co.z)))
        if amount(a, r) > .35 or (nm.startswith(('Face', 'Hair', 'Root', 'Plate', 'Dome', 'Snap')) and mx > .45):
            dead.append(o)
    for o in dead:
        if isinstance(coll, list):
            coll.remove(o)
        bpy.data.objects.remove(o, do_unlink=True)
    # 崩下來的土塊：堆在咬口正下方的地上
    am = (ang0 + ang1) / 2
    yb = -math.sin(am) * Re * wd * .95
    bm = bmesh.new()
    for i in range(V.get('ndebris', 16)):
        x = xp - R.uniform(.2, .9) * k
        y = yb + R.uniform(-.45, .45) * k
        s_ = k * R.uniform(.08, .22)
        b2 = bmesh.new()
        bmesh.ops.create_icosphere(b2, subdivisions=1 if low else 3, radius=1.0)
        off = Vector((R.uniform(-9, 9), R.uniform(-9, 9), R.uniform(-9, 9)))
        for q in b2.verts:
            d = q.co.copy()
            rr = 1 + .35 * fb(d * 1.3 + off, 1.0, 2) + .12 * fb(d * 4.5 + off, 1.0, 2)
            q.co = Vector((x + d.x * s_ * rr * 1.1, y + d.y * s_ * rr * .9, pit_height11(V, x, y) + s_ * .45 + d.z * s_ * rr * .6))
        me2 = bpy.data.meshes.new('tmp11')
        b2.to_mesh(me2)
        b2.free()
        bm.from_mesh(me2)
        bpy.data.meshes.remove(me2)
    me3 = bpy.data.meshes.new('DR11_Debris')
    bm.to_mesh(me3)
    bm.free()
    for p_ in me3.polygons:
        p_.use_smooth = True
    at = me3.attributes.new('MudMoss', 'FLOAT', 'POINT')
    at.data.foreach_set('value', np.zeros(len(me3.vertices), np.float32))
    me3.materials.append(mud.data.materials[0])
    ob = bpy.data.objects.new('Clods_Debris', me3)
    mud.users_collection[0].objects.link(ob)
    if isinstance(coll, list):
        coll.append(ob)
    print('CRUMBLE removed', len(dead), 'parts')


def clods11(V, coll, low):
    """坑邊翻起的土塊：沿堤頂一圈大大小小的扁土團（用坑的泥材質），坑底再散幾塊。"""
    import bmesh
    g = plate_geom(V)
    cx, ax_, ay = pit_frame11(V)
    R = random.Random(V['seed'] + 77)
    obs = coll if isinstance(coll, list) else list(coll.objects)
    pit_o = next(o for o in obs if o.name.split('.')[0].endswith('Pit'))
    bm = bmesh.new()
    n = V.get('nclod', 26)
    for i in range(n):
        inner = i >= n - 5
        t = R.uniform(0, 2 * math.pi)
        rho = (R.uniform(.1, .45) if V.get('dig') else R.uniform(.2, .7)) if inner else R.uniform(.88, 1.10)
        x, y = cx + math.cos(t) * ax_ * rho, math.sin(t) * ay * rho
        if x > g['xp'] - g['Tm'] * .5:                   # 不要塞到根盤底下
            continue
        s_ = g['k'] * (R.uniform(.06, .12) if inner else R.uniform(.08, .22))
        z0 = (-.02 if inner else V.get('pit_rim', .46) * g['k'] * .75) + s_ * .15
        if V.get('dig'):
            z0 = pit_height11(V, x, y) + s_ * .20
        b2 = bmesh.new()
        bmesh.ops.create_icosphere(b2, subdivisions=1 if low else 3, radius=1.0)
        off = Vector((R.uniform(-9, 9), R.uniform(-9, 9), R.uniform(-9, 9)))
        a = R.uniform(0, math.pi)
        ca, sa = math.cos(a), math.sin(a)
        for q in b2.verts:
            d = q.co.copy()
            rr = 1 + .30 * fb(d * 1.3 + off, 1.0, 2) + .14 * fb(d * 4.5 + off, 1.0, 2)
            dx, dy, dz = d.x * 1.15, d.y * .85, d.z * .60
            q.co = Vector((x + (dx * ca - dy * sa) * s_ * rr, y + (dx * sa + dy * ca) * s_ * rr, z0 + dz * s_ * rr))
        me2 = bpy.data.meshes.new('tmp11')
        b2.to_mesh(me2)
        b2.free()
        bm.from_mesh(me2)
        bpy.data.meshes.remove(me2)
    me = bpy.data.meshes.new('DR11_Clods')
    bm.to_mesh(me)
    bm.free()
    for p_ in me.polygons:
        p_.use_smooth = True
    at = me.attributes.new('MudMoss', 'FLOAT', 'POINT')
    at.data.foreach_set('value', np.zeros(len(me.vertices), np.float32))
    me.materials.append(pit_o.data.materials[0])
    ob = bpy.data.objects.new(pit_o.name.replace('Pit', 'Clods'), me)
    pit_o.users_collection[0].objects.link(ob)
    if isinstance(coll, list):
        coll.append(ob)
    return ob


MOSS11_C = ((.016, .030, .010, 1), (.060, .092, .030, 1))       # 參考：頂上的苔是深綠（DR06 的苔偏黃綠）


def moss_mat11(mud_mat):
    """頂上苔皮與垂苔用：複製泥材質，只把苔色換深綠（DR06 的泥材質不動）。"""
    m = bpy.data.materials.get('DR11_MossCap')
    if m:
        return m
    m = mud_mat.copy()
    m.name = 'DR11_MossCap'
    for n in m.node_tree.nodes:
        if n.type == 'VALTORGB':
            e = n.color_ramp.elements
            if tuple(round(c, 3) for c in e[1].color) == tuple(round(c, 3) for c in MOSS_C[1]):
                e[0].color, e[1].color = MOSS11_C
    return m


def hang_moss11(V, cap, n=70):
    """根面上緣垂下來的苔：一叢叢從上緣散下的細苔絲（每叢 3–7 縷），沿根面（含根）往下垂，長短不一，下半稍微離開根面。"""
    import bmesh
    g = plate_geom(V)
    k = g['k']
    R = random.Random(V['seed'] + 313)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    sc = bpy.context.scene
    me_c = cap.data
    bm0 = bmesh.new()
    bm0.from_mesh(me_c)
    edge = [v.co.copy() for v in bm0.verts if v.is_boundary and v.co.x < g['xp'] + .25 + v.co.z * math.tan(math.radians(V.get('tilt', 0.0))) and v.co.z > 1.2 * plate_geom(V)['k'] / .89]      # 仰角：根面上緣往 +X 移
    bm0.free()
    if not edge:
        return None
    bm = bmesh.new()
    made = 0
    def strand(pts, w0, t0):
        rings = []
        for j, (q, nrm) in enumerate(pts):
            u = j / (len(pts) - 1)
            w = w0 * (1 - u) ** .8 + .0025
            t_ = t0 * (1 - .6 * u) + .0015
            ring = []
            for a_ in range(5):
                th = 2 * math.pi * a_ / 5
                ring.append(bm.verts.new((q.x + math.cos(th) * t_, q.y + math.sin(th) * w * (1 + .3 * fb(q * 40, 1.0, 1)), q.z)))
            rings.append(ring)
        for j in range(len(rings) - 1):
            for a_ in range(5):
                b_ = (a_ + 1) % 5
                bm.faces.new((rings[j][a_], rings[j][b_], rings[j + 1][b_], rings[j + 1][a_]))
        bm.faces.new(list(reversed(rings[-1])))

    nw_all = 0
    for i in range(n * 3):                                # 第十一版回饋：垂苔太粗像胡蘿蔔 → 每叢上端一小撮，往下散成 3–7 縷細絲，長短不一、往兩側岔開、下半離開根面一點
        if made >= n:
            break
        p0 = edge[R.randrange(len(edge))]
        Lc = R.uniform(.15, .60) * k
        cv = V.get('cave')
        if cv and abs(p0.y) < cv[1] * plate_geom(V)['Re'] * V.get('wide', 1.0) * .85:
            Lc *= .45                                     # B：洞口上緣的垂苔短一點，不要把洞口整片遮住
        nw = R.randint(3, 7)
        ok_any = False
        for wi in range(nw):
            L_ = Lc * R.uniform(.45, 1.1)
            dy = R.uniform(-.09, .09) * k
            ph = R.uniform(0, 6.3)
            y0 = p0.y + R.uniform(-.02, .02)
            ns = 10
            pts = []
            xprev = None
            for j in range(ns + 1):
                u = j / ns
                z = p0.z + .02 - L_ * u
                y = y0 + dy * u ** 1.3 + .012 * k * math.sin(ph + u * 7.0) * u
                ok, loc, nrm, _, ob, _ = sc.ray_cast(dg, Vector((p0.x - 4, y, z)), Vector((1, 0, 0)))
                if not ok:
                    break
                lx = loc.x
                if xprev is not None:
                    if lx < xprev - .04:                  # 泥面往前凸（台階、根、土塊）：垂苔停在這裡，不沿台階折出去（會在斜看時變一層層橫條）
                        break
                    lx = min(lx, xprev + .015)           # 泥面往後退：垂苔懸空往下，只稍微往裡飄
                xprev = lx
                pts.append((Vector((lx, loc.y, loc.z)) - Vector((.010 + .035 * u ** 1.5 * R.uniform(.5, 1.0), 0, 0)), nrm))
            if len(pts) < 3:
                continue
            strand(pts, R.uniform(.006, .016) * k, .004 * k)
            nw_all += 1
            ok_any = True
        if ok_any:
            made += 1
    me = bpy.data.meshes.new('DR11_HangMoss')
    bm.to_mesh(me)
    bm.free()
    for p_ in me.polygons:
        p_.use_smooth = True
    at = me.attributes.new('MudMoss', 'FLOAT', 'POINT')
    at.data.foreach_set('value', np.ones(len(me.vertices), np.float32))
    me.materials.append(cap.data.materials[0])
    ob = bpy.data.objects.new('DR11_HangMoss', me)
    sc.collection.objects.link(ob)
    print('HANGMOSS', made, 'clumps', nw_all, 'wisps', len(me.polygons), 'faces')
    return ob


def hang_cards11(V, R, surf_obj, mat, n=60):
    """遊戲版垂苔：從苔的下緣（照高模苔皮同一套選面規則，在遊戲低模上找）往下垂的細長葉片，每處 2–3 片、20–50 cm。"""
    import bmesh
    g = plate_geom(V)
    k = g['k']
    tmp = moss_cap11(V, mud=surf_obj, name='DR11_TmpCap')
    if tmp is None:
        return None
    bm0 = bmesh.new()
    bm0.from_mesh(tmp.data)
    edge = [(v.co.copy(), v.normal.copy()) for v in bm0.verts if v.is_boundary and v.co.x < g['xp'] + .2 + v.co.z * math.tan(math.radians(V.get('tilt', 0.0))) and v.co.z > 1.4 * k / .89 and v.normal.x < -.2]
    bm0.free()
    bpy.data.objects.remove(tmp, do_unlink=True)
    if not edge:
        return None
    buf = core_plants.LeafBuf()
    made = 0
    for i in range(n):
        p0, nr = edge[R.randrange(len(edge))]
        for j in range(R.randint(3, 5)):
            d = Vector((R.uniform(-.35, -.15), R.uniform(-.25, .25), -1)).normalized()
            d, side, up = core_plants._frame(d)
            L = R.uniform(.10, .45) * k
            ph = R.uniform(0, 6.3)
            buf.leaf(p0 + nr * .02 + Vector((0, R.uniform(-.06, .06), R.uniform(-.04, .02))), d, side, up, L, R.uniform(.010, .026) * k,
                     shape=lambda q, ph=ph: (1 - q) ** 1.1 * (.55 + .45 * abs(math.sin(q * 13.0 + ph))), fold=.10, droop=R.uniform(0, .3),
                     tint=(1, 1, 1), nu=6, nv=1, twist=R.uniform(-.4, .4))
            made += 1
    # 苔的輪廓：頂上、上緣一叢叢短苔片（4–9 cm），往外冒；苔皮在低模上是光滑的弧面，輪廓要靠這些片
    sc = bpy.context.scene
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    wd = g['Re'] * V.get('wide', 1.0)
    nt = 0
    for i in range(V.get('nmoss_cards', 220) * 4):
        if nt >= V.get('nmoss_cards', 220):
            break
        x = g['xp'] + R.uniform(-1.6, 1.8) * g['Tp'] + (g['zc'] + g['Re']) * math.tan(math.radians(V.get('tilt', 0.0)))
        y = R.uniform(-.95, .95) * wd
        ok, loc, nrm, _, ob, _ = sc.ray_cast(dg, Vector((x, y, 12.0)), Vector((0, 0, -1)))
        if not ok or ob.name != surf_obj.name or nrm.z < .15 or loc.z < max(e[0].z for e in edge) - .9 * k:
            continue
        for j in range(R.randint(4, 7)):
            d = (nrm * 1.2 + Vector((R.uniform(-.6, .6), R.uniform(-.6, .6), R.uniform(-.2, .4)))).normalized()
            d, side, up = core_plants._frame(d)
            buf.leaf(loc - nrm * .01 + Vector((R.uniform(-.04, .04), R.uniform(-.04, .04), 0)), d, side, up, R.uniform(.04, .09) * k, R.uniform(.012, .025) * k,
                     shape=lambda q: (1 - q) ** .7, fold=.3, droop=R.uniform(.2, .7), tint=(1, 1, 1), nu=2, nv=1)
        nt += 1
    print('HANGCARDS', made, 'top tufts', nt)
    return buf.build('DR11_HangMossCards', mat)


def grass11(name, V, R, mat, n=26, surf=None, top_z=None):
    """根盤頂上的草：從苔皮裡長出的一叢叢細長草葉（每叢 12–26 片、15–40 cm），往外、往前垂（使用者：上面要有草，不是蕨）。"""
    g = plate_geom(V)
    k = g['k']
    wd = g['Re'] * V.get('wide', 1.0)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    sc = bpy.context.scene
    buf = core_plants.LeafBuf()
    made = 0
    for i in range(n * 8):
        if made >= n:
            break
        x = g['xp'] + R.uniform(-.9, 1.4) * g['Tp'] + (g['zc'] + g['Re']) * math.tan(math.radians(V.get('tilt', 0.0)))
        y = R.uniform(-.85, .85) * wd
        ok, loc, nrm, _, ob, _ = sc.ray_cast(dg, Vector((x, y, 12.0)), Vector((0, 0, -1)))
        if not ok or nrm.z < .25 or not ('MossCap' in ob.name or (surf and ob.name in surf)) or (top_z is not None and loc.z < top_z - .7):
            continue
        nb = R.randint(12, 26)
        H = R.uniform(.15, .40) * k
        out_ = Vector((nrm.x, nrm.y, 0)).normalized() if Vector((nrm.x, nrm.y)).length > 1e-3 else Vector((-1, 0, 0))
        for b in range(nb):
            a = R.uniform(0, 2 * math.pi)
            r = R.uniform(0, .05) * k
            p = loc + Vector((math.cos(a) * r, math.sin(a) * r, -.01))
            lean = R.uniform(.15, .65)
            d = (Vector((0, 0, 1)) + out_ * lean * .8 + Vector((math.cos(a), math.sin(a), 0)) * lean * .5).normalized()
            d, side, up = core_plants._frame(d)
            L = H * R.uniform(.55, 1.15)
            gg = R.uniform(.75, 1.2)
            buf.leaf(p, d, side, up, L, R.uniform(.005, .010) * k, shape=lambda q: (1 - q) ** .5, fold=.4,
                     droop=R.uniform(.3, 1.0), curl=R.uniform(-.1, .2), tint=(gg * R.uniform(.95, 1.15), gg, gg * .7), nu=6, nv=1)
        made += 1
    print('GRASS11', made, 'tufts')
    return buf.build(name, mat)


def moss_fuzz11(name, obs, R, mat, per_m2=4200, hang=False):
    """苔的細絲：在苔皮／垂苔表面按面積撒短葉片（1–3.5 cm），朝法線冒出、帶一點下垂；垂苔上的往下梳。
    第十版回饋「苔看起來像泥土捏出來的」：光靠鼓起的網格只有團塊，沒有苔的毛茸茸，要有一層真的細絲。"""
    buf = core_plants.LeafBuf()
    n_all = 0
    for ob in obs:
        me = ob.data
        me.calc_loop_triangles()
        tris = me.loop_triangles
        areas = np.array([t.area for t in tris])
        tot = float(areas.sum())
        if tot <= 0:
            continue
        cum = np.cumsum(areas) / tot
        cnt = int(tot * per_m2)
        idx = np.searchsorted(cum, np.array([R.random() for _ in range(cnt)]))
        vs = me.vertices
        for ti in idx:
            t = tris[min(int(ti), len(tris) - 1)]
            a, b, c = (vs[j].co for j in t.vertices)
            u, v = R.random(), R.random()
            if u + v > 1:
                u, v = 1 - u, 1 - v
            p = a + (b - a) * u + (c - a) * v
            nrm = t.normal.copy()
            tuft = .5 + .5 * fb(p * 14.0, 1.0, 2)
            d = nrm + Vector((R.uniform(-.55, .55), R.uniform(-.55, .55), R.uniform(-.35, .25)))
            if hang:
                d = d * .6 + Vector((0, 0, -1.0))
            d = d.normalized()
            d, side, up = core_plants._frame(d)
            L = R.uniform(.010, .028) * (.6 + .9 * tuft) * (1.5 if hang else 1.0)
            gg = R.uniform(.65, 1.15)
            buf.leaf(p - d * .004, d, side, up, L, L * .22, shape=lambda q: (1 - q) ** .6, fold=.3, droop=R.uniform(.1, .6),
                     tint=(gg * R.uniform(.8, 1.05), gg, gg * .75), nu=2, nv=1)
            n_all += 1
    print('MOSSFUZZ', name, n_all, 'blades')
    return buf.build(name, mat)


def moss_cap11(V, top_z=None, mud=None, name='DR11_MossCap'):
    """頂上一層厚苔皮：從泥丘網格取頂面（根盤翻起前的地表），往外鼓 3–8 cm，下緣參差、朝根面那邊垂下幾條苔舌；用泥材質的苔色（MudMoss=1）。"""
    import bmesh
    if mud is None:
        mud = next((o for o in bpy.data.objects if o.type == 'MESH' and o.name.split('.')[0].endswith('Mud') and 'DR11' not in o.name), None)
    if mud is None:
        return None
    g = plate_geom(V)
    k = g['k']
    bm = bmesh.new()
    bm.from_mesh(mud.data)
    bm.transform(mud.matrix_world)
    bm.normal_update()
    wd = g['Re'] * V.get('wide', 1.0)
    zmax = max(v.co.z for v in bm.verts)
    kill = []
    for f in bm.faces:
        c = f.calc_center_median()
        ay_ = min(1.0, abs(c.y) / wd)
        n1 = fb(Vector((c.y * 1.6, c.x * .8, 4.4)), 1.0, 3)
        tongue = max(0.0, fb(Vector((c.y * 3.2, 0, 9.1)), 1.0, 2)) * (1.6 if c.x < g['xp'] else .4)
        drop = ((1.15 if c.x < .1 + c.z * math.tan(math.radians(V.get('tilt', 0.0))) else .70) + .25 * n1 + tongue) * k * (1 - .40 * ay_) * V.get('cap_k', 1.0)
        if c.z < zmax - drop or f.normal.z < -.35:
            kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context='VERTS')
    if not bm.faces:
        bm.free()
        return None
    # 邊緣往內收（厚度 0），中間鼓起；距邊界的圈數當權重
    ring = {v: 0 for v in bm.verts if v.is_boundary}
    front = list(ring)
    for d_ in range(1, 4):
        nxt = []
        for v in front:
            for e in v.link_edges:
                o = e.other_vert(v)
                if o not in ring:
                    ring[o] = d_
                    nxt.append(o)
        front = nxt
    for v in bm.verts:
        w = min(1.0, ring.get(v, 4) / 3.0)
        th = k * (.035 + .045 * abs(fb(v.co * 5.0, 1.0, 3)) + .02 * fb(v.co * 18.0, 1.0, 2) + .075 * max(0.0, fb(v.co * 2.6 + Vector((3.1, 0, 0)), 1.0, 2)))
        v.co = v.co + v.normal * (th * (.25 + .75 * w))
    me = bpy.data.meshes.new('DR11_MossCap')
    bm.to_mesh(me)
    bm.free()
    for p_ in me.polygons:
        p_.use_smooth = True
    at = me.attributes.get('MudMoss') or me.attributes.new('MudMoss', 'FLOAT', 'POINT')      # 從泥丘帶過來的舊苔量要覆寫
    at.data.foreach_set('value', np.ones(len(me.vertices), np.float32))
    me.materials.append(moss_mat11(mud.data.materials[0]))
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    print('MOSSCAP faces', len(me.polygons))
    return ob


def dress11(V, quick=True, game=False, surf=None):
    """頂上：翻起來還連著的一層森林地表——厚苔叢、一排往前垂的蕨；兩側腳下大蕨；坑邊蕈；坑裡、坑邊落葉。"""
    R = random.Random(V['seed'] + 900)
    g = plate_geom(V)
    coll = _coll(f"DR11_{V['name']}_Plants")
    lm = core_plants._leaf_material
    mat = lambda n, *a, **k: bpy.data.materials.get(n) or lm(n, *a, **k)
    fern_mat = mat('D2_Fern', (.050, .090, .040, 1), (.11, .17, .075, 1), (.16, .22, .11, 1), gloss=.55)
    moss_mat = mat('D2_MossTuft', (.040, .058, .014, 1), (.10, .125, .032, 1), (.12, .15, .045, 1), gloss=.8)
    litter_mat = mat('DR06_LitterLeaf', (.15, .07, .022, 1), (.42, .22, .07, 1), (.48, .30, .11, 1), gloss=.3)
    stem_mat = bpy.data.materials.get('D2_Stem')
    if stem_mat is None:
        stem_mat = bpy.data.materials.new('D2_Stem')
        stem_mat.use_nodes = True
        next(n for n in stem_mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.05, .06, .025, 1)
    mush_mat = bpy.data.materials.get('UG_Mushroom') or core_plants.mushroom_material()
    sc = bpy.context.scene
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()

    def hit(x, y, z0=12.0):
        ok, loc, nrm, _, ob, _ = sc.ray_cast(dg, Vector((x, y, z0)), Vector((0, 0, -1)))
        return (loc, nrm, ob.name) if ok else None

    def keep(o):
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
        return o

    out = []
    k = g['k']
    wd = V.get('wide', 1.0)
    zs = []
    for i in range(60):                                   # 先量根盤頂高
        h = hit(g['xp'] + R.uniform(-.3, .9) * g['Tp'], R.uniform(-.5, .5) * g['Re'] * wd)
        if h:
            zs.append(h[0].z)
    top_z = max(zs) if zs else g['zc'] + g['Re']
    ok_top = lambda h, dz=.55, nz=.30: h and h[0].z > top_z - dz and h[1].z > nz and 'Pit' not in h[2] and 'Clods' not in h[2]
    # 頂上：沿上緣的厚苔叢
    mounds = []
    for i in range(V.get('nmoss', 70)):
        y = R.uniform(-.92, .92) * g['Re'] * wd
        x = g['xp'] + R.uniform(-1.2, 1.6) * g['Tp']
        h = hit(x, y)
        if ok_top(h, .9 * (1 - .5 * abs(y) / (g['Re'] * wd)) + .25):
            mounds.append((i, h[0].x, h[0].y, R.uniform(.26, .46) * k, R.uniform(.18, .30) * k, R.uniform(.07, .13), h[0].z - .03))
    gr_mat = mat('DR11_Grass', (.030, .050, .014, 1), (.10, .14, .040, 1), (.15, .19, .065, 1), gloss=.5)
    out.append(keep(grass11('DR11_TopGrass', V, R, gr_mat, V.get('ngrass', 26), surf=surf, top_z=top_z)))
    if game and surf:                                    # 遊戲版：垂苔改成幾片往下垂的細長葉片（高模的細絲烘進貼圖，這裡補輪廓）
        hc = hang_cards11(V, R, bpy.data.objects[surf[0]], mat('DR11_MossFiber', (.012, .026, .008, 1), (.045, .080, .022, 1), (.070, .105, .035, 1), gloss=.7))
        if hc:
            out.append(keep(hc))
    if mounds:
        out.append(keep(core_plants.moss_tufts('DR11_MossTufts', mounds, R, moss_mat, fb, density=2600 if quick else 5200)))
    # 頂上：一排蕨
    nf, nt = 0, V.get('nfern_top', 8)
    for i in range(200):
        if nf >= nt:
            break
        y = (-.78 + 1.56 * (nf + R.uniform(.15, .85)) / nt) * g['Re'] * wd
        x = g['xp'] + R.uniform(-.6, 1.0) * g['Tp']
        h = hit(x, y)
        if not ok_top(h, .7 * (1 - .5 * abs(y) / (g['Re'] * wd)) + .2, .40):
            continue
        o, so = core_plants.fern(f'DR11_TopFern{nf}', h[0] - Vector((0, 0, .04)), R, R.uniform(.80, 1.10) * k, fern_mat, stem_mat)
        out += [keep(o), keep(so)]
        nf += 1
    # 兩側腳下：大蕨
    for j, sg in enumerate((-1, 1, -1, 1, -1)):
        y = sg * g['Re'] * wd * R.uniform(.92, 1.10)
        x = g['xp'] + R.uniform(-.2, .5) - (.9 if j > 1 else 0)
        h = hit(x, y)
        z = h[0].z if h and h[0].z < .5 else 0.0
        o, so = core_plants.fern(f'DR11_FootFern{j}', Vector((x, y, z - .02)), R, R.uniform(1.0, 1.35) * k, fern_mat, stem_mat)
        out += [keep(o), keep(so)]
    # 坑邊：幾叢蕈
    RP = V['RP']
    cx, ax_, ay = g['xp'] - g['Tm'] - RP * .42, RP * .52, RP * .82
    for j in range(1):
        t = R.uniform(.55, 1.45) * math.pi
        x, y = cx + math.cos(t) * ax_ * 1.15, math.sin(t) * ay * 1.15
        h = hit(x, y, 3.0)
        out.append(keep(core_plants.mushrooms(f'DR11_Mush{j}', Vector((x, y, (h[0].z if h else 0) - .02)), R, R.randint(3, 5), 1.5 * k, mush_mat, cap=MUSH_CAP)))

    def place():                                          # 落葉：坑底多、坑邊少
        t = R.uniform(0, 2 * math.pi)
        rho = math.sqrt(R.random()) * 1.3
        x, y = cx + math.cos(t) * ax_ * rho, math.sin(t) * ay * rho
        if x > g['xp'] - g['Tm']:
            return None
        h = hit(x, y, 3.0)
        z = h[0].z if h else 0.0
        if z > .6:
            return None
        return (x, y), z
    lo, n = litter('DR11_Litter', R, int(420 * (.6 if quick else 1.0)), place, litter_mat)
    out.append(keep(lo))
    print('DRESS11', len(out), 'objects, moss mounds', len(mounds), 'top ferns', nf, 'litter', n, 'top_z', round(top_z, 2))
    return coll


def build(variant='A', quick=True, low=None, col=False, pre=''):
    """DR06 的根盤＋短樹幹，再把整組（淺坑除外）繞根盤底的 Y 軸往後仰 tilt 度。"""
    coll = _build6(variant, quick, low, col, pre)
    V = VAR
    if not col:
        if V.get('crown'):
            crown(V, coll, bool(low))
        if V.get('nmain'):
            face_roots11(V, coll, bool(low))
        clods11(V, coll, bool(low))
        if V.get('crumble'):
            crumble11(V, coll, bool(low))
        if V.get('rootplan'):
            plan_roots11(V, coll, bool(low))
            back_roots11(V, coll, bool(low))
        elif V.get('fan'):
            fan_roots11(V, coll, bool(low))
        if V.get('cave'):
            cave_clear11(V, coll)
    if V.get('split_end') or V.get('dents'):
        trunk_shape11(V, coll, bool(low) or col)
    drop_ = ('Hair', 'Brackets', 'DomeRoot') if (GREY and not col) else ('DomeRoot',) if V.get('rootplan') else ()
    if drop_:                                            # 灰模：細垂根（根鬚）、背面細根拿掉；B 材質版也拿掉舊的背面放射細根（已由 back_roots11 取代，留著會在幹上排成一圈尖刺）
        for o in list(coll if isinstance(coll, list) else coll.objects):
            if re.sub(r'\.\d{3}$', '', o.name).startswith(drop_):
                if isinstance(coll, list):
                    coll.remove(o)
                bpy.data.objects.remove(o, do_unlink=True)
    for o in list(coll if isinstance(coll, list) else coll.objects):          # 空網格（B 不放石塊、層孔菌時留下的 0 面物件）拿掉：遊戲版拆 UV 會失敗
        if o.type == 'MESH' and len(o.data.polygons) == 0:
            if isinstance(coll, list):
                coll.remove(o)
            bpy.data.objects.remove(o, do_unlink=True)
    th = math.radians(V.get('tilt', 0.0))
    if th:
        g = plate_geom(V)
        piv = Vector((g['xp'], 0.0, 0.0))
        M = Matrix.Translation(piv) @ Matrix.Rotation(th, 4, 'Y') @ Matrix.Translation(-piv)
        for o in (coll if isinstance(coll, list) else coll.objects):
            if o.type == 'MESH' and not o.name.split('.')[0].endswith(('Pit', 'Clods', 'Debris')):     # 坑、坑邊土塊在地上，不跟著根盤仰
                o.data.transform(M)                          # 零件物件都在原點、沒有旋轉，直接轉網格
                o.data.update()
    if V.get('fit') and not col and V.get('rootplan'):
        Mt = (Matrix.Translation(piv) @ Matrix.Rotation(th, 4, 'Y') @ Matrix.Translation(-piv)) if th else Matrix.Identity(4)
        fit_roots11(V, coll, bool(low), Mt)
        n0 = set(o.name for o in bpy.data.objects)
        collapse_clods11(V, coll, bool(low))               # 用貼合後的根（換回仰角前座標）放土塊，再一起仰
        for o in bpy.data.objects:
            if o.name not in n0 and o.type == 'MESH':
                o.data.transform(Mt)
                o.data.update()
    if not col and not GREY:
        moss11(V, coll, quick, bool(low), pre)
    if pre:                                              # DR11 自己加的件（根面粗根、土塊、苔）也要帶前綴，遊戲版才對得回高模同名件
        for o in (coll if isinstance(coll, list) else list(coll.objects)):
            if not o.name.startswith(pre):
                o.name = pre + re.sub(r'\.\d{3}$', '', o.name)
                o.data.name = o.name
    return coll


def moss11(V, coll, quick, low, pre):
    """頂上苔皮（高模、低模都有：低模拿來烘苔色）；高模另加垂苔細絲與苔絲（只拿來看、烘進貼圖，不進遊戲網格）。"""
    obs = coll if isinstance(coll, list) else list(coll.objects)
    mud = next(o for o in obs if re.sub(r'\.\d{3}$', '', o.name).endswith('Mud'))
    tgt = mud.users_collection[0]

    def put(o):
        for c in list(o.users_collection):
            c.objects.unlink(o)
        tgt.objects.link(o)
        if isinstance(coll, list):
            coll.append(o)
        return o
    if low:                                              # 遊戲版第二版：低模不另做苔皮殼（粗網格上像一張布）；苔皮、苔絲直接烘在低模泥丘上
        return
    cap = moss_cap11(V, mud=mud, name='MossCap')
    if cap is None:
        return
    put(cap)
    hm = hang_moss11(V, cap, V.get('nhang', 70))
    if hm:
        hm.name = hm.data.name = 'HangMoss'
        put(hm)
    lm = core_plants._leaf_material
    fz_mat = bpy.data.materials.get('DR11_MossFiber') or lm('DR11_MossFiber', (.012, .026, .008, 1), (.045, .080, .022, 1), (.070, .105, .035, 1), gloss=.7)
    R = random.Random(V['seed'] + 901)
    dens = V.get('fuzz', 4200) * (.5 if quick else 1.0)
    put(moss_fuzz11('MossFuzzCap', [cap], R, fz_mat, dens))
    if hm:
        put(moss_fuzz11('MossFuzzHang', [hm], R, fz_mat, dens * 1.6, hang=True))


def _views11(V):
    RP = V['RP']
    g = plate_geom(V)
    xp, zc = g['xp'], RP * .80
    return {
        'front': ((xp - 14, 0, 1.7), (xp, 0, zc), 30),            # 正對根面（-X）
        'side': ((xp + .4, -14, 1.7), (xp + .4, 0, zc), 30),
        'lside': ((xp + .4, 14, 1.7), (xp + .4, 0, zc), 30),      # 另一側（畫面左那側）
        'lplateside': ((xp - .3, 5.4, 1.3), (xp - .3, 0, 1.2), 35),
        'rroots': ((xp - 3.4, -2.9, 1.5), (xp - .4, -.85, 1.05), 34),     # 右側根（崩落區上下）
        'center': ((xp - 3.6, -.3, 1.2), (xp - .6, -.15, .95), 34),      # 中央主根
        'neck': ((xp - 3.4, -1.0, .55), (xp - .8, -.1, .15), 34),        # 根頸與土坑交界
        'topedge': ((xp - 3.2, -1.2, 3.6), (xp - .5, -.1, 2.2), 34),     # 上緣
        'embedo': ((xp - 3.2, 2.6, 2.1), (xp - .5, .78, 1.45), 34),      # 埋入→露出 斜角
        'tq': ((xp - 8.5, -6.5, 1.7), (xp + .3, 0, zc * .9), 28),
        'back': ((xp + 9, 6.5, 2.2), (xp + .6, 0, zc * .8), 28),
        'top': ((xp + .3, -.01, 16), (xp + .3, 0, 0), 30),
        'face': ((xp - 7.5, -2.4, 2.0), (xp, 0, zc), 30),       # 根面近景
        'pit': ((xp - 6.5, -3.2, 4.2), (xp - 1.6, 0, .3), 30),    # 坑：高一點往下看
        'moss': ((xp - 2.6, -1.3, 3.6), (xp - .1, -.2, 2.6), 35),   # 頂上苔近景
        'plateside': ((xp - .3, -5.4, 1.3), (xp - .3, 0, 1.2), 35),   # 根盤側面近景
        'oblique': ((xp - 5.6, -5.2, 5.4), (xp - .4, 0, .7), 30),   # 俯斜（四分之三、高處往下看）
        'gap': ((xp - 4.0, -2.4, 1.9), (xp - .1, -.75, 1.0), 32),   # 右側崩落區近景
        'lowgap': ((xp - 3.6, 2.2, 1.3), (xp - .2, .55, .45), 32),   # 左下缺口、土塊與石塊近景
        'embed': ((xp - 4.2, .80, 1.6), (xp - .5, .78, 1.55), 30),       # 正對 M1         # 主根 M1：下段露出→中段埋入→上段再露出（同一畫面）
        'embed2': ((xp - 3.0, -1.0, 2.5), (xp - .3, -.2, 1.95), 40),      # 次根 S3、主根 M2 上段：埋入→露出
        'botgap': ((xp - 3.2, -.9, .9), (xp - .3, -.35, .35), 35),        # 底邊缺口
        'trunktop': ((V['L'] + 1.3, -2.0, 2.4), (V['L'] - .1, 0, .35), 35),   # 斷端俯視（受光的木片上緣、木條）
        'trunkend': ((V['L'] + 2.6, -2.4, 1.3), (V['L'] + .1, 0, .45), 35),   # 倒幹末端劈裂近景
        'ofront': None, 'oside': None,                               # 正交：等高對照用
    }


OSCALE, OZ = 7.0, 1.3


def oshot(path, view, V, res=(1280, 720)):
    """正交出圖（水平視線）：寬 OSCALE 公尺、畫面中心高 OZ；地面 z = 0 在第 360 + OZ·px/m 列。"""
    import json
    sc = bpy.context.scene
    cam = bpy.data.objects.get('DR_OCam')
    if cam is None:
        cam = bpy.data.objects.new('DR_OCam', bpy.data.cameras.new('DR_OCam'))
        sc.collection.objects.link(cam)
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = OSCALE
    cam.data.clip_end = 200
    g = plate_geom(V)
    if view == 'ofront':
        cx = 0.0
        loc, tgt = Vector((g['xp'] - 30, 0, OZ)), Vector((g['xp'], 0, OZ))
    else:
        cx = g['xp'] + .4
        loc, tgt = Vector((cx, -30, OZ)), Vector((cx, 0, OZ))
    cam.location = loc
    cam.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    ppm = res[0] / OSCALE
    json.dump(dict(view=view, px_per_m=ppm, ground_row=res[1] / 2 + OZ * ppm, center_col=res[0] / 2, center_m=cx),
              open(path[:-4] + '.json', 'w'))


if __name__ == '__main__' and '--' in sys.argv:
    args = sys.argv[sys.argv.index('--') + 1:]
    var = args[0] if args else 'A'
    quick = (args[1] if len(args) > 1 else 'quick') == 'quick'
    outdir = args[2] if len(args) > 2 else 'D:/yun-jing-cache/dr11-work'
    os.makedirs(outdir, exist_ok=True)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    GREY = 'grey' in args
    build(var, quick)
    if 'bodyonly' in args:                               # 只留主體：泥丘、倒幹、木束、坑（不放粗根、土塊）
        keep = ('Mud', 'Trunk', 'Pit', 'StonesPit', 'Snap_TrunkBundle')
        for o in list(bpy.data.objects):
            if o.type == 'MESH' and not o.name.split('.')[0].startswith(keep):
                bpy.data.objects.remove(o, do_unlink=True)
    if 'nodress' not in args and not GREY:
        dress11(VAR, quick)
    import preview_dr
    preview_dr.setup(samples=24 if quick else 64, fog=False)
    ground_hole11(VAR)
    if GREY:                                             # 灰模：低角度主光（從根面右前方來），凹面、坑壁才有明暗
        sun = bpy.data.objects.get('DR_Sun')
        if sun:
            sun.data.energy = 4.5
            sun.rotation_euler = (math.radians(62), 0, math.radians(-50))
        bg = next((n for n in bpy.context.scene.world.node_tree.nodes if n.type == 'BACKGROUND'), None)
        if bg:
            bg.inputs[1].default_value = .7
    hum = bpy.data.objects.get('DR_Human_1p75m')
    if hum:
        hum.location = (plate_geom(VAR)['xp'] - 1.2, -VAR['RP'] * 1.35, .875)
    if 'clay' in args:
        m = bpy.data.materials.new('Clay')
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        b.inputs['Base Color'].default_value = (.20, .19, .18, 1)
        b.inputs['Roughness'].default_value = .8                 # 灰模粗糙度一致
        bpy.context.view_layer.material_override = m
    vw = _views11(VAR)
    ROOTID = 'rootid' in args
    if ROOTID:                                           # 檢查用：每條根上不同顏色並記下畫面位置（不進正式輸出）
        import colorsys, json
        from bpy_extras.object_utils import world_to_camera_view
        rid = sorted([o for o in bpy.data.objects if o.type == 'MESH' and re.sub(r'\.\d{3}$', '', o.name).startswith(('FaceRoot', 'BackRoot', 'Crown', 'RootsPit'))], key=lambda o: o.name)
        for i, o in enumerate(rid):
            m = bpy.data.materials.new('rid' + o.name)
            m.use_nodes = True
            b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
            b.inputs['Base Color'].default_value = (*colorsys.hsv_to_rgb((i * .137) % 1, .8, .9), 1)
            o.data.materials.clear()
            o.data.materials.append(m)
        bpy.context.view_layer.material_override = None
    want = args[3].split(',') if len(args) > 3 and args[3] not in ('-', 'clay', 'nodress', 'grey', 'bodyonly') else list(vw)
    for k in want:
        if k in ('ofront', 'oside'):
            hv = hum.hide_render if hum else None
            if hum:
                hum.hide_render = True
            oshot(os.path.join(outdir, f"DR11_{var}_{k}.png"), k, VAR)
            if hum:
                hum.hide_render = hv
            continue
        base = {'embedx': 'embed', 'embed2x': 'embed2', 'trunkfill': 'trunkend'}.get(k, k)
        loc, tgt, lens = vw[base]
        if hum:
            hum.hide_render = k != base or k in ('plateside', 'gap', 'lowgap', 'embed', 'embed2', 'botgap')          # 近景不放人形尺（會擋到）
        hid = []
        if k in ('embedx', 'embed2x'):                   # 驗證用：同一相機把泥盤、土塊藏起來，看根在土裡是否連續
            for o in bpy.data.objects:
                if o.type == 'MESH' and re.sub(r'\.\d{3}$', '', o.name).endswith(('Mud', 'ClodsRim', 'ClodsCollapse')):
                    o.hide_render = True
                    hid.append(o)
        fill = None
        if k == 'trunkfill':                             # 斷端背光：只這張加一盞補光（從相機方向打），標明是補光版
            ld = bpy.data.lights.new('DR11_Fill', 'AREA')
            ld.energy, ld.size = 650.0, 3.0
            fill = bpy.data.objects.new('DR11_Fill', ld)
            bpy.context.scene.collection.objects.link(fill)
            fill.location = Vector(loc) + Vector((0, 0, .6))
            fill.rotation_euler = (Vector(tgt) - fill.location).to_track_quat('-Z', 'Y').to_euler()
        preview_dr.shot(os.path.join(outdir, f"DR11_{var}_{k}.png"), loc, tgt, lens, (1280, 720))
        if ROOTID:
            sc_ = bpy.context.scene
            lab_ = []
            for o in rid:
                vs_ = [o.matrix_world @ v.co for v in o.data.vertices]
                c_ = world_to_camera_view(sc_, sc_.camera, vs_[len(vs_) // 2])
                if 0 < c_.x < 1 and 0 < c_.y < 1 and c_.z > 0:
                    lab_.append((re.sub(r'\.\d{3}$', '', o.name).replace('FaceRoot', '').replace('BackRoot', 'B'), c_.x, 1 - c_.y))
            json.dump(lab_, open(os.path.join(outdir, f"DR11_{var}_{k}.json"), 'w'))
        for o in hid:
            o.hide_render = False
        if fill:
            bpy.data.objects.remove(fill, do_unlink=True)
    zs = [(o.matrix_world @ Vector(c)).z for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith('DR_') for c in o.bound_box]
    ys = [(o.matrix_world @ Vector(c)).y for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith(('DR_', 'Pit')) and 'Ground' not in o.name for c in o.bound_box]
    print('DR11_SIZE', var, 'top', round(max(zs), 3), 'width_y', round(max(ys) - min(ys), 3))
    tops = sorted(((max((o.matrix_world @ Vector(c)).z for c in o.bound_box), o.name) for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith('DR_')), reverse=True)[:4]
    print('DR11_TOPOBJ', [(n, round(z, 3)) for z, n in tops])          # 頂高由哪個物件決定
    sv = [a_ for a_ in args[3:] if a_.endswith('.blend')]
    if sv:
        bpy.ops.wm.save_as_mainfile(filepath=sv[0])
