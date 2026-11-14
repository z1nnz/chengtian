"""SS01 三塊半埋踏石；依選定 AI 三視圖及 D2 V2/V3/V5 建模。"""
import bpy, bmesh, math, random, sys, json, os
import numpy as np
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'art/source/village-houses-b'))
import ti_core as core
import cr_parts as cp
import cr_mats as cm
import ti_pipeline as pl

REF = ROOT / 'art/references/core-d2-models-v1/SS01/turnaround.png'
assert REF.is_file()
OUT = ROOT / 'art/exports/core-d2-models-v1/SS01'
PRE = ROOT / 'art/previews/core-d2-models-v1/SS01'
SRC = ROOT / 'art/source/core-d2-models-v1/SS01'
OUT.mkdir(parents=True, exist_ok=True)
PRE.mkdir(parents=True, exist_ok=True)

SPECS = [
    ('A', .88, .63, .24, 2101),
    ('B', .67, .60, .21, 2102),
    ('C', .47, .45, .16, 2103),
]
infos = []
only = os.environ.get('SS01_ONLY')
source = (ROOT / 'art/source/core-ruins-v2/build_co02.py').read_text(encoding='utf-8-sig')

for variant, width, depth, height, seed in SPECS:
    if only and variant != only:
        continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    AID = f'SS01_SteppingStone_{variant}'
    core.reset_state(AID)
    stone = cm.stone(f'M_{AID}_Stone', light=(.36,.33,.29), dark=(.18,.17,.15),
                     ochre=(.30,.26,.19), moss=.82, crack=.63, lichen=.28)
    moss = cm.moss_tuft(f'M_{AID}_EdgeMoss', soft=True)
    rng = random.Random(seed)
    n = 32
    power = {'A':3.3, 'B':2.7, 'C':2.2}[variant]
    def outline(a):
        c,s=math.cos(a),math.sin(a)
        return math.copysign(abs(c)**(2/power),c),math.copysign(abs(s)**(2/power),s)
    rings = [(.80, -.07), (1.0, .035), (.96, height-.035), (.71, height-.005), (.39, height+.004)]
    verts, faces = [], []
    for k,(radius,z) in enumerate(rings):
        for i in range(n):
            a = math.tau*i/n
            rough = 1+.045*math.sin(5*a+seed)+.032*math.cos(9*a+seed*.13)
            rough += rng.uniform(-.015,.015)
            ox,oy=outline(a)
            x = ox*width*.5*radius*rough
            y = oy*depth*.5*radius*rough
            if variant == 'A': x += .075*y
            if variant == 'B': y += .04*math.sin(2*a)
            zz = z + (.009*math.sin(3*a+seed)+.005*math.cos(7*a))*(.4 if k<2 else 1)
            verts.append((x,y,zz))
    for k in range(len(rings)-1):
        for i in range(n):
            j=(i+1)%n
            faces.append((k*n+i,k*n+j,(k+1)*n+j,(k+1)*n+i))
    bot=len(verts); verts.append((0,0,-.07))
    top=len(verts); verts.append((0,0,height+.004))
    for i in range(n):
        j=(i+1)%n
        faces.append((bot,j,i))
        faces.append((4*n+i,4*n+j,top))
    rock=core.mesh('Worn_Step_Stone',verts,faces,stone,smooth=False,detail=0)
    for p in rock.data.polygons:
        p.use_smooth = p.index >= 3*n
    count=16 if variant!='C' else 12
    for i in range(count):
        if variant == 'B' and i == 10:
            continue
        a=math.tau*i/count+rng.uniform(-.11,.11)
        ox,oy=outline(a)
        x=ox*width*.455
        y=oy*depth*.455
        cp.tuft(f'Edge_Moss_{i:02d}',(x,y,height-.047),rng.uniform(.014,.028),moss,
                seed=seed+i,detail=2)

    tail=source[source.index('# 灰模：'):]
    tail=tail.replace("(3.2,-5.5,3.0)","(1.2,-1.8,1.1)")
    tail=tail.replace("(0,0,1.2)","(0,0,.07)")
    tail=tail.replace("cam.data.ortho_scale=3.8","cam.data.ortho_scale=1.32")
    tail=tail.replace('CO02_clay.png',f'{AID}_clay.png').replace('CO02_hero.png',f'{AID}_hero.png')
    tail=tail.replace('2048','1024').replace('v002','v001')
    tail=tail.replace("'古林碑'","'半埋踏石'").replace("'D4'","'D2'")
    tail=tail.replace('無文字；斜鑿槽使用 Boolean 真切割；AI 三視圖先於建模保存。',
                      '磨平頂面及帶苔不規則邊緣；安放時將底部埋入泥路約 0.06 m；AI 三視圖先檢視並保存。')
    tail=tail.replace("OUT/'model_info.json'", "OUT/f'{AID}_model_info.json'")
    tail=tail.replace('CO02_INFO','SS01_INFO')
    tail=tail.replace("ROOT/'art/source/core-ruins-v2'", "ROOT/'art/source/core-d2-models-v1/SS01'")
    exec(compile(tail, str(ROOT/'art/source/core-ruins-v2/build_co02.py'), 'exec'))
    infos.append(info)

all_infos = [json.loads((OUT/f'SS01_SteppingStone_{variant}_model_info.json').read_text(encoding='utf8'))
             for variant,*_ in SPECS]
(OUT/'model_info.json').write_text(json.dumps({'family':'SS01','variants':all_infos},ensure_ascii=False,indent=2),encoding='utf8')
