# DR10 第八輪：灰模正交剪影（正面 -Y 看、側面 +X 看、四分之三），透明背景，給等高對照與輪廓量測用。
# 用法：blender -b --python art/source/d2-logs-b/silhouette_dr10.py -- A <輸出資料夾> [build 腳本]
import bpy, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
R2 = HERE + '/../d2-roots-b'


def _load(p):
    g = {'__file__': p, '__name__': os.path.basename(p)[:-3]}
    exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), g)
    return g


a = sys.argv[sys.argv.index('--') + 1:]
v, out = a[0], a[1]
bp = a[2] if len(a) > 2 and a[2] != '-' else HERE + '/build_dr10.py'
b = _load(bp)
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
b['build'](v, quick=True)
V = b['VAR']
pv = _load(R2 + '/preview_dr.py')
pv['setup'](samples=24, fog=False)
for o in list(bpy.data.objects):                      # 去掉預覽地面、人形，只留樹
    if o.type == 'MESH' and (o.name.startswith('DR_') or 'Ground' in o.name or 'Floor' in o.name or 'Plane' in o.name):
        o.hide_render = True
m = bpy.data.materials.new('Clay')
m.use_nodes = True
bb = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bb.inputs['Base Color'].default_value = (.20, .19, .18, 1)
bb.inputs['Roughness'].default_value = .8
bpy.context.view_layer.material_override = m
sc = bpy.context.scene
sc.render.film_transparent = True
zs = [(o.matrix_world @ Vector(c)).z for o in bpy.data.objects if o.type == 'MESH' and not o.hide_render for c in o.bound_box]
top = max(zs)
cx, cy = b['axis_xy'](V, 0.0)
cam = bpy.data.objects.new('SilCam', bpy.data.cameras.new('SilCam'))
sc.collection.objects.link(cam)
cam.data.type = 'ORTHO'
H = top + .6
cam.data.ortho_scale = H * 1.25
sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 1000, 1250
os.makedirs(out, exist_ok=True)
for tag, d in (('front', (0, -1)), ('side', (1, 0)), ('side2', (-1, 0)), ('back', (0, 1)), ('tq', (-.62, -.78))):
    zc = H * .5 - .3
    cam.location = (cx + d[0] * 60, cy + d[1] * 60, zc)
    cam.rotation_euler = (Vector((cx, cy, zc)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = f'{out}/DR10_{v}_sil_{tag}.png'
    bpy.ops.render.render(write_still=True)
import json
json.dump(dict(top=top, H=H, zc=H * .5 - .3, res=[1000, 1250], px_per_m=1250 / (H * 1.25)), open(f'{out}/DR10_{v}_sil.json', 'w'))
print('SIL_DONE', v, 'top', round(top, 3))
