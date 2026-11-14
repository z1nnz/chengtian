"""trees-v2 core (2026-11-14 work pack 「樹木重做 v2：照天空島世界樹的做法」): solid five-vertex leaves along curling spray paths.

Method (docs/execution/2026-11-14/tree-method/天空島世界樹建模歷程與精修方法.md, section 7):
  silhouette -> S trunk (6-9 control points) -> 3 silhouette limbs, then 6-10 unequal limbs -> secondary and tip branches (three
  thickness levels) -> 12-20 crown anchors of different size in a front and a back layer -> 7-13 curling sprays per anchor, leaves
  placed along each spray's parameter t -> five-vertex solid leaves -> vertex colour from height / inside-outside + occlusion in A ->
  bark last.
No leaf cards, no leaf-mass atlas, no leaves scattered inside balls or ellipsoids.

Leaf mesh: every leaf is 5 vertices (4 outline points + a raised midrib) and 4 triangles, opaque, both faces drawn.
Leaf colour is written twice so any shader can use it:
  vertex colour 'Color' (FBX vertex colour, linear): RGB leaf colour, A canopy occlusion (not transparency);
  UV0 points into a small palette texture <SP>_Leaves_Palette.png (u = tone dark -> light, v = occlusion), so URP Lit and
  YunJing/QingxiFoliageWind show the same colours without a custom shader.
Wind: UV1 'Wind' u = sway weight (trunk 0, limbs low, tips and leaves high), v = phase 0..1.
Units metres, +Z up, front -Y, origin at the trunk's base centre on the ground (z = 0), roots down to z = -0.3.
"""
import bpy, math
import numpy as np
from mathutils import Vector
from tr_tree import Buf, catmull, resample


def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def to_lin(c):
    c = np.asarray(c, np.float32); return np.where(c <= .04045, c / 12.92, ((c + .055) / 1.055) ** 2.4)


# ------------------------------------------------------------------ growth helpers
def grow(rng, p, d, L, r0, r1, droop=0., upturn=.35, wander=.12, step=.3, zmin=-1e9, up_from=.75):
    """A branch that wanders, sags by `droop`, then its last part turns up. Returns points and radii."""
    n = max(3, int(round(L / step))); d = Vector(d).normalized(); pts = [Vector(p)]; rads = [r0]
    for k in range(1, n + 1):
        s = k / n
        lift = -droop * (.25 + .9 * s) if s < up_from else upturn
        d = (d + Vector(rng.normal(0, wander, 3)) + Vector((0, 0, lift * .3))).normalized()
        q = pts[-1] + d * (L / n)
        if q.z < zmin: d = (d + Vector((0, 0, .7))).normalized(); q = pts[-1] + d * (L / n)
        q.z = max(q.z, zmin); pts.append(q); rads.append(r0 + (r1 - r0) * s ** .8)
    return pts, rads


def at(pts, s):
    x = max(0., min(1., s)) * (len(pts) - 1); i = min(int(x), len(pts) - 2); return pts[i].lerp(pts[i + 1], x - i), i


def tangent(pts, s):
    _, i = at(pts, s); return (pts[i + 1] - pts[i]).normalized()


# ------------------------------------------------------------------ buffer with leaf colour and a wind UV
class Buf2(Buf):
    """tr_tree.Buf plus: per-vertex display colour (vc, default white / occlusion 1) and the wind UV (from Buf.col R and G)."""
    def __init__(self, H):
        super().__init__(H); self.vc = {}

    def leaf(self, center, frame, length, width, rib, colour, occl, tone, wind, phase, nrm_bias=None, bias=0., widest=-.06, rib_at=0.):
        """One five-vertex solid leaf. frame = (along, side, normal) unit vectors. Outline base, right, tip, left; centre = midrib
        lifted along the normal. `widest` places the side points along the leaf (-0.5 base .. 0.5 tip): about -0.06 for a broad
        leaf, about +0.25 for a needle fan (narrow at the twig, opening toward the tip). Normals: the leaf's own normal bent toward
        nrm_bias (the crown's outward direction) by `bias`, so thousands of leaves shade as one canopy and do not sparkle far away."""
        a, s, n = frame
        pts = (center - a * length * .5, center + s * width * .5 - n * rib * .4 + a * length * widest,
               center + a * length * .5, center - s * width * .5 - n * rib * .4 + a * length * widest, center + n * rib + a * length * rib_at)
        nn = n if nrm_bias is None else (n * (1 - bias) + nrm_bias * bias).normalized()
        base = len(self.v); u = (tone + .5) / 1.0; uv = (min(.995, max(.005, tone)), min(.98, max(.02, occl)))
        for p in pts:
            self.v.append(p); self.nrm.append(nn); self.col.append(self.wind(wind, phase, p.z)); self.vc[len(self.v) - 1] = (*colour, occl)
        for k in range(4):
            self.f.append((base + 4, base + k, base + (k + 1) % 4)); self.fmat.append(1); self.fuv.append((uv, uv, uv))

    def needle_pair(self, base, d1, d2, length, width, colour, occl, tone, wind, phase, nrm_bias, bias=.55):
        """One pine fascicle: five vertices, two triangles. Two needles leave a shared base (b) along d1 and d2 (a V, open in 3D);
        each needle is one sliver: base, a side point at 45 % of its length (half width out), tip. Normals bent toward nrm_bias."""
        base_i = len(self.v); uv = (min(.995, max(.005, tone)), min(.98, max(.02, occl)))
        pts = [base]
        for d in (d1, d2):
            side = d.cross(nrm_bias); side = side.normalized() if side.length > 1e-4 else d.orthogonal().normalized()
            pts += [base + d * length * .45 + side * width * .5, base + d * length]
        for p in pts:
            n = nrm_bias.normalized()
            self.v.append(p); self.nrm.append(n); self.col.append(self.wind(wind, phase, p.z)); self.vc[len(self.v) - 1] = (*colour, occl)
        for a, b in ((1, 2), (3, 4)):
            self.f.append((base_i, base_i + a, base_i + b)); self.fmat.append(1); self.fuv.append((uv, uv, uv))

    def build(self, name, mats):
        o = super().build(name, mats); me = o.data
        # wind UV from the old colour channels, then the display colour replaces the 'Wind' colour attribute
        w = np.array([c[0] for c in self.col], np.float32); ph = np.array([c[1] for c in self.col], np.float32)
        li = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', li)
        uv1 = me.uv_layers.new(name='Wind'); uv1.data.foreach_set('uv', np.stack([w[li], ph[li]], 1).ravel())
        me.color_attributes.remove(me.color_attributes['Wind'])
        vc = np.ones((len(self.v), 4), np.float32)
        for k, c in self.vc.items(): vc[k] = c
        ca = me.color_attributes.new('Color', 'FLOAT_COLOR', 'POINT'); ca.data.foreach_set('color', vc.ravel())
        me.color_attributes.active_color = ca; me.color_attributes.render_color_index = 0
        me.uv_layers.active_index = 0
        try: me.uv_layers[0].active_render = True
        except Exception: pass
        return o


# ------------------------------------------------------------------ palette texture
def palette_png(path, palette_srgb, occl_lo=.42, size=(256, 64)):
    """u: tone, continuous blend through the palette (dark -> light); v: occlusion (0 -> occl_lo x colour, 1 -> colour). sRGB PNG."""
    W, H = size; pal = np.array(palette_srgb, np.float32); n = len(pal)
    x = np.linspace(0, 1, W) * (n - 1); lo = np.minimum(n - 2, x.astype(int)); f = (x - lo)[:, None]
    row = to_lin(pal[lo]) * (1 - f) + to_lin(pal[lo + 1]) * f                       # blend in linear light
    occ = np.linspace(0, 1, H)[:, None, None]; img = row[None] * (occl_lo + (1 - occl_lo) * occ)
    srgb = np.where(img <= .0031308, img * 12.92, 1.055 * np.power(np.clip(img, 0, 1), 1 / 2.4) - .055)
    im = bpy.data.images.new(path.stem, W, H, alpha=True)
    im.pixels.foreach_set(np.concatenate([srgb, np.ones((H, W, 1))], -1).astype(np.float32).ravel())
    im.filepath_raw = str(path); im.file_format = 'PNG'; im.save(); bpy.data.images.remove(im)
    return path


def palette_colour(palette_srgb, tone, occl, occl_lo=.42):
    """The same colour the palette texture gives at (tone, occl), linear RGB (for the vertex colour)."""
    pal = np.array([hexc(c) if isinstance(c, str) else c for c in palette_srgb], np.float32)
    n = len(pal); x = min(.9999, max(0., tone)) * (n - 1); lo = int(x); f = x - lo
    c = to_lin(pal[lo]) * (1 - f) + to_lin(pal[min(n - 1, lo + 1)]) * f
    return tuple(float(v) for v in c * (occl_lo + (1 - occl_lo) * occl))


# ------------------------------------------------------------------ crown anchors and sprays
class Anchor:
    """A crown anchor: centre c, reach r (m), the outward heading (unit, horizontal), layer 'front' / 'back', its own twist."""
    def __init__(self, c, r, out, layer, twist, phase, idx, flat=.32, lift=.28, sprays=11):
        self.c = Vector(c); self.r = r; self.out = Vector(out); self.layer = layer; self.twist = twist; self.phase = phase; self.idx = idx
        self.flat = flat; self.lift = lift; self.sprays = sprays


def spray_paths(an, rng, spread=1.15, back=.35, droop=.0, curl_gain=1.0, n_pts=7, upturn=.12):
    """7-13 curling spray paths for one anchor, as point lists from near the anchor centre to the tip.
    Headings follow the golden angle (rotated by the anchor's twist) and lean outward (away from the trunk); each spray curls as it
    grows (heading + t x curl), rises in a sine arch and turns its tip up; reach and lift differ per spray, so the anchor never reads
    as a ball and leaves gaps between sprays."""
    out = []; base_h = math.atan2(an.out.y, an.out.x)
    for k in range(an.sprays):
        h = base_h + ((k * 2.399963 + an.twist) % (2 * math.pi) - math.pi) * spread * .5
        # pull headings that point back at the trunk partly outward
        dh = (h - base_h + math.pi) % (2 * math.pi) - math.pi
        if abs(dh) > math.pi * .55: h = base_h + dh * (1 - back)
        reach = an.r * rng.uniform(.52, .9); curl = (1.15 + .35 * math.sin(k * 1.7 + an.idx)) * rng.choice((-1, 1)) * .55 * curl_gain
        # two sub-layers per anchor (every other spray starts lower and reaches a little less), so a layer has thickness
        lower = k % 2 == 1
        z0 = (rng.uniform(-.55, -.25) if lower else rng.uniform(-.1, .3)) * an.r * an.flat; arch = rng.uniform(.6, 1.2) * an.lift * an.r
        if lower: reach *= .85
        start = an.c + Vector((math.cos(h), math.sin(h), 0)) * an.r * rng.uniform(.04, .16) + Vector((0, 0, z0))
        pts = []
        for j in range(n_pts):
            t = j / (n_pts - 1); hh = h + curl * t
            rr = reach * t
            z = arch * math.sin(t * math.pi * .8) + an.r * upturn * t * t - droop * an.r * t * t
            pts.append(start + Vector((math.cos(hh) * rr, math.sin(hh) * rr, z)))
        out.append(pts)
    return out


def envelope_fn(points, axis_fn):
    """Horizontal crown radius as a function of height (90th percentile of the distance from the trunk axis in 0.5 m bands)."""
    if not points: return lambda z: 1.
    z = np.array([p.z for p in points]); d = np.array([math.hypot(p.x - axis_fn(p.z).x, p.y - axis_fn(p.z).y) for p in points])
    bands = np.arange(z.min() - .5, z.max() + 1., .5); env = []
    for b in bands:
        m = np.abs(z - b) < .9
        env.append(np.percentile(d[m], 90) if m.sum() > 3 else 0.)
    env = np.maximum(np.array(env), .4)
    return lambda zz: float(np.interp(zz, bands, env))
