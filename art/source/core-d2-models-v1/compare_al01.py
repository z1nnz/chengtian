"""用相同相機、燈光與背景渲染 RL01 及 AL01；第二參數可指定 AL01 GLB。"""
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
args = sys.argv[sys.argv.index('--') + 1:]
variant = args[0]
out = ROOT / 'art/previews/core-d2-models-v1/RL01'
peer = Path(args[1]) if len(args) > 1 else \
    ROOT / 'art/exports/core-d2-v1/AL01_RootAltarTerrace/AL01_RootAltarTerrace_v001.glb'
assert peer.is_file(), peer
asset = ROOT / f'art/exports/core-d2-models-v1/RL01/RL01_RottenLog_{variant}_v001.glb'

for label, path in ((f'RL01_RottenLog_{variant}', asset), ('AL01_RootAltarTerrace', peer)):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path))
    for o in list(bpy.context.scene.objects):
        if o.type == 'MESH' and not o.name.endswith('_LOD0'):
            bpy.data.objects.remove(o, do_unlink=True)
    targets = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in targets for c in o.bound_box]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    shift = Vector((-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]))
    for o in targets:
        o.location += shift

    world = bpy.data.worlds.new('Comparison_World')
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes.get('Background').inputs['Color'].default_value = (.12, .13, .13, 1)
    world.node_tree.nodes.get('Background').inputs['Strength'].default_value = .8

    bpy.ops.object.camera_add(location=(5.4, -8.1, 5.8))
    cam = bpy.context.object
    cam.rotation_euler = (Vector((0, 0, .8)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 11.2
    bpy.context.scene.camera = cam
    bpy.ops.object.light_add(type='AREA', location=(3.5, -4.5, 7))
    light = bpy.context.object
    light.data.energy = 1100
    light.data.shape = 'DISK'
    light.data.size = 5

    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 700
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(out / f'{label}_same_setup.png')
    scene.view_settings.view_transform = 'AgX'
    bpy.ops.render.render(write_still=True)

print('SAME_SETUP', variant, flush=True)
