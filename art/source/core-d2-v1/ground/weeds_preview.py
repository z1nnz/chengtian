# 雜草樣板一字排開預覽：blender -b --factory-startup -P weeds_preview.py -- <tag>
import bpy, sys, math, random
from mathutils import Vector
S_ = 'D:/chengtian/4-素材與快取/bark-sample/'
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
TAG = argv[0] if argv else 'w1'
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
exec(compile(open(S_ + 'plants.py', encoding='utf-8').read(), S_ + 'plants.py', 'exec'))
exec(compile(open(S_ + 'weeds.py', encoding='utf-8').read(), S_ + 'weeds.py', 'exec'))
WM = weed_materials()
fern_mat = _leaf_material('UG01_Fern', (.040, .085, .022, 1), (.085, .16, .040, 1), (.12, .19, .06, 1), gloss=.5)
heart_mat = _leaf_material('UG02_Heart', (.030, .070, .022, 1), (.070, .13, .040, 1), (.13, .19, .08, 1), gloss=.35)
stem = bpy.data.materials.new('stem')
x = 0.0
items = [
    lambda p, R: fern('f', p, R, 1.0, fern_mat, stem),
    lambda p, R: heart_plant('h', p, R, 1.0, heart_mat, stem),
    lambda p, R: grass_tuft('g', p, R, 1.0, WM['grass'], 0),
    lambda p, R: grass_tuft('g2', p, R, 1.0, WM['grass'], .7),
    lambda p, R: sedge('s', p, R, 1.0, WM['sedge']),
    lambda p, R: clover('c', p, R, 1.0, WM['clover']),
    lambda p, R: rosette('r', p, R, 1.0, WM['rosette']),
    lambda p, R: sapling('sp', p, R, 1.0, WM['sapling'], stem),
]
for i, fn in enumerate(items):
    fn(Vector((i * 1.1, 0, 0)), random.Random(i + 3))
bpy.ops.mesh.primitive_plane_add(size=30, location=(4, 0, 0))
g = bpy.context.object
gm = bpy.data.materials.new('g')
gm.use_nodes = True
next(n for n in gm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.08, .06, .04, 1)
g.data.materials.append(gm)
sc = bpy.context.scene
w = bpy.data.worlds.new('W')
sc.world = w
w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND').inputs['Strength'].default_value = 1.5
sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN'))
sun.data.energy = 3
sun.rotation_euler = (.8, 0, .6)
sc.collection.objects.link(sun)
sc.render.engine = 'CYCLES'
sc.cycles.samples = 48
sc.cycles.use_denoising = True
sc.cycles.device = 'GPU'
sc.view_settings.view_transform = 'AgX'
sc.render.resolution_x, sc.render.resolution_y = 1800, 700
cd = bpy.data.cameras.new('c')
cd.lens = 30
c = bpy.data.objects.new('c', cd)
sc.collection.objects.link(c)
c.location = (3.85, -7.0, 1.4)
c.rotation_euler = (Vector((3.85, 0, .25)) - c.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = c
sc.render.filepath = S_ + f'weeds_{TAG}.png'
bpy.ops.render.render(write_still=True)
