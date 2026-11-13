"""XT01 leaf atlas painter (numpy, no Blender needed): stylised leaf clusters for the 承天 xianxia great tree.

Every cell is one leaf cluster drawn like a hand-painted game texture: chunky almond leaves radiating from a point a little below the
middle, outer leaves first, inner leaves on top with a soft drop shadow, each leaf folded (upper half lighter), a light midrib, a thin
darker rim and a lighter tip. The cluster as a whole is lighter at the top. The cells are GREY on purpose: the leaf shader turns the
grey value into colour with a three-stop ramp (deep / mid / tip) driven by the crown light mask in the vertex colour, so the green
and the gold tree share this one texture and one mesh (only the material colours change).

Atlas 2048 x 2048 (RGBA, sRGB, alpha = leaf coverage, clip 0.5):
  rows 0-1 (top half): 8 small cluster cells, 512 px (LOD0 cards)
  row 2              : 4 big cluster cells, 512 px (LOD1 / LOD2 cards: more, smaller leaves = a whole lobe)
  row 3 (bottom 512) : two impostors of the finished tree (green left, gold right), 1024 x 512 each, coloured (LOD3)
"""
import math
import numpy as np

SIZE = 2048
CELL = 512
SS = 2                      # supersampling: drawn at 1024 px per cell, averaged down to 512


def cell_rect(kind, i):
    """UV rect (u0, v0, u1, v1) of a cell; v up (row 0 is the top of the image)."""
    if kind == 'S': col, row = i % 4, i // 4
    elif kind == 'B': col, row = i % 4, 2
    else: raise KeyError(kind)
    u0 = col * CELL / SIZE; v1 = 1 - row * CELL / SIZE
    return (u0, v1 - CELL / SIZE, u0 + CELL / SIZE, v1)


IMPOSTOR_RECT = {'green': (0., 0., .5, .25), 'gold': (.5, 0., 1., .25)}


def _leaf(val, alp, p, d, L, W, v0, rng, shadow=True):
    """Paint one leaf into the canvas (val, alp: H x W float). p = base point (px), d = unit direction (image coords, y down)."""
    H_, W_ = val.shape
    tip = p + d * L; side = np.array([-d[1], d[0]])
    lo = np.floor(np.minimum(p, tip) - W).astype(int); hi = np.ceil(np.maximum(p, tip) + W).astype(int)
    x0, y0 = max(0, lo[0] - 8), max(0, lo[1] - 8); x1, y1 = min(W_, hi[0] + 9), min(H_, hi[1] + 9)
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)

    def shape(ox, oy):
        rx = xx - p[0] - ox; ry = yy - p[1] - oy
        s = (rx * d[0] + ry * d[1]) / L; t = (rx * side[0] + ry * side[1]) / (W * .5)
        sc = np.clip(s, 0, 1)
        f = np.sin(np.pi * sc ** .9) ** .62 * (s >= 0) * (s <= 1)
        return s, t, f, (np.abs(t) <= f) & (f > 0)
    if shadow:       # soft shadow cast down onto the leaves already painted
        _, _, _, m = shape(3. * SS, 6. * SS)
        val[y0:y1, x0:x1] = np.where(m & (alp[y0:y1, x0:x1] > 0), val[y0:y1, x0:x1] * .74, val[y0:y1, x0:x1])
    s, t, f, m = shape(0, 0)
    if not m.any(): return
    up = -d[1]                                   # image y points down: how much the leaf points up
    lit_side = 1. if side[1] < 0 else -1.        # the half whose side vector points up gets the light
    v = np.full_like(s, v0)
    v += .04 * np.sign(t) * lit_side            # folded along the midrib
    v += .07 * np.clip(s, 0, 1) * (.6 + .4 * up)  # tips catch the light
    v += .05 * (np.abs(t) < .09) * (s > .08) * (s < .85)          # light midrib
    edge = np.abs(t) > f - 1.7 * SS / max(W * .5, 1.)
    v = np.where(edge, v * .82, v)               # thin darker rim
    v += rng.normal(0, .012)
    val[y0:y1, x0:x1] = np.where(m, np.clip(v, 0, 1), val[y0:y1, x0:x1])
    alp[y0:y1, x0:x1] = np.where(m, 1., alp[y0:y1, x0:x1])


def cluster(rng, n, R, Lr, big=False):
    """One cluster cell (CELL x CELL after downsampling) -> (value, alpha)."""
    N = CELL * SS; val = np.zeros((N, N), np.float32); alp = np.zeros((N, N), np.float32)
    c = np.array([N / 2, N / 2 + N * .03]); stem = c + np.array([0, N * (.3 if not big else .2)])
    R = R * N; leaves = []
    # an opaque, shaded core under the leaves: the cluster never shows sky through its middle
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32); ang = np.arctan2(yy - c[1], xx - c[0]); rr = np.hypot(xx - c[0], yy - c[1])
    wob = 1 + .1 * np.sin(3 * ang + rng.uniform(0, 6)) + .07 * np.sin(5 * ang + rng.uniform(0, 6))
    core = rr < R * .56 * wob
    val[core] = .46 - .06 * ((yy[core] - c[1]) / R) + rng.normal(0, .015, int(core.sum())); alp[core] = 1.
    for k in range(n):
        a = rng.uniform(0, 2 * math.pi); r = R * rng.uniform(.03, 1.) ** .6
        q = c + np.array([math.cos(a), math.sin(a) * .92]) * r
        d = q - c + rng.normal(0, R * .18, 2) + np.array([0, -R * .12]); d /= np.linalg.norm(d) + 1e-6
        L = R * rng.uniform(*Lr) * (1.1 - .3 * r / R); W = L * rng.uniform(.5, .6)
        base = q - d * L * .45
        tip = base + d * L                         # keep the whole leaf inside the cell
        lim = N / 2 - 6 * SS
        over = max(abs(tip[0] - N / 2), abs(tip[1] - N / 2)) - lim
        if over > 0: L -= over * 1.05; W = L * .48
        if L < R * .12: continue
        top = -(q[1] - c[1]) / R
        v0 = rng.uniform(.6, .74) + .08 * top - .05 * (r / R) ** 2
        leaves.append((r, base, d, L, W, v0))
    leaves.sort(key=lambda x: -x[0])               # outer first, inner on top
    for r, base, d, L, W, v0 in leaves: _leaf(val, alp, base, d, L, W, v0, rng)
    # the cluster reads as a volume: lighter at the top, a touch darker round the lower rim
    yy = np.linspace(-1, 1, N)[:, None]; val *= (1.04 - .1 * yy)
    val = np.clip(val, 0, 1)
    # downsample
    v = (val * alp).reshape(CELL, SS, CELL, SS).sum((1, 3)); a = alp.reshape(CELL, SS, CELL, SS).sum((1, 3))
    vv = np.where(a > 0, v / np.maximum(a, 1e-6), 0.); a = a / (SS * SS)
    return vv.astype(np.float32), a.astype(np.float32)


def paint_atlas(seed=31):
    """-> rgba (SIZE x SIZE x 4, float, sRGB values, row 0 = top), cell list, mean opaque value of the leaf cells."""
    rng = np.random.default_rng(seed)
    out = np.zeros((SIZE, SIZE, 4), np.float32)
    cells = []
    for i in range(8):
        v, a = cluster(rng, int(rng.integers(40, 48)), .42, (.42, .56))
        u0, v0, u1, v1 = cell_rect('S', i); r0 = int((1 - v1) * SIZE); c0 = int(u0 * SIZE)
        out[r0:r0 + CELL, c0:c0 + CELL, 0] = v; out[r0:r0 + CELL, c0:c0 + CELL, 3] = a; cells.append(('S', i))
    for i in range(4):
        v, a = cluster(rng, int(rng.integers(120, 140)), .44, (.22, .3), big=True)
        u0, v0, u1, v1 = cell_rect('B', i); r0 = int((1 - v1) * SIZE); c0 = int(u0 * SIZE)
        out[r0:r0 + CELL, c0:c0 + CELL, 0] = v; out[r0:r0 + CELL, c0:c0 + CELL, 3] = a; cells.append(('B', i))
    top = out[:SIZE - CELL]
    m = top[..., 3] > .5; mean = float(top[..., 0][m].mean())
    # grey: copy the value to G and B; transparent texels take the mean value (no dark fringe in the mips)
    top[..., 0] = np.where(top[..., 3] > 0, top[..., 0], mean)
    top[..., 1] = top[..., 0]; top[..., 2] = top[..., 0]
    out[:SIZE - CELL] = top
    return out, cells, mean


def place_impostor(out, which, img):
    """img: h x w x 4 (row 0 = top), coloured; dropped into the impostor rect (bottom row), stretched to fill it."""
    u0, v0, u1, v1 = IMPOSTOR_RECT[which]
    r0 = int((1 - v1) * SIZE); r1 = int((1 - v0) * SIZE); c0 = int(u0 * SIZE); c1 = int(u1 * SIZE)
    h, w = r1 - r0, c1 - c0
    ys = (np.arange(h) * img.shape[0] / h).astype(int); xs = (np.arange(w) * img.shape[1] / w).astype(int)
    out[r0:r1, c0:c1] = img[ys][:, xs]


def dilate_rgb(rgb, alpha, reach=24):
    """Bleed opaque colour into transparent texels so mips and bilinear filtering never pull in black."""
    rgb = rgb.copy(); a = alpha > .5; filled = a.copy()
    for _ in range(reach):
        if filled.all(): break
        acc = np.zeros_like(rgb); cnt = np.zeros(a.shape, np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sh = np.zeros_like(filled); src = np.zeros_like(rgb)
            ys = slice(max(dy, 0), a.shape[0] + min(dy, 0)); yd = slice(max(-dy, 0), a.shape[0] + min(-dy, 0))
            xs = slice(max(dx, 0), a.shape[1] + min(dx, 0)); xd = slice(max(-dx, 0), a.shape[1] + min(-dx, 0))
            sh[yd, xd] = filled[ys, xs]; src[yd, xd] = rgb[ys, xs]
            acc += src * sh[..., None]; cnt += sh
        new = (~filled) & (cnt > 0)
        rgb[new] = acc[new] / cnt[new][:, None]; filled |= new
    return rgb
