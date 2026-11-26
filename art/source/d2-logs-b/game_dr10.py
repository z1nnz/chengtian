# DR10 枯立木的遊戲用模型：低模 → 拆 UV → 烘焙 → 植物 → LOD1／LOD2 → 碰撞 → FBX／GLB。
# 整套沿用 game_dr06.py（再往下是 D2 根與木的 game_dr02.py），照 game_dr07.py 的作法只換：
#   - 高模腳本換成 build_dr10.py，物件／集合名前綴 DR10_；
#   - 「藏起來的面」：外殼、心材、斷面彼此不算擋住（頂上斷口朽空，從上面看得到）；
#   - 樹皮遮罩：DR10 自己那份樹皮材質（DR10_Bark）也算樹皮；
#   - 斷口木刺、捲起的木片改用淺奶油灰的色條（參考圖的新鮮斷刺），不是 DR07 的橘褐朽木。
# 用法（背景）：blender -b --python game_dr10.py -- A 24（B 同）
import os, sys

_HERE10 = 'D:/yun-jing-d2-logs/art/source/d2-logs-b'
_src6 = _HERE10 + '/game_dr06.py'
_txt6 = open(_src6, encoding='utf-8').read()
for _a, _b in (("('ring', 'Peel', 'MudMoss')", "('ring', 'Peel', 'MudMoss', 'EndMoss')"),
               ("m.name.startswith('DR06_Bark')", "m.name.startswith(('DR06_Bark', 'DR05_Bark', 'DR07_Bark', 'DR10_Bark'))"),
               ("'DR06_LowG", "'DR10_LowG"), ("f'DR06_LowG", "f'DR10_LowG"),
               ("o.name.startswith('DR06_LowG')", "o.name.startswith('DR10_LowG')"),
               ("            _smart_uv(o)\n        o.data.materials.clear()",          # 第五輪：分部位 UV 權重（排 UV 前縮放）
                "            _smart_uv(o)\n        _uv_weight(o)\n        o.data.materials.clear()"),
               ("    for kind, btype, color, kw in (('BaseColor'",       # 第五輪：AO 只算 0.6 m 內（預設 10 m：裸木凹在樹皮唇下，整根樹幹都算進遮蔽，Unity 裡裸木 AO 平均 0.57）
                "    if sc.world is None:\n        sc.world = bpy.data.worlds.new('DR10_BakeWorld')\n    sc.world.light_settings.distance = AO_DIST\n"
                "    print('AO distance', sc.world.light_settings.distance)\n    for kind, btype, color, kw in (('BaseColor'"),
               ("uvo[sl, 0] = a0 + (a1 - a0) * (.08 + .84 * su[vi[sl]])",      # 每片木片（36–42 個頂點）尖端深淺不同
                "uvo[sl, 0] = a0 + (a1 - a0) * np.clip(.08 + .84 * su[vi[sl]] * (.45 + .55 * ((vi[sl] // 36 * .618034) % 1.0)), 0, .92)")):
    assert _a in _txt6 or _b in _txt6, _a
    _txt6 = _txt6.replace(_a, _b)
# 第五輪：UV 權重。原本所有件同一個 px/m，地面、碎石、心材內壁、細根吃掉大量圖集面積。
# 排 UV 前把每件的 UVMap 乘上權重（線性），pack_islands 再整體放大：近看會注意到的樹幹外殼、斷頂木束、主根拿到較多像素。
# 樹皮和裸木在同一個樹幹 UV 上，密度相同（裸木只是剝皮處的同一張圖）。TileUV（細節法線重複）不受影響。
UV_WEIGHT = (('Ground', .40), ('Stones', .45), ('Pebble', .45), ('Inner', .55), ('Rootlet', .60), ('Hole', .70),
             ('Root', .90), ('Limb', .90), ('Twig', .80), ('Flake', .80), ('Splinter', .80))


def _uv_weight(o):
    import numpy as _np
    nm = o.name[2:] if o.name.startswith('L_') else o.name
    w = next((k for key, k in UV_WEIGHT if nm.startswith(key)), 1.0)
    o['uv_weight'] = w
    if w == 1.0:
        return
    la = o.data.uv_layers['UVMap']
    uv = _np.empty(len(la.data) * 2, _np.float32)
    la.data.foreach_get('uv', uv)
    la.data.foreach_set('uv', uv * w)


_nm = globals().get('__name__')
globals()['__name__'] = 'game_dr06_lib'             # 不要跑 DR06 的主程式
exec(compile(_txt6, _src6, 'exec'), globals())
globals()['__name__'] = _nm

NAMES = {'A': 'DR10_DeadSnag_A', 'B': 'DR10_DeadSnag_B'}
_finish_textures6, _make_detail6 = finish_textures, make_detail


def _mush10():
    """第七輪：蕈改用 DR10 專用生成器，遊戲版的平塗色塊也換成它的調色盤（14 格；共用 game_dr06 的預設 5 格不變）。"""
    global MUSH, MUSH_PAINT
    MUSH = MUSH_PAINT = list(_build()['MUSH10'])


def finish_textures():
    _mush10()
    _finish_textures6()


def make_detail():
    _mush10()
    _make_detail6()

AO_DIST = .6                                    # 第五輪：烘焙 AO 的距離（公尺）
DET = 'Detail_DR10_Plants'
SHELL = ('Trunk', 'Inner', 'Rim0')
LOWRES = (.14, 6, 48, 1.0)                      # 低模：每 0.14 m 一環；細梢 6 邊、樹幹最多 48 邊
SHARD_C = ((.30, .27, .22), (.74, .68, .57))      # 斷口的木刺：根部灰褐 → 尖端淺奶油灰（參考圖）


def configure(v):
    global VARIANT, ASSET, EXP, TEX, WORKTEX
    VARIANT = v
    ASSET = NAMES[v]
    EXP = f'{ROOT}/art/exports/d2-logs-b/{ASSET}'
    TEX = EXP + '/Textures'
    WORKTEX = os.environ.get('DR_WORK10', 'D:/yun-jing-cache/dr10-work/') + f'bake_{v}'


def _build():
    global B
    if B is None:
        p = HERE6 + '/build_dr10.py'
        B = {'__file__': p, '__name__': 'build_dr10'}
        exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), B)
    B['set_variant'](VARIANT)
    return B


def _cn(kind):
    return f"DR10_{_build()['VAR']['name']}_{kind}"


def _hidden_verts(objs, margin=.03, zcut=-.5):
    """外殼、心材、斷面兩兩之間不互相判斷（從上面看得到心材朽空）；其他件照 DR06。"""
    from mathutils.bvhtree import BVHTree
    from mathutils import Vector
    import numpy as np
    base = lambda o: o.name.split('_', 1)[1] if o.name.startswith(('L_', 'C_', 'F_')) else o.name
    shell = [base(o) in SHELL for o in objs]
    dirs = [Vector(d) for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]
    data = []
    for o in objs:
        co = np.array([v.co[:] for v in o.data.vertices])
        t = BVHTree.FromPolygons([Vector(c) for c in co], [tuple(p.vertices) for p in o.data.polygons])
        data.append((co, t, co.min(0), co.max(0)))
    out = []
    for i, o in enumerate(objs):
        co, _, lo_i, hi_i = data[i]
        hide = co[:, 2] < zcut
        for j, (cj, tj, lo, hi) in enumerate(data):
            if j == i or (shell[i] and shell[j]) or (lo_i > hi).any() or (hi_i < lo).any():
                continue
            for vi in np.nonzero(~hide & (co >= lo).all(1) & (co <= hi).all(1))[0]:
                q = Vector(co[vi])
                loc, nrm, idx, dist = tj.find_nearest(q)
                if loc is not None and dist > margin and (q - loc).dot(nrm) < 0 and all(tj.ray_cast(q, d, 50)[0] is not None for d in dirs):
                    hide[vi] = True
        out.append(hide)
    return out


if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    if 'redetail' in a:
        configure(a[0])
        p = Vector(bpy.context.scene.get('dr_pivot', (0.0, 0.0, 0.0)))
        bpy.data.objects[f'{ASSET}_LOD0'].data.transform(Matrix.Translation(p))
        bpy.data.objects.remove(bpy.data.objects[f'{DET}_LOD0'], do_unlink=True)
        bpy.context.scene['dr_pivot'] = [0.0, 0.0, 0.0]
        make_detail()
        refinish(a[0])
    elif 'retex' in a:
        configure(a[0])
        finish_textures()
        refinish(a[0])
    elif 'refinish' in a:
        refinish(a[0])
    else:
        run_all(a[0] if a else 'A', int(a[1]) if len(a) > 1 else 24)
