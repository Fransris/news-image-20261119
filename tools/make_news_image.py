#!/usr/bin/env python3
"""Draw the 1024x1024 front page for Thursday 19 November 2026.

Run:  python3 tools/make_news_image.py repo/entry.png
The layout is a fixed grid of rules and text blocks: every block is measured
before it is drawn and the script fails loudly instead of overflowing a card.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 40

PAPER = (245, 240, 229)
INK = (18, 22, 27)
DARK = (21, 25, 30)
BODY = (58, 55, 50)
MUTED = (108, 100, 90)
ACCENT = (168, 32, 40)
GOLD = (216, 172, 98)
RULE = (196, 185, 168)
WHITE = (247, 243, 234)
DIM = (198, 192, 181)

FONT_DIRS = [
    Path("/usr/share/fonts/truetype/liberation"),
    Path("/usr/share/fonts/truetype/dejavu"),
    Path("/usr/share/fonts/TTF"),
]

SERIF_BOLD = ["LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"]
SERIF = ["LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"]
SANS_BOLD = ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]
SANS = ["DejaVuSans.ttf", "LiberationSans-Regular.ttf"]
SANS_COND_BOLD = ["DejaVuSansCondensed-Bold.ttf", "DejaVuSans-Bold.ttf"]


def load(names: list[str], size: int) -> ImageFont.FreeTypeFont:
    for name in names:
        for d in FONT_DIRS:
            p = d / name
            if p.exists():
                return ImageFont.truetype(str(p), size)
    raise SystemExit(f"no font of {names} found")


def wrap(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if font.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(draw, text, font, fill, x, y, max_w, line_h, max_lines=None):
    """Draw wrapped text; return the y just below it. Fails on overflow."""
    lines = wrap(text, font, max_w)
    if max_lines is not None and len(lines) > max_lines:
        raise SystemExit(f"text needs {len(lines)} lines, budget {max_lines}: {text[:40]!r}")
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y


def fit_headline(text, names, start, floor, max_w, max_lines, tracking=0):
    """Largest size that wraps inside max_lines; returns (font, lines)."""
    size = start
    while size >= floor:
        font = load(names, size)
        lines = wrap(text, font, max_w)
        if len(lines) <= max_lines:
            return font, lines, size
        size -= 2
    raise SystemExit(f"headline will not fit: {text[:40]!r}")


def draw_tracked(draw, xy, text, font, fill, tracking=1.0):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    return x


def rule(draw, x0, y0, x1, y1, fill=RULE, width=1):
    draw.line((x0, y0, x1, y1), fill=fill, width=width)


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------------------------------------------------------------- masthead
    mast = load(SERIF_BOLD, 46)
    draw_tracked(d, (MARGIN, 28), "THE WORLD TODAY", mast, INK, 1.2)
    sub = load(SANS_BOLD, 11)
    draw_tracked(d, (MARGIN + 3, 84), "ONE DAY  ·  ONE PAGE  ·  SIX STORIES", sub, MUTED, 1.6)

    date_f = load(SANS_BOLD, 15)
    date_txt = "THURSDAY 19 NOVEMBER 2026"
    d.text((W - MARGIN - date_f.getlength(date_txt), 40), date_txt, font=date_f, fill=INK)
    ed_f = load(SANS_BOLD, 11)
    ed_txt = "WORLD EDITION  ·  NO. 323"
    d.text((W - MARGIN - ed_f.getlength(ed_txt), 62), ed_txt, font=ed_f, fill=MUTED)
    d.rectangle((W - MARGIN - 34, 84, W - MARGIN, 84), fill=ACCENT)
    rule(d, MARGIN, 104, W - MARGIN, 104, INK, 2)

    # ------------------------------------------------------------------- hero
    top, bottom = 118, 496
    d.rectangle((MARGIN, top, W - MARGIN, bottom), fill=DARK)

    kick = load(SANS_BOLD, 13)
    draw_tracked(d, (MARGIN + 24, top + 22), "APEC  ·  SHENZHEN  ·  FIRST-EVER TRILATERAL", kick, GOLD, 1.5)

    hero_w = 560
    hfont, hlines, hsize = fit_headline("THREE POWERS, ONE TABLE", SERIF_BOLD, 64, 44, hero_w, 2)
    y = top + 52
    for line in hlines:
        d.text((MARGIN + 24, y), line, font=hfont, fill=WHITE)
        y += int(hsize * 1.04)

    y = block(
        d,
        "Xi Jinping, Donald Trump and Vladimir Putin sit down together for the first "
        "time, on APEC's sidelines, with a Trump-Putin one-to-one to follow. On the "
        "table: Ukraine, Iran, energy, nuclear arms.",
        load(SERIF, 18), DIM, MARGIN + 24, y + 14, hero_w, 24, max_lines=4,
    )

    # a pull quote, on the eve of the summit
    y += 10
    rule(d, MARGIN + 24, y + 2, MARGIN + 24, y + 40, GOLD, 3)
    y = block(d, "\u201cEnough power to stop Putin in one meeting.\u201d",
              load(SERIF, 20), WHITE, MARGIN + 40, y, hero_w - 20, 24, max_lines=1)
    block(d, "ZELENSKYY, AHEAD OF THE SHENZHEN SUMMIT", load(SANS_BOLD, 11), GOLD,
          MARGIN + 40, y + 2, hero_w - 20, 14, max_lines=1)

    if y + 18 > bottom - 50:
        raise SystemExit(f"hero column overflows: quote ends at {y + 18}, rule at {bottom - 50}")

    rule(d, MARGIN + 24, bottom - 44, MARGIN + 24 + hero_w, bottom - 44, (74, 78, 82))
    block(d, "THE AGENDA  ·  UKRAINE  ·  IRAN  ·  NUCLEAR ARMS  ·  TRADE",
          load(SANS_BOLD, 12), GOLD, MARGIN + 24, bottom - 32, hero_w, 16, max_lines=1)

    # right column of the hero: the number and the three seats
    num_f = load(SERIF_BOLD, 104)
    d.text((700, top + 44), "1st", font=num_f, fill=GOLD)
    block(d, "time the leaders of China, Russia and the United States share one table",
          load(SANS, 13), DIM, 706, top + 160, 258, 18, max_lines=3)

    bars = [("CN", 96, (196, 60, 52)), ("RU", 74, (222, 214, 196)), ("US", 112, (92, 132, 190))]
    bx, base = 706, bottom - 56
    for label, h, colour in bars:
        d.rectangle((bx, base - h, bx + 46, base), fill=colour)
        lab = load(SANS_BOLD, 11)
        d.text((bx + 2, base + 4), label, font=lab, fill=DIM)
        bx += 58

    # ------------------------------------------------------------- row A rules
    row_a_top, row_a_bot = 512, 704
    mid = 500
    rule(d, MARGIN, row_a_top - 8, W - MARGIN, row_a_top - 8, RULE, 1)
    rule(d, mid + 12, row_a_top, mid + 12, row_a_bot, RULE, 1)

    def card(x0, x1, kicker, metric, headline, body, hsize, hlines, bsize, blines, blh):
        y = row_a_top + 10
        d.rectangle((x0, y + 3, x0 + 22, y + 6), fill=ACCENT)
        y += 12
        kf = load(SANS_BOLD, 12)
        draw_tracked(d, (x0, y), kicker, kf, ACCENT, 1.3)
        if metric:
            mf = load(SERIF_BOLD, 21)
            d.text((x1 - mf.getlength(metric), y - 5), metric, font=mf, fill=ACCENT)
        y += 24
        hf, hl, used = fit_headline(headline, SANS_COND_BOLD, hsize, hsize - 8, x1 - x0, hlines)
        for line in hl:
            d.text((x0, y), line, font=hf, fill=INK)
            y += int(used * 1.12)
        y += 6
        block(d, body, load(SANS, bsize), BODY, x0, y, x1 - x0, blh, max_lines=blines)

    card(
        MARGIN, mid,
        "UKRAINE  ·  CRIMEA", "€45BN",
        "KERCH BRIDGE HIT A SECOND TIME",
        "Drones and missiles halt traffic on the bridge to Crimea days after the first "
        "strike; Dutch-made Destinus missiles are named, and Moscow asks if The Hague has "
        "joined the war. The EU offers a €45bn loan; Berlin's coalition of the willing "
        "meets US envoys.",
        hsize=27, hlines=2, bsize=14, blines=5, blh=18,
    )
    card(
        mid + 24, W - MARGIN,
        "IRAN  ·  THE GULF", "8 MONTHS",
        "STRIKES ARE BACK ON THE TABLE",
        "Trump weighs a joint US-Israeli campaign as Israel warns of chemical-weapons work; "
        "targets include Pickaxe Mountain. Gulf states urge restraint, Hormuz stays tense, "
        "and the war he promised would be quick enters its eighth month.",
        hsize=27, hlines=2, bsize=14, blines=5, blh=18,
    )

    # ------------------------------------------------------------- row B rules
    row_b_top, row_b_bot = 714, 878
    rule(d, MARGIN, row_b_top - 8, W - MARGIN, row_b_top - 8, RULE, 1)
    c1, c2 = 344, 656
    rule(d, c1, row_b_top, c1, row_b_bot, RULE, 1)
    rule(d, c2, row_b_top, c2, row_b_bot, RULE, 1)

    def small(x0, x1, kicker, metric, headline, body):
        y = row_b_top + 8
        d.rectangle((x0, y + 2, x0 + 18, y + 5), fill=ACCENT)
        y += 10
        kf = load(SANS_BOLD, 10)
        draw_tracked(d, (x0, y), kicker, kf, ACCENT, 1.1)
        if metric:
            mf = load(SERIF_BOLD, 17)
            d.text((x1 - mf.getlength(metric), y - 4), metric, font=mf, fill=ACCENT)
        y += 20
        hf, hl, used = fit_headline(headline, SANS_COND_BOLD, 19, 15, x1 - x0 - 18, 2)
        for line in hl:
            d.text((x0, y), line, font=hf, fill=INK)
            y += int(used * 1.14)
        y += 5
        block(d, body, load(SANS, 12), BODY, x0, y, x1 - x0 - 18, 16, max_lines=4)

    small(
        MARGIN, c1 - 18,
        "MARKETS", "$82.70",
        "ANTHROPIC'S DEBUT, OIL'S SLIDE",
        "Anthropic prices its IPO above range as it starts trading; Nvidia falls a fifth "
        "day; WTI at $82.70 and Brent near $91, the lowest in three months; gold drops 3%.",
    )
    small(
        c1 + 18, c2 - 18,
        "CHIPS  ·  TRADE", "AI CURBS",
        "WASHINGTON TIGHTENS, BEIJING VOWS REPLY",
        "New US limits on China's remote access to advanced AI chips draw a promise of "
        "retaliation, as Xi courts the Global South on open trade in Shenzhen.",
    )
    small(
        c2 + 18, W - MARGIN,
        "JAPAN  ·  CHINA", "1st",
        "A HANDSHAKE, NOT A THAW",
        "Sanae Takaichi meets Xi for the first time since taking office, ties still raw "
        "over Taiwan; she also holds her first talks with Putin.",
    )

    # ----------------------------------------------------------------- ticker
    tick_top = 892
    d.rectangle((0, tick_top, W, H), fill=DARK)
    d.rectangle((MARGIN, tick_top + 18, MARGIN + 6, tick_top + 30), fill=ACCENT)
    draw_tracked(d, (MARGIN + 16, tick_top + 15), "ALSO TODAY", load(SANS_BOLD, 12), GOLD, 1.4)
    block(
        d,
        "Grand Theft Auto 6 finally ships after 13 years  ·  Britain sends long-range drones "
        "to Kyiv  ·  Copper falls 5.7%  ·  Malaysia's inflation edges up to 2.0%  ·  "
        "Takaichi and Putin meet as a Japanese journalist is held in Russia",
        load(SANS, 13), DIM, MARGIN + 16, tick_top + 38, W - 2 * MARGIN - 16, 19, max_lines=3,
    )
    rule(d, 0, tick_top, W, tick_top, GOLD, 2)

    if img.size != (W, H):
        raise SystemExit("bad size")
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes, {img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
