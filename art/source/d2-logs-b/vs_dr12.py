# DR12 樹皮片 L 和參考圖並排：Blender 用參考圖的鏡位（眼高、約 4 m 外的四分之三視，捲起端在左）出 LOD0，
# 再和參考圖裁出的同一片樹皮排在一起（同方向、同取景比例）；另一列是捲起端特寫對參考細節圖 (a)。
#   blender -b art/source/d2-logs-b/blend/DR12_BarkSheet_L_v001.blend --python art/source/d2-logs-b/vs_dr12.py
#   然後：uv run --no-project --with pillow python art/source/d2-logs-b/vs_dr12.py compose
import sys, os

ROOT = 'D:/yun-jing-d2-logs'
ASSET = 'DR12_BarkSheet_L'
PRE = f'{ROOT}/art/previews/d2-logs-b/{ASSET}'
REF = f'{ROOT}/art/references/DR12/v001'
SHOTS = {'ref': ((.55, 3.15, 1.30), (-.05, 0, .22), 42), 'refclose': ((.95, .95, .62), (.42, -.05, .32), 40)}


def render():
    import bpy
    ns = {'__name__': 'preview_dr', '__file__': ROOT + '/art/source/d2-roots-b/preview_dr.py'}
    exec(compile(open(ns['__file__'], encoding='utf-8').read(), ns['__file__'], 'exec'), ns)
    ns['setup'](samples=96, fog=False)
    for o in bpy.data.objects:
        if o.type == 'MESH' and not o.name.startswith('DR_'):
            o.hide_render = o.name != f'{ASSET}_LOD0'
    h = bpy.data.objects.get('DR_Human_1p75m')
    if h:
        h.hide_render = True
    for k, (loc, tgt, lens) in SHOTS.items():
        ns['shot'](f'{PRE}/vs_{k}.png', loc, tgt, lens, (1536, 1024))


def compose():
    from PIL import Image, ImageDraw, ImageFont
    F = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 26)
    rows = [(Image.open(f'{REF}/DR12-threequarter.png').crop((40, 270, 890, 670)), Image.open(f'{PRE}/vs_ref.png').crop((260, 230, 1240, 720)),
             '參考 DR12-threequarter（Bark L）', '遊戲模型 LOD0，同方向（捲起端在左、眼高四分之三視）'),
            (Image.open(f'{REF}/DR12-detail.png').crop((0, 566, 510, 1024)), Image.open(f'{PRE}/vs_refclose.png').crop((180, 0, 1536, 1024)),
             '參考細節圖 (a)：捲起端、斷面三層、內皮纖維', '遊戲模型 LOD0 捲起端特寫')]
    H = 560
    out = []
    for a, b, ta, tb in rows:
        a = a.resize((int(a.width * H / a.height), H), Image.LANCZOS)
        b = b.resize((int(b.width * H / b.height), H), Image.LANCZOS)
        out.append((a, b, ta, tb))
    W = max(a.width + b.width for a, b, _, _ in out) + 60
    sheet = Image.new('RGB', (W, len(out) * (H + 70) + 20), (236, 236, 232))
    d = ImageDraw.Draw(sheet)
    y = 10
    for a, b, ta, tb in out:
        d.text((20, y), ta, fill=(30, 30, 30), font=F)
        d.text((40 + a.width, y), tb, fill=(30, 30, 30), font=F)
        sheet.paste(a, (20, y + 44))
        sheet.paste(b, (40 + a.width, y + 44))
        y += H + 70
    sheet.save(f'{PRE}/{ASSET}_vs_reference.jpg', quality=90)
    print('VS', sheet.size)


if __name__ == '__main__':
    if 'compose' in sys.argv:
        compose()
    else:
        render()
