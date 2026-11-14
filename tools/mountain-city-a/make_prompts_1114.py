"""11/14 package A three-view prompts (docs/execution/2026-11-14/A-120h-roads-yard-and-mountain-street.md). The package
has no object sentences, so they are written here from the package table and the A1 concept views (art/references/blocks/A1,
V1 overhead and V3 from the square: the yard east of the square has rope-wrapped wooden posts, a spear rack and a blank
banner). Single-object Layout + 5.2; negatives 5.3 plus the Japanese / European negatives the reviews asked for and the
package's "no writing anywhere".

    python tools/mountain-city-a/make_prompts_1114.py        -> tools/mountain-city-a/prompts_1114.json
    python tools/mountain-city-a/gen_threeviews.py --prompts prompts_1114.json TG01
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
base = json.loads((HERE / 'prompts.json').read_text(encoding='utf-8'))
NEG = ('Japanese style, makiwara, dojo, torii, shimenawa rope, kanji or any lettering, talismans with writing, European '
       'medieval training dummy, straw knight, armour, metal spikes, modern gym equipment, plastic, glossy, gold ornament, '
       'bright red lacquer')
VALLEY = (' Rural southern Chinese mountain village martial training yard, old dark weathered timber, hemp rope, a little '
          'dark iron, plain and well used; real-world scale.')
ITEMS = {
    'TG01': ('Three-view orthographic turnaround sheet of a Chinese wooden training dummy (mu ren zhuang) for a village '
             'martial arts yard, about 1.7 m tall, a thick round hardwood post about 0.3 m across set into the ground on a '
             'squat rough stone collar, three short wooden arms (two at shoulder height angled forward, one lower in the '
             'middle) and one bent wooden leg near the bottom, the arms and leg pushed through square mortises; the post is '
             'dented and splintered where it is struck, a band of hemp rope wrapped around the striking zone, the arm ends '
             'worn smooth and darker from hands, a few iron wedges at the mortises, moss at the foot.' + VALLEY +
             ' Show only this one dummy; no frame, no fence, no other equipment, no people, no writing.'),
}
items = {k: {'object': v, 'layout': 'single', 'negative_extra': NEG} for k, v in ITEMS.items()}
out = {k: base[k] for k in ('style52', 'negative53', 'layout_single', 'layout_building')}
out['items'] = items
(HERE / 'prompts_1114.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
print(len(items), 'items -> prompts_1114.json')
