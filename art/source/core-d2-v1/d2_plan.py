# 11/22 z1nnz 看了三個版本選 A：神木退回 v004 熔接版（v005/v006 改壞了，備份在 d2_plan_v006_backup.py）；保留水窪反光、拱門補苔
# D2 古樹區域 總平面＋六角度方塊模型（給 ChatGPT 照著畫設定圖用）
#   blender -b --factory-startup -P d2_plan.py -- [only=V1,V3] [quick]
#   座標：x 東、y 北，單位公尺；區塊 200×200（x,y ∈ -100..100）
import bpy, bmesh, sys, math, random, json
import numpy as np
from mathutils import Vector, noise

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
    pmr.inputs['From Min'].default_value, pmr.inputs['From Max'].default_value = .56, .60
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
    bmesh.ops.delete(_bm, geom=[f_ for f_ in _bm.faces if math.hypot(f_.calc_center_median().x - PIT[0], f_.calc_center_median().y - PIT[1]) < 5.3], context='FACES')
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
        verts = np.stack([XX.ravel(), YY.ravel(), Hf.ravel()], 1).astype(np.float32)
        ii = np.arange((nyf - 1) * (nxf - 1))
        r0 = ii // (nxf - 1); c0 = ii % (nxf - 1)
        v0 = r0 * nxf + c0
        quads = np.stack([v0, v0 + 1, v0 + nxf + 1, v0 + nxf], 1)
        cen = verts[quads].mean(1)
        keep = np.hypot(cen[:, 0] - PIT[0], cen[:, 1] - PIT[1]) >= 5.3
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
    for o in _d.objects:
        sc.collection.objects.link(o)
        o.location = (PIT[0], PIT[1], o.location.z + gh0(*PIT) + .012)
        if o.name == 'CO02_Pit':   # 坑外圈沒土的地方改用林床材質，交界才看不出接縫；坑內與鬆土保留坑自己的泥土材質
            o.data.materials.append(GM)
            _mk = o.data.color_attributes['Mask'].data
            for p_ in o.data.polygons:
                if max(_mk[v_].color[0] for v_ in p_.vertices) < .02:
                    p_.material_index = 1
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


def mossify(m, amount=1.0, lift=1.0, furrow=False, reach=0.0):   # reach：苔往側面爬多少（0 = 只長在朝上的面）
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


_GTO = append(S_ + ('GT01_out/GT01_GodTree_v004_fused.blend' if 'real' in argv else 'GT01_out/GT01_GodTree_v003.blend'),
              lambda nm: nm.endswith('_LOD0' if 'real' in argv else '_LOD1'), TREE, gh(*TREE) - .6)
if 'real' in argv:   # v004：樹幹 7 根管＋板根熔成一整塊（z1nnz 11/21「樹幹不連貫」）；熔接後沒有 UV → 樹皮改用盒投影掃描樹皮
    _BK = 'D:/chengtian/4-素材與快取/polyhaven-bark/'
    _bkm = bpy.data.materials.new('GT01_BarkFused')
    _bkm.use_nodes = True
    _bn = _bkm.node_tree
    _bb = next(x for x in _bn.nodes if x.type == 'BSDF_PRINCIPLED')
    _btc = _bn.nodes.new('ShaderNodeTexCoord')
    _bmp = _bn.nodes.new('ShaderNodeMapping')
    _bmp.inputs['Scale'].default_value = (1 / 1.1, 1 / 1.1, 1 / 2.0)   # 樹皮片沿樹幹拉長
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
    for _o in append(S_ + 'props_lib.blend', lambda nm: nm == 'AL02_Altar', ALT, gh(*ALT) - .12):
        _o.rotation_euler.z = .35
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
                        _gmr.inputs['From Min'].default_value, _gmr.inputs['From Max'].default_value = .47, .58
                        _gmr.inputs['To Max'].default_value = .85
                        _t.links.new(_gnz.outputs['Fac'], _gmr.inputs['Value'])
                        _gmx = _t.nodes.new('ShaderNodeMixRGB')
                        _gmx.blend_type = 'MULTIPLY'
                        _gmx.inputs[2].default_value = (2.3, 1.55, .38, 1)   # 金黃
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
                mossify(sl.material, 1.4 if o in _ARS else 1.6, 3.0, reach=.15)   # 11/22 設定圖 V2、V6 拱門側面也有一條條苔
    mossify(M_BARKR, .75, 1.6)

# ---------------- 神木的地上根：往祭壇、往外放射 ----------------
def root_ridge(a, b, r0, r1, m=M_ROOT, force=False):
    ax, ay = a; bx, by = b
    L = math.hypot(bx - ax, by - ay)
    N = max(3, int(L / 1.2))
    if REAL and not globals().get('_ROOTCOLS') is None:   # RT01 掃描樹皮長根（roots_lib.blend）
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
    for a, b, r in [((-1.5, 13), (5.5, -1), 1.1), ((-10, 11), (-5.5, -5), 1.2), ((-11.5, 9), (-15, -3), .9), ((-2, 16), (2, 6), .8)]:
        root_ridge(a, b, r, .4, force=True)

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
_CAMS = [(2.5, -97), (6, -13), (18.5, -10.5), (-6, 12), (1, 91)]
_CR = random.Random(31)
if 'real' in argv:   # 設定圖 V1：松樹比例高、樹冠之間看得到樹幹 → 外圍一部分圓冠樹換成傘頂松
    # 11/21 第二輪：設定圖 V1、V3 幾乎都是看得到樹幹的傘頂松，圓冠樹只零星幾棵 → 圓冠 75%、巨木 50% 換成松
    TREES = [(x, y, ('P' if (k == 'M' and math.hypot(x - CLEAR[0], y - CLEAR[1]) > CLEAR[2] + 8 and _CR.random() < .5) else k), s) for x, y, k, s in TREES]   # 11/22 他覺得上一版俯瞰較好 → 退回 50%
for x, y, k, s in TREES:
    if 'real' in argv and (any(math.hypot(x - cx, y - cy) < (16 if k == 'G' else 8) for cx, cy in _CAMS) or math.hypot(x - ARCH_N[0], y - ARCH_N[1]) < (24 if k == 'G' else 12)):
        continue   # 真樹的樹冠比方塊寬，相機旁邊的樹拿掉，免得鏡頭被擋
    KIND[k](x, y, s)
if 'real' in argv:   # V6 北入口兩側的近景大樹
    for (x_, y_, k_, s_) in [(-21, 99, 'B', 1.15), (11, 106, 'P', 1.05), (17, 113, 'P', .95), (-11, 120, 'B', 1.0), (6, 124, 'B', .9)]:
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
    HERO = [(5.5, -1.5, 1.8, 1), (12.5, -6.5, 1.3, 2), (21, -5.5, 1.3, 2), (-3.5, -8, 1.3, 1), (5, -89, 1.4, 2), (-5, 96, 1.3, 2)]
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
    GC = UG['clover'] + UG['rosette'] + UG['heart'][:1] + UG['grass'][:2]
    GW = [5] * len(UG['clover']) + [2] * len(UG['rosette']) + [2] + [1, 1]
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
            e.scale = (s_, s_, s_ * GR.uniform(.6, 1.0))
            e.rotation_euler.z = GR.uniform(0, 6.283)
            e.location = (x, y, gh(x, y) - .02)
            sc.collection.objects.link(e)
            ngc += 1
    print('GROUNDCOVER', ngc)
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
        for k in range(55):   # 設定圖 V2、V6 拱門垂藤很多
            p0 = SR.choice(cand)
            L_ = SR.uniform(.8, min(2.6, (p0.z - gh(p0.x, p0.y)) * .7))
            n_ = int(L_ / .06)
            for j in range(n_):
                t_ = j / n_
                q = p0 + Vector((math.sin(t_ * 4 + k) * .05, math.cos(t_ * 3 + k) * .05, -L_ * t_))
                if j % 2 == 0:
                    d = Vector((SR.uniform(-1, 1), SR.uniform(-1, 1), SR.uniform(-.6, .1)))
                    d, side, nrm = _frame(d)
                    Ll = SR.uniform(.025, .05) * (1 - .4 * t_)
                    vb.leaf(q, d, side, nrm, Ll, Ll * .55, shape=lambda u: math.sin(math.pi * min(1, u)) ** .7, fold=.2, droop=.3,
                            tint=(1, 1, 1), nu=4, nv=2)
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
if 'real' in argv:   # 陰天：天光為主、太陽弱（設定圖是散射光，不要逆光剪影）
    sc.view_settings.exposure = 1.0
    bg.inputs['Strength'].default_value = 3.4
    sun.energy = 1.2
sc.render.resolution_x, sc.render.resolution_y = 1536, 1024
SHOTS = {
    'V1': ((70, -105, 62), (-6, 18, 0), 24, '俯瞰全景（東南高處）'),
    'V2': ((2.5, -97, 1.7), (1.5, -60, 4.5), 22, '南入口（Josh 根拱）往北看'),
    'V3': ((4, -15, 1.9), (6, 18, 5.0), 16, '祭壇前（神木左、祭壇中右、坑右前）'),
    'V4': ((18.5, -10.5, 2.4), (13.5, -2.0, -.8), 24, '坑邊近景'),
    'V5': ((-6, 12, 2.2), (17, -21, 1.8), 18, '神木根旁回頭看（往南看祭壇與小路）'),
    'V6': ((1, 91, 1.7), (-5, 135, 5.0), 24, '北入口（核心組根拱）往外看'),
}
if ONLY and 'VM' in ONLY:   # 檢查用：神木根部近拍（看苔墊）
    SHOTS['VM'] = ((-10, 14, 2.2), (-22, 28, 1.0), 28, '神木根部近拍')
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