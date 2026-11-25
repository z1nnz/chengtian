

# ======================================================================== v028 檔尾
# 二、T1：俯視改往右後斜伸（約 30°，原本與前景主幹 A 同向平行）；正面的 x／z 不變（保持 v027 的上挑與拱形交錯）
ns['T1_27']['c'] = [(-.64, .02, .22), (-.44, .10, .33), (-.22, .22, .45), (-.02, .34, .56), (.20, .46, .67), (.45, .58, .77),
                    (.66, .68, .85), (.82, .75, .90), (.96, .82, .945)]

# 三、地衣：少數集中、大小不一的斑片（主幹正面一大兩小、主拱兩片、T1 一片），其餘露樹皮；細枝不再散布地衣
ns['LICH'] = [('A', .34, (0, -1, -.25), .125), ('A', .62, (0, -1, .15), .055), ('A', .92, (0, -.9, -.30), .075),
              ('B', .22, (0, -1, .35), .085), ('B', .74, (0, -1, .20), .045),
              ('T1', .60, (0, -.6, .70), .065)]

# 四、斷口：只改 3 片主要長裂片＋1 片前側中片。由根部就開始漸薄（keep 0.12）、外緣略低於樹皮（ro 0.96）、根部埋深 +0.06 m、末端多齒撕開
for _i in (0, 1, 2, 3):
    _st = ns['STAVES_A'][_i]
    _st.update(keep=.12, wedge=.45, ro=.96, dep=_st['dep'] + .06, teeth=(.20, .55, .85))
# v028 四之二、中片與下側片（v027 keep 0.45–0.48、wedge 0.35：離開主幹後一半長度等厚、末端方鈍，近照像外加方塊）
#   → 一離開主幹斷面就開始收薄（keep＝埋入深度／全長），楔形加大、外緣略低於樹皮；下側兩片加長，打散端面下半部圓鈍輪廓。
for _i, _st in enumerate(ns['STAVES_A']):
    if _i >= 4 and _st['ri'] > .5:
        _st.update(keep=round(_st['dep'] / (_st['dep'] + _st['ext']), 3), wedge=.48, ro=.95)
ns['STAVES_A'][-2]['ext'] = .20
ns['STAVES_A'][-1]['ext'] = .14


# v028 五、地上散落小枝：F1 改斜後，斷口左側空出，隨機小枝落到枝堆外（俯視、斜視像飄在外面的碎棍）。
#   散落種子不變，只把落在斷口左側（x < −1.62）或離任何主枝超過 0.30 m 的小枝標為不建。
ns['_lit27'] = ns['litter']


def litter28(R):
    _lit27(R)
    br = [x for x in RECS if x['kind'] == 'branch' and not x.get('dead')]
    BB = np.vstack([x['P'][:, :2] for x in br])
    cut = []
    for x in RECS:
        if x['kind'] == 'litter' and not x.get('dead'):
            dm = max(float(np.min(np.linalg.norm(BB - p[:2], axis=1))) for p in x['P'][::3])
            if x['P'][:, 0].min() < -1.62 or dm > .30:
                cut.append(x['id'])
    LIT_CUT[:] = cut
    print('LITTER28_CUT', cut)


ns['litter'] = types.FunctionType(litter28.__code__, ns, 'litter')
ns['LIT_CUT'] = []
ns['_cleanup27'] = ns['cleanup']


def cleanup28():                                   # cleanup 會重設全部 dead 旗標 → 之後再把散落枝外的小枝標為不建
    _cleanup27()
    for x in RECS:
        if x['id'] in LIT_CUT:
            x['dead'] = True


ns['cleanup'] = types.FunctionType(cleanup28.__code__, ns, 'cleanup')
