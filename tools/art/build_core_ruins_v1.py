"""Core-team ruins kit v1: CO02 old forest stele (D4 苔石古祠).

  blender -b --factory-startup -P tools/art/build_core_ruins_v1.py -- CO02

Reference first (art/references/core-ruins-v1/CO02): a tall rough slab on a half-sunk plinth, the inscription hacked
away in rows of chisel gouges, one small waning-moon mark left alone above them, moss on the shaded side.
How it is built: a dense sculpt mesh shaped and coloured with numpy (form, gouges, moon mark, moss, lichen, rain
streaks as vertex colour), then baked onto a decimated game mesh (colour, normal, ambient occlusion), three LODs
sharing one UV layout, alpha-cut fern cards as a Detail_* object, and a box collision shell.
Metres, Z up, front faces -Y, origin at ground centre. Writes art/source, art/exports, art/textures, art/previews.
"""
import bpy, bmesh, sys, json, math
import numpy as np
from pathlib import Path
from mathutils import Vector, Matrix

REPO = Path(__file__).resolve().parents[2]
KIT = 'core-ruins-v1'
SRC = REPO / 'art/source' / KIT; EXP = REPO / 'art/exports' / KIT; TEX = REPO / 'art/textures' / KIT; PRE = REPO / 'art/previews' / KIT
for d in (SRC, EXP, TEX, PRE): d.mkdir(parents=True, exist_ok=True)
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['CO02']
SIZE = 2048

# ---------------------------------------------------------------- numpy noise
def _hash(p):
    return np.modf(np.sin(p[..., 0] * 127.1 + p[..., 1] * 311.7 + p[..., 2] * 74.7) * 43758.5453)[0] % 1.0

def vnoise(p):
    i = np.floor(p); f = p - i; f = f * f * (3 - 2 * f)
    def c(dx, dy, dz): return _hash(i + np.array([dx, dy, dz], dtype=np.float64))
    x00 = c(0, 0, 0) * (1 - f[..., 0]) + c(1, 0, 0) * f[..., 0]; x10 = c(0, 1, 0) * (1 - f[..., 0]) + c(1, 1, 0) * f[..., 0]
    x01 = c(0, 0, 1) * (1 - f[..., 0]) + c(1, 0, 1) * f[..., 0]; x11 = c(0, 1, 1) * (1 - f[..., 0]) + c(1, 1, 1) * f[..., 0]
    y0 = x00 * (1 - f[..., 1]) + x10 * f[..., 1]; y1 = x01 * (1 - f[..., 1]) + x11 * f[..., 1]
    return y0 * (1 - f[..., 2]) + y1 * f[..., 2]

def fbm(p, octaves=4):
    v = np.zeros(p.shape[:-1]); a = .5
    for _ in range(octaves):
        v += a * vnoise(p); p = p * 2.03 + 17.1; a *= .5
    return v

def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

def mix(a, b, t):
    t = np.asarray(t)[..., None]; return np.asarray(a) * (1 - t) + np.asarray(b) * t

# ---------------------------------------------------------------- scene helpers
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene; s.unit_settings.system = 'METRIC'; s.unit_settings.scale_length = 1
    s.render.engine = 'CYCLES'; s.cycles.samples = 24; s.cycles.device = 'CPU'
    return s

def dense_box(name, size, cuts):
    """A box with an even grid on every face (cuts per metre), centred on XY, base at z = 0."""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    sx, sy, sz = size
    for v in bm.verts: v.co = Vector((v.co.x * sx, v.co.y * sy, (v.co.z + .5) * sz))
    for axis, length in ((Vector((1, 0, 0)), sx), (Vector((0, 1, 0)), sy), (Vector((0, 0, 1)), sz)):
        n = max(1, int(length * cuts))
        for k in range(1, n):
            co = Vector((0, 0, 0)); off = -length / 2 + length * k / n
            if axis.z: off = sz * k / n
            co = axis * off
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=axis, dist=1e-6)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob

def coords(ob):
    a = np.empty(len(ob.data.vertices) * 3); ob.data.vertices.foreach_get('co', a); return a.reshape(-1, 3)

def normals(ob):
    a = np.empty(len(ob.data.vertices) * 3); ob.data.vertices.foreach_get('normal', a); return a.reshape(-1, 3)

def set_coords(ob, p):
    ob.data.vertices.foreach_set('co', p.reshape(-1)); ob.data.update()

def set_colour(ob, rgb):
    me = ob.data
    att = me.color_attributes.get('Col') or me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
    # palettes in this file are written as they should look on screen (sRGB); the attribute stores linear light
    rgba = np.concatenate([np.clip(rgb, 0, 1) ** 2.2, np.ones((len(rgb), 1))], axis=1)
    att.data.foreach_set('color', rgba.reshape(-1)); me.color_attributes.active_color = att

def colour_material(name='Sculpt_Colour'):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission'); at = nt.nodes.new('ShaderNodeVertexColor')
    at.layer_name = 'Col'
    # painted edge light: ridges a little brighter, creases a little darker (Cycles' pointiness of the sculpt)
    geo = nt.nodes.new('ShaderNodeNewGeometry'); mp = nt.nodes.new('ShaderNodeMapRange'); mul = nt.nodes.new('ShaderNodeMixRGB')
    mp.inputs['From Min'].default_value = .44; mp.inputs['From Max'].default_value = .56; mp.inputs['To Min'].default_value = .62; mp.inputs['To Max'].default_value = 1.5
    mul.blend_type = 'MULTIPLY'; mul.inputs['Fac'].default_value = 1
    nt.links.new(geo.outputs['Pointiness'], mp.inputs['Value']); nt.links.new(at.outputs['Color'], mul.inputs['Color1']); nt.links.new(mp.outputs['Result'], mul.inputs['Color2'])
    nt.links.new(mul.outputs['Color'], em.inputs['Color']); nt.links.new(em.outputs[0], out.inputs['Surface'])
    return m

def image(name, alpha=False, colour=(0, 0, 0, 1), non_color=False):
    img = bpy.data.images.new(name, SIZE, SIZE, alpha=alpha); img.generated_color = colour
    if non_color: img.colorspace_settings.name = 'Non-Color'
    return img

def bake(high, low, img, kind, mat):
    nt = mat.node_tree
    node = nt.nodes.get('BakeTarget') or nt.nodes.new('ShaderNodeTexImage'); node.name = 'BakeTarget'
    node.image = img; nt.nodes.active = node
    for o in bpy.context.scene.objects: o.select_set(False)
    for h in high: h.select_set(True)
    low.select_set(True); bpy.context.view_layer.objects.active = low
    b = bpy.context.scene.render.bake
    b.use_selected_to_active = True; b.cage_extrusion = .05; b.max_ray_distance = .12; b.margin = 16
    bpy.ops.object.bake(type=kind)

def pixels(img):
    a = np.empty(SIZE * SIZE * 4, dtype=np.float32); img.pixels.foreach_get(a); return a.reshape(SIZE, SIZE, 4)

def save(arr, path, non_color=False):
    img = bpy.data.images.new(path.stem, arr.shape[1], arr.shape[0], alpha=True)
    if non_color: img.colorspace_settings.name = 'Non-Color'
    img.alpha_mode = 'CHANNEL_PACKED'      # colour under transparent texels is kept (no premultiply), for clean alpha-cut edges
    img.pixels.foreach_set(arr.astype(np.float32).reshape(-1)); img.filepath_raw = str(path); img.file_format = 'PNG'; img.save()
    return img

def chip(q, planes):
    """Knock flat facets off a block: everything beyond each plane is pushed back onto it (hewn, fractured stone)."""
    for c, n in planes:
        n = np.asarray(n, dtype=np.float64); n /= np.linalg.norm(n)
        d = (q - np.asarray(c)) @ n
        q = q - n[None, :] * np.clip(d, 0, None)[:, None]
    return q

def strokes(px, pz, rng, count, box, angle, length, width):
    """Chisel slashes on a face: the deepest stroke at each point (0..1) and its ragged profile."""
    best = np.zeros(len(px))
    for _ in range(count):
        cx = rng.uniform(box[0], box[1]); cz = rng.uniform(box[2], box[3])
        a = math.radians(rng.uniform(*angle)); L = rng.uniform(*length) * .5; w = rng.uniform(*width)
        dx, dz = math.cos(a), math.sin(a)
        t = np.clip((px - cx) * dx + (pz - cz) * dz, -L, L)
        dist = np.hypot(px - (cx + dx * t), pz - (cz + dz * t))
        taper = 1 - (np.abs(t) / L) ** 2.2                       # each cut runs out to a point at both ends
        cut = np.clip(1 - dist / (w * np.clip(taper, .05, 1)), 0, 1) ** .8 * rng.uniform(.6, 1)
        best = np.maximum(best, cut)
    return best

def game_material(name, albedo, normal=None, alpha=False):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Roughness'].default_value = .92; bsdf.inputs['Metallic'].default_value = 0
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = albedo; nt.links.new(t.outputs['Color'], bsdf.inputs['Base Color'])
    if alpha:
        nt.links.new(t.outputs['Alpha'], bsdf.inputs['Alpha'])
        if hasattr(m, 'surface_render_method'): m.surface_render_method = 'DITHERED'
        t.interpolation = 'Linear'; albedo.alpha_mode = 'CHANNEL_PACKED'
    if normal is not None:
        n = nt.nodes.new('ShaderNodeTexImage'); n.image = normal; nm = nt.nodes.new('ShaderNodeNormalMap')
        nt.links.new(n.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    return m

def decimated(src, name, tris):
    ob = src.copy(); ob.data = src.data.copy(); ob.name = name; ob.data.name = name
    bpy.context.scene.collection.objects.link(ob)
    mod = ob.modifiers.new('d', 'DECIMATE'); mod.ratio = min(1, tris / max(1, len(ob.data.polygons)))
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob

def tri_count(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)

# ---------------------------------------------------------------- CO02
def build_co02():
    ID = 'CO02_OldForestStele'
    reset()
    W, T, H = 1.1, .45, 2.4
    # ---- sculpt: the slab
    slab = dense_box('sculpt_slab', (W, T, H), 95)
    p = coords(slab); x, y, z = p[:, 0].copy(), p[:, 1].copy(), p[:, 2].copy()
    u = z / H
    front = smooth(-T * .5 + .02, -T * .5, y)                       # 1 on the front face
    # broken top: the top edge runs down from the left shoulder to the right, chipped
    top = H - .5 * smooth(-.1, .55, x) - .16 * smooth(-.55, -.3, -x) * 0 + .07 * (fbm(np.stack([x * 4, y * 6, np.zeros_like(x)], -1)) - .5)
    top -= .22 * smooth(.25, .55, x) * smooth(-.1, .22, y)            # a corner knocked off at the back right
    z = z * (top / H)
    # taper and a slight belly
    x = x * (1 - .13 * u + .04 * np.sin(u * 3.1))
    y = y * (1 - .3 * u)
    q = np.stack([x, y, z], -1)
    n0 = normals(slab)
    big = fbm(q * 1.7 + 3.1) - .5; mid = fbm(q * 5.5 + 9.7) - .5; fine = fbm(q * 19 + 1.3, 3) - .5
    # hewn stone: flat fracture facets off the corners, the shoulders and the broken top, then a little weathering
    rng = np.random.default_rng(20261111)
    planes = [((-.5, 0, 2.2), (-1, 0, 1.6)), ((.2, 0, 2.02), (.55, .1, 1)), ((.44, .1, 1.9), (1, .5, .9)), ((-.1, .17, 2.1), (-.2, 1, 1.3)),
              ((-.1, -.19, 2.2), (.1, -1, 1.5)), ((-.5, -.19, 1.2), (-1, -1, .1)), ((.47, -.19, 1.0), (1, -1.1, -.1)), ((.47, .17, .9), (1, 1, .15)),
              ((-.5, .18, 1.5), (-1, 1.2, .2)), ((-.52, -.17, .35), (-1, -.9, -.4)), ((.5, -.16, 1.9), (1, -.7, .3)), ((-.49, 0, 2.0), (-1, .1, .3))]
    for _ in range(16):   # small chips along the long edges
        sx_, sy_ = rng.choice([-1, 1]), rng.choice([-1, 1]); zc = rng.uniform(.3, 2.0)
        planes.append(((sx_ * (W * .5 - .1 * zc / H - rng.uniform(.0, .03)), sy_ * (T * .5 - .07 * zc / H - rng.uniform(.0, .025)), zc),
                       (sx_ * rng.uniform(.7, 1.3), sy_ * rng.uniform(.7, 1.3), rng.uniform(-.12, .12))))
    q = chip(q, planes)
    disp = .028 * big + .016 * mid + .006 * fine
    q = q + n0 * disp[:, None]
    # the hacked-away inscription: many separate slanted chisel slashes across the front, not tidy rows
    px, pz = q[:, 0], q[:, 2]
    cut = strokes(px, pz, rng, 64, (-.36, .34, .86, 1.86), (-34, -12), (.16, .5), (.014, .034))
    cut = np.maximum(cut, .8 * strokes(px, pz, rng, 26, (-.34, .32, .9, 1.8), (-52, -30), (.1, .26), (.01, .022)))
    ragged = .65 + .35 * smooth(.3, .62, fbm(q * np.array([9, 1, 20]) + 21))
    gouge = front * cut * ragged
    q[:, 1] += gouge * .05
    # the small waning moon above them, a shallow cut left untouched
    mx, mz, mr = .13, 2.02, .085
    d1 = np.hypot(q[:, 0] - mx, q[:, 2] - mz); d2 = np.hypot(q[:, 0] - (mx + .045), q[:, 2] - (mz + .012))
    moon = front * smooth(mr, mr - .008, d1) * smooth(mr * .93 - .008, mr * .93, d2)
    q[:, 1] += moon * .012
    set_coords(slab, q)
    # ---- sculpt: the plinth, half sunk
    PW, PT, PH = 1.38, .78, .34
    plinth = dense_box('sculpt_plinth', (PW, PT, PH), 80)
    pp = coords(plinth); pn = normals(plinth)
    pq = pp.copy(); pq[:, 2] -= .13
    pl = [((-.6, -.3, .16), (-1, -1, .9)), ((.62, -.33, .17), (1, -.8, 1.1)), ((.6, .33, .14), (.9, 1, 1.3)), ((-.62, .3, .18), (-1, .9, .7)),
          ((0, -.36, .2), (.05, -1, 1.4)), ((-.66, 0, .19), (-1, .1, 1.2)), ((.3, .37, .2), (.1, 1, 1.5))]
    for _ in range(10):
        sx_, sy_ = rng.choice([-1, 1]), rng.choice([-1, 1])
        pl.append(((sx_ * rng.uniform(.3, PW * .5 - .02), sy_ * (PT * .5 - rng.uniform(.0, .04)), .2 - rng.uniform(0, .04)), (sx_ * rng.uniform(0, .8), sy_ * 1, rng.uniform(.5, 1.6))))
    pq = chip(pq, pl)
    d = .022 * (fbm(pq * 2.3 + 60) - .5) + .012 * (fbm(pq * 8 + 70) - .5)
    pq = pq + pn * d[:, None]
    set_coords(plinth, pq)
    # ---- colour (vertex colour on the sculpt)
    def paint(ob, pts, is_slab):
        ob.data.update(); nn = normals(ob)
        stone = mix((.21, .245, .235), (.43, .46, .425), smooth(.3, .7, fbm(pts * 2.6 + 5)))
        stone = mix(stone, (.36, .33, .27), .3 * smooth(.5, .8, fbm(pts * 1.3 + 77)))                  # warm ochre drifts through the grey
        stone = mix(stone, (.43, .44, .39), .3 * smooth(.55, .8, fbm(pts * 9 + 33)))                 # paler flecks
        streak = smooth(.5, .78, fbm(pts * np.array([13, 13, .9]) + 11))                           # rain streaks run down
        stone = mix(stone, (.08, .1, .1), .5 * streak * smooth(.2, 1.6, pts[:, 2]))
        up = np.clip(nn[:, 2], 0, 1)
        if is_slab:
            g = gouge; stone = mix(stone, (.68, .65, .54), np.clip(g * 1.6, 0, 1) * .9)            # fresh stone inside the cuts
            stone = mix(stone, (.06, .07, .07), np.clip(g * (1 - g) * 3.6, 0, 1) * .65)            # shadow painted on the cut lips
            stone = mix(stone, (.66, .64, .52), np.clip(moon * 1.6, 0, 1))
            keep = 1 - np.clip(g * 2.5 + moon * 3, 0, 1)
        else:
            keep = np.ones(len(pts))
        shade = smooth(.15, -.45, pts[:, 0]) * .75 + smooth(-.05, .2, pts[:, 1]) * .5                 # left side and the back
        low = smooth(.75, .0, pts[:, 2])
        m = fbm(pts * 3.1 + 90) * .9 + fbm(pts * 11 + 14) * .35
        face = front if is_slab else 0
        moss = smooth(.64, .82, m + .34 * shade + .5 * up + .22 * low + (.14 if not is_slab else 0) - .2 * face) * keep
        mossc = mix((.1, .17, .06), (.27, .36, .12), smooth(.3, .75, fbm(pts * 14 + 3)))
        mossc = mix(mossc, (.45, .5, .2), .5 * smooth(.6, .85, fbm(pts * 30 + 8)) * up)             # sunlit tips
        col = mix(stone, mossc, moss)
        cell = fbm(pts * 6.5 + 200, 2); lichen = smooth(.69, .74, cell) * smooth(.45, .6, fbm(pts * 2.2 + 55)) * (1 - moss) * keep
        col = mix(col, (.55, .6, .47), lichen * .75)
        col = mix(col, (.17, .13, .09), smooth(.1, -.06, pts[:, 2]) * .8)                             # soil where it meets the ground
        set_colour(ob, col)
        return moss
    moss_s = paint(slab, q, True); moss_p = paint(plinth, pq, False)
    # moss has body: lift it a little off the stone
    slab.data.update(); plinth.data.update()
    set_coords(slab, q + normals(slab) * (moss_s * .016)[:, None]); set_coords(plinth, pq + normals(plinth) * (moss_p * .02)[:, None])
    # the slab leans, as if the ground gave under one side
    lean = Matrix.Rotation(math.radians(3.6), 4, 'Y') @ Matrix.Rotation(math.radians(-2.2), 4, 'X')
    slab.matrix_world = Matrix.Translation((0, .02, .1)) @ lean
    bpy.context.view_layer.update()
    for o in (slab, plinth):
        o.data.transform(o.matrix_world); o.matrix_world = Matrix.Identity(4)
        for poly in o.data.polygons: poly.use_smooth = True
        o.data.materials.append(colour_material('Sculpt_' + o.name))
    sculpt_tris = tri_count(slab) + tri_count(plinth)
    # ---- game mesh: both pieces joined, decimated, unwrapped once
    for o in bpy.context.scene.objects: o.select_set(False)
    a = slab.copy(); a.data = slab.data.copy(); b = plinth.copy(); b.data = plinth.data.copy()
    for o in (a, b): bpy.context.scene.collection.objects.link(o); o.select_set(True)
    bpy.context.view_layer.objects.active = a; bpy.ops.object.join(); joined = a; joined.name = 'joined'
    # drop what is under the ground (never seen) before decimating
    bm = bmesh.new(); bm.from_mesh(joined.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, -.02), plane_no=(0, 0, -1), clear_outer=True)
    bm.to_mesh(joined.data); bm.free()
    lod0 = decimated(joined, ID + '_LOD0', 5200)
    bpy.data.objects.remove(joined)
    lod0.data.materials.clear()
    for o in bpy.context.scene.objects: o.select_set(False)
    lod0.select_set(True); bpy.context.view_layer.objects.active = lod0
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(62), island_margin=.012)
    bpy.ops.object.mode_set(mode='OBJECT')
    for poly in lod0.data.polygons: poly.use_smooth = True
    # ---- bake
    bake_mat = bpy.data.materials.new('bake'); bake_mat.use_nodes = True; lod0.data.materials.append(bake_mat)
    col_img = image('bake_colour'); nrm_img = image('bake_normal', colour=(.5, .5, 1, 1), non_color=True); ao_img = image('bake_ao', colour=(1, 1, 1, 1), non_color=True)
    bake([slab, plinth], lod0, col_img, 'EMIT', bake_mat)
    bake([slab, plinth], lod0, nrm_img, 'NORMAL', bake_mat)
    bpy.context.scene.cycles.samples = 48
    bake([slab, plinth], lod0, ao_img, 'AO', bake_mat)
    col = pixels(col_img); ao = pixels(ao_img)[..., :1]
    shade = .42 + .58 * np.clip(ao, 0, 1) ** 1.4
    albedo = col.copy(); albedo[..., :3] = np.clip(col[..., :3] * shade * 1.06, 0, 1); albedo[..., 3] = 1
    mask = np.zeros_like(col); mask[..., 1] = np.clip(ao[..., 0], 0, 1); mask[..., 3] = .1                 # URP mask: G occlusion, A smoothness
    nrm = pixels(nrm_img); nrm[..., 3] = 1
    a_img = save(albedo, TEX / f'{ID}_Albedo.png'); n_img = save(nrm, TEX / f'{ID}_Normal.png', True); save(mask, TEX / f'{ID}_MaskURP.png', True)
    lod0.data.materials.clear(); lod0.data.materials.append(game_material(ID, a_img, n_img))
    # ---- ferns and dead leaves at the foot: alpha-cut cards, a Detail object low settings can drop
    fern_img = fern_texture(ID + '_Detail_Ferns')
    ferns = fern_cards(ID + '_Detail_Ferns_LOD0', [(-.62, -.42, 0, 20, .55), (-.5, -.5, 0, 75, .42), (.6, -.44, 0, 150, .5), (.72, -.2, 0, 110, .4),
                                                   (-.74, .12, 0, -40, .46), (.1, -.52, 0, 95, .34), (-.2, .5, 0, -100, .5), (.55, .46, 0, -150, .44)])
    ferns.data.materials.append(game_material(ID + '_Detail_Ferns', fern_img, alpha=True))
    # ---- LODs and collision
    lod1 = decimated(lod0, ID + '_LOD1', 2400); lod2 = decimated(lod0, ID + '_LOD2', 700)
    f1 = decimated(ferns, ID + '_Detail_Ferns_LOD1', tri_count(ferns) // 2)
    col_ob = dense_box(ID + '_Collision', (1.2, .7, 2.3), 0); col_ob.display_type = 'WIRE'
    for o in (slab, plinth): o.hide_render = True; o.hide_viewport = True
    game = [lod0, lod1, lod2, ferns, f1, col_ob]
    info = {
        'asset': ID, 'version': 'v001', 'name_zh': '古林碑', 'slot': 'D4_MossShrine_Stele', 'minTier': 'standard',
        'detailObjects': [ID + '_Detail_Ferns'],
        'note': '碑文被鑿掉，只留一枚缺月記號；不寫任何字。',
        'units': 'meters', 'front': '-Y (Blender)', 'origin': 'ground centre',
        'dimensions_m': [round(v, 3) for v in lod0.dimensions], 'sculpt_triangles': sculpt_tris,
        'lods': {'LOD0': tri_count(lod0) + tri_count(ferns), 'LOD1': tri_count(lod1) + tri_count(f1), 'LOD2': tri_count(lod2)},
        'detail_triangles': {'LOD0': tri_count(ferns), 'LOD1': tri_count(f1)},
        'materials': 2, 'textures_px': {f'{ID}_Albedo.png': SIZE, f'{ID}_Normal.png': SIZE, f'{ID}_MaskURP.png': SIZE, f'{ID}_Detail_Ferns_Albedo.png': 512},
        'collision': 'box 1.2 x 0.7 x 2.3 m',
        'status': {'Exported': True, 'Imported': False, 'VisuallyVerified': False, 'InGameVerified': False},
    }
    finish(ID, game, info, [lod0, ferns])

# ---------------------------------------------------------------- shared painting for loose pieces
def paint_piece(ob, kind, moss_bias=0.0, seed=0.0, ground=True):
    """Vertex colour for a sculpt piece in world space. kind: stone, granite, tile, timber, rope. ground: the piece stands on soil at z = 0."""
    ob.data.update(); pts = coords(ob) + seed; nn = normals(ob); up = np.clip(nn[:, 2], 0, 1); z = pts[:, 2] - seed
    if kind == 'stone':
        base = mix((.25, .27, .25), (.47, .48, .43), smooth(.3, .7, fbm(pts * 3.1 + 5)))
        base = mix(base, (.42, .38, .3), .3 * smooth(.5, .8, fbm(pts * 1.6 + 77)))
        base = mix(base, (.1, .12, .12), .4 * smooth(.5, .78, fbm(pts * np.array([14, 14, 1.2]) + 11)))
    elif kind == 'granite':   # B 區: pale grey-white granite, cool shadows in the cracks, a little warm staining
        base = mix((.56, .57, .55), (.8, .8, .76), smooth(.3, .7, fbm(pts * 1.9 + 5)))
        base = mix(base, (.7, .64, .54), .25 * smooth(.5, .8, fbm(pts * .9 + 77)))
        base = mix(base, (.3, .33, .36), .5 * smooth(.6, .82, fbm(pts * np.array([7, 7, 1.1]) + 11)))
        base = mix(base, (.42, .45, .47), .35 * smooth(.62, .7, fbm(pts * 5 + 300, 2)))
    elif kind == 'rope':
        twist = .5 + .5 * np.sin((pts[:, 0] * 60 + pts[:, 2] * 40 + pts[:, 1] * 40))
        base = mix((.36, .29, .18), (.6, .52, .34), twist)
    elif kind == 'tile':
        base = mix((.16, .18, .21), (.3, .32, .35), smooth(.3, .7, fbm(pts * 9 + 5)))
        base = mix(base, (.36, .25, .2), .25 * smooth(.6, .8, fbm(pts * 5 + 31)))                   # a little fired clay showing
    else:
        base = mix((.17, .11, .07), (.36, .25, .16), smooth(.3, .7, fbm(pts * np.array([2.5, 22, 22]) + 5)))
        base = mix(base, (.06, .05, .04), .55 * smooth(.55, .8, fbm(pts * np.array([1.5, 30, 30]) + 60)))   # rot along the grain
        base = mix(base, (.5, .45, .36), .2 * smooth(.6, .85, fbm(pts * 7 + 13)))
    m = fbm(pts * 3.4 + 90) * .9 + fbm(pts * 12 + 14) * .35
    moss = smooth(.76, .92, m + .34 * up + (.2 * smooth(.3, 0, z) if ground else 0) + moss_bias)
    mossc = mix((.11, .16, .07), (.25, .31, .13), smooth(.3, .75, fbm(pts * 14 + 3)))
    mossc = mix(mossc, (.4, .43, .2), .45 * smooth(.6, .85, fbm(pts * 30 + 8)) * up)
    col = mix(base, mossc, moss)
    lichen = smooth(.69, .74, fbm(pts * 7 + 200, 2)) * smooth(.45, .6, fbm(pts * 2.2 + 55)) * (1 - moss)
    col = mix(col, (.55, .6, .47), lichen * (.75 if kind == 'stone' else .3))
    if ground: col = mix(col, (.17, .13, .09), smooth(.05, -.04, z) * .8)
    set_colour(ob, col)
    set_coords(ob, coords(ob) + normals(ob) * (moss * .012)[:, None])
    for poly in ob.data.polygons: poly.use_smooth = True
    ob.data.materials.append(colour_material('Sculpt_' + ob.name))

def stone_block(name, size, cuts, chips, rng, rough=.02):
    ob = dense_box(name, size, cuts); p = coords(ob); n = normals(ob)
    planes = []
    sx, sy, sz = size
    for _ in range(chips):
        a, b = rng.choice([-1, 1]), rng.choice([-1, 1]); kind = rng.integers(0, 3)
        if kind == 0: planes.append(((a * (sx * .5 - rng.uniform(.0, .03)), b * (sy * .5 - rng.uniform(.0, .03)), rng.uniform(0, sz)), (a, b * rng.uniform(.6, 1.4), rng.uniform(-.2, .2))))
        elif kind == 1: planes.append(((a * (sx * .5 - rng.uniform(.0, .03)), rng.uniform(-sy, sy) * .5, sz - rng.uniform(.0, .025)), (a, rng.uniform(-.3, .3), rng.uniform(.6, 1.4))))
        else: planes.append(((rng.uniform(-sx, sx) * .5, b * (sy * .5 - rng.uniform(.0, .03)), sz - rng.uniform(.0, .025)), (rng.uniform(-.3, .3), b, rng.uniform(.6, 1.4))))
    p = chip(p, planes)
    p = p + n * (rough * (fbm(p * 3 + rng.uniform(0, 50)) - .5) + rough * .45 * (fbm(p * 11 + 7) - .5))[:, None]
    set_coords(ob, p)
    return ob

def place(ob, loc, rot=(0, 0, 0)):
    """Bake a rotation (degrees, XYZ) and a location into the mesh."""
    m = Matrix.Translation(loc) @ Matrix.Rotation(math.radians(rot[2]), 4, 'Z') @ Matrix.Rotation(math.radians(rot[1]), 4, 'Y') @ Matrix.Rotation(math.radians(rot[0]), 4, 'X')
    ob.data.transform(m); ob.data.update(); return ob

def lathe(name, profile, segments=72):
    """Revolve (radius, height) points around Z into a dense mesh."""
    bm = bmesh.new(); rings = []
    for r, h in profile:
        rings.append([bm.verts.new((max(r, .001) * math.cos(2 * math.pi * k / segments), max(r, .001) * math.sin(2 * math.pi * k / segments), h)) for k in range(segments)])
    for a, b in zip(rings, rings[1:]):
        for k in range(segments):
            bm.faces.new((a[k], a[(k + 1) % segments], b[(k + 1) % segments], b[k]))
    bmesh.ops.triangulate(bm, faces=bm.faces[:]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob

def bake_game_mesh(ID, sculpts, tris, lods, clip_ground=True):
    """Join copies of the sculpt pieces, decimate, unwrap, bake colour, normal and occlusion. Returns LOD0, LOD1, LOD2."""
    for o in bpy.context.scene.objects: o.select_set(False)
    copies = []
    for o in sculpts:
        c = o.copy(); c.data = o.data.copy(); bpy.context.scene.collection.objects.link(c); c.select_set(True); copies.append(c)
    bpy.context.view_layer.objects.active = copies[0]; bpy.ops.object.join(); joined = copies[0]
    if clip_ground:
        bm = bmesh.new(); bm.from_mesh(joined.data)
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, -.02), plane_no=(0, 0, -1), clear_outer=True)
        bm.to_mesh(joined.data); bm.free()
    lod0 = decimated(joined, ID + '_LOD0', tris); bpy.data.objects.remove(joined); lod0.data.materials.clear()
    for o in bpy.context.scene.objects: o.select_set(False)
    lod0.select_set(True); bpy.context.view_layer.objects.active = lod0
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(62), island_margin=.012); bpy.ops.object.mode_set(mode='OBJECT')
    for poly in lod0.data.polygons: poly.use_smooth = True
    bake_mat = bpy.data.materials.new('bake'); bake_mat.use_nodes = True; lod0.data.materials.append(bake_mat)
    col_img = image('bake_colour'); nrm_img = image('bake_normal', colour=(.5, .5, 1, 1), non_color=True); ao_img = image('bake_ao', colour=(1, 1, 1, 1), non_color=True)
    bpy.context.scene.cycles.samples = 24
    bpy.context.scene.render.bake.cage_extrusion = .03
    bake(sculpts, lod0, col_img, 'EMIT', bake_mat); bake(sculpts, lod0, nrm_img, 'NORMAL', bake_mat)
    bpy.context.scene.cycles.samples = 48; bake(sculpts, lod0, ao_img, 'AO', bake_mat)
    col = pixels(col_img); ao = pixels(ao_img)[..., :1]
    albedo = col.copy(); albedo[..., :3] = np.clip(col[..., :3] * (.42 + .58 * np.clip(ao, 0, 1) ** 1.4) * 1.06, 0, 1); albedo[..., 3] = 1
    mask = np.zeros_like(col); mask[..., 1] = np.clip(ao[..., 0], 0, 1); mask[..., 3] = .1
    nrm = pixels(nrm_img); nrm[..., 3] = 1
    a_img = save(albedo, TEX / f'{ID}_Albedo.png'); n_img = save(nrm, TEX / f'{ID}_Normal.png', True); save(mask, TEX / f'{ID}_MaskURP.png', True)
    lod0.data.materials.clear(); lod0.data.materials.append(game_material(ID, a_img, n_img))
    return [lod0] + [decimated(lod0, f'{ID}_LOD{i + 1}', t) for i, t in enumerate(lods)]

# ---------------------------------------------------------------- CO03
def build_co03():
    """Shrine remnants (D4): a stone offering table fallen on its broken leg, a tipped incense burner, broken tiles and rotted timber."""
    ID = 'CO03_ShrineRemnants'
    reset(); rng = np.random.default_rng(20261112); parts = []
    # the table: one leg stands, the other has snapped, so the slab rests at a tilt
    leg = place(stone_block('leg_standing', (.26, .3, .56), 110, 9, rng), (-.42, 0, 0)); parts.append((leg, 'stone', 0))
    cap = place(stone_block('leg_cap', (.34, .38, .09), 110, 6, rng), (-.42, 0, .55)); parts.append((cap, 'stone', .05))
    stub = place(stone_block('leg_stub', (.26, .3, .2), 110, 12, rng, .03), (.4, .02, 0), (0, 0, 8)); parts.append((stub, 'stone', .1))
    fallen = place(stone_block('leg_fallen', (.24, .28, .34), 110, 12, rng, .03), (.62, -.3, .11), (82, 0, 35)); parts.append((fallen, 'stone', .0))
    slab = stone_block('slab', (1.24, .52, .13), 120, 16, rng)
    place(slab, (-.02, 0, .425), (0, 22.5, 0)); parts.append((slab, 'stone', .06))
    # the incense burner: a round three-legged bowl lying on its side, empty, rim chipped
    prof = [(0.0, .1), (.07, .1), (.13, .13), (.17, .2), (.18, .27), (.165, .33), (.185, .35), (.2, .37), (.19, .385), (.165, .37), (.15, .34), (.155, .27), (.14, .2), (.1, .15), (.0, .14)]
    dense = []
    for (r0, h0), (r1, h1) in zip(prof, prof[1:]):
        for k in range(6): dense.append((r0 + (r1 - r0) * k / 6, h0 + (h1 - h0) * k / 6))
    dense.append(prof[-1])
    bowl = lathe('burner_bowl', dense, 96); bp = coords(bowl)
    bp = chip(bp, [((.16, .02, .37), (1, .2, .9)), ((-.05, .17, .38), (-.2, 1, 1.4))])
    bowl.data.update()
    set_coords(bowl, bp); bp = bp + normals(bowl) * (.006 * (fbm(bp * 14 + 3) - .5))[:, None]; set_coords(bowl, bp)
    legs = []
    for k in range(3):
        a = 2 * math.pi * k / 3 + .4
        f = place(stone_block(f'burner_leg{k}', (.06, .06, .13), 160, 3, rng, .006), (.1 * math.cos(a), .1 * math.sin(a), 0), (0, 0, math.degrees(a)))
        legs.append(f)
    for o in [bowl] + legs:
        place(o, (0, 0, -.2)); place(o, (-.06, -.48, .19), (72, 0, -28))
    parts.append((bowl, 'stone', -.05)); parts += [(f, 'stone', -.05) for f in legs]
    # broken roof tiles: curved shards in a small heap, some leaning on each other
    for k in range(9):
        L = rng.uniform(.1, .24); arc = rng.uniform(.9, 1.7); R = .1
        t = dense_box(f'tile{k}', (R * arc, L, .016), 220); tp = coords(t)
        ang = tp[:, 0] / R; rad = R + tp[:, 2]
        tp = np.stack([rad * np.sin(ang), tp[:, 1], rad * np.cos(ang) - R * math.cos(arc / 2)], -1)
        tp = chip(tp, [((rng.uniform(-.03, .03), L * .5 - rng.uniform(.01, .05), 0), (rng.uniform(-.6, .6), 1, rng.uniform(-.3, .3)))])
        set_coords(t, tp)
        place(t, (.34 + rng.uniform(-.2, .22), -.42 + rng.uniform(-.16, .16), .012 + .028 * (k % 3)), (rng.uniform(-22, 22), rng.uniform(-18, 18), rng.uniform(0, 360)))
        parts.append((t, 'tile', -.12))
    # rotted timber: what is left of the roof frame
    for k, (L, loc, rot) in enumerate([(.86, (.5, .34, .045), (4, 3, 18)), (.6, (-.2, .42, .04), (-3, -2, -12)), (.44, (.6, -.2, .12), (10, 24, 100))]):
        b = stone_block(f'timber{k}', (L, .085, .07), 150, 8, rng, .012)
        bp2 = coords(b); bp2[:, 2] -= .035
        ends = smooth(L * .5 - .12, L * .5, np.abs(bp2[:, 0])) * (.5 + fbm(bp2 * np.array([3, 40, 40]) + k)) * .05      # splintered ends
        bp2[:, 0] -= np.sign(bp2[:, 0]) * ends; set_coords(b, bp2)
        place(b, loc, rot); parts.append((b, 'timber', .08))
    for o, kind, bias in parts: paint_piece(o, kind, bias)
    sculpts = [o for o, _, _ in parts]
    sculpt_tris = sum(tri_count(o) for o in sculpts)
    lod0, lod1, lod2 = bake_game_mesh(ID, sculpts, 6200, (2900, 850))
    fern_img = fern_texture(ID + '_Detail_Ferns')
    ferns = fern_cards(ID + '_Detail_Ferns_LOD0', [(-.66, -.22, 0, 200, .46), (-.6, .3, 0, 150, .4), (.82, .16, 0, 20, .44), (.2, .52, 0, 80, .4), (-.2, -.72, 0, 260, .36), (.86, -.5, 0, -40, .38)])
    ferns.data.materials.append(game_material(ID + '_Detail_Ferns', fern_img, alpha=True))
    f1 = decimated(ferns, ID + '_Detail_Ferns_LOD1', tri_count(ferns) // 2)
    col_ob = dense_box(ID + '_Collision', (1.3, .6, .62), 0); col_ob.display_type = 'WIRE'
    for o in sculpts: o.hide_render = True; o.hide_viewport = True
    info = {
        'asset': ID, 'version': 'v001', 'name_zh': '祠內殘件', 'slot': 'D4_MossShrine_Remnants', 'minTier': 'standard',
        'detailObjects': [ID + '_Detail_Ferns'], 'note': '斷腿供桌、傾倒的空香爐、碎瓦與朽木；沒有神像、供品和文字。',
        'units': 'meters', 'front': '-Y (Blender)', 'origin': 'ground centre',
        'dimensions_m': [round(v, 3) for v in lod0.dimensions], 'sculpt_triangles': sculpt_tris,
        'lods': {'LOD0': tri_count(lod0) + tri_count(ferns), 'LOD1': tri_count(lod1) + tri_count(f1), 'LOD2': tri_count(lod2)},
        'detail_triangles': {'LOD0': tri_count(ferns), 'LOD1': tri_count(f1)},
        'materials': 2, 'textures_px': {f'{ID}_Albedo.png': SIZE, f'{ID}_Normal.png': SIZE, f'{ID}_MaskURP.png': SIZE, f'{ID}_Detail_Ferns_Albedo.png': 512},
        'collision': 'box 1.3 x 0.6 x 0.62 m (the table; the small pieces do not block)',
        'status': {'Exported': True, 'Imported': False, 'VisuallyVerified': False, 'InGameVerified': False},
    }
    finish(ID, [lod0, lod1, lod2, ferns, f1, col_ob], info, [lod0, ferns], target=(.2, 0, .45), dist=.62)

# ---------------------------------------------------------------- CO01
def height_disk(name, radius, per_m, height):
    """A round patch of ground as a dense height field: height(x, y) -> z. Faces outside the radius are dropped."""
    n = int(radius * 2 * per_m) + 1
    xs = np.linspace(-radius, radius, n); gx, gy = np.meshgrid(xs, xs, indexing='xy')
    pts = np.stack([gx.ravel(), gy.ravel(), np.zeros(n * n)], -1)
    pts[:, 2] = height(pts[:, 0], pts[:, 1])
    idx = np.arange(n * n).reshape(n, n)
    a, b, c, d = idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()
    cx = (pts[a, 0] + pts[c, 0]) * .5; cy = (pts[a, 1] + pts[c, 1]) * .5
    keep = np.hypot(cx, cy) < radius
    faces = np.concatenate([np.stack([a, b, c], -1)[keep], np.stack([a, c, d], -1)[keep]])
    me = bpy.data.meshes.new(name); me.from_pydata(pts.tolist(), [], faces.tolist()); me.update()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS'); bm.to_mesh(me); bm.free(); me.update()
    return ob

def tube(name, path, radii, segments=28, per_m=90):
    """A dense tube along a polyline (root, branch): path points, a radius at each."""
    path = [Vector(p) for p in path]; rings = []; bm = bmesh.new()
    pts = []; rs = []
    for (p0, p1), (r0, r1) in zip(zip(path, path[1:]), zip(radii, radii[1:])):
        steps = max(2, int((p1 - p0).length * per_m))
        for k in range(steps): t = k / steps; pts.append(p0.lerp(p1, t)); rs.append(r0 + (r1 - r0) * t)
    pts.append(path[-1]); rs.append(radii[-1])
    # smooth the polyline a little so the root bends instead of kinking
    for _ in range(40):
        pts = [pts[0]] + [(pts[i - 1] + pts[i] * 2 + pts[i + 1]) / 4 for i in range(1, len(pts) - 1)] + [pts[-1]]
    up = Vector((0, 0, 1))
    for i, (p, r) in enumerate(zip(pts, rs)):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = d.cross(up); side = side.normalized() if side.length > 1e-4 else Vector((1, 0, 0)); top = side.cross(d).normalized()
        rings.append([bm.verts.new(p + (side * math.cos(2 * math.pi * k / segments) + top * math.sin(2 * math.pi * k / segments)) * r) for k in range(segments)])
    for a, b in zip(rings, rings[1:]):
        for k in range(segments): bm.faces.new((a[k], a[(k + 1) % segments], b[(k + 1) % segments], b[k]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.triangulate(bm, faces=bm.faces[:]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob

def build_co01():
    """A freshly dug pit between two roots of the great tree (D2): spade-cut walls, a ring of thrown-up earth and stones, torn root ends."""
    ID = 'CO01_DugPit'
    reset(); rng = np.random.default_rng(20261113)
    DEPTH = .55; R = 2.0

    def ell(x, y): return np.sqrt((x / 1.1) ** 2 + (y / .8) ** 2)
    def spoil(x, y):
        e = ell(x, y); ang = np.arctan2(y, x)
        q = np.stack([x, y, np.zeros_like(x)], -1)
        lump = .55 + .9 * fbm(q * 2.2 + 31)
        side = .75 + .45 * np.cos(ang - .5)                                    # more earth thrown to one side
        ring = np.exp(-((e - 1.42) / .3) ** 2) * .42 * lump * side
        return ring
    def height(x, y):
        e = ell(x, y); ang = np.arctan2(y, x)
        q = np.stack([x, y, np.zeros_like(x)], -1)
        cut = e + .035 * np.sin(ang * 17 + 2 * fbm(q * 3)) + .05 * (fbm(q * 4 + 9) - .5)          # spade bites round the edge
        pit = -DEPTH * smooth(1.02, .8, cut)
        floor = .07 * (fbm(q * 5 + 50) - .5) * smooth(.9, .5, e)
        ground = .05 * (fbm(q * 1.6 + 70) - .5) + .02 * (fbm(q * 7 + 20) - .5)
        stones = .05 * smooth(.66, .78, fbm(q * 9 + 400, 3)) * smooth(1.05, 1.25, e)
        skirt = -.14 * smooth(R - .35, R, np.hypot(x, y))                         # the rim sinks into the terrain it is laid on
        return pit + floor + spoil(x, y) + ground + stones + skirt
    ground = height_disk('sculpt_ground', R, 105, height)
    gp = coords(ground); x, y, z = gp[:, 0], gp[:, 1], gp[:, 2]; e = ell(x, y)
    q = np.stack([x, y, np.zeros_like(x)], -1); gn = normals(ground)
    wall = smooth(1.08, .95, e) * smooth(.6, .85, e)
    soil = mix((.2, .14, .09), (.34, .25, .16), smooth(.3, .7, fbm(gp * 4 + 3)))
    fresh = mix((.36, .26, .17), (.48, .36, .23), smooth(.3, .7, fbm(gp * np.array([9, 9, 3]) + 12)))        # newly cut earth is paler
    col = mix(soil, fresh, np.clip(wall * 1.1 + .7 * smooth(.25, .05, np.abs(e - 1.42)) * (spoil(x, y) > .12), 0, 1))
    layers = .5 + .5 * np.sin(z * 34 + 2 * fbm(q * 2))                                                     # soil layers on the cut wall
    col = mix(col, (.17, .12, .08), wall * smooth(.55, .9, layers) * .5)
    col = mix(col, (.15, .1, .07), smooth(.75, .3, e) * .45)                                               # damp floor
    stone = smooth(.66, .78, fbm(q * 9 + 400, 3)) * smooth(1.05, 1.25, e)
    col = mix(col, mix((.33, .34, .32), (.5, .5, .46), smooth(.3, .7, fbm(gp * 13 + 5))), stone * .9)
    leaf = smooth(.71, .76, fbm(q * 15 + 800, 2)) * smooth(1.2, 1.5, e)
    col = mix(col, mix((.42, .26, .12), (.5, .36, .15), fbm(gp * 21 + 4)), leaf * .85)
    old = smooth(1.5, 1.85, e) + .5 * smooth(.2, -.6, np.cos(np.arctan2(y, x) - .5)) * smooth(1.2, 1.5, e)   # the older, outer ground has greened over
    moss = smooth(.6, .8, fbm(gp * 3 + 90) * .9 + fbm(gp * 12 + 14) * .35 + .3 * old) * (1 - wall) * smooth(.95, 1.2, e) * (1 - stone * .6)
    col = mix(col, mix((.11, .17, .07), (.26, .33, .13), smooth(.3, .75, fbm(gp * 14 + 3))), moss * .9)
    set_colour(ground, col)
    for poly in ground.data.polygons: poly.use_smooth = True
    ground.data.materials.append(colour_material('Sculpt_ground'))
    sculpts = [ground]
    # two roots of the great tree pass either side; the diggers cut through the small ones
    def zat(px, py): return float(height(np.array([px]), np.array([py]))[0])
    roots = [([(-1.95, .95), (-1.2, 1.05), (-.3, 1.2), (.7, 1.12), (1.9, 1.3)], (.2, .17, .15, .13, .1)),
             ([(-1.9, -1.2), (-1.0, -1.02), (.1, -1.12), (1.0, -1.25), (1.85, -1.0)], (.16, .14, .13, .1, .08)),
             ([(-.3, 1.2), (-.1, .95), (.05, .78)], (.07, .055, .04)), ([(.1, -1.12), (.0, -.9), (-.08, -.74)], (.06, .05, .035)),
             ([(.7, 1.12), (.82, .9), (.86, .62)], (.05, .04, .03))]
    for k, (pth, rad) in enumerate(roots):
        cut_end = k >= 2
        p3 = [(px, py, zat(px, py) + r * (.25 if not cut_end else .1) - (.18 if (cut_end and i == len(pth) - 1) else 0)) for i, ((px, py), r) in enumerate(zip(pth, rad))]
        t = tube(f'sculpt_root{k}', p3, rad)
        tp = coords(t); tn = normals(t)
        ridged = .012 * np.sin(np.arctan2(tn[:, 2], tn[:, 0] + 1e-6) * 9 + 6 * fbm(tp * 3)) + .014 * (fbm(tp * 9 + k) - .5)
        set_coords(t, tp + tn * ridged[:, None]); t.data.update()
        tp = coords(t); tn = normals(t)
        bark = mix((.17, .12, .08), (.33, .25, .17), smooth(.3, .7, fbm(tp * np.array([6, 6, 6]) + k)))
        bark = mix(bark, (.09, .07, .05), .5 * smooth(.5, .8, fbm(tp * 22 + 3)))
        if cut_end:
            endp = Vector(p3[-1]); dist = np.linalg.norm(tp - np.array(endp), axis=1)
            bark = mix(bark, (.72, .62, .44), smooth(rad[-1] * 1.5, rad[-1] * .6, dist))          # the torn end shows pale wood
        m = smooth(.62, .8, fbm(tp * 4 + 90) + .35 * np.clip(tn[:, 2], 0, 1))
        bark = mix(bark, mix((.11, .17, .07), (.26, .33, .13), fbm(tp * 14 + 3)), m * (.2 if cut_end else .8))
        set_colour(t, bark)
        for poly in t.data.polygons: poly.use_smooth = True
        t.data.materials.append(colour_material(f'Sculpt_root{k}')); sculpts.append(t)
    sculpt_tris = sum(tri_count(o) for o in sculpts)
    lod0, lod1, lod2 = bake_game_mesh(ID, sculpts, 6000, (2800, 800), clip_ground=False)
    fern_img = fern_texture(ID + '_Detail_Ferns')
    spots = []
    for (fx, fy, yaw, size) in [(-1.5, .45, 170, .5), (-1.62, -.3, 200, .42), (1.55, .4, 10, .46), (1.2, -1.55, -50, .44), (-.6, 1.62, 100, .4), (.4, -1.7, -90, .38), (1.7, -.3, -10, .36)]:
        spots.append((fx, fy, zat(fx, fy) - .02, yaw, size))
    ferns = fern_cards(ID + '_Detail_Ferns_LOD0', spots)
    ferns.data.materials.append(game_material(ID + '_Detail_Ferns', fern_img, alpha=True))
    f1 = decimated(ferns, ID + '_Detail_Ferns_LOD1', tri_count(ferns) // 2)
    col_ob = dense_box(ID + '_Collision', (2.5, 1.9, .7), 0); col_ob.location = (0, 0, -.1); col_ob.display_type = 'WIRE'
    for o in sculpts: o.hide_render = True; o.hide_viewport = True
    info = {
        'asset': ID, 'version': 'v001', 'name_zh': '神木旁被挖的坑', 'slot': 'D2_GreatTree_DugPit', 'minTier': 'standard',
        'detailObjects': [ID + '_Detail_Ferns'], 'note': '坑是空的，沒有工具、人和文字。坑底在原點下方 0.55 m：落位時該處地形要先壓低約 0.6 m，模型的外緣會沉進地表 0.14 m 蓋住接縫。',
        'units': 'meters', 'front': '-Y (Blender)', 'origin': 'ground level, pit centre',
        'dimensions_m': [round(v, 3) for v in lod0.dimensions], 'sculpt_triangles': sculpt_tris,
        'lods': {'LOD0': tri_count(lod0) + tri_count(ferns), 'LOD1': tri_count(lod1) + tri_count(f1), 'LOD2': tri_count(lod2)},
        'detail_triangles': {'LOD0': tri_count(ferns), 'LOD1': tri_count(f1)},
        'materials': 2, 'textures_px': {f'{ID}_Albedo.png': SIZE, f'{ID}_Normal.png': SIZE, f'{ID}_MaskURP.png': SIZE, f'{ID}_Detail_Ferns_Albedo.png': 512},
        'collision': 'box 2.5 x 1.9 x 0.7 m over the pit (walk around it)',
        'status': {'Exported': True, 'Imported': False, 'VisuallyVerified': False, 'InGameVerified': False},
    }
    finish(ID, [lod0, lod1, lod2, ferns, f1, col_ob], info, [lod0, ferns], target=(0, 0, .0), dist=.95, floor_z=-.75, high=True)

# ---------------------------------------------------------------- CO04
def reed_texture(name, W=512, H=1024):
    """A clump of reeds on one alpha texture: straw stalks, long bending leaves, feathery seed heads. Drawn with numpy."""
    rgba = np.zeros((H, W, 4), dtype=np.float32); rng = np.random.default_rng(404)
    def stamp(cx, cy, r, colour):
        x0, x1 = max(0, int(cx - r - 1)), min(W, int(cx + r + 2)); y0, y1 = max(0, int(cy - r - 1)), min(H, int(cy + r + 2))
        if x0 >= x1 or y0 >= y1: return
        yy, xx = np.mgrid[y0:y1, x0:x1]
        m = (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r
        rgba[y0:y1, x0:x1, :3][m] = colour; rgba[y0:y1, x0:x1, 3][m] = 1
    stalks = []
    for i in range(11):
        x0 = rng.uniform(.14, .86) * W; lean = rng.uniform(-.16, .16) * W; top = rng.uniform(.62, .93) * H; stalks.append((x0, lean, top))
    def sx(st, y): return st[0] + st[1] * (y / st[2]) ** 2
    # leaves first (behind the stalks)
    for st in stalks:
        for _ in range(int(rng.integers(3, 6))):
            y0 = rng.uniform(.12, .7) * st[2]; d = rng.choice([-1, 1]); L = rng.uniform(.16, .34) * H; wid = rng.uniform(3.2, 5.5)
            tone = rng.uniform(0, 1); droop = rng.uniform(.25, .8)
            for k in range(90):
                s = k / 89
                px = sx(st, y0) + d * L * (.42 * s + .2 * s * s); py = y0 + L * (.95 * s - droop * s * s)
                w = wid * math.sin(max(.03, s) ** .6 * math.pi) ** .7 + .6
                g = np.array([.3 + .12 * tone + .1 * s, .4 + .1 * tone + .05 * s, .17 + .05 * s]) * (.82 + .18 * math.sin(k * .7))
                dry = max(0, s - .75) * 2.2                                                  # tips dry to straw
                stamp(px, py, w, g * (1 - dry) + np.array([.6, .52, .3]) * dry)
    for st in stalks:
        for y in range(0, int(st[2])):
            t = y / st[2]
            c = np.array([.56, .5, .3]) * (1 - t) + np.array([.42, .46, .24]) * t
            if (y // 46) % 2 == 0 and (y % 46) < 3: c = c * .7                                # nodes
            stamp(sx(st, y), y, 2.6 - 1.2 * t, c)
        # seed head: a soft plume leaning with the stalk
        px, py = sx(st, st[2]), st[2]; ph = rng.uniform(.07, .11) * H; side = np.sign(st[1]) or 1
        for k in range(260):
            a = rng.uniform(0, 1); r = rng.normal(0, 1) * (1 - a) * 9 + 1
            col = np.array([.5, .38, .26]) * rng.uniform(.75, 1.15) + np.array([.14, .12, .1]) * a
            stamp(px + side * a * a * ph * .35 + r, py + a * ph, rng.uniform(1.2, 2.4), col)
    edge = rgba[..., 3] < .5; rgba[edge, :3] = (.4, .44, .24)
    return save(rgba, TEX / f'{name}_Albedo.png')

def reed_cards(name, cards, width, height):
    """Upright cards crossed through the centre, with a slight outward lean so the clump has body from above."""
    bm = bmesh.new(); uv = bm.loops.layers.uv.new()
    for i in range(cards):
        a = math.pi * i / cards + .2; d = Vector((math.cos(a), math.sin(a), 0)); n = Vector((-d.y, d.x, 0))
        off = n * (.07 * (1 if i % 2 else -1)); lean = n * (.16 * (1 if i % 2 else -1))
        pts = [(-d * width * .5 + off, (0, 0)), (d * width * .5 + off, (1, 0)), (d * width * .5 + off + lean + Vector((0, 0, height * .5)), (1, .5)),
               (-d * width * .5 + off + lean + Vector((0, 0, height * .5)), (0, .5))]
        top = [(-d * width * .5 + off + lean * 1.6 + Vector((0, 0, height)), (0, 1)), (d * width * .5 + off + lean * 1.6 + Vector((0, 0, height)), (1, 1))]
        v = [bm.verts.new(p) for p, _ in pts] + [bm.verts.new(p) for p, _ in top]
        f1 = bm.faces.new((v[0], v[1], v[2], v[3])); f2 = bm.faces.new((v[3], v[2], v[5], v[4]))
        for loop, st in zip(f1.loops, [(0, 0), (1, 0), (1, .5), (0, .5)]): loop[uv].uv = st
        for loop, st in zip(f2.loops, [(0, .5), (1, .5), (1, 1), (0, 1)]): loop[uv].uv = st
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob

def build_co04():
    """A light reed clump for water edges (A5 ferry, A3 creek): crossed alpha cards, cheap enough to plant by the hundred."""
    ID = 'CO04_ReedClump'
    reset()
    img = reed_texture(ID)
    mat = game_material(ID, img, alpha=True)
    lod0 = reed_cards(ID + '_LOD0', 4, 1.15, 2.3); lod1 = reed_cards(ID + '_LOD1', 3, 1.15, 2.3); lod2 = reed_cards(ID + '_LOD2', 2, 1.15, 2.3)
    for o in (lod0, lod1, lod2): o.data.materials.append(mat)
    info = {
        'asset': ID, 'version': 'v001', 'name_zh': '低面數蘆葦叢', 'slot': 'A5_FerryReeds, A3_CreekReeds', 'minTier': 'low',
        'note': '交叉面片加透明貼圖；可以大量種在水邊。沒有碰撞。QX_WaterReeds 面數太高，大片種植時用這件。',
        'units': 'meters', 'origin': 'ground centre', 'dimensions_m': [round(v, 3) for v in lod0.dimensions],
        'lods': {'LOD0': tri_count(lod0), 'LOD1': tri_count(lod1), 'LOD2': tri_count(lod2)},
        'materials': 1, 'textures_px': {f'{ID}_Albedo.png': [512, 1024]}, 'collision': 'none',
        'status': {'Exported': True, 'Imported': False, 'VisuallyVerified': False, 'InGameVerified': False},
    }
    finish(ID, [lod0, lod1, lod2], info, [lod0], target=(.4, 0, 1.0), dist=.9)

# ---------------------------------------------------------------- CO05
def build_co05():
    """One 4 m section of a cliffside plank walk (D8 東山徑): beams socketed into pale granite, braces, a plank deck, a rope rail.
    Origin: on the deck surface at the cliff face, centre of the section. The deck runs along X; the drop is on -Y."""
    ID = 'CO05_CliffPlankWalk'
    reset(); rng = np.random.default_rng(20261114); parts = []
    cliff = stone_block('cliff', (4.3, .8, 4.6), 42, 46, rng, .07)
    cp = coords(cliff); cp[:, 1] += .1 * (fbm(cp * np.array([.9, 1, .9]) + 4) - .5) * 2 + .05 * (fbm(cp * 3 + 9) - .5); set_coords(cliff, cp)
    place(cliff, (0, .42, -2.2)); parts.append((cliff, 'granite', -.12))
    for i, x in enumerate((-1.55, -.52, .52, 1.55)):
        beam = place(stone_block(f'beam{i}', (.2, 2.05, .2), 120, 8, rng, .012), (x, -.72, -.3)); parts.append((beam, 'timber', -.08))
        brace = stone_block(f'brace{i}', (.14, 1.75, .14), 120, 6, rng, .01)
        place(brace, (0, 0, -.07)); place(brace, (x, -.62, -.92), (-47, 0, 0)); parts.append((brace, 'timber', -.1))
        sock = place(stone_block(f'socket{i}', (.3, .1, .3), 110, 4, rng, .01), (x, .02, -.35)); parts.append((sock, 'granite', -.3))
    edge = place(stone_block('edge_beam', (4.1, .16, .16), 110, 10, rng, .012), (0, -1.62, -.2)); parts.append((edge, 'timber', -.08))
    n = 9; w = 4.0 / n
    for i in range(n):
        L = 1.72 + rng.uniform(-.05, .08)
        plank = stone_block(f'plank{i}', (w - .025, L, .06), 130, 7, rng, .008)
        pp = coords(plank)
        if i == 5:   # the cracked one: split along its length, one half dropped a little
            half = pp[:, 0] > .02 * np.sin(pp[:, 1] * 9); pp[half, 2] -= .035; pp[half, 0] += .012
        pp[:, 2] += .012 * np.sin(pp[:, 1] * 2.2 + i)                                    # planks cup and warp
        set_coords(plank, pp)
        place(plank, (-2 + w * (i + .5), -.86 + rng.uniform(-.03, .03), -.06), (rng.uniform(-1.2, 1.2), 0, rng.uniform(-1.4, 1.4))); parts.append((plank, 'timber', -.06))
    posts = []
    for i, x in enumerate((-1.92, -.64, .64, 1.92)):
        post = place(stone_block(f'post{i}', (.11, .11, 1.12), 130, 6, rng, .008), (x, -1.62, -.12), (rng.uniform(-2, 2), rng.uniform(-3, 3), 0)); parts.append((post, 'timber', -.1))
        posts.append((x, -1.62, .9))
    for i, (a, b) in enumerate(zip(posts, posts[1:])):
        mid = ((a[0] + b[0]) / 2, a[1] - .02, a[2] - .17)
        rope = tube(f'rope{i}', [a, ((a[0] * 3 + b[0]) / 4, a[1] - .01, a[2] - .12), mid, ((a[0] + b[0] * 3) / 4, a[1] - .01, a[2] - .12), b], (.022,) * 5, segments=10, per_m=60)
        parts.append((rope, 'rope', -1))
    for o, kind, bias in parts: paint_piece(o, kind, bias, ground=False)
    sculpts = [o for o, _, _ in parts]; sculpt_tris = sum(tri_count(o) for o in sculpts)
    lod0, lod1, lod2 = bake_game_mesh(ID, sculpts, 9000, (4200, 1300), clip_ground=False)
    col_deck = dense_box(ID + '_Collision', (4.0, 1.75, .14), 0); col_deck.location = (0, -.86, -.14); col_deck.display_type = 'WIRE'
    col_rail = dense_box(ID + '_Rail_Collision', (4.0, .1, 1.1), 0); col_rail.location = (0, -1.62, 0); col_rail.display_type = 'WIRE'
    col_wall = dense_box(ID + '_Cliff_Collision', (4.3, .7, 4.6), 0); col_wall.location = (0, .42, -2.2); col_wall.display_type = 'WIRE'
    for o in sculpts: o.hide_render = True; o.hide_viewport = True
    info = {
        'asset': ID, 'version': 'v001', 'name_zh': '崖邊棧道（一段 4 m）', 'slot': 'D8_EastMountainPath_PlankWalk', 'minTier': 'low',
        'note': 'B 區灰白花崗石風格。可首尾相接成一條路；橋面在原點高度，寬 1.75 m，外側有繩欄。崖面是一塊 4.3 × 4.6 m 的石板，接真正的山壁時埋進去即可。',
        'units': 'meters', 'front': '-Y is the drop', 'origin': 'deck surface at the cliff face, section centre',
        'dimensions_m': [round(v, 3) for v in lod0.dimensions], 'sculpt_triangles': sculpt_tris,
        'lods': {'LOD0': tri_count(lod0), 'LOD1': tri_count(lod1), 'LOD2': tri_count(lod2)},
        'materials': 1, 'textures_px': {f'{ID}_Albedo.png': SIZE, f'{ID}_Normal.png': SIZE, f'{ID}_MaskURP.png': SIZE},
        'collision': 'three boxes: deck, rail, cliff', 'walkable': 'deck 4.0 x 1.75 m, clear width about 1.6 m',
        'status': {'Exported': True, 'Imported': False, 'VisuallyVerified': False, 'InGameVerified': False},
    }
    finish(ID, [lod0, lod1, lod2, col_deck, col_rail, col_wall], info, [lod0], target=(0, -.5, -.2), dist=1.55, floor_z=-2.25, fig_at=(.6, -.9, 0))

def fern_texture(name):
    """Two fern fronds and a few dead leaves on one 512 px alpha texture, drawn with numpy."""
    N = 512; yy, xx = np.mgrid[0:N, 0:N] / N
    rgba = np.zeros((N, N, 4), dtype=np.float32)
    def frond(cx, base, tip, width, tone):
        t = np.clip((yy - base) / (tip - base), 0, 1); inside = (yy >= base) & (yy <= tip)
        spine = cx + .05 * np.sin(t * 2.2) * (tip - base)
        half = width * np.sin(np.clip(t, .02, 1) ** .75 * math.pi) ** .8 * (1 - .25 * t)
        dx = np.abs(xx - spine)
        teeth = .5 + .5 * np.sin((t * 34 + dx * 26) * math.pi)
        shape = inside & (dx < half * (.55 + .45 * teeth))
        rachis = inside & (dx < .004 + .004 * (1 - t))
        g = np.stack([.16 + .18 * t + .1 * tone, .3 + .22 * t + .12 * tone, .09 + .05 * t], -1) * (1 - .35 * (dx / np.maximum(half, 1e-4))[..., None] ** 2)
        rgba[shape, :3] = g[shape]; rgba[shape, 3] = 1
        rgba[rachis, :3] = (.2, .26, .1); rgba[rachis, 3] = 1
    frond(.17, .03, .97, .15, .0); frond(.5, .03, .9, .13, .6)
    def leaf(cx, cy, rx, ry, ang, colour):
        c, s = math.cos(ang), math.sin(ang); u = (xx - cx) * c + (yy - cy) * s; v = -(xx - cx) * s + (yy - cy) * c
        m = (u / rx) ** 2 + (v / ry) ** 2 * (1 + .8 * np.clip(u / rx, -1, 1)) < 1          # pointed at one end
        rgba[m, :3] = np.array(colour) * (1 - .3 * np.clip(np.abs(v[m] / ry), 0, 1))[:, None]; rgba[m, 3] = 1
        vein = m & (np.abs(v) < .0035); rgba[vein, :3] = np.array(colour) * .6
    for i, (cx, cy) in enumerate([(.78, .14), (.86, .36), (.74, .58), (.88, .78), (.75, .9)]):
        leaf(cx, cy, .1, .045, .5 + i * 1.1, [(.42, .26, .12), (.5, .34, .14), (.34, .2, .1), (.46, .3, .1), (.38, .24, .13)][i])
    edge = rgba[..., 3] < .5
    rgba[edge, :3] = (.24, .32, .12)                      # colour under the cut edge, so mip levels do not go black
    return save(rgba[::-1], TEX / f'{name}_Albedo.png')

def fern_cards(name, spots):
    """spots: (x, y, z, yaw degrees, size m). Each spot gets three arching fronds and a dead leaf lying on the ground."""
    bm = bmesh.new(); uv = bm.loops.layers.uv.new()
    rng = np.random.default_rng(7)
    def quad(pts, u0, u1):
        vs = [bm.verts.new(p) for p in pts]; f = bm.faces.new(vs)
        for loop, st in zip(f.loops, [(u0, 0), (u1, 0), (u1, 1), (u0, 1)]): loop[uv].uv = st
    for (x, y, z, yaw, size) in spots:
        for k in range(3):
            ang = math.radians(yaw + (k - 1) * 48 + rng.uniform(-12, 12)); L = size * rng.uniform(.8, 1.1); w = L * .34
            d = Vector((math.cos(ang), math.sin(ang), 0)); side = Vector((-d.y, d.x, 0))
            u0, u1 = (0, .34) if k % 2 == 0 else (.34, .66)
            segs = 4; prev = None
            for s in range(segs + 1):
                t = s / segs; c = Vector((x, y, z)) + d * (L * t * .85) + Vector((0, 0, L * (.62 * math.sin(t * 2.0) - .12 * t * t)))
                row = (c - side * w * .5, c + side * w * .5)
                if prev:
                    vs = [bm.verts.new(p) for p in (prev[0], prev[1], row[1], row[0])]; f = bm.faces.new(vs)
                    t0 = (s - 1) / segs
                    for loop, st in zip(f.loops, [(u0, t0), (u1, t0), (u1, t), (u0, t)]): loop[uv].uv = st
                prev = row
        a = math.radians(yaw + 200); o = Vector((x + .16 * math.cos(a), y + .16 * math.sin(a), z + .012)); s2 = .11
        i = int(rng.integers(0, 5)); v0, v1 = [(.04, .24), (.26, .46), (.48, .68), (.68, .88), (.82, .98)][i]
        vs = [bm.verts.new(o + Vector(p)) for p in ((-s2, -s2, 0), (s2, -s2, 0), (s2, s2, 0), (-s2, s2, 0))]; f = bm.faces.new(vs)
        for loop, st in zip(f.loops, [(.66, v0), (1, v0), (1, v1), (.66, v1)]): loop[uv].uv = st
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob

def finish(ID, game, info, show, target=(.25, 0, 1.15), dist=1.0, floor_z=-.02, high=False, fig_at=None):
    bpy.ops.wm.save_as_mainfile(filepath=str(SRC / f'{ID}_v001.blend'))
    for o in bpy.context.scene.objects: o.select_set(False)
    for o in game: o.hide_viewport = False; o.select_set(True)
    out = EXP / ID; out.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(out / f'{ID}_v001.glb'), use_selection=True, export_apply=True, export_yup=True)
    bpy.ops.export_scene.fbx(filepath=str(out / f'{ID}_v001.fbx'), use_selection=True, apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
                             bake_space_transform=True, mesh_smooth_type='FACE', add_leaf_bones=False, path_mode='STRIP')
    (out / 'model_info.json').write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
    # previews: three-quarter, front, side, back, with a 1.75 m figure
    s = bpy.context.scene; s.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'CYCLES'
    for o in game: o.hide_render = o not in show
    fig = dense_box('figure_1.75m', (.42, .24, 1.75), 0); fig.location = fig_at if fig_at else (2.7 if high else 1.35, .2, 0)
    fm = bpy.data.materials.new('fig'); fm.diffuse_color = (.55, .6, .66, 1); fm.use_nodes = True
    next(n for n in fm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.55, .6, .66, 1); fig.data.materials.append(fm)
    floor = dense_box('floor', (14, 14, .02), 0); floor.location = (0, 0, floor_z)
    gm = bpy.data.materials.new('floor'); gm.use_nodes = True
    next(n for n in gm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.56, .53, .49, 1); floor.data.materials.append(gm)
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sun.data.energy = 3.2; sun.rotation_euler = (math.radians(52), 0, math.radians(-38)); s.collection.objects.link(sun)
    world = bpy.data.worlds.new('w'); world.use_nodes = True; world.node_tree.nodes['Background'].inputs[0].default_value = (.62, .66, .72, 1); world.node_tree.nodes['Background'].inputs[1].default_value = .75; s.world = world
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera = cam; cam.data.lens = 55
    s.render.resolution_x, s.render.resolution_y = 1100, 1100
    target = Vector(target)
    views = {k: tuple(target + (Vector(v) - Vector((.25, 0, 1.15))) * dist) for k, v in
             {'threequarter': (3.4, -4.6, 1.9), 'front': (0, -6.2, 1.25), 'side': (6.2, 0, 1.25), 'back': (0, 6.2, 1.25)}.items()}
    if high: views = {'threequarter': tuple(target + Vector((3.6, -4.4, 4.4)) * dist), 'top': tuple(target + Vector((0, -.01, 7.5)) * dist), 'front': tuple(target + Vector((0, -6.2, 2.2)) * dist), 'side': tuple(target + Vector((6.2, 0, 2.2)) * dist)}
    for name, eye in views.items():
        cam.location = eye; cam.rotation_euler = (target - Vector(eye)).to_track_quat('-Z', 'Y').to_euler()
        s.render.filepath = str(PRE / f'{ID}_{name}.png'); bpy.ops.render.render(write_still=True)
    print('BUILT', ID, json.dumps(info['lods']), info['dimensions_m'])

if 'CO02' in args: build_co02()
if 'CO03' in args: build_co03()
if 'CO01' in args: build_co01()
if 'CO04' in args: build_co04()
if 'CO05' in args: build_co05()
