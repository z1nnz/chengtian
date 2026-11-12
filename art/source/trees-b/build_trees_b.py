"""trees-b (work pack 2026-11-11 B-64h, rebuild of every tree in the world): one species per process, three variants (A, B, C).

  blender --background --factory-startup --python art/source/trees-b/build_trees_b.py -- TR01
  ... -- TR01 --force      rebuild although validation.json exists

Per species <SP> (e.g. TR01) and variant <ID> (e.g. TR01_A_Pine):
  art/exports/trees-b/<SP>_Shared/Textures/<SP>_Bark_{BaseColor,Normal,MetallicSmoothness}.png      tiling bark, 1024
  art/exports/trees-b/<SP>_Shared/Textures/<SP>_Leaves_{BaseColor,Normal,MetallicSmoothness}.png    foliage atlas + 3 impostors, 2048
  art/exports/trees-b/<ID>/<ID>_v001.fbx, .glb, model_info.json, validation.json
  art/source/trees-b/blend/<SP>_v001.blend (all three variants)
FBX: root empty <ID>, children <ID>_LOD0..LOD3 (one mesh each, slots M_<SP>_Bark / M_<SP>_Leaves; LOD3 leaves only) and <ID>_Collision
(trunk prism, hide its renderer, use as MeshCollider). Unity builds the LODGroup from the _LOD suffixes.
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

KIT = 'trees-b'; VER = 'v001'
ART = HERE.parents[1]
EXP = ART / 'exports' / KIT
CAPS = {0: 25000, 1: 8000, 2: 2500, 3: 200}
LOD_SWITCH_M = [60, 100, 260, 1500]     # suggested switch distances: LOD0->1, 1->2, 2->3, 3->culled (40 deg vertical FOV, project LOD bias); Unity sets the LODGroup heights from them

SPECIES = {
    'TR01': dict(module='tr_pine', zh='松', half=False, height=(12., 14.), slot={'A': 'A1/A2/A4 全區', 'B': 'A1/A2/A4 全區', 'C': 'B1 崖邊'},
                 wood={0: (14, .42, 9, .36, 6, .35, True), 1: (9, .9, 6, .8, 4, .9, False), 2: (6, 2.2, 4, 1.8, 0, 0, False)},
                 cards={0: dict(density=12., size=1.0, grid=(3, 3), bend=.22), 1: dict(density=11., size=1.45, grid=(3, 2), bend=.16),
                        2: dict(density=8., size=1.9, grid=(2, 2), bend=0.)}),
    'TR02': dict(module='tr_cypress', zh='柏', half=False, height=(9., 11.), slot={'A': 'D1/D2/D4 古林', 'B': 'D1/D2/D4 古林', 'C': 'D1/D2/D4 古林'},
                 wood={0: (20, .24, 7, .4, 4, .45, True), 1: (10, .9, 5, 1.1, 3, 1.6, False), 2: (7, 1.6, 4, 1.6, 0, 0, False)},
                 # stylised: fewer, larger cards facing out (calm masses, notched rims), the shading from the mass normals
                 cards={0: dict(density=9., size=1.25, grid=(3, 3), bend=.2, rand_tilt=.12, depth=.22, spray_frac=.12),
                        1: dict(density=8., size=1.7, grid=(3, 2), bend=.14, rand_tilt=.12, depth=.2, spray_frac=.12),
                        2: dict(density=6., size=2.1, grid=(2, 2), bend=0., rand_tilt=.1, depth=.15, spray_frac=.2)}),
}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; sc.unit_settings.system = 'METRIC'; sc.unit_settings.scale_length = 1.


def material_bark(sp, tex):
    m = bpy.data.materials.new(f'M_{sp}_Bark'); m.use_nodes = True; nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    ic = nt.nodes.new('ShaderNodeTexImage'); ic.image = bpy.data.images.load(str(tex['BaseColor']), check_existing=True)
    inn = nt.nodes.new('ShaderNodeTexImage'); inn.image = bpy.data.images.load(str(tex['Normal']), check_existing=True); inn.image.colorspace_settings.name = 'Non-Color'
    ims = nt.nodes.new('ShaderNodeTexImage'); ims.image = bpy.data.images.load(str(tex['MetallicSmoothness']), check_existing=True); ims.image.colorspace_settings.name = 'Non-Color'
    nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(inn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs[0], bs.inputs['Normal'])
    nt.links.new(ic.outputs['Color'], bs.inputs['Base Color'])
    inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1
    nt.links.new(ims.outputs['Alpha'], inv.inputs[1]); nt.links.new(inv.outputs[0], bs.inputs['Roughness'])
    bs.inputs['Specular IOR Level'].default_value = .3
    return m


def material_leaves(sp, tex):
    m = bpy.data.materials.new(f'M_{sp}_Leaves'); m.use_nodes = True; nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    ic = nt.nodes.new('ShaderNodeTexImage'); ic.name = 'LEAF_COLOR'; ic.image = bpy.data.images.load(str(tex['BaseColor']), check_existing=True)
    inn = nt.nodes.new('ShaderNodeTexImage'); inn.image = bpy.data.images.load(str(tex['Normal']), check_existing=True); inn.image.colorspace_settings.name = 'Non-Color'
    # Preview only (Unity uses the normal map on URP Lit, both faces drawn, normals not flipped): Cycles goes black on a card's back
    # face when the sun is on the front, Unity lights it with the foliage-mass normal. A translucent BSDF on back faces gives the same
    # result (tested: plane lit from above, seen from below -> lit, as in Unity).
    nt.links.new(ic.outputs['Color'], bs.inputs['Base Color'])
    geo = nt.nodes.new('ShaderNodeNewGeometry'); tr = nt.nodes.new('ShaderNodeBsdfTranslucent'); nt.links.new(ic.outputs['Color'], tr.inputs['Color'])
    mx = nt.nodes.new('ShaderNodeMixShader'); out = nt.nodes['Material Output']
    nt.links.new(geo.outputs['Backfacing'], mx.inputs[0]); nt.links.new(bs.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    tm = nt.nodes.new('ShaderNodeMixShader'); trn = nt.nodes.new('ShaderNodeBsdfTransparent')
    nt.links.new(trn.outputs[0], tm.inputs[1]); nt.links.new(mx.outputs[0], tm.inputs[2])
    nt.links.new(tm.outputs[0], out.inputs['Surface'])
    rnd = nt.nodes.new('ShaderNodeMath'); rnd.operation = 'GREATER_THAN'; rnd.inputs[1].default_value = .5
    nt.links.new(ic.outputs['Alpha'], rnd.inputs[0]); nt.links.new(rnd.outputs[0], tm.inputs[0])
    bs.inputs['Roughness'].default_value = .82; bs.inputs['Specular IOR Level'].default_value = .2
    m.use_backface_culling = False
    try: m.surface_render_method = 'DITHERED'
    except Exception: pass
    return m


def build_lod(mod, var, lod, mats, spc, rng_seed):
    branches, puffs, H, P, R = mod.skeleton(var)
    buf = TT.Buf(H)
    ts, tst, ls, lst, ws, wst, stubs = spc['wood'][lod]
    trunk_range = (0, 0)
    if getattr(mod, 'WOOD', 'tube') == 'skin':      # fused wood (golden-spirit-tree method): one Skin mesh, decimated to the budget
        levels, subdiv, target = mod.SKIN_WOOD[lod]
        _, b0, b1 = TS.skin_wood(buf, branches, levels, subdiv, target); trunk_range = (b0, b1); branches_iter = []
    else: branches_iter = branches
    for i, br in enumerate(branches_iter):
        if br.kind == 'trunk': n0 = len(buf.v); buf.tube(br, ts, tst, seed=i); trunk_range = (n0, len(buf.v))
        elif br.kind == 'limb': buf.tube(br, ls, lst, seed=i)
        elif br.kind == 'twig' and ws: buf.tube(br, ws, wst, seed=i)
        elif br.kind == 'stub' and stubs: buf.tube(br, 6, .3, seed=i)
    rng0 = np.random.default_rng(rng_seed + 50 + lod)
    extra = mod.extra_geometry(buf, var, lod, P, R, rng0, trunk_range) if hasattr(mod, 'extra_geometry') else 0     # e.g. moss pads on the trunk (leaf material)
    wood = buf.tris()
    cc = spc['cards'][lod]; rng = np.random.default_rng(rng_seed + lod)
    cards = TT.sample_cards(puffs, rng, cc['density'], cc['size'], grid=cc['grid'], bend=cc['bend'], **{k: cc[k] for k in ('depth', 'spray_frac', 'top_bias', 'rand_tilt') if k in cc})
    if hasattr(mod, 'retone_cards'): mod.retone_cards(cards, H, rng)     # optional per-species atlas sub-cell choice (e.g. TR02 tone by height)
    aspect = getattr(mod, 'CELL_ASPECT', {})
    for cd in cards: cd['aspect'] = aspect.get(cd['cell'], 1.)
    per = (cc['grid'][0] - 1) * (cc['grid'][1] - 1) * 2
    cap = CAPS[lod] * (.5 if spc['half'] else 1.) * .94
    room = int((cap - wood) // per)
    if len(cards) > room:      # keep an even spread: drop the deepest cards first, then thin at random
        cards.sort(key=lambda c: c['dep']); keep = cards[:room]; cards = keep
    TT.add_cards(buf, cards, cc['grid'], cc['bend'], cells=getattr(mod, 'CELL_RECTS', None))
    o = buf.build(f'{spc["ids"][var]}_LOD{lod}', mats)
    tris = sum(len(p.vertices) - 2 for p in o.data.polygons)      # after mesh validation (it may drop a few degenerate faces, as Unity does)
    return o, dict(wood=wood - extra, extra=extra, cards=len(cards) + (getattr(mod, 'last_extra_cards', 0) if extra else 0), tris=tris), (branches, puffs, H, P, R)


def impostor(objs, k, tex_tmp, size=2048):
    """Front view (looking +Y) of LOD0, orthographic, under a uniform white sky (= albedo x occlusion), into a 682 x 1024 column."""
    scene = bpy.context.scene
    for o in scene.objects: o.hide_render = o not in objs
    lo = Vector((min(v[0] for o in objs for v in o.bound_box), min(v[1] for o in objs for v in o.bound_box), -.3))
    hi = Vector((max(v[0] for o in objs for v in o.bound_box), max(v[1] for o in objs for v in o.bound_box), max(v[2] for o in objs for v in o.bound_box)))
    half_w = max(abs(lo.x), abs(hi.x), abs(lo.y), abs(hi.y)) * 1.02
    W = size // 3; Hh = size // 2; aspect = W / Hh
    height = max(hi.z - lo.z + .1, 2 * half_w / aspect); width = height * aspect
    cam = bpy.data.objects.new('ImpCam', bpy.data.cameras.new('ImpCam')); scene.collection.objects.link(cam); scene.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = height; cam.data.clip_end = 200
    cam.location = (0, -60, lo.z + height / 2); cam.rotation_euler = (math.pi / 2, 0, 0)
    w = bpy.data.worlds.new('Imp_World'); w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (1, 1, 1, 1); bg.inputs[1].default_value = 1.
    keep_world = scene.world; scene.world = w
    scene.render.engine = 'CYCLES'; scene.cycles.samples = 64; scene.cycles.use_denoising = True
    scene.render.film_transparent = True; scene.render.resolution_x = W; scene.render.resolution_y = Hh; scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'Standard'; scene.view_settings.look = 'None'; scene.view_settings.exposure = 0
    fp = tex_tmp / f'imp_{k}.png'; scene.render.filepath = str(fp); bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(str(fp)); c = np.array(im.pixels[:], np.float32).reshape(Hh, W, 4); bpy.data.images.remove(im)
    c[..., 3] = (c[..., 3] > .5).astype(np.float32)
    leafy = (c[..., 1] > c[..., 0] * 1.05)[..., None]     # foliage pixels only (green over red); the bark stays as rendered
    c[..., :3] = np.where(leafy, np.clip(c[..., :3] * 1.18, 0, 1), c[..., :3])        # LOD3 foliage read a step darker than LOD0 in Unity
    n = TX.dome_normal(c[..., 3]); n = np.concatenate([n, np.ones((Hh, W, 1), np.float32)], -1)
    scene.world = keep_world; bpy.data.objects.remove(cam)
    for o in scene.objects: o.hide_render = False
    return {'c': c, 'n': n}, dict(x0=-width / 2, x1=width / 2, z0=lo.z, z1=lo.z + height)


def export(aid, root, children, fbx):
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
    base = lambda n: n.split('.')[0]          # re-imported objects get .001 suffixes next to the originals
    rep = {'objects': sorted(base(o.name) for o in new)}
    for o in new:
        if o.type != 'MESH': continue
        ws = [o.matrix_world @ Vector(c) for c in o.bound_box]
        lo = Vector([min(v[i] for v in ws) for i in range(3)]); hi = Vector([max(v[i] for v in ws) for i in range(3)])
        rep[base(o.name)] = dict(tris=sum(len(p.vertices) - 2 for p in o.data.polygons), min=[round(x, 3) for x in lo], max=[round(x, 3) for x in hi],
                           colour_layers=[a.name for a in o.data.color_attributes], materials=[m.name for m in o.data.materials if m])
    for o in new: bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(col); bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection
    return rep


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    argv = sys.argv[sys.argv.index('--') + 1:]
    sp = argv[0]; force = '--force' in argv
    spc = SPECIES[sp]; mod = __import__(spc['module'])
    spc['ids'] = {v: f'{sp}_{v}_{mod.NAMES[v]}' for v in mod.VARIANTS}
    if not force and all((EXP / spc['ids'][v] / 'validation.json').exists() for v in mod.VARIANTS):
        print('SKIP', sp, 'already built (use --force)'); return
    t0 = time.time(); reset()
    shared = EXP / f'{sp}_Shared' / 'Textures'; shared.mkdir(parents=True, exist_ok=True)
    tmp = Path(bpy.app.tempdir or '.') / f'trees_b_{sp}'; tmp.mkdir(parents=True, exist_ok=True)
    if hasattr(mod, 'BARK_PAINTED'): bark = TX.painted_bark(shared, sp, HERE / mod.BARK_PAINTED['src'], **{k: v for k, v in mod.BARK_PAINTED.items() if k != 'src'})
    else: bark = TX.bark_texture(shared, sp, TX.BARK_STYLES[mod.BARK], seed=int(hashlib.md5(sp.encode()).hexdigest()[:6], 16) % 1000)
    cells = TX.render_cells(mod.CELLS, shared, sp, cell_m=mod.CELL_M, ao_dist=getattr(mod, 'CELL_AO', .06))
    blank = [{'c': np.zeros((1024, 682, 4), np.float32), 'n': np.zeros((1024, 682, 4), np.float32)} for _ in range(3)]
    leaves = TX.assemble_atlas(cells, blank, shared, sp)
    mats = [material_bark(sp, bark), material_leaves(sp, leaves)]
    built = {}
    for k, var in enumerate(mod.VARIANTS):
        aid = spc['ids'][var]; col = bpy.data.collections.new(aid); bpy.context.scene.collection.children.link(col)
        lods = {}; stats = {}
        for lod in (0, 1, 2):
            o, st, skel = build_lod(mod, var, lod, mats, spc, 1000 + k * 17)
            col.objects.link(o); lods[lod] = o; stats[lod] = st
        built[var] = dict(aid=aid, col=col, lods=lods, stats=stats, skel=skel)
        print('BUILT', aid, {l: s['tris'] for l, s in stats.items()}, flush=True)
    imps = []
    for k, var in enumerate(mod.VARIANTS):
        res, frame = impostor([built[var]['lods'][0]], k, tmp); imps.append(res); built[var]['frame'] = frame
    leaves = TX.assemble_atlas(cells, imps, shared, sp)
    for im in bpy.data.images:
        if im.filepath and Path(bpy.path.abspath(im.filepath)).name.startswith(f'{sp}_Leaves'): im.reload()
    for k, var in enumerate(mod.VARIANTS):
        b = built[var]; H = b['skel'][2]; fr = b['frame']
        buf = TT.Buf(H); TT.cross_cards(buf, TT.IMPOSTOR_RECT(k), fr['x0'], fr['x1'], fr['z0'], fr['z1'])
        o3 = buf.build(f'{b["aid"]}_LOD3', [mats[1]]); b['col'].objects.link(o3); b['lods'][3] = o3; b['stats'][3] = dict(wood=0, cards=4, tris=buf.tris())
        P, R = b['skel'][3], b['skel'][4]; rc = R(.12) * 1.05
        co = TT.collision_prism(f'{b["aid"]}_Collision', rc, 0., 3.0, centre=(P(.12).x, P(.12).y)); b['col'].objects.link(co); b['coll'] = (co, rc)
    out_blend = HERE / 'blend' / f'{sp}_{VER}.blend'; out_blend.parent.mkdir(exist_ok=True)
    for var in mod.VARIANTS:
        b = built[var]; aid = b['aid']; d = EXP / aid; d.mkdir(parents=True, exist_ok=True)
        root = bpy.data.objects.new(aid, None); b['col'].objects.link(root)
        kids = [b['lods'][l] for l in range(4)] + [b['coll'][0]]
        for o in kids: o.parent = root
        fbx = d / f'{aid}_{VER}.fbx'; export(aid, root, kids, fbx)
        rt = roundtrip(fbx)
        lo0 = b['lods'][0]; ws = [Vector(c) for c in lo0.bound_box]
        lo = Vector([min(v[i] for v in ws) for i in range(3)]); hi = Vector([max(v[i] for v in ws) for i in range(3)])
        H = b['skel'][2]; co, rc = b['coll']
        budget = {f'LOD{l}': dict(triangles=b['stats'][l]['tris'], objects=1, objects_without_detail=1, materials=len([m for m in b['lods'][l].data.materials if m]),
                                  cap=int(CAPS[l] * (.5 if spc['half'] else 1)), wood_triangles=b['stats'][l]['wood'], extra_leaf_triangles=b['stats'][l].get('extra', 0), leaf_cards=b['stats'][l]['cards'])
                  for l in range(4)}
        texres = {}
        for p in sorted(shared.glob('*.png')):
            im = bpy.data.images.load(str(p), check_existing=True); texres[p.name] = list(im.size)
        info = dict(asset=aid, version=VER, minTier='low', detailObjects=[], name_zh=mod.ZH[var], species=sp, species_zh=spc['zh'], slot=spc['slot'][var],
                    work_pack='2026-11-11 B｜64 小時：世界裡的樹全部重做（九種），A 批', reference=f'art/references/{sp}/prompt.txt',
                    note=mod.__doc__.strip().splitlines()[0],
                    height_m=round(hi.z, 3), dimensions_m=[round(x, 3) for x in hi - lo], bounds_min_m=[round(x, 3) for x in lo], bounds_max_m=[round(x, 3) for x in hi],
                    ground_z_m=0., root_depth_m=.3, origin='trunk base centre, z = 0 on the ground; roots go down to z = -0.3',
                    collision=True, collision_note=f'{aid}_Collision: 8-sided prism around the trunk (radius {rc:.2f} m, z 0-3 m); hide its renderer and use it as a MeshCollider or replace it with a CapsuleCollider of the same size. The crown does not block.',
                    collision_capsule=dict(radius=round(rc, 3), height=3.0, centre=[round(co.data.vertices[0].co.x - rc, 3), round(co.data.vertices[0].co.y, 3), 1.5]),
                    materials=[m.name for m in mats], shared_textures=f'art/exports/{KIT}/{sp}_Shared/Textures',
                    leaf_material='alpha clip 0.5 on BaseColor alpha, both faces drawn, import BaseColor with Mip Maps Preserve Coverage (reference 0.5)',
                    wind_vertex_colour='Wind (FBX vertex colour, linear): R sway weight (trunk 0, limbs 0.02-0.3, twigs 0.3-0.5, leaf masses 0.6-1), G phase per mass, B height 0..1, A 1',
                    lod_switch_distance_m=LOD_SWITCH_M, lod3='two crossed cards with a front impostor of LOD0 from the leaves atlas (bottom half, column {})'.format('ABC'.index(var)),
                    budget_per_lod=budget, lod_totals={f'LOD{l}': b['stats'][l]['tris'] for l in range(4)}, texture_resolution_px=texres,
                    texture_naming='BaseColor = Albedo; MetallicSmoothness = URP mask (R metallic 0, A smoothness), same naming as village-houses-b (VL)',
                    status=dict(Exported=True, Imported='未驗', Visually_Verified='未驗', In_game_Verified='未驗'))
        (d / 'model_info.json').write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
        checks = {
            'lod_caps': all(budget[f'LOD{l}']['triangles'] <= budget[f'LOD{l}']['cap'] for l in range(4)),
            'height_in_range': spc['height'][0] <= hi.z <= spc['height'][1],
            'origin_ground': abs(lo.z + .3) < .05,
            'fbx_objects': sorted(rt['objects']) == sorted([aid] + [o.name for o in kids]),
            'fbx_lod0_height_err_m': round(abs(rt[f'{aid}_LOD0']['max'][2] - hi.z), 4) if f'{aid}_LOD0' in rt else None,
            'fbx_wind_colour': all('Wind' in str(rt[o.name]['colour_layers']) or rt[o.name]['colour_layers'] for o in kids[:4] if o.name in rt),
        }
        val = dict(asset=aid, version=VER, built=time.strftime('%Y-%m-%d %H:%M'), blender=bpy.app.version_string, checks=checks, fbx_roundtrip=rt,
                   files={p.name: sha(p) for p in sorted(d.glob('*')) if p.suffix in ('.fbx', '.glb')})
        (d / 'validation.json').write_text(json.dumps(val, ensure_ascii=False, indent=2), encoding='utf-8')
        print('EXPORTED', aid, checks, flush=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out_blend), compress=True)
    print('DONE', sp, round(time.time() - t0, 1), 's', flush=True)


if __name__ == '__main__':
    main()
