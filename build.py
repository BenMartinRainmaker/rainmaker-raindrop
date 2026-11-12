#!/usr/bin/env python3
"""Builds <month>/raindrop.html from <month>/content.md and the shared template.html.

Usage:  python3 build.py 2026-10-anduril
Edit the words in content.md; the design lives in template.html and never needs touching.
Run by render.sh automatically whenever content.md exists.
"""
import html, re, sys, os, math

ROOT = os.path.dirname(os.path.abspath(__file__))

# Icons for the "What they build" categories and the feature band. Pick by name in content.md:
#   ## Autonomous aircraft (aircraft)
ICONS = {
  "aircraft":   '<path d="M12 3l9 14-9-3-9 3z"/><path d="M12 14v6"/>',
  "missile":    '<path d="M12 2c3 3 4 8 4 12l-4 4-4-4c0-4 1-9 4-12z"/><path d="M8 14l-3 2 2 3M16 14l3 2-2 3"/>',
  "sensor":     '<path d="M12 21V9"/><path d="M8 21h8"/><path d="M7 7a7 7 0 0 1 10 0"/><path d="M4 4a11 11 0 0 1 16 0"/><circle cx="12" cy="9" r="1.5"/>',
  "shield":     '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M12 8v5M9.5 11.5L12 13l2.5-1.5"/>',
  "underwater": '<path d="M3 13c3-5 7-5 9 0s6 5 9 0"/><path d="M6 8l5 2 6-2-2 4"/><path d="M10 5v3"/>',
  "soldier":    '<path d="M4 12a8 8 0 0 1 16 0v3H4z"/><path d="M4 15h16M9 15v3h6v-3"/><path d="M14 10h3"/>',
  "rocket":     '<path d="M12 2c4 3 5 9 3 14H9c-2-5-1-11 3-14z"/><path d="M9 16l-3 3M15 16l3 3M12 16v5"/><circle cx="12" cy="9" r="1.5"/>',
  "chip":       '<rect x="7" y="7" width="10" height="10" rx="1.5"/><path d="M10 7V3M14 7V3M10 21v-4M14 21v-4M7 10H3M7 14H3M21 10h-4M21 14h-4"/>',
  "cloud":      '<path d="M7 18a4 4 0 0 1-.5-8A6 6 0 0 1 18 9a4 4 0 0 1 0 9z"/>',
  "building":   '<rect x="4" y="3" width="16" height="18"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2M10 21v-3h4v3"/>',
  "factory":    '<path d="M3 21V10l6 4v-4l6 4v-4l6 4v7z"/><path d="M7 21v-3M12 21v-3M17 21v-3"/>',
  "globe":      '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
  "car":        '<path d="M4 15l2-6h12l2 6v4H4z"/><circle cx="8" cy="16" r="1.5"/><circle cx="16" cy="16" r="1.5"/><path d="M4 12h16"/>',
  "satellite":  '<rect x="9" y="9" width="6" height="6" transform="rotate(45 12 12)"/><path d="M3 9l4-4 4 4-4 4zM13 15l4 4 4-4-4-4z"/><path d="M14 10l2-2"/>',
  "bolt":       '<path d="M13 2L5 14h6l-1 8 9-13h-6z"/>',
  "dollar":     '<circle cx="12" cy="12" r="9"/><path d="M15 9a3 3 0 0 0-3-2c-2 0-3 1-3 2.5S10 12 12 12s3 1 3 2.5S14 17 12 17a3 3 0 0 1-3-2M12 5v2M12 17v2"/>',
  "heart":      '<path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/>',
  "network":    '<circle cx="12" cy="12" r="2"/><circle cx="4" cy="6" r="1.5"/><circle cx="20" cy="5" r="1.5"/><circle cx="4" cy="18" r="1.5"/><circle cx="20" cy="19" r="1.5"/><path d="M12 12L4 6M12 12l8-7M12 12l-8 6M12 12l8 7"/>',
  "box":        '<path d="M12 3l9 5v8l-9 5-9-5V8z"/><path d="M3 8l9 5 9-5M12 13v8"/>',
}
# Larger version used in the navy feature band.
BAND_ICONS = {
  "network": '<circle cx="30" cy="30" r="5" fill="#d4af37"/><circle cx="10" cy="14" r="3"/><circle cx="50" cy="12" r="3"/><circle cx="8" cy="44" r="3"/><circle cx="52" cy="46" r="3"/><circle cx="30" cy="8" r="3"/><circle cx="30" cy="52" r="3"/><path d="M30 30L10 14M30 30L50 12M30 30L8 44M30 30L52 46M30 30V8M30 30V52" opacity=".7"/><path d="M10 14L30 8L50 12M8 44L30 52L52 46" opacity=".35"/>',
}

OPTION_KEYS = ("title", "subtitle", "icon", "caption", "reported", "unit")


# ---------- inline text: **bold**, *italic*, [text](url), smart quotes, HTML escaping ----------
def inline(s):
    s = s.strip()
    links = []
    def keep(m):
        links.append((m.group(1), m.group(2)))
        return "\x00%d\x00" % (len(links) - 1)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", keep, s)
    s = html.escape(s, quote=False)
    s = re.sub(r"(?<=\w)'", "\u2019", s)          # apostrophes
    s = re.sub(r"(^|[\s(])'", "\\1\u2018", s)
    s = re.sub(r'(^|[\s(])"', "\\1\u201c", s)     # opening double quote
    s = s.replace('"', "\u201d")                   # the rest are closing
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\w)\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<i>\1</i>", s)
    def restore(m):
        t, u = links[int(m.group(1))]
        return '<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (html.escape(u, quote=True), inline(t))
    return re.sub("\x00(\\d+)\x00", restore, s)


def bullet(line):
    """'Name: phrase' -> <li><b>Name:</b> phrase</li>; plain lines stay plain."""
    m = re.match(r"([^:]{1,60}):\s+(.+)", line)
    if m:
        return "<li><b>%s:</b> %s</li>" % (inline(m.group(1)), inline(m.group(2)))
    return "<li>%s</li>" % inline(line)


def cells(line):
    return [c.strip() for c in line.split("|")]


# ---------- parse content.md ----------
def parse(text):
    """Every section keeps its lines plus their 0-based line numbers in content.md ("ln"),
    so the page's edit mode can write a change back to the exact line."""
    meta, metaln, sections, cur = {}, {}, {}, None
    for n, raw in enumerate(text.splitlines()):
        line = raw.rstrip()
        if line.startswith("# "):
            name = line[2:].strip()
            cur = {"title": name, "options": {}, "optln": {}, "lines": [], "ln": [], "subs": []}
            sections[norm(name)] = cur
            continue
        if cur is None:
            if ":" in line:
                k, v = line.split(":", 1)
                meta[norm(k)] = v.strip()
                metaln[norm(k)] = n
            continue
        if line.startswith("## "):
            cur["subs"].append({"title": line[3:].strip(), "ln": n, "lines": [], "lns": []})
            continue
        m = re.match(r"(%s):\s*(.*)" % "|".join(OPTION_KEYS), line, re.I)
        if m and not cur["subs"]:
            cur["options"][m.group(1).lower()] = m.group(2).strip()
            cur["optln"][m.group(1).lower()] = n
            continue
        tgt = cur["subs"][-1] if cur["subs"] else cur
        tgt["lines"].append(line)
        (tgt["lns"] if cur["subs"] else tgt["ln"]).append(n)
    meta["_ln"] = metaln
    return meta, sections


def ed(kind, *a):
    """data-ed attribute telling the page's edit mode which content.md line(s) an element came from."""
    return ' data-ed="%s"' % ":".join([kind] + [str(x) for x in a])


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def paragraphs(lines, lns=None):
    out, buf, span = [], [], []
    lns = lns or [None] * len(lines)
    for l, n in list(zip(lines, lns)) + [("", None)]:
        if l.strip():
            buf.append(l.strip()); span.append(n)
        elif buf:
            attr = ed("text", span[0], span[-1]) if span[0] is not None else ""
            out.append("<p%s>%s</p>" % (attr, inline(" ".join(buf))))
            buf, span = [], []
    return "".join(out)


def text_range(sec):
    """Line range of a section's non-blank body lines, for one-block text (feature band, footer)."""
    ns = [n for l, n in zip(sec["lines"], sec["ln"]) if l.strip()]
    return ed("text", ns[0], ns[-1]) if ns else ""


def bullet_ed(line, n):
    return bullet(line).replace("<li>", "<li%s>" % ed("bullet", n), 1)


def bullets(lines, lns=None):
    lns = lns or [None] * len(lines)
    return "\n".join("          " + (bullet_ed(l[2:], n) if n is not None else bullet(l[2:])) for l, n in zip(lines, lns) if l.startswith("- "))


def rows(lines, lns=None):
    """Table rows as cell lists. With lns, returns (lineno, cells) pairs instead."""
    if lns is None:
        return [cells(l) for l in lines if "|" in l and not l.startswith("#")]
    return [(n, cells(l)) for l, n in zip(lines, lns) if "|" in l and not l.startswith("#")]


def cell_ed(tag, n, i, content, cls=""):
    c = (' class="%s"' % cls) if cls else ""
    return "<%s%s%s>%s</%s>" % (tag, c, ed("cell", n, i), content, tag)


# ---------- valuation chart ----------
def fmt_val(v):
    return ("%g" % v)


def valuation(sec, company):
    unit = sec["options"].get("unit", "B")
    word = {"B": "billion", "M": "million"}.get(unit, unit)
    pts = []
    for r in rows(sec["lines"]):
        if len(r) < 3:
            continue
        label, series, val = r[0], r[1], float(r[2])
        url = r[3] if len(r) > 3 else ""
        short = re.sub(r"^series\s+", "", series, flags=re.I)
        pts.append(dict(label=label, series=series, short=short, val=val, url=url,
                        title="%s: %s, $%s %s" % (label, series, fmt_val(val), word)))
    rep = None
    if "reported" in sec["options"]:
        r = cells(sec["options"]["reported"])
        val = float(r[0]); url = r[1] if len(r) > 1 else ""; note = r[2] if len(r) > 2 else "Reported, unconfirmed"
        rep = dict(val=val, url=url, title="%s, $%s %s" % (note, fmt_val(val), word), note=note)
    allv = [p["val"] for p in pts] + ([rep["val"]] if rep else [])
    top = max(allv)
    step = next(s for s in (0.5, 1, 2, 5, 10, 20, 25, 40, 50, 100, 200, 250, 500, 1000, 2000, 5000) if math.ceil(top / s) <= 4)
    axis_top = math.ceil(top / step) * step
    Y0, YT, X0, X1 = 154.0, 29.0, 44.0, 349.0
    n = len(pts) + (1 if rep else 0)
    xs = [X0 + (X1 - X0) * k / max(n - 1, 1) for k in range(n)]
    y = lambda v: Y0 - (Y0 - YT) * v / axis_top
    grid = ""
    t = 0
    while t <= axis_top + 1e-9:
        grid += '<line x1="36" y1="%.2f" x2="370" y2="%.2f" stroke="#dde5ee"/><text x="27" y="%.2f" text-anchor="end" class="chart-axis">%s</text>\n' % (y(t), y(t), y(t) + 4, fmt_val(t))
        t += step
    coords = ["%.0f,%.2f" % (xs[k], y(p["val"])) for k, p in enumerate(pts)]
    area = '<path d="M %.0f %.0f L %s L %.0f %.0f Z" fill="url(#valuation-fill)"/>' % (xs[0], Y0, " L ".join(coords), xs[len(pts) - 1], Y0)
    line = '<polyline points="%s" fill="none" stroke="#10305f" stroke-width="2.5" stroke-linejoin="round"/>' % " ".join(coords)
    dots = ""
    for k, p in enumerate(pts):
        cx, cy = xs[k], y(p["val"])
        dots += ('<a href="%s" target="_blank" rel="noopener noreferrer"><title>%s</title><circle cx="%.0f" cy="%.2f" r="4" fill="#10305f" stroke="#fff" stroke-width="2"/>'
                 '<text x="%.0f" y="%.2f" text-anchor="middle" class="chart-value">$%s%s</text><text x="%.0f" y="174" text-anchor="middle" class="chart-axis">%s</text>'
                 '<text x="%.0f" y="190" text-anchor="middle" class="chart-round">%s</text></a>\n'
                 % (html.escape(p["url"]), html.escape(p["title"]), cx, cy, cx, cy - 13, fmt_val(p["val"]), unit, cx, html.escape(p["label"]), cx, html.escape(p["short"])))
    dashed = ""
    if rep:
        cx, cy = xs[-1], y(rep["val"])
        dashed = '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#b48a2f" stroke-width="2.5" stroke-dasharray="5 4"/>' % (xs[len(pts) - 1], y(pts[-1]["val"]), cx, cy)
        dots += ('<a href="%s" target="_blank" rel="noopener noreferrer"><title>%s</title><circle cx="%.0f" cy="%.2f" r="4.8" fill="#fff" stroke="#b48a2f" stroke-width="2"/>'
                 '<text x="%.0f" y="%.2f" text-anchor="middle" class="chart-value" style="fill:#997020">$%s%s*</text><text x="%.0f" y="174" text-anchor="middle" class="chart-axis">Latest</text>'
                 '<text x="%.0f" y="190" text-anchor="middle" class="chart-round">valuation</text></a>\n'
                 % (html.escape(rep["url"]), html.escape(rep["title"]), cx, cy, cx, cy - 13, fmt_val(rep["val"]), unit, cx, cx))
    desc = "Completed rounds: " + "; ".join("%s %s, $%s %s" % (p["label"], p["series"], fmt_val(p["val"]), word) for p in pts) + "."
    if rep:
        desc += " The dashed gold extension ends at $%s %s, %s, not a completed round." % (fmt_val(rep["val"]), word, rep["note"][0].lower() + rep["note"][1:])
    desc += " Milestones are equally spaced; the vertical axis is linear in USD %ss." % word
    svg_title = "%s valuation milestones, ending at %s" % (company, ("a reported $%s %s target" % (fmt_val(rep["val"]), word)) if rep else ("$%s %s" % (fmt_val(pts[-1]["val"]), word)))
    cap = ('\n        <figcaption>%s</figcaption>' % inline(sec["options"]["caption"])) if sec["options"].get("caption") else ""
    return '''      <figure class="valuation" aria-labelledby="valuation-title">
        <div class="chart-heading"><h2 id="valuation-title">%s</h2><span>%s</span></div>
        <svg viewBox="0 0 400 205" role="img" aria-labelledby="valuation-svg-title valuation-svg-desc">
          <title id="valuation-svg-title">%s</title>
          <desc id="valuation-svg-desc">%s</desc>
          <defs><linearGradient id="valuation-fill" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#2f7fc0" stop-opacity=".24"/><stop offset="1" stop-color="#2f7fc0" stop-opacity=".02"/></linearGradient></defs>
          %s          %s
          %s
          %s
          %s        </svg>%s
      </figure>''' % (inline(sec["title"]), inline(sec["options"].get("subtitle", "")), html.escape(svg_title), html.escape(desc), grid, area, line, dashed, dots, cap)


# ---------- assemble ----------
def build(folder):
    path = os.path.join(ROOT, folder, "content.md")
    meta, S = parse(open(path, encoding="utf-8").read())
    def sec(name, required=True):
        s = S.get(norm(name))
        if s is None and required:
            sys.exit("content.md is missing the section '# %s'" % name)
        return s
    def need(key):
        if norm(key) not in meta:
            sys.exit("content.md is missing '%s:' at the top" % key)
        return meta[norm(key)]

    company = need("company")
    month = need("month")
    m = re.match(r"([A-Za-z]+)\s+(\d{4})", month)
    month_short = meta.get(norm("month short")) or ("%s %s" % (m.group(1)[:3].upper(), m.group(2)) if m else month.upper())
    v = {"company": html.escape(company), "month": html.escape(month), "month_short": html.escape(month_short),
         "subtitle": inline(meta.get("subtitle", "")), "drop_logo": meta.get(norm("logo in drop"), ""),
         "folder": html.escape(folder), "content_md": open(path, encoding="utf-8").read().replace("</", "<\\/")}
    if "subtitle" in meta["_ln"]:
        v["subtitle"] = "<span%s>%s</span>" % (ed("opt", meta["_ln"]["subtitle"], "subtitle"), v["subtitle"])
    if meta.get("wordmark"):
        v["company_name"] = '<img class="wordmark" src="%s" alt="%s">' % (meta["wordmark"], html.escape(company))
    else:
        v["company_name"] = html.escape(company)

    s = sec("Market note", False)
    v["market_note"] = paragraphs(s["lines"], s["ln"]) if s else ""
    s = sec("Introduction")
    v["introduction"] = paragraphs(s["lines"], s["ln"])

    s = sec("Quote", False)
    v["quote"] = ""
    if s:
        ls = [(l, n) for l, n in zip(s["lines"], s["ln"]) if l.strip()]
        if ls:
            q = ls[0][0].strip().strip('"\u201c\u201d')
            who = " ".join(l for l, n in ls[1:]).strip()
            v["quote"] = '<div class="quote">&ldquo;<span%s>%s</span>&rdquo;%s</div>' % (
                ed("quote", ls[0][1]), inline(q),
                ('<span class="who"%s>%s</span>' % (ed("text", ls[1][1], ls[-1][1]), inline(who))) if who else "")

    s = sec("Tags")
    v["tags"] = "\n".join('        <span class="chip"%s><b>%s</b> &nbsp;%s</span>' % (ed("tag", n), inline(a), inline(b))
                          for (a, b), n in (((l[2:] if l.startswith("- ") else l).split(":", 1), n) for l, n in zip(s["lines"], s["ln"]) if ":" in l))

    s = sec("Key numbers")
    v["key_numbers"] = "\n".join('      <div class="stat">%s%s%s</div>' % tuple(cell_ed("div", n, i, inline(c), cls) for i, (c, cls) in enumerate(zip((r + ["", ""])[:3], ("n", "l", "s"))))
                                 for n, r in rows(s["lines"], s["ln"]))

    imgs, caps, dots = [], [], []
    s = sec("Photos")
    for k, (n, r) in enumerate(rows(s["lines"], s["ln"])):
        src, alt, cap = r[0], r[1] if len(r) > 1 else "", r[2] if len(r) > 2 else ""
        pos = (' style="object-position:%s"' % html.escape(r[3])) if len(r) > 3 and r[3] else ""
        on = ' class="on"' if k == 0 else ""
        imgs.append('        <img%s src="%s" alt="%s"%s>' % (on, html.escape(src), html.escape(alt), pos))
        caps.append('          <span%s%s>%s</span>' % (on, ed("cell", n, 2), inline(cap)))
        dots.append('<i class="on"></i>' if k == 0 else "<i></i>")
    v["photo_imgs"], v["photo_caps"], v["photo_dots"] = "\n".join(imgs), "\n".join(caps), "".join(dots)

    s = sec("Valuation history", False)
    v["valuation"] = valuation(s, company) if s else ""

    s = sec("What they build")
    v["build_title"] = inline(s["options"].get("title", s["title"]))
    items = []
    for sub in s["subs"]:
        mm = re.match(r"(.*?)\s*\(([a-z]+)\)\s*$", sub["title"])
        title, icon = (mm.group(1), mm.group(2)) if mm else (sub["title"], "box")
        if icon not in ICONS:
            sys.exit("Unknown icon '%s' in '## %s'. Choose from: %s" % (icon, sub["title"], ", ".join(ICONS)))
        items.append('          <div class="item"><div class="ic"><svg viewBox="0 0 24 24">%s</svg></div><div><div class="t"%s>%s</div><ul>%s</ul></div></div>'
                     % (ICONS[icon], ed("sub", sub["ln"]), inline(title), "".join(bullet_ed(l[2:], n) for l, n in zip(sub["lines"], sub["lns"]) if l.startswith("- "))))
    v["build_items"] = "\n".join(items)

    s = sec("Customers")
    v["customers_title"] = inline(s["options"].get("title", s["title"]))
    v["customers"] = bullets(s["lines"], s["ln"])

    s = sec("Feature band")
    icon = s["options"].get("icon", "network")
    v["feature_icon"] = '<svg viewBox="0 0 60 60" fill="none" stroke="#d4af37" stroke-width="1.4">%s</svg>' % BAND_ICONS.get(icon, BAND_ICONS["network"])
    v["feature_title"] = '<span%s>%s</span>' % (ed("opt", s["optln"]["title"], "title"), inline(s["options"]["title"])) if "title" in s["options"] else ""
    v["feature_text"] = '<span%s>%s</span>' % (text_range(s), inline(" ".join(l.strip() for l in s["lines"] if l.strip())))

    s = sec("Timeline")
    v["timeline_title"] = inline(s["options"].get("title", s["title"]))
    tl = rows(s["lines"], s["ln"])
    v["timeline"] = "\n".join('        <div>%s%s</div>' % (cell_ed("div", n, 0, inline(r[0]).upper(), "m"), cell_ed("div", n, 1, inline(r[1] if len(r) > 1 else ""), "x")) for n, r in tl)
    v["timeline_style"] = "" if len(tl) == 4 else ' style="grid-template-columns:repeat(%d,1fr)"' % max(len(tl), 1)

    s = sec("Fine print")
    v["fine_print"] = '<span%s>%s</span>' % (text_range(s), inline(" ".join(l.strip() for l in s["lines"] if l.strip())))
    s = sec("Footer")
    v["footer"] = '<span%s>%s</span>' % (text_range(s), inline(" ".join(l.strip() for l in s["lines"] if l.strip())))

    tpl = open(os.path.join(ROOT, "template.html"), encoding="utf-8").read()
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: v.get(m.group(1), ""), tpl)
    missing = [k for k in re.findall(r"\{\{(\w+)\}\}", tpl) if k not in v]
    if missing:
        sys.exit("template.html has placeholders the builder does not know: %s" % missing)
    with open(os.path.join(ROOT, folder, "raindrop.html"), "w", encoding="utf-8") as f:
        f.write(out)
    print("built %s/raindrop.html from content.md" % folder)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    build(sys.argv[1])
