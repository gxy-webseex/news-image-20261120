#!/usr/bin/env python3
"""Draw entry.png: a newspaper front page summing up Friday 20 November 2026.

Build-time only (PIL + DejaVu). The shipped image is drawn now; main.ts just
copies it to /output. Deterministic: no randomness, no network, no timestamps.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PAPER = (248, 244, 236)      # off-white newsprint
INK = (26, 26, 26)           # near-black headline ink
SUB = (74, 74, 74)           # dark grey sub-label ink
NAVY = (22, 35, 63)          # header band
GOLD = (201, 162, 39)        # accent
PANEL = (255, 255, 255)      # panel fill
BORDER = (200, 192, 176)     # panel border
TEAL = (14, 110, 110)
CRIMSON = (168, 32, 40)
AMBER = (176, 112, 8)
BLUE = (30, 84, 160)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by pixel width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def tracked(draw, cx, y, text, fnt, fill, tracking=6):
    """Draw text with letter tracking, centred on cx."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


# ---------- icons (simple bold silhouettes) ----------

def icon_flags(d, x, y, s, color):
    """Three summit flags on poles."""
    pole_w = max(4, s // 28)
    for i, c in enumerate([CRIMSON, GOLD, BLUE]):
        px = x + i * (s // 3) + s // 12
        d.line([(px, y + s // 6), (px, y + s)], fill=color, width=pole_w)
        d.polygon([(px, y + s // 6), (px + s // 4, y + s // 4),
                   (px, y + s // 3)], fill=c)


def icon_controller(d, x, y, s, color):
    """Game controller: rounded body, D-pad, two buttons."""
    d.rounded_rectangle([x, y + s // 4, x + s, y + s * 3 // 4], radius=s // 6,
                        fill=color)
    d.rounded_rectangle([x - s // 10, y + s // 3, x + s // 10, y + s],
                        radius=s // 8, fill=color)
    d.rounded_rectangle([x + s * 9 // 10, y + s // 3, x + s + s // 10, y + s],
                        radius=s // 8, fill=color)
    # D-pad (plus sign)
    cx, cy, a = x + s // 4, y + s // 2, s // 10
    d.rectangle([cx - a, cy - a * 2, cx + a, cy + a * 2], fill=PAPER)
    d.rectangle([cx - a * 2, cy - a, cx + a * 2, cy + a], fill=PAPER)
    # two buttons
    d.ellipse([x + s * 5 // 8, y + s // 3, x + s * 5 // 8 + s // 7,
               y + s // 3 + s // 7], fill=PAPER)
    d.ellipse([x + s * 3 // 4, y + s // 2, x + s * 3 // 4 + s // 7,
               y + s // 2 + s // 7], fill=PAPER)


def icon_chart(d, x, y, s, color):
    """Rising stock chart with arrow."""
    d.line([(x, y + s), (x, y + s // 8)], fill=color, width=max(4, s // 24))
    d.line([(x, y + s), (x + s, y + s)], fill=color, width=max(4, s // 24))
    pts = [(x + s // 10, y + s * 3 // 4), (x + s * 3 // 10, y + s * 5 // 8),
           (x + s // 2, y + s * 2 // 3), (x + s * 7 // 10, y + s * 3 // 8),
           (x + s * 9 // 10, y + s // 6)]
    d.line(pts, fill=color, width=max(5, s // 18), joint="curve")
    # arrowhead
    ax, ay = pts[-1]
    d.polygon([(ax, ay - s // 10), (ax + s // 8, ay + s // 12),
               (ax - s // 12, ay + s // 8)], fill=color)
    # dollar sign
    d.text((x + s // 8, y + s // 10), "$", font=font(BOLD, s // 3), fill=color)


def icon_bridge(d, x, y, s, color):
    """Bridge with two towers, cables, and a blast burst over one span."""
    deck = y + s * 2 // 3
    d.line([(x, deck), (x + s, deck)], fill=color, width=max(5, s // 20))
    for tx in (x + s // 5, x + s * 3 // 5):
        d.rectangle([tx, y + s // 4, tx + s // 12, deck], fill=color)
        d.line([(tx + s // 24, y + s // 4), (x + s // 10, deck)],
               fill=color, width=max(3, s // 30))
        d.line([(tx + s // 24, y + s // 4), (x + s // 2, deck)],
               fill=color, width=max(3, s // 30))
    # blast burst (star) above the middle span
    bx, by, r = x + s // 2, y + s // 6, s // 6
    star = []
    for i in range(12):
        ang = math.pi * i / 6 - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.45
        star.append((bx + rr * math.cos(ang), by + rr * math.sin(ang)))
    d.polygon(star, fill=CRIMSON)


def icon_cyclone(d, x, y, s, color):
    """Cyclone spiral with a calm eye."""
    cx, cy = x + s / 2, y + s / 2
    pts = []
    turns = 2.4
    steps = 120
    for i in range(steps + 1):
        t = i / steps
        ang = t * turns * 2 * math.pi
        r = s * 0.06 + t * s * 0.42
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d.line(pts, fill=color, width=max(5, s // 16), joint="curve")
    d.ellipse([cx - s // 12, cy - s // 12, cx + s // 12, cy + s // 12],
              fill=PAPER, outline=color, width=max(3, s // 28))


# ---------- page ----------

def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- header band ----
    d.rectangle([0, 0, W, 150], fill=NAVY)
    d.rectangle([0, 150, W, 156], fill=GOLD)
    tracked(d, W // 2, 26, "WORLD NEWS", font(BOLD, 30), GOLD, tracking=10)
    d.text((W // 2, 62), "FRIDAY 20 NOVEMBER 2026", font=font(BOLD, 62),
           fill=(255, 255, 255), anchor="ma")

    MX = 28                      # side margin
    CW = W - 2 * MX              # content width

    # ---- lead story: APEC ----
    ly0, ly1 = 176, 372
    d.rectangle([MX, ly0, W - MX, ly1], fill=PANEL, outline=BORDER, width=2)
    d.rectangle([MX, ly0, W - MX, ly0 + 8], fill=GOLD)
    icon_flags(d, MX + 24, ly0 + 44, 120, NAVY)
    tx = MX + 190
    hl = wrap(d, "APEC ADOPTS SHENZHEN OUTLOOK", font(BOLD, 42),
              W - MX - tx - 24)
    for i, ln in enumerate(hl[:2]):
        d.text((tx, ly0 + 22 + i * 50), ln, font=font(BOLD, 42), fill=INK)
    sub = "Leaders close the Shenzhen summit; Xi calls for an Asia-Pacific community"
    for i, ln in enumerate(wrap(d, sub, font(REG, 26), W - MX - tx - 24)):
        d.text((tx, ly0 + 128 + i * 34), ln, font=font(REG, 26), fill=SUB)

    # ---- 2x2 grid ----
    gy0, gy1 = 392, 872
    gap = 20
    pw = (CW - gap) // 2
    ph = (gy1 - gy0 - gap) // 2
    stories = [
        ("GTA 6 LAUNCHES", "Vice City returns as the game goes on sale worldwide",
         icon_controller, CRIMSON, "GAMES"),
        ("ANTHROPIC IPOs AT $83", "AI firm targets $1.5tn; Wall St falls",
         icon_chart, AMBER, "MARKETS"),
        ("UKRAINE HITS CRIMEA BRIDGE", "Third strike this week; Putin vows to hit back",
         icon_bridge, BLUE, "WAR"),
        ("CYCLONE AKVAN HITS INDIA", "120,000 evacuated; trains cancelled",
         icon_cyclone, TEAL, "WEATHER"),
    ]
    for idx, (head, sub, icon, color, tag) in enumerate(stories):
        col, row = idx % 2, idx // 2
        x0 = MX + col * (pw + gap)
        y0 = gy0 + row * (ph + gap)
        x1, y1 = x0 + pw, y0 + ph
        d.rectangle([x0, y0, x1, y1], fill=PANEL, outline=BORDER, width=2)
        d.rectangle([x0, y0, x1, y0 + 8], fill=color)
        icon(d, x0 + 22, y0 + 46, 118, color)
        tx = x0 + 162
        tw = x1 - tx - 20
        hl = wrap(d, head, font(BOLD, 30), tw)
        for i, ln in enumerate(hl[:2]):
            d.text((tx, y0 + 30 + i * 38), ln, font=font(BOLD, 30), fill=INK)
        sy = y0 + 30 + len(hl[:2]) * 38 + 10
        for i, ln in enumerate(wrap(d, sub, font(REG, 24), tw)[:2]):
            d.text((tx, sy + i * 30), ln, font=font(REG, 24), fill=SUB)
        d.text((tx, y1 - 38), tag, font=font(BOLD, 20), fill=color)

    # ---- also strip ----
    ay0, ay1 = 892, 968
    d.rectangle([MX, ay0, W - MX, ay1], fill=(238, 232, 218),
                outline=BORDER, width=2)
    d.rectangle([MX, ay0, MX + 8, ay1], fill=GOLD)
    also = ("ALSO:  Tankers burn after mines near Hormuz  ·  "
            "Israel operation in Gaza  ·  "
            "Houthi strike hits Riyadh tower")
    for i, ln in enumerate(wrap(d, also, font(BOLD, 22), CW - 44)[:2]):
        d.text((MX + 24, ay0 + 12 + i * 28), ln, font=font(BOLD, 22), fill=INK)

    # ---- footer ----
    d.text((W // 2, 982), "All stories as reported on 20 November 2026",
           font=font(REG, 20), fill=(120, 112, 96), anchor="ma")

    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
