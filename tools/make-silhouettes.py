"""
Generates the SVG silhouette layers in /assets/svg.

Every tile is seamless horizontally (it is used with background-repeat: repeat-x),
and its colours come from the same grade as the photos: crushed teal-black
silhouettes, sodium-orange and dawn-amber light sources.

Run once:  python3 tools/make-silhouettes.py
"""
import math
import os
import random

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "svg")
os.makedirs(OUT, exist_ok=True)

SODIUM = "#ff8b2b"
SODIUM_HOT = "#ffc27a"
AMBER = "#f0a35c"


def svg(name, w, h, body, defs=""):
    doc = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" preserveAspectRatio="none">'
        f"<defs>{defs}</defs>{body}</svg>"
    )
    with open(os.path.join(OUT, name), "w") as f:
        f.write(doc)
    print(f"{name:28s} {len(doc) // 1024:>4d} KB")


def r(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def glow(gid, color, core=0.9):
    return (
        f'<radialGradient id="{gid}">'
        f'<stop offset="0" stop-color="{color}" stop-opacity="{core}"/>'
        f'<stop offset=".18" stop-color="{color}" stop-opacity="{core * 0.45}"/>'
        f'<stop offset="1" stop-color="{color}" stop-opacity="0"/>'
        f"</radialGradient>"
    )


def periodic_noise(rng, w, octaves):
    """Sum of sines whose frequencies are whole multiples of the tile width -> seamless."""
    waves = [(rng.randint(lo, hi), rng.uniform(0, math.tau), amp) for lo, hi, amp in octaves]
    return lambda x: sum(a * math.sin(f * math.tau * x / w + p) for f, p, a in waves)


def ridge_path(fn, w, h, step=8):
    pts = " ".join(f"L{r(x)} {r(fn(x))}" for x in range(0, w + step, step))
    return f'<path d="M0 {h} {pts} L{w} {h} Z"/>'


# ---------------------------------------------------------------- scene 1: departure
def city_far():
    rng = random.Random(11)
    w, h = 2400, 520
    body, lit = [], []
    x = 0
    while x < w:
        bw = rng.randint(40, 130)
        bh = rng.randint(90, 330) if rng.random() > 0.12 else rng.randint(340, 470)
        bw = min(bw, w - x)
        y = h - bh
        body.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}"/>')
        if rng.random() < 0.25:
            ax = x + rng.randint(6, max(7, bw - 6))
            body.append(f'<rect x="{ax}" y="{y - rng.randint(20, 60)}" width="2" height="60"/>')
        for wy in range(y + 14, h - 10, 16):
            for wx in range(x + 6, x + bw - 8, 12):
                if rng.random() < 0.035:
                    lit.append(f'<rect x="{wx}" y="{wy}" width="5" height="7"/>')
        x += bw + rng.choice([0, 0, 0, 4, 10])
    svg(
        "s1-city.svg", w, h,
        f'<g fill="#0a161b">{"".join(body)}</g><g fill="{AMBER}" opacity=".55">{"".join(lit)}</g>',
    )


def catenary(name, w, h, color, mast_x=60, light=None):
    """Railway overhead-line mast with cantilever arm; wires run across the tile edges."""
    top, wire_y = 60, 150
    body = [
        f'<rect x="{mast_x - 9}" y="{top}" width="18" height="{h - top}"/>',
        f'<rect x="{mast_x - 15}" y="{h - 30}" width="30" height="30"/>',
        f'<path d="M{mast_x} {top + 30} L{mast_x + 260} {wire_y - 8} L{mast_x + 260} {wire_y - 2} L{mast_x} {top + 40} Z"/>',
        f'<path d="M{mast_x} {top + 70} L{mast_x + 250} {wire_y + 2} L{mast_x + 250} {wire_y + 6} L{mast_x} {top + 76} Z"/>',
        f'<rect x="{mast_x + 248}" y="{wire_y - 10}" width="4" height="22"/>',
    ]
    # messenger wire (sagging) + contact wire (straight), continuous across tiles
    body.append(
        f'<path d="M0 {wire_y - 34} Q{w / 2} {wire_y - 4} {w} {wire_y - 34}" fill="none" stroke="{color}" stroke-width="2.4"/>'
    )
    body.append(f'<rect x="0" y="{wire_y + 12}" width="{w}" height="2.4"/>')
    for dx in range(80, w, 140):
        sag = wire_y - 34 + 30 * (1 - ((dx - w / 2) / (w / 2)) ** 2)
        body.append(f'<rect x="{dx}" y="{r(sag)}" width="1.4" height="{r(wire_y + 12 - sag)}"/>')
    defs, extra = "", ""
    if light:
        defs = glow("g", light)
        extra = f'<circle cx="{mast_x + 22}" cy="{top + 110}" r="150" fill="url(#g)"/>'
    svg(name, w, h, f'{extra}<g fill="{color}">{"".join(body)}</g>', defs)


def platform(name, w, h, color, lamp_color, edge_color):
    """Platform slab + lamp posts with a warm pool of light."""
    body, glows = [], []
    slab = h - 90
    body.append(f'<rect x="0" y="{slab}" width="{w}" height="90"/>')
    lamps = [180, 180 + w // 2]
    for lx in lamps:
        body.append(f'<rect x="{lx - 5}" y="{slab - 520}" width="10" height="520"/>')
        body.append(f'<path d="M{lx - 5} {slab - 520} h70 v10 h-70 Z"/>')
        glows.append(f'<ellipse cx="{lx + 55}" cy="{slab - 505}" rx="230" ry="230" fill="url(#lamp)"/>')
        glows.append(f'<ellipse cx="{lx + 55}" cy="{slab + 4}" rx="260" ry="26" fill="url(#pool)"/>')
        glows.append(f'<rect x="{lx + 30}" y="{slab - 512}" width="46" height="5" fill="{SODIUM_HOT}"/>')
    bench = w // 4 + 120
    body.append(f'<rect x="{bench}" y="{slab - 46}" width="120" height="10"/><rect x="{bench + 8}" y="{slab - 36}" width="6" height="36"/><rect x="{bench + 106}" y="{slab - 36}" width="6" height="36"/>')
    edge = f'<rect x="0" y="{slab}" width="{w}" height="4" fill="{edge_color}" opacity=".7"/>'
    defs = glow("lamp", lamp_color) + glow("pool", lamp_color, 0.6)
    svg(name, w, h, f'<g fill="{color}">{"".join(body)}</g>{edge}{"".join(glows)}', defs)


# ---------------------------------------------------------------- scene 2: countryside
def hills_farms():
    rng = random.Random(21)
    w, h = 2800, 380
    n = periodic_noise(rng, w, [(1, 2, 26), (3, 5, 12), (9, 14, 4)])
    base = lambda x: 250 + n(x)
    body = [ridge_path(base, w, h)]
    lit = []
    for fx in (420, 1300, 2150):
        y = base(fx)
        body.append(f'<path d="M{fx} {r(y)} v-34 l30 -20 l30 20 v34 Z"/>')
        body.append(f'<rect x="{fx + 70}" y="{r(y - 24)}" width="70" height="24"/>')
        lit.append(f'<rect x="{fx + 12}" y="{r(y - 22)}" width="6" height="6"/>')
    for _ in range(26):
        tx = rng.randint(0, w - 40)
        s = rng.uniform(10, 24)
        body.append(f'<ellipse cx="{tx}" cy="{r(base(tx) - s * 0.8)}" rx="{r(s)}" ry="{r(s * 0.9)}"/>')
    svg(
        "s2-hills.svg", w, h,
        f'<g fill="#1a3640">{"".join(body)}</g><g fill="{AMBER}">{"".join(lit)}</g>',
    )


def treeline(name, seed, w, h, color, base_y, poplars=True):
    rng = random.Random(seed)
    n = periodic_noise(rng, w, [(1, 3, 18), (4, 8, 8)])
    body = [f'<rect x="0" y="{base_y}" width="{w}" height="{h - base_y}"/>']
    x = 0
    while x < w:
        top = base_y - 60 + n(x)
        if poplars and rng.random() < 0.22:
            ph = rng.uniform(150, 230)
            body.append(f'<ellipse cx="{r(x)}" cy="{r(base_y - ph / 2)}" rx="{r(rng.uniform(12, 18))}" ry="{r(ph / 2)}"/>')
        else:
            for _ in range(3):
                cr = rng.uniform(22, 48)
                cx = x + rng.uniform(-14, 14)
                cy = top + rng.uniform(-18, 30)
                # crowns cut by the tile edge are repeated on the other side -> seamless
                for shift in (0, -w) if cx > w - 60 else (0, w) if cx < 60 else (0,):
                    body.append(f'<circle cx="{r(cx + shift)}" cy="{r(cy)}" r="{r(cr)}"/>')
        x += rng.uniform(26, 52)
    svg(name, w, h, f'<g fill="{color}">{"".join(body)}</g>')


def power_poles():
    w, h = 1200, 900
    px = 200
    c = "#05090b"
    body = [
        f'<rect x="{px - 7}" y="140" width="14" height="{h - 140}"/>',
        f'<rect x="{px - 70}" y="180" width="140" height="10"/>',
        f'<rect x="{px - 50}" y="240" width="100" height="8"/>',
        f'<path d="M{px - 60} 190 L{px} 260 L{px + 4} 254 L{px - 54} 190 Z"/>',
    ]
    for ix in (px - 64, px - 20, px + 20, px + 64):
        body.append(f'<rect x="{ix - 3}" y="170" width="6" height="12"/>')
    wires = []
    for k, (y0, sag) in enumerate([(178, 70), (178, 74), (178, 72), (178, 70), (238, 60)]):
        offs = [-64, -20, 20, 64, 0][k]
        x0 = px + offs
        wires.append(f'<path d="M{x0 - w} {y0} Q{x0 - w / 2} {y0 + sag * 2} {x0} {y0} Q{x0 + w / 2} {y0 + sag * 2} {x0 + w} {y0}" />')
    svg(
        "s2-poles.svg", w, h,
        f'<g fill="{c}">{"".join(body)}</g><g fill="none" stroke="{c}" stroke-width="2">{"".join(wires)}</g>',
    )


def grass():
    rng = random.Random(5)
    w, h = 1600, 260
    n = periodic_noise(rng, w, [(2, 4, 14), (7, 12, 6)])
    blades = [ridge_path(lambda x: 150 + n(x), w, h)]
    for _ in range(320):
        x = rng.uniform(0, w)
        bh = rng.uniform(40, 130)
        lean = rng.uniform(-30, 30)
        y = 160 + n(x)
        blades.append(f'<path d="M{r(x - 4)} {r(y)} Q{r(x + lean / 2)} {r(y - bh / 2)} {r(x + lean)} {r(y - bh)} Q{r(x + lean / 2 + 2)} {r(y - bh / 2)} {r(x + 4)} {r(y)} Z"/>')
    fence = "".join(f'<rect x="{fx}" y="70" width="12" height="190"/>' for fx in range(100, w, 400))
    wire = '<rect x="0" y="96" width="1600" height="2"/><rect x="0" y="136" width="1600" height="2"/>'
    svg("s2-grass.svg", w, h, f'<g fill="#030506">{fence}{wire}{"".join(blades)}</g>')


# ---------------------------------------------------------------- scene 3: deep night
def industry_far():
    rng = random.Random(31)
    w, h = 2600, 560
    c = "#0c1a1f"
    body, lights = [], []
    x = 0
    while x < w - 160:
        kind = rng.choice(["stack", "tank", "hall", "hall", "gantry"])
        if kind == "stack":
            sh = rng.randint(300, 470)
            body.append(f'<path d="M{x} {h} L{x + 8} {h - sh} h22 L{x + 38} {h} Z"/>')
            lights.append((x + 19, h - sh + 6, "#ff3b2b"))
            x += 60
        elif kind == "tank":
            tw = rng.randint(90, 150)
            th = rng.randint(80, 140)
            body.append(f'<rect x="{x}" y="{h - th}" width="{tw}" height="{th}"/><ellipse cx="{x + tw / 2}" cy="{h - th}" rx="{tw / 2}" ry="14"/>')
            x += tw + 20
        elif kind == "gantry":
            gh = rng.randint(180, 260)
            body.append(f'<rect x="{x}" y="{h - gh}" width="8" height="{gh}"/><rect x="{x + 90}" y="{h - gh}" width="8" height="{gh}"/><rect x="{x}" y="{h - gh}" width="98" height="8"/>')
            for k in range(0, gh, 40):
                body.append(f'<path d="M{x} {h - gh + k} L{x + 98} {h - gh + k + 40} v3 L{x} {h - gh + k + 3} Z"/>')
            lights.append((x + 49, h - gh + 14, SODIUM))
            x += 120
        else:
            hw = rng.randint(140, 260)
            hh = rng.randint(70, 150)
            body.append(f'<rect x="{x}" y="{h - hh}" width="{hw}" height="{hh}"/>')
            for lx in range(x + 20, x + hw - 10, 46):
                if rng.random() < 0.5:
                    lights.append((lx, h - hh + 18, SODIUM))
            x += hw + rng.randint(0, 30)
    body.append(f'<rect x="0" y="{h - 40}" width="{w}" height="40"/>')
    body.append(f'<path d="M0 {h - 160} H{w} v10 H0 Z"/>')  # pipe bridge
    dots = "".join(
        f'<circle cx="{lx}" cy="{ly}" r="40" fill="url(#{"red" if col != SODIUM else "na"})"/><circle cx="{lx}" cy="{ly}" r="2.4" fill="{col}"/>'
        for lx, ly, col in lights
    )
    defs = glow("na", SODIUM, 0.7) + glow("red", "#ff3b2b", 0.6)
    svg("s3-industry.svg", w, h, f'<g fill="{c}">{"".join(body)}</g>{dots}', defs)


def sodium_yard():
    """Warehouse wall, fence and sodium-vapour lamps throwing orange cones."""
    w, h = 1800, 700
    c = "#070d10"
    body = [
        f'<rect x="0" y="{h - 210}" width="{w}" height="210"/>',
        f'<rect x="300" y="{h - 330}" width="620" height="120"/>',
        f'<rect x="1260" y="{h - 290}" width="420" height="80"/>',
    ]
    for fx in range(0, w, 60):
        body.append(f'<rect x="{fx}" y="{h - 260}" width="3" height="60"/>')
    body.append(f'<rect x="0" y="{h - 262}" width="{w}" height="3"/><rect x="0" y="{h - 232}" width="{w}" height="2"/>')
    glows = []
    for lx in (120, 1020):
        body.append(f'<rect x="{lx - 6}" y="120" width="12" height="{h - 120}"/>')
        body.append(f'<path d="M{lx} 120 q0 -20 40 -22 h50 v12 h-50 q-26 2 -28 10 Z"/>')
        glows.append(f'<path d="M{lx + 50} 112 L{lx - 170} {h - 210} L{lx + 330} {h - 210} Z" fill="url(#cone)"/>')
        glows.append(f'<circle cx="{lx + 66}" cy="112" r="210" fill="url(#na)"/>')
        glows.append(f'<rect x="{lx + 46}" y="108" width="40" height="5" fill="{SODIUM_HOT}"/>')
    defs = glow("na", SODIUM, 0.85) + (
        f'<linearGradient id="cone" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{SODIUM}" stop-opacity=".35"/>'
        f'<stop offset="1" stop-color="{SODIUM}" stop-opacity="0"/></linearGradient>'
    )
    cones = [g for g in glows if "cone" in g]
    lamps = [g for g in glows if "cone" not in g]
    svg("s3-yard.svg", w, h, f'{"".join(cones)}<g fill="{c}">{"".join(body)}</g>{"".join(lamps)}', defs)


# ---------------------------------------------------------------- scene 4: arrival
def berlin_blocks():
    rng = random.Random(41)
    w, h = 2600, 460
    body, lit = [], []
    x = 0
    while x < w:
        bw = rng.randint(120, 260)
        bh = rng.randint(120, 300)
        bw = min(bw, w - x)
        body.append(f'<rect x="{x}" y="{h - bh}" width="{bw}" height="{bh}"/>')
        for wy in range(h - bh + 14, h - 12, 18):
            for wx in range(x + 8, x + bw - 10, 14):
                if rng.random() < 0.04:
                    lit.append(f'<rect x="{wx}" y="{wy}" width="6" height="8"/>')
        x += bw + rng.randint(10, 70)
    svg(
        "s4-blocks.svg", w, h,
        f'<g fill="#2a2a30">{"".join(body)}</g><g fill="{AMBER}" opacity=".6">{"".join(lit)}</g>',
    )


def canopy():
    """Glass station roof: columns, a deep beam and a ribbed glass edge."""
    w, h = 1400, 900
    c = "#0b0d10"
    body = [f'<rect x="0" y="0" width="{w}" height="70"/>', f'<rect x="0" y="70" width="{w}" height="14" opacity=".8"/>']
    for rx in range(0, w, 50):
        body.append(f'<rect x="{rx}" y="0" width="4" height="96"/>')
    for cx in (200, 900):
        body.append(f'<rect x="{cx - 12}" y="84" width="24" height="{h - 84}"/>')
        body.append(f'<path d="M{cx - 12} 120 L{cx - 160} 84 h20 L{cx - 12} 108 Z"/><path d="M{cx + 12} 120 L{cx + 160} 84 h-20 L{cx + 12} 108 Z"/>')
    lights = "".join(f'<rect x="{lx}" y="86" width="90" height="4" fill="{AMBER}" opacity=".85"/>' for lx in (420, 560, 1120, 1260, 40))
    svg("s4-canopy.svg", w, h, f'<g fill="{c}">{"".join(body)}</g>{lights}')


if __name__ == "__main__":
    city_far()
    catenary("s1-catenary.svg", 1500, 900, "#081114")
    platform("s1-platform.svg", 1800, 820, "#040709", SODIUM, "#c9a24a")
    hills_farms()
    treeline("s2-trees.svg", 22, 2400, 420, "#0b1c22", 300)
    power_poles()
    grass()
    industry_far()
    sodium_yard()
    catenary("s3-catenary.svg", 1300, 900, "#030607", light=SODIUM)
    berlin_blocks()
    canopy()
    platform("s4-platform.svg", 1800, 820, "#08080a", AMBER, "#d9b25c")
