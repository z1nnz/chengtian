"""XT01 leaf atlas painter (numpy, no Blender needed): stylised foliage clumps for the 承天 xianxia great tree.

v002 (2026-11-13, the first look was rejected: "全部都不對"). Every cell is one clump of foliage drawn like a hand-painted game texture:
a scalloped outline (a union of sub-circles) filled with hundreds of small rounded leaves, lower leaves first and upper ones lying over
them with a soft shadow, each leaf lighter on its upper edge, no outlines, low contrast; the clump is lighter at the top. Read from a
few metres it is soft fluffy foliage with a lacy rim, not separate drawn leaves. The cells are GREY on purpose: the leaf shader turns
the grey value into colour with a three-stop ramp (deep / mid / tip) driven by the crown light mask in the vertex colour, so the green
and the gold tree share this one texture and one mesh (only the material colours change).

Atlas 2048 x 2048 (RGBA, sRGB, alpha = leaf coverage, clip 0.5):
  rows 0-1 (top half): 8 small clump cells, 512 px (LOD0 cards, a clump about 2 m across: leaves of 10-15 cm)
  row 2              : 4 big clump cells, 512 px (LOD1 / LOD2 cards: a 3-4 m lump of the same leaves)
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


def _leaf(val, alp, p, d, L, W, v0, shadow=.88):
    """Paint one small leaf (val, alp: H x W float). p = base point (px), d = unit direction (image coords, y down).
    Small rounded leaf with no dark outline: the upper edge catches the light, the lower edge and a soft shadow under the leaf are a
    touch darker, so a mass of them reads as soft foliage."""
    H_, W_ = val.shape
    tip = p + d * L; side = np.array([-d[1], d[0]])
    lo = np.floor(np.minimum(p, tip) - W).astype(int); hi = np.ceil(np.maximum(p, tip) + W).astype(int)
    x0, y0 = max(0, lo[0] - 6), max(0, lo[1] - 4); x1, y1 = min(W_, hi[0] + 6), min(H_, hi[1] + 10)
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)

    def shape(ox, oy):
        rx = xx - p[0] - ox; ry = yy - p[1] - oy
        s = (rx * d[0] + ry * d[1]) / L; t = (rx * side[0] + ry * side[1]) / (W * .5)
        sc = np.clip(s, 0, 1)
        f = np.sin(np.pi * sc ** .8) ** .5 * (s >= 0) * (s <= 1)
        return s, (np.abs(t) <= f) & (f > 0)
    if shadow < 1:      # soft shadow cast down onto what is already painted
        _, m = shape(.6 * SS, 2.2 * SS)
        val[y0:y1, x0:x1] = np.where(m & (alp[y0:y1, x0:x1] > 0), val[y0:y1, x0:x1] * shadow, val[y0:y1, x0:x1])
    s, m = shape(0, 0)
    if not m.any(): return
    ry = yy - (p[1] + d[1] * L * .5)
    v = v0 - .05 * np.clip(ry / max(W * .5, 1.), -1, 1) + .03 * np.clip(s, 0, 1)
    val[y0:y1, x0:x1] = np.where(m, np.clip(v, 0, 1), val[y0:y1, x0:x1])
    alp[y0:y1, x0:x1] = np.where(m, 1., alp[y0:y1, x0:x1])


def _blob(rng, N, n_sub, spread, rsub):
    """A scalloped clump outline: a union of sub-circles round the middle. -> list of (centre, radius) in px."""
    c = np.array([N / 2, N / 2 + N * .03]); subs = [(c, N * rsub[1])]
    for k in range(n_sub):
        a = 2 * math.pi * k / n_sub + rng.uniform(-.35, .35)
        d = N * rng.uniform(*spread); q = c + np.array([math.cos(a), math.sin(a) * .85]) * d
        subs.append((q, N * rng.uniform(*rsub)))
    return subs


def cluster(rng, n, leaf, n_sub, spread, rsub):
    """One clump cell (CELL x CELL after downsampling) -> (value, alpha). The clump is a bunch of small sprigs (the sub-circles);
    each sprig is lit on top and shaded underneath, the lower sprigs are drawn first and the upper ones lie over them, so the clump
    has the soft cauliflower layering of stylised game foliage."""
    N = CELL * SS; val = np.zeros((N, N), np.float32); alp = np.zeros((N, N), np.float32)
    subs = _blob(rng, N, n_sub, spread, rsub)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    ymin = min(q[1] - r for q, r in subs); ymax = max(q[1] + r for q, r in subs)
    area = np.array([r * r for _, r in subs]); share = area / area.sum(); lim = N / 2 - 4 * SS
    order = sorted(range(len(subs)), key=lambda k: -subs[k][1] - rng.normal(0, N * .02))       # lowest sprig first
    for k in order:
        q, r = subs[k]
        H = 1 - (q[1] - ymin) / (ymax - ymin)          # 1 = the top of the clump
        # the sprig's shaded heart (seen between its leaves): darker underneath
        d2 = (xx - q[0]) ** 2 + (yy - q[1]) ** 2; core = d2 < (r * .58) ** 2
        lh = np.clip(-(yy[core] - q[1]) / r, -1, 1)
        val[core] = .44 + .08 * lh + .06 * H; alp[core] = 1.
        leaves = []; tries = 0; nk = int(n * share[k]) + 8
        while len(leaves) < nk and tries < nk * 20:
            tries += 1
            a = rng.uniform(0, 2 * math.pi); rr = r * rng.uniform(.05, 1.) ** .5
            pt = q + np.array([math.cos(a), math.sin(a)]) * rr
            out = (pt - q) / (np.linalg.norm(pt - q) + 1e-6)
            d = out * (.6 + .6 * rr / r) + rng.normal(0, .45, 2) + np.array([0, -.25]); d /= np.linalg.norm(d) + 1e-6
            L = N * rng.uniform(*leaf); W = L * rng.uniform(.56, .68)
            base = pt - d * L * .35; tip = base + d * L
            if max(abs(tip[0] - N / 2), abs(tip[1] - N / 2), abs(base[0] - N / 2), abs(base[1] - N / 2)) > lim: continue
            lh = -(pt[1] - q[1]) / r                            # -1 under the sprig .. 1 on top
            v0 = .6 + .13 * lh + .05 * H + .03 * (rr / r) + rng.normal(0, .02)
            leaves.append((pt[1] + rng.normal(0, r * .15), base, d, L, W, v0))
        leaves.sort(key=lambda x: -x[0])
        for _, base, d, L, W, v0 in leaves: _leaf(val, alp, base, d, L, W, v0)
    gy = np.linspace(-1, 1, N)[:, None]; val *= (1.03 - .06 * gy)
    val = np.clip(val, 0, 1)
    v = (val * alp).reshape(CELL, SS, CELL, SS).sum((1, 3)); a = alp.reshape(CELL, SS, CELL, SS).sum((1, 3))
    vv = np.where(a > 0, v / np.maximum(a, 1e-6), 0.); a = a / (SS * SS)
    return vv.astype(np.float32), a.astype(np.float32)


def paint_atlas(seed=31):
    """-> rgba (SIZE x SIZE x 4, float, sRGB values, row 0 = top), cell list, mean opaque value of the leaf cells."""
    rng = np.random.default_rng(seed)
    out = np.zeros((SIZE, SIZE, 4), np.float32)
    cells = []
    for i in range(8):
        v, a = cluster(rng, int(rng.integers(720, 780)), (.046, .064), int(rng.integers(9, 13)), (.1, .3), (.1, .15))
        u0, v0, u1, v1 = cell_rect('S', i); r0 = int((1 - v1) * SIZE); c0 = int(u0 * SIZE)
        out[r0:r0 + CELL, c0:c0 + CELL, 0] = v; out[r0:r0 + CELL, c0:c0 + CELL, 3] = a; cells.append(('S', i))
    for i in range(4):
        v, a = cluster(rng, int(rng.integers(1500, 1600)), (.029, .04), int(rng.integers(12, 16)), (.1, .32), (.08, .12))
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
