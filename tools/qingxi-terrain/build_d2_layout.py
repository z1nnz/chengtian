"""依 D2 六視圖與物件清單產生可重現的佈局資料及俯視施工圖。"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
BLOCK = ROOT / "tools/qingxi-terrain/blocks/D2.json"
PLAN = ROOT / "docs/execution/world-plan/D2-plan.png"
SEED = 1114

FR = "art/exports/forest-roots-b/"
FP = "art/exports/forest-paths-b/"
BM = "art/exports/modelling-basics-c/"
EN = "art/exports/qingxi-encounter-a/"
ET = "art/exports/elder-trees-v1/"


def asset(code: str) -> str:
    if code == "WORLD_TREE":
        return "missing/D2/WorldTreeButtressGroup.fbx"
    if code == "AL01":
        return "art/exports/core-d2-v1/AL01_RootAltarTerrace/AL01_RootAltarTerrace_v001.fbx"
    if code == "CO01":
        return "art/exports/core-ruins-v1/CO01_DugPit/CO01_DugPit_v001.fbx"
    if code.startswith("FR") or code.startswith("FO02"):
        folder = {
            "FR01_Braided": "FR01_RootWall_Braided",
            "FR01_Stacked": "FR01_RootWall_Stacked",
            "FR01_Wave": "FR01_RootWall_Wave",
            "FR02": "FR02_RootArch",
            "FR03_Dense": "FR03_VineCurtain_Dense",
            "FR03_Sparse": "FR03_VineCurtain_Sparse",
            "FO02_A": "FO02_GlowMushroom_A",
            "FO02_B": "FO02_GlowMushroom_B",
            "FO02_C": "FO02_GlowMushroom_C",
        }[code]
        return f"{FR}{folder}/{folder}_v001.fbx"
    if code.startswith("FP"):
        folder = {
            "FP01": "FP01_PathStraight",
            "FP02_L": "FP02_PathCurve30_L",
            "FP02_R": "FP02_PathCurve30_R",
            "FP03": "FP03_PathSlope",
            "FP04": "FP04_PathRootCrossing",
            "FP05": "FP05_PathLogSteps",
        }[code]
        return f"{FP}{folder}/{folder}_v001.fbx"
    if code.startswith("BM"):
        return f"{BM}{code}.fbx"
    if code.startswith("A0"):
        name = {
            "A03": "A03_FallenLog",
            "A04": "A04_MossBoulderCover",
            "A05": "A05_LayeredRockCover",
            "A06": "A06_RootStump",
        }[code]
        return f"{EN}{name}.fbx"
    if code.startswith("Elder"):
        return f"{ET}{code}.fbx"
    return f"missing/D2/{code}.fbx"


def status(code: str) -> str:
    return "needs-importer" if (ROOT / asset(code)).is_file() else "missing"


layout = json.loads(BLOCK.read_text(encoding="utf-8"))
layout["note"] = (
    "D2 神木林地依 V1–V6 重排；神木在微高中央，板根放射圍空地，南根拱、"
    "東往 D6 上坡、西往 D4、北留 D7。缺件仍記座標，整合時跳過。"
)
layout["noise"] = 0.13
layout["relief"] = 0.55
layout["cliffs"] = 1.5
layout["nodes"] = [
    {"id": i, "x": x, "z": z} for i, x, z in [
        ("d2-south", 10, 150.5), ("d2-gate", 10, 167),
        ("d2-view", 8, 178), ("d2-pit", 14, 182),
        ("d2-root-gap", 10, 194), ("d2-altar", 7, 205),
        ("d2-west-fork", -13, 211), ("d2-west", -49.5, 214),
        ("d2-east-gap", 25, 210), ("d2-east-slope", 38, 217),
        ("d2-east", 49.5, 221), ("d2-north", 4, 249.5),
    ]
]
layout["edges"] = [
    {"id": i, "from": a, "to": b, "width": w, "surface": "dirt"}
    for i, a, b, w in [
        ("entry", "d2-south", "d2-gate", 2.5),
        ("gate-view", "d2-gate", "d2-view", 2.4),
        ("view-root", "d2-view", "d2-root-gap", 2.3),
        ("root-altar", "d2-root-gap", "d2-altar", 2.4),
        ("pit-spur", "d2-view", "d2-pit", 1.8),
        ("west-fork", "d2-altar", "d2-west-fork", 2.3),
        ("west-exit", "d2-west-fork", "d2-west", 2.3),
        ("east-gap", "d2-altar", "d2-east-gap", 2.4),
        ("east-slope", "d2-east-gap", "d2-east-slope", 2.4),
        ("east-exit", "d2-east-slope", "d2-east", 2.4),
        ("north-exit", "d2-altar", "d2-north", 2.0),
    ]
]
layout["pads"] = [
    {"id": "tree-base", "surface": "forest", "x": 0, "z": 200, "halfX": 6, "halfZ": 6, "height": 6.3},
    {"id": "altar", "surface": "forest", "x": 7, "z": 205, "halfX": 3.5, "halfZ": 3.5, "height": 5.4},
    {"id": "pit", "surface": "forest", "x": 14, "z": 182, "halfX": 3, "halfZ": 3, "height": 5.5},
    {"id": "view", "surface": "forest", "x": 8, "z": 178, "halfX": 2, "halfZ": 2, "height": 6.0},
]
layout["heightPoints"] = [
    {"x": x, "z": z, "height": h} for x, z, h in [
        (-48, 152, 8.0), (10, 150.5, 7.9), (48, 152, 8.2),
        (-49.5, 214, 9.5), (-40, 200, 8.8), (-24, 202, 7.1),
        (-12, 191, 5.8), (0, 200, 6.3), (7, 205, 5.4),
        (14, 182, 5.5), (25, 210, 7.0), (38, 217, 8.5),
        (49.5, 221, 9.7), (48, 248, 9.4), (4, 249.5, 8.2),
        (-48, 248, 9.3), (10, 167, 6.9), (8, 178, 6.0),
    ]
]
layout["flats"] = [
    {"id": "south-arch", "note": "根拱下保持通行", "x": 10, "z": 167, "halfX": 4.2, "halfZ": 4.5, "height": 6.9, "blend": 3},
    {"id": "altar-approach", "note": "祭壇台階朝南", "x": 7, "z": 201, "halfX": 3, "halfZ": 4, "height": 5.4, "blend": 2},
    {"id": "east-root-gap", "note": "根隙往 D6 上坡", "x": 25, "z": 210, "halfX": 3, "halfZ": 4, "height": 7.0, "blend": 2.5},
]
layout["shots"] = [
    {"id": "D2-V1", "x": 42, "y": 72, "z": 129, "yaw": 320, "pitch": 45, "time": "陰天上午", "lookAtX": 0, "lookAtY": 6, "lookAtZ": 200},
    {"id": "D2-V2", "x": 10, "y": 9.5, "z": 152, "yaw": 0, "pitch": 0, "time": "上午", "lookAtX": 0, "lookAtY": 15, "lookAtZ": 200},
    {"id": "D2-V3", "x": 8, "y": 7.5, "z": 178, "yaw": 350, "pitch": -8, "time": "上午", "lookAtX": 1, "lookAtY": 16, "lookAtZ": 203},
    {"id": "D2-V4", "x": 7, "y": 7.0, "z": 205, "yaw": 180, "pitch": 0, "time": "上午", "lookAtX": 10, "lookAtY": 7, "lookAtZ": 167},
    {"id": "D2-V5", "x": 25, "y": 8.6, "z": 210, "yaw": 55, "pitch": 0, "time": "上午", "lookAtX": 49.5, "lookAtY": 10, "lookAtZ": 221},
    {"id": "D2-V6", "x": 14, "y": 6.3, "z": 184, "yaw": 315, "pitch": 5, "time": "上午", "lookAtX": 12, "lookAtY": 5.5, "lookAtZ": 183},
]

placements: list[dict] = []
clusters: list[dict] = []


def place(code: str, x: float, z: float, yaw: float, role: str, *,
          scale: float = 1, footprint: tuple[float, float, float] = (1, 1, 1),
          collider: str = "none", sink: float = 0, forced_status: str | None = None) -> None:
    n = sum(p["modelCode"] == code for p in placements) + 1
    placements.append({
        "id": f"D2_{code}_{n:03}", "zone": "d2-tree", "role": role,
        "modelCode": code, "model": asset(code), "x": round(x, 2), "z": round(z, 2),
        "yaw": round(yaw, 1), "scale": scale, "sink": sink,
        "footprint": list(footprint), "collider": collider,
        "status": forced_status or status(code), "author": "既有交付或待製作",
    })


def cluster(cid: str, x: float, z: float, radius: float, items: list[tuple[str, int, float, float]],
            note: str, yaw: str = "random", avoid_path: bool = True) -> None:
    radius = min(radius, x + 49, 49 - x, z - 151, 249 - z)
    clusters.append({
        "id": cid, "x": x, "z": z, "radius": radius,
        "items": [{"modelCode": code, "model": asset(code), "count": count,
                   "scaleMin": small, "scaleMax": large, "status": status(code)}
                  for code, count, small, large in items],
        "yaw": yaw, "avoidPath": avoid_path, "note": note,
    })


# 地標與大型物件；神木本體連板根必須由新交付件實現。
place("WORLD_TREE", 0, 200, 0, "神木本體與整組放射板根；舊 GLB 未通過 QA", footprint=(40, 40, 90), collider="trunk-compound")
place("AL01", 7, 205, 0, "祭壇台階朝南；可走面高 0.98 m", footprint=(6, 6, 1), collider="mesh")
place("CO01", 14, 182, 150, "直徑約 4 m 的被挖坑", footprint=(4, 4, .8), collider="rim-only")
place("FR02", 10, 167, 0, "南入口根拱；須在 Unity 核對 8 m 淨跨與 5 m 淨高", footprint=(8, 3, 5), collider="mesh")
for x, z, yaw in [(-17, 184, 235), (-23, 195, 255), (-18, 215, 295), (-7, 226, 350),
                   (12, 226, 25), (22, 215, 55), (22, 191, 115), (-3, 178, 165)]:
    place("BUTTRESS_ROOT", x, z, yaw, "神木放射板根延伸，待整組模型交付後核對", footprint=(12, 3, 4), collider="mesh")
for i, (x, z, yaw) in enumerate([(-24, 184, 35), (-27, 202, 70), (-25, 220, 115),
                                  (21, 228, 45), (31, 219, 65), (29, 190, 110), (22, 175, 140)]):
    place(["FR01_Braided", "FR01_Stacked", "FR01_Wave"][i % 3], x, z, yaw,
          "外圈補板根牆，入口與東西出口留缺口", footprint=(6, 2, 4), collider="mesh")
for x, z, code in [(-35, 232, "ElderPine_B"), (-37, 166, "ElderPine_C"),
                    (-39, 198, "ElderCypress_B"), (-29, 244, "ElderPine_D"),
                    (37, 241, "ElderCypress_C"), (42, 185, "ElderPine_B"),
                    (35, 160, "ElderCypress_D"), (-43, 218, "ElderPine_C")]:
    place(code, x, z, (x * 7 + z) % 360, "外圈次級巨木，中心區不可擋視線", footprint=(7, 7, 30), collider="trunk-compound")
for i, (x, z) in enumerate([(-29, 174), (-31, 188), (-34, 212), (-22, 231),
                             (-11, 238), (18, 239), (33, 230), (39, 209),
                             (32, 181), (25, 162), (-17, 160), (40, 167)]):
    place("A04" if i % 2 == 0 else "A05", x, z, i * 37 % 360,
          "外圈苔巨石；不堵主路", footprint=(3, 3, 2), collider="mesh")
place("HOLLOW_LOG", -34, 225, 38, "外圈唯一空心倒木", footprint=(8, 2, 2), collider="mesh")
for x, z, yaw in [(-32, 175, 48), (-38, 202, 91), (32, 234, 132), (38, 178, 207)]:
    place("A03", x, z, yaw, "外圈倒木；空地內不放", footprint=(6, 1.5, 1.5), collider="mesh")
for x, z, yaw in [(-31, 162, 30), (-37, 224, 77), (30, 244, 145), (37, 196, 250)]:
    place("A06", x, z, yaw, "外圈樹樁；空地內不放", footprint=(2, 2, 1.6), collider="mesh")

# 中型道具逐件落位。FP 模組只是局部木石補強，路面以地形土路為主。
path_parts = [
    ("FP01", 10, 157, 0), ("FP01", 10, 162, 0), ("FP04", 10, 173, 0),
    ("FP02_L", 9, 180, 350), ("FP01", 10, 187, 0), ("FP04", 10, 194, 0),
    ("FP05", 8, 199, 345), ("FP02_R", 2, 207, 270), ("FP01", -7, 210, 270),
    ("FP03", -23, 212, 270), ("FP01", -36, 213, 270),
    ("FP02_L", 15, 207, 75), ("FP04", 23, 210, 70),
    ("FP03", 31, 213, 60), ("FP03", 39, 217, 65), ("FP01", 46, 220, 65),
]
for code, x, z, yaw in path_parts:
    place(code, x, z, yaw, "土路局部補強，不鋪成連續人工棧道", footprint=(2.3, 6, .4), collider="mesh" if code in ("FP03", "FP04", "FP05") else "none")
for i in range(12):
    angle = i * math.tau / 12
    x = 25 * math.cos(angle)
    z = 200 + 24 * math.sin(angle)
    place("FR03_Dense" if i % 3 == 0 else "FR03_Sparse", x, z, i * 30,
          "貼外圈根牆的藤簾，保留通道淨高", footprint=(2, .3, 3))
for i in range(20):
    angle = i * 2.39996
    r = 15 + (i % 4) * 4
    place(["SURFACE_ROOT_A", "SURFACE_ROOT_B", "SURFACE_ROOT_C"][i % 3],
          round(r * math.cos(angle), 1), round(200 + r * math.sin(angle), 1),
          (math.degrees(angle) + 90) % 360, "半埋地表盤根；路線需可跨越", footprint=(3, 1.4, .35))
for i in range(6):
    angle = i * math.tau / 6 + .2
    place("ROTTEN_LOG", 33 * math.cos(angle), 200 + 33 * math.sin(angle), i * 59,
          "長蕈苔的朽木", footprint=(3, 1, 1))
for i in range(12):
    angle = i * math.tau / 12 + .3
    place("BRANCH_PILE", 28 * math.cos(angle), 200 + 28 * math.sin(angle), i * 31,
          "斷枝堆，林地邊緣", footprint=(2, 1.5, .7))
for i in range(22):
    angle = i * 2.39996
    r = 23 + (i % 5) * 4
    place(["BM03_01", "BM03_02", "BM04_01", "BM04_02"][i % 4],
          round(r * math.cos(angle), 1), round(200 + r * math.sin(angle), 1), i * 47 % 360,
          "中型苔石群", footprint=(1.5, 1.4, .8), collider="mesh")
for i, (x, z) in enumerate([(-33, 182), (-29, 234), (36, 228), (38, 173), (-43, 207)]):
    place("ElderWithered" if i % 2 else "JianmuSapling", x, z, i * 52,
          "幼樹或枯立木", footprint=(2, 2, 8), collider="trunk-compound")
for i in range(45):
    lane = i % 3
    if i < 24:
        z = 151 + (i // 3) * 6.3
        x = 10 + (-1.1, 0, 1.1)[lane]
        yaw = 0
    else:
        j = i - 24
        x = 14 + (j // 3) * 5.2
        z = 207 + (j // 3) * 1.7 + (-1.1, 0, 1.1)[lane]
        yaw = 65
    place(["STEP_STONE_A", "STEP_STONE_B", "STEP_STONE_C"][i % 3], x, z, yaw,
          "泥路半埋踏石", footprint=(.7, .5, .15), sink=.08)
for i, (x, z) in enumerate([(32, 213), (36, 216), (40, 218), (44, 219)]):
    place("UPHILL_STAIR", x, z, 65, "通 D6 的不規則嵌土石階；需核對 SG 尺寸", footprint=(2, 3, .5), collider="mesh")
for x, z in [(-6, 207), (18, 215)]:
    place("ROOT_CAVITY", x, z, 0, "根底樹洞口；應做進神木板根組", footprint=(1.5, 1, 1.6))
for i, (x, z) in enumerate([(6, 173), (15, 176), (18, 181), (12, 188), (4, 194),
                             (20, 201), (14, 211), (-5, 214), (29, 215), (11, 163)]):
    place("PUDDLE", x, z, i * 41, "林地淺水窪貼花，非河流", footprint=(1.1, .8, .02))
for i in range(10):
    angle = i * math.tau / 10
    place("PIT_EARTH", 14 + 2.5 * math.cos(angle), 182 + 2.5 * math.sin(angle), i * 36,
          "坑邊翻土與斷根", footprint=(.8, .6, .4))

# 每條路、入口、祭壇、坑與外圈都有小物聚落。固定種子由整合程式使用。
centres = [
    ("south-west", -5, 158, 14), ("south-east", 26, 158, 14),
    ("arch-west", -2, 168, 11), ("arch-east", 21, 169, 10),
    ("view-west", -7, 179, 11), ("view-east", 22, 178, 10),
    ("pit", 15, 184, 8), ("root-southwest", -13, 190, 10),
    ("root-southeast", 22, 192, 11), ("altar-west", -9, 208, 10),
    ("altar-east", 20, 207, 9), ("west-path", -31, 212, 12),
    ("east-path", 34, 215, 10), ("northwest", -25, 235, 13),
    ("northeast", 26, 235, 13), ("north", 5, 234, 11),
]
for i, (name, x, z, r) in enumerate(centres):
    cluster(f"d2-floor-{name}", x, z, r, [
        ("BM09_01", 3, .85, 1.2), ("BM09_02", 2, .85, 1.2),
        ("BROADLEAF_A", 2, .8, 1.2), ("BROADLEAF_B", 2, .8, 1.2),
        ("MUSHROOM_BROWN", 3, .8, 1.3), ("MOSS_CLUMP", 2, .7, 1.2),
        ("LEAF_PILE", 2, .8, 1.4), ("BM01_01", 2, .7, 1.2),
    ], "林下蕨、闊葉、蕈、苔、落葉與碎石；沿根和路外側密植")

for name, x, z, r in [
    ("arch-detail", 10, 169, 7), ("pit-detail", 14, 183, 6),
    ("altar-detail", 7, 205, 8), ("west-detail", -27, 210, 9),
    ("east-detail", 31, 214, 9), ("north-detail", 2, 225, 10),
]:
    cluster(f"d2-detail-{name}", x, z, r, [
        ("LARGE_FERN", 4, .85, 1.1), ("FO02_A", 2, .8, 1.2),
        ("FO02_B", 2, .8, 1.2), ("FO02_C", 1, .8, 1.2),
        ("MUSHROOM_WHITE", 3, .8, 1.2), ("WHITE_FLOWER", 4, .8, 1.2),
        ("TWIGS", 4, .75, 1.3), ("VINE_GROUND", 2, .8, 1.2),
        ("BM02_01", 3, .65, 1.25),
    ], "停留點前中景細節；坑緣、根腳與石台側密，台階留空")

for i, (x, z, r) in enumerate([(-38, 168, 11), (-43, 194, 10), (-38, 227, 11),
                               (-18, 243, 10), (13, 242, 10), (39, 231, 10),
                               (43, 196, 10), (35, 169, 11)]):
    cluster(f"d2-forest-{i+1:02}", x, z, r, [
        ("ElderPine_B" if i % 2 else "ElderPine_C", 6, .8, 1.15),
        ("ElderCypress_B" if i % 2 else "ElderCypress_C", 5, .8, 1.2),
        ("ElderCamphor_B", 3, .8, 1.1),
        ("SHRUB_A", 4, .75, 1.25), ("SHRUB_B", 4, .75, 1.25),
    ], "外圈松為主、黃綠闊葉穿插，中心視線與道路留空")

for name, x, z in [("root-west", -16, 194), ("root-east", 20, 201),
                    ("root-north", 3, 219), ("root-south", 1, 183)]:
    cluster(f"d2-root-{name}", x, z, 8, [
        ("VINE_ROOT", 7, .7, 1.2), ("BARK_PIECE", 5, .7, 1.2),
        ("MOSS_CLUMP", 4, .7, 1.2), ("MUSHROOM_BROWN", 4, .8, 1.2),
    ], "沿板根表面與根腳生長，需以實際模型接觸面校正", "outward")

layout["placements"] = placements
layout["clusters"] = clusters
layout["clusterSeed"] = SEED
layout["herbs"] = []
layout["fortunes"] = []
layout["checkpoints"] = []
layout["route"] = []
layout["creek"] = None


def draw_plan() -> None:
    image = Image.new("RGB", (1500, 1350), "#ede9da")
    d = ImageDraw.Draw(image)
    font_path = Path("C:/Windows/Fonts/msjh.ttc")
    font = ImageFont.truetype(str(font_path), 23) if font_path.is_file() else ImageFont.load_default()
    small = ImageFont.truetype(str(font_path), 18) if font_path.is_file() else ImageFont.load_default()
    x0, y0, s = 90, 80, 11

    def pt(x: float, z: float) -> tuple[int, int]:
        return (round(x0 + (x + 50) * s), round(y0 + (250 - z) * s))

    for i in range(11):
        x = x0 + i * 10 * s
        y = y0 + i * 10 * s
        d.line((x, y0, x, y0 + 1100), fill="#c7c4b8", width=1)
        d.line((x0, y, x0 + 1100, y), fill="#c7c4b8", width=1)
    d.rectangle((x0, y0, x0 + 1100, y0 + 1100), outline="#413b31", width=3)
    node = {n["id"]: n for n in layout["nodes"]}
    for e in layout["edges"]:
        a, b = node[e["from"]], node[e["to"]]
        d.line((*pt(a["x"], a["z"]), *pt(b["x"], b["z"])), fill="#9c7147", width=round(e["width"] * s))
        d.line((*pt(a["x"], a["z"]), *pt(b["x"], b["z"])), fill="#c2a27a", width=round(e["width"] * s * .64))
    for c in clusters:
        x, y = pt(c["x"], c["z"])
        r = round(c["radius"] * s)
        color = "#54744f" if "forest" in c["id"] else "#8fa979"
        d.ellipse((x-r, y-r, x+r, y+r), outline=color, width=2)
        d.ellipse((x-3, y-3, x+3, y+3), fill=color)
    colors = {"WORLD_TREE": "#315d39", "AL01": "#d7c69e", "CO01": "#714a34", "FR02": "#6f4933"}
    for p in placements:
        x, y = pt(p["x"], p["z"])
        code = p["modelCode"]
        if code in ("WORLD_TREE", "AL01", "CO01", "FR02"):
            r = 11 if code == "WORLD_TREE" else 7
            d.ellipse((x-r, y-r, x+r, y+r), fill=colors[code], outline="#2b2925", width=2)
            d.text((x+12, y-10), code, font=small, fill="#27231f")
        elif code == "BUTTRESS_ROOT":
            d.ellipse((x-7, y-7, x+7, y+7), fill="#6e7951")
        elif code.startswith("FR01"):
            d.rectangle((x-5, y-5, x+5, y+5), fill="#756f4a")
        elif code.startswith("Elder"):
            d.ellipse((x-4, y-4, x+4, y+4), fill="#315c49")
    for shot in layout["shots"]:
        x, y = pt(shot["x"], shot["z"])
        if x0 <= x <= x0 + 1100 and y0 <= y <= y0 + 1100:
            d.polygon([(x, y-10), (x-8, y+7), (x+8, y+7)], fill="#c85e42")
            d.text((x+12, y-9), shot["id"], font=small, fill="#7e3027")
    d.text((90, 1200), "D2 神木林地｜100 × 100 m｜+Z 北 ↑", font=font, fill="#222c27")
    d.text((90, 1240), "棕色＝土路　深綠＝外圈樹　淺綠圈＝小物聚落　橙色＝六鏡位", font=small, fill="#343d32")
    d.text((90, 1280), "神木 (0,200)　祭壇 (7,205)　坑 (14,182)　南根拱 (10,167)", font=small, fill="#343d32")
    PLAN.parent.mkdir(parents=True, exist_ok=True)
    image.save(PLAN)


def main() -> None:
    BLOCK.write_text(json.dumps(layout, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    draw_plan()
    counts = Counter(p["modelCode"] for p in placements)
    for c in clusters:
        counts.update({i["modelCode"]: i["count"] for i in c["items"]})
    print(json.dumps({"placements": len(placements), "clusters": len(clusters),
                      "total": sum(counts.values()), "types": len(counts),
                      "missing": sum(1 for p in placements if p["status"] == "missing")
                      + sum(i["count"] for c in clusters for i in c["items"] if i["status"] == "missing")},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
