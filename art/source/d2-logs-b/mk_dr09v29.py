P = 'D:/yun-jing-d2-logs/art/source/d2-logs-b/'
s = open(P + 'game_dr09v28.py', encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:120])
    s = s.replace(a, b)


HDR = """# DR09 斷枝堆 v029（L 樣品）：以 v028 另存（v028 及以前全部保留）。本輪只處理五項已確認問題，不動材質、蘑菇、落葉：
#   一、斷口下半部本體：A 左端（端點 0）改用獨立建的斷口本體網格（BRK29），取代原本「外張的一圈唇緣＋中心扇形」的蓋子；
#       沿木紋劈出不等長的殘片與凹口，殘片由厚漸薄，中央是內凹的撕裂木芯面；拿掉 v027 補在圓團下方的兩片短裂片。
#   二、斷口與主幹交界：本體直接接在主幹最後一圈上，外表面沿用主幹截面（角向細分 ×3），不再有外張唇緣造成的多面體折角。
#   三、俯視：T1 後段收短、改彎回中段；透空率另用同定義的遮罩重算（見 void_dr09.py）。
#   四、高度：正式版維持 ≤ 1.1 m；DR9STUDY=1 另建「參考比例研究版」（主要枝幹高度與曲線依參考調整，輸出到另一個檔）。
#   五、裂片截面（透鏡形）只作用在 A 左端裂片：參數 lens／edge 加上 scope＝('A', 0) 識別，T1 末端裂片恢復 v027 的截面。
"""
s = HDR + s
for a, b in (("'dr09_v5_for_v28'", "'dr09_v5_for_v29'"), ("ns['VER'] = 'v028'", "ns['VER'] = 'v029'"),
             ("'v028 先做 L 樣品'", "'v029 先做 L 樣品'"), ("f'::{fname}@v028'", "f'::{fname}@v029'"),
             ("scene['dr09_v28_contacts']", "scene['dr09_v29_contacts']"),
             ("bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_v028.blend', copy=True)",
              "bpy.ops.wm.save_as_mainfile(filepath=os.environ.get('DR9OUT2', f'{HERE}/blend/{asset}_v029.blend'), copy=True)"),
             ("f'{HERE}/blend/{asset}_v028_greybox.blend'", "f'{HERE}/blend/{asset}_v029_greybox.blend'")):
    rep(a, b)
s = s.replace('/game_dr09v28.py::', '/game_dr09v29.py::').replace('M_DR09_Layered_v028', 'M_DR09_Layered_v029')
assert 'v028_greybox.blend' not in s and "_v028.blend'" not in s and 'game_dr09v28.py' not in s

# ---- 五、透鏡形截面限定作用範圍：只有 scope＝(物件名, 端點) 相符的裂片才套用（T1 末端裂片恢復原截面）
rep("""            hj = lambda k: math.sin(q * 91.7 + k * 37.719 + st['th'] * 13.1) * .5 + .5
            L = st['dep'] + st['ext']
            wd = st.get('wedge', .5)
""", """            hj = lambda k: math.sin(q * 91.7 + k * 37.719 + st['th'] * 13.1) * .5 + .5
            L = st['dep'] + st['ext']
            wd = st.get('wedge', .5)
            _lz, _ez = (st.get('lens', 0.0), st.get('edge', 0.0)) if st.get('scope') == (rec.get('name'), e) else (0.0, 0.0)   # v029：限定作用範圍
""")
rep("* (1 - .06 * (1 - math.sin(math.pi * u)))", "* (1 - _ez * (1 - math.sin(math.pi * u)))")
rep("* (.22 + .78 * math.sin(math.pi * u) ** .6)", "* (1 - _lz * (1 - math.sin(math.pi * u) ** .6))")

# ---- 驗證用：只建指定物件（DR9ONLY）
rep("        R_ = [x for x in R_ if x['kind'] == 'branch' and x.get('name') in ('A', 'B', 'T1', 'R1')]\n",
    "        R_ = [x for x in R_ if x['kind'] == 'branch' and x.get('name') in tuple(os.environ.get('DR9ONLY', 'A,B,T1,R1').split(','))]\n")

# ---- 驗證用：只建部分物件時沿用完整模型的平移量（DR9PIV="x,y"），近照相機座標才對得上
rep("""    piv['to_bottom_centre'](root, o)
""", """    if os.environ.get('DR9PIV'):
        from mathutils import Matrix as _Mx, Vector as _Vc
        _c = _Vc([float(x) for x in os.environ['DR9PIV'].split(',')] + [0.0])
        for _o in root.children:
            if _o.type == 'MESH':
                _o.data.transform(_Mx.Translation(-_c))
    else:
        piv['to_bottom_centre'](root, o)
""")

# ---- 三、俯視：後緣超出參考的部分收回、左中空洞用中型枝補（不靠細枝落葉）
for a, b in (("    L2 = log('L2', [(-1.10, .66, 0), (-.72, .81, .03), (-.36, .92, 0)], .042, .55,",
              "    L2 = log('L2', [(-1.45, .05, 0), (-1.10, .25, .04), (-.76, .42, 0)], .062, .50,"),          # 左後 → 左中空洞（斜穿、加粗）
             ("    N8 = log('N8', [(-.98, .98, .02), (-.80, .82, .06), (-.62, .66, .10)], .055, .55, mode='rest')",
              "    N8 = log('N8', [(-1.32, .60, .02), (-1.08, .46, .07), (-.86, .30, .10)], .055, .55, mode='rest')"),   # 後緣 0.98 → 往內搭在 L2 上
             ("    N4 = log('N4', [(.48, .64, .0), (.78, .80, .09), (1.08, .92, .0)], .045, .55)",
              "    N4 = log('N4', [(.46, .58, .0), (.76, .72, .09), (1.06, .84, .0)], .045, .55)"),
             ("    M6 = log('M6', [(.30, .95, .05),", "    M6 = log('M6', [(.32, .84, .05),"),
             ("    D = log('D', [(.40, .86, 0), (.90, .76, .03), (1.42, .64, 0)], .085,", "    D = log('D', [(.42, .74, 0), (.90, .62, .03), (1.40, .50, 0)], .085,"),   # 右後大枝往前（俯視超出參考後緣）
             ("    F1 = log('F1', [(-1.02, -.91, 0), (-.62, -.81, .03), (-.25, -.71, .02), (.05, -.60, 0)], .048,",
              "    F1 = log('F1', [(-1.48, -.88, 0), (-1.02, -.86, .03), (-.55, -.76, .03), (-.15, -.66, .02), (.10, -.58, 0)], .052,"),   # 左前補量
             ("    F2 = log('F2', [(.95, -.55, 0), (1.20, -.75, .02), (1.48, -.92, 0)], .040,", "    F2 = log('F2', [(.95, -.55, 0), (1.30, -.73, .02), (1.72, -.90, 0)], .050,")):   # 右前補量
    rep(a, b)

# ---- 四、研究版：分叉、細枝高度上限依比例放寬（正式版不變）
rep("    V['H'] = 1.00 ", "    V['H'] = 1.00 * (globals().get('STUDY_H', 1.0) if os.environ.get('DR9STUDY') else 1.0) ")

TAIL = open(P + 'tail_dr09v29.py', encoding='utf-8').read()
a = "ns['cleanup'] = types.FunctionType(cleanup28.__code__, ns, 'cleanup')\n"
rep(a, a + TAIL)
open(P + 'game_dr09v29.py', 'w', encoding='utf-8').write(s)
print('ok', len(s))
