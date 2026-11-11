"""Writes tools/qingxi-terrain/blocks/A4.json (東坡茶田) from the same numbers as QingxiTeaTerraceKit.cs: the ground under
each terrace row is levelled to its tread, a strip in front of the first wall, the knoll for the pavilion, and the path
from the village's east road up the stairs to the pavilion. Change Rows/Modules/X0/Shift/Z0/Base/StairX in both places.

  python tools/qingxi-terrain/make-a4.py
"""
import json
from pathlib import Path
ROWS, MODULES, X0, SHIFT, Z0, BASE, STAIR = 6, 5, 64.0, 4.0, -26.0, 1.2, 3
PAV = (122.0, 22.0, 8.6)
front = lambda r: Z0 + 4 * r
lower = lambda r: BASE + r
mx = lambda r, i: X0 + SHIFT * r + 8 * i + 4
flats = [{"id": "a4-foot", "note": "in front of the first wall", "x": mx(0, 2), "z": front(0) - 3, "halfX": 22, "halfZ": 3, "height": lower(0) - .02, "blend": 3.5}]
for r in range(ROWS):
    flats.append({"id": f"a4-row{r}", "note": f"tread of terrace row {r}", "x": mx(r, 2), "z": front(r) + 2, "halfX": 16.5, "halfZ": 2,
                  "height": round(lower(r) + 1 - .03, 3), "blend": .25, "blendX": 6})   # the tapered end pieces run out into the slope
flats.append({"id": "a4-top", "note": "behind the top row, easing up to the knoll", "x": mx(ROWS - 1, 2), "z": front(ROWS - 1) + 6, "halfX": 20, "halfZ": 2,
              "height": round(lower(ROWS - 1) + 1 - .03, 3), "blend": 5})
layout = {
    "version": 2, "units": "m", "block": "A4",
    "note": "A4 東坡茶田（cell [1, 0]）。世界座標。六層梯田往東北爬，石階從中間上去，亭子在頂上的小丘。梯田下的地面由 flats 整平，數字和 QingxiTeaTerraceKit.cs 相同，由 tools/qingxi-terrain/make-a4.py 產生，不要手改。",
    "bounds": {"minX": 50, "minZ": -50, "sizeX": 100, "sizeZ": 100}, "noise": .3, "relief": 1.6, "terrace": 0, "cliffs": 0,
    "nodes": [{"id": "a4-west", "x": 50.5, "z": -14.5}, {"id": "a4-bend", "x": 76, "z": -31}, {"id": "a4-foot", "x": mx(0, STAIR), "z": front(0) - 3.2},
              {"id": "a4-top", "x": mx(ROWS - 1, STAIR), "z": front(ROWS - 1) + 4.6}, {"id": "a4-pavilion", "x": PAV[0] - 3.2, "z": PAV[1] - 3.2}],
    "edges": [{"id": "a4-road-1", "from": "a4-west", "to": "a4-bend", "width": 2.4, "surface": "dirt"},
              {"id": "a4-road-2", "from": "a4-bend", "to": "a4-foot", "width": 2.2, "surface": "dirt"},
              {"id": "a4-path-top", "from": "a4-top", "to": "a4-pavilion", "width": 1.6, "surface": "dirt"}],
    "pads": [{"id": "a4-pavilion", "surface": "dirt", "x": PAV[0], "z": PAV[1], "halfX": 4.2, "halfZ": 4.2, "height": PAV[2]}],
    "heightPoints": [{"x": 56, "z": -14, "height": .4}, {"x": 60, "z": -40, "height": .8}, {"x": 100, "z": -42, "height": 1.6}, {"x": 140, "z": -40, "height": 3.0},
                     {"x": 62, "z": 10, "height": 2.2}, {"x": 66, "z": 40, "height": 3.6}, {"x": 96, "z": 30, "height": 7.0}, {"x": 140, "z": 4, "height": 7.8},
                     {"x": 140, "z": 40, "height": 11.5}, {"x": 112, "z": 10, "height": 8.0},
                     # the hillside either side of the rows climbs with them, so the row ends run into slope, not a raised bank
                     {"x": 66, "z": -18, "height": 2.4}, {"x": 70, "z": -10, "height": 4.0}, {"x": 74, "z": -2, "height": 5.8}, {"x": 78, "z": 6, "height": 7.4},
                     {"x": 112, "z": -24, "height": 2.0}, {"x": 120, "z": -16, "height": 3.6}, {"x": 128, "z": -6, "height": 6.0}, {"x": 134, "z": 4, "height": 7.6}],
    "flats": flats, "placements": [], "herbs": [], "fortunes": [], "checkpoints": [], "route": [],
}
out = Path(__file__).with_name('blocks') / 'A4.json'
out.write_text(json.dumps(layout, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print('wrote', out, len(flats), 'flats')
