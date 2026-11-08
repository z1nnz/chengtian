"""Renders the world blueprint from world-blueprint.json.

Output: docs/execution/world-blueprint/README.md and overview.png, plus one map per block.
Also checks every model ID against what the repository really has, so a typo or a model
nobody made shows up as a missing part instead of a silent gap.

Run from anywhere: python tools/qingxi-terrain/render-world-blueprint.py
"""
import json
import math
import os
import re
import subprocess

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ROOT)
OUT = 'docs/execution/world-blueprint'
os.makedirs(OUT, exist_ok=True)
data = json.load(open('tools/qingxi-terrain/world-blueprint.json', encoding='utf-8'))
# Latin font first: map labels are IDs; msjh carries the Chinese title.
FONT = 'C:/Windows/Fonts/msjh.ttc'
font = ImageFont.truetype(FONT, 18)
small = ImageFont.truetype(FONT, 14)

tracked = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, encoding='utf-8').stdout.split('\n')
names = set()
for f in tracked:
    if f.lower().endswith(('.fbx', '.glb')):
        names.add(os.path.basename(f).rsplit('.', 1)[0])
# Models delivered on branches Codex collects in stage 0 are checked out here as files.
for base, _, files in os.walk('art/exports'):
    for f in files:
        if f.lower().endswith(('.fbx', '.glb')):
            names.add(f.rsplit('.', 1)[0])
# Runtime-only or generated pieces the world builder already provides.
BUILT_IN = {'BambooClump'}


def exists(model):
    if model in names or model in BUILT_IN:
        return True
    return any(n == model or re.match(re.escape(model) + r'(_v\d+|_LOD\d)', n) for n in names)


def check(block):
    bad = []
    for z in block['zones']:
        for g in z['groups']:
            if g.get('tag') == 'pending':
                continue
            for m in g['models'].split(','):
                if not exists(m.strip()):
                    bad.append(m.strip())
    return sorted(set(bad))


blocks = data['blocks']
by_id = {b['id']: b for b in blocks}
REGION = {'A': '#DCE3C2', 'D': '#B9CCA6', 'B': '#D9D7CF'}


def bounds(b):
    cx, cz = b['cell'][0] * 100, b['cell'][1] * 100
    return cx - 50, cz - 50, cx + 50, cz + 50


def arrow(d, a, b, col, width=3):
    d.line([a, b], fill=col, width=width)
    t = math.atan2(b[1] - a[1], b[0] - a[0])
    for s in (-1, 1):
        d.line([b, (b[0] - 12 * math.cos(t + s * .45), b[1] - 12 * math.sin(t + s * .45))], fill=col, width=width)


def overview():
    minx, maxx, minz, maxz = -160, 260, -260, 360
    S = 2.6
    W, H = int((maxx - minx) * S), int((maxz - minz) * S) + 44
    im = Image.new('RGB', (W, H), '#F3F1EA')
    d = ImageDraw.Draw(im)

    def P(x, z):
        return ((x - minx) * S, (maxz - z) * S)

    for b in blocks:
        x0, z0, x1, z1 = bounds(b)
        d.rectangle([P(x0, z1), P(x1, z0)], fill=REGION[b['id'][0]], outline='#8E8A7C', width=2)
        d.text((P(x0, z1)[0] + 6, P(x0, z1)[1] + 4), f"{b['order']}. {b['id']} {b['name']}", fill='#333', font=font)
        d.text((P(x0, z1)[0] + 6, P(x0, z1)[1] + 28), b['days'], fill='#555', font=small)
        for z in b['zones']:
            d.rectangle([P(z['x'] - z['hx'], z['z'] + z['hz']), P(z['x'] + z['hx'], z['z'] - z['hz'])], outline='#6A5A3C', width=1, fill='#EFE3C6')
    for r in data['route']:
        a, b = by_id[r['from']], by_id[r['to']]
        arrow(d, P(a['cell'][0] * 100, a['cell'][1] * 100), P(b['cell'][0] * 100, b['cell'][1] * 100), '#D08A3C' if r.get('free') else '#B4472F')
    for b in blocks:
        for s in b['shots']:
            q = P(s['x'], s['z'])
            a = math.radians(s['yaw'])
            e = (q[0] + math.sin(a) * 26, q[1] - math.cos(a) * 26)
            col = '#1E5FA8' if s.get('ka') else '#5B8DC4'
            d.line([q, e], fill=col, width=2)
            d.ellipse([q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4], fill=col)
    d.rectangle([0, H - 44, W, H], fill='#FFFFFF')
    d.text((10, H - 34), '紅＝常見走法　橘＝自由繞路　米色＝分區　深藍＝有主視覺的鏡頭　淺藍＝其他鏡頭　數字＝施工順序', fill='#222', font=font)
    im.save(f'{OUT}/overview.png')


def block_map(b):
    x0, z0, x1, z1 = bounds(b)
    pad = 8
    S = 7.5
    W, H = int((x1 - x0 + 2 * pad) * S), int((z1 - z0 + 2 * pad) * S) + 36
    im = Image.new('RGB', (W, H), '#F3F1EA')
    d = ImageDraw.Draw(im)

    def P(x, z):
        return ((x - x0 + pad) * S, (z1 + pad - z) * S)

    d.rectangle([P(x0, z1), P(x1, z0)], fill=REGION[b['id'][0]], outline='#8E8A7C', width=2)
    for g in range(0, 101, 25):
        d.line([P(x0 + g, z0), P(x0 + g, z1)], fill='#C8C5B8')
        d.line([P(x0, z0 + g), P(x1, z0 + g)], fill='#C8C5B8')
    # Real roads and creek, where the block is already laid out in data.
    f = 'tools/qingxi-terrain/novice-village.json' if b['id'] == 'A1' else f"tools/qingxi-terrain/blocks/{b['id']}.json"
    if os.path.exists(f):
        lay = json.load(open(f, encoding='utf-8'))
        n = {i['id']: i for i in lay.get('nodes', [])}
        for e in lay.get('edges', []):
            if e['from'] in n and e['to'] in n:
                d.line([P(n[e['from']]['x'], n[e['from']]['z']), P(n[e['to']]['x'], n[e['to']]['z'])], fill='#B08A5A', width=max(2, int(e.get('width', 3) * S)))
        c = lay.get('creek')
        if c:
            pts = c['points']
            d.line([P(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)], fill='#6E9DB8', width=max(3, int(c.get('width', 4) * S)))
    for z in b['zones']:
        d.rectangle([P(z['x'] - z['hx'], z['z'] + z['hz']), P(z['x'] + z['hx'], z['z'] - z['hz'])], fill='#EFE3C6', outline='#6A5A3C', width=2)
        d.text((P(z['x'] - z['hx'], z['z'] + z['hz'])[0] + 3, P(z['x'] - z['hx'], z['z'] + z['hz'])[1] + 2), z['name'], fill='#3A2C16', font=small)
    for s in b['shots']:
        q = P(s['x'], s['z'])
        col = '#1E5FA8' if s.get('ka') else '#5B8DC4'
        for side in (-1, 1):
            a = math.radians(s['yaw'] + side * 27.5)
            d.line([q, (q[0] + math.sin(a) * 110, q[1] - math.cos(a) * 110)], fill=col, width=2)
        d.ellipse([q[0] - 6, q[1] - 6, q[0] + 6, q[1] + 6], fill=col)
        d.text((q[0] + 8, q[1] - 8), s['id'].split('-')[1], fill=col, font=font)
    d.rectangle([0, H - 36, W, H], fill='#FFFFFF')
    d.text((8, H - 30), f"{b['id']} {b['name']}　格線 25 m　棕＝路　藍線＝水　藍點＝鏡頭", fill='#222', font=small)
    im.save(f"{OUT}/{b['id']}.png")


def markdown():
    L = ['# 世界施工圖 v1', '',
         '> 2026-11-08，Claude Code 依 z1nnz 指示規劃：「區塊所有的配置，哪裡要放什麼東西、地形要怎麼走，先規劃好再丟給 Codex，照著要求建出來，而且要有好多個畫面。」',
         '> 這份由 `tools/qingxi-terrain/world-blueprint.json` 產生，**要改請改 JSON** 再跑 `python tools/qingxi-terrain/render-world-blueprint.py`。',
         '> 上一層：[區塊規劃](../novice-world-block-plan.md)、[擺放填充](../novice-world-dressing-plan.md)。視覺標準：[場景畫面](../2026-11-08/codex-v5-scene-shots.md)。', '',
         '![總圖](overview.png)', '',
         '## 怎麼用', '',
         '1. **照順序一塊一塊建**，一塊通過才接下一塊。這是建造順序，不是玩家的遊玩順序。',
         '2. 擺法照「成組」：同一分區的東西要互相靠近，不要一件件隔開展示。',
         '3. 每塊建完，在每個**鏡頭**的位置截圖（眼高 1.6 m、水平視角 55°），存到 `art/previews/blueprint/<區塊>/<鏡頭>.jpg`。有主視覺的並排比對。',
         '4. 「必須看到」是驗收條件。', '',
         '## 自由度', '', '### 玩家', ''] + [f'- {x}' for x in data['freedom']['player']] + ['', '### 建造的人', ''] + [f'- {x}' for x in data['freedom']['builder']] + ['',
         '## 施工順序', '',
         '| 順序 | 區塊 | 什麼時候用到 | 感覺 | 鏡頭 | 分區 |', '|---:|---|---|---|---:|---:|']
    for b in sorted(blocks, key=lambda x: x['order']):
        L.append(f"| {b['order']} | [{b['id']} {b['name']}](#{b['id'].lower()}-{b['name']}) | {b['days']} | {b['feel']} | {len(b['shots'])} | {len(b['zones'])} |")
    total = sum(len(b['shots']) for b in blocks)
    L += ['', data.get('size', ''), '', f'共 {len(blocks)} 塊、{total} 個鏡頭。之後再規劃：' + '、'.join(data['later']) + '。', '']
    allbad = {}
    for b in sorted(blocks, key=lambda x: x['order']):
        L += [f"## {b['id']} {b['name']}", '', f"![{b['id']}]({b['id']}.png)", '',
              f"- **感覺**：{b['feel']}", f"- **地形**：{b['terrain']}", f"- **地標**：{b['landmark']}", f"- **填充**：{b['fill']}", '',
              '### 分區與擺放', '', '| 分區 | 中心 | 大小 | 模型 | 件數 | 擺法 |', '|---|---|---|---|---:|---|']
        for z in b['zones']:
            for i, g in enumerate(z['groups']):
                head = f"{z['name']} `{z['id']}` | ({z['x']}, {z['z']}) | {z['hx'] * 2:g}×{z['hz'] * 2:g}" if i == 0 else ' | | '
                models = g['models'].replace(',', '、')
                tag = '（待合併）' if g.get('tag') == 'pending' else ''
                L.append(f"| {head} | {models}{tag} | {g['count']} | {g['how']} |")
        L += ['', '### 鏡頭', '', '| 鏡頭 | 位置 | 朝向 | 時間 | 主視覺 | 必須看到 |', '|---|---|---:|---|---|---|']
        for s in b['shots']:
            L.append(f"| {s['id']} | ({s['x']}, {s['z']}) | {s['yaw']}° | {s['time']} | {s.get('ka', '—')} | {s['must']} |")
        miss = list(b['missing'])
        bad = check(b)
        if bad:
            allbad[b['id']] = bad
            miss.append('清單裡找不到模型檔：' + '、'.join(f'`{m}`' for m in bad))
        if miss:
            L += ['', '### 還缺', ''] + [f'- {m}' for m in miss]
        L.append('')
    open(f'{OUT}/README.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(L))
    return allbad, total


overview()
for b in blocks:
    block_map(b)
bad, total = markdown()
print('blocks', len(blocks), 'shots', total)
print('models not found:', json.dumps(bad, ensure_ascii=False))
