

# ======================================================================== v027 檔尾
# v027 左端斷口：依參考裸木區（等寬換算：上緣沿主幹頂面延伸到最左端 0.24 m 高、下緣 0.04 m、裸木與樹皮交界在端面往右 0.25–0.45 m）
#   先定長度、面積與方向：三片長薄撕裂片（上緣、上前、上後）從主幹內部連續長出、往左延伸 0.28–0.40 m；
#   中片較短、短片與內層芯材在端面深處；片薄（ri 0.56–0.68）、片間留深縫；out≈0（不放射）、扭轉小、長短不等。
#   th：0＝下、π/2＝後、−π/2＝前、π＝上。
_K27 = dict(bend=0., sw=0., dark=.42, lift=0., out=.01)
ns['STAVES_A'] = [
    dict(_K27, th=2.95, span=.42, ri=.62, ro=1.00, dep=.20, ext=.40, lift=.02, sw=.02, keep=.30, bias=.20, barkL=.40, wedge=.50, tw=.30, teeth=(.30,), split=.50, splitd=.45),
    dict(_K27, th=-2.45, span=.36, ri=.60, ro=1.00, dep=.16, ext=.34, keep=.30, bias=-.25, barkL=.15, wedge=.55, tw=-.35, teeth=(.70,), split=.45, splitd=.45),
    dict(_K27, th=2.30, span=.30, ri=.66, ro=1.00, dep=.14, ext=.28, sw=.02, keep=.35, bias=-.15, barkL=.35, wedge=.55, tw=-.25, teeth=(.60,), split=.30, splitd=.32),
    dict(_K27, th=-1.70, span=.38, ri=.56, ro=.99, dep=.12, ext=.20, keep=.30, bias=.25, barkL=.10, dark=.50, wedge=.60, tw=.35, teeth=(.25, .80), split=.55, splitd=.40),
    dict(_K27, th=1.50, span=.34, ri=.62, ro=.99, dep=.10, ext=.16, keep=.30, bias=-.20, barkL=.40, wedge=.55, tw=-.30, teeth=(.50,), split=.30, splitd=.30),
    dict(_K27, th=-.90, span=.32, ri=.64, ro=.99, dep=.08, ext=.12, lift=.03, keep=.35, bias=.20, barkL=.25, wedge=.55, tw=.25, teeth=(.40,), split=.55, splitd=.30),
    dict(_K27, th=.35, span=.40, ri=.68, ro=.98, dep=.05, ext=.06, keep=.30, bias=.20, barkL=.45, wedge=.50, tw=.20, teeth=(.35, .80), split=.60, splitd=.24),
    dict(_K27, th=-3.00, span=.32, ri=.10, ro=.45, dep=.24, ext=.11, keep=.35, bias=0., barkL=0., dark=.58, wedge=.55, tw=.15, teeth=(.50,), split=.40, splitd=.25),
    dict(_K27, th=-1.25, span=.28, ri=.20, ro=.50, dep=.18, ext=.07, keep=.35, bias=.10, barkL=0., dark=.55, wedge=.55, tw=-.15, teeth=(.45,), split=.30, splitd=.20),
]
for _i, _st in enumerate(ns['STAVES_A']):          # 片寬保持到接近末端才撕開（長條撕裂片，不是三角尖牙）
    if _st['ri'] > .5:
        _st['wedge'], _st['keep'] = (.28, .58) if _i < 3 else (.35, .48)
# 斷口下半部：兩片短、薄的下側裂片打碎端面圓鈍的下輪廓（不是放射尖刺：沿木紋、out≈0）
ns['STAVES_A'] += [
    dict(_K27, th=-.30, span=.40, ri=.55, ro=.99, dep=.10, ext=.14, keep=.45, bias=.20, barkL=.30, wedge=.35, tw=.20, teeth=(.40, .75), split=.50, splitd=.30),
    dict(_K27, th=.85, span=.36, ri=.60, ro=.99, dep=.07, ext=.09, keep=.45, bias=-.20, barkL=.40, wedge=.35, tw=-.20, teeth=(.55,), split=.40, splitd=.25),
]

# v027 地衣：主幹正面的斑片減半、縮小（原本連成一片白），保留大小不一的附著斑
ns['LICH'] = [(n_, f_, d_, R_ * (.80 if n_ != 'A' else .72)) for i_, (n_, f_, d_, R_) in enumerate(ns['LICH']) if not (n_ == 'A' and i_ % 2 == 1)]


def layer_mat27():
    """v027：在 v025 材質上調色——苔改橄欖綠（降飽和、壓暗、色相略偏黃）、地衣壓亮度；樹皮與裸木法線強度降低（減少全表面等強度凹凸）。"""
    m = _layer_mat25()
    if m.get('v027_tone'):
        return m
    N, Lk = m.node_tree.nodes, m.node_tree.links
    for n in list(N):
        if n.bl_idname == 'ShaderNodeTexImage' and n.image and ('Moss_v018_Albedo' in n.image.name or 'Lichen_v018_Albedo' in n.image.name):
            moss = 'Moss' in n.image.name
            outs = [l.to_socket for l in n.outputs['Color'].links]
            hs = N.new('ShaderNodeHueSaturation')
            hs.inputs['Hue'].default_value = .485 if moss else .5
            hs.inputs['Saturation'].default_value = .78 if moss else .85
            hs.inputs['Value'].default_value = .80 if moss else .82
            Lk.new(n.outputs['Color'], hs.inputs['Color'])
            for s_ in outs:
                Lk.new(hs.outputs['Color'], s_)
        elif n.bl_idname == 'ShaderNodeNormalMap':
            n.inputs['Strength'].default_value *= .55
        elif n.bl_idname == 'ShaderNodeBump':
            n.inputs['Strength'].default_value *= .55
    m['v027_tone'] = True
    return m


ns['_layer_mat25'] = ns['layer_mat']
ns['layer_mat'] = types.FunctionType(layer_mat27.__code__, ns, 'layer_mat')
