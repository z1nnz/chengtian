"""XT01 leaf atlas painter (numpy, no Blender needed): hand-painted leafy twigs for the 承天 xianxia great tree.

v003 atlas (tree v004, 2026-11-13). The clump atlases of tree v002 / v003 were rejected ("還是一坨", "還是像一團一團的"): a card that
is a whole clump of foliage makes the crown a pile of clumps. Now every cell is ONE TWIG: a thin stem with a handful of big, clear
ovate leaves (the team's life tree, z1nnz/elder-tree-esg, is the benchmark: thousands of separate leaves along real branches). Each
leaf is folded along its midrib (a lit half and a shaded half, a light midrib line, a slightly darker rim), leaves higher up the twig
lie over the lower ones with a soft shadow, the newest leaves at the tip are a touch lighter. Original drawing.
The cells are GREY on purpose: the leaf shader turns the grey value into colour with a three-stop ramp (deep / mid / tip) driven by
the crown light mask in the vertex colour, so the green and the gold tree share this one texture and one mesh.

Atlas 2048 x 2048 (RGBA, sRGB, alpha = leaf coverage, clip 0.5):
  rows 0-1 (top half): 8 twig cells, 512 px (LOD0 cards about 1 m long: 5-9 leaves of 25-35 cm on one twiglet)
  row 2              : 4 branchlet cells, 512 px (LOD1 / LOD2 cards: a small branch with four or five such twigs)
  row 3 (bottom 512) : two impostors of the finished tree (green left, gold right), 1024 x 512 each, coloured (LOD3)
In a cell the twig starts at the bottom middle and grows up (v up): the cards are placed base first.
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


def _leaf(val, alp, base, d, L, W, v0, shadow=.84):
    """One ovate leaf (val, alp: H x W float). base = petiole point (px), d = unit direction (image coords, y down), L length, W
    full width. Folded along the midrib: the half facing up in the image is lit, the other shaded; light midrib; darker rim."""
    H_, W_ = val.shape
    d = d / (np.linalg.norm(d) + 1e-9); side = np.array([-d[1], d[0]])
    tip = base + d * L
    lo = np.floor(np.minimum(base, tip) - W).astype(int); hi = np.ceil(np.maximum(base, tip) + W).astype(int)
    x0, y0 = max(0, lo[0] - 8), max(0, lo[1] - 8); x1, y1 = min(W_, hi[0] + 10), min(H_, hi[1] + 14)
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    lit_side = 1. if side[1] < 0 else -1.          # the side whose edge points up the image catches the light

    def shape(ox, oy):
        rx = xx - base[0] - ox; ry = yy - base[1] - oy
        s = (rx * d[0] + ry * d[1]) / L; t = (rx * side[0] + ry * side[1]) / (W * .5)
        sc = np.clip(s, 0, 1)
        f = np.sin(np.pi * sc ** .72) ** .8 * (1 - .12 * sc) * (s >= 0) * (s <= 1)
        return s, t, f, (np.abs(t) <= f) & (f > 0)
    if shadow < 1:
        _, _, _, m = shape(W * .05, W * .12)
        reg = alp[y0:y1, x0:x1] > 0
        val[y0:y1, x0:x1] = np.where(m & reg, val[y0:y1, x0:x1] * shadow, val[y0:y1, x0:x1])
    s, t, f, m = shape(0, 0)
    if not m.any(): return
    tl = t * lit_side
    v = v0 + .07 * np.tanh(tl * 5.) + .04 * np.clip(s, 0, 1)               # lit / shaded half, lighter towards the tip
    v = np.where(np.abs(t) < .045 + .03 * (1 - s), v + .07, v)             # midrib
    rimw = np.clip((np.abs(t) - (f - .16)) / .16, 0, 1)
    v = v * (1 - .1 * rimw)                                               # soft darker rim
    val[y0:y1, x0:x1] = np.where(m, np.clip(v, 0, 1), val[y0:y1, x0:x1])
    alp[y0:y1, x0:x1] = np.where(m, 1., alp[y0:y1, x0:x1])


def _stem(val, alp, pts, w0, w1, v=.28):
    """A tapering twig through pts (px), painted as overlapping discs."""
    H_, W_ = val.shape; n = len(pts)
    for i in range(n - 1):
        a, b = pts[i], pts[i + 1]; seg = np.linalg.norm(b - a); k = max(1, int(seg / 1.5))
        for j in range(k):
            p = a + (b - a) * j / k; w = w0 + (w1 - w0) * (i + j / k) / (n - 1)
            x0, x1 = int(max(0, p[0] - w - 1)), int(min(W_, p[0] + w + 2)); y0, y1 = int(max(0, p[1] - w - 1)), int(min(H_, p[1] + w + 2))
            if x1 <= x0 or y1 <= y0: continue
            yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            m = (xx - p[0]) ** 2 + (yy - p[1]) ** 2 <= w * w
            val[y0:y1, x0:x1] = np.where(m, v + .06 * ((xx - p[0]) < 0), val[y0:y1, x0:x1])
            alp[y0:y1, x0:x1] = np.where(m, 1., alp[y0:y1, x0:x1])


def _curve(p0, p1, bend, n=40):
    """Quadratic curve from p0 to p1 bowed sideways by bend (px) -> n x 2."""
    d = p1 - p0; s = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9); c = (p0 + p1) / 2 + s * bend
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * c + t * t * p1


def _rot(v, a):
    c, s = math.cos(a), math.sin(a); return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]])


def _twig_leaves(rng, pts, nl, L0, start=.2, spread=(1.0, .55), lim=None, N=None):
    """Leaves along a twig polyline: alternating sides, angle opening from spread[0] at the base to spread[1] near the tip, a
    terminal leaf. -> list of (order key, base, dir, L, W, value)."""
    out = []; n = len(pts)
    for i in range(nl):
        s = start + (.93 - start) * i / max(1, nl - 1)
        k = min(n - 2, int(s * (n - 1))); p = pts[k]; tg = pts[k + 1] - pts[k]; tg /= np.linalg.norm(tg) + 1e-9
        sgn = 1 if i % 2 == 0 else -1
        ang = (spread[0] + (spread[1] - spread[0]) * s) * sgn + rng.normal(0, .12)
        d = _rot(tg, ang); L = L0 * (1.05 - .25 * s) * rng.uniform(.88, 1.1)
        v0 = .6 + .06 * s + rng.normal(0, .025)
        out.append((s + rng.normal(0, .02), p.copy(), d, L, L * rng.uniform(.44, .52), v0))
    tg = pts[-1] - pts[-3]; tg /= np.linalg.norm(tg) + 1e-9
    out.append((1.1, pts[-1] - tg * L0 * .08, _rot(tg, rng.normal(0, .1)), L0 * .8, L0 * .38, .67))
    if lim is not None:        # shorten any leaf that would leave the cell
        fixed = []
        for key, b, d, L, W, v0 in out:
            for _ in range(12):
                tip = b + d * L
                if max(abs(tip[0] - N / 2), abs(tip[1] - N / 2)) <= lim and min(tip[1], b[1]) > N / 2 - lim: break
                L *= .9; W *= .9
            fixed.append((key, b, d, L, W, v0))
        out = fixed
    return out


def twig_cell(rng, nl, leaf, bend):
    """One LOD0 cell: a single twiglet, base at the bottom middle, 5-9 leaves. -> (value, alpha) CELL x CELL."""
    N = CELL * SS; val = np.zeros((N, N), np.float32); alp = np.zeros((N, N), np.float32); lim = N / 2 - 6 * SS
    p0 = np.array([N * .5 + rng.uniform(-.03, .03) * N, N * .985]); p1 = np.array([N * .5 + rng.uniform(-.1, .1) * N, N * .3])
    pts = _curve(p0, p1, bend * N)
    leaves = _twig_leaves(rng, pts, nl, N * leaf, lim=lim, N=N)
    back = [l for l in leaves if rng.random() < .3 and l[0] < 1]; front = [l for l in leaves if not any(l is b for b in back)]
    for key, b, d, L, W, v0 in sorted(back, key=lambda x: x[0]): _leaf(val, alp, b, d, L, W, v0 - .08)
    _stem(val, alp, pts, 3.2 * SS, 1.3 * SS)
    for key, b, d, L, W, v0 in sorted(front, key=lambda x: x[0]): _leaf(val, alp, b, d, L, W, v0)
    return _finish(val, alp)


def branchlet_cell(rng, n_twigs, leaf):
    """One LOD1/LOD2 cell: a small branch with several leafy twigs fanning out of it."""
    N = CELL * SS; val = np.zeros((N, N), np.float32); alp = np.zeros((N, N), np.float32); lim = N / 2 - 6 * SS
    p0 = np.array([N * .5, N * .99]); p1 = np.array([N * .5 + rng.uniform(-.08, .08) * N, N * .2])
    main = _curve(p0, p1, rng.uniform(-.06, .06) * N)
    groups = []
    for j in range(n_twigs):
        s = .3 + .55 * j / max(1, n_twigs - 1); k = int(s * (len(main) - 1)); b = main[k]
        tg = main[min(len(main) - 1, k + 1)] - main[k]; tg /= np.linalg.norm(tg) + 1e-9
        sgn = 1 if j % 2 == 0 else -1
        d = _rot(tg, sgn * rng.uniform(.65, .95)); Lt = N * rng.uniform(.26, .34) * (1.05 - .3 * s)
        tw = _curve(b, b + d * Lt, sgn * rng.uniform(.02, .05) * N, 24)
        groups.append((s, tw))
    groups.append((1., main[int(.55 * len(main)):]))
    allv = []
    for s, tw in groups:
        for lf in _twig_leaves(rng, tw, int(rng.integers(5, 8)), N * leaf, start=.15, lim=lim, N=N):
            allv.append((s + .2 * lf[0] + rng.normal(0, .05),) + lf[1:])
    allv.sort(key=lambda x: x[0])
    nb = int(len(allv) * .35)
    for key, b, d, L, W, v0 in allv[:nb]: _leaf(val, alp, b, d, L, W, v0 - .07)
    _stem(val, alp, main, 4.2 * SS, 1.6 * SS)
    for s, tw in groups[:-1]: _stem(val, alp, tw, 2.2 * SS, 1.1 * SS)
    for key, b, d, L, W, v0 in allv[nb:]: _leaf(val, alp, b, d, L, W, v0)
    return _finish(val, alp)


def _finish(val, alp):
    N = CELL * SS
    gy = np.linspace(-1, 1, N)[:, None]; val = np.clip(val * (1.03 - .06 * gy), 0, 1)
    v = (val * alp).reshape(CELL, SS, CELL, SS).sum((1, 3)); a = alp.reshape(CELL, SS, CELL, SS).sum((1, 3))
    vv = np.where(a > 0, v / np.maximum(a, 1e-6), 0.); a = a / (SS * SS)
    return vv.astype(np.float32), a.astype(np.float32)


def paint_atlas(seed=37):
    """-> rgba (SIZE x SIZE x 4, float, sRGB values, row 0 = top), cell list, mean opaque value of the leaf cells."""
    rng = np.random.default_rng(seed)
    out = np.zeros((SIZE, SIZE, 4), np.float32)
    cells = []
    for i in range(8):
        v, a = twig_cell(rng, int(rng.integers(8, 12)), rng.uniform(.22, .26), rng.uniform(-.09, .09))
        u0, v0, u1, v1 = cell_rect('S', i); r0 = int((1 - v1) * SIZE); c0 = int(u0 * SIZE)
        out[r0:r0 + CELL, c0:c0 + CELL, 0] = v; out[r0:r0 + CELL, c0:c0 + CELL, 3] = a; cells.append(('S', i))
    for i in range(4):
        v, a = branchlet_cell(rng, int(rng.integers(4, 6)), rng.uniform(.12, .145))
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
