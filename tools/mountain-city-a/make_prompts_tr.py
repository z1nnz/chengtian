"""Tree redo v2 three-view prompts (docs/execution/2026-11-14/樹木重做-v2-分工.md on feature/qingxi-creek-chapter, A's part:
TR04/06/07/08/09 v002). Object sentences are written from the package table, the world-tree method (tree-method/) and the A1
concept view V5 (the creek path: a weeping willow leaning over the water, long fine hanging streamers). Single-object Layout
+ 5.2; negatives 5.3 plus the package's bans (leaf cards, leaf clumps, ball crowns, mirrored branches) and no Japanese look.

    python tools/mountain-city-a/make_prompts_tr.py        -> tools/mountain-city-a/prompts_tr.json
    python tools/mountain-city-a/gen_threeviews.py --prompts prompts_tr.json TR06
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
base = json.loads((HERE / 'prompts.json').read_text(encoding='utf-8'))
NEG = ('Japanese garden style, bonsai, topiary, round ball-shaped crown, crown made of several balls, leaf clumps, flat leaf '
       'cards, symmetric mirrored branches, branches all the same thickness, straight vertical pole trunk, fluorescent neon '
       'green, glossy plastic leaves, cartoon lollipop tree, flowers, lettering, lanterns, people')
VALLEY = (' Rural southern Chinese mountain village by a clear stream; muted natural colours, realistic proportions, '
          'real-world scale.')
ITEMS = {
    'TR06': ('Three-view orthographic turnaround sheet (front, side, top) of a single mature weeping willow tree about 10 m '
             'tall growing on a stream bank: a stout gnarled trunk about 0.5 m across that leans clearly to one side over '
             'the water in a gentle S-curve, rough grey-brown furrowed bark with a swollen root flare and one burl; five to '
             'seven unequal main limbs arching up and out, asymmetric, one long limb reaching far over the water; from '
             'every limb many thin flexible twigs arch over and hang straight down in long fine curtains of streamers 2 to '
             '5 m long, some nearly touching the ground, with gaps between the curtains where the limbs and sky show '
             'through; each streamer carries many small narrow lance-shaped leaves; muted willow green, lighter yellow-green '
             'at the outer tops, darker cool green inside and below.' + VALLEY +
             ' Show only this one tree with a small patch of bank; no water plants, no fence, no buildings, no writing.'),
}
items = {k: {'object': v, 'layout': 'single', 'negative_extra': NEG} for k, v in ITEMS.items()}
out = {k: base[k] for k in ('style52', 'negative53', 'layout_single', 'layout_building')}
out['items'] = items
(HERE / 'prompts_tr.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
print(len(items), 'items -> prompts_tr.json')
