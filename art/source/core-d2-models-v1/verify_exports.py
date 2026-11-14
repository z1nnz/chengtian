"""回匯 FBX 與 GLB，確認 LOD 與非空網格。"""
import json
import sys
from pathlib import Path
import bpy

root = Path(__file__).resolve().parents[3]
family, aid, version = sys.argv[sys.argv.index('--') + 1:sys.argv.index('--') + 4]
base = root / 'art/exports/core-d2-models-v1' / family
result = {}
for ext in ('fbx', 'glb'):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    path = base / f'{aid}_{version}.{ext}'
    assert path.is_file() and path.stat().st_size > 0, path
    if ext == 'fbx':
        bpy.ops.import_scene.fbx(filepath=str(path))
    else:
        bpy.ops.import_scene.gltf(filepath=str(path))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    assert meshes and all(len(o.data.polygons) for o in meshes), ext
    names = [o.name for o in meshes]
    for level in ((0, 1, 2) if ext == 'fbx' else (0,)):
        assert any(f'LOD{level}' in name for name in names), (ext, level, names)
    result[ext] = {'bytes': path.stat().st_size,
                   'meshes': names,
                   'triangles': sum(len(o.data.loop_triangles) for o in meshes)}
print('VERIFY_EXPORTS', json.dumps(result), flush=True)
per_file = base / f'{aid}_model_info.json'
if per_file.is_file():
    info = json.loads(per_file.read_text(encoding='utf-8'))
    info['status']['Imported'] = True
    per_file.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
    family_file = base / 'model_info.json'
    if family_file.is_file():
        family_info = json.loads(family_file.read_text(encoding='utf-8'))
        for item in family_info.get('variants', []):
            if item.get('asset') == aid:
                item['status']['Imported'] = True
        family_file.write_text(json.dumps(family_info, ensure_ascii=False, indent=2), encoding='utf-8')
