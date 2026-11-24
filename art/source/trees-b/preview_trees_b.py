"""trees-b review renders (open the species .blend; nothing is written back to the model files).

  blender --background art/source/trees-b/blend/TR01_v001.blend --python art/source/trees-b/preview_trees_b.py -- TR01 <mode> [out_dir]
modes:
  hero      each variant LOD0, 3/4 at about 1.7 m eye height from 18 m, warm low morning sun and blue sky fill, soft ground
  lods      each variant LOD0..LOD3 side by side from the front, same light
  quick     the three variants side by side (fast, for iteration)
  grey      as hero but grey (base colour unlinked; leaf alpha stays)
  wire      as hero with a wireframe overlay
  ruler     the three variants side by side with a 1.75 m figure and a ruler (material and grey)
  ten       ten views per variant LOD0 (front, right, back, left, four diagonals, top, high front), orthographic
  far       each variant at 50 m and 100 m (perspective, 35 mm lens, 1600 x 900) with LOD chosen by screen height like Unity
"""
import bpy, sys, math, json
from pathlib import Path
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
SP, MODE = argv[0], argv[1]
HERE = Path(__file__).resolve().parent; ART = HERE.parents[1]
OUT = Path(argv[2]) if len(argv) > 2 else ART / 'previews' / 'trees-b'
OUT.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
ROOTS = sorted([o for o in bpy.data.objects if o.type == 'EMPTY' and o.name.startswith(SP + '_')], key=lambda o: o.name)


def lod(root, k):
    return next(c for c in root.children if c.name.endswith(f'_LOD{k}'))


def env(sun_strength=6.5, samples=96, res=(1400, 1400)):
    for o in [o for o in bpy.data.objects if o.name.startswith('PV_')]: bpy.data.objects.remove(o, do_unlink=True)
    w = bpy.data.worlds.get('PV_Sky') or bpy.data.worlds.new('PV_Sky'); w.use_nodes = True; nt = w.node_tree
    bg = nt.nodes['Background']; bg.inputs[0].default_value = (.42, .55, .72, 1); bg.inputs[1].default_value = .75
    scene.world = w
    sun = bpy.data.objects.new('PV_Sun', bpy.data.lights.new('PV_Sun', 'SUN')); scene.collection.objects.link(sun)
    sun.data.energy = sun_strength; sun.data.color = (1., .88, .72); sun.data.angle = math.radians(3)
    sun.rotation_euler = Vector((.55, .75, -.62)).to_track_quat('-Z', 'Y').to_euler()     # shining from front-left, 38 deg up
    me = bpy.data.meshes.new('PV_Ground'); s = 400
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    g = bpy.data.objects.new('PV_Ground', me); scene.collection.objects.link(g)
    gm = bpy.data.materials.get('PV_GroundMat') or bpy.data.materials.new('PV_GroundMat'); gm.use_nodes = True
    gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.16, .15, .1, 1)
    gm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .95
    me.materials.append(gm)
    scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = samples; scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = res; scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'AgX'; scene.view_settings.look = 'None'; scene.view_settings.exposure = 0
    scene.render.film_transparent = False; scene.render.image_settings.file_format = 'PNG'
    return g


def cam(loc, target, lens=35, ortho=None):
    c = bpy.data.objects.new('PV_Cam', bpy.data.cameras.new('PV_Cam')); scene.collection.objects.link(c); scene.camera = c
    c.location = loc; c.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    c.data.clip_end = 2000; c.data.clip_start = .05
    if ortho: c.data.type = 'ORTHO'; c.data.ortho_scale = ortho
    else: c.data.lens = lens
    return c


def show(objs):
    keep = set(objs)
    for o in scene.objects:
        if o.type == 'MESH' and not o.name.startswith('PV_'): o.hide_render = o not in keep


def render(path):
    scene.render.filepath = str(path); bpy.ops.render.render(write_still=True); print('WROTE', path, flush=True)


def place(objs_by_root, spacing):
    """Temporarily move roots side by side along X; returns undo list."""
    undo = []
    n = len(objs_by_root)
    for i, r in enumerate(objs_by_root):
        undo.append((r, r.location.copy())); r.location = Vector(((i - (n - 1) / 2) * spacing, 0, 0))
    bpy.context.view_layer.update(); return undo


def grey(on, _saved={}):
    for m in bpy.data.materials:
        if not m.name.startswith('M_' + SP) or not m.use_nodes: continue
        bs = m.node_tree.nodes['Principled BSDF']; inp = bs.inputs['Base Color']
        if on:
            _saved[m.name] = [l.from_socket for l in inp.links]
            for l in list(inp.links): m.node_tree.links.remove(l)
            inp.default_value = (.42, .42, .42, 1)
        else:
            for s in _saved.get(m.name, []): m.node_tree.links.new(s, inp)


def figure():
    """1.75 m stand-in: body, head; plus a ruler marked every 0.5 m."""
    mat = bpy.data.materials.get('PV_Fig') or bpy.data.materials.new('PV_Fig'); mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.75, .3, .12, 1)
    objs = []
    bpy.ops.mesh.primitive_cylinder_add(radius=.2, depth=1.5, location=(0, 0, .75)); objs.append(bpy.context.object)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.125, location=(0, 0, 1.625)); objs.append(bpy.context.object)
    white = bpy.data.materials.get('PV_W') or bpy.data.materials.new('PV_W'); white.use_nodes = True
    white.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.9, .9, .85, 1)
    blk = bpy.data.materials.get('PV_B') or bpy.data.materials.new('PV_B'); blk.use_nodes = True
    blk.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.05, .05, .05, 1)
    for k in range(30):     # 15 m ruler in 0.5 m bands
        bpy.ops.mesh.primitive_cube_add(size=1, location=(.6, 0, .25 + k * .5)); b = bpy.context.object; b.scale = (.08, .08, .5)
        b.data.materials.append(white if k % 2 == 0 else blk); objs.append(b)
    for o in objs:
        o.name = 'PV_' + o.name
        if not o.data.materials: o.data.materials.append(mat)
    return objs


if MODE in ('hero', 'grey', 'wire'):
    env()
    for r in ROOTS:
        o = lod(r, 0); show([o])
        top = max((o.matrix_world @ Vector(v)).z for v in o.bound_box)
        c = cam((8.5, -9.5, 2.0), (0, 0, top * .5), lens=20)
        if MODE == 'grey': grey(True)
        if MODE == 'wire':
            m = o.modifiers.new('PV_Wire', 'WIREFRAME'); m.thickness = .012; m.use_replace = False; m.material_offset = 5
            wm = bpy.data.materials.get('PV_WireMat') or bpy.data.materials.new('PV_WireMat'); wm.use_nodes = True
            wm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.02, .02, .02, 1)
            while len(o.data.materials) < 5: o.data.materials.append(None)
            o.data.materials.append(wm)
        render(OUT / r.name / f'{r.name}_{MODE}.png')
        if MODE == 'grey': grey(False)
        if MODE == 'wire':
            o.modifiers.remove(o.modifiers['PV_Wire'])
            while len(o.data.materials) > 2: o.data.materials.pop()
        bpy.data.objects.remove(c)
elif MODE == 'quick':
    env(samples=48, res=(2100, 1000))
    show([lod(r, 0) for r in ROOTS]); undo = place(ROOTS, 11)
    cam((0, -38, 4.5), (0, 0, 6), lens=32)
    render(OUT / f'{SP}_quick.png')
    for r, l in undo: r.location = l
elif MODE == 'lods':
    env(samples=64, res=(2400, 900))
    for r in ROOTS:
        objs = [lod(r, k) for k in range(4)]; show(objs)
        keep = [o.location.copy() for o in objs]
        for k, o in enumerate(objs): o.location = Vector(((k - 1.5) * 14, 0, 0))
        objs[3].visible_shadow = False      # LOD3 cards: no shadows, as set up in Unity
        cam((0, -50, 5), (0, 0, 6), lens=35)
        render(OUT / r.name / f'{r.name}_LOD_comparison.png')
        for o, l in zip(objs, keep): o.location = l
elif MODE == 'ruler':
    env(samples=64, res=(2400, 1100)); fig = figure()
    show([lod(r, 0) for r in ROOTS] + fig); undo = place(ROOTS, 11)
    for f in fig: f.location.x += -24; f.location.y += 0
    cam((-3.5, -62, 5), (-3.5, 0, 6.2), lens=35)
    render(OUT / f'{SP}_ruler_material.png'); grey(True); render(OUT / f'{SP}_ruler_grey.png'); grey(False)
    for r, l in undo: r.location = l
elif MODE == 'ten':
    env(samples=48, res=(1024, 1024))
    VIEWS = [('01_front', (0, -1, 0)), ('02_right', (1, 0, 0)), ('03_back', (0, 1, 0)), ('04_left', (-1, 0, 0)),
             ('05_front_right', (1, -1, 0)), ('06_back_right', (1, 1, 0)), ('07_back_left', (-1, 1, 0)), ('08_front_left', (-1, -1, 0)),
             ('09_top', (0, -.0001, 1)), ('10_high_front', (0, -1, .8))]
    for r in ROOTS:
        o = lod(r, 0); show([o])
        ws = [o.matrix_world @ Vector(v) for v in o.bound_box]
        lo = Vector([min(v[i] for v in ws) for i in range(3)]); hi = Vector([max(v[i] for v in ws) for i in range(3)]); ctr = (lo + hi) / 2
        rec = []
        for name, d in VIEWS:
            d = Vector(d).normalized(); c = cam(ctr + d * 60, ctr, ortho=(hi - lo).length * 1.02)
            render(OUT / r.name / 'turnaround' / f'{name}.png'); rec.append({'file': f'{name}.png', 'direction': list(d), 'projection': 'orthographic'})
            bpy.data.objects.remove(c)
        (OUT / r.name / 'turnaround' / 'views.json').write_text(json.dumps({'asset': r.name, 'render_of': 'LOD0 with the exported textures', 'views': rec}, indent=2))
elif MODE == 'far':
    env(samples=48, res=(1600, 900))
    for r in ROOTS:
        o0 = lod(r, 0); top = max(v[2] for v in o0.bound_box)
        for dist in (50, 100):
            # pick the LOD Unity would show: screen height fraction of the tree at this distance, 35 mm lens (vertical fov ~37.8 deg at 16:9)
            vfov = 2 * math.atan(12 / 35 * 900 / 1600 * 2 / 2)
            frac = top / (2 * dist * math.tan(vfov / 2))
            info = json.loads((ART / 'exports' / 'trees-b' / r.name / 'model_info.json').read_text(encoding='utf-8'))
            sw = info['lod_switch_distance_m']; k = next((l for l in range(4) if dist < sw[l]), 3)
            show([lod(r, k)]); c = cam((dist * .7, -dist * .71, 1.7), (0, 0, top * .5), lens=35)
            render(OUT / r.name / f'{r.name}_far_{dist}m_LOD{k}.png'); bpy.data.objects.remove(c)
