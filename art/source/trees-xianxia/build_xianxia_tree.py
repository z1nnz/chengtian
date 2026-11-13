"""XT01 xianxia great tree (仙俠風格大型綠樹) for 承天, with a gold-leaf version on the same mesh and textures.

  blender --background --factory-startup --python art/source/trees-xianxia/build_xianxia_tree.py

A big old broadleaf for sect courtyards, mountain woods and grassland: a short thick trunk on a wide root flare, a few heavy limbs
reaching out, and a wide, soft crown built from about forty leaf clusters of different sizes with sky between them (stylised
open-world look: between anime and natural, soft hand-painted feel). Original design; the reference shots only set the direction.

Method
- wood: the tr_broad engine of the TR series (trunk with root lobes, ridges and burls; seeded limbs; space colonisation towards the
  clusters; pipe-model radii; one fused Skin mesh, decimated to the LOD budget) plus surface roots running out over the ground.
- leaves: every cluster is an ellipsoid (lumpy, flattened underneath) covered with leaf-cluster cards from a grey hand-painted atlas.
  Card normals are bent to the cluster's own shape blended with the whole crown, so each cluster shades like one soft lobe while its
  rim stays toothy (the leaves in the texture). The vertex colour carries the wind and a light mask; the leaf shader turns the grey
  texture into colour with a deep / mid / tip ramp along that mask, so the green and the gold tree are two materials, nothing else.

Output (art/exports/trees-xianxia/XT01_XianxiaGreatTree/):
  XT01_XianxiaGreatTree_v001.fbx / .glb   root empty, children _LOD0.._LOD3 and _Collision
  Textures/XT01_Bark_{BaseColor,Normal,MetallicSmoothness}.png (1024), XT01_Leaves_BaseColor.png (2048, RGBA)
  model_info.json, validation.json; art/source/trees-xianxia/blend/XT01_XianxiaGreatTree_v001.blend
Vertex colour 'Wind' (linear float): R sway weight (trunk 0, limbs 0.02-0.25, twigs to 0.55, leaves 0.55-1), G phase,
B light mask 0..1 (leaves: deep inside / underneath -> sunlit tops and rim; wood: height), A cluster tint variation 0..1.
"""
import bpy, sys, json, math, time, hashlib
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'trees-b'))
import numpy as np
from mathutils import Vector, noise
import tr_tex as TX
import tr_tree as TT
import tr_skin as TS
from tr_broad import install
import xt_leaves as XL

AID = 'XT01_XianxiaGreatTree'; VER = 'v001'; SP = 'XT01'
ART = HERE.parents[1]
EXP = ART / 'exports' / 'trees-xianxia' / AID
TEX = EXP / 'Textures'
CAPS = {0: 25000, 1: 8000, 2: 2500, 3: 200}
LOD_SWITCH_M = [60, 110, 280, 1500]
HEIGHT_RANGE = (15., 18.5)

# leaf colour ramps (sRGB, as set on the Unity material; the project renders in gamma space, Blender previews convert)
LOOKS = {
    'green': dict(deep='#2C5A52', mid='#5B9A45', tip='#B8D86A', var_a='#B9A35A', var_b='#6F9E86', var_amount=.45, midpoint=.5),
    'gold':  dict(deep='#8A5222', mid='#D8952A', tip='#F2D35C', var_a='#C9B14E', var_b='#D9773A', var_amount=.45, midpoint=.5),
}
DETAIL = .8            # how far the painted leaf value pushes the light mask (leaf-by-leaf light inside a cluster)
GRAZE = (.24, .6)       # |card normal . view|: below the first value a card is clipped away, above the second it is whole
VALUE = .45              # how much of the painted value multiplies the colour (leaf rims, shadows between leaves)

# ------------------------------------------------------------------ tree shape (tr_broad species namespace)
NS = dict(
    PALETTE=[(0, 0, 0)] * 8, CELL_RECTS={}, CELL_ASPECT={}, CLUSTER_TONES=(1, 3, 4, 6),
    GROW=dict(step=.42, d_inf=3.6, d_kill=.85, trop=(0., 0., .1), iters=90, r_tip=.022, pipe=.42, top_r=.9, smooth=5,
              tip_back=1.0, squash=.78),
    SKIN_WOOD={0: ((0, 1, 2, 3), 3, 11500), 1: ((0, 1, 2), 1, 3000), 2: ((0, 1), 1, 820)},
    VARIANTS={'A': dict(
        H=16., seed=411, r0=1.15, twist=.035, zmin=6.6,
        trunk=[(0, 0, -.02, 1.), (0, 0, 0, .93), (.1, .04, .08, .74), (.3, .1, .17, .66), (.46, .12, .26, .62), (.52, .08, .33, .6)],
        burls=[(3.4, 3.4, .18), (5.1, 4.6, .15)],
        crown=(.3, .1, 10.6, 9.6, 9.0, 4.0, .2), clumps=(21, (2.6, 3.4), 130, .55),
        extra_clumps=[(-7.8, 2.6, 8.0, 2.8), (8.0, -2.2, 7.8, 2.9), (1.5, 7.9, 8.2, 2.7), (-2.4, -7.8, 8.0, 2.8)],
        scaffolds=[(1., 15, 26, 6.0), (1., 100, 32, 5.4), (1., 195, 22, 6.4), (1., 285, 28, 5.8), (1., 50, 62, 4.0)],
        stubs=[])},
)
install(NS)
VAR = NS['VARIANTS']['A']
ROOTS = [(15, .5, 3.0), (78, .3, 2.2), (140, .55, 3.3), (205, .35, 2.5), (262, .6, 3.4), (318, .3, 2.0)]      # (azimuth deg, buttress on the trunk x radius, surface root run m)


def _section(seed, burls):
    """Trunk cross-section: six uneven root buttresses that run out over the ground (the roots are part of the trunk surface, so
    the bark maps over them without seams), a wide flare, broad soft bark ridges turning slowly with height (stylised: calm, not
    deep cracks), and a couple of low burls."""
    from tr_cypress import _angdiff
    lobes = [(az, run) for az, run, _ in ROOTS]
    def fn(th, s, p):
        z = p.z + .3
        root = 0.
        for az, run in lobes:
            w = math.exp(-(_angdiff(th, math.radians(az) + .12 * math.sin(2.3 * z + az)) / .26) ** 2)      # roots wander a little as they rise
            root += run * w * math.exp(-z / (.8 + .25 * run))
        flare = .55 * math.exp(-z / 1.1)
        tw = th - 2 * math.pi * .035 * z
        rib = (.07 * math.cos(7 * tw + seed) + .04 * math.cos(12 * tw + 2.1 * seed + .6 * z)) * (.6 + .4 * math.exp(-z / 4))
        burl = 0.
        for (tb, zb, a) in burls:
            burl += a * math.exp(-(_angdiff(th, tb) / .4) ** 2 - ((z - zb) / .35) ** 2)
        return 1 + root + flare + rib + burl
    return fn


def skeleton():
    branches, puffs, H, P, R = NS['skeleton']('A')
    branches[0].section = _section(1.7, VAR['burls'])
    return branches, H, P, R


# ------------------------------------------------------------------ foliage
FOL = {0: dict(kind='S', size=(1.5, 2.0), cover=2.7, inner=.14),
       1: dict(kind='B', size=(2.3, 2.9), cover=1.9, inner=.08),
       2: dict(kind='B', size=(3.4, 4.2), cover=1.45, inner=0.)}
SQ = .8           # clusters are flatter than round


_CL = {}


def clusters():
    """The grown clusters, each broken into a main lobe and one or two smaller side lobes (up / out from the crown centre), so the
    crown reads as many soft lumps of different sizes, not a pile of balls. Cached: every LOD uses the same lobes."""
    if 'v' in _CL: return _CL['v']
    cs, rr = NS['_CLUMPS']['A']; cs = np.array(cs, float); rr = np.array(rr, float)
    rng = np.random.default_rng(23); cc = NS['_CROWN']['A'].c; out_c = []; out_r = []
    for c, r in zip(cs, rr):
        out_c.append(c); out_r.append(r * .82)
        o = c - np.array(cc); o[2] = 0; o /= np.linalg.norm(o) + 1e-6
        for j in range(int(rng.integers(1, 3))):
            a = rng.uniform(-1.6, 1.6); d = np.array([o[0] * math.cos(a) - o[1] * math.sin(a), o[0] * math.sin(a) + o[1] * math.cos(a), rng.uniform(.1, .7)])
            d /= np.linalg.norm(d); out_c.append(c + d * r * rng.uniform(.55, .75)); out_r.append(r * rng.uniform(.48, .64))
    _CL['v'] = (np.array(out_c), np.array(out_r)); return _CL['v']


def _ell(p, c, r):
    d = p - c; return np.array([d[0] / r, d[1] / r, d[2] / (r * SQ)])


def foliage(buf, lod, rng, room):
    """Cards on every cluster. Returns the number of cards."""
    cs, rr = clusters(); cr = NS['_CROWN']['A']; N = len(cs); cfg = FOL[lod]
    zlo = float((cs[:, 2] - rr * SQ).min()); zhi = float((cs[:, 2] + rr * SQ).max())
    tint = np.random.default_rng(91).random(N); phase = np.random.default_rng(92).random(N)
    cand = []
    for k in range(N):
        c = cs[k]; r = rr[k]; scale = (r / 2.4) ** .45
        s_mean = np.mean(cfg['size']) * scale
        area = 4 * math.pi * r * r * (1 + 2 * SQ) / 3
        n = int(area * cfg['cover'] / (s_mean * s_mean * .8))
        ga = math.pi * (3 - math.sqrt(5))
        for i in range(n):
            zf = 1 - 2 * (i + .5) / n; rad = math.sqrt(max(0., 1 - zf * zf)); th = ga * i + k
            u = np.array([math.cos(th) * rad, math.sin(th) * rad, zf]) + rng.normal(0, .12, 3); u /= np.linalg.norm(u)
            lump = 1 + .26 * noise.noise(Vector(u * 1.3 + k * 3.3)) + .12 * noise.noise(Vector(u * 3.1 + k * 1.1))
            inner = rng.random() < cfg['inner']
            spike = (not inner) and rng.random() < .22        # leaves poking out of the lobe: a toothy, uneven rim
            dep = rng.uniform(.45, .72) if inner else (rng.uniform(.98, 1.08) if spike else rng.uniform(.84, 1.))
            p = c + u * np.array([r, r, r * SQ]) * lump * dep
            if p[2] < VAR['zmin'] - .4: continue
            # buried inside a neighbour: mostly dropped (never seen), a few kept so no cluster shows sky through a seam
            e = np.sqrt((((p - cs) / np.stack([rr, rr, rr * SQ], 1)) ** 2).sum(1)); e[k] = 9
            if e.min() < .74 and rng.random() < .85: continue
            # deep inside the crown and facing its middle: nobody sees it
            q = Vector(p); cn = cr.normal(q)
            if cr.val(q) < .55 and Vector(u).dot(cn) < -.25 and rng.random() < .8: continue
            size = rng.uniform(*cfg['size']) * scale * (.85 if inner else 1.)
            cand.append((k, p, u, size, inner))
    if len(cand) > room:          # over budget: thin the inner cards first, then at random
        rng.shuffle(cand); cand.sort(key=lambda x: x[4]); cand = cand[:room]
    cells = [XL.cell_rect(cfg['kind'], i) for i in range(8 if cfg['kind'] == 'S' else 4)]
    for (k, p, u, size, inner) in cand:
        c = cs[k]; r = rr[k]
        n = Vector(u * .9 + rng.normal(0, .18, 3) + np.array([0, 0, .1])).normalized()
        if n.dot(Vector(u)) < .7: n = (n + Vector(u)).normalized()
        up = Vector(u * .8 + np.array([0, 0, .7]) + rng.normal(0, .35, 3))
        rect = cells[int(rng.integers(len(cells)))]
        _card(buf, Vector(p), n, up, size, rect, k, c, r, cr, zlo, zhi, tint[k], phase[k], inner, rng)
    return len(cand)


def _card(buf, c, n, up, size, rect, k, cc, r, cr, zlo, zhi, tint, phase, inner, rng):
    up = up - n * up.dot(n)
    if up.length < 1e-4: up = n.orthogonal()
    up.normalize(); side = up.cross(n).normalized(); hs = size * .5
    u0, v0, u1, v1 = rect; base = len(buf.v)
    jit = rng.normal(0, .04)
    for (x, y, uv) in ((-1, -1, (u0, v0)), (1, -1, (u1, v0)), (1, 1, (u1, v1)), (-1, 1, (u0, v1))):
        p = c + side * (x * hs) + up * (y * hs)
        pa = np.array(p); e = _ell(pa, cc, r); el = np.linalg.norm(e)
        nc = Vector((e[0] / r, e[1] / r, e[2] / (r * SQ))).normalized() if el > 1e-4 else Vector((0, 0, 1))
        sn = (nc * .74 + cr.normal(p) * .2 + Vector((0, 0, .1))).normalized()
        top = .5 + .5 * nc.z; hc = min(1., max(0., (p.z - zlo) / (zhi - zlo))); rim = min(1., cr.val(p))
        m = .5 * top + .2 * hc + .14 * rim ** 1.5 + .2 * min(1., el) - .08 + jit - (.1 if inner else 0.)
        reach = min(1., math.hypot(p.x, p.y) / 10.)
        w = .55 + .45 * reach
        buf.v.append(p); buf.nrm.append(sn); buf.col.append((w, (phase + .03 * rng.random()) % 1., min(1., max(0., m)), tint))
    buf.f.append((base, base + 1, base + 2, base + 3)); buf.fmat.append(1)
    buf.fuv.append(((u0, v0), (u1, v0), (u1, v1), (u0, v1)))


# ------------------------------------------------------------------ materials (Blender preview; Unity builds its own)
def _lin(h): return tuple(TX.to_lin(TX.hexc(h))) + (1.,)


def S(node, name, out=False):
    """Socket by name among the enabled ones (Mix nodes carry one A / B / Result per data type)."""
    return [x for x in (node.outputs if out else node.inputs) if x.name == name and x.enabled][0]


def material_bark(tex):
    m = bpy.data.materials.new(f'M_{SP}_Bark'); m.use_nodes = True; nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    ic = nt.nodes.new('ShaderNodeTexImage'); ic.image = bpy.data.images.load(str(tex['BaseColor']), check_existing=True)
    inn = nt.nodes.new('ShaderNodeTexImage'); inn.image = bpy.data.images.load(str(tex['Normal']), check_existing=True); inn.image.colorspace_settings.name = 'Non-Color'
    nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(inn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs[0], bs.inputs['Normal'])
    nt.links.new(ic.outputs['Color'], bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = .85; bs.inputs['Specular IOR Level'].default_value = .25
    return m


def material_leaves(atlas, look):
    """Preview of the Unity leaf shader: m = mask + (painted value - mid) * DETAIL -> deep/mid/tip ramp, tint variation, x value."""
    L = LOOKS[look]; m = bpy.data.materials.new(f'M_{SP}_Leaves_{look.capitalize()}'); m.use_nodes = True; nt = m.node_tree
    N = nt.nodes; Lk = nt.links.new; bs = N['Principled BSDF']; out = N['Material Output']
    im = N.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(str(atlas), check_existing=True)
    vc = N.new('ShaderNodeVertexColor'); vc.layer_name = 'Wind'
    sep = N.new('ShaderNodeSeparateColor'); Lk(vc.outputs['Color'], sep.inputs[0])
    g = N.new('ShaderNodeMath'); g.operation = 'POWER'; g.inputs[1].default_value = 1 / 2.2; Lk(im.outputs['Color'], g.inputs[0])      # grey value back to sRGB
    d = N.new('ShaderNodeMath'); d.operation = 'SUBTRACT'; d.inputs[1].default_value = MEAN[0]; Lk(g.outputs[0], d.inputs[0])
    d2 = N.new('ShaderNodeMath'); d2.operation = 'MULTIPLY_ADD'; d2.inputs[1].default_value = DETAIL; Lk(d.outputs[0], d2.inputs[0]); Lk(sep.outputs['Blue'], d2.inputs[2])
    d2.use_clamp = True
    rp = N.new('ShaderNodeValToRGB'); e = rp.color_ramp.elements
    e[0].position = 0.; e[0].color = TX.hexc(L['deep']).tolist() + [1.]; e[1].position = 1.; e[1].color = TX.hexc(L['tip']).tolist() + [1.]
    em = e.new(L['midpoint']); em.color = TX.hexc(L['mid']).tolist() + [1.]
    Lk(d2.outputs[0], rp.inputs[0])
    # variation: A < 0.5 -> var_a, A > 0.5 -> var_b, strength |2A - 1| * amount; tint colour x2 multiplies (0.5 grey = no change)
    ta = N.new('ShaderNodeMix'); ta.data_type = 'RGBA'; S(ta, 'A').default_value = TX.hexc(L['var_a']).tolist() + [1.]; S(ta, 'B').default_value = TX.hexc(L['var_b']).tolist() + [1.]
    st = N.new('ShaderNodeMath'); st.operation = 'GREATER_THAN'; st.inputs[1].default_value = .5; Lk(vc.outputs['Alpha'], st.inputs[0]); Lk(st.outputs[0], S(ta, 'Factor'))
    a2 = N.new('ShaderNodeMath'); a2.operation = 'MULTIPLY_ADD'; a2.inputs[1].default_value = 2.; a2.inputs[2].default_value = -1.; Lk(vc.outputs['Alpha'], a2.inputs[0])
    ab = N.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; Lk(a2.outputs[0], ab.inputs[0])
    am = N.new('ShaderNodeMath'); am.operation = 'MULTIPLY'; am.inputs[1].default_value = L['var_amount']; Lk(ab.outputs[0], am.inputs[0])
    tw = N.new('ShaderNodeMix'); tw.data_type = 'RGBA'; tw.blend_type = 'MULTIPLY'; Lk(rp.outputs['Color'], S(tw, 'A')); Lk(S(ta, 'Result', True), S(tw, 'B')); S(tw, 'Factor').default_value = 1.
    t2 = N.new('ShaderNodeMix'); t2.data_type = 'RGBA'; t2.blend_type = 'MULTIPLY'; Lk(S(tw, 'Result', True), S(t2, 'A')); S(t2, 'B').default_value = (2., 2., 2., 1.); S(t2, 'Factor').default_value = 1.
    vm = N.new('ShaderNodeMix'); vm.data_type = 'RGBA'; Lk(am.outputs[0], S(vm, 'Factor')); Lk(rp.outputs['Color'], S(vm, 'A')); Lk(S(t2, 'Result', True), S(vm, 'B'))
    # value: colour x lerp(1, value / mid, VALUE)
    vv = N.new('ShaderNodeMath'); vv.operation = 'DIVIDE'; vv.inputs[1].default_value = MEAN[0]; Lk(g.outputs[0], vv.inputs[0])
    vl = N.new('ShaderNodeMix'); vl.data_type = 'FLOAT'; S(vl, 'Factor').default_value = VALUE; S(vl, 'A').default_value = 1.; Lk(vv.outputs[0], S(vl, 'B'))
    mul = N.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; S(mul, 'Factor').default_value = 1.; Lk(S(vm, 'Result', True), S(mul, 'A'))
    cv = N.new('ShaderNodeCombineColor'); [Lk(S(vl, 'Result', True), cv.inputs[i]) for i in range(3)]; Lk(cv.outputs[0], S(mul, 'B'))
    lin = N.new('ShaderNodeGamma'); lin.inputs[1].default_value = 2.2; Lk(S(mul, 'Result', True), lin.inputs[0])
    _leafy_out(nt, lin.outputs[0], im.outputs['Alpha'], bs, out)
    return m


def material_impostor(atlas, look):
    m = bpy.data.materials.new(f'M_{SP}_Impostor_{look.capitalize()}'); m.use_nodes = True; nt = m.node_tree
    im = nt.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(str(atlas), check_existing=True)
    mp = nt.nodes.new('ShaderNodeMapping'); tc = nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(tc.outputs['UV'], mp.inputs['Vector'])
    mp.inputs['Location'].default_value = (.5 if look == 'gold' else 0., 0, 0); nt.links.new(mp.outputs[0], im.inputs['Vector'])
    _leafy_out(nt, im.outputs['Color'], im.outputs['Alpha'], nt.nodes['Principled BSDF'], nt.nodes['Material Output'])
    # the impostor is a picture of the lit crown: both faces of both crossed quads shaded alike (normal up, no back-face
    # translucency), or the quad turned from the sun reads as a dark half
    for l in [l for l in nt.links if l.from_node.bl_idname == 'ShaderNodeNewGeometry' and l.from_socket.name == 'Backfacing']: nt.links.remove(l)
    up = nt.nodes.new('ShaderNodeCombineXYZ'); up.inputs['Z'].default_value = 1.; nt.links.new(up.outputs[0], nt.nodes['Principled BSDF'].inputs['Normal'])
    for n in nt.nodes:
        if n.bl_idname == 'ShaderNodeMixShader' and not n.inputs[0].is_linked: n.inputs[0].default_value = 0.
    return m


def _leafy_out(nt, col, alpha, bs, out):
    N = nt.nodes; Lk = nt.links.new
    Lk(col, bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = .9; bs.inputs['Specular IOR Level'].default_value = .15
    geo = N.new('ShaderNodeNewGeometry'); tr = N.new('ShaderNodeBsdfTranslucent'); Lk(col, tr.inputs['Color'])
    mx = N.new('ShaderNodeMixShader'); Lk(geo.outputs['Backfacing'], mx.inputs[0]); Lk(bs.outputs[0], mx.inputs[1]); Lk(tr.outputs[0], mx.inputs[2])
    tm = N.new('ShaderNodeMixShader'); trn = N.new('ShaderNodeBsdfTransparent'); Lk(trn.outputs[0], tm.inputs[1]); Lk(mx.outputs[0], tm.inputs[2])
    # cards seen edge-on thin out (the Unity shader does the same): no smeared slivers on the crown rim
    dt = N.new('ShaderNodeVectorMath'); dt.operation = 'DOT_PRODUCT'; Lk(geo.outputs['True Normal'], dt.inputs[0]); Lk(geo.outputs['Incoming'], dt.inputs[1])
    ab = N.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; Lk(dt.outputs['Value'], ab.inputs[0])
    gz = N.new('ShaderNodeMapRange'); gz.inputs['From Min'].default_value = GRAZE[0]; gz.inputs['From Max'].default_value = GRAZE[1]
    gz.inputs['To Min'].default_value = .97; gz.inputs['To Max'].default_value = .5; Lk(ab.outputs[0], gz.inputs['Value'])
    gt = N.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; Lk(alpha, gt.inputs[0]); Lk(gz.outputs['Result'], gt.inputs[1]); Lk(gt.outputs[0], tm.inputs[0])
    Lk(tm.outputs[0], out.inputs['Surface'])
    m = next(mm for mm in bpy.data.materials if mm.node_tree == nt); m.use_backface_culling = False
    try: m.surface_render_method = 'DITHERED'
    except Exception: pass


MEAN = [.65]


# ------------------------------------------------------------------ build
def _roots(buf, P, R, sides, step):
    rng = np.random.default_rng(17)
    for az, _, run in ROOTS:
        a = math.radians(az + 9); d = Vector((math.cos(a), math.sin(a), 0)); sd = Vector((-d.y, d.x, 0)); b = P(.02); r0 = R(.05)
        pts = []; rads = []
        for k in range(9):
            s = k / 8; x = r0 * .55 + (run + r0 * .5) * s
            z = 1.15 * (1 - s) ** 1.9 + .1 * math.sin(math.pi * s) - .38 * s ** 4
            pts.append(Vector((b.x, b.y, 0)) + d * x + sd * (.22 * math.sin(2.4 * s + az)) + Vector((0, 0, z)))
            rads.append(r0 * .42 * (1 - .8 * s) + .03)
        buf.tube(TT.Branch(pts, rads, 1, 0., 0., 0., 'limb'), sides, step, seed=az)


def build_lod(lod, mats, branches, H, P, R):
    buf = TT.Buf(H)
    levels, subdiv, target = NS['SKIN_WOOD'][lod]
    wood, b0, b1 = TS.skin_wood(buf, branches, levels, subdiv, target, trunk_below=H * VAR['trunk'][-1][2] - .25, seal=True, face_uv=True)
    for i in range(len(buf.col)):          # wood: B = height (unused by the bark shader), A = 0
        w, ph, z, a = buf.col[i]; buf.col[i] = (w, ph, z, 0.)
    zlow = min(v.z for v in buf.v)            # the Skin end cap rounds the buried base up: stretch the part below ground to reach -0.3
    if -.3 < zlow < -.02:
        for v in buf.v:
            if v.z < 0: v.z *= .3 / -zlow
    if lod < 2:      # surface roots: their own bark tubes, born inside the buttresses, arching over the ground and diving in
        n0 = len(buf.v); _roots(buf, P, R, 12 if lod == 0 else 7, .22 if lod == 0 else .45)
        for i in range(n0, len(buf.v)):
            buf.v[i].z = max(buf.v[i].z, -.3); w, ph, z, a = buf.col[i]; buf.col[i] = (0., ph, z, 0.)
    rng = np.random.default_rng(500 + lod)
    room = int((CAPS[lod] * .96 - buf.tris()) // 2)
    cards = foliage(buf, lod, rng, room)
    o = buf.build(f'{AID}_LOD{lod}', mats)
    tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
    return o, dict(tris=tris, wood=wood, cards=cards)


def impostor_render(objs, look, mats_by_look, tmp):
    """Front (looking +Y) orthographic render of LOD0 under a uniform white sky (albedo x occlusion), in the given look."""
    scene = bpy.context.scene
    o0 = objs[0]; keep = list(o0.data.materials)
    o0.data.materials[1] = mats_by_look[look]
    for o in scene.objects: o.hide_render = o not in objs
    ws = [o0.matrix_world @ Vector(c) for c in o0.bound_box]
    lo = Vector([min(v[i] for v in ws) for i in range(3)]); hi = Vector([max(v[i] for v in ws) for i in range(3)])
    half = max(abs(lo.x), abs(hi.x)) * 1.01; z0, z1 = -.3, hi.z + .05
    W = 1024; Hh = max(64, int(W * (z1 - z0) / (2 * half)))
    cam = bpy.data.objects.new('ImpCam', bpy.data.cameras.new('ImpCam')); scene.collection.objects.link(cam); scene.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = 2 * half; cam.data.clip_end = 300
    cam.location = (0, -80, (z0 + z1) / 2); cam.rotation_euler = (math.pi / 2, 0, 0)
    w = bpy.data.worlds.new('Imp'); w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (1, 1, 1, 1); bg.inputs[1].default_value = 1.
    kw = scene.world; scene.world = w
    scene.render.engine = 'CYCLES'; scene.cycles.samples = 48; scene.cycles.use_denoising = True
    scene.render.film_transparent = True; scene.render.resolution_x = W; scene.render.resolution_y = Hh; scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'Standard'
    fp = tmp / f'imp_{look}.png'; scene.render.filepath = str(fp); bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(str(fp)); c = np.array(im.pixels[:], np.float32).reshape(Hh, W, 4)[::-1].copy(); bpy.data.images.remove(im)
    c[..., :3] = np.clip(c[..., :3], 0, 1)          # the 8-bit PNG already holds sRGB values (Standard view): no second gamma
    c[..., 3] = (c[..., 3] > .5).astype(np.float32)
    scene.world = kw; bpy.data.objects.remove(cam)
    for o in scene.objects: o.hide_render = False
    for i, m in enumerate(keep): o0.data.materials[i] = m
    return c, (-half, half, z0, z1)


def save_atlas(atlas, path):
    rgb = XL.dilate_rgb(atlas[..., :3], atlas[..., 3])
    out = np.concatenate([rgb, atlas[..., 3:]], -1)
    o = bpy.data.images.new('atlas', XL.SIZE, XL.SIZE, alpha=True); o.alpha_mode = 'STRAIGHT'
    o.pixels = out[::-1].ravel(); o.filepath_raw = str(path); o.file_format = 'PNG'; o.save(); bpy.data.images.remove(o)


def export(root, kids, fbx):
    bpy.ops.object.select_all(action='DESELECT'); root.select_set(True)
    for o in kids: o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, object_types={'MESH', 'EMPTY'}, apply_unit_scale=True,
                             apply_scale_options='FBX_SCALE_ALL', bake_space_transform=True, axis_forward='-Z', axis_up='Y',
                             mesh_smooth_type='FACE', use_mesh_modifiers=True, add_leaf_bones=False, bake_anim=False,
                             path_mode='STRIP', embed_textures=False, colors_type='LINEAR', prioritize_active_color=True)
    bpy.ops.export_scene.gltf(filepath=str(fbx.with_suffix('.glb')), use_selection=True, export_format='GLB', export_yup=True,
                              export_apply=True, export_vertex_color='ACTIVE', export_attributes=False)


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    TEX.mkdir(parents=True, exist_ok=True)
    tmp = Path(bpy.app.tempdir or '.') / 'xt01'; tmp.mkdir(parents=True, exist_ok=True)
    bark = TX.painted_bark(TEX, SP, HERE.parent / 'trees-b' / 'bark_src' / 'elder_tree_bark_v1.png', sat=.62, gain=1.18,
                           tint=(1.0, .94, .88), contrast=1.0, crack=.25, normal=9., smooth_val=.08, blur_n=(1, 3))
    atlas, cells, mean = XL.paint_atlas(); MEAN[0] = mean
    atlas_path = TEX / f'{SP}_Leaves_BaseColor.png'; save_atlas(atlas, atlas_path)
    mats_leaf = {lk: material_leaves(atlas_path, lk) for lk in LOOKS}
    mats_imp = {lk: material_impostor(atlas_path, lk) for lk in LOOKS}
    mbark = material_bark(bark)
    branches, H, P, R = skeleton()
    col = bpy.data.collections.new(AID); bpy.context.scene.collection.children.link(col)
    lods = {}; stats = {}
    for lod in (0, 1, 2):
        o, st = build_lod(lod, [mbark, mats_leaf['green']], branches, H, P, R); col.objects.link(o); lods[lod] = o; stats[lod] = st
        print('LOD', lod, st, flush=True)
    frames = {}
    for lk in LOOKS:
        img, fr = impostor_render([lods[0]], lk, mats_leaf, tmp); XL.place_impostor(atlas, lk, img); frames[lk] = fr
    save_atlas(atlas, atlas_path)
    for im in bpy.data.images:
        if im.filepath and Path(bpy.path.abspath(im.filepath)).name == atlas_path.name: im.reload()
    x0, x1, z0, z1 = frames['green']; u0, v0, u1, v1 = XL.IMPOSTOR_RECT['green']
    b3 = TT.Buf(H)
    for ax in (0, 1):
        def Pq(a, z): return (a, 0, z) if ax == 0 else (0, a, z)
        nrm = (0, -.25, 1) if ax == 0 else (.25, 0, 1)
        b3.quad([Pq(x0, z0), Pq(x1, z0), Pq(x1, z1), Pq(x0, z1)], [(u0, v0), (u1, v0), (u1, v1), (u0, v1)], nrm, 0,
                [(0, 0, .5, 0), (0, 0, .5, 0), (.5, 0, .5, 0), (.5, 0, .5, 0)])
    o3 = b3.build(f'{AID}_LOD3', [mats_imp['green']]); col.objects.link(o3); lods[3] = o3; stats[3] = dict(tris=b3.tris(), wood=0, cards=2)
    cpos = P(.1)       # collider: the trunk's real girth at 0.9-1.5 m (above the root buttresses), from the LOD0 bark
    me0 = lods[0].data; wv = set(v for p in me0.polygons if p.material_index == 0 for v in p.vertices)
    rr_ = [math.hypot(me0.vertices[i].co.x - cpos.x, me0.vertices[i].co.y - cpos.y) for i in wv if .9 < me0.vertices[i].co.z < 1.5]
    rc = float(np.percentile(rr_, 55))
    co = TT.collision_prism(f'{AID}_Collision', rc, 0., 3.5, sides=10, centre=(cpos.x, cpos.y)); col.objects.link(co)
    root = bpy.data.objects.new(AID, None); col.objects.link(root)
    kids = [lods[l] for l in range(4)] + [co]
    for o in kids: o.parent = root
    # gold preview copy of the mesh set (same meshes, gold materials) for the Blender file and the previews
    colg = bpy.data.collections.new(AID + '_GoldPreview'); bpy.context.scene.collection.children.link(colg)
    for l in range(4):
        og = lods[l].copy(); og.data = lods[l].data.copy(); og.name = f'{AID}_Gold_LOD{l}'
        og.data.materials[-1] = mats_imp['gold'] if l == 3 else mats_leaf['gold']
        og.location.x = 40; colg.objects.link(og)
    fbx = EXP / f'{AID}_{VER}.fbx'; export(root, kids, fbx)
    # FBX round trip
    before = set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=str(fbx)); new = [o for o in bpy.data.objects if o not in before]
    rt = {}
    for o in new:
        if o.type == 'MESH':
            ws_ = [o.matrix_world @ Vector(c) for c in o.bound_box]
            rt[o.name.split('.')[0]] = dict(tris=sum(len(p.vertices) - 2 for p in o.data.polygons), max_z=round(max(v.z for v in ws_), 3), min_z=round(min(v.z for v in ws_), 3),
                                            colour_layers=[a.name for a in o.data.color_attributes], materials=[m.name.split('.')[0] for m in o.data.materials if m])
    for o in new: bpy.data.objects.remove(o, do_unlink=True)
    ws = [Vector(c) for c in lods[0].bound_box]; lo = Vector([min(v[i] for v in ws) for i in range(3)]); hi = Vector([max(v[i] for v in ws) for i in range(3)])
    texres = {}
    for p in sorted(TEX.glob('*.png')):
        im = bpy.data.images.load(str(p), check_existing=True); texres[p.name] = list(im.size)
    budget = {f'LOD{l}': dict(triangles=stats[l]['tris'], cap=CAPS[l], objects=1, materials=len(lods[l].data.materials),
                              wood_triangles=stats[l]['wood'], leaf_cards=stats[l]['cards']) for l in range(4)}
    info = dict(asset=AID, version=VER, game='承天', name_zh='仙俠風格大型綠樹（另有金黃葉版本，共用模型與貼圖）', minTier='low',
                use='宗門庭院、山林、草原的地標大樹（多年古樹，不是世界樹）',
                height_m=round(hi.z, 3), crown_width_m=[round(hi.x - lo.x, 3), round(hi.y - lo.y, 3)], dimensions_m=[round(x, 3) for x in hi - lo],
                bounds_min_m=[round(x, 3) for x in lo], bounds_max_m=[round(x, 3) for x in hi],
                origin='trunk base centre, z = 0 on the ground; roots go down to z = -0.3', unit='1 Blender unit = 1 m; front = -Y',
                collision_capsule=dict(radius=round(rc, 3), height=3.5, centre=[round(cpos.x, 3), round(cpos.y, 3), 1.75]),
                collision_note=f'{AID}_Collision: 10-sided prism round the trunk (radius {rc:.2f} m, 0-3.5 m). Hide its renderer, use it as a MeshCollider. The crown and roots do not block.',
                looks={k: v for k, v in LOOKS.items()}, leaf_shader=dict(detail=DETAIL, value=VALUE, mean_value=round(mean, 4), graze_min=GRAZE[0], graze_max=GRAZE[1]),
                materials_per_look=[f'M_{SP}_Bark', f'M_{SP}_Leaves_<Look>', f'M_{SP}_Impostor_<Look>'],
                wind_vertex_colour='Wind (linear): R sway weight, G phase, B light mask (leaves), A tint variation (leaves)',
                lod_switch_distance_m=LOD_SWITCH_M, budget_per_lod=budget, texture_resolution_px=texres,
                status=dict(Exported=True, Imported='Unity 6000.3.28f1 編輯器批次檢查通過（XianxiaTreeCheck，2026-11-13）', Visually_Verified='Blender 與 Unity 審圖（2026-11-13）', In_game_Verified='未驗：只在 Qingxi 灰模裡擺拍（不存檔），沒有放進正式場景'))
    (EXP / 'model_info.json').write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
    checks = dict(lod_caps=all(budget[f'LOD{l}']['triangles'] <= CAPS[l] for l in range(4)), height_in_range=HEIGHT_RANGE[0] <= hi.z <= HEIGHT_RANGE[1],
                  roots_to_minus_0p3=abs(lo.z + .3) < .05, fbx_objects=sorted(rt) == sorted(o.name for o in kids),
                  fbx_height_err_m=round(abs(rt.get(f'{AID}_LOD0', {}).get('max_z', 0) - hi.z), 4),
                  fbx_wind_colour=all('Wind' in rt.get(o.name, {}).get('colour_layers', []) for o in kids[:4]))
    (EXP / 'validation.json').write_text(json.dumps(dict(asset=AID, version=VER, built=time.strftime('%Y-%m-%d %H:%M'), blender=bpy.app.version_string,
                                                         checks=checks, fbx_roundtrip=rt, files={p.name: sha(p) for p in sorted(EXP.glob('*.*')) if p.suffix in ('.fbx', '.glb')}),
                                                    ensure_ascii=False, indent=2), encoding='utf-8')
    print('CHECKS', checks, 'height', round(hi.z, 2), 'size', [round(x, 2) for x in hi - lo], flush=True)
    out = HERE / 'blend' / f'{AID}_{VER}.blend'; out.parent.mkdir(exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out), compress=True)
    print('DONE', round(time.time() - t0, 1), 's', flush=True)


if __name__ == '__main__':
    main()
