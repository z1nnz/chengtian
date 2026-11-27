# 11/26 D2 → Unity：由 d2_plan.py 在建完場景後 exec（共用全域變數 bpy, sc, argv, SHOTS 尚未建…）
#   stats  ：盤點
#   export ：匯出 FBX（顏色烘進頂點色）＋ D2_layout.json（重複物件的擺放、鏡頭、光、霧）
#   旗標：exp_only=<名稱片段,...> 只匯出名稱含這些字的東西（試跑用）；exp_out=<資料夾>
import collections, os, time
from mathutils import Matrix, Quaternion, Euler

bpy.context.view_layer.update()
_dg = bpy.context.evaluated_depsgraph_get()


def _tri_count(o):
    ev = o.evaluated_get(_dg)
    try:
        m = ev.to_mesh(); t = sum(len(p.vertices) - 2 for p in m.polygons); ev.to_mesh_clear(); return t
    except Exception:
        return 0


if 'stats' in argv:
    _rows = collections.Counter(); _tris = {}; _inst = collections.Counter()
    for o in sc.objects:
        if o.hide_render:
            continue
        if o.instance_type == 'COLLECTION' and o.instance_collection:
            _inst[o.instance_collection.name] += 1
        elif o.type in ('MESH', 'CURVE'):
            _rows[o.data.name] += 1
            _tris.setdefault(o.data.name, _tri_count(o))
    print('STATS unique meshes', len(_rows), 'tris', sum(_tris.values()))
    for k, n in _inst.most_common():
        c = bpy.data.collections[k]
        print('STATS coll', k, n, 'tris', sum(_tri_count(x) for x in c.all_objects if x.type in ('MESH', 'CURVE')))
    raise SystemExit(0)

# ---------------------------------------------------------------- export
OUT = next((a[8:] for a in argv if a.startswith('exp_out=')), 'D:/chengtian/1-進行中/unity63-main/apps/game/Assets/YunJing/Models/D2')
ONLY_ = next((a[9:].split(',') for a in argv if a.startswith('exp_only=')), None)
os.makedirs(OUT, exist_ok=True)
CELL = 50.0
MAXTRI = 400000                       # 單一獨立物件超過就減面（神木樹幹 990 萬 → 40 萬；之後再用法線貼圖補細節）
SKIP = ('PathLitter', 'LowFog', 'Fog', 'human')   # 路面落葉 530 萬面：第一版不搬，之後改用貼花
t0 = time.time()

# Blender（右手、Z 上）→ Unity（左手、Y 上）。FBX 匯出用預設軸向、Unity 端 bakeAxisConversion=true：
# 頂點 (x, y, z) 在 Unity 變成 (-x, z, -y)。擺放用同一個換算：U = C·M·C⁻¹
C = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))   # 11/26 實測：Unity 匯入後 Blender (x,y,z) → Unity (x,z,y)
Ci = C.inverted()


def to_unity(mw):
    u = C @ mw @ Ci
    loc, rot, scl = u.decompose()
    # C 是鏡射（det = -1），C·R·C⁻¹ 已經是 Unity 座標裡的純旋轉矩陣，直接取四元數（Unity 順序 x,y,z,w）
    return [round(loc.x, 4), round(loc.y, 4), round(loc.z, 4)], [round(rot.x, 6), round(rot.y, 6), round(rot.z, 6), round(rot.w, 6)], [round(scl.x, 4), round(scl.y, 4), round(scl.z, 4)]


def bake_vcol(o):
    """把材質的底色烘進頂點色 'Col'（不含光影）。"""
    me = o.data
    if not me.color_attributes.get('Col'):
        me.color_attributes.new('Col', 'BYTE_COLOR', 'CORNER')
    me.color_attributes.active_color = me.color_attributes['Col']
    try:
        me.color_attributes.render_color_index = me.color_attributes.active_color_index   # FBX 匯出用的是「算圖用」那組顏色
    except Exception:
        pass
    for ob in bpy.context.selected_objects:
        ob.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    sc.render.engine = 'CYCLES'; sc.cycles.samples = 1
    try:
        bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, target='VERTEX_COLORS')
    except Exception as e:
        print('BAKE fail', o.name, e)


def realize(objs, name, world=True, base_inv=None):
    """把一組物件（含修改器、曲線）轉成一個合併網格；world=True 用世界座標，否則用 base_inv 換到原型空間。"""
    bm_all = bmesh.new()
    mats = []
    for o in objs:
        ev = o.evaluated_get(_dg)
        try:
            m = ev.to_mesh()
        except Exception:
            continue
        if not m or not m.polygons:
            ev.to_mesh_clear(); continue
        mw = o.matrix_world if world else (base_inv @ o.matrix_world)
        tmp = bpy.data.meshes.new('tmp'); tmp_bm = bmesh.new(); tmp_bm.from_mesh(m); tmp_bm.transform(mw)
        # 材質索引對到合併後的清單
        off = len(mats)
        for s in o.material_slots:
            mats.append(s.material)
        for f in tmp_bm.faces:
            f.material_index += off
        tmp_bm.to_mesh(tmp); tmp_bm.free(); ev.to_mesh_clear()
        bm_all.from_mesh(tmp); bpy.data.meshes.remove(tmp)
    me = bpy.data.meshes.new(name); bm_all.to_mesh(me); bm_all.free()
    for m_ in mats:
        me.materials.append(m_)
    ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob)
    return ob


def export_fbx(ob, path):
    for x in bpy.context.selected_objects:
        x.select_set(False)
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'}, mesh_smooth_type='FACE',
                             use_mesh_modifiers=False, add_leaf_bones=False, bake_anim=False, path_mode='STRIP',
                             colors_type='SRGB', apply_scale_options='FBX_SCALE_ALL')


def reduce_to(ob, target):
    """減到約 target 面：先用 Decimate；減不下去（很多分開的小葉片）就隨機拿掉一部分小島，大的島（樹幹、粗枝）一定留著。"""
    tri = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    if tri <= target:
        return
    dm = ob.modifiers.new('dec', 'DECIMATE'); dm.ratio = max(target / tri, .005)
    bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier='dec')
    tri = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    if tri <= target * 1.3:
        return
    bm_ = bmesh.new(); bm_.from_mesh(ob.data); bm_.faces.ensure_lookup_table()
    seen_, isl_ = set(), []
    for f0 in bm_.faces:
        if f0.index in seen_:
            continue
        st_, cur_ = [f0], []
        while st_:
            f = st_.pop()
            if f.index in seen_:
                continue
            seen_.add(f.index); cur_.append(f)
            for e in f.edges:
                st_ += [g for g in e.link_faces if g.index not in seen_]
        isl_.append(cur_)
    isl_.sort(key=lambda fs: -sum(f.calc_area() for f in fs))
    keep_tri = 0; kill = []
    rr = random.Random(5)
    big_n = max(1, len(isl_) // 50)          # 最大的 2%（樹幹、主枝）一定留
    rest_tri = sum(sum(len(f.verts) - 2 for f in fs) for fs in isl_[big_n:])
    big_tri = tri - rest_tri
    keep_p = max(0.0, min(1.0, (target - big_tri) / max(rest_tri, 1)))
    for i, fs in enumerate(isl_):
        if i >= big_n and rr.random() > keep_p:
            kill += fs
    bmesh.ops.delete(bm_, geom=kill, context='FACES')
    bm_.to_mesh(ob.data); bm_.free()


def want(name):
    return ONLY_ is None or any(k in name for k in ONLY_)


layout = {'prototypes': [], 'instances': [], 'cells': [], 'cameras': [], 'notes': []}   # JsonUtility 讀得懂的形狀：全部是物件陣列

# 1) 重複擺放的物件：每種集合匯出一個原型 FBX，位置寫進 JSON
_inst = collections.defaultdict(list)
for o in list(sc.objects):
    if not o.hide_render and o.instance_type == 'COLLECTION' and o.instance_collection:
        _inst[o.instance_collection.name].append(o)
for cname, users in _inst.items():
    if not want(cname):
        continue
    col = bpy.data.collections[cname]
    objs = [x for x in col.all_objects if x.type in ('MESH', 'CURVE')]
    if not objs:
        continue
    off = Matrix.Translation(-col.instance_offset)
    ob = realize(objs, 'D2P_' + cname, world=False, base_inv=off)
    tri = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    reduce_to(ob, MAXTRI)
    bake_vcol(ob)
    fn = f'D2P_{cname}.fbx'
    # 原型在集合原點、不能帶自己的變換
    export_fbx(ob, os.path.join(OUT, fn))
    _pt = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    _lods = [fn]
    if _pt > 3000:   # 遠中近分級：LOD1 約 12%、LOD2 約 3%（近處照原模型，不犧牲畫質）
        for _li, _r in ((1, .12), (2, .03)):
            lo = ob.copy(); lo.data = ob.data.copy(); sc.collection.objects.link(lo)
            reduce_to(lo, max(int(_pt * _r), 300))
            _fl = f'D2P_{cname}_LOD{_li}.fbx'; export_fbx(lo, os.path.join(OUT, _fl)); _lods.append(_fl)
            bpy.data.objects.remove(lo)
    layout['prototypes'].append({'name': cname, 'fbx': fn, 'lods': _lods, 'tris': _pt, 'count': len(users)})
    for u in users:
        p, r, s_ = to_unity(u.matrix_world)
        layout['instances'].append({'proto': cname, 'pos': p, 'rot': r, 'scl': s_})
    bpy.data.objects.remove(ob)
    print('EXPORT proto', cname, len(users), 'x', _pt, f'{time.time() - t0:.0f}s')

# 2) 獨立物件：每 50 m 一格合併
_cells = collections.defaultdict(list)
for o in list(sc.objects):
    if o.hide_render or o.instance_type == 'COLLECTION' or o.type not in ('MESH', 'CURVE') or o.name.startswith(('D2P_', 'D2C_')):
        continue
    if any(o.name.startswith(k) for k in SKIP) or not want(o.name):
        continue
    if any(md.type == 'NODES' for md in getattr(o, 'modifiers', [])) and o.name.startswith('Fog'):
        continue
    if o.type == 'MESH' and o.data.materials and all(m and m.node_tree and any(n.type == 'OUTPUT_MATERIAL' and n.inputs['Volume'].links and not n.inputs['Surface'].links for n in m.node_tree.nodes) for m in o.data.materials):
        continue   # 純體積（霧）不搬
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    cx = sum(v.x for v in bb) / 8; cy = sum(v.y for v in bb) / 8
    _cells[(math.floor(cx / CELL), math.floor(cy / CELL))].append(o)
big = []
for key, objs in sorted(_cells.items()):
    small = []
    for o in objs:
        t = _tri_count(o)
        if t > MAXTRI:
            big.append((o, t))
        else:
            small.append(o)
    if small:
        name = f'D2C_{key[0]}_{key[1]}'
        ob = realize(small, name, world=True)
        bake_vcol(ob)
        export_fbx(ob, os.path.join(OUT, name + '.fbx'))
        layout['cells'].append({'fbx': name + '.fbx', 'tris': sum(len(p.vertices) - 2 for p in ob.data.polygons), 'objects': len(small)})
        bpy.data.objects.remove(ob)
        print('EXPORT cell', name, len(small), f'{time.time() - t0:.0f}s')
for o, t in big:
    name = 'D2B_' + ''.join(ch if ch.isalnum() or ch in '_-' else '_' for ch in o.name)
    ob = realize([o], name, world=True)
    reduce_to(ob, MAXTRI)
    bake_vcol(ob)
    export_fbx(ob, os.path.join(OUT, name + '.fbx'))
    layout['cells'].append({'fbx': name + '.fbx', 'tris': sum(len(p.vertices) - 2 for p in ob.data.polygons), 'objects': 1, 'decimatedFrom': t})
    bpy.data.objects.remove(ob)
    print('EXPORT big', name, t, '->', MAXTRI, f'{time.time() - t0:.0f}s')

# 3) 鏡頭（地面視角高度以腳下地面為準，跟 d2_plan 算圖一樣）、太陽、霧
_SH = {
    'V1': ((70, -105, 62), (-6, 18, 0), 24, False), 'V2': ((2.5, -97, 1.7), (1.5, -60, 4.5), 22, True),
    'V3': ((8, -10.5, 1.9), (11, 22.5, 5.0), 16, True), 'V4': ((18.5, -10.5, 2.4), (13.5, -2.0, -.8), 24, True),
    'V5': ((-6, 12, 2.2), (17, -21, 1.8), 18, True), 'V6': ((1, 91, 1.7), (-5, 135, 5.0), 24, True)}
for k, (loc, tgt, lens, rel) in _SH.items():
    l = Vector((loc[0], loc[1], (gh(loc[0], loc[1]) if rel else 0) + loc[2]))
    t = Vector((tgt[0], tgt[1], (gh(tgt[0], tgt[1]) if rel else 0) + tgt[2]))
    ul = C @ l.to_4d(); ut = C @ t.to_4d()
    import math as _m
    vfov = 2 * _m.degrees(_m.atan((36 * 1024 / 1536) / 2 / lens))   # Blender 感光片寬 36 mm、1536×1024
    layout['cameras'].append({'name': k, 'pos': [ul.x, ul.y, ul.z], 'target': [ut.x, ut.y, ut.z], 'vfov': vfov})
_sd = Euler((math.radians(50), 0, math.radians(150))).to_matrix() @ Vector((0, 0, -1))   # d2_plan 的太陽方向
layout['sunDir'] = [_sd.x, _sd.z, _sd.y]
layout['axisV2'] = True
layout['fogColour'] = [.66, .70, .74]
layout['notes'].append('PathLitter 5.3M tris skipped in v1; decals later')
with open(os.path.join(OUT, 'D2_layout.json'), 'w', encoding='utf-8') as f:
    json.dump(layout, f)
print('EXPORT done', len(layout['prototypes']), 'protos', len(layout['instances']), 'instances', len(layout['cells']), 'cells', f'{time.time() - t0:.0f}s')
