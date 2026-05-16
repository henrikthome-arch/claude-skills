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
    target_msek: float
    actual_msek: float
    gap_msek: float
    gap_pct: float
    status: str = "ok"            # ok | warn | critical


class TrendSeries(BaseModel):
    model_config = ConfigDict(extra="allow")
    title: str
    unit: str | None = None
    kind: str = "bar"             # bar | line | stacked_bar
    points: list[dict] | None = None        # [{month, value}] or with extra keys for stacked
    stacked_keys: list[str] | None = None   # for stacked_bar
    y_format: str = "auto"        # auto | thousands | percent
    color: str | None = None      # hex override (defaults to FINOPS_TEAL)
    baseline: float | None = None  # draw a horizontal reference line and fill to it
    figsize: tuple[float, float] | None = None  # (width_in, height_in) override


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


class Slide(BaseModel):
    model_config = ConfigDict(extra="allow")
    type: str
    title: str | None = None
    subtitle: str | None = None
    bullets: list[str] | None = None
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

            if stype == "trends_grid":
                series = src.get("series", {})
                trends = []
                for spec in slide.get("trends_layout", []):
                    t = {
                        "title": spec["title"],
                        "kind": spec.get("kind", "bar"),
                        "y_format": spec.get("y_format", "auto"),
                    }
                    if t["kind"] == "stacked_bar":
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
                    trends.append(t)
                slide["trends"] = trends

            elif stype == "cash_position":
                slide["cash_trend"] = {
                    "title": "EOM Cash Position",
                    "kind": "line",
                    "y_format": "thousands_sek",
                    "color": "#2647A8",
                    "baseline": 0,
                    "figsize": [5.5, 3.2],
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
    pattern = re.compile(rf"{safe} v0\.(\d+)\.pdf$")
    existing = [int(m.group(1)) for p in OUTPUT_DIR.iterdir() if (m := pattern.match(p.name))]
    n = (max(existing) + 1) if existing else 1
    return OUTPUT_DIR / f"{filename_prefix} v0.{n}.pdf"


def derive_filename_prefix(agenda) -> str:
    return f"Sonetel board meeting {format_date(agenda.meeting.date)}"


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

    seq.append({
        "page_class": "agenda",
        "type": "agenda",
        "title": "Agenda",
        "agenda_items": [item.model_dump() for item in agenda.agenda_items],
        "total_minutes": agenda.total_duration_minutes,
        "show_time": any_duration,
    })

    for item in agenda.agenda_items:
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
    """2026-04 -> Apr 26"""
    try:
        y, m = iso.split("-")[:2]
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
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
        return
    if fmt == "thousands":
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v/1000)}K"))
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

    months = [p["month"] for p in (series.points or [])]
    x = list(range(len(months)))
    labels = [month_short(m) for m in months]

    if series.kind == "stacked_bar" and series.stacked_keys:
        bottoms = [0.0] * len(x)
        colors = [FINOPS_TEAL_DARK, FINOPS_TEAL_LIGHT]
        nice_labels = ["With subscription", "Without subscription"]
        for i, k in enumerate(series.stacked_keys):
            vals = [(p.get(k) or 0) for p in series.points]
            ax.bar(x, vals, bottom=bottoms, color=colors[i % len(colors)],
                   width=0.72, label=nice_labels[i] if i < len(nice_labels) else k, zorder=2)
            bottoms = [b + v for b, v in zip(bottoms, vals)]
        ax.legend(loc="upper right", frameon=False, fontsize=7.5,
                  labelcolor="#444444", handlelength=1.2, ncol=2,
                  bbox_to_anchor=(1.0, 1.12))
        flat = []
        for p in series.points:
            flat.append(sum((p.get(k) or 0) for k in series.stacked_keys))
        _format_y(ax, series.y_format, flat)
    elif series.kind == "line":
        vals = [p.get("value") for p in series.points]
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
        _format_y(ax, series.y_format, [v for v in vals if v is not None])
    else:  # bar
        color = series.color or FINOPS_TEAL_LIGHT
        vals = [p.get("value") or 0 for p in series.points]
        ax.bar(x, vals, color=color, width=0.72, zorder=2)
        _format_y(ax, series.y_format, vals)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    _style_axes(ax)

    fig.tight_layout(pad=0.3)
    fig.savefig(out_path, facecolor=FINOPS_CARD_BG, dpi=dpi,
                bbox_inches="tight", pad_inches=0.08)
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
    ax.plot(dates, vals, color=BLUE, linewidth=2.0, zorder=3,
            solid_capstyle="round", solid_joinstyle="round",
            antialiased=True)

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


def attach_chart_paths(slide_seq: list[dict]) -> None:
    """Render any embedded charts (trends grid + cash position + cash flow forecast) to PNG."""
    for s in slide_seq:
        stype = s.get("type")
        if stype == "trends_grid":
            trends = s.get("trends") or []
            for idx, t in enumerate(trends):
                ts = TrendSeries(**t) if not isinstance(t, TrendSeries) else t
                slug = re.sub(r"[^A-Za-z0-9]+", "_", ts.title).strip("_").lower()
                out = CHARTS_DIR / f"trend-{s.get('agenda_number','x')}-{idx}-{slug}.png"
                render_chart(ts, out)
                t["image_path"] = str(out)
        elif stype == "cash_position":
            ct = s.get("cash_trend")
            if ct:
                ts = TrendSeries(**ct) if not isinstance(ct, TrendSeries) else ct
                out = CHARTS_DIR / f"cash-{s.get('agenda_number','x')}.png"
                render_chart(ts, out)
                ct["image_path"] = str(out)
        elif stype == "cash_flow_forecast":
            src = s.get("cashflow_source") or {}
            out = CHARTS_DIR / f"cashflow-{s.get('agenda_number','x')}.png"
            render_cashflow_forecast_chart(src, out)
            s["cashflow_chart_path"] = str(out)
            s["cashflow_top_items"] = src.get("top_forecast_items") or []
            s["cashflow_summary"] = {
                "as_of_date": src.get("as_of_date"),
                "actuals_through_date": src.get("actuals_through_date"),
                "assumed_revenue_msek_month": src.get("assumed_revenue_msek_month"),
                "assumed_revenue_sek_day": src.get("assumed_revenue_sek_day"),
                "minimum_projected_balance_sek": src.get("minimum_projected_balance_sek"),
                "minimum_projected_date": src.get("minimum_projected_date"),
                "credit_line_sek": src.get("credit_line_sek"),
                "revenue_assumption_rationale": src.get("revenue_assumption_rationale"),
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
