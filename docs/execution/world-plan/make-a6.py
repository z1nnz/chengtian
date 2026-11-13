"""按 A6 俯視配置固定產生水田、田埂、300 株稻與區塊 JSON。"""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "tools/qingxi-terrain/blocks/A6.json"


def placement(id_, role, model, x, z, yaw, footprint, collider="none", zone="a6-paddy"):
    return {
        "id": id_, "zone": zone, "role": role, "model": model,
        "x": round(x, 2), "z": round(z, 2), "yaw": yaw,
        "footprint": footprint, "collider": collider,
        "status": "needs-importer", "author": "既有美術包",
    }


field_centres = [
    (65, -92), (77, -93), (89, -91), (101, -94), (113, -92),
    (65, -113), (77, -111), (89, -114), (101, -112), (113, -113),
]

paddy_path = "art/exports/valley-and-home-v1/RI01/v014/RI01_Paddy.fbx"
rice_path = "art/exports/valley-and-home-v1/RI02/v006/RI02_Rice.fbx"
bund_root = "art/exports/valley-and-home-v1/RI01/v014/"
placements = [
    placement("A6_GreatWheel", "跨北渠的 9 m 大水車", "art/exports/tea-terraces-b/RI03_GreatWheel/RI03_GreatWheel_v001.fbx", 95, -70, 90, [9, 3, 9], "mesh", "a6-wheel"),
    placement("A6_CanalPlank", "田東側跨 2.2 m 水渠的踏板", "art/exports/qingxi-gathering-visual-kit-v1/QX_CreekSteppingPlank/v002/QX_CreekSteppingPlank.fbx", 125, -102, 90, [3.5, 2.2, 0.3], "box", "a6-paddy"),
]

for i, (cx, cz) in enumerate(field_centres, 1):
    placements.append(placement(f"A6_Paddy_{i:02d}", f"第 {i} 塊水田，水面與稻株底座", paddy_path, cx, cz, (i % 3) * 3, [9, 8, 0.25]))

bunds = []
for z in (-84, -121):
    for x in (65, 77, 89, 101, 113):
        bunds.append((x, z, 90, "Straight"))
for x in (59, 119):
    for z in (-90, -100, -110, -119):
        bunds.append((x, z, 0, "Straight"))
for x in (65, 77, 89, 101, 113):
    bunds.append((x, -102, 90, "Straight"))
for x in (71, 83, 95, 107):
    for z in (-93, -113):
        bunds.append((x, z, 0, "Corner" if x in (71, 107) else "Straight"))
bunds.append((95, -102, 0, "T"))
assert len(bunds) == 32
for i, (x, z, yaw, form) in enumerate(bunds, 1):
    model = f"RI01_Bund_{form}.fbx"
    placements.append(placement(f"A6_Bund_{i:02d}", f"第 {i} 段田埂，{form}", bund_root + model, x, z, yaw, [7 if form == "Straight" else 1.6, 0.8, 0.5], "box"))

for field_index, (cx, cz) in enumerate(field_centres, 1):
    for row in range(6):
        for col in range(5):
            n = (field_index - 1) * 30 + row * 5 + col + 1
            x = cx - 3.2 + col * 1.6 + ((row % 2) - 0.5) * 0.18
            z = cz - 3.1 + row * 1.24
            placements.append(placement(f"A6_Rice_{n:03d}", f"第 {field_index} 塊田第 {row + 1} 行第 {col + 1} 株稻", rice_path, x, z, (n * 37) % 360, [0.45, 0.45, 1.2]))
assert len(placements) == 344

data = {
    "version": 2, "units": "m", "block": "A6",
    "note": "A6 稻田與大水車，cell [1,-1]。世界座標，+Z 北。10 塊田、32 段埂、300 株稻是確定性落位，不靠隨機重抽。RI 模型待匯入；水車動畫與稻作階段由程式處理。",
    "bounds": {"minX": 50, "minZ": -150, "sizeX": 100, "sizeZ": 100},
    "noise": 0.12, "relief": 0.5, "terrace": 0, "cliffs": 0,
    "nodes": [
        {"id": "a6-west", "x": 50.5, "z": -90},
        {"id": "a6-field-west", "x": 55, "z": -90},
        {"id": "a6-upper-west", "x": 55, "z": -76},
        {"id": "a6-field-mid", "x": 55, "z": -102},
        {"id": "a6-field-south", "x": 55, "z": -126},
        {"id": "a6-south", "x": 60, "z": -149.5},
        {"id": "a6-wheel", "x": 88, "z": -70},
        {"id": "a6-north", "x": 95, "z": -50.5},
        {"id": "a6-field-east", "x": 124, "z": -102},
        {"id": "a6-east", "x": 149.5, "z": -100},
        {"id": "a6-shrine", "x": 135, "z": -105},
    ],
    "edges": [
        {"id": "a6-entry", "from": "a6-west", "to": "a6-field-west", "width": 2.4, "surface": "dirt"},
        {"id": "a6-upper-path", "from": "a6-field-west", "to": "a6-upper-west", "width": 2.4, "surface": "dirt"},
        {"id": "a6-wheel-path", "from": "a6-upper-west", "to": "a6-wheel", "width": 2.4, "surface": "dirt"},
        {"id": "a6-north-path", "from": "a6-wheel", "to": "a6-north", "width": 2.2, "surface": "dirt"},
        {"id": "a6-field-path-1", "from": "a6-field-west", "to": "a6-field-mid", "width": 1.8, "surface": "dirt"},
        {"id": "a6-field-path-2", "from": "a6-field-mid", "to": "a6-field-south", "width": 1.8, "surface": "dirt"},
        {"id": "a6-south-path", "from": "a6-field-south", "to": "a6-south", "width": 2.0, "surface": "dirt"},
        {"id": "a6-east-path", "from": "a6-field-mid", "to": "a6-field-east", "width": 1.8, "surface": "dirt"},
        {"id": "a6-shrine-path", "from": "a6-field-east", "to": "a6-shrine", "width": 1.8, "surface": "dirt"},
        {"id": "a6-border-east", "from": "a6-shrine", "to": "a6-east", "width": 2.0, "surface": "dirt"},
    ],
    "pads": [
        {"id": "a6-wheel-pad", "surface": "dirt", "x": 95, "z": -70, "halfX": 6, "halfZ": 5, "height": 1.8},
        {"id": "a6-shrine-pad", "surface": "dirt", "x": 135, "z": -105, "halfX": 4, "halfZ": 4, "height": 1.7},
    ] + [
        {"id": f"a6-field-{i:02d}", "surface": "forest", "x": x, "z": z, "halfX": 4.6, "halfZ": 4.1, "height": round(1.15 + (i % 3) * 0.22, 2)}
        for i, (x, z) in enumerate(field_centres, 1)
    ],
    "heightPoints": [
        {"x": 52, "z": -90, "height": 2.3},
        {"x": 52, "z": -130, "height": 1.9},
        {"x": 95, "z": -52, "height": 1.6},
        {"x": 135, "z": -52, "height": 2.6},
        {"x": 90, "z": -105, "height": 1.5},
        {"x": 145, "z": -100, "height": 2.0},
        {"x": 90, "z": -145, "height": 1.4},
        {"x": 140, "z": -145, "height": 1.8},
    ],
    "flats": [
        {"id": "a6-canal-bed", "note": "北渠及水車底", "x": 95, "z": -69, "halfX": 2.2, "halfZ": 12, "height": 1.2, "blend": 2.0},
    ],
    "creek": {
        "note": "以河道欄位暫表北渠；A4 南界尚無供水段，須由程式接通並區分水渠材質。",
        "width": 2.2, "depth": 0.7, "bank": 1.0, "waterLevel": 0.35,
        "points": [95, -50.5, 95, -70, 112, -79, 123, -89, 125, -124], "sourceEnd": True,
    },
    "placements": placements, "herbs": [], "fortunes": [], "checkpoints": [], "route": [],
}

OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"{OUT}: {len(placements)} placements")
