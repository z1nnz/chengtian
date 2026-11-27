"""LG01 v005 pair. Run with Blender 5.2: blender -b --factory-startup -P log_model_v005.py"""
import bpy
import math
import os
import random
from mathutils import Vector
from mathutils import noise as mathnoise
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'out')
os.makedirs(OUT, exist_ok=True)
REF = os.path.join(ROOT, 'ref', 'V5_concept_logs_crop.png')
TEX = r'D:\chengtian\4-素材與快取\polyhaven-bark'
random.seed(1901)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1


def image_node(nodes, name, colorspace):
    n = nodes.new('ShaderNodeTexImage')
    n.image = bpy.data.images.load(os.path.join(TEX, name), check_existing=True)
    n.image.colorspace_settings.name = colorspace
    n.image.pack()
    n.extension = 'REPEAT'
    return n


def mix_node(nodes, links, a, b, fac, typ='MIX'):
    n = nodes.new('ShaderNodeMixRGB')
    n.blend_type = typ
    n.inputs[0].default_value = fac
    links.new(a, n.inputs[1]); links.new(b, n.inputs[2])
    return n.outputs[0]


def make_bark():
    m = bpy.data.materials.new('LG01_Bark_Endwood_Lichen')
    m.diffuse_color = (.13, .115, .085, 1)
    m.use_nodes = True
    nd, lk = m.node_tree.nodes, m.node_tree.links
    nd.clear()
    out = nd.new('ShaderNodeOutputMaterial')
    bs = nd.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Metallic'].default_value = 0
    lk.new(bs.outputs[0], out.inputs['Surface'])
    uv = nd.new('ShaderNodeUVMap'); uv.uv_map = 'Longitudinal_UV'
    diff = image_node(nd, 'bark_brown_02_diff_2k.png', 'sRGB')
    normal = image_node(nd, 'bark_brown_02_nor_gl_2k.png', 'Non-Color')
    rough = image_node(nd, 'bark_brown_02_rough_2k.png', 'Non-Color')
    disp = image_node(nd, 'bark_brown_02_disp_2k.png', 'Non-Color')
    lk.new(uv.outputs['UV'], diff.inputs['Vector'])
    lk.new(uv.outputs['UV'], normal.inputs['Vector'])
    lk.new(uv.outputs['UV'], rough.inputs['Vector'])
    lk.new(uv.outputs['UV'], disp.inputs['Vector'])
    # Constrain the scan to the scene's grey-brown palette.  The longitudinal
    # UV still supplies all small bark detail; this ramp avoids bleached bark.
    grey = nd.new('ShaderNodeRGBToBW')
    lk.new(diff.outputs['Color'], grey.inputs['Color'])
    bark_ramp = nd.new('ShaderNodeValToRGB')
    bark_ramp.color_ramp.elements[0].position = .18
    bark_ramp.color_ramp.elements[0].color = (.16, .13, .10, 1)
    bark_ramp.color_ramp.elements[1].position = .76
    bark_ramp.color_ramp.elements[1].color = (.30, .27, .23, 1)
    lk.new(grey.outputs[0], bark_ramp.inputs[0])
    groove_attr = nd.new('ShaderNodeAttribute'); groove_attr.attribute_name = 'BarkGroove'
    groove_dark = nd.new('ShaderNodeRGB'); groove_dark.outputs[0].default_value = (.105,.085,.068,1)
    bark_color = mix_node(nd, lk, bark_ramp.outputs[0], groove_dark.outputs[0], 0)
    lk.new(groove_attr.outputs['Fac'], bark_color.node.inputs[0])
    geo = nd.new('ShaderNodeTexCoord')
    cluster = nd.new('ShaderNodeTexNoise'); cluster.inputs['Scale'].default_value = 2.8
    cluster.inputs['Detail'].default_value = 3
    lk.new(geo.outputs['Object'], cluster.inputs['Vector'])
    # Object coordinates preserve 2--6 cm speckles, independently of the tiled scan.
    micro = nd.new('ShaderNodeTexNoise'); micro.inputs['Scale'].default_value = 20
    micro.inputs['Detail'].default_value = 2.5
    lk.new(geo.outputs['Object'], micro.inputs['Vector'])
    cmp1 = nd.new('ShaderNodeMath'); cmp1.operation = 'GREATER_THAN'; cmp1.inputs[1].default_value = .55
    cmp2 = nd.new('ShaderNodeMath'); cmp2.operation = 'GREATER_THAN'; cmp2.inputs[1].default_value = .63
    lk.new(cluster.outputs['Fac'], cmp1.inputs[0]); lk.new(micro.outputs['Fac'], cmp2.inputs[0])
    lf = nd.new('ShaderNodeMath'); lf.operation = 'MULTIPLY'
    lk.new(cmp1.outputs[0], lf.inputs[0]); lk.new(cmp2.outputs[0], lf.inputs[1])
    pale = nd.new('ShaderNodeRGB'); pale.outputs[0].default_value = (.50, .52, .46, 1)
    col = mix_node(nd, lk, bark_color, pale.outputs[0], 0)
    # Override mix factor with clustered, small lichen flecks.
    moss_attr = nd.new('ShaderNodeAttribute'); moss_attr.attribute_name = 'MossMask'
    lichen_only = nd.new('ShaderNodeMath'); lichen_only.operation = 'MULTIPLY'
    inv_moss = nd.new('ShaderNodeMath'); inv_moss.operation = 'SUBTRACT'
    inv_moss.inputs[0].default_value = 1.0
    lk.new(moss_attr.outputs['Fac'], inv_moss.inputs[1])
    lk.new(lf.outputs[0], lichen_only.inputs[0]); lk.new(inv_moss.outputs[0], lichen_only.inputs[1])
    lk.new(lichen_only.outputs[0], col.node.inputs[0])
    end = nd.new('ShaderNodeAttribute'); end.attribute_name = 'EndMask'
    woodnoise = nd.new('ShaderNodeTexNoise'); woodnoise.inputs['Scale'].default_value = 10
    lk.new(geo.outputs['Object'], woodnoise.inputs['Vector'])
    woodramp = nd.new('ShaderNodeValToRGB')
    woodramp.color_ramp.elements[0].color = (.25, .17, .095, 1)
    woodramp.color_ramp.elements[1].color = (.42, .30, .18, 1)
    lk.new(woodnoise.outputs['Fac'], woodramp.inputs[0])
    rot = nd.new('ShaderNodeAttribute'); rot.attribute_name = 'EndRot'
    rotcolor = nd.new('ShaderNodeRGB'); rotcolor.outputs[0].default_value = (.045, .039, .028, 1)
    ringattr = nd.new('ShaderNodeAttribute'); ringattr.attribute_name = 'EndRing'
    ringdark = nd.new('ShaderNodeRGB'); ringdark.outputs[0].default_value = (.20, .13, .075, 1)
    ringcol = mix_node(nd, lk, woodramp.outputs[0], ringdark.outputs[0], 0)
    lk.new(ringattr.outputs['Fac'], ringcol.node.inputs[0])
    endrad = nd.new('ShaderNodeAttribute'); endrad.attribute_name = 'EndRad'
    ringfreq = nd.new('ShaderNodeMath'); ringfreq.operation = 'MULTIPLY'
    ringfreq.inputs[1].default_value = 115.0
    lk.new(endrad.outputs['Fac'], ringfreq.inputs[0])
    ringsin = nd.new('ShaderNodeMath'); ringsin.operation = 'SINE'
    lk.new(ringfreq.outputs[0], ringsin.inputs[0])
    ringline = nd.new('ShaderNodeMath'); ringline.operation = 'GREATER_THAN'
    ringline.inputs[1].default_value = .82
    lk.new(ringsin.outputs[0], ringline.inputs[0])
    finewood = nd.new('ShaderNodeRGB'); finewood.outputs[0].default_value = (.32,.215,.12,1)
    lined = mix_node(nd, lk, ringcol, finewood.outputs[0], 0)
    lk.new(ringline.outputs[0], lined.node.inputs[0])
    wood_final = mix_node(nd, lk, lined, rotcolor.outputs[0], 0)
    lk.new(rot.outputs['Fac'], wood_final.node.inputs[0])
    mossnoise = nd.new('ShaderNodeTexNoise'); mossnoise.inputs['Scale'].default_value = 5.5
    mossnoise.inputs['Detail'].default_value = 4
    mossfine = nd.new('ShaderNodeTexNoise'); mossfine.inputs['Scale'].default_value = 135
    mossfine.inputs['Detail'].default_value = 3
    lk.new(geo.outputs['Object'], mossnoise.inputs['Vector'])
    lk.new(geo.outputs['Object'], mossfine.inputs['Vector'])
    mr = nd.new('ShaderNodeValToRGB')
    mr.color_ramp.elements[0].position = .31
    mr.color_ramp.elements[0].color = (.05, .07, .015, 1)
    mr.color_ramp.elements[1].position = .77
    mr.color_ramp.elements[1].color = (.20, .23, .06, 1)
    mossbroad = nd.new('ShaderNodeTexNoise'); mossbroad.inputs['Scale'].default_value = 1.8
    mossbroad.inputs['Detail'].default_value = 3
    lk.new(geo.outputs['Object'], mossbroad.inputs['Vector'])
    mossdetail = nd.new('ShaderNodeMixRGB'); mossdetail.blend_type = 'MULTIPLY'
    mossdetail.inputs[0].default_value = .42
    lk.new(mossnoise.outputs['Fac'], mossdetail.inputs[1])
    lk.new(mossbroad.outputs['Fac'], mossdetail.inputs[2])
    lk.new(mossdetail.outputs[0], mr.inputs[0])
    mosscol = mix_node(nd, lk, col, mr.outputs['Color'], 0)
    lk.new(moss_attr.outputs['Fac'], mosscol.node.inputs[0])
    final = mix_node(nd, lk, mosscol, wood_final, 0)
    lk.new(end.outputs['Fac'], final.node.inputs[0])
    lk.new(final, bs.inputs['Base Color'])
    nr = nd.new('ShaderNodeNormalMap'); nr.inputs['Strength'].default_value = .80
    lk.new(normal.outputs['Color'], nr.inputs['Color'])
    bark_bump = nd.new('ShaderNodeBump'); bark_bump.inputs['Strength'].default_value = .52
    bark_bump.inputs['Distance'].default_value = .028
    lk.new(disp.outputs['Color'], bark_bump.inputs['Height'])
    lk.new(nr.outputs[0], bark_bump.inputs['Normal'])
    bump = nd.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = .48
    bump.inputs['Distance'].default_value = .014
    lk.new(mossfine.outputs['Fac'], bump.inputs['Height'])
    lk.new(bark_bump.outputs['Normal'], bump.inputs['Normal'])
    normalmix = mix_node(nd, lk, bark_bump.outputs['Normal'], bump.outputs['Normal'], 0)
    lk.new(moss_attr.outputs['Fac'], normalmix.node.inputs[0])
    lk.new(normalmix, bs.inputs['Normal'])
    mossrough = nd.new('ShaderNodeMapRange')
    mossrough.inputs['From Min'].default_value = .2
    mossrough.inputs['From Max'].default_value = .8
    mossrough.inputs['To Min'].default_value = .48
    mossrough.inputs['To Max'].default_value = .90
    lk.new(mossbroad.outputs['Fac'], mossrough.inputs['Value'])
    roughmix = mix_node(nd, lk, rough.outputs['Color'], mossrough.outputs[0], 0)
    lk.new(moss_attr.outputs['Fac'], roughmix.node.inputs[0])
    lk.new(roughmix, bs.inputs['Roughness'])
    return m


def make_moss():
    m = bpy.data.materials.new('LG01_Olive_Moss')
    m.diffuse_color = (.14, .17, .045, 1)
    m.use_nodes = True
    nd, lk = m.node_tree.nodes, m.node_tree.links
    nd.clear()
    out = nd.new('ShaderNodeOutputMaterial'); bs = nd.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Roughness'].default_value = .98
    bs.inputs['Sheen Weight'].default_value = .18
    lk.new(bs.outputs[0], out.inputs['Surface'])
    tex = nd.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = 22
    tex.inputs['Detail'].default_value = 5
    broad = nd.new('ShaderNodeTexNoise'); broad.inputs['Scale'].default_value = 3
    broad.inputs['Detail'].default_value = 4
    geo = nd.new('ShaderNodeTexCoord')
    lk.new(geo.outputs['Object'], tex.inputs['Vector'])
    lk.new(geo.outputs['Object'], broad.inputs['Vector'])
    ramp = nd.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = .30
    ramp.color_ramp.elements[0].color = (.038, .050, .012, 1)
    ramp.color_ramp.elements[1].position = .72
    ramp.color_ramp.elements[1].color = (.20, .22, .060, 1)
    lk.new(tex.outputs['Fac'], ramp.inputs[0])
    deep = nd.new('ShaderNodeRGB'); deep.outputs[0].default_value = (.055, .070, .019, 1)
    col = mix_node(nd, lk, deep.outputs[0], ramp.outputs[0], 0)
    lk.new(broad.outputs['Fac'], col.node.inputs[0])
    lk.new(col, bs.inputs['Base Color'])
    bump = nd.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = .30
    bump.inputs['Distance'].default_value = .012
    lk.new(tex.outputs['Fac'], bump.inputs['Height'])
    lk.new(bump.outputs['Normal'], bs.inputs['Normal'])
    return m


BARK = make_bark()


def build_log(name, length, r0, r1, nx, nt, lod, shift):
    # Axial centerline and ring radii are intentionally asymmetric.
    vertices, faces, mids, uvs, ends, rots, mosses, grooves, endrings, endrads = [], [], [], [], [], [], [], [], [], []
    # Noise coordinates stretch along X, making branched longitudinal bark grooves.
    # Cross-section coordinates use sin/cos, so the pattern is seamless at 2*pi.
    def n3(x, theta, axial, circum, seed=0):
        return mathnoise.noise(Vector((x*axial+seed, math.cos(theta)*circum,
                                       math.sin(theta)*circum)))
    def add(v, endmask=0, rot=0, moss=0, groove=0, endring=0, endrad=0):
        vertices.append(v); ends.append(endmask); rots.append(rot)
        mosses.append(moss); grooves.append(groove); endrings.append(endring); endrads.append(endrad)
        return len(vertices)-1
    def face(ids, mat, uv):
        faces.append(ids); mids.append(mat); uvs.append(uv)
    def moss_mask(x, theta, groove):
        signed_theta = (theta+math.pi)%(2*math.pi)-math.pi
        edge = 1.05 + .19*n3(x,theta,1.1,2.8,13)
        # Irregular lobes drip down from the moss belt, leaving bark visible between them.
        edge += .23*max(0.0,n3(x,theta,2.4,4.0,31)-.02)
        # Let some clumps reach the camera-facing flank without coating the bottom.
        belt = max(0.0,min(1.0,(edge-abs(signed_theta+.75))/.20+.5))
        belt = belt*belt*(3-2*belt)
        # Broad gaps cut through the upper belt; finer noise breaks the shore line.
        gap = .63 + .44*n3(x,theta,1.4,2.5,7) + .18*n3(x,theta,3.1,4.5,19)
        patch = max(0.0,min(1.0,(gap-.43)/.18))
        patch = patch*patch*(3-2*patch)
        return min(1.0,belt*patch + groove*.09*belt*patch)
    def ring_vertex(x, theta, bulge=0, cap=False):
        t = (x + length/2)/length
        r = r0*(1-t)+r1*t
        bend_y = .19*math.sin(math.pi*t) + .09*math.sin(2.4*math.pi*t+.35)
        bend_z = .055*math.sin(1.6*math.pi*t)
        # 3D low-frequency humps have no axial period or ring-shaped repetition.
        macro = .043*n3(x,theta,1.15,2.2,41) + .026*n3(x,theta,2.0,3.4,53)
        ang = theta + .07*math.sin(3.2*t)
        # 6--10x axial stretch relative to the circumference, with two scales.
        g1 = max(0.0,min(1.0,(n3(x,theta,.65,5.2,67)-.02)/.34))
        g2 = max(0.0,min(1.0,(n3(x,theta,1.25,10.0,79)-.09)/.37))
        furrow = -.043*g1*g1 - .014*g2*g2
        ridge = .012*n3(x,theta,.95,8.1,97)
        swelling = .065*n3(x,theta,.38,1.5,109)
        groove = max(0.0, min(1.0, -furrow/.057))
        moss = moss_mask(x,theta,groove)
        clump = .76 + .24*abs(n3(x,theta,8.5,7.2,127))
        clump += .12*max(0,n3(x,theta,15.5,11.0,137))
        radial = r*(1+swelling) + macro + ridge + furrow + bulge + (.064*moss*clump)
        yy = bend_y + radial*math.sin(ang)
        zz = r0*.78 + bend_z + radial*.91*math.cos(ang)
        if math.cos(ang) < -.71:
            zz = max(zz, -.025 + .008*n3(x,theta,1.8,7.0,149))
        return (x, yy, zz)
    def torn_plate(theta):
        phase = (8*theta+.38+math.pi)%(2*math.pi)-math.pi
        d = abs(phase)/8
        weight = max(0.0, min(1.0, (.155-d)/.075))
        weight = weight*weight*(3-2*weight)
        sector = int(round((8*theta+.38)/(2*math.pi))) % 8
        return (.12,.25,.17,.32,.21,.34,.15,.27)[sector]*weight
    # Side skin. UV U around the cross section, V down the length.
    rings = []
    for i in range(nx+1):
        t = i/nx; x = -length/2 + length*t
        rr = []
        for j in range(nt):
            th = 2*math.pi*j/nt
            xx = x + (.018 if i in (0,nx) else 0)*math.sin(th*7+i)
            # Eight broad, axial tears grow directly from the end rim.  The cap
            # annuli share these vertices, keeping the entire asset watertight.
            if i == nx:
                xx += torn_plate(th)
            groove = max(0.0,min(1.0,(.043*max(0.0,min(1.0,(n3(xx,th,.65,5.2,67)-.02)/.34))**2+.014*max(0.0,min(1.0,(n3(xx,th,1.25,10.0,79)-.09)/.37))**2)/.057))
            rr.append(add(ring_vertex(xx, th), moss=moss_mask(xx,th,groove), groove=.50*groove))
        rings.append(rr)
    for i in range(nx):
        for j in range(nt):
            k = (j+1)%nt
            face((rings[i][j], rings[i+1][j], rings[i+1][k], rings[i][k]), 0,
                 ((j/nt, i*length/nx/2.5), (j/nt, (i+1)*length/nx/2.5),
                  ((j+1)/nt, (i+1)*length/nx/2.5), ((j+1)/nt, i*length/nx/2.5)))
    # Jagged rim and recessed, uneven wood interior. Cap is a disk, not a flat lid.
    for side, ir in ((-1,0),(1,nx)):
        x0 = side*length/2
        rim = rings[ir]
        for idx in rim: endrads[idx]=1.0
        inner = []; core = []; rotcore = []
        for j in range(nt):
            th = 2*math.pi*j/nt
            tip = torn_plate(th) if side > 0 else 0.0
            p = Vector(ring_vertex(x0 + tip*.20 - side*(.022 + .024*math.sin(9*th+1)**2), th))
            cy = .02; cz = r0*.78
            p.y = cy + (p.y-cy)*.94; p.z = cz + (p.z-cz)*.94
            inner.append(add(tuple(p), 1, .08, endring=.12, endrad=.94))
            p2=Vector(p); p2.x=x0 - side*(.057+.015*math.sin(7*th));
            p2.y=cy+(p.y-cy)*.67; p2.z=cz+(p.z-cz)*.67
            core.append(add(tuple(p2),1,.12, endring=.45, endrad=.63))
            p3=Vector(p2); p3.x=x0-side*(.15+.012*math.sin(5*th+1))
            p3.y=cy+(p.y-cy)*.26; p3.z=cz+(p.z-cz)*.26
            rotcore.append(add(tuple(p3),1,.92,endring=.72,endrad=.16))
        center = add((x0-side*.19, .01, r0*.78), 1, 1, endring=.9,endrad=0)
        for j in range(nt):
            k=(j+1)%nt
            ids = (rim[k],rim[j],inner[j],inner[k]) if side > 0 else (rim[j],rim[k],inner[k],inner[j])
            face(ids,0,((0,0),(1,0),(1,1),(0,1)))
            ids2 = (inner[k],inner[j],core[j],core[k]) if side > 0 else (inner[j],inner[k],core[k],core[j])
            face(ids2,0,((0,0),(1,0),(1,1),(0,1)))
            ids3 = (core[k],core[j],rotcore[j],rotcore[k]) if side > 0 else (core[j],core[k],rotcore[k],rotcore[j])
            face(ids3,0,((0,0),(1,0),(1,1),(0,1)))
            ids4 = (rotcore[k],rotcore[j],center) if side > 0 else (rotcore[j],rotcore[k],center)
            face(ids4,0,((0,0),(1,0),(.5,.5)))
    # The closed torn rim replaces v002's floating needle fibers and open branch stubs.
    bottom=min(v[2] for v in vertices)
    vertices=[(x,y,z-bottom) for x,y,z in vertices]
    mesh=bpy.data.meshes.new(name+'_Mesh')
    mesh.from_pydata(vertices, [], faces); mesh.update()
    uv=mesh.uv_layers.new(name='Longitudinal_UV')
    attr=mesh.attributes.new('EndMask','FLOAT','POINT')
    for i,val in enumerate(ends): attr.data[i].value=val
    attr2=mesh.attributes.new('EndRot','FLOAT','POINT')
    for i,val in enumerate(rots): attr2.data[i].value=val
    attr3=mesh.attributes.new('MossMask','FLOAT','POINT')
    for i,val in enumerate(mosses): attr3.data[i].value=val
    groove_attr=mesh.attributes.new('BarkGroove','FLOAT','POINT')
    for i,val in enumerate(grooves): groove_attr.data[i].value=val
    attr4=mesh.attributes.new('EndRing','FLOAT','POINT')
    for i,val in enumerate(endrings): attr4.data[i].value=val
    attr5=mesh.attributes.new('EndRad','FLOAT','POINT')
    for i,val in enumerate(endrads): attr5.data[i].value=val
    for pi,p in enumerate(mesh.polygons):
        p.material_index=mids[pi]
        # Tear lips keep a crisp edge; the inner heartwood remains smooth.
        p.use_smooth = pi < nx*nt or (pi-nx*nt) % 4 != 0
        for li, coord in zip(p.loop_indices,uvs[pi]): uv.data[li].uv=coord
    mesh.materials.append(BARK)
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    ob.location=(0,shift,0)
    ob['lod_level']=lod
    ob['nominal_length_m']=length
    ob['nominal_diameter_start_m']=r0*2
    ob['nominal_diameter_end_m']=r1*2
    # Approximate the camera-visible hemisphere (front and upper surface).
    samples=[moss_mask(-length/2+length*i/160, -2.7+math.pi*j/80, 0)
             for i in range(160) for j in range(80)]
    ob['visible_moss_coverage']=sum(v>.5 for v in samples)/len(samples)
    return ob


A=build_log('LG01_A_LOD0',8,.65,.475,112,100,0,-.80)
B=build_log('LG01_B_LOD0',6.5,.525,.40,90,92,0,1.0)
A1=build_log('LG01_A_LOD1',8,.65,.475,68,62,1,-.80)
B1=build_log('LG01_B_LOD1',6.5,.525,.40,57,56,1,1.0)
for ob in (A,A1):
    ob.rotation_euler.z=math.radians(18)
for ob in (B,B1):
    ob.location.x=-.35
    ob.location.y=1.85
    ob.location.z=.42
    ob.rotation_euler.z=math.radians(30)
for ob in (A1,B1): ob.hide_render=True; ob.hide_set(True)

def tris(ob): return sum(len(p.vertices)-2 for p in ob.data.polygons)
for ob in (A,B,A1,B1):
    print('LG01_STATS',ob.name,'tris',tris(ob),'dimensions',tuple(round(x,3) for x in ob.dimensions),'materials',len(ob.data.materials),'visible_moss_coverage',round(ob['visible_moss_coverage'],3))

# Foggy overcast review stage. Stage pieces are removed before saving the asset file.
ground=bpy.data.meshes.new('ReviewGroundMesh')
ground.from_pydata([(-100,-100,.14),(100,-100,.14),(100,100,.14),(-100,100,.14)],[],[(0,1,2,3)])
ground.update(); go=bpy.data.objects.new('ReviewGround',ground); bpy.context.collection.objects.link(go)
gm=bpy.data.materials.new('Review_Ground'); gm.diffuse_color=(.08,.06,.04,1); gm.use_nodes=True
gm.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.08,.06,.04,1)
ground.materials.append(gm)
world=bpy.data.worlds.new('Grey_Foggy_Sky'); scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.55,.55,.55,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=1
sun=bpy.data.lights.new('Weak_Overcast_Sun','SUN'); sun.energy=.8; sun.angle=.7
so=bpy.data.objects.new('Weak_Overcast_Sun',sun); bpy.context.collection.objects.link(so)
so.rotation_euler=(math.radians(30),math.radians(-30),math.radians(-30))
camdata=bpy.data.cameras.new('Review_Camera'); cam=bpy.data.objects.new('Review_Camera',camdata)
bpy.context.collection.objects.link(cam); scene.camera=cam; camdata.type='PERSP'; camdata.lens=38

def aim(pos,target,scale):
    cam.location=pos
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    camdata.lens=scale

scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.cycles.use_denoising=True
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG'
scene.render.resolution_x=960; scene.render.resolution_y=540; scene.render.resolution_percentage=100
scene.render.film_transparent=False

shots=[
    ('check_side.png',(2.4,-5.5,1.65),(0,.10,.58),22),
    ('check_top.png',(0,-.15,9.5),(0,0,.35),34),
    ('check_end.png',(6.2,-1.4,1.15),(4.0,-.65,.60),45),
]
for filename,pos,target,scale in shots:
    aim(pos,target,scale)
    scene.render.filepath=os.path.join(OUT,filename)
    bpy.ops.render.render(write_still=True)
    print('LG01_RENDER',filename)

# Side-by-side comparison with the provided concept; all image work stays in Blender.
left=bpy.data.images.load(REF,check_existing=True)
right=bpy.data.images.load(os.path.join(OUT,'check_side.png'),check_existing=True)
def rgba(img):
    data=np.empty(len(img.pixels),dtype=np.float32)
    img.pixels.foreach_get(data)
    return data.reshape((img.size[1],img.size[0],4))
la,ra=rgba(left),rgba(right)
H,W=540,960
ys=(np.linspace(0,la.shape[0]-1,H)).astype(int)
xs=(np.linspace(0,la.shape[1]-1,W)).astype(int)
ll=la[ys[:,None],xs[None,:],:]
ys=(np.linspace(0,ra.shape[0]-1,H)).astype(int)
xs=(np.linspace(0,ra.shape[1]-1,W)).astype(int)
rr=ra[ys[:,None],xs[None,:],:]
combined=np.concatenate((ll,rr),axis=1)
ci=bpy.data.images.new('LG01_Concept_Compare',width=W*2,height=H,alpha=True)
ci.pixels.foreach_set(combined.ravel())
ci.filepath_raw=os.path.join(OUT,'check_compare.png'); ci.file_format='PNG'; ci.save()
print('LG01_RENDER check_compare.png')

# The delivered blend holds the two asset LODs and packed textures, no review stage.
for ob in (go,so,cam): bpy.data.objects.remove(ob,do_unlink=True)
scene.camera=None
scene.render.filepath=''
path=os.path.join(OUT,'LG01_MossLog_v005.blend')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=path)
print('LG01_SAVED',path)
