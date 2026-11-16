import bpy, sys, math
from mathutils import Vector
OUT = 'D:/chengtian/4-素材與快取/bark-sample/GT01_out/'
SRC = 'D:/chengtian/4-素材與快取/bark-sample/'
bpy.ops.wm.open_mainfile(filepath=OUT + 'GT01_GodTree_v003.blend')
sc = bpy.context.scene
with bpy.data.libraries.load(SRC + 'godtree_lo0.blend', link=False) as (s, d):
    d.objects = [n for n in s.objects if n in ('Grid', 'Cube') or n.startswith('Cylinder')]
for o in d.objects:
    sc.collection.objects.link(o)
    o.hide_render = False
for o in bpy.data.objects:
    if o.name.endswith('_LOD1') or o.name.endswith('_LOD2') or o.name.startswith('UCX_'):
        o.hide_render = True
sc.render.engine = 'CYCLES'
sc.cycles.samples = 64
sc.cycles.use_denoising = True
try:
    pr = bpy.context.preferences.addons['cycles'].preferences
    pr.compute_device_type = 'OPTIX'; pr.get_devices()
    for dv in pr.devices: dv.use = True
    sc.cycles.device = 'GPU'
except Exception as e:
    print(e)
def shot(n, loc, tgt, lens):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object; c.data.lens = lens
    c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = c
    sc.render.resolution_x, sc.render.resolution_y = 1536, 1024
    sc.render.filepath = OUT + f'game_{n}.png'
    bpy.ops.render.render(write_still=True)
shot('full', (0, -115, 6), (0, 0, 30), 22)
shot('base', (6, -40, 2.2), (0, 0, 9), 24)
