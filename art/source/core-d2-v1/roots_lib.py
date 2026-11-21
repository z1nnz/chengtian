# RT01 地表長根（神木延伸出來、半埋在土裡、長苔的長根）：掃描樹皮推進幾何（godtree_base.tube）
#   blender -b --factory-startup -P roots_lib.py -- lib [norender]
#   存 roots_lib.blend：RT01_Root_A–D，長度 1（沿 +X 從 0 到 1 單位長度 = 10 m），場景再依長度縮放
import os, sys, math, random
from mathutils import Vector, noise

os.environ.setdefault('GT_NUMIN', '40')
BASE = 'D:/chengtian/4-素材與快取/bark-sample/godtree_base.py'
src = open(BASE, encoding='utf-8').read()
exec(compile(src.split('# ---------------- 樹幹')[0], BASE, 'exec'))
S_ = 'D:/chengtian/4-素材與快取/bark-sample/'
L = 10.0
made = []
for vi, nm in enumerate('ABCD'):
    rr = random.Random(40 + vi)
    pts = []
    side = rr.uniform(-1, 1)
    for i in range(14):
        t = i / 13
        x = t * L
        y = math.sin(t * rr.uniform(2.5, 4.5) + vi) * rr.uniform(.4, .9) + side * t * t * 1.2
        # 根從樹幹那頭高起（0.9 m），往外貼地、中途偶爾拱起，最後鑽進土裡
        z = .85 * (1 - t) ** 1.6 + .18 * max(0.0, math.sin(t * 9 + vi * 2)) * (1 - t) - .35 * t ** 3
        pts.append((x, y, z))
    r0 = rr.uniform(.55, .75)
    o = tube(f'RT01_Root_{nm}', pts, radius=lambda t, r0=r0: r0 * (1 - t) ** .8 + .05,
             flat=lambda t: .72, seed=vi * 3.3 + 1, rib=.16, twist=.08)
    o.data.materials.append(MAT)
    made.append(o)
    # 分出一兩條細支根
    for k in range(rr.randint(1, 2)):
        t0 = rr.uniform(.25, .6)
        i0 = int(t0 * 13)
        p0 = Vector(pts[i0])
        d = Vector((rr.uniform(.4, .9), rr.choice((-1, 1)) * rr.uniform(.5, 1.0), 0)).normalized()
        sl = rr.uniform(2.5, 4.5)
        spts = [tuple(p0 + d * sl * s + Vector((0, math.sin(s * 5) * .2, -.25 * s * s))) for s in [j / 7 for j in range(8)]]
        r1 = r0 * (1 - t0) * .5
        b = tube(f'RT01_Root_{nm}_b{k}', spts, radius=lambda t, r1=r1: r1 * (1 - t) + .03, flat=lambda t: .8,
                 seed=vi * 7 + k, rib=.1, twist=.05)
        b.data.materials.append(MAT)
        made.append(b)
for o in bpy.data.objects:
    if o.type == 'MESH' and not o.name.startswith('RT01'):
        bpy.data.objects.remove(o, do_unlink=True)
print('ROOTS', [o.name for o in made], sum(len(p.vertices) - 2 for o in made for p in o.data.polygons))
bpy.ops.wm.save_as_mainfile(filepath=S_ + 'roots_lib.blend')
