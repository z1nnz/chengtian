"""CO03 祠內殘件 v002；三視圖先於建模保存。"""
import bpy, bmesh, math, sys, json, os
import numpy as np
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'art/source/village-houses-b'))
import ti_core as core
import cr_parts as cp
import cr_mats as cm
import vl_mats as vm
import ti_pipeline as pl

AID='CO03_ShrineRemnants'
OUT=ROOT/'art/exports/core-ruins-v2'/AID
PRE=ROOT/'art/previews/core-ruins-v2'/AID
OUT.mkdir(parents=True,exist_ok=True); PRE.mkdir(parents=True,exist_ok=True)
assert (ROOT/'art/references/core-ruins-v2/CO03/CO03_threeview_chosen.png').is_file()
bpy.ops.wm.read_factory_settings(use_empty=True)
core.reset_state(AID)

stone=cm.stone('CO03_OldStone',light=vm.STONE[2],dark=vm.STONE[1],ochre=vm.STONE[0],moss=.48,crack=.7,lichen=.5)
tile=cm.tile('CO03_BrokenRoofTile',base=(.03,.042,.055),light=(.078,.096,.11),moss=.32)
wood=cm.wood('CO03_RottedTimber',dark=vm.WOOD[2],light=vm.WOOD[0],wet_z=.18,moss=True,holes=.6,grey=.7)
bronze=vm.iron('CO03_OxidizedBronze')

# 半埋於地表的殘存祠堂鋪石把散件托住，也遮住世界地表接縫。
cp.rbox('Shrine_Floor_Remnant',(0,-.55,0),(2.94,2.02,.24),stone,r=.035,amp=.015,chips=65,hew=72,seed=3030,div=.085,taper=(.94,.92),detail=0)

# 供桌四腳之一斷裂；台面向缺腳一端微傾，殘柱與碎石托住下沉的一角。
slab=cp.rbox('Table_Slab',(0,.05,.99),(1.73,.76,.18),stone,r=.027,amp=.019,chips=72,hew=90,seed=3031,div=.048,rot=(.01,.15,-.016),detail=0)
# 斷腿上方的石板缺去大塊轉角，留下實際破口；不是貼圖畫的裂痕。
corner=core.box('Slab_Missing_Corner',(.86,-.34,.97),(.42,.48,.46),None,rot=(.12,.05,.58))
core.boolean(slab,corner)
cp.rbox('Table_Fascia_Front',(0,-.30,.855),(1.53,.10,.14),stone,r=.015,amp=.01,chips=16,hew=18,seed=3032,div=.05,rot=(.01,.15,-.016),detail=0)
for i,(x,y,h,tw) in enumerate(((-.67,-.20,1.02,-.04),(-.67,.28,1.02,.03),(.66,.28,.78,.04))):
    cp.rbox(f'Table_Leg_{i+1:02d}',(x,y,h/2),(.22,.22,h),stone,r=.024,amp=.01,chips=20,hew=26,seed=3035+i,div=.055,taper=(.90,.89),rot=(.016,tw,.02),detail=0)
cp.rbox('Broken_Leg_Stump',(.66,-.20,.23),(.23,.24,.43),stone,r=.023,amp=.013,chips=19,hew=24,seed=3042,div=.047,rot=(.05,.11,.11),detail=0)
cp.rbox('Broken_Leg_Fallen',(.78,-.36,.14),(.43,.22,.20),stone,r=.024,amp=.012,chips=20,hew=25,seed=3043,div=.045,rot=(.07,.03,-.34),detail=0)
for i,(x,y,z,s) in enumerate(((.62,-.31,.10,.17),(.94,-.19,.07,.12),(.43,-.44,.06,.09))):
    cp.rbox(f'Leg_Rubble_{i+1:02d}',(x,y,z),(s,s*.82,s*.75),stone,r=.01,amp=.009,chips=7,hew=8,seed=3050+i,div=.035,rot=(.1*i,.13*i,-.28*i),detail=1)
moss=cm.moss_tuft('CO03_JointMoss')
for i,(x,y,z) in enumerate(((-.64,-.26,.16),(.56,.30,.15),(.72,-.14,.15))):
    cp.tuft(f'Moss_Joint_{i+1:02d}',(x,y,z),.047,moss,seed=3080+i,detail=2)

# 空三足香爐：旋轉輪廓同 Eli 的 _lathe 做法，開口、內壁和空底都有真幾何。
cx,cy,cz=-.63,-.83,.34
profile=[(0,0),(.13,.015),(.22,.06),(.285,.15),(.29,.31),(.315,.35),(.315,.39),(.255,.39),(.245,.35),(.235,.17),(.17,.09),(0,.09)]
burner=[]
burner.append(core.lathe('Burner_EmptyBowl',profile,(cx,cy,cz),bronze,seg=32,detail=0))
for i in range(3):
    ang=i*math.tau/3
    px=cx+.21*math.cos(ang);py=cy+.21*math.sin(ang)
    burner.append(core.cyl(f'Burner_Foot_{i+1:02d}',(px,py,cz-.055),.048,.19,bronze,verts=10,detail=0))
M=Matrix.Translation(Vector((cx,cy,cz))) @ Matrix.Rotation(math.radians(78),4,'Y') @ Matrix.Translation(Vector((-cx,-cy,-cz)))
for ob in burner: ob.matrix_world=M @ ob.matrix_world

# 零散屋瓦不是一塊噪聲堆：每片有厚度、獨立破口與錯向壓疊。
for i,(x,y,z,a,w) in enumerate(((.08,-.87,.10,.28,.29),(.38,-.92,.14,-.31,.25),(.25,-.69,.11,.75,.24),(.48,-.74,.18,-.56,.25),(-.03,-.64,.18,-.26,.21),(.55,-.99,.15,.46,.18),(.11,-1.04,.16,-.72,.21))):
    cp.rbox(f'Tile_Shard_{i+1:02d}',(x,y,z),(w,.22,.035),tile,r=.009,amp=.006,chips=7,hew=7,seed=3060+i,div=.035,rot=(.05*i,.10*i,a),detail=1)

# 三段各有不同長度與斷裂端的朽木，與石、瓦分開擺放。
for i,(x,y,ln,a) in enumerate(((1.12,-.77,.64,.12),(1.00,-.99,.48,-.21),(.95,-1.19,.34,.37))):
    p0=(x-ln/2*math.cos(a),y-ln/2*math.sin(a),.165)
    p1=(x+ln/2*math.cos(a),y+ln/2*math.sin(a),.17)
    cp.log(f'Rotten_Timber_{i+1:02d}',[p0,p1],.055+i*.008,wood,seg=10,lump=.24,seed=3070+i,detail=1)

for ob in core.S['parts']:
    if ob.name!='Burner_EmptyBowl':
        for face in ob.data.polygons:face.use_smooth=False

# 共用 CO02 已驗證的灰模、圖集、烘焙、LOD 與匯出流程；不執行 CO02 的建模段。
source=(Path(__file__).with_name('build_co02.py')).read_text(encoding='utf-8-sig')
tail=source[source.index('# 灰模：'):]
tail=tail.replace('CO02_clay.png','CO03_clay.png').replace('CO02_hero.png','CO03_hero.png')
tail=tail.replace("'古林碑'","'祠內殘件'").replace("'D4'","'D4'")
tail=tail.replace('無文字；斜鑿槽使用 Boolean 真切割；AI 三視圖先於建模保存。','無神像、供品或文字；桌腳斷裂、空三足香爐、碎瓦與三段朽木均為獨立零件；AI 三視圖先於建模保存。')
tail=tail.replace('CO02_INFO','CO03_INFO')
exec(compile(tail,str(Path(__file__).with_name('build_co02.py')),'exec'))
