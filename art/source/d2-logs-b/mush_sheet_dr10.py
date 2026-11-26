# DR10 地面蘑菇變體排列圖（第七輪）：上三列＝三個色系 × 幼／成熟／老（各兩株，固定種子）；下一列＝實際成叢（色系 × 階段比例）。
# 用法：blender -b --python art/source/d2-logs-b/mush_sheet_dr10.py -- <輸出資料夾>
import bpy, sys, os, math, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
R2 = HERE + '/../d2-roots-b'


def _load(p):
    g = {'__file__': p, '__name__': os.path.basename(p)[:-3]}
    exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), g)
    return g


out = sys.argv[sys.argv.index('--') + 1]
os.makedirs(out, exist_ok=True)
b = _load(HERE + '/build_dr10.py')
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
pv = _load(R2 + '/preview_dr.py')
pv['setup'](samples=64, fog=False)
mat = bpy.data.materials.get('UG_Mushroom') or b['core_plants'].mushroom_material()
gnd = lambda x, y: 0.0
free = lambda l, r, h: True
k = (.55 + .45 * (1.0 / .5)) ** .5                    # A 的比例（DR10 dress 用 k ** .5）
stats = []
# 變體：每格一株
for fi in range(3):
    for si, stg in enumerate(('young', 'mature', 'old')):
        for j in range(2):
            x = (si * 2 + j) * .32 - .80
            y = fi * .34
            R = random.Random(5000 + fi * 100 + si * 10 + j)
            o = b['mushrooms10'](f'Var_{fi}_{stg}_{j}', Vector((x, y, 0)), R, fi, b['MUSH10_MIX'][1], 1, k, mat, gnd, free, force=stg)
            stats.append((o.name, len(o.data.vertices), round(o.dimensions.z, 3), round(max(o.dimensions.x, o.dimensions.y), 3)))
def ortho(path, loc, tgt, scale, res):
    sc = bpy.context.scene
    cam = bpy.data.objects.get('DR_Cam')
    pv['shot'](path, loc, tgt, 50, res=res)            # 先建好相機與輸出設定
    cam = bpy.data.objects.get('DR_Cam')
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = scale
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    cam.data.type = 'PERSP'


for fi in range(3):                                   # 每個色系一張（正交、略俯視，同比例）
    for o in bpy.data.objects:
        if o.name.startswith('Var_'):
            o.hide_render = not o.name.startswith(f'Var_{fi}_')
    ortho(f'{out}/DR10_mush_variants_{fi}.png', (0, -6.0 + fi * .34, 2.2), (0, fi * .34, .07), 1.95, (1600, 520))
for o in [o for o in bpy.data.objects if o.name.startswith('Var_')]:
    bpy.data.objects.remove(o, do_unlink=True)
# 成叢：三個色系 × 三種階段比例，固定種子（和 dress 的叢同一套公式，只是放在平地）
for fi in range(3):
    for mi in range(3):
        R = random.Random(7300 + fi * 10 + mi)
        o = b['mushrooms10'](f'Clump_{fi}_{mi}', Vector((mi * .85 - .85, fi * .85, 0)), R, fi, b['MUSH10_MIX'][mi], R.randint(4, 6), k, mat, gnd, free)
        stats.append((o.name, o['mush_stages'], len(o.data.vertices)))
ortho(f'{out}/DR10_mush_clumps.png', (0, -4.6, 3.6), (0, .85, .05), 3.1, (1600, 1100))
for s_ in stats:
    print('MUSH', s_)
print('MUSH_SHEET_DONE')
