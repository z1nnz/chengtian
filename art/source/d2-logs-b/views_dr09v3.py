# DR09 v003 預覽：正面（-Y）、側面（+X 看過去）、俯視、四分之三（斜 45°、人眼高 1.7 m）。
#   clay：灰模（本體換成淺灰材質＋深色線框，落葉卡不顯示），看輪廓、堆疊、接地與佈線。
#   mat ：材質預覽（遊戲材質＋落葉卡）。
# 用法：blender -b art/source/d2-logs-b/blend/DR09_BranchPile_L_v003.blend --python art/source/d2-logs-b/views_dr09v3.py -- L clay
# 輸出 art/previews/d2-logs-b/<物件>/v003/<物件>_<clay|mat>_<view>.png（只開檔渲染，不存檔）
import bpy, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
ROOT = os.path.abspath(HERE + '/../../..').replace('\\', '/')


def _load(p):
    g = {'__file__': p, '__name__': os.path.basename(p)[:-3]}
    exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), g)
    return g


def mat(name, rgb, rough=.8, emit=False):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Roughness'].default_value = rough
    return m


def run(v, mode, samples=48):
    asset = f'DR09_BranchPile_{v}'
    root = bpy.data.objects[asset]
    root.location = (0, 0, 0)
    bpy.context.view_layer.update()
    pv = _load(HERE + '/../d2-roots-b/preview_dr.py')
    pv['setup'](samples=samples, fog=False)
    gm = bpy.data.materials['DR_Mud']
    for n in gm.node_tree.nodes:
        if n.type == 'VALTORGB':
            n.color_ramp.elements[0].color = (.42, .40, .37, 1)
            n.color_ramp.elements[1].color = (.46, .44, .41, 1)
    body = bpy.data.objects[f'{asset}_LOD0']
    keep = {body.name} | ({'Detail_DR09_Leaves_LOD0'} if mode == 'mat' else set())
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.name not in keep and not o.name.startswith('DR_'):
            o.hide_render = True
    if mode == 'clay':
        clay = mat('V3_Clay', (.62, .60, .57))
        body.data.materials.clear()
        body.data.materials.append(clay)
        w = body.copy()
        w.data = body.data.copy()
        w.name = 'V3_Wire'
        bpy.context.scene.collection.objects.link(w)
        md = w.modifiers.new('wire', 'WIREFRAME')
        md.thickness = .0035
        md.use_replace = True
        w.data.materials.clear()
        w.data.materials.append(mat('V3_WireMat', (.05, .05, .05), .9))
        w.hide_render = False
    bpy.context.view_layer.update()
    bb = [body.matrix_world @ Vector(c) for c in body.bound_box]
    L = max(p.x for p in bb) - min(p.x for p in bb)
    W = max(p.y for p in bb) - min(p.y for p in bb)
    H = max(p.z for p in bb)
    hm = bpy.data.objects.get('DR_Human_1p75m')
    out = f'{ROOT}/art/previews/d2-logs-b/{asset}/v003/'
    os.makedirs(out, exist_ok=True)
    d = L * 1.45 + 1.4
    shots = {
        'front': ((-.35, -(L + 1.8) * 1.55, H * .55 + .12), (-.35, 0, H * .45), 50, (1536, 768), (-L / 2 - .7, .3, .875)),
        'side': (((W + 1.6) * 1.9, 0, H * .55 + .12), (0, 0, H * .45), 50, (1536, 768), (0, -W / 2 - .7, .875)),
        'top': ((0, -.01, max(L, W * 1.5) * 2.3 + 1), (0, 0, 0), 50, (1280, 960), None),
        'tq': ((-d * .62, -d * .78, 1.7), (0, 0, H * .35), 40, (1536, 1024), None),
    }
    for name, (loc, tgt, lens, res, human) in shots.items():
        if hm:
            hm.hide_render = human is None
            if human:
                hm.location = human
        pv['shot'](f'{out}{asset}_{mode}_{name}.png', loc, tgt, lens, res=res)
    print('VIEWS_DONE', out, mode)


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:]
    run(a[0], a[1], int(a[2]) if len(a) > 2 else 48)
