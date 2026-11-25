# DR09 斷枝堆的量測、檢查和審圖：開 blend/DR09_BranchPile_<v>_v001.blend（game_dr09.py 存的），寫
#   art/exports/d2-logs-b/<asset>/model_info.json、validation.json，
#   art/previews/d2-logs-b/<asset>/turnaround/（十個方位 1024，views.json）和審圖鏡位（tq、side、top、end、close、brk、各級 LOD 側面）。
# 檢查：外框尺寸對工作包、原點在底部中心、各級面數、枝與枝的 3D 穿插（擺放時的軸線＋半徑）、落葉卡有沒有埋進枝裡、FBX 回匯尺寸。
#   blender -b art/source/d2-logs-b/blend/DR09_BranchPile_M_v001.blend --python art/source/d2-logs-b/report_dr09.py -- M [norender]
import bpy, sys, os, json, math, hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = 'D:/yun-jing-d2-logs'
HERE = ROOT + '/art/source/d2-logs-b'
ROOTS = ROOT + '/art/source/d2-roots-b'
VER = 'v001'
DET = 'Detail_DR09_Leaves'
SPEC = {'S': dict(L=1.5, W=1.0, H=.40), 'M': dict(L=2.5, W=1.6, H=.70), 'L': dict(L=4.0, W=2.2, H=1.10)}
NAME_ZH = {'S': '斷枝堆 S：小堆（長約 1.5 m）', 'M': '斷枝堆 M：中堆（長約 2.5 m）', 'L': '斷枝堆 L：大堆（長約 4 m）'}


def _exec(path, name):
    ns = {'__name__': name, '__file__': path}
    exec(compile(open(path, encoding='utf-8').read(), path, 'exec'), ns)
    return ns


def bounds(objs):
    lo = Vector((1e9, 1e9, 1e9))
    hi = -lo
    for o in objs:
        for v in o.data.vertices:
            p = o.matrix_world @ v.co
            lo = Vector(map(min, lo, p))
            hi = Vector(map(max, hi, p))
    return [round(x, 4) for x in lo], [round(x, 4) for x in hi]


def tri(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def tree_of(o):
    co = [o.matrix_world @ v.co for v in o.data.vertices]
    return BVHTree.FromPolygons(co, [tuple(p.vertices) for p in o.data.polygons])


def _odd(tree, p, d):
    k, q = 0, p.copy()
    for _ in range(40):
        h = tree.ray_cast(q, d, 10)
        if h[0] is None:
            break
        k += 1
        q = h[0] + d * 1e-4
    return k % 2 == 1


def leaves_inside(body, det):
    """落葉卡的頂點在枝裡面多深：最近面背面＋三個方向射線都是奇數次才算在裡面。"""
    t = tree_of(body)
    n2 = n5 = 0
    for v in det.data.vertices:
        p = det.matrix_world @ v.co
        loc, nrm, _, d = t.find_nearest(p)
        if loc is None or (p - loc).dot(nrm) > -.02:
            continue
        if all(_odd(t, p, Vector(dd).normalized()) for dd in ((0, 0, 1), (1, .13, .07), (-.11, 1, .05))):
            n2 += 1
            if d > .05:
                n5 += 1
    return dict(vertices_checked=len(det.data.vertices), inside_body_over_2cm=n2, inside_body_over_5cm=n5)


def fbx_roundtrip(path, asset):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    l0 = next(o for o in new if o.name.startswith(f'{asset}_LOD0'))
    bpy.context.view_layer.update()
    lo, hi = bounds([l0])
    out = dict(objects=sorted(o.name.split('.')[0] for o in new), lod0_dimensions_m=[round(hi[i] - lo[i], 4) for i in range(3)],
               uv_layers=[u.name for u in l0.data.uv_layers], colour_attributes=[c.name for c in l0.data.color_attributes],
               materials=sorted({m.name.split('.')[0] for o in new if o.type == 'MESH' for m in o.data.materials if m}))
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    return out


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def report(v, render=True, samples=48):
    asset = f'DR09_BranchPile_{v}'
    EXP = f'{ROOT}/art/exports/d2-logs-b/{asset}'
    PRE = f'{ROOT}/art/previews/d2-logs-b/{asset}'
    os.makedirs(PRE + '/turnaround', exist_ok=True)
    G = bpy.data.objects.get
    lods = {lv: [G(f'{asset}_LOD{lv}'), G(f'{DET}_LOD{lv}')] for lv in (0, 1, 2)}
    col = G(f'{asset}_Collision')
    root = G(asset)
    root.location = (0, 0, 0)
    bpy.context.view_layer.update()
    plan = json.loads(bpy.context.scene['dr09_plan'])
    piv = Vector(bpy.context.scene.get('dr_pivot', (0, 0, 0)))
    lo, hi = bounds([lods[0][0]])
    dlo, dhi = bounds([lods[0][1]])
    dims = [round(hi[i] - lo[i], 4) for i in range(3)]
    centre = [round((lo[i] + hi[i]) / 2, 3) for i in (0, 1)]
    sp = SPEC[v]
    val = dict(asset=asset, version=VER, blender=bpy.app.version_string)
    val['bounds_main'] = dict(min=lo, max=hi, dims=dims)
    val['origin_at_bottom_centre'] = dict(footprint_centre_xy_m=centre, ok=all(abs(c) < .01 for c in centre))
    val['bounds_detail'] = dict(min=dlo, max=dhi)
    sc = dict(spec=sp, length_x_m=dims[0], width_y_m=dims[1], top_z_m=hi[2],
              length_ok=abs(dims[0] - sp['L']) <= .15 * sp['L'], width_ok=abs(dims[1] - sp['W']) <= .25 * sp['W'],
              height_ok=abs(hi[2] - sp['H']) <= .25 * sp['H'], in_pack_range_1p5_to_4m=1.3 <= dims[0] <= 4.4,
              note='工作包：斷枝堆三種大小，長 1.5–4 m。外框含腳下落葉土堆（四周比枝多出 0.3–0.4 m、外緣鑽進地面）；長容許 ±15%、寬 ±25%、頂高 ±25%（目標見 spec）')
    val['spec_check'] = sc
    val['branch_overlap'] = dict(plan['plan_check'], note='擺放時的解析檢查：每根枝的軸線＋半徑對其他枝的 3D 最近距離（負 = 穿進去）；分岔、斷枝樁、細枝和自己的母枝不算')
    val['pieces'] = plan['pieces']
    val['leaves_inside_body_lod0'] = leaves_inside(lods[0][0], lods[0][1])
    val['buried_depth_m'] = round(-lo[2], 3)
    tris = {f'LOD{lv}': {o.name: tri(o) for o in lst} for lv, lst in lods.items()}
    tris['collision'] = tri(col)
    val['tris'] = tris
    tot = [sum(tris[f'LOD{lv}'].values()) for lv in (0, 1, 2)]
    val['lod_ratio'] = {'LOD1': round(tot[1] / tot[0], 3), 'LOD2': round(tot[2] / tot[0], 3)}
    fbx = f'{EXP}/{asset}_{VER}.fbx'
    val['fbx_roundtrip'] = fbx_roundtrip(fbx, asset)
    val['fbx_dims_match'] = all(abs(a - b) < .01 for a, b in zip(val['fbx_roundtrip']['lod0_dimensions_m'], dims))
    texd = {f'DR08_Shared/Textures/DR08_{n}_{k}.png': [1024, 1024] for n in ('Bark', 'Moss', 'Rot', 'Inner', 'Soil') for k in ('Albedo', 'Normal')}
    texd.update({f'DR09_Shared/Textures/DR09_FreshWood_{k}.png': [1024, 1024] for k in ('Albedo', 'Normal')})
    texd['DR08_Shared/Textures/DR08_Plants_Albedo.png'] = [2048, 2048]
    for k in list(texd):
        im = bpy.data.images.load(f'{ROOT}/art/exports/d2-logs-b/{k}', check_existing=True)
        texd[k] = list(im.size)
    val['textures_px'] = texd
    val['texel_px_per_m'] = dict(bark='1024 × (1.0–2.6)：樹皮 UV 照枝粗細放大（半徑 10 cm 以上 1 倍、細枝最多 2.6 倍），鱗片大小跟著枝變', moss=2048, fresh_wood=1024, soil=1024)

    # 審圖鏡位（建模座標 = 資產座標 + dr_pivot；Unity 檢查把模型放回建模座標）
    L, H = dims[0], max(hi[2], .3)
    cams = [dict(name='tq', from_=(-L * .55 - 1.6, -L * .55 - 2.0, 1.2 + H), at=(0, 0, H * .35), lens=40),
            dict(name='side', from_=(0, -L * 1.55 - 1.0, .9), at=(0, 0, H * .45), lens=40),
            dict(name='top', from_=(0, -.6, L * 1.6 + 1.5), at=(0, 0, 0), lens=40),
            dict(name='end', from_=(L * .5 + 2.2, -.6, 1.0), at=(0, 0, H * .4), lens=40),
            dict(name='close', from_=(-L * .22, -1.4, .55 + H * .6), at=(-L * .22, 0, H * .35), lens=40),
            dict(name='brk', from_=(L * .22, -1.3, .5 + H * .5), at=(L * .22, 0, H * .3), lens=40),
            dict(name='back', from_=(L * .3, L * .8 + 2.0, 1.0 + H * .6), at=(0, 0, H * .35), lens=40)]
    sh = lambda p: [round(p[0] + piv.x, 3), round(p[1] + piv.y, 3), round(p[2], 3)]
    info = dict(asset=asset, version=VER, minTier='standard', detailObjects=[DET],
                name_zh=NAME_ZH[v], slot='D2 古樹空地四周的林地、路邊（工作包：三種大小共 12 處擺放；V4、V6）',
                note=('風雨後掉在神木底下的一堆枯斷枝：粗的主枝躺在最下面、略陷進落葉土，其他枝順著長向交疊、斜靠在下面的枝上（兩點支撐，一頭可以翹起）；'
                      '枝有彎、有分岔、有斷枝樁和細枝梢；斷口是撕裂的淺奶油色木刺束、一側剝皮露出新木；粗枝朝上的面長苔、樹皮上有淡灰綠地衣（畫在樹皮貼圖裡）；'
                      '交叉處夾著落葉，腳下一層落葉土和小枝。表面是 DR08 的六層手繪平鋪貼圖（撕裂纖維那層換成 DR09 淺色新斷木），用頂點權重混合，S／M／L 共用。'),
                references='art/references/DR09/v001/（Codex 依 D2 設定圖 V4、V6 畫的三視圖、四分之三視圖、細節圖）；淺色斷木貼圖原圖 art/source/d2-logs-b/tex_src_dr09/（Codex 畫）',
                budget_per_lod={f'LOD{lv}': dict(triangles=tot[lv], objects=2, objects_without_detail=1, materials=2) for lv in (0, 1, 2)},
                texture_resolution_px=texd, units='meters', front='-Y (Blender)：看斷枝堆的長邊；長向沿 X',
                up='+Z (Blender); FBX exported Y-up, -Z forward, transforms baked',
                origin='底部中心：LOD0 本體外框 XY 的中心正下方的地面；z = 0 是地面，主枝和落葉土陷進地面的部分在 z < 0',
                dimensions_m=dims, bounds_min_m=lo, bounds_max_m=hi, spec_check=sc, lods=tris,
                lod_rule='LOD 每級用同一份擺法重建（不是 decimate）：環距、每圈點數變粗；LOD2 拿掉細枝條和地上小枝、木刺只留 LOD0／1；落葉卡照組抽掉（LOD1 留約 50%、LOD2 約 15%）',
                materials=['M_DR09_Layered', 'M_DR08_Plants'], objects_per_lod=2,
                material_note='本體 M_DR09_Layered：YunJing/D2LayeredWood，DR08_Shared 的樹皮、苔、褐腐、內壁、土＋DR09_Shared 的淺色新斷木（纖維那格），六層 1024；Detail_DR09_Leaves 用 M_DR08_Plants（DR08 的 2048 手繪植物圖集，alpha 裁切、雙面）',
                uv=dict(UV0='UVMap：公尺（沿枝長 = u；細枝的樹皮 UV 放大最多 2.6 倍）；落葉卡是植物圖集的 UV', UV1='Extra：x = 土的權重，y = 頂點 AO（1 = 不遮）',
                        vertex_color='RGBA = 苔、褐腐木、撕裂纖維（這裡是淺色新斷木）、樹洞內壁的權重；樹皮 = 1 − 其他權重總和'),
                unity=dict(shader='YunJing/D2LayeredWood（apps/game/Assets/YunJing/Runtime/D2Logs/D2LayeredWood.shader）', fibre_slot='DR09_Shared/Textures/DR09_FreshWood_{Albedo,Normal}.png',
                           other_slots='DR08_Shared/Textures/DR08_{Bark,Moss,Rot,Inner,Soil}_{Albedo,Normal}.png', plants='Universal Render Pipeline/Lit，雙面、alpha clip 0.5'),
                collision=f'{asset}_Collision：MeshCollider（convex off），renderer 關；只收半徑 3 cm 以上的枝和分岔（6 邊、每 0.3 m 一環），細枝、落葉土不收',
                sockets_blender_xyz={}, build_origin_m=[round(-piv.x, 4), round(-piv.y, 4), 0.0],
                build_origin_note='建模座標（擺放時的座標，斷枝堆大致以原點為中心）的原點在本資產座標裡的位置；Unity 檢查把模型放在它的負值，審圖鏡位才對得上',
                length_build_m=round(dims[0], 3), ruler_build_xy=[round(lo[0] - .45 + piv.x, 3), round(hi[1] + .5 + piv.y, 3)],
                review_cams_build_xyz=[{'name': c['name'], 'from': sh(c['from_']), 'at': sh(c['at']), 'lens_mm': c['lens']} for c in cams],
                external_assets=[])
    if render:
        pv = _exec(ROOTS + '/preview_dr.py', 'preview_dr')
        pv['setup'](samples=samples)
        hm = bpy.data.objects.get('DR_Human_1p75m')
        if hm:
            hm.location = (lo[0] - .45, hi[1] + .5, .875)

        def show(names):
            for o in bpy.data.objects:
                if o.type == 'MESH' and not o.name.startswith('DR_'):
                    o.hide_render = o.name not in names
        show({o.name for o in lods[0]})
        R = max(dims[0], dims[1]) * 1.15 + 1.2
        cz = H * .4
        vj = []
        dirs = [('01_front', (0, -1, 0)), ('02_right', (1, 0, 0)), ('03_rear', (0, 1, 0)), ('04_left', (-1, 0, 0)),
                ('05_front_right', (1, -1, 0)), ('06_rear_right', (1, 1, 0)), ('07_rear_left', (-1, 1, 0)), ('08_front_left', (-1, -1, 0)),
                ('09_top', (0, -.001, 1)), ('10_high_front', (0, -1, 1.1))]
        for nm, d in dirs:
            d = Vector(d).normalized()
            loc = d * R + Vector((0, 0, cz + (.4 if d.z == 0 else 0)))
            pv['shot'](f'{PRE}/turnaround/{nm}.png', tuple(loc), (0, 0, cz), 50, res=(1024, 1024))
            vj.append(dict(name=nm, direction=list(d), camera=[round(c, 3) for c in loc], lens_mm=50, file=f'turnaround/{nm}.png', mesh='LOD0'))
        json.dump(dict(asset=asset, version=VER, views=vj, note=f'遊戲模型 LOD0＋{DET}；白柱是 1.75 m 人形尺；相機座標以原點（底部中心）為準'),
                  open(f'{PRE}/turnaround/views.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        cd = {c['name']: c for c in cams}
        for lv in (0, 1, 2):
            show({o.name for o in lods[lv]})
            c = cd['side']
            pv['shot'](f'{PRE}/{asset}_LOD{lv}_side.png', c['from_'], c['at'], c['lens'])
        show({lods[1][0].name})
        pv['shot'](f'{PRE}/{asset}_LOD1_nodetail_side.png', cd['side']['from_'], cd['side']['at'], cd['side']['lens'])
        show({o.name for o in lods[0]})
        for n in ('tq', 'top', 'end', 'close', 'brk', 'back'):
            c = cd[n]
            pv['shot'](f'{PRE}/{asset}_LOD0_{n}.png', c['from_'], c['at'], c['lens'])
    info['files_sha256'] = {os.path.basename(p): sha(p) for p in (fbx, f'{EXP}/{asset}_{VER}.glb') if os.path.exists(p)}
    json.dump(info, open(f'{EXP}/model_info.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    json.dump(val, open(f'{EXP}/validation.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(json.dumps({k: val[k] for k in ('bounds_main', 'origin_at_bottom_centre', 'spec_check', 'branch_overlap', 'leaves_inside_body_lod0', 'tris', 'lod_ratio', 'fbx_dims_match')}, indent=1, ensure_ascii=False))
    return val


if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    report(a[0] if a else 'M', render='norender' not in a)
    print('REPORT_DONE')
