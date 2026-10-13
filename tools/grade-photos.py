"""
Bakes the film grade into every photo, so the browser only has to draw pixels
(no CSS filters or blend modes while scrolling).

The grade: crushed blacks, teal pushed into the shadows, sodium orange into the
highlights, plus a per-scene split from top to bottom.

    python3 tools/grade-photos.py <folder with the original Unsplash JPGs>
"""
import os
import sys

from PIL import Image, ImageChops, ImageEnhance

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

#  source id      output name            width  bright contr  sat   split top   split bottom  tint (rgb, alpha)
PHOTOS = [
    ("GAlMu7FMdaw", "s1-city-dusk",        2000, .80, 1.18, .78, "#0d4652", "#b9521c", ((8, 40, 46), .28)),
    ("rMPhrNQWasM", "s2-fog-field",        2000, 1.05, 1.2, .65, "#10495a", "#1d3a48", ((40, 90, 120), .30)),
    ("nYogv37yUmE", "s3-sodium-station",   2000, .55, 1.35, 1.0, "#0b3a40", "#c4561a", ((6, 30, 34), .32)),
    ("KJYeTSawUdw", "s4-berlin-dawn",      2000, .90, 1.12, .82, "#3b5560", "#d9813a", ((40, 30, 24), .12)),
    # the horizontal reel at the end
    ("hXelAWDSQs0", "reel-power-lines",    1400, .85, 1.25, .7,  "#10495a", "#1d3a48", ((20, 60, 80), .25)),
    ("1uvJa08dNfQ", "reel-industry",       1400, .70, 1.3,  .85, "#0b3a40", "#c4561a", ((6, 30, 34), .25)),
    ("CZ_ha7B_Gl4", "reel-fog-station",    1400, .80, 1.25, .8,  "#2b4a55", "#b9714a", ((20, 40, 48), .2)),
    # own photographs, Berlin (portrait)
    ("IMG_9481",    "own-fernsehturm",     900,  .62, 1.3,  .6,  "#0d4652", "#3a2a22", ((20, 50, 60), .3)),
    ("IMG_9644",    "own-streetlamp",      900,  .85, 1.2,  .95, "#0b3a40", "#c4561a", ((6, 30, 34), .2)),
    ("IMG_9661",    "own-tower-dawn",      900,  .92, 1.15, .9,  "#3b5560", "#d9813a", ((40, 30, 24), .1)),
]


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def curve(shadow_lift, highlight_gain, crush=.06):
    """Per-channel tone curve: crush the toe, then tint shadows and highlights."""
    lut = []
    for v in range(256):
        x = max(0.0, (v / 255 - crush) / (1 - crush))
        x = x * x * (3 - 2 * x) * .35 + x * .65            # gentle S-curve
        shadow = (1 - x) ** 2                              # weight towards blacks
        light = x ** 2                                     # weight towards whites
        y = x + shadow_lift * shadow * x * 4 + highlight_gain * light * (1 - x) * 4
        lut.append(round(min(1, max(0, y)) * 255))
    return lut


def grade(im, bright, contrast, sat, top, bottom, tint):
    im = ImageEnhance.Brightness(im).enhance(bright)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = ImageEnhance.Color(im).enhance(sat)

    # teal shadows (R down, G/B up), orange highlights (R up, B down)
    r, g, b = im.split()
    r = r.point(curve(-.05, .10))
    g = g.point(curve(.03, .03))
    b = b.point(curve(.07, -.07))
    im = Image.merge("RGB", (r, g, b))

    # top-to-bottom split tone, blended soft-light like a grading layer
    split = Image.linear_gradient("L").resize(im.size)
    split_rgb = Image.composite(Image.new("RGB", im.size, hex_rgb(bottom)), Image.new("RGB", im.size, hex_rgb(top)), split)
    im = Image.blend(im, ImageChops.soft_light(im, split_rgb), .85)

    # overall tint, multiplied in
    color, alpha = tint
    im = Image.blend(im, ImageChops.multiply(im, Image.new("RGB", im.size, color)), alpha)
    return im


def save(im, name, limit=300_000):
    path = os.path.join(OUT, name + ".webp")
    for q in range(80, 30, -6):
        im.save(path, "WEBP", quality=q, alpha_quality=q // 2, method=6)
        if os.path.getsize(path) <= limit:
            break
    print(f"{name:22s} {im.size[0]}x{im.size[1]}  q{q}  {os.path.getsize(path) // 1024} KB")


for pid, name, width, *params in PHOTOS:
    im = Image.open(os.path.join(SRC, pid + ".jpg")).convert("RGB")
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    save(grade(im, *params), name, 300_000 if width > 1500 else 200_000)

# Rain on glass: the photo's brightness becomes transparency, so it needs no blend mode.
rain = Image.open(os.path.join(SRC, "1e60bqR1Ar0.jpg")).convert("L").resize((1200, 800), Image.LANCZOS)
alpha = rain.point(lambda v: max(0, min(255, (v - 28) * 2)))
tinted = Image.merge("RGBA", (*Image.new("RGB", rain.size, (255, 196, 140)).split(), alpha))
save(tinted, "fx-rain-glass", 200_000)
