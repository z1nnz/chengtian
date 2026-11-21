"""11/11 package A (40 h, river-valley commons) three-view prompts: CB01 covered bridge, OS01 village stage, MH01 meeting
hall, AW01 market awnings. Object sentences from the package section 6; prompt = object sentence + scope sentence +
building Layout (11/07 B package) + 5.2; negatives = 5.3 + the package's extra sentence (section 6) + per-item negatives.
The style / negative / layout blocks are read from prompts.json (same source as the 11/05 and 11/08 rounds).

    python tools/mountain-city-a/make_prompts_1111.py          -> tools/mountain-city-a/prompts_1111.json
    python tools/mountain-city-a/gen_threeviews.py --prompts prompts_1111.json CB01 OS01 MH01 AW01
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
base = json.loads((HERE / 'prompts.json').read_text(encoding='utf-8'))
PKG_NEG = ('not Japanese, no torii, no Noh stage, no noren, no round paper lanterns, not Tudor half-timbering, no bright teal roof, '
           'no gold ornament, no glossy plastic look')
VALLEY = ('river-valley village style of southern China: rough grey river stone, old dark weathered timber, dark grey clay tiles '
          '#3A4048, plain and modest, no white granite, no bronze fittings')
ITEMS = {
    'CB01': ('Three-view orthographic turnaround sheet of a rural Chinese covered timber bridge over a small river, about 16 m long, '
             '4.5 m wide and 6.5 m tall, two rough stone piers, heavy timber beams carrying a plank deck, a long open gallery roof of '
             'dark grey clay tiles along the whole bridge, plain wooden railings and a row of built-in benches on both sides, old '
             'weathered dark wood, moss on the piers, modest village craftsmanship, no people, no writing.',
             ' Show only this one bridge as a single game module, straight and level, the deck at the same height at both ends, a '
             'clear walkway at least 2.4 m wide and 2.6 m high inside the gallery, a strong recognisable roof silhouette from far '
             'away (a slightly raised middle roof section is welcome), ' + VALLEY + '; not a stone arch bridge, not a chain or rope '
             'bridge, no water, no river banks, no people, no lettering.',
             ', stone arch bridge, chain bridge, rope bridge, suspension bridge, red lacquer, painted beams, pagoda, multi-storey tower, water, river, landscape'),
    'OS01': ('Three-view orthographic turnaround sheet of a small rural Chinese village opera stage, about 8 m wide, 7 m deep and 7 m '
             'tall, a timber platform raised about 1.2 m on stone footings, open on three sides, a plank back wall with two small side '
             'doors, a hip-and-gable dark grey tile roof with restrained upturned eaves, one wooden side stair, completely empty stage, '
             'old weathered dark wood, no people, no props, no writing.',
             ' Show only this one stage as a single building, ' + VALLEY + ', no lettering, no banners.',
             ', red lacquer, painted beams, curtains, lanterns, people, actors, props, landscape'),
    'MH01': ('Three-view orthographic turnaround sheet of a modest rural Chinese village meeting hall, about 11 m wide, 8 m deep and '
             '6.5 m tall, a single-storey three-bay timber hall on a low stone platform with three stone steps, a front veranda under '
             'deep eaves, removable plank doors across the open front, plaster side walls on stone footings, dark grey clay tile gable '
             'roof, a blank wooden plaque board above the entrance, sturdy and plain, larger than a farmhouse but not grand, no people, '
             'no writing.',
             ' Show only this one building, ' + VALLEY + ', the plaque board completely blank.',
             ', red lacquer, painted beams, temple, palace, lettering on the plaque, people, landscape'),
    'AW01': ('Three-view orthographic turnaround sheet of three rustic Chinese market cloth awnings, each about 3 m wide, 2.5 m deep '
             'and 2.6 m tall, old patched cloth sagging between bamboo and wooden poles with guy ropes, shown as three types: single '
             'slope, double slope, and a slanted prop-pole lean-to, in faded indigo, ochre and off-white, no stall, no goods, no '
             'writing.',
             ' Show the three awnings side by side at the same scale, completely blank cloth with no symbols, no tables, no goods.',
             ', tent, camping tarp, modern canvas, metal poles, stall, table, goods, people, lettering'),
}
items = {k: {'object': o + s, 'layout': 'single' if k == 'AW01' else 'building', 'negative_extra': PKG_NEG + n} for k, (o, s, n) in ITEMS.items()}
out = {k: base[k] for k in ('style52', 'negative53', 'layout_single', 'layout_building')}
out['items'] = items
(HERE / 'prompts_1111.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
print(len(items), 'items -> prompts_1111.json')
