# 外圈古林散佈：六種樹（TR10 A/B/C 巨木、TR11 M1–M3 中型）各做成一個 collection，用 collection instance 隨機散開
#   由場景腳本 exec；需要 bpy, math, R, gh, S_, Vector
_TYPES = [('t10a', 1.0), ('t10b', 1.0), ('t10c', 1.0), ('t11m1', 1.0), ('t11m2', 1.0), ('t11m3', 1.0)]
_SKIPN = lambda n: n in ('Grid', 'Cube') or n.startswith(('Cylinder', 'Camera', 'Sun'))
_cols = {}
for _t, _w in _TYPES:
    _col = bpy.data.collections.new('TREE_' + _t)
    with bpy.data.libraries.load(S_ + f'godtree_{_t}.blend', link=False) as (_s, _d):
        _d.objects = [n for n in _s.objects if not _SKIPN(n)]
    for _o in _d.objects:
        if _o is not None and _o.type == 'MESH':
            _col.objects.link(_o)
    _cols[_t] = _col


def scatter_forest(region, avoid, n_target, min_gap=11.0, seed=7, scale_rng=(.85, 1.15)):
    """region(x,y)->bool 可種的地方；avoid: [(x,y,r)] 不能種的圓；樹之間至少 min_gap（巨木要更遠）。"""
    rr = __import__('random').Random(seed)
    placed = []
    tries = 0
    while len(placed) < n_target and tries < n_target * 400:
        tries += 1
        x, y = rr.uniform(-110, 110), rr.uniform(-40, 140)
        if not region(x, y):
            continue
        if any(math.hypot(x - ax, y - ay) < ar for ax, ay, ar in avoid):
            continue
        t = rr.choice(['t10a', 't10b', 't10c', 't11m1', 't11m2', 't11m3', 't11m1', 't11m2', 't11m3'])
        gap = min_gap * (1.6 if t.startswith('t10') else 1.0)
        if any(math.hypot(x - px, y - py) < max(gap, pg) for px, py, pg, _ in placed):
            continue
        placed.append((x, y, gap, t))
    for i, (x, y, gap, t) in enumerate(placed):
        e = bpy.data.objects.new(f'Forest_{i}_{t}', None)
        e.instance_type = 'COLLECTION'
        e.instance_collection = _cols[t]
        s = rr.uniform(*scale_rng)
        e.scale = (s, s, s * rr.uniform(.92, 1.1))
        e.rotation_euler.z = rr.uniform(0, 6.283)
        e.location = (x, y, gh(x, y) - .3)
        bpy.context.scene.collection.objects.link(e)
    print('FOREST', len(placed))
    return placed
