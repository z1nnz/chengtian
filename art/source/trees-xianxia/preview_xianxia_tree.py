"""Previews for XT01 (Blender EEVEE; Unity is the colour authority, see the Unity shots).

  blender --background art/source/trees-xianxia/blend/XT01_XianxiaGreatTree_v003.blend --python art/source/trees-xianxia/preview_xianxia_tree.py -- <mode> <outdir>

modes: hero (green + gold three-quarter), ten (ten views, green), tengold, clay (grey), wire, lods, ruler (with a 1.75 m figure),
far (50 m and 100 m, LOD the distance would pick), quick (one green three-quarter, small).
"""
import bpy, sys, math
from pathlib import Path
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
MODE = argv[0]; OUT = Path(argv[1]); OUT.mkdir(parents=True, exist_ok=True)
AID = 'XT01_XianxiaGreatTree'
sc = bpy.context.scene
for o in list(sc.objects):
    if o.name.endswith('_Collision') or o.type == 'EMPTY': o.hide_render = True
G = {l: bpy.data.objects[f'{AID}_LOD{l}'] for l in range(4)}
Y = {l: bpy.data.objects[f'{AID}_Gold_LOD{l}'] for l in range(4)}
H = max((G[0].matrix_world @ Vector(c)).z for c in G[0].bound_box)


def show(objs):
    for o in sc.objects:
        if o.type == 'MESH' and not o.name.endswith('_Collision') and not o.name.startswith('PV_'): o.hide_render = o not in objs


def setup(res=(1600, 1000), sky=(.52, .66, .86), sun_e=3.4):
    sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = 0.
    sc.render.film_transparent = False
    try:
        sc.eevee.use_shadows = True; sc.eevee.taa_render_samples = 48
    except Exception: pass
    w = bpy.data.worlds.new('PV_World'); w.use_nodes = True; nt = w.node_tree
    bg = nt.nodes['Background']; bg.inputs[0].default_value = sky + (1,); bg.inputs[1].default_value = .9
    sc.world = w
    sun = bpy.data.objects.new('PV_Sun', bpy.data.lights.new('PV_Sun', 'SUN')); sc.collection.objects.link(sun)
    sun.data.energy = sun_e; sun.data.color = (1., .95, .86); sun.data.angle = math.radians(2)
    sun.rotation_euler = (math.radians(48), 0, math.radians(30))
    # grass ground
    me = bpy.data.meshes.new('PV_Ground'); s = 400; me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    g = bpy.data.objects.new('PV_Ground', me); sc.collection.objects.link(g)
    m = bpy.data.materials.new('PV_Grass'); m.use_nodes = True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.16, .34, .07, 1)
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 1.; me.materials.append(m)
    return sun, g


def cam(loc, target, lens=35, ortho=None):
    c = bpy.data.objects.get('PV_Cam') or bpy.data.objects.new('PV_Cam', bpy.data.cameras.new('PV_Cam'))
    if c.name not in sc.collection.objects: sc.collection.objects.link(c)
    c.location = loc; d = Vector(target) - Vector(loc); c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    c.data.clip_end = 2000; c.data.lens = lens
    if ortho: c.data.type = 'ORTHO'; c.data.ortho_scale = ortho
    else: c.data.type = 'PERSP'
    sc.camera = c; return c


def shoot(name):
    sc.render.filepath = str(OUT / f'{name}.png'); bpy.ops.render.render(write_still=True); print('SHOT', name, flush=True)


def figure(x, y):
    import bmesh
    me = bpy.data.meshes.new('PV_Fig'); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=.22, radius2=.22, depth=1.45, matrix=__import__('mathutils').Matrix.Translation((0, 0, .725)))
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=.15, matrix=__import__('mathutils').Matrix.Translation((0, 0, 1.6)))
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new('PV_Fig', me); o.location = (x, y, 0); sc.collection.objects.link(o)
    m = bpy.data.materials.new('PV_FigM'); m.use_nodes = True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.7, .2, .06, 1); me.materials.append(m)
    return o


C = Vector((0, 0, H * .52))
sun, ground = setup()
if MODE == 'quick':
    sc.render.resolution_x, sc.render.resolution_y = 1200, 800
    show([G[0]]); cam((22, -27, 4.5), C, 30); shoot('quick_green')
elif MODE == 'hero':
    show([G[0]]); cam((22, -27, 3.5), C, 30); shoot(f'{AID}_hero_green')
    Y[0].location.x = 0; show([Y[0]]); shoot(f'{AID}_hero_gold')
    show([G[0]]); cam((5, -8, 1.7), Vector((0, 0, 6.5)), 18); shoot(f'{AID}_under_crown_eye_1p7')
elif MODE in ('ten', 'tengold'):
    objs = [G[0]] if MODE == 'ten' else [Y[0]]
    if MODE == 'tengold': Y[0].location.x = 0
    show(objs); tag = 'green' if MODE == 'ten' else 'gold'; R = 40
    views = [('front', 0, 3), ('front_right', 45, 3), ('right', 90, 3), ('back_right', 135, 3), ('back', 180, 3), ('back_left', 225, 3),
             ('left', 270, 3), ('front_left', 315, 3), ('high_front', 0, 22), ('top', 0, None)]
    for name, az, z in views:
        if z is None: cam((0, -.01, 60), Vector((0, 0, 0)), ortho=26); shoot(f'{AID}_{tag}_view_{name}'); continue
        a = math.radians(az); cam((R * math.sin(a), -R * math.cos(a), z), C, 35); shoot(f'{AID}_{tag}_view_{name}')
elif MODE == 'clay':
    m = bpy.data.materials.new('PV_Clay'); m.use_nodes = True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.6, .6, .6, 1)
    o = G[0]; keep = list(o.data.materials); o.data.materials[0] = m
    # leaves keep their alpha: clay shows the card silhouettes, not the solid quads
    show([o]); cam((22, -27, 3.5), C, 30); shoot(f'{AID}_clay')
    for i, mm in enumerate(keep): o.data.materials[i] = mm
elif MODE == 'wire':
    sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.light = 'FLAT'; sc.display.shading.color_type = 'SINGLE'
    sc.display.shading.single_color = (.85, .85, .85); sc.display.shading.show_object_outline = False
    show([G[0]]); ground.hide_render = True
    wf = G[0].modifiers.new('W', 'WIREFRAME'); wf.thickness = .015; cam((22, -27, 3.5), C, 30); shoot(f'{AID}_wireframe')
    G[0].modifiers.remove(wf)
elif MODE == 'lods':
    xs = [-36, -12, 12, 36]
    for l in range(4): G[l].location.x = xs[l]
    show([G[l] for l in range(4)]); sc.render.resolution_x = 2400; cam((0, -70, 8), Vector((0, 0, 8)), 28); shoot(f'{AID}_lods_0123')
elif MODE == 'ruler':
    show([G[0]]); f = figure(6, -10)
    sc.render.resolution_x = 1800; cam((0, -48, 8), Vector((0, 0, 8)), 32); shoot(f'{AID}_ruler_1p75m')
elif MODE == 'far':
    for d, l in ((50, 0), (100, 1), (250, 2), (300, 3)):       # the LOD the Unity LODGroup shows there (switches 60 / 110 / 280 m)
        show([G[l]]); a = math.radians(40); cam((d * math.sin(a), -d * math.cos(a), 1.7), C, 40); shoot(f'{AID}_far_{d}m_LOD{l}')
print('DONE', MODE)
