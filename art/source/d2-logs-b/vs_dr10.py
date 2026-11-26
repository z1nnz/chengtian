# DR10 「成品 vs 參考圖」並排圖用的成品渲染。參考圖 art/references/DR10/v001/DR10-threeview.png 是 A 正面、A 側面、B 正面、B 側面
# 四張並排（同比例、有 1.75 m 人形）；這裡用長鏡頭（近似正交）從正面、側面各拍一張，A、B 同一個鏡頭距離和焦距，比例一致。
# 另外照 DR10-threequarter.png 估一個仰看的四分之三鏡位（參考圖沒有相機資料，鏡位是對著畫面估的，不是量出來的）。
# 用法（Blender 背景模式，開遊戲 blend）：
#   blender -b art/source/d2-logs-b/blend/DR10_DeadSnag_A_v001.blend --python art/source/d2-logs-b/vs_dr10.py -- A
# 輸出 art/previews/d2-logs-b/<物件>/<物件>_LOD0_refcam_{front,side,tq}.png；再用 compose_dr10.py 和參考圖並排。
import bpy, sys, os, math

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
R2 = HERE + '/../d2-roots-b'
ROOT = os.path.abspath(HERE + '/../../..').replace('\\', '/')
ASSETS = {'A': 'DR10_DeadSnag_A', 'B': 'DR10_DeadSnag_B'}
ORTHO = dict(dist=80.0, lens=180, z=7.6, res=(768, 1024))         # A、B 同一組：畫面高約 16 m，地面在同一條線


def _load(p):
    g = {'__file__': p, '__name__': os.path.basename(p)[:-3]}
    exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), g)
    return g


def run(v, samples=64):
    asset = ASSETS[v]
    b = _load(HERE + '/build_dr10.py')
    V = b['set_variant'](v)
    pv = _load(R2 + '/preview_dr.py')
    dp = _load(R2 + '/dr_pivot.py')
    dp['frame'](asset, True)
    pv['setup'](samples=samples, fog=False)
    hm = bpy.data.objects.get('DR_Human_1p75m')
    keep = {f'{asset}_LOD0', 'Detail_DR10_Plants_LOD0', 'DR_Human_1p75m'}
    for o in bpy.data.objects:
        if o.type == 'MESH' and not o.name.startswith('DR_'):
            o.hide_render = o.name not in keep
    cx, cy = b['axis_xy'](V, 0.0)
    pre = f'{ROOT}/art/previews/d2-logs-b/{asset}'
    os.makedirs(pre, exist_ok=True)
    for tag, d, side in (('front', (0, -1), (1, 0)), ('side', (1, 0), (0, 1))):
        if hm:                                          # 人形尺放在樹幹右邊（畫面上），參考圖也是人在兩棵中間
            hm.location = (cx + side[0] * (V['R'] * 2.6 + .6), cy + side[1] * (V['R'] * 2.6 + .6), .875)
        frm = (cx + d[0] * ORTHO['dist'], cy + d[1] * ORTHO['dist'], ORTHO['z'])
        pv['shot'](f'{pre}/{asset}_LOD0_refcam_{tag}.png', frm, (cx, cy, ORTHO['z']), ORTHO['lens'], res=ORTHO['res'])
    # 四分之三仰看：參考圖從人眼高、約 15 m 外看，兩棵都整棵入鏡
    if hm:
        hm.location = (cx + V['R'] * 2.6 + .6, cy - V['R'] * 1.5, .875)
    H1 = V['H'][1]
    frm = (cx - H1 * .75, cy - H1 * 1.25, 1.7)
    pv['setup'](samples=samples, fog=True)
    pv['shot'](f'{pre}/{asset}_LOD0_refcam_tq.png', frm, (cx, cy, H1 * .50), 28, res=(1536, 1024))
    dp['frame'](asset, False)
    print('VS_DONE', pre)


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:]
    run(a[0], int(a[1]) if len(a) > 1 else 64)
