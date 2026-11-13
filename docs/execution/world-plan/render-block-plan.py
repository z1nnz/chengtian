"""依區塊 JSON 畫 100×100 m 配置圖；只使用 PIL，不產生或修改佈局資料。"""

import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
FONT_FILE = Path("C:/Windows/Fonts/msjh.ttc")
if not FONT_FILE.exists():
    FONT_FILE = Path("C:/Windows/Fonts/mingliu.ttc")
FONT = ImageFont.truetype(str(FONT_FILE), 18)
SMALL = ImageFont.truetype(str(FONT_FILE), 15)
TITLE = ImageFont.truetype(str(FONT_FILE), 26)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def height_at(points, x, z):
    if not points:
        return 0.0
    weights = []
    for p in points:
        dist = math.hypot(x - p["x"], z - p["z"])
        if dist < 0.01:
            return p["height"]
        weights.append((1 / (dist * dist), p["height"]))
    return sum(w * h for w, h in weights) / sum(w for w, _ in weights)


def render(block_id):
    data = read_json(ROOT / "tools/qingxi-terrain/blocks" / f"{block_id}.json")
    world = read_json(ROOT / "tools/qingxi-terrain/world-blueprint.json")
    descriptor = next(b for b in world["blocks"] if b["id"] == block_id)
    area = data["bounds"]
    assert area["sizeX"] == area["sizeZ"] == 100
    min_x, min_z = area["minX"], area["minZ"]
    px_per_m = 9
    left, top = 78, 94
    width, height = 1720, 1100
    img = Image.new("RGB", (width, height), "#F7F5EF")
    draw = ImageDraw.Draw(img)

    def xy(x, z):
        return (round(left + (x - min_x) * px_per_m), round(top + (min_z + 100 - z) * px_per_m))

    points = data.get("heightPoints", [])
    for x in range(min_x, min_x + 100, 5):
        for z in range(min_z, min_z + 100, 5):
            h = height_at(points, x + 2.5, z + 2.5)
            t = min(1, max(0, (h - 2) / 11))
            rgb = (round(214 - t * 64), round(225 - t * 52), round(194 - t * 60))
            xa, ya = xy(x, z + 5)
            xb, yb = xy(x + 5, z)
            draw.rectangle((xa, ya, xb, yb), fill=rgb)

    for x in range(min_x, min_x + 101, 10):
        px, _ = xy(x, min_z)
        draw.line((px, top, px, top + 900), fill="#96A79A", width=1)
        draw.text((px - 15, top + 905), str(x), font=SMALL, fill="#33443A")
    for z in range(min_z, min_z + 101, 10):
        _, py = xy(min_x, z)
        draw.line((left, py, left + 900, py), fill="#96A79A", width=1)
        draw.text((18, py - 10), str(z), font=SMALL, fill="#33443A")
    draw.rectangle((left, top, left + 900, top + 900), outline="#34483D", width=3)
    for point in points:
        px, py = xy(point["x"], point["z"])
        draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill="#344C82")
        draw.text((px + 4, py - 22), f'{point["height"]:g}m', font=SMALL, fill="#344C82")

    for pad in data.get("pads", []):
        xa, ya = xy(pad["x"] - pad["halfX"], pad["z"] + pad["halfZ"])
        xb, yb = xy(pad["x"] + pad["halfX"], pad["z"] - pad["halfZ"])
        draw.rectangle((xa, ya, xb, yb), fill="#D9CBB2", outline="#77634B", width=2)
        draw.text((xa + 3, ya + 2), f'{pad["id"]} {pad["height"]}m', font=SMALL, fill="#51402C")

    creek = data.get("creek")
    if creek and creek.get("points"):
        coords = [xy(creek["points"][i], creek["points"][i + 1]) for i in range(0, len(creek["points"]), 2)]
        draw.line(coords, fill="#408EA5", width=round(creek["width"] * px_per_m), joint="curve")

    nodes = {n["id"]: n for n in data.get("nodes", [])}
    for edge in data.get("edges", []):
        a, b = nodes[edge["from"]], nodes[edge["to"]]
        draw.line((xy(a["x"], a["z"]), xy(b["x"], b["z"])), fill="#7A5E42", width=max(3, round(edge["width"] * px_per_m)))
        draw.line((xy(a["x"], a["z"]), xy(b["x"], b["z"])), fill="#CCBA94", width=max(2, round((edge["width"] - 0.4) * px_per_m)))
    for node in nodes.values():
        px, py = xy(node["x"], node["z"])
        draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill="#493624")

    placements = data.get("placements", [])
    dense = lambda p: "_Rice_" in p["id"] or "_Bund_" in p["id"]
    numbered = [p for p in placements if not dense(p)]
    for idx, p in enumerate(placements, 1):
        px, py = xy(p["x"], p["z"])
        color = "#A34C40" if p.get("status") == "needs-importer" else "#316E62"
        if "_Rice_" in p["id"]:
            draw.ellipse((px - 2, py - 2, px + 2, py + 2), fill="#C6A959")
        elif "_Bund_" in p["id"]:
            draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill="#745C3D")
        else:
            number = numbered.index(p) + 1
            draw.ellipse((px - 8, py - 8, px + 8, py + 8), fill=color, outline="white", width=2)
            draw.text((px + 8, py - 15), str(number), font=SMALL, fill="#1D2924")

    for shot in descriptor.get("shots", []):
        if shot["x"] < min_x - 6 or shot["x"] > min_x + 106 or shot["z"] < min_z - 6 or shot["z"] > min_z + 106:
            continue
        px, py = xy(shot["x"], shot["z"])
        yaw = math.radians(shot["yaw"])
        tip = (round(px + math.sin(yaw) * 34), round(py - math.cos(yaw) * 34))
        draw.line(((px, py), tip), fill="#8B3443", width=4)
        draw.ellipse((px - 5, py - 5, px + 5, py + 5), fill="#8B3443")
        draw.text((px + 5, py + 5), shot["id"], font=SMALL, fill="#8B3443")

    draw.text((left, 24), f'{block_id} {descriptor["name"]}｜100×100 m 配置圖', font=TITLE, fill="#22392D")
    draw.text((left + 840, 53), "北 ↑　每格 10 m", font=FONT, fill="#22392D")
    draw.text((left, 1020), "底色為 heightPoints 反距離插值示意；實際地形另受 relief、cliffs、pads 影響。", font=SMALL, fill="#34483D")
    draw.text((left, 1043), "棕色＝路　米色＝平台　藍字＝高度點　紅點＝待匯入件　紅箭＝施工圖鏡位。", font=SMALL, fill="#34483D")

    lx = 1010
    draw.text((lx, 95), "擺放索引（世界座標 x,z；角度見 JSON）", font=FONT, fill="#22392D")
    for idx, p in enumerate(numbered, 1):
        col = 0 if idx <= 24 else 1
        row = idx - 1 if col == 0 else idx - 25
        x = lx + col * 340
        y = 128 + row * 34
        name = p["id"].removeprefix(block_id + "_")
        draw.text((x, y), f'{idx:02d} {name} ({p["x"]},{p["z"]})', font=SMALL, fill="#28392F")
    draw.text((lx, 1015), f'模型件數：{len(placements)}（含無編號的稻株與田埂）；尺寸、朝向見 {block_id}.json', font=SMALL, fill="#28392F")

    out = ROOT / "docs/execution/world-plan" / f"{block_id}-plan.png"
    img.save(out, optimize=True)
    print(out)


if __name__ == "__main__":
    for block_id in sys.argv[1:]:
        render(block_id)
