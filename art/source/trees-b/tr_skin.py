"""trees-b fused wood and cloud-mass foliage (the method of art/source/golden-spirit-tree/v001, 2026-11-12, cut to the game budget).

Wood: the species' Branch list becomes one skeleton graph (each branch hooks onto the nearest vertex of its parent), Blender's Skin
modifier wraps it and Subdivision smooths it, so every fork grows out of its parent instead of a cylinder pushed through it. The
trunk's own cross-section function (root lobes, ridges, burls) is applied afterwards as a radial scale, then Decimate cuts the wood
to the LOD budget. UVs, wind colour and normals come from the nearest skeleton segment, so they stay right after decimation.

Foliage masses: farthest-point sampling over the leaf-carrying points gives a few readable masses; each is a lumpy union of three
offset ellipsoids. Cards are kept only inside a mass (the rim thins out at random), so sky and limbs show between the masses.
"""
import bpy, bmesh, math
import numpy as np
from mathutils import Vector
from tr_tree import resample, TILE_M


# ------------------------------------------------------------------ wood
def _graph(branches, levels):
    """Skeleton vertices / edges / radii from Branch objects. Returns verts, radii, edges, seg (per edge: branch index, s0, s1)."""
    V = []; Rr = []; E = []; owner = []; S = []; lvl = []; roots = [0]
    for bi, br in enumerate(branches):
        if br.kind == 'trunk': lv = 0
        elif br.kind == 'stub': lv = 3
        else: lv = br.level
        if lv not in levels and br.kind != 'trunk': continue
        step = max(.16, 1.15 * float(np.mean(br.rads))) if br.kind == 'trunk' else max(.12, 1.6 * float(np.mean(br.rads)))
        pts, rs, ss, L = resample(br, step)
        ids = []
        k0 = 0
        if br.kind != 'trunk' and V:
            # hook onto the nearest vertex of a lower-level branch, measured from the first point outside the parent
            cand = [i for i in range(len(V)) if lvl[i] < max(1, lv) or (br.kind == 'stub' and lvl[i] == 0)]
            if not cand: cand = list(range(len(V)))
            P0 = np.array(pts[0]); C = np.array([V[i] for i in cand]); j = cand[int(np.argmin(((C - P0) ** 2).sum(1)))]
            if Rr[j] < 1.9 * rs[0]:          # a true fork (similar thickness): fuse into the parent vertex
                ids.append(j); k0 = 1
                while k0 < len(pts) - 1 and (Vector(pts[k0]) - Vector(V[j])).length < Rr[j] * .9: k0 += 1
            else:                             # a side limb on a much thicker parent: its own skin, starting inside the parent
                roots.append(len(V))
        for k in range(k0, len(pts)):
            V.append(tuple(pts[k])); Rr.append(max(.006, float(rs[k]))); owner.append(bi); S.append(ss[k] / max(L, 1e-6)); lvl.append(lv)
            if ids: E.append((ids[-1], len(V) - 1))
            ids.append(len(V) - 1)
    _graph.roots = roots
    return np.array(V), np.array(Rr), E, np.array(owner), np.array(S)


def _skin(V, Rr, E, subdiv):
    me = bpy.data.meshes.new('skel'); me.from_pydata([tuple(v) for v in V], E, [])
    ob = bpy.data.objects.new('skel', me); bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_add(type='SKIN')
    sk = ob.modifiers[0]; sk.branch_smoothing = .35; sk.use_smooth_shade = True
    sv = me.skin_vertices[0].data
    rt = set(getattr(_graph, 'roots', [0]))
    for k in range(len(V)): sv[k].radius = (Rr[k], Rr[k]); sv[k].use_root = (k in rt)
    if subdiv:
        m = ob.modifiers.new('Sub', 'SUBSURF'); m.levels = subdiv; m.render_levels = subdiv
    dg = bpy.context.evaluated_depsgraph_get(); out = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob); bpy.data.meshes.remove(me)
    return out


def _nearest(co, A, B, rA, rB):
    AB = B - A; L2 = (AB ** 2).sum(1) + 1e-9; seg = np.zeros(len(co), np.int64); tt = np.zeros(len(co))
    for s in range(0, len(co), 1200):
        P = co[s:s + 1200, None, :]; t = np.clip(((P - A[None]) * AB[None]).sum(2) / L2[None], 0, 1); C = A[None] + AB[None] * t[..., None]
        d = np.linalg.norm(P - C, axis=2) / (rA[None] + (rB - rA)[None] * t)
        k = d.argmin(1); seg[s:s + 1200] = k; tt[s:s + 1200] = t[np.arange(len(k)), k]
    return seg, tt


def _frame(ax):
    ref = np.where(np.abs(ax[:, 2:3]) < .9, np.array([[0, 0, 1.]]), np.array([[1., 0, 0]]))
    e1 = np.cross(ref, ax); e1 /= np.linalg.norm(e1, axis=1)[:, None] + 1e-9; e2 = np.cross(ax, e1)
    return e1, e2


def skin_wood(buf, branches, levels, subdiv, target_tris, z_floor=-.3, trunk_share=.4):
    """Append fused wood (material 0) for the branches whose level is in `levels` to buf; returns (triangles, first vertex, last vertex)."""
    V, Rr, E, owner, S = _graph(branches, levels)
    me = _skin(V, Rr, E, subdiv)
    Ei = np.array(E); A = V[Ei[:, 0]]; B = V[Ei[:, 1]]; rA = Rr[Ei[:, 0]]; rB = Rr[Ei[:, 1]]; ob_ = owner[Ei[:, 1]]; sA = S[Ei[:, 0]]; sB = S[Ei[:, 1]]
    # an edge that hooks onto a parent belongs to the child; its s at the parent end is 0
    sA = np.where(owner[Ei[:, 0]] != ob_, 0., sA)
    nv = len(me.vertices); co = np.zeros(nv * 3, np.float32); me.vertices.foreach_get('co', co); co = co.reshape(nv, 3).astype(np.float64)
    co[:, 2] = np.maximum(co[:, 2], z_floor)          # the Skin end cap below the burial depth would otherwise be blown out by the root flare
    # trunk cross-section (root lobes, ridges, burls) as a radial scale about the trunk axis
    seg, tt = _nearest(co, A, B, rA, rB)
    ax = (B - A)[seg]; ax /= np.linalg.norm(ax, axis=1)[:, None] + 1e-9; C = A[seg] + (B - A)[seg] * tt[:, None]
    rel = co - C; rel -= ax * (rel * ax).sum(1)[:, None]
    for bi, br in enumerate(branches):
        if br.kind != 'trunk' or not br.section: continue
        m = ob_[seg] == bi
        if not m.any(): continue
        e1 = np.tile(np.array([[1., 0, 0]]), (m.sum(), 1)); e2 = np.tile(np.array([[0, 1., 0]]), (m.sum(), 1))
        th = np.arctan2((rel[m] * e2).sum(1), (rel[m] * e1).sum(1))
        f = np.array([br.section(float(a), 0., Vector(p)) for a, p in zip(th, co[m])])
        co[m] = C[m] + rel[m] * f[:, None]
    co[:, 2] = np.maximum(co[:, 2], z_floor)
    me.vertices.foreach_set('co', co.astype(np.float32).ravel()); me.update()
    # decimate to the budget. 2026-11-12 ("樹幹像塑膠"): the trunk is decimated on its own and keeps `trunk_share` of the budget,
    # so its bark plates and outline survive instead of the triangles going to hundreds of thin twigs (faceted trunk outline).
    is_trunk_b = np.array([br.kind == 'trunk' for br in branches])
    vt = is_trunk_b[ob_[seg]]
    def _dec(mesh, target):
        tri = sum(len(p.vertices) - 2 for p in mesh.polygons)
        o = bpy.data.objects.new('wood_tmp', mesh); bpy.context.scene.collection.objects.link(o)
        if tri > target > 0:
            d = o.modifiers.new('Dec', 'DECIMATE'); d.ratio = target / tri; d.use_collapse_triangulate = True
            dg = bpy.context.evaluated_depsgraph_get(); out = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        else:
            out = mesh.copy()
        bpy.data.objects.remove(o); return out
    def _part(keep_trunk):
        m2 = me.copy(); bm_ = bmesh.new(); bm_.from_mesh(m2); bm_.verts.ensure_lookup_table()
        drop = [f for f in bm_.faces if (np.mean([vt[v.index] for v in f.verts]) >= .5) != keep_trunk]
        bmesh.ops.delete(bm_, geom=drop, context='FACES_ONLY')
        lv = [v for v in bm_.verts if not v.link_faces]
        if lv: bmesh.ops.delete(bm_, geom=lv, context='VERTS')
        bm_.to_mesh(m2); bm_.free(); return m2
    mt, mb = _part(True), _part(False)
    tt_ = sum(len(p.vertices) - 2 for p in mt.polygons); t_trunk = min(tt_, int(target_tris * trunk_share))
    dt, db = _dec(mt, t_trunk), _dec(mb, target_tris - t_trunk)
    for m_ in (mt, mb, me): bpy.data.meshes.remove(m_)
    bm = bmesh.new(); bm.from_mesh(dt); bm.from_mesh(db); me2 = db; bpy.data.meshes.remove(dt)            # zero-area triangles from Decimate: Unity drops them on import, so drop them here
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=2e-4)
    bad = [f for f in bm.faces if f.calc_area() < 1e-6 or len({v.index for v in f.verts}) < 3]
    if bad: bmesh.ops.delete(bm, geom=bad, context='FACES_ONLY')
    loose = [v for v in bm.verts if not v.link_faces]
    if loose: bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.to_mesh(me2); bm.free(); me2.update()
    nv = len(me2.vertices); co = np.zeros(nv * 3, np.float32); me2.vertices.foreach_get('co', co); co = co.reshape(nv, 3).astype(np.float64)
    nr = np.zeros(nv * 3, np.float32); me2.vertices.foreach_get('normal', nr); nr = nr.reshape(nv, 3)
    seg, tt = _nearest(co, A, B, rA, rB)
    # a limb's own Skin island starts inside the trunk; where it comes out, some of its vertices lie nearer the trunk axis and
    # took the trunk's UVs, so faces there mixed two mappings (stretched bark at limb roots). Every vertex of a non-trunk island
    # is mapped from the nearest non-trunk segment instead.
    ev = np.zeros(len(me2.edges) * 2, np.int32); me2.edges.foreach_get('vertices', ev); ev = ev.reshape(-1, 2)
    lab = np.arange(nv)
    while True:
        a = np.minimum(lab[ev[:, 0]], lab[ev[:, 1]]); new = lab.copy(); np.minimum.at(new, ev[:, 0], a); np.minimum.at(new, ev[:, 1], a)
        new = new[new]
        if (new == lab).all(): break
        lab = new
    vt2 = is_trunk_b[ob_[seg]]
    comp_trunk = np.zeros(nv, bool)
    for L_ in np.unique(lab):
        m = lab == L_; comp_trunk[m] = vt2[m].mean() >= .5
    fix = (~comp_trunk) & vt2
    if fix.any():
        nt_e = np.nonzero(~is_trunk_b[ob_])[0]
        s2, t2 = _nearest(co[fix], A[nt_e], B[nt_e], rA[nt_e], rB[nt_e]); seg[fix] = nt_e[s2]; tt[fix] = t2
    ax = (B - A)[seg]; ax /= np.linalg.norm(ax, axis=1)[:, None] + 1e-9; C = A[seg] + (B - A)[seg] * tt[:, None]
    rel = co - C; rel -= ax * (rel * ax).sum(1)[:, None]; e1, e2 = _frame(ax)
    ang = np.arctan2((rel * e2).sum(1), (rel * e1).sum(1))
    bi = ob_[seg]; s = sA[seg] + (sB - sA)[seg] * tt
    Lb = np.array([sum((br.pts[k + 1] - br.pts[k]).length for k in range(len(br.pts) - 1)) * 1.03 for br in branches])
    kk = np.array([max(1, round(2 * math.pi * float(np.mean(br.rads)) / TILE_M)) for br in branches])
    tw = np.array([getattr(br, 'twist', 0.) for br in branches])
    # optional per-branch bark scale (TR01 trunk, 2026-11-13 "樹幹還是很塑膠"): `uv_k` tiles around, `uv_tile` metres per tile along.
    # One tile round a thick pine base stretched the bark 3x sideways into soft horizontal waves.
    for j, br in enumerate(branches):
        if getattr(br, 'uv_k', None): kk[j] = br.uv_k
    arc = s * Lb[bi]
    u = (ang / (2 * math.pi) + .5) * kk[bi] + kk[bi] * tw[bi] * arc; v = arc / TILE_M
    # root flare: the surface there runs outward more than up, so v (height along the axis) alone smears the bark into stripes;
    # take the outward run as distance too (v goes down as the flare spreads out)
    # trunk: map by world height and the angle round the trunk axis at that height (projection onto the nearest skeleton segment
    # collapses at the flare and the end cap: measured stretch up to 130x there). The outward run of the flare counts as length.
    for tb in np.nonzero(is_trunk_b)[0]:
        m = bi == tb
        if not m.any(): continue
        br = branches[int(tb)]; tz = np.array([p.z for p in br.pts]); tx = np.array([p.x for p in br.pts]); ty = np.array([p.y for p in br.pts])
        z = co[m, 2]; dx = co[m, 0] - np.interp(z, tz, tx); dy = co[m, 1] - np.interp(z, tz, ty)
        rr = np.interp(z, tz, np.array(br.rads)); hd = np.hypot(dx, dy); a = np.arctan2(dy, dx)
        k = kk[int(tb)]; zz = z - tz[0]; T = getattr(br, 'uv_tile', TILE_M)
        u[m] = (a / (2 * math.pi) + .5) * k + k * tw[int(tb)] * zz
        v[m] = (zz - np.maximum(0., hd - 1.12 * rr)) / T
    w0 = np.array([br.w0 for br in branches]); w1 = np.array([br.w1 for br in branches]); ph = np.array([br.phase for br in branches])
    wind = w0[bi] + (w1 - w0)[bi] * s
    base = len(buf.v)
    for p, n, w, phs in zip(co, nr, wind, ph[bi]):
        buf.v.append(Vector(p)); buf.nrm.append(Vector(n)); buf.col.append(buf.wind(float(w), float(phs), float(p[2])))
    nl = len(me2.loops); li = np.zeros(nl, np.int32); me2.loops.foreach_get('vertex_index', li)
    for poly in me2.polygons:
        vids = [li[l] for l in range(poly.loop_start, poly.loop_start + poly.loop_total)]
        uu = np.array([u[i] for i in vids]); k = kk[bi[vids[0]]]
        if uu.max() - uu.min() > k * .5: uu = np.where(uu < uu.max() - k * .5, uu + k, uu)
        buf.f.append(tuple(base + int(i) for i in vids)); buf.fmat.append(0)
        buf.fuv.append(tuple((float(a), float(v[i])) for a, i in zip(uu, vids)))
    t = sum(len(p.vertices) - 2 for p in me2.polygons); bpy.data.meshes.remove(me2)
    return t, base, len(buf.v)


# ------------------------------------------------------------------ cloud masses
class Masses:
    """count masses over the points P (N x 3); each a lumpy union of three ellipsoids (radius r, height squash zs)."""
    def __init__(self, P, count, r_rng, zs_rng, seed, zw=2.2, lobe_z=(-.3, .25), gap=None, centres=None, radii=None, lobe_off=1.):
        mr = np.random.default_rng(seed)
        if centres is not None:            # given centres (e.g. one mass on the end of every main limb) and radii
            cs = list(centres); count = len(cs)
        else:
            cs = [P[int(mr.integers(len(P)))]]
            for _ in range(count - 1):
                d2 = np.min([((P - c) ** 2 * np.array([1, 1, zw])).sum(1) for c in cs], 0); cs.append(P[int(d2.argmax())])
        self.c = np.array(cs) + mr.normal(0, .12, (count, 3)); self.zs = mr.uniform(*zs_rng, count)
        self.r = np.array(radii, float) * mr.uniform(.9, 1.1, count) if radii is not None else mr.uniform(*r_rng, count)
        if gap:   # radius at most gap x the distance to the nearest other mass, so sky shows between masses
            dm = np.sqrt(((self.c[:, None] - self.c[None]) ** 2).sum(-1)); np.fill_diagonal(dm, 1e9); self.r = np.maximum(.65, np.minimum(self.r, gap * dm.min(1)))
        # three lobes per mass: the main one and two smaller ones pushed off to the sides, so no mass is a clean ball
        lob = []
        for k in range(count):
            a = mr.uniform(0, 6.28)
            for j, (f, off) in enumerate(((1., 0.), (.68, .55 * lobe_off), (.6, .6 * lobe_off), (.5, .7 * lobe_off))):
                aa = a + j * 2.2 + mr.normal(0, .3)
                lob.append((k, self.c[k] + np.array([math.cos(aa), math.sin(aa), mr.uniform(*lobe_z)]) * off * self.r[k], self.r[k] * f, self.zs[k]))
        self.lobes = lob
        self.lc = np.array([l[1] for l in lob]); self.lr = np.array([l[2] for l in lob]); self.lz = np.array([l[3] for l in lob]); self.lk = np.array([l[0] for l in lob])

    def test(self, q):
        """(normalised distance to the nearest lobe, mass index, relative position in that lobe)"""
        rel = (q[None] - self.lc) / self.lr[:, None]; rel[:, 2] /= self.lz; d = np.linalg.norm(rel, axis=1); j = int(d.argmin())
        return float(d[j]), int(self.lk[j]), rel[j]
