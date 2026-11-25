# DR09 v002 起「成品 vs 參考圖」用的成品渲染：正面平視（-Y，人形尺在左，照參考三視圖側視那一格）＋正上俯視。
# 參考圖沒有相機資料，鏡位是對著畫面估的；參考圖側視是貼地平視，所以鏡頭放低（約堆高的一半），不從上往下看（會把高度壓扁）。地面換成淺暖灰（參考圖是淺暖灰底、陰天均勻光），只為了比顏色，不是場景燈光。
# 用法：blender -b art/source/d2-logs-b/blend/DR09_BranchPile_L_v002.blend --python art/source/d2-logs-b/vs_dr09.py -- L
# 輸出 art/previews/d2-logs-b/<物件>/v002/<物件>_LOD0_{front,top}.png；再用 compose_dr09v2.py 和參考圖並排。
import bpy, sys, os

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
R2 = HERE + '/../d2-roots-b'
ROOT = os.path.abspath(HERE + '/../../..').replace('\\', '/')


def _load(p):
    g = {'__file__': p, '__name__': os.path.basename(p)[:-3]}
    exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), g)
    return g


def run(v, samples=64):
    asset = f'DR09_BranchPile_{v}'
    ver = os.environ.get('DR9VER', 'v002')
    root = bpy.data.objects[asset]
    root.location = (0, 0, 0)
    bpy.context.view_layer.update()
    pv = _load(R2 + '/preview_dr.py')
    pv['setup'](samples=samples, fog=False)
    gm = bpy.data.materials['DR_Mud']
    for n in list(gm.node_tree.nodes):
        if n.type == 'VALTORGB':
            n.color_ramp.elements[0].color = (.42, .40, .37, 1)
            n.color_ramp.elements[1].color = (.46, .44, .41, 1)
    keep = {f'{asset}_LOD0', 'Detail_DR09_Leaves_LOD0'}
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.name not in keep and not o.name.startswith('DR_'):
            o.hide_render = True
    body = bpy.data.objects[f'{asset}_LOD0']
    xs = [(body.matrix_world @ __import__('mathutils').Vector(c)) for c in body.bound_box]
    L = max(p.x for p in xs) - min(p.x for p in xs)
    W = max(p.y for p in xs) - min(p.y for p in xs)
    H = max(p.z for p in xs)
    hm = bpy.data.objects.get('DR_Human_1p75m')
    if hm:
        hm.location = (-L / 2 - .7, .3, .875)
    out = f'{ROOT}/art/previews/d2-logs-b/{asset}/{ver}/'
    os.makedirs(out, exist_ok=True)
    w = L + 1.8
    cx = -.45
    pv['shot'](out + f'{asset}_LOD0_front.png', (cx, -w * 1.55, H * .55 + .12), (cx, 0, H * .45), 50, res=(1536, 640))
    if hm:
        hm.hide_render = True
    d = L * 1.45 + 1.4                      # 斜 45°、人眼高 1.7 m（參考情境圖 DR09-threequarter 的看法）
    pv['shot'](out + f'{asset}_LOD0_tq.png', (-d * .62, -d * .78, 1.7), (0, 0, H * .35), 40, res=(1536, 1024))
    pv['shot'](out + f'{asset}_LOD0_top.png', (0, -.01, max(L, W * 1.5) * 2.4 + 1), (0, 0, 0), 50, res=(1280, 960))
    print('VS_DONE', out)


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:]
    run(a[0], int(a[1]) if len(a) > 1 else 64)
