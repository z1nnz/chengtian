"""trees-v2 review renders (Cycles). Same sun and sky for every view, so versions compare like for like.

  blender --background <blend> --python art/source/trees-v2/preview_trees_v2.py -- <out_dir> <asset id> [view ...]
views: front l35 r35 sil_front sil_r35 sil_top grey wire under far20 far60 lods scale  (default: all)
"""
import bpy, sys, math
from pathlib import Path
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
OUT = Path(argv[0]); OUT.mkdir(parents=True, exist_ok=True); AID = argv[1]
VIEWS = argv[2:] or ['front', 'l35', 'r35', 'sil_front', 'sil_r35', 'sil_top', 'grey', 'wire', 'under', 'far20', 'far60', 'lods', 'scale']
sc = bpy.context.scene


def lod(k):
    return bpy.data.objects.get(f'{AID}_LOD{k}')


def only(objs):
    for o in sc.objects:
        if o.type == 'MESH': o.hide_render = o not in objs
        if o.type == 'MESH' and o.name.endswith('_Collision'): o.hide_render = True


def bounds(objs):
    ws = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return Vector([min(v[i] for v in ws) for i in range(3)]), Vector([max(v[i] for v in ws) for i in range(3)])


def world(sky=True):
    w = bpy.data.worlds.get('Rev_World') or bpy.data.worlds.new('Rev_World'); w.use_nodes = True; nt = w.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_WORLD': nt.nodes.remove(n)
    out = [n for n in nt.nodes if n.type == 'OUTPUT_WORLD'][0]
    bg = nt.nodes.new('ShaderNodeBackground'); nt.links.new(bg.outputs[0], out.inputs[0])
    if sky:      # soft blue sky, lighter at the horizon (the standard image's sky), strength low so the sun reads
        tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); ramp = nt.nodes.new('ShaderNodeValToRGB')
        nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], ramp.inputs[0])
        ramp.color_ramp.elements[0].position = .5; ramp.color_ramp.elements[0].color = (.36, .55, .78, 1)
        ramp.color_ramp.elements[1].position = 1.; ramp.color_ramp.elements[1].color = (.12, .3, .62, 1)
        nt.links.new(ramp.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = .95
    else:
        bg.inputs[0].default_value = (1, 1, 1, 1); bg.inputs[1].default_value = 1.
    sc.world = w


def sun(on=True):
    s = bpy.data.objects.get('Rev_Sun')
    if s is None:
        s = bpy.data.objects.new('Rev_Sun', bpy.data.lights.new('Rev_Sun', 'SUN')); sc.collection.objects.link(s)
        s.data.energy = 4.2; s.data.angle = math.radians(3); s.data.color = (1., .96, .9)
        s.rotation_euler = (math.radians(48), 0, math.radians(35))      # from front-right, 42 deg up
    s.hide_render = not on


def ground(on=True):
    g = bpy.data.objects.get('Rev_Ground')
    if g is None:
        me = bpy.data.meshes.new('Rev_Ground'); r = 60
        me.from_pydata([(-r, -r, 0), (r, -r, 0), (r, r, 0), (-r, r, 0)], [], [(0, 1, 2, 3)])
        g = bpy.data.objects.new('Rev_Ground', me); sc.collection.objects.link(g)
        m = bpy.data.materials.new('Rev_Ground'); m.use_nodes = True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.16, .2, .11, 1)
        m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 1.; me.materials.append(m)
    g.hide_render = not on
    return g


def camera(loc, target, lens=50, ortho=None):
    c = bpy.data.objects.get('Rev_Cam')
    if c is None:
        c = bpy.data.objects.new('Rev_Cam', bpy.data.cameras.new('Rev_Cam')); sc.collection.objects.link(c)
    c.data.type = 'ORTHO' if ortho else 'PERSP'
    if ortho: c.data.ortho_scale = ortho
    c.data.lens = lens; c.data.clip_end = 1000; c.data.clip_start = .05; c.data.sensor_fit = "AUTO"
    c.location = loc; d = Vector(target) - Vector(loc); c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = c


def setup(res=(1200, 1500), samples=96):
    sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Base Contrast'; sc.view_settings.exposure = 0.


def render(name):
    sc.render.filepath = str(OUT / f'{name}.png'); bpy.ops.render.render(write_still=True); print('RENDER', name, flush=True)


_saved = {}
def override(mode):
    """None: original materials; 'grey': clay; 'black': silhouette; 'wire': clay with wireframe lines."""
    for o in sc.objects:
        if o.type != 'MESH' or o.name.startswith('Rev_') or o.name.startswith('Fig_'): continue
        if o.name not in _saved: _saved[o.name] = [s.material for s in o.material_slots]
        if mode is None:
            for s, m in zip(o.material_slots, _saved[o.name]): s.material = m
            continue
        m = bpy.data.materials.get(f'Rev_{mode}')
        if m is None:
            m = bpy.data.materials.new(f'Rev_{mode}'); m.use_nodes = True; nt = m.node_tree; bs = nt.nodes['Principled BSDF']; m.use_backface_culling = False
            if mode == 'black':
                out = nt.nodes['Material Output']; em = nt.nodes.new('ShaderNodeEmission'); em.inputs[0].default_value = (0, 0, 0, 1)
                nt.links.new(em.outputs[0], out.inputs['Surface'])
            else:
                bs.inputs['Base Color'].default_value = (.55, .55, .55, 1); bs.inputs['Roughness'].default_value = .8
                if mode == 'wire':
                    wf = nt.nodes.new('ShaderNodeWireframe'); wf.use_pixel_size = True; wf.inputs[0].default_value = .8
                    mix = nt.nodes.new('ShaderNodeMixRGB'); mix.inputs[1].default_value = (.62, .62, .62, 1); mix.inputs[2].default_value = (.04, .04, .04, 1)
                    nt.links.new(wf.outputs[0], mix.inputs[0]); nt.links.new(mix.outputs[0], bs.inputs['Base Color'])
        for s in o.material_slots: s.material = m


def figure(x, y):
    """1.75 m human scale (capsule body + head), mid grey."""
    if bpy.data.objects.get('Fig_Body'): return
    bpy.ops.mesh.primitive_cylinder_add(radius=.19, depth=1.45, location=(x, y, .725)); b = bpy.context.object; b.name = 'Fig_Body'
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.13, location=(x, y, 1.62)); h = bpy.context.object; h.name = 'Fig_Head'
    m = bpy.data.materials.new('Fig'); m.use_nodes = True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.5, .32, .22, 1)
    for o in (b, h): o.data.materials.append(m)


L0 = lod(0); lo, hi = bounds([L0]); ctr = (lo + hi) / 2; Ht = hi.z; Wd = max(hi.x - lo.x, hi.y - lo.y)
setup(); world(True); sun(True)


def orbit(deg, dist, z_cam, z_tgt):
    a = math.radians(deg); return (ctr.x + math.sin(a) * dist, ctr.y - math.cos(a) * dist, z_cam), (ctr.x, ctr.y, z_tgt)


fit = max(Ht, Wd * 1.25) * 1.9
for v in VIEWS:
    override(None); world(True); sun(True); ground(False); only([L0]); setup()
    if v in ('front', 'l35', 'r35'):
        deg = {'front': 0, 'l35': -35, 'r35': 35}[v]; loc, tg = orbit(deg, fit, Ht * .45, Ht * .52); camera(loc, tg, 50); render(f'{AID}_{v}')
    elif v.startswith('sil_'):
        override('black'); world(False); sun(False)
        if v == 'sil_top': camera((ctr.x, ctr.y, Ht + 60), (ctr.x, ctr.y, 0), ortho=Wd * 1.15); setup((1200, 1200))
        else:
            deg = 0 if v == 'sil_front' else 35; loc, tg = orbit(deg, 80, Ht * .5, Ht * .5); camera(loc, tg, ortho=max(Ht, Wd) * 1.12)
        sc.view_settings.view_transform = 'Standard'; render(f'{AID}_{v}')
    elif v == 'close':
        setup((1500, 1200), 96); loc, tg = orbit(20, Wd * .5, Ht * .6, Ht * .62); camera(loc, tg, 50); render(f'{AID}_close_crown')
    elif v == 'grey':
        override('grey'); loc, tg = orbit(25, fit, Ht * .45, Ht * .52); camera(loc, tg, 50); render(f'{AID}_grey')
    elif v == 'wire':
        override('wire'); setup((1500, 1500), 48); loc, tg = orbit(20, Wd * .55, Ht * .62, Ht * .66); camera(loc, tg, 50); render(f'{AID}_wire_crown')
        loc, tg = orbit(20, fit, Ht * .45, Ht * .52); camera(loc, tg, 50); setup((1200, 1500), 48); render(f'{AID}_wire')
    elif v == 'under':
        ground(True); a = lo.z
        loc = (ctr.x + 1.6, ctr.y - 2.4, 1.6); camera(loc, (ctr.x - .5, ctr.y + .5, Ht * .75), 18); setup((1500, 1200)); render(f'{AID}_under_crown')
    elif v in ('far20', 'far60'):
        d = 20 if v == 'far20' else 60; k = 0 if d < 35 else 1; obj = lod(k) or L0; only([obj]); ground(True)
        camera((ctr.x, ctr.y - d, 1.7), (ctr.x, ctr.y, Ht * (.5 if d < 35 else .4)), 35); setup((1920, 1080), 64)
        sc.camera.data.sensor_fit = 'VERTICAL'; sc.camera.data.angle = math.radians(40); render(f'{AID}_far{d}m_LOD{k}')
    elif v == 'lods':
        objs = [o for o in (lod(0), lod(1), lod(2), lod(3)) if o]
        keep = [o.location.copy() for o in objs]
        for i, o in enumerate(objs): o.location.x += i * Wd * 1.05
        only(objs); xs = (len(objs) - 1) * Wd * 1.05 / 2; span = len(objs) * Wd * 1.05
        setup((2400, max(600, int(2400 * (Ht + 1.5) / span))), 64)
        camera((ctr.x + xs, ctr.y - 80, Ht * .5), (ctr.x + xs, ctr.y, Ht * .5), ortho=span * 1.02); render(f'{AID}_lods')
        for o, l in zip(objs, keep): o.location = l
    elif v == 'scale':
        figure(ctr.x + Wd * .55, ctr.y - 1.5); only([L0]); ground(True)
        for n in ('Fig_Body', 'Fig_Head'): bpy.data.objects[n].hide_render = False
        loc, tg = orbit(10, fit, 1.7, Ht * .5); camera(loc, tg, 50); render(f'{AID}_scale_1p75m')
        for n in ('Fig_Body', 'Fig_Head'): bpy.data.objects[n].hide_render = True
print('PREVIEW DONE')
