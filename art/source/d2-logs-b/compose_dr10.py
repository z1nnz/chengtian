# DR10「參考圖 vs 成品」並排圖：
#   1. 三視圖：上排 art/references/DR10/v001/DR10-threeview.png（A 正、A 側、B 正、B 側），下排 vs_dr10.py 長鏡頭拍的成品同樣四張（A、B 同比例）；
#   2. 四分之三：DR10-threequarter.png 旁邊放 A、B 的 refcam_tq。
# 用法：uv run --no-project --with pillow python art/source/d2-logs-b/compose_dr10.py
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
ASSETS = {'A': 'DR10_DeadSnag_A', 'B': 'DR10_DeadSnag_B'}
REF = os.path.join(ROOT, 'art', 'references', 'DR10', 'v001')
try:
    FONT = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 26)
except OSError:
    FONT = ImageFont.load_default()


def pre(v):
    return os.path.join(ROOT, 'art', 'previews', 'd2-logs-b', ASSETS[v])


def fit_h(im, h):
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


def threeview():
    ref = Image.open(os.path.join(REF, 'DR10-threeview.png')).convert('RGB')
    W = 1800
    ref = ref.resize((W, round(ref.height * W / ref.width)), Image.LANCZOS)
    ours = [Image.open(os.path.join(pre(v), f'{ASSETS[v]}_LOD0_refcam_{t}.png')).convert('RGB') for v in 'AB' for t in ('front', 'side')]
    h = round(W / 4 * ours[0].height / ours[0].width)
    ours = [im.resize((W // 4, h), Image.LANCZOS) for im in ours]
    canvas = Image.new('RGB', (W + 24, ref.height + h + 140), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    canvas.paste(ref, (12, 12))
    d.text((16, ref.height + 18), '參考圖（Codex 依 V1、V5 畫）：A 正、A 側、B 正、B 側', fill=(235, 235, 235), font=FONT)
    y = ref.height + 60
    for i, im in enumerate(ours):
        canvas.paste(im, (12 + i * (W // 4), y))
    d.text((16, y + h + 14), '成品 LOD0＋植物（長鏡頭近似正交；A、B 同比例；白柱 1.75 m）：A 正、A 側、B 正、B 側', fill=(235, 235, 235), font=FONT)
    out = os.path.join(pre('A'), 'DR10_DeadSnag_AB_vs_reference_threeview.jpg')
    canvas.save(out, quality=90)
    print(out, canvas.size)


def threequarter():
    H = 640
    ref = fit_h(Image.open(os.path.join(REF, 'DR10-threequarter.png')).convert('RGB'), H)
    tiles = [(ref, '參考圖（四分之三）')] + [(fit_h(Image.open(os.path.join(pre(v), f'{ASSETS[v]}_LOD0_refcam_tq.png')).convert('RGB'), H), f'成品 {v}（仰看，鏡位估的）') for v in 'AB']
    W = sum(t[0].width for t in tiles) + 12 * (len(tiles) + 1)
    canvas = Image.new('RGB', (W, H + 60), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    x = 12
    for im, label in tiles:
        canvas.paste(im, (x, 12))
        d.text((x + 4, H + 20), label, fill=(235, 235, 235), font=FONT)
        x += im.width + 12
    out = os.path.join(pre('A'), 'DR10_DeadSnag_AB_vs_reference_threequarter.jpg')
    canvas.save(out, quality=90)
    print(out, canvas.size)


if __name__ == '__main__':
    threeview()
    threequarter()
