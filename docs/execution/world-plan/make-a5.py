"""固定產生 A5 渡口的模型座標與區塊佈局。"""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "tools/qingxi-terrain/blocks/A5.json"


def item(id_, role, model, x, z, yaw, footprint, collider="none", zone="a5-pier"):
    return {
        "id": id_, "zone": zone, "role": role, "model": model,
        "x": x, "z": z, "yaw": yaw, "footprint": footprint,
        "collider": collider, "status": "needs-importer", "author": "既有美術包",
    }


fe = "art/exports/valley-and-home-v1/"
segments = [
    (-97, -80, "Straight"), (-97, -78, "Straight"),
    (-97, -76, "Straight"), (-97, -74, "Straight"),
    (-98, -72, "Corner"), (-100, -72, "Straight"),
    (-102, -72, "Straight"), (-104, -72, "End"),
]
versions = {"Straight": "v006", "Corner": "v004", "End": "v004"}
items = []
for i, (x, z, kind) in enumerate(segments, 1):
    model = f"{fe}FE01/{kind}/{versions[kind]}/FE01_{kind}.fbx"
    items.append(item(f"A5_Pier_{i:02d}", f"L 形木棧橋第 {i} 段", model, x, z, 0 if i <= 4 else 270, [2.2, 2.4, 0.5], "box"))

items += [
    item("A5_Ferry", "繫在棧橋末端的擺渡船", fe + "FE02/v007/FE02_Ferry.fbx", -109, -72, 45, [5.5, 2.2, 1.7], "mesh"),
    item("A5_Shed", "南岸渡口小棚", fe + "FE03/v007/FE03_FerryShed.fbx", -90, -82, 230, [5, 3.5, 3], "box", "a5-shed"),
    item("A5_Milestone", "往官道的里程石", "Assets/YunJing/Models/RuinsB/R05_Milestone/R05_Milestone_v001.fbx", -64, -90, 90, [0.9, 0.6, 1.6], "box", "a5-shed"),
]

reed_points = [
    (-101, -77), (-94, -74),
    (-116, -57), (-119, -60), (-123, -65), (-127, -69),
    (-133, -76), (-138, -83), (-143, -90), (-122, -83),
    (-118, -86), (-113, -88), (-107, -86), (-103, -84),
]
for i, (x, z) in enumerate(reed_points, 1):
    items.append(item(f"A5_Reed_{i:02d}", f"河灣低面數蘆葦第 {i} 叢", "art/exports/core-ruins-v1/CO04_ReedClump/CO04_ReedClump_v001.fbx", x, z, (i * 37) % 360, [1.5, 1.5, 1.8]))

fish_points = [(-94, -85), (-92, -86), (-90, -87), (-88, -86), (-93, -88)]
for i, (x, z) in enumerate(fish_points, 1):
    items.append(item(f"A5_Fishing_{i:02d}", f"渡口釣具第 {i} 件", f"art/exports/creekside-life-c/FI{i:02d}_v001.fbx", x, z, (i * 53) % 360, [0.8, 0.8, 1.2], "none", "a5-shed"))
assert len(items) == 30

data = {
    "version": 2, "units": "m", "block": "A5",
    "note": "A5 河灣渡口，cell [-1,-1]。世界座標，+Z 北。creek 保持 A3 接縫 4.5 m；河灣擴至約 18 m 與遠湖卡須程式延展。FE01 8 段 L 形、FE02 船、FE03 棚、R05 石、CO04 蘆葦、FI 釣具均有來源檔，需匯入。",
    "bounds": {"minX": -150, "minZ": -150, "sizeX": 100, "sizeZ": 100},
    "noise": 0.15, "relief": 0.75, "terrace": 0, "cliffs": 0,
    "nodes": [
        {"id": "a5-north", "x": -106, "z": -50.5},
        {"id": "a5-bank", "x": -95, "z": -68},
        {"id": "a5-pier-base", "x": -97, "z": -80},
        {"id": "a5-shed", "x": -90, "z": -82},
        {"id": "a5-road", "x": -75, "z": -90},
        {"id": "a5-east", "x": -50.5, "z": -90},
        {"id": "a5-south", "x": -90, "z": -149.5},
        {"id": "a5-reed-view", "x": -115, "z": -101},
    ],
    "edges": [
        {"id": "a5-north-path", "from": "a5-north", "to": "a5-bank", "width": 2, "surface": "dirt"},
        {"id": "a5-bank-pier", "from": "a5-bank", "to": "a5-pier-base", "width": 2.2, "surface": "dirt"},
        {"id": "a5-pier-shed", "from": "a5-pier-base", "to": "a5-shed", "width": 2.2, "surface": "dirt"},
        {"id": "a5-shed-road", "from": "a5-shed", "to": "a5-road", "width": 2.4, "surface": "dirt"},
        {"id": "a5-east-road", "from": "a5-road", "to": "a5-east", "width": 2.4, "surface": "dirt"},
        {"id": "a5-south-path", "from": "a5-road", "to": "a5-south", "width": 2, "surface": "dirt"},
        {"id": "a5-reed-path", "from": "a5-pier-base", "to": "a5-reed-view", "width": 1.8, "surface": "dirt"},
    ],
    "pads": [
        {"id": "a5-pier-pad", "surface": "dirt", "x": -97, "z": -80, "halfX": 4.5, "halfZ": 4.5, "height": 0.8},
        {"id": "a5-shed-pad", "surface": "dirt", "x": -90, "z": -82, "halfX": 4, "halfZ": 3, "height": 1.0},
        {"id": "a5-reed-view-pad", "surface": "dirt", "x": -115, "z": -101, "halfX": 2, "halfZ": 2, "height": 0.5},
    ],
    "heightPoints": [
        {"x": -110, "z": -52, "height": 0.9},
        {"x": -140, "z": -52, "height": 1.0},
        {"x": -52, "z": -90, "height": 2.2},
        {"x": -90, "z": -82, "height": 1.0},
        {"x": -120, "z": -85, "height": 0.35},
        {"x": -145, "z": -95, "height": 0.4},
        {"x": -140, "z": -140, "height": 0.8},
        {"x": -90, "z": -145, "height": 1.3},
        {"x": -55, "z": -140, "height": 1.8},
    ],
    "flats": [
        {"id": "a5-pier-bank", "note": "木棧橋岸側前 5 m 底", "x": -98, "z": -79, "halfX": 3, "halfZ": 5, "height": 0.8, "blend": 2.5},
    ],
    "creek": {
        "note": "A3 南端進來，先用固定 4.5 m 寬保接縫；河灣在 (-121,-75) 需程式擴至 18 m，遠湖卡另做。",
        "width": 4.5, "depth": 1, "bank": 3, "waterLevel": 0.6,
        "points": [-110, -50.5, -110, -60, -112, -68, -121, -75, -134, -85, -148, -96],
        "sourceEnd": True,
    },
    "placements": items, "herbs": [], "fortunes": [], "checkpoints": [], "route": [],
}
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(OUT, len(items))
