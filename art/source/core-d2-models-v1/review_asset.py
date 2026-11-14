"""在已載入的資產 .blend 製作四視角、線框與 1.75 m 人形尺。"""
import bpy, bmesh, sys
from pathlib import Path
from mathutils import Matrix

aid=sys.argv[sys.argv.index('--')+1]
root=Path(__file__).resolve().parents[3]
out=root/'art/previews/core-d2-models-v1'/aid.split('_')[0]
out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,'C:/Users/User/.agents/skills/blender-asset-qa/scripts')
import review_shots
asset=next(o for o in bpy.data.objects if o.type=='MESH' and o.name.endswith('_LOD0') and o.name.startswith(aid))
review_shots.run(objects=[asset.name],out=str(out/f'{aid}_four_angles.png'),
                 views=['front','right','back','three_quarter'],mode='material',res=420)
review_shots.run(objects=[asset.name],out=str(out/f'{aid}_wire.png'),
                 views=['front','right','top','three_quarter'],mode='wire',res=420)

mat=bpy.data.materials.new('Scale_Figure_Matte')
mat.diffuse_color=(.56,.62,.65,1)
figure=[]
for name,x,z0,z1,r1,r2 in [('Torso',0,.78,1.48,.17,.17),
                           ('LegL',-.095,0,.83,.075,.06),('LegR',.095,0,.83,.075,.06),
                           ('ArmL',-.235,.82,1.44,.05,.04),('ArmR',.235,.82,1.44,.05,.04),
                           ('Neck',0,1.45,1.56,.05,.05),('Head',0,1.54,1.75,.11,.11)]:
    bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,segments=12,radius1=r1,radius2=r2,
                                        depth=z1-z0,matrix=Matrix.Translation((0,0,(z0+z1)/2)))
    me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new('Scale_'+name,me);bpy.context.scene.collection.objects.link(ob)
    ob.location.x=max(asset.dimensions.x/2+.55,1.1)+x;me.materials.append(mat);figure.append(ob.name)
review_shots.run(objects=[asset.name]+figure,out=str(out/f'{aid}_human_175cm.png'),
                 views=['front','three_quarter'],mode='material',res=520)
