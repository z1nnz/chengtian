# TR21 黃綠闊葉樹（BL_KIND=B）／TR22 圓冠中型樹（BL_KIND=M）——D2 設定圖 V1–V6 裡的兩種闊葉樹
#   BL_KIND=B blender -b --factory-startup -P broadleaf.py -- <tag> [quick] [seed] [save] [norender]
#   樹形用 tree_gen（天空島做法）；樹皮用掃描樹皮推進幾何（godtree_base.tube 的材質）
import os, sys, math, random
from mathutils import Vector, noise

KIND = os.environ.get('BL_KIND', 'B')
BASE = 'D:/chengtian/4-素材與快取/bark-sample/godtree_base.py'
src = open(BASE, encoding='utf-8').read()
exec(compile(src.split('# ---------------- 樹幹')[0], BASE, 'exec'))
SEED = int([a for a in ARGS if a.isdigit()][0]) if any(a.isdigit() for a in ARGS) else (11 if KIND == 'B' else 21)
noise.seed_set(SEED)
tail = src[src.index('# ---------------- 地面'):]
SPEC = {
    # 高、主幹半徑、葉片半長、調色盤（深→亮）
    'B': dict(H=16.0, TR=.50, LL=(.08, .12),
              PAL=((.05, .07, .02), (.11, .14, .03), (.22, .25, .06), (.40, .40, .10), (.58, .54, .17))),
    'M': dict(H=11.0, TR=.34, LL=(.07, .10),
              PAL=((.020, .050, .022), (.040, .090, .035), (.075, .150, .055), (.14, .23, .08), (.24, .33, .12))),
}[KIND]
TH = SPEC['H']


def gh(x, y):
    return fb((x, y, 0), .05, 3) * .4


_TG = 'C:/Users/User/AppData/Local/Temp/claude/5b1d5a1d6e0ced79/95010672-bf02-4e75-99c7-37774fc10d08/scratchpad/lifetree/tree_gen.py'
code = open(_TG, encoding='utf-8').read()
lm_src = code[code.index('def leaf_material'):code.index('def scene_and_render')]
code = code[:code.index('def bark_material')] + lm_src
code = code.replace("(.02 if level == 4 else .045)", "(.013 if level == 4 else .03)")
if KIND == 'M':
    # 圓冠：枝開角小一點、側枝短一點，樹冠收成圓團
    code = code.replace("cl = length * {0: rr.uniform(1.15, 1.4),", "cl = length * {0: rr.uniform(.95, 1.15),")
    code = code.replace("elif level == 1: trop = UP * (.20 - .36 * t)", "elif level == 1: trop = UP * (.24 - .30 * t)")
sv = sys.argv
sys.argv = ['x', '--', '.', str(SEED)]
TG = {}
exec(compile(code, _TG, 'exec'), TG)
sys.argv = sv
TG['noise'].seed_set(SEED)
TG['R'].seed(SEED)
TG.update(HEIGHT=TH, TRUNK_R=SPEC['TR'], LEAF_LEN=SPEC['LL'], PALETTE=SPEC['PAL'])
TG['grow'](Vector((0, 0, -.3)), Vector((.08, .03, 1)), TH * (.5 if KIND == 'B' else .42), SPEC['TR'], 0, SEED)
# 根：短、粗、很快鑽進土裡（不要尖刺狀長根）
_rr = random.Random(SEED + 5)
for _k in range(6):
    _a = _k / 6 * 6.283 + _rr.uniform(-.3, .3)
    _d = Vector((math.cos(_a), math.sin(_a), 0))
    _L = _rr.uniform(1.0, 1.8) * SPEC['TR'] / .5
    _pts = [_d * (SPEC['TR'] * .3) + Vector((0, 0, .9 * SPEC['TR'] / .5)), _d * (SPEC['TR'] + _L * .45) + Vector((0, 0, .15)), _d * (SPEC['TR'] + _L) + Vector((0, 0, -.35))]
    TG['branches'].append((1, _pts, [SPEC['TR'] * .55, SPEC['TR'] * .35, .06]))
# 主幹、主枝、根：用掃描樹皮推進幾何的 tube（有 UV、有凹凸）；細枝留 tree_gen 的網格
big = [b for b in TG['branches'] if b[0] <= 1]
TG['branches'][:] = [b for b in TG['branches'] if b[0] > 1]


def interp(rad, t):
    x = t * (len(rad) - 1)
    i = min(len(rad) - 2, int(x))
    return rad[i] + (rad[i + 1] - rad[i]) * (x - i)


os.environ['GT_NUMIN'] = '16'
for i, (lev, pts, rad) in enumerate(big):
    if lev == 0:
        rf = lambda t, rad=rad: interp(rad, t) * (1 + 1.0 * max(0.0, .10 - t) * 10)
    else:
        rf = lambda t, rad=rad: interp(rad, t)
    objs.append(tube(f'Limb{i}', [tuple(p) for p in pts], radius=rf, flat=lambda t: 1.0, seed=i * 1.7 + SEED,
                     rib=.10 if lev == 0 else .05, twist=.04))
wood = TG['tube_mesh']()
uvw = wood.uv_layers.new(name='UV')
_lv = [wood.vertices[l.vertex_index].co for l in wood.loops]
uvw.data.foreach_set('uv', [c for co in _lv for c in ((co.x + co.y) * .9, co.z * .9)])
_mk = wood.color_attributes.new('Mask', 'BYTE_COLOR', 'CORNER')
_mk.data.foreach_set('color', [0, .5, .2, 1] * len(wood.loops))
wo = bpy.data.objects.new('Twigs', wood)
bpy.context.scene.collection.objects.link(wo)
wo.data.materials.append(MAT)
for o in objs:
    if not o.data.materials:
        o.data.materials.append(MAT)
lm, nleaf = TG['leaf_mesh']()
lo = bpy.data.objects.new('Leaves', lm)
bpy.context.scene.collection.objects.link(lo)
lo.data.materials.append(TG['leaf_material']())
zs = [v.co.z for v in lm.vertices]
print('KIND', KIND, 'LEAVES', nleaf, 'HEIGHT', round(max(zs), 1), 'TRIS', sum(len(p.vertices) - 2 for o in (wo, lo) for p in o.data.polygons))

if 'save' in ARGS:
    bpy.ops.wm.save_as_mainfile(filepath=f'D:/chengtian/4-素材與快取/bark-sample/broadleaf_{KIND}_{TAG}.blend')
if 'norender' in ARGS:
    raise SystemExit
tail = tail[:tail.index('# 1.75 m 人形尺')]
tail = tail.replace("primitive_grid_add(x_subdivisions=400, y_subdivisions=400, size=130)", "primitive_grid_add(x_subdivisions=200, y_subdivisions=200, size=100)")
tail = tail.replace("vol.inputs['Density'].default_value = .0055", "vol.inputs['Density'].default_value = .003")
exec(compile(tail, BASE, 'exec'))
hm = bpy.data.materials.new('Human')
hm.use_nodes = True
next(n for n in hm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.75, .72, .66, 1)
bpy.ops.mesh.primitive_cylinder_add(radius=.22, depth=1.75, location=(3.5, -2.5, .875))
bpy.context.object.data.materials.append(hm)


def shot(n, loc, tgt, lens, res=(1200, 1200)):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.data.lens = lens
    c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = c
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = OUT + f'bl{KIND}_{TAG}_{n}.png'
    bpy.ops.render.render(write_still=True)


s = TH / 16
shot('full', (0, -40 * s, 5 * s), (0, 0, 8 * s), 32)
shot('crown', (14 * s, -16 * s, 6 * s), (0, 0, 10 * s), 30)
