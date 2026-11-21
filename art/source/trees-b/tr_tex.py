"""trees-b textures: tileable bark (painted in numpy) and the foliage atlas (rendered from real leaf / needle geometry).

Bark: one 1024 tile per species, seamless in u and v (all noise is periodic), covering TILE_M x TILE_M metres on the trunk.
  <SP>_Bark_BaseColor.png (sRGB), <SP>_Bark_Normal.png (OpenGL, +Y up), <SP>_Bark_MetallicSmoothness.png (R metal 0, A smoothness).
Foliage atlas, 2048:
  top half    cell 0 (left)  dense foliage clump seen from outside, cell 1 (right) open spray for the mass edges and undersides
  bottom half three 682 x 1024 impostor columns, one per variant (A, B, C), for the LOD3 cross cards
  <SP>_Leaves_BaseColor.png (sRGB + alpha, clip at 0.5), <SP>_Leaves_Normal.png, <SP>_Leaves_MetallicSmoothness.png
Colours are written already sRGB-encoded (byte images store what is written).
"""
import bpy, math, tempfile
import numpy as np
from pathlib import Path

TILE_M = 1.2          # one bark tile covers 1.2 m around and 1.2 m along a branch


# ------------------------------------------------------------------ colour helpers
def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def to_lin(c):
    c = np.asarray(c, np.float32); return np.where(c <= .04045, c / 12.92, ((c + .055) / 1.055) ** 2.4)


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ periodic noise
def pnoise(H, W, cy, cx, rng, octaves=3, gain=.5):
    """Periodic value noise in [0, 1], cy x cx cells at the first octave."""
    out = np.zeros((H, W), np.float32); amp = 1.; tot = 0.
    for o in range(octaves):
        gy, gx = cy * 2 ** o, cx * 2 ** o
        g = rng.random((gy, gx)).astype(np.float32)
        y = (np.arange(H) + .5) / H * gy; x = (np.arange(W) + .5) / W * gx
        y0 = np.floor(y).astype(int); x0 = np.floor(x).astype(int); fy = y - y0; fx = x - x0
        fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
        y1 = (y0 + 1) % gy; x1 = (x0 + 1) % gx; y0 %= gy; x0 %= gx
        a = g[y0][:, x0]; b = g[y0][:, x1]; c = g[y1][:, x0]; d = g[y1][:, x1]
        v = (a * (1 - fx) + b * fx) * (1 - fy)[:, None] + (c * (1 - fx) + d * fx) * fy[:, None]
        out += v * amp; tot += amp; amp *= gain
    return out / tot


def worley(H, W, ny, nx, rng, sy=1., sx=1., warp=None, jitter=.85):
    """Periodic Worley: F1, F2 (in 'cell' units scaled by sx / sy) and the index of the nearest cell."""
    pts = np.stack(np.meshgrid(np.arange(ny), np.arange(nx), indexing='ij'), -1).astype(np.float32) + .5 + (rng.random((ny, nx, 2)).astype(np.float32) - .5) * jitter
    PY, PX = np.meshgrid((np.arange(H) + .5) / H * ny, (np.arange(W) + .5) / W * nx, indexing='ij')
    if warp is not None: PY = PY + warp[0]; PX = PX + warp[1]
    f1 = np.full((H, W), 1e9, np.float32); f2 = f1.copy(); idx = np.zeros((H, W), np.int32)
    for j in range(ny):
        for i in range(nx):
            cy, cx = pts[j, i]
            dy = (PY - cy + ny / 2) % ny - ny / 2; dx = (PX - cx + nx / 2) % nx - nx / 2
            d = np.sqrt((dy * sy) ** 2 + (dx * sx) ** 2)
            closer = d < f1
            f2 = np.where(closer, f1, np.minimum(f2, d)); idx = np.where(closer, j * nx + i, idx); f1 = np.where(closer, d, f1)
    return f1, f2, idx


def blur(a, r):
    """Periodic box blur, three passes (close to a Gaussian)."""
    for _ in range(3):
        for ax in (0, 1):
            acc = np.zeros_like(a)
            for k in range(-r, r + 1): acc += np.roll(a, k, ax)
            a = acc / (2 * r + 1)
    return a


def normal_from_height(h, strength):
    """Tangent-space OpenGL normal (+Y = up the texture = +v) from a periodic height field (rows from the bottom)."""
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * .5; dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * .5
    n = np.stack([-dx * strength, -dy * strength, np.ones_like(h)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return n * .5 + .5


def save_png(arr, path, srgb=True):
    """arr (H, W, 3|4), rows from the bottom (Blender order)."""
    H, W = arr.shape[:2]
    if arr.shape[2] == 3: arr = np.concatenate([arr, np.ones((H, W, 1), np.float32)], -1)
    im = bpy.data.images.new(Path(path).stem, W, H, alpha=True, float_buffer=False)
    im.colorspace_settings.name = 'sRGB' if srgb else 'Non-Color'
    im.pixels.foreach_set(np.clip(arr, 0, 1).astype(np.float32).ravel()); im.filepath_raw = str(path); im.file_format = 'PNG'; im.save()
    bpy.data.images.remove(im)
    return Path(path)


def write_ms(path, smooth_map, size):
    ms = np.zeros((size, size, 4), np.float32); ms[..., 3] = smooth_map
    return save_png(ms, path, srgb=False)


# ------------------------------------------------------------------ bark
def bark_texture(tex_dir, prefix, style, size=1024, seed=1):
    """Paint a seamless bark tile. style: dict of colours and plate shape (see BARK_STYLES)."""
    tex_dir.mkdir(parents=True, exist_ok=True)
    out = {k: tex_dir / f'{prefix}_Bark_{k}.png' for k in ('BaseColor', 'Normal', 'MetallicSmoothness')}
    rng = np.random.default_rng(seed); S = size; st = style
    warp = (pnoise(S, S, 3, 5, rng, 3) - .5) * st['warp'], (pnoise(S, S, 3, 5, rng, 3) - .5) * st['warp'] * .6
    f1, f2, idx = worley(S, S, st['ny'], st['nx'], rng, sy=st['sy'], sx=1., warp=warp)
    edge = f2 - f1
    n_cells = st['ny'] * st['nx']
    pr = rng.random(n_cells).astype(np.float32); ptone = pr[idx]
    # fissures: V-shaped, wide and uneven; the long (vertical) ones wider than the cross cracks
    fw = st['fissure'] * (.55 + .9 * pnoise(S, S, 3, 8, rng, 3))
    fiss = 1 - smooth(0., fw, edge)
    vdepth = np.clip(1 - edge / np.maximum(fw, 1e-4), 0, 1) ** 1.5      # 1 at the bottom of the crack
    # flakes: each plate is a stack of overlapping scales; the top lip of a scale catches light, under it a dark seam
    yy = (np.arange(S)[:, None] / S * st['ny'] * st['flakes'] + pr[idx] * 3 + warp[0] * 1.5 + .25 * pnoise(S, S, 4, 12, rng, 2)) % 1.
    lip = smooth(.0, .08, yy) * (1 - smooth(.08, .55, yy))               # bright band just above a seam
    seam = 1 - smooth(.0, .05, yy) * (1 - smooth(.94, 1., yy))           # thin dark seam
    plate_h = .55 + .25 * ptone + .25 * (1 - yy) - .2 * seam + .1 * pnoise(S, S, 12, 16, rng, 2)
    h = plate_h * (1 - fiss) - .6 * vdepth * fiss
    h = blur(h, 1)
    big = pnoise(S, S, 2, 2, rng, 2)
    c_pl = [hexc(c) for c in st['plate']]; t = ptone[..., None]
    plate = c_pl[0] * (1 - t) + c_pl[1] * t
    grey = hexc(st['weather']); wmask = smooth(.5, .78, pnoise(S, S, 2, 4, rng, 3))[..., None] * st['weather_amt']
    plate = plate * (1 - wmask) + grey * wmask
    lit = hexc(st['flake_lit'])
    plate = plate + (lit - plate) * (lip * .45)[..., None]
    plate = plate * (1 - .35 * seam[..., None]) * (.9 + .12 * (1 - yy[..., None]))
    rim = smooth(.0, .5, edge / np.maximum(fw, 1e-4)) * (1 - smooth(.5, 1.6, edge / np.maximum(fw, 1e-4)))
    plate = plate + (lit - plate) * (rim * .25)[..., None]
    fis_c = hexc(st['fissure_c']); deep = hexc(st['deep'])
    fis_col = fis_c * (1 - vdepth[..., None]) + deep * vdepth[..., None]
    col = plate * (1 - fiss[..., None]) + fis_col * fiss[..., None]
    col = col * (.9 + .18 * big[..., None])
    strokes = pnoise(S, S, 2, 20, rng, 2)
    col = col + (lit - col) * (smooth(.64, .82, strokes) * (1 - fiss) * .1)[..., None]
    save_png(col, out['BaseColor'])
    save_png(normal_from_height(h, st['normal']), out['Normal'], srgb=False)
    write_ms(out['MetallicSmoothness'], np.clip(.2 - .12 * fiss + .05 * lip, 0, 1), S)
    return out


BARK_STYLES = {
    # Chinese pine: long reddish-brown plates, deep dark fissures, a few grey weathered patches
    'pine': dict(ny=3, nx=7, sy=.36, warp=.7, fissure=.16, flakes=2.6,
                 plate=('#584A43', '#6C5B4F'), flake_lit='#8E7E70', weather='#6C6660', weather_amt=.55,
                 fissure_c='#3E3532', deep='#29252B', normal=26.),
}


# ------------------------------------------------------------------ foliage atlas (rendered)
def _emit_mat(name, fn):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission')
    nt.links.new(em.outputs[0], out.inputs['Surface']); fn(nt, em)
    return m


def _colour_mat(name, ao_dist, shade_rgb):
    """Colour from the per-corner 'Col' attribute times local AO (blue-violet in the shade, never black)."""
    def fn(nt, em):
        at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = 'Col'
        ao = nt.nodes.new('ShaderNodeAmbientOcclusion'); ao.only_local = True; ao.samples = 16; ao.inputs['Distance'].default_value = ao_dist
        nt.links.new(at.outputs['Color'], ao.inputs['Color'])
        ramp = nt.nodes.new('ShaderNodeValToRGB'); nt.links.new(ao.outputs['AO'], ramp.inputs[0])
        ramp.color_ramp.elements[0].color = (*shade_rgb, 1); ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
        mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1
        nt.links.new(at.outputs['Color'], mul.inputs['A']); nt.links.new(ramp.outputs[0], mul.inputs['B']); nt.links.new(mul.outputs['Result'], em.inputs['Color'])
    return _emit_mat(name, fn)


def _normal_mat(name):
    def fn(nt, em):
        g = nt.nodes.new('ShaderNodeNewGeometry')
        sc = nt.nodes.new('ShaderNodeVectorMath'); sc.operation = 'MULTIPLY_ADD'
        sc.inputs[1].default_value = (.5, .5, .5); sc.inputs[2].default_value = (.5, .5, .5)
        nt.links.new(g.outputs['Normal'], sc.inputs[0]); nt.links.new(sc.outputs[0], em.inputs['Color'])
    return _emit_mat(name, fn)


class Strips:
    """Collects thin tapered strips (needles, leaf blades, twigs) as one mesh with a per-corner colour."""
    def __init__(self): self.v = []; self.f = []; self.c = []

    def strip(self, pts, widths, cols, up=(0, 0, 1), ridge=.25):
        """pts along the strip, widths per point, cols per point (linear rgb). Three verts across, the middle one raised for a ridge normal."""
        up = np.array(up, np.float32); k0 = len(self.v); n = len(pts)
        for i, p in enumerate(pts):
            d = np.array(pts[min(i + 1, n - 1)]) - np.array(pts[max(i - 1, 0)]); d /= (np.linalg.norm(d) + 1e-9)
            s = np.cross(d, up); s /= (np.linalg.norm(s) + 1e-9)
            w = widths[i]
            for x in (-1, 0, 1):
                q = np.array(p) + s * w * x + up * (w * ridge * (1 - abs(x)))
                self.v.append(tuple(q)); self.c.append(cols[i])
        for i in range(n - 1):
            for x in range(2):
                a = k0 + i * 3 + x
                self.f.append((a, a + 1, a + 4, a + 3))

    def blob(self, c, radius, col_in, col_out, rng, n=28, rough=.18, z=0.):
        """A soft filled disc with a ragged rim (the dark body of a foliage clump under its needles / leaves)."""
        k0 = len(self.v); self.v.append((c[0], c[1], z)); self.c.append(col_in)
        ph = rng.uniform(0, 6.3)
        for i in range(n):
            a = i / n * 2 * math.pi
            r = radius * (1 + rough * (math.sin(3 * a + ph) * .5 + rng.uniform(-1, 1) * .5))
            self.v.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a), z)); self.c.append(col_out)
        for i in range(n):
            self.f.append((k0, k0 + 1 + i, k0 + 1 + (i + 1) % n))

    def build(self, name):
        me = bpy.data.meshes.new(name); me.from_pydata(self.v, [], self.f); me.update()
        ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT'); ca.data.foreach_set('color', [x for c in self.c for x in (*c, 1.)])
        for p in me.polygons: p.use_smooth = True
        return bpy.data.objects.new(name, me)


def render_cells(builders, tex_dir, prefix, size=2048, ao_dist=.06, shade='#3A3F55', cell_m=1.0, seed=7):
    """builders: [fn(Strips, rng, cell_m) for cell 0, cell 1]. Renders each top-down into a 1024 cell (colour + raw normal).
    Returns float arrays (rows from the bottom) for the two cells; impostors are added later by finish_atlas."""
    scene = bpy.context.scene; h = size // 2
    keep = dict(engine=scene.render.engine, ft=scene.render.film_transparent, vt=scene.view_settings.view_transform, look=scene.view_settings.look,
                rx=scene.render.resolution_x, ry=scene.render.resolution_y, fs=scene.render.filter_size, cam=scene.camera, ex=scene.view_settings.exposure)
    scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 24; scene.cycles.use_denoising = False
    scene.render.film_transparent = True; scene.render.resolution_x = scene.render.resolution_y = h; scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_mode = 'RGBA'; scene.render.filter_size = .9
    scene.view_settings.exposure = 0
    cam = bpy.data.objects.new('AtlasCam', bpy.data.cameras.new('AtlasCam')); scene.collection.objects.link(cam); scene.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = cell_m; cam.location = (0, 0, 2); cam.data.clip_end = 10
    cm = _colour_mat('Atlas_Colour', ao_dist, tuple(to_lin(hexc(shade)))); nm = _normal_mat('Atlas_Normal')
    tmp = Path(tempfile.gettempdir()) / f'trees_b_{prefix}'; tmp.mkdir(exist_ok=True)
    cells = []
    for k, fn in enumerate(builders):
        rng = np.random.default_rng(seed + k); st = Strips(); fn(st, rng, cell_m)
        o = st.build(f'Cell_{k}'); scene.collection.objects.link(o)
        res = {}
        for pas, m, vt in (('c', cm, 'Standard'), ('n', nm, 'Raw')):
            o.data.materials.clear(); o.data.materials.append(m)
            try: scene.view_settings.view_transform = vt
            except TypeError: scene.view_settings.view_transform = 'Standard'
            scene.view_settings.look = 'None'
            fp = tmp / f'{k}_{pas}.png'; scene.render.filepath = str(fp); bpy.ops.render.render(write_still=True)
            im = bpy.data.images.load(str(fp)); res[pas] = np.array(im.pixels[:], np.float32).reshape(h, h, 4); bpy.data.images.remove(im)
        cells.append(res)
        bpy.data.objects.remove(o)
    bpy.data.objects.remove(cam)
    for m in (cm, nm): bpy.data.materials.remove(m)
    scene.render.engine = keep['engine']; scene.render.film_transparent = keep['ft']; scene.view_settings.view_transform = keep['vt']; scene.view_settings.look = keep['look']
    scene.render.resolution_x, scene.render.resolution_y, scene.render.filter_size, scene.camera = keep['rx'], keep['ry'], keep['fs'], keep['cam']
    scene.view_settings.exposure = keep['ex']
    return cells


def dilate(col, alpha, reach=32, blank=(.1, .15, .12)):
    """Push colours past the alpha edge so lower mips do not pull the background in."""
    a = alpha > .5; rgb = col.copy(); filled = a.copy()
    def shift(x, dy, dx):      # like np.roll but nothing wraps round the atlas edge
        out = np.zeros_like(x)
        ys = slice(max(dy, 0), x.shape[0] + min(dy, 0)); yd = slice(max(-dy, 0), x.shape[0] + min(-dy, 0))
        xs = slice(max(dx, 0), x.shape[1] + min(dx, 0)); xd = slice(max(-dx, 0), x.shape[1] + min(-dx, 0))
        out[ys, xs] = x[yd, xd]; return out
    for _ in range(reach):
        acc = np.zeros_like(rgb); cnt = np.zeros(a.shape, np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sh = shift(filled, dy, dx); acc += shift(rgb, dy, dx) * sh[..., None]; cnt += sh
        grow = (~filled) & (cnt > 0)
        if not grow.any(): break
        rgb[grow] = acc[grow] / cnt[grow][:, None]; filled |= grow
    rgb[~filled] = blank
    return rgb


def assemble_atlas(cells, impostors, tex_dir, prefix, size=2048, smooth_val=.18):
    """cells: two dicts {'c','n'} (1024); impostors: three dicts {'c','n'} (1024 tall x 682 wide). Writes the three PNGs."""
    h = size // 2; w3 = size // 3
    col = np.zeros((size, size, 4), np.float32); nrm = np.zeros((size, size, 4), np.float32); nrm[...] = (.5, .5, 1, 1)
    for k, c in enumerate(cells):            # top half: rows h..size
        c0 = k * h
        col[h:, c0:c0 + h] = c['c']; nrm[h:, c0:c0 + h] = np.where(c['c'][..., 3:4] > .5, c['n'], (.5, .5, 1, 1))
    for k, c in enumerate(impostors):        # bottom half: three columns
        c0 = k * w3; ww = c['c'].shape[1]
        col[:h, c0:c0 + ww] = c['c']; nrm[:h, c0:c0 + ww] = np.where(c['c'][..., 3:4] > .5, c['n'], (.5, .5, 1, 1))
    a = col[..., 3]
    rgb = dilate(col[..., :3], a)
    out = np.concatenate([rgb, (a > .5).astype(np.float32)[..., None]], -1)
    files = {'BaseColor': save_png(out, tex_dir / f'{prefix}_Leaves_BaseColor.png'),
             'Normal': save_png(nrm, tex_dir / f'{prefix}_Leaves_Normal.png', srgb=False)}
    files['MetallicSmoothness'] = write_ms(tex_dir / f'{prefix}_Leaves_MetallicSmoothness.png', np.full((size, size), smooth_val, np.float32), size)
    return files


def dome_normal(alpha, radius=40):
    """Billboard normal: a soft dome over the silhouette so the far card shades like a rounded crown."""
    a = (alpha > .5).astype(np.float32)
    h = blur(np.pad(a, radius, mode='constant'), max(4, radius // 3))[radius:-radius, radius:-radius]
    return normal_from_height(h * 1.0, 18.)
