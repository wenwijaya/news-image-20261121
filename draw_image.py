#!/usr/bin/env python3
"""Draw the entry image for make.fun news-image-20261121.

A newspaper front page for Saturday 21 November 2026, drawn from scratch
with Pillow: masthead, one hero story, three story cards, an also-today
strip and a footer. Run once to (re)create entry.png in this directory:

    python3 draw_image.py

All facts were checked against news reports dated 21 November 2026 before
drawing. The image is 1024x1024, RGB, well under the 1 MiB limit.
"""

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (248, 243, 230)
INK = (18, 18, 18)
RED = (163, 30, 34)
DARKRED = (122, 20, 24)
GREY = (96, 96, 96)
LIGHTGREY = (210, 205, 190)
CARD = (255, 255, 255)
NAVY = (28, 48, 80)
TEAL = (18, 120, 110)
GREEN = (46, 125, 60)
ORANGE = (230, 110, 20)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_width, fill, spacing=4):
    """Draw wrapped text; returns the y just below the last line."""
    lines = wrap(draw, text, fnt, max_width)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def chart_panel(draw, x0, y0, x1, y1):
    """A plunging stock chart: grid, axes, red line falling to the right."""
    draw.rectangle([x0, y0, x1, y1], fill=(255, 255, 255), outline=INK, width=2)
    # grid
    for i in range(1, 4):
        gy = y0 + (y1 - y0) * i // 4
        draw.line([(x0 + 8, gy), (x1 - 8, gy)], fill=(225, 222, 210), width=1)
    for i in range(1, 5):
        gx = x0 + (x1 - x0) * i // 5
        draw.line([(gx, y0 + 8), (gx, y1 - 8)], fill=(225, 222, 210), width=1)
    # the fall: steady, then a cliff
    pts = [
        (x0 + 16, y0 + 42),
        (x0 + 70, y0 + 52),
        (x0 + 120, y0 + 48),
        (x0 + 170, y0 + 78),
        (x0 + 210, y0 + 74),
        (x0 + 250, y0 + 118),
        (x0 + 290, y0 + 172),
        (x0 + 330, y0 + 236),
    ]
    draw.line(pts, fill=RED, width=7, joint="curve")
    # arrowhead at the end
    ex, ey = pts[-1]
    draw.polygon([(ex, ey), (ex - 20, ey - 4), (ex - 6, ey - 20)], fill=RED)
    # labels
    lab = font(SANS_B, 30)
    draw.text((x0 + 14, y0 + 10), "NASDAQ -5.3%", font=lab, fill=RED)
    draw.text((x0 + 14, y1 - 44), "NVIDIA -14%", font=lab, fill=RED)


def burst(draw, cx, cy, r, fill):
    """A simple explosion star: alternating long/short spikes."""
    import math

    pts = []
    for i in range(24):
        ang = math.pi * i / 12
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def globe_icon(draw, x0, y0, x1, y1):
    """A small globe: blue disc, green land blobs, latitude lines."""
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = (y1 - y0) // 2 - 6
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(64, 130, 190))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=2)
    draw.ellipse([cx - r + 12, cy - r + 16, cx - 6, cy - 8], fill=GREEN)
    draw.ellipse([cx + 2, cy + 4, cx + r - 10, cy + r - 12], fill=GREEN)
    draw.ellipse([cx - r + 26, cy + r - 26, cx - 2, cy + r - 10], fill=GREEN)
    for dy in (-r // 2, 0, r // 2):
        draw.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(255, 255, 255))
        draw.line([(cx - r + 4, cy + dy), (cx + r - 4, cy + dy)],
                  fill=(255, 255, 255), width=1)


def hospital_icon(draw, x0, y0, x1, y1):
    """A red cross on white with a teal pulse line beneath it."""
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2 - 8
    s = 26
    draw.rectangle([cx - s // 2, cy - s, cx + s // 2, cy + s], fill=RED)
    draw.rectangle([cx - s, cy - s // 2, cx + s, cy + s // 2], fill=RED)
    pulse = [(x0 + 12, y1 - 22), (x0 + 70, y1 - 22), (x0 + 88, y1 - 38),
             (x0 + 106, y1 - 8), (x0 + 124, y1 - 22), (x1 - 12, y1 - 22)]
    draw.line(pulse, fill=TEAL, width=4, joint="curve")


def strike_icon(draw, x0, y0, x1, y1):
    """City silhouettes at dusk with an orange blast above them."""
    draw.rectangle([x0, y0, x1, y1], fill=(52, 58, 74))
    base = y1 - 8
    for bx, bw, bh in [(0, 46, 52), (52, 34, 74), (92, 52, 44),
                       (150, 30, 66), (186, 44, 38), (236, 40, 58)]:
        draw.rectangle([x0 + bx, base - bh, x0 + bx + bw, base], fill=(28, 30, 40))
    burst(draw, (x0 + x1) // 2, y0 + 34, 30, ORANGE)
    burst(draw, (x0 + x1) // 2, y0 + 34, 16, (255, 200, 60))
    draw.text((x0 + 10, y1 - 26), "KRYVYI RIH", font=font(SANS_B, 18),
              fill=(255, 255, 255))


def card(draw, x0, y0, w, h, icon, kicker, headline, body):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=CARD, outline=INK, width=2)
    icon(draw, x0 + 2, y0 + 2, x0 + w - 2, y0 + 112)
    draw.line([(x0 + 2, y0 + 112), (x0 + w - 2, y0 + 112)], fill=INK, width=2)
    tx = x0 + 14
    ty = y0 + 126
    draw.text((tx, ty), kicker, font=font(SANS_B, 19), fill=RED)
    ty += 28
    ty = draw_wrapped(draw, tx, ty, headline, font(SERIF_B, 27), w - 28, INK, 2)
    ty += 6
    draw_wrapped(draw, tx, ty, body, font(SANS, 20), w - 28, (40, 40, 40), 3)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # double outer rule
    d.rectangle([10, 10, W - 11, H - 11], outline=INK, width=3)
    d.rectangle([18, 18, W - 19, H - 19], outline=INK, width=1)

    # masthead
    title = "THE WORLD TODAY"
    tf = font(SERIF_B, 84)
    tw = d.textlength(title, font=tf)
    d.text(((W - tw) / 2, 34), title, font=tf, fill=INK)
    d.line([(28, 138), (W - 28, 138)], fill=INK, width=2)

    # date band
    d.rectangle([28, 150, W - 28, 198], fill=RED)
    date = "SATURDAY, 21 NOVEMBER 2026"
    df = font(SANS_B, 38)
    dw = d.textlength(date, font=df)
    d.text(((W - dw) / 2, 158), date, font=df, fill=(255, 255, 255))
    sub = "THE WORLD'S NEWS IN ONE PICTURE"
    sf = font(SANS, 19)
    sw = d.textlength(sub, font=sf)
    d.text(((W - sw) / 2, 206), sub, font=sf, fill=GREY)

    # hero panel
    d.rectangle([28, 238, W - 28, 540], fill=CARD, outline=INK, width=2)
    hx = 52
    hy = 258
    d.text((hx, hy), "MARKETS", font=font(SANS_B, 24), fill=RED)
    hy += 34
    hy = draw_wrapped(d, hx, hy, "MARKETS PLUNGE\nAS AI SELL-OFF\nDEEPENS",
                      font(SERIF_B, 47), 540, INK, 2)
    hy += 10
    draw_wrapped(d, hx, hy,
                 "Nasdaq falls 5.3% and Nvidia drops 14% in the worst "
                 "week for US tech stocks since Covid.",
                 font(SANS, 24), 540, (40, 40, 40), 4)
    chart_panel(d, 628, 258, 976, 520)

    # three story cards
    cy, ch, cw = 556, 296, 304
    card(d, 28, cy, cw, ch, strike_icon, "UKRAINE",
         "MISSILE HITS KRYVYI RIH",
         "Two killed and 42 hurt, four of them children, as Russia "
         "strikes the city.")
    card(d, 360, cy, cw, ch, hospital_icon, "BRAZIL",
         "BOLSONARO IN HOSPITAL",
         "Brazil's jailed former president rushed in with severe "
         "abdominal pain.")
    card(d, 692, cy, cw, ch, globe_icon, "CLIMATE",
         "COP31 IN FINAL STRETCH",
         "Climate talks in Turkey race for a deal on fossil fuels "
         "and finance.")

    # also-today strip
    d.rectangle([28, 868, W - 28, 958], fill=(255, 255, 255),
                outline=INK, width=2)
    d.text((48, 880), "ALSO TODAY", font=font(SANS_B, 22), fill=RED)
    draw_wrapped(d, 48, 910,
                 "Trump presses Nvidia to bring back Huang; SEC said to "
                 "be probing Nvidia's books.",
                 font(SANS, 21), 928, INK, 2)
    d.text((48, 936),
           "Akvan's rains lash India's east coast; India 159/1 in "
           "Wellington; Sensex up 898.",
           font=font(SANS, 21), fill=INK)

    # footer
    foot = "The world's news of Saturday 21 November 2026 · Drawn from reports of the day"
    ff = font(SANS, 17)
    fw = d.textlength(foot, font=ff)
    d.text(((W - fw) / 2, 968), foot, font=ff, fill=GREY)

    img.save(OUT, "PNG", optimize=True)
    data = open(OUT, "rb").read()
    print("wrote", OUT)
    print("bytes:", len(data), "sha256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
