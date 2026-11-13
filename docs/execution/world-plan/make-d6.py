"""固定產生 D6 古林到山腳的區塊資料。"""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "tools/qingxi-terrain/blocks/D6.json"


def item(id_, role, model, x, z, yaw, footprint, collider="mesh", status="needs-importer", zone="d6-slope"):
    return {"id": id_, "zone": zone, "role": role, "model": model, "x": x, "z": z,
            "yaw": yaw, "footprint": footprint, "collider": collider,
            "status": status, "author": "既有美術包"}


items = [
    item("D6_Marker", "山腳界碑暫以 R05 里程石代替", "Assets/YunJing/Models/RuinsB/R05_Milestone/R05_Milestone_v001.fbx", 140, 198, 90, [0.9, 0.6, 1.6], "box", "ready", "d6-marker"),
]

for i in range(8):
    x = 124 + i * 3.4
    z = 201 - i * 0.4
    items.append(item(f"D6_Stair_{i+1:02d}", f"上山第一段石階第 {i+1} 件", "Assets/YunJing/Models/TeaTerracesB/TE03_Stair/TE03_Stair_v001.fbx", round(x, 1), round(z, 1), 88, [2.4, 3.2, 0.65], "mesh", "ready", "d6-marker"))

forest = "art/exports/forest-paths-b/"
items += [
    item("D6_Path_1", "林道前段", forest + "FP01_PathStraight/FP01_PathStraight_v001.fbx", 67, 219, 85, [2.4, 6, 0.25], "none"),
    item("D6_Path_2", "林道彎段", forest + "FP02_PathCurve30_R/FP02_PathCurve30_R_v001.fbx", 87, 215, 95, [2.4, 6, 0.25], "none"),
    item("D6_Path_3", "林道坡段", forest + "FP03_PathSlope/FP03_PathSlope_v001.fbx", 110, 209, 110, [2.4, 6, 0.4], "mesh"),
    item("D6_RootWall", "西側最後一片巨根", "art/exports/forest-roots-b/FR01_RootWall_Wave/FR01_RootWall_Wave_v001.fbx", 72, 226, 30, [7, 2, 4], "mesh"),
]

rock_points = [(76, 185), (88, 196), (102, 186), (110, 232), (119, 222),
               (130, 231), (134, 180), (143, 217), (96, 239), (59, 190)]
for i, (x, z) in enumerate(rock_points, 1):
    items.append(item(f"D6_Rock_{i:02d}", f"山腳岩石第 {i} 群", "art/exports/qingxi-encounter-a/A05_LayeredRockCover.fbx", x, z, (i * 31) % 360, [2.5, 2.5, 1.8], "mesh"))

for i, (x, z) in enumerate([(65, 207), (79, 229), (95, 226), (115, 187)], 1):
    items.append(item(f"D6_Fern_{i:02d}", f"林石交界蕨第 {i} 叢", "art/exports/modelling-basics-c/BM09_01.fbx", x, z, (i * 53) % 360, [1.3, 1.3, 0.8], "none"))
assert len(items) == 27

data = {
    "version": 2, "units": "m", "block": "D6",
    "note": "D6 古林深處往山腳，cell [1,2]。世界座標，+Z 北。D2 東口 (49.5,221) 接 D6 西口 (50.5,221)；東緣 (149.5,200) 接 B1。BS01 尚無 FBX，以 R05 里程石暫代。",
    "bounds": {"minX": 50, "minZ": 150, "sizeX": 100, "sizeZ": 100},
    "noise": 0.2, "relief": 1.1, "terrace": 0, "cliffs": 4.2,
    "nodes": [
        {"id": "d6-west", "x": 50.5, "z": 221},
        {"id": "d6-forest", "x": 72, "z": 219},
        {"id": "d6-turn", "x": 100, "z": 213},
        {"id": "d6-stair-foot", "x": 122, "z": 202},
        {"id": "d6-marker", "x": 140, "z": 198},
        {"id": "d6-east", "x": 149.5, "z": 200},
    ],
    "edges": [
        {"id": "d6-trail-1", "from": "d6-west", "to": "d6-forest", "width": 2.4, "surface": "dirt"},
        {"id": "d6-trail-2", "from": "d6-forest", "to": "d6-turn", "width": 2.4, "surface": "dirt"},
        {"id": "d6-trail-3", "from": "d6-turn", "to": "d6-stair-foot", "width": 2.4, "surface": "dirt"},
        {"id": "d6-stairs", "from": "d6-stair-foot", "to": "d6-marker", "width": 2.4, "surface": "plaza"},
        {"id": "d6-to-b1", "from": "d6-marker", "to": "d6-east", "width": 2.4, "surface": "plaza"},
    ],
    "pads": [
        {"id": "d6-marker-pad", "surface": "plaza", "x": 140, "z": 198, "halfX": 5, "halfZ": 5, "height": 27.5},
        {"id": "d6-stair-foot-pad", "surface": "dirt", "x": 122, "z": 202, "halfX": 3, "halfZ": 3, "height": 22.5},
    ],
    "heightPoints": [
        {"x": 52, "z": 221, "height": 9.7},
        {"x": 52, "z": 155, "height": 10.2},
        {"x": 72, "z": 219, "height": 13.1},
        {"x": 100, "z": 213, "height": 18.2},
        {"x": 122, "z": 202, "height": 22.5},
        {"x": 140, "z": 198, "height": 27.5},
        {"x": 148, "z": 200, "height": 29.5},
        {"x": 148, "z": 155, "height": 21.0},
        {"x": 145, "z": 245, "height": 28.0},
        {"x": 55, "z": 245, "height": 11.0},
    ],
    "flats": [
        {"id": f"d6-step-flat-{i+1:02d}", "note": f"TE03 第 {i+1} 件底座", "x": round(124+i*3.4,1), "z": round(201-i*0.4,1), "halfX": 1.4, "halfZ": 1.4, "height": round(22.8+i*0.8,1), "blend": 1.4}
        for i in range(8)
    ],
    "placements": items, "creek": None, "herbs": [], "fortunes": [], "checkpoints": [], "route": [],
}
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(OUT, len(items))
