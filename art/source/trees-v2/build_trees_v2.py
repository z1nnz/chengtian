"""trees-v2 (2026-11-14 work pack 「樹木重做 v2：照天空島世界樹的做法」): one species per process, three variants (A, B, C).

  blender --background --factory-startup --python art/source/trees-v2/build_trees_v2.py -- TR01
  ... -- TR01 --force          rebuild although validation.json exists
  ... -- TR01 --only A         one variant (sample / iteration)
  ... -- TR01 --only A --quick LOD0 only, no export (look development); saves blend/<SP>_quick.blend

Per species <SP> and variant <ID> (e.g. TR01_A_Pine):
  art/exports/trees-v2/<SP>_Shared/Textures/<SP>_Bark_{BaseColor,Normal,MetallicSmoothness}.png   tiling bark, 1024
  art/exports/trees-v2/<SP>_Shared/Textures/<SP>_Leaves_Palette.png                                leaf colour lookup, 256 x 64
  art/exports/trees-v2/<SP>_Shared/Textures/<SP>_Impostor_{BaseColor,Normal}.png                  LOD3 front views, 512 x 512 per variant (1536 x 512)
  art/exports/trees-v2/<ID>/<ID>_v002.fbx, .glb, model_info.json, validation.json
  art/source/trees-v2/blend/<SP>_v002.blend
FBX: root empty <ID>, children <ID>_LOD0..LOD3 (one mesh each; slots M_<SP>_Bark / M_<SP>_Leaves; LOD3 M_<SP>_Impostor only) and
<ID>_Collision (trunk prism: hide its renderer, use as MeshCollider or a capsule of the same size). Unity builds the LODGroup from the
_LOD suffixes.
"""
import bpy, sys, json, math, time, hashlib
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np
from mathutils import Vector
import tr_tex as TX
import tr_tree as TT
import tr_skin as TS
import tv2_core as C

KIT = 'trees-v2'; VER = 'v002'
ART = HERE.parents[1]
EXP = ART / 'exports' / KIT
CAPS = {0: 60000, 1: 15000, 2: 4000, 3: 200}
LOD_SWITCH_M = [35, 90, 220, 1200]      # suggested: LOD0->1, 1->2, 2->3, 3->culled (40 deg vertical FOV); Unity sets LODGroup heights from them
SPECIES = {
    'TR01': dict(module='tv2_pine', zh='松', half=False, height=(12., 18.),
                 slot={'A': 'D2 外圈主林、A1、A4', 'B': 'D2 外圈主林、A1、A4', 'C': 'B1 崖邊'}),
}
WORK_PACK = '2026-11-14 樹木重做 v2：照天空島世界樹的做法（B：針葉和大喬木）'


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; sc.unit_settings.system = 'METRIC'; sc.unit_settings.scale_length = 1.


def _img(p, non_color=False):
    im = bpy.data.images.load(str(p), check_existing=True)
    if non_color: im.colorspace_settings.name = 'Non-Color'
    return im


def material_bark(sp, tex):
    m = bpy.data.materials.new(f'M_{sp}_Bark'); m.use_nodes = True; nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    ic = nt.nodes.new('ShaderNodeTexImage'); ic.image = _img(tex['BaseColor'])
    inn = nt.nodes.new('ShaderNodeTexImage'); inn.image = _img(tex['Normal'], True)
    ims = nt.nodes.new('ShaderNodeTexImage'); ims.image = _img(tex['MetallicSmoothness'], True)
    nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(inn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs[0], bs.inputs['Normal'])
    nt.links.new(ic.outputs['Color'], bs.inputs['Base Color'])
    inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1
    nt.links.new(ims.outputs['Alpha'], inv.inputs[1]); nt.links.new(inv.outputs[0], bs.inputs['Roughness'])
    bs.inputs['Specular IOR Level'].default_value = .3
    return m


def material_leaves(sp, palette):
    """Opaque, both faces, high roughness; colour from the palette texture via UV0 (identical to the vertex colour). Back faces get a
    translucent BSDF in the preview only (Unity's two-sided foliage lighting wraps the shaded side; Cycles would go black)."""
    m = bpy.data.materials.new(f'M_{sp}_Leaves'); m.use_nodes = True; nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    ic = nt.nodes.new('ShaderNodeTexImage'); ic.name = 'LEAF_COLOR'; ic.image = _img(palette); ic.interpolation = 'Linear'; ic.extension = 'EXTEND'
    uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'UVMap'; nt.links.new(uvn.outputs[0], ic.inputs[0])
    nt.links.new(ic.outputs['Color'], bs.inputs['Base Color'])
    geo = nt.nodes.new('ShaderNodeNewGeometry'); tr = nt.nodes.new('ShaderNodeBsdfTranslucent')
    dim = nt.nodes.new('ShaderNodeMixRGB'); dim.blend_type = 'MULTIPLY'; dim.inputs[0].default_value = 1.; dim.inputs[2].default_value = (.7, .74, .7, 1)
    nt.links.new(ic.outputs['Color'], dim.inputs[1]); nt.links.new(dim.outputs[0], tr.inputs['Color'])
    mx = nt.nodes.new('ShaderNodeMixShader'); out = nt.nodes['Material Output']
    nt.links.new(geo.outputs['Backfacing'], mx.inputs[0]); nt.links.new(bs.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs['Surface'])
    bs.inputs['Roughness'].default_value = .9; bs.inputs['Specular IOR Level'].default_value = .15
    m.use_backface_culling = False
    return m


def material_impostor(sp, tex):
    m = bpy.data.materials.new(f'M_{sp}_Impostor'); m.use_nodes = True; nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    ic = nt.nodes.new('ShaderNodeTexImage'); ic.image = _img(tex['BaseColor'])
    nt.links.new(ic.outputs['Color'], bs.inputs['Base Color'])
    tm = nt.nodes.new('ShaderNodeMixShader'); trn = nt.nodes.new('ShaderNodeBsdfTransparent'); out = nt.nodes['Material Output']
    rnd = nt.nodes.new('ShaderNodeMath'); rnd.operation = 'GREATER_THAN'; rnd.inputs[1].default_value = .5
    nt.links.new(ic.outputs['Alpha'], rnd.inputs[0]); nt.links.new(rnd.outputs[0], tm.inputs[0])
    nt.links.new(trn.outputs[0], tm.inputs[1]); nt.links.new(bs.outputs[0], tm.inputs[2]); nt.links.new(tm.outputs[0], out.inputs['Surface'])
    bs.inputs['Roughness'].default_value = .9; m.use_backface_culling = False
    return m


def build_lod(mod, var, lod, mats, rng_seed, aid):
    sk = mod.skeleton(var); H = sk['H']
    buf = C.Buf2(H)
    if hasattr(mod, 'wood'):        # the species builds its own wood (TR01 since 2026-11-15: tubes, child inside parent)
        wood = mod.wood(buf, sk, lod)
    else:
        levels, subdiv, target = mod.SKIN_WOOD[lod]
        wood, b0, b1 = TS.skin_wood(buf, sk['branches'], levels, subdiv, target)
    rng = np.random.default_rng(rng_seed + lod)
    blades, twig = mod.foliage(buf, sk, lod, var, rng)
    o = buf.build(f'{aid}_LOD{lod}', mats)
    tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
    return o, dict(wood=wood + twig, spray_twigs=twig, leaves=blades, leaf_tris=tris - wood - twig, tris=tris, anchors=len(sk['anchors'])), sk


def impostor(objs, tmp, W=512, Hh=512):
    """Front view (looking +Y) of LOD0, orthographic, under a uniform white sky (= albedo x occlusion)."""
    scene = bpy.context.scene
    for o in scene.objects: o.hide_render = o not in objs
    ws = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(v.x for v in ws), min(v.y for v in ws), -.3)); hi = Vector((max(v.x for v in ws), max(v.y for v in ws), max(v.z for v in ws)))
    cx = (lo.x + hi.x) / 2; half_w = max(hi.x - cx, cx - lo.x) * 1.02; aspect = W / Hh
    height = max(hi.z - lo.z + .1, 2 * half_w / aspect); width = height * aspect
    cam = bpy.data.objects.new('ImpCam', bpy.data.cameras.new('ImpCam')); scene.collection.objects.link(cam); scene.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = height; cam.data.clip_end = 300
    cam.location = (cx, -80, lo.z + height / 2); cam.rotation_euler = (math.pi / 2, 0, 0)
    w = bpy.data.worlds.new('Imp_World'); w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (1, 1, 1, 1); bg.inputs[1].default_value = 1.
    keep_world = scene.world; scene.world = w
    scene.render.engine = 'CYCLES'; scene.cycles.samples = 64; scene.cycles.use_denoising = True
    scene.render.film_transparent = True; scene.render.resolution_x = W; scene.render.resolution_y = Hh; scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'Standard'; scene.view_settings.look = 'None'; scene.view_settings.exposure = 0
    fp = tmp / f'imp_{objs[0].name}.png'; scene.render.filepath = str(fp); bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(str(fp)); c = np.array(im.pixels[:], np.float32).reshape(Hh, W, 4); bpy.data.images.remove(im)
    c[..., 3] = (c[..., 3] > .5).astype(np.float32)
    n = TX.dome_normal(c[..., 3]); n = np.concatenate([n, np.ones((Hh, W, 1), np.float32)], -1)
    scene.world = keep_world; bpy.data.objects.remove(cam)
    for o in scene.objects: o.hide_render = False
    return {'c': c, 'n': n}, dict(x0=cx - width / 2, x1=cx + width / 2, z0=lo.z, z1=lo.z + height)


def save_impostor_atlas(imps, shared, sp, W=512, Hh=512):
    cols = len(imps); out = {}
    for key, name, srgb in (('c', 'BaseColor', True), ('n', 'Normal', False)):
        a = np.zeros((Hh, W * cols, 4), np.float32)
        for k, im in enumerate(imps): a[:, k * W:(k + 1) * W] = im[key]
        if key == 'c':     # bleed colour into the cut-out area so mips do not halo
            col, al = a[..., :3], a[..., 3]; a[..., :3] = TX.dilate(col, al, reach=24, blank=(.12, .18, .14))
        # the rendered PNG already holds display (sRGB) values, and Blender hands byte-image pixels back unchanged
        out[name] = TX.save_png(a, shared / f'{sp}_Impostor_{name}.png', srgb=srgb)
    return out


def impostor_cards(name, rect, fr, mat, H):
    """LOD3: two crossed cards through the crown centre, normals up-and-out."""
    buf = C.Buf2(H); u0, v0, u1, v1 = rect; cx = (fr['x0'] + fr['x1']) / 2; hw = (fr['x1'] - fr['x0']) / 2
    for ax in (0, 1):
        def Pp(a, z): return (cx + a, 0, z) if ax == 0 else (cx, a, z)
        nrm = (0, -.2, 1) if ax == 0 else (.2, 0, 1)
        buf.quad([Pp(-hw, fr['z0']), Pp(hw, fr['z0']), Pp(hw, fr['z1']), Pp(-hw, fr['z1'])], [(u0, v0), (u1, v0), (u1, v1), (u0, v1)], nrm, 0,
                 [buf.wind(0, 0, fr['z0'])] * 2 + [buf.wind(.25, 0, fr['z1'])] * 2)
    return buf.build(name, [mat])


def export(root, children, fbx):
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    for o in children: o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, object_types={'MESH', 'EMPTY'}, apply_unit_scale=True,
                             apply_scale_options='FBX_SCALE_ALL', bake_space_transform=True, axis_forward='-Z', axis_up='Y',
                             mesh_smooth_type='FACE', use_mesh_modifiers=True, add_leaf_bones=False, bake_anim=False,
                             path_mode='STRIP', embed_textures=False, colors_type='LINEAR', prioritize_active_color=True)
    bpy.ops.export_scene.gltf(filepath=str(fbx.with_suffix('.glb')), use_selection=True, export_format='GLB', export_yup=True,
                              export_apply=True, export_vertex_color='ACTIVE', export_attributes=False)


def roundtrip(fbx):
    before = set(bpy.data.objects)
    col = bpy.data.collections.new('99_FBX_Check'); bpy.context.scene.collection.children.link(col)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[col.name]
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    new = [o for o in bpy.data.objects if o not in before]; bpy.context.view_layer.update()
    base = lambda n: n.split('.')[0]
    rep = {'objects': sorted(base(o.name) for o in new)}
    for o in new:
        if o.type != 'MESH': continue
        ws = [o.matrix_world @ Vector(c) for c in o.bound_box]
        lo = Vector([min(v[i] for v in ws) for i in range(3)]); hi = Vector([max(v[i] for v in ws) for i in range(3)])
        rep[base(o.name)] = dict(tris=sum(len(p.vertices) - 2 for p in o.data.polygons), min=[round(x, 3) for x in lo], max=[round(x, 3) for x in hi],
                                 colour_layers=[a.name for a in o.data.color_attributes], uv_layers=[u.name for u in o.data.uv_layers],
                                 materials=[m.name for m in o.data.materials if m])
    for o in new: bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(col); bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection
    return rep


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    argv = sys.argv[sys.argv.index('--') + 1:]
    sp = argv[0]; force = '--force' in argv; quick = '--quick' in argv
    only = argv[argv.index('--only') + 1] if '--only' in argv else None
    spc = SPECIES[sp]; mod = __import__(spc['module'])
    variants = [v for v in mod.VARIANTS if only is None or v == only]
    ids = {v: f'{sp}_{v}_{mod.NAMES[v]}' for v in mod.VARIANTS}
    if not force and not quick and all((EXP / ids[v] / 'validation.json').exists() for v in variants):
        print('SKIP', sp, 'already built (use --force)'); return
    t0 = time.time(); reset()
    shared = EXP / f'{sp}_Shared' / 'Textures'; shared.mkdir(parents=True, exist_ok=True)
    tmp = Path(bpy.app.tempdir or '.') / f'trees_v2_{sp}'; tmp.mkdir(parents=True, exist_ok=True)
    bark = TX.painted_bark(shared, sp, HERE / mod.BARK_PAINTED['src'], **{k: v for k, v in mod.BARK_PAINTED.items() if k != 'src'})
    pal = C.palette_png(shared / f'{sp}_Leaves_Palette.png', [C.hexc(h) for h in mod.PALETTE], mod.OCCL_LO)
    mats = [material_bark(sp, bark), material_leaves(sp, pal)]
    built = {}
    for k, var in enumerate(variants):
        aid = ids[var]; col = bpy.data.collections.new(aid); bpy.context.scene.collection.children.link(col)
        lods = {}; stats = {}
        for lod in ((0,) if quick else (0, 1, 2)):
            o, st, sk = build_lod(mod, var, lod, mats, 1000 + 'ABC'.index(var) * 17, aid)
            col.objects.link(o); lods[lod] = o; stats[lod] = st
            print('BUILT', aid, f'LOD{lod}', st, flush=True)
        built[var] = dict(aid=aid, col=col, lods=lods, stats=stats, sk=sk)
    if quick:
        out = HERE / 'blend' / f'{sp}_quick.blend'; out.parent.mkdir(exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(out)); print('QUICK', out, round(time.time() - t0, 1), 's'); return
    imps = []
    for var in variants:
        res, frame = impostor([built[var]['lods'][0]], tmp); imps.append(res); built[var]['frame'] = frame
    imp_tex = save_impostor_atlas(imps, shared, sp)
    mat_imp = material_impostor(sp, imp_tex)
    for k, var in enumerate(variants):
        b = built[var]; H = b['sk']['H']; n = len(variants)
        o3 = impostor_cards(f'{b["aid"]}_LOD3', (k / n, 0., (k + 1) / n, 1.), b['frame'], mat_imp, H)
        b['col'].objects.link(o3); b['lods'][3] = o3; b['stats'][3] = dict(wood=0, leaves=0, tris=4)
        P, R = b['sk']['P'], b['sk']['R']; rc = R(.12) * 1.05
        co = TT.collision_prism(f'{b["aid"]}_Collision', rc, 0., 3.0, centre=(P(.12).x, P(.12).y)); b['col'].objects.link(co); b['coll'] = (co, rc)
    out_blend = HERE / 'blend' / f'{sp}_{VER}.blend'; out_blend.parent.mkdir(exist_ok=True)
    texres = {}
    for p in sorted(shared.glob('*.png')):
        im = bpy.data.images.load(str(p), check_existing=True); texres[p.name] = list(im.size)
    for var in variants:
        b = built[var]; aid = b['aid']; d = EXP / aid; d.mkdir(parents=True, exist_ok=True)
        root = bpy.data.objects.new(aid, None); b['col'].objects.link(root)
        kids = [b['lods'][l] for l in range(4)] + [b['coll'][0]]
        for o in kids: o.parent = root
        fbx = d / f'{aid}_{VER}.fbx'; export(root, kids, fbx)
        rt = roundtrip(fbx)
        lo0 = b['lods'][0]; ws = [Vector(c) for c in lo0.bound_box]
        lo = Vector([min(v[i] for v in ws) for i in range(3)]); hi = Vector([max(v[i] for v in ws) for i in range(3)])
        co, rc = b['coll']; st = b['stats']
        budget = {f'LOD{l}': dict(triangles=st[l]['tris'], cap=CAPS[l], objects=1, materials=len([m for m in b['lods'][l].data.materials if m]),
                                  wood_triangles=st[l].get('wood', 0), leaf_blades=st[l].get('leaves', 0)) for l in range(4)}
        sk = b['sk']
        info = dict(asset=aid, version=VER, minTier='low', name_zh=mod.ZH[var], species=sp, species_zh=spc['zh'], slot=spc['slot'][var],
                    work_pack=WORK_PACK, method='docs/execution/2026-11-14/tree-method（天空島世界樹）：S 形主幹、不對稱主枝、三級枝、葉冠錨點＋枝梢流、五頂點立體葉、頂點色',
                    reference=getattr(mod, 'REFERENCE', f'art/references/{sp}/v002/prompt.txt'),
                    height_m=round(hi.z, 3), dimensions_m=[round(x, 3) for x in hi - lo], bounds_min_m=[round(x, 3) for x in lo], bounds_max_m=[round(x, 3) for x in hi],
                    ground_z_m=0., root_depth_m=.3, origin='trunk base centre, z = 0 on the ground; roots go down to z = -0.3', front='-Y (Blender) = +Z (Unity)',
                    crown_anchors=st[0]['anchors'], main_limbs=sk.get('main_limbs') or len(mod.VARIANTS[var]['limbs']), seed=mod.VARIANTS[var]['seed'],
                    collision=True, collision_note=f'{aid}_Collision: 8-sided prism round the trunk (radius {rc:.2f} m, z 0-3 m); hide its renderer, use it as a MeshCollider or a CapsuleCollider of the same size. The crown does not block.',
                    collision_capsule=dict(radius=round(rc, 3), height=3.0, centre=[round(co.data.vertices[0].co.x - rc, 3), round(co.data.vertices[0].co.y, 3), 1.5]),
                    objects_per_lod=1, materials=[m.name for m in mats] + [mat_imp.name], material_slots={'LOD0-2': [m.name for m in mats], 'LOD3': [mat_imp.name]},
                    shared_textures=f'art/exports/{KIT}/{sp}_Shared/Textures', texture_resolution_px=texres,
                    leaf_geometry=getattr(mod, 'LEAF_GEOMETRY', ''),
                    leaf_material='opaque (no alpha), both faces drawn, roughness about 0.9, metallic 0; BaseColor = the palette texture on UV0 (or multiply the vertex colour instead)',
                    vertex_colour='Color (FBX vertex colour, linear): leaves RGB = leaf colour from height / inside-outside, A = canopy occlusion (not transparency); wood RGB 1, A 1',
                    wind='UV1 "Wind": u = sway weight (trunk 0, limbs 0.03-0.3, secondaries 0.3-0.5, tips 0.5-0.8, leaves 0.62-1), v = phase 0..1',
                    lod_switch_distance_m=LOD_SWITCH_M, lod3='two crossed cards with a front impostor of LOD0 (impostor atlas column {})'.format(variants.index(var)),
                    budget_per_lod=budget, lod_totals={f'LOD{l}': st[l]['tris'] for l in range(4)},
                    texture_naming='BaseColor = Albedo; MetallicSmoothness = URP mask (R metallic 0, A smoothness), same naming as village-houses-b (VL)',
                    status=dict(Exported=True, Imported='未驗', Visually_Verified='未驗', In_game_Verified='未驗'))
        (d / 'model_info.json').write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
        checks = {
            'lod_caps': all(budget[f'LOD{l}']['triangles'] <= CAPS[l] for l in range(4)),
            'height_in_range': spc['height'][0] <= hi.z <= spc['height'][1],
            'origin_ground': abs(lo.z + .3) < .05,
            'anchors_12_20': 12 <= st[0]['anchors'] <= 20,
            'fbx_objects': sorted(rt['objects']) == sorted([aid] + [o.name for o in kids]),
            'fbx_lod0_height_err_m': round(abs(rt[f'{aid}_LOD0']['max'][2] - hi.z), 4) if f'{aid}_LOD0' in rt else None,
            'fbx_vertex_colour': all(rt[o.name]['colour_layers'] for o in kids[:3] if o.name in rt),
            'fbx_wind_uv': all(len(rt[o.name]['uv_layers']) >= 2 for o in kids[:3] if o.name in rt),
        }
        val = dict(asset=aid, version=VER, built=time.strftime('%Y-%m-%d %H:%M'), blender=bpy.app.version_string, checks=checks, fbx_roundtrip=rt,
                   files={p.name: sha(p) for p in sorted(d.glob('*')) if p.suffix in ('.fbx', '.glb')})
        (d / 'validation.json').write_text(json.dumps(val, ensure_ascii=False, indent=2), encoding='utf-8')
        print('EXPORTED', aid, checks, flush=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out_blend), compress=True)
    print('DONE', sp, round(time.time() - t0, 1), 's', flush=True)


if __name__ == '__main__':
    main()
