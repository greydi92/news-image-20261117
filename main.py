#!/usr/bin/env python3
"""Draws one front-page infographic summing up the world news of
Tuesday 17 November 2026, and writes it to /output/entry.png.

Pure standard library: the picture is drawn pixel by pixel with a
small built-in 5x7 bitmap font, then encoded as PNG by hand
(zlib + struct). No network, no timestamps, no randomness, so two
runs produce byte-identical output.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)   # warm newsprint
INK = (26, 36, 51)        # dark navy ink
WHITE = (255, 255, 255)
NAVY = (31, 62, 96)       # masthead band
RED = (178, 44, 36)       # alert red
BLUE = (43, 108, 163)     # story blue
GOLD = (201, 138, 32)     # warm gold
TEAL = (38, 122, 102)     # teal
GREY = (110, 116, 122)
LIGHT = (232, 226, 208)   # panel divider
ORANGE = (214, 106, 28)
SKY = (140, 190, 220)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows; each row is a 5-bit value (bit 4 = left pixel).
# Only capitals, digits and common punctuation: all text is uppercased.
def _g(rows):
    out = []
    for r in rows:
        v = 0
        for ch in r:
            v = (v << 1) | (1 if ch == "#" else 0)
        out.append(v)
    return tuple(out)

FONT = {
    "A": _g([".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"]),
    "B": _g(["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."]),
    "C": _g([".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."]),
    "D": _g(["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."]),
    "E": _g(["#####", "#....", "#....", "####.", "#....", "#....", "#####"]),
    "F": _g(["#####", "#....", "#....", "####.", "#....", "#....", "#...."]),
    "G": _g([".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"]),
    "H": _g(["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"]),
    "I": _g([".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."]),
    "J": _g(["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."]),
    "K": _g(["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"]),
    "L": _g(["#....", "#....", "#....", "#....", "#....", "#....", "#####"]),
    "M": _g(["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"]),
    "N": _g(["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"]),
    "O": _g([".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."]),
    "P": _g(["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."]),
    "Q": _g([".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"]),
    "R": _g(["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"]),
    "S": _g([".####", "#....", "#....", ".###.", "....#", "....#", "####."]),
    "T": _g(["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."]),
    "U": _g(["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."]),
    "V": _g(["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."]),
    "W": _g(["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"]),
    "X": _g(["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"]),
    "Y": _g(["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."]),
    "Z": _g(["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"]),
    "0": _g([".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."]),
    "1": _g(["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."]),
    "2": _g([".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"]),
    "3": _g(["#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."]),
    "4": _g(["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."]),
    "5": _g(["#####", "#....", "####.", "....#", "....#", "#...#", ".###."]),
    "6": _g(["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."]),
    "7": _g(["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."]),
    "8": _g([".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."]),
    "9": _g([".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."]),
    " ": _g(["....."] * 7),
    ".": _g([".....", ".....", ".....", ".....", ".....", ".##..", ".##.."]),
    ",": _g([".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."]),
    ":": _g([".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."]),
    ";": _g([".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."]),
    "!": _g(["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."]),
    "?": _g([".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."]),
    "'": _g(["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."]),
    "-": _g([".....", ".....", ".....", ".###.", ".....", ".....", "....."]),
    "/": _g(["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."]),
    "(": _g(["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."]),
    ")": _g([".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."]),
    "&": _g([".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"]),
    "%": _g(["##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#.##.", "#..##"]),
    "+": _g([".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."]),
    "=": _g([".....", ".....", "#####", ".....", "#####", ".....", "....."]),
}

# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for t in range(thick):
                self.put(x0 + t, y0, c)
                self.put(x0, y0 + t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.put(xx, yy, c)
                else:
                    if abs(d2 - r * r) <= r * 2:
                        self.put(xx, yy, c)

    def tri(self, pts, c):
        # filled triangle via scanlines
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            inter = []
            for i in range(3):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % 3]
                if y0 == y1:
                    continue
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    inter.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
            if len(inter) >= 2:
                a, b = int(min(inter)), int(max(inter))
                for xx in range(a, b + 1):
                    self.put(xx, yy, c)

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s.upper()) * 6 * scale - scale

    def wrap(self, s, max_w, scale):
        words = s.upper().split(" ")
        lines, cur = [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if self.text_w(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


cv = Canvas(W, H, PAPER)

# ------------------------------------------------------------------ helpers
def panel(x, y, w, h, tag, tag_c):
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, 4, tag_c)          # top accent bar
    cv.rect(x, y, w, 2, INK)           # frame
    cv.rect(x, y + h - 2, w, 2, INK)
    cv.rect(x, y, 2, h, INK)
    cv.rect(x + w - 2, y, 2, h, INK)
    # tag chip
    tw = cv.text_w(tag, 2) + 16
    cv.rect(x + 14, y + 14, tw, 24, tag_c)
    cv.text(x + 22, y + 19, tag, 2, WHITE)


def headline_block(x, y, w, head, body, hscale, bscale, head_c=INK):
    lines = cv.wrap(head, w, hscale)
    yy = y
    for ln in lines:
        cv.text(x, yy, ln, hscale, head_c)
        yy += 8 * hscale
    yy += 4
    for ln in cv.wrap(body, w, bscale):
        cv.text(x, yy, ln, bscale, (58, 66, 76))
        yy += 9 * bscale
    return yy


# -------------------------------------------------------------- pictograms
def draw_bridge(cx, cy, s):
    # deck, two towers, cables, blast starburst at mid-span
    cv.rect(cx - 95 * s // 10, cy + 18 * s // 10, 190 * s // 10, 6 * s // 10, INK)
    for tx in (-62, 62):
        cv.rect(cx + tx * s // 10 - 4 * s // 10, cy - 55 * s // 10,
                8 * s // 10, 80 * s // 10, NAVY)
        cv.rect(cx + tx * s // 10 - 7 * s // 10, cy - 62 * s // 10,
                14 * s // 10, 7 * s // 10, NAVY)
    cv.line(cx - 62 * s // 10, cy - 55 * s // 10, cx, cy + 18 * s // 10, GREY, 2)
    cv.line(cx + 62 * s // 10, cy - 55 * s // 10, cx, cy + 18 * s // 10, GREY, 2)
    # blast starburst
    bx, by = cx, cy - 8 * s // 10
    for ang in range(0, 360, 30):
        import math
        r1 = 30 * s // 10
        r2 = 12 * s // 10
        x1 = bx + int(r1 * math.cos(math.radians(ang)))
        y1 = by + int(r1 * math.sin(math.radians(ang)))
        x2 = bx + int(r2 * math.cos(math.radians(ang + 15)))
        y2 = by + int(r2 * math.sin(math.radians(ang + 15)))
        cv.tri([(bx, by), (x1, y1), (x2, y2)], ORANGE)
    cv.circle(bx, by, 10 * s // 10, GOLD, True)
    cv.circle(bx, by, 5 * s // 10, RED, True)


def draw_radar(cx, cy, s):
    # radar dish + sweeping beam + drone above
    cv.line(cx - 45 * s // 10, cy + 30 * s // 10, cx, cy - 10 * s // 10, INK, 3)
    cv.line(cx, cy - 10 * s // 10, cx + 40 * s // 10, cy - 42 * s // 10, INK, 3)
    cv.circle(cx - 8 * s // 10, cy + 34 * s // 10, 6 * s // 10, INK, True)
    for r in (18, 30, 42):
        cv.circle(cx, cy - 10 * s // 10, r * s // 10, TEAL, False)
    # drone
    dx, dy = cx + 62 * s // 10, cy - 52 * s // 10
    cv.rect(dx - 16 * s // 10, dy - 5 * s // 10, 32 * s // 10, 10 * s // 10, RED)
    cv.circle(dx - 18 * s // 10, dy - 8 * s // 10, 4 * s // 10, INK, True)
    cv.circle(dx + 18 * s // 10, dy - 8 * s // 10, 4 * s // 10, INK, True)
    cv.line(dx - 26 * s // 10, dy - 8 * s // 10, dx - 10 * s // 10, dy - 8 * s // 10, INK, 2)
    cv.line(dx + 10 * s // 10, dy - 8 * s // 10, dx + 26 * s // 10, dy - 8 * s // 10, INK, 2)


def draw_flags(cx, cy, s):
    # three summit flags on poles above a table arc
    cols = [RED, BLUE, GOLD]
    for i, col in enumerate(cols):
        px = cx + (i - 1) * 52 * s // 10
        cv.rect(px, cy - 58 * s // 10, 4 * s // 10, 78 * s // 10, INK)
        cv.rect(px + 4 * s // 10, cy - 58 * s // 10, 38 * s // 10, 24 * s // 10, col)
        cv.rect(px + 4 * s // 10, cy - 58 * s // 10, 38 * s // 10, 4 * s // 10, WHITE)
    cv.rect(cx - 78 * s // 10, cy + 20 * s // 10, 156 * s // 10, 8 * s // 10, NAVY)
    cv.rect(cx - 66 * s // 10, cy + 28 * s // 10, 12 * s // 10, 22 * s // 10, NAVY)
    cv.rect(cx + 54 * s // 10, cy + 28 * s // 10, 12 * s // 10, 22 * s // 10, NAVY)


def draw_jet(cx, cy, s):
    # simple jet in flight, nose right, with dashed trail
    cv.tri([(cx - 70 * s // 10, cy), (cx + 55 * s // 10, cy - 12 * s // 10),
            (cx + 55 * s // 10, cy + 12 * s // 10)], SKY)
    cv.tri([(cx + 55 * s // 10, cy - 12 * s // 10), (cx + 78 * s // 10, cy),
            (cx + 55 * s // 10, cy + 12 * s // 10)], INK)
    cv.tri([(cx - 10 * s // 10, cy - 8 * s // 10), (cx - 34 * s // 10, cy - 42 * s // 10),
            (cx - 2 * s // 10, cy - 8 * s // 10)], NAVY)
    cv.tri([(cx - 10 * s // 10, cy + 8 * s // 10), (cx - 34 * s // 10, cy + 42 * s // 10),
            (cx - 2 * s // 10, cy + 8 * s // 10)], NAVY)
    cv.tri([(cx - 58 * s // 10, cy - 6 * s // 10), (cx - 70 * s // 10, cy - 26 * s // 10),
            (cx - 48 * s // 10, cy - 6 * s // 10)], NAVY)
    # short motion ticks just behind the tail, kept inside the panel
    for i in range(3):
        cv.rect(cx - 82 * s // 10 - i * 12 * s // 10, cy - 2 * s // 10,
                7 * s // 10, 4 * s // 10, GREY)


def draw_virus(cx, cy, s):
    cv.circle(cx, cy, 34 * s // 10, RED, True)
    import math
    for ang in range(0, 360, 30):
        x1 = cx + int(34 * s // 10 * math.cos(math.radians(ang)))
        y1 = cy + int(34 * s // 10 * math.sin(math.radians(ang)))
        x2 = cx + int(48 * s // 10 * math.cos(math.radians(ang)))
        y2 = cy + int(48 * s // 10 * math.sin(math.radians(ang)))
        cv.line(x1, y1, x2, y2, RED, 5)
        cv.circle(x2, y2, 5 * s // 10, RED, True)
    cv.circle(cx - 12 * s // 10, cy - 8 * s // 10, 6 * s // 10, WHITE, True)
    cv.circle(cx + 12 * s // 10, cy + 8 * s // 10, 6 * s // 10, WHITE, True)
    cv.circle(cx + 10 * s // 10, cy - 12 * s // 10, 4 * s // 10, WHITE, True)


def draw_gavel(cx, cy, s):
    # courthouse columns under a red ban circle
    cv.tri([(cx - 62 * s // 10, cy - 30 * s // 10), (cx + 62 * s // 10, cy - 30 * s // 10),
            (cx, cy - 58 * s // 10)], NAVY)
    for i in (-1, 0, 1):
        cv.rect(cx + i * 38 * s // 10 - 6 * s // 10, cy - 28 * s // 10,
                12 * s // 10, 52 * s // 10, INK)
    cv.rect(cx - 66 * s // 10, cy + 24 * s // 10, 132 * s // 10, 8 * s // 10, NAVY)
    cv.circle(cx + 46 * s // 10, cy - 34 * s // 10, 26 * s // 10, RED, False)
    cv.line(cx + 46 * s // 10 - 18 * s // 10, cy - 34 * s // 10 - 18 * s // 10,
            cx + 46 * s // 10 + 18 * s // 10, cy - 34 * s // 10 + 18 * s // 10, RED, 5)


# ------------------------------------------------------------------- layout
# masthead band
cv.rect(0, 0, W, 148, NAVY)
cv.rect(0, 148, W, 4, GOLD)
cv.text(24, 14, "THE WORLD IN ONE DAY", 3, GOLD)
date = "TUESDAY 17 NOVEMBER 2026"
dw = cv.text_w(date, 6)
cv.text((W - dw) // 2, 46, date, 6, WHITE)
cv.text(24, 112, "SIX STORIES FROM ONE DAY - AS REPORTED ON 17 NOVEMBER 2026", 2, (200, 210, 220))

# lead story: Ukraine, full width
panel(24, 164, 976, 184, "EUROPE - WAR IN UKRAINE", RED)
draw_bridge(150, 290, 10)
headline_block(300, 222, 676,
               "UKRAINE HITS THE CRIMEAN BRIDGE AGAIN",
               "Second strike in two days. Zelenskyy hails an "
               "\"unprecedented operation\" as Russia hits bridges "
               "in Kyiv in reply.",
               3, 2)

# grid: four stories, 2 x 2. Each panel: tag chip, headline across
# the full width, then pictogram on the left and the summary on the
# right, so nothing wraps into more lines than the panel holds.
GY = 364
GH = 252
GW = 480
GX = [24, 520]


def grid_panel(x, y, tag, tag_c, pic, head, body):
    panel(x, y, GW, GH, tag, tag_c)
    lines = cv.wrap(head, GW - 28, 3)
    yy = y + 48
    for ln in lines:
        cv.text(x + 14, yy, ln, 3, INK)
        yy += 24
    pic(x + 88, y + 172, 8)
    byy = y + 120
    for ln in cv.wrap(body, GW - 184, 2):
        cv.text(x + 170, byy, ln, 2, (58, 66, 76))
        byy += 18


# 1 - Iran / Bahrain
grid_panel(GX[0], GY, "MIDDLE EAST", TEAL, draw_radar,
           "IRAN FIRES DRONES AT US BASE IN BAHRAIN",
           "Drones aimed at a US radar site. Bahrain says "
           "all were intercepted. No casualties reported.")

# 2 - Trump Asia trip
grid_panel(GX[1], GY, "DIPLOMACY - ASIA", BLUE, draw_flags,
           "TRUMP LANDS IN MANILA, BOUND FOR CHINA",
           "ASEAN summit first, then APEC in Shenzhen, "
           "where talks with Xi and Putin are set for Thursday.")

# 3 - Japan jets
grid_panel(GX[0], GY + GH + 16, "ASIA - SECURITY", NAVY, draw_jet,
           "JAPAN SCRAMBLES JETS AS RUSSIAN PLANES ENTER ITS AIRSPACE",
           "Tokyo says two suspected Russian aircraft crossed "
           "in early on Tuesday and protests strongly.")

# 4 - Measles
grid_panel(GX[1], GY + GH + 16, "HEALTH - USA", ORANGE, draw_virus,
           "US LOSES MEASLES-FREE STATUS AFTER 26 YEARS",
           "Health body PAHO rules the virus spread without "
           "a break for 12 months. 5,412 cases in 2026.")

# bottom strip: sixth story - West Bank sanctions, full width
# (drawn manually: too short for the panel tag chip, so the gold bar
#  marks it and the headline carries the story)
cv.rect(24, 900, 976, 72, WHITE)
cv.rect(24, 900, 976, 4, GOLD)
cv.rect(24, 900, 976, 2, INK)
cv.rect(24, 970, 976, 2, INK)
cv.rect(24, 900, 2, 72, INK)
cv.rect(998, 900, 2, 72, INK)
draw_gavel(96, 946, 5)
cv.text(170, 916, "UK SANCTIONS FIRMS BUILDING WEST BANK SETTLEMENTS", 2, INK)
cv.text(170, 942, "EIGHT SETTLEMENT BUILDERS SANCTIONED, PLUS A GROUP BLOCKING AID.", 2, (58, 66, 76))

# ------------------------------------------------------------------ footer
cv.rect(0, 984, W, 40, INK)
foot = "ALL SIX STORIES HAPPENED OR WERE FIRST REPORTED ON TUESDAY 17 NOVEMBER 2026"
fw = cv.text_w(foot, 2)
cv.text((W - fw) // 2, 996, foot, 2, WHITE)

# ------------------------------------------------------------------- PNG out
def write_png(path):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    write_png(os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
