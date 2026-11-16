import bpy, sys, os, math
import numpy as np
ARGS = sys.argv[sys.argv.index('--') + 1:]
SRC = 'D:/chengtian/4-素材與快取/bark-sample/'
OUT = ARGS[0]
TEX = 4096
NAME = 'GT01_GodTree'
bpy.ops.wm.open_mainfile(filepath=OUT + 'stage1.blend')
sc = bpy.context.scene
code = open(SRC + 'gt_bake.py', encoding='utf-8').read()
head = code[:code.index('bpy.ops.wm.open_mainfile')]
exec(compile(head.split("ARGS = ")[0], 'h', 'exec'))
helpers = code[code.index('def bark_objs'):code.index('# ---------- 低模 LOD0')]
exec(compile(helpers, 'helpers', 'exec'))
def log(*a): print('[GT01]', *a, flush=True)
lo0 = bpy.data.objects[f'{NAME}_Wood_LOD0']
img = {}
for k, cs in (('BaseColor', 'sRGB'), ('Normal', 'Non-Color'), ('AO', 'Non-Color')):
    im = bpy.data.images.load(OUT + f'Textures/{NAME}_{k}.png')
    im.colorspace_settings.name = cs
    img[k] = im
tail = code[code.index('# ---------- 遊戲用樹皮材質'):]
exec(compile(tail, 'tail', 'exec'))
