P = 'D:/yun-jing-d2-logs/art/source/d2-logs-b/'
s = open(P + 'game_dr09v25.py', encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:120])
    s = s.replace(a, b)


HDR = """# DR09 斷枝堆 v026（L 樣品）：以 v025 另存（v025 及以前全部保留）。大幅修整版：
#   比例：規格 L＝4.0 × 2.2 × 1.1 m，v025 長 4.15、寬 2.27 已超出；參考正面高寬比約 0.30，限高 1.1 m 下主體長約 3.65 m。
#     → 全部構件的平面位置等比收到 0.883（x）、0.93（y），高度依參考重新指定（不是非等比壓扁或拉高）；半徑 ×0.94。
#   主要形體（前景主幹 A、中央主拱 B、最高主枝 T1、右枝 T2、右下落地枝 R1）依參考正面特徵點（同寬換算）重新給控制點（NEW26）。
#   斷口、樹皮、苔、地衣、蘑菇、落葉見檔尾 v026 區段。
"""
s = HDR + s
for a, b in (("'dr09_v5_for_v25'", "'dr09_v5_for_v26'"), ("ns['VER'] = 'v025'", "ns['VER'] = 'v026'"),
             ("'v025 先做 L 樣品'", "'v026 先做 L 樣品'"), ("f'::{fname}@v025'", "f'::{fname}@v026'"),
             ("'/game_dr09v25.py::splinter'", "'/game_dr09v26.py::splinter'"), ("_tb, HERE + '/game_dr09v25.py::tube'", "_tb, HERE + '/game_dr09v26.py::tube'"),
             ("_tb18, HERE + '/game_dr09v25.py::tube'", "_tb18, HERE + '/game_dr09v26.py::tube'"),
             ("scene['dr09_v25_contacts']", "scene['dr09_v26_contacts']"),
             ("f'{HERE}/blend/{asset}_v025.blend'", "f'{HERE}/blend/{asset}_v026.blend'"),
             ("f'{HERE}/blend/{asset}_v025_greybox.blend'", "f'{HERE}/blend/{asset}_v026_greybox.blend'")):
    rep(a, b)
s = s.replace('M_DR09_Layered_v025', 'M_DR09_Layered_v026')
assert 'v025_greybox.blend' not in s and "_v025.blend'" not in s

# ---- 比例：規格內的長寬；平面等比收、高度依參考指定
rep("ns['VARIANTS']['L'].update(twigs=12, litter=8, seed=91313)",
    "ns['VARIANTS']['L'].update(twigs=12, litter=8, seed=91313, L=3.65, W=2.05, margin=.36)   # v026：規格內（4.0 × 2.2 × 1.1）")
rep("        r0, mode, tp = o.get('r0', r0), o.get('mode', mode), o.get('tp', tp)\n",
    "        r0, mode, tp = o.get('r0', r0), o.get('mode', mode), o.get('tp', tp)\n"
    "        if name in NEW26:                                                   # v026：依參考重新設計的主要形體（新座標）\n"
    "            ctrl3, r0, tp = NEW26[name]['c'], NEW26[name].get('r0', r0 * SR26), NEW26[name].get('tp', tp)\n"
    "            knots, mode = NEW26[name].get('knots', knots), NEW26[name].get('mode', mode)\n"
    "        else:                                                               # 其餘：平面等比收、高度依參考比例\n"
    "            ctrl3 = [(x * SX26, y * SY26, z * SZ26) for x, y, z in ctrl3]\n"
    "            r0 = r0 * SR26\n")
rep("        P, s, r = rec['P'], rec['s'], rec['r']\n        i = int(len(P) * t)\n",
    "        P, s, r = rec['P'], rec['s'], rec['r']\n        fl = fl * SX26                                                      # v026：分叉長度跟著等比收\n        i = int(len(P) * t)\n")
# 沿軸距離（公尺）的參數跟著收
rep("    A['xs']['twk'] = [(.55, 1.1, .10), (1.20, -.9, .12), (1.85, .6, .14)]",
    "    A['xs']['twk'] = [(.49, 1.1, .10), (1.06, -.9, .12), (1.63, .6, .14)]")
rep("    A['xs']['ek'] = [(.45, .55, .22), (1.05, -.30, .22), (1.60, .45, .25), (2.25, .35, .30)]",
    "    A['xs']['ek'] = [(.40, .55, .20), (.93, -.30, .20), (1.41, .45, .22), (1.99, .35, .27)]")
rep("    A['und'] = [(.30, .15, .60), (.66, .09, -1.15), (1.06, .16, .16)]",
    "    A['und'] = UND26")
rep("    B['xs']['twk'] = [(.9, -1.0, .12), (2.0, .8, .12)]", "    B['xs']['twk'] = [(.8, -1.0, .12), (1.75, .8, .12)]")
rep("    B['xs']['ek'] = [(.7, .45, .25), (1.6, -.25, .22), (2.3, .40, .25)]", "    B['xs']['ek'] = [(.6, .45, .22), (1.4, -.30, .20), (2.0, .40, .22)]")

#@@EDITS@@
rep("    A['xs']['twr'] = .95 ", "    A['xs']['twr'] = .28 ")   # v026 六：截面扭轉減小（原本扁圓截面大幅螺旋＝麻繩感）
rep("    B['xs']['twr'] = -.80", "    B['xs']['twr'] = -.22")
rep("        rec['xs']['twr'] = U(R, .20, .50) * R.choice((-1, 1))", "        rec['xs']['twr'] = U(R, .06, .18) * R.choice((-1, 1))")
rep("    PATCH = {'A': ((.72, .62, 1.0), (2.05, .17, .55)), 'B': ((.86, .22, .72), (1.75, .15, .50)), 'B3': ((.75, .16, .38),)}", "    PATCH = PATCH26")
rep("""    (-1.37, -.47, .130, .110, -.10, -.08),
    (-1.23, -.40, .092, .085, .10, -.05),
    (-1.47, -.53, .072, .066, -.16, .04),""", """    (-1.18, -.43, .125, .115, -.06, -.12),    # v026 九：主蘑菇移到 A 隆起段的苔毯上（不長在斷口裸木上），大、中、小三朵，高低不同
    (-1.01, -.40, .088, .078, .12, -.08),
    (-1.31, -.49, .066, .058, -.16, -.05),""")
rep("T1a_ = fork_any('T1a', T1, (.47, .44, .51, .55),", "T1a_ = fork_any('T1a', T1, (.30, .34, .27, .38),")   # v026：上叉根部移到參考 x≈−0.07
rep("T1c_ = fork_any('T1c', T1, (.66, .62, .70),", "T1c_ = fork_any('T1c', T1, (.72, .68, .76, .64, .80),")   # v026：右叉（參考 0.73/0.76 → 1.03/0.69）
rep("            kk = 21\n            P[:, 2] += np.convolve(np.pad(up, kk // 2, mode='edge'), np.hanning(kk) / np.hanning(kk).sum(), 'valid') * 2.2\n",
    "            kk = 15                                                         # v026：避讓抬升不過衝（原 21 點 ×2.2 會把整段連帶抬高、再撞上更上層的枝）\n"
    "            P[:, 2] += np.convolve(np.pad(up, kk // 2, mode='edge'), np.hanning(kk) / np.hanning(kk).sum(), 'valid') * 1.3\n")

TAIL = open(r'C:/Users/joshs/AppData/Local/Temp/claude/b31c72c76ae68f3f/8f05215e-20df-4abf-90b4-48efd7d2a75e/scratchpad/tail26.py', encoding='utf-8').read()
a = "ns['PATCH_DONE'] = True\n" if "ns['PATCH_DONE'] = True\n" in s else None
# 檔尾附加區段插在 v025 的 STAVES_T1 定義之後（run() 之前）
a = s[s.index("# v025 二、T1 端部"):]
a = a[:a.index("]\n") + 2]
rep(a, a + TAIL)
open(P + 'game_dr09v26.py', 'w', encoding='utf-8').write(s)
print('ok', len(s))
