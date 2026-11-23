"""Sonetel Board Meeting deck renderer.

Pipeline:  agenda.json + data.json
        -> pydantic validate
        -> Jinja2 HTML render (template/template.html + style.css)
        -> WeasyPrint -> 16:9 landscape PDF

Run from the meeting folder root:
    python3 slides/render.py

Optional flags:
    --data <path>     override data.json
    --agenda <path>   override agenda.json
    --out <path>      override output PDF path (otherwise auto-versions v0.N.pdf)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# WeasyPrint needs Homebrew libs on macOS.
os.environ.setdefault("DYLD_LIBRARY_PATH", "/opt/homebrew/lib")

from pydantic import BaseModel, ConfigDict, Field, field_validator
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


SLIDES_DIR = Path(__file__).resolve().parent
MEETING_DIR = SLIDES_DIR.parent
TEMPLATE_DIR = SLIDES_DIR / "template"
ASSETS_DIR = SLIDES_DIR / "assets"
OUTPUT_DIR = SLIDES_DIR / "output"
CHARTS_DIR = SLIDES_DIR / "assets" / "charts"
DEFAULT_AGENDA = MEETING_DIR / "agenda" / "agenda.json"
DEFAULT_DATA = SLIDES_DIR / "data.json"

# Design-system inks (mirror style.css :root tokens)
SWA_INK = "#0a0a0a"
SWA_INK_2 = "#292929"
SWA_INK_3 = "#666666"
SWA_RULE = "#e0e0e0"
SWA_RULE_SOFT = "#f0f0f0"
# Finops Monthly Pulse chart palette
FINOPS_TEAL = "#5FA5A5"
FINOPS_TEAL_LIGHT = "#7BC4C4"
FINOPS_TEAL_DARK = "#3D7B81"
FINOPS_CHURN_RED = "#E15454"
FINOPS_CARD_BG = "#F5F5F5"


# ---------------------------------------------------------------- models

class Meeting(BaseModel):
    model_config = ConfigDict(extra="allow")
    title: str
    company: str
    meeting_number: int
    date: str
    time: str | None = None
    location: str | None = None
    language: str = "English"
    status: str = "Draft"
    attendees: list[str] = Field(default_factory=list)


class AgendaSubItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    title: str
    presenter: str | None = None
    duration_minutes: int | None = None


class AgendaItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    number: int
    title: str
    presenter: str | None = None
    duration_minutes: int | None = None
    type: str | None = None
    content_file: str | None = None
    slides_section: str | None = None
    decisions: list[str] = Field(default_factory=list)
    notes: str | None = None
    section_header: bool = True  # set false to omit this item's divider slide (item stays on the agenda)
    subitems: list[AgendaSubItem] = Field(default_factory=list)


class Agenda(BaseModel):
    meeting: Meeting
    agenda_items: list[AgendaItem]
    total_duration_minutes: int | None = None


class PnlRow(BaseModel):
    model_config = ConfigDict(extra="allow")
    label: str
    actual: float | None = None
    budget: float | None = None
    variance_abs: float | None = None
    variance_pct: float | None = None
    section_header: bool = False
    summa: bool = False


class KpiCard(BaseModel):
    model_config = ConfigDict(extra="allow")
    label: str
    value: str
    lines: list[str] = Field(default_factory=list)
    tone: str = "neutral"   # neutral | positive | negative | warn


class BreakevenBox(BaseModel):
    model_config = ConfigDict(extra="allow")
    label: str                    # "Breakeven Achieved" / "Cash Flow Positive"
    target_msek: float | None = None
    actual_msek: float | None = None
    gap_msek: float | None = None
    gap_pct: float | None = None
    status: str = "ok"            # ok | warn | critical
    rows: list[list[str]] | None = None   # preformatted [label, value] rows (CR-2026-11-03b boxes)
    scope: str | None = None


class TrendSeries(BaseModel):
    model_config = ConfigDict(extra="allow")
    title: str
    unit: str | None = None
    kind: str = "bar"             # bar | line | stacked_bar
    points: list[dict] | None = None        # [{month, value}] or with extra keys for stacked
    stacked_keys: list[str] | None = None   # for stacked_bar
    stacked_labels: list[str] | None = None   # legend labels for `stacked_keys`
    y_format: str = "auto"        # auto | thousands | percent
    color: str | None = None      # hex override (defaults to FINOPS_TEAL)
    baseline: float | None = None  # draw a horizontal reference line and fill to it
    figsize: tuple[float, float] | None = None  # (width_in, height_in) override
    # Named thresholds drawn across the plot. On vertical charts they are
    # horizontal lines; on `hbar` they are vertical. Each entry:
    #   {value, label?, color?, style?}   style: "dashed" (default) | "solid"
    reference_lines: list[dict] | None = None
    # Shaded band between two values (e.g. "where we are today: 103-105").
    #   {from, to, label?, color?}
    band: dict | None = None
    # Per-point emphasis for bar/hbar. A point may carry "tone":
    #   "primary" (dark teal) | "muted" (grey) | "warn" (red) | default light teal
    value_label_fmt: str | None = None   # e.g. "{v:+.2f}%" ; defaults per y_format


class CashImpactItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    label: str
    amount_sek: float
    note: str | None = None


class NumberedEntry(BaseModel):
    model_config = ConfigDict(extra="allow")
    text: str
    badge: str | None = None
    badge_tone: str = "neutral"   # positive | warn | info | neutral


class ArrSummaryRow(BaseModel):
    model_config = ConfigDict(extra="allow")
    label: str
    documented_arr_usd: float | None = None       # ARR from documented mechanism customers (12mo)
    silent_per_documented: float | None = None    # silent cohort customers per 1 documented (= 1/contact_rate − 1)
    viable_silent_pct: float | None = None        # operator estimate of % of silent the fix would also save


class MechanismRow(BaseModel):
    model_config = ConfigDict(extra="allow")
    label: str
    customers: int | None = None                # raw count of customers in this cohort exhibiting this mechanism
    pct_of_bucket: float | None = None          # mechanism customers / sample size × 100
    solvable: bool | None = None                # Yes / No
    arr_usd: float | None = None                # annual ARR realistic (USD); None or 0 → shown as "—"
    # Legacy fields (kept optional for backward compat with prior data.json shapes)
    cohort_loss_pct: float | None = None
    pct_of_identified: float | None = None


class DataTableColumn(BaseModel):
    model_config = ConfigDict(extra="allow")
    label: str
    align: str = "right"          # left | right | center


class DataTableRow(BaseModel):
    model_config = ConfigDict(extra="allow")
    cells: list[str]
    emphasis: bool = False        # bold the row (the row the board should read first)


class Slide(BaseModel):
    model_config = ConfigDict(extra="allow")
    type: str
    title: str | None = None
    subtitle: str | None = None
    # Generic data table (price tables, competitor comparisons, sensitivity)
    columns: list[DataTableColumn] | None = None
    rows: list[DataTableRow] | None = None

    @field_validator("columns", mode="before")
    @classmethod
    def _coerce_columns(cls, v):
        # accept plain strings; first column defaults to left-aligned, the rest right
        if v is None:
            return None
        out = []
        for i, c in enumerate(v):
            c = {"label": c} if isinstance(c, str) else dict(c)
            c.setdefault("align", "left" if i == 0 else "right")
            out.append(c)
        return out

    @field_validator("rows", mode="before")
    @classmethod
    def _coerce_rows(cls, v):
        # accept plain lists of cells, or {"cells": [...], "emphasis": bool}
        if v is None:
            return None
        return [{"cells": [str(x) for x in r]} if isinstance(r, list) else r for r in v]

    bullets: list[dict] | None = None  # each: {"text": str, "label"?: str} — label rendered bold
    left: list[str] | None = None
    right: list[str] | None = None
    entries: list[NumberedEntry] | None = None
    quote: str | None = None

    @field_validator("entries", mode="before")
    @classmethod
    def _coerce_entries(cls, v):
        if v is None:
            return None
        return [{"text": item} if isinstance(item, str) else item for item in v]

    @field_validator("bullets", mode="before")
    @classmethod
    def _coerce_bullets(cls, v):
        # accept plain strings or {"label","text"} dicts; a bold "label" prefixes the text
        if v is None:
            return None
        return [{"text": item} if isinstance(item, str) else item for item in v]
    attribution: str | None = None
    image: str | None = None
    notes: str | None = None
    # Mechanism table (churn/conversion analysis)
    mechanism_rows: list[MechanismRow] | None = None
    mechanism_columns: list[str] | None = None
    caveat: str | None = None
    # ARR summary table (per-bucket recoverable ARR with silent-bounce sensitivity)
    arr_summary_rows: list[ArrSummaryRow] | None = None
    summary_takeaway: str | None = None
    # Financial slide fields
    pnl_rows: list[PnlRow] | None = None
    pnl_columns: list[str] | None = None
    kpis: list[KpiCard] | None = None
    breakeven_boxes: list[BreakevenBox] | None = None
    breakeven_note: str | None = None
    trends: list[TrendSeries] | None = None
    cash_trend: TrendSeries | None = None
    cash_drivers: list[CashImpactItem] | None = None
    drivers_title: str | None = None
    # Cash flow forecast slide fields (populated by expand_data_refs)
    cashflow_chart_path: str | None = None
    cashflow_top_items: list[dict[str, Any]] | None = None
    cashflow_summary: dict[str, Any] | None = None


class DeckMeta(BaseModel):
    model_config = ConfigDict(extra="allow")
    cover_subtitle: str | None = None
    cover_date_label: str | None = None
    closing_message: str | None = "Thank you"


class Deck(BaseModel):
    meta: DeckMeta = Field(default_factory=DeckMeta)
    items: dict[str, list[Slide]] = Field(default_factory=dict)


# ---------------------------------------------------------------- helpers

def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def expand_data_refs(raw: dict) -> dict:
    """Walk slides; for slides with `data_ref`, load the file and transform
    the source data into the slide-type's expected fields. Path is relative
    to the meeting folder (one level above slides/)."""
    for slides in (raw.get("items") or {}).values():
        for slide in slides or []:
            ref = slide.get("data_ref")
            if not ref:
                continue
            src = json.loads((MEETING_DIR / ref).read_text(encoding="utf-8"))
            stype = slide.get("type")

            if stype in ("trends_grid", "chart_comment"):
                series = src.get("series", {})
                trends = []
                for spec in slide.get("trends_layout", []):
                    t = {
                        "title": spec["title"],
                        "kind": spec.get("kind", "bar"),
                        "y_format": spec.get("y_format", "auto"),
                    }
                    # Presentation-only keys pass straight through from the layout
                    # spec to the series. Kept as a whitelist so a typo in data.json
                    # surfaces as a missing feature, not as a silently-extra field.
                    for k in ("figsize", "show_values", "value_labels_inside",
                              "color", "baseline", "reference_lines", "band",
                              "value_label_fmt", "unit", "stacked_labels"):
                        if spec.get(k) is not None:
                            t[k] = spec[k]
                    if t["kind"] in ("stacked_bar", "flow"):
                        keys = spec["keys"]
                        months = [p["month"] for p in series[keys[0]]]
                        points = []
                        for i, m in enumerate(months):
                            point = {"month": m}
                            for k in keys:
                                point[k] = series[k][i]["value"]
                            points.append(point)
                        t["points"] = points
                        t["stacked_keys"] = keys
                    else:
                        t["points"] = series[spec["key"]]
                    # Optional per-chart window trim. Needed when one series in a grid has a
                    # shorter TRUSTWORTHY history than its neighbours — e.g. new_visitors comes
                    # from ab_page_views (95-day purge, so the oldest month is truncated and
                    # degrades daily) while the conversion series comes from ab_conversions
                    # (365-day retention) and is fine further back. Trim the affected chart
                    # only, rather than throwing away good data on the others.
                    if spec.get("from_month"):
                        t["points"] = [p for p in t["points"] if p["month"] >= spec["from_month"]]
                    trends.append(t)
                # A 2x2 grid of default-shaped charts is ~150mm tall against ~106mm of room:
                # WeasyPrint paginates the grid and the bottom row lands on a header-less page.
                # The 13-month trends slide shipped that way to the board on 2026-08-04. A
                # 118mm-wide image may be at most ~34mm tall once card padding and the
                # rotated month labels are counted (2.25 still clipped by 12.6mm), so give
                # 2x2 charts a flat shape unless the layout sets one (SKILL.md §60).
                if len(trends) == 4:
                    # 2x2 charts are height-capped at ~34mm by fitting two rows (44mm clipped both
                    # 4-chart slides). Don't spend the full 118mm card width on that: 118x34 is
                    # 3.5:1 and flattens every trend (Henrik, 2026-09-10). 88mm wide keeps the
                    # height and gives 2.6:1 — the CSS width for .cols-2.rows-2 matches.
                    for t in trends:
                        t.setdefault("figsize", [5.2, 1.95])
                slide["trends"] = trends

            elif stype == "cash_position":
                slide["cash_trend"] = {
                    "title": "EOM Cash Position",
                    "kind": "line",
                    "y_format": "thousands_sek",
                    "color": "#2647A8",
                    "baseline": 0,
                    # 2.75, not 3.2: at the card's fixed 127mm width a 3.2-high chart made the
                    # slide 7.2mm too tall (hidden until the width:100% mis-measure was fixed, §60)
                    "figsize": [5.5, 2.75],
                    "points": src.get("trend", []),
                }
                slide["cash_drivers"] = src.get("april_drivers", []) or []

            elif stype == "cash_flow_forecast":
                slide["cashflow_source"] = src

            elif stype == "ir_calendar":
                f = slide.get("ir_filter") or {}
                from_d = f.get("from_date") or "0000-01-01"
                to_d = f.get("to_date") or "9999-12-31"
                inc_types = set(f.get("include_types") or [])
                exc_types = set(f.get("exclude_types") or [])
                inc_tags = set(f.get("include_tags") or [])
                # Headline language preference: 'sv' (Swedish-primary, IR canon) or 'en'
                headline_lang = (f.get("headline_lang") or "sv").lower()
                # Match the canonical HTML view: hide non-active items unless overridden
                exc_statuses = set(f.get("exclude_statuses") or ["done", "cancelled", "deferred"])
                exclude_placeholders = f.get("exclude_placeholders", False)
                MONTHS_SHORT = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
                MONTHS_LONG = ["January","February","March","April","May","June","July","August","September","October","November","December"]
                events = []
                for a in src.get("activities") or []:
                    sd = a.get("start_date") or ""
                    if not (from_d <= sd <= to_d):
                        continue
                    a_type = a.get("type")
                    if a_type in exc_types:
                        continue
                    if a.get("status") in exc_statuses:
                        continue
                    if exclude_placeholders and a.get("confidence") == "placeholder":
                        continue
                    a_tags = set(a.get("tags") or [])
                    if inc_types and a_type not in inc_types and not (a_tags & inc_tags):
                        continue
                    is_flag = "flagship" in a_tags
                    is_blackout = a_type == "blackout"
                    is_financial = a_type == "disclosure" and "financial-report" in a_tags
                    is_internal = a_type in {"ops", "decision", "subscription-renewal"}
                    if is_blackout:
                        kind = "quiet"
                    elif is_flag:
                        kind = "flag"
                    elif a_type == "disclosure":
                        kind = "reg"
                    else:
                        kind = "other"
                    try:
                        y, mth, dy = sd.split("-")
                        date_short = f"{MONTHS_SHORT[int(mth)-1]} {int(dy)}"
                        month_key = f"{y}-{mth}"
                        month_label = f"{MONTHS_LONG[int(mth)-1]} {y}"
                    except Exception:
                        date_short = sd
                        month_key = sd[:7]
                        month_label = sd[:7]
                    end = a.get("end_date")
                    if end and end != sd:
                        try:
                            ey, em, ed = end.split("-")
                            date_short = f"{date_short} → {MONTHS_SHORT[int(em)-1]} {int(ed)}"
                        except Exception:
                            date_short = f"{sd} → {end}"
                    # Prefer publication-ready headlines; fall back to internal title
                    h_sv = (a.get("headline_sv") or "").strip()
                    h_en = (a.get("headline_en") or "").strip()
                    if headline_lang == "en":
                        title = h_en or h_sv
                    else:
                        title = h_sv or h_en
                    if not title:
                        title = a.get("title") or ""
                        for prefix in ("CEO LinkedIn post — ", "Monthly hub post — "):
                            if title.startswith(prefix):
                                title = title[len(prefix):]
                                break
                        for suffix in (" — flagship product launch", " — flagship event", " — flagship",
                                       " — hub post + Kristina-candidate pitch", " — hub post"):
                            if title.endswith(suffix):
                                title = title[:-len(suffix)]
                                break
                    title = title.strip().strip('"').strip()
                    events.append({
                        "start_date": sd,
                        "date_short": date_short,
                        "month_key": month_key,
                        "month_label": month_label,
                        "title": title,
                        "kind": kind,
                        "is_flag": is_flag,
                        "is_internal": is_internal,
                        "is_financial": is_financial,
                    })
                events.sort(key=lambda e: e["start_date"])
                groups = []
                current = None
                for e in events:
                    if current is None or current["key"] != e["month_key"]:
                        current = {"key": e["month_key"], "label": e["month_label"], "events": []}
                        groups.append(current)
                    current["events"].append(e)
                # Partition month-groups into N columns (target equal "weight" per column,
                # where weight ≈ header + events). Keeps months unsplit across columns.
                n_cols = int(f.get("columns") or 3)
                weights = [1 + len(g["events"]) for g in groups]  # header + events
                total = sum(weights) or 1
                target = total / n_cols
                cols = [[] for _ in range(n_cols)]
                ci, running = 0, 0
                for g, w in zip(groups, weights):
                    if ci < n_cols - 1 and running + w / 2 > target:
                        ci += 1
                        running = 0
                    cols[ci].append(g)
                    running += w
                slide["ir_columns"] = cols
                slide.pop("ir_groups", None)

            slide.pop("data_ref", None)
            slide.pop("trends_layout", None)
            slide.pop("ir_filter", None)
    return raw


def next_versioned_path(filename_prefix: str) -> Path:
    """Find the next v0.N.pdf for the given prefix (derived from agenda)."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe = re.escape(filename_prefix)
    # Match ANY prefix, not just today's: when the prefix changes (e.g. "#" stripped for Teams,
    # 2026-09-12) a prefix-bound regex restarts numbering at v0.1, which then sorts as older
    # than v0.105 and merge_deck picks the wrong base.
    pattern = re.compile(r" v0\.(\d+)\.pdf$")
    existing = [int(m.group(1)) for p in OUTPUT_DIR.iterdir() if (m := pattern.search(p.name))]
    n = (max(existing) + 1) if existing else 1
    return OUTPUT_DIR / f"{filename_prefix} v0.{n}.pdf"


def derive_filename_prefix(agenda) -> str:
    # Teams (SharePoint) refuses \ / : * ? " < > | # % in a filename, and the meeting title
    # carries a "#" ("Board Meeting #8") — Henrik could not upload the deck (2026-09-12).
    # Strip those characters from the FILENAME only; the cover keeps the title as written.
    name = f"Sonetel {agenda.meeting.title} {format_date(agenda.meeting.date)}"
    return re.sub(r"\s{2,}", " ", re.sub(r'[\\/:*?"<>|#%]', "", name)).strip()


def prepare_growth_stack(slide: dict) -> None:
    """Size each block of a growth stack in mm, proportional to what it is worth.

    The whole point of the slide is that block SIZE = growth, so the geometry is
    computed from the values rather than authored. A minimum height keeps the
    smallest opportunity legible without letting it lie about its size.
    """
    blocks = slide.get("blocks") or []
    if not blocks:
        return
    total_mm = float(slide.get("stack_height_mm", 84))
    min_mm = 9.0
    vals = [max(0.0, float(b["value"])) for b in blocks]
    gross = sum(vals) or 1.0

    # Give every block its proportional share, then lift any below the legibility
    # floor and take the difference back off the blocks that can afford it.
    heights = [total_mm * v / gross for v in vals]
    deficit = sum(max(0.0, min_mm - h) for h in heights)
    surplus = sum(h - min_mm for h in heights if h > min_mm) or 1.0
    out = []
    for h in heights:
        out.append(min_mm if h < min_mm else h - (h - min_mm) * deficit / surplus)
    for b, h, v in zip(blocks, out, vals):
        b["height_mm"] = f"{h:.1f}"
        b["pct_label"] = b.get("pct_label") or f"+{v:.2f}%".rstrip("0").rstrip(".")
    slide["stack_total"] = f"+{sum(vals):.2f}%".rstrip("0").rstrip(".")


def prepare_orbit(slide: dict) -> None:
    """Concentric rings around the phone number, ordered by distance from it.

    The distance metric is the strategy's own: a call is zero hops from the
    number, an online meeting is one, a conversation in the room is one, a
    note-taking app is none. Ring radius therefore encodes something real —
    how far a capability sits from the asset we own — rather than being drawn
    to look tidy.
    """
    rings = slide.get("rings") or []
    core_r = float(slide.get("core_radius", 21))
    step = float(slide.get("ring_step", 15.5))
    cx = cy = float(slide.get("centre", 92))
    slide["cx"] = f"{cx:.1f}"
    slide["cy"] = f"{cy:.1f}"
    slide["core_r"] = f"{core_r:.1f}"
    for i, r in enumerate(rings):
        radius = core_r + step * (i + 1)
        r["r"] = f"{radius:.1f}"
        r["label_y"] = f"{cy - radius + 5.2:.1f}"   # sits just inside the ring, at the top
        r["index"] = i + 1


def prepare_knobs(slide: dict) -> None:
    """Turn each knob's `fill` (0..1) into SVG arc + needle geometry.

    An amplifier dial: a 270-degree track from 7 o'clock round to 5 o'clock, a
    coloured arc showing how far this lever is turned up, and a needle. The maths
    lives here so the template stays declarative.
    """
    import math
    R, CX, CY = 34.0, 40.0, 40.0
    START, SWEEP = 135.0, 270.0

    def pt(deg):
        r = math.radians(deg)
        return CX + R * math.cos(r), CY + R * math.sin(r)

    for k in slide.get("knobs") or []:
        fill = max(0.0, min(1.0, float(k.get("fill", 0.5))))
        end = START + SWEEP * fill
        x0, y0 = pt(START)
        x1, y1 = pt(end)
        xe, ye = pt(START + SWEEP)
        k["track_path"] = f"M {x0:.2f} {y0:.2f} A {R} {R} 0 1 1 {xe:.2f} {ye:.2f}"
        k["fill_path"] = f"M {x0:.2f} {y0:.2f} A {R} {R} 0 {1 if SWEEP*fill > 180 else 0} 1 {x1:.2f} {y1:.2f}"
        nx, ny = pt(end)
        k["needle_x"] = f"{CX + (nx - CX) * 0.60:.2f}"
        k["needle_y"] = f"{CY + (ny - CY) * 0.60:.2f}"


def build_slide_sequence(agenda: Agenda, deck: Deck) -> list[dict[str, Any]]:
    """Flatten cover + agenda + (section + content) per item + closing."""
    seq: list[dict[str, Any]] = []

    cover_subtitle = deck.meta.cover_subtitle
    if not cover_subtitle:
        loc = agenda.meeting.location
        if loc and loc.upper() != "TBD":
            cover_subtitle = loc

    seq.append({
        "page_class": "cover",
        "type": "cover",
        "title": agenda.meeting.company,
        "heading": agenda.meeting.title,
        "subtitle": cover_subtitle,
        "date_label": deck.meta.cover_date_label or format_date(agenda.meeting.date),
    })

    any_duration = any(
        (item.duration_minutes or any(sub.duration_minutes for sub in item.subitems))
        for item in agenda.agenda_items
    )

    # Start times: run the clock from meeting.time through the item durations, and through the
    # subitem durations inside each item. A board reads "when does the vision start", not "how many
    # minutes is item 13" (Henrik, 2026-09-12). Falls back to durations if meeting.time is unusable.
    agenda_rows = [item.model_dump() for item in agenda.agenda_items]
    clock = None
    mtime = getattr(agenda.meeting, "time", None)
    if isinstance(mtime, str) and re.fullmatch(r"\d{1,2}:\d{2}", mtime.strip()):
        h, m = (int(x) for x in mtime.strip().split(":"))
        clock = h * 60 + m
    if clock is not None:
        fmt = lambda t: f"{(t // 60) % 24:02d}:{t % 60:02d}"
        for row in agenda_rows:
            row["start_time"] = fmt(clock)
            sub_clock = clock
            for sub in row.get("subitems") or []:
                sub["start_time"] = fmt(sub_clock)
                sub_clock += sub.get("duration_minutes") or 0
            clock += row.get("duration_minutes") or 0
        end_time = fmt(clock)
    else:
        end_time = None

    # Items keyed "0" are opening slides (e.g. "Key messages"): after the cover, before the
    # agenda, no section divider, eyebrow "Summary" (Henrik, 2026-11-03).
    for slide in deck.items.get("0", []):
        seq.append({**slide.model_dump(), "page_class": "content",
                    "agenda_number": None, "agenda_title": "Summary"})

    seq.append({
        "page_class": "agenda",
        "type": "agenda",
        "title": "Agenda",
        "agenda_items": agenda_rows,
        "total_minutes": agenda.total_duration_minutes,
        "end_time": end_time,
        "show_time": any_duration,
    })

    for item in agenda.agenda_items:
        if item.section_header:
            seq.append({
                "page_class": "section",
                "type": "section",
                "number": item.number,
                "title": item.title,
                "presenter": item.presenter,
                "duration_minutes": item.duration_minutes,
                "subitems": [sub.model_dump() for sub in item.subitems],
            })
        item_slides = deck.items.get(str(item.number), [])
        for slide in item_slides:
            # Keep None values so templates can use `is not none` checks
            seq.append({
                "page_class": "content",
                "type": slide.type,
                "agenda_number": item.number,
                "agenda_title": item.title,
                **slide.model_dump(),
            })

    seq.append({
        "page_class": "closing",
        "type": "closing",
        "message": deck.meta.closing_message or "Thank you",
        "company": agenda.meeting.company,
    })
    return seq


SWEDISH_MONTHS = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December",
}

MONTH_ABBREV = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
    "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
}


def format_date(iso: str) -> str:
    """2026-05-21 -> May 21, 2026"""
    try:
        y, m, d = iso.split("-")
        return f"{SWEDISH_MONTHS[m]} {int(d)}, {y}"
    except Exception:
        return iso


def month_short(iso: str) -> str:
    """2026-04 -> Apr 26; 2026-07-13 (a week bucket) -> 13 Jul"""
    try:
        parts = iso.split("-")
        if len(parts) == 3:                      # weekly bucket: day + month, no year
            return f"{int(parts[2])} {MONTH_ABBREV[parts[1]]}"
        y, m = parts[:2]
        return f"{MONTH_ABBREV[m]} {y[2:]}"
    except Exception:
        return iso


# ---------------------------------------------------------------- chart rendering

def _style_axes(ax):
    """Apply Finops Monthly Pulse styling to a matplotlib axes."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#D0D0D0")
    ax.spines["bottom"].set_linewidth(0.6)
    ax.tick_params(axis="y", colors="#666666", labelsize=8.5, length=0, pad=4)
    ax.tick_params(axis="x", colors="#666666", labelsize=8.5, length=0, pad=4)
    ax.grid(axis="y", color="#EAEAEA", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)


def _format_y(ax, fmt: str, values: list[float]):
    if fmt == "percent":
        # :g, not :.1f — matplotlib picks 0.25 steps on a narrow range, and one fixed
        # decimal printed 1.75 as "1.8%" and 0.25 as "0.2%" (§58).
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{round(v, 3):g}%"))
        return
    if fmt == "thousands":
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v/1000)}K"))
        return
    if fmt == "count":
        # plain integers for counts in the low thousands (2,686 must not read "2K" or "$2K")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}".replace(",", " ")))
        return
    if fmt == "ratio":
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}×"))
        return
    if fmt == "thousands_sek":
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v/1000):+,d}K".replace(",", " ").replace("+0K", "0K")))
        return
    if fmt == "msek":
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1_000_000:.1f} MSEK"))
        return
    if fmt == "usd_k":
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${int(v/1000)}K"))
        return
    if fmt == "usd_m":
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1_000_000:.1f}M"))
        return
    if fmt == "k":
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v/1000)}K"))
        return
    # auto
    if not values:
        return
    m = max(abs(v) for v in values if v is not None)
    if m >= 1_000_000:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1_000_000:.1f}M" if abs(v) >= 1_000_000 else f"${int(v/1000)}K"))
    elif m >= 1000:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${int(v/1000)}K"))


TONE_COLORS = {
    "primary": FINOPS_TEAL_DARK,
    "muted":   "#C9C9C9",
    "warn":    FINOPS_CHURN_RED,
    "neutral": FINOPS_TEAL_LIGHT,
}


def _point_colors(points: list[dict], default: str) -> list[str]:
    return [TONE_COLORS.get(p.get("tone") or "", default) for p in points]


def _value_label(v: float, y_format: str, fmt: str | None) -> str:
    if fmt:
        return fmt.format(v=v)
    if y_format == "percent":
        return f"{v:+.2f}%".rstrip("0").rstrip(".") if abs(v) < 10 else f"{v:.1f}%"
    if y_format in ("thousands", "k"):
        return f"{v/1000:.0f}K"
    if y_format == "count":
        return f"{v:,.0f}".replace(",", " ")
    if y_format == "ratio":
        return f"{v:.1f}×"
    if y_format == "usd_m":
        return f"${v/1_000_000:.2f}M"
    return f"{v:,.0f}".replace(",", " ")


def _draw_reference_lines(ax, series: TrendSeries, horizontal: bool) -> None:
    """Draw a shaded band and/or named thresholds.

    `horizontal=True` -> axhline/axhspan (vertical charts); False -> the vertical
    equivalents (hbar). Labels get their own reserved margin rather than sitting
    over the data: two thresholds a few units apart otherwise collide with each
    other and with the bars.
    """
    band = series.band
    refs = series.reference_lines or []
    wants_label = bool((band or {}).get("label")) or any(r.get("label") for r in refs)

    label_x = None
    if horizontal and wants_label:
        x0, x1 = ax.get_xlim()
        label_x = x1
        ax.set_xlim(x0, x1 + (x1 - x0) * 0.55)

    if band:
        lo, hi = float(band["from"]), float(band["to"])
        col = band.get("color") or "#BFD9D9"
        (ax.axhspan if horizontal else ax.axvspan)(lo, hi, color=col, alpha=0.55, zorder=0.4)
        if band.get("label"):
            if horizontal:
                # Anchor to the band's TOP edge and grow upward. A multi-line label
                # centred on a band only a few units tall spills across it and over
                # its own boundary lines.
                va = band.get("label_va", "bottom")
                ax.annotate(band["label"], xy=(label_x, hi if va == "bottom" else lo),
                            xycoords="data", xytext=(8, 2 if va == "bottom" else -2),
                            textcoords="offset points",
                            fontsize=9.5, color=band.get("label_color", "#3D7B81"),
                            va=va, ha="left", linespacing=1.4, zorder=6)
            else:
                ax.annotate(band["label"], xy=((lo + hi) / 2, 1.0),
                            xycoords=("data", "axes fraction"),
                            xytext=(0, 5), textcoords="offset points",
                            fontsize=9.5, color=band.get("label_color", "#3D7B81"),
                            va="bottom", ha="center", zorder=6)

    for ref in refs:
        val = float(ref["value"])
        col = ref.get("color") or "#333333"
        solid = ref.get("style") == "solid"
        style = "-" if solid else (0, (4, 3))
        if horizontal:
            ax.axhline(val, color=col, linewidth=1.1, linestyle=style, zorder=4)
        else:
            ax.axvline(val, color=col, linewidth=1.1, linestyle=style, zorder=4)
        if not ref.get("label"):
            continue
        if horizontal:
            ax.annotate(ref["label"], xy=(label_x, val), xycoords="data",
                        xytext=(8, 0), textcoords="offset points",
                        fontsize=9.5, color=col, ha="left",
                        va=ref.get("label_va", "center"), linespacing=1.35, zorder=6)
        else:
            ax.annotate(ref["label"], xy=(val, 1.0), xycoords=("data", "axes fraction"),
                        xytext=(0, 5), textcoords="offset points",
                        bbox=dict(facecolor=FINOPS_CARD_BG, edgecolor="none", pad=1.5),
                        fontsize=9.5, color=col, va="bottom", ha="center", zorder=6)


def render_chart(series: TrendSeries, out_path: Path, dpi: int = 200) -> Path:
    """Render a single trend chart in Finops Monthly Pulse style.

    Use bbox_inches="tight" so the saved PNG = chart content (no figsize
    whitespace). figsize controls the relative size of axis labels vs bars.
    CSS sizes the displayed image at the card's natural width.
    """
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    figsize = series.figsize or (5.0, 2.7)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    fig.patch.set_facecolor(FINOPS_CARD_BG)
    ax.set_facecolor(FINOPS_CARD_BG)

    pts = series.points or []
    x = list(range(len(pts)))
    # A point is keyed either by `month` (time series -> "Jul 26" labels) or by
    # `label` (categorical -> used verbatim). Mixing them in one series is a bug.
    labels = [month_short(p["month"]) if "month" in p else str(p.get("label", "")) for p in pts]

    if series.kind == "hbar":
        return _render_hbar(series, pts, fig, ax, out_path, dpi)

    if series.kind == "stacked_bar" and series.stacked_keys:
        bottoms = [0.0] * len(x)
        # 6-colour palette: a stack can carry more than the original two subscription
        # series (e.g. signup sources). Labels come from the layout's `stacked_labels`
        # when given, else the two subscription defaults, else the raw key.
        colors = [FINOPS_TEAL_DARK, FINOPS_TEAL_LIGHT, "#2647A8", "#9F6A20",
                  FINOPS_CHURN_RED, "#C9C9C9", "#E5E5E5"]
        nice_labels = series.stacked_labels or ["With subscription", "Without subscription"]
        for i, k in enumerate(series.stacked_keys):
            vals = [(p.get(k) or 0) for p in series.points]
            ax.bar(x, vals, bottom=bottoms, color=colors[i % len(colors)],
                   width=0.72, label=nice_labels[i] if i < len(nice_labels) else k, zorder=2)
            bottoms = [b + v for b, v in zip(bottoms, vals)]
        # 2 series fit on one line at the top right; more (e.g. 7 signup sources) need a wider
        # grid above the plot or the last entries land on top of the bars.
        n_keys = len(series.stacked_keys)
        ax.legend(loc="lower right", frameon=False, fontsize=7 if n_keys > 4 else 7.5,
                  labelcolor="#444444", handlelength=1.2,
                  ncol=4 if n_keys > 4 else 2,
                  bbox_to_anchor=(1.0, 1.01), borderaxespad=0.0)
        flat = []
        for p in series.points:
            flat.append(sum((p.get(k) or 0) for k in series.stacked_keys))
        _format_y(ax, series.y_format, flat)
    elif series.kind == "flow" and series.stacked_keys:
        # "Paying customers with subscriptions" (Henrik 2026-11-09, his Excel chart rebuilt from
        # Finops): keys = [net, new, lost]. Net = green columns with whole-number labels; new =
        # blue line, lost (churn) = red line, one shared y-axis.
        k_net, k_new, k_lost = series.stacked_keys[:3]
        names = series.stacked_labels or ["Net increase per day", "New paying customers per day",
                                          "Lost customers per day (churn)"]
        net = [p.get(k_net) or 0 for p in pts]
        newv = [p.get(k_new) for p in pts]
        lost = [p.get(k_lost) for p in pts]
        ax.bar(x, net, color="#8DB255", width=0.5, zorder=2, label=names[0])
        ax.axhline(0, color="#BBBBBB", linewidth=0.8, zorder=1)
        ax.plot(x, newv, color="#2F6DB5", linewidth=2.2, zorder=3, label=names[1])
        ax.plot(x, lost, color="#C0392B", linewidth=2.2, zorder=3, label=names[2])
        span = max(max(newv + lost), 1) - min(min(net), 0)
        for xi, v in zip(x, net):
            off = span * 0.025
            ax.text(xi, v + off if v >= 0 else v - off, f"{v:.0f}", ha="center",
                    va="bottom" if v >= 0 else "top", fontsize=8, color="#333333", zorder=4)
        ax.margins(y=0.08)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False,
                  fontsize=8, labelcolor="#444444", handlelength=1.6)
    elif series.kind == "line":
        # Coerce null -> nan (NOT 0) so a leading/embedded gap breaks the line
        # rather than crashing ax.plot/fill_between (which reject Python None).
        vals = [(p.get("value") if p.get("value") is not None else float("nan"))
                for p in series.points]
        # Auto-color: red for percent (churn), teal otherwise
        color = series.color or (FINOPS_CHURN_RED if series.y_format == "percent" else FINOPS_TEAL_LIGHT)
        fill_color = color
        if series.baseline is not None:
            ax.axhline(series.baseline, color="#D0D0D0", linewidth=0.8, zorder=0.5)
            ax.fill_between(x, vals, series.baseline, color=fill_color, alpha=0.18, zorder=1)
        else:
            ax.fill_between(x, vals, color=fill_color, alpha=0.18, zorder=1)
        ax.plot(x, vals, color=color, linewidth=2.0, zorder=2)
        ax.scatter(x, vals, color=color, s=22, zorder=3, edgecolor="white", linewidth=1.2)
        _format_y(ax, series.y_format, [v for v in vals if v == v])  # v==v drops nan
    else:  # bar
        color = series.color or FINOPS_TEAL_LIGHT
        vals = [p.get("value") or 0 for p in pts]
        ax.bar(x, vals, color=_point_colors(pts, color), width=0.72, zorder=2)
        if getattr(series, "show_values", False):
            # Labels sit ABOVE the bar by default. Set `value_labels_inside` when a
            # reference line or band sits close to the bar tops — otherwise the
            # labels land on top of it and both become unreadable.
            inside = bool(getattr(series, "value_labels_inside", False))
            if not inside:
                ax.margins(y=0.16)  # headroom so bar labels aren't clipped
            for xi, v in zip(x, vals):
                if v:
                    lbl = (f"{v:.0f}%" if series.y_format == "percent"
                           else f"{v/1000:.0f}K" if series.y_format in ("thousands", "k")
                           else f"{v:.1f}×" if series.y_format == "ratio"
                           else f"{v:,.0f}")
                    if inside:
                        ax.text(xi, v, lbl, ha="center", va="top",
                                fontsize=9, color="#3A3A3A", zorder=3,
                                bbox=dict(facecolor="none", edgecolor="none", pad=1.5))
                    else:
                        ax.text(xi, v, lbl, ha="center", va="bottom",
                                fontsize=9, color="#333333", zorder=3)
        _format_y(ax, series.y_format, vals)

    _draw_reference_lines(ax, series, horizontal=True)

    ax.set_xticks(x)
    rot = 45 if any("month" in p for p in pts) else 0
    ax.set_xticklabels(labels, rotation=rot, ha="right" if rot else "center", fontsize=8)
    _style_axes(ax)

    fig.tight_layout(pad=0.3)
    fig.savefig(out_path, facecolor=FINOPS_CARD_BG, dpi=dpi,
                bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    return out_path


def _render_hbar(series: TrendSeries, pts: list[dict], fig, ax, out_path: Path, dpi: int) -> Path:
    """Horizontal bars for CATEGORICAL comparisons — lever sizes, sensitivity
    ladders, option grids. Categories read top-to-bottom in the order given,
    which is why the y-axis is inverted rather than the list reversed.

    Long category names are why this exists: a vertical bar chart puts them on
    the x-axis where they rotate 45 degrees and become unreadable on a slide.
    """
    labels = [str(p.get("label", "")) for p in pts]
    vals = [float(p.get("value") or 0) for p in pts]
    y = list(range(len(pts)))

    ax.barh(y, vals, color=_point_colors(pts, series.color or FINOPS_TEAL_LIGHT),
            height=0.62, zorder=2)

    span = max([abs(v) for v in vals] or [1])
    for yi, v, pt in zip(y, vals, pts):
        ax.text(v + span * 0.02, yi, _value_label(v, series.y_format, series.value_label_fmt),
                va="center", ha="left", fontsize=11.5, color="#333333",
                fontweight="medium" if pt.get("tone") == "primary" else "normal", zorder=3)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=11, color="#333333")
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.margins(x=0.18)

    _draw_reference_lines(ax, series, horizontal=False)

    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=6)
    ax.grid(False)

    fig.tight_layout(pad=0.3)
    fig.savefig(out_path, facecolor=FINOPS_CARD_BG, dpi=dpi,
                bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    return out_path


def render_growth_waterfall(spec: dict, out_path: Path, dpi: int = 200) -> Path:
    """A waterfall on a real growth axis: where we are, each lever, where we land.

    Replaces a stacked block chart whose total floated with no baseline. Today's
    growth is a RANGE, so it is drawn as a range bar rather than a point — the
    uncertainty in the starting position is wider than three of the four levers.
    """
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    steps = spec.get("steps") or []
    start_lo = float(spec["start_lo"]); start_hi = float(spec["start_hi"])

    labels = [spec.get("start_label", "Where we are now")]
    fig, ax = plt.subplots(figsize=tuple(spec.get("figsize", (11.0, 3.6))), dpi=dpi)
    fig.patch.set_facecolor(FINOPS_CARD_BG); ax.set_facecolor(FINOPS_CARD_BG)

    W = 0.62
    ax.bar(0, start_hi - start_lo, bottom=start_lo, width=W, color="#B9B9B9", zorder=2)
    ax.text(0, start_hi + 0.25, f"{start_lo:+.1f} to {start_hi:+.1f}%", ha="center",
            va="bottom", fontsize=10, color="#444444", zorder=3)

    # Increments build from the FLAT line, not from either end of today's range.
    # Stacking them on start_hi traced the optimistic path, while the total was
    # drawn from start_lo — so the last lever appeared to deliver nothing.
    running = 0.0
    for i, s in enumerate(steps, start=1):
        v = float(s["value"])
        ax.bar(i, v, bottom=running, width=W,
               color=s.get("color", FINOPS_TEAL_DARK), zorder=2)
        ax.text(i, running + v + 0.25, f"+{v:.1f}", ha="center", va="bottom",
                fontsize=11, color="#333333", fontweight="medium", zorder=3)
        # connector to the next step
        ax.plot([i - W / 2 - 0.06, i + W / 2 + 0.06], [running, running],
                color="#C4C4C4", linewidth=0.8, zorder=1)
        running += v
        labels.append(s["label"])

    total = running
    n = len(steps) + 1
    # The result column rises from zero to the sum, so every increment visibly
    # contributes to it and the destination is the tallest thing on the chart.
    ax.bar(n, total, bottom=0, width=W, color="#2F6E74", zorder=2)
    ax.text(n, total + 0.25, f"+{total:.1f}%", ha="center", va="bottom",
            fontsize=11.5, color="#2F6E74", fontweight="semibold", zorder=3)
    labels.append(spec.get("end_label", "If all four land"))

    ax.axhline(0, color="#111111", linewidth=1.2, zorder=4)
    ax.annotate("flat", xy=(1.0, 0), xycoords=("axes fraction", "data"),
                xytext=(6, 0), textcoords="offset points", fontsize=10,
                color="#111111", va="center", ha="left", zorder=5)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=9.5, color="#333333")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:+.0f}%"))
    ax.set_ylim(float(spec.get("y_min", -4)), float(spec.get("y_max", 8)))
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="both", length=0, labelsize=9.5, colors="#666666")
    ax.grid(False)

    fig.tight_layout(pad=0.3)
    fig.savefig(out_path, facecolor=FINOPS_CARD_BG, dpi=dpi,
                bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)
    return out_path


def render_cashflow_forecast_chart(src: dict, out_path: Path, dpi: int = 200) -> Path:
    """Render the Daily Cash Balance Projection chart (Finops UI style).

    Finops UI uses a smooth line with no per-point markers (Chart.js default
    line chart). We mimic with matplotlib's `solid_capstyle='round'` and
    `solid_joinstyle='round'` for clean turns, NO scatter markers on the
    104 daily points (would look noisy on the slide).
    """
    from datetime import datetime
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    daily = src.get("daily_balance") or []
    dates = [datetime.strptime(p["date"], "%Y-%m-%d") for p in daily]
    vals = [p["balance_sek"] for p in daily]
    if not dates:
        return out_path

    fig, ax = plt.subplots(figsize=(8.0, 2.8), dpi=dpi)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    # Main balance line (Finops blue) — smooth, no per-point markers
    BLUE = "#2563EB"
    flat = src.get("flat_scenario") or None
    g = src.get("revenue_growth_pct_monthly")
    ax.plot(dates, vals, color=BLUE, linewidth=2.0, zorder=3,
            solid_capstyle="round", solid_joinstyle="round",
            antialiased=True, label=f"{g:g}% growth a month" if g else "Forecast")
    # No-growth scenario (Annika, board 2026-11-09): same forecast with revenue held flat.
    if flat and flat.get("daily_balance"):
        fd = [datetime.strptime(p["date"], "%Y-%m-%d") for p in flat["daily_balance"]]
        fv = [p["balance_sek"] for p in flat["daily_balance"]]
        ax.plot(fd, fv, color="#6B7280", linewidth=1.8, zorder=2.5, linestyle=(0, (6, 3)),
                solid_capstyle="round", antialiased=True, label=flat.get("label") or "No growth")
        ax.legend(loc="upper left", frameon=False, fontsize=8, labelcolor="#444444", handlelength=2.4)

    # Reference lines: 0 (green), warning (orange), credit (red)
    credit = src.get("credit_line_sek")
    warning = src.get("warning_line_sek")
    ax.axhline(0, color="#1F9D55", linewidth=1.0, linestyle=(0, (5, 4)), zorder=1)
    if warning is not None:
        ax.axhline(warning, color="#E1A04E", linewidth=1.0,
                   linestyle=(0, (5, 4)), zorder=1)
    if credit is not None:
        ax.axhline(credit, color="#D9534F", linewidth=1.0,
                   linestyle=(0, (5, 4)), zorder=1)

    # Vertical line: actuals through
    actuals_through = src.get("actuals_through_date")
    if actuals_through:
        a_dt = datetime.strptime(actuals_through, "%Y-%m-%d")
        ax.axvline(a_dt, color="#888888", linewidth=0.9,
                   linestyle=(0, (3, 3)), zorder=1)

    # Annotate min projected balance
    min_date = src.get("minimum_projected_date")
    min_val = src.get("minimum_projected_balance_sek")
    if min_date and min_val is not None:
        m_dt = datetime.strptime(min_date, "%Y-%m-%d")
        ax.scatter([m_dt], [min_val], color="#D9534F", s=44, zorder=5,
                   edgecolor="white", linewidth=1.4)

    # Y axis: thousands SEK
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{int(v):,}".replace(",", " ")))

    # X axis: date ticks at week intervals
    import matplotlib.dates as mdates
    # Weekly "%m-%d" ticks suit a ~90-day window. At the 600-day horizon (Henrik, 2026-09)
    # that was ~85 overlapping labels — an unreadable smear. Past ~4 months, tick monthly
    # and thin to at most ~12 labels (SKILL.md §61).
    span_days = (dates[-1] - dates[0]).days
    if span_days > 120:
        step = max(1, round(span_days / 30.4 / 12))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=step))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    else:
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    fig.autofmt_xdate(rotation=0, ha="center")

    # Styling
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#D0D0D0")
    ax.spines["bottom"].set_linewidth(0.6)
    ax.tick_params(axis="both", colors="#444444", labelsize=8.5, length=0, pad=4)
    ax.grid(axis="y", color="#EAEAEA", linewidth=0.6, zorder=0)
    ax.grid(axis="x", color="#F4F4F4", linewidth=0.4, zorder=0)
    ax.set_axisbelow(True)

    # Right-side labels for reference lines
    xmax = dates[-1]
    if credit is not None:
        ax.annotate(f"Credit line {int(credit):,}".replace(",", " "),
                    xy=(xmax, credit), xytext=(4, 0), textcoords="offset points",
                    fontsize=7.5, color="#D9534F", va="center")
    if warning is not None:
        ax.annotate(f"{int(warning):,}".replace(",", " "),
                    xy=(xmax, warning), xytext=(4, 0), textcoords="offset points",
                    fontsize=7.5, color="#9F6A20", va="center")
    ax.annotate("0 kr", xy=(xmax, 0), xytext=(4, 0),
                textcoords="offset points", fontsize=7.5, color="#1F9D55", va="center")

    fig.tight_layout(pad=0.3)
    fig.subplots_adjust(right=0.92)
    fig.savefig(out_path, facecolor="#FFFFFF", dpi=dpi,
                bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    return out_path


def render_saas40_chart(periods: list[dict], benchmark: float, out_path: Path, dpi: int = 200) -> Path:
    """SaaS40 (Rule of 40) stacked-bar trend: nettoomsättning YoY growth (bottom)
    + EBITDA margin (top), total = SaaS40, with a benchmark line at `benchmark`."""
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    labels = [p.get("label", "") for p in periods]
    growth = [float(p.get("growth_pct") or 0) for p in periods]
    margin = [float(p.get("margin_pct") or 0) for p in periods]
    totals = [float(p["saas40_pct"]) if p.get("saas40_pct") is not None else g + m
              for p, g, m in zip(periods, growth, margin)]
    x = list(range(len(labels)))

    fig, ax = plt.subplots(figsize=(6.6, 3.0))
    fig.patch.set_facecolor(FINOPS_CARD_BG)
    ax.set_facecolor(FINOPS_CARD_BG)
    w = 0.52
    # Positive growth stacks under the margin, so the bar top IS the total. Negative growth
    # cannot stack: drawn from 0 downward it vanished under ylim(0, …) and the margin bar
    # alone read as "SaaS40 = margin" (Q2 2026: 33.8 margin, −16.2 growth, shown as a plain
    # 18% margin bar). So negative growth goes below the axis in red, the margin rises from
    # 0, and the total is a marked tick on the bar (§58).
    pos = [max(g, 0) for g in growth]
    neg = [min(g, 0) for g in growth]
    ax.bar(x, pos, width=w, color=FINOPS_TEAL_DARK, zorder=2, label="Nettoomsättning YoY growth")
    ax.bar(x, margin, width=w, bottom=pos, color=FINOPS_TEAL_LIGHT, zorder=2, label="EBITDA margin")
    if any(neg):
        ax.bar(x, neg, width=w, color=FINOPS_CHURN_RED, zorder=2, label="Revenue decline YoY")
        ax.axhline(0, color="#999999", linewidth=0.8, zorder=3)
    ax.axhline(benchmark, color="#9F6A20", linewidth=1.2, linestyle=(0, (5, 4)), zorder=3)

    for xi, t, g, m in zip(x, totals, growth, margin):
        if g >= 0:
            ax.annotate(f"{t:.0f}%", xy=(xi, t), xytext=(0, 5), textcoords="offset points",
                        ha="center", va="bottom", fontsize=12, fontweight="bold",
                        color="#222222", zorder=4)
        else:
            ax.plot([xi - w / 2 - 0.06, xi + w / 2 + 0.06], [t, t], color="#222222",
                    linewidth=2.2, zorder=5, solid_capstyle="butt")
            ax.annotate(f"= {t:.0f}%", xy=(xi + w / 2 + 0.06, t), xytext=(4, 0),
                        textcoords="offset points", ha="left", va="center", fontsize=12,
                        fontweight="bold", color="#222222", zorder=5)
            ax.annotate(f"+{m:.0f}", xy=(xi, m), xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", fontsize=8.5, color="#444444", zorder=4)
            ax.annotate(f"{g:.0f}", xy=(xi, g), xytext=(0, -3), textcoords="offset points",
                        ha="center", va="top", fontsize=8.5, color=FINOPS_CHURN_RED, zorder=4)

    _style_axes(ax)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    top = max(totals + margin + [benchmark]) * 1.20
    ax.set_ylim(min(neg) * 1.35 if any(neg) else 0, top)
    ax.annotate(f"Rule of {benchmark:.0f}", xy=(x[-1] + 0.4, benchmark), xytext=(2, 2),
                textcoords="offset points", fontsize=8, color="#9F6A20", va="bottom", ha="right")
    ax.legend(loc="upper right", fontsize=8, frameon=False, labelcolor="#444444",
              handlelength=1.1, borderaxespad=0.2)

    fig.tight_layout(pad=0.3)
    fig.savefig(out_path, facecolor=FINOPS_CARD_BG, dpi=dpi, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    return out_path


def attach_knob_geometry(slide_seq: list[dict]) -> None:
    for s in slide_seq:
        if s.get("type") == "knob_row":
            prepare_knobs(s)
        elif s.get("type") == "growth_stack":
            prepare_growth_stack(s)
        elif s.get("type") == "orbit":
            prepare_orbit(s)


def attach_chart_paths(slide_seq: list[dict]) -> None:
    """Render any embedded charts (trends grid + cash position + cash flow forecast) to PNG.

    Filenames carry the slide's position in the deck (`si`). Without it, two
    single-chart slides under the same agenda item whose series have no title
    both resolve to the same path and the second overwrites the first — the deck
    then renders one chart twice with no error.
    """
    for si, s in enumerate(slide_seq):
        stype = s.get("type")
        if stype in ("trends_grid", "chart_comment"):
            trends = s.get("trends") or []
            for idx, t in enumerate(trends):
                ts = TrendSeries(**t) if not isinstance(t, TrendSeries) else t
                slug = re.sub(r"[^A-Za-z0-9]+", "_", ts.title).strip("_").lower() or "chart"
                out = CHARTS_DIR / f"trend-{s.get('agenda_number','x')}-{si}-{idx}-{slug}.png"
                render_chart(ts, out)
                t["image_path"] = str(out)
        elif stype == "growth_waterfall":
            out = CHARTS_DIR / f"waterfall-{s.get('agenda_number','x')}-{si}.png"
            render_growth_waterfall(s, out)
            s["chart_path"] = str(out)
        elif stype == "saas40":
            out = CHARTS_DIR / f"saas40-{s.get('agenda_number','x')}-{si}.png"
            render_saas40_chart(s.get("periods") or [], float(s.get("benchmark") or 40), out)
            s["saas40_chart_path"] = str(out)
        elif stype == "cash_position":
            ct = s.get("cash_trend")
            if ct:
                ts = TrendSeries(**ct) if not isinstance(ct, TrendSeries) else ct
                out = CHARTS_DIR / f"cash-{s.get('agenda_number','x')}-{si}.png"
                render_chart(ts, out)
                ct["image_path"] = str(out)
        elif stype == "cash_flow_forecast":
            src = s.get("cashflow_source") or {}
            out = CHARTS_DIR / f"cashflow-{s.get('agenda_number','x')}-{si}.png"
            render_cashflow_forecast_chart(src, out)
            s["cashflow_chart_path"] = str(out)
            s["cashflow_top_items"] = src.get("top_forecast_items") or []
            s["cashflow_summary"] = {
                "as_of_date": src.get("as_of_date"),
                "actuals_through_date": src.get("actuals_through_date"),
                "assumed_revenue_msek_month": src.get("assumed_revenue_msek_month"),
                "assumed_revenue_sek_day": src.get("assumed_revenue_sek_day"),
                # Growth must always be visible (Henrik 2026-11-04): Finops compounds it monthly.
                "revenue_growth_pct_monthly": src.get("revenue_growth_pct_monthly"),
                "growth_anchor_label": (__import__("datetime").date.fromisoformat(src["growth_anchor_month"]).strftime("%B %Y")
                                        if src.get("growth_anchor_month") else "now"),
                "minimum_projected_balance_sek": src.get("minimum_projected_balance_sek"),
                "minimum_projected_date": src.get("minimum_projected_date"),
                "credit_line_sek": src.get("credit_line_sek"),
                "revenue_assumption_rationale": src.get("revenue_assumption_rationale"),
                "flat_min_sek": (src.get("flat_scenario") or {}).get("minimum_projected_balance_sek"),
                "flat_min_date": (src.get("flat_scenario") or {}).get("minimum_projected_date"),
            }


# ---------------------------------------------------------------- main

def render(agenda_path: Path, data_path: Path, out_path: Path) -> Path:
    agenda = Agenda(**load_json(agenda_path))
    if data_path.exists():
        raw = load_json(data_path)
        raw = expand_data_refs(raw)
        deck = Deck(**raw)
    else:
        deck = Deck()

    slides = build_slide_sequence(agenda, deck)
    attach_chart_paths(slides)
    attach_knob_geometry(slides)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["assets_dir"] = str(ASSETS_DIR)
    template = env.get_template("template.html")

    html = template.render(
        meeting=agenda.meeting.model_dump(),
        slides=slides,
        deck_meta=deck.meta.model_dump(),
    )

    # For debugging, write the rendered HTML alongside.
    (SLIDES_DIR / ".last_render.html").write_text(html, encoding="utf-8")

    css_path = TEMPLATE_DIR / "style.css"
    HTML(string=html, base_url=str(SLIDES_DIR)).write_pdf(
        target=str(out_path),
        stylesheets=[CSS(filename=str(css_path))],
    )
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agenda", type=Path, default=DEFAULT_AGENDA)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    if args.out is not None:
        out_path = args.out
    else:
        agenda_for_prefix = Agenda(**load_json(args.agenda))
        out_path = next_versioned_path(derive_filename_prefix(agenda_for_prefix))
    result = render(args.agenda, args.data, out_path)
    print(f"Rendered -> {result}")


if __name__ == "__main__":
    main()
