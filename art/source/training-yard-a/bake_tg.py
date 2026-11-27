"""Scanned surfaces for TG01 (review on PR #119, 11/15 standard section 5): old wood and mossy stone baked from a displaced high model.

The wood and stone parts are joined into one game mesh. Its high model is a smooth subdivision (16 faces per face) pushed in
along the normal by the Poly Haven scan displacement, sampled with a box (tri-planar) projection in object space, so the
furrows run up the post. Cycles bakes the high model's normal and colour onto the game mesh through a new non-overlapping
UV: one 1024 atlas T_TG01_Baked_Albedo / _Normal. The big cracks, dents and the split top are geometry in the game mesh itself.

kind (per-vertex attribute): 0 wood, 1 polished grip (arm and leg ends), 2 stone.
Scans (CC0, not in the repo): <BARK_SCANS or D:/yj-assets/polyhaven/>{bark_willow_02,mossy_rock}_{diff,disp}_2k.png.
"""
import bpy, math, os
import numpy as np

SCANS = os.environ.get('BARK_SCANS', 'D:/yj-assets/polyhaven/')
WOOD, STONE = 'bark_willow_02', 'mossy_rock'
TILE = {0: .55, 1: .55, 2: .45}          # metres per scan tile
DEPTH = {0: .012, 1: .002, 2: .018}      # furrow depth on the high model (grips are worn smooth)


def scan(set_, kind):
    p = f'{SCANS}{set_}_{kind}_2k.png'
    if not os.path.exists(p): raise FileNotFoundError(f'scan missing: {p} (download from polyhaven.com/a/{set_})')
    return p


def _arr(set_):
    im = bpy.data.images.load(scan(set_, 'disp'), check_existing=True); im.colorspace_settings.name = 'Non-Color'
    w, h = im.size; a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, -1)[..., 0]
    return (a - a.min()) / max(a.max() - a.min(), 1e-6)


def _samp(a, u, v):
    h, w = a.shape; x = (u % 1.0) * w; y = (v % 1.0) * h
    x0 = np.floor(x).astype(int) % w; y0 = np.floor(y).astype(int) % h; x1 = (x0 + 1) % w; y1 = (y0 + 1) % h; fx = x - np.floor(x); fy = y - np.floor(y)
    return (a[y0, x0] * (1 - fx) + a[y0, x1] * fx) * (1 - fy) + (a[y1, x0] * (1 - fx) + a[y1, x1] * fx) * fy


def _triplanar(a, co, nr, tile):
    w = np.abs(nr) ** 4; w /= w.sum(1, keepdims=True) + 1e-9; p = co / tile
    return w[:, 0] * _samp(a, p[:, 1], p[:, 2]) + w[:, 1] * _samp(a, p[:, 0], p[:, 2]) + w[:, 2] * _samp(a, p[:, 0], p[:, 1])


def high_model(low):
    hi = low.copy(); hi.data = low.data.copy(); hi.name = low.name + '_Hi'; bpy.context.scene.collection.objects.link(hi)
    m = hi.modifiers.new('sub', 'SUBSURF'); m.subdivision_type = 'CATMULL_CLARK'; m.levels = m.render_levels = 2
    with bpy.context.temp_override(object=hi, active_object=hi, selected_objects=[hi], selected_editable_objects=[hi]):
        bpy.ops.object.modifier_apply(modifier=m.name)
    me = hi.data; me.update(); n = len(me.vertices)
    co = np.zeros(n * 3, np.float32); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    nr = np.zeros(n * 3, np.float32); me.vertices.foreach_get('normal', nr); nr = nr.reshape(-1, 3)
    k = np.zeros(n, np.float32); me.attributes['kind'].data.foreach_get('value', k); k = np.rint(k).astype(int)
    d = np.zeros(n, np.float32)
    for kind, set_ in ((0, WOOD), (1, WOOD), (2, STONE)):
        s = k == kind
        if s.any(): d[s] = (_triplanar(_arr(set_), co[s], nr[s], TILE[kind]) - 1.0) * DEPTH[kind]
    me.vertices.foreach_set('co', (co + nr * d[:, None]).ravel()); me.update()
    hi.data.materials.clear(); hi.data.materials.append(_hi_material())
    return hi


def _hi_material():
    """Scan colour by box projection, chosen by `kind`: wood graded to the valley's old dark timber, the grips smoother and warmer,
    stone with moss on the up-facing faces; the wood darkens and greens toward the foot (moss at the base)."""
    m = bpy.data.materials.new('M_TG01_Hi'); m.use_nodes = True; nt = m.node_tree; L = nt.links
    bs = next(x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED')
    tc = nt.nodes.new('ShaderNodeTexCoord'); geo = nt.nodes.new('ShaderNodeNewGeometry'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs[0])
    def tex(set_, tile):
        mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1 / tile,) * 3; L.new(tc.outputs['Object'], mp.inputs['Vector'])
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(scan(set_, 'diff'), check_existing=True); t.projection = 'BOX'; t.projection_blend = .25
        L.new(mp.outputs['Vector'], t.inputs['Vector']); return t
    def mix(a, b, f, kind='MIX'):
        x = nt.nodes.new('ShaderNodeMix'); x.data_type = 'RGBA'; x.blend_type = kind
        for s, v in ((x.inputs[0], f), (x.inputs[6], a), (x.inputs[7], b)):
            L.new(v, s) if not isinstance(v, (float, tuple)) else setattr(s, 'default_value', v if isinstance(v, float) else (*v, 1))
        return x.outputs[2]
    def hsv(c, s, v):
        h = nt.nodes.new('ShaderNodeHueSaturation'); h.inputs['Saturation'].default_value = s; h.inputs['Value'].default_value = v; L.new(c, h.inputs['Color']); return h.outputs['Color']
    att = nt.nodes.new('ShaderNodeAttribute'); att.attribute_name = 'kind'
    wood = mix(hsv(tex(WOOD, .55).outputs['Color'], .9, .78), (.62, .42, .28), 1.0, 'MULTIPLY')        # bark scan warmed toward old brown timber
    grip = mix(wood, (.30, .17, .09), .65)                                                               # hands polish the ends dark and even
    # foot of the post: darker, mossy below ~25 cm
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 9; L.new(tc.outputs['Object'], nz.inputs['Vector'])
    foot = nt.nodes.new('ShaderNodeMapRange'); foot.inputs['From Min'].default_value = .30; foot.inputs['From Max'].default_value = .08; L.new(sep.outputs['Z'], foot.inputs['Value'])
    fm = nt.nodes.new('ShaderNodeMath'); fm.operation = 'MULTIPLY'; L.new(foot.outputs['Result'], fm.inputs[0]); L.new(nz.outputs['Fac'], fm.inputs[1])
    fm2 = nt.nodes.new('ShaderNodeMath'); fm2.operation = 'MULTIPLY'; fm2.inputs[1].default_value = 1.6; L.new(fm.outputs[0], fm2.inputs[0]); fm2.use_clamp = True
    wood = mix(wood, (.10, .14, .05), fm2.outputs[0])
    stone = hsv(tex(STONE, .45).outputs['Color'], .8, .95)
    up = nt.nodes.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Normal'], up.inputs[0])
    mo = nt.nodes.new('ShaderNodeMapRange'); mo.inputs['From Min'].default_value = .55; mo.inputs['From Max'].default_value = .95; L.new(up.outputs['Z'], mo.inputs['Value'])
    nz2 = nt.nodes.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 6; L.new(tc.outputs['Object'], nz2.inputs['Vector'])
    mo2 = nt.nodes.new('ShaderNodeMath'); mo2.operation = 'MULTIPLY'; L.new(mo.outputs['Result'], mo2.inputs[0]); L.new(nz2.outputs['Fac'], mo2.inputs[1])
    mo3 = nt.nodes.new('ShaderNodeMath'); mo3.operation = 'MULTIPLY'; mo3.inputs[1].default_value = .95; mo3.use_clamp = True; L.new(mo2.outputs[0], mo3.inputs[0])
    stone = mix(stone, (.10, .13, .055), mo3.outputs[0])   # grey stone with patches of dark moss (the three-view), not a green cap
    is_grip = nt.nodes.new('ShaderNodeMath'); is_grip.operation = 'COMPARE'; is_grip.inputs[1].default_value = 1; is_grip.inputs[2].default_value = .5; L.new(att.outputs['Fac'], is_grip.inputs[0])
    is_stone = nt.nodes.new('ShaderNodeMath'); is_stone.operation = 'GREATER_THAN'; is_stone.inputs[1].default_value = 1.5; L.new(att.outputs['Fac'], is_stone.inputs[0])
    c = mix(mix(wood, grip, is_grip.outputs[0]), stone, is_stone.outputs[0])
    L.new(c, bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = .9
    return m


def open_zero_uv(o, eps=.0006):
    """A sliver face (smart project, or a 2 mm bevel strip projected onto the trim sheet) can end up with zero UV area, which QA
    reports as an error: open it by a fraction of a texel."""
    uv = o.data.uv_layers['UVMap'].data; fixed = 0
    for p in o.data.polygons:
        ls = list(p.loop_indices); q = [uv[i].uv.copy() for i in ls]
        area = sum(q[i].x * q[(i + 1) % len(q)].y - q[(i + 1) % len(q)].x * q[i].y for i in range(len(q))) / 2
        if abs(area) < 1e-8:
            for k, i in enumerate(ls[1:3]): uv[i].uv = (q[k + 1].x + (eps if k == 0 else 0), q[k + 1].y + (0 if k == 0 else eps))
            fixed += 1
    if fixed: print('ZERO_UV opened', o.name, fixed, flush=True)
    return fixed


def bake(low, hi, name, out_dir, size=1024):
    """Non-overlapping UV on `low`, then hi -> low normal and colour. Returns the game material M_<name>_Baked."""
    bpy.ops.object.select_all(action='DESELECT'); low.select_set(True); bpy.context.view_layer.objects.active = low
    low.data.uv_layers.active = low.data.uv_layers['UVMap']
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(55), island_margin=.006, scale_to_bounds=False)
    bpy.ops.uv.pack_islands(margin=.006, rotate=True); bpy.ops.object.mode_set(mode='OBJECT')
    open_zero_uv(low)
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 4; sc.cycles.use_denoising = False
    try:
        pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = 'OPTIX'; pr.get_devices()
        for d in pr.devices: d.use = True
        sc.cycles.device = 'GPU'
    except Exception: pass
    cage = low.copy(); cage.data = low.data.copy(); cage.name = low.name + '_Cage'; sc.collection.objects.link(cage)
    me = cage.data; me.update(); n = len(me.vertices)
    co = np.zeros(n * 3, np.float32); me.vertices.foreach_get('co', co); nr = np.zeros(n * 3, np.float32); me.vertices.foreach_get('normal', nr)
    me.vertices.foreach_set('co', co + nr * .012); me.update()
    b = sc.render.bake; b.use_selected_to_active = True; b.use_cage = True; b.cage_object = cage; b.max_ray_distance = .05; b.margin = 8
    m = bpy.data.materials.new(f'M_{name}_Baked'); m.use_nodes = True; nt = m.node_tree; bs = next(x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED')
    bs.inputs['Roughness'].default_value = .88
    imgs = {}
    for kind, cs in (('Albedo', 'sRGB'), ('Normal', 'Non-Color')):
        im = bpy.data.images.new(f'T_{name}_Baked_{kind}', size, size, alpha=False); im.colorspace_settings.name = cs
        im.filepath_raw = str(out_dir / f'T_{name}_Baked_{kind}.png'); im.file_format = 'PNG'; imgs[kind] = im
    t = nt.nodes.new('ShaderNodeTexImage'); low.data.materials.clear(); low.data.materials.append(m)
    bpy.ops.object.select_all(action='DESELECT'); hi.select_set(True); low.select_set(True); bpy.context.view_layer.objects.active = low
    for kind, typ in (('Normal', 'NORMAL'), ('Albedo', 'DIFFUSE')):
        t.image = imgs[kind]; nt.nodes.active = t
        if typ == 'DIFFUSE': b.use_pass_direct = b.use_pass_indirect = False; b.use_pass_color = True
        bpy.ops.object.bake(type=typ); imgs[kind].save()
    nt.nodes.remove(t); b.use_cage = False; bpy.data.objects.remove(cage, do_unlink=True)
    ta = nt.nodes.new('ShaderNodeTexImage'); ta.image = imgs['Albedo']; nt.links.new(ta.outputs['Color'], bs.inputs['Base Color'])
    tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = imgs['Normal']; tn.image.colorspace_settings.name = 'Non-Color'
    nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], bs.inputs['Normal'])
    return m
