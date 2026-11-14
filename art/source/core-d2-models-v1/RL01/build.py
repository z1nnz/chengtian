"""RL01 兩種苔蕈朽木；依選定 AI 三視圖及 D2 V5/V6 建模。"""
import bpy, bmesh, math, random, sys, json, os
import numpy as np
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'art/source/village-houses-b'))
import ti_core as core
import cr_parts as cp
import cr_mats as cm
import fr_parts as FP
import fr_mats as fm
import ti_pipeline as pl

assert (ROOT/'art/references/core-d2-models-v1/RL01/turnaround.png').is_file()
OUT=ROOT/'art/exports/core-d2-models-v1/RL01'
PRE=ROOT/'art/previews/core-d2-models-v1/RL01'
OUT.mkdir(parents=True,exist_ok=True)
PRE.mkdir(parents=True,exist_ok=True)
source=(ROOT/'art/source/core-ruins-v2/build_co02.py').read_text(encoding='utf-8-sig')
SPECS=[('A',4.45),('B',3.25)]
only=os.environ.get('RL01_ONLY')

for variant,length in SPECS:
    if only and variant!=only: continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    AID=f'RL01_RottenLog_{variant}'
    core.reset_state(AID)
    bark=fm.bark(f'M_{AID}_RottenBark',tone=1.14,moss=1.17,ground_h=.15)
    exposed=fm.root_tip(f'M_{AID}_ExposedWood')
    weathered=cm.wood(f'M_{AID}_WeatheredWood',dark=(.065,.047,.032),
                       light=(.19,.145,.105),moss=False,grey=.23)
    rotwood=cm.wood(f'M_{AID}_RotInterior',dark=(.018,.014,.009),light=(.045,.035,.022),moss=False,grey=.15)
    capmat=cm.wood(f'M_{AID}_BrownCap',dark=(.10,.052,.028),light=(.31,.18,.09),moss=False,grey=.08)
    stemmat=cm.wood(f'M_{AID}_MushroomStem',dark=(.21,.16,.11),light=(.47,.36,.23),moss=False,grey=.05)
    rng=random.Random(4100+ord(variant))
    segments=[(-length/2,length/2)] if variant=='A' else [(-length/2,-.12),(.12,length/2)]
    for si,(x0,x1) in enumerate(segments):
        span=x1-x0
        pts=[(x0,.02,.34),(x0+span*.25,-.025,.37),(x0+span*.55,.02,.36),(x0+span*.8,.045,.34),(x1,.01,.34)]
        radii=[.32,.37,.39,.35,.31] if variant=='A' else [.29,.34,.34,.32,.27]
        trunk=FP.sweep(f'Rotten_Trunk_{si:02d}',pts,radii,bark,step=.055,aspect=.84,
                 fiss=.43,twist=.42,plates=4.0,worn=.34,lump=.21,nring=32,
                 seed=4200+si+ord(variant),tip=(exposed,.14) if variant=='A' else None,
                 cap=False,ground=None,detail=0)
        # 左端露出長短不同的木質破裂片；根部深入主幹，尖端逐步收束。
        for k in range(9 if variant=='A' else 7):
            count=9 if variant=='A' else 7
            ang=math.tau*k/count+rng.uniform(-.12,.12)
            reach=rng.uniform(.19,.54) if k%3 else rng.uniform(.38,.64)
            verts=[]
            for row,(xx,rad,w) in enumerate(((x0+.35,.19,.15),(x0-.07,.30,.12),
                                            (x0-reach*.65,.33,.085),(x0-reach,.32,.012))):
                for side in (-1,1):
                    th=ang+side*w
                    verts.append((xx,pts[0][1]+rad*math.cos(th),
                                  pts[0][2]+rad*.84*math.sin(th)+.013*math.sin(k+row)))
            faces=[(2*j,2*j+1,2*j+3,2*j+2) for j in range(3)]
            core.mesh(f'Torn_Wood_Lamina_{si}_{k}',verts,faces,
                      weathered if k%3 else exposed,smooth=False,solid=.012,detail=1)
        # 破皮在主幹表面分配材質，避免獨立浮片與穿插。
        if weathered.name not in trunk.data.materials:
            trunk.data.materials.append(weathered)
        exposed_slot=list(trunk.data.materials).index(weathered)
        for face in trunk.data.polygons:
            idx=face.vertices[0]
            if idx>=len(trunk.data.vertices)-2:continue
            row=idx//32;col=idx%32
            progress=row/max(1,(len(trunk.data.vertices)-2)//32-1)
            plate=(col in (0,1,2,3,4) and
                   .17+.022*math.sin(col*2.1)<progress<.33+.018*math.sin(col*1.7)) or \
                  (col in (29,30,31,0,1) and
                   .58+.015*math.sin(col*2.4)<progress<.68+.025*math.sin(col*1.3))
            if plate and (row+col*3+si)%17!=0:face.material_index=exposed_slot
        for k in range(2 if variant=='A' else 1):
            x=x0+span*(.28+.22*k)
            side=-1 if k%2==0 else 1
            FP.sweep(f'Broken_Branch_Stub_{si}_{k}',[(x,side*.24,.42),
                     (x+.05,side*.32,.43),(x+.08,side*.39,.36)],
                     [.068,.057,.032],bark,step=.045,aspect=.83,
                     fiss=.31,plates=3.5,tip=(exposed,.09),seed=4600+k+si*11,
                     ground=None,detail=1)
        # 開裂端是真正後退的腐空，另一端是有年輪的截面。
        for is_left in (True,False):
            end=x0 if is_left else x1
            facing=-1 if is_left else 1
            rr=radii[0] if is_left else radii[-1]
            yy=pts[0][1] if is_left else pts[-1][1]
            zz=pts[0][2] if is_left else pts[-1][2]
            hollow=is_left or (variant=='B' and (si==0 or is_left))
            if hollow:
                verts=[];faces=[];n=32
                for depth,rad in ((0,rr*.92),(-.022,rr*.65),(-.105,rr*.56)):
                    for j in range(n):
                        th=j*math.tau/n
                        wave=1+.08*math.sin(5*th+si)+.05*math.sin(13*th)
                        verts.append((end+facing*depth,yy+rad*wave*math.cos(th),
                                      zz+rad*.84*wave*math.sin(th)))
                for ring in range(2):
                    for j in range(n):
                        a=ring*n+j;b=ring*n+(j+1)%n
                        faces.append((a,b,b+n,a+n))
                core.mesh(f'Rot_Hollow_Lip_{si}_{int(is_left)}',verts,faces,exposed,
                          smooth=False,detail=0)
                core.cyl(f'Rot_Hollow_Dark_{si}_{int(is_left)}',
                         (end-facing*.11,yy,zz),rr*.54,.012,rotwood,
                         verts=32,bevel=0,detail=1,axis='x')
            else:
                verts=[(end-facing*.018,yy,zz)];faces=[];n=32
                for j in range(n):
                    th=j*math.tau/n
                    r=rr*(.88+.035*math.sin(7*th+si))
                    verts.append((end-facing*.014,yy+r*math.cos(th),
                                  zz+r*.84*math.sin(th)))
                for j in range(n):faces.append((0,1+j,1+(j+1)%n))
                core.mesh(f'Endgrain_{si}',verts,faces,weathered,smooth=False,detail=1)
    # 苔沿上方與背光側形成片狀殖落，頂部只留少量厚苔。
    # 側面多層檐菇，圓鈍檐片從木身長出。
    shelf_count=9 if variant=='A' else 6
    for i in range(shelf_count):
        x=-length*.35+i*length*.70/(shelf_count-1)+rng.uniform(-.035,.035)
        if variant=='B' and abs(x)<.20:continue
        side=-1 if i%3 else 1
        y=side*rng.uniform(.09,.14);z=rng.uniform(.29,.44)
        radius=rng.uniform(.085,.16)
        cap=core.lathe(f'Shelf_Fungus_{i:02d}',[(0,0),(radius*.65,0),
                        (radius,.012),(radius*.92,.027),(radius*.48,.041),(0,.048)],
                        (x,y+side*radius*.32,z),capmat,seg=18,detail=1)
        for v in cap.data.vertices:v.co.y*=.72
    # 褐色小傘菇沿朽木頂部不規則成簇。
    for i in range(7 if variant=='A' else 5):
        x=(-length*.32+i*length*.11)+rng.uniform(-.06,.06)
        if variant=='B' and abs(x)<.18: x+=.28
        y=rng.uniform(-.18,.18)
        H=rng.uniform(.24,.34); R=rng.uniform(.045,.082)
        base=.43
        core.cyl(f'Mushroom_Stem_{i:02d}',(x,y,base+H*.38),R*.22,H*.76,stemmat,
                 verts=10,bevel=0,detail=1)
        core.lathe(f'Mushroom_Cap_{i:02d}',[(0,0),(R*.62,0),(R,.012),
                   (R*.92,.025),(R*.38,.055),(0,.067)],(x,y,base+H*.76),
                   capmat,seg=16,detail=1)
    if os.environ.get('RL01_GEOMETRY_ONLY')=='1':
        pl.normalise();pl.join_groups()
        bpy.ops.wm.save_as_mainfile(filepath=str(PRE/f'{AID}_geometry_only.blend'))
        continue
    tail=source[source.index('# 灰模：'):]
    tail=tail.replace("(3.2,-5.5,3.0)",str((length*.65,-length*1.2,length*.72)))
    tail=tail.replace("(0,0,1.2)","(0,0,.35)")
    tail=tail.replace("cam.data.ortho_scale=3.8",f"cam.data.ortho_scale={length*1.26:.3f}")
    tail=tail.replace('CO02_clay.png',f'{AID}_clay.png').replace('CO02_hero.png',f'{AID}_hero.png')
    tail=tail.replace('v002','v001')
    tail=tail.replace("'古林碑'","'苔蕈朽木'").replace("'D4'","'D2'")
    tail=tail.replace('無文字；斜鑿槽使用 Boolean 真切割；AI 三視圖先於建模保存。',
                      '朽木有破裂木片、苔團及褐蕈；未在 Unity 地形上擺放；AI 三視圖先檢視並保存。')
    tail=tail.replace("OUT/'model_info.json'", "OUT/f'{AID}_model_info.json'")
    tail=tail.replace('CO02_INFO','RL01_INFO')
    tail=tail.replace("ROOT/'art/source/core-ruins-v2'", "ROOT/'art/source/core-d2-models-v1/RL01'")
    exec(compile(tail,str(ROOT/'art/source/core-ruins-v2/build_co02.py'),'exec'))

if os.environ.get('RL01_GEOMETRY_ONLY')!='1':
    infos=[json.loads((OUT/f'RL01_RottenLog_{v}_model_info.json').read_text(encoding='utf8')) for v,*_ in SPECS]
    (OUT/'model_info.json').write_text(json.dumps({'family':'RL01','variants':infos},ensure_ascii=False,indent=2),encoding='utf8')
