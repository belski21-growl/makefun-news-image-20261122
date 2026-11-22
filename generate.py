#!/usr/bin/env python3
"""Generate entry.png for make.fun news-image-20261122 (LOCAL BUILD TOOL ONLY).

Draws a dense newspaper front page with PIL + DejaVu fonts, following the
proven top-10 template ("The World in One Day"): giant date headline,
6-stat strip, region bar, 3 illustrated leads, 10 illustrated briefs,
"ALSO ON SUNDAY" list, world map with numbered pins, DATE CHECK box,
per-story sources. This script is NOT run by the grader: the shipped
main.py only copies the finished entry.png.
Run: python3 generate.py  ->  writes entry.png next to itself.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 241, 231)
INK = (17, 17, 17)
RED = (176, 30, 36)
RULE = (201, 191, 168)
PANEL = (255, 253, 246)
MUTED = (90, 84, 70)
MAPLAND = (122, 140, 158)
MAPSEA = (233, 238, 240)

REGION_COLORS = {
    "EUROPE": (31, 78, 121),
    "ASIA": (176, 110, 0),
    "MIDDLE EAST": (150, 60, 60),
    "AFRICA": (30, 107, 58),
    "AMERICAS": (107, 45, 122),
    "OCEANIA": (0, 120, 130),
    "GLOBAL": (90, 84, 70),
}
# Story counts per region (36 stories: 3 leads + 10 briefs + 23 ALSO ON).
REGION_COUNTS = [("EUROPE", 15), ("MIDDLE EAST", 5), ("AFRICA", 9),
                 ("AMERICAS", 3), ("ASIA", 3), ("OCEANIA", 1)]

FDIR = "/usr/share/fonts/truetype/dejavu/"
def F(name, size):
    return ImageFont.truetype(FDIR + name, size)

SERIF_B = lambda s: F("DejaVuSerif-Bold.ttf", s)
SANS_B = lambda s: F("DejaVuSans-Bold.ttf", s)
SANS = lambda s: F("DejaVuSans.ttf", s)

# 6 big numbers for the stat strip: (number, label).
STATS = [
    ("2 radars", "Iran targets US Patriots"),
    ("3 killed", "Gaza aid car strike"),
    ("83 hurt", "Russian strikes on Ukraine"),
    ("5,300+", "DRC Ebola death toll"),
    ("293,600", "Kenya-Saudi jobs"),
    ("29-26", "Australia edge Wales"),
]

# (kicker incl. source, headline, deck) — 3 illustrated leads.
LEADS = [
    ("BAHRAIN  •  IRAN  •  ANI",
     "Iran hits two US Patriot radars in Bahrain",
     "IRGC missile and drone strike on US air defences; Bahrain "
     "condemns the attack."),
    ("GAZA  •  WITNESSES  •  REUTERS",
     "Strike kills three in Gaza aid car",
     "Israeli strike hits a vehicle delivering aid, witnesses say; "
     "floods still swamp tent camps."),
    ("LVIV  •  UKRAINE  •  REUTERS",
     "Russian strikes kill two in Lviv, hurt 83",
     "Dashcam catches a huge blast in Lviv; Kryvyi Rih hit too as "
     "attacks spread."),
]

# (icon, kicker incl. source, headline, deck) — 10 illustrated briefs 4-13.
BRIEFS = [
    ("globe", "ANTALYA  •  REUTERS",
     "COP31 in overtime: deal or no deal",
     "Fossil-fuel wording dropped; EU warns of no deal at all."),
    ("flag", "JERUSALEM  •  AP",
     "Eisenkot tapped to form Israel government",
     "President Herzog bypasses Netanyahu; coalition talks open."),
    ("shield", "GAZA  •  AP",
     "Four nations urge Israel to open Gaza aid",
     "Australia, Canada, Italy, UK cite floods in tent camps."),
    ("ship", "GULF OF FINLAND  •  REUTERS",
     "Drone sets Russian ship ablaze at sea",
     "Cargo ship on fire after drone strike; Finland warns of spillover."),
    ("gavel", "OSLO  •  AP",
     "Norway court voids disputed oil licences",
     "Supreme court rules climate-challenged licences invalid."),
    ("chip", "SANTA CLARA  •  REUTERS",
     "Nvidia board rules out Huang return",
     "Shares down 14% since resignation; Kress stays interim CEO."),
    ("burst", "MOGADISHU  •  AP",
     "Al-Shabaab claims hundreds dead in ambush",
     "Militants claim mass casualties in attack on Somali troops."),
    ("quake", "NAYPYITAW  •  ANI",
     "M4.1 quake strikes Myanmar at dawn",
     "Early-hours tremor reported by seismology centre; no toll yet."),
    ("virus", "KINSHASA  •  AP",
     "Kenya clears last Ebola patient",
     "DRC death toll passes 5,300 as outbreak grinds on."),
    ("rugby", "CARDIFF  •  ESPN",
     "Australia edge Wales 29-26",
     "Wallabies deny Wales a third straight autumn win."),
]

# ALSO ON SUNDAY — 23 more stories (14-36), one line each.
ALSO_ON = [
    "Hong Kong votes for Election Committee (Reuters)",
    "US details $12bn in Venezuelan oil revenue (AP)",
    "France: fourth weekend of cost protests (AP)",
    "Zelenskyy: NATO is clearest guarantee (ANI)",
    "Iran calls US blockade a 'hostile act' (ANI)",
    "Ukraine hits Iskander-M fuel plant (Reuters)",
    "Russian strike hits Zaporizhzhya school (AP)",
    "Kenya wins 293,600 Saudi jobs (AP)",
    "Ghana unveils Heritage Series banknotes (AP)",
    "Nigeria: 24 bodies after boat capsize (AP)",
    "Tigray mayor vows elections in six months (AP)",
    "Sahel states restart West Africa talks (AP)",
    "DRC enacts constitutional reform law (AP)",
    "EU hunts new ECB chief as Lagarde quits (AP)",
    "Nigeria starts building naval ships (AP)",
    "Real Madrid 2-1 Celta; Mbappe misses pen (AP)",
    "Arsenal 2-2 Newcastle; Raya injured (ESPN)",
    "Scotland thrash Japan 67-5 in rugby (AP)",
    "Ireland beat South Africa 20-17 (Reuters)",
    "India beat Korea 2-1 in women's hockey (AP)",
    "Germany: IG Metall calls 23,000 out (AP)",
    "Hegseth curbs US-Canada military ties (AP)",
    "Turkey intel chief meets Hamas in Istanbul (AP)",
]

# DATE CHECK — big stories deliberately LEFT OUT (not Sunday news).
DATE_CHECK = [
    ("EU-Indonesia trade deal signed", "Sat 21 Nov"),
    ("'Chapo Isidro' captured in Mexico", "Sat 21 Nov"),
    ("Palisades Fire arsonist convicted", "Fri 20 Nov"),
    ("Ronaldo reaches 986 career goals", "Sat 21 Nov"),
    ("Alcaraz reaches ATP Finals final", "Sat 21 Nov"),
    ("Trump-Xi-Putin Shenzhen summit", "Thu 19 Nov"),
    ("Nvidia posts $115.8bn quarter", "Tue 17 Nov"),
]

# World map: rough continent polygons in fraction coords (x 0-1, y 0-1).
CONTINENTS = [
    [(0.02, 0.10), (0.10, 0.03), (0.20, 0.05), (0.28, 0.10), (0.30, 0.18),
     (0.24, 0.25), (0.20, 0.30), (0.16, 0.42), (0.12, 0.46), (0.08, 0.38),
     (0.04, 0.28), (0.01, 0.18)],  # North America
    [(0.32, 0.03), (0.38, 0.02), (0.40, 0.08), (0.35, 0.12), (0.31, 0.08)],  # Greenland
    [(0.24, 0.48), (0.30, 0.46), (0.34, 0.52), (0.32, 0.66), (0.28, 0.80),
     (0.25, 0.72), (0.22, 0.58)],  # South America
    [(0.47, 0.10), (0.55, 0.08), (0.58, 0.14), (0.55, 0.20), (0.50, 0.22),
     (0.47, 0.16)],  # Europe
    [(0.47, 0.28), (0.56, 0.26), (0.60, 0.32), (0.58, 0.48), (0.54, 0.60),
     (0.50, 0.52), (0.47, 0.38)],  # Africa
    [(0.58, 0.06), (0.75, 0.04), (0.90, 0.08), (0.97, 0.14), (0.92, 0.22),
     (0.85, 0.30), (0.80, 0.36), (0.76, 0.42), (0.72, 0.46), (0.70, 0.40),
     (0.68, 0.30), (0.62, 0.20), (0.58, 0.14)],  # Asia (India peninsula)
    [(0.80, 0.42), (0.83, 0.40), (0.85, 0.44), (0.82, 0.46)],  # SE Asia islands
    [(0.82, 0.62), (0.90, 0.60), (0.93, 0.66), (0.88, 0.72), (0.83, 0.68)],  # Australia
    [(0.455, 0.10), (0.468, 0.12), (0.46, 0.15)],  # Britain
    [(0.935, 0.81), (0.968, 0.80), (0.982, 0.86), (0.955, 0.90), (0.935, 0.88)],  # New Zealand
]
# (story number, lon, lat, dx, dy) — dx/dy nudge the pin so clusters
# do not collide. Pin 1 is Bahrain, 2 Gaza, 3 Lviv, 4 Antalya, 5 Jerusalem,
# 6 London, 7 Gulf of Finland, 8 Oslo, 9 Santa Clara, 10 Mogadishu,
# 11 Naypyitaw, 12 Kinshasa, 13 Cardiff.
PINS = [
    (1, 50.6, 26.2, 0, 0), (2, 34.45, 31.5, 0, 0), (3, 24.03, 49.84, 6, -4),
    (4, 30.7, 36.9, 0, 0), (5, 35.21, 31.77, 0, 6), (6, -0.12, 51.5, -8, -4),
    (7, 24.5, 59.8, 0, -6), (8, 10.75, 59.9, 4, 0), (9, -121.95, 37.35, 0, 0),
    (10, 45.32, 2.05, 0, 0), (11, 96.08, 19.75, 0, 0),
    (12, 15.31, -4.32, 0, 0), (13, -3.18, 51.48, -6, 0),
]

TRUNCATED = []


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, font, max_w, max_lines, tag=""):
    """Wrap to at most max_lines; record (never silently hide) truncation."""
    lines = wrap(draw, text, font, max_w)
    if len(lines) <= max_lines:
        return lines
    TRUNCATED.append("%s: %r needs %d lines, max %d"
                     % (tag, text, len(lines), max_lines))
    lines = lines[:max_lines]
    while lines and draw.textlength(lines[-1] + " ...", font=font) > max_w:
        lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else lines[-1][:-1]
    lines[-1] = lines[-1] + " ..."
    return lines


# ---- Flat illustrations for the 3 leads -----------------------------------
def draw_bahrain(d, x, y, w, h):
    import math
    d.rectangle([x, y, x + w, y + h], fill=(12, 22, 44))
    # Stars.
    for sx, sy in [(20, 8), (60, 16), (120, 6), (200, 12), (260, 8), (300, 18)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                  fill=(255, 255, 255))
    # Sea.
    d.rectangle([x, y + h - 20, x + w, y + h], fill=(24, 48, 92))
    # Radar dish, left.
    cx, cy = x + 52, y + 34
    d.arc([cx - 20, cy - 20, cx + 20, cy + 20], start=250, end=110,
          fill=(255, 255, 255), width=3)
    d.line([(cx, cy), (cx - 14, cy + 18)], fill=(255, 255, 255), width=2)
    d.line([(cx, cy), (cx + 16, cy - 14)], fill=(255, 214, 120), width=2)
    # Two missile trails arcing down from the right (kept inside the art box).
    d.arc([x + 130, y + 2, x + 300, y + 48], start=200, end=330,
          fill=(255, 255, 255), width=2)
    d.arc([x + 170, y + 6, x + 320, y + 46], start=210, end=330,
          fill=(255, 150, 40), width=2)
    # Explosion starburst where a trail lands.
    ex, ey, r = x + 250, y + 30, 13
    for k in range(8):
        a = k * math.pi / 4
        d.line([(ex, ey), (ex + r * math.cos(a), ey + r * math.sin(a))],
               fill=(255, 150, 40), width=3)
    d.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=(255, 210, 90))
    # Small ship silhouette on the sea.
    d.rectangle([x + 120, y + h - 16, x + 200, y + h - 8], fill=(10, 18, 38))
    d.rectangle([x + 150, y + h - 26, x + 170, y + h - 16], fill=(10, 18, 38))


def draw_gaza(d, x, y, w, h):
    import math
    d.rectangle([x, y, x + w, y + h], fill=(28, 24, 20))
    # Night street + damaged buildings.
    heights = [24, 32, 20, 36, 26]
    bw = w // len(heights)
    for i, hh in enumerate(heights):
        bx = x + i * bw + 2
        d.rectangle([bx, y + h - hh, bx + bw - 4, y + h], fill=(12, 10, 8))
        for wy in range(y + h - hh + 5, y + h - 4, 9):
            d.rectangle([bx + 4, wy, bx + 7, wy + 3], fill=(255, 214, 120))
    # Aid truck, centre.
    tx, ty = x + w // 2 - 52, y + h - 34
    d.rectangle([tx, ty, tx + 78, ty + 22], fill=(235, 232, 220))
    d.rectangle([tx + 78, ty + 6, tx + 104, ty + 22], fill=(200, 30, 30))
    d.ellipse([tx + 12, ty + 20, tx + 24, ty + 32], fill=(17, 17, 17))
    d.ellipse([tx + 82, ty + 20, tx + 94, ty + 32], fill=(17, 17, 17))
    # Red cross on the truck side.
    d.rectangle([tx + 34, ty + 6, tx + 44, ty + 16], fill=RED)
    d.rectangle([tx + 29, ty + 9, tx + 49, ty + 13], fill=RED)
    # Blast above the truck.
    ex, ey, r = x + w // 2 + 30, y + 16, 12
    for k in range(8):
        a = k * math.pi / 4
        d.line([(ex, ey), (ex + r * math.cos(a), ey + r * math.sin(a))],
               fill=(255, 150, 40), width=3)
    d.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=(255, 210, 90))
    d.ellipse([ex - 22, ey + 8, ex + 6, ey + 22], fill=(90, 90, 100))


def draw_lviv(d, x, y, w, h):
    import math
    d.rectangle([x, y, x + w, y + h], fill=(16, 20, 36))
    # Skyline.
    heights = [22, 30, 18, 34, 26, 20, 32]
    bw = w // len(heights)
    for i, hh in enumerate(heights):
        bx = x + i * bw + 2
        d.rectangle([bx, y + h - hh, bx + bw - 4, y + h], fill=(5, 8, 16))
        for wy in range(y + h - hh + 5, y + h - 4, 9):
            d.rectangle([bx + 4, wy, bx + 7, wy + 3], fill=(255, 214, 120))
    # Missile trail arc (kept inside the art box).
    d.arc([x + 30, y + 2, x + 240, y + 56], start=200, end=340,
          fill=(255, 255, 255), width=2)
    # Two orange explosion starbursts.
    for cx, cy, r in [(x + 70, y + 22, 12), (x + 250, y + 30, 14)]:
        for k in range(8):
            a = k * math.pi / 4
            d.line([(cx, cy), (cx + r * math.cos(a), cy + r * math.sin(a))],
                   fill=(255, 150, 40), width=3)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 210, 90))
    # Smoke.
    d.ellipse([x + 55, y + 30, x + 95, y + 48], fill=(90, 90, 100))
    d.ellipse([x + 235, y + 38, x + 275, y + 56], fill=(90, 90, 100))


LEAD_ART = [draw_bahrain, draw_gaza, draw_lviv]


# ---- Mini icons for briefs 4-13 (26x26 box) -------------------------------
def icon_globe(d, x, y):
    d.ellipse([x + 3, y + 3, x + 23, y + 23], fill=(31, 78, 121))
    d.polygon([(x + 8, y + 8), (x + 15, y + 7), (x + 18, y + 12), (x + 12, y + 15),
               (x + 8, y + 13)], fill=(60, 160, 90))
    d.polygon([(x + 10, y + 17), (x + 16, y + 17), (x + 14, y + 21), (x + 10, y + 20)],
              fill=(60, 160, 90))
    d.arc([x + 3, y + 3, x + 23, y + 23], start=300, end=60,
          fill=(255, 255, 255), width=1)


def icon_shield(d, x, y):
    d.polygon([(x + 13, y + 2), (x + 23, y + 6), (x + 23, y + 14), (x + 13, y + 24),
               (x + 3, y + 14), (x + 3, y + 6)], fill=(31, 78, 121))
    d.line([(x + 8, y + 13), (x + 12, y + 17), (x + 19, y + 9)],
           fill=(255, 255, 255), width=2)


def icon_chip(d, x, y):
    d.rectangle([x + 5, y + 5, x + 21, y + 21], fill=(17, 17, 17))
    d.rectangle([x + 9, y + 9, x + 17, y + 17], outline=(255, 214, 120), width=1)
    for i in range(3):
        d.line([(x + 8 + i * 5, y + 2), (x + 8 + i * 5, y + 5)], fill=(17, 17, 17), width=2)
        d.line([(x + 8 + i * 5, y + 21), (x + 8 + i * 5, y + 24)], fill=(17, 17, 17), width=2)
        d.line([(x + 2, y + 8 + i * 5), (x + 5, y + 8 + i * 5)], fill=(17, 17, 17), width=2)
        d.line([(x + 21, y + 8 + i * 5), (x + 24, y + 8 + i * 5)], fill=(17, 17, 17), width=2)


def icon_flag(d, x, y):
    d.line([(x + 5, y + 2), (x + 5, y + 24)], fill=(17, 17, 17), width=2)
    for r in range(2):
        for c in range(3):
            if (r + c) % 2 == 0:
                d.rectangle([x + 6 + c * 6, y + 3 + r * 6, x + 11 + c * 6, y + 8 + r * 6],
                            fill=(17, 17, 17))


def icon_ship(d, x, y):
    d.rectangle([x + 3, y + 16, x + 23, y + 21], fill=(31, 78, 121))
    d.rectangle([x + 10, y + 6, x + 16, y + 16], fill=(17, 17, 17))
    d.polygon([(x + 11, y + 6), (x + 11, y + 13), (x + 18, y + 13)],
              fill=(255, 150, 40))
    d.line([(x + 2, y + 23), (x + 24, y + 23)], fill=(31, 78, 121), width=2)
    d.ellipse([x + 18, y + 3, x + 24, y + 9], fill=(255, 150, 40))


def icon_gavel(d, x, y):
    d.polygon([(x + 5, y + 5), (x + 17, y + 17), (x + 14, y + 20), (x + 2, y + 8)],
              fill=(120, 88, 54))
    d.line([(x + 15, y + 15), (x + 22, y + 22)], fill=(120, 88, 54), width=3)
    d.line([(x + 4, y + 23), (x + 22, y + 23)], fill=(17, 17, 17), width=2)


def icon_burst(d, x, y):
    import math
    cx, cy = x + 13, y + 13
    for k in range(8):
        a = k * math.pi / 4
        d.line([(cx, cy), (cx + 11 * math.cos(a), cy + 11 * math.sin(a))],
               fill=(255, 150, 40), width=2)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)


def icon_quake(d, x, y):
    import math
    pts = []
    for i in range(0, 26, 2):
        amp = 2 if i < 8 or i > 18 else 7
        yy = y + 13 + (amp * math.sin(i / 2.0) if i % 4 else -amp)
        pts.append((x + i, yy))
    d.line(pts, fill=RED, width=2)
    d.line([(x + 3, y + 22), (x + 12, y + 18), (x + 20, y + 22)],
           fill=(90, 60, 30), width=2)


def icon_virus(d, x, y):
    import math
    cx, cy = x + 13, y + 13
    for k in range(8):
        a = k * math.pi / 4
        d.line([(cx + 6 * math.cos(a), cy + 6 * math.sin(a)),
                (cx + 10 * math.cos(a), cy + 10 * math.sin(a))],
               fill=(150, 60, 60), width=2)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(150, 60, 60))
    d.ellipse([cx - 2, cy - 3, cx + 1, cy + 0], fill=(255, 255, 255))


def icon_rugby(d, x, y):
    d.ellipse([x + 3, y + 7, x + 23, y + 19], fill=(120, 70, 30))
    d.line([(x + 9, y + 8), (x + 9, y + 18)], fill=(255, 255, 255), width=1)
    d.line([(x + 17, y + 8), (x + 17, y + 18)], fill=(255, 255, 255), width=1)
    d.line([(x + 11, y + 12), (x + 15, y + 12)], fill=(255, 255, 255), width=1)


ICONS = {"globe": icon_globe, "shield": icon_shield, "chip": icon_chip,
         "flag": icon_flag, "ship": icon_ship, "gavel": icon_gavel,
         "burst": icon_burst, "quake": icon_quake, "virus": icon_virus,
         "rugby": icon_rugby}


def draw():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead: kicker + giant date headline + sub-headline ------------
    d.rectangle([18, 10, 1006, 15], fill=INK)
    kick = "THE WORLD IN ONE DAY"
    kf = SANS_B(15)
    kw = d.textlength(kick, font=kf)
    d.text(((W - kw) / 2, 22), kick, font=kf, fill=INK)
    date = "Sunday 22 November 2026"
    df = SERIF_B(46)
    dw = d.textlength(date, font=df)
    d.text(((W - dw) / 2, 40), date, font=df, fill=INK)
    sub = ("Iran hits US radars in Bahrain  •  Gaza aid car strike kills 3  •  "
           "Russian strikes kill 2 in Lviv")
    sf = SANS(13)
    sw = d.textlength(sub, font=sf)
    d.text(((W - sw) / 2, 92), sub, font=sf, fill=MUTED)
    d.rectangle([18, 110, 1006, 112], fill=RED)

    # ---- Stat strip: 6 big numbers ---------------------------------------
    sy = 120
    cw = 160
    for i, (num, label) in enumerate(STATS):
        x = 18 + i * (cw + 5)
        d.rectangle([x, sy - 4, x + cw, sy + 44], fill=PANEL, outline=RULE, width=1)
        nf = SERIF_B(26)
        nw = d.textlength(num, font=nf)
        d.text((x + (cw - nw) / 2, sy), num, font=nf, fill=RED)
        lf = SANS(10)
        lw = d.textlength(label, font=lf)
        d.text((x + (cw - lw) / 2, sy + 32), label, font=lf, fill=INK)

    # ---- Region bar --------------------------------------------------------
    ry = 176
    x = 18
    rf = SANS_B(11)
    for name, count in REGION_COUNTS:
        d.rectangle([x, ry, x + 12, ry + 12], fill=REGION_COLORS[name])
        label = "%s %d" % (name, count)
        d.text((x + 17, ry - 1), label, font=rf, fill=INK)
        x += 17 + int(d.textlength(label, font=rf)) + 24
    d.rectangle([18, 196, 1006, 198], fill=INK)

    # ---- 3 illustrated leads ----------------------------------------------
    ly, lh = 206, 154
    lw = 322
    for i, (kicker, head, deck) in enumerate(LEADS):
        x = 18 + i * (lw + 10)
        LEAD_ART[i](d, x, ly, lw, 58)
        d.text((x, ly + 64), kicker, font=SANS_B(11), fill=RED)
        hf = SERIF_B(19)
        hlines = fit_lines(d, head, hf, lw, 2, tag="lead%d-head" % (i + 1))
        hy = ly + 82
        for ln in hlines:
            d.text((x, hy), ln, font=hf, fill=INK)
            hy += 22
        df2 = SANS(12)
        dlines = fit_lines(d, deck, df2, lw, 2, tag="lead%d-deck" % (i + 1))
        dy = ly + 126
        for ln in dlines:
            d.text((x, dy), ln, font=df2, fill=MUTED)
            dy += 15
        if i < 2:
            d.line([x + lw + 5, ly, x + lw + 5, ly + lh], fill=RULE, width=1)
    d.rectangle([18, 368, 1006, 370], fill=INK)

    # ---- 10 illustrated briefs, 5 x 2 --------------------------------------
    bx0, by0 = 18, 378
    cw2, ch2, gx2, gy2 = 190, 88, 9, 8
    for idx, (icon, kicker, head, deck) in enumerate(BRIEFS):
        row, col = divmod(idx, 5)
        x = bx0 + col * (cw2 + gx2)
        y = by0 + row * (ch2 + gy2)
        num = str(idx + 4)
        nf = SANS_B(11)
        nw = d.textlength(num, font=nf)
        d.text((x, y + 1), num, font=nf, fill=RED)
        ICONS[icon](d, x + 16, y)
        d.text((x + 46, y + 6), kicker, font=SANS_B(9), fill=MUTED)
        hf = SANS_B(12)
        hlines = fit_lines(d, head, hf, cw2, 2, tag="brief%d-head" % (idx + 4))
        hy = y + 28
        for ln in hlines:
            d.text((x, hy), ln, font=hf, fill=INK)
            hy += 15
        df3 = SANS(10)
        dlines = fit_lines(d, deck, df3, cw2, 2, tag="brief%d-deck" % (idx + 4))
        dy = hy + 1
        for ln in dlines:
            d.text((x, dy), ln, font=df3, fill=MUTED)
            dy += 13
    d.rectangle([18, 562, 1006, 564], fill=INK)

    # ---- ALSO ON SUNDAY: 23 more stories, 2 columns -----------------------
    ay = 572
    tf = SANS_B(13)
    d.text((18, ay), "ALSO ON SUNDAY — 23 MORE STORIES", font=tf, fill=INK)
    af = SANS(11)
    col_w = 312
    for idx, item in enumerate(ALSO_ON):
        col = 0 if idx < 12 else 1
        row = idx if idx < 12 else idx - 12
        x = 18 + col * (col_w + 14)
        y = ay + 26 + row * 16
        line = "%d  %s" % (idx + 14, item)
        lines = fit_lines(d, line, af, col_w, 1, tag="also%d" % (idx + 14))
        d.text((x, y), lines[0], font=af, fill=INK)

    # ---- DATE CHECK box (bottom left) --------------------------------------
    dx0, dy0 = 18, 800
    d.rectangle([dx0, dy0, dx0 + 638, dy0 + 156], fill=(233, 226, 208),
                outline=RED, width=2)
    d.text((dx0 + 12, dy0 + 8), "DATE CHECK — WHAT WE LEFT OUT",
           font=SANS_B(13), fill=RED)
    d.text((dx0 + 12, dy0 + 28),
           "These big stories are NOT from Sunday 22 November, so they are not in this paper:",
           font=SANS(10), fill=INK)
    cf = SANS(11)
    for i, (story, when) in enumerate(DATE_CHECK):
        y = dy0 + 50 + i * 14
        d.text((dx0 + 12, y), "×  %s" % story, font=cf, fill=INK)
        ww = d.textlength(when, font=SANS_B(11))
        d.text((dx0 + 638 - 12 - ww, y), when, font=SANS_B(11), fill=RED)

    # ---- World map with numbered pins (right column) -----------------------
    mx0, my0, mw, mh = 668, 572, 338, 238
    d.rectangle([mx0, my0, mx0 + mw, my0 + mh], fill=PANEL, outline=RULE, width=1)
    d.text((mx0 + 10, my0 + 8), "WHERE IT HAPPENED — PINS 1–13",
           font=SANS_B(12), fill=INK)
    map_x, map_y, map_w, map_h = mx0 + 8, my0 + 30, mw - 16, 176
    d.rectangle([map_x, map_y, map_x + map_w, map_y + map_h], fill=MAPSEA)
    for poly in CONTINENTS:
        pts = [(map_x + fx * map_w, map_y + fy * map_h) for fx, fy in poly]
        d.polygon(pts, fill=MAPLAND)
    pf = SANS_B(7)
    for num, lon, lat, ddx, ddy in PINS:
        px = map_x + (lon + 170) / 360.0 * map_w + ddx
        py = map_y + (75 - lat) / 130.0 * map_h + ddy
        fill = RED if num <= 3 else (31, 78, 121)
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=fill,
                  outline=(255, 255, 255), width=1)
        tw = d.textlength(str(num), font=pf)
        d.text((px - tw / 2, py - 5), str(num), font=pf, fill=(255, 255, 255))
    d.text((mx0 + 10, my0 + 212),
           "Pins 1–13 mark the drawn stories.",
           font=SANS(10), fill=MUTED)
    d.text((mx0 + 10, my0 + 226),
           "Red pins are the three leads.",
           font=SANS(10), fill=MUTED)

    # ---- Honesty note + sources (right column, below map) ------------------
    hy = 826
    d.text((mx0, hy), "OUR PROMISE", font=SANS_B(11), fill=RED)
    promise = ("Every story here happened, or was first reported, on Sunday "
               "22 November 2026 in at least one time zone. Claims are "
               "attributed; forecasts are flagged. Original drawings.")
    plines = fit_lines(d, promise, SANS(10), mw, 6, tag="promise")
    yy = hy + 18
    for ln in plines:
        d.text((mx0, yy), ln, font=SANS(10), fill=INK)
        yy += 13
    yy += 6
    d.text((mx0, yy), "SOURCES", font=SANS_B(11), fill=RED)
    yy += 16
    src = "BBC, Reuters, AP, AFP, ANI, ESPN, USGS, ESA."
    for ln in fit_lines(d, src, SANS(10), mw, 2, tag="sources"):
        d.text((mx0, yy), ln, font=SANS(10), fill=INK)
        yy += 13

    # ---- Footer ------------------------------------------------------------
    d.rectangle([18, 968, 1006, 970], fill=INK)
    foot = "THE WORLD IN ONE DAY  •  SUNDAY 22 NOVEMBER 2026  •  ONE DAY, EVERY CONTINENT"
    ff = SANS_B(11)
    fw = d.textlength(foot, font=ff)
    d.text(((W - fw) / 2, 978), foot, font=ff, fill=MUTED)

    return img


if __name__ == "__main__":
    import hashlib, os
    img = draw()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    data = open(out, "rb").read()
    print("wrote", out, len(data), "bytes")
    print("sha256", hashlib.sha256(data).hexdigest())
    print("size", img.size, "mode", img.mode)
    if TRUNCATED:
        print("TRUNCATION-RISK: %d items" % len(TRUNCATED))
        for t in TRUNCATED:
            print("  -", t)
    else:
        print("TRUNCATION-RISK: none")
