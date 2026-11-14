"""SR01 三種地表盤根；依選定 AI 三視圖及 D2 V2/V3/V5 建模。"""
import bpy, bmesh, math, random, sys, json, os
import numpy as np
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'art/source/village-houses-b'))
import ti_core as core
import fr_parts as FP
import fr_mats as fm
import ti_pipeline as pl

assert (ROOT/'art/references/core-d2-models-v1/SR01/turnaround.png').is_file()
OUT=ROOT/'art/exports/core-d2-models-v1/SR01'
PRE=ROOT/'art/previews/core-d2-models-v1/SR01'
OUT.mkdir(parents=True,exist_ok=True)
PRE.mkdir(parents=True,exist_ok=True)

SPECS=[
 ('A',.19,[(-2.35,.04,-.10),(-1.65,-.03,.03),(-.85,.01,.24),(0,.02,.30),(.9,.00,.23),(1.65,.03,.04),(2.35,.13,-.10)],
      [(-.65,-.02,.27),(-.95,-.42,.22),(-1.25,-.72,.03),(-1.53,-.84,-.11)],
      [(.70,.01,.25),(.95,.35,.20),(1.38,.64,.02),(1.56,.75,-.11)]),
 ('B',.15,[(-1.77,.15,-.10),(-1.34,.06,.02),(-.68,-.02,.19),(.05,-.10,.24),(.72,-.04,.16),(1.28,.10,.03),(1.75,.20,-.10)],
      [(-.35,-.08,.22),(-.56,-.38,.13),(-.78,-.59,-.09)],
      [(.64,-.05,.18),(.93,.30,.12),(1.18,.47,-.09)]),
 ('C',.105,[(-1.17,-.24,-.08),(-.70,-.10,.06),(-.22,.05,.15),(.30,.12,.17),(.78,.01,.09),(1.16,-.25,-.08)],
      [(-.22,.05,.15),(-.26,.32,.09),(-.47,.53,-.08)],
      [(.53,.09,.13),(.72,-.26,.05),(.84,-.43,-.08)]),
]
only=os.environ.get('SR01_ONLY')
source=(ROOT/'art/source/core-ruins-v2/build_co02.py').read_text(encoding='utf-8-sig')

for variant,radius,main,branch1,branch2 in SPECS:
    if only and variant!=only: continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    AID=f'SR01_SurfaceRoot_{variant}'
    core.reset_state(AID)
    bark=fm.bark(f'M_{AID}_OldBark',tone=1.34,moss=.76,ground_h=.06)
    main_radii=[radius*(.32+.68*math.sin(math.pi*i/(len(main)-1))**.65)
                for i in range(len(main))]
    FP.sweep('Arching_Main_Root',main,main_radii,bark,step=.055,aspect=.79,
             fiss=.28,twist=.35,plates=3.2,worn=.48,lump=.14,nring=24,
             seed=3100+ord(variant),detail=0)
    for i,branch in enumerate((branch1,branch2)):
        branch_radii=[radius*.62*(1-.78*j/(len(branch)-1)) for j in range(len(branch))]
        FP.sweep(f'Fork_{i:02d}',branch,branch_radii,bark,step=.05,aspect=.74,
                 fiss=.24,twist=.27,plates=2.8,worn=.45,lump=.13,nring=16,
                 seed=3200+ord(variant)*3+i,detail=0)
    tail=source[source.index('# 灰模：'):]
    span=main[-1][0]-main[0][0]
    tail=tail.replace("(3.2,-5.5,3.0)",str((span*.8,-span*1.3,span*.7)))
    tail=tail.replace("(0,0,1.2)","(0,0,.10)")
    tail=tail.replace("cam.data.ortho_scale=3.8",f"cam.data.ortho_scale={span*1.25:.3f}")
    tail=tail.replace('CO02_clay.png',f'{AID}_clay.png').replace('CO02_hero.png',f'{AID}_hero.png')
    tail=tail.replace('2048','1024').replace('v002','v001')
    tail=tail.replace("'古林碑'","'地表盤根'").replace("'D4'","'D2'")
    tail=tail.replace('無文字；斜鑿槽使用 Boolean 真切割；AI 三視圖先於建模保存。',
                      '兩端及分叉末端埋入土中，中央拱起供道路跨過；AI 三視圖先檢視並保存。')
    tail=tail.replace("OUT/'model_info.json'", "OUT/f'{AID}_model_info.json'")
    tail=tail.replace('CO02_INFO','SR01_INFO')
    tail=tail.replace("ROOT/'art/source/core-ruins-v2'", "ROOT/'art/source/core-d2-models-v1/SR01'")
    exec(compile(tail,str(ROOT/'art/source/core-ruins-v2/build_co02.py'),'exec'))

infos=[json.loads((OUT/f'SR01_SurfaceRoot_{v}_model_info.json').read_text(encoding='utf8')) for v,*_ in SPECS]
(OUT/'model_info.json').write_text(json.dumps({'family':'SR01','variants':infos},ensure_ascii=False,indent=2),encoding='utf8')
