"""把六張 D2 設定圖與同鏡位 Unity 截圖左右並排。"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "art/references/blocks/D2"
CAPTURE = ROOT / "artifacts/windows-novice-village/keyart-shots"
OUTPUT = ROOT / "docs/execution/world-plan/compare"


def fit(image: Image.Image, width: int, height: int) -> Image.Image:
    image = image.convert("RGB")
    image.thumbnail((width, height), Image.Resampling.LANCZOS)
    panel = Image.new("RGB", (width, height), "#202521")
    panel.paste(image, ((width - image.width) // 2, (height - image.height) // 2))
    return panel


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    font_path = Path("C:/Windows/Fonts/msjh.ttc")
    font = ImageFont.truetype(str(font_path), 25) if font_path.is_file() else ImageFont.load_default()
    for number in range(1, 7):
        name = f"D2-V{number}"
        reference = REFERENCE / f"V{number}.png"
        capture = CAPTURE / f"{name}.png"
        if not reference.is_file() or not capture.is_file():
            raise FileNotFoundError(f"缺少並排圖輸入：{reference} 或 {capture}")
        with Image.open(reference) as left, Image.open(capture) as right:
            if not right.convert("RGB").getbbox():
                raise RuntimeError(f"Unity 截圖全黑，不能作為對圖證據：{capture}")
            result = Image.new("RGB", (2560, 760), "#202521")
            result.paste(fit(left, 1280, 720), (0, 40))
            result.paste(fit(right, 1280, 720), (1280, 40))
            d = ImageDraw.Draw(result)
            d.text((20, 7), f"{name} 設定圖", font=font, fill="#f5f0df")
            d.text((1300, 7), f"{name} Unity 同鏡位", font=font, fill="#f5f0df")
            result.save(OUTPUT / f"{name}.jpg", quality=90, subsampling=0)
            print(OUTPUT / f"{name}.jpg")


if __name__ == "__main__":
    main()
