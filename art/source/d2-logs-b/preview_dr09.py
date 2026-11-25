# DR09 斷枝堆遊戲模型的快速預覽：開 blend/DR09_BranchPile_<v>_v001.blend，只留 LOD0（本體＋植物），
# 陰天天光＋斜上方太陽，拍幾個鏡位到 D:/yun-jing-cache/dr09-work/T_<v>_<鏡位>.png（不交付，只給自己看）。
#   blender -b art/source/d2-logs-b/blend/DR09_BranchPile_M_v001.blend --python art/source/d2-logs-b/preview_dr09.py -- M tq,side
import bpy, sys, math
from mathutils import Vector

a = sys.argv[sys.argv.index('--') + 1:]
v = a[0]
views = (a[1] if len(a) > 1 else 'tq,side,midc,leftc,rightc').split(',')
asset = f'DR09_BranchPile_{v}'
root = bpy.data.objects[asset]
root.location = Vector((0, 0, 0))                     # 原點 = 底部中心
for o in bpy.data.objects:
    keep = o.name in (f'{asset}_LOD0', f'Detail_DR09_Leaves_LOD0', asset)
    o.hide_render = not keep
bpy.context.view_layer.update()
lo = Vector((1e9, 1e9, 1e9))
hi = -lo
for o in (bpy.data.objects[f'{asset}_LOD0'],):
    for c in o.bound_box:
        p = o.matrix_world @ Vector(c)
        lo = Vector(map(min, lo, p))
        hi = Vector(map(max, hi, p))
L = hi.x - lo.x
sc = bpy.context.scene
try:
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
sc.view_settings.view_transform = 'Standard'
w = sc.world or bpy.data.worlds.new('W')
sc.world = w
w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (.55, .60, .66, 1)
bg.inputs['Strength'].default_value = .9
sun = bpy.data.objects.new('PrevSun', bpy.data.lights.new('PrevSun', 'SUN'))
sun.data.energy = 2.6
sun.data.angle = math.radians(8)
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))
sc.collection.objects.link(sun)
gme = bpy.data.meshes.new('PrevGround')
gme.from_pydata([(-20, -20, 0), (20, -20, 0), (20, 20, 0), (-20, 20, 0)], [], [(0, 1, 2, 3)])
gm = bpy.data.materials.new('PrevGround')
gm.use_nodes = True
next(n for n in gm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.055, .045, .033, 1)
gme.materials.append(gm)
g = bpy.data.objects.new('PrevGround', gme)
g.location.z = -.003
sc.collection.objects.link(g)
cam = bpy.data.objects.new('PrevCam', bpy.data.cameras.new('PrevCam'))
sc.collection.objects.link(cam)
sc.camera = cam
H = hi.z
CAMS = {'tq': ((-L * .55 - 1.6, -L * .55 - 2.0, 1.2 + H), (0, 0, H * .35), 40), 'side': ((0, -L * 1.55 - 1.0, .9), (0, 0, H * .45), 40),
        'top': ((0, -.6, L * 1.6 + 1.5), (0, 0, 0), 40), 'end': ((L * .5 + 2.2, -.6, 1.0), (0, 0, H * .4), 40),
        'close': ((-L * .22, -1.4, .55 + H * .6), (-L * .22, 0, H * .35), 40), 'brk': ((L * .22, -1.3, .5 + H * .5), (L * .22, 0, H * .3), 40)}
L = hi.x - lo.x
for vw in views:
    p, t, lens = CAMS[vw]
    cam.location = p
    cam.rotation_euler = (Vector(t) - Vector(p)).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = lens
    sc.render.filepath = f'D:/yun-jing-cache/dr09-work/T_{v}_{vw}.png'
    bpy.ops.render.render(write_still=True)
    print('PREVIEW', sc.render.filepath)
