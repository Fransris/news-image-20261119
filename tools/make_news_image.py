#!/usr/bin/env python3
"""Draw the 1024x1024 front page for Thursday 19 November 2026.

Run:  python3 tools/make_news_image.py repo/entry.png

One page for one day: a lead on the Shenzhen summit, the day in numbers, then
four columns of news by region, each story a headline and two lines of wire
copy. Every block is measured before it is drawn and the script fails loudly
instead of overflowing.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 26

PAPER = (245, 240, 229)
INK = (18, 22, 27)
DARK = (21, 25, 30)
BODY = (58, 55, 49)
MUTED = (106, 98, 88)
ACCENT = (168, 32, 40)
GOLD = (216, 172, 98)
RULE = (196, 185, 168)
WHITE = (247, 243, 234)
DIM = (202, 196, 185)

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


def load(names, size):
    for name in names:
        for d in FONT_DIRS:
            p = d / name
            if p.exists():
                return ImageFont.truetype(str(p), int(size))
    raise SystemExit(f"no font of {names} found")


def wrap(text, font, max_w):
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


def block(d, text, font, fill, x, y, max_w, line_h, max_lines=None):
    lines = wrap(text, font, max_w)
    if max_lines is not None and len(lines) > max_lines:
        raise SystemExit(f"{len(lines)} lines, budget {max_lines}: {text[:46]!r}")
    for line in lines:
        d.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y


def fit_headline(text, names, start, floor, max_w, max_lines):
    size = start
    while size >= floor:
        font = load(names, size)
        lines = wrap(text, font, max_w)
        if len(lines) <= max_lines:
            return font, lines, size
        size -= 0.5
    raise SystemExit(f"headline will not fit: {text[:46]!r}")


def tracked(d, xy, text, font, fill, tracking=1.0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    return x


def rule(d, x0, y0, x1, y1, fill=RULE, width=1):
    d.line((x0, y0, x1, y1), fill=fill, width=width)


LEAD = (
    "THREE POWERS, ONE TABLE",
    "Xi Jinping, Donald Trump and Vladimir Putin sit down together for the first time, "
    "on APEC's sidelines in Shenzhen, with a Trump-Putin one-to-one to follow. On the "
    "table: Ukraine, Iran, energy and nuclear arms.",
    "\u201cThey have enough power to stop Putin in one meeting.\u201d  \u2014 ZELENSKYY",
)

SECONDARY = [
    ("ICJ: A GENOCIDE VERDICT", "The Hague rules on whether Myanmar committed genocide "
     "against the Rohingya, more than 740,000 of whom fled to Bangladesh."),
    ("THE BIGGEST IPO EVER", "Anthropic raises $81.3bn at $83 a share, a $1.5tn company, "
     "and starts trading on the Nasdaq as ANT."),
]

NUMBERS = [
    ("$81.3bn", "Anthropic's record IPO, the largest ever"),
    ("1 light-day", "Voyager 1's distance from Earth"),
    ("740,000", "Rohingya who fled Myanmar in 2017"),
    ("\u20ac45bn", "EU loan for Kyiv's 2027 budget"),
    ("13 years", "between GTA V and GTA VI"),
    ("2,230", "civilians killed in Sudan this year"),
]

COLUMNS = [
    ("ASIA-PACIFIC", [
        ("Cyclone Akvan nears India's east coast",
         "90-100 kmph winds due Friday; 50,000 evacuated, red alert in 13 districts."),
        ("Takaichi gets a muted welcome in Shenzhen",
         "No formal Xi talks for Japan's PM; she presses Putin on a detained reporter."),
        ("Russian bombers send Asia a message",
         "Two Tu-95s at Da Nang, after flights that scrambled Taiwan's and Japan's jets."),
        ("Quad adds eyes at sea",
         "US, India, Japan and Australia agree maritime surveillance and a joint drill."),
        ("Canberra signs a US AI pact",
         "Australia joins a 10-nation deal on AI supply chains, tilting away from Beijing."),
        ("Xi and Putin, for the 50th time",
         "They call for a multipolar world; Putin calls Europe a hegemon in decline."),
        ("Tencent misses as capex soars",
         "Q3 revenue 207.3bn yuan vs 210.5bn expected; operating profit down 7%."),
        ("Hong Kong and Tokyo slip",
         "Hang Seng -0.9% on AI monetisation worries; Japan's bank index opens -2.1%."),
        ("Trump lands in Manila first",
         "Manila defence ties tightened before the summit; South China Sea on the agenda."),
    ]),
    ("EUROPE", [
        ("Kerch bridge hit a second time",
         "Traffic halted days after the first strike; Dutch-made Destinus missiles named."),
        ("Brussels offers Kyiv \u20ac45bn more",
         "A new EU loan would fill two-thirds of Ukraine's \u20ac70bn hole for 2027."),
        ("Berlin gathers the coalition of the willing",
         "Merz, Macron, Burnham, Tusk, Meloni and Rutte meet US envoys on guarantees."),
        ("Britain arms Kyiv for the deep fight",
         "Long-range drones able to strike inside Russia join the new package."),
        ("EU and Britain edge towards a reset",
         "Friday's summit draft drops 'trusted partnership' as car talks drag."),
        ("Prague bars Russian athletes",
         "No visas for January's women's under-18 ice hockey world championship."),
        ("Europe's third losing session",
         "Stoxx 600 -1.0%, DAX -1.2%, FTSE -1.3%; miners -4.7% as copper drops 5.7%."),
        ("SAP and HSBC drag, chips bounce",
         "SAP -3.8%, HSBC -2.1%; ASML, STMicro and Infineon each gain over 2.5%."),
        ("Zelenskyy: one meeting could end it",
         "Trump, Putin and Xi have the power to stop the war, he says; Kyiv must be in."),
    ]),
    ("MIDDLE EAST & AFRICA", [
        ("Strikes on Iran are back on the table",
         "Trump weighs a joint campaign with Israel over chemical-weapons fears."),
        ("Mossad and CENTCOM make the rounds",
         "Israel's spy chief pressed Washington; Admiral Cooper shuttled to Riyadh."),
        ("Drones over US bases in the Gulf",
         "Iran resumes attacks in Kuwait and Bahrain; most intercepted, Hormuz tense."),
        ("Oil at a three-month low",
         "WTI $82.70, Brent $91.46, as the IEA sees a 2m-barrel surplus."),
        ("Sudan's year of the drone",
         "2,230 civilians killed since January, 1,630 of them by drones, the UN says."),
        ("Airstrikes empty West Kordofan",
         "A week of raids around El Khuwei shuts markets and displaces thousands."),
        ("Sudan's talks lose a bloc",
         "The SPLM-RDC boycotts next week's Nyon process over Islamist inclusion."),
        ("Lagos cocaine route cut",
         "Eight couriers held with 13.8kg bound for Europe across the Sahara."),
        ("Guinea's mining crackdown",
         "1,263 arrests; up to 160,000 miners pushed into Mali as a refinery opens."),
    ]),
    ("THE AMERICAS & WORLD", [
        ("Hegseth reopens the Venezuelan door",
         "In Caracas he signs a military partnership on training and intelligence."),
        ("Oilfields for a partner",
         "NABEP, 35% US-owned, targets 250,000 barrels a day by year-end."),
        ("A 'Donroe Doctrine' with a body count",
         "Boat strikes have killed more than 200 people since last year, officials say."),
        ("Waller wants a half-point hike",
         "The Fed governor cites core inflation running near 3.5% annualised."),
        ("October minutes land hawkish",
         "A December rise is priced in; Nvidia's post-earnings rally fizzles out."),
        ("Nvidia's fifth straight fall",
         "Moody's cuts its outlook to stable as the AI trade cools further."),
        ("Voyager 1 is one light-day away",
         "16.1bn miles out, a first for any human object; its data link is silent."),
        ("GTA VI finally ships",
         "Vice City opens after 13 years at $79.99, the most pre-ordered game ever."),
        ("Bel\u00e9m pledges to triple adaptation",
         "COP30 targets $120bn a year for adaptation by 2035, with no baseline set."),
    ]),
]

TICKER = (
    "ALSO TODAY  \u00b7  US curbs on China's remote access to AI chips draw a promise of "
    "retaliation  \u00b7  Take-Two projects $3.5bn of launch-quarter bookings  \u00b7  "
    "Malaysia's inflation seen at 2.0%  \u00b7  Britain and the EU drop 'trusted "
    "partnership' from the summit draft"
)


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ------------------------------------------------------------- masthead
    tracked(d, (M, 12), "THE WORLD IN ONE DAY", load(SERIF_BOLD, 42), INK, 1.1)
    tracked(d, (M + 2, 62), "THURSDAY 19 NOVEMBER 2026  \u00b7  39 STORIES  \u00b7  6 CONTINENTS",
            load(SANS_BOLD, 10), MUTED, 1.5)
    df = load(SANS_BOLD, 13)
    dt = "WORLD EDITION \u00b7 NO. 323"
    d.text((W - M - df.getlength(dt), 26), dt, font=df, fill=INK)
    d.rectangle((W - M - 30, 48, W - M, 51), fill=ACCENT)
    rule(d, M, 84, W - M, 84, INK, 2)

    # ----------------------------------------------------------------- lead
    top, band_bot = 90, 240
    d.rectangle((M, top, W - M, band_bot), fill=DARK)
    kick = load(SANS_BOLD, 10)
    tracked(d, (M + 18, top + 10), "APEC \u00b7 SHENZHEN \u00b7 FIRST-EVER TRILATERAL", kick, GOLD, 1.3)
    hf, hl, hs = fit_headline(LEAD[0], SERIF_BOLD, 40, 24, 586, 1)
    y = top + 27
    for line in hl:
        d.text((M + 18, y), line, font=hf, fill=WHITE)
        y += int(hs * 1.04)
    y = block(d, LEAD[1], load(SERIF, 13), DIM, M + 18, y + 4, 586, 16.5, max_lines=4)
    y = block(d, LEAD[2], load(SANS_BOLD, 9.4), GOLD, M + 18, y + 2, 586, 12, max_lines=1)
    if y > band_bot - 4:
        raise SystemExit(f"lead column overflows: {y} > {band_bot - 4}")

    # secondary stories, right of the lead
    sx = M + 628
    sy = top + 12
    for head, body in SECONDARY:
        d.rectangle((sx, sy + 1, sx + 14, sy + 3), fill=ACCENT)
        sy = block(d, head, load(SANS_COND_BOLD, 12.5), WHITE, sx, sy + 8, W - M - 16 - sx, 14, max_lines=1)
        sy = block(d, body, load(SANS, 9.6), DIM, sx, sy + 2, W - M - 16 - sx, 12, max_lines=3)
        sy += 8
    if sy > band_bot - 6:
        raise SystemExit(f"secondary stories overflow the lead band: {sy} > {band_bot - 6}")

    # -------------------------------------------------------- numbers strip
    nb_top = band_bot + 6
    nb_bot = nb_top + 54
    rule(d, M, nb_top, W - M, nb_top, INK, 1)
    cell = (W - 2 * M) / 6
    for i, (num, cap) in enumerate(NUMBERS):
        x = M + i * cell
        if i:
            rule(d, x - 6, nb_top + 6, x - 6, nb_bot - 6, RULE, 1)
        d.text((x, nb_top + 5), num, font=load(SERIF_BOLD, 21), fill=ACCENT)
        block(d, cap, load(SANS, 8.6), MUTED, x, nb_top + 29, cell - 12, 9.8, max_lines=2)
    rule(d, M, nb_bot, W - M, nb_bot, RULE, 1)

    # -------------------------------------------------------------- columns
    col_top = nb_bot + 7
    col_bot = 952
    gut = 13
    colw = (W - 2 * M - 3 * gut) / 4
    for ci, (region, stories) in enumerate(COLUMNS):
        x0 = M + ci * (colw + gut)
        x1 = x0 + colw
        if ci:
            rule(d, x0 - gut / 2, col_top, x0 - gut / 2, col_bot, RULE, 1)
        d.rectangle((x0, col_top, x1, col_top + 14), fill=INK)
        tracked(d, (x0 + 4, col_top + 3), f"{region}  \u00b7  {len(stories)}",
                load(SANS_BOLD, 7.8), WHITE, 0.7)
        y = col_top + 20
        for n, (head, body) in enumerate(stories):
            hfont, hlines, hsz = fit_headline(head, SANS_COND_BOLD, 13.5, 9.5, colw, 2)
            for line in hlines:
                d.text((x0, y), line, font=hfont, fill=INK)
                y += int(hsz * 1.15)
            y = block(d, body, load(SANS, 10.2), BODY, x0, y + 1, colw, 12, max_lines=2)
            y += 7 if n < len(stories) - 1 else 0
        if y > col_bot:
            raise SystemExit(f"column {region} overflows: {y} > {col_bot}")

    # --------------------------------------------------------------- ticker
    rule(d, M, col_bot + 6, W - M, col_bot + 6, INK, 2)
    block(d, TICKER, load(SANS, 9.2), MUTED, M, col_bot + 12, W - 2 * M, 11.5, max_lines=2)

    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes, {img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
