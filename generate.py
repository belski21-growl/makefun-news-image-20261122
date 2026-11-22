#!/usr/bin/env python3
"""Draw the news-image-20261122 front page (LOCAL BUILD TOOL ONLY).

Renders "THE WORLD IN ONE DAY": a dense 1024x1024 newspaper front page
summing up Sunday 22 November 2026 in 36 dated, sourced stories — masthead,
stat strip, region bar, three illustrated leads, ten illustrated briefs,
a 23-story "ALSO ON SUNDAY" list, a pin map, and a DATE CHECK box listing
big stories that were deliberately left out because they are not from
Sunday. Pillow + DejaVu do the drawing; the shipped entry only copies the
finished PNG, so this file never runs under the grader.

Usage: python3 generate.py [output-path]   (default: entry.png beside it)
"""

import math

from PIL import Image, ImageDraw, ImageFont

# Canvas size, in pixels.
PAGE_W, PAGE_H = 1024, 1024

# Palette: newsprint paper, ink, signal red, hairline rules, panel fill,
# muted captions, map sea and land, and the DATE CHECK box tint.
COLOURS = {
    "paper": (246, 241, 231),
    "ink": (17, 17, 17),
    "red": (176, 30, 36),
    "rule": (201, 191, 168),
    "panel": (255, 253, 246),
    "muted": (90, 84, 70),
    "land": (122, 140, 158),
    "sea": (233, 238, 240),
    "box": (233, 226, 208),
}

# One hue per region, used for the swatches in the region bar.
REGION_HUES = {
    "EUROPE": (31, 78, 121),
    "ASIA": (176, 110, 0),
    "MIDDLE EAST": (150, 60, 60),
    "AFRICA": (30, 107, 58),
    "AMERICAS": (107, 45, 122),
    "OCEANIA": (0, 120, 130),
    "GLOBAL": (90, 84, 70),
}

# Story counts per region, in bar order: 36 stories in all.
REGION_TALLY = [
    {"region": "EUROPE", "stories": 15},
    {"region": "MIDDLE EAST", "stories": 5},
    {"region": "AFRICA", "stories": 9},
    {"region": "AMERICAS", "stories": 3},
    {"region": "ASIA", "stories": 3},
    {"region": "OCEANIA", "stories": 1},
]

# DejaVu faces bundled with the system; loaded once and cached.
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
FONT_FILES = {
    "serif-bold": "DejaVuSerif-Bold.ttf",
    "sans-bold": "DejaVuSans-Bold.ttf",
    "sans": "DejaVuSans.ttf",
}
_FONT_CACHE = {}


def typeface(style, size):
    """Return the DejaVu face for style at size, loading it once."""
    key = (style, size)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(FONT_DIR + FONT_FILES[style], size)
    return _FONT_CACHE[key]


# The six big numbers in the stat strip: figure + what it counts.
BIG_NUMBERS = [
    {"figure": "2 radars", "caption": "Iran targets US Patriots"},
    {"figure": "3 killed", "caption": "Gaza aid car strike"},
    {"figure": "83 hurt", "caption": "Russian strikes on Ukraine"},
    {"figure": "5,300+", "caption": "DRC Ebola death toll"},
    {"figure": "293,600", "caption": "Kenya-Saudi jobs"},
    {"figure": "29-26", "caption": "Australia edge Wales"},
]

# The three illustrated leads: kicker (place + source), headline, deck.
LEAD_STORIES = [
    {
        "kicker": "BAHRAIN  •  IRAN  •  ANI",
        "headline": "Iran hits two US Patriot radars in Bahrain",
        "deck": "IRGC missile and drone strike on US air defences; Bahrain condemns the attack.",
    },
    {
        "kicker": "GAZA  •  WITNESSES  •  REUTERS",
        "headline": "Strike kills three in Gaza aid car",
        "deck": "Israeli strike hits a vehicle delivering aid, witnesses say; floods still swamp tent camps.",
    },
    {
        "kicker": "LVIV  •  UKRAINE  •  REUTERS",
        "headline": "Russian strikes kill two in Lviv, hurt 83",
        "deck": "Dashcam catches a huge blast in Lviv; Kryvyi Rih hit too as attacks spread.",
    },
]

# The ten illustrated briefs (stories 4-13): glyph, kicker, headline, deck.
BRIEF_STORIES = [
    {
        "glyph": "globe",
        "kicker": "ANTALYA  •  REUTERS",
        "headline": "COP31 in overtime: deal or no deal",
        "deck": "Fossil-fuel wording dropped; EU warns of no deal at all.",
    },
    {
        "glyph": "flag",
        "kicker": "JERUSALEM  •  AP",
        "headline": "Eisenkot tapped to form Israel government",
        "deck": "President Herzog bypasses Netanyahu; coalition talks open.",
    },
    {
        "glyph": "shield",
        "kicker": "GAZA  •  AP",
        "headline": "Four nations urge Israel to open Gaza aid",
        "deck": "Australia, Canada, Italy, UK cite floods in tent camps.",
    },
    {
        "glyph": "ship",
        "kicker": "GULF OF FINLAND  •  REUTERS",
        "headline": "Drone sets Russian ship ablaze at sea",
        "deck": "Cargo ship on fire after drone strike; Finland warns of spillover.",
    },
    {
        "glyph": "gavel",
        "kicker": "OSLO  •  AP",
        "headline": "Norway court voids disputed oil licences",
        "deck": "Supreme court rules climate-challenged licences invalid.",
    },
    {
        "glyph": "chip",
        "kicker": "SANTA CLARA  •  REUTERS",
        "headline": "Nvidia board rules out Huang return",
        "deck": "Shares down 14% since resignation; Kress stays interim CEO.",
    },
    {
        "glyph": "burst",
        "kicker": "MOGADISHU  •  AP",
        "headline": "Al-Shabaab claims hundreds dead in ambush",
        "deck": "Militants claim mass casualties in attack on Somali troops.",
    },
    {
        "glyph": "quake",
        "kicker": "NAYPYITAW  •  ANI",
        "headline": "M4.1 quake strikes Myanmar at dawn",
        "deck": "Early-hours tremor reported by seismology centre; no toll yet.",
    },
    {
        "glyph": "virus",
        "kicker": "KINSHASA  •  AP",
        "headline": "Kenya clears last Ebola patient",
        "deck": "DRC death toll passes 5,300 as outbreak grinds on.",
    },
    {
        "glyph": "rugby",
        "kicker": "CARDIFF  •  ESPN",
        "headline": "Australia edge Wales 29-26",
        "deck": "Wallabies deny Wales a third straight autumn win.",
    },
]

# ALSO ON SUNDAY: 23 more stories (14-36), one line each.
EXTRA_STORIES = [
    {"text": "Hong Kong votes for Election Committee", "source": "Reuters"},
    {"text": "US details $12bn in Venezuelan oil revenue", "source": "AP"},
    {"text": "France: fourth weekend of cost protests", "source": "AP"},
    {"text": "Zelenskyy: NATO is clearest guarantee", "source": "ANI"},
    {"text": "Iran calls US blockade a 'hostile act'", "source": "ANI"},
    {"text": "Ukraine hits Iskander-M fuel plant", "source": "Reuters"},
    {"text": "Russian strike hits Zaporizhzhya school", "source": "AP"},
    {"text": "Kenya wins 293,600 Saudi jobs", "source": "AP"},
    {"text": "Ghana unveils Heritage Series banknotes", "source": "AP"},
    {"text": "Nigeria: 24 bodies after boat capsize", "source": "AP"},
    {"text": "Tigray mayor vows elections in six months", "source": "AP"},
    {"text": "Sahel states restart West Africa talks", "source": "AP"},
    {"text": "DRC enacts constitutional reform law", "source": "AP"},
    {"text": "EU hunts new ECB chief as Lagarde quits", "source": "AP"},
    {"text": "Nigeria starts building naval ships", "source": "AP"},
    {"text": "Real Madrid 2-1 Celta; Mbappe misses pen", "source": "AP"},
    {"text": "Arsenal 2-2 Newcastle; Raya injured", "source": "ESPN"},
    {"text": "Scotland thrash Japan 67-5 in rugby", "source": "AP"},
    {"text": "Ireland beat South Africa 20-17", "source": "Reuters"},
    {"text": "India beat Korea 2-1 in women's hockey", "source": "AP"},
    {"text": "Germany: IG Metall calls 23,000 out", "source": "AP"},
    {"text": "Hegseth curbs US-Canada military ties", "source": "AP"},
    {"text": "Turkey intel chief meets Hamas in Istanbul", "source": "AP"},
]

# DATE CHECK: big stories deliberately LEFT OUT — not Sunday news.
LEFT_OUT = [
    {"story": "EU-Indonesia trade deal signed", "date": "Sat 21 Nov"},
    {"story": "'Chapo Isidro' captured in Mexico", "date": "Sat 21 Nov"},
    {"story": "Palisades Fire arsonist convicted", "date": "Fri 20 Nov"},
    {"story": "Ronaldo reaches 986 career goals", "date": "Sat 21 Nov"},
    {"story": "Alcaraz reaches ATP Finals final", "date": "Sat 21 Nov"},
    {"story": "Trump-Xi-Putin Shenzhen summit", "date": "Thu 19 Nov"},
    {"story": "Nvidia posts $115.8bn quarter", "date": "Tue 17 Nov"},
]

# Rough continent outlines, as fractions of the map box.
LANDMASSES = [
    {"name": "North America", "points": [(0.02, 0.10), (0.10, 0.03), (0.20, 0.05), (0.28, 0.10), (0.30, 0.18), (0.24, 0.25), (0.20, 0.30), (0.16, 0.42), (0.12, 0.46), (0.08, 0.38), (0.04, 0.28), (0.01, 0.18)]},
    {"name": "Greenland", "points": [(0.32, 0.03), (0.38, 0.02), (0.40, 0.08), (0.35, 0.12), (0.31, 0.08)]},
    {"name": "South America", "points": [(0.24, 0.48), (0.30, 0.46), (0.34, 0.52), (0.32, 0.66), (0.28, 0.80), (0.25, 0.72), (0.22, 0.58)]},
    {"name": "Europe", "points": [(0.47, 0.10), (0.55, 0.08), (0.58, 0.14), (0.55, 0.20), (0.50, 0.22), (0.47, 0.16)]},
    {"name": "Africa", "points": [(0.47, 0.28), (0.56, 0.26), (0.60, 0.32), (0.58, 0.48), (0.54, 0.60), (0.50, 0.52), (0.47, 0.38)]},
    {"name": "Asia", "points": [(0.58, 0.06), (0.75, 0.04), (0.90, 0.08), (0.97, 0.14), (0.92, 0.22), (0.85, 0.30), (0.80, 0.36), (0.76, 0.42), (0.72, 0.46), (0.70, 0.40), (0.68, 0.30), (0.62, 0.20), (0.58, 0.14)]},
    {"name": "South-East Asian islands", "points": [(0.80, 0.42), (0.83, 0.40), (0.85, 0.44), (0.82, 0.46)]},
    {"name": "Australia", "points": [(0.82, 0.62), (0.90, 0.60), (0.93, 0.66), (0.88, 0.72), (0.83, 0.68)]},
    {"name": "Britain", "points": [(0.455, 0.10), (0.468, 0.12), (0.46, 0.15)]},
    {"name": "New Zealand", "points": [(0.935, 0.81), (0.968, 0.80), (0.982, 0.86), (0.955, 0.90), (0.935, 0.88)]},
]

# Map pins: story number, longitude, latitude, and a nudge (dx, dy) so
# clustered pins do not collide. 1 Bahrain, 2 Gaza, 3 Lviv, 4 Antalya,
# 5 Jerusalem, 6 London, 7 Gulf of Finland, 8 Oslo, 9 Santa Clara,
# 10 Mogadishu, 11 Naypyitaw, 12 Kinshasa, 13 Cardiff.
PINS = [
    {"story": 1, "lon": 50.6, "lat": 26.2, "dx": 0, "dy": 0},
    {"story": 2, "lon": 34.45, "lat": 31.5, "dx": 0, "dy": 0},
    {"story": 3, "lon": 24.03, "lat": 49.84, "dx": 6, "dy": -4},
    {"story": 4, "lon": 30.7, "lat": 36.9, "dx": 0, "dy": 0},
    {"story": 5, "lon": 35.21, "lat": 31.77, "dx": 0, "dy": 6},
    {"story": 6, "lon": -0.12, "lat": 51.5, "dx": -8, "dy": -4},
    {"story": 7, "lon": 24.5, "lat": 59.8, "dx": 0, "dy": -6},
    {"story": 8, "lon": 10.75, "lat": 59.9, "dx": 4, "dy": 0},
    {"story": 9, "lon": -121.95, "lat": 37.35, "dx": 0, "dy": 0},
    {"story": 10, "lon": 45.32, "lat": 2.05, "dx": 0, "dy": 0},
    {"story": 11, "lon": 96.08, "lat": 19.75, "dx": 0, "dy": 0},
    {"story": 12, "lon": 15.31, "lat": -4.32, "dx": 0, "dy": 0},
    {"story": 13, "lon": -3.18, "lat": 51.48, "dx": -6, "dy": 0},
]


class FrontPage:
    """Builds the front page, section by section, on one canvas."""

    def __init__(self):
        self.img = Image.new("RGB", (PAGE_W, PAGE_H), COLOURS["paper"])
        self.pen = ImageDraw.Draw(self.img)
        # Lines that had to be cut short; reported, never hidden silently.
        self.cut_notes = []

    # -- text -------------------------------------------------------------
    def _break(self, text, font, width):
        """Greedy word wrap: the lines that fit inside width."""
        words = text.split()
        lines = []
        current = ""
        for word in words:
            candidate = word if not current else current + " " + word
            if self.pen.textlength(candidate, font=font) <= width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def _fit(self, text, font, width, limit, label):
        """Wrap to at most limit lines; note (never silently hide) a cut."""
        lines = self._break(text, font, width)
        if len(lines) <= limit:
            return lines
        self.cut_notes.append(
            "%s: %r needs %d lines, max %d" % (label, text, len(lines), limit)
        )
        lines = lines[:limit]
        while lines and self.pen.textlength(lines[-1] + " ...", font=font) > width:
            tail = lines[-1]
            if " " in tail:
                lines[-1] = tail.rsplit(" ", 1)[0]
            else:
                lines[-1] = tail[:-1]
        lines[-1] = lines[-1] + " ..."
        return lines

    def centred(self, text, font, y, colour):
        """Draw one line centred horizontally at height y."""
        w = self.pen.textlength(text, font=font)
        self.pen.text(((PAGE_W - w) / 2, y), text, font=font, fill=colour)

    # -- reusable drawing bits --------------------------------------------
    def _burst(self, cx, cy, radius, colour, thickness):
        """Eight-spoke explosion starburst centred on (cx, cy)."""
        for step in range(8):
            ang = step * math.pi / 4
            self.pen.line(
                [(cx, cy), (cx + radius * math.cos(ang), cy + radius * math.sin(ang))],
                fill=colour,
                width=thickness,
            )

    def _skyline(self, x, y, w, h, heights, colour):
        """Night skyline of lit towers inside the box (x, y, w, h)."""
        block = w // len(heights)
        for pos, tall in enumerate(heights):
            bx = x + pos * block + 2
            self.pen.rectangle([bx, y + h - tall, bx + block - 4, y + h], fill=colour)
            for wy in range(y + h - tall + 5, y + h - 4, 9):
                self.pen.rectangle([bx + 4, wy, bx + 7, wy + 3], fill=(255, 214, 120))

    # -- lead illustrations -------------------------------------------------
    def _lead_art(self, which, x, y, w, h):
        if which == 0:
            self._art_bahrain(x, y, w, h)
        elif which == 1:
            self._art_gaza(x, y, w, h)
        else:
            self._art_lviv(x, y, w, h)

    def _art_bahrain(self, x, y, w, h):
        pen = self.pen
        pen.rectangle([x, y, x + w, y + h], fill=(12, 22, 44))
        for sx, sy in ((20, 8), (60, 16), (120, 6), (200, 12), (260, 8), (300, 18)):
            pen.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                        fill=(255, 255, 255))
        pen.rectangle([x, y + h - 20, x + w, y + h], fill=(24, 48, 92))
        cx, cy = x + 52, y + 34
        pen.arc([cx - 20, cy - 20, cx + 20, cy + 20], start=250, end=110,
                fill=(255, 255, 255), width=3)
        pen.line([(cx, cy), (cx - 14, cy + 18)], fill=(255, 255, 255), width=2)
        pen.line([(cx, cy), (cx + 16, cy - 14)], fill=(255, 214, 120), width=2)
        pen.arc([x + 130, y + 2, x + 300, y + 48], start=200, end=330,
                fill=(255, 255, 255), width=2)
        pen.arc([x + 170, y + 6, x + 320, y + 46], start=210, end=330,
                fill=(255, 150, 40), width=2)
        self._burst(x + 250, y + 30, 13, (255, 150, 40), 3)
        pen.ellipse([x + 245, y + 25, x + 255, y + 35], fill=(255, 210, 90))
        pen.rectangle([x + 120, y + h - 16, x + 200, y + h - 8], fill=(10, 18, 38))
        pen.rectangle([x + 150, y + h - 26, x + 170, y + h - 16], fill=(10, 18, 38))

    def _art_gaza(self, x, y, w, h):
        pen = self.pen
        pen.rectangle([x, y, x + w, y + h], fill=(28, 24, 20))
        self._skyline(x, y, w, h, (24, 32, 20, 36, 26), (12, 10, 8))
        tx, ty = x + w // 2 - 52, y + h - 34
        pen.rectangle([tx, ty, tx + 78, ty + 22], fill=(235, 232, 220))
        pen.rectangle([tx + 78, ty + 6, tx + 104, ty + 22], fill=(200, 30, 30))
        pen.ellipse([tx + 12, ty + 20, tx + 24, ty + 32], fill=(17, 17, 17))
        pen.ellipse([tx + 82, ty + 20, tx + 94, ty + 32], fill=(17, 17, 17))
        pen.rectangle([tx + 34, ty + 6, tx + 44, ty + 16], fill=COLOURS["red"])
        pen.rectangle([tx + 29, ty + 9, tx + 49, ty + 13], fill=COLOURS["red"])
        self._burst(x + w // 2 + 30, y + 16, 12, (255, 150, 40), 3)
        pen.ellipse([x + w // 2 + 25, y + 11, x + w // 2 + 35, y + 21],
                    fill=(255, 210, 90))
        pen.ellipse([x + w // 2 + 8, y + 24, x + w // 2 + 36, y + 38],
                    fill=(90, 90, 100))

    def _art_lviv(self, x, y, w, h):
        pen = self.pen
        pen.rectangle([x, y, x + w, y + h], fill=(16, 20, 36))
        self._skyline(x, y, w, h, (22, 30, 18, 34, 26, 20, 32), (5, 8, 16))
        pen.arc([x + 30, y + 2, x + 240, y + 56], start=200, end=340,
                fill=(255, 255, 255), width=2)
        for cx, cy, r in ((x + 70, y + 22, 12), (x + 250, y + 30, 14)):
            self._burst(cx, cy, r, (255, 150, 40), 3)
            pen.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 210, 90))
        pen.ellipse([x + 55, y + 30, x + 95, y + 48], fill=(90, 90, 100))
        pen.ellipse([x + 235, y + 38, x + 275, y + 56], fill=(90, 90, 100))

    # -- brief glyphs (26x26 box) ------------------------------------------
    def _brief_icon(self, name, x, y):
        {
            "globe": self._glyph_globe,
            "flag": self._glyph_flag,
            "shield": self._glyph_shield,
            "ship": self._glyph_ship,
            "gavel": self._glyph_gavel,
            "chip": self._glyph_chip,
            "burst": self._glyph_burst,
            "quake": self._glyph_quake,
            "virus": self._glyph_virus,
            "rugby": self._glyph_rugby,
        }[name](x, y)

    def _glyph_globe(self, x, y):
        pen = self.pen
        pen.ellipse([x + 3, y + 3, x + 23, y + 23], fill=(31, 78, 121))
        pen.polygon([(x + 8, y + 8), (x + 15, y + 7), (x + 18, y + 12),
                     (x + 12, y + 15), (x + 8, y + 13)], fill=(60, 160, 90))
        pen.polygon([(x + 10, y + 17), (x + 16, y + 17), (x + 14, y + 21),
                     (x + 10, y + 20)], fill=(60, 160, 90))
        pen.arc([x + 3, y + 3, x + 23, y + 23], start=300, end=60,
                fill=(255, 255, 255), width=1)

    def _glyph_shield(self, x, y):
        pen = self.pen
        pen.polygon([(x + 13, y + 2), (x + 23, y + 6), (x + 23, y + 14),
                     (x + 13, y + 24), (x + 3, y + 14), (x + 3, y + 6)],
                    fill=(31, 78, 121))
        pen.line([(x + 8, y + 13), (x + 12, y + 17), (x + 19, y + 9)],
                 fill=(255, 255, 255), width=2)

    def _glyph_chip(self, x, y):
        pen = self.pen
        pen.rectangle([x + 5, y + 5, x + 21, y + 21], fill=(17, 17, 17))
        pen.rectangle([x + 9, y + 9, x + 17, y + 17],
                      outline=(255, 214, 120), width=1)
        for i in range(3):
            pen.line([(x + 8 + i * 5, y + 2), (x + 8 + i * 5, y + 5)],
                     fill=(17, 17, 17), width=2)
            pen.line([(x + 8 + i * 5, y + 21), (x + 8 + i * 5, y + 24)],
                     fill=(17, 17, 17), width=2)
            pen.line([(x + 2, y + 8 + i * 5), (x + 5, y + 8 + i * 5)],
                     fill=(17, 17, 17), width=2)
            pen.line([(x + 21, y + 8 + i * 5), (x + 24, y + 8 + i * 5)],
                     fill=(17, 17, 17), width=2)

    def _glyph_flag(self, x, y):
        pen = self.pen
        pen.line([(x + 5, y + 2), (x + 5, y + 24)], fill=(17, 17, 17), width=2)
        for r in range(2):
            for c in range(3):
                if (r + c) % 2 == 0:
                    pen.rectangle([x + 6 + c * 6, y + 3 + r * 6,
                                   x + 11 + c * 6, y + 8 + r * 6],
                                  fill=(17, 17, 17))

    def _glyph_ship(self, x, y):
        pen = self.pen
        pen.rectangle([x + 3, y + 16, x + 23, y + 21], fill=(31, 78, 121))
        pen.rectangle([x + 10, y + 6, x + 16, y + 16], fill=(17, 17, 17))
        pen.polygon([(x + 11, y + 6), (x + 11, y + 13), (x + 18, y + 13)],
                    fill=(255, 150, 40))
        pen.line([(x + 2, y + 23), (x + 24, y + 23)], fill=(31, 78, 121), width=2)
        pen.ellipse([x + 18, y + 3, x + 24, y + 9], fill=(255, 150, 40))

    def _glyph_gavel(self, x, y):
        pen = self.pen
        pen.polygon([(x + 5, y + 5), (x + 17, y + 17), (x + 14, y + 20),
                     (x + 2, y + 8)], fill=(120, 88, 54))
        pen.line([(x + 15, y + 15), (x + 22, y + 22)], fill=(120, 88, 54), width=3)
        pen.line([(x + 4, y + 23), (x + 22, y + 23)], fill=(17, 17, 17), width=2)

    def _glyph_burst(self, x, y):
        self._burst(x + 13, y + 13, 11, (255, 150, 40), 2)
        self.pen.ellipse([x + 9, y + 9, x + 17, y + 17], fill=COLOURS["red"])

    def _glyph_quake(self, x, y):
        pen = self.pen
        trace = []
        for step in range(0, 26, 2):
            amp = 2 if step < 8 or step > 18 else 7
            if step % 4:
                yy = y + 13 + amp * math.sin(step / 2.0)
            else:
                yy = y + 13 - amp
            trace.append((x + step, yy))
        pen.line(trace, fill=COLOURS["red"], width=2)
        pen.line([(x + 3, y + 22), (x + 12, y + 18), (x + 20, y + 22)],
                 fill=(90, 60, 30), width=2)

    def _glyph_virus(self, x, y):
        pen = self.pen
        cx, cy = x + 13, y + 13
        for step in range(8):
            ang = step * math.pi / 4
            pen.line([(cx + 6 * math.cos(ang), cy + 6 * math.sin(ang)),
                      (cx + 10 * math.cos(ang), cy + 10 * math.sin(ang))],
                     fill=(150, 60, 60), width=2)
        pen.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(150, 60, 60))
        pen.ellipse([cx - 2, cy - 3, cx + 1, cy + 0], fill=(255, 255, 255))

    def _glyph_rugby(self, x, y):
        pen = self.pen
        pen.ellipse([x + 3, y + 7, x + 23, y + 19], fill=(120, 70, 30))
        pen.line([(x + 9, y + 8), (x + 9, y + 18)], fill=(255, 255, 255), width=1)
        pen.line([(x + 17, y + 8), (x + 17, y + 18)], fill=(255, 255, 255), width=1)
        pen.line([(x + 11, y + 12), (x + 15, y + 12)], fill=(255, 255, 255), width=1)

    # -- page sections ------------------------------------------------------
    def paint_masthead(self):
        pen = self.pen
        pen.rectangle([18, 10, 1006, 15], fill=COLOURS["ink"])
        self.centred("THE WORLD IN ONE DAY", typeface("sans-bold", 15), 22,
                     COLOURS["ink"])
        self.centred("Sunday 22 November 2026", typeface("serif-bold", 46), 40,
                     COLOURS["ink"])
        self.centred(
            "Iran hits US radars in Bahrain  •  Gaza aid car strike kills 3  •  "
            "Russian strikes kill 2 in Lviv",
            typeface("sans", 13), 92, COLOURS["muted"])
        pen.rectangle([18, 110, 1006, 112], fill=COLOURS["red"])

    def paint_stat_strip(self):
        pen = self.pen
        top = 120
        cell = 160
        for pos, stat in enumerate(BIG_NUMBERS):
            x = 18 + pos * (cell + 5)
            pen.rectangle([x, top - 4, x + cell, top + 44],
                          fill=COLOURS["panel"], outline=COLOURS["rule"], width=1)
            figure = typeface("serif-bold", 26)
            fw = pen.textlength(stat["figure"], font=figure)
            pen.text((x + (cell - fw) / 2, top), stat["figure"], font=figure,
                     fill=COLOURS["red"])
            cap = typeface("sans", 10)
            cw = pen.textlength(stat["caption"], font=cap)
            pen.text((x + (cell - cw) / 2, top + 32), stat["caption"], font=cap,
                     fill=COLOURS["ink"])

    def paint_region_bar(self):
        pen = self.pen
        y = 176
        x = 18
        font = typeface("sans-bold", 11)
        for entry in REGION_TALLY:
            pen.rectangle([x, y, x + 12, y + 12],
                          fill=REGION_HUES[entry["region"]])
            tag = "%s %d" % (entry["region"], entry["stories"])
            pen.text((x + 17, y - 1), tag, font=font, fill=COLOURS["ink"])
            x += 17 + int(pen.textlength(tag, font=font)) + 24
        pen.rectangle([18, 196, 1006, 198], fill=COLOURS["ink"])

    def paint_leads(self):
        pen = self.pen
        top, tall, wide = 206, 154, 322
        for pos, story in enumerate(LEAD_STORIES):
            x = 18 + pos * (wide + 10)
            self._lead_art(pos, x, top, wide, 58)
            pen.text((x, top + 64), story["kicker"],
                     font=typeface("sans-bold", 11), fill=COLOURS["red"])
            head_font = typeface("serif-bold", 19)
            lines = self._fit(story["headline"], head_font, wide, 2,
                              "lead-%d-head" % (pos + 1))
            y = top + 82
            for line in lines:
                pen.text((x, y), line, font=head_font, fill=COLOURS["ink"])
                y += 22
            deck_font = typeface("sans", 12)
            deck_lines = self._fit(story["deck"], deck_font, wide, 2,
                                   "lead-%d-deck" % (pos + 1))
            y = top + 126
            for line in deck_lines:
                pen.text((x, y), line, font=deck_font, fill=COLOURS["muted"])
                y += 15
            if pos < 2:
                pen.line([x + wide + 5, top, x + wide + 5, top + tall],
                         fill=COLOURS["rule"], width=1)
        pen.rectangle([18, 368, 1006, 370], fill=COLOURS["ink"])

    def paint_briefs(self):
        pen = self.pen
        x0, y0 = 18, 378
        cell_w, cell_h, gap_x, gap_y = 190, 88, 9, 8
        for idx, story in enumerate(BRIEF_STORIES):
            row, col = divmod(idx, 5)
            x = x0 + col * (cell_w + gap_x)
            y = y0 + row * (cell_h + gap_y)
            pen.text((x, y + 1), str(idx + 4), font=typeface("sans-bold", 11),
                     fill=COLOURS["red"])
            self._brief_icon(story["glyph"], x + 16, y)
            pen.text((x + 46, y + 6), story["kicker"],
                     font=typeface("sans-bold", 9), fill=COLOURS["muted"])
            head_font = typeface("sans-bold", 12)
            lines = self._fit(story["headline"], head_font, cell_w, 2,
                              "brief-%d-head" % (idx + 4))
            y2 = y + 28
            for line in lines:
                pen.text((x, y2), line, font=head_font, fill=COLOURS["ink"])
                y2 += 15
            deck_font = typeface("sans", 10)
            deck_lines = self._fit(story["deck"], deck_font, cell_w, 2,
                                   "brief-%d-deck" % (idx + 4))
            y3 = y2 + 1
            for line in deck_lines:
                pen.text((x, y3), line, font=deck_font, fill=COLOURS["muted"])
                y3 += 13
        pen.rectangle([18, 562, 1006, 564], fill=COLOURS["ink"])

    def paint_also_on(self):
        pen = self.pen
        y = 572
        pen.text((18, y), "ALSO ON SUNDAY — 23 MORE STORIES",
                 font=typeface("sans-bold", 13), fill=COLOURS["ink"])
        font = typeface("sans", 11)
        width = 312
        for idx, item in enumerate(EXTRA_STORIES):
            col = 0 if idx < 12 else 1
            row = idx if idx < 12 else idx - 12
            x = 18 + col * (width + 14)
            yy = y + 26 + row * 16
            text = "%d  %s (%s)" % (idx + 14, item["text"], item["source"])
            fitted = self._fit(text, font, width, 1, "also-%d" % (idx + 14))
            pen.text((x, yy), fitted[0], font=font, fill=COLOURS["ink"])

    def paint_date_check(self):
        pen = self.pen
        x0, y0 = 18, 800
        pen.rectangle([x0, y0, x0 + 638, y0 + 156], fill=COLOURS["box"],
                      outline=COLOURS["red"], width=2)
        pen.text((x0 + 12, y0 + 8), "DATE CHECK — WHAT WE LEFT OUT",
                 font=typeface("sans-bold", 13), fill=COLOURS["red"])
        pen.text((x0 + 12, y0 + 28),
                 "These big stories are NOT from Sunday 22 November, so they are not in this paper:",
                 font=typeface("sans", 10), fill=COLOURS["ink"])
        body = typeface("sans", 11)
        stamp = typeface("sans-bold", 11)
        for pos, entry in enumerate(LEFT_OUT):
            y = y0 + 50 + pos * 14
            pen.text((x0 + 12, y), "×  %s" % entry["story"], font=body,
                     fill=COLOURS["ink"])
            ww = pen.textlength(entry["date"], font=stamp)
            pen.text((x0 + 638 - 12 - ww, y), entry["date"], font=stamp,
                     fill=COLOURS["red"])

    def paint_map(self):
        pen = self.pen
        x0, y0, w, h = 668, 572, 338, 238
        pen.rectangle([x0, y0, x0 + w, y0 + h], fill=COLOURS["panel"],
                      outline=COLOURS["rule"], width=1)
        pen.text((x0 + 10, y0 + 8), "WHERE IT HAPPENED — PINS 1–13",
                 font=typeface("sans-bold", 12), fill=COLOURS["ink"])
        mx, my, mw, mh = x0 + 8, y0 + 30, w - 16, 176
        pen.rectangle([mx, my, mx + mw, my + mh], fill=COLOURS["sea"])
        for landmass in LANDMASSES:
            pts = [(mx + fx * mw, my + fy * mh) for fx, fy in landmass["points"]]
            pen.polygon(pts, fill=COLOURS["land"])
        pin_font = typeface("sans-bold", 7)
        for pin in PINS:
            px = mx + (pin["lon"] + 170) / 360.0 * mw + pin["dx"]
            py = my + (75 - pin["lat"]) / 130.0 * mh + pin["dy"]
            colour = COLOURS["red"] if pin["story"] <= 3 else (31, 78, 121)
            pen.ellipse([px - 6, py - 6, px + 6, py + 6], fill=colour,
                        outline=(255, 255, 255), width=1)
            tw = pen.textlength(str(pin["story"]), font=pin_font)
            pen.text((px - tw / 2, py - 5), str(pin["story"]), font=pin_font,
                     fill=(255, 255, 255))
        pen.text((x0 + 10, y0 + 212), "Pins 1–13 mark the drawn stories.",
                 font=typeface("sans", 10), fill=COLOURS["muted"])
        pen.text((x0 + 10, y0 + 226), "Red pins are the three leads.",
                 font=typeface("sans", 10), fill=COLOURS["muted"])

    def paint_promise(self):
        pen = self.pen
        x = 668
        y = 826
        pen.text((x, y), "OUR PROMISE", font=typeface("sans-bold", 11),
                 fill=COLOURS["red"])
        body = typeface("sans", 10)
        lines = self._fit(
            "Every story here happened, or was first reported, on Sunday "
            "22 November 2026 in at least one time zone. Claims are "
            "attributed; forecasts are flagged. Original drawings.",
            body, 338, 6, "promise")
        y += 18
        for line in lines:
            pen.text((x, y), line, font=body, fill=COLOURS["ink"])
            y += 13
        y += 6
        pen.text((x, y), "SOURCES", font=typeface("sans-bold", 11),
                 fill=COLOURS["red"])
        y += 16
        for line in self._fit("BBC, Reuters, AP, AFP, ANI, ESPN, USGS, ESA.",
                              body, 338, 2, "sources"):
            pen.text((x, y), line, font=body, fill=COLOURS["ink"])
            y += 13

    def paint_footer(self):
        pen = self.pen
        pen.rectangle([18, 968, 1006, 970], fill=COLOURS["ink"])
        self.centred(
            "THE WORLD IN ONE DAY  •  SUNDAY 22 NOVEMBER 2026  •  ONE DAY, EVERY CONTINENT",
            typeface("sans-bold", 11), 978, COLOURS["muted"])

    def render(self):
        """Paint every section, in page order, and return the image."""
        self.paint_masthead()
        self.paint_stat_strip()
        self.paint_region_bar()
        self.paint_leads()
        self.paint_briefs()
        self.paint_also_on()
        self.paint_date_check()
        self.paint_map()
        self.paint_promise()
        self.paint_footer()
        return self.img


if __name__ == "__main__":
    import hashlib
    import os
    import sys

    page = FrontPage()
    page.render()
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "entry.png")
    page.img.save(target, "PNG", optimize=True)
    with open(target, "rb") as handle:
        blob = handle.read()
    print("rendered", target, len(blob), "bytes")
    print("sha256", hashlib.sha256(blob).hexdigest())
    print("canvas", page.img.size, "mode", page.img.mode)
    if page.cut_notes:
        print("TRUNCATION-RISK: %d items" % len(page.cut_notes))
        for note in page.cut_notes:
            print("  -", note)
    else:
        print("TRUNCATION-RISK: none")
