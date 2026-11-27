# DR11 遊戲版出圖：用遊戲相機條件看根盤（遊戲模型 LOD0／LOD1／LOD2，實際貼圖）。
# 相機與 LOD 門檻照 gamecam_dr10.py（QingxiOrbitCamera：焦點角色腳下 + 1.45 m、離焦點 6.5 m；垂直 FOV 60°；LOD 0.25／0.08／0.015）。
# 根面朝 -X：正面鏡位從 -X 看，四分之三從 -X -Y 看。資產已移到底部中心（dr_pivot），所以用 LOD0 的外框中心瞄準。
# 用法：blender -b art/source/d2-logs-b/blend/DR11_RootPlate_A_v001.blend --python art/source/d2-logs-b/gamecam_dr11.py -- A <輸出資料夾> [clay]
import bpy, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
R2 = HERE + '/../d2-roots-b'
ASSETS = {'A': 'DR11_RootPlate_A', 'B': 'DR11_RootPlate_B'}
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
    pv = _load(R2 + '/preview_dr.py')
    dp = _load(R2 + '/dr_pivot.py')
    dp['frame'](asset, True)
    pv['setup'](samples=48, fog=False)
    if clay:
        m = bpy.data.materials.new('DR11_Clay')
        m.use_nodes = True
        bb = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        bb.inputs['Base Color'].default_value = (.20, .19, .18, 1)
        bb.inputs['Roughness'].default_value = .8
        bpy.context.view_layer.material_override = m
    os.makedirs(out, exist_ok=True)
    lod0 = bpy.data.objects[f'{asset}_LOD0']
    pts = [lod0.matrix_world @ Vector(c) for c in lod0.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    c = (lo + hi) / 2
    size = max(hi - lo)
    tag = 'clay' if clay else 'mat'

    def show(lod):
        for o in bpy.data.objects:
            if o.type == 'MESH' and not o.name.startswith('DR_'):
                o.hide_render = not (o.name.endswith(f'_LOD{lod}') and (o.name.startswith(asset) or o.name.startswith('Detail_')))
        hm = bpy.data.objects.get('DR_Human_1p75m')
        if hm:
            hm.hide_render = True

    log = []
    for az_name, az in (('front', math.pi), ('tq', math.pi * 1.25)):
        for D in (8.0, 16.0, 26.0):
            pitch = math.radians(-10.0)
            camz = FOCUS_H - ORBIT * math.sin(pitch)
            cam = (c.x + math.cos(az) * D, c.y + math.sin(az) * D, max(.3, camz))
            tgt = (c.x, c.y, hi.z * .45)
            lod, rel = lod_for(size, D)
            show(lod)
            p = f'{out}/DR11_{v}_game_{tag}_{az_name}_{int(D)}m_LOD{lod}.png'
            render(p, cam, tgt)
            log.append((os.path.basename(p), round(rel, 3)))
    # LOD 對照：正面 8 m，看根面上半（苔、垂苔、草）
    cam = (c.x - 8.0, c.y - 1.5, 2.2)
    for lod in (0, 1, 2):
        show(lod)
        render(f'{out}/DR11_{v}_game_{tag}_lodzoom_LOD{lod}.png', cam, (c.x, c.y, hi.z * .62), vfov=28.0, res=(960, 720))
    dp['frame'](asset, False)
    for l_ in log:
        print('GAMECAM', *l_)
    print('GAMECAM_DONE', out, 'size', round(size, 2))


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:]
    run(a[0], a[1], 'clay' in a[2:])
