# DR10 枯立木：量尺寸（總高、樹幹徑、斷口高低、根頸張開多寬、枝展、剝皮比例、擋不擋人）、FBX 回匯檢查、十視圖、
# LOD 比較、model_info.json／validation.json。由 report_dr07.py 改寫（拿掉積水）。
# 在做完 game_dr10 的 Blender 裡（或背景）：blender -b <DR10_DeadSnag_A_v001.blend> --python report_dr10.py -- A
import bpy, math, os, sys, json, hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = 'D:/yun-jing-d2-logs/art/source/d2-roots-b'
HERE6 = 'D:/yun-jing-d2-logs/art/source/d2-logs-b'
ROOT = 'D:/yun-jing-d2-logs'
VER = 'v001'
ASSETS = {'A': 'DR10_DeadSnag_A', 'B': 'DR10_DeadSnag_B'}
DET = 'Detail_DR10_Plants'
NAME_ZH = {'A': '枯立木 A（高 8 m，頂上折斷）', 'B': '枯立木 B（高 14 m，斜、S 彎，上半段長枯枝）'}
SPEC = {'A': dict(H=8.0), 'B': dict(H=14.0)}
SLOT = 'D2 古樹林地（工作包：兩種共擺 3 個；看 V1、V5）'
VIEWS = [('01_front', (0, -1, .06)), ('02_right', (1, 0, .06)), ('03_rear', (0, 1, .06)), ('04_left', (-1, 0, .06)),
         ('05_front_right', (1, -1, .45)), ('06_rear_right', (1, 1, .45)), ('07_rear_left', (-1, 1, .45)),
         ('08_front_left', (-1, -1, .45)), ('09_top', (0, -.001, 1)), ('10_high_front', (0, -1, 1))]


def texel_by_part(objs):
    """第五輪：分部位貼圖密度。量法：LOD0 每個物件的 UVMap（UV0，烘焙圖集）面積 ÷ 世界 3D 表面積，開根號 × 圖寬。
    2048 = Blender 烘焙輸出的圖寬；1024 = Unity 匯入（StandaloneWindows64 最大 1024）後實際用到的。
    樹皮和裸木共用樹幹 UV（同一個數）。植物另用共用 Detail 圖，不在圖集裡，另列。"""
    import bmesh as _bm
    groups = {}
    for o in objs:
        if o.type != 'MESH' or 'UVMap' not in o.data.uv_layers:
            continue
        nm = o.name.split('_', 1)[1] if o.name.startswith(('L_', 'F_', 'DR10_')) else o.name
        key = ('樹幹（樹皮＋裸木）' if nm.startswith(('Trunk', 'Rim')) else '斷頂木束' if nm.startswith('Slab') else
               '主根' if nm.startswith('Root') and not nm.startswith('Rootlet') else '細根' if nm.startswith('Rootlet') else
               '枝' if nm.startswith(('Limb', 'Twig', 'Stub')) else '心材內壁' if nm.startswith('Inner') else
               '地面' if nm.startswith(('Ground', 'Stones', 'Pebble')) else '其他（木刺、碎片、洞、菌）')
        b = _bm.new()
        b.from_mesh(o.data)
        b.transform(o.matrix_world)
        uv = b.loops.layers.uv['UVMap']
        a3 = au = 0.0
        for f in b.faces:
            a3 += f.calc_area()
            p = [l[uv].uv for l in f.loops]
            for k in range(1, len(p) - 1):
                au += abs((p[k] - p[0]).cross(p[k + 1] - p[0])) * .5
        b.free()
        g = groups.setdefault(key, [0.0, 0.0])
        g[0] += a3
        g[1] += au
    out = {}
    for k, (a3, au) in groups.items():
        d = math.sqrt(au / max(a3, 1e-9))
        out[k] = dict(area_m2=round(a3, 2), atlas_share=round(au, 3), px_per_m_2048=round(d * 2048, 1), px_per_m_unity1024=round(d * 1024, 1))
    return out


def _load(p):
    g = {'__file__': p, '__name__': os.path.basename(p)[:-3]}
    exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), g)
    return g


def tri(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def bounds(objs):
    lo, hi = [1e9] * 3, [-1e9] * 3
    for o in objs:
        mw = o.matrix_world
        for v in o.data.vertices:
            p = mw @ v.co
            for i in range(3):
                lo[i] = min(lo[i], p[i])
                hi[i] = max(hi[i], p[i])
    return [round(v, 4) for v in lo], [round(v, 4) for v in hi]


def bvh_of(o):
    return BVHTree.FromPolygons([o.matrix_world @ v.co for v in o.data.vertices], [tuple(p.vertices) for p in o.data.polygons])


def plants_inside(plants, body):
    t = bvh_of(body)
    M = plants.matrix_world
    n = in2 = in5 = 0
    for v in plants.data.vertices:
        q = M @ v.co
        if q.z < .05:
            continue
        n += 1
        loc, nr, _, _ = t.find_nearest(q, 1.0)
        if loc is None:
            continue
        d = (q - loc).dot(nr)
        in2 += d < -.02
        in5 += d < -.05
    return dict(vertices_checked=n, inside_body_over_2cm=in2, inside_body_over_5cm=in5)


def shape(o, b, V, col=False):
    """（建模座標：樹幹沿 +Z、軸心照 axis_xy）
    總高：外框最高點；樹幹徑：1.3 m 高處從 X、Y 兩向往軸心打，兩兩相減；斷口頂：每 10° 在殼壁中間從上往下打（最低＝矮邊、最高＝斷刺）；
    根頸：0.05 m 高處從 16 個方向往軸心打，最外的距離 × 2；枝展：外框 X、Y 寬；人橫穿（0.3／1.0 m 高、三條線）擋不擋。"""
    t = bvh_of(o)
    H0, H1 = V['H']
    W = [o.matrix_world @ v.co for v in o.data.vertices]
    cx, cy = b['axis_xy'](V, 1.3)
    c1 = Vector((cx, cy, 1.3))
    outer = {}
    for nm, d in (('x', Vector((1, 0, 0))), ('y', Vector((0, 1, 0)))):
        p = t.ray_cast(c1 + d * 12, -d, 24)[0]
        q = t.ray_cast(c1 - d * 12, d, 24)[0]
        outer[nm] = round((p - q).length, 3) if (p and q) else None
    tops = []
    cx_, cy_ = b['axis_xy'](V, H0)
    rm = (b['out_r'](V, H0) + b['in_r'](V, H0)) / 2
    for k in range(36):
        a = math.radians(k * 10)
        z = H1 + 2
        h = t.ray_cast(Vector((cx_ + math.cos(a) * rm, cy_ + math.sin(a) * rm, z)), Vector((0, 0, -1)), 3.0)[0]
        tops.append(round(h.z, 3) if h else None)
    cx0, cy0 = b['axis_xy'](V, 0.0)
    spread = []
    for k in range(16):
        a = 2 * math.pi * k / 16
        d = Vector((math.cos(a), math.sin(a), 0))
        st = Vector((cx0, cy0, .05)) + d * 12
        h = t.ray_cast(st, -d, 12)[0]
        if h:
            spread.append((h - Vector((cx0, cy0, .05))).length)
    blocked = []
    for off in (-.5, 0.0, .5):
        y = cy0 + off * V['R']
        blocked.append([t.ray_cast(Vector((cx0 - 12, y, z)), Vector((1, 0, 0)), 24)[0] is not None for z in (.3, 1.0)])
    vt = [x for x in tops if x is not None and x > H0 - 1.5]
    return dict(total_height_m=round(max(p.z for p in W), 3),
                crown_spread_xy_m=[round(max(p.x for p in W) - min(p.x for p in W), 3), round(max(p.y for p in W) - min(p.y for p in W), 3)],
                trunk_diameter_at_1p3m_xy_m=outer,
                trunk_diameter_at_1p3m_m=round(sum(v for v in outer.values() if v) / max(1, sum(1 for v in outer.values() if v)), 3),
                break_top_z_every_10deg=tops, break_low_m=min(vt) if vt else None, break_high_m=max(vt) if vt else None,
                root_collar_spread_diameter_m=round(2 * max(spread), 3) if spread else None,
                blocked_at_0p3_1p0m_three_lines=blocked)


def peel_fraction():
    o = bpy.data.objects.get('Trunk')
    if o is None or 'Peel' not in o.data.attributes:
        return None
    import numpy as np
    pe = np.empty(len(o.data.vertices), np.float32)
    o.data.attributes['Peel'].data.foreach_get('value', pe)
    a = p_ = 0.0
    for f in o.data.polygons:
        if f.center.z < .45 or abs(f.normal.z) > .6:
            continue
        a += f.area
        if pe[list(f.vertices)].mean() > .5:
            p_ += f.area
    return round(p_ / max(a, 1e-9), 3)


def fbx_roundtrip(path, asset):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    m0 = [o for o in new if o.type == 'MESH' and o.name.split('.')[0] == f'{asset}_LOD0']
    lo, hi = bounds(m0)
    rep = dict(objects=sorted(o.name.split('.')[0] for o in new), lod0_dimensions_m=[round(hi[i] - lo[i], 4) for i in range(3)],
               uv_layers=[u.name for u in m0[0].data.uv_layers] if m0 else [],
               materials=sorted({s.material.name.split('.')[0] for o in new if o.type == 'MESH' for s in o.material_slots if s.material}))
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    return rep


def show(names):
    for c in bpy.data.collections:
        if c.name.startswith('DR10_'):
            c.hide_render = False
            for o in c.objects:
                o.hide_render = o.hide_viewport = o.name not in names


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def report(v, render=True, samples=48):
    asset = ASSETS[v]
    EXP = f'{ROOT}/art/exports/d2-logs-b/{asset}'
    PRE = f'{ROOT}/art/previews/d2-logs-b/{asset}'
    os.makedirs(PRE + '/turnaround', exist_ok=True)
    b = _load(HERE6 + '/build_dr10.py')
    V = b['set_variant'](v)
    pv = _load(HERE + '/preview_dr.py')
    G = lambda n: bpy.data.objects[n]
    lods = {lv: [G(f'{asset}_LOD{lv}'), G(f'{DET}_LOD{lv}')] for lv in (0, 1, 2)}
    col = G(f'{asset}_Collision')
    dp = _load(HERE + '/dr_pivot.py')
    P = dp['pivot']()
    dp['frame'](asset, False)
    lo, hi = bounds([lods[0][0]])
    dlo, dhi = bounds([lods[0][1]])
    centre_xy = [round((lo[i] + hi[i]) / 2, 3) for i in (0, 1)]
    dp['frame'](asset, True)                  # 量形狀、拍審圖鏡位用建模座標
    val = dict(asset=asset, version=VER, blender=bpy.app.version_string)
    val['bounds_main'] = dict(min=lo, max=hi, dims=[round(hi[i] - lo[i], 4) for i in range(3)])
    val['origin_at_bottom_centre'] = dict(footprint_centre_xy_m=centre_xy, ok=all(abs(c) < .01 for c in centre_xy))
    val['build_origin_in_asset_m'] = [round(-P.x, 4), round(-P.y, 4), 0.0]
    val['bounds_detail'] = dict(min=dlo, max=dhi)
    val['shape_lod0'] = shape(lods[0][0], b, V)
    val['shape_collision'] = shape(col, b, V, col=True)
    sp = SPEC[v]
    s0 = val['shape_lod0']
    D = s0['trunk_diameter_at_1p3m_m']
    val['spec_check'] = dict(spec=sp, total_height_m=s0['total_height_m'], trunk_diameter_at_1p3m_m=D,
                             break_low_m=s0['break_low_m'], break_high_m=s0['break_high_m'],
                             root_collar_spread_ratio=round(s0['root_collar_spread_diameter_m'] / D, 2) if D else None,
                             height_ok=abs(s0['total_height_m'] - sp['H']) <= .25,
                             woodpecker_holes=len(V['holes']), bracket_fungi_clusters=len(V['fungi']),
                             note='工作包：高 8／14 m；樹皮剝落、頂端斷折、啄木洞；剪影要好看、不長葉。底徑工作包沒寫，照參考圖比例。'
                                  '總高量外框最高點；樹幹徑量 1.3 m 高處 X、Y 兩向平均；斷口高度量殼壁中間每 10° 從上往下打到的頂；'
                                  '根頸張開量 0.05 m 高處最外的根到軸心距離 × 2')
    val['peel_fraction_side_high'] = peel_fraction()
    val['plants_inside_body_lod0'] = plants_inside(lods[0][1], lods[0][0])
    val['buried_depth_m'] = round(-lo[2], 3)
    val['tris'] = {f'LOD{lv}': {o.name: tri(o) for o in lst} for lv, lst in lods.items()}
    val['tris']['collision'] = tri(col)
    val['lod_ratio'] = {f'LOD{lv}': round(sum(tri(o) for o in lods[lv]) / sum(tri(o) for o in lods[0]), 3) for lv in (1, 2)}
    fbx = f'{EXP}/{asset}_{VER}.fbx'
    val['fbx_roundtrip'] = fbx_roundtrip(fbx, asset)
    val['fbx_dims_match'] = all(abs(a - c) < .01 for a, c in zip(sorted(val['fbx_roundtrip']['lod0_dimensions_m']), sorted(val['bounds_main']['dims'])))
    tex = {}
    for f in sorted(os.listdir(EXP + '/Textures')):
        im = bpy.data.images.load(f'{EXP}/Textures/{f}', check_existing=False)
        tex[f] = list(im.size)
        bpy.data.images.remove(im)
    val['textures_px'] = tex
    upm = bpy.context.scene.get('dr02_uv_per_m', 0) * 2048
    val['texel_px_per_m'] = round(upm, 1)
    _lf = next((c for c in bpy.data.collections if c.name.endswith('_LowFull')), None)
    val['texel_by_part'] = texel_by_part(list(_lf.objects) if _lf else lods[0])
    val['hidden_tris_removed_lod0'] = int(bpy.context.scene.get('dr06_hidden_tris_removed', 0))
    cx, cy = b['axis_xy'](V, 0.0)
    val['snag_build'] = dict(axis_x=round(cx, 3), axis_y=round(cy, 3), break_low=s0['break_low_m'], radius=V['R'], limbs=len(V['limbs']))
    val['checks_not_in_this_file'] = [f'Unity 匯入與引擎內外觀：另見 art/previews/d2-logs-b/{asset}/unity/report.txt',
                                      '放進 D2 場景後的同鏡位截圖（場景由核心組擺）', '實機效能、FPS']
    json.dump(val, open(f'{EXP}/validation.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    mats = [bpy.data.materials[f'M_{asset}_{S}'] for S in ('A', 'Leaf')]
    sh = 'Shared/D2Bark_Detail_Normal.png'
    info = {
        'asset': asset, 'version': VER, 'minTier': 'standard', 'detailObjects': [DET],
        'name_zh': NAME_ZH[v], 'slot': SLOT,
        'note': ('死了還站著的樹，不長葉。頂上折斷：參差斷口、一側幾根長的淺色木刺；心材朽空一個淺碗。'
                 '樹幹大片剝皮，露出淺銀灰風化木（長縱裂紋），剩下的樹皮深灰褐縱溝，剝皮邊緣皮往外翹；兩三個啄木洞排成一直排；下段層狀菌。'
                 '枝條：從樹幹長出有枝領，往外、往上彎，末端斷成木刺或收尖；B 上半段幾根長枯枝和二、三級枝，剪影像骨架。'
                 '根頸張開，5–6 條根扭著鑽進土裡，根頸和根的朝上面長苔；高處只有淡灰綠地衣斑。'
                 '樹皮：Poly Haven bark_brown_02 掃描凹凸推進高模幾何再烘焙。'
                 f'{DET}：根頸的苔叢、腳邊的蕨、闊葉草、蕈、地上的落葉。'),
        'references': 'art/references/DR10/v001/（Codex 依 D2 設定圖 V1、V5（另參考 V4）畫的三視圖、四分之三視圖、細節圖）',
        'budget_per_lod': {f'LOD{lv}': dict(triangles=sum(tri(o) for o in lst), objects=2, objects_without_detail=1, materials=len(mats)) for lv, lst in lods.items()},
        'texture_resolution_px': {**tex, sh: [1024, 1024], sh.replace('_Normal', '_Albedo'): [1024, 1024]},
        'units': 'meters', 'front': '-Y (Blender)；啄木洞朝正面；斷口最高的木刺朝 hinge 方位角',
        'hinge_azimuth_deg': round(math.degrees(V['hinge']), 1),
        'up': '+Z (Blender); FBX exported Y-up, -Z forward, transforms baked',
        'origin': '底部中心：LOD0 本體外框 XY 的中心正下方的地面；z = 0 是地面，鑽進土裡的根在 z < 0',
        'snag_build': val['snag_build'], 'peel_fraction_side': val['peel_fraction_side_high'],
        'dimensions_m': val['bounds_main']['dims'], 'bounds_min_m': lo, 'bounds_max_m': hi,
        'shape': val['shape_lod0'], 'spec_check': val['spec_check'],
        'lods': val['tris'], 'lod_rule': 'LOD0 不刪細節；LOD1／LOD2：本體每件各自 collapse 再刪藏起來的面，植物整件 collapse；照實得比例修正，本體＋植物合計約為 LOD0 的 50%／15%；面積 0 的三角形匯出前刪掉',
        'materials': [m.name for m in mats], 'objects_per_lod': 2,
        'material_note': f'本體一個物件、一個材質 M_{asset}_A（一組貼圖 2048）；{DET} 一個材質 M_{asset}_Leaf（同一組貼圖，雙面）',
        'uv': {'UV0': 'UVMap：烘焙圖集，所有 UV 島同比例（%.1f px/m）、不旋轉' % upm, 'UV1': 'TileUV：樹皮件是每 2.6 m 重複的樹皮 UV，其他件同 UV0'},
        'unity': {'shader': 'Universal Render Pipeline/Lit', 'detail_normal': sh, 'detail_albedo': sh.replace('_Normal', '_Albedo'),
                  'detail_mask': 'Albedo.png 的 alpha（1 = 樹皮，0 = 苔和葉）', 'detail_tiling_on_uv0': round(mats[0].get('unity_detail_tiling', 0), 2),
                  'mask_map': 'MaskURP.png（R metal、G AO、A smoothness）'},
        'collision': f'{asset}_Collision: MeshCollider (convex off), renderer hidden；樹幹分段 10 邊斜柱（跟著樹幹彎，到斷口矮邊 0.95 高）＋根頸一圈 0.40 m 高的矮台；枝條在頭頂以上不做碰撞',
        'sockets_blender_xyz': {},
        'build_origin_m': val['build_origin_in_asset_m'],
        'build_origin_note': '建模座標（樹幹軸心在原點附近、沿 +Z）的原點在本資產座標裡的位置；Unity 檢查把模型放在它的負值，審圖鏡位才對得上',
        'length_build_m': V['H'][1],
        'ruler_build_xy': list(V['human']),
        'review_cams_build_xyz': [dict(name=k, **{'from': [round(c, 3) for c in f], 'at': [round(c, 3) for c in t]}, lens_mm=ln)
                                  for k, (f, t, ln) in b['_views'](V).items()],
        'external_assets': [{'name': 'bark_brown_02', 'source': 'https://polyhaven.com/a/bark_brown_02', 'license': 'CC0'}],
        'files_sha256': {f: sha(f'{EXP}/{f}') for f in sorted(os.listdir(EXP)) if f.endswith(('.fbx', '.glb'))},
    }
    json.dump(info, open(f'{EXP}/model_info.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    if render:
        pv['setup'](samples=samples, fog=False)
        hm = bpy.data.objects.get('DR_Human_1p75m')
        if hm:
            hm.location = (V['human'][0], V['human'][1], .875)
        HT = V['H'][1] + .8 * max([s_[2] for s_ in V.get('slabs', ())] or [0.0])     # 第四輪：斷頂裂片也要入鏡
        cz = HT * .5
        cx_, cy_ = b['axis_xy'](V, cz)
        dist = HT * 1.55 + 2
        sub = 'turnaround'
        show({o.name for o in lods[0]})
        vj = []
        for nm, d in VIEWS:
            dv = Vector(d).normalized()
            loc = Vector((cx_, cy_, cz)) + dv * (dist if nm != '09_top' else dist + 2)
            pv['shot'](f'{PRE}/{sub}/{nm}.png', tuple(loc), (cx_, cy_, cz), 50, res=(1024, 1024))
            vj.append(dict(name=nm, direction=list(d), camera=[round(c, 3) for c in loc - P], lens_mm=50, file=f'{sub}/{nm}.png', mesh='LOD0'))
        json.dump(dict(asset=asset, version=VER, views=vj,
                       note=f'遊戲模型 LOD0＋{DET}，烘焙貼圖；白柱是 1.75 m 人形尺；相機座標以原點（底部中心）為準'),
                  open(f'{PRE}/{sub}/views.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        pv['setup'](samples=samples)
        hm = bpy.data.objects.get('DR_Human_1p75m')
        if hm:
            hm.location = (V['human'][0], V['human'][1], .875)
        vw = b['_views'](V)
        for lv in (0, 1, 2):
            show({o.name for o in lods[lv]})
            loc, tgt, lens = vw['front']
            pv['shot'](f'{PRE}/{asset}_LOD{lv}_front.png', loc, tgt, lens, res=(1536, 864))
        show({lods[1][0].name})
        loc, tgt, lens = vw['front']
        pv['shot'](f'{PRE}/{asset}_LOD1_nodetail_front.png', loc, tgt, lens, res=(1536, 864))
        show({o.name for o in lods[0]})
        for n in ('tq', 'side', 'back', 'break', 'holes', 'base'):
            loc, tgt, lens = vw[n]
            pv['shot'](f'{PRE}/{asset}_LOD0_{n}.png', loc, tgt, lens, res=(1536, 864))
    dp['frame'](asset, False)
    print(json.dumps({k: val[k] for k in ('bounds_main', 'origin_at_bottom_centre', 'spec_check', 'buried_depth_m', 'tris', 'lod_ratio',
                                          'fbx_dims_match', 'texel_px_per_m', 'plants_inside_body_lod0', 'peel_fraction_side_high')}, indent=1, ensure_ascii=False))
    print(json.dumps(val['shape_lod0'], ensure_ascii=False))
    print(val['fbx_roundtrip'])
    return val


if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    report(a[0] if a else 'A', render='norender' not in a)
    print('REPORT_DONE')
