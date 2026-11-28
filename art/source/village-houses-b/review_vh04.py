"""VH04 review renders in daylight: a warm low sun from the street side (as in A1_concept_2_entry), a sky, a packed-earth ground.
Used while modelling (the preview blend) and for the delivered previews (the LOD0 of the exported blend); studio renders (ti_pipeline)
light a building evenly and leave the open shop front black, which says nothing about how it reads in the village.

  blender -b <blend> --python art/source/village-houses-b/review_vh04.py -- <out_dir> [shot ...] [--samples N]
Shots: street (concept 2's angle: eye height, along the street, the near gable on the right), front, inside, high, back, gable.
"""
import bpy, sys, math
from pathlib import Path
from mathutils import Vector

SHOTS = {
    'street': ((7.2, -9.6, 1.65), (-.9, .3, 2.3), 30),
    'front': ((.4, -10.5, 1.7), (0., 0., 2.6), 32),
    'inside': ((1.0, -4.3, 1.6), (-.1, 1.2, 1.3), 24),
    'high': ((8.5, -10.5, 7.5), (0., 0., 2.4), 34),
    'back': ((-7.5, 9.5, 2.6), (0., 0., 2.6), 32),
    'gable': ((11.5, .6, 1.8), (0., .4, 2.8), 32),
}


def setup(samples=64):
    sc = bpy.context.scene
    for o in sc.objects:
        n = o.name
        if o.type == 'MESH':
            o.hide_render = ('_LOD1' in n or '_LOD2' in n or 'Collision' in n or o.hide_render and 'LOD0' not in n)
        if o.type == 'LIGHT': o.hide_render = True
    for c in bpy.data.collections:
        if c.name.startswith('80_') or c.name.startswith('90_'): c.hide_render = True
    g = bpy.data.objects.get('REV_Ground')
    if not g:
        me = bpy.data.meshes.new('REV_Ground'); me.from_pydata([(-40, -40, 0), (40, -40, 0), (40, 40, 0), (-40, 40, 0)], [], [(0, 1, 2, 3)])
        g = bpy.data.objects.new('REV_Ground', me); sc.collection.objects.link(g)
        m = bpy.data.materials.new('REV_Ground'); m.use_nodes = True
        bs = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        bs.inputs['Base Color'].default_value = (.16, .125, .085, 1); bs.inputs['Roughness'].default_value = .95
        me.materials.append(m)
        g.location.z = -.002
    sun = bpy.data.objects.get('REV_Sun')
    if not sun:
        L = bpy.data.lights.new('REV_Sun', 'SUN'); L.energy = 4.2; L.color = (1., .86, .68); L.angle = math.radians(1.5)
        sun = bpy.data.objects.new('REV_Sun', L); sc.collection.objects.link(sun)
        d = Vector((.55, .95, -.48)).normalized()            # light travels into the shop front from the south-west, low
        sun.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    w = bpy.data.worlds.new('REV_Sky'); w.use_nodes = True; sc.world = w
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (.55, .66, .82, 1); bg.inputs[1].default_value = .9
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = 1536, 1024; sc.render.resolution_percentage = 50 if "--half" in sys.argv else 100
    sc.render.image_settings.file_format = 'PNG'; sc.view_settings.view_transform = 'AgX'; sc.view_settings.exposure = 0.
    sc.render.film_transparent = False


def shot(path, loc, tgt, lens):
    sc = bpy.context.scene
    cam = bpy.data.objects.get('REV_Cam') or bpy.data.objects.new('REV_Cam', bpy.data.cameras.new('REV_Cam'))
    if cam.name not in sc.collection.objects: sc.collection.objects.link(cam)
    cam.data.lens = lens; cam.data.clip_start = .05; cam.data.clip_end = 200
    cam.location = loc; cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam; sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:]
    out = Path(a[0]).resolve(); out.mkdir(parents=True, exist_ok=True)
    samples = int(a[a.index('--samples') + 1]) if '--samples' in a else 64
    names = [x for x in a[1:] if x in SHOTS] or list(SHOTS)
    setup(samples)
    for k in names:
        shot(out / f'review_{k}.png', *SHOTS[k])
        print('REVIEW', k, flush=True)
