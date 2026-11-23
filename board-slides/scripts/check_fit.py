"""Fail-loud fit check for the rendered deck.

WeasyPrint neither warns nor paginates when a slide's content exceeds its box:
`.slide` is height:167mm + overflow:hidden, so it silently CLIPS. Page count
alone proves nothing (board-slides SKILL.md §21). This walks the box tree and
reports, per slide, content height against that slide's own content box.

Run from the meeting folder root:  python3 slides/check_fit.py
"""
import os, sys
os.environ.setdefault("DYLD_LIBRARY_PATH", "/opt/homebrew/lib")
from weasyprint import HTML, CSS
from pathlib import Path

SLIDES = Path(__file__).resolve().parent
MM = 96 / 25.4

doc = HTML(string=(SLIDES / ".last_render.html").read_text(),
           base_url=str(SLIDES)).render(
               stylesheets=[CSS(filename=str(SLIDES / "template" / "style.css"))])

def walk(b, out=None):
    out = out if out is not None else []
    out.append(b)
    for c in getattr(b, "all_children", lambda: [])():
        walk(c, out)
    return out

print(f"pages: {len(doc.pages)}\n{'pg':>3}  {'slide':<28}{'used':>8}{'box':>8}{'slack':>8}")
over = []
spill = []
prev_el = None
for i, page in enumerate(doc.pages, 1):
    secs = [b for b in walk(page._page_box)
            if b.element is not None and b.element.tag == "section"]
    if not secs:
        continue
    s = secs[0]
    # A slide whose content cannot fit is either CLIPPED (overflow:hidden) or, for
    # display:grid/flex-wrap content, PAGINATED: WeasyPrint continues the same <section>
    # on the next page, which then looks like a small slide that fits. The 13-month
    # trends 2x2 shipped that way to the board on 2026-08-04 (SKILL.md §60). The tell is
    # that the page's first section is the SAME element as the previous page's.
    if s.element is prev_el:
        spill.append(i)
        print(f"{i:>3}  {'(continuation of p' + str(i-1) + ')':<28}{'':>8}{'':>8}{'':>8}  SPILLED")
        prev_el = secs[-1].element
        continue
    prev_el = secs[-1].element
    cls = (s.element.get("class") or "").replace("slide slide-content ", "").replace("slide ", "")
    used = sum((c.margin_height() if hasattr(c, "margin_height") else c.height)
               for c in s.all_children())
    slack = (s.height - used) / MM
    mark = "  CLIPPED" if slack < -0.5 else ("  tight" if slack < 2 else "")
    if slack < -0.5:
        over.append((i, cls, slack))
    print(f"{i:>3}  {cls:<28}{used/MM:7.1f}{s.height/MM:8.1f}{slack:+8.1f}{mark}")

if spill:
    print(f"\n{len(spill)} slide(s) spilled onto a header-less extra page: "
          + ", ".join(f"p{i-1}->p{i}" for i in spill))
if over:
    print(f"\n{len(over)} slide(s) clipped:")
    for i, cls, sl in over:
        print(f"  p{i} {cls} over by {-sl:.1f} mm")
if spill or over:
    sys.exit(1)
print("\nAll slides fit.")
