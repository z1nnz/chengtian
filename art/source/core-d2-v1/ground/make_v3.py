S = 'D:/chengtian/4-素材與快取/bark-sample/'
s = open(S + 'd2_scene_v2.py', encoding='utf-8').read().replace('\r\n', '\n')
rep = [
    ("# D2 設定圖 V2（南入口）構圖組裝", "# D2 設定圖 V3（祭壇前）構圖組裝：神木在左近處、祭壇在中右、坑在右前、泥路彎向祭壇"),
    ("TREE_Y = 60.0", "TREE_Y = 22.0\nTREE_X = -17.0\nALT = (12.0, 13.0)\nPIT = (13.5, 0.5)"),
    ("def path_x(y):\n    return 1.2 * math.sin(y * .11) + .6 * math.sin(y * .29 + 1)",
     "def path_x(y):\n    return 1.0 + .55 * max(0.0, y + 14) * min(1.0, max(0.0, y + 14) / 14) * .62 + .5 * math.sin(y * .29 + 1)"),
    ("    return base + side - pmask(x, y) * .16 + max(0, y - 14) * .02",
     "    rp = math.hypot(x - PIT[0], y - PIT[1])\n    pit = -1.15 * max(0.0, 1 - rp / 2.7) ** .6\n    return base + side - pmask(x, y) * .16 + max(0, y - 20) * .02 + pit"),
    ("JOSH = _os.environ.get('ARCH', 'josh') == 'josh'\nif JOSH:", "JOSH = False\nif False:"),
    ("else:\n    append(S_ + 'root_arch_lib.blend', lambda n: not SKIP(n), dz=-.25)", "else:\n    pass"),
    ("append(S_ + 'GT01_out/GT01_GodTree_v003.blend', lambda n: n.endswith('_LOD0'), offset=(2, TREE_Y, 0), dz=gh(2, TREE_Y) - .6)",
     "append(S_ + 'GT01_out/GT01_GodTree_v003.blend', lambda n: n.endswith('_LOD0'), offset=(TREE_X, TREE_Y, 0), dz=gh(TREE_X, TREE_Y) - .6)\n"
     "# 祭壇 AL01、被挖的坑 CO01（核心組 v001／v002）\n"
     "for _g, _p, _dz in (('AL01_RootAltarTerrace/AL01_RootAltarTerrace_v001.glb', ALT, -.05), ('CO01_ExcavatedPit/CO01_ExcavatedPit_v002.glb', PIT, -.02)):\n"
     "    _before = set(bpy.data.objects)\n"
     "    bpy.ops.import_scene.gltf(filepath='D:/chengtian/1-進行中/core-d2-altar/art/exports/core-d2-v1/' + _g)\n"
     "    for _o in set(bpy.data.objects) - _before:\n"
     "        if _o.type != 'MESH' or 'Collision' in _o.name or '_LOD1' in _o.name or '_LOD2' in _o.name:\n"
     "            bpy.data.objects.remove(_o, do_unlink=True)\n"
     "            continue\n"
     "        _o.location.x += _p[0]; _o.location.y += _p[1]\n"
     "        _o.location.z += (gh(_p[0], _p[1]) if _g.startswith('AL') else 0) + _dz"),
    ("append(S_ + 'd2_wood_lib.blend', lambda n: n.startswith('DR02_A'), offset=(1, 9, 0), dz=gh(-16, 18) - .1)",
     "append(S_ + 'd2_wood_lib.blend', lambda n: n.startswith('DR02_A'), offset=(30, 11, 0), dz=gh(13, 20) - .1)"),
    ("append(S_ + 'd2_wood_lib.blend', lambda n: n.startswith('DR02_C'), offset=(3, 5, 0), dz=gh(18, 14) - .1)",
     "append(S_ + 'd2_wood_lib.blend', lambda n: n.startswith('DR02_C'), offset=(12, 14, 0), dz=gh(27, 23) - .1)"),
    ("append(S_ + 'd2_wood_lib.blend', lambda n: n.startswith('DR07_A'), offset=(-34, 30, 0), dz=gh(-24, 25) - .1)", "pass"),
    ("append(S_ + 'd2_wood_lib.blend', lambda n: n.startswith('DR06_A'), offset=(34, 34, 0), dz=gh(26, 28) - .1)", "pass"),
    ("for (x, y, s1, s2, s3) in [(6.5, -9.5, 2.0, 1.5, 1.5), (9.2, -7.2, 1.1, .9, .8), (-7.5, -8, 1.5, 1.2, 1.0), (-10.5, -4.5, .9, .8, .6),\n                             (12, 6, 1.6, 1.3, 1.1), (-13, 12, 1.8, 1.4, 1.2), (7, 20, 1.2, 1.0, .8), (-6, 24, 1.3, 1.0, .9), (3.5, -11, .6, .5, .4)]:",
     "for (x, y, s1, s2, s3) in [(10.5, -10.5, 2.4, 1.8, 1.7), (6.5, -6, 1.2, 1.0, .9), (-5.5, -6.5, 1.3, 1.1, .9), (-8.5, -2, .9, .8, .6),\n                             (4.5, 4.5, 1.0, .8, .7), (17, 6, 1.4, 1.1, .9), (19, -6, 1.1, .9, .8)]:"),
    ("for (x, y, s) in [(-4.5, -11.5, 1.7), (-6.2, -9.8, 1.5), (-3.2, -9.2, 1.2), (5.0, -12.2, 1.6), (7.8, -11.5, 1.4), (4.2, -9.5, 1.1), (-8.5, -11, 1.3)]:",
     "for (x, y, s) in [(-4.5, -12.5, 1.9), (-6.5, -10.2, 1.7), (-2.8, -10.5, 1.3), (-8.5, -12, 1.5), (14, -11.5, 1.6), (16, -9, 1.3)]:"),
    ("for (py_, r1, r2) in [(-12.5, .9, .6), (-7.5, .7, .45), (-3, 1.0, .5), (4, .8, .5)]:", "for (py_, r1, r2) in [(-12.0, .9, .6), (-9.5, .6, .4), (-6, .8, .45)]:"),
    ("# 背景古林：用神木的遠景版縮小、轉向", "spots_override = True\n# 背景古林：用神木的遠景版縮小、轉向"),
    ("spots = [(-30, 28, .42), (-44, 50, .5), (-26, 62, .36), (-52, 78, .5), (-34, 92, .45), (30, 26, .4), (46, 46, .5), (27, 66, .36),",
     "spots = [(-40, 60, .42), (-58, 74, .5), (-20, 80, .36), (6, 70, .4), (22, 58, .42), (40, 46, .5), (34, 78, .36), (56, 30, .4),"),
    ("         (54, 80, .5), (36, 96, .44), (-60, 30, .45), (62, 28, .45), (-14, 100, .4), (16, 104, .4), (-22, 44, .3), (24, 44, .3)]",
     "         (60, 62, .5), (18, 96, .44), (-6, 104, .45), (44, 98, .45), (30, 34, .32), (48, 18, .34)]"),
    ("    x, y = R.uniform(-13, 13), R.uniform(-14, 8)\n    if pmask(x, y) > .35", "    x, y = R.uniform(-13, 22), R.uniform(-14, 10)\n    if math.hypot(x - PIT[0], y - PIT[1]) < 3.4 or math.hypot(x - ALT[0], y - ALT[1]) < 5.5 or pmask(x, y) > .35"),
    ("    if not free(x, y) or abs(x - path_x(y)) > 16 + R.uniform(-4, 4):",
     "    if not free(x, y) or abs(x - path_x(y)) > 16 + R.uniform(-4, 4) or math.hypot(x - PIT[0], y - PIT[1]) < 3.6 or math.hypot(x - ALT[0], y - ALT[1]) < 5.8:"),
    ("shot('V2', (.6, -15.5, 1.7), (.3, 0, 3.3), 21)", "shot('V3', (3.5, -16.5, 2.4), (2.0, 8, 4.0), 20)"),
    ("sc.render.filepath = OUT + f'd2v2_{TAG}_{nm_}.png'", "sc.render.filepath = OUT + f'd2v3_{TAG}_{nm_}.png'"),
]
for a, b in rep:
    if a not in s:
        print('MISSING:', a[:70])
    s = s.replace(a, b)
# 根腳小根段落（3a）只屬於我的拱，這裡不需要；但神木根邊要蕨與蕈：沿神木根腳補
s = s.replace("# 3b 拱身上成片的心形葉", """# 3c 神木根腳：蕨、心形葉、蕈沿根邊
for j in range(70):
    a = R.uniform(-1.2, 1.4)
    rr_ = R.uniform(14, 24)
    x, y = TREE_X + math.cos(a) * rr_, TREE_Y - abs(math.sin(a)) * rr_ * .9
    if R.random() < .6:
        fern(f'TF{j}', Vector((x, y, gh(x, y) - .03)), R, R.uniform(.9, 1.6), fern_mat, stem_mat)
    else:
        heart_plant(f'TH{j}', Vector((x, y, gh(x, y))), R, R.uniform(1.0, 1.6), heart_mat, stem_mat)
for j in range(14):
    a = R.uniform(-1.0, 1.2)
    rr_ = R.uniform(13, 20)
    x, y = TREE_X + math.cos(a) * rr_, TREE_Y - abs(math.sin(a)) * rr_ * .9
    mushrooms(f'TM{j}', Vector((x, y, 0)), R, R.randint(5, 11), R.uniform(1.4, 2.2), mush_mat, ground=gh)
# 3b 拱身上成片的心形葉""")
open(S + 'd2_scene_v3.py', 'w', encoding='utf-8').write(s)
print('written')
