# DR10 灰模形體對照：只看輪廓，不看材質。固定鏡位（不跟模型高度走），修改前後用同一組相機、光線、比例。
# 用法（Blender 背景）：
#   blender -b --python art/source/d2-logs-b/gray_dr10.py -- A <輸出資料夾> [build 腳本路徑或 -] [mat]
#   加 mat：同一組鏡位改拍實際材質＋植物（輸出 DR10_<A|B>_mat_*.png）
# 輸出 <資料夾>/DR10_<A|B>_gray_{front,side,tq}.png；1.75 m 白柱放在樹幹右前方當尺。
import bpy, sys, os, math

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
R2 = HERE + '/../d2-roots-b'
# 固定鏡位：兩棵同一組（畫面高約 16 m，地面同一條線）；四分之三也固定，不看模型尺寸
CAMS = {
    'front': ((0, -80, 7.6), (0, 0, 7.6), 180),
    'side': ((80, 0, 7.6), (0, 0, 7.6), 180),
    'tq': ((-11.0, -18.0, 1.7), (0, 0, 6.2), 28),
}
RES = {'front': (768, 1024), 'side': (768, 1024), 'tq': (1024, 1024)}


def _load(p):
    g = {'__file__': p, '__name__': os.path.basename(p)[:-3]}
    exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), g)
    return g


def clay():
    m = bpy.data.materials.get('DR10_Clay') or bpy.data.materials.new('DR10_Clay')
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (.20, .19, .18, 1)
    b.inputs['Roughness'].default_value = .8
    return m


def run(v, out, build_path, mat=False):
    b = _load(build_path)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    b['build'](v, quick=True)
    if mat:                                               # 材質版：同一組鏡位，加植物、用實際材質
        b['dress'](b['VAR'], quick=True)
    pv = _load(R2 + '/preview_dr.py')
    pv['setup'](samples=48 if mat else 32, fog=False)
    if not mat:
        bpy.context.view_layer.material_override = clay()
    V = b['VAR']
    cx, cy = b['axis_xy'](V, 0.0)
    bpy.ops.mesh.primitive_cylinder_add(radius=.22, depth=1.75, location=(cx + 3.2, cy - 2.0, .875))
    os.makedirs(out, exist_ok=True)
    for tag, (frm, to, lens) in CAMS.items():
        frm = (frm[0] + cx, frm[1] + cy, frm[2])
        to = (to[0] + cx, to[1] + cy, to[2])
        pv['shot'](f'{out}/DR10_{v}_{"mat" if mat else "gray"}_{tag}.png', frm, to, lens, res=RES[tag])
    if os.environ.get('DR10_CLOSE'):                      # 近景：斷頂、分岔、幹基根系（鏡位跟著該變體的斷口高度，前後輪一致）
        V = b['VAR']
        # 第六輪：近景鏡位固定在第五輪的斷口高度與主枝位置（世界座標），前後版本同一個鏡頭、同一個高度
        H0, lz, lphi, ax_ = {'A': (5.95, 4.85, .10, ((0, 0, 0), (1.5, .03, 0), (3.5, .10, -.06), (5.5, .06, -.14), (7.0, -.04, -.16), (8.5, -.12, -.16))),
                             'B': (12.15, 7.70, -.30, ((0, 0, 0), (1.5, -.08, .08), (4.0, -.80, .55), (6.5, -1.35, .70), (9.0, -.85, .15), (11.0, .05, -.45),
                                                        (13.0, .75, -.70), (14.5, 1.05, -.75)))}[v]
        L0 = dict(z=lz, phi=lphi)
        Vc = dict(V, axis=ax_)
        hx, hy = b['axis_xy'](Vc, H0)
        lx, ly = b['axis_xy'](Vc, L0['z'])
        close = {'top': ((hx - 3.0, hy - 4.6, H0 + 2.0), (hx, hy, H0 + .7), 35),
                 'fork': ((lx + math.cos(L0['phi']) * 2.5 - 2.5, ly + math.sin(L0['phi']) * 2.5 - 5.5, L0['z'] + 1.5),
                          (lx + math.cos(L0['phi']) * 2.4, ly + math.sin(L0['phi']) * 2.4, L0['z'] + .9), 35),
                 'root': ((cx - 4.5, cy - 6.5, 1.8), (cx, cy, .5), 28),
                 'rootside': ((cx + 7.8, cy - .6, 1.8), (cx, cy, .5), 28),         # 第六輪：根盤側面、背面四分之三
                 'rootback': ((cx + 4.5, cy + 6.5, 1.8), (cx, cy, .5), 28),
                 'topside': ((hx + 5.2, hy - 1.0, H0 + 2.0), (hx, hy, H0 + .7), 35)}
        # 第六輪：層狀菌、地面蘑菇近景：照實際物件的外框中心取景，鏡頭從樹外側、略高處看（不穿進樹幹）
        from mathutils import Vector as _V
        for tag, pref, dist, lift in (('fungi', 'Brackets', 2.2, .55), ('mush', 'DR10_Mush', 1.5, .65)):
            ob = next((o for o in bpy.data.objects if o.name.startswith(pref) and o.type == 'MESH'), None)
            if ob is None:
                continue
            bb = [ob.matrix_world @ _V(c_) for c_ in ob.bound_box]
            if tag == 'fungi':                           # 菌叢太分散：取最低那一叢附近（外框下 40%）
                vs = sorted((ob.matrix_world @ v_.co for v_ in ob.data.vertices), key=lambda q: q.z)
                vs = vs[:max(1, len(vs) // 3)]
                ctr = sum(vs, _V()) / len(vs)
            else:
                ctr = sum(bb, _V()) / 8
            ax0 = _V((*b['axis_xy'](V, max(ctr.z, 0.0)), ctr.z))
            out_ = (ctr - ax0); out_.z = 0
            out_ = out_.normalized() if out_.length > 1e-3 else _V((0, -1, 0))
            side = _V((-out_.y, out_.x, 0)) * .35
            close[tag] = (tuple(ctr + out_ * dist + side + _V((0, 0, lift))), tuple(ctr), 45)
            if tag == 'fungi':                           # 第七輪：俯看菌蓋上面（看環紋），同一叢、固定光線
                close['fungitop'] = (tuple(ctr + out_ * 1.25 + side * .6 + _V((0, 0, 1.45))), tuple(ctr), 45)
        for tag, (frm, to, lens) in close.items():
            pv['shot'](f'{out}/DR10_{v}_{"mat" if mat else "gray"}_{tag}.png', frm, to, lens, res=(1024, 768))
    zs = [(o.matrix_world @ c).z for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith(('Cylinder', 'DR_'))
          for c in [__import__('mathutils').Vector(b_) for b_ in o.bound_box]]
    print('GRAY_DONE', v, out, 'top_z', round(max(zs), 3))


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:]
    run(a[0], a[1], a[2] if len(a) > 2 and a[2] != '-' else HERE + '/build_dr10.py', 'mat' in a[3:])
