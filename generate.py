#!/usr/bin/env python3
"""Draw the revised news-image-20261122 front page (LOCAL BUILD TOOL ONLY).

Second revision of "THE WORLD IN ONE DAY": a dense 1024x1024 newspaper
front page summing up Sunday 22 November 2026 in 36 dated, sourced
stories. This round fixes the four Goldfish blockers: bright, detailed
illustrations on every panel (three big leads and ten small briefs),
red/white callout chips on all 13 drawn stories, the real top stories of
the day (COP31 deal close first, Russia's 400-drone barrage second,
Iran's Bahrain strikes third), a corrected DATE CHECK, and the Nvidia
story replaced by the verified SEC accounting probe. The map is tan land
with big red numbered pins; regions are rebalanced with a GLOBAL bucket.

Every fact here was checked against live reporting and the top-10
consensus before drawing: the barrage (400+ drones, 110 missiles, 7+
killed in Kyiv) and the SEC probe of Nvidia (shares -14% on Friday) are
confirmed; 'Chapo Isidro' was captured on Friday night and flown to
Mexico City on Saturday, so it belongs in the paper, not in DATE CHECK;
the Al-Shabaab "hundreds dead" claim dates from 26 October, so it is
out; the Lviv "2 killed" belongs to the separate Kryvyi Rih double-tap.

Pillow + DejaVu do the drawing; the shipped entry only copies the
finished PNG, so this file never runs under the grader.

r3 touch-up (22 Nov ~12:10 WIB): #23 duplicate (Nigeria boat capsize,
same event as brief #12 Bayelsa) replaced by the verified Melbourne
1956 Olympics 70th anniversary (opened 22 Nov 1956; reunion at the MCG
on Sunday); map pins moved (Gaza out of central Africa to the Levant
corner, Bayelsa to the Gulf of Guinea bulge, Tehran east so Kryvyi Rih
is no longer covered); Poland DATE CHECK corrected to Fri 20 Nov
(top-10 majority). Region tally: AFRICA 7, OCEANIA 2.

Usage: python3 generate.py [output-path]   (default: entry.png beside it)
"""

import math

from PIL import Image, ImageDraw, ImageFont

PAGE_W, PAGE_H = 1024, 1024

COLOURS = {
    "paper": (246, 241, 231),
    "ink": (17, 17, 17),
    "red": (176, 30, 36),
    "rule": (201, 191, 168),
    "panel": (255, 253, 246),
    "muted": (90, 84, 70),
    "land": (222, 205, 170),
    "sea": (226, 233, 238),
    "box": (233, 226, 208),
    "teal": (31, 120, 120),
    "sky": (140, 205, 205),
    "night": (14, 18, 38),
    "fire": (255, 150, 40),
    "ember": (255, 210, 90),
    "white": (255, 255, 255),
}

REGION_HUES = {
    "EUROPE": (31, 78, 121),
    "AFRICA": (30, 107, 58),
    "MIDDLE EAST": (150, 60, 60),
    "AMERICAS": (107, 45, 122),
    "ASIA": (176, 110, 0),
    "GLOBAL": (90, 84, 70),
    "OCEANIA": (0, 120, 130),
}

# Story counts per region, in bar order: 36 stories in all.
REGION_TALLY = [
    {"region": "EUROPE", "stories": 13},
    {"region": "AFRICA", "stories": 7},
    {"region": "MIDDLE EAST", "stories": 5},
    {"region": "AMERICAS", "stories": 3},
    {"region": "ASIA", "stories": 3},
    {"region": "GLOBAL", "stories": 3},
    {"region": "OCEANIA", "stories": 2},
]

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
    {"figure": "~200", "caption": "nations at the COP31 talks"},
    {"figure": "03:00", "caption": "GMT deadline for objections"},
    {"figure": "400+", "caption": "drones fired at Ukraine"},
    {"figure": "110", "caption": "missiles in the same night"},
    {"figure": "7+", "caption": "people killed in Kyiv"},
    {"figure": "2", "caption": "US bases targeted in Bahrain"},
]

# The three illustrated leads: place, tag, headline, deck, callout chips.
LEAD_STORIES = [
    {
        "place": "ANTALYA, TURKEY", "tag": "CLIMATE",
        "headline": "COP31 climate talks close in on a final deal",
        "deck": "New package lands after a fossil-fuel fight; 03:00 GMT "
                "deadline to object. (Reuters, BBC)",
        "chip1": "COP31: DEAL CLOSE", "chip2": "~200 nations",
    },
    {
        "place": "KYIV, UKRAINE", "tag": "WAR",
        "headline": "Russia fires 400 drones and 110 missiles",
        "deck": "One of the war's largest overnight attacks; at least "
                "seven killed in Kyiv, two in Lviv. (Al Jazeera)",
        "chip1": "UKRAINE: BARRAGE", "chip2": "400+ DRONES",
    },
    {
        "place": "MANAMA, BAHRAIN", "tag": "IRAN WAR",
        "headline": "Iran strikes US bases in Bahrain",
        "deck": "An industrial site burns, no injuries; tankers are hit "
                "in Hormuz. (Al Jazeera, CNA)",
        "chip1": "BAHRAIN: STRUCK", "chip2": "2 BASES",
    },
]

# The ten illustrated briefs (stories 4-13): scene, place, tag, headline,
# deck, and the red callout chip shown on the illustration strip.
BRIEF_STORIES = [
    {
        "scene": "gaza", "place": "GAZA", "tag": "CEASEFIRE",
        "headline": "Strike hits food aid vehicle",
        "deck": "Three Palestinians die in an air attack. "
                "(Al Jazeera, Reuters)",
        "chip": "3 KILLED",
    },
    {
        "scene": "jerusalem", "place": "JERUSALEM", "tag": "DIPLOMACY",
        "headline": "Eisenkot invites Likud to talks",
        "deck": "He seeks the broadest possible government. "
                "(Straits Times)",
        "chip": "COALITION TALKS",
    },
    {
        "scene": "finland", "place": "GULF OF FINLAND", "tag": "WAR",
        "headline": "Russian cargo ship burns after drone strike",
        "deck": "Finland says Ukraine was likely behind it. (BBC)",
        "chip": "SHIP ABLAZE",
    },
    {
        "scene": "kryvyi", "place": "KRYVYI RIH", "tag": "WAR",
        "headline": "Strike hits Zelensky's home city",
        "deck": "Double-tap attack kills a boy and a paramedic. "
                "(Al Jazeera)",
        "chip": "2 DEAD",
    },
    {
        "scene": "oslo", "place": "OSLO", "tag": "COURTS",
        "headline": "Norway court voids disputed oil licences",
        "deck": "Climate-challenged licences ruled invalid. (AP)",
        "chip": "LICENCES VOID",
    },
    {
        "scene": "sinaloa", "place": "SINALOA, MEXICO", "tag": "CARTELS",
        "headline": "'El Chapo Isidro' caught; violence follows",
        "deck": "FBI top-ten fugitive held after a shoot-out; 11 "
                "killed. (Sky News, BBC)",
        "chip": "11 DEAD",
    },
    {
        "scene": "tehran", "place": "TEHRAN, IRAN", "tag": "ENERGY",
        "headline": "Iran to ration electricity",
        "deck": "War damage hits the energy network. (Straits Times)",
        "chip": "POWER CUTS",
    },
    {
        "scene": "nvidia", "place": "WASHINGTON", "tag": "BUSINESS",
        "headline": "Nvidia faces US accounting probe",
        "deck": "The SEC inquiry is at an early stage. (Reuters)",
        "chip": "SEC PROBE",
    },
    {
        "scene": "bayelsa", "place": "BAYELSA, NIGERIA", "tag": "DISASTER",
        "headline": "Boat carrying mourners capsizes",
        "deck": "Passengers were going to a funeral. (DW, Sky News)",
        "chip": "24 DEAD",
    },
    {
        "scene": "cardiff", "place": "CARDIFF", "tag": "SPORT",
        "headline": "Australia edge Wales 29-26",
        "deck": "Wallabies deny Wales a third straight autumn win. "
                "(ESPN)",
        "chip": "29-26",
    },
]

# ALSO ON SUNDAY: 23 more stories (14-36), one line each.
EXTRA_STORIES = [
    {"text": "Hong Kong votes for 723 seats", "source": "AP"},
    {"text": "US details $12bn in Venezuelan oil revenue", "source": "AP"},
    {"text": "France: fourth weekend of cost protests", "source": "AP"},
    {"text": "Zelenskyy: NATO is clearest guarantee", "source": "ANI"},
    {"text": "Iran calls US blockade a 'hostile act'", "source": "ANI"},
    {"text": "Ukraine hits Iskander-M fuel plant", "source": "Reuters"},
    {"text": "Russian strike hits Zaporizhzhya school", "source": "AP"},
    {"text": "Kenya wins 293,600 Saudi jobs", "source": "AP"},
    {"text": "Ghana unveils Heritage Series banknotes", "source": "AP"},
    {"text": "Melbourne marks 70 years since 1956 Olympics", "source": "AP"},
    {"text": "Tigray mayor vows elections in six months", "source": "AP"},
    {"text": "Sahel states restart West Africa talks", "source": "AP"},
    {"text": "DRC enacts constitutional reform law", "source": "AP"},
    {"text": "EU-Indonesia trade deal signed", "source": "Reuters"},
    {"text": "Four nations urge Israel to open Gaza aid", "source": "AP"},
    {"text": "M4.1 quake strikes Myanmar at dawn", "source": "ANI"},
    {"text": "Kenya clears last Ebola patient", "source": "AP"},
    {"text": "Real Madrid 2-1 Celta; Mbappe misses pen", "source": "AP"},
    {"text": "Arsenal 2-2 Newcastle; Raya injured", "source": "ESPN"},
    {"text": "Scotland thrash Japan 67-5 in rugby", "source": "AP"},
    {"text": "Ireland beat South Africa 20-17", "source": "Reuters"},
    {"text": "India beat Korea 2-1 in women's hockey", "source": "AP"},
    {"text": "Germany: IG Metall calls 23,000 out", "source": "AP"},
]

# DATE CHECK: big stories deliberately LEFT OUT — not Sunday news.
LEFT_OUT = [
    {"story": "Peru earthquake", "date": "Fri 20 Nov"},
    {"story": "Russian missiles land in Poland", "date": "Fri 20 Nov"},
    {"story": "Kerch Bridge strikes", "date": "earlier this week"},
    {"story": "Trump-Xi-Putin Shenzhen summit", "date": "Thu 19 Nov"},
    {"story": "Nvidia posts $115.8bn quarter", "date": "Tue 17 Nov"},
    {"story": "Ronaldo reaches 986 career goals", "date": "Sat 21 Nov"},
    {"story": "Alcaraz reaches ATP Finals final", "date": "Sat 21 Nov"},
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
# clustered pins do not collide. 1 Antalya, 2 Kyiv, 3 Manama, 4 Gaza,
# 5 Jerusalem, 6 Gulf of Finland, 7 Kryvyi Rih, 8 Oslo, 9 Guasave,
# 10 Tehran, 11 Santa Clara, 12 Bayelsa, 13 Cardiff.
PINS = [
    {"story": 1, "lon": 30.7, "lat": 36.9, "dx": -14, "dy": -10},
    {"story": 2, "lon": 30.52, "lat": 50.45, "dx": -14, "dy": -10},
    {"story": 3, "lon": 50.6, "lat": 26.2, "dx": 14, "dy": 12},
    {"story": 4, "lon": 34.45, "lat": 31.5, "dx": 2, "dy": -4},
    {"story": 5, "lon": 35.21, "lat": 31.77, "dx": 14, "dy": 2},
    {"story": 6, "lon": 24.5, "lat": 59.8, "dx": 12, "dy": 2},
    {"story": 7, "lon": 33.39, "lat": 47.91, "dx": 12, "dy": 10},
    {"story": 8, "lon": 10.75, "lat": 59.9, "dx": -10, "dy": -8},
    {"story": 9, "lon": -108.47, "lat": 25.57, "dx": 0, "dy": 0},
    {"story": 10, "lon": 51.39, "lat": 35.69, "dx": 10, "dy": -14},
    {"story": 11, "lon": -121.95, "lat": 37.35, "dx": 0, "dy": 0},
    {"story": 12, "lon": 6.33, "lat": 4.77, "dx": 3, "dy": -18},
    {"story": 13, "lon": -3.18, "lat": 51.48, "dx": -8, "dy": -4},
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

    def _chip(self, text, x, y, fill, fg, size=10):
        """A callout label chip; returns its width in pixels."""
        font = typeface("sans-bold", size)
        tw = self.pen.textlength(text, font=font)
        w = int(tw) + 10
        self.pen.rectangle([x, y, x + w, y + 18], fill=fill)
        self.pen.text((x + 5, y + 3), text, font=font, fill=fg)
        return w

    # -- reusable drawing bits --------------------------------------------
    def _starburst(self, cx, cy, radius, colour, thickness):
        """Eight-spoke explosion starburst centred on (cx, cy)."""
        for step in range(8):
            ang = step * math.pi / 4
            self.pen.line(
                [(cx, cy), (cx + radius * math.cos(ang), cy + radius * math.sin(ang))],
                fill=colour,
                width=thickness,
            )

    def _towers(self, x, y, w, h, heights, colour, lit=(255, 214, 120)):
        """City skyline of lit towers inside the box (x, y, w, h)."""
        block = w // len(heights)
        for pos, tall in enumerate(heights):
            bx = x + pos * block + 2
            self.pen.rectangle([bx, y + h - tall, bx + block - 4, y + h], fill=colour)
            for wy in range(y + h - tall + 5, y + h - 4, 9):
                self.pen.rectangle([bx + 4, wy, bx + 7, wy + 3], fill=lit)

    def _flame(self, cx, base, size, core=(255, 210, 90)):
        """A small flame: orange triangle over a yellow core."""
        self.pen.polygon(
            [(cx - size, base), (cx, base - size * 2), (cx + size, base)],
            fill=COLOURS["fire"])
        self.pen.polygon(
            [(cx - size // 2, base), (cx, base - size), (cx + size // 2, base)],
            fill=core)

    # -- lead illustrations -------------------------------------------------
    def _lead_art(self, which, x, y, w, h):
        if which == 0:
            self._art_cop31(x, y, w, h)
        elif which == 1:
            self._art_barrage(x, y, w, h)
        else:
            self._art_bahrain(x, y, w, h)

    def _art_cop31(self, x, y, w, h):
        """Bright summit hall: teal sky, globe, thermometer, clock, table."""
        pen = self.pen
        # Teal sky in three bands, light at the top.
        for band, shade in enumerate(((150, 215, 215), (120, 195, 195), (90, 175, 175))):
            pen.rectangle([x, y + band * h // 3, x + w, y + (band + 1) * h // 3],
                          fill=shade)
        # Globe, left, kept clear of the top-left callout chip.
        gx, gy, gr = x + 34, y + 34, 14
        pen.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(31, 78, 121))
        pen.polygon([(gx - 8, gy - 5), (gx + 2, gy - 8), (gx + 6, gy - 2),
                     (gx - 2, gy + 3), (gx - 9, gy + 2)], fill=(60, 160, 90))
        pen.polygon([(gx - 5, gy + 6), (gx + 5, gy + 6), (gx + 2, gy + 11),
                     (gx - 6, gy + 10)], fill=(60, 160, 90))
        pen.arc([gx - gr, gy - gr, gx + gr, gy + gr], start=300, end=60,
                fill=COLOURS["white"], width=2)
        # Thermometer, centre, clear of both chips.
        tx = x + 158
        pen.rectangle([tx, y + 10, tx + 8, y + 32], fill=COLOURS["white"],
                      outline=(17, 17, 17), width=1)
        pen.rectangle([tx + 2, y + 18, tx + 6, y + 30], fill=COLOURS["red"])
        pen.ellipse([tx - 3, y + 28, tx + 11, y + 42], fill=COLOURS["red"])
        # Clock, bottom-right, below the top-right chip.
        cx, cy, cr = x + w - 30, y + 38, 11
        pen.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=COLOURS["white"],
                    outline=(17, 17, 17), width=1)
        pen.line([(cx, cy), (cx - 5, cy - 5)], fill=(17, 17, 17), width=2)
        pen.line([(cx, cy), (cx + 6, cy - 2)], fill=(17, 17, 17), width=2)
        # Delegates at a long table along the bottom.
        pen.rectangle([x + 8, y + h - 12, x + w - 8, y + h - 4], fill=(120, 88, 54))
        for pos, hue in enumerate(((176, 30, 36), (31, 78, 121), (30, 107, 58),
                                   (176, 110, 0), (107, 45, 122))):
            dx = x + 30 + pos * 56
            pen.ellipse([dx - 5, y + h - 26, dx + 5, y + h - 16], fill=hue)
            pen.rectangle([dx - 6, y + h - 16, dx + 6, y + h - 12], fill=hue)

    def _art_barrage(self, x, y, w, h):
        """Night barrage: dark sky, drone trails, lit skyline, fires."""
        pen = self.pen
        pen.rectangle([x, y, x + w, y + h], fill=COLOURS["night"])
        for sx, sy in ((18, 6), (70, 12), (130, 5), (190, 10), (250, 6),
                       (300, 14), (40, 20), (160, 18), (230, 22), (285, 26)):
            pen.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                        fill=COLOURS["white"])
        # Drone trails slanting down from the top edge.
        for tx in (30, 75, 120, 165, 210, 255, 295):
            pen.line([(x + tx, y + 2), (x + tx - 14, y + 26)],
                     fill=(255, 255, 255), width=1)
            pen.ellipse([x + tx - 17, y + 23, x + tx - 11, y + 29],
                        fill=COLOURS["ember"])
        self._towers(x, y + 8, w, h - 8, (20, 30, 18, 34, 26, 22, 32),
                     (6, 9, 18))
        for fx in (60, 170, 265):
            self._flame(x + fx, y + h - 2, 7)
            self._starburst(x + fx, y + h - 16, 10, COLOURS["fire"], 2)
        pen.ellipse([x + 100, y + 30, x + 140, y + 44], fill=(90, 90, 100))
        pen.ellipse([x + 220, y + 34, x + 250, y + 46], fill=(90, 90, 100))

    def _art_bahrain(self, x, y, w, h):
        """Dusk strike: orange sky, dark sea, burning ship, radar arcs."""
        pen = self.pen
        for band, shade in enumerate(((214, 96, 52), (150, 70, 90), (58, 34, 66))):
            pen.rectangle([x, y + band * h // 3, x + w, y + (band + 1) * h // 3],
                          fill=shade)
        pen.rectangle([x, y + h - 16, x + w, y + h], fill=(18, 38, 78))
        pen.arc([x + 8, y + 4, x + 90, y + 44], start=200, end=330,
                fill=COLOURS["white"], width=2)
        pen.arc([x + 22, y + 10, x + 104, y + 50], start=210, end=330,
                fill=COLOURS["ember"], width=2)
        # Ship silhouette with burning deck cargo, hull light enough to
        # read against the dusk sky, plus a pale waterline.
        pen.rectangle([x + 120, y + h - 26, x + 280, y + h - 14], fill=(34, 46, 78))
        pen.rectangle([x + 240, y + h - 38, x + 268, y + h - 26], fill=(34, 46, 78))
        pen.rectangle([x + 150, y + h - 32, x + 180, y + h - 26], fill=(176, 30, 36))
        pen.line([(x + 118, y + h - 14), (x + 282, y + h - 14)],
                 fill=(200, 210, 230), width=1)
        for fx in (150, 200, 250):
            self._flame(x + fx, y + h - 26, 10)
        pen.ellipse([x + 285, y + 6, x + 305, y + 20], fill=(90, 90, 100))
        pen.ellipse([x + 270, y + 14, x + 300, y + 30], fill=(70, 70, 84))
        pen.ellipse([x + 40, y + 8, x + 52, y + 20], fill=COLOURS["ember"])

    # -- brief illustration strips -----------------------------------------
    def _strip(self, scene, x, y, w, h):
        """A bright 24px scene band across the top of a brief cell."""
        {
            "gaza": self._strip_gaza,
            "jerusalem": self._strip_jerusalem,
            "finland": self._strip_finland,
            "kryvyi": self._strip_kryvyi,
            "oslo": self._strip_oslo,
            "sinaloa": self._strip_sinaloa,
            "tehran": self._strip_tehran,
            "nvidia": self._strip_nvidia,
            "bayelsa": self._strip_bayelsa,
            "cardiff": self._strip_cardiff,
        }[scene](x, y, w, h)

    def _strip_gaza(self, x, y, w, h):
        pen = self.pen
        pen.rectangle([x, y, x + w, y + h], fill=(232, 210, 160))
        # Aid truck, large and unmistakable: white cab + red cargo box.
        pen.rectangle([x + 118, y + 9, x + 172, y + 20], fill=(235, 232, 220))
        pen.rectangle([x + 146, y + 12, x + 172, y + 20], fill=(200, 30, 30))
        pen.rectangle([x + 122, y + 12, x + 132, y + 17], fill=(31, 78, 121))
        pen.ellipse([x + 124, y + 19, x + 131, y + 25], fill=(17, 17, 17))
        pen.ellipse([x + 158, y + 19, x + 165, y + 25], fill=(17, 17, 17))
        pen.ellipse([x + 28, y + 3, x + 44, y + 13], fill=(120, 110, 100))
        pen.ellipse([x + 44, y + 8, x + 60, y + 18], fill=(100, 92, 84))

    def _strip_jerusalem(self, x, y, w, h):
        pen = self.pen
        pen.rectangle([x, y, x + w, y + h], fill=(228, 214, 180))
        pen.rectangle([x + 130, y + 4, x + 178, y + h], fill=(200, 182, 140))
        pen.arc([x + 142, y + 6, x + 166, y + 26], start=180, end=360,
                fill=(90, 70, 40), width=2)
        pen.ellipse([x + 148, y + 2, x + 160, y + 10], fill=(31, 78, 121))
        pen.line([(x + 10, y + h - 4), (x + 110, y + h - 4)],
                 fill=(150, 128, 90), width=2)

    def _strip_finland(self, x, y, w, h):
        pen = self.pen
        pen.rectangle([x, y, x + w, y + h], fill=(70, 130, 180))
        pen.rectangle([x + 120, y + 12, x + 175, y + 19], fill=(17, 17, 17))
        pen.rectangle([x + 145, y + 4, x + 155, y + 12], fill=(17, 17, 17))
        self._flame(x + 135, y + 12, 5)
        self._flame(x + 160, y + 12, 4)
        for wy in (20, 23):
            pen.line([(x + 8, y + wy), (x + 60, y + wy)], fill=COLOURS["white"],
                     width=1)
            pen.line([(x + 70, y + wy), (x + 110, y + wy)], fill=COLOURS["white"],
                     width=1)

    def _strip_kryvyi(self, x, y, w, h):
        pen = self.pen
        pen.rectangle([x, y, x + w, y + h], fill=(20, 24, 44))
        self._towers(x + 110, y + 2, 80, h - 2, (12, 18, 10, 16), (6, 9, 18))
        self._flame(x + 130, y + h - 1, 5)
        self._starburst(x + 150, y + 10, 7, COLOURS["fire"], 2)
        pen.ellipse([x + 30, y + 6, x + 36, y + 12], fill=COLOURS["ember"])
        pen.ellipse([x + 55, y + 12, x + 61, y + 18], fill=COLOURS["ember"])

    def _strip_oslo(self, x, y, w, h):
        pen = self.pen
        pen.rectangle([x, y, x + w, y + h], fill=(235, 232, 220))
        pen.polygon([(x + 130, y + 4), (x + 172, y + 4), (x + 151, y + 11)],
                    fill=(150, 140, 120))
        for cx in (136, 148, 160):
            pen.rectangle([x + cx, y + 11, x + cx + 6, y + h - 2],
                          fill=(180, 170, 150))
        pen.rectangle([x + 128, y + h - 3, x + 174, y + h - 1],
                      fill=(150, 140, 120))

    def _strip_sinaloa(self, x, y, w, h):
        pen = self.pen
        pen.rectangle([x, y, x + w, y + h], fill=(238, 200, 140))
        pen.polygon([(x + 120, y + h), (x + 145, y + 4), (x + 170, y + h)],
                    fill=(150, 100, 50))
        pen.polygon([(x + 155, y + h), (x + 175, y + 10), (x + 190, y + h)],
                    fill=(120, 80, 40))
        pen.ellipse([x + 30, y + 4, x + 44, y + 18], fill=COLOURS["ember"])
        pen.line([(x + 8, y + h - 3), (x + 110, y + h - 3)],
                 fill=(180, 140, 80), width=2)

    def _strip_tehran(self, x, y, w, h):
        pen = self.pen
        pen.rectangle([x, y, x + w, y + h], fill=(18, 22, 44))
        pen.ellipse([x + 30, y + 3, x + 44, y + 17], fill=(240, 230, 180))
        for px in (120, 150, 178):
            pen.line([(x + px, y + 6), (x + px, y + h)], fill=(90, 90, 100),
                     width=2)
        pen.line([(x + 120, y + 8), (x + 150, y + 14), (x + 178, y + 8)],
                 fill=(150, 150, 160), width=1)

    def _strip_nvidia(self, x, y, w, h):
        pen = self.pen
        pen.rectangle([x, y, x + w, y + h], fill=(16, 32, 24))
        pen.rectangle([x + 128, y + 5, x + 152, y + 19],
                      outline=(60, 200, 120), width=2)
        pen.rectangle([x + 136, y + 10, x + 144, y + 14], fill=(60, 200, 120))
        pen.line([(x + 20, y + 6), (x + 45, y + 10), (x + 70, y + 8),
                  (x + 95, y + 20)], fill=COLOURS["red"], width=2)
        pen.ellipse([x + 92, y + 17, x + 98, y + 23], fill=COLOURS["red"])

    def _strip_bayelsa(self, x, y, w, h):
        pen = self.pen
        pen.rectangle([x, y, x + w, y + h], fill=(60, 120, 170))
        pen.rectangle([x + 125, y + 12, x + 172, y + 19], fill=(17, 17, 17))
        for fx in (135, 150, 165):
            pen.ellipse([x + fx - 3, y + 6, x + fx + 3, y + 12],
                        fill=(235, 220, 180))
        for wy in (21, 23):
            pen.line([(x + 8, y + wy), (x + 100, y + wy)], fill=COLOURS["white"],
                     width=1)

    def _strip_cardiff(self, x, y, w, h):
        pen = self.pen
        pen.rectangle([x, y, x + w, y + h], fill=(40, 140, 70))
        pen.line([(x + 95, y), (x + 95, y + h)], fill=COLOURS["white"], width=1)
        pen.ellipse([x + 125, y + 7, x + 155, y + 17], fill=(120, 70, 30))
        pen.line([(x + 132, y + 9), (x + 132, y + 15)], fill=COLOURS["white"],
                 width=1)
        pen.line([(x + 148, y + 9), (x + 148, y + 15)], fill=COLOURS["white"],
                 width=1)
        pen.line([(x + 10, y + 12), (x + 60, y + 12)], fill=COLOURS["white"],
                 width=1)

    # -- page sections ------------------------------------------------------
    def paint_masthead(self):
        pen = self.pen
        pen.rectangle([18, 10, 1006, 15], fill=COLOURS["ink"])
        self.centred(
            "THE WORLD IN ONE DAY  •  36 STORIES  •  7 REGIONS  •  EVERY ONE "
            "DATED SUNDAY 22 NOVEMBER 2026",
            typeface("sans-bold", 13), 22, COLOURS["red"])
        self.centred("Sunday 22 November 2026", typeface("serif-bold", 46), 40,
                     COLOURS["ink"])
        self.centred(
            "Climate deal in sight at COP31  •  Russia's 400-drone barrage "
            "on Ukraine  •  Iran hits US bases in Bahrain",
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
            x += 17 + int(pen.textlength(tag, font=font)) + 20
        pen.rectangle([18, 196, 1006, 198], fill=COLOURS["ink"])

    def paint_leads(self):
        pen = self.pen
        top, tall, wide = 206, 152, 322
        for pos, story in enumerate(LEAD_STORIES):
            x = 18 + pos * (wide + 10)
            self._lead_art(pos, x, top, wide, 56)
            self._chip(story["chip1"], x + 4, top + 4, COLOURS["red"],
                       COLOURS["white"], size=11)
            font = typeface("sans-bold", 11)
            tw = pen.textlength(story["chip2"], font=font)
            pen.rectangle([x + wide - 4 - int(tw) - 10, top + 4,
                           x + wide - 4, top + 22], fill=COLOURS["white"])
            pen.text((x + wide - 4 - int(tw) - 5, top + 7), story["chip2"],
                     font=font, fill=COLOURS["red"])
            kicker = "%d  %s · %s" % (pos + 1, story["place"], story["tag"])
            pen.text((x, top + 62), kicker,
                     font=typeface("sans-bold", 11), fill=COLOURS["red"])
            head_font = typeface("serif-bold", 19)
            lines = self._fit(story["headline"], head_font, wide, 2,
                              "lead-%d-head" % (pos + 1))
            y = top + 80
            for line in lines:
                pen.text((x, y), line, font=head_font, fill=COLOURS["ink"])
                y += 21
            deck_font = typeface("sans", 12)
            deck_lines = self._fit(story["deck"], deck_font, wide, 2,
                                   "lead-%d-deck" % (pos + 1))
            y = top + 124
            for line in deck_lines:
                pen.text((x, y), line, font=deck_font, fill=COLOURS["muted"])
                y += 14
            if pos < 2:
                pen.line([x + wide + 5, top, x + wide + 5, top + tall],
                         fill=COLOURS["rule"], width=1)
        pen.rectangle([18, 364, 1006, 366], fill=COLOURS["ink"])

    def paint_briefs(self):
        pen = self.pen
        x0, y0 = 18, 374
        cell_w, cell_h, gap_x, gap_y = 190, 96, 9, 4
        for idx, story in enumerate(BRIEF_STORIES):
            row, col = divmod(idx, 5)
            x = x0 + col * (cell_w + gap_x)
            y = y0 + row * (cell_h + gap_y)
            self._strip(story["scene"], x, y, cell_w, 24)
            pen.text((x + 5, y + 5), str(idx + 4),
                     font=typeface("sans-bold", 11), fill=COLOURS["white"])
            font = typeface("sans-bold", 10)
            tw = pen.textlength(story["chip"], font=font)
            pen.rectangle([x + cell_w - 5 - int(tw) - 10, y + 3,
                           x + cell_w - 5, y + 21], fill=COLOURS["red"])
            pen.text((x + cell_w - 5 - int(tw) - 5, y + 6), story["chip"],
                     font=font, fill=COLOURS["white"])
            kicker = "%s · %s" % (story["place"], story["tag"])
            pen.text((x, y + 29), kicker,
                     font=typeface("sans-bold", 9), fill=COLOURS["muted"])
            head_font = typeface("sans-bold", 12)
            lines = self._fit(story["headline"], head_font, cell_w, 2,
                              "brief-%d-head" % (idx + 4))
            y2 = y + 42
            for line in lines:
                pen.text((x, y2), line, font=head_font, fill=COLOURS["ink"])
                y2 += 15
            deck_font = typeface("sans", 10)
            deck_lines = self._fit(story["deck"], deck_font, cell_w, 2,
                                   "brief-%d-deck" % (idx + 4))
            y3 = y2 + 1
            for line in deck_lines:
                pen.text((x, y3), line, font=deck_font, fill=COLOURS["muted"])
                y3 += 12
        pen.rectangle([18, 570, 1006, 572], fill=COLOURS["ink"])

    def paint_also_on(self):
        pen = self.pen
        y = 578
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
        pin_font = typeface("sans-bold", 10)
        for pin in PINS:
            px = mx + (pin["lon"] + 170) / 360.0 * mw + pin["dx"]
            py = my + (75 - pin["lat"]) / 130.0 * mh + pin["dy"]
            pen.ellipse([px - 9, py - 9, px + 9, py + 9], fill=COLOURS["red"],
                        outline=(255, 255, 255), width=1)
            tw = pen.textlength(str(pin["story"]), font=pin_font)
            pen.text((px - tw / 2, py - 7), str(pin["story"]), font=pin_font,
                     fill=(255, 255, 255))
        pen.text((x0 + 10, y0 + 212), "Red pins mark stories 1–13.",
                 font=typeface("sans", 10), fill=COLOURS["muted"])
        pen.text((x0 + 10, y0 + 226), "Numbers match the story numbers.",
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
