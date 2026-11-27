# GT01 神木：把 godtree_v3（種子 1，z1nnz 定版）的高模烘焙成遊戲用 LOD0–2 並匯出
#   先用 godtree_v3.py 產生 godtree_hi.blend（GT_STEP=0.1）與 godtree_lo0/1/2.blend（GT_AMP=0, nocrown）
#   blender -b --factory-startup -P gt_bake.py -- <out_dir> [tex_size]
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SRC = 'D:/chengtian/4-素材與快取/bark-sample/'
OUT = ARGS[0] if ARGS else SRC + 'GT01_out/'
TEX = int(ARGS[1]) if len(ARGS) > 1 else 4096
os.makedirs(OUT + 'Textures', exist_ok=True)
NAME = 'GT01_GodTree'


def log(*a):
    print('[GT01]', *a, flush=True)


bpy.ops.wm.open_mainfile(filepath=SRC + 'godtree_lo0.blend')
sc = bpy.context.scene


def bark_objs(prefix=''):
    return [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(prefix)
            and 'Mask' in o.data.color_attributes and o.name not in ('CrownWood', 'CrownLeaves')
            and not o.name.startswith('Small')]


def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    o.name = name
    o.data.name = name
    return o


def append_from(path, want):
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if want(n)]
    out = []
    for o in dst.objects:
        if o is not None:
            sc.collection.objects.link(o)
            out.append(o)
    return out


# ---------- 低模 LOD0 樹幹與根 ----------
lo0 = join(bark_objs(), f'{NAME}_Wood_LOD0')
bark_mat = lo0.data.materials[0]
for p in lo0.data.polygons:
    p.use_smooth = True
uv = lo0.data.uv_layers.new(name='BakeUV')
lo0.data.uv_layers.active = uv
bpy.ops.object.select_all(action='DESELECT')
lo0.select_set(True)
bpy.context.view_layer.objects.active = lo0
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.0015)
bpy.ops.uv.select_all(action='SELECT')
bpy.ops.uv.average_islands_scale()
bpy.ops.uv.pack_islands(rotate=True, margin=0.0008)
bpy.ops.object.mode_set(mode='OBJECT')
log('LOD0 wood tris', sum(len(p.vertices) - 2 for p in lo0.data.polygons))

# ---------- 高模（帶掃描凹凸）----------
hi_parts = append_from(SRC + 'godtree_hi.blend', lambda n: n not in ('CrownWood', 'CrownLeaves', 'Grid', 'Cube')
                       and not n.startswith('Cylinder') and not n.startswith('Camera') and not n.startswith('Sun'))
hi_parts = [o for o in hi_parts if o.type == 'MESH' and 'Mask' in o.data.color_attributes and not o.name.startswith('Small')]
hi = join(hi_parts, 'HI_Wood')
log('HI tris', len(hi.data.polygons) * 2)

# ---------- 烘焙 ----------
sc.render.engine = 'CYCLES'
try:
    pr = bpy.context.preferences.addons['cycles'].preferences
    pr.compute_device_type = 'OPTIX'
    pr.get_devices()
    for d in pr.devices:
        d.use = True
    sc.cycles.device = 'GPU'
except Exception as e:
    log('gpu', e)
sc.cycles.samples = 16
# 霧盒會擋住烘焙光線，先隱藏
for o in bpy.data.objects:
    if o.name.startswith('Cube') or o.name.startswith('Grid') or o.name.startswith('Cylinder'):
        o.hide_render = True

# 低模用一個只帶影像節點的材質接收烘焙
img = {}
for k, cs in (('BaseColor', 'sRGB'), ('Normal', 'Non-Color'), ('AO', 'Non-Color')):
    im = bpy.data.images.new(f'{NAME}_{k}', TEX, TEX, alpha=False, float_buffer=(k == 'Normal'))
    im.colorspace_settings.name = cs
    img[k] = im
recv = bpy.data.materials.new('GT01_BakeRecv')
recv.use_nodes = True
tn = recv.node_tree.nodes.new('ShaderNodeTexImage')
recv.node_tree.nodes.active = tn
lo0.data.materials.clear()
lo0.data.materials.append(recv)

bpy.ops.object.select_all(action='DESELECT')
hi.select_set(True)
lo0.select_set(True)
bpy.context.view_layer.objects.active = lo0
bk = sc.render.bake
bk.use_selected_to_active = True
bk.cage_extrusion = 0.7
bk.max_ray_distance = 1.6
bk.margin = 8
for k, typ in (('Normal', 'NORMAL'), ('BaseColor', 'DIFFUSE'), ('AO', 'AO')):
    tn.image = img[k]
    if typ == 'DIFFUSE':
        bk.use_pass_direct = False
        bk.use_pass_indirect = False
        bk.use_pass_color = True
    log('bake', k)
    bpy.ops.object.bake(type=typ, use_selected_to_active=True, cage_extrusion=0.7, max_ray_distance=1.6, margin=8)
    p = OUT + f'Textures/{NAME}_{k}.png'
    img[k].filepath_raw = p
    img[k].file_format = 'PNG'
    img[k].save()
    log('saved', p)

# UV 順序：BakeUV 當第一組（Unity UV0，烘焙圖用），原本的重複樹皮 UV 改名 TileUV 當第二組（細節貼圖用）
_tile = lo0.data.uv_layers['UV']
_t = lo0.data.uv_layers.new(name='TileUV')
_buf = np.empty(len(_tile.data) * 2, np.float32)
_tile.data.foreach_get('uv', _buf)
_t.data.foreach_set('uv', _buf)
lo0.data.uv_layers.remove(lo0.data.uv_layers['UV'])
bpy.data.objects.remove(hi, do_unlink=True)
for _im in img.values():
    _im.pack()
bpy.ops.wm.save_as_mainfile(filepath=OUT + 'stage1.blend')
log('STAGE1 saved')
if 'stage1' in ARGS:
    raise SystemExit(0)

# ---------- 遊戲用樹皮材質（烘焙圖）----------
gm = bpy.data.materials.new('GT01_Bark')
gm.use_nodes = True
N, L = gm.node_tree.nodes, gm.node_tree.links
bsdf = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
uvn = N.new('ShaderNodeUVMap')
uvn.uv_map = 'BakeUV'
tb = N.new('ShaderNodeTexImage')
tb.image = img['BaseColor']
tnn = N.new('ShaderNodeTexImage')
tnn.image = img['Normal']
ta = N.new('ShaderNodeTexImage')
ta.image = img['AO']
for t in (tb, tnn, ta):
    L.new(uvn.outputs[0], t.inputs[0])
mul = N.new('ShaderNodeMixRGB')
mul.blend_type = 'MULTIPLY'
mul.inputs[0].default_value = 0.45
L.new(tb.outputs[0], mul.inputs[1])
L.new(ta.outputs[0], mul.inputs[2])
L.new(mul.outputs[0], bsdf.inputs['Base Color'])
nm = N.new('ShaderNodeNormalMap')
nm.uv_map = 'BakeUV'
L.new(tnn.outputs[0], nm.inputs['Color'])
uvt = N.new('ShaderNodeUVMap')
uvt.uv_map = 'TileUV'
td = N.new('ShaderNodeTexImage')
td.image = bpy.data.images.load(SRC + '../polyhaven-bark/bark_brown_02_nor_gl_2k.png', check_existing=True)
td.image.colorspace_settings.name = 'Non-Color'
L.new(uvt.outputs[0], td.inputs[0])
nd = N.new('ShaderNodeNormalMap')
nd.uv_map = 'TileUV'
nd.inputs['Strength'].default_value = 1.2
L.new(td.outputs[0], nd.inputs['Color'])
# 合成：巨觀法線（烘焙）＋細節法線（重複掃描）→ 用凹凸疊加
bpd = N.new('ShaderNodeBump')
bpd.inputs['Strength'].default_value = .0
L.new(nm.outputs[0], bsdf.inputs['Normal'])
DETAIL = (td, nd)
bsdf.inputs['Roughness'].default_value = .88
lo0.data.materials.clear()
lo0.data.materials.append(gm)

# ---------- LOD1、LOD2 樹幹：從各自檔案取，UV 從 LOD0 轉過來 ----------
woods = {0: lo0}
for lv in (1, 2):
    parts = append_from(SRC + f'godtree_lo{lv}.blend', lambda n: n not in ('CrownWood', 'CrownLeaves', 'Grid', 'Cube')
                        and not n.startswith('Cylinder') and not n.startswith('Camera') and not n.startswith('Sun'))
    parts = [o for o in parts if o.type == 'MESH' and 'Mask' in o.data.color_attributes and not o.name.startswith('Small')]
    w = join(parts, f'{NAME}_Wood_LOD{lv}')
    for p in w.data.polygons:
        p.use_smooth = True
    w.data.uv_layers.new(name='BakeUV')
    w.data.uv_layers.active = w.data.uv_layers['BakeUV']
    mod = w.modifiers.new('uv', 'DATA_TRANSFER')
    mod.object = lo0
    mod.use_loop_data = True
    mod.data_types_loops = {'UV'}
    mod.loop_mapping = 'POLYINTERP_NEAREST'
    bpy.context.view_layer.objects.active = w
    bpy.ops.object.select_all(action='DESELECT')
    w.select_set(True)
    bpy.ops.object.modifier_apply(modifier='uv')
    w.data.materials.clear()
    w.data.materials.append(gm)
    woods[lv] = w
    log(f'LOD{lv} wood tris', sum(len(p.vertices) - 2 for p in w.data.polygons))

# ---------- 葉子：依遠近抽稀，留下的葉子放大補覆蓋 ----------
leaf_src = append_from(SRC + 'godtree_hi.blend', lambda n: n == 'CrownLeaves')[0]
me = leaf_src.data
nv = len(me.vertices)
co = np.empty(nv * 3, np.float32)
me.vertices.foreach_get('co', co)
co = co.reshape(-1, 5, 3)                       # 每片葉 5 個頂點：四點輪廓＋抬高的中脈
col_attr = me.color_attributes['LeafColour']
cc = np.empty(nv * 4, np.float32)
col_attr.data.foreach_get('color', cc)
cc = cc.reshape(-1, 5, 4)
nleaf = co.shape[0]
log('leaves in', nleaf)
leaf_mat = leaf_src.data.materials[0] if leaf_src.data.materials else None
rng = np.random.default_rng(1)
order = rng.permutation(nleaf)


def leaf_lod(lv, keep, scale, five):
    idx = np.sort(order[:max(1, nleaf // keep)])
    v = co[idx].copy()
    c = v[:, :4, :].mean(axis=1, keepdims=True)
    v = c + (v - c) * scale
    col = cc[idx]
    n = len(idx)
    if five:
        verts = v.reshape(-1, 3)
        base = (np.arange(n) * 5)[:, None]
        faces = np.concatenate([np.stack([base[:, 0] + 4, base[:, 0] + s, base[:, 0] + (s + 1) % 4], 1) for s in range(4)])
        vcol = col.reshape(-1, 4)
    else:
        verts = v[:, :4, :].reshape(-1, 3)
        base = (np.arange(n) * 4)
        faces = np.stack([base, base + 1, base + 2, base + 3], 1)
        vcol = col[:, :4, :].reshape(-1, 4)
    m = bpy.data.meshes.new(f'{NAME}_Leaves_LOD{lv}')
    m.vertices.add(len(verts))
    m.vertices.foreach_set('co', verts.ravel())
    nl = faces.shape[1]
    m.loops.add(len(faces) * nl)
    m.loops.foreach_set('vertex_index', faces.ravel().astype(np.int32))
    m.polygons.add(len(faces))
    m.polygons.foreach_set('loop_start', (np.arange(len(faces)) * nl).astype(np.int32))
    m.polygons.foreach_set('loop_total', np.full(len(faces), nl, np.int32))
    m.update()
    ca = m.color_attributes.new('LeafColour', 'FLOAT_COLOR', 'POINT')
    ca.data.foreach_set('color', vcol.ravel())
    m.uv_layers.new(name='UVMap')
    o = bpy.data.objects.new(f'{NAME}_Leaves_LOD{lv}', m)
    sc.collection.objects.link(o)
    if leaf_mat:
        m.materials.append(leaf_mat)
    log(f'LOD{lv} leaves', n, 'faces', len(faces))
    return o


leaves = {0: leaf_lod(0, 12, 2.4, False), 1: leaf_lod(1, 45, 4.4, False), 2: leaf_lod(2, 200, 8.8, False)}
bpy.data.objects.remove(leaf_src, do_unlink=True)

# ---------- 細枝：遊戲版只留看得到的枝（godtree_v3 'gamecrown' 產生）----------
tmat = bpy.data.materials.new('GT01_Twig')
tmat.use_nodes = True
next(n for n in tmat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.075, .062, .05, 1)
twigs = {}
for lv in (0, 1):
    t = append_from(SRC + 'godtree_hi.blend', lambda n, lv=lv: n == f'CrownWoodG{lv}')[0]
    t.name = f'{NAME}_Twigs_LOD{lv}'
    t.data.materials.clear()
    t.data.materials.append(tmat)
    twigs[lv] = t
    log(f'LOD{lv} twig tris', sum(len(p.vertices) - 2 for p in t.data.polygons))

# ---------- 碰撞：樹幹與板根的簡化殼 ----------
colo = woods[2].copy()
colo.data = woods[2].data.copy()
colo.name = f'UCX_{NAME}'
sc.collection.objects.link(colo)
d = colo.modifiers.new('dec', 'DECIMATE')
d.ratio = .2
bpy.context.view_layer.objects.active = colo
bpy.ops.object.select_all(action='DESELECT')
colo.select_set(True)
bpy.ops.object.modifier_apply(modifier='dec')
colo.data.materials.clear()
log('collision tris', len(colo.data.polygons))

# ---------- 統計 ----------
def tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


stats = {}
for lv in (0, 1, 2):
    s = tris(woods[lv]) + tris(leaves[lv]) + (tris(twigs[lv]) if lv in twigs else 0)
    stats[f'LOD{lv}'] = {'wood': tris(woods[lv]), 'leaves': tris(leaves[lv]), 'twigs': tris(twigs[lv]) if lv in twigs else 0, 'total': s}
log('STATS', stats)

# ---------- 清場、匯出 ----------
keep = set([woods[0], woods[1], woods[2], leaves[0], leaves[1], leaves[2], twigs[0], twigs[1], colo])
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o not in keep:
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT + f'{NAME}_v003.blend')
bpy.ops.object.select_all(action='DESELECT')
for o in keep:
    o.select_set(True)
bpy.ops.export_scene.fbx(filepath=OUT + f'{NAME}_v003.fbx', use_selection=True, apply_unit_scale=True,
                         axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE', path_mode='COPY', embed_textures=False)
try:
    bpy.ops.export_scene.gltf(filepath=OUT + f'{NAME}_v003.glb', use_selection=True, export_format='GLB',
                              )
except Exception as e:
    log('gltf', e)
import json
json.dump({'id': 'GT01', 'name': '神木', 'version': 'v003', 'source': 'art/source/core-d2-v1/godtree/godtree_v3.py (GT_NSEED=1)',
           'bake': {'texture_px': TEX, 'maps': ['BaseColor', 'Normal (OpenGL)', 'AO'], 'uv': 'BakeUV'},
           'triangles': stats, 'collision': f'UCX_{NAME}', 'origin': '樹幹底部中心，z=0 在地面',
           'size_m': {'height': round(max(v.co.z for v in leaves[0].data.vertices), 1)}},
          open(OUT + 'model_info.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
log('DONE')
