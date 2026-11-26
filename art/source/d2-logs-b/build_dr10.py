# DR10 枯立木（高模）：死了還站著的樹，不長葉。兩種：
#   A：高 8 m、樹幹底徑約 0.7 m。頂上約 7.4–8.0 m 處折斷，參差斷口、一側幾根長木刺；兩三個短枝樁、一根往上彎的長枯枝；根頸張開成 5 條短根抓地。
#   B：高 14 m、底徑約 1.0 m，稍微斜、S 形彎。上半段幾根長的扭曲枯枝（往上、往外、末端斷），像骨架的剪影；頂端一根細斷刺；根頸 6 條根。
#   兩種：大片剝皮露出淺銀灰風化木（長縱裂紋）、剩下的樹皮深灰褐縱溝；兩三個啄木洞排成一直排（徑 10–14 cm、暗）；下段層狀菌；
#   苔只在根頸和根的朝上面；高處淡灰綠地衣斑；腳邊落葉和苔。
# 樹幹沿 +Z 直立；正面 -Y；z = 0 是地面；樹幹底中心在原點。
# 沿用 DR07 巨樹樁（exec build_dr07.py → DR05 → DR06 → ../d2-roots-b/dr_core.py）的樹皮材質、剝皮、斷口、根頸、層狀菌、植物。
# 參考：art/references/DR10/v001/（Codex 依設定圖 V1、V5 畫的三視圖／斜視／近照）。文字規格（高度、底徑）優先於參考圖比例。
# 用法（背景，不要加 --factory-startup）：
#   blender -b --python build_dr10.py -- A quick|full <輸出資料夾> [鏡位,鏡位] [nodress] [存檔.blend]
import bpy, bmesh, math, random, sys, os
import numpy as np
from mathutils import Vector, Matrix

_HERE10 = os.path.dirname(os.path.abspath(globals().get('__file__', 'D:/yun-jing-d2-logs/art/source/d2-logs-b/build_dr10.py')))
_p7 = os.path.join(_HERE10, 'build_dr07.py')
_nm10 = globals().get('__name__')
globals()['__name__'] = 'build_dr07_lib'            # 不要跑 DR07 的主程式
exec(compile(open(_p7, encoding='utf-8').read(), _p7, 'exec'), globals())
globals()['__name__'] = _nm10
__file__ = os.path.join(_HERE10, 'build_dr10.py')
WATER = False

# R 胸高半徑、H (斷口矮邊, 最高斷刺)、W 頂上心材朽空的殼厚、FL 根頸張開量、TK 頂端半徑 / 胸高半徑
# bend：樹幹軸 (x, y) 的偏移函式參數 ((sx, sy) S 彎幅度, (lx, ly) 斜度)
# limbs：dict(z 高, phi 世界方位角, ln 長, rf 枝徑/該處樹幹半徑, pitch 仰角, curl 越往外越往上彎的量, yaw 水平彎, tip 'break'|'taper', kids)
#   kids：(沿母枝比例, 張開角, 繞母枝角, 長, 枝徑/母枝該處半徑, curl, tip, kids)
# holes：啄木洞 (z, phi, 半徑)；fungi：(高度/H1, 方位角, 片數)
# 第四輪（形體重建）新增：
#   axis：主幹中心線控制點 (z, x, y)，Catmull-Rom 內插（取代 bend）；B 正面、側面各自一個相位不同的 S 彎
#   twist：稜脊／幹基板根稜扭轉率（rad/m），剝皮帶照同一個扭轉走
#   slabs：斷頂裂片 (方位角, 半寬角, 高出斷口的長度, 外傾, 厚度, 沿纖維扭轉)；主長、次長、短碎片三層
#   roots：主根 (方位角, 伸出距離/R, 粗/R, 起根高度)；幹基照主根方位隆起板根稜，根和幹連成一體
#   limbs 新鍵：c0 起段下垂量、hook 末段回挑量（取代單一 curl）
VARIANTS = {
    # 第六輪：完整幹身降低、破裂段拉長（總高不變）；slabs 只留一束主導長木束＋兩束次長＋一束短裂；notches 是深入幹身的縱裂缺口
    #   notches：(世界方位角, 半寬角, 深度 m)；limbs 的 segs：(沿枝比例, 仰角, 相對 phi 的水平偏角) 控制整段中心線
    'A': dict(name='SnagA', R=.80, H=(5.30, 5.80), W=.30, FL=.08, TK=.82, seed=103, hinge=1.15, pool=4.95,          # 第八輪：幹徑照參考等高對照（幹寬/樹高 0.17–0.21），R 1.00 → 0.80
              axis=((0, 0, 0), (1.5, .03, 0), (3.5, .10, -.06), (5.5, .06, -.14), (7.0, -.04, -.16), (8.5, -.12, -.16)),
              twist=.22, rib_twist=.04, rib=.26, peel_thr=-.12, nroots=6, amp=.11, butt=.62,
              teeth=((0.0, .30, .40), (.55, .18, .28), (-1.30, .12, .14)),
              # 第八輪：參考 A 的斷頂是外殼參差到 0.7–0.8 H、中空裡四五束長短不一的纖維束到 0.85–1.0 H；木束多、覆蓋大半圈
              slabs=((2.55, .70, 2.72, -.08, .20, .14), (1.75, .42, 1.95, -.03, .18, -.10), (-2.70, .48, 1.80, .00, .17, .12),
                     (-1.85, .30, 1.15, .04, .14, 0.0), (.95, .32, 1.30, .05, .14, 0.0), (-.55, .26, .70, .08, .12, 0.0)),
              notches=((-1.50, .25, 1.15, .35), (.20, .22, 1.10, -.30), (1.30, .08, .55), (-2.20, .08, .50)),
              tips=True,
              limbs=(dict(z=4.85, phi=.10, ln=3.00, rf=.40, pitch=.75, tip='taper',        # 第八輪：參考主枝從 0.62 H 往右上 S 形升到 0.82 H
                          segs=((0, .75, 0), (.25, .45, .10), (.50, .55, 0.0), (.70, .85, -.10), (.88, 1.05, 0.0), (1.0, 1.20, .10)),
                          kids=((.30, .70, 1.9, .95, .50, .30, 'break', ()),
                                (.55, .60, 1.2, 1.20, .55, .35, 'taper', ((.55, .50, 1.9, .45, .60, .20, 'taper', ()),)),
                                (.68, .50, -1.6, .55, .50, .30, 'taper', ()))),
                     dict(z=4.40, phi=2.90, ln=.50, rf=.36, pitch=.30, tip='break', kids=()),          # 參考：左側 0.55 H 斷枝樁
                     dict(z=3.35, phi=-.60, ln=.30, rf=.26, pitch=.15, tip='break', kids=())),         # 參考：右側 0.42 H 斷枝樁
              # 第八輪：主根肩部抬高（板根從 0.1 H 隆起）、伸出約 0.25 H 入土
              roots=((-.45, 2.3, .44, 1.10), (.55, 1.9, .36, .90), (1.55, 2.5, .46, 1.15), (2.55, 2.0, .36, .85),
                     (-2.40, 2.2, .42, 1.05), (-1.30, 2.0, .32, .80), (3.10, 1.7, .28, .70)),
              root_lift=.55, root_sh=.18, ell=.80,          # 第八輪：參考側視幹寬約正面的 0.8（橢圓斷面）；根肩照等高對照 0.05 H 幹寬 0.22 壓低
              rootlets=4,
              holes=((3.25, -1.45, .080), (3.70, -1.42, .072), (4.10, -1.47, .065)),
              fungi=((.15, .55, 5), (.17, 2.9, 4)), human=(2.9, -2.3)),
    'B': dict(name='SnagB', R=1.22, H=(11.70, 12.15), W=.12, FL=.08, TK=.52, seed=117, hinge=-.35, pool=11.40,
              # 第六輪：正面 下段稍往右、中段往左、上段往右；側面 下段往 +y、中段反向 -y、上段回正（兩個方向相位錯開）
              # 第八輪：照等高對照修正——正面中段少往左 0.3–0.5 m、0.7 H 起回到中線偏右；側面下段多往後、上段少往前
              axis=((0, 0, 0), (1.5, .14, .12), (3.0, .16, .52), (4.8, -.35, .80), (6.5, -.88, .48), (8.0, -.62, -.20),
                    (9.6, .05, -.28), (11.0, .70, -.40), (12.6, 1.20, -.10), (14.5, 1.55, .20)),
              twist=.30, rib_twist=.05, rib=.24, peel_thr=-.04, nroots=7, amp=.13, butt=.62,
              teeth=((0.0, .40, .40), (.95, .22, .22), (-1.1, .20, .18)),
              slabs=((2.95, .78, 2.05, -.12, .17, .22), (2.10, .44, .95, -.02, .17, -.18), (-2.55, .40, .65, .03, .15, 0.0),
                     (1.40, .28, .32, .10, .10, 0.0)),
              notches=((.55, .14, .95), (-1.25, .18, .80), (2.52, .10, .60)),
              # 第八輪：主枝照參考重排。L0 右下：外伸、中段下垂、末端上挑；L1 左：陡升、末端回勾向幹；L2 右上：斜升回挑；L3 後側：升起回勾
              limbs=(dict(z=8.00, phi=-.35, ln=4.20, rf=.37, pitch=.30, tip='taper',
                          segs=((0, .35, 0), (.25, .10, .10), (.50, -.12, .05), (.70, .25, -.05), (.85, .75, -.10), (1.0, 1.15, -.15)),
                          kids=((.40, .70, 1.4, 1.00, .50, .40, 'taper', ()),
                                (.80, .50, -1.6, .55, .55, .50, 'taper', ()))),
                     dict(z=8.90, phi=math.pi - .10, ln=5.00, rf=.36, pitch=.85, tip='taper',
                          segs=((0, .80, 0), (.20, .95, .05), (.45, 1.25, .10), (.70, 1.38, 0.0), (.85, 1.50, 0.0), (1.0, 1.85, 0.0)),
                          kids=((.35, .65, 1.5, 1.10, .55, .40, 'taper', ()),
                                (.62, .55, -1.4, .70, .55, .35, 'break', ()))),
                     dict(z=10.20, phi=-.70, ln=3.80, rf=.33, pitch=.55, tip='taper',
                          segs=((0, .55, 0), (.30, .35, .10), (.55, .55, .05), (.80, 1.00, -.05), (1.0, 1.30, -.10)),
                          kids=((.50, .60, 1.3, .90, .55, .40, 'taper', ()),
                                (.86, .45, -1.5, .45, .55, .30, 'taper', ()))),
                     dict(z=10.10, phi=1.85, ln=3.00, rf=.32, pitch=.70, tip='taper',
                          segs=((0, .65, 0), (.35, .45, .05), (.60, .75, 0.0), (.85, 1.25, -.10), (1.0, 1.65, -.10)),
                          kids=((.55, .55, 1.5, .60, .55, .30, 'taper', ()),)),
                     dict(z=7.20, phi=2.60, ln=.50, rf=.30, pitch=.35, tip='break', kids=()),
                     dict(z=6.30, phi=1.50, ln=.45, rf=.26, pitch=.25, tip='break', kids=()),
                     dict(z=4.40, phi=-1.10, ln=.30, rf=.20, pitch=.15, tip='break', kids=())),
              roots=((-.25, 2.4, .42, 1.75), (.70, 2.0, .33, 1.30), (1.65, 2.6, .44, 1.85), (2.55, 2.1, .34, 1.40),
                     (-2.95, 2.3, .40, 1.55), (-2.05, 2.5, .42, 1.70), (-1.15, 2.1, .30, 1.20)),
              root_lift=.60, root_sh=.18,
              rootlets=4,
              holes=((5.30, -1.62, .090), (5.85, -1.60, .082), (6.35, -1.64, .074)),
              fungi=((.12, -.35, 6), (.10, 2.4, 5)), human=(3.4, -2.8)),
}
VAR = VARIANTS['A']
PRE = 'DR10'
DBG = set(os.environ.get('DR10_DBG', '').split(','))     # 除錯：notwist（管子稜紋不扭）、noflute（不加扭轉寬稜）、nopeel（不剝皮）


def set_variant(v):
    global VAR
    VAR = VARIANTS[v]
    VAR['id'] = v
    VAR['L'] = VAR['H'][1]
    return VAR


# ---------------- 材質（DR10 副本） ----------------
def bark10_material():
    """DR07 樹皮的副本：剝皮處的風化木改成參考圖的淺銀灰（DR06／07 是灰褐）。
    第四輪在最後接三層：樹皮（Peel 低）偏暖褐；剝皮邊緣（Peel 0.08–0.45）一圈橘褐；
    地衣群落：低頻大塊 × 中頻破碎邊，只長在樹皮上、離地 1.6 m 以上、朝上和側面，灰白偏淡青。"""
    m = bpy.data.materials.get('DR10_Bark')
    if m:
        return m
    m = bark7_material().copy()
    m.name = 'DR10_Bark'
    for n in m.node_tree.nodes:
        if n.type == 'VALTORGB':
            e = n.color_ramp.elements
            if abs(e[0].color[0] - .13) < 1e-3 and abs(e[1].color[0] - .36) < 1e-3:
                e[0].color, e[1].color = (.17, .15, .13, 1), (.42, .37, .31, 1)      # 第四輪：風化木偏暖灰（參考圖），不要冷藍
    N, Lk = m.node_tree.nodes, m.node_tree.links
    bs = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    lk = bs.inputs['Base Color'].links[0]
    src = lk.from_socket
    Lk.remove(lk)
    pa = N.new('ShaderNodeAttribute')
    pa.attribute_name = 'Peel'
    # 1. 樹皮偏暖：乘一個暖色，量 = 1 − Peel
    warm = N.new('ShaderNodeMixRGB')
    warm.blend_type = 'MULTIPLY'
    warm.inputs[2].default_value = (1.20, .92, .70, 1)
    inv = N.new('ShaderNodeMath')
    inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1.0
    Lk.new(pa.outputs['Fac'], inv.inputs[1])
    Lk.new(inv.outputs[0], warm.inputs[0])
    Lk.new(src, warm.inputs[1])
    # 2. 剝皮邊緣橘褐
    er = N.new('ShaderNodeFloatCurve') if False else N.new('ShaderNodeMapRange')
    er.inputs['From Min'].default_value, er.inputs['From Max'].default_value = .08, .45
    Lk.new(pa.outputs['Fac'], er.inputs['Value'])
    bump = N.new('ShaderNodeMath')
    bump.operation = 'MULTIPLY'
    Lk.new(er.outputs['Result'], bump.inputs[0])
    one_m = N.new('ShaderNodeMath')
    one_m.operation = 'SUBTRACT'
    one_m.inputs[0].default_value = 1.0
    Lk.new(er.outputs['Result'], one_m.inputs[1])
    Lk.new(one_m.outputs[0], bump.inputs[1])
    edge = N.new('ShaderNodeMath')
    edge.operation = 'MULTIPLY'
    edge.inputs[1].default_value = 2.6
    Lk.new(bump.outputs[0], edge.inputs[0])
    edge.use_clamp = True
    orng = N.new('ShaderNodeMixRGB')
    orng.inputs[2].default_value = (.42, .22, .085, 1)
    Lk.new(edge.outputs[0], orng.inputs[0])
    Lk.new(warm.outputs[0], orng.inputs[1])
    # 3. 地衣群落
    geo = N.new('ShaderNodeNewGeometry')
    big = N.new('ShaderNodeTexNoise')
    big.inputs['Scale'].default_value = .85
    big.inputs['Detail'].default_value = 3.0
    Lk.new(geo.outputs['Position'], big.inputs['Vector'])
    small = N.new('ShaderNodeTexNoise')
    small.inputs['Scale'].default_value = 7.5
    small.inputs['Detail'].default_value = 4.0
    Lk.new(geo.outputs['Position'], small.inputs['Vector'])
    comb = N.new('ShaderNodeMath')
    comb.operation = 'MULTIPLY_ADD'
    comb.inputs[1].default_value = .45
    Lk.new(small.outputs['Fac'], comb.inputs[0])
    Lk.new(big.outputs['Fac'], comb.inputs[2])
    lr = N.new('ShaderNodeMapRange')
    lr.inputs['From Min'].default_value, lr.inputs['From Max'].default_value = .78, .83
    Lk.new(comb.outputs[0], lr.inputs['Value'])
    clu = N.new('ShaderNodeTexNoise')                       # 第五輪：群落尺度（約 3 m），群落之間留白
    clu.inputs['Scale'].default_value = .32
    clu.inputs['Detail'].default_value = 1.0
    Lk.new(geo.outputs['Position'], clu.inputs['Vector'])
    clr = N.new('ShaderNodeMapRange')
    clr.inputs['From Min'].default_value, clr.inputs['From Max'].default_value = .43, .54
    Lk.new(clu.outputs['Fac'], clr.inputs['Value'])
    lrc = N.new('ShaderNodeMath')
    lrc.operation = 'MULTIPLY'
    Lk.new(lr.outputs['Result'], lrc.inputs[0])
    Lk.new(clr.outputs['Result'], lrc.inputs[1])
    pk = N.new('ShaderNodeMapRange')                        # 只長在樹皮上，離剝皮邊界留一點距離（Peel 0 → 0.06 漸無）
    pk.inputs['From Min'].default_value, pk.inputs['From Max'].default_value = 0.0, .06
    pk.inputs['To Min'].default_value, pk.inputs['To Max'].default_value = 1.0, 0.0
    Lk.new(pa.outputs['Fac'], pk.inputs['Value'])
    sep = N.new('ShaderNodeSeparateXYZ')
    Lk.new(geo.outputs['Position'], sep.inputs['Vector'])
    hz = N.new('ShaderNodeMapRange')
    hz.inputs['From Min'].default_value, hz.inputs['From Max'].default_value = 1.6, 2.6
    Lk.new(sep.outputs['Z'], hz.inputs['Value'])
    m1 = N.new('ShaderNodeMath')
    m1.operation = 'MULTIPLY'
    Lk.new(lrc.outputs[0], m1.inputs[0])
    Lk.new(hz.outputs['Result'], m1.inputs[1])
    m2 = N.new('ShaderNodeMath')
    m2.operation = 'MULTIPLY'
    Lk.new(m1.outputs[0], m2.inputs[0])
    Lk.new(pk.outputs['Result'], m2.inputs[1])
    core = N.new('ShaderNodeMapRange')                      # 群落邊緣（剛過門檻）偏亮灰，中心是低飽和灰綠
    core.inputs['From Min'].default_value, core.inputs['From Max'].default_value = .83, .89
    Lk.new(comb.outputs[0], core.inputs['Value'])
    lcol = N.new('ShaderNodeMixRGB')
    lcol.inputs[1].default_value = (.36, .37, .33, 1)
    lcol.inputs[2].default_value = (.215, .245, .165, 1)
    Lk.new(core.outputs['Result'], lcol.inputs[0])
    lich = N.new('ShaderNodeMixRGB')
    Lk.new(lcol.outputs[0], lich.inputs[2])
    Lk.new(m2.outputs[0], lich.inputs[0])
    Lk.new(orng.outputs[0], lich.inputs[1])
    Lk.new(lich.outputs[0], bs.inputs['Base Color'])
    for nd in [n for n in N if n.type in ('NORMAL_MAP', 'BUMP')]:              # 第六輪
        s0 = nd.inputs['Strength'].default_value
        sm = N.new('ShaderNodeMath')
        sm.operation = 'MULTIPLY_ADD'                                           # s0·0.8 − s0·0.4·Peel
        sm.inputs[1].default_value = -.40 * s0
        sm.inputs[2].default_value = .80 * s0
        Lk.new(pa.outputs['Fac'], sm.inputs[0])
        Lk.new(sm.outputs[0], nd.inputs['Strength'])
    return m


def break10_material():
    """斷口、木刺、心材：DR07 的橘褐朽木去飽和、提亮成淺奶油灰（參考圖的新鮮斷刺）。"""
    m = bpy.data.materials.get('DR10_Break')
    if m:
        return m
    m = rot7_material().copy()
    m.name = 'DR10_Break'
    N, Lk = m.node_tree.nodes, m.node_tree.links
    b = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    lk = b.inputs['Base Color'].links[0]
    src = lk.from_socket
    Lk.remove(lk)
    hs = N.new('ShaderNodeHueSaturation')
    hs.inputs['Saturation'].default_value = .45
    hs.inputs['Value'].default_value = 1.9
    Lk.new(src, hs.inputs['Color'])
    mx = N.new('ShaderNodeMixRGB')
    mx.inputs[0].default_value = .35
    mx.inputs[2].default_value = (.46, .40, .30, 1)
    Lk.new(hs.outputs['Color'], mx.inputs[1])
    Lk.new(mx.outputs[0], b.inputs['Base Color'])
    return m


def peel10(V, ob, pts, seed, thr=.02):
    """第四輪：剝皮重做。
    - 分布：方位角先照樹幹扭轉率 V['twist'] 轉回（ps = phi + twist·z），再用低頻、被扭曲過的雜訊切出寬幅裸木帶；
      小塊殘留樹皮島把帶子打斷；正面、鉸點對面多一點。不是等距螺紋。
    - 幾何：樹皮是蓋在木頭上的一層（厚 6.5% r），剝掉處退到木頭面，保留原本的截面起伏與板根稜；
      裸木加沿扭轉方向的長纖維（約 12 cm 一道）和幾條深縱裂；剝皮邊緣的樹皮翹起、加厚。點屬性 Peel。"""
    rings, nu, co = ring_info(ob, pts)
    mo = vert_moss(ob.data)
    w = np.zeros(len(co))
    ph0 = V['hinge'] + math.pi * .62
    tw = V.get('twist', .4)
    for k, (c, r, fl, s_) in enumerate(rings):
        cc = np.array(c)
        for i in range(nu):
            j = k * nu + i
            z = co[j][2]
            if z < .2:
                continue
            d = co[j] - cc
            d[2] = 0
            rr = np.linalg.norm(d)
            if rr < 1e-6:
                continue
            dn = d / rr
            phi = math.atan2(dn[1], dn[0])
            ps = phi + tw * z
            ps += .55 * fb((math.cos(phi) * .8, math.sin(phi) * .8, z * .22 + seed + 9), 1.0, 2)          # 帶子邊界蜿蜒、寬窄不一
            pn = fb((math.cos(ps) * .95, math.sin(ps) * .95, z * .075 + seed), 1.0, 3)
            pn -= .34 * max(0.0, fb((math.cos(ps) * 3.2, math.sin(ps) * 3.2, z * .55 + seed + 3), 1.0, 2) - .15)   # 殘留樹皮島
            pn += .10 * fb(co[j] * 2.4, 1.0, 2)
            pn += .30 * (1 - _adist(phi, ph0) / 1.6) + .22 * (1 - _adist(phi, -math.pi / 2) / 1.6)
            zc = .75 + .55 * fb((math.cos(phi) * 1.4, math.sin(phi) * 1.4, seed + 21), 1.0, 2)      # 下緣高低不齊（不要一圈水平線）
            ww = _sm((pn - V.get('peel_thr', thr)) / .05) * (1 - _sm((mo[j] - .15) / .25)) * _sm((z - zc) / .35)
            bark_t = .085 * r                                                    # 第六輪：樹皮較厚，和裸木分界清楚
            if ww <= 0:
                continue
            w[j] = ww
            fib = .006 * r * math.sin(ps * 2 * math.pi * r / .12 + .8 * fb((ps * 3, z * .2, seed), 1.0, 1))
            crack = -.035 * r * max(0.0, fb((math.cos(ps) * 6.0, math.sin(ps) * 6.0, z * .12 + seed + 5), 1.0, 2) - .30) ** 2 * 6
            wood = rr - bark_t + fib + crack
            lip = .09 * r * math.sin(math.pi * min(1.0, ww * 1.7)) ** 2           # 剝皮邊緣的樹皮翹起
            co[j] = cc + dn * (rr * (1 - ww) + wood * ww + lip) + np.array((0, 0, co[j][2] - cc[2]))
    me = ob.data
    me.vertices.foreach_set('co', co.ravel())
    me.attributes.new('Peel', 'FLOAT', 'POINT').data.foreach_set('value', w.astype(np.float32))
    me.update()
    print('peel verts', int((w > .5).sum()), 'of', len(w))
    return w


# ---------------- 樹幹形狀 ----------------
def _axis_cr(ax, z):
    """控制點 (z, x, y) 的 Catmull-Rom；超出最後一點照最後一段直線外插。"""
    n = len(ax)
    if z <= ax[0][0]:
        return ax[0][1], ax[0][2]
    if z >= ax[-1][0]:
        (z0, x0, y0), (z1, x1, y1) = ax[-2], ax[-1]
        t = (z - z1) / (z1 - z0)
        return x1 + (x1 - x0) * t, y1 + (y1 - y0) * t
    i = max(k for k in range(n - 1) if ax[k][0] <= z)
    P0, P1, P2, P3 = ax[max(i - 1, 0)], ax[i], ax[i + 1], ax[min(i + 2, n - 1)]
    t = (z - P1[0]) / (P2[0] - P1[0])
    t2, t3 = t * t, t * t * t
    out = []
    for c in (1, 2):
        out.append(.5 * (2 * P1[c] + (-P0[c] + P2[c]) * t + (2 * P0[c] - 5 * P1[c] + 4 * P2[c] - P3[c]) * t2 + (-P0[c] + 3 * P1[c] - 3 * P2[c] + P3[c]) * t3))
    return out[0], out[1]


def axis_xy(V, z):
    """樹幹軸心：有 axis 控制點就用 Catmull-Rom（第四輪）；否則舊的 S 彎（sin）＋斜。"""
    if V.get('axis'):
        return _axis_cr(V['axis'], max(z, 0.0))
    H1 = V['H'][1]
    u = max(z, 0.0) / H1
    (sx, sy), (lx, ly) = V['bend']
    w = math.sin(math.pi * u) * u ** .35
    (tx, ty) = V.get('bend2', (0.0, 0.0))          # 第三輪：二次諧波，讓 B 有真正的 S 彎（參考圖上半段反折）
    w2 = math.sin(2 * math.pi * u) * u ** .5
    return sx * w + tx * w2 + lx * u ** 1.6, sy * w + ty * w2 + ly * u ** 1.6


def out_r(V, z):
    H1 = V['H'][1]
    zz = max(z, 0.0)
    return V['R'] * (1 + V['FL'] * math.exp(-zz / .85)) * (1 - (1 - V['TK']) * (zz / H1) ** 1.15)


def in_r(V, z):
    return max(.04, out_r(V, z) - V['W']) * (1 + .035 * math.sin(z * 2.3 + V['seed']))


def trunk_pts(V):
    H1 = V['H'][1]
    zs = [-.45, -.20, 0.0, .10, .22, .38, .58, .85, 1.2] + list(np.linspace(1.6, H1 + .08, max(4, int((H1 + .08 - 1.6) / .5) + 1)))
    return [(*axis_xy(V, z), z, out_r(V, z), 1.0) for z in zs]


def snag_moss(V):
    """苔只在根頸一圈和朝上的面（低處）；高處不長苔（地衣在材質裡）。"""
    def f(p, n):
        collar = _sm((1.7 - p.z) / .90)
        pat = fb((p.x * .9, p.y * .9, p.z * .5 + 3.0), 1.0, 3)
        return -.30 + .62 * collar * (.55 + pat) + .25 * max(0.0, n.z) * collar
    return f


def col_shell10(V, coll, sides=10):
    """碰撞：樹幹分段斜柱（跟著彎）到矮邊 0.95 高＋根頸一圈矮台。枝條在頭頂以上，不做碰撞。"""
    vs, fs = [], []

    def ring(z, r):
        cx, cy = axis_xy(V, max(z, 0.0))
        return [(cx + math.cos(2 * math.pi * i / sides) * r, cy + math.sin(2 * math.pi * i / sides) * r, z) for i in range(sides)]

    def prism(r0, z0, r1, z1):
        b = len(vs)
        vs.extend(ring(z0, r0) + ring(z1, r1))
        for i in range(sides):
            i2 = (i + 1) % sides
            fs.append((b + i, b + i2, b + sides + i2, b + sides + i))
        fs.append(tuple(b + i for i in range(sides))[::-1])
        fs.append(tuple(b + sides + i for i in range(sides)))
    zt = V['H'][0] * .95
    zk = [-.15] + list(np.linspace(1.2, zt, max(2, int(zt / 2.4) + 1)))
    for a, b in zip(zk[:-1], zk[1:]):
        prism(out_r(V, max(a, .5)) * .95, a, out_r(V, b) * .95, b)
    prism(V['R'] * (1 + V['FL']) * 1.30, -.15, V['R'] * 1.05, .40)
    me = bpy.data.meshes.new('Collision')
    me.from_pydata(vs, [], fs)
    me.update()
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    return _obj('Shell', me, coll)


# ---------------- 枝條 ----------------
def _perp(d):
    a = Vector((0, 0, 1)) if abs(d.z) < .9 else Vector((1, 0, 0))
    s = d.cross(a).normalized()
    return s, s.cross(d).normalized()


def _branch_path(start, d0, ln, r0, tipk, curl, yaw, seed, pre_len=0.0, collar=None, hook=None, c0=0.0, kinks=(), taper=.85, segs=None):
    """一根枝的路徑：從 start 往 d0 方向長 pre_len（埋在母枝裡）+ ln。越往外越往上彎（curl）、水平彎（yaw）、小幅扭動。
    回傳 [(x, y, z, r, 1)] 與每點的 (位置, 方向, 半徑, 在 ln 上的比例)。"""
    R = random.Random(seed)
    tot = pre_len + ln
    n = max(6, int(tot / .22) + 1)
    p = Vector(start)
    d = Vector(d0).normalized()
    s1, s2 = _perp(d)
    ph1, ph2 = R.uniform(0, 6.3), R.uniform(0, 6.3)
    pts, fr = [], []
    up = Vector((0, 0, 1))
    for i in range(n + 1):
        s = tot * i / n
        u = min(1.0, max(0.0, (s - pre_len) / max(ln, 1e-6)))
        if i and segs:                                  # 第六輪：照 segs 的 (比例, 仰角, 水平偏角) 平滑內插方向
            ph0 = math.atan2(d0.y, d0.x)
            j = max(k_ for k_ in range(len(segs)) if segs[k_][0] <= u + 1e-9)
            j2 = min(j + 1, len(segs) - 1)
            ua, ub = segs[j][0], segs[j2][0]
            w_ = 0.0 if j2 == j else _sm((u - ua) / max(ub - ua, 1e-6))
            pit = segs[j][1] + (segs[j2][1] - segs[j][1]) * w_
            yw = segs[j][2] + (segs[j2][2] - segs[j][2]) * w_
            tgt = Vector((math.cos(pit) * math.cos(ph0 + yw), math.cos(pit) * math.sin(ph0 + yw), math.sin(pit)))
            d = (d * .35 + tgt * .65).normalized() if u > 0 else d
            wob = .22 * (tot / n) / max(ln, .3)
            d = (d + s1 * math.sin(u * 7.0 + ph1) * wob + s2 * math.sin(u * 5.3 + ph2) * wob).normalized()
            p = p + d * (tot / n)
        elif i:
            hz = Vector((d.x, d.y, 0))
            if hz.length > 1e-4 and (curl or hook):
                ax = hz.cross(up).normalized()          # 往上翻：繞水平軸轉
                if hook is None:
                    cu = curl * (.6 + .8 * u)
                else:                                   # 第四輪：粗枝基部先往外壓（c0 < 0 下垂），外段回挑（hook）
                    cu = c0 * (1 - u) ** 1.5 * 1.6 + hook * u ** 2.4 * 3.4
                d = Matrix.Rotation(-cu * (tot / n) / max(ln, .3), 3, ax) @ d
            if yaw:
                d = Matrix.Rotation(yaw * (tot / n) / max(ln, .3), 3, up) @ d
            for (ku, ka) in kinks:                      # 彎折：走到 ku 時往上（ka > 0）或往下折一下，分兩步轉完
                if u > 0 and ku <= u < ku + 2.0 / n * tot / max(ln, .3) and hz.length > 1e-4:
                    d = Matrix.Rotation(-ka * .5, 3, hz.cross(up).normalized()) @ d
            wob = .34 * (tot / n) / max(ln, .3)
            d = (d + s1 * math.sin(u * 7.0 + ph1) * wob + s2 * math.sin(u * 5.3 + ph2) * wob).normalized()
            p = p + d * (tot / n)
        if s <= pre_len:
            k = collar if collar else 1.0
            r = r0 * k
        else:
            r = r0 * (1 - (1 - tipk) * u ** taper) * (1 + .10 * math.sin(u * 9 + ph1))
            if collar and u < .16:
                r *= 1 + (collar - 1) * (1 - u / .16) ** 2
        pts.append((p.x, p.y, p.z, r, 1.0))
        fr.append((p.copy(), d.copy(), r, u))
    return pts, fr


def _at(fr, t):
    """路徑上比例 t（在 ln 段）處的 (位置, 方向, 半徑)。"""
    best = min(fr, key=lambda q: abs(q[3] - t))
    return best[0], best[1], best[2]


def limbs10(V, coll, mat, low=False):
    """主枝（從樹幹長出、有枝領）＋二級、三級枝。斷頭用 DR06 的 snap_cap（參差木刺）；細梢收尖封口。"""
    objs = []
    seed0 = V['seed'] + 500
    k_amp = CFG['amp']
    cnt = [0]

    def make(name, pts, br, tip, sd):
        CFG.update(amp=0.0 if low else min(k_amp, .30 * br), moss=0.0)
        o = tube(name, pts, sd, rib=.16, twist=.25, collection=coll,
                 moss_bias=lambda p, nn: -.45 + .30 * max(0.0, nn.z) * _sm((2.2 - p.z) / 1.0), cap_end=(tip == 'taper'))
        o.data.materials.append(mat)
        objs.append(o)
        if tip == 'break':                              # 高模、低模都做（DR06 的作法：同名物件，烘焙對得上）
            cap = snap_cap(name + 'Cap', o, pts, pts[-1][3] * 1.0, sd + 1, coll, reach=.65, nspk=4, sub=1 if low else 2, shards=3, top=1.0,
                           splay=.25, shard_w=1.2, slen=(.6, 1.6))
            objs.append(cap)
        return o

    def kids(fr, plist, depth, base):
        for q, (t, ang, roll, ln, rf, curl, tip, sub) in enumerate(plist):
            p, d, r = _at(fr, t)
            s1, s2 = _perp(d)
            perp = s1 * math.cos(roll) + s2 * math.sin(roll)
            dd = (d * math.cos(ang) + perp * math.sin(ang)).normalized()
            br = r * rf
            st = p - dd * r * .55
            pts, fr2 = _branch_path(st, dd, ln * 1.35, br, .22 if tip == 'taper' else .55, curl, 0.0, base + q * 7, pre_len=r * .55, collar=1.38, taper=1.1,
                                    hook=curl * .22, c0=-.05)
            if tip == 'taper':
                x, y, z, rr, fl = pts[-1]
                pts[-1] = (x, y, z, max(.006, rr * .4), fl)
            cnt[0] += 1
            make(f'Twig{cnt[0]}', pts, br, tip, base + q * 7 + 1)
            if sub:
                kids(fr2, sub, depth + 1, base + q * 31 + 100)

    for i, L in enumerate(V['limbs']):
        c, n, up, r = _surf7(None, L['z'], L['phi'])
        br = r * L['rf']
        d0 = (n * math.cos(L['pitch']) + up * math.sin(L['pitch'])).normalized()
        pre = r * .75 / max(.35, n.dot(d0))
        st = c + n * r * .05
        pts, fr = _branch_path(st, d0, L['ln'], br, .45 if L['tip'] == 'break' else .24, L.get('curl', 0.0), L.get('yaw', 0.0), seed0 + i * 13,
                               kinks=L.get('kinks', ()), taper=1.45 if L['ln'] > 1.0 else .85, segs=L.get('segs'),
                               pre_len=pre, collar=1.55 if L['ln'] > 1.0 else 1.15, hook=L.get('hook', 0) * .80 if L.get('hook') is not None else None, c0=L.get('c0', 0.0))
        if L['tip'] == 'taper':
            x, y, z, rr, fl = pts[-1]
            pts[-1] = (x, y, z, max(.008, rr * .4), fl)
        make(f'Limb{i}', pts, br, L['tip'], seed0 + i * 13 + 1)
        kids(fr, L['kids'], 1, seed0 + i * 101)
    CFG.update(amp=k_amp)
    return objs


# ---------------- 啄木洞 ----------------
def hole_material():
    m = bpy.data.materials.get('DR10_HoleDark')
    if m:
        return m
    m = bpy.data.materials.new('DR10_HoleDark')
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (.035, .024, .015, 1)
    b.inputs['Roughness'].default_value = .95
    return m


def holes10(V, trunk):
    """在樹幹網格上挖圓洞：刪掉洞口範圍的面，洞口一圈點拉到正圓上（稍微內縮一圈當洞緣），往裡做一個暗色的杯（深 0.16 m）。"""
    me = trunk.data
    me.materials.append(hole_material())
    mi = len(me.materials) - 1
    bm = bmesh.new()
    bm.from_mesh(me)
    for (z, phi, rh) in V['holes']:
        c, n, up, r = _surf7(None, z, phi)
        hc = c + n * r
        bm.verts.ensure_lookup_table()
        near = [e for e in bm.edges if min((v.co - hc).length for v in e.verts) < rh * 2.2]      # 先細分附近的面，洞口才圓
        cuts = max(1, min(4, int(math.ceil(max(e.calc_length() for e in near) / (rh * .45))) - 1)) if near else 0
        if cuts:
            bmesh.ops.subdivide_edges(bm, edges=near, cuts=cuts, use_grid_fill=True)
            bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
        kill = [f for f in bm.faces if (f.calc_center_median() - hc).length < rh * .95]
        if not kill:
            continue
        bmesh.ops.delete(bm, geom=kill, context='FACES')
        bnd = [e for e in bm.edges if e.is_boundary and (sum((v.co for v in e.verts), Vector()) / 2 - hc).length < rh * 2.2]
        vs = list({v for e in bnd for v in e.verts})
        if len(vs) < 5:
            continue
        s1 = up.cross(n).normalized()
        s2 = n.cross(s1).normalized()
        ang = lambda v: math.atan2((v.co - hc).dot(s2), (v.co - hc).dot(s1))
        vs.sort(key=ang)
        for v in vs:                                    # 洞口拉圓（只動切線方向，保留表面起伏）
            a = ang(v)
            q = hc + s1 * math.cos(a) * rh + s2 * math.sin(a) * rh
            dn = (v.co - hc).dot(n)
            v.co = q + n * dn
        rows = [vs]
        for k_, (dep, sc) in enumerate(((.018, .97), (.06, .93), (.12, .80), (.16, .45))):
            row = []
            for v in vs:
                a = ang(v)
                row.append(bm.verts.new(hc - n * dep + (s1 * math.cos(a) + s2 * math.sin(a)) * rh * sc))
            rows.append(row)
        m = len(vs)
        for k_ in range(len(rows) - 1):
            for j in range(m):
                j2 = (j + 1) % m
                try:
                    f = bm.faces.new((rows[k_][j2], rows[k_][j], rows[k_ + 1][j], rows[k_ + 1][j2]))
                    f.material_index = mi if k_ else 0
                    f.smooth = True
                except ValueError:
                    pass
        cv = bm.verts.new(hc - n * .17)
        for j in range(m):
            try:
                f = bm.faces.new((rows[-1][(j + 1) % m], rows[-1][j], cv))
                f.material_index = mi
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    me.update()
    _surf7.cache.clear()


# ---------------- 第四輪：幹基板根稜＋扭轉稜脊（幾何） ----------------
def trunk_lobes10(V, ob):
    """直接改樹幹頂點：幹基照主根方位隆起板根稜（往上漸消），整段加三道隨高度扭轉的寬稜（扭轉率 V['twist']）。
    這是截面形狀本身在扭，不是貼圖；剝皮帶照同一個扭轉率走。"""
    me = ob.data
    co = np.array([v.co[:] for v in me.vertices])
    tw, s = V.get('twist', .3), V['seed']
    H0 = V['H'][0]
    rph = [(r[0], r[2]) for r in V.get('roots', ())]
    for j in range(len(co)):
        x, y, z = co[j]
        cx, cy = axis_xy(V, z)
        dx, dy = x - cx, y - cy
        rr = math.hypot(dx, dy)
        if rr < 1e-6:
            continue
        phi = math.atan2(dy, dx)
        zz = max(z, 0.0)
        bt = V.get('butt', .3) * math.exp(-zz / 1.25)
        k = 0.0
        for pk, th in rph:
            c = math.cos(phi - pk - .10 * zz)
            if c > 0:
                k += c ** 22 * (th / .40)                # 窄而高的板根稜，稜與稜之間凹下去
        jit = .9 * fb((math.cos(phi) * .7, math.sin(phi) * .7, z * .25 + s), 1.0, 2)          # 相位抖動：稜脊寬窄、間距不等，不像繩索
        fl = (.045 * math.cos(3 * (phi + tw * z) + s + jit) + .025 * math.cos(5 * (phi + tw * 1.1 * z) + s * 2 - jit)) * (.6 + .8 * max(0.0, fb((phi, z * .3, s + 4), 1.0, 1) + .4))
        fl *= 1 - _sm((z - (H0 - 1.2)) / 1.0)
        if 'noflute' in DBG:
            fl = 0.0
        sc = 1 + bt * k + fl
        co[j][0], co[j][1] = cx + dx * sc, cy + dy * sc
    me.vertices.foreach_set('co', co.ravel())
    me.update()
    _surf7.cache.clear()


# ---------------- 第四輪：斷頂裂片 ----------------
def tip_profile(kind, na, R):
    """第七輪：裂束末端每一欄（寬度方向 na+1 欄）的高度差，單位是木束長度的比例（負值＝較短）。
    spike 長尖；oblique 斜斷；blunt 鈍折（大致齊、小鋸齒）；step 階梯式破口；corner 局部缺角。"""
    n = na + 1
    if kind == 'spike':
        kp = R.choice((0, na)) if R.random() < .6 else R.randrange(n)
        return [.18 - .95 * abs(kk - kp) / na + R.uniform(-.14, .10) * (1.0 if kk % 2 else .5) for kk in range(n)]
    if kind == 'oblique':
        sg = R.choice((-1, 1))
        dr = R.uniform(.22, .34)
        return [-.04 - dr * (.5 + .5 * (-1 + 2 * kk / na) * sg) + R.uniform(-.03, .03) + (.03 if kk % 2 else 0.0) for kk in range(n)]
    jag = lambda kk: R.uniform(.025, .06) * (1 if kk % 2 else -1) + R.uniform(-.02, .02)   # 斷口鋸齒（不是平切）
    if kind == 'blunt':
        sl = R.uniform(-.10, .10)
        out = [-.08 + sl * (-1 + 2 * kk / na) + jag(kk) for kk in range(n)]
        out[R.randrange(n)] += R.uniform(.06, .10)        # 鈍折上留一顆短齒
        return out
    if kind == 'step':
        ks = R.randint(max(1, na // 3), max(1, (2 * na) // 3))
        hi_left = R.random() < .5
        dz = R.uniform(.20, .30)
        out = []
        for kk in range(n):
            up = (kk < ks) == hi_left
            u_ = kk / na if hi_left else 1 - kk / na
            v = (0.0 - .24 * u_ if up else -dz - .12 * (1 - u_)) + jag(kk)          # 每一階各自斜、帶鋸齒
            out.append(v)
        e = 0 if hi_left else na                          # 高的那側外緣再小缺一階
        out[e] -= R.uniform(.06, .10)
        return out
    # corner
    sl = R.uniform(-.08, .08)
    out = [-.02 + sl * (-1 + 2 * kk / na) + jag(kk) for kk in range(n)]
    c = R.choice((0, na))
    out[c] -= R.uniform(.28, .36)
    out[c + (1 if c == 0 else -1)] -= R.uniform(.14, .20)
    return out


def slabs10(V, coll, bark, brk, low=False):
    """第五輪：斷頂改成「縱向撕開的木束」。每個 slabs 條目是一塊沿主幹外殼往上的木片，再縱向撕成 m 條寬窄不一的木束：
    - 木束之間在各自的裂開高度以下彼此貼著（看得出原本是同一塊），以上裂縫逐漸張開（幾何縫，2 → 7 cm）；
    - 每束長度、厚度、外傾、尖端高度都不同，最高的那束不一定在中間；尖端是參差的撕裂端，不是收成一點；
    - 外面有縱向纖維溝、寬束中間有一道縱向深裂；內面（劈裂面）起伏較大；
    - 少數木束邊緣附一兩條短碎纖維（細條），只當點綴。
    主長、次長、短碎片三層仍由 V['slabs'] 的長度決定。"""
    objs = []
    s0 = V['seed'] + 700
    H1 = V['H'][1]
    for q, (pc, hw, ln, lean, th, tws) in enumerate(V.get('slabs', ())):
        R = random.Random(s0 + q * 3)
        th0 = _top_base(V, pc)
        zb = th0 - (1.0 if ln > 1.5 else .55)            # 第六輪：主導木束從斷口下 1 m 就是幹身外殼的延續
        r_mid = out_r(V, min(th0, H1))
        m = 3 if hw > .6 else (2 if hw > .36 else 1)     # 第六輪：主導 3 束、次長 2 束、短裂 1 束（不是一排細條）
        tips = V.get('tips')
        if tips and hw > .6:
            m = 4                                         # 第七輪：主導木片多撕出一條細木條                          # 主長片撕成 3 束、次長 2–3 束、短片 1–2 束（不是一叢細刺）
        if low:
            m = max(2, (m + 1) // 2)
        wts = [R.uniform(.5, 1.7) for _ in range(m)]
        cut = [-hw]
        for w_ in wts:
            cut.append(cut[-1] + 2 * hw * w_ / sum(wts))
        peak = R.randrange(m)
        fiber = -1
        kinds = ['spike'] * m
        if tips:
            if m >= 4:
                fiber = peak + 1 if peak + 1 < m else peak - 1
                wts[fiber] = .30 * sum(wts) / m
                cut = [-hw]
                for w_ in wts:
                    cut.append(cut[-1] + 2 * hw * w_ / sum(wts))
            pool = ['oblique', 'blunt', 'corner', 'step']
            R.shuffle(pool)
            for k in range(m):
                kinds[k] = pool[k % 4]
            if q == 0:
                kinds[peak] = 'oblique'                   # 主裂束：保留寬厚，末端斜斷（第八輪：階梯平頭看起來像方塊，改斜斷；階梯留給其他束）
            if fiber >= 0:
                kinds[fiber] = 'spike'                    # 撕出的細木條：少量長尖之一
            if q == 2:
                kinds[peak] = 'spike'                     # 另一根長尖
        bm = bmesh.new()
        uvl = bm.loops.layers.uv.new('UV')
        uvp = bm.loops.layers.uv.new('Param')
        col = bm.loops.layers.color.new('Mask')

        def face(vs, mi, uvs):
            try:
                f = bm.faces.new(vs)
            except ValueError:
                return
            f.material_index = mi
            f.smooth = True
            for lp, uv in zip(f.loops, uvs):
                lp[uvl].uv = uv
                lp[uvp].uv = uv
                lp[col] = (0.0, .55, .30, 1.0)

        def strip(a0, a1, L, tk0, lean_k, tw_k, zc, sd, tip_rag, na, crack, kind='spike', curvy=False):
            nt = (6 if low else 16)
            outer, inner = [], []
            for i in range(nt + 1):
                t = i / nt
                z = zb + (th0 - zb + L) * t
                cx, cy = axis_xy(V, z)                       # 第六輪：斷口以上沿主幹中心線延伸方向走（接續幹身曲率，不是垂直木板）
                above = max(0.0, z - zc)
                gap = 0.0 if above <= 0 else (.010 + .035 * min(1.0, above / max(L, .3))) / max(r_mid, .3)
                prof = (1 - max(0.0, (t - .60) / .40)) ** .7
                wid = (a1 - a0) / 2 - gap
                if kind == 'spike':
                    wid = max(.012 / max(r_mid, .3), wid * (1 - .78 * t ** 1.4))   # 第六輪：寬度沿長度平順收窄（不是等寬木板），尖端再參差撕開
                else:                                                               # 第七輪：寬度保留到接近末端
                    wid = max(.012 / max(r_mid, .3), wid * (1 - .28 * t ** 1.6 - .22 * max(0.0, (t - .82) / .18) ** 2))
                mid = (a0 + a1) / 2 + tw_k * t
                out_off = lean_k * max(0.0, t - .35) ** 2 * L
                tk = tk0 * ((1 - .80 * t ** 1.2) if kind == 'spike' else (1 - .30 * t ** 2)) + .010   # 第六輪收細；第七輪非尖型保留厚度
                if curvy:                                       # 第八輪：木束不是平直木板——寬、厚沿長度不均，側向與內外彎曲
                    wid *= 1 + .16 * math.sin(t * 4.2 + sd)
                    tk *= 1 + .25 * math.sin(t * 5.1 + sd * 1.3)
                    mid += .06 * math.sin(t * 2.6 + sd) * t
                    out_off += .07 * L * math.sin(t * 4.4 + sd * .7) * t
                    if kind != 'spike':                         # 第八輪：寬束末端不留方形平頭——最後三成收窄、變薄，再由鋸齒斷
                        wid *= 1 - .45 * _sm((t - .68) / .32)
                        tk *= 1 - .35 * _sm((t - .70) / .30)
                ro_row, ri_row = [], []
                for k in range(na + 1):
                    a = -1 + 2 * k / na
                    ang = mid + a * wid
                    dn = Vector((math.cos(ang), math.sin(ang), 0))
                    zs_ = min(z, th0 - .08)
                    cc_, _, _, rs_ = _surf7(None, zs_, ang)
                    ax_s = axis_xy(V, zs_)
                    ro = rs_ * (1.0 + .012 * min(1.0, t * 5)) - .03 * (1 - min(1.0, t * 5)) + (cc_ - Vector((ax_s[0], ax_s[1], zs_))).dot(dn)
                    fib = .014 * math.sin(a * na * 2.1 + sd) * (1 - .5 * t)                     # 外面縱向纖維溝
                    if crack and abs(a) < .34:
                        fib -= .045 * (1 - abs(a) / .34) * _sm((z - zb - .3) / .4)           # 寬束中間一道縱向深裂
                    spl = .035 * fb((a * 2.5, t * 3.0, sd + 7), 1.0, 2)                      # 劈裂面起伏
                    zj = tip_rag[k] * L * (.55 * t ** 2.5 if kind == 'spike' else _sm((t - .58) / .42))   # 第七輪：非尖型只在末端斷
                    c3 = Vector((cx, cy, z + zj))
                    ro_row.append(bm.verts.new(c3 + dn * (ro + out_off + fib)))
                    ri_row.append(bm.verts.new(c3 + dn * (ro + out_off - tk + spl)))
                outer.append(ro_row)
                inner.append(ri_row)
            for i in range(nt):
                v0, v1 = i / nt * L, (i + 1) / nt * L
                for k in range(na):
                    uv = [(k / na * .3, v0), ((k + 1) / na * .3, v0), ((k + 1) / na * .3, v1), (k / na * .3, v1)]
                    face((outer[i][k], outer[i][k + 1], outer[i + 1][k + 1], outer[i + 1][k]), 0, uv)
                    face((inner[i][k + 1], inner[i][k], inner[i + 1][k], inner[i + 1][k + 1]), 1, uv)
                for k, flip in ((0, True), (na, False)):
                    vs = (outer[i][k], inner[i][k], inner[i + 1][k], outer[i + 1][k])
                    face(vs if flip else vs[::-1], 1, [(0, v0), (.02, v0), (.02, v1), (0, v1)])
            for k in range(na):
                face((outer[0][k + 1], outer[0][k], inner[0][k], inner[0][k + 1]), 1, [(0, 0), (.1, 0), (.1, .02), (0, .02)])
                face((outer[-1][k], outer[-1][k + 1], inner[-1][k + 1], inner[-1][k]), 1, [(0, 0), (.1, 0), (.1, .02), (0, .02)])

        for k in range(m):
            a0, a1 = cut[k], cut[k + 1]
            d = abs(k - peak)
            Lk = ln * (1.0 if k == peak else (R.uniform(.55, .75) if d == 1 else R.uniform(.30, .45)))   # 第六輪：主導、次長、短裂明確分層
            wm = (a1 - a0) * r_mid
            na = 2 if low else max(4, min(7, int(wm / .06)))
            if tips:
                if low:
                    na = 3
                kd = kinds[k]
                rag = tip_profile(kd, na, R)
                if k == fiber:
                    Lk = ln * R.uniform(.74, .84)
                    zc = th0 + Lk * .12                   # 細木條較早撕開，基部仍和主片相連
                    lk_ = lean + R.uniform(.10, .16)
                    tk_ = th * R.uniform(.45, .60)
                else:
                    zc = th0 + Lk * R.uniform(.25, .55)
                    lk_ = lean + R.uniform(-.06, .16)
                    tk_ = th * (R.uniform(.95, 1.2) if k == peak else R.uniform(.70, 1.1))
                strip(pc + a0, pc + a1, Lk, tk_, lk_, tws * R.uniform(.3, 1.0) + R.uniform(-.06, .06),
                      zc, s0 + q * 31 + k, rag, na, (not low) and wm > .28, kd, curvy=True)
            else:
                kp = R.choice((0, na)) if R.random() < .6 else R.randrange(na + 1)      # 尖端偏向一側
                rag = [.18 - .95 * abs(kk - kp) / na + R.uniform(-.14, .10) * (1.0 if kk % 2 else .5) for kk in range(na + 1)]
                zc = th0 + Lk * R.uniform(.25, .55)          # 第六輪：撕開點拉高，下段木束彼此相連
                strip(pc + a0, pc + a1, Lk, th * R.uniform(.65, 1.2), lean + R.uniform(-.06, .16), tws * R.uniform(.3, 1.0) + R.uniform(-.06, .06),
                      zc, s0 + q * 31 + k, rag, na, (not low) and wm > .28)
            if not low and R.random() < .45 and Lk > .4:                     # 邊緣附一條短碎纖維
                e = pc + (a1 if R.random() < .5 else a0)
                zf = th0 + R.uniform(.1, .6) * Lk
                strip(e - .03 / r_mid, e + .03 / r_mid, R.uniform(.18, .45), .025, lean + R.uniform(.1, .3), 0.0,
                      th0 - .6, s0 + q * 31 + k + 500, [R.uniform(-.3, .2) for _ in range(3)], 2, False)
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=.002)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        me = bpy.data.meshes.new(f'Slab{q}')
        bm.to_mesh(me)
        bm.free()
        sd = s0 + q
        pe = np.array([_sm((v.co.z - (zb + .50 + .35 * fb((v.co.x * 2.5, v.co.y * 2.5, sd + 17), 1.0, 2))) / .25) for v in me.vertices], np.float32)
        if V.get('tips'):                                  # 第八輪：部分角度保留外側樹皮到斷口上方，和裸木裂束交錯（不是一條水平接縫）
            for j_, v_ in enumerate(me.vertices):
                ax_ = axis_xy(V, v_.co.z)
                an_ = math.atan2(v_.co.y - ax_[1], v_.co.x - ax_[0])
                kb = _sm((fb((math.cos(an_) * 2.4, math.sin(an_) * 2.4, sd + 41), 1.0, 2) - .02) / .20)
                hb = th0 + .4 + 1.0 * _sm(.5 + .5 * math.sin(an_ * 5 + sd))
                pe[j_] *= 1 - kb * _sm((hb - v_.co.z) / .35)
        me.attributes.new('Peel', 'FLOAT', 'POINT').data.foreach_set('value', pe)
        me.attributes.new('EndMoss', 'FLOAT', 'POINT').data.foreach_set('value', np.zeros(len(me.vertices), np.float32))
        me.materials.append(bark)
        me.materials.append(brk)
        objs.append(_obj(f'Slab{q}', me, coll))
    return objs


# ---------------- 第七輪：DR10 專用地面蘑菇（不改 d2-roots-b/core_plants.py 的共用 mushrooms()） ----------------
# 三個色系（線性色）：菇傘中段。同一叢共用色系、菇柄長寬比、傘形、傾向；不同叢才換。
MUSH10_TONES = ((.165, .088, .040),     # 土棕
                (.132, .101, .068),     # 灰褐
                (.300, .172, .066))     # 淡赭
MUSH10_STEM = (.42, .37, .28)
MUSH10_GILL = (.40, .33, .23)
MUSH10_RIM = (.30, .23, .14)
# 生長階段：傘半徑倍率、柄高倍率、傘隆起、傘肉厚（相對傘半徑）
MUSH10_STAGE = {'young': ((.45, .60), (.55, .72), (.78, .92), .55),
                'mature': ((.85, 1.12), (.92, 1.08), None, .32),
                'old': ((1.00, 1.28), (1.00, 1.12), (.22, .45), .24)}
# 每叢的階段比例（幼、成、老）
MUSH10_MIX = (('young', .50, 'mature', .40, 'old', .10),
              ('young', .25, 'mature', .55, 'old', .20),
              ('young', .15, 'mature', .45, 'old', .40))


def _lerp3(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _desat(c, t):
    g = (c[0] + c[1] + c[2]) / 3
    return tuple(c[i] + (g - c[i]) * t for i in range(3))


def mush10_palette():
    """遊戲版：蕈的頂點色量化成的平塗色塊（sRGB）。每個色系：傘心、傘中、傘緣、菌褶；再加菇柄、柄基、老菇傘。"""
    out = []
    for tn in MUSH10_TONES:
        for c in (tuple(x * .70 for x in tn), tn, _lerp3(tn, MUSH10_RIM, .30), _lerp3(MUSH10_GILL, tn, .30)):
            out.append(c)
    out += [MUSH10_STEM, tuple(x * .55 for x in MUSH10_STEM), tuple(x * .85 for x in _desat(MUSH10_TONES[0], .35))]
    return [tuple(max(0.0, x) ** (1 / 2.2) for x in c) for c in out]


MUSH10 = mush10_palette()


def mushrooms10(name, pos, R, fam, mix, n, scale, mat, ground, free, force=None):
    """一叢蕈。R 是這一叢自己的固定種子亂數。參數彼此相關：柄高跟傘徑、柄粗跟傘徑、傘形跟生長階段走。
    ground(x, y) → 地表高度（坡太陡回 None）；free(loc, r, hz) → 該高度半徑 r 內沒有樹身。"""
    tone = MUSH10_TONES[fam]
    bR = .055 * scale                                # 成熟菇傘半徑基準
    slender = R.uniform(1.5, 2.2)                    # 同叢：柄高／傘徑
    dome0 = R.uniform(.36, .55)                      # 同叢：成熟菇傘隆起
    lean0 = Vector((R.uniform(-1, 1), R.uniform(-1, 1), 0))
    lean0 = lean0.normalized() * R.uniform(.05, .18) if lean0.length > 1e-3 else Vector((0, 0, 0))
    names = (mix[0], mix[2], mix[4])
    wts = (mix[1], mix[3], mix[5])
    stages = ['mature'] + [R.choices(names, wts)[0] for _ in range(n - 1)]
    if force:                                        # 變體排列圖：指定階段
        stages = [force] * n
    Vv, F, C = [], [], []
    placed = []
    seg = 20
    for m, stg in enumerate(stages):
        sR, sH, sD, tcf = MUSH10_STAGE[stg]
        cr = bR * R.uniform(*sR)
        h = cr * slender * R.uniform(*sH) * (1.0 if stg != 'young' else 1.25)
        sr = cr * R.uniform(.16, .20) * (1.25 if stg == 'young' else 1.0)
        dome = R.uniform(*sD) if sD else dome0 * R.uniform(.82, 1.18)
        tc = cr * tcf
        ok = False
        for _ in range(30):
            a = R.uniform(0, 2 * math.pi)
            d = 0.0 if m == 0 else R.uniform(.03, .06 + .022 * n)
            bx, by = pos.x + math.cos(a) * d, pos.y + math.sin(a) * d
            gz = ground(bx, by)
            if gz is None:
                continue
            radial = Vector((math.cos(a), math.sin(a), 0)) * (.10 if m else 0.0)
            lean = lean0 * R.uniform(.6, 1.4) + radial
            top = Vector((bx, by, gz + h)) + lean * h
            ch = dome * cr + tc                              # 傘高
            if any((top.xy - q[0].xy).length < .92 * (cr + q[1]) and ((top.xy - q[0].xy).length < .50 * (cr + q[1]) or
                   not (top.z + ch + .02 < q[0].z - q[2] * .3 or q[0].z + q[3] + .02 < top.z - tc * .3))
                   for q in placed):                      # 傘面重疊時，必須一朵整個在另一朵傘底下
                continue
            if not free(Vector((bx, by, gz)), cr * 1.05, h + tc * .5):
                continue
            ok = True
            break
        if not ok:
            continue
        placed.append((top, cr, tc, ch))
        bz = gz - .015                                  # 柄基埋進土 1.5 cm
        # 顏色：同叢色系，個體只調明度與少量飽和度
        vk = R.uniform(.88, 1.10)
        sat = R.uniform(-.10, .12)
        capm = tuple(max(0.0, c * vk) for c in _desat(tone, -sat))
        capc = tuple(c * .70 for c in capm)
        capr = _lerp3(capm, MUSH10_RIM, R.uniform(.22, .38))
        gill = _lerp3(MUSH10_GILL, tone, .30)
        if stg == 'old':
            capm, capc, capr = (tuple(x * .82 for x in _desat(c, .22)) for c in (capm, capc, capr))
            gill = tuple(x * .70 for x in gill)
        stem = tuple(x * R.uniform(.92, 1.05) for x in MUSH10_STEM)
        stemb = tuple(x * .55 for x in stem)
        # 柄：彎曲中心線 off(z) = lean·h·(z/h)²，傘跟著柄頂切線傾斜
        def sc_(z):
            u = z / h
            return Vector((bx, by, bz + z)) + lean * h * u * u
        tan_top = (Vector((0, 0, 1)) + lean * 2.0).normalized()
        rows = []
        for (zz, rr, cc) in ((0.0, sr * 1.40, stemb), (h * .10, sr * 1.12, _lerp3(stemb, stem, .6)), (h * .35, sr * 1.0, stem),
                             (h * .70, sr * .93, stem), (h * .97, sr * .90, stem)):
            rows.append((sc_(zz), Vector((0, 0, 1)), rr, cc, None))
        # 傘：在柄頂的局部座標（tan_top 為上），偏心 ecc，老菇邊緣起伏／缺口／下垂
        ctop = sc_(h)
        e1 = tan_top.cross(Vector((1, 0, 0)))
        e1 = (e1 if e1.length > 1e-3 else tan_top.cross(Vector((0, 1, 0)))).normalized()
        e2 = tan_top.cross(e1).normalized()
        ea = R.uniform(0, 2 * math.pi)
        ecc = (e1 * math.cos(ea) + e2 * math.sin(ea)) * cr * R.uniform(0, .10)
        und = (R.uniform(.04, .065) if stg == 'old' else (R.uniform(0, .03) if stg == 'mature' else 0.0), R.randint(3, 5), R.uniform(0, 6.3))
        chunk = (R.uniform(0, 6.3), R.uniform(.45, .85)) if stg == 'old' and R.random() < .7 else None
        droop = (R.uniform(0, 6.3), cr * R.uniform(.10, .20)) if stg == 'old' else None
        if stg == 'young':                              # 幼菇：傘緣內捲、往下包
            rim_z, rim_r = -cr * .30, .86
        elif stg == 'mature':
            rim_z, rim_r = tc * R.uniform(.05, .30), 1.0
        else:
            rim_z, rim_r = tc * R.uniform(.25, .55), 1.0  # 老菇：傘緣平展或略上翻
        prof = [(sr * .95, tc * .05, gill, 0.0), (cr * .45 * rim_r, rim_z * .45 + tc * .12, gill, .45),
                (cr * .85 * rim_r, rim_z * .85 + tc * .06, gill, .85), (cr * rim_r, rim_z, capr, 1.0),
                (cr * rim_r * 1.0, rim_z + tc * .35, capr, 1.0)]
        for j in range(1, 7):
            u = 1 - j / 6
            zt = rim_z + tc * .35 + (dome * cr + tc - rim_z - tc * .35) * (1 - u ** 2) ** (.75 if stg != 'young' else .55)
            cc = _lerp3(capc, capm, _sm(u / .55)) if u < .55 else _lerp3(capm, capr, _sm((u - .55) / .45))
            prof.append((cr * rim_r * u if j < 6 else 0.0, zt, cc, u))
        for (rr, zz, cc, uu) in prof:
            rows.append((ctop + ecc * uu, tan_top, rr, cc, (uu, zz)))
        base = len(Vv)
        for (c0, up, rr, cc, cap) in rows:
            for s_ in range(seg):
                th = 2 * math.pi * s_ / seg
                dvec = e1 * math.cos(th) + e2 * math.sin(th)
                if cap is None:
                    Vv.append(tuple(c0 + Vector((math.cos(th), math.sin(th), 0)) * rr))
                    C.append((*cc, 1.0))
                    continue
                uu, zz = cap
                r2 = rr * (1 + und[0] * math.sin(th * und[1] + und[2]) * uu ** 2)
                if chunk:
                    dd = abs((th - chunk[0] + math.pi) % (2 * math.pi) - math.pi)
                    if dd < chunk[1]:
                        r2 *= 1 - .28 * uu ** 2 * _sm(1 - dd / chunk[1])
                z2 = zz
                if droop:
                    z2 -= droop[1] * uu ** 2 * max(0.0, math.cos(th - droop[0]))
                Vv.append(tuple(c0 + dvec * r2 + up * z2))
                C.append((*cc, 1.0))
        for i in range(len(rows) - 1):
            for s_ in range(seg):
                a0 = base + i * seg + s_
                a1 = base + i * seg + (s_ + 1) % seg
                F.append((a0, a1, a1 + seg, a0 + seg))
    if not Vv:
        return None
    me = bpy.data.meshes.new(name)
    me.from_pydata(Vv, [], F)
    me.validate()
    ca = me.color_attributes.new('Tint', 'FLOAT_COLOR', 'POINT')
    ca.data.foreach_set('color', np.array(C, np.float32).ravel())
    for p_ in me.polygons:
        p_.use_smooth = True
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o['mush_stages'] = ','.join(stages)
    return o


def bracket10_material():
    """第七輪：層狀菌自己的材質（不動共用 UG_Mushroom）：頂點色 Tint 的 alpha 控制粗糙度。"""
    m = bpy.data.materials.get('DR10_Bracket')
    if m:
        return m
    m = core_plants.mushroom_material()
    m.name = 'DR10_Bracket'
    N, L = m.node_tree.nodes, m.node_tree.links
    b = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    vc = next(n for n in N if n.type == 'VERTEX_COLOR')
    nz = next(n for n in N if n.type == 'TEX_NOISE')
    nz.inputs['Scale'].default_value = 140                # 近景細紋
    mr = N.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value, mr.inputs['To Max'].default_value = .32, .78
    L.new(vc.outputs['Alpha'], mr.inputs['Value'])
    L.new(mr.outputs[0], b.inputs['Roughness'])
    return m


# ---------------- 第四輪：主根 ----------------
def roots10(V, coll, mat):
    """幾條粗主根：從幹基殼壁裡（板根稜的位置）隆起，立起來的板（扁度 1.75 → 1.0），往外彎、蛇行，逐漸收細鑽進土裡；
    長短粗細都不同、方位不等距。主根之間幾條短的次根，貼地半埋。"""
    Rt = V['R']
    objs = []
    R = random.Random(V['seed'] + 2)
    for k, (phi, reach, thk, h0) in enumerate(V['roots']):
        wob = R.uniform(-.55, .55)
        yaw = R.uniform(-.45, .45)
        h0 = h0 * V.get('root_lift', .62)                 # 第八輪：板根從幹身較高處隆起
        pts = []
        nq = 11
        for q in range(nq + 1):
            u = q / nq
            a = phi + yaw * u + wob * math.sin(u * 2.6 + k) * u
            rad = Rt * (.72 + (reach * 1.30 - .72) * u ** .85)
            z = h0 * (1 - u) ** 1.55 + V.get('root_sh', .16) * Rt * math.sin(math.pi * min(1.0, u * 1.25)) * (1 - u) ** .6 - .42 * u ** 2.6 + .07 * math.sin(u * 7 + k) * u * (1 - u)   # 第六輪：肩部隆起再入土
            r = Rt * thk * 1.10 * (1 - .72 * u ** 1.05) * (1 + .12 * math.sin(u * 9 + k * 2)) + .03
            fl = 1.12 - .14 * u                                     # 第六輪：截面近圓（原 1.30 立板，相鄰主根連成斜坡）
            cx, cy = axis_xy(V, max(z, 0.0))
            pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad, z, r, fl))
        o = tube(f'Root{k}', pts, V['seed'] + 40 + k, rib=.22, twist=.25, collection=coll, moss_bias=.22)
        o.data.materials.append(mat)
        objs.append(o)
    rp = sorted(r[0] % (2 * math.pi) for r in V['roots'])
    nlet = V.get('rootlets', len(rp))
    for k in range(len(rp)):
        if k % max(1, round(len(rp) / max(nlet, 1))) and k >= 1:
            continue                                   # 次根：主根之間，短、細、半埋
        a0 = rp[k]
        a1 = rp[(k + 1) % len(rp)] + (2 * math.pi if k == len(rp) - 1 else 0)
        phi = a0 + (a1 - a0) * R.uniform(.35, .65)
        reach = R.uniform(1.4, 2.0)
        pts = []
        for q in range(7):
            u = q / 6
            a = phi + .3 * math.sin(u * 3 + k) * u
            rad = Rt * (.80 + (reach - .80) * u)
            z = .30 * (1 - u) ** 2 - .20 * u ** 2
            cx, cy = axis_xy(V, 0.0)
            pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad, z, Rt * (.13 * (1 - .7 * u)) + .02, 1.3 - .3 * u))
        o = tube(f'Rootlet{k}', pts, V['seed'] + 80 + k, rib=.15, twist=.3, collection=coll, moss_bias=.10)
        o.data.materials.append(mat)
        objs.append(o)
    return objs


def ground10(V, coll, lowpoly=False):
    """DR07 的根間土丘，第五輪壓低到 35%（原本整圈隆起，和根連成一圈裙邊）。
    第六輪：主根之間（離主根方位 > 0.25 rad）再往下壓 6–14 cm，深淺不一，形成根間凹谷；主根方位附近不動。"""
    g = ground7(V, coll, lowpoly)
    co = np.array([v.co[:] for v in g.data.vertices])
    co[:, 2] = np.where(co[:, 2] > 0, co[:, 2] * .35, co[:, 2])
    cx, cy = axis_xy(V, 0.0)
    rph = [r[0] for r in V['roots']]
    Rt = V['R']
    for j in range(len(co)):
        dx, dy = co[j][0] - cx, co[j][1] - cy
        rr = math.hypot(dx, dy)
        if rr < Rt * .9 or rr > Rt * 2.8:
            continue
        ph = math.atan2(dy, dx)
        dm = min(abs((ph - q + math.pi) % (2 * math.pi) - math.pi) for q in rph)
        k = _sm((dm - .25) / .30) * math.sin(math.pi * (rr - Rt * .9) / (Rt * 1.9))
        dep = .06 + .08 * (.5 + .5 * fb((math.cos(ph) * 2.0, math.sin(ph) * 2.0, V['seed'] + 3), 1.0, 2))
        co[j][2] -= dep * k
    g.data.vertices.foreach_set('co', co.ravel())
    g.data.update()
    return g


def brackets10(V, coll, R, mat):
    """第五輪層狀菌：每叢一片主體（寬約 0.32 R + 0.10 m）、1–3 片陪襯（0.55–0.8 倍）、1–3 片新生小菇（0.2–0.35 倍）。
    高度錯落（不等距）、前後深淺不同、朝向各偏 ±25°；菌蓋上面是穹起的厚肉、往邊緣收薄並帶一點波浪，
    底面微凹、奶油色；貼樹處加一圈附著肉。顏色差異克制：頂面褐、邊緣淺褐、底面奶油。"""
    V_, F_, C_ = [], [], []
    L = V['H'][1]
    for (f, ang, cnt) in V['fungi']:
        s0 = f * L
        sizes = [1.0] + [R.uniform(.55, .80) for _ in range(min(3, max(1, cnt - 3)))] + [R.uniform(.20, .35) for _ in range(R.randint(1, 3))]
        zs = sorted([s0 + R.uniform(-.25, .45) * V['R'] for _ in sizes], reverse=True)
        R.shuffle(sizes)
        for q, (sz, s) in enumerate(zip(sizes, zs)):
            an = ang + R.uniform(-.35, .35) * (1.2 - sz * .4)
            c, n, a, r = _surf7(None, max(.15, s), an)
            w = (V['R'] * .32 + .10) * sz
            dep = w * R.uniform(.55, .72)
            th = w * R.uniform(.20, .28)
            yaw = R.uniform(-.45, .45)
            p0 = c + n * (r - .02)
            hz = Vector((0, 0, 1))
            out = (n - hz * n.dot(hz)).normalized()
            out = (Matrix.Rotation(yaw * .5, 3, hz) @ out).normalized()
            along = hz.cross(out).normalized()
            tilt = R.uniform(-.08, .12)
            base = len(V_)
            na, nrad = 24, 26                          # 第七輪：色帶需要徑向解析度
            ph = R.uniform(0, 6.3)
            # 第七輪：以附著點為中心的弧形色帶：間距不等、寬窄不一、沿弧起伏、局部中斷／融合
            Rb = random.Random(V['seed'] * 101 + int(s * 1000) * 7 + q)     # 色帶用自己的亂數：菌的位置、大小和第六輪相同
            nb = Rb.randint(3, 5)
            gaps = [Rb.uniform(.6, 1.6) for _ in range(nb)]
            gsum = sum(gaps)
            rr_, acc = [], .12
            for gq in gaps:
                acc += .72 * gq / gsum
                rr_.append(acc)
            bands = []
            for bi, rb in enumerate(rr_):
                sgn = -1 if bi % 2 == 0 else 1
                if Rb.random() < .2:
                    sgn = -sgn
                bands.append((rb, Rb.uniform(.050, .100), sgn * Rb.uniform(.45, 1.0), Rb.uniform(0, 6.3), Rb.uniform(2.0, 4.5),
                              Rb.random() < .55, Rb.uniform(1.5, 3.5)))

            def band_val(rho, t):
                v = 0.0
                for (rb, wb, sb, sd, fq, gated, gf) in bands:
                    rc = rb + .030 * math.sin(t * fq + sd) + .015 * math.sin(t * 2 * fq + sd * 1.7)
                    g = math.exp(-((rho - rc) / wb) ** 2)
                    if gated:
                        gate = .5 + .5 * math.sin(t * gf + sd * 2.3)
                        g *= min(1.0, max(0.0, (gate - .20) / .35))
                    v += sb * g
                return max(-1.0, min(1.0, v))
            for top in (1, 0):
                for i in range(nrad + 1):
                    rho = i / nrad
                    for j in range(na + 1):
                        t = math.pi * j / na
                        wav = 1 + .07 * math.sin(t * 6 + ph) * rho ** 2
                        x = math.cos(t) * w * rho * wav
                        y = math.sin(t) * dep * rho * wav
                        edge = .12 * th
                        if top:
                            bv = band_val(rho, t)
                            zz = edge + (th - edge) * (1 - rho ** 2) ** .8 + .03 * th * math.sin(t * 9 + ph) * rho + .025 * th * bv * (1 - rho)
                        else:
                            zz = -edge * .3 - .10 * th * (1 - rho ** 2) + .18 * th * (1 - rho) ** 3       # 底面微凹，貼樹處附著肉
                        zz += tilt * y - .18 * th * rho ** 2
                        P = p0 + along * x + out * y + hz * zz
                        V_.append(tuple(P))
                        if top:
                            base_c = _lerp3((.050, .030, .015), (.120, .072, .034), _sm(rho / .70))       # 附著點深褐 → 中段褐
                            base_c = _lerp3(base_c, (.250, .185, .110), _sm((rho - .80) / .20))           # 生長緣略亮（淺褐，不是白邊）
                            mul = 1 + (.60 if bv > 0 else .55) * bv                                     # 暗帶 ×0.45、亮帶 ×1.6
                            cc = (min(1, base_c[0] * mul), min(1, base_c[1] * mul), min(1, base_c[2] * (1 + .40 * bv)), .55 - .18 * bv)
                        else:
                            cc = (.42, .37, .27, .80) if rho > .15 else (.22, .18, .12, .80)
                        C_.append(cc)
            row = na + 1
            for tp in range(2):
                off = base + tp * (nrad + 1) * row
                for i in range(nrad):
                    for j in range(na):
                        a0 = off + i * row + j
                        quad = (a0, a0 + 1, a0 + row + 1, a0 + row)
                        F_.append(quad if tp == 0 else quad[::-1])
            o1 = base + nrad * row
            o2 = base + (nrad + 1) * row + nrad * row
            for j in range(na):                                  # 薄邊：上下兩面的外緣接起來
                F_.append((o1 + j + 1, o1 + j, o2 + j, o2 + j + 1))
    me = bpy.data.meshes.new('DR10_Brackets')
    me.from_pydata(V_, [], F_)
    ca = me.color_attributes.new('Tint', 'FLOAT_COLOR', 'POINT')
    ca.data.foreach_set('color', np.array(C_, np.float32).ravel())
    for p_ in me.polygons:
        p_.use_smooth = True
    me.materials.append(mat)
    return _obj('Brackets', me, coll)


_top_h7 = top_h


def top_h(V, phi, inner=False):
    """第六輪：DR07 的斷口高度，再減掉縱裂缺口（V 形、邊緣參差，深入幹身 0.5–1.1 m）。"""
    v = _top_h7(V, phi, inner)
    for nt_ in V.get('notches', ()):
        pc, wk, dep = nt_[:3]
        sk = nt_[3] if len(nt_) > 3 else 0.0
        dd_ = (phi - pc + math.pi) % (2 * math.pi) - math.pi
        dt = abs(dd_)
        wk = wk * (1 + sk if dd_ >= 0 else 1 - sk)               # 第七輪：一側陡、一側緩
        if dt < wk:
            k = (1 - dt / wk) ** 1.4
            jag = 1 + .18 * fb((math.cos(phi) * 14, math.sin(phi) * 14, V['seed'] + pc), 1.0, 2)
            v -= dep * k * jag
    return v


_top_base = top_h


def top_h(V, phi, inner=False):
    """第八輪（A）：外殼口緣在每束木束的位置往上升（從完整幹身逐步裂開，木束不是插在平切樹頂上），兩側鋸齒。"""
    v = _top_base(V, phi, inner)
    if not V.get('tips'):
        return v
    best = v
    for (pc, hw, ln, *_r) in V.get('slabs', ()):
        dd = abs((phi - pc + math.pi) % (2 * math.pi) - math.pi)
        w = hw * 1.05
        if dd < w:
            rise = min(1.1, .45 * ln) * (.40 if inner else 1.0)
            k = _sm((w - dd) / (.55 * w))
            jag = .14 * fb((math.cos(phi) * 11, math.sin(phi) * 11, V['seed'] + pc), 1.0, 2)
            best = max(best, v + rise * (1 + jag) * k)
    return best


_ragged_top7 = ragged_top


def ragged_top(V, ob, pts, inner=False):
    """第六輪：壓縮起點照方位角下降（缺口處從缺口底下 0.35 m 開始壓），其他同 DR07。"""
    rings, nu, co = ring_info(ob, pts)
    zt = rings[-1][0].z
    zb = V['H'][0] - (.55 if not inner else .9)
    for j in range(len(co)):
        z = co[j][2]
        cx, cy = axis_xy(V, z)
        phi = math.atan2(co[j][1] - cy, co[j][0] - cx)
        ztop = top_h(V, phi, inner)
        z0 = min(zb, ztop - .35)
        if z <= z0:
            continue
        co[j][2] = z0 + (z - z0) * (ztop - z0) / (zt - z0)
    ob.data.vertices.foreach_set('co', co.ravel())
    ob.data.update()
    return rings, nu, co


# ---------------- 組起來 ----------------
def squash10(V, ob):
    """第八輪：橢圓斷面——相對主幹軸心把 Y 向偏移乘 ell（根頸 0.6 m 以下漸回圓形，根照舊接上）。"""
    e = V.get('ell', 1.0)
    if e == 1.0:
        return
    for v in ob.data.vertices:
        ax = axis_xy(V, v.co.z)
        k = 1 - (1 - e) * _sm((v.co.z - .15) / .60)
        v.co.y = ax[1] + (v.co.y - ax[1]) * k
    ob.data.update()


def build(variant='A', quick=True, low=None, col=False, pre=''):
    V = set_variant(variant)
    CFG.update(step=.10 if quick else .045, numin=24 if quick else 40, numax=360, amp=V['amp'], moss=.07, nuk=.8, crest=.40)
    if low:
        CFG.update(step=low[0], numin=low[1], numax=low[2], amp=0.0, moss=0.0, nuk=low[3])
    seed = V['seed']
    noise.seed_set(seed)
    R = random.Random(seed)
    coll = _coll(f"{PRE}_{V['name']}_{'Col' if col else ('Low' if low else 'High')}")
    if col:
        col_shell10(V, coll)
        return _finish_names(coll, pre)
    mat = bark10_material()
    rmat = break10_material()
    objs = []
    tp = trunk_pts(V)
    trunk = tube('Trunk', tp, seed, rib=V.get('rib', .24), twist=0.0 if 'notwist' in DBG else V.get('rib_twist', .05), collection=coll, moss_bias=snag_moss(V), cap_end=False)
    trunk.data.materials.append(mat)
    objs.append(trunk)
    trunk_lobes10(V, trunk)
    squash10(V, trunk)
    if not low and 'nopeel' not in DBG:
        peel10(V, trunk, tp, seed)
    elif not low:
        trunk.data.attributes.new('Peel', 'FLOAT', 'POINT')
    else:
        trunk.data.attributes.new('Peel', 'FLOAT', 'POINT')
    rings_o, nu_o, co_o = ragged_top(V, trunk, tp)
    _surf7.cache.clear()
    amp0, moss0 = CFG['amp'], CFG['moss']
    CFG.update(amp=amp0 * .4, moss=0.0)
    ip = inner_pts(V)
    inner = tube('Inner', ip, seed + 5, rib=.10, twist=.06, collection=coll, moss_bias=-1.0, cap_end=False)
    squash10(V, inner)
    CFG.update(amp=amp0, moss=moss0)
    rings_i, nu_i, co_i = ragged_top(V, inner, ip, inner=True)
    if not low:
        inner_fibres7(V, inner)
    clear_inner7(V, trunk, inner, gap=min(.06, V['W'] * .4))
    co_i = np.array([v.co[:] for v in inner.data.vertices])
    inner_moss7(V, inner)
    flip(inner)
    inner.data.materials.append(rmat)
    objs.append(inner)
    ro, ri = top_ring(V, co_o, nu_o), top_ring(V, co_i, nu_i)
    upv = Vector((0, 0, 1))
    rm = rim(V, coll, 'Rim0', ro, ri, upv, rmat, seed, lowpoly=bool(low))
    rim_moss7(V, rm, 15 if low else 22)
    objs.append(rm)
    kf = V['R'] / 1.25
    objs.append(rim_flakes(V, coll, random.Random(seed + 30), rmat, 0, ro, ri, upv,
                           n=int(4 + 8 * kf), lowpoly=False, trunk=trunk, n_sh=0))      # 第四輪：少一點，不連成一圈橫帶
    # DR07 的木刺長度照 (R/1.25)^.5：枯立木的斷口要長木刺（參考圖 0.3–1 m），借放大的 R 拉長
    objs.append(splinters(dict(V, R=V['R'] * 1.3), coll, random.Random(seed + 31), rmat, ro, ri, 4 if not low else 3))   # 第六輪：10 → 4、短一點
    objs += slabs10(V, coll, mat, rmat, low=bool(low))
    if not low:
        holes10(V, trunk)
    objs += limbs10(V, coll, mat, low=bool(low))
    objs += roots10(V, coll, mat)
    objs.append(ground10(V, coll, lowpoly=bool(low)))
    objs.append(pebbles(V, coll, random.Random(seed + 6), 10, sub=1 if low else 2))
    print('BUILD', V['id'], 'low' if low else 'high', len(coll.objects), 'objects')
    return _finish_names(coll, pre)


def _views(V):
    H0, H1 = V['H']
    Rt = V['R']
    hx, hy = math.cos(V['hinge']), math.sin(V['hinge'])
    D = H1 * 1.85
    tx, ty = axis_xy(V, H1 * .5)
    hcx, hcy = axis_xy(V, H0)
    h0 = V['holes'][1]
    c, n, up, r = _surf7(None, h0[0], h0[1])
    return {
        'front': ((tx, -D, 1.6), (tx, ty, H1 * .48), 30),
        'side': ((D, ty, 1.6), (tx, ty, H1 * .48), 30),
        'back': ((tx, D, 1.6), (tx, ty, H1 * .48), 30),
        'left': ((-D, ty, 1.6), (tx, ty, H1 * .48), 30),
        'tq': ((-D * .62, -D * .78, 1.7), (tx, ty, H1 * .48), 30),
        'top': ((tx, ty - .01, H1 + 16), (tx, ty, H1 * .3), 30),
        'break': ((hcx - hx * 2.6, hcy - hy * 2.6 - 1.2, H0 + .9), (hcx, hcy, H0 + .05), 30),
        'holes': (tuple(c + n * 2.4 + Vector((0, 0, .3))), tuple(c), 40),
        'base': ((-2.6 * Rt / .35 * .8, -3.4 * Rt / .35 * .8, 1.3), (0, 0, .45), 28),
    }


def dress(V, quick=True, seed=None, game=False, surf=('Trunk',)):
    """腳邊：根頸上的苔叢、根間的蕨、闊葉草、蕈；下段的層狀菌；地上落葉。高處不放植物。"""
    seed = V['seed'] + 900 if seed is None else seed
    R = random.Random(seed)
    Rt = V['R']
    Rb = Rt * (1 + V['FL'])
    k = .55 + .45 * (Rt / .5)
    coll = _coll(f"{PRE}_{V['name']}_{'GamePlants' if game else 'Plants'}")
    lm = core_plants._leaf_material
    mat = lambda n, *a, **kw: bpy.data.materials.get(n) or lm(n, *a, **kw)
    fern_mat = mat('D2_Fern', (.050, .090, .040, 1), (.11, .17, .075, 1), (.16, .22, .11, 1), gloss=.55)
    heart_mat = mat('D2_HeartLeafPale', (.060, .105, .050, 1), (.135, .20, .10, 1), (.22, .29, .16, 1), gloss=.4)
    moss_mat = mat('D2_MossTuft', (.040, .058, .014, 1), (.10, .125, .032, 1), (.12, .15, .045, 1), gloss=.8)
    litter_mat = mat('DR06_LitterLeaf', (.15, .07, .022, 1), (.42, .22, .07, 1), (.48, .30, .11, 1), gloss=.3)
    stem_mat = bpy.data.materials.get('D2_Stem')
    if stem_mat is None:
        stem_mat = bpy.data.materials.new('D2_Stem')
        stem_mat.use_nodes = True
        next(n for n in stem_mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (.05, .06, .025, 1)
    mush_mat = bpy.data.materials.get('UG_Mushroom') or core_plants.mushroom_material()
    sc = bpy.context.scene
    dg = bpy.context.evaluated_depsgraph_get()

    def base(nm):
        return nm.split('_', 1)[1] if nm.startswith(('L_', 'C_', 'F_')) else nm

    def cat(loc, nm):
        nm = base(nm)
        if not game:
            return nm
        cx, cy = axis_xy(V, max(loc.z, 0.0))
        rr = math.hypot(loc.x - cx, loc.y - cy)
        if rr > Rb * 1.05 and loc.z < .10:
            return 'Ground'
        if loc.z < 1.5:
            return 'Root'
        return 'Trunk'

    def hit(x, y, z0=2.5):
        ok, loc, nrm, _, ob, _ = sc.ray_cast(dg, Vector((x, y, z0)), Vector((0, 0, -1)))
        return (loc, nrm, cat(loc, ob.name)) if ok else None

    def keep(o):
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
        return o

    def clear(loc, rad, hs=(.15, .30, .45)):
        """loc 周圍 rad 內（離地 hs 各層，各 10 個方向）沒有樹幹、根、裂片等本體表面。第五輪：葉子展開半徑全算進去。"""
        for hh in hs:
            o = Vector((loc.x, loc.y, loc.z + hh))
            for kk in range(10):
                a_ = 2 * math.pi * kk / 10
                ok, l2, _, _, ob, _ = sc.ray_cast(dg, o, Vector((math.cos(a_), math.sin(a_), 0)), distance=rad)
                if ok and (not ob.name.startswith(('DR10_', 'Ground', 'L_Ground', 'Pebble')) or 'DeadSnag' in ob.name):   # 第七輪：遊戲低模 DR10_DeadSnag_*_LOD0 也算樹身
                    return False
        return True

    def polar(r0, r1):
        a = R.uniform(0, 2 * math.pi)
        rr = Rb * R.uniform(r0, r1)
        return math.cos(a) * rr, math.sin(a) * rr, a

    out = []
    mounds = []
    for i in range(70):
        x, y, a = polar(.55, 1.9)
        h = hit(x, y)
        if not h or h[1].z < .65 or h[0].z > 1.3:
            continue
        if h[2].startswith(('Root', 'Trunk')) and R.random() < .6:
            mounds.append((i, h[0].x, h[0].y, R.uniform(.08, .18) * k, R.uniform(.06, .12) * k, R.uniform(.02, .04), h[0].z - .02))
    if mounds and not game:
        out.append(keep(core_plants.moss_tufts('DR10_MossTufts', mounds, R, moss_mat, fb, density=2600 if quick else 5200)))
    nf = 0
    for i in range(240):
        if nf >= 4:
            break
        x, y, a = polar(1.4, 3.8)
        h = hit(x, y)
        sz = R.uniform(.70, 1.05) * k
        if h and h[2] == 'Ground' and h[1].z > .8 and clear(h[0], .75 * sz):
            o, so = core_plants.fern(f'DR10_FootFern{nf}', h[0] - Vector((0, 0, .02)), R, sz, fern_mat, stem_mat)
            out += [keep(o), keep(so)]
            nf += 1
    nh = 0
    for i in range(200):
        if nh >= 2:
            break
        x, y, a = polar(1.4, 3.8)
        h = hit(x, y)
        sz = R.uniform(.55, .85) * k
        if h and h[2] == 'Ground' and clear(h[0], .65 * sz):
            o = core_plants.heart_plant(f'DR10_Heart{nh}', h[0] - Vector((0, 0, .01)), R, sz, heart_mat, stem_mat)
            out.append(keep(o))
            so = bpy.data.objects.get(f'DR10_Heart{nh}_stem')
            if so:
                out.append(keep(so))
            nh += 1
    nm_ = 0
    for i in range(400):
        if nm_ >= 4:
            break
        x, y, a = polar(.9, 2.2)
        h = hit(x, y)
        if not h or h[1].z < .55:
            continue
        on_root = h[2].startswith('Root')
        if ((on_root and nm_ < 2) or (h[2] == 'Ground' and nm_ >= 2)) and clear(h[0], .15, hs=(.12, .25)):
            RM = random.Random(V['seed'] * 7 + 1300 + nm_ * 17)          # 第七輪：每叢固定種子
            fam = (V['seed'] + nm_) % 3
            mix = MUSH10_MIX[(nm_ * 2 + V['seed']) % 3]

            def gnd(x_, y_):
                hh = hit(x_, y_)
                return hh[0].z if hh and hh[1].z > .60 else None
            mo = mushrooms10(f'DR10_Mush{nm_}', h[0], RM, fam, mix, RM.randint(3, 6), k ** .5, mush_mat, gnd,
                             lambda l_, r_, hz_: clear(l_, r_, hs=(hz_,)))
            if mo is not None:
                out.append(keep(mo))
            nm_ += 1
    # 下段層狀菌（DR06 的 brackets：大小照 R，枯立木細，放大到像參考圖的 15–25 cm）
    g = globals()
    old = g.get('surf')
    g['surf'] = _surf7
    _surf7.cache.clear()
    try:
        out.append(keep(brackets10(V, coll, random.Random(seed + 4), bracket10_material())))
    finally:
        g['surf'] = old

    def place():
        x, y, a = polar(.95, 3.2)
        h = hit(x, y)
        if h and h[2] in ('Ground', 'Stones') or h and h[2].startswith('Rootlet'):
            return (x, y), h[0].z
        if h is None or h[0].z < .02:
            return (x, y), 0.0
        return None
    lo, n = litter('DR10_Litter', R, int(300 * k * (.6 if quick else 1.0)), place, litter_mat)
    out.append(keep(lo))
    print('DRESS', len(out), 'plant objects, litter', n)
    return coll


if __name__ == '__main__' and '--' in sys.argv:
    args = sys.argv[sys.argv.index('--') + 1:]
    var = args[0] if args else 'A'
    quick = (args[1] if len(args) > 1 else 'quick') == 'quick'
    outdir = args[2] if len(args) > 2 else 'D:/yun-jing-cache/dr10-work'
    os.makedirs(outdir, exist_ok=True)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    build(var, quick)
    if 'nodress' not in args:
        dress(VAR, quick)
    import preview_dr
    preview_dr.setup(samples=24 if quick else 64, fog=False)
    hum = bpy.data.objects.get('DR_Human_1p75m')
    if hum:
        hum.location = (VAR['human'][0], VAR['human'][1], .875)
    want = args[3].split(',') if len(args) > 3 and args[3] != 'all' else list(_views(VAR))
    for k in want:
        loc, tgt, lens = _views(VAR)[k]
        preview_dr.shot(os.path.join(outdir, f"DR10_{var}_{k}.png"), loc, tgt, lens, (1280, 720))
    for a_ in args[4:]:
        if a_.endswith('.blend'):
            bpy.ops.wm.save_as_mainfile(filepath=a_)
