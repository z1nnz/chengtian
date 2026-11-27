# DR11 翻起的倒樹根盤的遊戲用模型：低模 → 拆 UV → 烘焙 → 植物 → LOD1／LOD2 → 碰撞 → FBX／GLB。
# 整套沿用 game_dr06.py（再往下是 D2 根與木的 game_dr02.py），照 game_dr10.py 的作法只換：
#   - 高模腳本換成 build_dr11.py（根盤零件本來就是 DR06 的，集合名沿用 DR06_<變體名>_High／Low）；
#   - 苔：頂上苔皮（MossCap）高模、低模都有，苔色烘進貼圖；垂苔細絲（HangMoss）與苔絲（MossFuzzCap／MossFuzzHang）
#     只在高模，烘焙時加進每一組低模的來源 → 垂苔、苔絲的顏色與法線烘在根面、苔皮的貼圖上，不進遊戲網格；
#   - 植物：dress11（頂上草、兩側腳下蕨、坑邊蕈、坑裡落葉），草借用圖集裡「闊葉」那一格（DR11 沒有闊葉、小樹苗），改畫草色。
# 用法（背景）：blender -b --python game_dr11.py -- A 24（B 同）
import os, sys

_HERE11 = 'D:/yun-jing-d2-logs/art/source/d2-logs-b'
_src6 = _HERE11 + '/game_dr06.py'
_txt6 = open(_src6, encoding='utf-8').read()
EXTRA_SRC = ('MossCap', 'HangMoss', 'MossFuzzCap', 'MossFuzzHang', 'Hair')     # 第二版：苔皮、根鬚也只烘進貼圖（低模沒有這些件）
for _a, _b in (("            src = [highs[n] for n in low['srcs'] if n in highs]",
                "            src = [highs[n] for n in low['srcs'] if n in highs] + [o for n_, o in highs.items() if n_.startswith(EXTRA_SRC) and _near(o, low)]"),
               ("        coll = b['dress'](b['VAR'], quick=True, game=True, surf=(low.name,))",
                "        coll = b['dress11'](b['VAR'], quick=True, game=True, surf=(low.name,))"),
               ("        b['dress'](b['VAR'], quick=False)", "        b['dress11'](b['VAR'], quick=False)"),
               ("        elif 'Heart' in n:", "        elif 'HangMoss' in n:\n            grp = 'Sapling'\n        elif 'Heart' in n or 'Grass' in n:"),
               # 第二版：根鬚在遊戲版是一根根硬棍 → 不放進植物網格，改烘進根面貼圖
               ("    highs = {o.name: o for o in hi_c.objects if not o.name.startswith('Hair')}", "    highs = {o.name: o for o in hi_c.objects}"),
               ("    for h in bpy.data.collections[_cn('HairLow')].objects:", "    for h in []:"),
               # 第二版：分部位 UV 權重（照 game_dr10.py）：根面、泥丘、根面粗根拿多一點像素；坑、土塊、背面短樹幹、圓頂根少一點
               ("            _smart_uv(o)\n        o.data.materials.clear()", "            _smart_uv(o)\n        _uv_weight(o)\n        o.data.materials.clear()")):
    assert _txt6.count(_a) == 1, _a
    _txt6 = _txt6.replace(_a, _b)

def _near(o, low, pad=.35):
    """第三版：苔、根鬚只加進外框和這組低模重疊（放寬 pad 公尺）的那幾組來源；第二版每組都算全部，烘焙要 3 小時。"""
    from mathutils import Vector as _V
    key = '_bb_' + o.name
    if key not in _BB:
        _BB[key] = _bbox(o)
    lo1, hi1 = _bbox(low)
    lo2, hi2 = _BB[key]
    return all(lo1[i] - pad <= hi2[i] and lo2[i] <= hi1[i] + pad for i in range(3))


_BB = {}


def _bbox(o):
    import numpy as _np
    co = _np.empty(len(o.data.vertices) * 3, _np.float32)
    o.data.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    M = _np.array(o.matrix_world)
    w = co @ M[:3, :3].T + M[:3, 3]
    return w.min(0), w.max(0)


UV_WEIGHT = (('Pit', .35), ('Clods', .45), ('Trunk', .55), ('Snap_', .55), ('DomeRoot', .50), ('Brackets', .50),
             ('Stones', .60), ('PlateRoot', .75), ('Root', .80))


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

VER = os.environ.get('DR11_VER', 'v001')            # v002：B 根盤根系貼土重整（g40–g42）後重烘；用 DR11_VER=v002 跑
NAMES = {'A': 'DR11_RootPlate_A', 'B': 'DR11_RootPlate_B'}
DET = 'Detail_DR11_Plants'
LEAF['Sapling'] = (LEAF['Sapling'][0], LEAF['Sapling'][1], (.025, .045, .015), (.10, .15, .05))     # 這一格畫垂苔、苔片（深綠；第二版偏淺）
LEAF['Leaves'] = (LEAF['Leaves'][0], LEAF['Leaves'][1], (.12, .17, .06), (.30, .37, .15))      # 這一格畫草（暗 → 亮，sRGB）


def configure(v):
    global VARIANT, ASSET, EXP, TEX, WORKTEX
    VARIANT = v
    ASSET = NAMES[v]
    EXP = f'{ROOT}/art/exports/d2-logs-b/{ASSET}'
    TEX = EXP + '/Textures'
    WORKTEX = os.environ.get('DR_WORK11', 'D:/yun-jing-cache/dr11-work/') + f'bake_{v}'
    if VER != 'v001':                                 # 新版本貼圖、烘焙暫存分開放，不覆蓋 v001
        TEX += '_' + VER
        WORKTEX += '_' + VER


def _build():
    global B
    if B is None:
        p = HERE6 + '/build_dr11.py'
        B = {'__file__': p, '__name__': 'build_dr11'}
        exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), B)
    B['set_variant'](VARIANT)
    return B


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
