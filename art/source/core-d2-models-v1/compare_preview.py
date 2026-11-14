"""把模型預覽與倉庫內同類作品並排，保留原圖來源。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

aid, peer, label=sys.argv[1:4]
root=Path(__file__).resolve().parents[3]
out=root/'art/previews/core-d2-models-v1'/aid.split('_')[0]
hero=next(out.glob(f'{aid}_hero.png'))
peer_path=root/peer
canvas=Image.new('RGB',(1600,850),(54,55,55))
draw=ImageDraw.Draw(canvas)
for i,(path,title) in enumerate(((hero,aid),(peer_path,label))):
    im=Image.open(path).convert('RGB')
    im.thumbnail((760,760),Image.Resampling.LANCZOS)
    x=i*800+(800-im.width)//2
    y=70+(760-im.height)//2
    canvas.paste(im,(x,y))
    draw.text((i*800+28,24),title,fill=(235,235,235))
canvas.save(out/f'{aid}_comparison.png')
