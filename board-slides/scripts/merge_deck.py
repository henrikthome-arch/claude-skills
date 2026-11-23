#!/usr/bin/env python3
"""Splice every contributor PDF into the rendered board deck, each at its own agenda item.

Run from the meeting folder root:  python3 slides/merge_deck.py

  base   = newest slides/output/*v0.N.pdf (never a previously merged file)
  extras = for each agenda item carrying `external_deck` or `external_decks`, that PDF's pages,
           scaled onto our page size and inserted just BEFORE the divider of the next item that
           renders one (or before the closing slide, for the last item).
  out    = "<base stem> + complete.pdf"  — the file the board gets.

AGENDA CONFIG (agenda/agenda.json)
  "external_deck": true        -> the vision deck: newest slides/vision/*.pdf
  "external_decks": [          -> contributor files, in the order given
      {"file": "contributions/tomas/260917-3-r4-growth-och-issues.pdf"},
      {"file": "contributions/prashant/DRAFT ….pdf", "pages": "3-6"}
  ]
`file` is relative to slides/. `pages` is 1-based inclusive ("3-6", "3-6,9", "12-"); omit for the
whole file. Use it to drop a contributor's own cover and agenda — which would otherwise duplicate
ours — or to split one contributor deck across the several agenda items it covers.

WHY ANCHORS ARE RESOLVED FIRST: inserting pages shifts page numbers. Every anchor is found against
the UNTOUCHED base deck and the output is then written in one pass, so several contributions can
land in one deck without each shifting the next one's target (2026-09-16, meeting #8: four
contributor decks across five agenda items).
"""
import glob
import json
import os
import re
import sys

from pypdf import PdfReader, PdfWriter, PageObject, Transformation

MEETING = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLIDES = os.path.join(MEETING, "slides")


def newest(pattern):
    hits = [h for h in glob.glob(pattern) if " + " not in os.path.basename(h)]
    return max(hits, key=os.path.getmtime) if hits else None


def text(page):
    try:
        return re.sub(r"\s+", " ", (page.extract_text() or "")).strip()
    except Exception:
        return ""


def parse_pages(spec, n):
    """'3-6,9' / '12-' -> 0-based indices, clamped to the file."""
    if not spec:
        return list(range(n))
    out = []
    for part in str(spec).split(","):
        part = part.strip()
        if "-" in part:
            a, _, b = part.partition("-")
            lo, hi = (int(a) if a else 1), (int(b) if b else n)
        else:
            lo = hi = int(part)
        out += [i - 1 for i in range(lo, hi + 1) if 1 <= i <= n]
    if not out:
        sys.exit(f"pages spec {spec!r} selects nothing in a {n}-page file")
    return out


def scaled(src, w, h):
    """Contributors export at their own page size (720x405pt is common); ours is 842x473."""
    s = min(w / float(src.mediabox.width), h / float(src.mediabox.height))
    dst = PageObject.create_blank_page(width=w, height=h)
    dx = (w - float(src.mediabox.width) * s) / 2
    dy = (h - float(src.mediabox.height) * s) / 2
    dst.merge_transformed_page(src, Transformation().scale(s).translate(dx, dy))
    return dst


def main():
    base_path = newest(os.path.join(SLIDES, "output", "*v0.*.pdf"))
    if not base_path:
        sys.exit("No rendered deck in slides/output.")
    base = PdfReader(base_path)
    W = float(base.pages[0].mediabox.width)
    H = float(base.pages[0].mediabox.height)

    items = json.loads(open(os.path.join(MEETING, "agenda", "agenda.json")).read())["agenda_items"]

    contributions = {}
    for it in items:
        specs = []
        if it.get("external_deck"):
            v = newest(os.path.join(SLIDES, "vision", "*.pdf"))
            if not v:
                sys.exit("external_deck is set but slides/vision/ holds no PDF.")
            specs.append((v, None))
        for spec in it.get("external_decks") or []:
            path = os.path.join(SLIDES, spec["file"])
            if not os.path.exists(path):
                sys.exit(f"external_decks: missing file {spec['file']}")
            specs.append((path, spec.get("pages")))
        if specs:
            loaded = []
            for path, pages in specs:
                r = PdfReader(path)
                loaded.append((os.path.basename(path), r, parse_pages(pages, len(r.pages))))
            contributions[it["number"]] = loaded
    if not contributions:
        sys.exit("No agenda item carries external_deck or external_decks — nothing to merge.")

    # Where does an item start in the base deck? Its divider ("05 Financials") when it renders one,
    # else its first slide's kicker ("5 · FINANCIALS"). Henrik dropped the dividers on 2026-11-05
    # ("The header pages may not be useful"), so the kicker is the normal anchor now. Items with no
    # page of their own (contributor-only items) are skipped: their pages go before the next item
    # that has one, and contributions keep agenda order.
    def start_page(num):
        for prefix in (f"{num:02d} ", f"{num} · "):
            hit = next((i for i, p in enumerate(base.pages) if text(p).startswith(prefix)), None)
            if hit is not None:
                return hit
        return None

    anchors, where = {}, {}
    for num in sorted(contributions):
        idx, nxt = None, None
        for later in sorted(i["number"] for i in items if i["number"] > num):
            idx = start_page(later)
            if idx is not None:
                nxt = later
                break
        if idx is None:
            idx = len(base.pages) - 1
            where[num] = "before the closing slide"
        else:
            where[num] = f"before item {nxt} (page {idx + 1})"
        anchors.setdefault(idx, []).extend(contributions[num])

    out = PdfWriter()
    for i, page in enumerate(base.pages):
        for _, reader, pages in anchors.get(i, []):
            for p in pages:
                out.add_page(scaled(reader.pages[p], W, H))
        out.add_page(page)

    stem = os.path.basename(base_path).replace(".pdf", "")
    dst = os.path.join(SLIDES, "output", f"{stem} + complete.pdf")
    with open(dst, "wb") as fh:
        out.write(fh)

    print(f"base   {os.path.basename(base_path)} ({len(base.pages)} pp)")
    for num in sorted(contributions):
        for label, reader, pages in contributions[num]:
            print(f"item {num:>2}  {label} — {len(pages)} pp, {where[num]}")
    print(f"-> {os.path.basename(dst)} ({len(out.pages)} pp)")


if __name__ == "__main__":
    main()
