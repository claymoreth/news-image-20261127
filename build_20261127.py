#!/usr/bin/env python3
"""Build the news-image-20261127 entry: one 1024x1024 page.

Friday 27 November 2026, Mana's 35 stories verbatim (7 regions x 5),
layout 100% like build_20261126.py: masthead, title, ticker,
7 region tabs, thick navy line, timeline, 3 heroes + 10 cards with
WIDE scenes (full card width) and stat banners OVERLAID on the bottom
of the scene (heroes: 2 stacked banners, stat1 region colour, stat2
navy; cards: 1 region-coloured banner), map + 13 pins, 22 briefs in
TWO columns (11 each, 2 lines each, spread evenly y685..y923),
DATE CHECK, HOW SURE, footer. OFFICIAL pill = bright light green
(144, 238, 144) + navy text; REPORTED = red + white. SE ASIA bar
red, stat panel orange. No repo, no push, no bundle, no kit check,
no submit: PREVIEW ONLY. Deterministic: no time, no randomness,
no network. PIL only.
"""
import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

W, H = 1024, 1024
CREAM = (247, 242, 234)
NAVY = (16, 28, 58)
RED = (207, 31, 38)
ORANGE = (222, 110, 24)
INK = (25, 25, 25)
GREY = (96, 96, 96)
GREEN = (46, 139, 87)
GOLD = (176, 132, 24)

FDIR = "/usr/share/fonts/truetype/liberation/"
SERIF_B = FDIR + "LiberationSerif-Bold.ttf"
SERIF_R = FDIR + "LiberationSerif-Regular.ttf"
SERIF_I = FDIR + "LiberationSerif-Italic.ttf"
SANS_B = FDIR + "LiberationSans-Bold.ttf"
SANS_R = FDIR + "LiberationSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, int(size))


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, path, size, max_w, max_lines, min_size=8):
    """Shrink font until text wraps to at most max_lines; return (font, lines)."""
    s = size
    while s > min_size:
        fnt = font(path, s)
        lines = wrap(draw, text, fnt, max_w)
        if len(lines) <= max_lines:
            return fnt, lines
        s -= 0.5
    fnt = font(path, min_size)
    return fnt, wrap(draw, text, fnt, max_w)[:max_lines]


def fit_single(draw, text, path, size, max_w, min_size=7):
    """Shrink font until text fits on one line; return font."""
    s = size
    while s > min_size:
        fnt = font(path, s)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt
        s -= 0.5
    return font(path, min_size)


def fit_head(draw, text, path, size, max_w, min_size=9):
    """Headline: prefer 2 lines (shrinking down to min_size); else 3 lines."""
    fnt, lines = fit_lines(draw, text, path, size, max_w, 2, min_size)
    if len(lines) <= 2:
        return fnt, lines
    return fit_lines(draw, text, path, size, max_w, 3, min_size)


def thumb_cover(fn, w, h):
    """Resize a thumb to cover a (w, h) box, center-cropped."""
    im = fn()
    scale = max(w / im.width, h / im.height)
    nw, nh = round(im.width * scale), round(im.height * scale)
    im = im.resize((nw, nh), Image.LANCZOS)
    x0 = (nw - w) // 2
    y0 = (nh - h) // 2
    return im.crop((x0, y0, x0 + w, y0 + h))


# Region colours. Region index: 0 N. AMERICA, 1 EUROPE, 2 MID EAST,
# 3 SE ASIA, 4 E & S ASIA, 5 AFRICA, 6 S. AMERICA & OCEANIA.
# SE ASIA bar is red; its stat panel is ORANGE, never red.
TAB_COLORS = [(110, 62, 150), (34, 120, 74), GOLD, RED, (36, 84, 160),
              NAVY, (20, 130, 138)]
REGION_COLORS = [(110, 62, 150), (34, 120, 74), GOLD, ORANGE,
                 (36, 84, 160), NAVY, (20, 130, 138)]


# ---------------------------------------------------------------- thumbnails
# Flat 2D stylised scenes drawn with PIL. Heroes drawn 648x200 (2x of
# 324x100), cards 384x90 (2x of 192x45). No text inside any scene.
def thumb_storm():
    im = Image.new("RGB", (648, 200), (58, 70, 92))
    d = ImageDraw.Draw(im)
    # storm clouds
    d.ellipse([-40, -30, 160, 50], fill=(40, 48, 66))
    d.ellipse([120, -40, 320, 40], fill=(48, 56, 76))
    d.ellipse([300, -30, 500, 50], fill=(40, 48, 66))
    d.ellipse([470, -40, 680, 40], fill=(48, 56, 76))
    # rain streaks
    for x in range(0, 648, 18):
        d.line([(x, 30), (x - 10, 70)], fill=(150, 165, 190), width=2)
        d.line([(x + 8, 90), (x - 2, 130)], fill=(150, 165, 190), width=2)
    # ground
    d.rectangle([0, 150, 648, 200], fill=(52, 58, 52))
    # fallen utility pole, leaning across the ground
    d.line([(90, 168), (300, 96)], fill=(70, 50, 30), width=10)
    d.line([(280, 92), (330, 78)], fill=(70, 50, 30), width=6)
    d.line([(300, 96), (320, 130)], fill=(70, 50, 30), width=5)
    # sagging power lines from the pole
    d.arc([300, 60, 560, 150], 200, 340, fill=(30, 30, 30), width=3)
    d.arc([120, 100, 420, 190], 180, 330, fill=(30, 30, 30), width=3)
    # parade balloon, deflated low on the ground, right side
    d.ellipse([420, 96, 560, 168], fill=(207, 31, 38))
    d.ellipse([470, 110, 540, 156], fill=(255, 255, 255))
    d.polygon([(470, 168), (500, 186), (530, 168)], fill=(120, 90, 40))
    d.line([(500, 186), (500, 196)], fill=(120, 90, 40), width=3)
    # puddle reflections
    d.ellipse([60, 176, 200, 190], fill=(90, 105, 130))
    d.ellipse([330, 180, 470, 192], fill=(90, 105, 130))
    return im


def thumb_kuwait():
    im = Image.new("RGB", (648, 200), (60, 40, 80))
    d = ImageDraw.Draw(im)
    # dusk sky bands
    d.rectangle([0, 0, 648, 70], fill=(90, 60, 100))
    d.rectangle([0, 70, 648, 120], fill=(200, 110, 60))
    d.rectangle([0, 120, 648, 150], fill=(240, 170, 90))
    # sun low on the horizon
    d.ellipse([280, 96, 360, 150], fill=(255, 210, 120))
    # skyline silhouette
    for x0, y0, x1 in [(0, 90, 70), (80, 70, 130), (140, 100, 200),
                       (210, 80, 260), (380, 95, 430), (440, 75, 500),
                       (510, 105, 570), (580, 85, 648)]:
        d.rectangle([x0, y0, x1, 200], fill=(35, 28, 45))
        for wy in range(y0 + 8, 190, 16):
            for wx in range(x0 + 8, x1 - 6, 16):
                d.rectangle([wx, wy, wx + 6, wy + 8], fill=(255, 210, 120))
    # tall tower with spire, centre
    d.rectangle([300, 50, 340, 200], fill=(35, 28, 45))
    d.polygon([(300, 50), (340, 50), (320, 18)], fill=(35, 28, 45))
    d.rectangle([316, 60, 324, 80], fill=(255, 210, 120))
    # explosion burst above the skyline, left of the tower
    d.polygon([(150, 10), (166, 34), (190, 26), (176, 46), (198, 54),
               (174, 62), (182, 82), (158, 68), (148, 88), (138, 66),
               (114, 74), (128, 54), (106, 46), (130, 38), (120, 18),
               (144, 28)], fill=(255, 140, 0))
    d.polygon([(148, 32), (158, 46), (172, 42), (162, 56), (150, 58),
               (144, 44)], fill=(255, 200, 0))
    # smoke
    d.ellipse([110, 0, 160, 22], fill=(120, 120, 125))
    d.ellipse([180, 2, 235, 26], fill=(140, 140, 145))
    # drone silhouette, top right
    d.ellipse([500, 22, 528, 36], fill=(20, 20, 20))
    d.line([(488, 18), (540, 18)], fill=(20, 20, 20), width=4)
    d.line([(488, 40), (540, 40)], fill=(20, 20, 20), width=4)
    d.line([(514, 36), (514, 46)], fill=(20, 20, 20), width=3)
    return im


def _eu_flag(d, x, y, w, h):
    """Small EU flag: blue field, circle of 12 gold stars."""
    d.rectangle([x, y, x + w, y + h], fill=(0, 51, 153))
    cx, cy = x + w / 2, y + h / 2
    r = min(w, h) * 0.32
    for k in range(12):
        ang = math.radians(k * 30 - 90)
        sx = cx + r * math.cos(ang)
        sy = cy + r * math.sin(ang)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 209, 0))


def thumb_eu():
    im = Image.new("RGB", (648, 200), (205, 215, 228))
    d = ImageDraw.Draw(im)
    # hall wall
    d.rectangle([0, 0, 648, 140], fill=(225, 225, 230))
    d.rectangle([0, 140, 648, 200], fill=(150, 120, 90))
    # three EU flags on poles
    for fx in (90, 300, 510):
        d.line([(fx, 20), (fx, 140)], fill=(90, 90, 90), width=4)
        _eu_flag(d, fx + 4, 24, 84, 56)
    # long summit table
    d.rectangle([60, 140, 588, 162], fill=(110, 75, 45))
    d.rectangle([60, 162, 588, 170], fill=(85, 58, 35))
    # chairs + microphones along the table
    for cx in (120, 220, 320, 420, 520):
        d.rectangle([cx - 22, 170, cx + 22, 200], fill=(40, 60, 100))
        d.line([(cx, 140), (cx, 122)], fill=(60, 60, 60), width=3)
        d.ellipse([cx - 5, 116, cx + 5, 126], fill=(30, 30, 30))
        d.rectangle([cx - 14, 146, cx + 14, 154], fill=(255, 255, 255))
    return im


def thumb_port():
    im = Image.new("RGB", (384, 90), (175, 205, 230))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 60, 384, 90], fill=(25, 75, 145))
    d.line([(0, 60), (384, 60)], fill=(255, 255, 255), width=2)
    # dock
    d.rectangle([0, 52, 384, 62], fill=(120, 120, 115))
    # gantry cranes
    for cx in (70, 300):
        d.line([(cx, 8), (cx, 52)], fill=(200, 60, 40), width=5)
        d.line([(cx - 30, 12), (cx + 46, 12)], fill=(200, 60, 40), width=4)
        d.line([(cx + 40, 12), (cx + 40, 34)], fill=(90, 90, 90), width=2)
        d.rectangle([cx + 32, 34, cx + 48, 44], fill=(40, 40, 40))
    # stacked containers
    cols = [(207, 31, 38), (36, 84, 160), (46, 139, 87), (222, 110, 24)]
    for i, (x0, y0) in enumerate([(150, 34), (190, 34), (230, 34),
                                  (170, 18), (210, 18)]):
        d.rectangle([x0, y0, x0 + 38, y0 + 16], fill=cols[i % 4],
                    outline=(255, 255, 255), width=1)
    # ship hull, right
    d.polygon([(320, 62), (384, 62), (372, 78), (332, 78)],
              fill=(30, 30, 30))
    d.rectangle([336, 44, 372, 62], fill=(240, 240, 240))
    return im


def thumb_nikkei():
    im = Image.new("RGB", (384, 90), (235, 238, 240))
    d = ImageDraw.Draw(im)
    # grid
    for gy in (20, 40, 60):
        d.line([(10, gy), (250, gy)], fill=(210, 215, 220), width=1)
    # rising chart line
    pts = [(20, 72), (60, 62), (100, 66), (140, 48), (180, 52),
           (220, 30), (252, 18)]
    d.line(pts, fill=(46, 139, 87), width=4)
    d.polygon([(252, 18), (238, 20), (250, 30)], fill=(46, 139, 87))
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(46, 139, 87))
    # Tokyo tower silhouette, right
    d.polygon([(300, 90), (318, 10), (336, 90)], fill=(200, 60, 40))
    d.polygon([(312, 40), (324, 40), (330, 90), (306, 90)],
              fill=(235, 238, 240))
    d.rectangle([314, 4, 322, 14], fill=(200, 60, 40))
    d.rectangle([296, 62, 340, 68], fill=(200, 60, 40))
    return im


def thumb_oil_gold():
    im = Image.new("RGB", (384, 90), (190, 215, 235))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 64, 384, 90], fill=(220, 190, 140))
    # sun
    d.ellipse([300, 6, 336, 42], fill=(255, 210, 120))
    # oil pumpjack silhouette, left
    d.polygon([(40, 64), (60, 20), (80, 64)], fill=(30, 30, 30))
    d.line([(60, 20), (130, 10)], fill=(30, 30, 30), width=5)
    d.line([(60, 20), (130, 34)], fill=(30, 30, 30), width=4)
    d.rectangle([124, 30, 140, 64], fill=(30, 30, 30))
    d.ellipse([56, 16, 66, 26], fill=(30, 30, 30))
    # gold bars, right foreground
    for bx, by in [(210, 66), (250, 66), (290, 66), (230, 52), (270, 52)]:
        d.polygon([(bx, by), (bx + 8, by - 10), (bx + 32, by - 10),
                   (bx + 40, by)], fill=(255, 209, 0))
        d.polygon([(bx, by), (bx + 8, by - 10), (bx + 32, by - 10),
                   (bx + 40, by)], outline=(180, 140, 0), width=1)
    return im


def thumb_crown_stage():
    im = Image.new("RGB", (384, 90), (60, 30, 90))
    d = ImageDraw.Draw(im)
    # stage curtains
    d.polygon([(0, 0), (70, 0), (50, 90), (0, 90)], fill=(150, 30, 40))
    d.polygon([(384, 0), (314, 0), (334, 90), (384, 90)],
              fill=(150, 30, 40))
    # spotlights
    d.polygon([(90, 0), (130, 0), (170, 90), (130, 90)],
              fill=(240, 230, 180))
    d.polygon([(294, 0), (254, 0), (214, 90), (254, 90)],
              fill=(240, 230, 180))
    d.rectangle([0, 74, 384, 90], fill=(40, 20, 60))
    # gold crown, centre
    d.polygon([(150, 66), (150, 30), (168, 48), (182, 20), (192, 46),
               (202, 20), (216, 48), (234, 30), (234, 66)],
              fill=(212, 175, 55))
    d.ellipse([188, 50, 196, 58], fill=(207, 31, 38))
    d.ellipse([168, 54, 174, 60], fill=(36, 84, 160))
    d.ellipse([210, 54, 216, 60], fill=(36, 84, 160))
    d.ellipse([179, 12, 185, 18], fill=(255, 255, 255))
    d.ellipse([199, 12, 205, 18], fill=(255, 255, 255))
    return im


def thumb_server():
    im = Image.new("RGB", (384, 90), (25, 28, 40))
    d = ImageDraw.Draw(im)
    # two server racks
    for rx in (30, 230):
        d.rectangle([rx, 8, rx + 110, 82], fill=(45, 48, 60),
                    outline=(120, 125, 140), width=1)
        for ry in range(14, 78, 12):
            d.rectangle([rx + 6, ry, rx + 104, ry + 7], fill=(60, 64, 78))
            for lx in range(rx + 10, rx + 100, 14):
                d.ellipse([lx, ry + 1, lx + 5, ry + 6],
                          fill=(80, 200, 120) if (lx // 14) % 3 else
                          (255, 200, 60))
    # chip, centre front
    d.rectangle([160, 28, 224, 62], fill=(40, 90, 180),
                outline=(120, 170, 230), width=2)
    d.rectangle([176, 38, 208, 52], fill=(20, 50, 110))
    for px in (172, 186, 200, 214):
        d.line([(px, 28), (px, 20)], fill=(180, 180, 180), width=2)
        d.line([(px, 62), (px, 70)], fill=(180, 180, 180), width=2)
    for py in (36, 46, 56):
        d.line([(160, py), (152, py)], fill=(180, 180, 180), width=2)
        d.line([(224, py), (232, py)], fill=(180, 180, 180), width=2)
    return im


def thumb_bank():
    im = Image.new("RGB", (384, 90), (190, 210, 225))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 76, 384, 90], fill=(140, 140, 135))
    # steps
    d.rectangle([90, 76, 294, 82], fill=(170, 170, 165))
    d.rectangle([100, 70, 284, 76], fill=(185, 185, 180))
    # columns
    for cx in (130, 170, 214, 254):
        d.rectangle([cx - 8, 30, cx + 8, 70], fill=(240, 240, 235),
                    outline=(200, 200, 195), width=1)
        d.rectangle([cx - 11, 26, cx + 11, 30], fill=(225, 225, 220))
        d.rectangle([cx - 11, 70, cx + 11, 74], fill=(225, 225, 220))
    # pediment
    d.polygon([(110, 28), (274, 28), (192, 6)], fill=(235, 235, 230))
    d.ellipse([184, 14, 200, 28], fill=(212, 175, 55))
    # door
    d.rectangle([180, 48, 204, 70], fill=(90, 70, 50))
    return im


def thumb_tanker_fire():
    im = Image.new("RGB", (384, 90), (225, 215, 195))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 66, 384, 90], fill=(90, 90, 90))
    d.line([(0, 76), (384, 76)], fill=(255, 255, 255), width=2)
    # tanker truck
    d.rounded_rectangle([60, 34, 250, 62], radius=12, fill=(200, 200, 200),
                        outline=(120, 120, 120), width=1)
    d.rectangle([250, 40, 300, 62], fill=(180, 60, 40))
    d.rectangle([262, 44, 286, 54], fill=(160, 200, 230))
    for wx in (90, 150, 210, 272):
        d.ellipse([wx - 10, 58, wx + 10, 78], fill=(25, 25, 25))
        d.ellipse([wx - 4, 64, wx + 4, 72], fill=(150, 150, 150))
    # flames over the tank
    d.polygon([(110, 34), (130, 6), (150, 34)], fill=(255, 140, 0))
    d.polygon([(150, 34), (172, 0), (194, 34)], fill=(255, 200, 0))
    d.polygon([(190, 34), (210, 10), (230, 34)], fill=(255, 140, 0))
    # smoke
    d.ellipse([120, 0, 160, 16], fill=(150, 150, 150))
    d.ellipse([180, 0, 220, 14], fill=(170, 170, 170))
    return im


def thumb_un():
    im = Image.new("RGB", (384, 90), (180, 205, 230))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 74, 384, 90], fill=(110, 140, 90))
    # UN slab tower
    d.rectangle([150, 10, 234, 74], fill=(200, 210, 220),
                outline=(150, 160, 170), width=1)
    for wy in range(16, 70, 10):
        d.line([(156, wy), (228, wy)], fill=(90, 130, 170), width=3)
    # low wing
    d.rectangle([234, 44, 300, 74], fill=(220, 225, 230),
                outline=(150, 160, 170), width=1)
    for wy in range(50, 70, 10):
        d.line([(240, wy), (294, wy)], fill=(90, 130, 170), width=3)
    # row of small houses, left
    for hx in (20, 60, 100):
        d.rectangle([hx, 52, hx + 32, 74], fill=(220, 180, 130))
        d.polygon([(hx - 4, 52), (hx + 16, 36), (hx + 36, 52)],
                  fill=(180, 80, 60))
        d.rectangle([hx + 12, 60, hx + 20, 74], fill=(90, 70, 50))
    # flag pole with blue flag
    d.line([(320, 10), (320, 74)], fill=(90, 90, 90), width=3)
    d.rectangle([320, 12, 352, 28], fill=(36, 84, 160))
    return im


def thumb_london():
    im = Image.new("RGB", (384, 90), (190, 205, 225))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 68, 384, 90], fill=(70, 110, 150))
    d.line([(0, 68), (384, 68)], fill=(255, 255, 255), width=2)
    # skyline
    for x0, y0, x1 in [(0, 44, 40), (48, 30, 90), (100, 48, 140),
                       (240, 40, 280), (288, 52, 330), (338, 44, 384)]:
        d.rectangle([x0, y0, x1, 68], fill=(70, 90, 120))
        for wy in range(y0 + 6, 64, 10):
            for wx in range(x0 + 6, x1 - 4, 12):
                d.rectangle([wx, wy, wx + 5, wy + 5],
                            fill=(255, 220, 120))
    # Big Ben
    d.rectangle([170, 8, 196, 68], fill=(180, 150, 100))
    d.polygon([(170, 8), (196, 8), (183, -2)], fill=(120, 100, 70))
    d.ellipse([174, 14, 192, 32], fill=(245, 245, 240),
              outline=(60, 60, 60), width=1)
    d.line([(183, 23), (183, 17)], fill=(25, 25, 25), width=2)
    d.line([(183, 23), (188, 25)], fill=(25, 25, 25), width=2)
    return im


def thumb_space_poetry():
    im = Image.new("RGB", (384, 90), (8, 14, 36))
    d = ImageDraw.Draw(im)
    for sx, sy in [(20, 12), (60, 40), (110, 16), (150, 50), (200, 14),
                   (260, 44), (320, 12), (360, 46), (40, 70), (300, 66),
                   (180, 74), (240, 24)]:
        d.ellipse([sx, sy, sx + 3, sy + 3], fill=(255, 255, 255))
    # crescent moon
    d.ellipse([330, 4, 372, 46], fill=(240, 230, 200))
    d.ellipse([342, 8, 378, 46], fill=(8, 14, 36))
    # space station module, left
    d.rectangle([30, 38, 120, 54], fill=(170, 170, 175))
    d.rectangle([10, 30, 30, 62], fill=(40, 90, 180))
    d.rectangle([120, 30, 140, 62], fill=(40, 90, 180))
    d.rectangle([70, 26, 82, 38], fill=(200, 200, 205))
    # floating astronaut, right of the station
    d.ellipse([180, 34, 200, 52], fill=(240, 240, 240))
    d.ellipse([184, 38, 196, 48], fill=(60, 140, 200))
    d.rectangle([178, 52, 202, 74], fill=(240, 240, 240))
    d.line([(178, 58), (164, 66)], fill=(240, 240, 240), width=5)
    d.line([(202, 58), (216, 50)], fill=(240, 240, 240), width=5)
    d.line([(184, 74), (180, 86)], fill=(240, 240, 240), width=5)
    d.line([(196, 74), (202, 86)], fill=(240, 240, 240), width=5)
    # tether back to the station
    d.line([(164, 66), (140, 56)], fill=(200, 200, 200), width=1)
    return im


# ---------------------------------------------------------------- map
AFRICA_POLY = [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31),
               (35, 28), (43, 12), (51, 11), (48, 0), (40, -10), (35, -20),
               (32, -28), (25, -34), (18, -35), (15, -27), (12, -18),
               (9, -1), (9, 4), (-8, 4), (-13, 8)]

CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 80), (-85, 70),
     (-75, 62), (-65, 60), (-55, 47), (-70, 42), (-75, 35), (-80, 25),
     (-85, 20), (-90, 15), (-95, 18), (-105, 20), (-110, 23), (-120, 32),
     (-125, 40), (-130, 55), (-150, 60)],
    [(-80, 10), (-75, 5), (-60, 0), (-50, 0), (-40, -5), (-35, -10),
     (-40, -20), (-48, -28), (-55, -35), (-65, -40), (-70, -50),
     (-73, -40), (-72, -20), (-78, -5)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 70), (40, 68),
     (45, 60), (40, 50), (35, 45), (30, 42), (28, 40), (23, 36),
     (19, 40), (15, 38), (12, 44), (8, 44), (3, 43), (-2, 37)],
    AFRICA_POLY,
    [(30, 70), (40, 68), (55, 70), (70, 72), (90, 75), (110, 74),
     (130, 72), (150, 70), (170, 66), (178, 65), (162, 60), (158, 52),
     (142, 50), (140, 40), (135, 35), (127, 33), (122, 38), (120, 30),
     (110, 20), (105, 10), (100, 8), (95, 15), (90, 22), (85, 20),
     (80, 8), (77, 8), (72, 20), (66, 25), (60, 25), (55, 28),
     (50, 30), (48, 30), (43, 35), (36, 36), (30, 42)],
    [(95, 5), (105, 0), (110, -5), (115, -8), (120, -10), (130, -5),
     (135, 0), (140, -5), (140, 2), (130, 5), (120, 8), (105, 10)],
    [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32),
     (137, -35), (140, -38), (145, -38), (150, -37), (153, -27),
     (150, -22), (146, -19), (142, -11), (136, -12), (132, -11),
     (126, -14), (122, -17), (118, -20)],
    [(167, -45), (170, -42), (174, -39), (178, -38), (175, -41),
     (172, -43), (168, -47)],
]

# ---------------------------------------------------------------- content
# Mana's 35 stories of Friday 27 November 2026, facts unchanged.
# Region index: 0 N. AMERICA, 1 EUROPE, 2 MID EAST, 3 SE ASIA,
# 4 E & S ASIA, 5 AFRICA, 6 S. AMERICA & OCEANIA.
TICKER = ("STORM: 400,000 lose power, parade delayed \u00b7 KUWAIT: "
          "drone strike kills two \u00b7 EU: \u20ac1.78 trillion budget "
          "deadlock")

TIMELINE_ITEMS = ["18% max tariff", "Nikkei 57,499", "Brent $94.83",
                  "Gold $3,598", "400,000 powerless",
                  "77,000 UK migration"]

TABS = ["N. AMERICA 5", "EUROPE 5", "MID EAST 5", "SE ASIA 5",
        "E & S ASIA 5", "AFRICA 5", "S. AMERICA & OCEANIA 5"]

HEROES = [
    dict(num=1, bar="EAST COAST, USA - STORM", region=0, pill="REPORTED",
         stat1="400,000+ WITHOUT POWER", stat2="MACY'S PARADE DELAYED",
         source="Reuters \u00b7 AP \u00b7 AFP",
         head="Storm knocks out power for 400,000 and delays Macy's parade",
         deck=("A powerful storm batters the US East Coast, cutting power "
               "to more than 400,000 people, cancelling hundreds of "
               "flights and delaying the 100th Macy's Thanksgiving Day "
               "Parade for the first time ever."),
         thumb=thumb_storm),
    dict(num=2, bar="KUWAIT - DRONE STRIKE", region=2, pill="REPORTED",
         stat1="2 KILLED", stat2="GULF TENSIONS RISE",
         source="Reuters \u00b7 AP \u00b7 AFP",
         head="Drone strike in Kuwait kills two as Gulf tensions rise",
         deck=("A drone attack in Kuwait kills two people, while Iran's "
               "foreign minister calls the incident suspicious and offers "
               "help with the investigation."),
         thumb=thumb_kuwait),
    dict(num=3, bar="BRUSSELS - EU BUDGET", region=1, pill="OFFICIAL",
         stat1="\u20ac1.78 TRILLION", stat2="NO DEAL",
         source="Reuters \u00b7 AP \u00b7 AFP",
         head="EU leaders deadlock over \u20ac1.78 trillion seven-year budget",
         deck=("EU leaders end their summit without agreement on the "
               "seven-year budget after sharp differences between France "
               "and Germany, delaying a \u20ac45 billion loan for Ukraine."),
         thumb=thumb_eu),
]

CARDS = [
    dict(num=4, bar="WASHINGTON - US TARIFFS", region=3, pill="REPORTED",
         stat="18% MAX", source="Reuters \u00b7 AP \u00b7 AFP",
         head="US proposes tariffs up to 18% on Indonesian goods",
         deck=("The Trump administration proposes new import tariffs on 14 "
               "major trading partners, with Indonesian products facing "
               "up to 18 percent."),
         thumb=thumb_port),
    dict(num=5, bar="TOKYO - NIKKEI", region=4, pill="OFFICIAL",
         stat="57,499 +0.86%", source="Reuters \u00b7 AP \u00b7 AFP",
         head="Nikkei climbs 0.86% to 57,499 ahead of inflation data",
         deck=("Japan's Nikkei 225 rises ahead of the release of core "
               "inflation data and China's industrial profit figures."),
         thumb=thumb_nikkei),
    dict(num=6, bar="GLOBAL MARKETS - OIL & GOLD", region=0,
         pill="OFFICIAL", stat="$94.83 / $3,598",
         source="Reuters \u00b7 AP \u00b7 AFP",
         head="Brent crude climbs to $94.83 as gold hits $3,598",
         deck=("Brent crude rises on Middle East tensions while gold "
               "strengthens to US$3,598 an ounce."),
         thumb=thumb_oil_gold),
    dict(num=7, bar="SAN JUAN - MISS UNIVERSE", region=6, pill="OFFICIAL",
         stat="MISS UNIVERSE", source="Reuters \u00b7 AP \u00b7 AFP",
         head="Jennifer Barreto wins Miss Universe 2026",
         deck=("Jennifer Barreto of Puerto Rico is crowned Miss Universe "
               "2026, the first mother and wife to win the pageant."),
         thumb=thumb_crown_stage),
    dict(num=8, bar="SOUTHEAST ASIA - NVIDIA", region=3, pill="REPORTED",
         stat="SHIPPING HALT", source="Reuters \u00b7 AP \u00b7 AFP",
         head="Nvidia halts AI server shipments to Southeast Asia",
         deck=("Nvidia stops shipping AI servers to several Southeast "
               "Asian countries including Indonesia, sending regional "
               "telecom shares sharply lower."),
         thumb=thumb_server),
    dict(num=9, bar="BUENOS AIRES - ARGENTINA", region=6, pill="OFFICIAL",
         stat="PRINTING BANNED", source="Reuters \u00b7 AP \u00b7 AFP",
         head="Argentina bans central bank from printing money",
         deck=("Argentina's government bans the central bank from printing "
               "money to finance the budget deficit."),
         thumb=thumb_bank),
    dict(num=10, bar="CAIRO - FIRE", region=5, pill="REPORTED",
         stat="31 KILLED", source="Reuters \u00b7 AP \u00b7 AFP",
         head="Cairo fuel tanker fire kills 31, driver detained",
         deck=("Egyptian police detain a fuel tanker driver after a deadly "
               "fire in Cairo kills 31 people."),
         thumb=thumb_tanker_fire),
    dict(num=11, bar="NAIROBI - HOUSING", region=5, pill="OFFICIAL",
         stat="UN SUMMIT", source="Reuters \u00b7 AP \u00b7 AFP",
         head="UN global housing conference opens in Nairobi",
         deck=("Government officials and housing experts gather at the UN "
               "headquarters in Nairobi to tackle the global housing "
               "crisis."),
         thumb=thumb_un),
    dict(num=12, bar="LONDON - MIGRATION", region=1, pill="OFFICIAL",
         stat="77,000", source="Reuters \u00b7 AP \u00b7 AFP",
         head="UK net migration falls to 77,000, lowest since 1997",
         deck=("Net migration to Britain falls to 77,000, its lowest level "
               "since 1997 outside the pandemic years."),
         thumb=thumb_london),
    dict(num=13, bar="CHINA SPACE STATION - POETRY", region=4,
         pill="REPORTED", stat="IQBAL IN ORBIT",
         source="Reuters \u00b7 AP \u00b7 AFP",
         head="Pakistan's first astronaut reads Iqbal poem in space",
         deck=("Pakistan's first astronaut captures attention by reciting "
               "a poem by Muhammad Iqbal aboard China's space station."),
         thumb=thumb_space_poetry),
]

# (story num, lon, lat, dx, dy) — pins for the 13 featured stories.
# Offsets separate the tight US east-coast / Europe clusters.
PINS = [(1, -74.0, 40.7, 12, -12), (2, 47.5, 29.4, 0, 0),
        (3, 4.35, 50.85, -14, -12), (4, -77.0, 38.9, -14, 12),
        (5, 139.7, 35.7, 0, 0), (6, 2.0, 57.0, 12, -12),
        (7, -66.1, 18.5, 8, 12), (8, 106.8, -6.2, 0, 12),
        (9, -58.4, -34.6, 0, 0), (10, 31.2, 30.0, 0, 0),
        (11, 36.8, -1.3, 0, 0), (12, -0.1, 51.5, 10, 12),
        (13, 98.5, 39.8, 0, -10)]

# (display num 1-35, "Lead: rest", region index, wire source).
# Two lines each, two columns (nums 14-24 left, nums 25-35 right),
# 11 briefs per column, spread evenly y685..y923. No CLAIM tags.
BRIEFS = [
    (14, "Jakarta: President Prabowo to address Bank Indonesia annual meeting on global market turmoil", 3, "Reuters"),
    (15, "Jakarta: over 15,100 Indonesians caught in online scams in 2026, 97.7% in Southeast Asia", 3, "AP"),
    (16, "Jakarta: parliament agrees first draft of Strategic Commodities Bill on downstreaming", 3, "AFP"),
    (17, "Pyongyang: Kim Jong Un vows wider diplomacy after declining Trump's meeting offer", 4, "Reuters"),
    (18, "Asia: Nvidia falls 3.9% as AI spending fears weigh on tech shares", 4, "AP"),
    (19, "Beijing: markets await China's October industrial profit data today", 4, "AFP"),
    (20, "Riyadh: Houthis strike financial district tower and Jazan refinery, one killed", 2, "Reuters"),
    (21, "Tehran: US blockade and subsidy cuts squeeze Iranians as fuel and food prices bite", 2, "AP"),
    (22, "Gaza: winter rain displaces Palestinians again as meningitis cases surge", 2, "AFP"),
    (23, "Dubai: Indonesian facility services firms join Big 5 Global to expand Gulf exports", 2, "Reuters"),
    (24, "Kyiv: Ukraine tells Libya Russian ships hit off Benghazi were military targets only", 1, "AP"),
    (25, "Ibiza: Spain races to contain fuel spill after ship capsizes off the island", 1, "AFP"),
    (26, "Europe: NBA commits \u20ac10 billion to new arenas ahead of NBA Europe launch in 2027", 1, "Reuters"),
    (27, "Florida: Trump uses Thanksgiving post to attack rivals and accuse agencies of faking data", 0, "AP"),
    (28, "San Francisco: king tide floods coastal areas as extreme tides hit California", 0, "Reuters"),
    (29, "Ottawa: Canada's top court tests Quebec ban on religious symbols for public workers", 0, "AFP"),
    (30, "Latin America: Brazil mid-month inflation 4.62% as Mexico jobless rate holds at 2.8%", 6, "Reuters"),
    (31, "Bogota: teenager's death in security operation fuels debate on Colombia crackdown", 6, "AP"),
    (32, "Mexico: magnitude 5.7 quake strikes off Revillagigedo Islands at 10 km depth", 6, "AFP"),
    (33, "Bamako: Barrick CEO meets Mali PM for first time since gold mine tax dispute settled", 5, "Reuters"),
    (34, "Wellington: New Zealand counts final 400,000 special votes to decide parliament", 5, "AP"),
    (35, "Sydney: safety probe after Qantas and Air New Zealand incident at airport", 5, "AFP"),
]

LEGEND = [("N. AMERICA", 0, 5), ("EUROPE", 1, 5), ("MID EAST", 2, 5),
          ("SE ASIA", 3, 5), ("E & S ASIA", 4, 5), ("AFRICA", 5, 5),
          ("S. AMERICA & OCEANIA", 6, 5)]

MAP_CAPTION = ("Pins locate the 13 illustrated lead & feature stories; "
               "all 35 items color-coded across 7 regions below.")

HOW_SURE = ("HOW SURE: CONFIRMED = 2+ outlets \u00b7 OFFICIAL = on record "
            "\u00b7 REPORTED = single wire/local \u00b7 CLAIM = one side's "
            "account \u00b7 Drawn scenes")

DATE_CHECK = ("Friday 27 November 2026 \u2014 a storm knocks out power "
              "for more than 400,000 and delays the Macy's Thanksgiving "
              "Day Parade for the first time ever, a drone strike in "
              "Kuwait kills two, EU leaders deadlock over a \u20ac1.78 "
              "trillion budget, Washington proposes tariffs of up to 18% "
              "on 14 partners, and Brent crude climbs to $94.83 a barrel.")


# ---------------------------------------------------------------- layout helpers
def _pill_colors(status):
    """(fill, text, outline) for a status pill, hero and card alike.

    OFFICIAL = bright light green (144, 238, 144) + navy text.
    """
    if status == "OFFICIAL":
        return ((144, 238, 144), NAVY, NAVY)
    if status == "REPORTED":
        return (RED, "white", None)
    return (NAVY, "white", None)


def _draw_pill(d, x, y, status, height=11, font_size=8):
    """Draw a status pill at (x, y); returns its width."""
    pf = font(SANS_B, font_size)
    pw = d.textlength(status, font=pf) + 12
    fill, tfill, outline = _pill_colors(status)
    d.rounded_rectangle([x, y, x + pw, y + height], radius=height // 2,
                        fill=fill, outline=outline, width=1)
    d.text((x + 6, y + 1), status, font=pf, fill=tfill)
    return pw


def _top_bar(d, x, y, w, h, color, num, text, pill, text_size=11,
             light=False):
    """Top bar: circle + number, bar text, status pill at the right.

    light=True (heroes): white bar with a thin light-grey outline, navy
    text, navy circle with a white number. Otherwise the bar keeps its
    region colour, white text and a white circle with a navy number.
    pill=None draws no pill and lets the text use the full bar width.
    """
    if light:
        d.rectangle([x, y, x + w, y + h], fill="white",
                    outline=(205, 205, 205), width=1)
    else:
        d.rectangle([x, y, x + w, y + h], fill=color)
    r = (h - 4) // 2
    d.ellipse([x + 4, y + 2, x + 4 + 2 * r, y + 2 + 2 * r],
              fill=NAVY if light else "white")
    nf = font(SANS_B, 8 if h >= 16 else 7)
    ns = str(num)
    d.text((x + 4 + r - d.textlength(ns, font=nf) / 2,
            y + 2 + r - 5), ns, font=nf,
           fill="white" if light else NAVY)
    text_right = x + w - 4
    if pill is not None:
        pf = font(SANS_B, 8)
        pw = d.textlength(pill, font=pf) + 12
        px = x + w - pw - 4
        _draw_pill(d, px, y + 2, pill, height=h - 4, font_size=8)
        text_right = px - 6
    tf = fit_single(d, text, SANS_B, text_size,
                    text_right - (x + 4 + 2 * r + 4), min_size=6.5)
    d.text((x + 4 + 2 * r + 4, y + 2), text, font=tf,
           fill=NAVY if light else "white")


def _deck(d, x, text, width, head_lines, y_top, y_bottom, size=11,
          lh=12):
    """Deck text between y_top and y_bottom; returns end y.

    3 lines when the headline took 2, else 2 — clipped by the space left
    before the source line.
    """
    max_dl = 3 if head_lines <= 2 else 2
    room = max(1, int((y_bottom - y_top) // lh))
    max_dl = min(max_dl, room)
    df, dlines = fit_lines(d, text, SANS_R, size, width, max_dl, min_size=8)
    y = y_top
    for ln in dlines:
        d.text((x, y), ln, font=df, fill=INK)
        y += lh
    return y, len(dlines), len(wrap(d, text, df, width))


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    problems = []

    # ---- masthead on cream paper
    f = font(SERIF_B, 14)
    d.text((14, 6), "THE WORLD IN ONE DAY", font=f, fill=RED)
    f2 = font(SANS_B, 9)
    right = ("35 DATED STORIES \u00b7 7 REGIONS \u00b7 "
             "ALL FROM FRI 27 NOV 2026")
    d.text((W - 14 - d.textlength(right, font=f2), 8), right, font=f2,
           fill=NAVY)

    # ---- date masthead, 58 pt
    t = "Friday 27 November 2026"
    f = fit_single(d, t, SERIF_B, 58, W - 28)
    d.text(((W - d.textlength(t, font=f)) / 2, 20), t, font=f, fill=NAVY)

    # ---- ticker: 3 hero headlines, red italic, one line
    tf = fit_single(d, TICKER, SERIF_I, 15, W - 28)
    d.text(((W - d.textlength(TICKER, font=tf)) / 2, 81), TICKER,
           font=tf, fill=RED)

    # ---- region tabs
    tw = 996 / 7
    for i, tab in enumerate(TABS):
        x0 = 14 + tw * i
        d.rectangle([x0, 98, x0 + tw - 2, 114], fill=TAB_COLORS[i])
        f = fit_single(d, tab, SANS_B, 10, tw - 6, min_size=7)
        d.text((x0 + (tw - 2) / 2 - d.textlength(tab, font=f) / 2, 101),
               tab, font=f, fill="white")

    # ---- thick navy line, 2 px, x14-1010
    d.rectangle([14, 116, 1010, 117], fill=(20, 26, 32))

    # ---- timeline: red FRIDAY box + 6 key numbers, spread even
    d.rectangle([14, 120, 124, 136], fill=RED)
    wf = font(SANS_B, 10)
    wt = "FRIDAY"
    d.text((14 + (110 - d.textlength(wt, font=wf)) / 2, 122), wt,
           font=wf, fill="white")
    tx0, tx1 = 130, 1010
    ts = 11.5
    while ts >= 10.5:
        tf = font(SANS_B, ts)
        widths = [d.textlength(it, font=tf) for it in TIMELINE_ITEMS]
        gap = ((tx1 - 8) - (tx0 + 8) - sum(widths)) / (len(TIMELINE_ITEMS) - 1)
        if gap >= 20:
            break
        ts -= 0.5
    tf = font(SANS_B, ts)
    widths = [d.textlength(it, font=tf) for it in TIMELINE_ITEMS]
    gap = ((tx1 - 8) - (tx0 + 8) - sum(widths)) / (len(TIMELINE_ITEMS) - 1)
    if gap < 20:
        problems.append(f"timeline gap {gap:.1f}px at {ts}pt (items tight)")
    cx = tx0 + 8
    for i, it in enumerate(TIMELINE_ITEMS):
        d.text((cx, 122), it, font=tf, fill=INK)
        cx += widths[i]
        if i < len(TIMELINE_ITEMS) - 1:
            d.line([cx + gap / 2, 122, cx + gap / 2, 134],
                   fill=(150, 150, 150), width=1)
            cx += gap

    # ---- heroes: white bar + pill, 100 px visual slot (y156..256),
    # WIDE scene (324 px, full card width) with TWO stacked stat
    # banners OVERLAID on the bottom of the scene: stat1 y216..236 in
    # the hero's region colour, stat2 y236..256 navy, white bold text
    # centred. NO side panel, NO text beside the scene. Headline,
    # deck, source below.
    hx = [14, 350, 686]
    HW = 324
    for col, h in enumerate(HEROES):
        x = hx[col]
        _top_bar(d, x, 140, HW, 16, RED, h["num"], h["bar"], h["pill"],
                 text_size=11, light=True)
        img.paste(thumb_cover(h["thumb"], HW, 100), (x, 156))
        d.rectangle([x, 216, x + HW, 236],
                    fill=REGION_COLORS[h["region"]])
        f1 = fit_single(d, h["stat1"], SANS_B, 12, HW - 12, min_size=8)
        d.text((x + HW / 2, 226), h["stat1"], font=f1,
               fill="white", anchor="mm")
        d.rectangle([x, 236, x + HW, 256], fill=NAVY)
        f2 = fit_single(d, h["stat2"], SANS_B, 10, HW - 12, min_size=8)
        d.text((x + HW / 2, 246), h["stat2"], font=f2,
               fill="white", anchor="mm")
        hf, lines = fit_head(d, h["head"], SERIF_B, 19, HW - 12)
        y = 260
        for ln in lines:
            d.text((x + 6, y), ln, font=hf, fill=INK)
            y += int(hf.size * 1.08)
        end, n_drawn, n_full = _deck(d, x + 6, h["deck"], HW - 12,
                                     len(lines), y + 2, 340)
        if n_drawn < n_full:
            problems.append(
                f"hero {h['num']} deck truncated: {n_drawn}/{n_full} lines")
        assert end <= 340, (h["bar"], end)
        sf = font(SANS_R, 9)
        d.text((x + 6, 342), h["source"], font=sf, fill=GREY)
        d.rectangle([x - 1, 139, x + HW + 1, 356],
                    outline=(130, 130, 130), width=1)

    # ---- small cards, two rows of five (145 px tall): region-coloured
    # bar, WIDE scene (192 px, full card width, 45 px tall) with ONE
    # region-coloured stat banner OVERLAID on the bottom of the scene
    # (y0+45..y0+60, ~15 px, white bold text centred). Region 3
    # (SE ASIA) uses ORANGE, never red. NO side panel, NO text beside
    # the scene. Headline, 3-line deck room, wire source at the bottom
    # right, status pill at the bottom left.
    rows_y = [360, 510]
    CARD_H = 145
    CW2 = 192
    for ri, y0 in enumerate(rows_y):
        for ci in range(5):
            c = CARDS[ri * 5 + ci]
            x = 14 + ci * 201
            _top_bar(d, x, y0, CW2, 15, TAB_COLORS[c["region"]], c["num"],
                     c["bar"], None, text_size=8.5)
            img.paste(thumb_cover(c["thumb"], CW2, 45), (x, y0 + 15))
            pcol = REGION_COLORS[c["region"]]
            d.rectangle([x, y0 + 45, x + CW2, y0 + 60], fill=pcol)
            f1 = fit_single(d, c["stat"], SANS_B, 11, CW2 - 12,
                            min_size=7)
            d.text((x + CW2 / 2, y0 + 15 + 37), c["stat"],
                   font=f1, fill="white", anchor="mm")
            hf, lines = fit_head(d, c["head"], SERIF_B, 13, CW2 - 12)
            y = y0 + 64
            for ln in lines:
                d.text((x + 6, y), ln, font=hf, fill=INK)
                y += 15
            src_y = y0 + CARD_H - 16
            end, n_drawn, n_full = _deck(d, x + 6, c["deck"], CW2 - 12,
                                         len(lines), y, src_y - 2,
                                         size=9.5, lh=11)
            if n_drawn < n_full:
                problems.append(
                    f"card {c['num']} deck truncated: "
                    f"{n_drawn}/{n_full} lines")
            if len(lines) > 2:
                problems.append(f"card {c['num']} head took "
                                f"{len(lines)} lines")
            assert end <= src_y, (c["bar"], end - y0)
            sf = font(SANS_R, 8.5)
            src = c["source"]
            d.text((x + CW2 - 6 - d.textlength(src, font=sf), src_y),
                   src, font=sf, fill=GREY)
            _draw_pill(d, x + 6, src_y, c["pill"], height=11,
                       font_size=8)
            d.rectangle([x - 1, y0 - 1, x + CW2 + 1, y0 + CARD_H],
                        outline=(130, 130, 130), width=1)

    # ---- bottom: solid-land map + briefs (two columns, 22 briefs, 2 lines each)
    d.text((14, 665), "WHERE IT HAPPENED \u00b7 13 PINS",
           font=font(SANS_B, 11), fill=INK)
    bh = ("ALSO ON FRIDAY 27 NOVEMBER \u00b7 22 MORE DATED BRIEFS "
          "(7 REGIONS MATCHED BY COLOR)")
    bf = fit_single(d, bh, SANS_B, 11, 670)
    d.text((340, 665), bh, font=bf, fill=INK)
    d.line([14, 681, W - 14, 681], fill=INK, width=1)

    # solid-land map, x 14..330, y 685..815, on a pale blue-grey box
    mx0, my0, mx1, my1 = 14, 685, 330, 815
    mw, mh = mx1 - mx0, my1 - my0
    d.rectangle([mx0, my0, mx1, my1], fill=(208, 221, 232),
                outline=(120, 130, 140), width=1)
    for poly in CONTINENTS:
        pts = [(mx0 + (lon + 180) / 360 * mw,
                my0 + (84 - lat) / 142 * mh) for lon, lat in poly]
        d.polygon(pts, fill=(213, 197, 163))
    nf = font(SANS_B, 8)
    for num, lon, lat, dx, dy in PINS:
        px = mx0 + (lon + 180) / 360 * mw + dx
        py = my0 + (84 - lat) / 142 * mh + dy
        px = min(max(px, mx0 + 9), mx1 - 9)
        py = min(max(py, my0 + 9), my1 - 9)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline="white", width=1)
        s = str(num)
        d.text((px - d.textlength(s, font=nf) / 2, py - 6), s,
               font=nf, fill="white")

    # map caption + 7-region legend, flowed under the map
    cf, clines = fit_lines(d, MAP_CAPTION, SANS_R, 8.5, 316, 2, min_size=8)
    cy = 819
    for ln in clines:
        d.text((14, cy), ln, font=cf, fill=INK)
        cy += 11
    ly = cy + 4
    lx = 14
    lf = font(SANS_B, 8)
    for name, ci, cnt in LEGEND:
        label = f"{name} {cnt}"
        iw = 10 + d.textlength(label, font=lf) + 10
        if lx + iw > 330:
            lx = 14
            ly += 13
        d.ellipse([lx, ly + 2, lx + 7, ly + 9], fill=TAB_COLORS[ci])
        d.text((lx + 10, ly), label, font=lf, fill=INK)
        lx += iw
    if ly + 11 > 920:
        problems.append(f"legend overflows: ly={ly}")

    # briefs: TWO columns, 2 lines each — col 1: briefs 14-24, the
    # first 11 in list order (x 340..665), col 2: briefs 25-35, the
    # remaining 11 (x 675..1010). Every brief
    # is EXACTLY 2 lines: line 1: coloured chip with the display
    # number, bold lead (place before the colon) + start of the rest;
    # line 2: rest continued with a hanging indent (aligned with line
    # 1 text, not under the chip), wire source right-aligned at the
    # end of line 2. 8 pt, 8.5 px leading per line, so each brief is
    # 17 px tall. 11 briefs per column, spread EVENLY from y685 to
    # y923 (pitch = (923 - 685 - 17) / 10 = 22.1 px), so the last
    # brief ends exactly at y923, 3 px above the DATE CHECK box.
    # NOTE: every brief's full text fits on ONE line at 8 pt in these
    # column widths, so the split is width-balanced across the 2 lines
    # (lead always whole on line 1) instead of greedily filling line 1,
    # which would leave line 2 empty. Per-brief shrink to 7.5 pt if a
    # more than 2 lines; never 3 lines, never truncated text.
    BRIEF_Y0 = 685
    BRIEF_LEAD = 8.5
    BRIEF_H = 2 * BRIEF_LEAD  # 17 px per brief
    BRIEF_END = 923
    BRIEF_COLS = [(340, 665, BRIEFS[:11]),
                  (675, 1010, BRIEFS[11:])]

    brief_bottom = BRIEF_Y0
    for x, col_right, col_briefs in BRIEF_COLS:
        col_w = col_right - x
        n = len(col_briefs)
        pitch = (BRIEF_END - BRIEF_Y0 - BRIEF_H) / (n - 1) if n > 1 else 0
        for k, (num, txt, reg, src) in enumerate(col_briefs):
            y = BRIEF_Y0 + k * pitch
            bf = font(SANS_B, 8.5)
            ns = str(num)
            d.rectangle([x, y - 1, x + 17, y + 13], fill=TAB_COLORS[reg])
            d.text((x + (18 - d.textlength(ns, font=bf)) / 2, y), ns,
                   font=bf, fill="white")
            tx = x + 22
            lead, rest = txt.split(": ", 1)
            lead_disp = lead + ":"
            words = rest.split(" ")
            sf = font(SANS_R, 8)
            src_w = d.textlength(src, font=sf)
            l1_max = col_w - 22
            l2_max = col_w - 22 - src_w - 6
            chosen = None
            for sz in (8.0, 7.5, 7.0):
                blf = font(SANS_B, sz)
                rlf = font(SANS_R, sz)
                lead_w = d.textlength(lead_disp, font=blf)
                sp_w = d.textlength(" ", font=rlf)
                # pref[i] = width of lead + first i rest words on line 1
                pref = [lead_w]
                for w in words:
                    pref.append(pref[-1] + sp_w
                                + d.textlength(w, font=rlf))
                total = pref[len(words)]

                def line2_w(i):
                    if i >= len(words):
                        return 0.0
                    return total - pref[i] - sp_w

                best = None
                for i in range(len(words) + 1):
                    if pref[i] <= l1_max and line2_w(i) <= l2_max:
                        score = abs(pref[i] - line2_w(i))
                        if best is None or score < best[0]:
                            best = (score, i)
                if best is not None:
                    chosen = (sz, blf, rlf, best[1])
                    break
            if chosen is None:
                problems.append(f"brief {num} needs >2 lines")
                sz = 7.0
                blf = font(SANS_B, sz)
                rlf = font(SANS_R, sz)
                chosen = (sz, blf, rlf, len(words))
            sz, blf, rlf, split = chosen
            line1_rest = " ".join(words[:split])
            line2_rest = " ".join(words[split:])
            d.text((tx, y), lead_disp, font=blf, fill=INK)
            if line1_rest:
                d.text((tx + d.textlength(lead_disp, font=blf) + 3, y),
                       line1_rest, font=rlf, fill=INK)
            if line2_rest:
                d.text((tx, y + BRIEF_LEAD), line2_rest, font=rlf,
                       fill=INK)
            d.text((col_right - src_w, y + BRIEF_LEAD), src, font=sf,
                   fill=GREY)
            brief_bottom = max(brief_bottom, y + BRIEF_H)
    if brief_bottom > 924:
        problems.append(f"briefs overflow: bottom {brief_bottom:.1f}")

    # ---- date check box: paragraph, 2 lines — try 9.5 pt first, then
    # 9.0, then 8.5 (text unchanged); box y 926..962 (36 px): briefs
    # end y 923, box starts 3 px below, HOW SURE stays y 972.
    # Label at the left, vertically centred in the box.
    d.rectangle([14, 926, W - 14, 962], outline=RED, width=2)
    lf = fit_single(d, "DATE CHECK", SANS_B, 11, 168, min_size=8)
    d.text((24, 938), "DATE CHECK", font=lf, fill=RED)
    dc_size = None
    for s in (9.5, 9.0, 8.5):
        tf_try = font(SANS_R, s)
        if len(wrap(d, DATE_CHECK, tf_try, 806)) == 2:
            dc_size = s
            break
    if dc_size is None:
        problems.append("date check does not wrap to 2 lines at 8.5pt")
        dc_size = 8.5
    tf = font(SANS_R, dc_size)
    dc_lines = wrap(d, DATE_CHECK, tf, 806)
    if len(dc_lines) != 2:
        problems.append(f"date check wrapped to {len(dc_lines)} lines, "
                        "expected 2")
    dc_y = 932
    for ln in dc_lines:
        d.text((204, dc_y), ln, font=tf, fill=INK)
        dc_y += 12.5

    # ---- how sure line + sources
    hs_b = font(SANS_B, 9)
    hs_r = font(SANS_R, 9)
    hs_head = "HOW SURE: "
    d.text((14, 972), hs_head, font=hs_b, fill=GREY)
    d.text((14 + d.textlength(hs_head, font=hs_b), 972), HOW_SURE[10:],
           font=hs_r, fill=GREY)
    rt = "Sources: Reuters, AP, AFP."
    f = font(SANS_R, 9)
    d.text((W - 14 - d.textlength(rt, font=f), 972), rt, font=f, fill=GREY)

    # ---- footer bar
    d.rectangle([0, 992, W, H], fill=NAVY)
    d.text((14, 1002), "THE WORLD IN ONE DAY", font=font(SANS_B, 11),
           fill="white")
    rt = "FRIDAY 27 NOVEMBER 2026 \u00b7 ONE PAGE"
    f = font(SANS_B, 9)
    d.text((W - 14 - d.textlength(rt, font=f), 1004), rt, font=f,
           fill="white")

    return img, problems


if __name__ == "__main__":
    img, problems = build()
    # Brightness +10%, same as the 20261126 predecessor.
    # Only brightness — layout/content/numbers/sources untouched.
    img = ImageEnhance.Brightness(img).enhance(1.10)
    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True, compress_level=9)
    data = open(out, "rb").read()
    print(out, img.size, len(data), "bytes",
          hashlib.sha256(data).hexdigest())
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print(" -", p)
    else:
        print("no problems detected by build checks")
