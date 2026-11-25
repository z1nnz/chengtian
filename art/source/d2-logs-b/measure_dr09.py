# DR09 尺寸量測：只量木質本體（LOD0，不含落葉卡、碰撞殼、地面、人形尺）。
#   full  ：本體全部頂點（含外伸細枝梢）的包圍盒
#   core  ：去掉細枝（獨立網格塊的最小外框邊 < 3 cm 視為細枝梢／小枝）後的包圍盒
#   另報主要構件頂點的最高點（core 的 z 最大值），和「1.1 m 約略高度」比較。
#   blender -b <blend> --python art/source/d2-logs-b/measure_dr09.py -- <輸出 json>
import bpy, bmesh, sys, json
import numpy as np
out = sys.argv[sys.argv.index('--') + 1]
body = next(o for o in bpy.data.objects if o.name.endswith('_LOD0') and o.name.startswith('DR09_BranchPile'))
bm = bmesh.new(); bm.from_mesh(body.data); bm.transform(body.matrix_world)
bm.verts.ensure_lookup_table()
seen = set(); isl = []
for v in bm.verts:
    if v.index in seen: continue
    st = [v]; seen.add(v.index); ids = []
    while st:
        a = st.pop(); ids.append(a.index)
        for e in a.link_edges:
            b = e.other_vert(a)
            if b.index not in seen:
                seen.add(b.index); st.append(b)
    isl.append(ids)
co = np.array([v.co[:] for v in bm.verts])
def box(p):
    lo, hi = p.min(0), p.max(0)
    return dict(min=[round(float(x), 3) for x in lo], max=[round(float(x), 3) for x in hi], size=[round(float(x), 3) for x in hi - lo])
core = []
thin = 0
for ids in isl:
    p = co[ids]
    # 估計粗細：沿主軸投影後，垂直方向的範圍
    c = p - p.mean(0)
    u, s, vt = np.linalg.svd(c, full_matrices=False)
    w = c @ vt[1:].T
    th = float(np.min(w.max(0) - w.min(0)))
    if th >= .03:
        core.append(p)
    else:
        thin += 1
core = np.concatenate(core)
res = dict(object=body.name, islands=len(isl), thin_islands=thin, full=box(co), core=box(core))
res['full_hw_ratio_front'] = round(res['full']['size'][2] / res['full']['size'][0], 3)
res['core_hw_ratio_front'] = round(res['core']['size'][2] / res['core']['size'][0], 3)
json.dump(res, open(out, 'w'), indent=1)
print('MEASURE', json.dumps(res))
