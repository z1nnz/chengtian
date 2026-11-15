"""Tree generator prototype (camphor-like broadleaf), following the life tree of elder-tree-esg (build_life_tree.py):
individual cupped leaves (not cards), small leaves set along thin twigs in sprays, four branch orders ending in fine twigs,
colour by height and depth in the crown, a fluted trunk with a root flare.

  blender -b --factory-startup -P tree_gen.py -- <out_dir> [seed]
"""
import bpy, bmesh, sys, math, random
from mathutils import Vector, Matrix, Quaternion, noise

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = argv[0] if argv else '.'
SEED = int(argv[1]) if len(argv) > 1 else 7
R = random.Random(SEED)
UP = Vector((0, 0, 1))

HEIGHT = 12.0
TRUNK_R = .62
RINGS = {0: 18, 1: 10, 2: 7, 3: 5, 4: 3}
LEAF_LEN = (.07, .11)        # half length of a leaf, m
PALETTE = ((.03, .10, .05), (.06, .19, .075), (.13, .30, .09), (.25, .42, .12), (.42, .54, .2))

branches = []      # (level, [points], [radii])
leaves_at = []     # (point, twig direction, level)


def perp(v):
    a = v.cross(UP)
    return a.normalized() if a.length > 1e-4 else Vector((1, 0, 0))


def rotated(v, axis, ang):
    return Quaternion(axis, ang) @ v


def grow(start, direction, length, radius, level, seed):
    """One branch: a wandering path that bends by its order's tropism; children leave it at golden-angle azimuths."""
    rr = random.Random(seed)
    n = {0: 12, 1: 12, 2: 9, 3: 7, 4: 5}[level]
    seg = length / n
    pts, rad = [start.copy()], [radius]
    d = direction.normalized(); p = start.copy()
    off = Vector((rr.uniform(-99, 99), rr.uniform(-99, 99), rr.uniform(-99, 99)))
    for i in range(1, n + 1):
        t = i / n
        wander = noise.noise_vector(off + p * (.35 if level < 2 else .9)) * (.16 if level == 0 else .3 if level == 1 else .38)
        if level == 0: trop = UP * .22
        elif level == 1: trop = UP * (.20 - .36 * t)            # limbs rise, then level out and reach
        elif level == 2: trop = UP * (.10 - .2 * t)
        else: trop = UP * (-.05 - .22 * t)                      # twigs droop a little at the tip
        d = (d + wander + trop).normalized()
        p = p + d * seg
        pts.append(p.copy())
        taper = (1 - t) ** (.75 if level == 0 else 1.05)
        rad.append(max(.006, radius * (.16 + .84 * taper)) if level < 4 else max(.004, radius * (1 - .8 * t)))
    branches.append((level, pts, rad))
    if level >= 3:
        first = 1 if level == 4 else n // 3
        for i in range(first, n + 1):
            a, b = pts[i - 1], pts[i]
            leaves_at.append((a, b, level))
    if level == 4: return
    kids = {0: 10, 1: 6, 2: 5, 3: 5}[level]
    t0 = {0: .5, 1: .3, 2: .22, 3: .15}[level]
    az = rr.uniform(0, math.tau)
    for k in range(kids):
        t = t0 + (1 - t0) * (k + rr.uniform(.2, .8)) / kids
        if level == 0 and k == kids - 1: t = 1.
        i = min(n - 1, int(t * n)); f = t * n - i
        o = pts[i].lerp(pts[i + 1], min(1., f)); tan = (pts[i + 1] - pts[i]).normalized()
        az += 2.39996 + rr.uniform(-.35, .35)
        spread = math.radians({0: rr.uniform(52, 78), 1: rr.uniform(36, 62), 2: rr.uniform(32, 60), 3: rr.uniform(30, 62)}[level])
        if level == 0: spread *= (.55 + .45 * (1 - (t - t0) / (1 - t0)))   # top limbs are steeper, low limbs reach wide
        side = rotated(perp(tan), tan, az)
        cd = rotated(tan, side, spread)
        if level >= 1 and cd.z < -.15: cd.z = -.15; cd.normalize()         # no branch starts off pointing at the ground
        r_here = rad[i] + (rad[i + 1] - rad[i]) * min(1., f)
        cr = r_here * {0: rr.uniform(.42, .58), 1: rr.uniform(.48, .62), 2: rr.uniform(.5, .62), 3: rr.uniform(.5, .6)}[level]
        cl = length * {0: rr.uniform(1.15, 1.4), 1: rr.uniform(.42, .56), 2: rr.uniform(.46, .6), 3: rr.uniform(.5, .66)}[level] * (1.12 - .34 * t)
        grow(o, cd, cl, cr, level + 1, seed * 31 + k + 1)


def tube_mesh():
    """All branches as one mesh; ring size by order; the trunk is fluted and flares into the roots."""
    V, F, lev = [], [], []
    for level, pts, rad in branches:
        m = RINGS[level]; n = len(pts)
        t = (pts[1] - pts[0]).normalized(); N = perp(t)
        base = len(V)
        for i in range(n):
            if i:
                t2 = (pts[min(n - 1, i + 1)] - pts[i - 1]).normalized()
                ax = t.cross(t2)
                if ax.length > 1e-6: N = rotated(N, ax.normalized(), t.angle(t2))
                t = t2
            B = t.cross(N).normalized()
            for k in range(m):
                th = math.tau * k / m
                r = rad[i]
                if level == 0:
                    z = pts[i].z
                    amp = .09 + .13 * max(0., 1 - z / 2.2)
                    r *= 1 + amp * math.sin(th * 5 + z * 1.15) + .035 * math.sin(th * 9 - z * .72)
                    r *= 1 + .9 * math.exp(-z / .55)
                elif level == 1:
                    r *= 1 + .07 * math.sin(th * 4 + i * .9)
                V.append(pts[i] + (N * math.cos(th) + B * math.sin(th)) * r); lev.append(level)
        for i in range(n - 1):
            for k in range(m):
                a = base + i * m + k; b = base + i * m + (k + 1) % m
                F.append((a, b, b + m, a + m))
        V.append(pts[-1] + t * rad[-1] * .5); lev.append(level); c = len(V) - 1
        for k in range(m): F.append((base + (n - 1) * m + k, base + (n - 1) * m + (k + 1) % m, c))
    me = bpy.data.meshes.new('Tree_Wood'); me.from_pydata([tuple(v) for v in V], [], F)
    for p in me.polygons: p.use_smooth = True
    me.update()
    return me


def roots():
    for k in range(7):
        a = math.tau * k / 7 + R.uniform(-.3, .3)
        d = Vector((math.cos(a), math.sin(a), 0))
        L = R.uniform(2.2, 3.6); r0 = TRUNK_R * R.uniform(.42, .6)
        pts, rad = [], []
        for i in range(9):
            t = i / 8
            p = d * (TRUNK_R * .5 + L * t) + Vector((0, 0, .75 * (1 - t) ** 2.2 - .18 * t)) + perp(d) * math.sin(t * 3.4 + k) * .28 * t
            pts.append(p); rad.append(max(.03, r0 * (1 - t) ** .9))
        branches.append((1, pts, rad))


def leaf_mesh():
    """Each leaf its own cupped blade (5 vertices: four on the outline, the midrib raised), set alternately along the twigs,
    its stalk turned out from the twig, its face up and outward, the tip dropped a little."""
    lo = min(a.z for a, b, l in leaves_at); hi = max(a.z for a, b, l in leaves_at)
    cx = sum(a.x for a, b, l in leaves_at) / len(leaves_at); cy = sum(a.y for a, b, l in leaves_at) / len(leaves_at)
    cen = Vector((cx, cy, lo + (hi - lo) * .42))
    rmax = max((a - cen).length for a, b, l in leaves_at)
    V, F, C = [], [], []
    for si, (a, b, level) in enumerate(leaves_at):
        axis = (b - a); L = axis.length; axis.normalize()
        per = int(max(3, round(L / (.02 if level == 4 else .045))))
        side = perp(axis)
        for j in range(per):
            t = (j + R.random()) / per
            o = a.lerp(b, t)
            ang = j * 2.39996 + si * .7 + R.uniform(-.4, .4)
            out = rotated(side, axis, ang)
            out = (out + axis * R.uniform(.25, .7) + UP * R.uniform(-.05, .3)).normalized()      # leaves lean towards the twig tip
            half = R.uniform(*LEAF_LEN); w = half * R.uniform(.42, .56)
            centre = o + out * (half + R.uniform(.01, .04))
            radial = (centre - cen); radial.normalize()
            nrm = (UP * R.uniform(.5, 1.) + radial * R.uniform(.25, .7) + Vector((R.uniform(-.35, .35), R.uniform(-.35, .35), 0))).normalized()
            y = out - nrm * out.dot(nrm)
            y = y.normalized() if y.length > 1e-4 else perp(nrm)
            x = y.cross(nrm).normalized()
            droop = R.uniform(.1, .35) * half
            base = len(V)
            for px, py, pz in ((0, -half, 0), (w, -half * .08, -half * .07), (0, half, -droop), (-w, -half * .08, -half * .07), (0, half * .05, half * .1)):
                V.append(centre + x * px + y * py + nrm * pz)
            for s in range(4): F.append((base + 4, base + s, base + (s + 1) % 4))
            # colour: brighter and yellower high up and at the outside of the crown, deep green low and inside
            h = (centre.z - lo) / (hi - lo); depth = min(1., (centre - cen).length / rmax)
            sun = max(0., nrm.dot(Vector((.35, -.45, .82)).normalized()))
            tone = max(0., min(3.999, (h * .55 + depth * .3 + sun * .25 + R.uniform(-.08, .08)) * 4.2 - .2))
            i0 = int(tone); m = tone - i0
            col = [PALETTE[i0][c] * (1 - m) + PALETTE[i0 + 1][c] * m for c in range(3)]
            occ = .5 + .5 * max(h * .5 + depth * .5, depth)
            C.extend([(col[0] * occ, col[1] * occ, col[2] * occ, 1.)] * 5)
    me = bpy.data.meshes.new('Tree_Leaves'); me.from_pydata([tuple(v) for v in V], [], F)
    for p in me.polygons: p.use_smooth = True
    me.update()
    att = me.color_attributes.new(name='LeafColour', type='FLOAT_COLOR', domain='POINT')
    att.data.foreach_set('color', [c for col in C for c in col])
    return me, len(V) // 5


def bark_material():
    m = bpy.data.materials.new('Bark'); m.use_nodes = True
    nt = m.node_tree; b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1., 1., .22)
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 9.; nz.inputs['Detail'].default_value = 8.; nz.inputs['Roughness'].default_value = .62
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = .33; ramp.color_ramp.elements[0].color = (.028, .017, .010, 1)
    ramp.color_ramp.elements[1].position = .72; ramp.color_ramp.elements[1].color = (.17, .105, .058, 1)
    nt.links.new(nz.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = .9; bump.inputs['Distance'].default_value = .06
    nt.links.new(nz.outputs['Fac'], bump.inputs['Height']); nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    b.inputs['Roughness'].default_value = .88
    return m


def leaf_material():
    m = bpy.data.materials.new('Leaf'); m.use_nodes = True
    nt = m.node_tree; b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'LeafColour'
    nt.links.new(vc.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = .55
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    tr = nt.nodes.new('ShaderNodeBsdfTranslucent'); mix = nt.nodes.new('ShaderNodeMixShader'); mix.inputs['Fac'].default_value = .28
    hue = nt.nodes.new('ShaderNodeHueSaturation'); hue.inputs['Saturation'].default_value = 1.15; hue.inputs['Value'].default_value = 1.6
    nt.links.new(vc.outputs['Color'], hue.inputs['Color']); nt.links.new(hue.outputs['Color'], tr.inputs['Color'])
    nt.links.new(b.outputs['BSDF'], mix.inputs[1]); nt.links.new(tr.outputs['BSDF'], mix.inputs[2]); nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return m


def scene_and_render(objs, tris, nleaf):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.samples = 40; sc.cycles.use_denoising = True
    try: sc.cycles.device = 'GPU'
    except Exception: pass
    sc.render.resolution_x = 1100; sc.render.resolution_y = 1100
    sc.view_settings.view_transform = 'Filmic' if 'Filmic' in [i.identifier for i in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else sc.view_settings.view_transform
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND'); bg.inputs['Color'].default_value = (.36, .55, .85, 1); bg.inputs['Strength'].default_value = 1.0
    sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN')); sun.data.energy = 4.2; sun.data.angle = math.radians(3)
    sun.rotation_euler = (math.radians(48), 0, math.radians(35)); sc.collection.objects.link(sun)
    bpy.ops.mesh.primitive_plane_add(size=120); g = bpy.context.object
    gm = bpy.data.materials.new('Ground'); gm.use_nodes = True
    next(n for n in gm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.12, .2, .07, 1); g.data.materials.append(gm)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); sc.collection.objects.link(cam); sc.camera = cam
    lo = Vector((min(v.co.x for o in objs for v in o.data.vertices), min(v.co.y for o in objs for v in o.data.vertices), 0))
    hi = Vector((max(v.co.x for o in objs for v in o.data.vertices), max(v.co.y for o in objs for v in o.data.vertices), max(v.co.z for o in objs for v in o.data.vertices)))
    c = (lo + hi) / 2; size = (hi - lo).length
    def shot(name, d, lens, dist, target=None):
        t = target or c
        cam.data.lens = lens; cam.location = t + Vector(d).normalized() * dist
        cam.rotation_euler = (t - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = f'{OUT}/{name}.png'; bpy.ops.render.render(write_still=True)
    shot('tree_full', (.25, -1, .22), 50, size * 1.35)
    shot('tree_crown', (.5, -1, .1), 85, size * .95, Vector((c.x + size * .16, c.y, hi.z * .68)))
    shot('tree_under', (.3, -1, -.28), 35, size * .5, Vector((c.x, c.y, hi.z * .55)))
    print('TREE_STATS', 'tris', tris, 'leaves', nleaf, 'branches', len(branches), 'size', [round(v, 2) for v in hi - lo], flush=True)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    grow(Vector((0, 0, 0)), Vector((.08, .03, 1)), HEIGHT * .42, TRUNK_R, 0, SEED)
    roots()
    wood = bpy.data.objects.new('Tree_Wood', tube_mesh()); wood.data.materials.append(bark_material())
    lm, nleaf = leaf_mesh()
    leaf = bpy.data.objects.new('Tree_Leaves', lm); leaf.data.materials.append(leaf_material())
    for o in (wood, leaf): bpy.context.scene.collection.objects.link(o)
    tris = sum(len(p.vertices) - 2 for o in (wood, leaf) for p in o.data.polygons)
    scene_and_render([wood, leaf], tris, nleaf)
    bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/tree.blend')


main()
