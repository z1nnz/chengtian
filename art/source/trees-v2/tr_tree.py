"""trees-b geometry: branch tubes with tiling bark UVs, leaf cards around 'puffs' (ellipsoid foliage masses), LOD3 cross cards.

One mesh per LOD, two material slots (0 bark, 1 leaves). Custom normals: tubes radial; cards take the normal of the foliage mass
they belong to (ellipsoid gradient), tilted down for cards deep inside, so each mass shades as one soft rounded volume.
Colour attribute 'Wind' (exported as the FBX vertex colour, linear): R sway weight (trunk 0, limbs low, leaf masses and tips high),
G phase per mass / branch, B height 0..1 over the tree, A 1.
Units metres, +Z up, origin at the trunk's base centre on the ground (z = 0); the root flare goes down to z = -0.3.
"""
import bpy, math
import numpy as np
from mathutils import Vector, Matrix, noise

TILE_M = 1.2
# atlas rectangles (u0, v0, u1, v1)
CELL = {0: (0., .5, .5, 1.), 1: (.5, .5, 1., 1.)}
def IMPOSTOR_RECT(k, size=2048):
    w = (size // 3) / size; return (k * w, 0., k * w + w, .5)


class Branch:
    def __init__(self, pts, rads, level, w0=0., w1=0., phase=0., kind='limb', section=None, cap=False):
        self.pts = [Vector(p) for p in pts]; self.rads = list(rads); self.level = level
        self.w0, self.w1, self.phase, self.kind, self.section, self.cap = w0, w1, phase, kind, section, cap


class Puff:
    def __init__(self, c, r, mass, phase=0., bottom=.65, wind=1.):
        self.c = Vector(c); self.r = Vector(r); self.mass = mass; self.phase = phase; self.bottom = bottom; self.wind = wind

    def radii(self, d):
        return Vector((self.r.x, self.r.y, self.r.z * (self.bottom if d.z < 0 else 1.)))

    def value(self, p):
        q = p - self.c; rz = self.r.z * (self.bottom if q.z < 0 else 1.)
        return (q.x / self.r.x) ** 2 + (q.y / self.r.y) ** 2 + (q.z / rz) ** 2

    def grad(self, p):
        q = p - self.c; rz = self.r.z * (self.bottom if q.z < 0 else 1.)
        g = Vector((q.x / self.r.x ** 2, q.y / self.r.y ** 2, q.z / rz ** 2))
        return g.normalized() if g.length > 1e-8 else Vector((0, 0, 1))

    def area(self):
        a, b, c = self.r.x, self.r.y, self.r.z * (1 + self.bottom) / 2; p = 1.6
        return 4 * math.pi * (((a * b) ** p + (a * c) ** p + (b * c) ** p) / 3) ** (1 / p)


# ------------------------------------------------------------------ curves
def catmull(pts, per=6):
    """Dense Catmull-Rom through the control points (ends clamped)."""
    P = [pts[0]] + list(pts) + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(per):
            t = k / per; t2, t3 = t * t, t * t * t
            out.append(.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(Vector(pts[-1])); return out


def resample(br, step, nmin=3):
    """Rings along the branch every ~step metres (at least 3): positions, radii, arc length."""
    dense = catmull(br.pts, 8)
    rd = np.interp(np.linspace(0, 1, len(dense)), np.linspace(0, 1, len(br.rads)), br.rads)
    seg = [0.] + [(dense[i] - dense[i - 1]).length for i in range(1, len(dense))]
    s = np.cumsum(seg); L = s[-1]
    n = max(nmin, int(math.ceil(L / step)) + 1)
    ss = np.linspace(0, L, n)
    pts = [Vector(np.interp(x, s, [p[k] for p in dense]) for k in range(3)) for x in ss]
    rs = np.interp(ss, s, rd)
    return pts, list(rs), list(ss), L


class Buf:
    def __init__(self, H):
        self.v = []; self.f = []; self.fuv = []; self.fmat = []; self.col = []; self.nrm = []; self.H = H

    def wind(self, w, phase, z):
        return (max(0., min(1., w)), phase % 1., max(0., min(1., z / self.H)), 1.)

    # -------------------------------------------------------------- tubes
    def tube(self, br, sides, step, seed=0., nmin=3):
        pts, rs, ss, L = resample(br, step, nmin)
        n = len(pts)
        T = [(pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized() for i in range(n)]
        N = T[0].orthogonal().normalized(); frames = []
        for i in range(n):
            if i:
                rot = T[i - 1].rotation_difference(T[i]); N = (rot @ N); N = (N - T[i] * N.dot(T[i])).normalized()
            frames.append((N.copy(), T[i].cross(N).normalized()))
        circ = 2 * math.pi * float(np.mean(rs)); k = max(1, round(circ / TILE_M))
        base = len(self.v); cols = sides + 1
        for i in range(n):
            Nn, Bn = frames[i]
            for j in range(cols):
                th = j / sides * 2 * math.pi
                radial = Nn * math.cos(th) + Bn * math.sin(th)
                m = br.section(th, ss[i], pts[i]) if br.section else 1.
                m *= 1 + .05 * noise.noise(Vector((math.cos(th) * 1.3 + seed, math.sin(th) * 1.3, ss[i] * .9)))
                p = pts[i] + radial * rs[i] * m
                if br.kind == 'trunk' and p.z < -.3: p.z = -.3       # the root flare stays inside the 0.3 m burial depth
                self.v.append(p); self.nrm.append(radial)
                t = ss[i] / max(L, 1e-6)
                self.col.append(self.wind(br.w0 + (br.w1 - br.w0) * t, br.phase, p.z))
        tw = getattr(br, 'twist', 0.)       # turns per metre: the bark strips follow a spiralling trunk (u shifts with height)
        for i in range(n - 1):
            o0, o1 = k * tw * ss[i], k * tw * ss[i + 1]
            for j in range(sides):
                a = base + i * cols + j
                self.f.append((a, a + 1, a + cols + 1, a + cols)); self.fmat.append(0)
                u0, u1 = j / sides * k, (j + 1) / sides * k; v0, v1 = ss[i] / TILE_M, ss[i + 1] / TILE_M
                self.fuv.append(((u0 + o0, v0), (u1 + o0, v0), (u1 + o1, v1), (u0 + o1, v1)))
        if br.cap:      # a broken end: a low cone of splinters
            c = base + (n - 1) * cols; tip = pts[-1] + T[-1] * rs[-1] * .6
            ti = len(self.v); self.v.append(tip); self.nrm.append(T[-1]); self.col.append(self.wind(br.w1, br.phase, tip.z))
            for j in range(sides):
                self.f.append((c + j, c + j + 1, ti)); self.fmat.append(0)
                self.fuv.append(((j / sides, 0), ((j + 1) / sides, 0), (.5, .3)))
        return n * cols

    # -------------------------------------------------------------- cards
    def card(self, c, n, size, rect, roll_dir, grid, bend, shade_fn, wind, phase, aspect=1.):
        """A leaf card centred on c facing n; its +v axis points along roll_dir (projected). grid: verts across (2 or 3) x along (2 or 3)."""
        n = n.normalized(); up = roll_dir - n * roll_dir.dot(n)
        if up.length < 1e-4: up = n.orthogonal()
        up.normalize(); side = up.cross(n).normalized()
        gu, gv = grid; base = len(self.v); u0, v0, u1, v1 = rect
        hw, hh = size * .5 * aspect, size * .5
        for j in range(gv):
            y = j / (gv - 1) * 2 - 1
            for i in range(gu):
                x = i / (gu - 1) * 2 - 1
                p = c + side * (x * hw) + up * (y * hh) - n * (bend * size * .5 * (x * x + .6 * y * y))
                self.v.append(p); self.nrm.append(shade_fn(p))
                self.col.append(self.wind(wind, phase, p.z))
        for j in range(gv - 1):
            for i in range(gu - 1):
                a = base + j * gu + i
                self.f.append((a, a + 1, a + gu + 1, a + gu)); self.fmat.append(1)
                uv = lambda ii, jj: (u0 + (u1 - u0) * ii / (gu - 1), v0 + (v1 - v0) * jj / (gv - 1))
                self.fuv.append((uv(i, j), uv(i + 1, j), uv(i + 1, j + 1), uv(i, j + 1)))

    def quad(self, corners, uvs, normal, mat, cols):
        base = len(self.v)
        for p, c in zip(corners, cols): self.v.append(Vector(p)); self.nrm.append(Vector(normal)); self.col.append(c)
        self.f.append((base, base + 1, base + 2, base + 3)); self.fmat.append(mat); self.fuv.append(tuple(uvs))

    def tris(self):
        return sum(len(f) - 2 for f in self.f)

    # -------------------------------------------------------------- object
    def build(self, name, mats):
        me = bpy.data.meshes.new(name)
        me.from_pydata([tuple(v) for v in self.v], [], self.f); me.update()
        uvl = me.uv_layers.new(name='UVMap'); loop_uv = [c for f in self.fuv for uv in f for c in uv]
        uvl.data.foreach_set('uv', loop_uv)
        me.polygons.foreach_set('material_index', self.fmat)
        me.polygons.foreach_set('use_smooth', [True] * len(self.f))
        for m in mats: me.materials.append(m)
        ca = me.color_attributes.new('Wind', 'FLOAT_COLOR', 'POINT'); ca.data.foreach_set('color', [x for c in self.col for x in c])
        me.color_attributes.active_color = ca; me.color_attributes.render_color_index = 0
        me.normals_split_custom_set_from_vertices([tuple(v.normalized()) for v in self.nrm])
        me.validate(clean_customdata=False); me.update()
        return bpy.data.objects.new(name, me)


# ------------------------------------------------------------------ foliage
def sample_cards(puffs, rng, density, size, depth=.35, spray_frac=.18, top_bias=.12, rand_tilt=.26, grid=(3, 3), bend=.18, shade_depth=.55):
    """Card list for all puffs: dicts (c, n, size, cell, roll, shade puff, wind, phase)."""
    out = []
    for pf in puffs:
        cnt = max(3, int(round(density * pf.area() / (size * size))))
        for _ in range(cnt):
            d = Vector(rng.normal(size=3)).normalized()
            rr = pf.radii(d); dep = rng.random() ** 1.6 * depth
            q = pf.c + Vector((d.x * rr.x, d.y * rr.y, d.z * rr.z)) * (1 - dep)
            if any(o is not pf and o.value(q) < .8 for o in puffs): continue     # buried inside a neighbour: not seen
            ns = pf.grad(q)
            cn = (ns * (1 - rand_tilt) + Vector(rng.normal(size=3)).normalized() * rand_tilt + Vector((0, 0, top_bias))).normalized()
            if cn.dot(ns) < .25: cn = (cn + ns).normalized()      # never let a card turn its back on the outside
            under = d.z < -.35
            cell = 1 if (under or rng.random() < spray_frac) else 0
            outward = Vector((q.x - pf.c.x, q.y - pf.c.y, 0)); outward = outward.normalized() if outward.length > 1e-4 else Vector((1, 0, 0))
            roll = outward if cell == 1 else Vector(rng.normal(size=3)).normalized()
            rad = (q - pf.c).length / max(pf.r.x, pf.r.y)
            out.append(dict(c=q, n=cn, size=size * rng.uniform(.85, 1.15), cell=cell, roll=roll, puff=pf, dep=dep / max(depth, 1e-6),
                            wind=pf.wind * (.6 + .4 * min(1., rad)), phase=pf.phase + rng.uniform(0, .08)))
    return out


def shade_for(pf, dep, shade_depth):
    def fn(p):
        g = pf.grad(p)
        return (g + Vector((0, 0, -shade_depth * dep))).normalized()
    return fn


def add_cards(buf, cards, grid, bend, shade_depth=.35, cells=None):
    """cells: optional per-species atlas rectangles {cell: (u0, v0, u1, v1)}; a card may carry 'aspect' (width / height) and its own 'bend'."""
    rects = cells or CELL
    for cd in cards:
        buf.card(cd['c'], cd['n'], cd['size'], rects[cd['cell']], cd['roll'], grid, cd.get('bend', bend), shade_for(cd['puff'], cd['dep'], shade_depth),
                 cd['wind'], cd['phase'], aspect=cd.get('aspect', 1.))


def cross_cards(buf, rect, x0, x1, z0, z1, wind=.25):
    """LOD3: two crossed cards through the trunk axis showing the impostor; normals face up-and-out so the far tree is lit like a crown."""
    for ax in (0, 1):
        def P(a, z): return (a, 0, z) if ax == 0 else (0, a, z)
        u0, v0, u1, v1 = rect
        nrm = (0, -.2, 1) if ax == 0 else (.2, 0, 1)        # mostly up: both cards take the sun the same way, the far crown reads lit from above
        for flip in (False,):
            corners = [P(x0, z0), P(x1, z0), P(x1, z1), P(x0, z1)]
            uvs = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
            cols = [buf.wind(0, 0, z0), buf.wind(0, 0, z0), buf.wind(wind, 0, z1), buf.wind(wind, 0, z1)]
            buf.quad(corners, uvs, nrm, 1, cols)


def collision_prism(name, r, z0, z1, sides=8, centre=(0, 0)):
    v = []; f = []
    for z in (z0, z1):
        for j in range(sides):
            a = j / sides * 2 * math.pi; v.append((centre[0] + r * math.cos(a), centre[1] + r * math.sin(a), z))
    for j in range(sides):
        a, b = j, (j + 1) % sides; f.append((a, b, b + sides, a + sides))
    f.append(tuple(range(sides - 1, -1, -1))); f.append(tuple(range(sides, 2 * sides)))
    me = bpy.data.meshes.new(name); me.from_pydata(v, [], f); me.update()
    return bpy.data.objects.new(name, me)
