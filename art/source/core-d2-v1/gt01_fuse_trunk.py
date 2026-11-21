# 神木樹幹熔成一整塊：7 根樹幹管 + 板根原本是各自獨立、互相插在一起的網格 → 接縫處一條條橫線（z1nnz 11/21「樹幹不連貫」）
import bpy,sys,time
vs=float(sys.argv[-1])
S='D:/chengtian/4-素材與快取/bark-sample/GT01_out/'
with bpy.data.libraries.load(S+'GT01_GodTree_v003.blend',link=False) as (s,d):
    d.objects=[n for n in s.objects if n.endswith('_LOD0')]
for o in d.objects: bpy.context.scene.collection.objects.link(o)
w=bpy.data.objects['GT01_GodTree_Wood_LOD0']
t=time.time()
import bmesh
print('SCALE',tuple(w.scale),tuple(w.dimensions))
bm=bmesh.new(); bm.from_mesh(w.data)
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.002)
bd=[e for e in bm.edges if e.is_boundary]
bmesh.ops.holes_fill(bm,edges=bd,sides=0)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
print('BOUND_AFTER',sum(1 for e in bm.edges if e.is_boundary))
bm.to_mesh(w.data); bm.free()
m=w.modifiers.new('R','REMESH'); m.mode='VOXEL'; m.voxel_size=vs; m.adaptivity=0; m.use_smooth_shade=True
bpy.context.view_layer.objects.active=w
bpy.ops.object.modifier_apply(modifier='R')
print('REMESH',len(w.data.vertices),round(time.time()-t,1))
# 接縫的內凹折角柔化（不要整棵糊掉）
cs=w.modifiers.new('S','CORRECTIVE_SMOOTH'); cs.factor=.5; cs.iterations=6; cs.smooth_type='SIMPLE'; cs.use_only_smooth=True
bpy.ops.object.modifier_apply(modifier='S')
w.name='GT01_GodTree_Wood_LOD0'
bpy.ops.wm.save_as_mainfile(filepath=S+'GT01_GodTree_v004_fused.blend')
print('SAVED')
