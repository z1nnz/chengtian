"""CO02 古林碑 v002。先有 AI 三視圖，灰模審查後才烘焙。"""
import bpy, bmesh, math, sys, json, os
import numpy as np
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'art/source/village-houses-b'))
import ti_core as core
import cr_parts as cp
import cr_mats as cm
import vl_mats as vm
import ti_pipeline as pl

AID='CO02_OldForestStele'
OUT=ROOT/'art/exports/core-ruins-v2'/AID
PRE=ROOT/'art/previews/core-ruins-v2'/AID
OUT.mkdir(parents=True,exist_ok=True); PRE.mkdir(parents=True,exist_ok=True)
assert (ROOT/'art/references/core-ruins-v2/CO02/CO02_threeview_chosen.png').is_file()
bpy.ops.wm.read_factory_settings(use_empty=True)
core.reset_state(AID)
mainmat=cm.stone('CO02_ChiselledGranite',light=vm.STONE[2],dark=vm.STONE[1],ochre=vm.STONE[0],moss=.45,crack=.55,lichen=.33)
base_mat=cm.stone('CO02_MossyBase',light=vm.STONE[2],dark=vm.STONE[1],ochre=vm.STONE[0],moss=.95,crack=.65,lichen=.55)
moonmat=cm.stone('CO02_MoonCut',light=vm.STONE[2],dark=vm.STONE[1],ochre=vm.STONE[0],moss=.08,crack=.2,lichen=.0)
# 主碑用真正的鑿平面、缺角與略斜的收分。正面朝 -Y。
PROFILE=[(-.93,-.015,-.010),(-.67,.024,.006),(-.42,-.018,-.009),(-.15,.030,.010),(.12,-.026,-.004),(.38,.022,.007),(.67,-.019,-.012),(.93,.011,.004)]
def rough_profile(q):
    for i in range(len(PROFILE)-1):
        lo,hi=PROFILE[i],PROFILE[i+1]
        if q.z<=hi[0] or i==len(PROFILE)-2:
            t=max(0,min(1,(q.z-lo[0])/(hi[0]-lo[0])))
            edge=lo[1]*(1-t)+hi[1]*t
            face=lo[2]*(1-t)+hi[2]*t
            if abs(q.x)>.30:q.x+=math.copysign(edge,q.x)
            q.y+=face
            break
slab=cp.rbox('Stone_Main',(.02,.01,1.40),(.86,.41,1.95),mainmat,r=.028,amp=.016,freq=11,chips=54,hew=58,seed=202,div=.075,taper=(.80,.88),skew=(.07,.025),warp=rough_profile,rot=(.012,.035,-.022),detail=0)
# 正面三道斜鑿槽：Boolean 切進石材 7–10 cm，不是畫線。
def gouge(name,z,angle,thick,depth,x=0,span=(-.62,.62)):
    # 非等寬折線切口；封閉的立體切削體深入碑面，石緣留下不規則缺損。
    xs=tuple(span[0]+(span[1]-span[0])*i/8 for i in range(9))
    offs=(.006,-.013,.018,-.011,.009,-.017,.012,-.010,.006)
    low=[];high=[]
    for i,xx in enumerate(xs):
        mid=z+math.tan(angle)*(xx-x)+offs[(i+int(z*10))%len(offs)]
        width=thick*(1.15 if i in (2,5) else .82 if i in (1,7) else 1.0)
        low.append((xx,mid-width*.5));high.append((xx,mid+width*.5))
    poly=low+list(reversed(high));n=len(poly)
    verts=[(xx,-.43,zz) for xx,zz in poly]+[(xx,-.11,zz) for xx,zz in poly]
    faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
    for i in range(n):j=(i+1)%n;faces.append((j,i,n+i,n+j))
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(mainmat)
    cut=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(cut)
    bpy.ops.object.select_all(action='DESELECT');slab.select_set(True)
    bpy.context.view_layer.objects.active=slab
    m=slab.modifiers.new(name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cut,do_unlink=True)
for args in [('Chisel_1',.73,-.25,.085,.20,-.08,(-.53,.31)),('Chisel_2',1.15,-.48,.11,.23,.07,(-.54,.54)),('Chisel_3',1.63,-.33,.068,.21,-.10,(-.37,.46))]:
    gouge(*args)
# 石座由逐塊粗鑿石組成，部分埋入地表，錯縫。
blocks=[(-.39,-.18,.19,.49,.40,.36,-.10),(.14,-.24,.19,.55,.43,.34,.04),(.46,.11,.15,.40,.49,.29,.16),(-.31,.22,.15,.50,.40,.31,-.18),(.04,.32,.13,.49,.36,.27,.08),(-.56,.03,.105,.27,.35,.22,.12),(.55,-.16,.11,.30,.28,.22,-.11)]
for i,(x,y,z,w,d,h,ang) in enumerate(blocks):
    cp.rbox(f'Base_Stone_{i+1:02d}',(x,y,z),(w,d,h),base_mat,r=.025,amp=.013,freq=11,chips=12,hew=16,seed=300+i,div=.065,taper=(.78,.80),skew=(ang*.14,ang*.09),rot=(.02,ang*.2,ang),detail=0 if i<5 else 1)
mossmat=cm.moss_tuft('CO02_JointMoss')
for i,(x,y,z) in enumerate(((-.18,-.39,.29),(.30,-.39,.25),(-.43,.29,.20),(.51,.18,.22),(-.26,.25,.27))):
    cp.tuft(f'Moss_Joint_{i+1:02d}',(x,y,z),.055,mossmat,seed=600+i)
# 小缺月記號是一個淺浮雕，只有石面小面積；它不是碑文。
bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=.065,depth=.012,location=(.19,-.160,1.99),rotation=(math.pi/2,0,0))
moon=bpy.context.object;moon.name='Moon_Mark'
bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=.054,depth=.032,location=(.218,-.160,1.99),rotation=(math.pi/2,0,0))
mooncut=bpy.context.object
bpy.ops.object.select_all(action='DESELECT');moon.select_set(True);bpy.context.view_layer.objects.active=moon
m=moon.modifiers.new('Moon_Inner_Cut','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=mooncut
bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(mooncut,do_unlink=True)
core.finish(moon,'Moon_Mark',moonmat,detail=2)
for ob in core.S['parts']:
    if ob.name!='Moon_Mark':
        for face in ob.data.polygons:face.use_smooth=False
# 灰模：在上材質與烘焙之前保留檢視圖。
def camera_and_light():
    bpy.ops.object.camera_add(location=(3.2,-5.5,3.0))
    cam=bpy.context.object;cam.name='Review_Camera';direction=Vector((0,0,1.2))-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.8
    bpy.context.scene.camera=cam
    bpy.ops.object.light_add(type='AREA',location=(2.0,-3.0,5.0));bpy.context.object.data.energy=850;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=4
    bpy.context.scene.render.resolution_x=1200;bpy.context.scene.render.resolution_y=1200;bpy.context.scene.render.resolution_percentage=100
camera_and_light()
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.55,.56,.55);scene.display.shading.background_type='VIEWPORT';scene.display.shading.background_color=(.16,.17,.17)
scene.render.filepath=str(PRE/'CO02_clay.png');bpy.ops.render.render(write_still=True)
if os.environ.get('CO02_CLAY_ONLY')=='1': sys.exit(0)
# 依 Josh 的流程併組、圖集、烘焙、LOD。先拿掉小件才減面。
pl.normalise();pl.join_groups()
for obj in core.S['lod0'].values():
    bm=bmesh.new();bm.from_mesh(obj.data);large=[face for face in bm.faces if len(face.verts)>4]
    if large:bmesh.ops.triangulate(bm,faces=large)
    bm.to_mesh(obj.data);bm.free()
pl.uv_atlas(size=2048,objs=list(core.S['lod0'].values()))
pl.bake(OUT/'Textures',2048)
# Eli 的輔助烘焙清單：AO、物件法線、邊緣、位置，再合成 Albedo／ORM／MaskURP。
def aux_bake(label,kind):
    size=2048
    img=bpy.data.images.new(f'{AID}_{label}',width=size,height=size,alpha=True,float_buffer=False)
    img.colorspace_settings.name='Non-Color'
    lod0=list(core.S['lod0'].values())[0]
    bpy.ops.object.select_all(action='DESELECT');lod0.select_set(True);bpy.context.view_layer.objects.active=lod0
    edits=[]
    for mat in lod0.data.materials:
        if mat is None:continue
        nt=mat.node_tree;out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
        old=out.inputs['Surface'].links[0].from_socket
        target=nt.nodes.new('ShaderNodeTexImage');target.image=img;nt.nodes.active=target
        nodes=[target]
        if kind in ('POINT','POSITION'):
            geo=nt.nodes.new('ShaderNodeNewGeometry');em=nt.nodes.new('ShaderNodeEmission');nodes.extend([geo,em])
            if kind=='POINT':nt.links.new(geo.outputs['Pointiness'],em.inputs['Color'])
            else:
                mul=nt.nodes.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=(.35,.40,.40)
                add=nt.nodes.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=(.5,.5,0)
                nt.links.new(geo.outputs['Position'],mul.inputs[0]);nt.links.new(mul.outputs[0],add.inputs[0]);nt.links.new(add.outputs[0],em.inputs['Color']);nodes.extend([mul,add])
            nt.links.new(em.outputs[0],out.inputs['Surface'])
        edits.append((nt,out,old,nodes))
    scene.render.bake.margin=8;scene.render.bake.use_clear=True;scene.cycles.samples=16
    if kind=='AO':bpy.ops.object.bake(type='AO')
    elif kind=='OBJECT_NORMAL':bpy.ops.object.bake(type='NORMAL',normal_space='OBJECT')
    else:bpy.ops.object.bake(type='EMIT')
    for nt,out,old,nodes in edits:
        nt.links.new(old,out.inputs['Surface'])
        for n in nodes:nt.nodes.remove(n)
    path=OUT/'Textures'/f'{AID}_{label}.png';img.filepath_raw=str(path);img.file_format='PNG';img.save()
    print('AUX_BAKED',label,flush=True)
    return img
AO=aux_bake('AO','AO')
ON=aux_bake('ObjectNormal','OBJECT_NORMAL')
ED=aux_bake('Pointiness','POINT')
POS=aux_bake('Position','POSITION')
def pixels(img):return np.array(img.pixels[:],dtype=np.float32).reshape(2048,2048,4)
def save_map(label,arr,color):
    img=bpy.data.images.new(f'{AID}_{label}_Final',width=2048,height=2048,alpha=True,float_buffer=False)
    img.colorspace_settings.name='sRGB' if color else 'Non-Color'
    img.pixels.foreach_set(np.clip(arr,0,1).astype(np.float32).ravel())
    path=OUT/'Textures'/f'{AID}_{label}.png';img.filepath_raw=str(path);img.file_format='PNG';img.save();return path
base=pixels(bpy.data.images.load(str(core.S['tex']['BaseColor']),check_existing=True))
rough=pixels(bpy.data.images.load(str(core.S['tex']['Roughness']),check_existing=True))[...,0]
metal=pixels(bpy.data.images.load(str(core.S['tex']['Metallic']),check_existing=True))[...,0]
ao=pixels(AO)[...,0];edge=pixels(ED)[...,0];pos=pixels(POS)[...,2]
albedo=base.copy();albedo[...,:3]*=(.76+.24*ao)[...,None]
albedo[...,:3]*=(.97+.06*edge)[...,None]
albedo[...,:3]*=(1-.07*np.clip((.24-pos)*4,0,1))[...,None]
core.S['tex']['BaseColor']=save_map('Albedo',albedo,True)
bpy.data.images[f'{AID}_Albedo_Final'].name=f'{AID}_BaseColor'
one=np.ones_like(ao);zero=np.zeros_like(ao)
core.S['tex']['ORM']=save_map('ORM',np.stack([ao,rough,metal,one],axis=2),False)
core.S['tex']['MaskURP']=save_map('MaskURP',np.stack([metal,ao,zero,1-rough],axis=2),False)
pl.make_lods();pl.export_materials()
pl.export_fbx(OUT/f'{AID}_v002.fbx')
# GLB 只含 LOD0，能直接預覽。
bpy.ops.object.select_all(action='DESELECT')
for ob in core.S['lods'][0].values():ob.select_set(True)
bpy.context.view_layer.objects.active=list(core.S['lods'][0].values())[0]
bpy.ops.export_scene.gltf(filepath=str(OUT/f'{AID}_v002.glb'),export_format='GLB',use_selection=True,export_apply=True)
# 記錄版本、尺寸、LOD、限制，避免誤稱已在 Unity 驗證。
lo,hi=pl.eval_bounds(list(core.S['lods'][0].values()))
info={'asset':AID,'version':'v002','name_zh':'古林碑','slot':'D4','units':'meters','front':'-Y','dimensions_m':[round(hi[i]-lo[i],3) for i in range(3)],'lod_triangles':{f'LOD{lv}':sum(pl.tri_count(o) for o in group.values()) for lv,group in core.S['lods'].items()},'status':{'Exported':True,'Imported':False,'VisuallyVerified':True,'InGameVerified':False},'note':'無文字；斜鑿槽使用 Boolean 真切割；AI 三視圖先於建模保存。'}
(OUT/'model_info.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf8')
# 正式材質預覽僅顯示 LOD0。
for lv,groups in core.S['lods'].items():
    for ob in groups.values():ob.hide_render=(lv!=0)
for ob in core.S['parts']:ob.hide_render=True
scene.render.engine='BLENDER_EEVEE';scene.world=bpy.data.worlds.new('Review_World');scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.22,.23,.23,1);scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.65;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(PRE/'CO02_hero.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/source/core-ruins-v2'/f'{AID}_v002.blend'))
print('CO02_INFO',json.dumps(info,ensure_ascii=False),flush=True)











