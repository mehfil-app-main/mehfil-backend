#!/usr/bin/env python3
"""Mehfil app icon — one SVG master (mehfil-icon.svg), rasterised with macOS QuickLook, cut into every asset.

  branding/mehfil-icon.svg                master: brand mesh + gold ribbon M (edit this)
  branding/mehfil-mark.svg                mark only, transparent (for docs, print, the consent screen)
  branding/mehfil-icon-1024.png           App Store Connect / Xcode AppIcon
  branding/mehfil-icon-512.png            Google Play listing icon
  branding/mehfil-icon-120.png            Google OAuth consent-screen logo
  branding/mehfil-feature-1024x500.png    Google Play feature graphic
  ios/Mehfil/Assets.xcassets/AppIcon.appiconset/icon-1024.png
  android …/res/mipmap-*/ic_launcher_background.png   adaptive-icon background (mesh)
  android …/res/mipmap-*/ic_launcher_foreground.png   adaptive-icon foreground (M + sparkles in the safe zone)
  android …/res/drawable/ic_launcher_monochrome.xml   themed-icon layer (Android 13+)
  android …/res/mipmap-*/ic_launcher.png              legacy launcher bitmaps

Run:  python3 make_icon.py   (needs Pillow; QuickLook does the SVG rendering)
"""
import re, subprocess, tempfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]          # …/mehfil
OUT = Path(__file__).resolve().parent
MASTER = OUT / "mehfil-icon.svg"
NAVY = "#1C1E54"
FONT_LIGHT = ROOT / "ios/Mehfil/Fonts/Inter-Light.ttf"
FONT_REG = ROOT / "ios/Mehfil/Fonts/Inter-Regular.ttf"
# Android adaptive icons show the inner 66dp of a 108dp canvas; the mark is scaled about the centre to fit that circle.
ANDROID_MARK_SCALE = 0.68
DENSITIES = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}


def render(svg_text: str, size: int) -> Image.Image:
    """QuickLook renders SVG (gradients, blur, shadows) to PNG; returns RGBA."""
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "icon.svg"; src.write_text(svg_text)
        subprocess.run(["qlmanage", "-t", "-s", str(size), "-o", td, str(src)], check=True, capture_output=True)
        im = Image.open(Path(td) / "icon.svg.png").convert("RGBA"); im.load()
    return im if im.size == (size, size) else im.resize((size, size), Image.LANCZOS)


def render_alpha(svg_text: str, size: int) -> Image.Image:
    """QuickLook flattens transparency onto white, so render over black and over white and solve for alpha."""
    def with_ground(c): return svg_text.replace('<g clip-path="url(#square)">', f'<g clip-path="url(#square)"><rect width="1024" height="1024" fill="{c}"/>', 1)
    b = np.asarray(render(with_ground("#000000"), size)).astype(np.float32)[..., :3]
    w = np.asarray(render(with_ground("#FFFFFF"), size)).astype(np.float32)[..., :3]
    alpha = np.clip(1 - (w - b).mean(axis=2) / 255, 0, 1)
    rgb = np.where(alpha[..., None] > 0, b / np.maximum(alpha[..., None], 1e-4), 0)
    out = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    return Image.fromarray(out)


def layer(svg: str, keep: str, transform=None) -> str:
    """The master with only one top-level layer kept (ground-layer | mark-layer), optionally wrapped in a transform."""
    other = "mark-layer" if keep == "ground-layer" else "ground-layer"
    s = re.sub(rf'  <g id="{other}">.*?\n  </g>\n', "", svg, flags=re.S)
    if transform:
        s = s.replace(f'<g id="{keep}">', f'<g id="{keep}" transform="{transform}">')
    return s


def rounded(im: Image.Image, radius_frac: float) -> Image.Image:
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.width * radius_frac, fill=255)
    out = im.copy(); out.putalpha(mask); return out


def android_scale_transform():
    k = ANDROID_MARK_SCALE; off = 512 * (1 - k)
    return f"translate({off:.1f} {off:.1f}) scale({k})"


def monochrome_xml() -> str:
    """Vector themed-icon layer: the M stroke and the two sparkles in white, same geometry as the SVG."""
    k = 66 / 1024; off = (108 - 1024 * k) / 2
    inner = ANDROID_MARK_SCALE; ioff = 512 * (1 - inner)
    return f'''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
  <group android:scaleX="{k:.6f}" android:scaleY="{k:.6f}" android:translateX="{off:.4f}" android:translateY="{off:.4f}">
    <group android:scaleX="{inner}" android:scaleY="{inner}" android:translateX="{ioff:.1f}" android:translateY="{ioff:.1f}">
      <path android:strokeColor="#FFFFFFFF" android:strokeWidth="76" android:strokeLineJoin="round" android:strokeLineCap="round" android:pathData="M262,712 V330 L512,618 L762,330 V712"/>
      <path android:fillColor="#FFFFFFFF" android:pathData="M818,192 C826,236 842,252 886,260 C842,268 826,284 818,328 C810,284 794,268 750,260 C794,252 810,236 818,192 Z"/>
      <path android:fillColor="#FFFFFFFF" android:pathData="M300,236 C304,258 312,266 334,270 C312,274 304,282 300,304 C296,282 288,274 266,270 C288,266 296,258 300,236 Z"/>
    </group>
  </group>
</vector>
'''


def feature_graphic(icon: Image.Image):
    """Play Store feature graphic (1024×500): the icon tile on the left, wordmark and tagline in Inter."""
    W, H, ss = 1024, 500, 3
    im = Image.new("RGBA", (W * ss, H * ss), NAVY)
    d = ImageDraw.Draw(im)
    tile = rounded(icon.resize((300 * ss, 300 * ss), Image.LANCZOS), 0.22)
    im.alpha_composite(tile, (80 * ss, 100 * ss))
    light = ImageFont.truetype(str(FONT_LIGHT), 96 * ss); regular = ImageFont.truetype(str(FONT_REG), 30 * ss)
    d.text((440 * ss, 150 * ss), "Mehfil", font=light, fill="#FFFFFF", anchor="ls")
    d.text((440 * ss, 205 * ss), "Run the wedding season", font=regular, fill="#C9CBEA", anchor="ls")
    d.text((440 * ss, 248 * ss), "without the spreadsheet.", font=regular, fill="#C9CBEA", anchor="ls")
    d.rounded_rectangle((440 * ss, 290 * ss, 520 * ss, 298 * ss), radius=4 * ss, fill="#F4CD5A")
    im.convert("RGB").resize((W, H), Image.LANCZOS).save(OUT / "mehfil-feature-1024x500.png")


def main():
    svg = MASTER.read_text()
    icon = render(svg, 1024)
    (OUT / "mehfil-mark.svg").write_text(layer(svg, "mark-layer"))

    # store + consent screen (no alpha)
    icon.convert("RGB").save(OUT / "mehfil-icon-1024.png")
    icon.resize((512, 512), Image.LANCZOS).convert("RGB").save(OUT / "mehfil-icon-512.png")
    icon.resize((120, 120), Image.LANCZOS).convert("RGB").save(OUT / "mehfil-icon-120.png")
    feature_graphic(icon)

    # iOS
    icon.convert("RGB").save(ROOT / "ios/Mehfil/Assets.xcassets/AppIcon.appiconset/icon-1024.png")

    # Android adaptive layers: the 1024 art is the whole 108dp canvas; the mark is pre-scaled into the safe zone.
    res = ROOT / "android/app/src/main/res"
    bg = render(layer(svg, "ground-layer"), 1024)
    fg = render_alpha(layer(svg, "mark-layer", android_scale_transform()), 1024)
    for dpi, mult in DENSITIES.items():
        d = res / f"mipmap-{dpi}"; d.mkdir(exist_ok=True)
        px = int(108 * mult)
        bg.resize((px, px), Image.LANCZOS).convert("RGB").save(d / "ic_launcher_background.png")
        fg.resize((px, px), Image.LANCZOS).save(d / "ic_launcher_foreground.png")
        lp = int(48 * mult)   # legacy launcher bitmap: rounded square of the full icon
        rounded(icon, 0.2).resize((lp, lp), Image.LANCZOS).save(d / "ic_launcher.png")
    (res / "drawable").mkdir(exist_ok=True)
    (res / "drawable/ic_launcher_monochrome.xml").write_text(monochrome_xml())
    fgx = res / "drawable/ic_launcher_foreground.xml"
    if fgx.exists(): fgx.unlink()   # bitmap layers replace the old vector foreground
    print("wrote icon set")


if __name__ == "__main__":
    main()
