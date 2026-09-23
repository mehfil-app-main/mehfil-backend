#!/usr/bin/env python3
"""Store screenshots — frames raw phone captures (any size) into 1080×1920 (9:16) listing images with a caption.

  branding/screenshots/raw/<n>-<slug>.png   raw captures (adb screencap / simctl screenshot)
  branding/screenshots/captions.txt          one line per raw file: "<slug>|Headline|Sub line"
  branding/screenshots/play/<n>-<slug>.png   1080×1920 framed output (Google Play, also fine for App Store 6.5")

Run:  python3 make_screenshots.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).resolve().parent
RAW, OUT = HERE / "screenshots/raw", HERE / "screenshots/play"
ROOT = HERE.parents[1]
FONT_LIGHT = ROOT / "ios/Mehfil/Fonts/Inter-Light.ttf"
FONT_REG = ROOT / "ios/Mehfil/Fonts/Inter-Regular.ttf"
W, H = 1080, 1920
ICON = HERE / "mehfil-icon-1024.png"


def background():
    """The icon's ground, blurred and darkened toward ink, as a soft backdrop."""
    bg = Image.open(ICON).convert("RGB").resize((W, W), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), "#222222")
    canvas.paste(bg.resize((W, H)), (0, 0))
    canvas = canvas.filter(ImageFilter.GaussianBlur(160))
    shade = Image.new("RGB", (W, H), "#222222")
    return Image.blend(canvas, shade, 0.35)


def frame(raw: Path, headline: str, sub: str, out: Path):
    shot = Image.open(raw).convert("RGBA")
    im = background().convert("RGBA")
    d = ImageDraw.Draw(im)
    h1 = ImageFont.truetype(str(FONT_LIGHT), 72); h2 = ImageFont.truetype(str(FONT_REG), 34)
    d.text((W / 2, 150), headline, font=h1, fill="#FFFFFF", anchor="mm")
    d.text((W / 2, 222), sub, font=h2, fill="#D6D3F5", anchor="mm")
    # phone: scale to fit under the caption, rounded corners, soft shadow
    target_h = H - 330
    k = target_h / shot.height
    ph = shot.resize((int(shot.width * k), int(target_h)), Image.LANCZOS)
    r = int(ph.width * 0.075)
    mask = Image.new("L", ph.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, ph.width - 1, ph.height - 1), radius=r, fill=255)
    ph.putalpha(mask)
    x, y = (W - ph.width) // 2, 300
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x, y + 24, x + ph.width, y + ph.height + 24), radius=r, fill=(13, 37, 61, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    im.alpha_composite(shadow); im.alpha_composite(ph, (x, y))
    im.convert("RGB").save(out, quality=95)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    captions = {}
    for line in (HERE / "screenshots/captions.txt").read_text().splitlines():
        if "|" in line:
            slug, head, sub = (line.split("|") + [""])[:3]
            captions[slug.strip()] = (head.strip(), sub.strip())
    for raw in sorted(RAW.glob("*.png")):
        slug = raw.stem.split("-", 1)[1] if "-" in raw.stem else raw.stem
        head, sub = captions.get(slug, (slug.replace("-", " ").title(), ""))
        frame(raw, head, sub, OUT / raw.name)
        print("framed", raw.name)


if __name__ == "__main__":
    main()
