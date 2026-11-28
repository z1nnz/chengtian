# DR12 樹皮片的量測、檢查和審圖：開 blend/DR12_BarkSheet_L_v001.blend（game_dr12.py 存的），寫
#   art/exports/d2-logs-b/<asset>/model_info.json、validation.json，
#   art/previews/d2-logs-b/<asset>/turnaround/（十個方位 1024，views.json）和審圖鏡位（tq、curl、teeth、end、top、back、各級 LOD 側面、碰撞殼）。
# 檢查：外框尺寸對工作包（0.3–1.5 m）、原點在底部中心、各級面數與比例、捲起高度、厚度、法線朝外、FBX 回匯尺寸。
#   blender -b art/source/d2-logs-b/blend/DR12_BarkSheet_L_v001.blend --python art/source/d2-logs-b/report_dr12.py -- BarkL [norender]
import bpy, sys, os, json, math, hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = 'D:/yun-jing-d2-logs'
HERE = ROOT + '/art/source/d2-logs-b'
ROOTS = ROOT + '/art/source/d2-roots-b'
VER = 'v001'
NAMES = {'BarkL': 'DR12_BarkSheet_L'}
NAME_ZH = {'BarkL': '地上的大片剝落樹皮 L（長約 1.5 m，捲起成浪頭）'}


def _exec(path, name):
    ns = {'__name__': name, '__file__': path}
    exec(compile(open(path, encoding='utf-8').read(), path, 'exec'), ns)
    return ns


R9 = _exec(HERE + '/report_dr09.py', 'report_dr09_lib')
bounds, tri, sha, fbx_roundtrip = R9['bounds'], R9['tri'], R9['sha'], R9['fbx_roundtrip']


def thickness(o, n=400):
    """從內皮面沿法線反方向打射線到外皮面的距離（公尺）：中位數、最小、最大。"""
    mw = o.matrix_world
    co = [mw @ v.co for v in o.data.vertices]
    t = BVHTree.FromPolygons(co, [tuple(p.vertices) for p in o.data.polygons])
    ps = list(o.data.polygons)
    step = max(1, len(ps) // n)
    d = []
    for p in ps[::step]:
        c = mw @ p.center
        nn = (mw.to_3x3() @ p.normal).normalized()
        h = t.ray_cast(c - nn * 1e-4, -nn, .3)
        if h[0] is not None:
            d.append((h[0] - c).length)
    d.sort()
    return dict(samples=len(d), median_m=round(d[len(d) // 2], 4), p10_m=round(d[len(d) // 10], 4), p90_m=round(d[9 * len(d) // 10], 4)) if d else {}


def outward_normals(o):
    """每個面中心沿法線往外打：再撞到自己奇數次 = 法線朝內（翻面）。"""
    mw = o.matrix_world
    co = [mw @ v.co for v in o.data.vertices]
    t = BVHTree.FromPolygons(co, [tuple(p.vertices) for p in o.data.polygons])
    bad = 0
    ps = list(o.data.polygons)[::7]
    for p in ps:
        c = mw @ p.center
        nn = (mw.to_3x3() @ p.normal).normalized()
        k, q = 0, c + nn * 2e-4
        for _ in range(12):
            h = t.ray_cast(q, nn, 5)
            if h[0] is None:
                break
            k += 1
            q = h[0] + nn * 2e-4
        bad += k % 2
    return dict(faces_checked=len(ps), inward=bad)


def report(var, render=True, samples=64):
    asset = NAMES[var]
    EXP = f'{ROOT}/art/exports/d2-logs-b/{asset}'
    PRE = f'{ROOT}/art/previews/d2-logs-b/{asset}'
    os.makedirs(PRE + '/turnaround', exist_ok=True)
    G = bpy.data.objects.get
    lods = {lv: G(f'{asset}_LOD{lv}') for lv in (0, 1, 2)}
    col = G(f'{asset}_Collision')
    root = G(asset)
    root.location = (0, 0, 0)
    bpy.context.view_layer.update()
    game = json.loads(bpy.context.scene['dr12_game'])
    lo, hi = bounds([lods[0]])
    dims = [round(hi[i] - lo[i], 4) for i in range(3)]
    centre = [round((lo[i] + hi[i]) / 2, 3) for i in (0, 1)]
    val = dict(asset=asset, version=VER, blender=bpy.app.version_string)
    val['bounds_main'] = dict(min=lo, max=hi, dims=dims)
    val['origin_at_bottom_centre'] = dict(footprint_centre_xy_m=centre, ok=all(abs(c) < .01 for c in centre) and -.03 < lo[2] <= 0)
    L = max(dims[0], dims[1])
    sc = dict(spec='工作包 DR12：0.3–1.5 m（大片樹皮與樹瘤，共擺 20 處；BarkL 是其中最大的一種）', longest_m=L, in_range=.3 <= L <= 1.5,
              curl_top_m=hi[2], curl_ratio=round(hi[2] / L, 3), curl_ok=.3 <= hi[2] / L <= .6,
              note='參考圖：前段平貼地、後段往上捲成浪頭；捲起高約為長的 0.35–0.55')
    val['spec_check'] = sc
    val['thickness_lod0'] = thickness(lods[0])
    val['normals_lod0'] = outward_normals(lods[0])
    tris = {f'LOD{lv}': tri(o) for lv, o in lods.items()}
    tris['collision'] = tri(col)
    val['tris'] = tris
    val['lod_ratio'] = {'LOD1': round(tris['LOD1'] / tris['LOD0'], 3), 'LOD2': round(tris['LOD2'] / tris['LOD0'], 3)}
    val['lod_ratio_ok'] = .42 <= val['lod_ratio']['LOD1'] <= .58 and .10 <= val['lod_ratio']['LOD2'] <= .20
    clo, chi = bounds([col])
    val['collision_bounds'] = dict(min=clo, max=chi, covers_lod0=all(abs(clo[i] - lo[i]) < .06 and abs(chi[i] - hi[i]) < .06 for i in range(3)))
    fbx = f'{EXP}/{asset}_{VER}.fbx'
    rt = fbx_roundtrip(fbx, asset)
    val['fbx_roundtrip'] = rt
    val['fbx_dims_match'] = all(abs(a - b) < .01 for a, b in zip(rt['lod0_dimensions_m'], dims))
    val['layers'] = game['layers']
    texd = {f'DR08_Shared/Textures/DR08_{n}_{k}.png': None for n in ('Moss', 'Rot', 'Inner', 'Soil') for k in ('Albedo', 'Normal')}
    texd['DR08_Shared/Textures/DR08_Bark_Normal.png'] = None
    texd.update({f'DR09_Shared/Textures/DR09_{n}.png': None for n in ('Bark_Albedo', 'FreshWood_Albedo', 'FreshWood_Normal')})
    for k in list(texd):
        im = bpy.data.images.load(f'{ROOT}/art/exports/d2-logs-b/{k}', check_existing=True)
        texd[k] = list(im.size)
    val['textures_px'] = texd
    checks = dict(size=sc['in_range'], curl=sc['curl_ok'], origin=val['origin_at_bottom_centre']['ok'], lod=val['lod_ratio_ok'],
                  normals=val['normals_lod0']['inward'] <= max(2, val['normals_lod0']['faces_checked'] // 200),
                  fbx=val['fbx_dims_match'], collision=val['collision_bounds']['covers_lod0'],
                  textures_1024=all(s == [1024, 1024] for s in texd.values()))
    val['checks'] = checks
    val['all_pass'] = all(checks.values())

    X, Y, H = dims[0], dims[1], hi[2]
    cams = [dict(name='tq', from_=(-X * .9 - .9, -X * 1.1 - 1.0, .95 + H), at=(0, 0, H * .35), lens=40),
            dict(name='side', from_=(0, -X * 1.4 - 1.2, .45), at=(0, 0, H * .42), lens=40),
            dict(name='curl', from_=(X * .95, -X * .9, .75), at=(X * .22, 0, H * .5), lens=40),
            dict(name='teeth', from_=(-X * .95, -X * .55, .42), at=(-X * .32, 0, .05), lens=40),
            dict(name='end', from_=(-X * 1.6 - .6, -.25, .55), at=(0, 0, H * .35), lens=40),
            dict(name='top', from_=(0, -.3, X * 1.7 + 1.0), at=(0, 0, 0), lens=40),
            dict(name='back', from_=(X * .7, X * 1.2 + .9, .9 + H * .5), at=(0, 0, H * .35), lens=40)]
    info = dict(asset=asset, version=VER, minTier='standard', detailObjects=[],
                name_zh=NAME_ZH[var], slot='D2 古樹空地、林地路邊（工作包：樹皮與樹瘤共擺 20 處；V2、V6）',
                note=('從倒木剝下來、躺在地上的一大片樹皮：前段平貼地、兩側微翹成淺槽，後段往上捲、翻過來像浪頭；'
                      '朝上的內面是淺奶油色的長條纖維、帶受潮深色斑，捲起的外側是深灰褐樹皮（板塊做在幾何上）、朝上處長苔；'
                      '前端撕斷成一排長短不齊的纖維尖齒，捲起端內層纖維一縷縷垂下；厚度斷面三層：深色外皮、紅褐中層、淺色內皮。'
                      '表面是 D2 倒木的分層手繪平鋪貼圖（DR08_Shared＋DR09 淺色新斷木），和 DR08／DR09 共用，不另出貼圖。'),
                references='art/references/DR12/v001/（Codex 依 D2 設定圖 V2、V6、V4 畫的三視圖、四分之三視圖、細節圖）',
                budget_per_lod={f'LOD{lv}': dict(triangles=tris[f'LOD{lv}'], objects=1, objects_without_detail=1, materials=1) for lv in (0, 1, 2)},
                texture_resolution_px=texd, units='meters', front='-Y (Blender)：看樹皮片的長邊；撕斷端在 -X、捲起端在 +X',
                up='+Z (Blender); FBX exported Y-up, -Z forward, transforms baked',
                origin='底部中心：LOD0 外框 XY 的中心正下方的地面；z = 0 是地面，貼地的樹皮略陷進地面 1 cm',
                dimensions_m=dims, bounds_min_m=lo, bounds_max_m=hi, spec_check=sc, lods=tris,
                lod_rule=f"LOD 每級用同一組參數重建（不是 decimate），只換取樣密度：LOD0 {game['res']['0']}、LOD1 {game['res']['1']}、LOD2 {game['res']['2']}（相對高模 150 × 96 格）",
                materials=['M_DR09_Layered'], objects_per_lod=1,
                material_note='M_DR09_Layered：YunJing/D2LayeredWood，DR08_Shared 的苔、褐腐、內壁、土、樹皮法線＋DR09_Shared 的樹皮顏色（偏橄欖深灰褐）與淺色新斷木（纖維那格），全部 1024，和 DR09 斷枝堆同一個材質',
                uv=dict(UV0=f"UVMap：公尺 × {game['uv_per_m']}（u 沿樹皮長向 = 原本的樹幹方向，v 橫向）", UV1='Extra：x = 土的權重，y = 頂點 AO（1 = 不遮）',
                        vertex_color='RGBA = 苔、褐腐（受潮斑、紅褐中層）、撕裂纖維（淺色內皮）、內壁的權重；樹皮 = 1 − 其他權重總和'),
                unity=dict(shader='YunJing/D2LayeredWood（apps/game/Assets/YunJing/Runtime/D2Logs/D2LayeredWood.shader）', fibre_slot='DR09_Shared/Textures/DR09_FreshWood_{Albedo,Normal}.png',
                           bark_slot='DR09_Shared/Textures/DR09_Bark_Albedo.png＋DR08_Shared/Textures/DR08_Bark_Normal.png',
                           other_slots='DR08_Shared/Textures/DR08_{Moss,Rot,Inner,Soil}_{Albedo,Normal}.png'),
                collision=f"{asset}_Collision：MeshCollider（convex off），renderer 關；同一組參數取樣 {game['res']['col']} 重建的低模（{tris['collision']} 面），捲起處擋得住、平段可以踩上去",
                sockets_blender_xyz={}, build_origin_m=[0.0, 0.0, 0.0],
                review_cams_build_xyz=[{'name': c['name'], 'from': [round(v, 3) for v in c['from_']], 'at': [round(v, 3) for v in c['at']], 'lens_mm': c['lens']} for c in cams],
                ruler_build_xy=[round(lo[0] - .45, 3), round(hi[1] + .5, 3)], length_build_m=round(dims[0], 3),
                external_assets=['樹皮法線、苔、褐腐、內壁、土：DR08_Shared（B 自製手繪平鋪貼圖，見 DR08 README）', '樹皮顏色、淺色新斷木：DR09_Shared（Codex 畫，見 DR09 README）'])
    if render:
        pv = _exec(ROOTS + '/preview_dr.py', 'preview_dr')
        pv['setup'](samples=samples, fog=False)
        hm = G('DR_Human_1p75m')
        if hm:
            hm.location = (lo[0] - .45, hi[1] + .5, .875)

        def show(names):
            for o in bpy.data.objects:
                if o.type == 'MESH' and not o.name.startswith('DR_'):
                    o.hide_render = o.name not in names
        show({lods[0].name})
        R = max(X, Y) * 1.15 + 1.0
        cz = H * .4
        vj = []
        dirs = [('01_front', (0, -1, 0)), ('02_right', (1, 0, 0)), ('03_rear', (0, 1, 0)), ('04_left', (-1, 0, 0)),
                ('05_front_right', (1, -1, 0)), ('06_rear_right', (1, 1, 0)), ('07_rear_left', (-1, 1, 0)), ('08_front_left', (-1, -1, 0)),
                ('09_top', (0, -.001, 1)), ('10_high_front', (0, -1, 1.1))]
        for nm, d in dirs:
            d = Vector(d).normalized()
            loc = d * R + Vector((0, 0, cz + (.3 if d.z == 0 else 0)))
            pv['shot'](f'{PRE}/turnaround/{nm}.png', tuple(loc), (0, 0, cz), 50, res=(1024, 1024))
            vj.append(dict(name=nm, direction=list(d), camera=[round(c, 3) for c in loc], lens_mm=50, file=f'turnaround/{nm}.png', mesh='LOD0'))
        json.dump(dict(asset=asset, version=VER, views=vj, note='遊戲模型 LOD0；白柱是 1.75 m 人形尺；相機座標以原點（底部中心）為準'),
                  open(f'{PRE}/turnaround/views.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        cd = {c['name']: c for c in cams}
        for lv in (0, 1, 2):
            show({lods[lv].name})
            for n in ('side', 'tq'):
                c = cd[n]
                pv['shot'](f'{PRE}/{asset}_LOD{lv}_{n}.png', c['from_'], c['at'], c['lens'])
        show({lods[0].name})
        for n in ('curl', 'teeth', 'end', 'top', 'back'):
            c = cd[n]
            pv['shot'](f'{PRE}/{asset}_LOD0_{n}.png', c['from_'], c['at'], c['lens'])
        col.hide_render = False
        cm = bpy.data.materials.get('DR_CollisionPreview') or bpy.data.materials.new('DR_CollisionPreview')
        cm.diffuse_color = (.2, .6, 1, 1)
        col.data.materials.clear()
        col.data.materials.append(cm)
        show({col.name})
        pv['shot'](f'{PRE}/{asset}_collision_tq.png', cd['tq']['from_'], cd['tq']['at'], cd['tq']['lens'])
        col.hide_render = True
    info['files_sha256'] = {os.path.basename(p): sha(p) for p in (fbx, f'{EXP}/{asset}_{VER}.glb') if os.path.exists(p)}
    json.dump(info, open(f'{EXP}/model_info.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    json.dump(val, open(f'{EXP}/validation.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(json.dumps({k: val[k] for k in ('bounds_main', 'spec_check', 'thickness_lod0', 'normals_lod0', 'tris', 'lod_ratio', 'checks', 'all_pass')}, indent=1, ensure_ascii=False))
    return val


if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    report(a[0] if a else 'BarkL', render='norender' not in a)
    print('REPORT_DONE')
