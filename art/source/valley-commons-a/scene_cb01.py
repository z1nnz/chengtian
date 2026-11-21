"""CB01 in a simple creek setting (Cycles, LOD0): the bridge over a creek bed with water, two grassy banks at deck height,
1.75 m figures. Views: three-quarter, the walkway at 1.7 m eye height, the silhouette from 80 m away at the village path
(package: recognisable from the village entrance 80 m away), from the creek, looking up at the open roof timbers from
the walkway (review #113) and a close look at a gable end. --only name,name renders just those views. --clay for the grey model.

    blender -b --factory-startup -P art/source/valley-commons-a/scene_cb01.py -- [--clay] [--samples 64]
"""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]; PKG = 'valley-commons-a'
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
CLAY = '--clay' in args; ONLY = args[args.index('--only') + 1].split(',') if '--only' in args else None; SAMPLES = int(args[args.index('--samples') + 1]) if '--samples' in args else 64
OUT = ROOT / 'art/previews' / PKG / 'scene'; OUT.mkdir(parents=True, exist_ok=True)
info = json.loads((ROOT / 'art/exports' / PKG / 'CB01.model_info.json').read_text(encoding='utf-8')); DT = info['extra']['deckTop_m']

bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
try:
    pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = 'OPTIX'; pr.get_devices()
    for d in pr.devices: d.use = True
    sc.cycles.device = 'GPU'
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000; sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (.66, .70, .74, 1); bg.inputs['Strength'].default_value = .65
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sun.data.energy = 3.4; sun.data.color = (1, .88, .72); sun.data.angle = .08
sun.rotation_euler = (math.radians(52), 0, math.radians(-35)); sc.collection.objects.link(sun)
def mat(nm, col, rough=.9):
    m = bpy.data.materials.new(nm); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; return m
def quad(nm, v, m):
    me = bpy.data.meshes.new(nm); me.from_pydata(v, [], [(0, 1, 2, 3)]); o = bpy.data.objects.new(nm, me); me.materials.append(m); sc.collection.objects.link(o); return o
grass, bed, water = mat('bank', (.30, .36, .22)), mat('bed', (.30, .29, .26)), mat('water', (.20, .30, .32), .08)
for sx in (-1, 1):   # banks at deck height beyond the deck ends, sloping down to the creek bed
    quad(f'bank{sx}', [(sx * 8, -60, DT), (sx * 120, -60, DT), (sx * 120, 60, DT), (sx * 8, 60, DT)][::sx], grass)
    quad(f'slope{sx}', [(sx * 6.4, -60, 0), (sx * 8, -60, DT), (sx * 8, 60, DT), (sx * 6.4, 60, 0)][::sx], grass)
quad('bed', [(-6.4, -60, 0), (6.4, -60, 0), (6.4, 60, 0), (-6.4, 60, 0)], bed)
quad('water', [(-6.6, -60, .35), (6.6, -60, .35), (6.6, 60, .35), (-6.6, 60, .35)], water)
with bpy.data.libraries.load(str(HERE / 'CB01.blend')) as (src, dst): dst.objects = [n for n in src.objects if n.endswith('_LOD0')]
clay = mat('clay', (.72, .70, .66), .8)
for o in dst.objects:
    sc.collection.objects.link(o)
    if CLAY: o.data.materials.clear(); o.data.materials.append(clay)
fm = mat('fig', (.35, .38, .42))
def figure(p):
    bpy.ops.mesh.primitive_cylinder_add(radius=.18, depth=1.45, location=(p[0], p[1], p[2] + .725)); b = bpy.context.object
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.13, location=(p[0], p[1], p[2] + 1.62)); h = bpy.context.object
    for o in (b, h): o.data.materials.append(fm)
for f in ((-1.5, .4, DT), (2.8, -.7, DT), (-10.5, -2.0, DT)): figure(f)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
def shot(name, loc, look, lens, ev=0.0):
    if ONLY and name not in ONLY: return
    sc.view_settings.exposure = ev   # +EV only on the under-roof views, written in the file name
    cam.data.lens = lens; cam.location = Vector(loc); cam.rotation_euler = (Vector(look) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = str(OUT / f'CB01_{name}{"_clay" if CLAY else ""}{f"_ev+{ev:g}" if ev else ""}.png'); bpy.ops.render.render(write_still=True); print('wrote', sc.render.filepath, flush=True)
shot('scene_three_quarter', (-17.0, -16.0, 7.5), (0, 0, 3.0), 32)
shot('walkway_eye_1p7m', (-9.5, -.3, DT + 1.7), (6.0, .2, DT + 1.3), 22)
shot('walkway_look_up', (-4.5, .25, DT + 1.6), (1.5, -.1, DT + 3.9), 16, ev=1.5)
shot('gable_end_close', (-11.5, -4.5, 5.6), (-7.0, 0, 4.6), 30)
shot('silhouette_80m', (-56.0, -57.0, DT + 1.7), (0, 0, 3.6), 50)
shot('from_creek', (3.0, -15.0, 1.2), (0, 0, 2.8), 24)
