"""Scanned bark for the trees-v2-a trunks and limbs (review on PR #120, 11/15 standard section 5).

The high model is the wood mesh, smooth-subdivided (16 faces per face) and pushed out along the normal by the Poly Haven scan displacement
(furrows 5-15 cm deep on the trunk, scaled down with the branch radius), sampled at the tube's own UV (u round the branch,
v along it, square texels). Cycles then bakes the high model's normal and colour onto the game mesh through a new,
non-overlapping UV (the tube strips, rescaled and packed), so every tree gets its own 2048 bark atlas (T_<id>_Bark_Albedo / _Normal).

Scans (CC0, not in the repo): D:/yj-assets/polyhaven/<set>_{diff,nor_gl,rough,disp}_2k.png, or BARK_SCANS=<folder>.
"""
import bpy, bmesh, math, os
import numpy as np
from mathutils import Vector

SCANS = os.environ.get('BARK_SCANS', 'D:/yj-assets/polyhaven/')
DEPTH_K, DEPTH_MAX, DEPTH_MIN = .38, .11, .004   # furrow depth = radius * DEPTH_K, clamped (trunk r 0.25 m -> 9.5 cm)


def scan(set_, kind):
    p = f'{SCANS}{set_}_{kind}_2k.png'
    if not os.path.exists(p): raise FileNotFoundError(f'bark scan missing: {p} (download from polyhaven.com/a/{set_})')
    return p


def _disp_array(set_):
    im = bpy.data.images.load(scan(set_, 'disp'), check_existing=True); im.colorspace_settings.name = 'Non-Color'
    w, h = im.size; a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, -1)[..., 0]
    return (a - a.min()) / max(a.max() - a.min(), 1e-6)


def _sample(a, u, v):
    h, w = a.shape; x = (u % 1.0) * w; y = (v % 1.0) * h
    x0 = np.floor(x).astype(int) % w; y0 = np.floor(y).astype(int) % h; x1 = (x0 + 1) % w; y1 = (y0 + 1) % h; fx = x - np.floor(x); fy = y - np.floor(y)
    return (a[y0, x0] * (1 - fx) + a[y0, x1] * fx) * (1 - fy) + (a[y1, x0] * (1 - fx) + a[y1, x1] * fx) * fy


def high_model(low, radius, set_, tile=1.0):
    """Copy of `low` (tube UVs in 'UVMap', per-vertex branch radius in `radius`), 4x subdivided and displaced by the scan."""
    hi = low.copy(); hi.data = low.data.copy(); hi.name = low.name + '_BarkHi'; bpy.context.scene.collection.objects.link(hi)
    ra = hi.data.attributes.new('rad', 'FLOAT', 'POINT'); ra.data.foreach_set('value', np.asarray(radius, dtype=np.float32))
    m = hi.modifiers.new('sub', 'SUBSURF'); m.subdivision_type = 'CATMULL_CLARK'; m.levels = m.render_levels = 2   # smooth like the shaded game mesh (SIMPLE kept the facets -> striped, black-creased normals)
    with bpy.context.temp_override(object=hi, active_object=hi, selected_objects=[hi], selected_editable_objects=[hi]):
        bpy.ops.object.modifier_apply(modifier=m.name)
    me = hi.data; n = len(me.vertices)
    uvl = me.uv_layers['UVMap'].data; li = np.array([l.vertex_index for l in me.loops]); uv = np.zeros(len(me.loops) * 2, np.float32); uvl.foreach_get('uv', uv); uv = uv.reshape(-1, 2)
    vu = np.zeros((n, 2), np.float32); vu[li] = uv   # one loop per vertex is enough: the tube seam has its own duplicated vertices
    r = np.zeros(n, np.float32); me.attributes['rad'].data.foreach_get('value', r)
    co = np.zeros(n * 3, np.float32); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    me.update(); nr = np.zeros(n * 3, np.float32); me.vertices.foreach_get('normal', nr); nr = nr.reshape(-1, 3)
    d = _sample(_disp_array(set_), vu[:, 0] * tile, vu[:, 1] * tile)
    depth = np.clip(r * DEPTH_K, DEPTH_MIN, DEPTH_MAX)
    co += nr * ((d - 1.0) * depth)[:, None]   # plates stay at the surface, furrows cut in (the silhouette does not grow)
    me.vertices.foreach_set('co', co.ravel()); me.update()
    hi.data.materials.clear(); hi.data.materials.append(_hi_material(set_, tile))
    return hi


def _hi_material(set_, tile):
    """Scan colour on the tube UV, darker in the furrows (from the displacement), times the vertex colour (hollow darkening)."""
    m = bpy.data.materials.new(f'M_BarkHi_{set_}'); nt = m.node_tree if m.node_tree else None
    if nt is None: m.use_nodes = True; nt = m.node_tree
    bs = next(x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED')
    uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'UVMap'; mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (tile, tile, 1)
    nt.links.new(uvn.outputs['UV'], mp.inputs['Vector'])
    def tex(kind, cs):
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(scan(set_, kind), check_existing=True); t.image.colorspace_settings.name = cs
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector']); return t
    dif, dsp = tex('diff', 'sRGB'), tex('disp', 'Non-Color')
    cav = nt.nodes.new('ShaderNodeMapRange'); cav.inputs['From Min'].default_value = .15; cav.inputs['From Max'].default_value = .65; cav.inputs['To Min'].default_value = .55
    nt.links.new(dsp.outputs['Color'], cav.inputs['Value'])
    mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1
    nt.links.new(dif.outputs['Color'], mul.inputs[6]); nt.links.new(cav.outputs['Result'], mul.inputs[7])
    vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Col'
    mul2 = nt.nodes.new('ShaderNodeMix'); mul2.data_type = 'RGBA'; mul2.blend_type = 'MULTIPLY'; mul2.inputs['Factor'].default_value = 1
    nt.links.new(mul.outputs[2], mul2.inputs[6]); nt.links.new(vc.outputs['Color'], mul2.inputs[7])
    nt.links.new(mul2.outputs[2], bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value = .9
    return m


def bake_uv(low, margin=.004):
    """Replace the tiled tube UV of the game mesh with a non-overlapping one (the high model keeps the tiled UV for sampling)."""
    bpy.ops.object.select_all(action='DESELECT'); low.select_set(True); bpy.context.view_layer.objects.active = low
    low.data.uv_layers.active = low.data.uv_layers['UVMap']
    # each tube is already one unbroken UV strip (u round, v along, seam duplicated): keep the strips, give them texels in
    # proportion to their real size, and pack them without overlap -> the bark runs on along every branch, no cut-up islands
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(margin=margin, rotate=True)
    bpy.ops.object.mode_set(mode='OBJECT')


def bake(low, hi, name, out_dir, size=2048, tint=(1, 1, 1)):
    """Bake hi -> low: tangent normal and colour; low gets material M_<name>_Bark using the two textures. Returns the material."""
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 4; sc.cycles.use_denoising = False
    try:
        pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = 'OPTIX'; pr.get_devices()
        for d in pr.devices: d.use = True
        sc.cycles.device = 'GPU'
    except Exception: pass
    # the high model lies on or inside the game surface (furrows cut in), so the rays start just outside and stop past the deepest
    # furrow: longer rays reach the neighbouring limb inside a fork or a root inside the flare (wrong colours in the normal map)
    sc.render.bake.use_selected_to_active = True; sc.render.bake.max_ray_distance = DEPTH_MAX + .05; sc.render.bake.margin = 16
    # cage = the game mesh pushed 2 cm out along the same vertex normals the high model was displaced on: each ray runs from
    # the cage point straight down that normal, so in the trunk's ridged grooves it cannot cross to the opposite wall
    cage = low.copy(); cage.data = low.data.copy(); cage.name = low.name + '_Cage'; sc.collection.objects.link(cage)
    me = cage.data; me.update(); n = len(me.vertices)
    co = np.zeros(n * 3, np.float32); me.vertices.foreach_get('co', co); nr = np.zeros(n * 3, np.float32); me.vertices.foreach_get('normal', nr)
    me.vertices.foreach_set('co', co + nr * .02); me.update()
    sc.render.bake.use_cage = True; sc.render.bake.cage_object = cage
    m = bpy.data.materials.new(f'M_{name}_Bark'); m.use_nodes = True; nt = m.node_tree; bs = next(x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED')
    bs.inputs['Roughness'].default_value = .92
    imgs = {}
    for kind, cs in (('Albedo', 'sRGB'), ('Normal', 'Non-Color')):
        im = bpy.data.images.new(f'T_{name}_Bark_{kind}', size, size, alpha=False); im.colorspace_settings.name = cs
        im.filepath_raw = str(out_dir / f'T_{name}_Bark_{kind}.png'); im.file_format = 'PNG'; imgs[kind] = im
    t = nt.nodes.new('ShaderNodeTexImage'); low.data.materials.clear(); low.data.materials.append(m)
    bpy.ops.object.select_all(action='DESELECT'); hi.select_set(True); low.select_set(True); bpy.context.view_layer.objects.active = low
    for kind, typ in (('Normal', 'NORMAL'), ('Albedo', 'DIFFUSE')):
        t.image = imgs[kind]; nt.nodes.active = t
        if typ == 'DIFFUSE':
            sc.render.bake.use_pass_direct = sc.render.bake.use_pass_indirect = False; sc.render.bake.use_pass_color = True
        bpy.ops.object.bake(type=typ)
        if typ == 'DIFFUSE' and tint != (1, 1, 1):   # species tint baked in (Unity _BaseColor stays white)
            px = np.array(imgs[kind].pixels[:], np.float32).reshape(-1, 4); px[:, :3] *= np.asarray(tint, np.float32) ** (1 / 2.2); imgs[kind].pixels.foreach_set(np.clip(px, 0, 1).ravel())
        imgs[kind].save()
    nt.nodes.remove(t); sc.render.bake.use_cage = False; bpy.data.objects.remove(cage, do_unlink=True)
    ta = nt.nodes.new('ShaderNodeTexImage'); ta.image = imgs['Albedo']; nt.links.new(ta.outputs['Color'], bs.inputs['Base Color'])
    tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = imgs['Normal']; tn.image.colorspace_settings.name = 'Non-Color'
    nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], bs.inputs['Normal'])
    return m
