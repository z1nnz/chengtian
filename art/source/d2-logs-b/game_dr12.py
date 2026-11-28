# DR12 地上的大片剝落樹皮（BarkL，樣品）的遊戲模型：直接建遊戲網格（不烘焙），照 game_dr09.py 的作法沿用 D2 倒木那套分層材質。
#   - 形狀：build_dr12.py 的 bark_sheet()（前段平、兩側微翹、後段往上捲成浪頭；撕斷端一排尖齒；外皮板塊推在幾何上）。
#     各級 LOD 用同一個參數重建，只換取樣密度（不是 decimate）：(沿長, 橫向) LOD0 0.32×0.80、LOD1 0.235×0.52、LOD2 0.13×0.31；碰撞殼 0.10。
#   - 材質：M_DR09_Layered（Unity：YunJing/D2LayeredWood）。UV0 = 公尺（u 沿樹皮長向 = 原本的樹幹方向，v 橫向），
#     頂點色 RGBA = 苔、褐腐、撕裂纖維、內壁的權重，UV1 = (土, AO)。
#       外皮（捲起的背面、平段底面）= 樹皮層（DR09 調色的深灰褐）＋苔（外皮朝上處的斑塊）；
#       內皮（朝上的大片）= 纖維層（DR09 淺奶油色新斷木）＋受潮深色斑（褐腐層淡淡疊上）；
#       厚度斷面 = 外側一半褐腐（紅褐中層）、內側纖維。貼地的地方疊一點土。
#   - 尺寸：工作包 DR12 0.3–1.5 m；BarkL 長約 1.48 m、寬 0.81 m、捲起高 0.66 m。原點在底部中心，z = 0 是地面（略陷 1 cm）。
# 用法（背景，不要加 --factory-startup）：blender -b --python art/source/d2-logs-b/game_dr12.py -- BarkL
import bpy, bmesh, sys, os, json, math, time, traceback
import numpy as np
from mathutils import Vector, Matrix, noise
from mathutils.bvhtree import BVHTree

ROOT = 'D:/yun-jing-d2-logs'
HERE = ROOT + '/art/source/d2-logs-b'
ROOTS = ROOT + '/art/source/d2-roots-b'
VER = 'v001'
NAMES = {'BarkL': 'DR12_BarkSheet_L'}
SCALE = {'BarkL': .74}                       # 形狀照參考圖比例做（build_dr12 的 scale .78 → 1.56 m），縮到工作包上限 1.5 m 以內
RES = {0: (.32, .80), 1: (.235, .52), 2: (.13, .31), 'col': (.10, .10)}      # (沿長, 橫向)：橫向密一點，前端尖齒才尖
UVK = 1.25                                   # UV0 每公尺放大：樹皮片是從大樹幹剝下來的，鱗片比 DR08 樹幹（1 倍）略小


def _exec(path, name):
    ns = {'__name__': name, '__file__': path}
    exec(compile(open(path, encoding='utf-8').read(), path, 'exec'), ns)
    return ns


B12 = _exec(HERE + '/build_dr12.py', 'build_dr12_lib')
G9 = _exec(HERE + '/game_dr09.py', 'game_dr09_lib')


def sm(x, e0, e1):
    t = np.clip((np.asarray(x, float) - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def _tri(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def sheet(var, res, name):
    V = dict(B12['VARIANTS'][var])
    c = B12['_coll']('DR12_Work')
    o = B12['bark_sheet'](V, c, name, res)
    o.data.transform(Matrix.Scale(SCALE[var], 4))
    for cc in list(o.users_collection):
        cc.objects.unlink(o)
    bpy.context.scene.collection.objects.link(o)
    return o


def to_layered(o, lv):
    """bark_sheet 的三個材質槽（0 外皮、1 內皮、2 厚度斷面）、Mask（R = 苔）、Depth（1 內皮側、0 外皮側）→ 分層材質的權重。"""
    me = o.data
    n = len(me.loops)
    mi = np.empty(len(me.polygons), np.int32)
    me.polygons.foreach_get('material_index', mi)
    lt = np.empty(len(me.polygons), np.int32)
    me.polygons.foreach_get('loop_total', lt)
    lmat = np.repeat(mi, lt)
    vi = np.empty(n, np.int32)
    me.loops.foreach_get('vertex_index', vi)
    dep = np.empty(len(me.vertices), np.float32)
    me.attributes['Depth'].data.foreach_get('value', dep)
    mask = np.empty(n * 4, np.float32)
    me.color_attributes['Mask'].data.foreach_get('color', mask)
    mask = mask.reshape(-1, 4)
    par = np.empty(n * 2, np.float32)
    me.uv_layers['Param'].data.foreach_get('uv', par)
    par = par.reshape(-1, 2) * SCALE[o['var']]              # (y 橫向, s 沿長)，公尺
    co = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    p = co[vi]
    nz = np.array([noise.noise(Vector(q * 3.0 + 7.1)) for q in p])
    nz2 = np.array([noise.noise(Vector(q * 7.5 + 2.3)) for q in p])
    W = np.zeros((n, 5))
    outer, inner, edge = lmat == 0, lmat == 1, lmat == 2
    # 外皮：苔（build 時算好的斑塊：外皮朝上、成片）
    W[outer, 0] = np.clip(mask[outer, 0] * 1.1, 0, 1)
    # 內皮：淺色纖維；受潮深色斑、捲起內側陰濕處淡淡疊褐腐
    W[inner, 2] = 1.0
    W[inner, 1] = .42 * sm(nz[inner] + .4 * nz2[inner], .12, .45)
    # 厚度斷面：外半邊紅褐中層（褐腐）、內半邊纖維；外皮那一圈仍是樹皮
    d = dep[vi]
    W[edge & (d > .5), 2] = 1.0
    W[edge & (d <= .5), 1] = .85
    # 貼地處：土
    W[:, 4] = sm(.035 - p[:, 2], 0, .035) * .55 * (1 - W[:, 0])
    s = W[:, :4].sum(1, keepdims=True)
    W[:, :4] = np.where(s > 1, W[:, :4] / np.maximum(s, 1e-6), W[:, :4])
    ao = G9['vertex_ao'](o, dist=.22) if lv < 2 else np.ones(len(me.vertices))
    ao = ao * (.70 + .30 * sm(co[:, 2], -.01, .10))
    ca = me.color_attributes.new('Layers', 'FLOAT_COLOR', 'CORNER')
    ca.data.foreach_set('color', W[:, :4].astype(np.float32).ravel())
    me.color_attributes.active_color = ca
    uv = np.stack([par[:, 1], par[:, 0]], -1)            # (s 沿長, y 橫向)
    # 厚度斷面：上下兩圈的 (s, y) 一樣，直接用會在斷面上拉成直條紋。每個斷面面照它沿哪個方向走：
    # 兩側（沿 s）→ u = s；兩頭（沿 y）→ u = y（另移開一段）；v = 從內皮往外皮的深度（公尺），纖維、紅褐層、外皮在斷面上是一層層橫帶。
    cut_t = .09
    ls = np.concatenate([[0], np.cumsum(lt)[:-1]])
    for fi in np.nonzero(mi == 2)[0]:
        a, k = ls[fi], lt[fi]
        q = uv[a:a + k]
        side = np.ptp(q[:, 0]) >= np.ptp(q[:, 1])
        along = q[:, 0] if side else q[:, 1] + 3.0
        uv[a:a + k, 0] = along
        uv[a:a + k, 1] = 5.0 + (1 - d[a:a + k]) * cut_t
    uv0 = me.uv_layers.new(name='UVMap')
    uv0.data.foreach_set('uv', (uv * UVK).astype(np.float32).ravel())
    me.uv_layers.new(name='Extra').data.foreach_set('uv', np.stack([W[:, 4], ao[vi]], -1).astype(np.float32).ravel())
    for nm in ('UV', 'Param'):
        me.uv_layers.remove(me.uv_layers[nm])
    me.color_attributes.remove(me.color_attributes['Mask'])
    me.uv_layers.active_index = 0
    for l in me.uv_layers:
        l.active_render = l.name == 'UVMap'
    me.materials.clear()
    me.materials.append(G9['layer_mat']())
    me.polygons.foreach_set('material_index', np.zeros(len(me.polygons), np.int32))
    G9['_triangulate'](o)
    return dict(moss_mean_outer=round(float(W[outer, 0].mean()), 3), fibre_share=round(float(inner.mean()), 3))


def run(var='BarkL'):
    t0 = time.time()
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    asset = NAMES[var]
    lods, info = {}, {}
    for lv in (0, 1, 2):
        o = sheet(var, RES[lv], f'{asset}_LOD{lv}')
        o['var'] = var
        lods[lv] = o
    col = sheet(var, RES['col'], f'{asset}_Collision')
    # 同一個平移放到地上：LOD0 最低點略低於地面 1 cm、XY 外框中心到原点（dr_pivot 再精確對一次）
    vs = np.array([v.co[:] for v in lods[0].data.vertices])
    lo, hi = vs.min(0), vs.max(0)
    off = Matrix.Translation(Vector((-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2] - .01)))
    for o in list(lods.values()) + [col]:
        o.data.transform(off)
    for lv, o in lods.items():
        info[lv] = to_layered(o, lv)
        print('LOD', lv, _tri(o), round(time.time() - t0), 's')
    col.data.materials.clear()
    G9['_triangulate'](col)
    col.hide_render = True
    col.display_type = 'WIRE'
    root = bpy.data.objects.new(asset, None)
    bpy.context.scene.collection.objects.link(root)
    for o in list(lods.values()) + [col]:
        o.data.name = o.name
        o.parent = root
    piv = _exec(ROOTS + '/dr_pivot.py', 'dr_pivot')
    piv['to_bottom_centre'](root, lods[0])
    exp = f'{ROOT}/art/exports/d2-logs-b/{asset}'
    os.makedirs(exp, exist_ok=True)
    allm = list(lods.values()) + [col]
    col.hide_render = False
    G9['_select'](allm + [root], root)
    bpy.ops.export_scene.fbx(filepath=f'{exp}/{asset}_{VER}.fbx', use_selection=True, object_types={'MESH', 'EMPTY'},
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', bake_space_transform=True,
                             axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE', use_mesh_modifiers=True, colors_type='LINEAR',
                             add_leaf_bones=False, bake_anim=False, path_mode='STRIP', embed_textures=False)
    try:
        G9['_select']([lods[0], root], root)
        bpy.ops.export_scene.gltf(filepath=f'{exp}/{asset}_{VER}.glb', use_selection=True, export_format='GLB', export_yup=True)
    except Exception as e:
        print('glb', e)
    col.hide_render = True
    tris = {f'LOD{lv}': _tri(o) for lv, o in lods.items()}
    tris['collision'] = _tri(col)
    bpy.context.scene['dr12_game'] = json.dumps(dict(variant=var, tris=tris, layers=info, res=RES, scale=SCALE[var], uv_per_m=UVK))
    print('TRIS', json.dumps(tris))
    os.makedirs(HERE + '/blend', exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_{VER}.blend', copy=True)
    print('GAME_DONE', asset, round(time.time() - t0), 's')


if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    try:
        run(a[0] if a else 'BarkL')
    except Exception:
        traceback.print_exc()
        sys.exit(1)
