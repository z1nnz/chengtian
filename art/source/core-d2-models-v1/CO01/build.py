"""CO01 被挖的坑；依已保存並檢視的三視圖製作。"""
import bpy, bmesh, math, random, sys, json, os
import numpy as np
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'art/source/village-houses-b'))
import ti_core as core
import cr_parts as cp
import cr_mats as cm
import fr_mats as fm
import ti_pipeline as pl

AID = 'CO01_ExcavatedPit'
OUT = ROOT / 'art/exports/core-d2-models-v1/CO01'
PRE = ROOT / 'art/previews/core-d2-models-v1/CO01'
OUT.mkdir(parents=True, exist_ok=True)
PRE.mkdir(parents=True, exist_ok=True)
assert (ROOT / 'art/references/core-d2-models-v1/CO01/turnaround.png').is_file()
bpy.ops.wm.read_factory_settings(use_empty=True)
core.reset_state(AID)

earth = cm.packed_earth('M_CO01_DampEarth', moss=.18, strata_amt=.56)
loam = fm.forest_earth('M_CO01_ForestLoam', moss=.55)
stone = cm.stone('M_CO01_Stone', light=(.34,.34,.30), dark=(.16,.17,.16), moss=.45)
bark = fm.bark('M_CO01_ExposedRoot', moss=.72)
cut = cm.wood('M_CO01_FreshCut', dark=(.24,.16,.09), light=(.57,.43,.26), moss=False, grey=.04)
moss = cm.moss_tuft('M_CO01_Moss')

# 一片連續的封底放射面：外緣地表、隆起坑沿、陡峭土壁、淺凹坑底。
# z=0 是世界地表；匯出前轉為坑底 pivot，放置時須將物件下降 0.6 m。
N = 80
rings = [(.12,-.60),(.42,-.59),(1.22,-.54),(1.56,-.40),(1.82,-.12),
         (1.98,.16),(2.14,.19),(2.29,.02)]
verts=[]; faces=[]
for k,(rad,z0) in enumerate(rings):
    for i in range(N):
        a=2*math.pi*i/N
        wig=(.11*math.sin(5*a+.3)+.06*math.sin(13*a+1.2)+.025*math.sin(29*a+2.1))*(.3+.7*k/7) if k>=3 else 0
        r=rad+wig
        mound=.12*max(0,math.sin(a-.08))**7 if k in (5,6) else 0
        z=z0 + mound + ((.035*math.sin(9*a+1.3)+.024*math.cos(23*a))*(.4+.6*k/7) if k>=3 else 0)
        z+=.018*math.sin(4.7*r+6*a) if 3<=k<5 else 0
        verts.append((r*math.cos(a),r*math.sin(a),z))
for k in range(len(rings)-1):
    for i in range(N):
        j=(i+1)%N
        faces.append((k*N+i,(k+1)*N+i,(k+1)*N+j,k*N+j))
# 封閉底面置於可埋入的深度，避免底部透視時開洞。
base=len(verts)
for i in range(N):
    a=2*math.pi*i/N
    verts.append((2.29*math.cos(a),2.29*math.sin(a),-.68))
for i in range(N):
    j=(i+1)%N
    faces.append((7*N+i,base+i,base+j,7*N+j))
faces.append(tuple(base+i for i in range(N-1,-1,-1)))
center=len(verts);verts.append((0,0,-.60))
for i in range(N):
    faces.append((center,i,(i+1)%N))
pit=core.mesh('Excavated_Earth',verts,faces,earth,smooth=False,detail=0)

R=random.Random(1101)
# 三團相互重疊的濕土高堆，讓坑後側有連續且不等高的翻土輪廓。
for i,(a,r,sx,sy,sz) in enumerate(((.62,2.00,.49,.32,.19),(1.42,2.01,.58,.34,.23),
                                  (2.41,2.01,.43,.30,.17))):
    bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=2,radius=1)
    for v in bm.verts:
        q=v.co.copy(); und=1+.13*math.sin(7*q.x+3*i)+.09*math.cos(9*q.y-2*i)
        v.co=Vector((q.x*sx*und,q.y*sy*und,q.z*sz*und))
    me=bpy.data.meshes.new(f'Turned_Earth_Mound_{i:02d}');bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(ob)
    core.finish(ob,ob.name,loam,detail=0)
    ob.location=(r*math.cos(a),r*math.sin(a),.14)
# 土堆偏向畫面後方，前緣留低；每塊是有體積且嵌在土壁的破碎土團。
for i in range(55):
    a=R.uniform(.02,math.pi*.99) if i<42 else R.uniform(0,math.tau)
    r=R.uniform(1.84,2.16)
    x,y=r*math.cos(a),r*math.sin(a)
    s=R.uniform(.12,.28); h=R.uniform(.07,.19)*(1.4 if i<42 else .75)
    # 粗塊以有棱角的不規則二十面體做，避免一圈方磚的外觀。
    bm=bmesh.new(); bmesh.ops.create_icosphere(bm,subdivisions=1,radius=1)
    rr=random.Random(1200+i)
    for v in bm.verts:
        q=v.co.copy(); jitter=rr.uniform(.82,1.17)
        v.co=Vector((q.x*s*.65*jitter,q.y*s*.52*jitter,q.z*h*.72*jitter))
    me=bpy.data.meshes.new(f'Earth_Clod_{i:02d}');bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(f'Earth_Clod_{i:02d}',me);bpy.context.scene.collection.objects.link(ob)
    core.finish(ob,ob.name,loam,detail=1)
    ob.location=(x,y,.02+h*.16)

# 破石大小錯落，讓側壁與坑沿的受力位置可讀。
for i in range(25):
    a=R.uniform(0,math.tau); r=R.uniform(1.65,2.23)
    x,y=r*math.cos(a),r*math.sin(a)
    s=R.uniform(.07,.23)
    z=-.43 if r<1.78 else (-.13 if r<1.95 else -.06)
    if i==24: z-=.14
    cp.rbox(f'Rock_{i:02d}',(x,y,z),(s*1.2,s*.84,s*.62),stone,
            r=.012,amp=.009,chips=8,hew=10,seed=1300+i,div=.045,
            rot=(R.uniform(-.2,.2),R.uniform(-.2,.2),a),detail=1)

# 三條半埋的粗根在坑緣斷開，新增短段淺色木質斷面。
root_paths=[[( -2.20,-.95,.10),(-2.05,-.68,.22),(-1.85,-.37,.18),(-1.62,-.18,-.10)],
            [(2.20,.91,.09),(2.05,.65,.22),(1.86,.42,.19),(1.68,.30,-.02)],
            [(-2.20,1.14,.10),(-2.03,.99,.17),(-1.82,.85,.16),(-1.67,.80,-.02)]]
for i,path in enumerate(root_paths):
    cp.log(f'Root_{i:02d}',path,.11 if i<2 else .075,bark,seg=12,lump=.13,seed=1400+i,detail=0,step=.095)
    end=Vector(path[-1]); before=Vector(path[-2]); axis=(end-before).normalized()
    cp.log(f'Root_FreshBreak_{i:02d}',[tuple(end-axis*.012),tuple(end+axis*.035)],
           .092 if i<2 else .062,cut,seg=12,lump=.03,seed=1450+i,detail=0,step=.03)

for i in range(18):
    a=R.uniform(0,math.tau); r=R.uniform(1.86,2.20)
    cp.tuft(f'Moss_{i:02d}',(r*math.cos(a),r*math.sin(a),-.05 if i==3 else .09),R.uniform(.035,.075),moss,
            seed=1500+i,detail=2)

for ob in core.S['parts']:
    for face in ob.data.polygons: face.use_smooth=(ob is pit)

# 共用已交付 CO02 的烘焙與 LOD 匯出流程。
source=(ROOT/'art/source/core-ruins-v2/build_co02.py').read_text(encoding='utf-8-sig')
tail=source[source.index('# 灰模：'):]
tail=tail.replace("(3.2,-5.5,3.0)","(5.2,-7.5,5.1)")
tail=tail.replace("(0,0,1.2)","(0,0,-.12)")
tail=tail.replace("cam.data.ortho_scale=3.8","cam.data.ortho_scale=6.6")
tail=tail.replace('CO02_clay.png','CO01_clay.png').replace('CO02_hero.png','CO01_hero.png')
tail=tail.replace("'古林碑'","'被挖的坑'").replace("'D4'","'D2'")
tail=tail.replace('無文字；斜鑿槽使用 Boolean 真切割；AI 三視圖先於建模保存。',
                  '外徑約 4.8 m、坑深約 0.6 m；匯出 pivot 置於最低處，地表放置時模型下移約 0.68 m，且需對地形開孔；AI 三視圖已先檢視並保存。')
tail=tail.replace('CO02_INFO','CO01_INFO')
tail=tail.replace("ROOT/'art/source/core-ruins-v2'", "ROOT/'art/source/core-d2-models-v1/CO01'")
exec(compile(tail,str(ROOT/'art/source/core-ruins-v2/build_co02.py'),'exec'))
