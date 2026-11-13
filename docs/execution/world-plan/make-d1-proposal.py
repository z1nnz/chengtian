"""產生 D1 補完提案；不修改既有 blocks/D1.json。"""

import json
from pathlib import Path


OUT = Path(__file__).with_name("D1-proposal.json")


def item(id_, role, model, x, z, yaw, footprint, collider="none", zone="d1-rabbit"):
    return {
        "id": id_, "zone": zone, "role": role, "model": model,
        "x": x, "z": z, "yaw": yaw, "footprint": footprint,
        "collider": collider, "status": "needs-importer", "author": "既有美術包",
    }


enc = "art/exports/qingxi-encounter-a/"
ruins = "art/exports/qingxi-world-ruins-b/"
forest_root = "art/exports/forest-roots-b/"
forest_path = "art/exports/forest-paths-b/"
items = [
    item("D1_WatchTower", "獵場瞭望台，既有空槽替換", enc + "A10_WatchPlatform.fbx", 22, 104, 200, [4, 4, 6], "box", "d1-watch"),
    item("D1_WarningRack", "瞭望台路旁警示布架", enc + "A11_WarningClothRack.fbx", 16, 100, 180, [1.7, 0.9, 2.2], "box", "d1-watch"),
    item("D1_Firewood_1", "工具棚旁柴堆", ruins + "R03_FirewoodScattered/R03_FirewoodScattered_v001.fbx", -13, 85, 40, [1.6, 1.3, 1], "box", "d1-shed"),
    item("D1_Firewood_2", "工具棚後柴堆", ruins + "R03_FirewoodScattered/R03_FirewoodScattered_v001.fbx", -19, 91, 110, [1.6, 1.3, 1], "box", "d1-shed"),
]

tile_models = ["A01_SlopeTile", "A07_RabbitTrailTile", "A02_HollowTile"] * 2
tile_points = [(8, 65), (11, 68), (14, 71), (16, 74), (19, 76), (21, 79)]
for i, (model, (x, z)) in enumerate(zip(tile_models, tile_points), 1):
    items.append(item(f"D1_RabbitTile_{i:02d}", f"山兔坡地表第 {i} 件", enc + model + ".fbx", x, z, 15 * i, [3, 3, 0.3]))

for i, (x, z, model) in enumerate([
    (20, 67, "A03_FallenLog"), (25, 72, "A06_RootStump"),
    (17, 81, "A03_FallenLog"), (25, 82, "A06_RootStump"),
    (7, 79, "A03_FallenLog"), (2, 82, "A06_RootStump"),
], 1):
    items.append(item(f"D1_RabbitWood_{i:02d}", f"兔徑旁倒木或樹樁第 {i} 件", enc + model + ".fbx", x, z, (i * 47) % 360, [5, 1.5, 1.4] if "Log" in model else [2, 2, 1.5], "mesh"))

for i, (x, z, yaw) in enumerate([(27, 67, 35), (29, 72, 70), (27, 78, 110)], 1):
    items.append(item(f"D1_RabbitFence_{i:02d}", f"兔徑外側破竹籬第 {i} 段", enc + "A08_BrokenBambooFence.fbx", x, z, yaw, [2.4, 0.5, 1.8], "box"))

rock_points = [(-28, 108), (-22, 118), (-36, 131), (-41, 98), (-32, 72), (-10, 64), (31, 89), (38, 108), (34, 127), (33, 145), (-34, 143), (-26, 97)]
for i, (x, z) in enumerate(rock_points, 1):
    model = "A04_MossBoulderCover" if i % 2 else "A05_LayeredRockCover"
    items.append(item(f"D1_Rock_{i:02d}", f"林下苔石第 {i} 群", enc + model + ".fbx", x, z, (i * 29) % 360, [2.2, 2, 1.3], "mesh", "d1-forest"))

items += [
    item("D1_NorthRoot_W", "往神木路西側盤根", forest_root + "FR01_RootWall_Braided/FR01_RootWall_Braided_v001.fbx", 15, 137, 60, [7, 2, 4], "mesh", "d1-north"),
    item("D1_NorthRoot_E", "往神木路東側盤根", forest_root + "FR01_RootWall_Wave/FR01_RootWall_Wave_v001.fbx", 34, 134, 300, [7, 2, 4], "mesh", "d1-north"),
    item("D1_NorthPath_1", "北向林道第一段", forest_path + "FP01_PathStraight/FP01_PathStraight_v001.fbx", 25, 120, 0, [2.2, 6, 0.25], "none", "d1-north"),
    item("D1_NorthPath_2", "北向林道第二段", forest_path + "FP02_PathCurve30_L/FP02_PathCurve30_L_v001.fbx", 25, 141, 320, [2.2, 6, 0.25], "none", "d1-north"),
]

proposal = {
    "note": "D1 既有 JSON 由程式端維護；本檔只作精確補完提案。render-block-plan.py 會將同 id 取代既有槽位後畫圖。",
    "heightPoints": [
        {"x": 25, "z": 120, "height": 7.1},
        {"x": 25, "z": 141, "height": 7.8},
        {"x": 10, "z": 149, "height": 7.9},
    ],
    "nodes": [
        {"id": "d1-n1", "x": 25, "z": 120},
        {"id": "d1-n2", "x": 25, "z": 141},
        {"id": "d1-north", "x": 10, "z": 149.5},
    ],
    "edges": [
        {"id": "d1-north-1", "from": "d1-watch", "to": "d1-n1", "width": 2.2, "surface": "dirt"},
        {"id": "d1-north-2", "from": "d1-n1", "to": "d1-n2", "width": 2.2, "surface": "dirt"},
        {"id": "d1-north-3", "from": "d1-n2", "to": "d1-north", "width": 2.2, "surface": "dirt"},
    ],
    "placements": items,
}
assert len(items) == 35
OUT.write_text(json.dumps(proposal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(OUT, len(items))
