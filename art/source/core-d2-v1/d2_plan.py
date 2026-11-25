# 11/22 z1nnz 看了三個版本選 A：神木退回 v004 熔接版（v005/v006 改壞了，備份在 d2_plan_v006_backup.py）；保留水窪反光、拱門補苔
# D2 古樹區域 總平面＋六角度方塊模型（給 ChatGPT 照著畫設定圖用）
#   blender -b --factory-startup -P d2_plan.py -- [only=V1,V3] [quick]
#   座標：x 東、y 北，單位公尺；區塊 200×200（x,y ∈ -100..100）
import bpy, bmesh, sys, math, random, json
import numpy as np
from mathutils import Vector, Matrix, noise

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
QUICK = 'quick' in argv
ONLY = next((a[5:].split(',') for a in argv if a.startswith('only=')), None)
S_ = 'D:/chengtian/4-素材與快取/bark-sample/'
EXP = 'D:/chengtian/1-進行中/core-d2-altar/art/exports/core-d2-v1/'
OUT = S_ + 'plan/'
noise.seed_set(5)
R = random.Random(5)
sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# ---------------- 平面配置（總圖，所有角度都照這個） ----------------
TREE = (-24.0, 30.0)          # 神木
ALT = (7.0, 7.0)              # 祭壇
PIT = (14.5, -3.0)            # 被挖的坑（z1nnz 11/21：離走道遠一點）
PIT2, PIT2_S = (8.6, -8.4), .65   # 11/24 故事「有人來挖過」：V3 右前方再一個小的試挖坑（設定圖 V3 右前方看得到坑）
ARCH_S = (2.0, -84.0)         # 南入口（Josh 的根拱）
ARCH_N = (-4.0, 108.0)         # 北入口（核心組根拱）
CLEAR = (-4.0, 10.0, 38.0)    # 林中空地：中心、半徑
VIEW_E = (38.0, 4.0)          # 東側開口（看向 B 區山）方向的 y 範圍中心、半寬
# 主路：南入口 → 祭壇前 → 繞神木東側 → 北入口
PATH = [(2, -100), (2, -84), (-3, -62), (4, -40), (2, -20), (4, -6), (9, 1), (18, 14), (20, 32), (14, 52), (2, 70), (-2, 86), (-4, 108), (-4, 125)]


def seg_d(px, py, a, b):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


# 支路：神木根旁 → 祭壇西側 → 接回主路（設定圖 V5 從神木旁往南看的那條路）
PATH2 = [(-16, 26), (-8, 15), (-1, 3), (3, -5)]


def path_d(x, y):
    d1 = min(seg_d(x, y, PATH[i], PATH[i + 1]) for i in range(len(PATH) - 1))
    d2 = min(seg_d(x, y, PATH2[i], PATH2[i + 1]) for i in range(len(PATH2) - 1)) + .35   # 支路窄一點
    return min(d1, d2)


def fb(x, y, s, o=3):
    return noise.fractal(Vector((x * s, y * s, 0)), .5, 2.0, o)


def gh0(x, y):
    # z1nnz 11/21：空地裡沒那麼上坡 → 空地中心起伏壓小，往外才慢慢恢復
    dc = math.hypot(x - CLEAR[0], y - CLEAR[1])
    k = .3 + .7 * max(0.0, min(1.0, (dc - 25) / 35)) if REAL else 1.0
    if REAL:   # 神木根的範圍保留原本地形，不然樹根底下的地被壓低、根會懸空翹起來
        dt = math.hypot(x - TREE[0], y - TREE[1])
        k = max(k, max(0.0, min(1.0, (30 - dt) / 8)))
    h = (fb(x, y, .02) * 2.2 + fb(x, y, .12) * .25) * k
    h += max(0.0, x - 40) * -.06                       # 東側往下斜，看出去是谷地
    h += max(0.0, -x - 50) * .05 + max(0.0, y - 60) * .03   # 西、北緩升
    return h


def gh(x, y):
    h = gh0(x, y)
    rp = math.hypot(x - PIT[0], y - PIT[1])
    if REAL:   # 坑是獨立模型（CO02）；坑周圍 6 m 內地面整平，讓坑模型平平地鋪上去
        w = max(0.0, min(1.0, (11.5 - rp) / 4.0))
        h = h * (1 - w) + gh0(*PIT) * w
        if 'pit2' in argv:
            rp2 = math.hypot(x - PIT2[0], y - PIT2[1]); w2 = max(0.0, min(1.0, (6.2 * PIT2_S + 2.5 - rp2) / 2.5))
            h = h * (1 - w2) + gh0(*PIT2) * w2
    h -= max(0.0, 1 - path_d(x, y) / 2.2) * .18
    if not REAL:
        h -= 1.1 * max(0.0, 1 - rp / 2.7) ** .6
    return h


REAL = 'real' in argv


def pit_h(dx, dy, r):
    """被挖的坑（設定圖 V4）：陡壁深坑、坑底不平，坑緣一圈翻出來的鬆土堆（不均勻、一側堆得高）。"""
    a = math.atan2(dy, dx)
    rw = 2.6 + .35 * noise.noise(Vector((math.cos(a) * 1.3, math.sin(a) * 1.3, 7.1)))   # 坑口不圓
    h = 0.0
    if r < rw:
        u = r / rw
        h -= 1.25 * (1 - u ** 3.2) + .12 * noise.noise(Vector((dx * 1.4, dy * 1.4, 3.3)))
    # 坑緣土堆：在坑口外 0.3–2.0 m，幾坨鬆土，朝東北那側堆得最高
    m = .5 + .5 * noise.noise(Vector((math.cos(a) * 1.8, math.sin(a) * 1.8, 2.2)))
    side = .55 + .45 * math.cos(a - .7)
    ring = math.exp(-((r - rw - .9) / .75) ** 2)
    h += ring * (.25 + .75 * m) * side * .6
    h += ring * (.10 * noise.noise(Vector((dx * 2.5, dy * 2.5, 9.0))) + .06 * noise.noise(Vector((dx * 6, dy * 6, 4.0))))                  # 土塊顆粒
    # 壁面陡、往上接土堆
    if rw <= r < rw + .5:
        h -= .35 * (1 - (r - rw) / .5) ** 2
    return h


def mat(name, col, rough=.9, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    return m


M_GROUND = mat('ground', (.13, .15, .07))
M_PATH = mat('path', (.30, .20, .12))
M_TRUNK = mat('trunk', (.22, .16, .11))
M_PINE = mat('pine', (.06, .14, .07))
M_BROAD = mat('broad', (.32, .36, .08))
M_ROUND = mat('round', (.10, .22, .07))
M_GIANT = mat('giant', (.14, .20, .07))
M_ROCK = mat('rock', (.30, .31, .27))
M_MOSS = mat('moss', (.12, .22, .05))
M_ROOT = mat('root', (.20, .15, .10))
M_MTN = mat('mtn', (.35, .38, .40))
M_BARKR = mat('barkr', (.20, .15, .10))
if 'real' in argv:   # 方塊材質換成掃描材質（腐葉林床、泥路、苔石）
    _GT = 'D:/chengtian/4-素材與快取/polyhaven-ground/'

    def texmat(m, diff, nor, rough, scale, tint=(1, 1, 1), box=False):
        nt = m.node_tree
        b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
        tc = nt.nodes.new('ShaderNodeTexCoord')
        mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (1 / scale,) * 3
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])

        def im(fn, cs):
            t = nt.nodes.new('ShaderNodeTexImage')
            t.image = bpy.data.images.load(_GT + fn)
            t.image.colorspace_settings.name = cs
            if box:
                t.projection, t.projection_blend = 'BOX', .3
            nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
            return t
        d = im(diff, 'sRGB')
        mx = nt.nodes.new('ShaderNodeMixRGB')
        mx.blend_type = 'MULTIPLY'
        mx.inputs[0].default_value = 1
        mx.inputs[2].default_value = (*tint, 1)
        nt.links.new(d.outputs['Color'], mx.inputs[1])
        nt.links.new(mx.outputs['Color'], b.inputs['Base Color'])
        nm = nt.nodes.new('ShaderNodeNormalMap')
        nt.links.new(im(nor, 'Non-Color').outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
        nt.links.new(im(rough, 'Non-Color').outputs['Color'], b.inputs['Roughness'])

    texmat(M_GROUND, 'forest_leaves_02_diffuse_2k.png', 'forest_leaves_02_nor_gl_2k.png', 'forest_leaves_02_rough_2k.png', 2.5, (.85, .9, .75))
    texmat(M_PATH, 'brown_mud_02_diff_2k.png', 'brown_mud_02_nor_gl_2k.png', 'brown_mud_02_rough_2k.png', 2.0)
    texmat(M_ROCK, 'mossy_rock_diff_2k.png', 'mossy_rock_nor_gl_2k.png', 'mossy_rock_rough_2k.png', 1.5, box=True)
    texmat(M_MOSS, 'mossy_rock_diff_2k.png', 'mossy_rock_nor_gl_2k.png', 'mossy_rock_rough_2k.png', 1.5, (.6, 1.0, .5), box=True)
    texmat(M_BARKR, '../polyhaven-bark/bark_brown_02_diff_2k.png', '../polyhaven-bark/bark_brown_02_nor_gl_2k.png', '../polyhaven-bark/bark_brown_02_rough_2k.png', .9, (.26, .30, .17), box=True)
    texmat(M_ROOT, 'mossy_rock_diff_2k.png', 'mossy_rock_nor_gl_2k.png', 'mossy_rock_rough_2k.png', 1.2, (.7, .55, .4), box=True)

# ---------------- 地面 ----------------
X0, X1, RES = (-175, 175, 1.0) if 'real' in argv else (-130, 130, 1.0)
n = int((X1 - X0) / RES)
xs = np.linspace(X0, X1, n + 1)
V = [(x, y, gh(x, y)) for y in xs for x in xs]
F = [(j * (n + 1) + i, j * (n + 1) + i + 1, (j + 1) * (n + 1) + i + 1, (j + 1) * (n + 1) + i) for j in range(n) for i in range(n)]
me = bpy.data.meshes.new('Ground')
me.from_pydata(V, [], F)
me.materials.append(M_GROUND)
me.materials.append(M_PATH)
for p in me.polygons:
    c = p.center
    p.material_index = 1 if path_d(c.x, c.y) < 1.4 + .4 * math.sin(c.y * .3) else 0
    p.use_smooth = True
if 'real' in argv:   # 泥路用平滑遮罩混材質（不要方塊鋸齒邊）；林床偏綠、帶苔
    pm = np.array([max(0.0, min(1.0, 1 - (path_d(v[0], v[1]) - (1.3 + .4 * math.sin(v[1] * .3))) / 1.1)) for v in V], np.float32)
    ca = me.color_attributes.new('Mask', 'FLOAT_COLOR', 'POINT')
    ca.data.foreach_set('color', np.stack([pm, pm, pm, np.ones_like(pm)], 1).ravel())
    for p in me.polygons:
        p.material_index = 0
    GM = bpy.data.materials.new('GroundReal')
    GM.use_nodes = True
    nt = GM.node_tree
    b = next(x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED')
    tc = nt.nodes.new('ShaderNodeTexCoord')

    def gimg(fn, cs, sc_):
        mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (1 / sc_,) * 3
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = bpy.data.images.load(_GT + fn)
        t.image.colorspace_settings.name = cs
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
        return t.outputs['Color']
    at = nt.nodes.new('ShaderNodeVertexColor')
    at.layer_name = 'Mask'
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = .6
    nz.inputs['Detail'].default_value = 6
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    mk = nt.nodes.new('ShaderNodeMath')
    mk.operation = 'MULTIPLY_ADD'
    nt.links.new(nz.outputs['Fac'], mk.inputs[0])
    mk.inputs[1].default_value = .7
    nt.links.new(at.outputs['Color'], mk.inputs[2])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = .75, 1.05
    nt.links.new(mk.outputs[0], mr.inputs['Value'])
    # 林床：腐葉掃描 × 苔綠斑塊
    leaf = gimg('forest_leaves_02_diffuse_2k.png', 'sRGB', 2.5)
    mz = nt.nodes.new('ShaderNodeTexNoise')
    mz.inputs['Scale'].default_value = .25
    mz.inputs['Detail'].default_value = 4
    nt.links.new(tc.outputs['Object'], mz.inputs['Vector'])
    mrz = nt.nodes.new('ShaderNodeMapRange')
    mrz.inputs['From Min'].default_value, mrz.inputs['From Max'].default_value = .30, .50
    nt.links.new(mz.outputs['Fac'], mrz.inputs['Value'])
    tintA = nt.nodes.new('ShaderNodeMixRGB')
    tintA.inputs[1].default_value = (.30, .27, .21, 1)    # 濕腐葉（深、偏褐，森林地面，不是枯草原）
    tintA.inputs[2].default_value = (.16, .26, .08, 1)    # 苔綠
    nt.links.new(mrz.outputs[0], tintA.inputs[0])
    lf = nt.nodes.new('ShaderNodeMixRGB')
    lf.blend_type = 'MULTIPLY'
    lf.inputs[0].default_value = 1
    nt.links.new(leaf, lf.inputs[1])
    nt.links.new(tintA.outputs[0], lf.inputs[2])
    mud0 = gimg('brown_mud_02_diff_2k.png', 'sRGB', 2.0)
    mt_ = nt.nodes.new('ShaderNodeMixRGB')   # 泥土偏暖棕、濕（設定圖的土色），不要灰水泥色
    mt_.blend_type = 'MULTIPLY'
    mt_.inputs[0].default_value = 1
    mt_.inputs[2].default_value = (1.05, .72, .46, 1)
    nt.links.new(mud0, mt_.inputs[1])
    mud = mt_.outputs[0]
    cm = nt.nodes.new('ShaderNodeMixRGB')
    nt.links.new(mr.outputs[0], cm.inputs[0])
    nt.links.new(lf.outputs[0], cm.inputs[1])
    nt.links.new(mud, cm.inputs[2])
    nt.links.new(cm.outputs[0], b.inputs['Base Color'])
    nmx = nt.nodes.new('ShaderNodeMixRGB')
    nt.links.new(mr.outputs[0], nmx.inputs[0])
    n1 = gimg('forest_leaves_02_nor_gl_2k.png', 'Non-Color', 2.5)
    n2 = gimg('brown_mud_02_nor_gl_2k.png', 'Non-Color', 2.0)
    nt.links.new(n1, nmx.inputs[1])
    nt.links.new(n2, nmx.inputs[2])
    nmn = nt.nodes.new('ShaderNodeNormalMap')
    nt.links.new(nmx.outputs[0], nmn.inputs['Color'])
    nt.links.new(nmn.outputs['Normal'], b.inputs['Normal'])
    _PUD_N = nmn   # 積水窪裡法線要平（水面），下面接 1-pmul 到強度
    rmx = nt.nodes.new('ShaderNodeMapRange')
    nt.links.new(mr.outputs[0], rmx.inputs['Value'])
    rmx.inputs['To Min'].default_value, rmx.inputs['To Max'].default_value = .85, .45   # 泥路濕、反光
    pn = nt.nodes.new('ShaderNodeTexNoise')   # 積水小窪：路上一塊塊
    pn.inputs['Scale'].default_value = .45
    pn.inputs['Detail'].default_value = 4
    nt.links.new(tc.outputs['Object'], pn.inputs['Vector'])
    pmr = nt.nodes.new('ShaderNodeMapRange')
    pmr.inputs['From Min'].default_value, pmr.inputs['From Max'].default_value = .535, .575   # 11/24 設定圖路上水窪多 → 多一些
    nt.links.new(pn.outputs['Fac'], pmr.inputs['Value'])
    pmul = nt.nodes.new('ShaderNodeMath')
    pmul.operation = 'MULTIPLY'
    nt.links.new(pmr.outputs[0], pmul.inputs[0])
    nt.links.new(mr.outputs[0], pmul.inputs[1])
    rfin = nt.nodes.new('ShaderNodeMix')
    nt.links.new(pmul.outputs[0], rfin.inputs['Factor'])
    nt.links.new(rmx.outputs[0], rfin.inputs['A'])
    rfin.inputs['B'].default_value = .04
    nt.links.new(rfin.outputs['Result'], b.inputs['Roughness'])
    cdk = nt.nodes.new('ShaderNodeMixRGB')
    nt.links.new(pmul.outputs[0], cdk.inputs[0])
    nt.links.new(cm.outputs[0], cdk.inputs[1])
    cdk.inputs[2].default_value = (.035, .03, .025, 1)
    nt.links.new(cdk.outputs[0], b.inputs['Base Color'])
    # 11/22 水窪要像設定圖那樣反光：水面法線平、不帶泥土凹凸（原本整片凹凸 → 看起來像灰色濕斑）
    _pinv = nt.nodes.new('ShaderNodeMath'); _pinv.operation = 'SUBTRACT'; _pinv.inputs[0].default_value = 1.0
    nt.links.new(pmul.outputs[0], _pinv.inputs[1])
    nt.links.new(_pinv.outputs[0], _PUD_N.inputs['Strength'])
    b.inputs['IOR'].default_value = 1.33
    me.materials[0] = GM
    # 坑（CO02 獨立模型）底下的主地面壓低，不要蓋住坑洞
    _bm = bmesh.new()   # 坑模型底下的主地面挖掉（不能只壓低，斜面會穿進坑裡）
    _bm.from_mesh(me)
    bmesh.ops.delete(_bm, geom=[f_ for f_ in _bm.faces if math.hypot(f_.calc_center_median().x - PIT[0], f_.calc_center_median().y - PIT[1]) < 5.3 or ('pit2' in argv and math.hypot(f_.calc_center_median().x - PIT2[0], f_.calc_center_median().y - PIT2[1]) < 5.3 * PIT2_S)], context='FACES')
    # 11/21 地面細化（z1nnz：「地板的建模沒有到圖那麼精細」）：近景三區改成 8 cm 細網格，材質做真位移
    #   泥路的凹凸、路邊微微隆起的土埂、積水窪真的凹下去；主地面沒有 DispW 屬性 → 不位移，接縫對得上
    PATCHES = [(-30, 32, -24, 36), (-12, 16, -100, -68), (-16, 14, 86, 118)]
    bmesh.ops.delete(_bm, geom=[f_ for f_ in _bm.faces if any(a_ <= f_.calc_center_median().x <= b_ and c_ <= f_.calc_center_median().y <= d_
                                                              for a_, b_, c_, d_ in PATCHES)], context='FACES')
    _bm.to_mesh(me)
    _bm.free()

    def _pmask(x, y):
        return max(0.0, min(1.0, 1 - (path_d(x, y) - (1.3 + .4 * math.sin(y * .3))) / 1.1))

    def _bilin(Zc, k):   # 粗網格（每 k 格取一點）→ 細網格，分兩軸線性內插
        ny_, nx_ = Zc.shape
        fx = np.linspace(0, nx_ - 1, (nx_ - 1) * k + 1)
        fy = np.linspace(0, ny_ - 1, (ny_ - 1) * k + 1)
        A = np.array([np.interp(fx, np.arange(nx_), r_) for r_ in Zc])
        return np.array([np.interp(fy, np.arange(ny_), A[:, i_]) for i_ in range(A.shape[1])]).T

    _patch_objs = []
    for _pi, (a_, b_, c_, d_) in enumerate(PATCHES):
        K = 3   # 粗 0.25 m 算地形，細 1/12 m 出網格
        xc = np.arange(a_, b_ + 1e-6, .25); yc = np.arange(c_, d_ + 1e-6, .25)
        Hc = np.array([[gh(x_, y_) for x_ in xc] for y_ in yc])
        Mc = np.array([[_pmask(x_, y_) for x_ in xc] for y_ in yc])
        Hf = _bilin(Hc, K); Mf = _bilin(Mc, K)
        nyf, nxf = Hf.shape
        xf = np.linspace(a_, b_, nxf); yf = np.linspace(c_, d_, nyf)
        # 邊界一圈：照主地面 1 m 格的線性高度，不留裂縫
        gi = lambda xx, yy: gh(xx, yy)
        xi = np.arange(a_, b_ + 1); yi = np.arange(c_, d_ + 1)
        Hf[0, :] = np.interp(xf, xi, [gi(x_, c_) for x_ in xi]); Hf[-1, :] = np.interp(xf, xi, [gi(x_, d_) for x_ in xi])
        Hf[:, 0] = np.interp(yf, yi, [gi(a_, y_) for y_ in yi]); Hf[:, -1] = np.interp(yf, yi, [gi(b_, y_) for y_ in yi])
        XX, YY = np.meshgrid(xf, yf)
        edge = np.minimum.reduce([XX - a_, b_ - XX, YY - c_, d_ - YY])
        W = np.clip(edge / 1.5, 0, 1)
        rp_ = np.hypot(XX - PIT[0], YY - PIT[1])
        W = W * np.clip((rp_ - 5.6) / 1.4, 0, 1)
        if 'pit2' in argv:
            W = W * np.clip((np.hypot(XX - PIT2[0], YY - PIT2[1]) - 5.6 * PIT2_S) / 1.4, 0, 1)
        verts = np.stack([XX.ravel(), YY.ravel(), Hf.ravel()], 1).astype(np.float32)
        ii = np.arange((nyf - 1) * (nxf - 1))
        r0 = ii // (nxf - 1); c0 = ii % (nxf - 1)
        v0 = r0 * nxf + c0
        quads = np.stack([v0, v0 + 1, v0 + nxf + 1, v0 + nxf], 1)
        cen = verts[quads].mean(1)
        keep = (np.hypot(cen[:, 0] - PIT[0], cen[:, 1] - PIT[1]) >= 5.3) & (('pit2' not in argv) | (np.hypot(cen[:, 0] - PIT2[0], cen[:, 1] - PIT2[1]) >= 5.3 * PIT2_S))
        quads = quads[keep]
        pme = bpy.data.meshes.new(f'GroundFine{_pi}')
        pme.vertices.add(len(verts)); pme.vertices.foreach_set('co', verts.ravel())
        pme.loops.add(quads.size); pme.loops.foreach_set('vertex_index', quads.ravel().astype(np.int32))
        pme.polygons.add(len(quads))
        pme.polygons.foreach_set('loop_start', (np.arange(len(quads)) * 4).astype(np.int32))
        pme.update(); pme.validate()
        pme.shade_smooth()
        Mv = Mf.ravel().astype(np.float32)
        ca_ = pme.color_attributes.new('Mask', 'FLOAT_COLOR', 'POINT')
        ca_.data.foreach_set('color', np.stack([Mv, Mv, Mv, np.ones_like(Mv)], 1).ravel())
        dw = pme.attributes.new('DispW', 'FLOAT', 'POINT')
        dw.data.foreach_set('value', W.ravel().astype(np.float32))
        pme.materials.append(GM)
        po_ = bpy.data.objects.new(f'GroundFine{_pi}', pme)
        sc.collection.objects.link(po_)
        _patch_objs.append(po_)
        print('PATCH', _pi, len(verts))
    # 位移：林床腐葉 3.5 cm、泥路 9 cm 的掃描高度圖；路邊土埂 +5 cm；積水窪 -5 cm
    _dw = nt.nodes.new('ShaderNodeAttribute'); _dw.attribute_name = 'DispW'
    _dl = gimg('forest_leaves_02_disp_2k.png', 'Non-Color', 2.5)
    _dmud = gimg('brown_mud_02_disp_2k.png', 'Non-Color', 2.0)
    _dmx = nt.nodes.new('ShaderNodeMix')
    nt.links.new(mr.outputs[0], _dmx.inputs['Factor'])
    nt.links.new(_dl, _dmx.inputs['A']); nt.links.new(_dmud, _dmx.inputs['B'])
    _amp = nt.nodes.new('ShaderNodeMapRange')
    nt.links.new(mr.outputs[0], _amp.inputs['Value'])
    _amp.inputs['To Min'].default_value, _amp.inputs['To Max'].default_value = .04, .14
    _dc = nt.nodes.new('ShaderNodeMath'); _dc.operation = 'SUBTRACT'; _dc.inputs[1].default_value = .55
    nt.links.new(_dmx.outputs['Result'], _dc.inputs[0])
    _dh = nt.nodes.new('ShaderNodeMath'); _dh.operation = 'MULTIPLY'
    nt.links.new(_dc.outputs[0], _dh.inputs[0]); nt.links.new(_amp.outputs[0], _dh.inputs[1])
    _l1 = nt.nodes.new('ShaderNodeMath'); _l1.operation = 'SUBTRACT'; _l1.inputs[0].default_value = 1.0
    nt.links.new(mr.outputs[0], _l1.inputs[1])
    _l2 = nt.nodes.new('ShaderNodeMath'); _l2.operation = 'MULTIPLY'
    nt.links.new(mr.outputs[0], _l2.inputs[0]); nt.links.new(_l1.outputs[0], _l2.inputs[1])
    _l3 = nt.nodes.new('ShaderNodeMath'); _l3.operation = 'MULTIPLY_ADD'   # 土埂 .2·m(1-m)·... + 前面
    nt.links.new(_l2.outputs[0], _l3.inputs[0]); _l3.inputs[1].default_value = .2
    nt.links.new(_dh.outputs[0], _l3.inputs[2])
    _pd = nt.nodes.new('ShaderNodeMix')   # 積水窪：水面是平的（不跟著泥土凹凸），比周圍低 6 cm
    nt.links.new(pmul.outputs[0], _pd.inputs['Factor'])
    nt.links.new(_l3.outputs[0], _pd.inputs['A']); _pd.inputs['B'].default_value = -.06
    _dwm = nt.nodes.new('ShaderNodeMath'); _dwm.operation = 'MULTIPLY'
    nt.links.new(_pd.outputs['Result'], _dwm.inputs[0]); nt.links.new(_dw.outputs['Fac'], _dwm.inputs[1])
    _dsp = nt.nodes.new('ShaderNodeDisplacement')
    _dsp.inputs['Midlevel'].default_value = 0.0
    _dsp.inputs['Scale'].default_value = 1.0
    nt.links.new(_dwm.outputs[0], _dsp.inputs['Height'])
    nt.links.new(_dsp.outputs[0], next(x_ for x_ in nt.nodes if x_.type == 'OUTPUT_MATERIAL').inputs['Displacement'])
    try:
        GM.displacement_method = 'BOTH'
    except Exception:
        GM.cycles.displacement_method = 'BOTH'
    with bpy.data.libraries.load(S_ + 'pit_lib.blend', link=False) as (_s, _d):
        _d.objects = [nm for nm in _s.objects if nm.startswith('CO02')]
    _z0 = {}
    for o in _d.objects:
        sc.collection.objects.link(o)
        _z0[o.name] = o.location.z
        o.location = (PIT[0], PIT[1], o.location.z + gh0(*PIT) + .012)
        if o.name == 'CO02_Pit':   # 坑外圈沒土的地方改用林床材質，交界才看不出接縫；坑內與鬆土保留坑自己的泥土材質
            o.data.materials.append(GM)
            _mk = o.data.color_attributes['Mask'].data
            for p_ in o.data.polygons:
                if max(_mk[v_].color[0] for v_ in p_.vertices) < .02:
                    p_.material_index = 1
    if 'pit2' in argv:   # 11/24 小試挖坑：同一個坑模型縮小一份，放在 V3 右前方
        for o in list(_d.objects):
            o2 = o.copy(); o2.data = o.data.copy(); sc.collection.objects.link(o2)
            o2.scale = (PIT2_S, PIT2_S, PIT2_S * .8); o2.rotation_euler.z = 2.1
            o2.location = (PIT2[0], PIT2[1], _z0[o.name] * PIT2_S * .8 + gh0(*PIT2) + .012)
g = bpy.data.objects.new('Ground', me)
sc.collection.objects.link(g)

# 遠方 B 區山（世界地圖上真實存在、之後可到達；東方 600 m 外，只在霧裡露輪廓）
bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=420, radius2=40, depth=260, location=(640, 60, 60))
mt = bpy.context.object
mt.name = 'B_Mountain_real'
mt.scale = (1.0, 1.6, 1.0)
mt.data.materials.append(M_MTN)
# 東側谷地地面延伸到山腳（不留假背景板）
bpy.ops.mesh.primitive_plane_add(size=1, location=(380, 40, -9))
pl = bpy.context.object
pl.scale = (520, 700, 1)
pl.data.materials.append(M_GROUND)


def put(o, m):
    o.data.materials.append(m)
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def blob(loc, r, m, sq=(1, 1, 1), sub=2):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r, location=loc)
    o = bpy.context.object
    o.scale = sq
    return put(o, m)


def cyl(loc, r1, r2, h, m, v=12):
    bpy.ops.mesh.primitive_cone_add(vertices=v, radius1=r1, radius2=r2, depth=h, location=(loc[0], loc[1], loc[2] + h / 2))
    return put(bpy.context.object, m)


# ---------------- 真實模型：神木、祭壇、坑、兩座根拱 ----------------
def append(path, want, offset, dz):
    with bpy.data.libraries.load(path, link=False) as (s, d):
        d.objects = [nm for nm in s.objects if want(nm)]
    got = [o for o in d.objects if o is not None]
    for o in got:
        sc.collection.objects.link(o)
    for o in got:
        if o.parent is None or o.parent not in got:
            o.location = Vector(o.location) + Vector((offset[0], offset[1], dz))
    return got


_MOSSED = set()


def mossify(m, amount=1.0, lift=1.0, furrow=False, reach=0.0, lichen=0.0):   # reach：苔往側面爬多少（0 = 只長在朝上的面）
    """照拱門的做法給樹皮加苔（z1nnz 11/21）：朝上的面、凹處長一片片青苔，凸處帶灰白地衣；樹皮整體提亮成棕灰。
    只改材質節點，接在原本的 Base Color 後面。"""
    if m is None or m.name in _MOSSED or not m.use_nodes:
        return
    _MOSSED.add(m.name)
    nt = m.node_tree
    b = next((x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED'), None)
    if b is None:
        return
    src = b.inputs['Base Color'].links[0].from_socket if b.inputs['Base Color'].links else None
    base_rgb = nt.nodes.new('ShaderNodeRGB')
    base_rgb.outputs[0].default_value = b.inputs['Base Color'].default_value
    hs = nt.nodes.new('ShaderNodeHueSaturation')
    hs.inputs['Value'].default_value = lift
    hs.inputs['Saturation'].default_value = .85
    nt.links.new(src if src else base_rgb.outputs[0], hs.inputs['Color'])
    wt = nt.nodes.new('ShaderNodeMixRGB')   # 偏暖的棕灰（設定圖的樹皮色）
    wt.blend_type = 'MULTIPLY'
    wt.inputs[0].default_value = 1
    wt.inputs[2].default_value = (1.12, .96, .80, 1)
    nt.links.new(hs.outputs[0], wt.inputs[1])
    hs = wt
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['Normal'], sep.inputs[0])
    up = nt.nodes.new('ShaderNodeMapRange')
    up.inputs['From Min'].default_value, up.inputs['From Max'].default_value = .15 - reach, .75 - reach * .6
    nt.links.new(sep.outputs['Z'], up.inputs['Value'])
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = .9
    nz.inputs['Detail'].default_value = 9
    nz.inputs['Roughness'].default_value = .65
    nt.links.new(geo.outputs['Position'], nz.inputs['Vector'])
    pm = nt.nodes.new('ShaderNodeMath')
    pm.operation = 'MULTIPLY_ADD'
    nt.links.new(up.outputs[0], pm.inputs[0])
    pm.inputs[1].default_value = .5 * amount
    nt.links.new(nz.outputs['Fac'], pm.inputs[2])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = .78, 1.0
    nt.links.new(pm.outputs[0], mr.inputs['Value'])
    # 苔色：深綠到黃綠，細碎的苔絨顆粒
    mn = nt.nodes.new('ShaderNodeTexNoise')
    mn.inputs['Scale'].default_value = 60
    mn.inputs['Detail'].default_value = 6
    nt.links.new(geo.outputs['Position'], mn.inputs['Vector'])
    mc = nt.nodes.new('ShaderNodeValToRGB')
    mc.color_ramp.elements[0].position, mc.color_ramp.elements[1].position = .3, .75
    mc.color_ramp.elements[0].color = (.040, .050, .013, 1)   # 橄欖色、斑駁（不要像綠漆）；設定圖 v2 偏黃橄欖
    mc.color_ramp.elements[1].color = (.17, .18, .048, 1)
    nt.links.new(mn.outputs['Fac'], mc.inputs[0])
    mx = nt.nodes.new('ShaderNodeMixRGB')
    nt.links.new(mr.outputs[0], mx.inputs[0])
    nt.links.new(hs.outputs[0], mx.inputs[1])
    nt.links.new(mc.outputs[0], mx.inputs[2])
    # 地衣：灰白小斑，長在沒苔的地方
    ln = nt.nodes.new('ShaderNodeTexNoise')
    ln.inputs['Scale'].default_value = 4.5
    ln.inputs['Detail'].default_value = 10
    nt.links.new(geo.outputs['Position'], ln.inputs['Vector'])
    lr = nt.nodes.new('ShaderNodeMapRange')
    lr.inputs['From Min'].default_value, lr.inputs['From Max'].default_value = .66, .74
    nt.links.new(ln.outputs['Fac'], lr.inputs['Value'])
    lmx = nt.nodes.new('ShaderNodeMixRGB')
    lmx.inputs[2].default_value = (.30, .31, .27, 1)
    lf = nt.nodes.new('ShaderNodeMath')
    lf.operation = 'MULTIPLY'
    lf.inputs[1].default_value = .6
    nt.links.new(lr.outputs[0], lf.inputs[0])
    nt.links.new(lf.outputs[0], lmx.inputs[0])
    nt.links.new(mx.outputs[0], lmx.inputs[1])
    nt.links.new(lmx.outputs[0], b.inputs['Base Color'])
    if lichen > 0:   # 11/25 設定圖 V2、V6 拱門：樹皮上滿是 2–6 cm 的灰白地衣小斑，一群一群，長在沒苔的樹皮上
        sp = nt.nodes.new('ShaderNodeTexNoise')
        sp.inputs['Scale'].default_value = 22
        sp.inputs['Detail'].default_value = 3
        sp.inputs['Roughness'].default_value = .5
        nt.links.new(geo.outputs['Position'], sp.inputs['Vector'])
        spr = nt.nodes.new('ShaderNodeMapRange')
        spr.inputs['From Min'].default_value, spr.inputs['From Max'].default_value = .55, .62   # v1 .60/.66 太少
        nt.links.new(sp.outputs['Fac'], spr.inputs['Value'])
        cl = nt.nodes.new('ShaderNodeTexNoise')   # 成群：大尺度遮罩
        cl.inputs['Scale'].default_value = 1.6
        cl.inputs['Detail'].default_value = 3
        nt.links.new(geo.outputs['Position'], cl.inputs['Vector'])
        clr = nt.nodes.new('ShaderNodeMapRange')
        clr.inputs['From Min'].default_value, clr.inputs['From Max'].default_value = .34, .54
        nt.links.new(cl.outputs['Fac'], clr.inputs['Value'])
        inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'
        inv.inputs[0].default_value = 1
        nt.links.new(mr.outputs[0], inv.inputs[1])   # 苔的地方不長
        f1 = nt.nodes.new('ShaderNodeMath'); f1.operation = 'MULTIPLY'
        nt.links.new(spr.outputs[0], f1.inputs[0]); nt.links.new(clr.outputs[0], f1.inputs[1])
        f2 = nt.nodes.new('ShaderNodeMath'); f2.operation = 'MULTIPLY'
        nt.links.new(f1.outputs[0], f2.inputs[0]); nt.links.new(inv.outputs[0], f2.inputs[1])
        f3 = nt.nodes.new('ShaderNodeMath'); f3.operation = 'MULTIPLY'; f3.use_clamp = True
        nt.links.new(f2.outputs[0], f3.inputs[0]); f3.inputs[1].default_value = lichen
        smx = nt.nodes.new('ShaderNodeMixRGB')
        smx.inputs[2].default_value = (.66, .68, .61, 1)   # 灰白偏一點綠（v1 .50 太暗看不出）
        nt.links.new(f3.outputs[0], smx.inputs[0])
        nt.links.new(lmx.outputs[0], smx.inputs[1])
        nt.links.new(smx.outputs[0], b.inputs['Base Color'])
    if furrow:   # 粗樹皮溝紋（只給神木；拱門用了會變成一格格蛇皮）：沿著樹幹往上拉長的深溝（設定圖神木的樹皮）
        fv = nt.nodes.new('ShaderNodeMapping')
        fv.inputs['Scale'].default_value = (1.6, 1.6, .22)
        nt.links.new(geo.outputs['Position'], fv.inputs['Vector'])
        # 拉長的雜訊取 |fac-.5| 當「離溝多遠」：彎彎曲曲、粗細不一的縱溝（Voronoi 會變成黑色多邊形格線）
        _fn = nt.nodes.new('ShaderNodeTexNoise')
        _fn.inputs['Scale'].default_value = 1.3
        _fn.inputs['Detail'].default_value = 5
        _fn.inputs['Roughness'].default_value = .55
        _fn.inputs['Distortion'].default_value = .4
        nt.links.new(fv.outputs['Vector'], _fn.inputs['Vector'])
        _fs = nt.nodes.new('ShaderNodeMath'); _fs.operation = 'SUBTRACT'; _fs.inputs[1].default_value = .5
        nt.links.new(_fn.outputs['Fac'], _fs.inputs[0])
        _fa = nt.nodes.new('ShaderNodeMath'); _fa.operation = 'ABSOLUTE'
        nt.links.new(_fs.outputs[0], _fa.inputs[0])

        class _VO:   # 跟原本 vo.outputs['Distance'] 同介面
            outputs = {'Distance': _fa.outputs[0]}
        vo = _VO
        fr = nt.nodes.new('ShaderNodeMapRange')
        fr.inputs['From Min'].default_value, fr.inputs['From Max'].default_value = .0, .09
        nt.links.new(vo.outputs['Distance'], fr.inputs['Value'])
        # 只在直立的樹幹面上有縱溝；橫躺的板根、朝上的面不要（不然變一格格）
        _ab = nt.nodes.new('ShaderNodeMath'); _ab.operation = 'ABSOLUTE'
        nt.links.new(sep.outputs['Z'], _ab.inputs[0])
        vert = nt.nodes.new('ShaderNodeMapRange')
        vert.inputs['From Min'].default_value, vert.inputs['From Max'].default_value = .25, .6
        vert.inputs['To Min'].default_value, vert.inputs['To Max'].default_value = 1.0, 0.0
        nt.links.new(_ab.outputs[0], vert.inputs['Value'])
        _fm = nt.nodes.new('ShaderNodeMath'); _fm.operation = 'MULTIPLY'
        nt.links.new(fr.outputs[0], _fm.inputs[0]); nt.links.new(vert.outputs[0], _fm.inputs[1])
        fr = _fm
        bp2 = nt.nodes.new('ShaderNodeBump')
        bp2.inputs['Strength'].default_value = 2.2
        bp2.inputs['Distance'].default_value = .18
        nt.links.new(fr.outputs[0], bp2.inputs['Height'])
        if b.inputs['Normal'].links:
            nt.links.new(b.inputs['Normal'].links[0].from_socket, bp2.inputs['Normal'])
        nt.links.new(bp2.outputs['Normal'], b.inputs['Normal'])
        gd = nt.nodes.new('ShaderNodeMixRGB')   # 溝裡較暗
        gd.blend_type = 'MULTIPLY'
        ginv = nt.nodes.new('ShaderNodeMapRange')
        _iv = nt.nodes.new('ShaderNodeMath'); _iv.operation = 'MULTIPLY_ADD'   # 距離 + (1 - 直立度)：非直立面不加暗溝
        _iv.inputs[1].default_value = -1.0
        nt.links.new(vert.outputs[0], _iv.inputs[0])
        _iv2 = nt.nodes.new('ShaderNodeMath'); _iv2.operation = 'ADD'
        _iv.inputs[2].default_value = 1.0
        nt.links.new(_iv.outputs[0], _iv2.inputs[0]); nt.links.new(vo.outputs['Distance'], _iv2.inputs[1])
        nt.links.new(_iv2.outputs[0], ginv.inputs['Value'])
        ginv.inputs['From Min'].default_value, ginv.inputs['From Max'].default_value = .0, .06
        ginv.inputs['To Min'].default_value, ginv.inputs['To Max'].default_value = .5, 1.0
        nt.links.new(ginv.outputs[0], gd.inputs[2])
        gd.inputs[0].default_value = 1
        nt.links.new(lmx.outputs[0], gd.inputs[1])
        nt.links.new(gd.outputs[0], b.inputs['Base Color'])
    # 苔的地方凸一點、帶絨毛顆粒（苔的範圍 mr × 細雜訊 當高度）
    _mh = nt.nodes.new('ShaderNodeMath'); _mh.operation = 'MULTIPLY'
    nt.links.new(mr.outputs[0], _mh.inputs[0]); nt.links.new(mn.outputs['Fac'], _mh.inputs[1])
    _mbp = nt.nodes.new('ShaderNodeBump')
    _mbp.inputs['Strength'].default_value = .8
    _mbp.inputs['Distance'].default_value = .04
    nt.links.new(_mh.outputs[0], _mbp.inputs['Height'])
    if b.inputs['Normal'].links:
        nt.links.new(b.inputs['Normal'].links[0].from_socket, _mbp.inputs['Normal'])
    nt.links.new(_mbp.outputs['Normal'], b.inputs['Normal'])
    # 苔的地方比較霧面
    if not b.inputs['Roughness'].links:
        b.inputs['Roughness'].default_value = max(b.inputs['Roughness'].default_value, .8)


def glb(path, at, dz, rotz=0.0):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = list(set(bpy.data.objects) - before)
    bpy.context.view_layer.update()
    keep = []
    for o in new:      # 先把網格的世界座標固定下來、解除父子，再刪空物件
        if o.type == 'MESH':
            mw = o.matrix_world.copy()
            o.parent = None
            o.matrix_world = mw
    for o in new:
        if o.type != 'MESH' or 'Collision' in o.name or 'UCX' in o.name or '_LOD1' in o.name or '_LOD2' in o.name:
            bpy.data.objects.remove(o, do_unlink=True)
        else:
            keep.append(o)
    for o in keep:
        o.location = Vector((o.location.x + at[0], o.location.y + at[1], o.location.z + gh(*at) + dz))
    print('GLB', path.split('/')[-1], len(keep))
    return keep


_GTO = append(S_ + ('GT01_out/GT01_GodTree_v004b_detail.blend' if 'real' in argv else 'GT01_out/GT01_GodTree_v003.blend'),
              lambda nm: nm.endswith('_LOD0' if 'real' in argv else '_LOD1'), TREE, gh(*TREE) - .6)
if 'real' in argv:   # v004：樹幹 7 根管＋板根熔成一整塊（z1nnz 11/21「樹幹不連貫」）；熔接後沒有 UV → 樹皮改用盒投影掃描樹皮
    _BK = 'D:/chengtian/4-素材與快取/polyhaven-bark/'
    _bkm = bpy.data.materials.new('GT01_BarkFused')
    _bkm.use_nodes = True
    _bn = _bkm.node_tree
    _bb = next(x for x in _bn.nodes if x.type == 'BSDF_PRINCIPLED')
    _btc = _bn.nodes.new('ShaderNodeTexCoord')
    _bmp = _bn.nodes.new('ShaderNodeMapping')
    _bmp.inputs['Scale'].default_value = (1 / 2.8, 1 / 2.8, 1 / 4.5)   # 11/22 第二步：樹皮板放大約 2.5 倍（跟 gt01_bark_detail.py 的幾何凹凸同一組）
    _bn.links.new(_btc.outputs['Object'], _bmp.inputs['Vector'])

    def _bim(fn, cs):
        t = _bn.nodes.new('ShaderNodeTexImage')
        t.image = bpy.data.images.load(_BK + fn)
        t.image.colorspace_settings.name = cs
        t.projection, t.projection_blend = 'BOX', .35
        _bn.links.new(_bmp.outputs['Vector'], t.inputs['Vector'])
        return t
    _bn.links.new(_bim('bark_brown_02_diff_2k.png', 'sRGB').outputs[0], _bb.inputs['Base Color'])
    _bnm = _bn.nodes.new('ShaderNodeNormalMap')
    _bnm.inputs['Strength'].default_value = 1.5
    _bn.links.new(_bim('bark_brown_02_nor_gl_2k.png', 'Non-Color').outputs[0], _bnm.inputs['Color'])
    _bn.links.new(_bnm.outputs[0], _bb.inputs['Normal'])
    _bb.inputs['Roughness'].default_value = .85
    for _o in _GTO:
        if 'Wood' in _o.name:
            _o.data.materials.clear()
            _o.data.materials.append(_bkm)
if REAL:   # AL02 重做的三層石砌祭壇（正面石階朝南、朝主路）
    _ALTOBJ = append(S_ + 'props_lib.blend', lambda nm: nm == 'AL02_Altar', ALT, gh(*ALT) - .12)
    for _o in _ALTOBJ:
        _o.rotation_euler.z = .35
        if _o.type == 'MESH' and 'nochip' not in argv:   # 11/25 祭壇做舊：石塊缺角（約四成石塊的一兩個角崩掉一塊）＋邊緣不平整的磨損
            _o.data = _o.data.copy()
            _cb = bmesh.new(); _cb.from_mesh(_o.data); _cb.verts.ensure_lookup_table()
            _seen = set(); _CR = random.Random(31); _nchip = 0
            for _v0 in _cb.verts:
                if _v0.index in _seen:
                    continue
                _part, _st = [], [_v0]
                while _st:   # 找出這一塊石頭的全部頂點
                    _x = _st.pop()
                    if _x.index in _seen:
                        continue
                    _seen.add(_x.index); _part.append(_x); _st += [e_.other_vert(_x) for e_ in _x.link_edges]
                _lo = Vector((min(v_.co.x for v_ in _part), min(v_.co.y for v_ in _part), min(v_.co.z for v_ in _part)))
                _hi = Vector((max(v_.co.x for v_ in _part), max(v_.co.y for v_ in _part), max(v_.co.z for v_ in _part)))
                _ct = (_lo + _hi) / 2; _sz = _hi - _lo
                for v_ in _part:   # 邊緣磨損：靠近稜角的頂點往內縮一點、不均勻
                    _e = sum(1 for k_ in range(3) if min(v_.co[k_] - _lo[k_], _hi[k_] - v_.co[k_]) < .07)
                    if _e >= 2:
                        v_.co += (_ct - v_.co).normalized() * .03 * (1 + noise.noise(v_.co * 9))
                for _ in range(_CR.choice((0, 1, 1, 2))):   # v2：v1 從 V3 看不出來 → 缺角變大變多。缺角：只崩上面的角（下面埋在石堆裡看不到）
                    _c = Vector((_CR.choice((_lo.x, _hi.x)), _CR.choice((_lo.y, _hi.y)), _hi.z))
                    _R = min(_sz.x, _sz.y, _sz.z) * _CR.uniform(.65, 1.0)
                    for v_ in _part:
                        d_ = (v_.co - _c).length
                        if d_ < _R:
                            v_.co += (_ct - v_.co).normalized() * (_R - d_) * 1.0 * (1 + .35 * noise.noise(v_.co * 14))
                    _nchip += 1
            _cb.to_mesh(_o.data); _cb.free()
            print('ALTAR CHIPS', _nchip)
        for _sl in _o.material_slots:   # 11/22 優化 2：祭壇補苔（設定圖石階頂面、邊緣、石縫都有橄欖色苔）
            if _sl.material:
                mossify(_sl.material, 2.2, 1.0, reach=.35)   # 1.3 看不出差別（石材本身已偏綠）→ 加量
else:
    glb(EXP + 'AL01_RootAltarTerrace/AL01_RootAltarTerrace_v001.glb', ALT, -.05)
_rim = sum(gh(PIT[0] + 3.3 * math.cos(a_), PIT[1] + 3.3 * math.sin(a_)) for a_ in (0, 1.57, 3.14, 4.71)) / 4
if not REAL:   # 真模型模式的坑直接挖在地形裡（CO01 v002 是平板狀，不像設定圖）
    glb(EXP + 'CO01_ExcavatedPit/CO01_ExcavatedPit_v002.glb', PIT, _rim - gh(*PIT) - .05)
_ARS = glb('D:/chengtian/4-素材與快取/josh-dr01/DR01_RootArch_v006.glb', ARCH_S, -.15)
_ARN = append(S_ + 'root_arch_lib.blend', lambda nm: not (nm in ('Grid', 'Cube') or nm.startswith(('Cylinder', 'Camera', 'Sun', 'Ground', 'Floor'))),
       ARCH_N, gh(*ARCH_N) - .15)
for o in list(bpy.data.objects):     # 根拱庫裡若有非網格物件就拿掉
    if o.type not in ('MESH', 'EMPTY'):
        bpy.data.objects.remove(o, do_unlink=True)
if REAL:   # 神木、兩座拱門：樹皮加苔、提亮（設定圖的棕灰帶苔）
    for o in _GTO:   # 神木樹冠在霧裡太淡 → 壓暗加飽和
        if o.type == 'MESH' and any(k_ in o.name for k_ in ('Leaf', 'Leaves', 'Crown')):
            for sl in o.material_slots:
                m_ = sl.material
                if m_ and m_.use_nodes:
                    b_ = next((x_ for x_ in m_.node_tree.nodes if x_.type == 'BSDF_PRINCIPLED'), None)
                    if b_ and b_.inputs['Base Color'].links:
                        s_ = b_.inputs['Base Color'].links[0].from_socket
                        hs_ = m_.node_tree.nodes.new('ShaderNodeHueSaturation')
                        hs_.inputs['Saturation'].default_value = 1.3
                        hs_.inputs['Value'].default_value = .58
                        m_.node_tree.links.new(s_, hs_.inputs['Color'])
                        # 設定圖：樹冠深綠裡夾一叢叢金黃（外緣最多）→ 世界座標雜訊分出大塊金黃葉叢
                        _t = m_.node_tree
                        _gg = _t.nodes.new('ShaderNodeNewGeometry')
                        _gnz = _t.nodes.new('ShaderNodeTexNoise')
                        _gnz.inputs['Scale'].default_value = .16
                        _gnz.inputs['Detail'].default_value = 3
                        _t.links.new(_gg.outputs['Position'], _gnz.inputs['Vector'])
                        _gmr = _t.nodes.new('ShaderNodeMapRange')
                        _gmr.inputs['From Min'].default_value, _gmr.inputs['From Max'].default_value = .43, .56   # 11/24 六張比對：金黃葉叢再多一點、偏橙
                        _gmr.inputs['To Max'].default_value = .95
                        _t.links.new(_gnz.outputs['Fac'], _gmr.inputs['Value'])
                        _gmx = _t.nodes.new('ShaderNodeMixRGB')
                        _gmx.blend_type = 'MULTIPLY'
                        _gmx.inputs[2].default_value = (2.5, 1.45, .32, 1)   # 金黃偏橙
                        _t.links.new(_gmr.outputs[0], _gmx.inputs[0])
                        _t.links.new(hs_.outputs[0], _gmx.inputs[1])
                        _t.links.new(_gmx.outputs[0], b_.inputs['Base Color'])
    for o in _GTO:
        if o.type == 'MESH' and not any(k_ in o.name for k_ in ('Leaf', 'Leaves', 'Twig', 'Crown')):
            print('MOSS', o.name)
            for sl in o.material_slots:
                mossify(sl.material, 1.0, 1.0, furrow=True)   # 厚苔改用真的苔墊；樹皮本身維持深棕（V3 原本整片發灰綠）
    for o in _ARS + [o_ for o_ in _ARN if o_.type == 'MESH']:
        for sl in o.material_slots:
            if sl.material and not any(k_ in sl.material.name for k_ in ('Leaf', 'Fern', 'Vine', 'Moss', 'UG')):
                mossify(sl.material, 1.4 if o in _ARS else 1.6, 3.0, reach=.15, lichen=(0 if 'nolichen' in argv else 1.0))   # 11/22 設定圖 V2、V6 拱門側面也有一條條苔
    mossify(M_BARKR, .75, 1.6)

# ---------------- 神木的地上根：往祭壇、往外放射 ----------------
def root_ridge(a, b, r0, r1, m=M_ROOT, force=False, tube=False):
    ax, ay = a; bx, by = b
    L = math.hypot(bx - ax, by - ay)
    N = max(3, int(L / 1.2))
    if REAL and not tube and not globals().get('_ROOTCOLS') is None:   # RT01 掃描樹皮長根（roots_lib.blend）
        rc = globals()['_ROOTCOLS']
        L = math.hypot(bx - ax, by - ay)
        if not force and any(path_d(ax + (bx - ax) * s, ay + (by - ay) * s) < 2.2 for s in (.3, .5, .7, .9)):
            return   # 長根不橫跨走道（設定圖的根都沿著路邊）
        e = bpy.data.objects.new('Root', None)
        e.instance_type = 'COLLECTION'
        e.instance_collection = rc[int(abs(ax * 7 + by * 3)) % len(rc)]
        th = r0 / .65
        e.scale = (L / 10.0, th * (1 if (int(ax + by) % 2) else -1), th)
        e.rotation_euler.z = math.atan2(by - ay, bx - ax)
        e.location = (ax, ay, gh(ax, ay) - .1 * th)
        sc.collection.objects.link(e)
        return
    if REAL:   # 真模型模式：一整條漸細、半埋在土裡的樹根（掃描樹皮），不是一顆顆石頭
        cu = bpy.data.curves.new('RootRidge', 'CURVE')
        cu.dimensions = '3D'
        cu.bevel_depth = 1.0
        cu.bevel_resolution = 4
        sp = cu.splines.new('NURBS')
        sp.points.add(N)
        for i in range(N + 1):
            t = i / N
            x = ax + (bx - ax) * t + math.sin(t * 5 + ax) * 1.2
            y = ay + (by - ay) * t + math.cos(t * 4 + ay) * 1.2
            r = (r0 + (r1 - r0) * t) * .55
            sp.points[i].co = (x, y, gh(x, y) + r * .15 - .05 * t, 1)
            sp.points[i].radius = r * (1 - .6 * t ** 2)
        sp.use_endpoint_u = True
        sp.order_u = 3
        o = bpy.data.objects.new('RootRidge', cu)
        sc.collection.objects.link(o)
        cu.resolution_u = 24
        cu.bevel_resolution = 6
        _tx = bpy.data.textures.get('RootLumps') or bpy.data.textures.new('RootLumps', 'CLOUDS')
        _tx.noise_scale = .35
        cu.materials.append(M_BARKR)
        bpy.context.view_layer.update()
        _me = bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bpy.data.objects.remove(o, do_unlink=True)
        o = bpy.data.objects.new('RootRidge', _me)   # 曲線轉成網格才能加凹凸
        sc.collection.objects.link(o)
        _sub = o.modifiers.new('Sub', 'SUBSURF')
        _sub.levels = _sub.render_levels = 1
        _dm = o.modifiers.new('Lumps', 'DISPLACE')   # 樹根表面不規則的瘤與起伏
        _dm.texture = _tx
        _dm.strength = r0 * .35
        _dm.mid_level = .5
        _dm.texture_coords = 'GLOBAL'
        return
    for i in range(N + 1):
        t = i / N
        x = ax + (bx - ax) * t + math.sin(t * 5 + ax) * 1.2
        y = ay + (by - ay) * t + math.cos(t * 4 + ay) * 1.2
        r = r0 + (r1 - r0) * t
        blob((x, y, gh(x, y) + r * .1), r, m, sq=(1, 1, .55), sub=1)


if REAL:
    _ROOTCOLS = []
    with bpy.data.libraries.load(S_ + 'roots_lib.blend', link=False) as (_s, _d):
        _d.objects = [nm for nm in _s.objects if nm.startswith('RT01')]
    for _v in 'ABCD':
        _c = bpy.data.collections.new('RT01_' + _v)
        for _o in _d.objects:
            if _o is not None and _o.name.startswith('RT01_Root_' + _v):
                _c.objects.link(_o)
        _ROOTCOLS.append(_c)
    for _o in _d.objects:   # 長根：樹皮為主、頂上一條條苔（不要整條綠）
        if _o is not None:
            for _sl in _o.material_slots:
                mossify(_sl.material, .9, 1.2, reach=.25)   # 11/22 V5 右邊長根：設定圖頂上整條厚苔
else:
    _ROOTCOLS = None
ROOTS = []
for k in range(9):
    ang = -1.25 + k * .55 + R.uniform(-.15, .15)
    L = R.uniform(14, 24)
    ROOTS.append(((TREE[0] + math.cos(ang) * 6, TREE[1] - math.sin(ang) * 6), (TREE[0] + math.cos(ang) * L, TREE[1] - math.sin(ang) * L)))
ROOTS.append(((TREE[0] + 6, TREE[1] - 5), (ALT[0] - 4, ALT[1] + 2)))           # 兩條長根延伸到祭壇邊
ROOTS.append(((TREE[0] + 4, TREE[1] - 7), (ALT[0] - 2, ALT[1] - 4)))
for a, b in ROOTS:
    root_ridge(a, b, 1.5, .45)
if REAL:   # V5 設定圖：支路兩旁各有幾條沿著路走的長根
    for a, b, r in [((-11.5, 9), (-15, -3), .9), ((-2, 16), (2, 6), .8)]:
        root_ridge(a, b, r, .4, force=True, tube=True)   # 11/22 掃描根頭尾是切面、頂上一片平苔 → 改整條漸細的根
    # 11/22 V5 路右邊兩條交疊的大苔根（設定圖：從畫面右邊伸過來、往路邊斜下去鑽進土裡；前面那條壓在後面那條上）
    #   z1nnz「又翹起來了」：根要貼地、下半埋進土裡，不能斜斜翹在空中
    #   整條漸細的獨立模型（不是頭尾切面的掃描根）；點用 V5 鏡頭座標（往前 fd、往右 rd）
    _c5 = Vector((-6, 12)); _f5 = Vector((23, -33)).normalized(); _r5 = Vector((_f5.y, -_f5.x))
    _v5m = _bkm.copy()
    _v5m.name = 'V5RootBark'
    next(x_ for x_ in _v5m.node_tree.nodes if x_.type == 'MAPPING').inputs['Scale'].default_value = (1 / .4, 1 / .4, 1 / .4)   # 細一點：大塊盒投影在圓根上會拉成直條紋
    _vt = _v5m.node_tree
    _vuv = _vt.nodes.new('ShaderNodeUVMap'); _vuv.uv_map = 'UVMap'
    _vmp = next(x_ for x_ in _vt.nodes if x_.type == 'MAPPING'); _vmp.inputs['Scale'].default_value = (1, 1, 1)
    _vt.links.new(_vuv.outputs['UV'], _vmp.inputs['Vector'])
    for _ti in _vt.nodes:
        if _ti.type == 'TEX_IMAGE':
            _ti.projection = 'FLAT'
    mossify(_v5m, .45, 1.0)   # 11/22：苔只留在背脊一條（整片頂面都是苔 → 從低角度看像草皮平台）
    for _k, (_pts, _r0, _r1) in enumerate((
            ([(3.6, 4.9, .38), (4.3, 3.4, .34), (5.1, 2.2, .24), (6.0, 1.4, -.12)], .58, .2),   # 近的、粗的：從畫面右下斜上去
            ([(6.8, 7.6, .32), (7.4, 5.6, .3), (8.4, 3.7, .2), (9.4, 2.4, -.1)], .45, .16))):   # 後面那條：從右邊較高處下來
        # 11/22：曲線轉出來的根從低角度看像平台 → 改成自己一圈圈建的圓管（截面一定是圓的）
        _ctr = []
        for _j, (_fd, _rd, _z) in enumerate(_pts):
            _p = _c5 + _f5 * _fd + _r5 * _rd
            _rr = _r0 + (_r1 - _r0) * (_j / (len(_pts) - 1))
            _ctr.append((Vector((_p.x, _p.y, gh(_p.x, _p.y) + (_rr * .45 if _z > 0 else _z))), _rr))
            if _j < len(_pts) - 1:
                _q = _c5 + _f5 * _pts[_j + 1][0] + _r5 * _pts[_j + 1][1]
                for _u in range(6):
                    globals().setdefault('_V5RP', []).append(_p + (_q - _p) * (_u / 6))
        _bm = bmesh.new(); _rings = []; _NS = 40
        for _i in range(_NS + 1):
            _t = _i / _NS * (len(_ctr) - 1); _a = min(int(_t), len(_ctr) - 2); _f = _t - _a
            _c = _ctr[_a][0].lerp(_ctr[_a + 1][0], _f); _rr = _ctr[_a][1] + (_ctr[_a + 1][1] - _ctr[_a][1]) * _f
            _c.z = gh(_c.x, _c.y) + (_rr * .45 if _i < _NS * .8 else _rr * .45 - (_i - _NS * .8) / (_NS * .2) * _rr * 1.4)
            _tg = (_ctr[_a + 1][0] - _ctr[_a][0]); _tg.z = 0; _tg.normalize()
            _sd = Vector((-_tg.y, _tg.x, 0))
            _rg = []
            for _j in range(16):
                _an = 2 * math.pi * _j / 16
                _off = _sd * math.cos(_an) + Vector((0, 0, 1)) * math.sin(_an)
                _rg.append(_bm.verts.new(_c + _off * _rr * (1 + .08 * noise.noise(Vector((_i * .4, _j * .5, _k * 3))))))
            _rings.append(_rg)
        for _i in range(_NS):
            for _j in range(16):
                _bm.faces.new((_rings[_i][_j], _rings[_i][(_j + 1) % 16], _rings[_i + 1][(_j + 1) % 16], _rings[_i + 1][_j]))
        _uvl = _bm.loops.layers.uv.new('UVMap')   # u 繞一圈、v 沿根長度 → 樹皮紋路順著根走
        for _fc in _bm.faces:
            for _lp in _fc.loops:
                _vi = _lp.vert.index
                _lp[_uvl].uv = ((_vi % 16) / 16 * 2 * math.pi * _r0 / 1.2, (_vi // 16) / _NS * 6.0 / 1.6)
        _me = bpy.data.meshes.new(f'V5Root{_k}'); _bm.to_mesh(_me); _bm.free()
        for _pp in _me.polygons:
            _pp.use_smooth = True
        _me.materials.append(_v5m)
        _o = bpy.data.objects.new(f'V5Root{_k}', _me); sc.collection.objects.link(_o)
        _o.hide_render = 'v5root' not in argv   # 11/22：試了曲線、圓管、順向 UV，從 V5 低角度看都像一塊草皮平台 → 先不放，之後換真的根模型
        _o.modifiers.new('Sub', 'SUBSURF').render_levels = 1
        _dm = _o.modifiers.new('Lumps', 'DISPLACE')   # 根表面不規則的瘤與起伏
        _dm.texture = bpy.data.textures.get('RootLumps') or bpy.data.textures.new('RootLumps', 'CLOUDS')
        _dm.texture.noise_scale = .35
        _dm.strength = .12; _dm.mid_level = .5; _dm.texture_coords = 'GLOBAL'
    # 11/22 新物件：倒木與斷枝（設定圖 V5 左下一根灰白枯枝、V3 路邊零星斷枝）；全部貼地、下半截埋進土裡
    _dwm = bpy.data.materials.new('DeadWood'); _dwm.use_nodes = True
    _dn = _dwm.node_tree; _db = next(x_ for x_ in _dn.nodes if x_.type == 'BSDF_PRINCIPLED')
    _dtc = _dn.nodes.new('ShaderNodeTexCoord'); _dmp = _dn.nodes.new('ShaderNodeMapping'); _dmp.inputs['Scale'].default_value = (1 / .5, 1 / .5, 1 / .9)
    _dn.links.new(_dtc.outputs['Object'], _dmp.inputs['Vector'])
    _dti = _dn.nodes.new('ShaderNodeTexImage'); _dti.image = bpy.data.images.load('D:/chengtian/4-素材與快取/polyhaven-bark/bark_brown_02_diff_2k.png')
    _dti.projection, _dti.projection_blend = 'BOX', .3; _dn.links.new(_dmp.outputs['Vector'], _dti.inputs['Vector'])
    _dhs = _dn.nodes.new('ShaderNodeHueSaturation'); _dhs.inputs['Saturation'].default_value = .35; _dhs.inputs['Value'].default_value = 1.6   # 枯木灰白
    _dn.links.new(_dti.outputs['Color'], _dhs.inputs['Color']); _dn.links.new(_dhs.outputs['Color'], _db.inputs['Base Color'])
    _db.inputs['Roughness'].default_value = .9
    mossify(_dwm, .7, 1.0)

    def deadbranch(p0, ang, L, r0, seed, mind=2.0):
        rr_ = random.Random(seed)
        d_ = Vector((math.cos(ang), math.sin(ang), 0))
        sd_ = Vector((-d_.y, d_.x, 0))
        segs = [(d_ * (L * t) + sd_ * (.25 * math.sin(t * 5 + seed)), r0 * (1 - .6 * t)) for t in (0, .25, .5, .75, 1)]
        parts = [segs]
        for _i in range(rr_.randint(2, 4)):   # 側枝：從主枝長出去，也躺在地上
            t0 = rr_.uniform(.25, .85); b0 = d_ * (L * t0) + sd_ * (.25 * math.sin(t0 * 5 + seed))
            ba = ang + rr_.choice((-1, 1)) * rr_.uniform(.5, 1.0); bl = rr_.uniform(.4, 1.2) * L * .4
            bd = Vector((math.cos(ba), math.sin(ba), 0))
            parts.append([(b0, r0 * .4), (b0 + bd * bl * .5, r0 * .3), (b0 + bd * bl, r0 * .12)])
        for _k, pts_ in enumerate(parts):
            # 11/22 z1nnz「擋到路了」：枝條任何一點進到走道（離路中線 2 m 內）就不放
            if any(path_d(p0[0] + q_.x, p0[1] + q_.y) < mind for q_, r_ in pts_):
                print('DEADBRANCH skip', seed, _k)
                continue
            cu_ = bpy.data.curves.new('DeadBranch', 'CURVE'); cu_.dimensions = '3D'; cu_.bevel_depth = 1.0; cu_.bevel_resolution = 4
            cu_.use_fill_caps = True; cu_.resolution_u = 12
            sp_ = cu_.splines.new('NURBS'); sp_.points.add(len(pts_) - 1)
            for _j, (q_, r_) in enumerate(pts_):
                w_ = Vector((p0[0], p0[1], 0)) + q_
                sp_.points[_j].co = (w_.x, w_.y, gh(w_.x, w_.y) + r_ * .35, 1)   # 中心只比地面高 0.35 倍半徑 → 下半截在土裡
                sp_.points[_j].radius = r_
            sp_.use_endpoint_u = True; sp_.order_u = min(3, len(pts_))
            cu_.materials.append(_dwm)
            ob_ = bpy.data.objects.new('DeadBranch', cu_); sc.collection.objects.link(ob_)

    _c3 = Vector((4, -15)); _f3 = Vector((2, 33)).normalized(); _r3 = Vector((_f3.y, -_f3.x))
    _p = _c5 + (_f5 * 2.6 + _r5 * -4.4 if 'oldv5branch' in argv else _f5 * 2.2 + _r5 * -2.3)   # V5 左下那根灰白枯枝：躺在路左邊，順著路的方向，不伸進走道（11/25 原位置在畫面外 → 移進左下角）
    _dv = _f5 * .97 + _r5 * -.25
    deadbranch((_p.x, _p.y), math.atan2(_dv.y, _dv.x), 4.6, .17, 1, mind=1.8)
    if 'notwigs' not in argv:   # 11/25 設定圖 V5 左下、V2 路邊：一根根細枯枝（1–3 cm 粗、20–80 cm 長，帶一兩個分叉），散在路邊草和泥上，不進走道
        _TW = random.Random(57); _ntw = 0
        _twc = [(_c5.x, _c5.y), (2.5, -90), (2.0, -78), (4, -15), (8, -2)]
        for cx_, cy_ in _twc:
            for _ in range(700):
                x_, y_ = cx_ + _TW.uniform(-14, 14), cy_ + _TW.uniform(-14, 14)
                pd_ = path_d(x_, y_)
                if not (2.0 < pd_ < 4.8) or _TW.random() > (.9 if pd_ < 3.2 else .5):   # v2：v1 太稀、有的落在泥路邊
                    continue
                a_ = _TW.uniform(0, 6.283); L_ = _TW.uniform(.2, .8); r_ = _TW.uniform(.008, .022) * (.6 + L_)
                d_ = Vector((math.cos(a_), math.sin(a_), 0)); sd_ = Vector((-d_.y, d_.x, 0))
                bend_ = _TW.uniform(-.12, .12)
                main_ = [(d_ * (L_ * t) + sd_ * (bend_ * math.sin(t * 3.1) * L_), r_ * (1 - .55 * t)) for t in (0, .33, .66, 1)]
                parts_ = [main_]
                for _f in range(_TW.choice((0, 1, 1, 2))):   # 分叉
                    t0 = _TW.uniform(.3, .75); b0 = main_[1][0].lerp(main_[2][0], t0)
                    ba = a_ + _TW.choice((-1, 1)) * _TW.uniform(.4, .9); bl = L_ * _TW.uniform(.25, .5)
                    parts_.append([(b0, r_ * .5), (b0 + Vector((math.cos(ba), math.sin(ba), 0)) * bl, r_ * .25)])
                if any(path_d(x_ + q_.x, y_ + q_.y) < 1.9 for pt_ in parts_ for q_, _r in pt_):
                    continue
                for pt_ in parts_:
                    cu_ = bpy.data.curves.new('Twig', 'CURVE'); cu_.dimensions = '3D'; cu_.bevel_depth = 1.0; cu_.bevel_resolution = 1
                    cu_.use_fill_caps = True; cu_.resolution_u = 4
                    sp_ = cu_.splines.new('POLY'); sp_.points.add(len(pt_) - 1)
                    for _j, (q_, rq_) in enumerate(pt_):
                        w_ = Vector((x_, y_, 0)) + q_
                        sp_.points[_j].co = (w_.x, w_.y, gh(w_.x, w_.y) + rq_ * .6 + _TW.uniform(0, .015), 1)   # 細枝架在落葉草上，不全埋
                        sp_.points[_j].radius = rq_
                    cu_.materials.append(_dwm)
                    sc.collection.objects.link(bpy.data.objects.new('Twig', cu_))
                _ntw += 1
        print('TWIGS', _ntw)
    for _fd, _rd, _ang, _L, _r0, _sd in ((7, -4.5, .4, 3.2, .12, 2), (9.5, 3.5, 2.6, 2.6, .1, 3), (12, -6.5, 1.2, 3.4, .13, 4), (5.5, 5.5, -.3, 2.2, .08, 5)):   # V3 路邊零星斷枝
        _p = _c3 + _f3 * _fd + _r3 * _rd
        deadbranch((_p.x, _p.y), _ang, _L, _r0, _sd)
    # 11/22 新物件：苔丘（設定圖 V5 路左邊、祭壇後面一團長滿厚苔的小土丘）；獨立模型，底部埋進地裡
    _mm = bpy.data.materials.new('MossMound'); _mm.use_nodes = True
    _mn = _mm.node_tree; _mb = next(x_ for x_ in _mn.nodes if x_.type == 'BSDF_PRINCIPLED')
    _mg = _mn.nodes.new('ShaderNodeNewGeometry')
    _mz1 = _mn.nodes.new('ShaderNodeTexNoise'); _mz1.inputs['Scale'].default_value = 2.5; _mz1.inputs['Detail'].default_value = 6
    _mn.links.new(_mg.outputs['Position'], _mz1.inputs['Vector'])
    _mcr = _mn.nodes.new('ShaderNodeValToRGB')
    _mcr.color_ramp.elements[0].position, _mcr.color_ramp.elements[1].position = .3, .75
    _mcr.color_ramp.elements[0].color = (.025, .032, .01, 1); _mcr.color_ramp.elements[1].color = (.10, .11, .035, 1)   # 暗橄欖，不要亮綠
    _mn.links.new(_mz1.outputs['Fac'], _mcr.inputs[0]); _mn.links.new(_mcr.outputs[0], _mb.inputs['Base Color'])
    _mz2 = _mn.nodes.new('ShaderNodeTexNoise'); _mz2.inputs['Scale'].default_value = 90; _mz2.inputs['Detail'].default_value = 2
    _mn.links.new(_mg.outputs['Position'], _mz2.inputs['Vector'])
    _mbp = _mn.nodes.new('ShaderNodeBump'); _mbp.inputs['Strength'].default_value = .8; _mbp.inputs['Distance'].default_value = .015
    _mn.links.new(_mz2.outputs['Fac'], _mbp.inputs['Height']); _mn.links.new(_mbp.outputs['Normal'], _mb.inputs['Normal'])
    _mb.inputs['Roughness'].default_value = .95
    try:
        _mb.inputs['Sheen Weight'].default_value = .5; _mb.inputs['Sheen Tint'].default_value = (.5, .6, .3, 1)
    except KeyError:
        pass

    def moss_mound(x, y, w, h, seed):
        bm_ = bmesh.new(); bmesh.ops.create_icosphere(bm_, subdivisions=5, radius=1)
        off_ = Vector((seed * 3.1, 1.3, 0))
        for v in bm_.verts:
            c = v.co.copy()
            lump = noise.noise(c * 1.6 + off_) * .25 + noise.noise(c * 4.5 + off_) * .07   # 一團團隆起，不是正圓
            r = 1 + lump
            v.co = Vector((c.x * w * r, c.y * w * .85 * r, max(c.z, -.3) * h * (1 + lump)))
        me_ = bpy.data.meshes.new('MossMound'); bm_.to_mesh(me_); bm_.free()
        for p_ in me_.polygons:
            p_.use_smooth = True
        me_.materials.append(_mm)
        ob_ = bpy.data.objects.new('MossMound', me_); sc.collection.objects.link(ob_)
        ob_.location = (x, y, gh(x, y) - h * .25)
    _p = _c5 + _f5 * 11 + _r5 * -3.0
    moss_mound(_p.x, _p.y, 2.0, 1.0, 1)

    # 11/23 故事「從前是聖地」：石燈籠（一座站著但歪了、一座倒下摔成兩截）＋斷石柱；石材跟祭壇同一套、長苔
    _stm = bpy.data.materials.get('AL02_Stone')
    _lsm = _stm.copy() if _stm else bpy.data.materials.new('LanternStone')
    _lsm.name = 'LanternStone'
    _MOSSED.discard(_lsm.name)
    mossify(_lsm, 1.6, 1.0, reach=.2)

    def _oct(bm_, z0, h, r0, r1, seg=8, ox=0.0):
        g = bmesh.ops.create_cone(bm_, cap_ends=True, segments=seg, radius1=r0, radius2=r1, depth=h)
        bmesh.ops.translate(bm_, verts=g['verts'], vec=Vector((ox, 0, z0 + h / 2)))
        return g['verts']

    def _box(bm_, z0, sx, sy, sz):
        g = bmesh.ops.create_cube(bm_, size=1)
        for v in g['verts']:
            v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz + z0 + sz / 2))
        return g['verts']

    def lantern_parts(seed):
        # 由下到上：基座、柱、托盤、燈室（四面開窗）、屋頂（翹角）、寶珠；全高約 2.3 m
        rr_ = random.Random(seed)
        lower = bmesh.new(); upper = bmesh.new()
        _oct(lower, 0, .22, .42, .38); _oct(lower, .22, .08, .3, .3)
        _oct(lower, .3, .85, .14, .12, seg=8)
        _oct(lower, 1.15, .12, .2, .34, seg=6)
        _box(upper, 0, .46, .46, .42)                              # 燈室
        for k in range(4):                                         # 四面窗：往內凹的暗格
            a = k * math.pi / 2
            w = bmesh.ops.create_cube(upper, size=1)['verts']
            for v in w:
                v.co = Vector((v.co.x * .2, v.co.y * .06, v.co.z * .22))
                v.co.rotate(Matrix.Rotation(a, 3, 'Z'))
                v.co += Vector((math.cos(a + math.pi / 2) * 0, 0, 0)) + Vector((math.sin(a) * .22, math.cos(a) * .22, .21))
        rf = _oct(upper, .42, .32, .52, .06, seg=6)               # 六角屋頂
        for v in rf:                                               # 翹角：外緣角上翹
            if v.co.z < .5 and v.co.xy.length > .45:
                v.co.z += .06
        _oct(upper, .74, .1, .07, .02, seg=8); bmesh.ops.create_uvsphere(upper, u_segments=8, v_segments=6, radius=.07)
        for v in upper.verts:
            if v.co.length < .08 and abs(v.co.z) < .08:
                v.co.z += .88
        out = []
        for nm, bm_ in (('LanternLower', lower), ('LanternUpper', upper)):
            for v in bm_.verts:   # 邊角缺損：每個頂點隨機往內縮一點（舊、被風化）
                v.co *= 1 - .04 * rr_.random()
            me_ = bpy.data.meshes.new(nm); bm_.to_mesh(me_); bm_.free()
            me_.materials.append(_lsm)
            out.append(me_)
        return out

    def place_lantern(x, y, rot, tilt, fallen, seed):
        lo, up = lantern_parts(seed)
        z = gh(x, y)
        if not fallen:   # 站著但歪了、底座陷進土裡
            for me_, dz in ((lo, 0), (up, 1.27)):
                o = bpy.data.objects.new(me_.name, me_); sc.collection.objects.link(o)
                o.location = (x, y, z - .12)
                o.rotation_euler = (tilt, 0, rot)
                o.data.transform(Matrix.Translation((0, 0, dz)))
        else:            # 倒下：下半截橫躺，上半截（燈室＋屋頂）摔到一邊、斜插在土裡
            o = bpy.data.objects.new(lo.name, lo); sc.collection.objects.link(o)
            o.location = (x, y, z + .18); o.rotation_euler = (math.pi / 2 - .05, 0, rot)
            o2 = bpy.data.objects.new(up.name, up); sc.collection.objects.link(o2)
            d_ = Vector((math.cos(rot + math.pi / 2), math.sin(rot + math.pi / 2), 0))
            p2 = Vector((x, y, 0)) + d_ * -1.9 + Vector((-d_.y, d_.x, 0)) * .5
            o2.location = (p2.x, p2.y, gh(p2.x, p2.y) - .1); o2.rotation_euler = (1.1, .4, rot + .7)
        print('LANTERN', round(x, 1), round(y, 1), 'fallen' if fallen else 'tilted')

    def broken_pillar(x, y, h, rot, seed):
        rr_ = random.Random(seed)
        bm_ = bmesh.new()
        _box(bm_, 0, .5, .5, .25)                     # 柱礎
        g = _oct(bm_, .25, h, .2, .19, seg=12)
        for v in g:                                    # 斷口：頂面高低不平
            if v.co.z > .25 + h * .9:
                v.co.z -= rr_.uniform(0, .35)
        for v in bm_.verts:
            v.co *= 1 - .03 * rr_.random()
        me_ = bpy.data.meshes.new('BrokenPillar'); bm_.to_mesh(me_); bm_.free(); me_.materials.append(_lsm)
        o = bpy.data.objects.new('BrokenPillar', me_); sc.collection.objects.link(o)
        o.location = (x, y, gh(x, y) - .15); o.rotation_euler = (rr_.uniform(-.06, .06), rr_.uniform(-.06, .06), rot)
        # 斷下來的那一截倒在旁邊
        bm2 = bmesh.new(); _oct(bm2, 0, h * .7, .19, .18, seg=12)
        me2 = bpy.data.meshes.new('PillarPiece'); bm2.to_mesh(me2); bm2.free(); me2.materials.append(_lsm)
        o2 = bpy.data.objects.new('PillarPiece', me2); sc.collection.objects.link(o2)
        d_ = Vector((math.cos(rot), math.sin(rot), 0)); q = Vector((x, y, 0)) + d_ * .5
        o2.location = (q.x, q.y, gh(q.x, q.y) + .1); o2.rotation_euler = (math.pi / 2, 0, rot + .2)
        print('PILLAR', round(x, 1), round(y, 1))

    def _clear(x, y, need=2.4):   # 不擋路：離路中線 need m 以上，否則沿著遠離路的方向推出去
        for _ in range(20):
            if path_d(x, y) >= need:
                return x, y
            e = .2
            gx = path_d(x + e, y) - path_d(x - e, y); gy = path_d(x, y + e) - path_d(x, y - e)
            n = math.hypot(gx, gy) or 1
            x += gx / n * .4; y += gy / n * .4
        return x, y
    _PROPS = []   # 11/24 影片「接地」：每個擺件底下補土堆、周圍長草 (x, y, 半徑)
    _q = _clear(ALT[0] - 4.2, ALT[1] - 3.2); place_lantern(*_q, .35, .09, False, 1); _PROPS.append((*_q, .45))      # 祭壇前左：歪掉的那座
    _q = _clear(ALT[0] + 4.0, ALT[1] - 2.6); place_lantern(*_q, .35, 0, True, 2); _PROPS.append((*_q, .55))         # 祭壇前右：倒下摔成兩截
    _q = _clear(ALT[0] - 6.5, ALT[1] + 3.0); broken_pillar(*_q, 1.4, .6, 3); _PROPS.append((*_q, .6))               # 祭壇左後：斷石柱

    # 11/23 故事「有人來挖過」：坑邊丟下的工具——斷柄木鏟、翻倒的破竹簍、碎陶片（V4 看得到的坑口前緣）
    def _mat(nm, col, rough, noise_s=0.0, col2=None):
        m = bpy.data.materials.new(nm); m.use_nodes = True
        b = next(x_ for x_ in m.node_tree.nodes if x_.type == 'BSDF_PRINCIPLED')
        b.inputs['Roughness'].default_value = rough
        if col2:
            t = m.node_tree; n_ = t.nodes.new('ShaderNodeTexNoise'); n_.inputs['Scale'].default_value = noise_s
            cr = t.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = (*col, 1); cr.color_ramp.elements[1].color = (*col2, 1)
            t.links.new(n_.outputs['Fac'], cr.inputs[0]); t.links.new(cr.outputs[0], b.inputs['Base Color'])
        else:
            b.inputs['Base Color'].default_value = (*col, 1)
        return m
    _m_iron = _mat('RustyIron', (.03, .025, .02), .75, 18, (.12, .05, .02))
    _m_handle = _mat('OldHandle', (.09, .07, .05), .85, 25, (.05, .04, .03))   # 舊木柄：暗、髒（枯木灰白太亮、像新的）
    _m_bamboo = _mat('OldBamboo', (.16, .12, .06), .8, 30, (.08, .06, .035))   # 舊竹篾：暗、髒
    _m_pot = _mat('Pottery', (.30, .14, .07), .8, 12, (.18, .10, .06))
    _pf = Vector((-5, 8.5)).normalized(); _pr = Vector((_pf.y, -_pf.x)); _rim = Vector(PIT) - _pf * 4.3   # V4 鏡頭這一側的坑口外
    # 木鏟：斷掉的木柄（斷口參差）＋鏽鐵鏟頭，斜躺在翻土上
    _sp = _rim + _pr * 1.4; _sa = math.atan2(_pr.y, _pr.x) + .5
    bm_ = bmesh.new()
    g = bmesh.ops.create_cone(bm_, cap_ends=True, segments=10, radius1=.022, radius2=.02, depth=.85)
    for v in g['verts']:
        if v.co.z > .4:
            v.co.z += random.Random(int(v.co.x * 1000)).uniform(-.05, .04)   # 斷口
    bmesh.ops.rotate(bm_, verts=g['verts'], cent=Vector(), matrix=Matrix.Rotation(math.pi / 2, 3, 'Y'))
    bmesh.ops.translate(bm_, verts=g['verts'], vec=Vector((.42, 0, 0)))
    me_ = bpy.data.meshes.new('ShovelHandle'); bm_.to_mesh(me_); bm_.free(); me_.materials.append(_m_handle)
    bm_ = bmesh.new(); g = bmesh.ops.create_cube(bm_, size=1)
    for v in g['verts']:
        v.co = Vector((-.14 + v.co.x * .28 * (1 if v.co.x > 0 else .85), v.co.y * .2 * (1 - .3 * (v.co.x < 0)), v.co.z * .012))
    me2 = bpy.data.meshes.new('ShovelBlade'); bm_.to_mesh(me2); bm_.free(); me2.materials.append(_m_iron)
    for me_x in (me_, me2):
        o = bpy.data.objects.new(me_x.name, me_x); sc.collection.objects.link(o)
        o.location = (_sp.x, _sp.y, gh0(*PIT) + .06); o.rotation_euler = (.05, -.06, _sa)   # 鏟頭半埋在土裡
    # 竹簍：直立竹篾 + 一圈圈箍，翻倒側躺，一側破一個缺口
    _bp = _rim - _pr * 2.2; _ba = math.atan2(_pf.y, _pf.x) + 1.2
    bm_ = bmesh.new(); R_b, H_b = .26, .42
    for k in range(28):
        a = 2 * math.pi * k / 28
        if 2.2 < a < 2.9:
            continue   # 破洞
        g = bmesh.ops.create_cube(bm_, size=1)
        for v in g['verts']:
            v.co = Vector((v.co.x * .012, v.co.y * .03, v.co.z * H_b + H_b / 2))
        bmesh.ops.rotate(bm_, verts=g['verts'], cent=Vector(), matrix=Matrix.Rotation(a, 3, 'Z'))
        bmesh.ops.translate(bm_, verts=g['verts'], vec=Vector((math.cos(a) * R_b * (1 + .1 * (k % 3 == 0)), math.sin(a) * R_b, 0)))
    for zz in (.03, .2, .39):
        g = bmesh.ops.create_cone(bm_, cap_ends=False, segments=24, radius1=R_b + .015, radius2=R_b + .015, depth=.025)
        bmesh.ops.translate(bm_, verts=g['verts'], vec=Vector((0, 0, zz)))
    me_ = bpy.data.meshes.new('Basket'); bm_.to_mesh(me_); bm_.free(); me_.materials.append(_m_bamboo)
    o = bpy.data.objects.new('Basket', me_); sc.collection.objects.link(o)
    o.location = (_bp.x, _bp.y, gh0(*PIT) + R_b * .85 + .05); o.rotation_euler = (math.pi / 2 - .15, 0, _ba)
    # 碎陶片：彎的破片，散在竹簍旁和坑口
    PR_ = random.Random(9)
    bm_ = bmesh.new()
    for k in range(14):
        c = _bp + Vector((PR_.uniform(-1.3, 1.6), PR_.uniform(-1, 1.2)))
        a0, da = PR_.uniform(0, 6.28), PR_.uniform(.5, 1.1); h_ = PR_.uniform(.06, .14); rr = PR_.uniform(.12, .2)
        vs = [[bm_.verts.new(Vector((math.cos(a0 + da * i / 4) * rr, math.sin(a0 + da * i / 4) * rr, h_ * j))) for j in (0, 1)] for i in range(5)]
        for i in range(4):
            bm_.faces.new((vs[i][0], vs[i + 1][0], vs[i + 1][1], vs[i][1]))
        rot = Matrix.Rotation(PR_.uniform(1.2, 1.7), 3, 'X') @ Matrix.Rotation(PR_.uniform(0, 6.28), 3, 'Z')
        for col in vs:
            for v in col:
                v.co = rot @ v.co + Vector((c.x, c.y, gh0(*PIT) + .06))
    me_ = bpy.data.meshes.new('PotShards'); bm_.to_mesh(me_); bm_.free(); me_.materials.append(_m_pot)
    sol = bpy.data.objects.new('PotShards', me_); sc.collection.objects.link(sol)
    sol.modifiers.new('Th', 'SOLIDIFY').thickness = .012
    print('PITTOOLS', [round(v, 1) for v in (_sp.x, _sp.y, _bp.x, _bp.y)])

    # 11/24 故事「荒廢很多年」：從前砍掉的老樹留下的樹樁——根部往外張、埋進土裡；切口風化下陷、一側留著撕裂的木舌；長苔
    _skm = _bkm.copy(); _skm.name = 'StumpBark'
    next(x_ for x_ in _skm.node_tree.nodes if x_.type == 'MAPPING').inputs['Scale'].default_value = (1.2, 1.2, 1.0)
    mossify(_skm, 1.1, 1.0, reach=.3)
    _ctm = bpy.data.materials.new('StumpCut'); _ctm.use_nodes = True   # 切口：灰褐舊木，年輪＋裂紋
    _cn = _ctm.node_tree; _cb = next(x_ for x_ in _cn.nodes if x_.type == 'BSDF_PRINCIPLED')
    _ctc = _cn.nodes.new('ShaderNodeTexCoord')
    _cwv = _cn.nodes.new('ShaderNodeTexWave'); _cwv.wave_type = 'RINGS'; _cwv.rings_direction = 'Z'
    _cwv.inputs['Scale'].default_value = 9; _cwv.inputs['Distortion'].default_value = 3; _cwv.inputs['Detail'].default_value = 4
    _cn.links.new(_ctc.outputs['Object'], _cwv.inputs['Vector'])
    _ccr = _cn.nodes.new('ShaderNodeValToRGB')
    _ccr.color_ramp.elements[0].color = (.018, .013, .009, 1); _ccr.color_ramp.elements[1].color = (.055, .04, .028, 1)   # 11/24 第二次調暗：還是像灰石板 → 改成深色爛木頭   # 11/24 調暗：原本淺色圓盤太乾淨、像新鋸的
    _cn.links.new(_cwv.outputs['Fac'], _ccr.inputs[0]); _cn.links.new(_ccr.outputs[0], _cb.inputs['Base Color'])
    _cbp = _cn.nodes.new('ShaderNodeBump'); _cbp.inputs['Strength'].default_value = .6
    _cn.links.new(_cwv.outputs['Fac'], _cbp.inputs['Height']); _cn.links.new(_cbp.outputs['Normal'], _cb.inputs['Normal'])
    _cb.inputs['Roughness'].default_value = .95
    try:
        _cb.inputs['Specular IOR Level'].default_value = .15   # 斜面反射天空會發白
    except KeyError:
        pass

    _STUMPS = []

    def stump(x, y, r, h, seed):
        rr_ = random.Random(seed); N = 36; off_ = Vector((seed * 2.3, .7, 0))
        lobes = rr_.randint(4, 6); ph = rr_.uniform(0, 6.28)
        tilt = Vector((rr_.uniform(-.06, .06), rr_.uniform(-.06, .06)))   # 鋸口不是水平的
        zs = [-.35, -.1, .05, .15, .3, .5, .75, 1.0]
        bm_ = bmesh.new(); rings = []
        for z01 in zs:
            z = z01 * h if z01 > 0 else z01
            flare = max(0.0, 1 - max(z, 0) / (h * .6)) ** 2   # 底部往外張的板根
            row = []
            for i in range(N):
                a = 6.2832 * i / N
                lobe = max(0.0, math.sin(a * lobes + ph)) ** 2
                rad = r * (1 + noise.noise(Vector((math.cos(a), math.sin(a), z)) * 2 + off_) * .12 + flare * (.35 + .9 * lobe))
                zz = z + (tilt.x * math.cos(a) + tilt.y * math.sin(a)) * r if z01 == 1.0 else z
                row.append(bm_.verts.new(Vector((math.cos(a) * rad, math.sin(a) * rad, zz))))
            rings.append(row)
        for k in range(len(rings) - 1):
            for i in range(N):
                bm_.faces.new((rings[k][i], rings[k][(i + 1) % N], rings[k + 1][(i + 1) % N], rings[k + 1][i]))
        # 切口：一圈圈往中間收、中心爛得下陷；一側留一片撕裂木舌（砍倒時沒鋸斷的地方）
        top = rings[-1]; prev = top; tongue = rr_.uniform(0, 6.28)
        for s_ in (.85, .6, .35):
            row = []
            for i, v in enumerate(top):
                a = 6.2832 * i / N
                c = Vector((v.co.x * s_, v.co.y * s_, v.co.z - (1 - s_) * .12 * r / .5 - rr_.uniform(0, .015)))
                row.append(bm_.verts.new(c))
            for i in range(N):
                f_ = bm_.faces.new((prev[i], prev[(i + 1) % N], row[(i + 1) % N], row[i])); f_.material_index = 1
            prev = row
        cen = bm_.verts.new(Vector((0, 0, sum(v.co.z for v in prev) / N - .03)))
        for i in range(N):
            f_ = bm_.faces.new((prev[i], prev[(i + 1) % N], cen)); f_.material_index = 1
        for i, v in enumerate(top):   # 木舌：切口外緣一段往上撕起、參差
            a = 6.2832 * i / N; da = math.atan2(math.sin(a - tongue), math.cos(a - tongue))
            if abs(da) < .7:
                v.co.z += (1 - abs(da) / .7) * r * .3 + rr_.uniform(0, .05)
        me_ = bpy.data.meshes.new('Stump'); bm_.to_mesh(me_); bm_.free()
        for p_ in me_.polygons:
            p_.use_smooth = True
        me_.materials.append(_skm); me_.materials.append(_ctm)
        ob_ = bpy.data.objects.new('Stump', me_); sc.collection.objects.link(ob_)
        ob_.location = (x, y, min(gh(x + dx, y + dy) for dx in (-r, 0, r) for dy in (-r, 0, r)) - .02)
        ob_.rotation_euler = (0, 0, rr_.uniform(0, 6.28))
        _PROPS.append((x, y, r * 1.5)); _STUMPS.append((x, y, r, h))
        print('STUMP', round(x, 1), round(y, 1))
    for _fd, _rd, _r, _h, _sd in ((5.5, 3.4, .55, .6, 11), (6.5, -3.4, .6, .5, 12)):   # V3 路兩旁：兩個老樹樁（11/24 移進鏡頭：原本一個在畫框外、一個被蕨蓋住）
        _p = _c3 + _f3 * _fd + _r3 * _rd
        stump(*_clear(_p.x, _p.y, 3.0), _r, _h, _sd)
    _p = _c5 + _f5 * 6.5 + _r5 * 4.2   # V5 路右邊一個
    stump(*_clear(_p.x, _p.y, 3.0), .5, .5, 13)

    # 11/24 接地：擺件底下一圈壓實的土、邊緣不規則，擺件看起來是陷在土裡，不是放在草上
    _bmm = bpy.data.materials.new('BaseSoil'); _bmm.use_nodes = True   # 壓實的深色濕土＋落葉碎屑色
    _bt = _bmm.node_tree; _bbs = next(x_ for x_ in _bt.nodes if x_.type == 'BSDF_PRINCIPLED')
    _btc2 = _bt.nodes.new('ShaderNodeTexCoord'); _bmp2 = _bt.nodes.new('ShaderNodeMapping'); _bmp2.inputs['Scale'].default_value = (1.5, 1.5, 1.5)
    _bt.links.new(_btc2.outputs['Object'], _bmp2.inputs['Vector'])
    _bti = _bt.nodes.new('ShaderNodeTexImage'); _bti.image = bpy.data.images.load(_GT + 'brown_mud_02_diff_2k.png')
    _bt.links.new(_bmp2.outputs['Vector'], _bti.inputs['Vector'])
    _bmx = _bt.nodes.new('ShaderNodeMixRGB'); _bmx.blend_type = 'MULTIPLY'; _bmx.inputs[0].default_value = 1; _bmx.inputs[2].default_value = (.75, .6, .45, 1)
    _bt.links.new(_bti.outputs['Color'], _bmx.inputs[1]); _bt.links.new(_bmx.outputs[0], _bbs.inputs['Base Color'])
    _bbs.inputs['Roughness'].default_value = .95

    def base_mound(x, y, r, seed):
        bm_ = bmesh.new(); bmesh.ops.create_circle(bm_, cap_ends=True, segments=28, radius=1)
        bmesh.ops.subdivide_edges(bm_, edges=bm_.edges[:], cuts=2, use_grid_fill=True)
        off_ = Vector((seed * 1.7, 3.3, 0))
        for v in bm_.verts:
            d = v.co.length; a = math.atan2(v.co.y, v.co.x)
            rr = (r + .35) * (1 + .25 * noise.noise(Vector((math.cos(a), math.sin(a), 0)) * 1.5 + off_))
            v.co = Vector((v.co.x * rr, v.co.y * rr, 0))
            v.co.z = gh(x + v.co.x, y + v.co.y) - gh(x, y) + .1 * max(0.0, 1 - d) ** .7 - .03
        me_ = bpy.data.meshes.new('BaseMound'); bm_.to_mesh(me_); bm_.free()
        for p_ in me_.polygons:
            p_.use_smooth = True
        me_.materials.append(_bmm)
        ob_ = bpy.data.objects.new('BaseMound', me_); sc.collection.objects.link(ob_)
        ob_.location = (x, y, gh(x, y))
    for _k, (_x, _y, _r) in enumerate(_PROPS):
        base_mound(_x, _y, _r, _k)
    globals()['_PROPS'] = _PROPS
    if 'pit2' in argv:
        _PROPS.append((PIT2[0], PIT2[1], 6.2 * PIT2_S * .75))   # 大蕨退開、坑外一圈矮草（土堆已經在坑模型裡）
    # 11/24 祭壇做舊：腳下一圈崩落的碎石塊（角掉下來的），半埋、成堆不均勻
    bpy.context.view_layer.update()
    _abb = [o_.matrix_world @ Vector(c) for o_ in _ALTOBJ if o_.type == 'MESH' for c in o_.bound_box]
    _ax0, _ax1 = min(v.x for v in _abb), max(v.x for v in _abb); _ay0, _ay1 = min(v.y for v in _abb), max(v.y for v in _abb)
    _RB = random.Random(23); _nrb = 0
    for _cl in range(6):   # 6 堆，每堆 3–7 塊
        side = _RB.randint(0, 3); t_ = _RB.random()
        cx_, cy_ = ((_ax0 + (_ax1 - _ax0) * t_, _ay0 - .2), (_ax0 + (_ax1 - _ax0) * t_, _ay1 + .2), (_ax0 - .2, _ay0 + (_ay1 - _ay0) * t_), (_ax1 + .2, _ay0 + (_ay1 - _ay0) * t_))[side]
        for _ in range(_RB.randint(3, 7)):
            x_, y_ = cx_ + _RB.gauss(0, .35), cy_ + _RB.gauss(0, .35)
            if path_d(x_, y_) < 1.8:
                continue
            sz = _RB.choice([_RB.uniform(.06, .12), _RB.uniform(.06, .12), _RB.uniform(.12, .22)])
            bm_ = bmesh.new(); bmesh.ops.create_icosphere(bm_, subdivisions=1, radius=1)
            for v in bm_.verts:   # 有稜角的碎塊，不是圓球
                v.co = Vector((v.co.x * _RB.uniform(.8, 1.3), v.co.y * _RB.uniform(.8, 1.3), v.co.z * _RB.uniform(.5, .9)))
            me_ = bpy.data.meshes.new('AltarRubble'); bm_.to_mesh(me_); bm_.free(); me_.materials.append(_lsm)
            ob_ = bpy.data.objects.new('AltarRubble', me_); sc.collection.objects.link(ob_)
            ob_.scale = (sz, sz, sz); ob_.location = (x_, y_, gh(x_, y_) + sz * .15)
            ob_.rotation_euler = (_RB.uniform(-.4, .4), _RB.uniform(-.4, .4), _RB.uniform(0, 6.28)); _nrb += 1
    print('ALTAR RUBBLE', _nrb)
    # 11/24 故事「從前是聖地」：祭壇正面通到主路的舊石板路——歪斜、半埋、有的斷成兩半、有的不見了，縫裡長草
    _af = Vector((math.sin(.35), -math.cos(.35)))   # 祭壇正面方向（轉了 0.35）
    _half = max(abs((v.xy - Vector(ALT)).dot(_af)) for v in _abb)
    _st = Vector(ALT) + _af * (_half + .25)
    _L = 0.0
    while path_d(*(_st + _af * _L)) > .8 and _L < 12:
        _L += .2
    # 11/24 第二版：祭壇前那段太短看不到 → 祭壇附近的主路、支路底下原本都是石板路，現在大多被土蓋掉、只剩一段段露出來
    _RUNS = [(tuple(_st), tuple(_st + _af * (_L + .5)), 1.0), ((4, -10), (4, -6), .55), ((4, -6), (9, 1), 1.0), ((9, 1), (14, 8), .7),
             ((3, -5), (-1, 3), .9), ((-1, 3), (-5, 9), .55)]
    _slm = (_stm or _lsm).copy(); _slm.name = 'PathSlabStone'   # 11/24 第三次：純灰色太新、像紙板 → 用祭壇石材紋理、去掉綠、壓暗，再長一點苔
    _snt = _slm.node_tree; _sbs = next(x_ for x_ in _snt.nodes if x_.type == 'BSDF_PRINCIPLED')
    if _sbs.inputs['Base Color'].links:
        _src_ = _sbs.inputs['Base Color'].links[0].from_socket
        _hsv = _snt.nodes.new('ShaderNodeHueSaturation'); _hsv.inputs['Saturation'].default_value = .35; _hsv.inputs['Value'].default_value = .7
        _snt.links.new(_src_, _hsv.inputs['Color']); _snt.links.new(_hsv.outputs['Color'], _sbs.inputs['Base Color'])
    mossify(_slm, .9, 1.0)
    _SR = random.Random(41); _nsl = 0; _SLABS = []
    for (ax_, ay_), (bx_, by_), keep in _RUNS:
        A_, B_ = Vector((ax_, ay_)), Vector((bx_, by_)); dv = (B_ - A_); Lr = dv.length; dv = dv.normalized(); sv = Vector((-dv.y, dv.x))
        _d = 0.0
        while _d < Lr:
            dep = _SR.uniform(.45, .65)
            patch = .5 + .5 * noise.noise(Vector(((A_ + dv * _d).x * .35, (A_ + dv * _d).y * .35, 2.2)))   # 一段段露出、一段段被土蓋
            for col in (-.62, 0, .62):
                if _SR.random() > keep * (.25 + .9 * patch):
                    continue
                w_ = _SR.uniform(.5, .62); c = A_ + dv * (_d + dep / 2) + sv * (col + _SR.uniform(-.05, .05))
                pieces = [(0, 1)] if _SR.random() > .25 else [(0, .55), (.6, 1)]   # 有的斷成兩半
                for a0, a1 in pieces:
                    bm_ = bmesh.new(); bmesh.ops.create_cube(bm_, size=1)
                    for v in bm_.verts:
                        v.co = Vector((v.co.x * w_ * _SR.uniform(.92, 1.0), (a0 + (v.co.y + .5) * (a1 - a0) - .5) * dep * _SR.uniform(.92, 1.0), v.co.z * .14))
                    for _cc in range(_SR.choice((0, 0, 1, 1, 2))):   # 缺角：切掉一兩個角，不要整齊方磚
                        sx_, sy_ = _SR.choice((-1, 1)), _SR.choice((-1, 1)); cut = _SR.uniform(.08, .18)
                        co_ = Vector((sx_ * (w_ / 2 - cut), sy_ * ((a1 - a0) * dep / 2 - cut) + ((a0 + a1) / 2 - .5) * dep, 0))
                        no_ = Vector((sx_, sy_ * _SR.uniform(.6, 1.6), _SR.uniform(-.3, .3))).normalized()
                        bmesh.ops.bisect_plane(bm_, geom=bm_.verts[:] + bm_.edges[:] + bm_.faces[:], plane_co=co_, plane_no=no_, clear_outer=True)
                        bmesh.ops.holes_fill(bm_, edges=[e for e in bm_.edges if e.is_boundary])
                    bmesh.ops.bevel(bm_, geom=bm_.edges[:], offset=.02, segments=2, affect='EDGES')
                    for v in bm_.verts:   # 磨圓、表面不平
                        v.co.z += noise.noise(v.co * 6 + Vector((_nsl, 0, 0))) * .015
                    me_ = bpy.data.meshes.new('ShrineSlab'); bm_.to_mesh(me_); bm_.free(); me_.materials.append(_slm)
                    ob_ = bpy.data.objects.new('ShrineSlab', me_); sc.collection.objects.link(ob_)
                    ob_.location = (c.x, c.y, gh(c.x, c.y) - .012 - _SR.uniform(0, .02))   # 11/24 抬高：原本被路面的泥蓋掉 → 石面露出 4–7 cm
                    ob_.rotation_euler = (_SR.uniform(-.05, .05), _SR.uniform(-.05, .05), math.atan2(dv.y, dv.x) - math.pi / 2 + _SR.uniform(-.1, .1) + (_SR.uniform(-.15, .15) if len(pieces) > 1 else 0))
                    _nsl += 1; _SLABS.append((c.x, c.y))
            _d += dep + _SR.uniform(.06, .14)
    globals()['_SLABS'] = _SLABS
    print('SLABS', _nsl)

    # 11/24 V5 右前方：設定圖兩根長滿苔的大倒木 → 放 Josh 的 DR08 朽木 v002（#127），我們自己做的倒木不用了
    def place_glb_log(path, x, y, ang, sink, scale=1.0):
        objs = glb(path, (0, 0), -gh(0, 0))
        bpy.context.view_layer.update()
        pts = [o_.matrix_world @ Vector(c) for o_ in objs for c in o_.bound_box]
        dx_ = max(p_.x for p_ in pts) - min(p_.x for p_ in pts); dy_ = max(p_.y for p_ in pts) - min(p_.y for p_ in pts)
        a0 = 0.0 if dx_ >= dy_ else math.pi / 2; L_ = max(dx_, dy_) * scale
        M_ = Matrix.Translation((x, y, gh(x, y) - sink)) @ Matrix.Rotation(ang - a0, 4, 'Z') @ Matrix.Scale(scale, 4)
        for o_ in objs:
            o_.matrix_world = M_ @ o_.matrix_world
            if 'Plants' in o_.name:
                continue
            if 'scanbark' in argv:   # 11/25 試過：換掃描樹皮貼圖 → 從 V5 看像一塊淺色石頭，不用（scanbark 才開）。 換成神木同一套掃描樹皮（盒投影、溝紋深）＋頂上一塊塊苔；dr08mat = 11/24 的壓暗版
                # v3：盒投影的紋路方向轉不過來 → 改用 Josh 自己的 UV（紋路本來就順著倒木），只把貼圖換成神木的掃描樹皮
                for sl_ in o_.material_slots:
                    m_ = sl_.material
                    if not m_ or 'Plants' in m_.name or not m_.use_nodes or m_.get('scanbark'):
                        continue
                    m_['scanbark'] = 1
                    _nt = m_.node_tree
                    _uvn = _nt.nodes.new('ShaderNodeUVMap'); _mpn = _nt.nodes.new('ShaderNodeMapping'); _mpn.inputs['Scale'].default_value = (2.0, 2.0, 1.0)
                    _nt.links.new(_uvn.outputs['UV'], _mpn.inputs['Vector'])
                    for t_ in [n_ for n_ in _nt.nodes if n_.type == 'TEX_IMAGE']:
                        nor_ = 'Normal' in t_.image.name
                        t_.image = bpy.data.images.load(_BK + ('bark_brown_02_nor_gl_2k.png' if nor_ else 'bark_brown_02_diff_2k.png'), check_existing=True)
                        t_.image.colorspace_settings.name = 'Non-Color' if nor_ else 'sRGB'
                        _nt.links.new(_mpn.outputs['Vector'], t_.inputs['Vector'])
                    for n_ in _nt.nodes:
                        if n_.type == 'NORMAL_MAP':
                            n_.inputs['Strength'].default_value = 1.5
                    mossify(m_, .6, 1.0, reach=.12)
                continue
            for sl_ in o_.material_slots:   # 我們自己修：場景裡太亮太橘（像紅磚）→ 壓暗、降飽和，再長苔（從頂上往側面爬）
                m_ = sl_.material
                if not m_ or m_.get('dr08fix') or not m_.use_nodes:
                    continue
                m_['dr08fix'] = 1
                b_ = next((x_ for x_ in m_.node_tree.nodes if x_.type == 'BSDF_PRINCIPLED'), None)
                if b_ and b_.inputs['Base Color'].links:
                    src_ = b_.inputs['Base Color'].links[0].from_socket
                    hs_ = m_.node_tree.nodes.new('ShaderNodeHueSaturation'); hs_.inputs['Saturation'].default_value = (.5 if 'dr08mat' in argv else .42); hs_.inputs['Value'].default_value = (.5 if 'dr08mat' in argv else .78)   # 11/25 v4：保留 Josh 的樹皮貼圖，提亮成設定圖的灰棕（dr08mat = 11/24 的深色）
                    for n_ in m_.node_tree.nodes:
                        if n_.type == 'NORMAL_MAP' and 'dr08mat' not in argv:
                            n_.inputs['Strength'].default_value = 2.2   # 樹皮溝紋加深
                    m_.node_tree.links.new(src_, hs_.inputs['Color']); m_.node_tree.links.new(hs_.outputs[0], b_.inputs['Base Color'])
                mossify(m_, (.9 if 'dr08mat' in argv else (.6 if 'baredr08' in argv else 1.05)), 1.0, reach=.14)   # 11/25 .6 太禿、.78 看不出差 → 1.05；苔只在頂上，側面露出樹皮（1.4／0.4 蓋滿整根像苔丘）
        d_ = Vector((math.cos(ang), math.sin(ang)))
        globals().setdefault('_LOGS', []).append((Vector((x, y)) - d_ * L_ / 2, ang, L_, min(dx_, dy_) * scale / 2))   # 倒木上不長蕨
        print('DR08', path.split('/')[-1], round(x, 1), round(y, 1), 'len', round(L_, 1))
    _DR = 'D:/chengtian/4-素材與快取/josh-dr08/'
    _dlm = _bkm.copy(); _dlm.name = 'DR08_ScanBark'
    next(x_ for x_ in _dlm.node_tree.nodes if x_.type == 'MAPPING').inputs['Scale'].default_value = (1.3, 1.3, 1.3)   # 倒木比神木細 → 樹皮紋路縮小
    mossify(_dlm, .6, 1.0, reach=.12)   # .9 頂上整片綠 → 減
    if 'nodr08' not in argv and 'longlog' not in argv:   # 11/25 z1nnz 覺得 Josh 的 DR08 形狀不錯、只是材質差一點 → 留 DR08、換材質；longlog = 我們的程式長倒木
        _la =math.atan2((_f5 * .55 - _r5).y, (_f5 * .55 - _r5).x)   # 從右前往左後斜躺（設定圖從右下角斜進畫面）
        _old = 'oldpos' in argv   # 11/25 z1nnz「這個擺的位置不要擺在這」：原本貼著路、蓋住半個畫面 → 往右邊畫面邊緣挪，和路之間留一排蕨（設定圖）；oldpos = 原位置
        if 'v5logs' in argv:   # 11/25 試了三個位置：放大或轉向後從 V5 看都像一塊大石頭 → 預設搬出 V5（v5logs = 留在 V5 右邊畫面邊緣）
            _p = _c5 + _f5 * 4.2 + _r5 * 5.8; place_glb_log(_DR + 'DR08_RottenLog_C_v002.glb', *_clear(_p.x, _p.y, 4.2), _la, .14, 1.2)
            _p = _c5 + _f5 * 8.5 + _r5 * 7.0; place_glb_log(_DR + 'DR08_RottenLog_B_v002.glb', *_clear(_p.x, _p.y, 4.5), _la + .25, .12, 1.1)
        elif _old:
            _p = _c5 + _f5 * 3.4 + _r5 * 3.6; place_glb_log(_DR + 'DR08_RottenLog_C_v002.glb', *_clear(_p.x, _p.y, 2.9), _la, .14, 1.2)
            _p = _c5 + _f5 * 7.0 + _r5 * 4.8; place_glb_log(_DR + 'DR08_RottenLog_B_v002.glb', *_clear(_p.x, _p.y, 3.2), _la + .25, .12, 1.1)
        else:   # 搬到 V5 鏡頭左後方的林子裡（六張圖都不入鏡，玩家走過去看得到）
            _p = _c5 - _f5 * 3.0 - _r5 * 12.0; place_glb_log(_DR + 'DR08_RottenLog_C_v002.glb', *_clear(_p.x, _p.y, 4.5), _la + 1.1, .14, 1.2)
            _p = _c5 - _f5 * 7.0 - _r5 * 9.0; place_glb_log(_DR + 'DR08_RottenLog_B_v002.glb', *_clear(_p.x, _p.y, 4.5), _la + .6, .12, 1.1)

    # 11/24 地面細節：落葉堆（堆在樹樁、石頭、根邊的角落，風吹過去積起來的）、松果、小蕈叢（樹樁上、落葉堆邊）
    _lfm = [_mat('LeafBrown', (.16, .08, .03), .85, 30, (.09, .045, .02)), _mat('LeafOrange', (.30, .13, .04), .85, 30, (.18, .07, .02)), _mat('LeafDark', (.06, .04, .02), .9, 30, (.035, .025, .015))]
    _pcm = _mat('PineCone', (.11, .06, .03), .8, 60, (.05, .03, .015))
    _mcap = _mat('MushCap', (.30, .17, .08), .6, 15, (.18, .09, .04)); _mstem = _mat('MushStem', (.55, .50, .40), .7)
    _LR = random.Random(91)

    def leaf_pile(x, y, w, hgt, seed):   # 一團低矮的土丘＋上面密密的落葉片（單一網格）
        rr_ = random.Random(seed); bm_ = bmesh.new(); ax_ = rr_.uniform(0, 6.28)
        for _ in range(int(380 * w)):
            a = rr_.uniform(0, 6.283); d = math.sqrt(rr_.random()); lx, ly = math.cos(a) * d * w, math.sin(a) * d * w * .7
            px, py = x + lx * math.cos(ax_) - ly * math.sin(ax_), y + lx * math.sin(ax_) + ly * math.cos(ax_)
            z = gh(px, py) + hgt * (1 - d * d) + rr_.uniform(0, .02)
            sz = rr_.uniform(.035, .07); rot = Matrix.Rotation(rr_.uniform(0, 6.28), 3, 'Z') @ Matrix.Rotation(rr_.uniform(-.6, .6), 3, 'X')
            cv = [rot @ Vector(q) * sz for q in ((-1, -.5, 0), (1, -.5, 0), (1.1, .5, .15), (-1.1, .5, .15))]   # 微捲的葉片
            f_ = bm_.faces.new([bm_.verts.new(Vector((px, py, z)) + c) for c in cv]); f_.material_index = rr_.choices((0, 1, 2), (.5, .25, .25))[0]
        me_ = bpy.data.meshes.new('LeafPile'); bm_.to_mesh(me_); bm_.free()
        for m_ in _lfm:
            me_.materials.append(m_)
        ob_ = bpy.data.objects.new('LeafPile', me_); sc.collection.objects.link(ob_)
        ob_.modifiers.new('Th', 'SOLIDIFY').thickness = .003

    _cone_bm = bmesh.new()   # 松果樣板：一層層鱗片（每圈 8 片小三角）
    for k in range(7):
        t = k / 6; rad = .035 * math.sin(math.pi * (.15 + .8 * t)); z = .1 * t
        for i in range(8):
            a = 6.283 * (i + .5 * k) / 8
            p0 = Vector((math.cos(a) * rad * .4, math.sin(a) * rad * .4, z)); tip = Vector((math.cos(a) * rad, math.sin(a) * rad, z - .012))
            side = Vector((-math.sin(a), math.cos(a), 0)) * rad * .45
            _cone_bm.faces.new((_cone_bm.verts.new(p0 - side), _cone_bm.verts.new(tip), _cone_bm.verts.new(p0 + side), _cone_bm.verts.new(p0 + Vector((0, 0, .015)))))
    _cme = bpy.data.meshes.new('PineCone'); _cone_bm.to_mesh(_cme); _cone_bm.free(); _cme.materials.append(_pcm)

    def pine_cones(x, y, n, spread):
        for _ in range(n):
            px, py = x + _LR.gauss(0, spread), y + _LR.gauss(0, spread)
            if path_d(px, py) < 1.6:
                continue
            ob_ = bpy.data.objects.new('PineCone', _cme); sc.collection.objects.link(ob_)
            s_ = _LR.uniform(.8, 1.3); ob_.scale = (s_, s_, s_)
            ob_.location = (px, py, gh(px, py) + .025); ob_.rotation_euler = (math.pi / 2 + _LR.uniform(-.3, .3), 0, _LR.uniform(0, 6.28))   # 側躺

    def mush_cluster(x, y, z0, n, size, seed):   # 一叢大小不一的小蕈
        rr_ = random.Random(seed); bm_ = bmesh.new()
        for k in range(n):
            px, py = x + rr_.gauss(0, size * 2), y + rr_.gauss(0, size * 2); s_ = size * rr_.uniform(.5, 1.3)
            zb = (z0 if z0 is not None else gh(px, py)) - .01; h_ = s_ * rr_.uniform(1.2, 2.2); tl = Vector((rr_.uniform(-.15, .15), rr_.uniform(-.15, .15), 1)).normalized()
            g = bmesh.ops.create_cone(bm_, cap_ends=False, segments=8, radius1=s_ * .18, radius2=s_ * .14, depth=h_)
            for v in g['verts']:
                v.co = Vector((px, py, zb)) + Vector((v.co.x, v.co.y, 0)) + tl * (v.co.z + h_ / 2)
            for f_ in bm_.faces:
                if f_.material_index == 0 and not f_.tag:
                    f_.material_index = 1; f_.tag = True
            g = bmesh.ops.create_uvsphere(bm_, u_segments=12, v_segments=6, radius=s_ * rr_.uniform(.45, .65))
            top = Vector((px, py, zb)) + tl * h_
            for v in g['verts']:
                v.co = top + Vector((v.co.x, v.co.y, max(v.co.z, -s_ * .05) * .55))
            for f_ in bm_.faces:
                if not f_.tag:
                    f_.material_index = 0; f_.tag = True
        me_ = bpy.data.meshes.new('MushCluster'); bm_.to_mesh(me_); bm_.free(); me_.materials.append(_mcap); me_.materials.append(_mstem)
        for p_ in me_.polygons:
            p_.use_smooth = True
        ob_ = bpy.data.objects.new('MushCluster', me_); sc.collection.objects.link(ob_)

    _np = 0
    for _x, _y, _r, _h in _STUMPS:   # 樹樁：根邊一側積落葉、切口上長一叢小蕈、旁邊幾顆松果
        a = _LR.uniform(0, 6.28); leaf_pile(_x + math.cos(a) * (_r + .35), _y + math.sin(a) * (_r + .35), .7, .12, _np); _np += 1
        mush_cluster(_x + _LR.uniform(-.1, .1), _y + _LR.uniform(-.1, .1), gh(_x, _y) + _h * .95 - .05, _LR.randint(4, 7), .045, _np)
        mush_cluster(_x + math.cos(a + 2) * (_r + .15), _y + math.sin(a + 2) * (_r + .15), None, _LR.randint(3, 6), .04, _np + 50)
        pine_cones(_x, _y, _LR.randint(3, 6), .9)
    for _cx, _fx, _rx in ((_c3, 6.0, 4.6), (_c3, 12.0, -4.4), (_c3, 15.0, 5.0), (_c5, 4.0, -3.2), (_c5, 9.0, 3.6), (_c5, 13.0, -4.0)):   # V3、V5 路邊：落葉堆＋小蕈＋松果，成堆不平均
        _bx_ = _c3 if _cx is _c3 else _c5; _ff = _f3 if _cx is _c3 else _f5; _rr = _r3 if _cx is _c3 else _r5
        _p = _bx_ + _ff * _fx + _rr * _rx; _q = _clear(_p.x, _p.y, 2.6)
        leaf_pile(*_q, _LR.uniform(.6, 1.1), _LR.uniform(.08, .16), _np); _np += 1
        if _LR.random() < .6:
            mush_cluster(_q[0] + _LR.uniform(-.6, .6), _q[1] + _LR.uniform(-.6, .6), None, _LR.randint(3, 8), .04, _np + 80)
        pine_cones(*_q, _LR.randint(2, 7), 1.2)
        _PROPS.append((_q[0], _q[1], .6))   # 大蕨退開、周圍長矮草
    print('LITTER piles', _np)

    # 11/24 故事「從前是聖地」：神木腰上綁的舊祈福繩＋垂下來的褪色布條（z1nnz 同意動神木，只加繩子、不改樹）
    if 'norope' not in argv:
        _wood = [o_ for o_ in _GTO if o_.type == 'MESH' and 'Wood' in o_.name]
        def _surf_r(a, z):   # 這個角度、高度上，樹幹最外側離中心多遠
            d = Vector((math.cos(a), math.sin(a), 0)); best = 99.0   # 11/24 修：從中心往外打、取最近的面（從外往內會先打到外圍的根和枝 → 半徑 12–25 m）
            for o_ in _wood:
                mi = o_.matrix_world.inverted()
                ok_, loc_, _n, _i = o_.ray_cast(mi @ Vector((TREE[0], TREE[1], z)), (mi.to_3x3() @ d).normalized())
                if ok_:
                    best = min(best, ((o_.matrix_world @ loc_).xy - Vector(TREE)).length)
            return best if best < 99 else 3.0
        NR = 128   # 3.4 m、8 m 都還在板根區（繩子變成圍欄浮在外面）→ 往上找樹幹截面夠圓（最大/最小 < 1.45）的最低高度
        for _h in [8 + .75 * k for k in range(20)]:
            _rz = gh(*TREE) + _h
            _rad = [_surf_r(6.2832 * i / NR, _rz) for i in range(NR)]
            if max(_rad) / max(min(_rad), .1) < 1.45:
                break
        print('ROPE height', _h)
        _rad = [max(_rad[(i + k) % NR] for k in range(-2, 3)) + .08 for i in range(NR)]   # 只跨過細溝，貼著樹幹
        _rpm = _mat('OldRope', (.30, .25, .15), .9, 40, (.17, .14, .09))
        mossify(_rpm, .5, 1.0)
        def _rope(zoff, thick, sag_ph):
            cu_ = bpy.data.curves.new('ShrineRope', 'CURVE'); cu_.dimensions = '3D'; cu_.bevel_depth = thick; cu_.bevel_resolution = 3
            sp_ = cu_.splines.new('NURBS'); sp_.points.add(NR - 1); sp_.use_cyclic_u = True; sp_.order_u = 3
            for i in range(NR):
                a = 6.2832 * i / NR; rr = _rad[i] + thick
                z = _rz + zoff + .3 * math.sin(a * 3 + sag_ph) + .1 * math.sin(a * 7)   # 綁得不平、有鬆有緊
                sp_.points[i].co = (TREE[0] + math.cos(a) * rr, TREE[1] + math.sin(a) * rr, z, 1)
            cu_.materials.append(_rpm)
            ob_ = bpy.data.objects.new('ShrineRope', cu_); sc.collection.objects.link(ob_)
        _rope(0, .16, 0); _rope(-.45, .1, 1.3)   # 神木很大（樹幹半徑約 9 m）→ 繩子要粗   # 一粗一細兩道
        _cl = [_mat('ClothRed', (.30, .05, .035), .9, 20, (.16, .04, .03)), _mat('ClothWhite', (.42, .40, .34), .9, 20, (.25, .23, .18)), _mat('ClothYellow', (.40, .30, .12), .9, 20, (.22, .17, .08))]
        _CR = random.Random(77); _nst = 0
        bm_ = bmesh.new(); _mi_of = []
        for i in range(NR):
            if _CR.random() > .45:
                continue
            a = 6.2832 * i / NR + _CR.uniform(-.02, .02)
            d = Vector((math.cos(a), math.sin(a), 0)); t_ = Vector((-d.y, d.x, 0))
            L_ = _CR.uniform(1.2, 2.8); W_ = _CR.uniform(.2, .35); z0 = _rz + .3 * math.sin(a * 3) + .1 * math.sin(a * 7) - .1
            low = max(_surf_r(a, z0 - L_ * .5), _surf_r(a, z0 - L_)) + .1
            rows = []
            for j in range(9):
                f = j / 8; z = z0 - L_ * f
                rr = max(_rad[i] + .1, low) + .05 * math.sin(f * 3 + i)   # 垂下時離開樹皮
                w = W_ * (1 - .25 * f) * (1 if j < 8 else _CR.uniform(.3, 1))   # 尾端破掉
                c = Vector((TREE[0], TREE[1], 0)) + d * rr + Vector((0, 0, z)) + t_ * (.03 * math.sin(f * 4 + i))
                rows.append((bm_.verts.new(c - t_ * w / 2), bm_.verts.new(c + t_ * w / 2 + Vector((0, 0, _CR.uniform(-.04, 0) if j == 8 else 0)))))
            k_ = _CR.choices((0, 1, 2), (.5, .3, .2))[0]
            for j in range(8):
                f_ = bm_.faces.new((rows[j][0], rows[j][1], rows[j + 1][1], rows[j + 1][0])); f_.material_index = k_
            _nst += 1
        me_ = bpy.data.meshes.new('ClothStrips'); bm_.to_mesh(me_); bm_.free()
        for m_ in _cl:
            me_.materials.append(m_)
        for p_ in me_.polygons:
            p_.use_smooth = True
        ob_ = bpy.data.objects.new('ClothStrips', me_); sc.collection.objects.link(ob_)
        ob_.modifiers.new('Th', 'SOLIDIFY').thickness = .004
        print('ROPE r', round(min(_rad), 1), round(max(_rad), 1), 'strips', _nst)

    # 11/23 故事「荒廢很多年」：倒下的老樹（獨立模型）——整根橫躺、半埋、長苔，一頭根盤翹起帶著土
    _flm = _bkm.copy(); _flm.name = 'FallenLogBark'
    _ft = _flm.node_tree
    _fuv = _ft.nodes.new('ShaderNodeUVMap'); _fuv.uv_map = 'UVMap'
    _fmp = next(x_ for x_ in _ft.nodes if x_.type == 'MAPPING'); _fmp.inputs['Scale'].default_value = (1, 1, 1)
    _ft.links.new(_fuv.outputs['UV'], _fmp.inputs['Vector'])
    for _ti in _ft.nodes:
        if _ti.type == 'TEX_IMAGE':
            _ti.projection = 'FLAT'
    mossify(_flm, 1.3, 1.0, reach=.15)
    _fdirt = bpy.data.materials.new('RootPlateSoil'); _fdirt.use_nodes = True   # 根盤帶起來的土：亮一點的濕棕土（原本誤用樹皮材質 → 一團黑）
    _sn = _fdirt.node_tree; _sb = next(x_ for x_ in _sn.nodes if x_.type == 'BSDF_PRINCIPLED')
    _stc = _sn.nodes.new('ShaderNodeTexCoord'); _smp = _sn.nodes.new('ShaderNodeMapping'); _smp.inputs['Scale'].default_value = (2.5, 2.5, 2.5)
    _sn.links.new(_stc.outputs['Object'], _smp.inputs['Vector'])
    _sti = _sn.nodes.new('ShaderNodeTexImage'); _sti.image = bpy.data.images.load(_GT + 'brown_mud_02_diff_2k.png'); _sti.projection = 'BOX'
    _sn.links.new(_smp.outputs['Vector'], _sti.inputs['Vector'])
    _smx = _sn.nodes.new('ShaderNodeMixRGB'); _smx.blend_type = 'MULTIPLY'; _smx.inputs[0].default_value = 1; _smx.inputs[2].default_value = (1.25, .9, .6, 1)
    _sn.links.new(_sti.outputs['Color'], _smx.inputs[1]); _sn.links.new(_smx.outputs[0], _sb.inputs['Base Color'])
    _sb.inputs['Roughness'].default_value = .9

    def fallen_log(x, y, ang, L, R0, seed):
        rr_ = random.Random(seed)
        d_ = Vector((math.cos(ang), math.sin(ang), 0)); s_ = Vector((-d_.y, d_.x, 0))
        bm_ = bmesh.new(); uvl_ = bm_.loops.layers.uv.new('UVMap')
        NS, NR = 60, 20
        rings = []
        for i in range(NS + 1):
            t = i / NS
            c = Vector((x, y, 0)) + d_ * (L * t) + s_ * (.5 * math.sin(t * 2.6 + seed))
            r = R0 * (1 - .45 * t) * (1 + .7 * max(0, .1 - t) / .1)   # 根端粗、樹梢細
            c.z = gh(c.x, c.y) + r * .55   # 半埋：下面四成多在土裡
            rg = []
            for j in range(NR):
                a = 2 * math.pi * j / NR
                bump = 1 + .07 * noise.noise(Vector((t * 9, j * .7, seed))) + .05 * noise.noise(Vector((t * 30, j * 2.1, seed)))
                rg.append(bm_.verts.new(c + (s_ * math.cos(a) + Vector((0, 0, 1)) * math.sin(a)) * r * bump))
            rings.append(rg)
        for i in range(NS):
            for j in range(NR):
                f = bm_.faces.new((rings[i][j], rings[i][(j + 1) % NR], rings[i + 1][(j + 1) % NR], rings[i + 1][j]))
                for lp, (ii, jj) in zip(f.loops, ((i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j))):
                    lp[uvl_].uv = (jj / NR * 2 * math.pi * R0 / 1.4, ii / NS * L / 2.2)
        for _cf in (bm_.faces.new(rings[-1][::-1]), bm_.faces.new(rings[0])):   # 斷口、根端封起來；截面 UV 用平面投影（不然拉成直條紋）
            for lp in _cf.loops:
                lp[uvl_].uv = (lp.vert.co.dot(s_) * .3, lp.vert.co.z * .3)
        me_ = bpy.data.meshes.new('FallenLog'); bm_.to_mesh(me_); bm_.free()
        for p_ in me_.polygons:
            p_.use_smooth = True
        me_.materials.append(_flm)
        ob_ = bpy.data.objects.new('FallenLog', me_); sc.collection.objects.link(ob_)
        # 根盤：倒下時從土裡翻起來的一面，直立的圓盤 + 一圈斷根 + 根上帶的土
        base = Vector((x, y, gh(x, y))) - d_ * .3
        bm2 = bmesh.new()
        for k in range(22):   # 11/23：斷根粗細差很多、長短不一、彎曲，尖端收細（原本一樣粗的圓頭棍 → 像一叢尖刺）
            a = 2 * math.pi * k / 22 + rr_.uniform(-.2, .2)
            dirr = (s_ * math.cos(a) + Vector((0, 0, 1)) * math.sin(a)).normalized()
            thick = rr_.choice((.34, .26, .2, .14, .1, .08))
            Lr = R0 * rr_.uniform(.9, 2.8) * (1.2 if thick > .2 else 1)
            bend = Vector((rr_.uniform(-1, 1), rr_.uniform(-1, 1), rr_.uniform(-1, .3))) * .35
            prev = None
            for u in range(9):
                tt = u / 8
                c = base + Vector((0, 0, R0 * .9)) + dirr * (Lr * tt) - d_ * (.4 * tt * tt) + bend * (Lr * tt * tt)
                rad = R0 * thick * (1 - .92 * tt ** .8) + .015
                ring = [bm2.verts.new(c + (d_ * math.cos(b) + dirr.cross(d_).normalized() * math.sin(b)) * rad) for b in [2 * math.pi * q / 8 for q in range(8)]]
                if prev:
                    for q in range(8):
                        bm2.faces.new((prev[q], prev[(q + 1) % 8], ring[(q + 1) % 8], ring[q]))
                prev = ring
        me2 = bpy.data.meshes.new('RootPlate'); bm2.to_mesh(me2); bm2.free()
        for p_ in me2.polygons:
            p_.use_smooth = True
        me2.materials.append(_bkm)   # 斷根沒有 UV → 用神木的盒投影樹皮（不然會拉成條紋）
        # 11/23 z1nnz「看不出來是什麼」：程式拼的根盤從正面看是一團 → 不放，等 Tripo 做根盤
        bm3 = bmesh.new(); bmesh.ops.create_icosphere(bm3, subdivisions=4, radius=1)
        for v in bm3.verts:
            c = v.co.copy(); lump = noise.noise(c * 2.2 + Vector((seed, 0, 0))) * .3
            v.co = Vector((c.x * .35 * (1 + lump), c.y * (1 + lump), c.z * (1 + lump)))
        me3 = bpy.data.meshes.new('RootDirt'); bm3.to_mesh(me3); bm3.free()
        for p_ in me3.polygons:
            p_.use_smooth = True
        me3.materials.append(_fdirt)
        od = bpy.data.objects.new('RootDirt', me3)   # 11/23：一整片土盤從正面看像一塊紙板 → 不放
        od.scale = (R0 * 1.05,) * 3; od.rotation_euler.z = ang
        od.location = base + Vector((0, 0, R0 * .9)) - d_ * .15
        # 翻起後留下的淺坑
        print('FALLENLOG', round(x, 1), round(y, 1))

    # 自動找位置：在 V3、V5 畫面裡、林中（離路 > 4.5 m、離祭壇 > 10、離坑 > 9、離神木 > 18），樹幹大致橫在畫面上
    for (cx_, cy_), (tx_, ty_), seed_, L_, R_ in (((4, -15), (6, 18), 41, 12, .9), ((-6, 12), (17, -21), 42, 10, .8)):
        f_ = Vector((tx_ - cx_, ty_ - cy_)).normalized(); r_ = Vector((f_.y, -f_.x))
        best_ = None
        for fd_ in range(8, 30):
            for rd_ in ((6, 8, 10, 12, 14, 16) if seed_ == 41 else (-16, -14, -12, -10, -8, -6, 6, 8, 10, 12, 14, 16)):   # V3 那棵放畫面右邊（左邊被神木和蕨擋住）
                p_ = Vector((cx_, cy_)) + f_ * fd_ + r_ * rd_
                a_ = math.atan2(r_.y, r_.x) + (.12 if rd_ > 0 else -.12)   # 倒木幾乎橫在畫面上，看得到整根側面（斜對鏡頭只看得到截面）
                e_ = p_ + Vector((math.cos(a_), math.sin(a_))) * L_
                ok_ = all(path_d(*(p_ + (e_ - p_) * u_)) > 3.2 for u_ in (0, .25, .5, .75, 1))
                ok_ = ok_ and min(math.hypot(q_.x - ALT[0], q_.y - ALT[1]) for q_ in (p_, e_)) > 8
                ok_ = ok_ and min(math.hypot(q_.x - PIT[0], q_.y - PIT[1]) for q_ in (p_, e_)) > 7.5
                ok_ = ok_ and min(math.hypot(q_.x - TREE[0], q_.y - TREE[1]) for q_ in (p_, e_)) > 18
                if ok_ and (best_ is None or fd_ < best_[0]):
                    best_ = (fd_, p_, a_)
        if False and best_ and 'logs' in argv:   # 11/25 舊的程式倒木停用（被下面 long_log 取代）；11/23：程式拼的倒木從 V5 看是一團／一塊圓盤，看不出是樹 → 先不放（argv 加 logs 才放），等 Tripo
            fallen_log(best_[1].x, best_[1].y, best_[2], L_, R_, seed_)
            globals().setdefault('_LOGS', []).append((best_[1], best_[2], L_, R_))

    # 11/25 V5 右前方兩根長倒木（設定圖：圓、長、斜躺，頂上厚苔、側面露樹皮，兩頭伸出畫面或是斷口）
    _llm = _bkm.copy(); _llm.name = 'LongLogBark'   # 11/25 v2：苔只長成頂上一塊塊，側面露出樹皮（v1 頂上整片平平的綠 → 像長滿草的花台）
    _lt = _llm.node_tree; _luv = _lt.nodes.new('ShaderNodeUVMap'); _luv.uv_map = 'UVMap'
    _lmp = next(x_ for x_ in _lt.nodes if x_.type == 'MAPPING'); _lmp.inputs['Scale'].default_value = (1, 1, 1)
    _lt.links.new(_luv.outputs['UV'], _lmp.inputs['Vector'])
    for _ti in _lt.nodes:
        if _ti.type == 'TEX_IMAGE':
            _ti.projection = 'FLAT'
    mossify(_llm, .45, 1.0, reach=0.0)   # v3：.8 還是整片綠 → 再減

    def long_log(p0, p1, R0, seed, sink=.25, stubs=2):
        rr_ = random.Random(seed)
        d3 = Vector((p1.x - p0.x, p1.y - p0.y, 0)); L = d3.length; d_ = d3.normalized(); s_ = Vector((-d_.y, d_.x, 0))
        bm_ = bmesh.new(); uvl_ = bm_.loops.layers.uv.new('UVMap')
        NS, NR = max(40, int(L * 7)), 28
        rings = []; cen = []
        bend = rr_.uniform(-.25, .25)
        for i in range(NS + 1):
            t = i / NS
            c = Vector((p0.x, p0.y, 0)) + d_ * (L * t) + s_ * (bend * math.sin(t * math.pi))
            r = R0 * (1 - .25 * t)
            c.z = max(gh(c.x, c.y), gh(c.x + s_.x * r, c.y + s_.y * r), gh(c.x - s_.x * r, c.y - s_.y * r)) + r * (1 - 2 * sink)   # 直徑的 sink 比例埋在土裡
            cen.append((c, r))
            rg = []
            for j in range(NR):
                a = 2 * math.pi * j / NR
                # 樹皮縱向溝紋 + 低頻起伏；斷口那頭最後 6% 參差不齊
                ridge = .07 * abs(math.sin(j * 2.3 + t * L * .35 + noise.noise(Vector((t * 4, j, seed))) * 2))   # v3：溝紋加深、沿著樹幹微微扭
                bump = 1 + .13 * noise.noise(Vector((t * 2.5, math.cos(2 * math.pi * j / NR) * .8, math.sin(2 * math.pi * j / NR) * .8 + seed))) + ridge
                if t > .9:   # 斷口：最後一成參差、往內收
                    bump *= 1 - (t - .9) / .1 * rr_.uniform(.15, .8)
                rg.append(bm_.verts.new(c + (s_ * math.cos(a) + Vector((0, 0, 1)) * math.sin(a)) * r * bump))
            rings.append(rg)
        for i in range(NS):
            for j in range(NR):
                f = bm_.faces.new((rings[i][j], rings[i][(j + 1) % NR], rings[i + 1][(j + 1) % NR], rings[i + 1][j]))
                for lp, (ii, jj) in zip(f.loops, ((i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j))):
                    lp[uvl_].uv = (jj / NR * 2 * math.pi * R0 / 1.4, ii / NS * L / 2.2)
        for _cf in (bm_.faces.new(rings[-1][::-1]), bm_.faces.new(rings[0])):
            for lp in _cf.loops:
                lp[uvl_].uv = (lp.vert.co.dot(s_) * .3, lp.vert.co.z * .3)
        # 斷掉的枝椿：往上、往側面伸出一小截
        for k in range(stubs):
            t = rr_.uniform(.3, .8); c, r = cen[int(t * NS)]
            a = rr_.uniform(.4, 1.3) * rr_.choice((1, -1))
            dirr = (s_ * math.cos(a) + Vector((0, 0, 1)) * math.sin(a) + d_ * .35).normalized()
            rs = r * rr_.uniform(.18, .3); Ls = r * rr_.uniform(.9, 1.6)
            prev = None
            for u in range(6):
                tt = u / 5; cc = c + dirr * (r * .8 + Ls * tt)
                q_ = dirr.cross(Vector((0, 0, 1))).normalized(); w_ = dirr.cross(q_).normalized()
                ring = [bm_.verts.new(cc + (q_ * math.cos(b) + w_ * math.sin(b)) * rs * (1 - .55 * tt)) for b in [2 * math.pi * q / 10 for q in range(10)]]
                if prev:
                    for q in range(10):
                        bm_.faces.new((prev[q], prev[(q + 1) % 10], ring[(q + 1) % 10], ring[q]))
                prev = ring
            bm_.faces.new(prev[::-1])
        me_ = bpy.data.meshes.new('LongLog'); bm_.to_mesh(me_); bm_.free()
        for p_ in me_.polygons:
            p_.use_smooth = True
        me_.materials.append(_llm)
        ob_ = bpy.data.objects.new('LongLog', me_); sc.collection.objects.link(ob_)
        globals().setdefault('_LOGS', []).append((Vector((p0.x, p0.y)), math.atan2(d_.y, d_.x), L, R0))
        print('LONGLOG', round(p0.x, 1), round(p0.y, 1), '->', round(p1.x, 1), round(p1.y, 1), 'R', R0)
    if 'longlog' in argv:
        # 第一根：從右前方畫面外，往左後斜躺，斷口落在畫面右側中間
        # v2：順著視線方向往後躺（v1 橫在畫面上像兩條長椅）；近端從畫面右下角外面進來
        long_log(_c5 - _f5 * 1.0 + _r5 * 4.2, _c5 + _f5 * 10.0 + _r5 * 2.6, .8, 61, stubs=0)
        # 第二根：更近、更低，貼著右下角，斷口落在畫面下緣中間偏右
        long_log(_c5 - _f5 * .5 + _r5 * 2.6, _c5 + _f5 * 3.8 + _r5 * 1.7, .55, 62, stubs=0)

# ---------------- 樹（三種新樹種＋古林巨木），依分區散佈 ----------------
# P 傘頂松：直幹 26–36 m，頂上 2–3 層平展樹冠（深綠）→ 東側坡、北側高處
# B 黃綠闊葉：12–20 m，團狀樹冠（黃綠）→ 空地邊緣、東側開口兩旁
# M 圓冠中樹：8–13 m，圓團樹冠 → 林下、遠處成片
# G 古林巨木：22–30 m，粗幹大冠 → 西側、北側深林
TREES = []


def pine(x, y, s):
    z = gh(x, y)
    H = 30 * s
    cyl((x, y, z - .3), .55 * s, .28 * s, H, M_TRUNK)
    for i in range(R.choice((2, 3))):
        zz = z + H * (.82 + i * .08)
        ox, oy = R.uniform(-1.5, 1.5) * s, R.uniform(-1.5, 1.5) * s
        rr = (6.5 - i * 1.6) * s
        blob((x + ox, y + oy, zz), rr, M_PINE, sq=(1, R.uniform(.8, 1.1), .32))


def broad(x, y, s):
    z = gh(x, y)
    H = 16 * s
    cyl((x, y, z - .3), .6 * s, .35 * s, H * .62, M_TRUNK)
    for i in range(6):
        a = R.uniform(0, 6.28)
        d = R.uniform(0, 4.2) * s
        blob((x + math.cos(a) * d, y + math.sin(a) * d, z + H * R.uniform(.62, .95)), R.uniform(2.8, 4.2) * s, M_BROAD, sq=(1, 1, .75))


def roundt(x, y, s):
    z = gh(x, y)
    H = 10 * s
    cyl((x, y, z - .3), .35 * s, .2 * s, H * .6, M_TRUNK)
    blob((x, y, z + H * .72), 3.6 * s, M_ROUND, sq=(1, 1, .9))


def giant(x, y, s):
    z = gh(x, y)
    H = 26 * s
    cyl((x, y, z - .5), 1.6 * s, .9 * s, H * .6, M_TRUNK, v=16)
    for i in range(7):
        a = R.uniform(0, 6.28)
        d = R.uniform(2, 8) * s
        blob((x + math.cos(a) * d, y + math.sin(a) * d, z + H * R.uniform(.6, .92)), R.uniform(4.5, 6.5) * s, M_GIANT, sq=(1, 1, .7))


KIND = {'P': pine, 'B': broad, 'M': roundt, 'G': giant}
if 'real' in argv:     # 換成真的樹模型（collection instance）
    _LIB = {'P': ['umbrella_pine_lib', 'umbrella_pine_lib2', 'umbrella_pine_lib3'], 'B': ['broadleaf_B_lib'], 'M': ['broadleaf_M_lib'], 'G': ['godtree_t10a', 'godtree_t10b', 'godtree_t10c']}
    _SK = lambda nm: nm in ('Grid', 'Cube') or nm.startswith(('Cylinder', 'Camera', 'Sun', 'Human'))
    _COLS = {}
    for _k, _fs in _LIB.items():
        _COLS[_k] = []
        for _fn in _fs:
            _c = bpy.data.collections.new('T_' + _fn)
            with bpy.data.libraries.load(S_ + _fn + '.blend', link=False) as (_s, _d):
                _d.objects = [nm for nm in _s.objects if not _SK(nm)]
            for _o in _d.objects:
                if _o is not None and _o.type == 'MESH':
                    _c.objects.link(_o)
            _COLS[_k].append(_c)

    def _inst(k):
        def f(x, y, s):
            e = bpy.data.objects.new(f'Tree_{k}', None)
            e.instance_type = 'COLLECTION'
            e.instance_collection = R.choice(_COLS[k])
            s = s * (.62 if k == 'G' else 1.0)    # 巨木庫是神木做法、樹冠很寬；縮到設定圖裡的比例
            e.scale = (s, s, s * R.uniform(.94, 1.06))
            e.rotation_euler = (R.uniform(-.05, .05), R.uniform(-.05, .05), R.uniform(0, 6.283)) if k == 'P' else (0, 0, R.uniform(0, 6.283))   # 松樹微微傾斜、不整齊
            if k == 'P':
                e.scale = (s, s, s * R.uniform(.82, 1.15))
            e.location = (x, y, gh(x, y) - .25)
            sc.collection.objects.link(e)
        return f
    KIND = {k: _inst(k) for k in KIND}
    # 古林巨木的葉子在霧裡偏奶白 → 壓暗、加飽和（設定圖 V1 是深綠帶黃綠）
    for _c in _COLS['G']:
        for _o in _c.objects:
            for _sl in _o.material_slots:
                _m = _sl.material
                if _m and 'Leaf' in _m.name and _m.use_nodes and not _m.get('tinted'):
                    _m['tinted'] = 1
                    _b = next((x_ for x_ in _m.node_tree.nodes if x_.type == 'BSDF_PRINCIPLED'), None)
                    if _b and _b.inputs['Base Color'].links:
                        _src = _b.inputs['Base Color'].links[0].from_socket
                        _hs = _m.node_tree.nodes.new('ShaderNodeHueSaturation')
                        _hs.inputs['Saturation'].default_value = 1.35
                        _hs.inputs['Value'].default_value = .62
                        _m.node_tree.links.new(_src, _hs.inputs['Color'])
                        _m.node_tree.links.new(_hs.outputs[0], _b.inputs['Base Color'])
GAP = {'P': 9.0, 'B': 9.0, 'M': 6.5, 'G': 14.0}


def zone_kind(x, y):
    dc = math.hypot(x - CLEAR[0], y - CLEAR[1])
    if x > 30 and -30 < y < 60:
        return R.choice('PPPBM')           # 東坡：松為主
    if dc < CLEAR[2] + 12:
        return R.choice('PPBBM')           # 空地邊緣：松與黃綠闊葉（照設定圖 V3）
    if x < -40 or y > 55:
        return R.choice('GPPMM')           # 西、北深林：巨木與松
    return R.choice('PPMBG')


def ok(x, y):
    if math.hypot(x - CLEAR[0], y - CLEAR[1]) < CLEAR[2]:
        return False
    if math.hypot(x - TREE[0], y - TREE[1]) < 34:
        return False
    if path_d(x, y) < 5.5:
        return False
    if x > 34 and abs(y - VIEW_E[0] * 0 - 20) < 18 and x < 110:   # 東側看向 B 區山的開口
        return R.random() < .15
    return True


import os as _os2
_LOCK = OUT + 'D2_plan_locked.json'   # 樹位置鎖定（六張設定圖就是照這份畫的），改路線也不重洗整片森林
if _os2.path.exists(_LOCK):
    TREES = [tuple(t_) for t_ in json.load(open(_LOCK, encoding='utf-8'))['trees'] if path_d(t_[0], t_[1]) > 4.0]
tries = 0 if not TREES else 10 ** 9
while len(TREES) < (260 if not QUICK else 120) and tries < 60000:
    tries += 1
    x, y = R.uniform(-125, 125), R.uniform(-125, 125)
    if not ok(x, y):
        continue
    k = zone_kind(x, y)
    if any(math.hypot(x - tx, y - ty) < max(GAP[k], GAP[tk]) * R.uniform(.85, 1.1) for tx, ty, tk, _ in TREES):
        continue
    TREES.append((x, y, k, R.uniform(.85, 1.15)))
_CAMS = [(2.5, -97), (8, -10.5), (18.5, -10.5), (-6, 12), (1, 91)]
_CR = random.Random(31)
if 'real' in argv:   # 設定圖 V1：松樹比例高、樹冠之間看得到樹幹 → 外圍一部分圓冠樹換成傘頂松
    # 11/21 第二輪：設定圖 V1、V3 幾乎都是看得到樹幹的傘頂松，圓冠樹只零星幾棵 → 圓冠 75%、巨木 50% 換成松
    TREES = [(x, y, ('P' if (k == 'M' and math.hypot(x - CLEAR[0], y - CLEAR[1]) > CLEAR[2] + 8 and _CR.random() < .5) else k), s) for x, y, k, s in TREES]   # 11/22 他覺得上一版俯瞰較好 → 退回 50%
if 'real' in argv and 'nofill' not in argv:   # 11/24 z1nnz 同意 V1 補樹：空地外圈（離空地中心 22–38 m）樹與樹之間露太多草地 → 補一圈松為主的樹；空地中心、路、祭壇、坑、神木樹冠下照舊空著
    _FR = random.Random(124); _nf = 0
    for _ in range(6000):
        x, y = _FR.uniform(-45, 40), _FR.uniform(-35, 55)
        dc = math.hypot(x - CLEAR[0], y - CLEAR[1])
        if not (22 < dc < CLEAR[2] + 2) or path_d(x, y) < 6 or math.hypot(x - ALT[0], y - ALT[1]) < 13 or math.hypot(x - PIT[0], y - PIT[1]) < 11 or math.hypot(x - TREE[0], y - TREE[1]) < 27:
            continue
        if any(math.hypot(x - tx, y - ty) < 9.5 for tx, ty, _k, _s in TREES):
            continue
        _vx, _vy = x - 8, y + 10.5   # 11/25 補的樹不要擋 V3：V3 鏡頭前 40 m、左右 ±35° 內不補
        _vd = math.hypot(_vx, _vy)
        if _vd < 40 and (_vx * 3 + _vy * 33) / (_vd * math.hypot(3, 33) + 1e-6) > math.cos(math.radians(35)):
            continue
        TREES.append((x, y, 'P' if _FR.random() < .7 else 'M', _FR.uniform(.8, 1.1))); _nf += 1
        if _nf >= 28:
            break
    print('V1 FILL', _nf)
for x, y, k, s in TREES:
    if 'real' in argv and (any(math.hypot(x - cx, y - cy) < (16 if k == 'G' else 8) for cx, cy in _CAMS) or math.hypot(x - ARCH_N[0], y - ARCH_N[1]) < (24 if k == 'G' else 12)):
        continue   # 真樹的樹冠比方塊寬，相機旁邊的樹拿掉，免得鏡頭被擋
    if 'real' in argv and y < 10 and path_d(x, y) < 13:   # 11/22 z1nnz 選了試做版
        continue   # 11/22 試做：V1 俯瞰前景那段路兩旁清出一條林間空帶，從上面看得到小路
    KIND[k](x, y, s)
if 'real' in argv:   # V6 北入口兩側的近景大樹
    # 11/22 V6 框景：右邊近處一棵粗幹老樹、左邊近處一棵黃綠闊葉樹，把拱門框在中間（設定圖 V6）
    for (x_, y_, k_, s_) in [(-21, 99, 'B', 1.15), (11, 106, 'P', 1.05), (17, 113, 'P', .95), (-11, 120, 'B', 1.0), (6, 124, 'B', .9), (6.0, 100.7, 'B', 1.1), (-7.2, 100, 'B', 1.0)]:   # 樹幹落在畫面左右兩邊緣
        KIND[k_](x_, y_, s_)
if 'real' in argv:   # 區塊外（鄰近區塊）的林子也種上，遠景才不會空掉；用另一個亂數，不動區塊內的樹
    FR = random.Random(99)
    extra = []
    for _ in range(40000):
        x, y = FR.uniform(-172, 172), FR.uniform(-172, 172)
        if max(abs(x), abs(y)) < 126 or path_d(x, y) < 5 or (x > 40 and -10 < y < 50) or math.hypot(x - ARCH_N[0], y - ARCH_N[1]) < 20:
            continue
        if any(math.hypot(x - a_, y - b_) < 14 for a_, b_ in extra):   # 疏一點：俯瞰要看得到樹幹和林間白霧
            continue
        extra.append((x, y))
        KIND[FR.choice('PPBMMG')](x, y, FR.uniform(.85, 1.15))
        if len(extra) >= 320:
            break
    print('EXTRA', len(extra))

# ---------------- 大苔石、板根牆、倒木 ----------------
ROCKS = [(-6, -10, 1.6), (12, -14, 2.0), (-12, -2, 1.3), (22, 2, 1.8), (-2, -30, 1.2), (8, -48, 1.5), (-10, 52, 1.7), (24, 44, 1.4)]
if REAL:   # RK01 大苔石（真模型）；另外在路邊、根旁多擺一些小的
    _rk = append(S_ + 'props_lib.blend', lambda nm: nm.startswith('RK01_Boulder'), (0, 0), 0)
    _rkc = []
    for _o in _rk:
        _c = bpy.data.collections.new('C_' + _o.name)
        for _u in list(_o.users_collection):
            _u.objects.unlink(_o)
        _c.objects.link(_o)
        _o.location = (0, 0, 0)
        _rkc.append(_c)
    _RR = random.Random(71)
    _rocks = list(ROCKS) + [(_RR.uniform(-40, 40), _RR.uniform(-95, 110), _RR.uniform(.4, 1.1)) for _ in range(70)]
    for x, y, r in _rocks:
        if path_d(x, y) < 1.8 or math.hypot(x - PIT[0], y - PIT[1]) < 6 or math.hypot(x - ALT[0], y - ALT[1]) < 6:
            continue
        e = bpy.data.objects.new('Rock', None)
        e.instance_type = 'COLLECTION'
        e.instance_collection = _rkc[0 if r > 1.7 else 1 if r > 1.3 else 2 if r > .9 else 3] if _RR.random() < .8 else _RR.choice(_rkc)
        s_ = r / 1.2
        e.scale = (s_, s_, s_ * _RR.uniform(.8, 1.1))
        e.rotation_euler.z = _RR.uniform(0, 6.283)
        e.location = (x, y, gh(x, y) - .06 * s_)
        globals().setdefault('_ALLROCK', []).append((x, y, r))
        sc.collection.objects.link(e)
        _nrk = globals().get('_nrk', 0) + 1
        globals()['_nrk'] = _nrk
    print('ROCKS', globals().get('_nrk', 0), [len(c_.objects) for c_ in _rkc])
    # 設定圖裡各鏡頭前景的大苔石（手擺）
    # 11/22：V4 坑邊那顆放大（設定圖比較大）；新增 V3 右下角前景一顆大苔石
    HERO = [(5.5, -1.5, 1.8, 1), (12.5, -6.5, 1.7, 2), (21, -5.5, 1.3, 2), (-3.5, -8, 1.3, 1), (5, -89, 1.4, 2), (-5, 96, 1.3, 2), (7.4, -11.9, 1.9, 1)]
    for x, y, r, ci in HERO:
        e = bpy.data.objects.new('HeroRock', None)
        e.instance_type = 'COLLECTION'
        e.instance_collection = _rkc[ci]
        e.scale = (r / 1.2,) * 3
        e.rotation_euler.z = _RR.uniform(0, 6.283)
        e.location = (x, y, gh(x, y) - .12 * r / 1.2)
        sc.collection.objects.link(e)
    globals()['_HERO'] = HERO
else:
  for x, y, r in ROCKS:
    blob((x, y, gh(x, y) + r * .2), r, M_ROCK, sq=(1.2, 1, .7))
    blob((x, y, gh(x, y) + r * .55), r * .8, M_MOSS, sq=(1.2, 1, .35))
WALLS = [((22, 4), (30, 16)), ((-14, 4), (-22, -6)), ((-36, 20), (-46, 30))]
for a, b in WALLS:
    root_ridge(a, b, 1.1, .8)
LOGS = [((-30, -20), (-22, -26)), ((30, -34), (36, -24))]
for (ax, ay), (bx, by) in LOGS:
    L = math.hypot(bx - ax, by - ay)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=.7, depth=L, location=((ax + bx) / 2, (ay + by) / 2, gh(ax, ay) + .5),
                                        rotation=(math.pi / 2, 0, math.atan2(by - ay, bx - ax) - math.pi / 2))
    put(bpy.context.object, M_TRUNK)

# 被挖的坑：坑邊翻出來的土堆（方塊模型用，讓每個角度都看得出坑在哪）
M_DIRT = mat('dirt', (.36, .22, .12))
if 'real' in argv:
    texmat(M_DIRT, 'brown_mud_02_diff_2k.png', 'brown_mud_02_nor_gl_2k.png', 'brown_mud_02_rough_2k.png', .6, (1.05, .72, .46), box=True)
for i in range(0 if 'real' in argv else 14):   # 真模型模式用核心組的 CO01 坑模型，不放方塊土堆
    a = i / 14 * 6.283 + R.uniform(-.2, .2)
    rr = 3.2 + R.uniform(-.3, .6)
    x, y = PIT[0] + math.cos(a) * rr, PIT[1] + math.sin(a) * rr
    blob((x, y, gh(x, y) + .05), R.uniform(.7, 1.2), M_DIRT, sq=(1.5, 1.1, .38), sub=3 if 'real' in argv else 1)
if 'real' not in argv:
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=2.6, depth=.05, location=(PIT[0], PIT[1], gh(*PIT) + .15))
    put(bpy.context.object, mat('hole', (.06, .04, .03)))

# ---------------- 林下植物（真模型模式）：蕨叢、心形葉，做幾個樣板再用 instance 鋪滿路旁與空地 ----------------
if 'real' in argv:
    from mathutils import Matrix
    exec(compile(open(S_ + 'plants.py', encoding='utf-8').read(), S_ + 'plants.py', 'exec'))
    fern_mat = _leaf_material('UG01_Fern', (.040, .085, .022, 1), (.085, .16, .040, 1), (.12, .19, .06, 1), gloss=.5)
    heart_mat = _leaf_material('UG02_Heart', (.030, .070, .022, 1), (.070, .13, .040, 1), (.13, .19, .08, 1), gloss=.35)
    stem_mat = bpy.data.materials.new('UG_Stem')
    stem_mat.use_nodes = True
    next(x for x in stem_mat.node_tree.nodes if x.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.05, .07, .02, 1)
    exec(compile(open(S_ + 'weeds.py', encoding='utf-8').read(), S_ + 'weeds.py', 'exec'))
    WM = weed_materials()
    PR = random.Random(17)
    # 樣板：各種雜草多個隨機變體（z1nnz 11/21：重複率太高 → 種類、變體都加多）
    SPEC_UG = [   # (類別, 建造函式, 變體數, 權重)
        ('fern', lambda nm, R_: fern(nm, Vector((0, 0, 0)), R_, R_.uniform(.8, 1.2), fern_mat, stem_mat), 6, .64),
        ('heart', lambda nm, R_: heart_plant(nm, Vector((0, 0, 0)), R_, R_.uniform(.8, 1.2), heart_mat, stem_mat), 3, .12),
        ('grass', lambda nm, R_: grass_tuft(nm, Vector((0, 0, 0)), R_, R_.uniform(.7, 1.3), WM['grass'], dry=R_.choice([0, .3])), 6, .08),
        ('sedge', lambda nm, R_: sedge(nm, Vector((0, 0, 0)), R_, R_.uniform(.8, 1.2), WM['sedge']), 3, .03),
        ('clover', lambda nm, R_: clover(nm, Vector((0, 0, 0)), R_, R_.uniform(.8, 1.3), WM['clover']), 4, .07),
        ('rosette', lambda nm, R_: rosette(nm, Vector((0, 0, 0)), R_, R_.uniform(.8, 1.2), WM['rosette']), 3, .04),
        ('sapling', lambda nm, R_: sapling(nm, Vector((0, 0, 0)), R_, R_.uniform(.8, 1.3), WM['sapling'], stem_mat), 3, .02),
    ]
    UG = {}
    for cat, fn, nv_, w_ in SPEC_UG:
        UG[cat] = []
        for v_ in range(nv_):
            before = set(bpy.data.objects)
            fn(f'UG_{cat}{v_}', random.Random(sum(map(ord, cat)) * 31 + v_))
            col = bpy.data.collections.new(f'UG_{cat}{v_}')
            for o in set(bpy.data.objects) - before:
                for c_ in list(o.users_collection):
                    c_.objects.unlink(o)
                col.objects.link(o)
            UG[cat].append(col)
    CATS = [c for c, *_ in SPEC_UG]
    WTS = [w for *_, w in SPEC_UG]
    nug = 0
    for i in range(300000):
        x, y = PR.uniform(-70, 70), PR.uniform(-105, 125)
        pdist = path_d(x, y)
        near = min([math.hypot(x - cx, y - cy) for cx, cy in _CAMS] + [math.hypot(x - ARCH_N[0], y - ARCH_N[1]) * .8, math.hypot(x - ARCH_S[0], y - ARCH_S[1]) * .8])
        if any(math.hypot(x - hx, y - hy) < hr * 1.3 for hx, hy, hr, _ in globals().get('_HERO', [])) or any(math.hypot(x - hx, y - hy) < hr * 1.1 for hx, hy, hr in globals().get('_ALLROCK', [])):
            continue
        if pdist < 3.0 or math.hypot(x - PIT[0], y - PIT[1]) < 5.0 or math.hypot(x - ALT[0], y - ALT[1]) < 6.5:
            continue
        if any(math.hypot(x - q_.x, y - q_.y) < 1.4 for q_ in globals().get('_V5RP', [])):
            continue
        if any(math.hypot(x - px_, y - py_) < pr_ + .5 for px_, py_, pr_ in globals().get('_PROPS', [])):   # 擺件旁不長大蕨（只留矮草）
            continue
        _skip = False
        for _lp, _la, _lL, _lR in globals().get('_LOGS', []):   # 倒木上不長蕨（壓在上面會穿模）
            _ld = Vector((math.cos(_la), math.sin(_la))); _rel = Vector((x, y)) - _lp
            _tt = max(0.0, min(_lL, _rel.dot(_ld)))
            if (_rel - _ld * _tt).length < _lR + .3:
                _skip = True
        if _skip:
            continue
        # V3 相機到坑之間是一片矮地（設定圖 V3 看得到坑），不長高的蕨
        _ax, _ay, _bx, _by = 4, -15, PIT[0], PIT[1]
        _t = max(0, min(1, ((x - _ax) * (_bx - _ax) + (y - _ay) * (_by - _ay)) / ((_bx - _ax) ** 2 + (_by - _ay) ** 2)))
        if _t > .35 and math.hypot(x - _ax - _t * (_bx - _ax), y - _ay - _t * (_by - _ay)) < 3.0:
            continue
        # 密度降低、成叢成片：用低頻雜訊做出有草的區塊和空地
        patch = .5 + .5 * noise.noise(Vector((x * .09, y * .09, 4.4)))
        p = min(1.0, max(1.0 * math.exp(-near / 20), .6 * math.exp(-(pdist - 2.6) / 7), .08) * (.55 + .8 * patch))
        if PR.random() > p:
            continue
        # 每一區偏某幾種草（同種成片，不同區不同），再混一點別的
        zone = .5 + .5 * noise.noise(Vector((x * .05, y * .05, 8.8)))
        w2 = [w * (1.5 if (k / len(CATS) <= zone < (k + 2) / len(CATS)) else .8) for k, w in enumerate(WTS)]
        cat = PR.choices(CATS, w2)[0]
        e = bpy.data.objects.new('UG', None)
        e.instance_type = 'COLLECTION'
        e.instance_collection = PR.choice(UG[cat])
        s_ = PR.choice([PR.uniform(.35, .65), PR.uniform(.35, .65), PR.uniform(.6, .95), PR.uniform(.6, .95), PR.uniform(.9, 1.5)])
        if cat == 'fern':   # 蕨＝原本那種大蕨叢（z1nnz：原本的草很好看），大小有高有低
            s_ = PR.choice([PR.uniform(.5, .8), PR.uniform(.8, 1.2), PR.uniform(.8, 1.2), PR.uniform(1.1, 1.6)]) * (1.2 if pdist < 6 else 1.0)
        elif cat == 'heart':
            s_ = PR.uniform(.7, 1.4)
        else:   # 其他雜草當點綴、偏小
            s_ = s_ * .7
        e.scale = (s_ * PR.uniform(.85, 1.15), s_ * PR.uniform(.85, 1.15), s_ * PR.uniform(.8, 1.25))
        e.rotation_euler = (PR.uniform(-.08, .08), PR.uniform(-.08, .08), PR.uniform(0, 6.283))
        e.location = (x, y, gh(x, y) - .03)
        sc.collection.objects.link(e)
        nug += 1
        if cat in ('clover',):   # 小草成小片：旁邊再長 1–4 叢同種不同變體
            for _ in range(PR.randint(0, 2)):
                x2, y2 = x + PR.uniform(-.7, .7), y + PR.uniform(-.7, .7)
                if path_d(x2, y2) < 2.4:
                    continue
                e2 = bpy.data.objects.new('UG', None)
                e2.instance_type = 'COLLECTION'
                e2.instance_collection = PR.choice(UG[cat])
                s2 = PR.uniform(.35, 1.0)
                e2.scale = (s2, s2, s2 * PR.uniform(.8, 1.2))
                e2.rotation_euler.z = PR.uniform(0, 6.283)
                e2.location = (x2, y2, gh(x2, y2) - .03)
                sc.collection.objects.link(e2)
                nug += 1
        if nug >= 20000:
            break
    print('UNDERGROWTH', nug)
    # 11/24 過渡：擺件底部一圈矮草、莎草（成叢、不均勻）
    _BG = random.Random(71); _SMALL = UG['grass'] + UG['sedge'] + UG['clover']
    def _tuft(x, y, z, s):
        e = bpy.data.objects.new('UG', None); e.instance_type = 'COLLECTION'; e.instance_collection = _BG.choice(_SMALL)
        e.scale = (s, s, s * _BG.uniform(.8, 1.3)); e.rotation_euler.z = _BG.uniform(0, 6.283)
        e.location = (x, y, z); sc.collection.objects.link(e)
    for _x, _y, _r in globals().get('_PROPS', []):
        for _ in range(_BG.randint(7, 12)):
            a = _BG.uniform(0, 6.283) if _BG.random() < .4 else _BG.gauss(1.0, .8)   # 偏一側長得多
            d = _r + _BG.uniform(.0, .55); x2, y2 = _x + math.cos(a) * d, _y + math.sin(a) * d
            if path_d(x2, y2) > 1.8:
                _tuft(x2, y2, gh(x2, y2) + .02, _BG.uniform(.35, .75))
    # 11/24 祭壇做舊：石階邊緣、石縫長草（往下打射線，找祭壇頂面上靠邊的位置）
    _nseam = 0
    bpy.context.view_layer.update()
    for _o in globals().get('_ALTOBJ', []):
        if _o.type != 'MESH':
            continue
        _mw = _o.matrix_world; _mi = _mw.inverted(); _bb = [_mw @ Vector(c) for c in _o.bound_box]
        _x0, _x1 = min(v.x for v in _bb), max(v.x for v in _bb); _y0, _y1 = min(v.y for v in _bb), max(v.y for v in _bb); _zt = max(v.z for v in _bb) + 1
        def _hit(px, py):
            o_ = _mi @ Vector((px, py, _zt)); d_ = (_mi.to_3x3() @ Vector((0, 0, -1))).normalized()
            ok_, loc_, nor_, _ = _o.ray_cast(o_, d_)
            return (_mw @ loc_, (_mw.to_3x3() @ nor_).normalized()) if ok_ else (None, None)
        for _ in range(4000):
            px, py = _BG.uniform(_x0, _x1), _BG.uniform(_y0, _y1)
            lo, no = _hit(px, py)
            if lo is None or no.z < .9 or lo.z < gh(px, py) + .12:
                continue
            edge = False
            for dx, dy in ((.22, 0), (-.22, 0), (0, .22), (0, -.22)):
                l2, _n2 = _hit(px + dx, py + dy)
                if l2 is None or l2.z < lo.z - .1:
                    edge = True
            if edge and _BG.random() < .35:
                _tuft(lo.x, lo.y, lo.z - .01, _BG.uniform(.25, .5)); _nseam += 1
            if _nseam >= 70:
                break
    print('BASEGRASS', len(globals().get('_PROPS', [])), 'SEAM', _nseam)
    for _x, _y in globals().get('_SLABS', []):   # 石板縫長草
        for _ in range(_BG.randint(1, 3)):
            a = _BG.uniform(0, 6.283); x2, y2 = _x + math.cos(a) * .4, _y + math.sin(a) * .4
            _tuft(x2, y2, gh(x2, y2) + .01, _BG.uniform(.15, .3) if path_d(x2, y2) < 1.2 else _BG.uniform(.25, .45))   # 路中間只有貼地小草
    # 11/22 優化：地上的草 → 一片片平貼的三葉草太多、看起來像貼上去的 → 三葉草減少，加入各種高度的草叢與莎草
    GC = UG['clover'] + UG['rosette'] + UG['heart'][:1] + UG['grass'] + UG['sedge']
    GW = [1.6] * len(UG['clover']) + [1.2] * len(UG['rosette']) + [1.5] + [1.4] * len(UG['grass']) + [1.0] * len(UG['sedge'])
    GR = random.Random(57)
    ngc = 0
    for cx, cy in _CAMS + [ARCH_S, ARCH_N, PIT, ALT, TREE]:
        for i in range(1500):
            a_, r_ = GR.uniform(0, 6.283), 32 * GR.random() ** .6
            x, y = cx + math.cos(a_) * r_, cy + math.sin(a_) * r_
            if path_d(x, y) < 3.0 or math.hypot(x - PIT[0], y - PIT[1]) < 4.6 or math.hypot(x - ALT[0], y - ALT[1]) < 6.0:
                continue
            e = bpy.data.objects.new('GC', None)
            e.instance_type = 'COLLECTION'
            e.instance_collection = GR.choices(GC, GW)[0]
            s_ = GR.uniform(.35, .8)
            e.scale = (s_, s_, s_ * GR.uniform(.5, 1.5))   # 高矮不一
            e.rotation_euler.z = GR.uniform(0, 6.283)
            e.location = (x, y, gh(x, y) - .02)
            sc.collection.objects.link(e)
            ngc += 1
    print('GROUNDCOVER', ngc)
    # 11/22 新物件：常春藤爬在 V6 兩棵框景樹的樹幹上（設定圖 V6 右邊那棵整根爬滿藤）
    _ivm = bpy.data.materials.new('IvyLeaf'); _ivm.use_nodes = True
    _ivn = _ivm.node_tree; _ivb = next(x_ for x_ in _ivn.nodes if x_.type == 'BSDF_PRINCIPLED')
    _ivo = _ivn.nodes.new('ShaderNodeObjectInfo'); _ivc = _ivn.nodes.new('ShaderNodeValToRGB')
    _ivc.color_ramp.elements[0].color = (.025, .045, .015, 1); _ivc.color_ramp.elements[1].color = (.09, .13, .04, 1)
    _ivr = _ivn.nodes.new('ShaderNodeAttribute'); _ivr.attribute_name = 'LeafTone'
    _ivn.links.new(_ivr.outputs['Fac'], _ivc.inputs[0]); _ivn.links.new(_ivc.outputs[0], _ivb.inputs['Base Color'])
    _ivb.inputs['Roughness'].default_value = .45
    try:
        _ivb.inputs['Transmission Weight'].default_value = .0
        _ivb.inputs['Subsurface Weight'].default_value = .1
    except KeyError:
        pass
    _IR = random.Random(77)
    for (tx_, ty_, s_) in ((6.0, 100.7, 1.1), (-7.2, 100, 1.0)):
        z0_ = gh(tx_, ty_) - .3
        Ht_ = 16 * s_ * .62
        bm_ = bmesh.new(); tone_ = []
        for st_ in range(9):   # 9 條藤從樹腳往上繞
            a_ = _IR.uniform(0, 6.283); z_ = _IR.uniform(0, .5); zt_ = Ht_ * _IR.uniform(.55, .95)
            while z_ < zt_:
                t_ = z_ / Ht_
                rr_ = (.6 * s_ * (1 - t_) + .35 * s_ * t_) + .04
                for _ in range(3):   # 每一節 3 片葉
                    la_ = a_ + _IR.uniform(-.25, .25); lz_ = z_ + _IR.uniform(-.08, .08)
                    n_ = Vector((math.cos(la_), math.sin(la_), 0))
                    c_ = Vector((tx_ + n_.x * rr_, ty_ + n_.y * rr_, z0_ + lz_)) + n_ * _IR.uniform(0, .06)
                    up_ = Vector((0, 0, 1)); sd_ = n_.cross(up_)
                    sz_ = _IR.uniform(.07, .14)
                    tilt_ = n_ * _IR.uniform(.2, .6)
                    v0 = bm_.verts.new(c_ - up_ * sz_ * .2)
                    v1 = bm_.verts.new(c_ + sd_ * sz_ * .55 + up_ * sz_ * .35 + tilt_ * sz_)
                    v2 = bm_.verts.new(c_ + up_ * sz_ * 1.0 + tilt_ * sz_ * 1.4)
                    v3 = bm_.verts.new(c_ - sd_ * sz_ * .55 + up_ * sz_ * .35 + tilt_ * sz_)
                    bm_.faces.new((v0, v1, v2, v3)); tone_ += [_IR.random()] * 4
                a_ += _IR.uniform(.05, .22) / max(rr_, .2); z_ += _IR.uniform(.07, .13)
        me_ = bpy.data.meshes.new('Ivy'); bm_.to_mesh(me_); bm_.free()
        at_ = me_.attributes.new('LeafTone', 'FLOAT', 'POINT'); at_.data.foreach_set('value', tone_)
        me_.materials.append(_ivm)
        ob_ = bpy.data.objects.new('Ivy', me_); sc.collection.objects.link(ob_)
        print('IVY', len(me_.polygons))
    # 路上的積水小窪、落葉（設定圖每一張路面都有）
    litter_mat = _leaf_material('Litter', (.55, .5, .45, 1), (.85, .8, .72, 1), (.9, .85, .7, 1), gloss=.6)
    LR = random.Random(41)

    def _lit_place():
        cx, cy = LR.choice(_CAMS + [ARCH_S, ARCH_N, PIT, ALT])
        a_, r_ = LR.uniform(0, 6.283), 24 * LR.random() ** .7
        x, y = cx + math.cos(a_) * r_, cy + math.sin(a_) * r_
        if math.hypot(x - PIT[0], y - PIT[1]) < 3.6:
            return None
        return (x, y), gh(x, y)
    litter('PathLitter', LR, 110000, _lit_place, litter_mat)
    pw = bpy.data.materials.new('Puddle')
    pw.use_nodes = True
    _pb = next(x_ for x_ in pw.node_tree.nodes if x_.type == 'BSDF_PRINCIPLED')
    _pb.inputs['Base Color'].default_value = (.03, .028, .025, 1)
    _pb.inputs['Roughness'].default_value = .03
    npd = 0
    for i in range(4000):
        x, y = LR.uniform(-30, 30), LR.uniform(-100, 110)
        if True:   # 改用路面材質的濕窪（模型窪會浮起來、像鏡子）
            continue
        r_ = LR.uniform(.15, .55)
        bpy.ops.mesh.primitive_circle_add(vertices=20, radius=r_, fill_type='NGON', location=(x, y, gh(x, y) + .012))
        pu = bpy.context.object
        pu.scale = (LR.uniform(1, 1.8), LR.uniform(.6, 1), 1)
        pu.rotation_euler.z = LR.uniform(0, 3.14)
        pu.data.materials.append(pw)
        npd += 1
    print('PUDDLES', npd)

    # ---------------- 小件：蕈叢、苔丘、小石頭、拱門垂藤 ----------------
    SR = random.Random(83)

    def _template(nm, build):
        before = set(bpy.data.objects)
        build()
        col = bpy.data.collections.new(nm)
        for o in set(bpy.data.objects) - before:
            for u in list(o.users_collection):
                u.objects.unlink(o)
            col.objects.link(o)
        return col

    def _inst(col, x, y, s, z_off=0.0, rz=None):
        e = bpy.data.objects.new('Small', None)
        e.instance_type = 'COLLECTION'
        e.instance_collection = col
        e.scale = (s, s, s)
        e.rotation_euler.z = SR.uniform(0, 6.283) if rz is None else rz
        e.location = (x, y, gh(x, y) + z_off)
        sc.collection.objects.link(e)

    # 蕈叢：4 種（褐、淺茶、橘褐、小白），長在石頭邊、根邊、倒木旁
    mmat = mushroom_material()
    MUSH = [_template(f'MU{i}', lambda i=i: mushrooms(f'MU{i}', Vector((0, 0, 0)), random.Random(90 + i), SR.randint(4, 11),
                                                       [1.3, 1.0, 1.6, .8][i], mmat, cap=[(.30, .17, .08), (.48, .36, .22), (.42, .20, .07), (.70, .66, .58)][i]))
            for i in range(4)]
    anchors = [(x, y, r) for x, y, r in globals().get('_ALLROCK', [])] + [(hx, hy, hr) for hx, hy, hr, _ in globals().get('_HERO', [])]
    for a, b in ROOTS:
        for s in (.35, .6, .85):
            anchors.append((a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s, .6))
    nmu = 0
    for x0, y0, r0_ in anchors:
        for _ in range(SR.randint(0, 3)):
            ang = SR.uniform(0, 6.283)
            x, y = x0 + math.cos(ang) * (r0_ * .55 + SR.uniform(.1, .5)), y0 + math.sin(ang) * (r0_ * .55 + SR.uniform(.1, .5))
            if path_d(x, y) < 1.6:
                continue
            _inst(SR.choice(MUSH), x, y, SR.uniform(1.8, 3.0))
            nmu += 1
    # 苔丘：毛茸茸的短苔，貼著石頭腳、根腳、路邊
    mmoss = _leaf_material('UG20_Moss', (.035, .06, .014, 1), (.12, .16, .045, 1), (.13, .17, .05, 1), gloss=.8)
    _fbf = lambda p, s, o: noise.fractal(Vector(p) * s, .5, 2.0, o)
    MOSS = [_template(f'MO{i}', lambda i=i: moss_tufts(f'MO{i}', [(i, 0, 0, [.45, .7, .35, .9][i], [.35, .5, .3, .55][i], [.08, .12, .06, .1][i], -.01)],
                                                      random.Random(70 + i), mmoss, _fbf, density=4200)) for i in range(4)]
    nmo = 0
    for x0, y0, r0_ in anchors:
        for _ in range(SR.randint(1, 4)):
            ang = SR.uniform(0, 6.283)
            x, y = x0 + math.cos(ang) * (r0_ * .5 + SR.uniform(0, .4)), y0 + math.sin(ang) * (r0_ * .5 + SR.uniform(0, .4))
            if path_d(x, y) < 1.4:
                continue
            _inst(SR.choice(MOSS), x, y, SR.uniform(.7, 1.6), -.02)
            nmo += 1
    # 厚苔（設定圖 v2）：真的有厚度的苔墊，鋪在神木根部、長根、拱門朝上的面
    import numpy as _np

    def _moss_on(objs, n, zmax=None, smin=.35, smax=.8, seed=5):
        rr_ = random.Random(seed)
        pts = []
        for o_, mw_ in objs:
            me_ = o_.data
            npo = len(me_.polygons)
            if npo == 0:
                continue
            ce = _np.zeros(npo * 3); nr = _np.zeros(npo * 3); ar = _np.zeros(npo)
            me_.polygons.foreach_get('center', ce); me_.polygons.foreach_get('normal', nr); me_.polygons.foreach_get('area', ar)
            ce = ce.reshape(-1, 3); nr = nr.reshape(-1, 3)
            for i_ in rr_.sample(range(npo), min(npo, 4000)):
                p_ = mw_ @ Vector(ce[i_])
                q_ = (mw_.to_3x3() @ Vector(nr[i_])).normalized()
                if q_.z < .5 or (zmax is not None and p_.z - gh(p_.x, p_.y) > zmax):
                    continue
                if path_d(p_.x, p_.y) < 1.2:
                    continue
                pts.append((p_, q_))
        rr_.shuffle(pts)
        for p_, q_ in pts[:n]:
            e = bpy.data.objects.new('MossPad', None)
            e.instance_type = 'COLLECTION'
            e.instance_collection = rr_.choice(MOSSP)
            s_ = rr_.uniform(smin, smax)
            rot = q_.to_track_quat('Z', 'Y') @ Matrix.Rotation(rr_.uniform(0, 6.283), 4, 'Z').to_quaternion()
            e.rotation_mode = 'QUATERNION'
            e.rotation_quaternion = rot
            e.scale = (s_, s_, s_ * rr_.uniform(.8, 1.2))
            e.location = p_ - q_ * .03
            sc.collection.objects.link(e)
        return min(n, len(pts))
    # 樹上的苔墊：設定圖是受光的黃橄欖色、厚厚一團，比地上的苔亮
    # 苔墊本體：實心、一團團隆起的苔枕（不是一層細毛）；表面用細碎凹凸做出絨毛感，邊緣貼合樹皮
    mmossp = bpy.data.materials.new('UG22_BarkMoss')
    mmossp.use_nodes = True
    _mt = mmossp.node_tree
    _mb = next(x_ for x_ in _mt.nodes if x_.type == 'BSDF_PRINCIPLED')
    _mp = _mt.nodes.new('ShaderNodeNewGeometry')
    _mn1 = _mt.nodes.new('ShaderNodeTexNoise'); _mn1.inputs['Scale'].default_value = 3.0; _mn1.inputs['Detail'].default_value = 4
    _mt.links.new(_mp.outputs['Position'], _mn1.inputs['Vector'])
    _mcr = _mt.nodes.new('ShaderNodeValToRGB')
    _mcr.color_ramp.elements[0].position, _mcr.color_ramp.elements[1].position = .3, .72
    _mcr.color_ramp.elements[0].color = (.045, .055, .014, 1)
    _mcr.color_ramp.elements[1].color = (.20, .21, .055, 1)   # 受光處偏黃橄欖（設定圖）
    _mt.links.new(_mn1.outputs['Fac'], _mcr.inputs[0])
    _mao = _mt.nodes.new('ShaderNodeAmbientOcclusion'); _mao.inputs['Distance'].default_value = .15
    _mmx = _mt.nodes.new('ShaderNodeMixRGB'); _mmx.blend_type = 'MULTIPLY'; _mmx.inputs[0].default_value = .7
    _mt.links.new(_mcr.outputs[0], _mmx.inputs[1]); _mt.links.new(_mao.outputs['AO'], _mmx.inputs[2])
    _mt.links.new(_mmx.outputs[0], _mb.inputs['Base Color'])
    _mb.inputs['Roughness'].default_value = .95
    _mn2 = _mt.nodes.new('ShaderNodeTexNoise'); _mn2.inputs['Scale'].default_value = 140; _mn2.inputs['Detail'].default_value = 2
    _mt.links.new(_mp.outputs['Position'], _mn2.inputs['Vector'])
    _mbp = _mt.nodes.new('ShaderNodeBump'); _mbp.inputs['Strength'].default_value = .9; _mbp.inputs['Distance'].default_value = .01
    _mt.links.new(_mn2.outputs['Fac'], _mbp.inputs['Height'])
    _mt.links.new(_mbp.outputs['Normal'], _mb.inputs['Normal'])
    try:
        _mb.inputs['Sheen Weight'].default_value = .6
        _mb.inputs['Sheen Tint'].default_value = (.5, .6, .3, 1)
    except KeyError:
        pass

    def _cushion(i):
        bm_ = bmesh.new()
        bmesh.ops.create_icosphere(bm_, subdivisions=4, radius=1)
        rr_ = random.Random(300 + i)
        k1 = rr_.uniform(.7, 1.2)
        off = Vector((i * 5.3, 1.7, 0))
        for v in bm_.verts:
            c = v.co.copy()
            lump = noise.noise(c * 2.2 + off) * .22 + noise.noise(c * 5 + off) * .06
            r = 1 + lump
            z = c.z * .38 * (1 + lump * 1.5)
            if z < -.06:   # 底面壓平、稍微埋進樹皮
                z = -.06 - (-.06 - z) * .1
            v.co = Vector((c.x * k1 * r, c.y * r, z))
        me_ = bpy.data.meshes.new(f'MP{i}')
        bm_.to_mesh(me_)
        bm_.free()
        for p in me_.polygons:
            p.use_smooth = True
        me_.materials.append(mmossp)
        sc.collection.objects.link(bpy.data.objects.new(f'MP{i}', me_))
    MOSSP = [_template(f'MP{i}', lambda i=i: _cushion(i)) for i in range(5)]
    _gt_bark = [(o_, o_.matrix_world) for o_ in _GTO if o_.type == 'MESH' and not any(k_ in o_.name for k_ in ('Leaf', 'Leaves', 'Twig', 'Crown'))]
    _arch_m = [(o_, o_.matrix_world) for o_ in (_ARS + [a_ for a_ in _ARN if a_.type == 'MESH']) if o_.type == 'MESH']
    bpy.context.view_layer.update()
    _root_m = []
    for e_ in list(sc.collection.objects):
        if e_.name.startswith('Root') and e_.instance_type == 'COLLECTION' and e_.instance_collection:
            for o_ in e_.instance_collection.objects:
                if o_.type == 'MESH':
                    _root_m.append((o_, e_.matrix_world @ o_.matrix_world))
    bpy.context.view_layer.update()
    # 試過實心苔枕（11/21）：看起來像黏上去的塑膠塊，比材質苔差 → 不放，改加強 mossify 的苔（顏色、絨毛凹凸）
    if 'mosspad' in argv:
        print('MOSSPAD', _moss_on(_gt_bark, 900, zmax=9, smin=.3, smax=.75, seed=5),
              _moss_on(_arch_m, 500, smin=.2, smax=.45, seed=6), _moss_on(_root_m, 700, smin=.25, smax=.55, seed=7))
    for cx, cy in _CAMS:   # 路邊一塊塊苔
        for _ in range(60):
            x, y = cx + SR.uniform(-16, 16), cy + SR.uniform(-16, 16)
            pd_ = path_d(x, y)
            if 1.6 < pd_ < 4.5:
                _inst(SR.choice(MOSS), x, y, SR.uniform(.6, 1.4), -.02)
                nmo += 1
    # 小石頭：深灰褐、半埋，路面和路邊最多
    stm = bpy.data.materials.new('SmallStone')
    stm.use_nodes = True
    _sb = next(x_ for x_ in stm.node_tree.nodes if x_.type == 'BSDF_PRINCIPLED')
    _sb.inputs['Base Color'].default_value = (.085, .08, .07, 1)
    _sb.inputs['Roughness'].default_value = .75
    texmat(stm, 'mossy_rock_diff_2k.png', 'mossy_rock_nor_gl_2k.png', 'mossy_rock_rough_2k.png', .45, (.62, .58, .52), box=True)   # 設定圖的小石頭是灰褐帶斑，不是黑豆

    def _stone(i):
        bm_ = bmesh.new()
        bmesh.ops.create_icosphere(bm_, subdivisions=2, radius=1)
        rr_ = random.Random(i)
        k1, k2 = rr_.uniform(.7, 1.3), rr_.uniform(.35, .6)
        for v in bm_.verts:
            v.co = Vector((v.co.x * k1, v.co.y, v.co.z * k2)) * (1 + .18 * noise.noise(v.co * 1.7 + Vector((i * 3, 0, 0))))
        me_ = bpy.data.meshes.new(f'ST{i}')
        bm_.to_mesh(me_)
        bm_.free()
        for p in me_.polygons:
            p.use_smooth = True
        me_.materials.append(stm)
        sc.collection.objects.link(bpy.data.objects.new(f'ST{i}', me_))
    STN = [_template(f'STC{i}', lambda i=i: _stone(i)) for i in range(5)]
    nst = 0
    for cx, cy in _CAMS + [ARCH_S, ARCH_N]:
        for _ in range(260):
            x, y = cx + SR.uniform(-18, 18), cy + SR.uniform(-18, 18)
            pd_ = path_d(x, y)
            if pd_ < 3.5 and SR.random() < (.9 if pd_ < 1.5 else .5):
                _inst(SR.choice(STN), x, y, SR.uniform(.04, .16), -.03)
                nst += 1
            if 1.2 < pd_ < 3.0 and SR.random() < .12:   # 路邊半埋的大一點石頭（設定圖每張路邊都有）
                _inst(SR.choice(STN), x, y, SR.uniform(.18, .34), -.08)
                nst += 1
    # 11/22 優化 1：路面碎石（設定圖泥路上滿是 2–8 cm 的小碎石，集中在路中間和車轍邊）
    GR_ = random.Random(23)
    for cx, cy in _CAMS + [ARCH_S, ARCH_N]:
        for _ in range(14000):   # 第一版太少看不出來、第二版 1.5 萬顆像鋪石子路 → 取中間：稀疏、小顆、半埋
            x, y = cx + GR_.uniform(-20, 20), cy + GR_.uniform(-20, 20)
            if path_d(x, y) < 1.7 and GR_.random() < .4:
                _inst(GR_.choice(STN), x, y, GR_.uniform(.03, .06) if GR_.random() < .85 else GR_.uniform(.06, .1), -.03)
                nst += 1
    print('STONES', nst)
    # 拱門垂藤：從拱頂內側垂下的細藤，帶小葉（設定圖 V2、V6）
    vmat = _leaf_material('UG21_Vine', (.04, .07, .02, 1), (.10, .15, .045, 1), (.12, .17, .06, 1), gloss=.5)
    nvine = 0
    for arch in (_ARS + [o_ for o_ in _ARN if o_.type == 'MESH']):
        if arch.type != 'MESH' or len(arch.data.vertices) < 20000:
            continue
        mw = arch.matrix_world
        _vv = arch.data.vertices
        ws = [mw @ _vv[i_].co for i_ in range(0, len(_vv), max(1, len(_vv) // 6000))]
        zt = max(w.z for w in ws)
        zb = min(w.z for w in ws)
        cand = [w for w in ws if w.z > zb + (zt - zb) * .55]
        vb = LeafBuf()
        for k in range(95 if arch in _ARS else 55):   # 設定圖 V2、V6 拱門垂藤很多（11/24 V2 南拱再加）
            p0 = SR.choice(cand)
            L_ = SR.uniform(.8, min(2.6, (p0.z - gh(p0.x, p0.y)) * .7))
            n_ = int(L_ / .06)
            for j in range(n_):
                t_ = j / n_
                q = p0 + Vector((math.sin(t_ * 4 + k) * .05, math.cos(t_ * 3 + k) * .05, -L_ * t_))
                if 'oldvine' in argv:
                    if j % 2 == 0:
                        d = Vector((SR.uniform(-1, 1), SR.uniform(-1, 1), SR.uniform(-.6, .1)))
                        d, side, nrm = _frame(d)
                        Ll = SR.uniform(.025, .05) * (1 - .4 * t_)
                        vb.leaf(q, d, side, nrm, Ll, Ll * .55, shape=lambda u: math.sin(math.pi * min(1, u)) ** .7, fold=.2, droop=.3,
                                tint=(1, 1, 1), nu=4, nv=2)
                elif j % 2 == 0 or t_ < .35:   # 11/25 設定圖 V2、V6：常春藤心形葉 6–11 cm，上段一串串密、往下漸疏漸小
                    for _ in range(2 if t_ < .35 else 1):
                        d = Vector((SR.uniform(-1, 1), SR.uniform(-1, 1), SR.uniform(-.9, -.2)))   # 葉尖朝下垂
                        d, side, nrm = _frame(d)
                        Ll = SR.uniform(.06, .11) * (1 - .45 * t_)
                        tn_ = SR.uniform(.85, 1.15)
                        vb.leaf(q, d, side, nrm, Ll, Ll * .9,
                                shape=lambda u: (math.sin(math.pi * min(1, u) ** .7) ** .6) * (.75 + .25 * min(1, u * 4)),   # 心形：基部寬、尖頭
                                fold=.25, droop=.35, tint=(tn_, tn_, tn_), nu=5, nv=2)
            # 藤莖
            vb.leaf(p0, Vector((0, 0, -1)), Vector((1, 0, 0)), Vector((0, 1, 0)), L_, .004, shape=lambda u: 1.0, fold=0, tint=(.5, .45, .35), nu=6, nv=1)
            nvine += 1
        vb.build(f'Vines_{arch.name}', vmat)
    print('SMALL mush', nmu, 'moss', nmo, 'stones', nst, 'vines', nvine)

# 1.75 m 人形尺（祭壇前）
cyl((4, -6, gh(4, -6)), .22, .18, 1.75, mat('human', (.8, .1, .1))).hide_render = True

# ---------------- 燈光、霧、相機 ----------------
w = bpy.data.worlds.new('W')
sc.world = w
w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (.66, .70, .74, 1)   # 設定圖 v2：霧白、透
bg.inputs['Strength'].default_value = 1.6
if 'real' in argv and 'plainsky' not in argv:   # 11/24 六張比對：設定圖都是灰色多雲的天 → 鏡頭看到的天空加雲（只換鏡頭看到的，打光不變）
    _wt = w.node_tree; _wo = next(n for n in _wt.nodes if n.type == 'OUTPUT_WORLD')
    _cbg = _wt.nodes.new('ShaderNodeBackground'); _cbg.inputs['Strength'].default_value = 1.6
    _wtc = _wt.nodes.new('ShaderNodeTexCoord'); _wcn = _wt.nodes.new('ShaderNodeTexNoise')
    _wcn.inputs['Scale'].default_value = 2.2; _wcn.inputs['Detail'].default_value = 8; _wcn.inputs['Roughness'].default_value = .62
    _wmp = _wt.nodes.new('ShaderNodeMapping'); _wmp.inputs['Scale'].default_value = (1, 1, 3.5)   # 雲壓扁成一層層
    _wt.links.new(_wtc.outputs['Generated'], _wmp.inputs['Vector']); _wt.links.new(_wmp.outputs['Vector'], _wcn.inputs['Vector'])
    _wcr = _wt.nodes.new('ShaderNodeValToRGB'); _wcr.color_ramp.elements[0].position, _wcr.color_ramp.elements[1].position = .38, .68
    _wcr.color_ramp.elements[0].color = (.40, .43, .47, 1); _wcr.color_ramp.elements[1].color = (.74, .77, .80, 1)
    _wt.links.new(_wcn.outputs['Fac'], _wcr.inputs[0]); _wt.links.new(_wcr.outputs[0], _cbg.inputs['Color'])
    _wlp = _wt.nodes.new('ShaderNodeLightPath'); _wmx = _wt.nodes.new('ShaderNodeMixShader')
    _wt.links.new(_wlp.outputs['Is Camera Ray'], _wmx.inputs[0]); _wt.links.new(bg.outputs[0], _wmx.inputs[1]); _wt.links.new(_cbg.outputs[0], _wmx.inputs[2])
    _wt.links.new(_wmx.outputs[0], _wo.inputs['Surface'])
sun = bpy.data.lights.new('Sun', 'SUN')
sun.energy = 3.2
sun.angle = .2
so = bpy.data.objects.new('Sun', sun)
so.rotation_euler = (math.radians(50), 0, math.radians(150))
sc.collection.objects.link(so)
bpy.ops.mesh.primitive_cube_add(size=1, location=(200, 50, 40))
fog = bpy.context.object
fog.name = 'Fog'
fog.scale = (1200, 1200, 140)
if 'real' in argv:   # 林間低霧層：貼地一層較濃的霧（設定圖 V1 樹冠間的白霧）
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 10, 2))   # 底面壓到地下 15 m：地勢低的地方（V2）相機才不會在霧層外、看到一條霧的邊界線
    _lf = bpy.context.object
    _lf.name = 'LowFog'
    _lf.scale = (420, 420, 34)
    _lfm = bpy.data.materials.new('lowfog')
    _lfm.use_nodes = True
    _nt = _lfm.node_tree
    for _nd in list(_nt.nodes):
        if _nd.type == 'BSDF_PRINCIPLED':
            _nt.nodes.remove(_nd)
    _vs = _nt.nodes.new('ShaderNodeVolumePrincipled')
    _vs.inputs['Color'].default_value = (.97, .98, 1.0, 1)
    # 11/21 修：原本雜訊吃物件座標（方塊本地只有 -0.5..0.5）→ 整片均勻，沒有一縷縷的霧。改用世界座標、沿東西拉長成霧帶
    _nz = _nt.nodes.new('ShaderNodeTexNoise')
    _nz.inputs['Scale'].default_value = 1.0
    _nz.inputs['Detail'].default_value = 4
    _nz.inputs['Roughness'].default_value = .6
    _gp = _nt.nodes.new('ShaderNodeNewGeometry')
    _lmp = _nt.nodes.new('ShaderNodeMapping')
    _lmp.inputs['Scale'].default_value = (1 / 45, 1 / 22, 1 / 9)
    _nt.links.new(_gp.outputs['Position'], _lmp.inputs['Vector'])
    _nt.links.new(_lmp.outputs['Vector'], _nz.inputs['Vector'])
    _mr = _nt.nodes.new('ShaderNodeMapRange')
    _mr.inputs['From Min'].default_value, _mr.inputs['From Max'].default_value = .42, .66
    _mr.inputs['To Min'].default_value, _mr.inputs['To Max'].default_value = .0, .005   # 11/22 退回上一版的淡霧
    _nt.links.new(_nz.outputs['Fac'], _mr.inputs['Value'])
    # 高度：貼地到樹冠中段濃、往上漸淡
    _lsz = _nt.nodes.new('ShaderNodeSeparateXYZ'); _nt.links.new(_gp.outputs['Position'], _lsz.inputs[0])
    _lhz = _nt.nodes.new('ShaderNodeMapRange')
    _lhz.inputs['From Min'].default_value, _lhz.inputs['From Max'].default_value = 6, 19
    _lhz.inputs['To Min'].default_value, _lhz.inputs['To Max'].default_value = 1.0, 0.0
    _nt.links.new(_lsz.outputs['Z'], _lhz.inputs['Value'])
    # 空地裡不要（V3、V5 神木要清楚）：離 (-9,16) 22–40 m 漸漸出現
    _lvm = _nt.nodes.new('ShaderNodeVectorMath'); _lvm.operation = 'SUBTRACT'; _lvm.inputs[1].default_value = (-9, 16, 0)
    _nt.links.new(_gp.outputs['Position'], _lvm.inputs[0])
    _lsx = _nt.nodes.new('ShaderNodeSeparateXYZ'); _nt.links.new(_lvm.outputs[0], _lsx.inputs[0])
    _lcx = _nt.nodes.new('ShaderNodeCombineXYZ')
    _nt.links.new(_lsx.outputs['X'], _lcx.inputs['X']); _nt.links.new(_lsx.outputs['Y'], _lcx.inputs['Y'])
    _lln = _nt.nodes.new('ShaderNodeVectorMath'); _lln.operation = 'LENGTH'; _nt.links.new(_lcx.outputs[0], _lln.inputs[0])
    _lcl = _nt.nodes.new('ShaderNodeMapRange')
    _lcl.inputs['From Min'].default_value, _lcl.inputs['From Max'].default_value = 22, 40
    _nt.links.new(_lln.outputs['Value'], _lcl.inputs['Value'])
    _lm1 = _nt.nodes.new('ShaderNodeMath'); _lm1.operation = 'MULTIPLY'
    _nt.links.new(_mr.outputs[0], _lm1.inputs[0]); _nt.links.new(_lhz.outputs[0], _lm1.inputs[1])
    _lm2 = _nt.nodes.new('ShaderNodeMath'); _lm2.operation = 'MULTIPLY'
    _nt.links.new(_lm1.outputs[0], _lm2.inputs[0]); _nt.links.new(_lcl.outputs[0], _lm2.inputs[1])
    _nt.links.new(_lm2.outputs[0], _vs.inputs['Density'])
    _nt.links.new(_vs.outputs['Volume'], next(_nd for _nd in _nt.nodes if _nd.type == 'OUTPUT_MATERIAL').inputs['Volume'])
    _lf.data.materials.append(_lfm)
    fog.location.z, fog.scale.z = 4, 26
fm = bpy.data.materials.new('fog')
fm.use_nodes = True
nt = fm.node_tree
for nd in list(nt.nodes):
    if nd.type == 'BSDF_PRINCIPLED':
        nt.nodes.remove(nd)
vs = nt.nodes.new('ShaderNodeVolumePrincipled')
vs.inputs['Density'].default_value = .003 if 'real' in argv else .005
vs.inputs['Color'].default_value = (.95, .96, .98, 1)
if 'real' in argv:   # 空地裡霧薄（神木看得清楚、像設定圖），離開空地 15–45 m 漸漸變回林間的霧
    _g = nt.nodes.new('ShaderNodeNewGeometry')
    _vm = nt.nodes.new('ShaderNodeVectorMath'); _vm.operation = 'SUBTRACT'
    _vm.inputs[1].default_value = (-9, 16, 0)
    nt.links.new(_g.outputs['Position'], _vm.inputs[0])
    _sx = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(_vm.outputs[0], _sx.inputs[0])
    _cx = nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(_sx.outputs['X'], _cx.inputs['X']); nt.links.new(_sx.outputs['Y'], _cx.inputs['Y'])
    _ln = nt.nodes.new('ShaderNodeVectorMath'); _ln.operation = 'LENGTH'
    nt.links.new(_cx.outputs[0], _ln.inputs[0])
    _dm = nt.nodes.new('ShaderNodeMapRange')
    _dm.inputs['From Min'].default_value, _dm.inputs['From Max'].default_value = 15, 45
    _dm.inputs['To Min'].default_value, _dm.inputs['To Max'].default_value = .0008, .003
    nt.links.new(_ln.outputs['Value'], _dm.inputs['Value'])
    nt.links.new(_dm.outputs[0], vs.inputs['Density'])
nt.links.new(vs.outputs['Volume'], next(nd for nd in nt.nodes if nd.type == 'OUTPUT_MATERIAL').inputs['Volume'])
fog.data.materials.append(fm)

sc.render.engine = 'CYCLES'
try:
    bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'OPTIX'
    bpy.context.preferences.addons['cycles'].preferences.get_devices()
    for d in bpy.context.preferences.addons['cycles'].preferences.devices:
        d.use = True
    sc.cycles.device = 'GPU'
except Exception as e:
    print('GPU?', e)
sc.cycles.samples = 24 if QUICK else 64
sc.cycles.use_denoising = True
sc.cycles.volume_step_rate = 4
sc.view_settings.view_transform = 'AgX'
if 'real' in argv:   # 神木樹冠底下太暗：從南邊打一盞大面積的柔光，像霧裡反射回來的天光
    _fl = bpy.data.lights.new('TrunkFill', 'AREA')
    _fl.energy = 5000
    _fl.size = 50
    _fl.color = (1.0, .96, .9)
    _flo = bpy.data.objects.new('TrunkFill', _fl)
    sc.collection.objects.link(_flo)
    _flo.visible_volume_scatter = False   # 不要把霧照白
    _rc = bpy.data.collections.new('TrunkFillReceivers')   # 只照神木（光源連結），路面、近景不被照白
    for _o in _GTO:
        if _o.type == 'MESH':
            _rc.objects.link(_o)
    _flo.light_linking.receiver_collection = _rc
    _flo.location = (TREE[0] + 18, TREE[1] - 40, gh(*TREE) + 14)
    _flo.rotation_euler = (Vector((TREE[0], TREE[1], gh(*TREE) + 12)) - _flo.location).to_track_quat('-Z', 'Y').to_euler()
    # 11/24 影片「有來源的光」：樹冠縫漏下一道光柱打在祭壇上（順著太陽方向；柱內霧濃一點才看得到光束）
    if 'noshaft' not in argv:   # 11/24 第二版（z1nnz「光打得很假」）：不再是一根實心錐體 → 祭壇一帶一團一縷縷的薄霧，只被三道從樹冠縫射下的柔邊光照亮
        bpy.context.view_layer.update()
        _sd = (so.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
        _tgt = Vector((ALT[0], ALT[1], gh(*ALT) + .8))
        _SH = random.Random(5)
        for _k, (_dx, _dy, _ang, _en) in enumerate(((0, 0, 5.0, 220000), (1.8, -1.2, 2.6, 90000), (-1.5, 1.6, 3.4, 120000))):
            _t2 = _tgt + Vector((_dx, _dy, 0)); _src = _t2 - _sd * 26   # 光源在樹冠高度（約 17 m）往下打
            _sp = bpy.data.lights.new(f'AltarShaft{_k}', 'SPOT'); _sp.energy = _en; _sp.spot_size = math.radians(_ang); _sp.spot_blend = 1.0
            _sp.color = (1.0, .9, .74); _sp.shadow_soft_size = .15
            _spo = bpy.data.objects.new(f'AltarShaft{_k}', _sp); sc.collection.objects.link(_spo)
            _spo.location = _src; _spo.rotation_euler = (_t2 - _src).to_track_quat('-Z', 'Y').to_euler()
        # 局部薄霧：雜訊做出一縷縷、離地越高越淡；太陽和補光不照它（光源連結排除），只有光束照得到
        bpy.ops.mesh.primitive_cube_add(size=1, location=(ALT[0] + _sd.x * -8, ALT[1] + _sd.y * -8, gh(*ALT) + 11))
        _svo = bpy.context.object; _svo.name = 'ShaftHaze'; _svo.scale = (30, 30, 22)
        _svm = bpy.data.materials.new('ShaftHaze'); _svm.use_nodes = True; _st = _svm.node_tree
        for _nd in list(_st.nodes):
            if _nd.type == 'BSDF_PRINCIPLED':
                _st.nodes.remove(_nd)
        _sv = _st.nodes.new('ShaderNodeVolumePrincipled'); _sv.inputs['Color'].default_value = (1, .97, .92, 1); _sv.inputs['Anisotropy'].default_value = .6   # 往前散射：逆光看光束才亮
        _sg = _st.nodes.new('ShaderNodeNewGeometry')
        _snz = _st.nodes.new('ShaderNodeTexNoise'); _snz.inputs['Scale'].default_value = .18; _snz.inputs['Detail'].default_value = 5; _snz.inputs['Roughness'].default_value = .65
        _st.links.new(_sg.outputs['Position'], _snz.inputs['Vector'])
        _smr = _st.nodes.new('ShaderNodeMapRange'); _smr.inputs['From Min'].default_value, _smr.inputs['From Max'].default_value = .38, .72
        _smr.inputs['To Min'].default_value, _smr.inputs['To Max'].default_value = .0, .012
        _st.links.new(_snz.outputs['Fac'], _smr.inputs['Value'])
        _ssz = _st.nodes.new('ShaderNodeSeparateXYZ'); _st.links.new(_sg.outputs['Position'], _ssz.inputs[0])
        _shz = _st.nodes.new('ShaderNodeMapRange'); _shz.inputs['From Min'].default_value, _shz.inputs['From Max'].default_value = gh(*ALT) + 2, gh(*ALT) + 20
        _shz.inputs['To Min'].default_value, _shz.inputs['To Max'].default_value = 1.0, .15
        _st.links.new(_ssz.outputs['Z'], _shz.inputs['Value'])
        _smu = _st.nodes.new('ShaderNodeMath'); _smu.operation = 'MULTIPLY'
        _st.links.new(_smr.outputs[0], _smu.inputs[0]); _st.links.new(_shz.outputs[0], _smu.inputs[1])
        _st.links.new(_smu.outputs[0], _sv.inputs['Density'])
        _st.links.new(_sv.outputs['Volume'], next(_nd for _nd in _st.nodes if _nd.type == 'OUTPUT_MATERIAL').inputs['Volume'])
        _svo.data.materials.append(_svm)
        _hzc = bpy.data.collections.new('NoHaze'); _hzc.objects.link(_svo)
        for _lo in (so, _flo):
            _lo.light_linking.receiver_collection = _hzc
            _hzc.collection_objects[0].light_linking.link_state = 'EXCLUDE'
        print('SHAFT', [round(v, 2) for v in _sd])
if 'real' in argv:   # 陰天：天光為主、太陽弱（設定圖是散射光，不要逆光剪影）
    sc.view_settings.exposure = 1.0
    bg.inputs['Strength'].default_value = 3.4
    sun.energy = 1.2
    if 'flat' not in argv:   # 11/22 z1nnz 選了試做版（預設開）：設定圖受光面和陰影對比較強 → 太陽加強、天光減弱、AgX 中高對比
        bg.inputs['Strength'].default_value = 2.6
        sun.energy = 2.6
        for _lk in ('AgX - Medium High Contrast', 'Medium High Contrast'):
            try:
                sc.view_settings.look = _lk
                break
            except TypeError:
                pass
        print('LOOK', sc.view_settings.look)
sc.render.resolution_x, sc.render.resolution_y = 1536, 1024
SHOTS = {
    'V1': ((70, -105, 62), (-6, 18, 0), 24, '俯瞰全景（東南高處）'),
    'V2': ((2.5, -97, 1.7), (1.5, -60, 4.5), 22, '南入口（Josh 根拱）往北看'),
    'V3': ((8, -10.5, 1.9), (11, 22.5, 5.0), 16, '祭壇前（神木左、祭壇中右、坑右前）'),
    'V4': ((18.5, -10.5, 2.4), (13.5, -2.0, -.8), 24, '坑邊近景'),
    'V5': ((-6, 12, 2.2), (17, -21, 1.8), 18, '神木根旁回頭看（往南看祭壇與小路）'),
    'V6': ((1, 91, 1.7), (-5, 135, 5.0), 24, '北入口（核心組根拱）往外看'),
}
if ONLY and 'VM' in ONLY:   # 檢查用：神木根部近拍（看苔墊）
    SHOTS['VM'] = ((-10, 14, 2.2), (-22, 28, 1.0), 28, '神木根部近拍')
if ONLY and 'VL' in ONLY:   # 檢查用：林子裡那兩根 DR08 倒木（11/25 移出六張圖之後看不到）
    SHOTS['VL'] = ((7, 15, 1.9), (-.5, 22, .3), 24, 'DR08 倒木近拍')
for k, (loc, tgt, lens, _) in SHOTS.items():
    if ONLY and k not in ONLY:
        continue
    cd = bpy.data.cameras.new(k)
    cd.lens = lens
    cd.clip_end = 3000
    co = bpy.data.objects.new(k, cd)
    sc.collection.objects.link(co)
    if k != 'V1':      # 地面視角：高度以腳下地面為準
        loc = (loc[0], loc[1], gh(loc[0], loc[1]) + loc[2])
        tgt = (tgt[0], tgt[1], gh(tgt[0], tgt[1]) + tgt[2])
    co.location = loc
    co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = co
    sc.render.filepath = OUT + (f'D2_real_{k}.png' if 'real' in argv else f'D2_plan_{k}.png')
    if 'real' in argv:   # 11/22 V6 在框景樹冠底下太黑（設定圖是明亮霧天）→ 只有這一鏡曝光加一點，不動全場光
        sc.view_settings.exposure = 2.5 if k == 'V6' else 1.0
    bpy.ops.render.render(write_still=True)
    print('SHOT', k)

# 俯視總圖（正交，霧關掉）
if not ONLY or 'TOP' in ONLY:
    fog.hide_render = True
    cd = bpy.data.cameras.new('TOP')
    cd.type = 'ORTHO'
    cd.ortho_scale = 230
    cd.clip_end = 3000
    co = bpy.data.objects.new('TOP', cd)
    sc.collection.objects.link(co)
    co.location = (0, 0, 400)
    sc.camera = co
    sc.render.resolution_x = sc.render.resolution_y = 2048
    sc.render.filepath = OUT + 'D2_plan_TOP.png'
    bpy.ops.render.render(write_still=True)

json.dump({'TREE': TREE, 'ALT': ALT, 'PIT': PIT, 'ARCH_S': ARCH_S, 'ARCH_N': ARCH_N, 'PATH': PATH,
           'trees': TREES, 'rocks': ROCKS, 'shots': {k: [list(v[0]), list(v[1]), v[2], v[3]] for k, v in SHOTS.items()}},
          open(OUT + 'D2_plan.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('DONE', len(TREES))