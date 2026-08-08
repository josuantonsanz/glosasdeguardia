"""Generates the favicon PNG/ICO raster assets from the same design as
templates/favicon.svg (paper rounded square, black serif G, orange underline).

Run once with:  uv run --with pillow make_favicon.py
Outputs templates/favicon-32.png, templates/favicon-180.png, templates/favicon.ico
"""
import os

from PIL import Image, ImageDraw, ImageFont

# Flexoki palette (kept in sync with templates/scss/_palette.scss / favicon.svg)
PAPER = "#FFFCF0"
INK = "#100F0F"
EDGE = "#E6E4D9"
ORANGE = "#CB6120"

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")


def serif_bold_font(size):
    for path in (
        "C:/Windows/Fonts/georgiab.ttf",                 # Windows: Georgia Bold
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",  # macOS
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    ):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_favicon(px):
    """Draws the favicon at a given pixel size (design coordinates in /64)."""
    img = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Paper rounded square with subtle edge
    radius = px * 13 / 64
    edge_w = max(1, round(px * 1.5 / 64))
    d.rounded_rectangle([0, 0, px - 1, px - 1], radius=radius, fill=PAPER,
                        outline=EDGE, width=edge_w)

    # Serif G (center of the glyph around 0.49 * px, as in the SVG)
    font = serif_bold_font(int(px * 42 / 64))
    d.text((px * 0.5, px * 0.49), "G", font=font, fill=INK, anchor="mm")

    # Orange annotation underline: quadratic bezier (matching SVG path)
    p0 = (px * 20 / 64, px * 52 / 64)
    c = (px * 32 / 64, px * 48 / 64)
    p1 = (px * 44 / 64, px * 52 / 64)
    pts = []
    for i in range(41):
        t = i / 40
        mt = 1 - t
        pts.append((mt * mt * p0[0] + 2 * mt * t * c[0] + t * t * p1[0],
                    mt * mt * p0[1] + 2 * mt * t * c[1] + t * t * p1[1]))
    d.line(pts, fill=ORANGE, width=max(2, round(px * 4 / 64)), joint="curve")

    return img


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    draw_favicon(32).save(os.path.join(OUT_DIR, "favicon-32.png"))
    draw_favicon(180).save(os.path.join(OUT_DIR, "favicon-180.png"))
    draw_favicon(32).save(
        os.path.join(OUT_DIR, "favicon.ico"),
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
    )
    print(f"Favicon assets written to {OUT_DIR}")


if __name__ == "__main__":
    main()
