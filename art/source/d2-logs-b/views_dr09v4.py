# DR09 v004 對照用渲染：固定鏡位（不依模型大小調整），v002 與 v004 用同一組鏡頭，才能直接比較。
#   front：正交、從 -Y 平視（參考三視圖的側視是正交平視），正交寬 6.4 m，人形尺 1.75 m 固定在 x = -3.0
#   top  ：正交、正上方，正交寬 6.4 m
#   tq   ：透視、斜 45°、人眼高 1.7 m，距離固定
# 模式：clay = 本體換淺灰＋深色線框，不顯示落葉卡；mat = 遊戲材質＋落葉卡
# 用法：blender -b <blend> --python art/source/d2-logs-b/views_dr09v4.py -- L <v002|v004|v004_greybox> <clay|mat> [samples]
# 輸出 art/previews/d2-logs-b/<物件>/v004/<物件>_<tag>_<mode>_<view>.png（只開檔渲染，不存檔）
import bpy, sys, os
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
ROOT = os.path.abspath(HERE + '/../../..').replace('\\', '/')


def _load(p):
    g = {'__file__': p, '__name__': os.path.basename(p)[:-3]}
    exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), g)
    return g


def mat(name, rgb, rough=.8):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Roughness'].default_value = rough
    return m


def run(v, tag, mode, samples=32):
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
        clay = mat('V4_Clay', (.62, .60, .57))
        body.data.materials.clear()
        body.data.materials.append(clay)
    if mode == 'clay' and not os.environ.get('DR9NOWIRE'):   # v017：DR9NOWIRE=1 → 純灰材質、不加線框
        w = body.copy()
        w.data = body.data.copy()
        w.name = 'V4_Wire'
        bpy.context.scene.collection.objects.link(w)
        md = w.modifiers.new('wire', 'WIREFRAME')
        md.thickness = .003
        md.use_replace = True
        w.data.materials.clear()
        w.data.materials.append(mat('V4_WireMat', (.06, .06, .06), .9))
        w.hide_render = False
    if mode == 'sil':                    # v013：輪廓疊圖用的剪影（白色自發光本體、黑背景、不顯示地面與人形）
        sil = bpy.data.materials.new('V13_Sil')
        sil.use_nodes = True
        nt = sil.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        em = nt.nodes.new('ShaderNodeEmission')
        em.inputs['Strength'].default_value = 1.0
        outn = nt.nodes.new('ShaderNodeOutputMaterial')
        nt.links.new(em.outputs[0], outn.inputs[0])
        body.data.materials.clear()
        body.data.materials.append(sil)
        for o in bpy.data.objects:
            if o.type == 'MESH' and o.name != body.name:
                o.hide_render = True
        wd = bpy.context.scene.world
        wd.use_nodes = True
        for n in wd.node_tree.nodes:
            if n.type == 'BACKGROUND':
                n.inputs['Strength'].default_value = 0.0
        bpy.context.scene.view_settings.view_transform = 'Standard'
    cam = bpy.data.objects.get('DR_Cam')
    if cam is None:
        cam = bpy.data.objects.new('DR_Cam', bpy.data.cameras.new('DR_Cam'))
        bpy.context.scene.collection.objects.link(cam)
    hm = bpy.data.objects.get('DR_Human_1p75m')
    out = f"{ROOT}/art/previews/d2-logs-b/{asset}/{os.environ.get('DR9OUT', 'v004')}/"   # v005 起用 DR9OUT=v005 輸出到該版資料夾
    os.makedirs(out, exist_ok=True)
    shots = {   # 位置, 目標, 正交寬（None = 透視）, 焦段, 解析度, 人形尺位置
        'front': ((-.6, -20, .75), (-.6, 0, .75), 6.4, 50, (1536, 600), (-3.0, .6, .875)),
        'top': ((0, -.001, 20), (0, 0, 0), 6.4, 50, (1280, 800), None),
        'tq': ((-7.8 * .62, -7.8 * .78, 1.7), (0, 0, .35), None, 40, (1536, 1024), None),
    }
    if os.environ.get('DR9CLOSE'):      # v012 起：中上層近景（透視），目標點用模型座標，扣掉底部置中的平移
        pv_ = Vector(bpy.context.scene.get('dr_pivot', (0.0, 0.0, 0.0)))
        tx, ty, tz = (float(v) for v in os.environ['DR9CLOSE'].split(','))
        t_ = Vector((tx, ty, tz)) - pv_
        off_ = Vector(tuple(float(v) for v in os.environ.get('DR9CLOSEOFF', '-1.25,-2.35,.95').split(',')))   # 鏡頭相對目標點的位移
        shots = {'close': (tuple(t_ + off_), tuple(t_), None, 35, (1536, 1024), None)}
    for name, (loc, tgt, osc, lens, res, human) in shots.items():
        if hm:
            hm.hide_render = human is None or mode == 'sil'
            if human:
                hm.location = human
        if osc:
            cam.data.type = 'ORTHO'
            cam.data.ortho_scale = osc
        else:
            cam.data.type = 'PERSP'
        pv['shot'](f'{out}{asset}_{tag}_{mode}_{name}.png', loc, tgt, lens, res=res)
    print('VIEWS_DONE', out, tag, mode)


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:]
    run(a[0], a[1], a[2], int(a[3]) if len(a) > 3 else 32)
