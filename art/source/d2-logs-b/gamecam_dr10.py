# DR10 第七輪：用遊戲相機條件看斷頂與縱裂（遊戲模型 LOD0／LOD1／LOD2，實際貼圖）。
# 相機照 apps/game/Assets/YunJing/Runtime/QingxiOrbitCamera.cs：焦點在角色腳下 + 1.45 m、離焦點 6.5 m（可 3.5–9 m）、俯仰 -15°～65°；
# Unity 相機預設垂直 FOV 60°；輸出 1280×720（ProjectSettings defaultScreenWidth／Height）。
# LOD 切換照 unity/D2LogsVerify.cs 的 LODGroup 門檻 0.25／0.08／0.015（畫面相對高度 = 物件大小 ÷ (2·距離·tan 30°)，以最大邊估算）。
# 用法：blender -b art/source/d2-logs-b/blend/DR10_DeadSnag_A_v001.blend --python art/source/d2-logs-b/gamecam_dr10.py -- A <輸出資料夾> [clay]
import bpy, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
R2 = HERE + '/../d2-roots-b'
ASSETS = {'A': 'DR10_DeadSnag_A', 'B': 'DR10_DeadSnag_B'}
VFOV = 60.0
RES = (1280, 720)
ORBIT, FOCUS_H = 6.5, 1.45


def _load(p):
    g = {'__file__': p, '__name__': os.path.basename(p)[:-3]}
    exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), g)
    return g


def lod_for(size, d):
    rel = size / (2 * d * math.tan(math.radians(VFOV / 2)))
    return (0 if rel > .25 else (1 if rel > .08 else 2)), rel


def render(path, loc, tgt, vfov=VFOV, res=RES):
    sc = bpy.context.scene
    cam = bpy.data.objects.get('DR_Cam')
    if cam is None:
        cam = bpy.data.objects.new('DR_Cam', bpy.data.cameras.new('DR_Cam'))
        sc.collection.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    cam.data.sensor_fit = 'VERTICAL'
    cam.data.angle = math.radians(vfov)
    cam.data.clip_end = 500
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def run(v, out, clay=False):
    asset = ASSETS[v]
    b = _load(HERE + '/build_dr10.py')
    V = b['set_variant'](v)
    pv = _load(R2 + '/preview_dr.py')
    dp = _load(R2 + '/dr_pivot.py')
    dp['frame'](asset, True)
    pv['setup'](samples=48, fog=False)
    if clay:
        m = bpy.data.materials.new('DR10_Clay')
        m.use_nodes = True
        bb = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        bb.inputs['Base Color'].default_value = (.20, .19, .18, 1)
        bb.inputs['Roughness'].default_value = .8
        bpy.context.view_layer.material_override = m
    os.makedirs(out, exist_ok=True)
    lod0 = bpy.data.objects[f'{asset}_LOD0']
    size = max(lod0.dimensions)
    cx, cy = b['axis_xy'](V, 0.0)
    H0 = V['H'][0]
    tag = 'clay' if clay else 'mat'

    def show(lod):
        for o in bpy.data.objects:
            if o.type == 'MESH' and not o.name.startswith('DR_'):
                o.hide_render = not (o.name.endswith(f'_LOD{lod}') and (o.name.startswith(asset) or o.name.startswith('Detail_')))
        hm = bpy.data.objects.get('DR_Human_1p75m')
        if hm:
            hm.hide_render = True

    log = []
    # 遊戲距離：角色站在離樹 D − 6.5 m，鏡頭仰 10°（往上看樹頂）；方位：正面（-Y）與四分之三（-X -Y）
    for az_name, az in (('front', -math.pi / 2), ('tq', -math.pi * .75)):
        for D in (16.0, 26.0, 36.0):
            pitch = math.radians(-10.0)                       # 負＝往上看（Unity pitch 往下為正）
            camz = FOCUS_H - ORBIT * math.sin(pitch)
            cam = (cx + math.cos(az) * D, cy + math.sin(az) * D, max(.3, camz))
            dirv = Vector((-math.cos(az) * math.cos(pitch), -math.sin(az) * math.cos(pitch), -math.sin(pitch)))
            tgt = Vector(cam) + dirv * 10
            lod, rel = lod_for(size, D)
            show(lod)
            p = f'{out}/DR10_{v}_game_{tag}_{az_name}_{int(D)}m_LOD{lod}.png'
            render(p, cam, tgt)
            log.append((os.path.basename(p), round(rel, 3)))
    # LOD 對照：同一鏡位（正面 16 m）放大到斷頂（垂直 FOV 12°），LOD0／1／2 各一張
    D = 16.0
    camz = FOCUS_H - ORBIT * math.sin(math.radians(-10.0))
    cam = (cx, cy - D, camz)
    tz = H0 + .9
    tx, ty = b['axis_xy'](V, tz)
    for lod in (0, 1, 2):
        show(lod)
        render(f'{out}/DR10_{v}_game_{tag}_lodzoom_LOD{lod}.png', cam, (tx, ty, tz), vfov=16.0, res=(960, 720))
    # 背面（+Y）放大：另一側的主要縱裂在輪廓上
    cam = (cx, cy + D, camz)
    for lod in (0, 1):
        show(lod)
        render(f'{out}/DR10_{v}_game_{tag}_lodzoom_back_LOD{lod}.png', cam, (tx, ty, tz), vfov=16.0, res=(960, 720))
    dp['frame'](asset, False)
    for l_ in log:
        print('GAMECAM', *l_)
    print('GAMECAM_DONE', out, 'size', round(size, 2))


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:]
    run(a[0], a[1], 'clay' in a[2:])
