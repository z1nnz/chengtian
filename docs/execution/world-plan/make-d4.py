"""固定產生 D4 苔石古祠的區塊資料。"""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "tools/qingxi-terrain/blocks/D4.json"


def item(id_, role, model, x, z, yaw, footprint, collider="mesh", zone="d4-shrine", status="needs-importer"):
    return {
        "id": id_, "zone": zone, "role": role, "model": model,
        "x": x, "z": z, "yaw": yaw, "footprint": footprint,
        "collider": collider, "status": status, "author": "既有美術包",
    }


ruins = "Assets/YunJing/Models/RuinsB/"
enc = "art/exports/qingxi-encounter-a/"
bm = "art/exports/modelling-basics-c/"
forest = "art/exports/forest-paths-b/"
wall_points = [(-107, 204, 0), (-104, 204, 0), (-101, 204, 0), (-98, 204, 0),
               (-107, 193, 90), (-107, 196, 90), (-107, 199, 90), (-107, 202, 90)]
items = []
for i, (x, z, yaw) in enumerate(wall_points, 1):
    form = "Collapsed" if i in (1, 4, 5, 8) else "Straight"
    model = f"{ruins}R01_DryStoneWall_{form}/R01_DryStoneWall_{form}_v001.fbx"
    items.append(item(f"D4_Wall_{i:02d}", f"古祠兩面殘牆第 {i} 段", model, x, z, yaw, [3, 0.8, 1.8], "box", status="ready"))

items += [
    item("D4_Lantern_1", "倒在東側舊石路旁的破燈", ruins + "R04_StoneLanternBroken/R04_StoneLanternBroken_v001.fbx", -87, 201, 45, [0.8, 0.8, 1.6], "box", status="ready"),
    item("D4_Lantern_2", "倒在祠前的破燈", ruins + "R04_StoneLanternBroken/R04_StoneLanternBroken_v001.fbx", -95, 196, 240, [0.8, 0.8, 1.6], "box", status="ready"),
    item("D4_Stele", "面向東路的古林碑，缺月記號", "art/exports/core-ruins-v1/CO02_OldForestStele/CO02_OldForestStele_v001.fbx", -100, 202, 90, [1.5, 0.8, 3.2]),
    item("D4_Remnants", "祠內香爐、斷供桌與碎瓦", "art/exports/core-ruins-v1/CO03_ShrineRemnants/CO03_ShrineRemnants_v001.fbx", -101, 198, 90, [3, 2.4, 1.6]),
]

rocks = [(-118, 192), (-115, 211), (-109, 216), (-125, 205), (-131, 184), (-112, 177),
         (-88, 219), (-82, 224), (-76, 184), (-64, 235), (-135, 229), (-121, 236)]
for i, (x, z) in enumerate(rocks, 1):
    items.append(item(f"D4_MossRock_{i:02d}", f"苔石第 {i} 群", enc + "A04_MossBoulderCover.fbx", x, z, (i * 31) % 360, [2.2, 2, 1.4], "mesh", "d4-forest"))

for i, (x, z) in enumerate([(-111, 194), (-107, 190), (-92, 207), (-89, 213), (-118, 217), (-81, 192)], 1):
    items.append(item(f"D4_Fern_{i:02d}", f"苔石坡蕨第 {i} 叢", bm + ("BM09_01.fbx" if i % 2 else "BM09_02.fbx"), x, z, (i * 53) % 360, [1.3, 1.3, 0.8], "none", "d4-forest"))

items += [
    item("D4_OldPath_1", "舊石路東段底", forest + "FP01_PathStraight/FP01_PathStraight_v001.fbx", -74, 210, 270, [2.2, 6, 0.3], "none", "d4-path"),
    item("D4_OldPath_2", "舊石路祠前底", forest + "FP03_PathSlope/FP03_PathSlope_v001.fbx", -89, 204, 280, [2.2, 6, 0.4], "mesh", "d4-path"),
]
assert len(items) == 32

data = {
    "version": 2, "units": "m", "block": "D4",
    "note": "D4 苔石古祠，cell [-1,2]。世界座標，+Z 北。東路接 D2 (-50.5,214)，塌牆只留北、西兩面供玩家從東進來。CO02/CO03 模型存在但待匯入；隱藏洞府入口尚無資料與模型，不預放。",
    "bounds": {"minX": -150, "minZ": 150, "sizeX": 100, "sizeZ": 100},
    "noise": 0.22, "relief": 1.2, "terrace": 0, "cliffs": 2.6,
    "nodes": [
        {"id": "d4-east", "x": -50.5, "z": 214},
        {"id": "d4-path-1", "x": -72, "z": 211},
        {"id": "d4-path-2", "x": -88, "z": 205},
        {"id": "d4-shrine", "x": -100, "z": 200},
        {"id": "d4-stele", "x": -100, "z": 195},
    ],
    "edges": [
        {"id": "d4-old-road-1", "from": "d4-east", "to": "d4-path-1", "width": 2.2, "surface": "dirt"},
        {"id": "d4-old-road-2", "from": "d4-path-1", "to": "d4-path-2", "width": 2.2, "surface": "dirt"},
        {"id": "d4-old-road-3", "from": "d4-path-2", "to": "d4-shrine", "width": 2.2, "surface": "dirt"},
        {"id": "d4-courtyard", "from": "d4-shrine", "to": "d4-stele", "width": 2.0, "surface": "dirt"},
    ],
    "pads": [
        {"id": "d4-shrine-pad", "surface": "plaza", "x": -100, "z": 200, "halfX": 8, "halfZ": 7, "height": 13.5},
        {"id": "d4-stele-pad", "surface": "plaza", "x": -100, "z": 195, "halfX": 2, "halfZ": 2, "height": 13.5},
    ],
    "heightPoints": [
        {"x": -140, "z": 152, "height": 14.5},
        {"x": -60, "z": 152, "height": 12.0},
        {"x": -145, "z": 200, "height": 11.5},
        {"x": -125, "z": 200, "height": 10.8},
        {"x": -100, "z": 200, "height": 13.5},
        {"x": -75, "z": 200, "height": 10.8},
        {"x": -52, "z": 214, "height": 9.5},
        {"x": -140, "z": 245, "height": 11.8},
        {"x": -100, "z": 245, "height": 12.2},
        {"x": -55, "z": 245, "height": 10.2},
    ],
    "flats": [
        {"id": "d4-old-road-flat", "note": "舊石路祠前 2.2 m 通行底", "x": -90, "z": 204, "halfX": 9, "halfZ": 2.1, "height": 12.3, "blend": 3},
    ],
    "placements": items, "creek": None,
    "herbs": [], "fortunes": [], "checkpoints": [], "route": [],
}
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(OUT, len(items))
