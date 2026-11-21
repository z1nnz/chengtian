"""Preview renders for the tree redo v2 package A (trees-v2-a), per the package's section 2-3 delivery list:
colour views (3/4, front, left / right 35 deg, side, top) with a 1.75 m figure, black silhouettes (front, +-35 deg), clay, wire,
under-canopy upward view, 20 m / 60 m eye-height views, LOD0-3 side by side.

    blender -b --factory-startup -P render_tr.py -- --out <dir> [--samples 64] TR06_A [TR06_B ...]
    blender -b --factory-startup -P render_tr.py -- --out <dir> --only sil,clay TR06_A
"""
import bpy, math, sys
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
args = sys.argv[sys.argv.index('--') + 1:]
def opt(k, d=None):
    if k in args: i = args.index(k); v = args[i + 1]; del args[i:i + 2]; return v
    return d
OUT = Path(opt('--out')); SAMPLES = int(opt('--samples', '64')); ONLY = set((opt('--only', '') or '').split(',')) - {''}
OUT.mkdir(parents=True, exist_ok=True)
WANT = lambda k: not ONLY or k in ONLY


def reset(engine='CYCLES', res=(1600, 1200)):
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    if engine == 'CYCLES':
        sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
        try:
            pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = 'OPTIX'; pr.get_devices()
            for d in pr.devices: d.use = True
            sc.cycles.device = 'GPU'
        except Exception: pass
        sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
        w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']
        bg.inputs['Color'].default_value = (.60, .66, .74, 1); bg.inputs['Strength'].default_value = .65
        sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sun.data.energy = 3.4; sun.data.color = (1, .9, .74); sun.data.angle = .06
        sun.rotation_euler = (math.radians(52), 0, math.radians(-35)); sc.collection.objects.link(sun)
        g = bpy.data.meshes.new('ground'); g.from_pydata([(-120, -120, 0), (120, -120, 0), (120, 120, 0), (-120, 120, 0)], [], [(0, 1, 2, 3)])
        go = bpy.data.objects.new('ground', g); m = bpy.data.materials.new('ground'); m.use_nodes = True
        m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.20, .21, .15, 1); g.materials.append(m); sc.collection.objects.link(go)
    else:
        sc.render.engine = 'BLENDER_WORKBENCH'; sh = sc.display.shading; sh.light = 'FLAT'; sh.color_type = 'OBJECT'
        g = bpy.data.meshes.new('ground'); g.from_pydata([(-120, -120, 0), (120, -120, 0), (120, 120, 0), (-120, 120, 0)], [], [(0, 1, 2, 3)])
        go = bpy.data.objects.new('ground', g); go.color = (1, 1, 1, 1); sc.collection.objects.link(go)   # white ground hides the buried roots
        sc.view_settings.view_transform = 'Standard'; w = bpy.data.worlds.new('w'); sc.world = w; w.color = (1, 1, 1)
        sh.background_type = 'WORLD'


def append(vid, lod=0, offset=(0, 0, 0), clay=False, wire=False):
    with bpy.data.libraries.load(str(HERE / f'{vid}.blend')) as (src, dst): dst.objects = [n for n in src.objects if n == f'{vid}_LOD{lod}']
    objs = []
    for o in dst.objects:
        bpy.context.scene.collection.objects.link(o); o.location = Vector(offset); objs.append(o)
    if clay or wire:
        cm = bpy.data.materials.get('clay') or bpy.data.materials.new('clay'); cm.use_nodes = True
        cm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.72, .70, .66, 1)
        for o in objs:
            o.data = o.data.copy(); o.data.materials.clear(); o.data.materials.append(cm)
            if wire:
                wm = bpy.data.materials.new('wire'); wm.use_nodes = True; wm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.05, .06, .08, 1)
                o.data.materials.append(wm); m = o.modifiers.new('w', 'WIREFRAME'); m.thickness = .004; m.use_replace = False; m.material_offset = 1
    return objs


def figure(x, y):
    bpy.ops.mesh.primitive_cylinder_add(radius=.18, depth=1.45, location=(x, y, .725)); b = bpy.context.object
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.13, location=(x, y, 1.62)); h = bpy.context.object
    m = bpy.data.materials.new('fig'); m.use_nodes = True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.35, .38, .42, 1)
    for o in (b, h): o.data.materials.append(m)
    return [b, h]


def bounds(objs):
    bpy.context.view_layer.update()
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for o in objs:
        for c in o.bound_box: w = o.matrix_world @ Vector(c); mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    return mn, mx


def cam_at(loc, target, lens=40, ortho=None):
    sc = bpy.context.scene; cam = sc.camera
    if cam is None:
        cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.clip_end = 1000
    if ortho: cam.data.type = 'ORTHO'; cam.data.ortho_scale = ortho
    else: cam.data.type = 'PERSP'; cam.data.lens = lens
    cam.location = loc; cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()


def shot(path):
    """Colour renders are saved as JPEG (PNG goes to Git LFS and these are large); silhouettes stay PNG."""
    st = bpy.context.scene.render.image_settings
    if 'silhouette' not in Path(path).name:
        path = Path(path).with_suffix('.jpg'); st.file_format = 'JPEG'; st.quality = 90
    bpy.context.scene.render.filepath = str(path); bpy.ops.render.render(write_still=True); print('wrote', path, flush=True)


def orbit_views(objs, tag, views):
    """front = looking from -Y (the water side) toward +Y; left/right 35 deg orbit around the trunk."""
    mn, mx = bounds(objs); ctr = (mn + mx) / 2; ext = mx - mn; asp = 1200 / 1600
    for v in views:
        if v == 'three_quarter':
            d = max(ext) * 1.9; cam_at(ctr + Vector((-.55, -.85, .30)).normalized() * d, ctr, 40)
        elif v == 'top':
            cam_at(ctr + Vector((0, -.001, 1)) * 60, ctr, ortho=max(ext.x, ext.y / asp) * 1.1)
        else:
            a = {'front': 0, 'left35': -35, 'right35': 35, 'side': 90}[v]; r = math.radians(a)
            dv = Vector((math.sin(r), -math.cos(r), .055)).normalized(); w = max(abs(ext.x * math.cos(r)) + abs(ext.y * math.sin(r)), ext.z / asp)
            cam_at(ctr + dv * 80, ctr, ortho=w * 1.1)
        shot(OUT / f'{tag}_{v}.png')


for vid in args:
    if WANT('color'):
        reset(); objs = append(vid); mn, mx = bounds(objs); objs += figure(mx.x + .6, mn.y - .4)
        orbit_views(objs, vid, ['three_quarter', 'front', 'left35', 'right35', 'side', 'top'])
    if WANT('sil'):
        reset('WORKBENCH', (1200, 1200)); objs = append(vid)
        for o in objs: o.color = (0, 0, 0, 1)
        orbit_views(objs, f'{vid}_silhouette', ['front', 'left35', 'right35'])
    if WANT('clay'):
        reset(); objs = append(vid, clay=True); orbit_views(objs, f'{vid}_clay', ['three_quarter'])
    if WANT('wire'):
        reset(); objs = append(vid, wire=True); mn, mx = bounds(objs); ctr = (mn + mx) / 2
        cam_at(ctr + Vector((-.5, -.86, .1)).normalized() * max(mx - mn) * .75, ctr + Vector((0, 0, 1)), 40); shot(OUT / f'{vid}_wire_three_quarter.png')
    if WANT('under'):   # standing under the crown, looking up: twigs must run into the leaves
        reset(); objs = append(vid); mn, mx = bounds(objs); ctr = (mn + mx) / 2
        cam_at(Vector((ctr.x * .5 + .9, ctr.y * .5 - .9, 1.6)), Vector((ctr.x, ctr.y, mx.z * .8)), 20); shot(OUT / f'{vid}_under_canopy.png')
    if WANT('far'):     # 20 m / 60 m at eye height, 50 mm
        for dist, lod in ((20, 0), (20, 1), (60, 1), (60, 2)):
            reset(res=(1600, 900)); objs = append(vid, lod); mn, mx = bounds(objs); ctr = (mn + mx) / 2
            cam_at(Vector((ctr.x, ctr.y - dist, 1.7)), Vector((ctr.x, ctr.y, (mx.z + 1.7) / 2 if dist < 30 else 3.0)), 35 if dist < 30 else 50)
            shot(OUT / f'{vid}_far_{dist}m_LOD{lod}.png')
    if WANT('lod'):
        reset(res=(2400, 900)); objs = []
        for lod in range(4):
            objs += append(vid, lod, (lod * 11.0, 0, 0))
        mn, mx = bounds(objs); ctr = (mn + mx) / 2; cam_at(Vector((ctr.x, ctr.y - 120, ctr.z)), ctr, ortho=(mx.x - mn.x) * 1.06)
        shot(OUT / f'{vid}_LOD0-3.png')
