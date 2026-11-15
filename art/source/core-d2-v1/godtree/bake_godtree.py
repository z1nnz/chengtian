"""Build the D2 GT01 game mesh from the approved six-strand v3 shape.

Run: blender -b --factory-startup -P bake_godtree.py -- game
The Poly Haven scan set is local-only in ./tex; see README.md.
"""
import json
import math
import random
import shutil
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2]
OUT = ART / 'exports' / 'core-d2-v1' / 'GT01_GodTree'
PREVIEW = ART / 'previews' / 'core-d2-v1' / 'GT01_GodTree'
BLEND = ART / 'source' / 'core-d2-v1' / 'blend' / 'GT01_GodTree_v001.blend'
TEX = HERE / 'tex'
for d in (OUT, OUT / 'Textures', PREVIEW, BLEND.parent):
    d.mkdir(parents=True, exist_ok=True)

required = ('diff', 'nor_gl', 'rough', 'ao', 'disp')
for key in required:
    if not (TEX / f'bark_brown_02_{key}_2k.png').is_file():
        raise FileNotFoundError(f'Missing {key}: download bark_brown_02 2k PNG to {TEX}')

# The v3 shape code ends before its offline render and very dense render-only crown.
v3 = HERE / 'godtree_v3.py'
shape = v3.read_text(encoding='utf-8').split('# ---------------- 樹冠：')[0]
exec(compile(shape, str(v3), 'exec'))
OUT = ART / 'exports' / 'core-d2-v1' / 'GT01_GodTree'
TEX = HERE / 'tex'


def image_material(name, base, normal=None, rough=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    t = nodes.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(str(base), check_existing=True)
    t.image.colorspace_settings.name = 'sRGB'
    links.new(t.outputs['Color'], bsdf.inputs['Base Color'])
    if normal:
        n = nodes.new('ShaderNodeTexImage')
        n.image = bpy.data.images.load(str(normal), check_existing=True)
        n.image.colorspace_settings.name = 'Non-Color'
        nm = nodes.new('ShaderNodeNormalMap')
        links.new(n.outputs['Color'], nm.inputs['Color'])
        links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    if rough:
        r = nodes.new('ShaderNodeTexImage')
        r.image = bpy.data.images.load(str(rough), check_existing=True)
        r.image.colorspace_settings.name = 'Non-Color'
        links.new(r.outputs['Color'], bsdf.inputs['Roughness'])
    return m


# The source scans are the texture-space detail used to displace the v3 wood.
# These maps are scan-derived, not a claimed high-to-low mesh bake.
maps = {}
for key, suffix in [('diff', 'BaseColor'), ('nor_gl', 'Normal'),
                    ('rough', 'Roughness'), ('ao', 'AO')]:
    dst = OUT / 'Textures' / f'GT01_GodTree_{suffix}.png'
    shutil.copy2(TEX / f'bark_brown_02_{key}_2k.png', dst)
    maps[suffix] = dst
wood_mat = image_material('GT01_ScannedBark', maps['BaseColor'], maps['Normal'], maps['Roughness'])
for ob in objs:
    ob.data.materials.clear()
    ob.data.materials.append(wood_mat)


def join_named(objects, name):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    objects[0].name = name
    objects[0].data.name = name
    return objects[0]


wood = join_named(objs, 'GT01_Wood_LOD0')

# Sparse three-dimensional leaf cards create the wide, irregular v3 canopy.
# They have their own mesh, so the game's foliage shader can use cutout lighting.
leaf_vertices, leaf_faces, leaf_uv = [], [], []
rng = random.Random(20261115)
palette = ((.025, .060, .027, 1), (.041, .077, .032, 1),
           (.070, .085, .028, 1), (.155, .135, .042, 1))
leaf_mats = []
for idx, color in enumerate(palette):
    mat = bpy.data.materials.new(f'GT01_Leaf_{idx}')
    mat.use_nodes = True
    bs = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value = color
    bs.inputs['Roughness'].default_value = .85
    leaf_mats.append(mat)
leaf_ids = []
for center, direction, radius in TIPS:
    for _ in range(150):
        span = rng.uniform(.6, 3.8)
        p = center + Vector((rng.gauss(0, span), rng.gauss(0, span), rng.gauss(0, span * .4)))
        a = rng.random() * math.tau
        size = rng.uniform(.18, .46)
        across = Vector((math.cos(a), math.sin(a), rng.uniform(-.24, .24))) * size
        along = Vector((-math.sin(a), math.cos(a), rng.uniform(-.20, .20))) * size * 1.5
        base = len(leaf_vertices)
        tip = p + along + Vector((0, 0, size * .25))
        tail = p - along * .72
        leaf_vertices.extend([tuple(p - across), tuple(tip), tuple(p + across), tuple(tail)])
        leaf_faces.extend(((base, base + 1, base + 2), (base, base + 2, base + 3)))
        leaf_uv.extend((((0, .4), (.5, 1), (1, .4)), ((0, .4), (1, .4), (.5, 0))))
        mid = rng.choices(range(4), (50, 30, 15, 5))[0]
        leaf_ids.extend((mid, mid))
mesh = bpy.data.meshes.new('GT01_Leaves_LOD0')
mesh.from_pydata(leaf_vertices, [], leaf_faces)
mesh.update()
uv = mesh.uv_layers.new(name='UVMap')
for poly, coords, mid in zip(mesh.polygons, leaf_uv, leaf_ids):
    poly.material_index = mid
    for li, xy in zip(poly.loop_indices, coords):
        uv.data[li].uv = xy
leaves = bpy.data.objects.new('GT01_Leaves_LOD0', mesh)
bpy.context.scene.collection.objects.link(leaves)
for mat in leaf_mats:
    mesh.materials.append(mat)


def triangle_count(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def lod_copy(source, name, ratio):
    ob = source.copy()
    ob.data = source.data.copy()
    ob.name = name
    bpy.context.scene.collection.objects.link(ob)
    mod = ob.modifiers.new('LODReduction', 'DECIMATE')
    mod.ratio = ratio
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob


wood1 = lod_copy(wood, 'GT01_Wood_LOD1', .50)
wood2 = lod_copy(wood, 'GT01_Wood_LOD2', .15)
leaves1 = lod_copy(leaves, 'GT01_Leaves_LOD1', .50)
leaves2 = lod_copy(leaves, 'GT01_Leaves_LOD2', .15)

# A simple trunk blocking volume is included for scene placement.
bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=9.2, radius2=5.0, depth=30, location=(0, 0, 15))
collision = bpy.context.object
collision.name = 'GT01_Collision_Trunk'
collision.hide_render = True
collision.display_type = 'WIRE'

lods = [(wood, leaves), (wood1, leaves1), (wood2, leaves2)]
counts = {f'LOD{i}': sum(triangle_count(o) for o in pair) for i, pair in enumerate(lods)}
lo = [min((ob.matrix_world @ Vector(v.co))[i] for ob in (wood, leaves) for v in ob.data.vertices) for i in range(3)]
hi = [max((ob.matrix_world @ Vector(v.co))[i] for ob in (wood, leaves) for v in ob.data.vertices) for i in range(3)]
geometry = [ob for pair in lods for ob in pair] + [collision]

bpy.ops.object.select_all(action='DESELECT')
for ob in geometry:
    ob.select_set(True)
bpy.context.view_layer.objects.active = wood
fbx = OUT / 'GT01_GodTree_v001.fbx'
glb = OUT / 'GT01_GodTree_v001.glb'
bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, axis_forward='-Z', axis_up='Y',
                         apply_unit_scale=True, bake_space_transform=True, path_mode='STRIP', add_leaf_bones=False)
bpy.ops.export_scene.gltf(filepath=str(glb), export_format='GLB', use_selection=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

info = {
    'asset': 'GT01_GodTree', 'version': 'v001', 'units': 'meters',
    'source': 'godtree_v3.py six-strand shape; game tessellation and leaf cards in bake_godtree.py',
    'reference': 'art/references/core-d2-v1/godtree/godtree-three-view-v1.png',
    'scan': {'name': 'Poly Haven bark_brown_02', 'url': 'https://polyhaven.com/a/bark_brown_02', 'license': 'CC0'},
    'textures': {k: v.name for k, v in maps.items()},
    'texture_note': '2k scan-derived maps; mesh-specific high-to-low Normal/AO/Base Color baking is pending',
    'triangles': counts, 'bounds_min_m': [round(v, 3) for v in lo],
    'bounds_max_m': [round(v, 3) for v in hi],
    'dimensions_m': [round(b-a, 3) for a,b in zip(lo,hi)],
    'collision': collision.name,
}
(OUT / 'model_info.json').write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
checks = {
    'exports_nonempty': fbx.stat().st_size > 1000 and glb.stat().st_size > 1000,
    'lod_order': counts['LOD0'] > counts['LOD1'] > counts['LOD2'],
    'lod0_150k_to_250k': 150000 <= counts['LOD0'] <= 250000,
    'scan_maps_2k': all(tuple(bpy.data.images.load(str(p), check_existing=True).size) == (2048, 2048) for p in maps.values()),
    'bottom_below_ground': lo[2] < 0,
}
(OUT / 'validation.json').write_text(json.dumps({'checks': checks, 'pass': all(checks.values()), 'triangles': counts}, indent=2), encoding='utf-8')

for ob in geometry:
    ob.hide_render = ob not in (wood, leaves)
# The ground and person are preview-only; they never enter the exported asset.
bpy.ops.mesh.primitive_plane_add(size=180, location=(0, 0, -.12))
ground = bpy.context.object
ground.name = 'Preview_Mud'
mud = bpy.data.materials.new('Preview_Mud')
mud.use_nodes = True
next(n for n in mud.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.105, .09, .07, 1)
ground.data.materials.append(mud)
bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=.18, depth=1.75, location=(3, -18, .875))
person = bpy.context.object
person.name = 'Preview_1p75m_Person'
person.data.materials.append(mud)
bpy.ops.object.camera_add(location=(0, -105, 35))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 28)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.lens = 30
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(35), 0, math.radians(-25)))
bpy.context.object.data.energy = 3.0
world = bpy.data.worlds.new('Preview_Overcast')
world.use_nodes = True
background = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
background.inputs['Color'].default_value = (.50, .55, .60, 1)
background.inputs['Strength'].default_value = 1.0
bpy.context.scene.world = world
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x, scene.render.resolution_y = 1200, 900
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(PREVIEW / 'GT01_GodTree_hero.png')
bpy.ops.render.render(write_still=True)
print('GT01_RESULT', json.dumps({'triangles': counts, 'checks': checks, 'files': [str(fbx), str(glb)]}))
