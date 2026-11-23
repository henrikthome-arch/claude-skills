"""Splice the externally-produced Vision deck into the rendered board deck.

The Vision item is presented from a separate deck built in Claude Design. Its own
cover acts as the section divider, so agenda.json sets `section_header: false` on
it and data.json carries no slides for it — this script drops the vision pages
into the gap that leaves.

The insertion point is DERIVED from agenda.json, not hard-coded: find the item
with `section_header: false`, then insert before the next item's divider. An
earlier version looked for the literal "05 " prefix and would have silently put
the vision deck in the wrong place when the agenda was renumbered.

The two PDFs are both 16:9 but different sizes (ours 842x473pt from a 297x167mm
page, the export 720x405pt), so vision pages are scaled onto our page size —
otherwise the merged file changes page dimensions halfway through.

Run from the meeting folder root:  python3 slides/merge_deck.py
"""
import glob, json, os, re, sys
from pypdf import PdfReader, PdfWriter, PageObject, Transformation

MEETING = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = max(glob.glob(os.path.join(MEETING, "slides/output/*v0.*.pdf")), key=os.path.getmtime)
VISION = max(glob.glob(os.path.join(MEETING, "slides/vision/*.pdf")), key=os.path.getmtime)

with open(os.path.join(MEETING, "agenda/agenda.json")) as fh:
    items = json.load(fh)["agenda_items"]

external = [i for i in items if i.get("external_deck")]
if len(external) != 1:
    sys.exit(f"expected exactly one item with external_deck:true, found {len(external)}")
ext_num = external[0]["number"]

base = PdfReader(BASE)
vision = PdfReader(VISION)

def text(p):
    return re.sub(r"\s+", " ", (p.extract_text() or "")).strip()

# The external deck goes where its own section would have been. If it is the LAST
# agenda item there is no following divider to anchor to, so it lands immediately
# before the closing slide instead.
nxt = next((i for i in items
            if i["number"] > ext_num and i.get("section_header") is not False), None)
if nxt is None:
    # Nothing after it renders a divider (it is last, or only breaks/wrap follow).
    insert_at = len(base.pages) - 1
    where = "before the closing slide"
else:
    prefix = f"{nxt['number']:02d} "
    insert_at = next((i for i, p in enumerate(base.pages) if text(p).startswith(prefix)), None)
    if insert_at is None:
        sys.exit(f"could not find the divider for agenda item {nxt['number']} (prefix {prefix!r})")
    where = f"before the item-{nxt['number']} divider"

W = float(base.pages[0].mediabox.width)
H = float(base.pages[0].mediabox.height)
sx = W / float(vision.pages[0].mediabox.width)
sy = H / float(vision.pages[0].mediabox.height)

w = PdfWriter()
for p in base.pages[:insert_at]:
    w.add_page(p)
for p in vision.pages:
    canvas = PageObject.create_blank_page(width=W, height=H)
    canvas.merge_transformed_page(p, Transformation().scale(sx, sy))
    w.add_page(canvas)
for p in base.pages[insert_at:]:
    w.add_page(p)

stem = os.path.basename(BASE).replace(".pdf", "")
out = os.path.join(MEETING, "slides/output", f"{stem} + vision.pdf")
with open(out, "wb") as fh:
    w.write(fh)

print(f"base    {os.path.basename(BASE)} ({len(base.pages)} pp)")
print(f"vision  {os.path.basename(VISION)} ({len(vision.pages)} pp, scaled x{sx:.4f})")
print(f"vision item is #{ext_num}; inserted {where}, at page {insert_at + 1}")
print(f"-> {os.path.basename(out)} ({len(w.pages)} pp)")
