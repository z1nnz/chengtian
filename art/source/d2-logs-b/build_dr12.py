# DR12 地上的大片樹皮與樹瘤（高模）。參考：art/references/DR12/v001/（Codex 依 D2 設定圖 V2、V6、V4 畫）。
#   BarkL：一大片剝落樹皮（長約 1.5 m、寬 0.7 m、厚 4–6 cm）躺在地上，前段平、兩側微翹成淺槽，後段往上捲、翻過來像浪頭；
#          朝上是淺奶油色內皮纖維（長條纖維、深色受潮斑），捲起來的外側是深灰褐樹皮（掃描樹皮推幾何、地衣、苔）；
#          前端撕斷成一排長短不齊的纖維尖齒；厚度斷面三層：深色外皮、紅褐中層、淺色內皮。
#   （BarkM 捲筒、BarkS 碎片、BurlA 地上樹瘤、BurlB 根上樹瘤：樣品通過後再做）
# 座標：長度沿 +X（撕斷端在 -X、捲起端在 +X），正面 -Y，z = 0 地面；原點底部中心。1 單位 = 1 m。
# 樹皮、苔、地衣沿用 D2 根與木同一套（../d2-roots-b/dr_core.py、build_dr06.bark_material）。
# 用法（背景，不要加 --factory-startup）：
#   blender -b --python build_dr12.py -- BarkL <輸出資料夾> [鏡位,鏡位] [clay] [存檔.blend]
import bpy, bmesh, math, random, sys, os, importlib
import numpy as np
from mathutils import Vector, noise

HERE = os.path.dirname(os.path.abspath(globals().get('__file__', 'D:/yun-jing-d2-logs/art/source/d2-logs-b/build_dr12.py')))
ROOTS = os.path.join(os.path.dirname(HERE), 'd2-roots-b')
for _p in (ROOTS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import dr_core
importlib.reload(dr_core)
from dr_core import fb, sdisp_row, TILE
import build_dr06 as B6

# Ls 中線弧長、W 寬、T 厚；flat 平段長（之後開始捲）、kmax 捲到最後的曲率（1/半徑）；trough 兩側翹（y² 的係數）
# teeth：撕斷端尖齒（個數、最長 m）；twist：沿長扭轉（弧度）
VARIANTS = {
    'BarkL': dict(kind='sheet', Ls=2.85, W=.78, T=.110, flat=.80, kmax=1 / .215, trough=.85, teeth=(17, .30), twist=.10, seed=1201, scale=.78, lat=.16, crest=(13, .13), plate=(.075, .115, .022)),
}


def _sm(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _np_sm(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def _coll(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(c)
    return c


# ------------------------------------------------------------------ 材質
def fibre_material():
    """內皮：淺奶油褐、沿長度的細纖維條紋（UV 的 v = 沿長公尺），大片受潮深色斑。"""
    m = bpy.data.materials.get('DR12_Fibre')
    if m:
        return m
    m = bpy.data.materials.new('DR12_Fibre')
    m.use_nodes = True
    N, Lk = m.node_tree.nodes, m.node_tree.links
    b = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    uv = N.new('ShaderNodeUVMap')
    uv.uv_map = 'Param'
    mp = N.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (70.0, 3.0, 1.0)          # 橫向密、沿長拉長：一條條纖維
    Lk.new(uv.outputs[0], mp.inputs['Vector'])
    nz = N.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 1.0
    nz.inputs['Detail'].default_value = 6
    nz.inputs['Roughness'].default_value = .55
    Lk.new(mp.outputs[0], nz.inputs['Vector'])
    fc = B6._ramp(N, .30, .72, (.15, .095, .048, 1), (.44, .33, .20, 1))      # 參考圖內皮：奶油褐，不是白
    Lk.new(nz.outputs['Fac'], fc.inputs[0])
    mp2 = N.new('ShaderNodeMapping')
    mp2.inputs['Scale'].default_value = (4.0, 1.6, 1.0)          # 受潮斑：10–30 cm、沿纖維拉長
    Lk.new(uv.outputs[0], mp2.inputs['Vector'])
    nz2 = N.new('ShaderNodeTexNoise')
    nz2.inputs['Scale'].default_value = 1.0
    nz2.inputs['Detail'].default_value = 4
    Lk.new(mp2.outputs[0], nz2.inputs['Vector'])
    st = B6._ramp(N, .46, .64, (1, 1, 1, 1), (.30, .22, .15, 1))
    # 纖維一縷縷翹起、深淺不一：拉長的 Voronoi 邊（纖維束之間的縫）＋較粗的纖維束明暗
    mp3 = N.new('ShaderNodeMapping')
    mp3.inputs['Scale'].default_value = (16.0, 1.3, 1.0)
    Lk.new(uv.outputs[0], mp3.inputs['Vector'])
    vo = N.new('ShaderNodeTexVoronoi')
    vo.feature = 'DISTANCE_TO_EDGE'
    vo.inputs['Scale'].default_value = 1.0
    Lk.new(mp3.outputs[0], vo.inputs['Vector'])
    gap = B6._ramp(N, .0, .07, (.35, .28, .22, 1), (1, 1, 1, 1))
    Lk.new(vo.outputs['Distance'], gap.inputs[0])
    vo2 = N.new('ShaderNodeTexVoronoi')
    vo2.inputs['Scale'].default_value = 1.0
    Lk.new(mp3.outputs[0], vo2.inputs['Vector'])
    bun = B6._ramp(N, .0, 1.0, (.70, .66, .62, 1), (1.08, 1.04, 1.0, 1))
    Lk.new(vo2.outputs['Color'], bun.inputs[0])
    gm = N.new('ShaderNodeMixRGB')
    gm.blend_type = 'MULTIPLY'
    gm.inputs[0].default_value = 1.0
    Lk.new(gap.outputs[0], gm.inputs[1])
    Lk.new(bun.outputs[0], gm.inputs[2])
    Lk.new(nz2.outputs['Fac'], st.inputs[0])
    mx = N.new('ShaderNodeMixRGB')
    mx.blend_type = 'MULTIPLY'
    mx.inputs[0].default_value = 1.0
    Lk.new(fc.outputs[0], mx.inputs[1])
    Lk.new(st.outputs[0], mx.inputs[2])
    mx2 = N.new('ShaderNodeMixRGB')
    mx2.blend_type = 'MULTIPLY'
    mx2.inputs[0].default_value = 1.0
    Lk.new(mx.outputs[0], mx2.inputs[1])
    Lk.new(gm.outputs[0], mx2.inputs[2])
    Lk.new(mx2.outputs[0], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = .88
    bp = N.new('ShaderNodeBump')
    bp.inputs['Strength'].default_value = .8
    bp.inputs['Distance'].default_value = .004
    hh = N.new('ShaderNodeMath')
    hh.operation = 'ADD'
    Lk.new(nz.outputs['Fac'], hh.inputs[0])
    gh = N.new('ShaderNodeMapRange')
    gh.inputs['From Max'].default_value = .07
    gh.inputs['To Min'].default_value = -1.2
    gh.inputs['To Max'].default_value = 0.0
    Lk.new(vo.outputs['Distance'], gh.inputs['Value'])
    Lk.new(gh.outputs[0], hh.inputs[1])
    Lk.new(hh.outputs[0], bp.inputs['Height'])
    Lk.new(bp.outputs[0], b.inputs['Normal'])
    return m


def bark12_material():
    """DR06 樹皮的 DR12 副本：樹皮片只有 1.5 m，地衣斑要縮小、多一點才看得到（DR06 那份不動）。"""
    m = bpy.data.materials.get('DR12_Bark')
    if m:
        return m
    m = B6.bark_material().copy()
    m.name = 'DR12_Bark'
    for n in m.node_tree.nodes:
        if n.type == 'TEX_NOISE' and abs(n.inputs['Scale'].default_value - 3.6) < 1e-3:
            n.inputs['Scale'].default_value = 9.0               # 地衣斑 5–12 cm
        elif n.type == 'VALTORGB':
            e = n.color_ramp.elements
            if abs(e[0].position - .600) < 1e-3 and abs(e[1].position - .640) < 1e-3:
                e[0].position, e[1].position = .545, .585
        elif n.type == 'MIX_RGB' and n.blend_type == 'MIX' and abs(n.inputs[2].default_value[0] - .31) < 1e-3:
            n.inputs[2].default_value = (.40, .44, .40, 1)
    return m


def layer_material():
    """撕裂邊的厚度斷面：外 → 內 深色外皮、紅褐中層、淺色內皮（點屬性 Depth：0 外、1 內）。"""
    m = bpy.data.materials.get('DR12_Layers')
    if m:
        return m
    m = bpy.data.materials.new('DR12_Layers')
    m.use_nodes = True
    N, Lk = m.node_tree.nodes, m.node_tree.links
    b = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    at = N.new('ShaderNodeAttribute')
    at.attribute_name = 'Depth'
    tc = N.new('ShaderNodeTexCoord')
    nz = N.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 18
    Lk.new(tc.outputs['Object'], nz.inputs['Vector'])
    ad = N.new('ShaderNodeMath')
    ad.operation = 'MULTIPLY_ADD'
    ad.inputs[2].default_value = 0.0
    Lk.new(nz.outputs['Fac'], ad.inputs[0])
    ad.inputs[1].default_value = .16
    ad2 = N.new('ShaderNodeMath')
    ad2.operation = 'ADD'
    Lk.new(at.outputs['Fac'], ad2.inputs[0])
    Lk.new(ad.outputs[0], ad2.inputs[1])
    r = N.new('ShaderNodeValToRGB')
    e = r.color_ramp.elements
    e[0].position, e[0].color = .0, (.040, .032, .025, 1)
    e[1].position, e[1].color = .26, (.065, .042, .028, 1)
    for p, c in ((.31, (.17, .060, .030, 1)), (.60, (.24, .095, .045, 1)), (.68, (.44, .32, .19, 1)), (1.0, (.52, .40, .25, 1))):
        el = e.new(p)
        el.color = c
    Lk.new(ad2.outputs[0], r.inputs[0])
    Lk.new(r.outputs[0], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = .9
    return m


# ------------------------------------------------------------------ 樹皮片
def _centre(V):
    """中線：前段平、之後曲率漸增往上捲（XZ 平面）。回傳弧長取樣 s、點 C、切線角 th。"""
    Ls, s0, k1 = V['Ls'], V['flat'], V['kmax']
    ds = .002
    s = np.arange(0, Ls + ds, ds)
    k = np.array([0.0 if x < s0 else k1 * _sm((x - s0) / (Ls - s0)) ** 1.15 for x in s])
    k += .05 * np.sin(s * 5.1 + V['seed'] % 7)          # 平段的微小起伏
    th = np.concatenate([[0.0], np.cumsum((k[1:] + k[:-1]) * .5 * ds)])
    th -= .03                                            # 撕斷端略往下貼地
    x = np.concatenate([[0.0], np.cumsum((np.cos(th[1:]) + np.cos(th[:-1])) * .5 * ds)])
    z = np.concatenate([[0.0], np.cumsum((np.sin(th[1:]) + np.sin(th[:-1])) * .5 * ds)])
    return s, x, z, th


def _teeth(V, rng):
    """撕斷端：b（0–1 橫向）處往 -s 伸出的長度。幾根長短不一的三角尖齒疊在一起。"""
    n, Lmax = V['teeth']
    tk = []
    for i in range(n):
        c = (i + .5 + rng.uniform(-.35, .35)) / n
        tk.append((c, rng.uniform(.20, 1.0) ** .8 * Lmax, rng.uniform(.30, .60) / n))
    def f(b):
        v = 0.0
        for c, L, hw in tk:
            v = max(v, L * max(0.0, 1 - abs(b - c) / hw) ** 1.4)
        return v + .012 * fb((b * 9, 3.1, V['seed'] % 11), 1.0)
    return f


def bark_sheet(V, coll, name='BarkL', res=(1.0, 1.0)):
    rng = random.Random(V['seed'])
    sd = V['seed'] % 97
    s_, cx, cz, cth = _centre(V)
    Ls, W, T = V['Ls'], V['W'], V['T']
    teeth = _teeth(V, rng)
    tmax = V['teeth'][1]

    def cl(s):
        x = np.interp(s, s_, cx)
        z = np.interp(s, s_, cz)
        t = np.interp(s, s_, cth)
        return Vector((x, 0, z)), Vector((math.cos(t), 0, math.sin(t))), Vector((-math.sin(t), 0, math.cos(t)))

    def hw(s):                                           # 半寬：撕斷端略寬、捲起處略窄，邊緣不齊
        return W * .5 * (1.04 - .10 * _sm((s - V['flat']) / (Ls - V['flat']))) * (1 + .07 * fb((s * 2.3, sd, 1.7), 1.0))

    def mid(s, y):
        C, Tn, Nn = cl(s)
        tw = V['twist'] * (s / Ls - .5)
        Yd = Vector((0, 1, 0)) * math.cos(tw) + Nn * math.sin(tw)
        tr = V['trough'] * (1.15 - .35 * _sm(s / V['flat']))
        warp = .022 * fb((s * 1.7, y * 2.2, sd + .3), 1.0, 3)
        lat = V.get('lat', 0) * math.sin(1.15 * math.pi * s / Ls + .35)       # 俯視是 S 彎，不是一條直的長方形
        return C + Yd * (y + lat) + Nn * (tr * y * y + warp)

    nA = int(150 * res[0])
    nB = int(96 * res[1])
    # 每列（橫向 b）自己的弧長範圍：前端尖齒、後端（捲起端）小的不齊
    s0b = [tmax - teeth(j / (nB - 1)) for j in range(nB)]
    crest = _teeth(dict(V, teeth=V['crest'], seed=V['seed'] + 7), random.Random(V['seed'] + 7)) if V.get('crest') else (lambda b: 0.0)
    cmax = V['crest'][1] if V.get('crest') else 0.0
    s1b = [Ls - cmax + crest(j / (nB - 1)) - .02 * abs(math.sin(j * .9 + sd)) for j in range(nB)]      # 捲起端：內層纖維一縷縷垂下來
    P = np.zeros((nA, nB, 3))
    S = np.zeros((nA, nB))
    Y = np.zeros((nA, nB))
    for i in range(nA):
        a = i / (nA - 1)
        for j in range(nB):
            b = j / (nB - 1)
            s = s0b[j] + (s1b[j] - s0b[j]) * a
            h = hw(s)
            y = (b * 2 - 1) * h * (1 + .05 * fb((s * 7, b * 3, sd + 2), 1.0) * _sm((abs(b * 2 - 1) - .75) / .25))      # 只有邊緣不齊（平滑過渡，不然邊上折出一道縫）
            P[i, j] = mid(s, y)
            S[i, j], Y[i, j] = s, y
    # 中面法線（朝上 = 內皮面）：直接對 (s, y) 求偏微分。每列的弧長範圍不同（尖齒、捲起端不齊），
    # 用格點鄰居差分的話橫向那一條其實是斜的，法線會亂轉，厚度往亂方向推就皺成一團。
    Nm = np.zeros((nA, nB, 3))
    e = .004
    for i in range(nA):
        for j in range(nB):
            s, y = S[i, j], Y[i, j]
            n_ = (mid(s + e, y) - mid(s - e, y)).cross(mid(s, y + e) - mid(s, y - e))
            Nm[i, j] = n_.normalized()
    if Nm[nA // 4, nB // 2, 2] < 0:
        Nm = -Nm
    # 厚度：尖齒處變薄；外皮掃描凹凸（沿長＝樹幹方向）
    tooth_t = np.array([[_sm((S[i, j] - s0b[j]) / .14) * (.5 + .5 * _sm((s1b[j] - S[i, j]) / .10)) for j in range(nB)] for i in range(nA)])
    th = T * (.15 + .85 * tooth_t ** .8) * (1 + .15 * np.sin(S * 3.7 + sd))      # 尖齒處收成薄片（遊戲版低取樣時，厚的齒端像一排方塊）
    disp = np.zeros((nA, nB))
    for i in range(nA):
        disp[i] = sdisp_row(Y[i] / TILE * 1.6 + .37, (S[i, nB // 2] / TILE) + .11)
    bb = np.abs(np.linspace(-1, 1, nB))[None, :]
    edge = 1 - .75 * np.clip((bb - .80) / .20, 0, 1) ** 2                 # 兩側邊緣樹皮凹凸收小：邊上斷面是乾淨的三層，不是一排鋸齒
    amp = .026 * (.45 + .55 * tooth_t) * edge
    if V.get('plate'):
        pw, pl, ph = V['plate']
        prng = np.random.default_rng(V['seed'])
        hts = prng.uniform(.45, 1.0, (64, 64))
        cy = Y / pw
        row = np.floor(S / pl).astype(int)
        cy = cy + .5 * (row % 2) + .25 * np.sin(row * 1.7)
        col_ = np.floor(cy).astype(int)
        fy, fs = cy - col_, S / pl - row
        ed = np.minimum(np.minimum(fy, 1 - fy) * pw, np.minimum(fs, 1 - fs) * pl)      # 到板邊的距離（公尺）
        plate = hts[row % 64, col_ % 64] * _np_sm(ed / .014) * ph
        plate *= edge * (.35 + .65 * tooth_t)
    else:
        plate = 0.0
    fib = np.abs(np.array([[noise.noise(Vector((Y[i, j] * 55, S[i, j] * 2.2, sd))) for j in range(nB)] for i in range(nA)]))
    top = P + Nm * (th * .5 - .0035 * fib)[..., None]
    bot = P - Nm * np.maximum(th * .5 + amp * (disp - .35) + plate, th * .22)[..., None]      # 外皮凹溝不能穿過中面（薄的尖齒處會翻面皺成一團）
    # 苔：外皮朝上的地方（捲起的背面），斑塊狀
    moss = np.zeros((nA, nB))
    for i in range(nA):
        for j in range(nB):
            up = -Nm[i, j, 2]
            pn = fb((P[i, j, 0] * 3.2, P[i, j, 1] * 3.2, P[i, j, 2] * 3.2 + sd), 1.0, 3)
            moss[i, j] = _sm((up - .25) / .5) * _sm((pn + .15) / .35)

    bm = bmesh.new()
    uvT = bm.loops.layers.uv.new('UV')
    uvP = bm.loops.layers.uv.new('Param')
    col = bm.loops.layers.color.new('Mask')
    dep = bm.verts.layers.float.new('Depth')
    vt = [[bm.verts.new(top[i, j]) for j in range(nB)] for i in range(nA)]
    vb = [[bm.verts.new(bot[i, j]) for j in range(nB)] for i in range(nA)]
    for i in range(nA):
        for j in range(nB):
            vt[i][j][dep] = 1.0
            vb[i][j][dep] = 0.0

    def put(f, ij, mat):
        f.material_index = mat
        for lp, (i, j) in zip(f.loops, ij):
            lp[uvT].uv = (Y[i, j] / TILE * 1.6 + .37, S[i, j] / TILE + .11)
            lp[uvP].uv = (Y[i, j], S[i, j])
            g = float(disp[i, j]) if mat == 0 else .6
            lp[col] = (float(moss[i, j]) if mat == 0 else 0.0, g, .5, 1.0)

    for i in range(nA - 1):
        for j in range(nB - 1):
            q = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            put(bm.faces.new([vt[a][b] for a, b in q]), q, 1)
            q2 = q[::-1]
            put(bm.faces.new([vb[a][b] for a, b in q2]), q2, 0)
    # 邊：沿外框一圈，上下接起來
    ring = [(0, j) for j in range(nB)] + [(i, nB - 1) for i in range(1, nA)] + [(nA - 1, j) for j in range(nB - 2, -1, -1)] + [(i, 0) for i in range(nA - 2, 0, -1)]
    for k in range(len(ring)):
        a, b = ring[k], ring[(k + 1) % len(ring)]
        f = bm.faces.new([vt[a[0]][a[1]], vt[b[0]][b[1]], vb[b[0]][b[1]], vb[a[0]][a[1]]])
        put(f, [a, b, b, a], 2)
    bm.normal_update()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.validate()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    for mt in (bark12_material(), fibre_material(), layer_material()):
        me.materials.append(mt)
    # 法線一致（外側朝外）
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    return o


def ground_fit(objs, sink=.012):
    """整組放到地上：最低點略低於 z=0；外框 XY 中心移到原點。"""
    vs = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
    hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    off = Vector((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z - sink))
    for o in objs:
        o.data.transform(__import__('mathutils').Matrix.Translation(off))
    return hi - lo


def build(var='BarkL', quick=True):
    V = VARIANTS[var]
    coll = _coll('DR12_' + var)
    o = bark_sheet(V, coll, var, (.6, .6) if quick else (1.0, 1.0))
    if V.get('scale', 1.0) != 1.0:                        # 形狀照參考圖的比例做，最後整體縮到規格尺寸
        o.data.transform(__import__('mathutils').Matrix.Scale(V['scale'], 4))
    size = ground_fit([o])
    print('DR12_SIZE', var, ' x '.join(f'{c:.3f}' for c in size), 'tris', sum(len(p.vertices) - 2 for p in o.data.polygons))
    return [o]


def _views(size):
    L = max(size.x, size.y)
    return {
        'tq': ((-L * 1.3, -L * 1.7, 1.25), (0, 0, size.z * .35), 35),
        'front': ((0, -L * 2.4, .55), (0, 0, size.z * .4), 35),
        'side': ((-.01, -L * 2.6, size.z * .45), (0, 0, size.z * .45), 35),
        'back': ((L * 1.5, L * 1.5, 1.2), (0, 0, size.z * .35), 35),
        'end': ((-L * 2.2, -.4, .7), (0, 0, size.z * .3), 35),
        'top': ((0, -.01, L * 2.8), (0, 0, 0), 35),
        'curl': ((L * .9, -L * 1.0, .9), (L * .25, 0, size.z * .5), 35),
        'teeth': ((-L * .95, -L * .55, .45), (-L * .35, 0, .03), 35),
    }


if __name__ == '__main__' and '--' in sys.argv:
    args = sys.argv[sys.argv.index('--') + 1:]
    var = args[0] if args else 'BarkL'
    outdir = args[1] if len(args) > 1 else 'D:/yun-jing-cache/dr12-work'
    os.makedirs(outdir, exist_ok=True)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    quick = 'full' not in args
    objs = build(var, quick)
    vs = [v.co for o in objs for v in o.data.vertices]
    size = Vector((max(v.x for v in vs) - min(v.x for v in vs), max(v.y for v in vs) - min(v.y for v in vs), max(v.z for v in vs)))
    import preview_dr
    preview_dr.setup(samples=32 if quick else 96, fog=False)
    hum = bpy.data.objects.get('DR_Human_1p75m')
    if hum:
        hum.location = (size.x * .5 + .9, .9, .875)
    if 'clay' in args:
        cm = bpy.data.materials.new('Clay')
        cm.use_nodes = True
        next(n for n in cm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.5, .5, .5, 1)
        for o in objs:
            for k in range(len(o.data.materials)):
                o.data.materials[k] = cm
    vw = _views(size)
    want = args[2].split(',') if len(args) > 2 and not args[2].endswith('.blend') and args[2] not in ('clay', 'full') else list(vw)
    for k in want:
        loc, tgt, lens = vw[k]
        preview_dr.shot(os.path.join(outdir, f'DR12_{var}_{k}.png'), loc, tgt, lens, (1280, 720))
    sv = [a for a in args if a.endswith('.blend')]
    if sv:
        bpy.ops.wm.save_as_mainfile(filepath=sv[0])
